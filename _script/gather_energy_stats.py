#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gather_energy_stats.py — CURE Lab energy market dashboard builder.

Maintains a local archive of daily energy / macro indicators, renders an
interactive Plotly dashboard, and records a recursive P10/P50/P90 outlook for
next week's WTI crude and Henry Hub gas.

The forecasting engine itself lives in `energy_predictor.py` — features,
hyperparameter tuning, fitting and the Monte-Carlo rollout. This file fetches,
archives and draws.

Output
------
_images/energy_stats.html    the dashboard
__datafile/energy_panel.csv  aggregated price archive, grows every run
__datafile/forecast_log.csv  every forecast ever made, for scoring

Usage
-----
    py -3.13 _script/gather_energy_stats.py
    py -3.13 _script/gather_energy_stats.py --display-days 45 --open
    py -3.13 _script/gather_energy_stats.py --no-cache      # full refetch

Notes
-----
* Runs are incremental. Each series resumes from its cached tail (minus a
  short overlap so revisions land) rather than re-downloading years of
  history; a missing or too-short archive triggers a full pull automatically.
* Three windows, deliberately different: the archive keeps everything, the
  figure is handed ~400 days so it can be panned, and the initial view is the
  last 90 days plus the forecast horizon.
* Every data source is fetched defensively. A source that fails falls back to
  the archive rather than raising.
* Each run logs its whole fan. Once a predicted day's close prints, the
  previous run's next-day P50 is drawn as a star on that candle — gold if the
  up/down call was right, navy if it was wrong, i.e. whether a daily
  long/short on the model would have made money. The header carries the
  resulting direction F1. Rows written by run_backtest_last_30days.py are
  tagged `source=backtest`; live runs are tagged `live` and always win.
* Set EIA_API_KEY in the environment to prefer the EIA v2 API over FRED.
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import math
import os
import re
import sys
import warnings
from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np
import pandas as pd
import requests

# The forecasting engine lives in its own module so this file stays about
# fetching, archiving and drawing. Swapping the model means editing that one.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import energy_predictor as P                                 # noqa: E402

warnings.filterwarnings("ignore")

# Korean console code pages (cp949) choke on em-dashes and Hangul in the
# progress log; force UTF-8 on the streams where the platform allows it.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                      # noqa: BLE001
        pass

# --------------------------------------------------------------------------
# Paths & constants
# --------------------------------------------------------------------------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_HTML = os.path.join(ROOT, "_images", "energy_stats.html")
PAGE_MD = os.path.join(ROOT, "i_7_energy_stats.markdown")

DATA_DIR = os.path.join(ROOT, "__datafile")
PANEL_CSV = os.path.join(DATA_DIR, "energy_panel.csv")
FORECAST_CSV = os.path.join(DATA_DIR, "forecast_log.csv")

# Re-pull this many days past the cached tail on every run. Yahoo settles its
# last bars and FRED revises, so the newest cached rows cannot be trusted as
# final — refetching a short overlap lets corrections land.
REFETCH_OVERLAP_DAYS = 10

# Vertical padding the wrapper adds around the figure (see PAGE_CSS).
WRAP_PAD = 14 + 22

DISPLAY_DAYS = 90       # window actually plotted (~3 months)
PLOT_DAYS = 400         # history handed to the figure (pannable beyond view)
TRAIN_YEARS = 4         # history pulled for model fitting

# Modelling constants belong to the predictor; re-exported here so the rest of
# this file and the backtest script keep reading them from one place.
LOOKBACK = P.LOOKBACK
FORECAST_HORIZON = P.FORECAST_HORIZON
N_PATHS = P.N_PATHS
METHOD = P.METHOD
RANDOM_STATE = P.RANDOM_STATE

KST = dt.timezone(dt.timedelta(hours=9))

PRIMARY = "#005BAC"
ACCENT = "#c0392b"
GRID = "#eef2f7"

UA = {"User-Agent": "Mozilla/5.0 (compatible; CURE-EnergyStats/1.0)"}


# --------------------------------------------------------------------------
# Series registry
# --------------------------------------------------------------------------

@dataclass
class Series:
    key: str
    label: str                   # legend entry / trace name
    source: str                  # yahoo | fred | eia | bakerhughes
    ids: list                    # candidate identifiers, tried in order
    kind: str = "line"           # line | candle | step
    tier: int = 3                # 1 = hero panel, 2+ = grouped context panel
    unit: str = ""
    note: str = ""
    color: str = PRIMARY
    secondary: bool = False      # draw against the right-hand y-axis
    dash: str = "solid"
    data: Optional[pd.DataFrame] = field(default=None, repr=False)
    status: str = "pending"
    resolved: str = ""           # "source:id" that actually returned data

    def cadence_days(self) -> float:
        """Median spacing between observations, in days."""
        if self.data is None or len(self.data) < 3:
            return float("nan")
        return float(pd.Series(self.data.index).diff()
                     .dt.days.median())


@dataclass
class Panel:
    """A context subplot, possibly holding several series."""
    title: str
    members: list                # Series keys, in draw order
    dual: bool = False           # second y-axis on the right
    y_left: str = ""
    y_right: str = ""


def panels() -> list:
    """
    Grouped context panels, laid out three per row beneath the hero row.

    Series whose levels differ by more than a factor of ~2 share a panel via a
    second y-axis; comparable ones (the three Treasury tenors, the two dollar
    indices) share a single axis so the curves can actually be read against
    each other.
    """
    return [
        Panel("원유 변동성 & 휘발유 · OVX (L) vs RBOB (R)",
              ["ovx", "rbob"], dual=True, y_left="OVX", y_right="$/gal"),
        Panel("S&P 500 (L) & 에너지 ETF XLE (R)",
              ["sp500", "xle"], dual=True, y_left="index", y_right="$"),
        Panel("미국 국채 금리 · UST 2Y / 10Y / 30Y",
              ["ust2", "ust10", "ust30"], y_left="%"),
        # Titled generically on purpose: FRED has no 2Y TIPS, so the short
        # leg resolves to 5Y and the colour key below carries the real tenors.
        Panel("미국 실질 금리 · TIPS Real Yields",
              ["tips2", "tips10", "tips30"], y_left="%"),
        Panel("달러 지수 · Broad TW USD & DXY",
              ["twdollar", "dxy"], y_left="index"),
        Panel("탄소배출권 ETF (KRBN)",
              ["eua"], y_left="$"),
    ]


def registry() -> list:
    """Declare every indicator requested for the dashboard."""
    return [
        # ---- tier 1 : the two hero panels -----------------------------
        Series("wti", "WTI 원유 (WTI Crude, $/bbl)", "yahoo", ["CL=F"],
               kind="candle", tier=1, unit="$/bbl"),
        Series("brent", "Brent 원유 (Brent)", "yahoo", ["BZ=F"],
               kind="line", tier=1, unit="$/bbl", color="#1a7a4a"),
        Series("gas", "천연가스 (Henry Hub, $/MMBtu)", "yahoo", ["NG=F"],
               kind="candle", tier=1, unit="$/MMBtu"),

        # ---- tier 2 : grouped context panels --------------------------
        Series("ovx", "OVX", "yahoo", ["^OVX"], tier=2, unit="",
               color=ACCENT),
        Series("rbob", "RBOB", "yahoo", ["RB=F"], tier=2, unit="$/gal",
               color="#5b3cc4", secondary=True),

        Series("sp500", "S&P 500", "yahoo", ["^GSPC"], tier=2, unit="idx"),
        Series("xle", "XLE", "yahoo", ["XLE"], tier=2, unit="$",
               color="#1a7a4a", secondary=True),

        Series("ust2", "UST 2Y", "fred", ["DGS2"], tier=2, unit="%",
               color="#7fb2e5"),
        Series("ust10", "UST 10Y", "fred", ["DGS10"], tier=2, unit="%",
               color=PRIMARY),
        Series("ust30", "UST 30Y", "fred", ["DGS30"], tier=2, unit="%",
               color="#002F6C"),

        # FRED publishes TIPS yields from 5Y out — there is no 2Y real rate
        # series — so the short leg falls back to 5Y and relabels itself.
        Series("tips2", "TIPS 2Y", "fred", ["DFII2", "DFII5"], tier=2,
               unit="%", color="#e8a33d"),
        Series("tips10", "TIPS 10Y", "fred", ["DFII10"], tier=2, unit="%",
               color="#c0392b"),
        Series("tips30", "TIPS 30Y", "fred", ["DFII30", "DFII20"], tier=2,
               unit="%", color="#7a1f16"),

        Series("twdollar", "Broad TW USD", "fred", ["DTWEXBGS"], tier=2,
               unit="idx", color=PRIMARY),
        Series("dxy", "DXY", "yahoo", ["DX-Y.NYB", "DX=F"], tier=2,
               unit="idx", color="#e8a33d"),

        Series("eua", "Carbon (KRBN)", "yahoo", ["KRBN"], tier=2, unit="$",
               color="#1a7a4a", note="ETF proxy"),
    ]


# A resolved FRED id that differs from the first choice should relabel its
# trace rather than quietly mislabel the tenor.
LEGEND_BY_ID = {
    "DFII5": "TIPS 5Y", "DFII10": "TIPS 10Y",
    "DFII20": "TIPS 20Y", "DFII30": "TIPS 30Y",
}


# --------------------------------------------------------------------------
# Fetchers — each returns a DataFrame indexed by date, or None
# --------------------------------------------------------------------------

def fetch_yahoo(ticker: str, start: dt.date, end: dt.date):
    """Daily OHLCV from Yahoo Finance."""
    import yfinance as yf

    df = yf.download(ticker, start=start, end=end, progress=False,
                     auto_adjust=False, threads=False)
    if df is None or df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.title)
    keep = [c for c in ("Open", "High", "Low", "Close") if c in df.columns]
    if "Close" not in keep:
        return None
    out = df[keep].copy()
    out.index = pd.to_datetime(out.index).tz_localize(None).normalize()
    return out.dropna(how="all")


def _get(url: str, tries: int = 3, timeout: int = 30):
    """GET with a short backoff. A 404 is a wrong ID — fail fast, no retry."""
    last = None
    for attempt in range(tries):
        try:
            r = requests.get(url, timeout=timeout, headers=UA)
            if r.status_code == 404:
                r.raise_for_status()
            r.raise_for_status()
            return r
        except requests.HTTPError:
            raise
        except Exception as exc:                           # noqa: BLE001
            last = exc
            if attempt < tries - 1:
                import time
                time.sleep(1.5 * (attempt + 1))
    raise last


def fetch_fred(series_id: str, start: dt.date, end: dt.date):
    """Daily/weekly/monthly observation from FRED's public CSV endpoint."""
    url = ("https://fred.stlouisfed.org/graph/fredgraph.csv"
           f"?id={series_id}&cosd={start:%Y-%m-%d}&coed={end:%Y-%m-%d}")
    r = _get(url)
    df = pd.read_csv(io.StringIO(r.text))
    if df.shape[1] < 2:
        return None
    date_col = df.columns[0]
    val_col = df.columns[1]
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df[val_col] = pd.to_numeric(df[val_col].replace(".", np.nan),
                                errors="coerce")
    df = df.dropna(subset=[date_col, val_col])
    if df.empty:
        return None
    out = df.set_index(date_col)[[val_col]].rename(columns={val_col: "Close"})
    out.index = out.index.normalize()
    return out


def fetch_eia(spec: str, start: dt.date, end: dt.date):
    """
    EIA Open Data v2. `spec` is "<route>:<series id>", e.g.
    "petroleum/stoc/wstk:WCESTUS1". Requires a free API key in EIA_API_KEY;
    without one this returns None and the caller falls back to FRED.
    """
    key = os.environ.get("EIA_API_KEY", "").strip()
    if not key:
        return None
    route, _, sid = spec.partition(":")
    url = (f"https://api.eia.gov/v2/{route}/data/"
           f"?api_key={key}&frequency=weekly&data[0]=value"
           f"&facets[series][]={sid}"
           f"&start={start:%Y-%m-%d}&end={end:%Y-%m-%d}"
           f"&sort[0][column]=period&sort[0][direction]=asc&length=5000")
    r = _get(url)
    rows = r.json().get("response", {}).get("data", [])
    if not rows:
        return None
    df = pd.DataFrame(rows)
    df["period"] = pd.to_datetime(df["period"], errors="coerce")
    df["Close"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["period", "Close"])
    if df.empty:
        return None
    return df.set_index("period")[["Close"]].sort_index()


def fetch_bakerhughes(_id: str, start: dt.date, end: dt.date):
    """
    Baker Hughes North America rotary rig count.

    There is no public API and no stable file URL — the workbook sits behind a
    rotating `static-files/<guid>` link on the landing page — so this scrapes
    the page for the current spreadsheet link and parses it. The site also
    rejects non-browser clients from many networks, in which case this simply
    returns None and the indicator is reported as unavailable.
    """
    page_url = "https://rigcount.bakerhughes.com/na-rig-count"
    r = _get(page_url, tries=2, timeout=25)
    hrefs = re.findall(r'href="([^"]+)"', r.text, re.I)
    links = [h for h in hrefs
             if re.search(r"\.(xlsx|xlsb|xls)(\?|$)", h, re.I)
             or "static-files" in h.lower()]
    for href in links[:6]:
        url = href if href.startswith("http") else (
            "https://rigcount.bakerhughes.com" + href)
        try:
            blob = _get(url, tries=1, timeout=40).content
            for skip in (0, 4, 6, 7):
                try:
                    xl = pd.read_excel(io.BytesIO(blob), sheet_name=0,
                                       skiprows=skip)
                except Exception:
                    continue
                cols = {str(c).strip().lower(): c for c in xl.columns}
                dcol = next((c for k, c in cols.items() if "date" in k), None)
                vcol = next((c for k, c in cols.items()
                             if "count" in k or "total" in k), None)
                if dcol is None or vcol is None:
                    continue
                out = xl[[dcol, vcol]].dropna()
                out.columns = ["date", "Close"]
                out["date"] = pd.to_datetime(out["date"], errors="coerce")
                out["Close"] = pd.to_numeric(out["Close"], errors="coerce")
                out = out.dropna().set_index("date").sort_index()
                if not out.empty:
                    return out.loc[str(start):]
        except Exception:
            continue
    return None


FETCHERS: dict = {
    "yahoo": fetch_yahoo,
    "fred": fetch_fred,
    "eia": fetch_eia,
    "bakerhughes": fetch_bakerhughes,
}


def gather(series_list: list, start: dt.date, end: dt.date,
           starts: Optional[dict] = None) -> list:
    """
    Populate `.data` / `.status` on every Series, never raising.

    Each candidate in `Series.ids` may carry an explicit "source@identifier"
    prefix; bare identifiers use the Series' default source. Candidates are
    tried in order and the first that returns rows wins, so an indicator can
    prefer the EIA API and quietly fall back to FRED.

    `starts` gives a per-series resume date from the archive, so a routine run
    downloads a few days rather than several years.
    """
    starts = starts or {}
    for s in series_list:
        s_start = starts.get(s.key, start)
        span = (end - s_start).days
        for ident in s.ids:
            source, sep, real_id = ident.partition("@")
            if not sep:
                source, real_id = s.source, ident
            fetcher: Callable = FETCHERS[source]
            try:
                df = fetcher(real_id, s_start, end)
            except Exception as exc:                      # noqa: BLE001
                msg = str(exc).split("\n")[0][:110]
                print(f"  ! {s.key:9s} [{source}:{real_id}] "
                      f"{type(exc).__name__}: {msg}")
                continue
            if df is not None and not df.empty:
                s.data = df
                s.resolved = f"{source}:{real_id}"
                s.status = f"ok ({len(df)} obs)"
                if real_id in LEGEND_BY_ID:
                    s.label = LEGEND_BY_ID[real_id]
                print(f"  + {s.key:9s} {s.status} via {s.resolved} "
                      f"[{s.label}]  (+{span}d)")
                break
        if s.data is None:
            s.status = "no new rows"
            print(f"  - {s.key:9s} no new rows this run")
    return series_list


def mark_cadence(series_list: list) -> None:
    """
    Draw a series solid only if it really is daily; anything coarser is dashed
    and says so, so a forward-filled monthly benchmark is never mistaken for a
    daily quote. Run after hydration, when `data` spans the whole archive — a
    single incremental pull is too short to measure cadence from.
    """
    for s in series_list:
        cadence = s.cadence_days()
        if cadence == cadence and cadence > 4:
            s.dash = "dot"
            s.note = "monthly, held" if cadence > 20 else "weekly, held"
            print(f"      {s.key}: ~{cadence:.0f}d cadence -> {s.note}")


# --------------------------------------------------------------------------
# Local archive — __datafile/energy_panel.csv
# --------------------------------------------------------------------------

def _cache_cols(s: "Series") -> list:
    """OHLC is only kept for the two candle contracts; the rest need Close."""
    return ["Open", "High", "Low", "Close"] if s.kind == "candle" \
        else ["Close"]


def load_panel_cache() -> pd.DataFrame:
    """Read the aggregated archive, or an empty frame on first run."""
    if not os.path.exists(PANEL_CSV):
        return pd.DataFrame()
    try:
        df = pd.read_csv(PANEL_CSV, index_col=0, parse_dates=[0])
        df.index = pd.to_datetime(df.index).normalize()
        return df[~df.index.duplicated(keep="last")].sort_index()
    except Exception as exc:                                   # noqa: BLE001
        print(f"  ! cache unreadable ({type(exc).__name__}); starting fresh")
        return pd.DataFrame()


def save_panel_cache(df: pd.DataFrame) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    df.sort_index().to_csv(PANEL_CSV, index_label="date",
                           float_format="%.6g")


def fetch_start_for(s: "Series", cache: pd.DataFrame, full_start: dt.date,
                    ) -> dt.date:
    """
    Where to resume fetching this series.

    Normally just past the cached tail, minus an overlap. Two cases force a
    full pull: no cached column at all, and a cache that does not reach far
    enough back to train on (otherwise a short first cache would permanently
    cap the training window).
    """
    col = f"{s.key}_Close"
    if cache.empty or col not in cache.columns:
        return full_start
    valid = cache[col].dropna()
    if valid.empty:
        return full_start
    if valid.index.min().date() > full_start + dt.timedelta(days=45):
        return full_start
    return max(full_start,
               valid.index.max().date()
               - dt.timedelta(days=REFETCH_OVERLAP_DAYS))


def series_to_frame(series_list: list) -> pd.DataFrame:
    """Flatten freshly-fetched series into one wide `key_Field` frame."""
    frames = []
    for s in series_list:
        if s.data is None or s.data.empty:
            continue
        cols = [c for c in _cache_cols(s) if c in s.data.columns]
        if not cols:
            continue
        sub = s.data[cols].copy()
        sub.columns = [f"{s.key}_{c}" for c in cols]
        frames.append(sub)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, axis=1).sort_index()
    return out[~out.index.duplicated(keep="last")]


def merge_cache(old: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    """Union of both, with freshly-fetched values winning on any overlap."""
    if old.empty:
        return new
    if new.empty:
        return old
    merged = new.combine_first(old)
    return merged[~merged.index.duplicated(keep="last")].sort_index()


def hydrate_from_cache(series_list: list, cache: pd.DataFrame) -> None:
    """Rebuild every `Series.data` from the archive, not just today's pull."""
    if cache.empty:
        return
    for s in series_list:
        prefix = f"{s.key}_"
        cols = [c for c in cache.columns if c.startswith(prefix)]
        if not cols:
            continue
        sub = cache[cols].copy()
        sub.columns = [c[len(prefix):] for c in cols]
        sub = sub.apply(pd.to_numeric, errors="coerce").dropna(how="all")
        if sub.empty:
            continue
        s.data = sub
        if s.status.startswith("ok") or s.status == "unavailable":
            s.status = f"{s.status} | archive {len(sub)} obs"


# --------------------------------------------------------------------------
# Forecast track record — __datafile/forecast_log.csv
# --------------------------------------------------------------------------

FORECAST_COLS = ["run_date", "target", "step", "horizon_date",
                 "p10", "p50", "p90", "spot", "source"]


def load_forecast_log() -> pd.DataFrame:
    if not os.path.exists(FORECAST_CSV):
        return pd.DataFrame(columns=FORECAST_COLS)
    try:
        df = pd.read_csv(FORECAST_CSV,
                         parse_dates=["run_date", "horizon_date"])
        for c in FORECAST_COLS:
            if c not in df.columns:
                df[c] = np.nan
        return df
    except Exception as exc:                                   # noqa: BLE001
        print(f"  ! forecast log unreadable ({type(exc).__name__})")
        return pd.DataFrame(columns=FORECAST_COLS)


def record_forecasts(log: pd.DataFrame, forecasts: dict,
                     source: str = "live") -> pd.DataFrame:
    """
    Append this run's whole fan to the log, keyed by the date it was made.

    Step 1 is the next-day call that later gets scored against the actual
    close; the remaining steps are kept so longer-horizon accuracy can be
    checked too. Re-running on the same data overwrites rather than
    duplicating, so the log stays one row per (run date, target, step).
    """
    rows = []
    for key, fc in forecasts.items():
        t0 = pd.Timestamp(fc["asof"]).normalize()
        for i, (p10, p50, p90) in enumerate(
                zip(fc["path_p10"], fc["path_p50"], fc["path_p90"]), start=1):
            rows.append({
                "run_date": t0, "target": key, "step": i,
                "horizon_date": (t0 + pd.tseries.offsets.BDay(i)).normalize(),
                "p10": p10, "p50": p50, "p90": p90, "spot": fc["spot"],
                "source": source,
            })
    if not rows:
        return log
    new = pd.DataFrame(rows)
    combined = pd.concat([log, new], ignore_index=True)
    # New rows are appended last, so a live run supersedes a backtested row
    # for the same day rather than the other way round.
    combined = combined.drop_duplicates(subset=["run_date", "target", "step"],
                                        keep="last")
    return combined.sort_values(["target", "run_date", "step"])


def save_forecast_log(log: pd.DataFrame) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    out = log.copy()
    for c in ("run_date", "horizon_date"):
        out[c] = pd.to_datetime(out[c]).dt.strftime("%Y-%m-%d")
    if "source" not in out.columns:
        out["source"] = "live"
    out["source"] = out["source"].fillna("live")
    out[FORECAST_COLS].to_csv(FORECAST_CSV, index=False, float_format="%.6g")


def score_predictions(log: pd.DataFrame, actual: pd.Series):
    """
    Line up next-day (step 1) calls against the closes that have since
    printed.

    Returns a frame indexed by the predicted date with the price call, the
    close that arrived, and the *direction* verdict — did the model say up or
    down relative to the last known close, and did the market agree. The
    direction is what a daily long/short would have traded on, so it is
    scored separately from the price error.
    """
    if log is None or log.empty or actual is None or actual.empty:
        return None
    sub = log[log["step"] == 1].copy()
    if sub.empty:
        return None
    sub["horizon_date"] = pd.to_datetime(sub["horizon_date"]).dt.normalize()
    sub = sub.sort_values("run_date").drop_duplicates(
        subset=["horizon_date"], keep="last")
    sub = sub.set_index("horizon_date").sort_index()

    idx = sub.index.intersection(actual.dropna().index)
    if len(idx) == 0:
        return None

    out = pd.DataFrame(index=idx)
    out["pred"] = pd.to_numeric(sub["p50"].reindex(idx), errors="coerce")
    out["spot"] = pd.to_numeric(sub["spot"].reindex(idx), errors="coerce")
    out["actual"] = pd.to_numeric(actual.reindex(idx), errors="coerce")
    if "source" in sub.columns:
        out["source"] = sub["source"].reindex(idx).fillna("live")
    else:
        out["source"] = "live"
    out = out.dropna(subset=["pred", "spot", "actual"])
    if out.empty:
        return None

    out["err_pct"] = (out["pred"] / out["actual"] - 1.0) * 100.0
    out["pred_ret"] = (out["pred"] / out["spot"] - 1.0) * 100.0
    out["act_ret"] = (out["actual"] / out["spot"] - 1.0) * 100.0
    out["pred_up"] = out["pred"] > out["spot"]
    out["act_up"] = out["actual"] > out["spot"]
    out["correct"] = out["pred_up"] == out["act_up"]
    return out


def directional_stats(scored: Optional[pd.DataFrame]) -> Optional[dict]:
    """
    Treat each next-day call as a long/short decision and score it.

    "Up" is the positive class, so precision is how often a long was right
    and recall is how many of the up days were caught. F1 balances the two,
    which matters because a model that simply always predicts up can post a
    respectable hit rate in a rising market while being useless.
    """
    if scored is None or scored.empty:
        return None
    tp = int((scored["pred_up"] & scored["act_up"]).sum())
    fp = int((scored["pred_up"] & ~scored["act_up"]).sum())
    fn = int((~scored["pred_up"] & scored["act_up"]).sum())
    tn = int((~scored["pred_up"] & ~scored["act_up"]).sum())
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    n = len(scored)
    return {
        "n": n, "hits": tp + tn, "hit_rate": (tp + tn) / n if n else 0.0,
        "precision": prec, "recall": rec, "f1": f1,
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "mae_pct": float(scored["err_pct"].abs().mean()),
    }


# --------------------------------------------------------------------------
# Forecasting — multivariate random forest with residual-bootstrap quantiles
# --------------------------------------------------------------------------

def daily_panel(series_list: list) -> pd.DataFrame:
    """
    Business-day close panel of every available series.

    Weekly (EIA) and monthly (industrial production) series are forward-filled
    without a limit: the last published figure genuinely *is* the market's
    best information until the next release. Capping the fill would leave the
    low-frequency columns mostly NaN and, once rows with any NaN are dropped,
    silently destroy the entire training set.
    """
    cols = {}
    for s in series_list:
        if s.data is not None and "Close" in s.data.columns:
            cols[s.key] = s.data["Close"]
    if not cols:
        return pd.DataFrame()
    panel = pd.DataFrame(cols).sort_index()
    panel = panel.resample("B").last().ffill()
    return panel.dropna(how="all")


# --------------------------------------------------------------------------
# Figure construction
# --------------------------------------------------------------------------

# A 6-column grid: the two hero rows span all six, every context row 2+2+2.
NCOLS = 6

# Target drawn height per row, in pixels. The figure height is solved back
# from these so panels keep a usable aspect ratio however many rows appear.
OIL_ROW_PX = 380
GAS_ROW_PX = 330
CTX_ROW_PX = 250
VSPACE = 0.045


def _layout_plan(series_list: list, panel_list: list):
    """
    Row 1: crude oil, full width. Row 2: natural gas, full width.
    Rows 3+: three grouped context panels per row.

    Panels whose members all failed to fetch are dropped entirely, so an
    unavailable indicator leaves no empty axes behind.
    """
    by_key = {s.key: s for s in series_list}
    live = []
    for p in panel_list:
        members = [by_key[k] for k in p.members
                   if k in by_key and by_key[k].data is not None]
        if members:
            live.append((p, members))

    full = [{"colspan": NCOLS}] + [None] * (NCOLS - 1)
    specs = [list(full), list(full)]
    titles = ["원유 가격 · Crude Oil (WTI candles · Brent line)",
              "천연가스 가격 · Natural Gas (Henry Hub)"]

    placements = []
    n_rows = math.ceil(len(live) / 3) if live else 0
    idx = 0
    for _ in range(n_rows):
        row_spec = [None] * NCOLS
        for slot in range(3):
            col = slot * 2 + 1
            if idx < len(live):
                panel, members = live[idx]
                row_spec[col - 1] = {"colspan": 2,
                                     "secondary_y": bool(panel.dual)}
                titles.append(panel.title)
                placements.append((panel, members, len(specs) + 1, col))
                idx += 1
            else:
                # Pad the trailing gap with an empty cell so make_subplots
                # keeps the remaining panels left-aligned at their width.
                row_spec[col - 1] = {"colspan": 2}
                titles.append("")
        specs.append(row_spec)

    px = [OIL_ROW_PX, GAS_ROW_PX] + [CTX_ROW_PX] * n_rows
    total = sum(px)
    heights = [h / total for h in px]
    return specs, titles, heights, placements, total


def _hero(fig, go, s, name, row, col, clip, legend, up="#c0392b",
          down="#1a6dcc"):
    """Draw one hero contract as candles, falling back to a line."""
    d = clip(s.data)
    if d.empty:
        return
    if {"Open", "High", "Low", "Close"} <= set(d.columns):
        fig.add_trace(go.Candlestick(
            x=d.index, open=d["Open"], high=d["High"], low=d["Low"],
            close=d["Close"], name=name, whiskerwidth=0.4,
            increasing_line_color=up, decreasing_line_color=down,
            showlegend=True, legend=legend,
        ), row=row, col=col)
    else:
        fig.add_trace(go.Scatter(
            x=d.index, y=d["Close"], name=name, showlegend=True,
            legend=legend, line=dict(color=s.color, width=2),
        ), row=row, col=col)


# Direction called right / wrong — i.e. a daily long-short on the model's
# next-day sign would have made money / lost it.
STAR_HIT = "#ffc400"
STAR_MISS = "#123a6b"


def _add_prediction_stars(fig, go, key, row, legend, s, scored, clip) -> int:
    """
    Overlay the previous run's next-day P50 on the candle it was predicting,
    coloured by whether the *direction* was right.

    Read as a daily long/short: gold means the model's up/down call matched
    what the close did, navy means it was on the wrong side.
    """
    if scored is None or scored.empty or s.data is None:
        return 0
    visible = clip(s.data)
    if len(visible):
        scored = scored[scored.index >= visible.index.min()]
    if scored.empty:
        return 0

    for correct, colour, edge, label in (
            (True, STAR_HIT, "#7a5c00", "Direction called right"),
            (False, STAR_MISS, "#06203f", "Direction called wrong")):
        part = scored[scored["correct"] == correct]
        if part.empty:
            continue
        fig.add_trace(go.Scatter(
            x=part.index, y=part["pred"], mode="markers", name=label,
            legend=legend, showlegend=True,
            marker=dict(symbol="star", size=11, color=colour,
                        line=dict(width=1, color=edge)),
            # A list of tuples, not np.column_stack: stacking a string column
            # with floats upcasts the whole array to strings and the numeric
            # hover formats below would silently stop working.
            customdata=list(zip(
                part["actual"].astype(float),
                part["err_pct"].astype(float),
                part["pred_ret"].astype(float),
                part["act_ret"].astype(float),
                part["source"].astype(str))),
            hovertemplate=(
                "<b>Predicted</b> %{y:,.2f} "
                "(%{customdata[2]:+.2f}%)<br>"
                "Actual %{customdata[0]:,.2f} "
                "(%{customdata[3]:+.2f}%)<br>"
                "Price error %{customdata[1]:+.2f}%<br>"
                "<i>%{customdata[4]}</i><extra></extra>"),
        ), row=row, col=1)
    return len(scored)


def _y_range(chunks: list, pad: float = 0.07):
    """Padded [lo, hi] over the given arrays, or None if there is nothing."""
    arrays = [np.asarray(c, dtype=float).ravel() for c in chunks
              if c is not None and len(c)]
    if not arrays:
        return None
    vals = np.concatenate(arrays)
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return None
    lo, hi = float(vals.min()), float(vals.max())
    margin = (hi - lo) * pad if hi > lo else (abs(hi) * 0.05 or 1.0)
    return [lo - margin, hi + margin]


def _in_view(s, view_start, cols=("Close",)) -> list:
    """Values of `s` inside the opening view, per requested column."""
    if s is None or s.data is None:
        return []
    d = s.data[s.data.index >= view_start]
    out = []
    for c in cols:
        if c in d.columns:
            out.append(pd.to_numeric(d[c], errors="coerce").dropna().values)
    return out


def _apply_view_yranges(fig, by_key, placements, forecasts, view_start):
    """
    Scale each panel's y-axis to what is actually on screen.

    The traces carry far more history than the opening view, so Plotly's
    autorange would fit the y-axis to years of data and squash the last three
    months into a sliver. Ranges are therefore pinned to the visible window —
    including the forecast fan, so it is never clipped.
    """
    # Hero panels: candle extremes plus the forecast band.
    for key, row, extra in (("wti", 1, ("brent",)), ("gas", 2, ())):
        s = by_key.get(key)
        chunks = _in_view(s, view_start, ("Low", "High", "Close"))
        for k in extra:
            chunks += _in_view(by_key.get(k), view_start)
        fc = forecasts.get(key)
        if fc:
            chunks += [fc["path_p10"], fc["path_p90"], [fc["spot"]]]
        rng = _y_range(chunks)
        if rng:
            fig.update_yaxes(range=rng, row=row, col=1)

    # Context panels, primary and secondary axes scaled independently.
    for panel, members, row, col in placements:
        for secondary in (False, True):
            if secondary and not panel.dual:
                continue
            group = [m for m in members
                     if bool(panel.dual and m.secondary) == secondary]
            chunks = []
            for m in group:
                chunks += _in_view(m, view_start)
            rng = _y_range(chunks)
            if rng:
                fig.update_yaxes(range=rng, row=row, col=col,
                                 secondary_y=secondary)


PERF_WINDOW = 28         # scored days the red band always covers
STOP_LOSS = 0.02         # intraday loss at which the day's position is closed
BACKTEST_FILL = "rgba(214,48,49,0.10)"


def longshort_returns(scored: Optional[pd.DataFrame],
                      ohlc: Optional[pd.DataFrame] = None,
                      stop: float = STOP_LOSS) -> Optional[dict]:
    """
    Equity multiples from trading the model's daily direction call.

    Base rule: long one unit when it says tomorrow closes higher, short one
    unit when it says lower, entered at the previous close and held to this
    one. 1.10 means the stake grew a tenth.

    Stop rule: the same, but the position is closed the moment the day's move
    goes `stop` against it, capping that day near -2% instead of riding the
    full adverse move. The day's own high and low decide whether the stop was
    touched, and a gap through it fills at the open — worse than the stop —
    rather than pretending the exit was free.

    Both are frictionless: no spread, financing or slippage. Treat them as
    ceilings on what the signal is worth.
    """
    if scored is None or scored.empty:
        return None
    long_side = scored["pred_up"].values
    entry = scored["spot"].values.astype(float)
    close = scored["actual"].values.astype(float)

    plain = np.where(long_side, close / entry - 1.0, -(close / entry - 1.0))

    stopped = np.zeros(len(scored), dtype=bool)
    ret = plain.copy()
    if ohlc is not None and {"Open", "High", "Low"} <= set(ohlc.columns):
        bar = ohlc.reindex(scored.index)
        op = pd.to_numeric(bar["Open"], errors="coerce").values
        hi = pd.to_numeric(bar["High"], errors="coerce").values
        lo = pd.to_numeric(bar["Low"], errors="coerce").values
        have = np.isfinite(op) & np.isfinite(hi) & np.isfinite(lo)

        for i in range(len(scored)):
            if not have[i]:
                continue
            if long_side[i]:
                trigger = entry[i] * (1.0 - stop)
                if op[i] <= trigger:                  # gapped through it
                    ret[i], stopped[i] = op[i] / entry[i] - 1.0, True
                elif lo[i] <= trigger:
                    ret[i], stopped[i] = -stop, True
            else:
                trigger = entry[i] * (1.0 + stop)
                if op[i] >= trigger:
                    ret[i], stopped[i] = -(op[i] / entry[i] - 1.0), True
                elif hi[i] >= trigger:
                    ret[i], stopped[i] = -stop, True

    return {
        "plain": float(np.prod(1.0 + plain)),
        "stopped": float(np.prod(1.0 + ret)),
        "n": int(len(scored)),
        "n_stopped": int(stopped.sum()),
        "has_bars": bool(ohlc is not None
                         and {"Open", "High", "Low"} <= set(ohlc.columns)),
    }


def _add_performance_band(fig, by_key, log) -> dict:
    """
    Shade the most recent `PERF_WINDOW` scored days and label what trading
    them would have returned.

    The window is deliberately rolling rather than the full history: it always
    covers the last 28 scored calls, so the band stays the same size as live
    days accumulate instead of creeping wider every run.

    The band is a background shape, not a trace, so it adds no legend entry;
    the y-ranges are already pinned by this point, so the label can sit at a
    known height.
    """
    out = {}
    if log is None or log.empty:
        return out
    for key, row, yname in (("wti", 1, "yaxis"), ("gas", 2, "yaxis2")):
        s = by_key.get(key)
        if s is None or s.data is None:
            continue
        scored = score_predictions(log[log["target"] == key],
                                   s.data["Close"])
        if scored is None or scored.empty:
            continue
        scored = scored.tail(PERF_WINDOW)

        x0, x1 = scored.index.min(), scored.index.max()
        fig.add_vrect(x0=x0 - pd.Timedelta(hours=12),
                      x1=x1 + pd.Timedelta(hours=12),
                      row=row, col=1, layer="below",
                      fillcolor=BACKTEST_FILL, line_width=0)

        res = longshort_returns(scored, s.data)
        if res is None:
            continue
        out[key] = res

        try:
            lo, hi = fig.layout[yname].range
        except Exception:                                  # noqa: BLE001
            continue
        if lo is None or hi is None:
            continue
        sub = (f"2% stop-loss · last {res['n']} days · "
               f"{res['n_stopped']} stopped<br>no stop: "
               f"{res['plain'] * 100:,.1f}%")
        fig.add_annotation(
            x=x0 + (x1 - x0) / 2, y=lo + 0.90 * (hi - lo), row=row, col=1,
            showarrow=False, align="center",
            text=(f"<b>{res['stopped'] * 100:,.1f}%</b><br>"
                  f"<span style='font-size:9.5px;color:#8a5a55'>{sub}</span>"),
            font=dict(size=16, color="#c0392b"),
            bgcolor="rgba(255,255,255,0.72)", borderpad=3,
        )
    return out


def _add_hero_legends(fig, rows: int) -> None:
    """
    A legend box per hero panel. Plotly's multi-legend support lets each sit
    inside its own subplot instead of one shared key far from the data; the
    context panels keep their inline colour swatches.
    """
    try:
        r1 = tuple(fig.get_subplot(1, 1).yaxis.domain)
        r2 = tuple(fig.get_subplot(2, 1).yaxis.domain)
    except Exception:                                          # noqa: BLE001
        r1, r2 = (0.78, 1.0), (0.55, 0.75)

    common = dict(
        xanchor="left", yanchor="top", x=0.006, orientation="v",
        bgcolor="rgba(255,255,255,0.88)", bordercolor="#c9d6e6",
        borderwidth=1, font=dict(size=10), itemsizing="constant",
        tracegroupgap=2,
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(title=dict(text="<b>Crude oil</b>",
                               font=dict(size=10, color=PRIMARY)),
                    y=r1[1] - 0.004, **common),
        legend2=dict(title=dict(text="<b>Natural gas</b>",
                                font=dict(size=10, color=PRIMARY)),
                     y=r2[1] - 0.004, **common),
    )


def build_figure(series_list: list, forecasts: dict, window_start,
                 display_days: int, log=None, view_start=None,
                 view_end=None):
    """
    `window_start` bounds the data handed to the traces; `view_start`/
    `view_end` bound only the initial camera. Loading more than is shown is
    what makes panning back possible without regenerating the page.
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    by_key = {s.key: s for s in series_list}
    panel_list = panels()
    specs, titles, heights, placements, rows_px = _layout_plan(
        series_list, panel_list)
    rows = len(specs)

    fig = make_subplots(
        rows=rows, cols=NCOLS, specs=specs, subplot_titles=titles,
        row_heights=heights, vertical_spacing=VSPACE,
        horizontal_spacing=0.055,
    )

    def clip(df):
        return df[df.index >= window_start]

    # ---------------- row 1 : crude oil ----------------
    wti = by_key.get("wti")
    if wti and wti.data is not None:
        _hero(fig, go, wti, "WTI", 1, 1, clip, "legend")

    brent = by_key.get("brent")
    if brent is not None and brent.data is not None:
        d = clip(brent.data)
        if not d.empty:
            label = "Brent" + (f" ({brent.note})" if brent.note else "")
            fig.add_trace(go.Scatter(
                x=d.index, y=d["Close"], name=label, opacity=0.9,
                legend="legend", showlegend=True,
                line=dict(color=brent.color, width=1.8, dash=brent.dash),
                hovertemplate=f"<b>{label}</b> %{{y:,.2f}}<extra></extra>",
            ), row=1, col=1)

    # ---------------- row 2 : natural gas ----------------
    gas = by_key.get("gas")
    if gas and gas.data is not None:
        _hero(fig, go, gas, "Henry Hub", 2, 1, clip, "legend2")

    # ---------------- track record: yesterday's call on today's bar --------
    n_scored, stats = {}, {}
    for key, hero_row, lg in (("wti", 1, "legend"), ("gas", 2, "legend2")):
        s = by_key.get(key)
        if s is None or s.data is None or log is None or log.empty:
            continue
        scored = score_predictions(log[log["target"] == key],
                                   s.data["Close"])
        stats[key] = directional_stats(scored)
        n_scored[key] = _add_prediction_stars(
            fig, go, key, hero_row, lg, s, scored, clip)

    # ---------------- forecast fans on the hero panels ----------------
    for key, hero_row, lg in (("wti", 1, "legend"), ("gas", 2, "legend2")):
        fc = forecasts.get(key)
        if not fc:
            continue
        t0 = pd.Timestamp(fc["asof"])
        steps = [t0 + pd.tseries.offsets.BDay(i + 1)
                 for i in range(len(fc["path_p50"]))]
        # Anchor the fan at today's close so it grows out of the last candle.
        xs = [t0] + steps
        upper = [fc["spot"]] + fc["path_p90"]
        lower = [fc["spot"]] + fc["path_p10"]
        mid = [fc["spot"]] + fc["path_p50"]

        fig.add_trace(go.Scatter(
            x=xs + xs[::-1], y=upper + lower[::-1],
            fill="toself", mode="lines", line=dict(width=0),
            fillcolor="rgba(91,60,196,0.15)", hoverinfo="skip",
            name="Forecast P10–P90", legend=lg, showlegend=True,
        ), row=hero_row, col=1)
        fig.add_trace(go.Scatter(
            x=xs, y=mid, mode="lines+markers",
            line=dict(color="#5b3cc4", width=2, dash="dash"),
            marker=dict(size=5, symbol="diamond"), name="Forecast P50",
            legend=lg, showlegend=True,
            hovertemplate="P50 %{y:,.2f}<extra></extra>",
        ), row=hero_row, col=1)

    # ---------------- grouped context panels ----------------
    for panel, members, row, col in placements:
        for s in members:
            d = clip(s.data)
            if d.empty or "Close" not in d.columns:
                continue
            sec = bool(panel.dual and s.secondary)
            fig.add_trace(go.Scatter(
                x=d.index, y=d["Close"], name=s.label, mode="lines",
                line=dict(color=s.color, width=1.9,
                          dash="dash" if sec else "solid",
                          shape="hv" if s.kind == "step" else "linear"),
                legendgroup=s.key, showlegend=False,
                hovertemplate=f"<b>{s.label}</b> %{{y:,.2f}} {s.unit}"
                              "<extra></extra>",
            ), row=row, col=col, secondary_y=sec)

        # Name each axis so a dual panel is readable without a legend.
        if panel.y_left:
            fig.update_yaxes(title_text=panel.y_left, row=row, col=col,
                             title_font=dict(size=9.5, color="#8b97a8"),
                             secondary_y=False)
        if panel.dual and panel.y_right:
            fig.update_yaxes(title_text=panel.y_right, row=row, col=col,
                             title_font=dict(size=9.5, color="#8b97a8"),
                             showgrid=False, secondary_y=True)

        # Inline colour key, since per-trace legends would be unreadable
        # across a dozen small panels.
        key_txt = "  ".join(
            f"<span style='color:{s.color}'>&#9632; {s.label}</span>"
            for s in members)
        fig.add_annotation(
            text=key_txt, row=row, col=col, xref="x domain", yref="y domain",
            x=0.01, y=0.99, xanchor="left", yanchor="top", showarrow=False,
            font=dict(size=9.5), bgcolor="rgba(255,255,255,0.72)",
            borderpad=2,
        )

    # ---------------- subplot title styling ----------------
    for i, t in enumerate(fig.layout.annotations[:len(titles)]):
        t.font.size = 15 if i < 2 else 11.5
        t.font.color = "#12395e" if i < 2 else "#44546a"

    # ---------------- synchronised axes ----------------
    # Every panel shares one x-range: pan or zoom anywhere and the whole
    # dashboard follows. `matches` links the ranges; the shared spike line
    # makes the common cursor position visible across panels.
    fig.update_xaxes(showgrid=True, gridcolor=GRID, rangeslider_visible=False,
                     showspikes=True, spikemode="across", spikethickness=1,
                     spikecolor="#8b97a8", spikedash="dot",
                     matches="x")
    # `matches` was just applied to every axis including the anchor itself;
    # leaving xaxis pointing at "x" is a self-reference that Plotly.js
    # rejects. The anchor must be the one axis with no match.
    fig.layout.xaxis.matches = None
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False,
                     tickfont=dict(size=9.5))

    # make_subplots leaves a few percent of unused width on the right when
    # columns are spanned (it charges the inter-column gap to the last cell of
    # each span). Rescale every x domain so the grid actually reaches the
    # right edge; relative widths and gaps are preserved.
    x_axes = [k for k in fig.layout if k.startswith("xaxis")]
    right = max(fig.layout[k].domain[1] for k in x_axes)
    if right < 0.999:
        scale = 1.0 / right
        for k in x_axes:
            d0, d1 = fig.layout[k].domain
            fig.layout[k].domain = (d0 * scale, min(d1 * scale, 1.0))

    stamp = dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    n_ok = sum(1 for s in series_list if s.data is not None)

    # Solve the figure height back from the per-row pixel targets. Plotly
    # splits the plot area between rows and (rows-1) gaps of VSPACE each, so
    # the drawable fraction is 1 - (rows-1)*VSPACE.
    margin_t, margin_b = 205, 96
    usable = max(1.0 - (rows - 1) * VSPACE, 0.35)
    fig_height = int(round(rows_px / usable)) + margin_t + margin_b

    fig.update_layout(
        height=fig_height,
        margin=dict(l=58, r=48, t=margin_t, b=margin_b),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="-apple-system,BlinkMacSystemFont,Segoe UI,"
                         "Helvetica,Arial,sans-serif", size=11.5,
                  color="#25313f"),
        hovermode="x unified",
        dragmode="pan",
        title=dict(
            text=(f"<b>CURE Energy Market Monitor</b><br>"
                  f"<span style='font-size:13px;color:#005BAC'>"
                  f"<b>Prof. Honggeun Jo</b> · CURE, Inha University "
                  f"— script &amp; methodology</span><br>"
                  f"<span style='font-size:12px;color:#6b7787'>"
                  f"Updated {stamp} &nbsp;·&nbsp; last {display_days} days "
                  f"&nbsp;·&nbsp; {n_ok} indicators</span>"),
            x=0.0, xanchor="left", y=0.99, yanchor="top",
            font=dict(size=19, color="#002F6C"),
        ),
    )
    # Default view: the last `display_days` plus the forecast horizon. More
    # history is loaded into the traces than this, so panning back works
    # without a reload; the archive itself goes back further still.
    if view_start is not None and view_end is not None:
        fig.update_xaxes(range=[view_start, view_end], row=1, col=1)
        _apply_view_yranges(fig, by_key, placements, forecasts, view_start)

    # After the y-ranges are pinned, so the label can sit at a known height.
    equity = _add_performance_band(fig, by_key, log)
    for k, r in equity.items():
        print(f"  long/short last {r['n']}d — {k}: "
              f"{r['stopped']*100:.1f}% with 2% stop "
              f"({r['n_stopped']} stopped), "
              f"{r['plain']*100:.1f}% without")

    _add_hero_legends(fig, rows)
    _add_outlook_header(fig, forecasts, stats)
    _add_attribution(fig)
    if n_scored:
        print("  track record plotted: " + ", ".join(
            f"{k} {v} scored call(s)" for k, v in n_scored.items()))
    return fig


def _add_attribution(fig) -> None:
    """
    Liability disclaimer under the figure. Authorship itself now sits on the
    second line of the title, so it is not repeated here.
    """
    fig.add_annotation(
        text=("<b>예측 결과에 대해 어떠한 책임도 지지 않습니다.</b> &nbsp;"
              "본 자료는 연구 참고용이며 투자 판단의 근거가 될 수 없습니다."),
        xref="paper", yref="paper", x=0.0, y=-0.045,
        xanchor="left", yanchor="top", showarrow=False,
        font=dict(size=11, color="#8a6d00"),
    )
    fig.add_annotation(
        text=("No responsibility is accepted for any forecast outcome or for "
              "any use of, or reliance on, this page. &nbsp;·&nbsp; "
              "Data: Yahoo Finance, FRED."),
        xref="paper", yref="paper", x=0.0, y=-0.068,
        xanchor="left", yanchor="top", showarrow=False,
        font=dict(size=10, color="#8b97a8"),
    )


def _add_outlook_header(fig, forecasts: dict, stats: Optional[dict] = None):
    """
    Put the one-week P10/P50/P90 outlook at the very top of the figure, in
    the header margin above the hero row.
    """
    if not forecasts:
        return
    names = {"wti": "WTI Crude ($/bbl)", "gas": "Henry Hub ($/MMBtu)"}
    fig.add_annotation(
        text="<b>ONE-WEEK OUTLOOK &nbsp;·&nbsp; P10 / P50 / P90</b>",
        xref="paper", yref="paper", x=0.0, y=1.077, xanchor="left",
        yanchor="bottom", showarrow=False,
        font=dict(size=11, color=PRIMARY),
    )
    # Wide enough apart that the two cards never crowd each other, and
    # generous internal padding so the text is not tight against the border.
    card_gap = 0.46
    for i, (key, fc) in enumerate(forecasts.items()):
        delta = (fc["p50"] / fc["spot"] - 1.0) * 100.0
        arrow = "▲" if delta >= 0 else "▼"
        dcol = "#1a7a4a" if delta >= 0 else "#c0392b"
        st = (stats or {}).get(key)
        if st and st["n"]:
            # Colour the F1 against the coin-flip a direction model must beat.
            f1col = "#1a7a4a" if st["f1"] >= 0.55 else (
                "#8a6d00" if st["f1"] >= 0.45 else "#c0392b")
            score = (f"<br><span style='font-size:10.5px;color:#6b7787'>"
                     f"direction F1 "
                     f"<b style='color:{f1col}'>{st['f1']:.2f}</b>"
                     f"&nbsp;·&nbsp;hit {st['hit_rate']*100:.0f}%"
                     f"&nbsp;·&nbsp;{st['hits']}/{st['n']} calls"
                     f"&nbsp;·&nbsp;MAE {st['mae_pct']:.2f}%</span>")
        else:
            score = ("<br><span style='font-size:10.5px;color:#9aa5b5'>"
                     "direction F1 — no scored calls yet</span>")

        txt = (
            f"<b>{names.get(key, key)}</b>&nbsp;&nbsp;"
            f"spot <b>{fc['spot']:,.2f}</b>&nbsp;&nbsp;"
            f"<span style='color:{dcol}'>{arrow} {delta:+.1f}%</span><br>"
            f"<span style='font-size:11px'>"
            f"P10 <b>{fc['p10']:,.2f}</b>&nbsp;·&nbsp;"
            f"P50 <b>{fc['p50']:,.2f}</b>&nbsp;·&nbsp;"
            f"P90 <b>{fc['p90']:,.2f}</b></span>"
            f"{score}"
        )
        fig.add_annotation(
            text=txt, xref="paper", yref="paper",
            x=card_gap * i, y=1.026, xanchor="left", yanchor="bottom",
            showarrow=False, align="left", font=dict(size=12, color="#25313f"),
            bgcolor="rgba(245,248,252,0.95)", bordercolor="#c9d6e6",
            borderwidth=1, borderpad=11,
        )


# --------------------------------------------------------------------------
# HTML assembly
# --------------------------------------------------------------------------

PAGE_CSS = """
html,body{margin:0;padding:0;background:#fff;overflow-x:hidden;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
  color:#25313f;}
.wrap{max-width:1480px;margin:0 auto;padding:14px 16px 22px;}
.wrap .plotly-graph-div{width:100%;}
@media(max-width:700px){.wrap{padding:10px 8px 16px;}}
"""

# Reports the rendered height to the embedding page, so the iframe on
# i_7_energy_stats.markdown fits exactly instead of relying on a hardcoded
# guess. Works cross-origin too, unlike reading contentDocument.
SIZE_JS = """
(function () {
  function post() {
    var h = Math.max(document.body.scrollHeight,
                     document.documentElement.scrollHeight);
    if (window.parent !== window) {
      window.parent.postMessage({ cureEnergyHeight: h }, "*");
    }
  }
  window.addEventListener("load", function () {
    post();
    setTimeout(post, 400);
    setTimeout(post, 1500);
  });
  window.addEventListener("resize", post);
})();
"""


def build_html(fig, series_list: list, forecasts: dict,
               display_days: int) -> str:
    """The page is the figure — sources and method live on the Jekyll page."""
    plot_div = fig.to_html(
        full_html=False, include_plotlyjs="cdn",
        config={"displaylogo": False, "responsive": True,
                "scrollZoom": True,
                "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CURE Energy Market Monitor</title>
<style>{PAGE_CSS}</style>
</head>
<body>
<div class="wrap">
{plot_div}
</div>
<script>{SIZE_JS}</script>
</body>
</html>
"""


def sync_page_height(md_path: str, page_height: int) -> bool:
    """
    Rewrite the iframe height in the Jekyll page to match the figure just
    rendered. The embed also self-sizes via postMessage, but the CSS value is
    what the browser uses before the frame loads — keeping it accurate is the
    difference between a clean first paint and a visible jump.
    """
    if not os.path.exists(md_path):
        print(f"  ! page not found, skipping height sync: {md_path}")
        return False
    with open(md_path, encoding="utf-8") as fh:
        src = fh.read()

    pattern = re.compile(r"(\.eng-frame-wrap iframe\{[^}]*?height:)\s*\d+px")
    new, n = pattern.subn(rf"\g<1>{page_height}px", src)
    if n == 0:
        print("  ! no iframe height rule found; page left untouched")
        return False
    if new == src:
        print(f"  = page height already {page_height}px")
        return False
    with open(md_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)
    print(f"  + synced {n} iframe height rule(s) to {page_height}px "
          f"in {os.path.basename(md_path)}")
    return True


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--display-days", type=int, default=DISPLAY_DAYS,
                    help="length of the plotted window (default 30)")
    ap.add_argument("--out", default=OUT_HTML, help="output html path")
    ap.add_argument("--no-forecast", action="store_true",
                    help="skip the model outlook")
    ap.add_argument("--retune", action="store_true",
                    help="force a hyperparameter search even if the cached "
                         "one in __datafile is still fresh")
    ap.add_argument("--plot-days", type=int, default=PLOT_DAYS,
                    help="history loaded into the figure and pannable "
                         "(default 400); the archive keeps everything")
    ap.add_argument("--no-cache", action="store_true",
                    help="ignore __datafile and refetch the full history "
                         "without writing the archive or forecast log")
    ap.add_argument("--no-sync-page", action="store_true",
                    help="do not rewrite the iframe height in "
                         "i_7_energy_stats.markdown")
    ap.add_argument("--open", action="store_true",
                    help="open the result in a browser when done")
    args = ap.parse_args(argv)

    today = dt.date.today()
    hist_start = today - dt.timedelta(days=int(365.25 * TRAIN_YEARS))
    end = today + dt.timedelta(days=1)
    window_start = pd.Timestamp(today - dt.timedelta(days=args.display_days))
    plot_start = pd.Timestamp(today - dt.timedelta(days=args.plot_days))

    print(f"CURE energy stats — {today}")
    print(f"  history {hist_start} .. {today}  "
          f"(display last {args.display_days}d)")

    cache = pd.DataFrame() if args.no_cache else load_panel_cache()
    if not cache.empty:
        print(f"  archive: {len(cache)} rows, "
              f"{cache.index.min().date()} .. {cache.index.max().date()}, "
              f"{len(cache.columns)} cols")
    else:
        print("  archive: empty — full history pull")

    registry_list = registry()
    starts = {s.key: fetch_start_for(s, cache, hist_start)
              for s in registry_list}

    print("Fetching:")
    series_list = gather(registry_list, hist_start, end, starts=starts)

    fresh = series_to_frame(series_list)
    cache = merge_cache(cache, fresh)
    if cache.empty:
        print("FATAL: no data available from archive or network.",
              file=sys.stderr)
        return 1
    if not args.no_cache:
        save_panel_cache(cache)
        print(f"  archive saved: {PANEL_CSV} "
              f"({len(cache)} rows, {len(cache.columns)} cols)")

    # Everything downstream works off the archive, not just today's delta.
    hydrate_from_cache(series_list, cache)
    mark_cadence(series_list)

    if not any(s.data is not None for s in series_list):
        print("FATAL: no series resolved; nothing to plot.", file=sys.stderr)
        return 1

    forecasts = {}
    if not args.no_forecast:
        print(f"Forecasting ({METHOD}, recursive, {LOOKBACK}d lookback "
              f"-> 1d step, x{FORECAST_HORIZON}, {N_PATHS} paths):")
        panel = daily_panel(series_list)
        for key in ("wti", "gas"):
            try:
                fc = P.forecast_target(panel, key, retune=args.retune)
            except Exception as exc:                       # noqa: BLE001
                print(f"  ! {key}: {type(exc).__name__}: {exc}")
                fc = None
            if fc:
                forecasts[key] = fc
                print(f"  + {key:4s} spot {fc['spot']:.2f} -> "
                      f"P10 {fc['p10']:.2f} / P50 {fc['p50']:.2f} / "
                      f"P90 {fc['p90']:.2f}  (n={fc['n_train']}, "
                      f"oos direction {fc['oos_direction']:.3f})")
                print(f"       drivers: " + ", ".join(
                    f"{n} {v*100:.0f}%" for n, v in fc["top_drivers"][:3]))
            else:
                print(f"  - {key:4s} no forecast")

    # Log this run's fan before drawing, so the newest call is on record even
    # if rendering later fails.
    log = load_forecast_log()
    if forecasts and not args.no_cache:
        log = record_forecasts(log, forecasts)
        save_forecast_log(log)
        print(f"  forecast log: {FORECAST_CSV} ({len(log)} rows)")

    view_end = pd.Timestamp(today) + pd.tseries.offsets.BDay(
        FORECAST_HORIZON + 1)

    print("Rendering...")
    fig = build_figure(series_list, forecasts, plot_start,
                       args.display_days, log=log,
                       view_start=window_start, view_end=view_end)
    html = build_html(fig, series_list, forecasts, args.display_days)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(html)

    size_kb = os.path.getsize(args.out) / 1024
    page_height = int(fig.layout.height) + WRAP_PAD
    print(f"Wrote {args.out}  ({size_kb:,.0f} KB, "
          f"figure {int(fig.layout.height)}px + {WRAP_PAD}px padding "
          f"= {page_height}px)")

    if not args.no_sync_page:
        sync_page_height(PAGE_MD, page_height)

    if args.open:
        import webbrowser
        webbrowser.open("file://" + os.path.abspath(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
