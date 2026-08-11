#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gather_energy_stats.py — CURE Lab energy market dashboard builder.

Pulls ~1 month of daily energy / macro indicators, renders an interactive
Plotly dashboard, and appends a Random-Forest based P10/P50/P90 outlook for
next week's WTI crude and Henry Hub natural gas prices.

Output
------
_images/energy_stats.html   (standalone, self-contained page; Plotly via CDN)

Usage
-----
    py -3.13 _script/gather_energy_stats.py
    py -3.13 _script/gather_energy_stats.py --display-days 45 --open

Notes
-----
* Every data source is fetched defensively. A source that fails is dropped
  from the dashboard and reported in the coverage table rather than raising.
* The dashboard *displays* ~1 month, but the forecast model *trains* on
  several years of history (a month of daily bars is far too little to fit a
  random forest on).
* Set EIA_API_KEY in the environment to prefer the EIA v2 API over FRED for
  the weekly inventory / utilisation series.
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

# Vertical padding the wrapper adds around the figure (see PAGE_CSS).
WRAP_PAD = 14 + 22

DISPLAY_DAYS = 90       # window actually plotted (~3 months)
TRAIN_YEARS = 4         # history pulled for model fitting
LOOKBACK = 14           # trading days of own history feeding one prediction
FORECAST_HORIZON = 5    # recursive one-day steps (~1 week)
N_PATHS = 2000          # Monte-Carlo paths for the recursive fan
RF_TREES = 500
RANDOM_STATE = 42

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
    derived: Optional[pd.Series] = field(default=None, repr=False)
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
        # Daily Dubai first; POILDUBUSDM is monthly and only a last resort.
        # `note`/dash are corrected after the fetch so the panel never claims
        # daily resolution it does not have.
        Series("dubai", "Dubai 원유 (Dubai)", "fred",
               ["DCOILDUBAI", "DPOILDUB", "POILDUBUSDD", "POILDUBUSDM"],
               kind="line", tier=1, unit="$/bbl", color="#8a6d00"),
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


def gather(series_list: list, start: dt.date, end: dt.date) -> list:
    """
    Populate `.data` / `.status` on every Series, never raising.

    Each candidate in `Series.ids` may carry an explicit "source@identifier"
    prefix; bare identifiers use the Series' default source. Candidates are
    tried in order and the first that returns rows wins, so an indicator can
    prefer the EIA API and quietly fall back to FRED.
    """
    for s in series_list:
        for ident in s.ids:
            source, sep, real_id = ident.partition("@")
            if not sep:
                source, real_id = s.source, ident
            fetcher: Callable = FETCHERS[source]
            try:
                df = fetcher(real_id, start, end)
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
                      f"[{s.label}]")
                break
        if s.data is None:
            s.status = "unavailable"
            print(f"  - {s.key:9s} unavailable")
            continue

        # Draw a series solid only if it really is daily; anything coarser is
        # dashed and says so, so a forward-filled monthly benchmark is never
        # mistaken for a daily quote.
        cadence = s.cadence_days()
        if cadence == cadence and cadence > 4:
            s.dash = "dot"
            s.note = "monthly, held" if cadence > 20 else "weekly, held"
            print(f"      {s.key}: ~{cadence:.0f}d cadence -> {s.note}")
    return series_list


def derive_daily_dubai(series_list: list) -> None:
    """
    Build a daily Dubai line when only the monthly benchmark is available.

    No free source publishes Dubai spot daily — FRED carries only the monthly
    POILDUBUSDM. Dubai does, however, trade at a slowly-moving spread to
    Brent (the Brent–Dubai EFS), so the daily path is reconstructed as

        Dubai_daily = Brent_daily + interp(monthly Dubai − monthly Brent)

    The day-to-day *shape* is therefore Brent's; only the level is Dubai's.
    It is labelled "Brent-implied" wherever it appears, the true monthly
    prints are overlaid as markers, and it is deliberately kept out of the
    forecast panel — feeding a Brent-derived series to the model would add a
    collinear predictor carrying no independent information.
    """
    by = {s.key: s for s in series_list}
    dub, brent = by.get("dubai"), by.get("brent")
    if dub is None or dub.data is None or brent is None or brent.data is None:
        return
    if not (dub.cadence_days() > 4):        # already daily — nothing to do
        return

    b = brent.data["Close"].astype(float).dropna()
    d = dub.data["Close"].astype(float).dropna()
    bm = b.resample("MS").mean()
    common = d.index.intersection(bm.index)
    if len(common) < 6:
        print("      dubai: too few overlapping months to imply a daily line")
        return

    spread = d.loc[common] - bm.loc[common]
    idx = b.index.union(spread.index)
    sp_daily = (spread.reindex(idx).interpolate("time")
                .ffill().bfill().reindex(b.index))
    dub.derived = (b + sp_daily).dropna()
    print(f"      dubai: implied daily line from Brent + spread "
          f"(last spread {spread.iloc[-1]:+.2f} $/bbl, "
          f"{len(dub.derived)} pts)")


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


def exog_features(panel: pd.DataFrame, exclude: str) -> pd.DataFrame:
    """
    Cross-market state: short/medium momentum and a level z-score for every
    series other than the forecast target. Differences (not log returns) keep
    yield and real-rate series — which can be zero or negative — well defined.

    These are held frozen through the recursion (see `simulate_paths`).
    """
    feats = {}
    for col in panel.columns:
        if col == exclude:
            continue
        s = panel[col].astype(float)
        vol = s.diff().rolling(60, min_periods=20).std().replace(0, np.nan)
        for lag in (1, 3, 5, 10):
            feats[f"{col}_d{lag}"] = s.diff(lag) / (vol * math.sqrt(lag))
        mu = s.rolling(60, min_periods=20).mean()
        sd = s.rolling(60, min_periods=20).std().replace(0, np.nan)
        feats[f"{col}_z"] = (s - mu) / sd
    out = pd.DataFrame(feats, index=panel.index)
    return out.replace([np.inf, -np.inf], np.nan)


# Own-history feature block. Two implementations must stay in lockstep: the
# pandas one builds the training matrix over all dates, the numpy one runs
# inside the recursion on simulated paths. `_assert_blocks_agree` checks them
# against each other at run time — if they ever drift, the model would be
# predicting from features it was never trained on, silently.
TARGET_FEAT_NAMES = ([f"r_lag{i}" for i in range(LOOKBACK)]
                     + ["r_sum5", "r_sum14", "lvl_z", "vol_z"])


def target_block_pandas(price: pd.Series) -> pd.DataFrame:
    """Own-history features for every date, from a price series."""
    p = price.astype(float)
    r = np.log(p).diff()
    vol = r.rolling(60, min_periods=60).std().replace(0, np.nan)
    feats = {f"r_lag{i}": r.shift(i) / vol for i in range(LOOKBACK)}
    feats["r_sum5"] = r.rolling(5).sum() / (vol * math.sqrt(5))
    feats["r_sum14"] = r.rolling(14).sum() / (vol * math.sqrt(14))
    feats["lvl_z"] = ((p - p.rolling(60, min_periods=60).mean())
                      / p.rolling(60, min_periods=60).std().replace(0, np.nan))
    feats["vol_z"] = (r.rolling(20, min_periods=20).std()
                      / r.rolling(120, min_periods=120).std()
                      .replace(0, np.nan))
    out = pd.DataFrame(feats, index=p.index)[TARGET_FEAT_NAMES]
    return out.replace([np.inf, -np.inf], np.nan)


def target_block_numpy(paths: np.ndarray) -> np.ndarray:
    """
    Same features as `target_block_pandas`, evaluated at the final column of
    each row. `paths` is (n_paths, T) of prices; returns (n_paths, n_feats).
    """
    lp = np.log(paths)
    r = np.diff(lp, axis=1)                       # (n, T-1)
    vol = r[:, -60:].std(axis=1, ddof=1)
    vol = np.where(vol == 0, np.nan, vol)[:, None]

    cols = [r[:, -1 - i][:, None] / vol for i in range(LOOKBACK)]
    cols.append(r[:, -5:].sum(axis=1)[:, None] / (vol * math.sqrt(5)))
    cols.append(r[:, -14:].sum(axis=1)[:, None] / (vol * math.sqrt(14)))

    win = paths[:, -60:]
    lvl_z = ((paths[:, -1] - win.mean(axis=1))
             / np.where(win.std(axis=1, ddof=1) == 0, np.nan,
                        win.std(axis=1, ddof=1)))
    cols.append(lvl_z[:, None])

    short = r[:, -20:].std(axis=1, ddof=1)
    long = r[:, -120:].std(axis=1, ddof=1)
    cols.append((short / np.where(long == 0, np.nan, long))[:, None])
    return np.hstack(cols)


def _assert_blocks_agree(price: pd.Series) -> None:
    """Guard against the two feature implementations drifting apart."""
    pdf = target_block_pandas(price).dropna()
    if pdf.empty:
        return
    last_date = pdf.index[-1]
    hist = price.loc[:last_date].values[None, :]
    npy = target_block_numpy(hist)[0]
    ref = pdf.iloc[-1].values
    bad = ~np.isclose(npy, ref, rtol=1e-8, atol=1e-10, equal_nan=True)
    if bad.any():
        names = np.array(TARGET_FEAT_NAMES)[bad]
        raise RuntimeError(
            "target feature implementations disagree on "
            f"{list(names)}: numpy={npy[bad]} vs pandas={ref[bad]}")


def simulate_paths(model, price: pd.Series, exog_last: np.ndarray,
                   resid: np.ndarray, horizon: int, n_paths: int,
                   seed: int = RANDOM_STATE) -> np.ndarray:
    """
    Roll the one-day model forward `horizon` times.

    Each step predicts tomorrow's log return from the trailing 14 days, adds a
    residual drawn from the model's own out-of-sample error distribution, and
    appends the resulting price so the next step sees it. Uncertainty
    therefore compounds through the horizon instead of being assumed.

    The exogenous block is held at its last observed value: the dollar, the
    curve and volatility are not themselves forecast, so the fan answers
    "where does this contract drift if the rest of the market stands still".
    """
    rng = np.random.default_rng(seed)
    hist = price.dropna().values.astype(float)
    tail = hist[-260:]                            # enough for the 120d window
    paths = np.repeat(tail[None, :], n_paths, axis=0)
    exog = np.tile(exog_last, (n_paths, 1))

    out = np.empty((n_paths, horizon))
    for h in range(horizon):
        feats = target_block_numpy(paths)
        X = np.nan_to_num(np.hstack([feats, exog]), nan=0.0,
                          posinf=0.0, neginf=0.0)
        mu = model.predict(X)
        eps = rng.choice(resid, size=n_paths, replace=True)
        nxt = paths[:, -1] * np.exp(mu + eps)
        paths = np.hstack([paths, nxt[:, None]])
        out[:, h] = nxt
    return out


def forecast_target(panel: pd.DataFrame, target: str,
                    horizon: int = FORECAST_HORIZON) -> Optional[dict]:
    """
    Fit a one-day-ahead random forest on the trailing 14 days of the target
    plus the current cross-market state, then roll it forward recursively to
    build a P10/P50/P90 fan over the horizon.
    """
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import TimeSeriesSplit

    if target not in panel.columns:
        return None

    price = panel[target].astype(float).dropna()
    if len(price) < 400:
        return None
    _assert_blocks_agree(price)

    tgt_feats = target_block_pandas(price)
    exo_feats = exog_features(panel, exclude=target).reindex(price.index)

    # One-day-ahead log return.
    y = np.log(price.shift(-1) / price)

    # Drop predictors that are still mostly empty (a series whose history
    # starts late, say) before row-wise dropna, so one sparse column cannot
    # take the whole training set with it.
    exo_ok = [c for c in exo_feats.columns
              if exo_feats[c].notna().mean() >= 0.70]
    feats = tgt_feats.join(exo_feats[exo_ok])
    data = feats.join(y.rename("__y__")).dropna()
    if len(data) < 250:
        print(f"  ! {target}: only {len(data)} usable training rows")
        return None

    X = data.drop(columns="__y__")
    yv = data["__y__"]

    # Walk-forward residuals of the one-day model. These are what the
    # recursion resamples, so the fan widens with horizon on its own.
    resid = []
    for tr, te in TimeSeriesSplit(n_splits=5).split(X):
        m = RandomForestRegressor(
            n_estimators=200, min_samples_leaf=5, max_features="sqrt",
            random_state=RANDOM_STATE, n_jobs=-1)
        m.fit(X.iloc[tr], yv.iloc[tr])
        resid.append(yv.iloc[te].values - m.predict(X.iloc[te]))
    resid = np.concatenate(resid)

    model = RandomForestRegressor(
        n_estimators=RF_TREES, min_samples_leaf=5, max_features="sqrt",
        random_state=RANDOM_STATE, n_jobs=-1)
    model.fit(X, yv)

    exog_last = (exo_feats[exo_ok].reindex(columns=X.columns[len(
        TARGET_FEAT_NAMES):]).ffill().iloc[-1].fillna(0.0).values)

    sims = simulate_paths(model, price, exog_last, resid, horizon, N_PATHS)
    q10, q50, q90 = np.percentile(sims, [10, 50, 90], axis=0)

    spot = float(price.iloc[-1])
    imp = pd.Series(model.feature_importances_, index=X.columns)
    by_series = {}
    for name, val in imp.items():
        base = "own history" if name in TARGET_FEAT_NAMES \
            else name.rsplit("_", 1)[0]
        by_series[base] = by_series.get(base, 0.0) + float(val)
    top = sorted(by_series.items(), key=lambda kv: -kv[1])[:5]

    return {
        "spot": spot,
        "p10": float(q10[-1]), "p50": float(q50[-1]), "p90": float(q90[-1]),
        "path_p10": q10.tolist(),
        "path_p50": q50.tolist(),
        "path_p90": q90.tolist(),
        "n_train": int(len(data)),
        "resid_sd": float(np.std(resid)),
        "top_drivers": top,
        "asof": price.index[-1],
    }


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
    titles = ["원유 가격 · Crude Oil (WTI candles · Brent / Dubai lines)",
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


def _hero(fig, go, s, name, row, col, clip, up="#c0392b", down="#1a6dcc"):
    """Draw one hero contract as candles, falling back to a line."""
    d = clip(s.data)
    if d.empty:
        return
    if {"Open", "High", "Low", "Close"} <= set(d.columns):
        fig.add_trace(go.Candlestick(
            x=d.index, open=d["Open"], high=d["High"], low=d["Low"],
            close=d["Close"], name=name, whiskerwidth=0.4,
            increasing_line_color=up, decreasing_line_color=down,
            showlegend=False,
        ), row=row, col=col)
    else:
        fig.add_trace(go.Scatter(
            x=d.index, y=d["Close"], name=name, showlegend=False,
            line=dict(color=s.color, width=2),
        ), row=row, col=col)


def build_figure(series_list: list, forecasts: dict, window_start,
                 display_days: int):
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

    # ---------------- row 1, col 1 : crude oil ----------------
    wti = by_key.get("wti")
    if wti and wti.data is not None:
        _hero(fig, go, wti, "WTI", 1, 1, clip)

    for key in ("brent", "dubai"):
        s = by_key.get(key)
        if s is None or s.data is None:
            continue

        if s.derived is not None:
            # Daily reconstruction as the main line, true prints as markers.
            dd = s.derived[s.derived.index >= window_start]
            if not dd.empty:
                fig.add_trace(go.Scatter(
                    x=dd.index, y=dd.values, name="Dubai (Brent-implied)",
                    opacity=0.9, line=dict(color=s.color, width=1.8),
                    hovertemplate="<b>Dubai</b> %{y:,.2f} "
                                  "<i>Brent-implied</i><extra></extra>",
                ), row=1, col=1)
            raw = clip(s.data)
            if not raw.empty:
                fig.add_trace(go.Scatter(
                    x=raw.index, y=raw["Close"], mode="markers",
                    name="Dubai (monthly actual)",
                    marker=dict(color=s.color, size=7, symbol="circle-open",
                                line=dict(width=2)),
                    hovertemplate="<b>Dubai</b> %{y:,.2f} "
                                  "<i>monthly actual</i><extra></extra>",
                ), row=1, col=1)
            continue

        d = clip(s.data)
        if d.empty:
            continue
        label = key.title() + (f" ({s.note})" if s.note else "")
        fig.add_trace(go.Scatter(
            x=d.index, y=d["Close"], name=label, opacity=0.9,
            line=dict(color=s.color, width=1.8, dash=s.dash),
            hovertemplate=f"<b>{label}</b> %{{y:,.2f}}<extra></extra>",
        ), row=1, col=1)

    # ---------------- row 2 : natural gas ----------------
    gas = by_key.get("gas")
    if gas and gas.data is not None:
        _hero(fig, go, gas, "Henry Hub", 2, 1, clip)

    # ---------------- forecast fans on the hero panels ----------------
    for key, hero_row in (("wti", 1), ("gas", 2)):
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
            name="P10–P90", showlegend=False,
        ), row=hero_row, col=1)
        fig.add_trace(go.Scatter(
            x=xs, y=mid, mode="lines+markers",
            line=dict(color="#5b3cc4", width=2, dash="dash"),
            marker=dict(size=5, symbol="diamond"), name="P50",
            showlegend=False,
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
        hovermode="x unified", showlegend=False,
        dragmode="pan",
        title=dict(
            text=(f"<b>CURE Energy Market Monitor</b><br>"
                  f"<span style='font-size:13px;color:#005BAC'>"
                  f"<b>Prof. Honggeun Jo</b> · CURE, Inha University "
                  f"— script &amp; methodology</span><br>"
                  f"<span style='font-size:12px;color:#6b7787'>"
                  f"Updated {stamp} &nbsp;·&nbsp; last {display_days} days "
                  f"&nbsp;·&nbsp; {n_ok} indicators &nbsp;·&nbsp; "
                  f"all panels share one time axis — pan or zoom any chart "
                  f"and the rest follow</span>"),
            x=0.0, xanchor="left", y=0.99, yanchor="top",
            font=dict(size=19, color="#002F6C"),
        ),
    )
    _add_outlook_header(fig, forecasts)
    _add_attribution(fig)
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


def _add_outlook_header(fig, forecasts: dict):
    """
    Put the one-week P10/P50/P90 outlook at the very top of the figure, in
    the header margin above the hero row.
    """
    if not forecasts:
        return
    names = {"wti": "WTI Crude ($/bbl)", "gas": "Henry Hub ($/MMBtu)"}
    fig.add_annotation(
        text="<b>ONE-WEEK OUTLOOK &nbsp;·&nbsp; P10 / P50 / P90</b>",
        xref="paper", yref="paper", x=0.0, y=1.118, xanchor="left",
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
        txt = (
            f"<b>{names.get(key, key)}</b>&nbsp;&nbsp;"
            f"spot <b>{fc['spot']:,.2f}</b>&nbsp;&nbsp;"
            f"<span style='color:{dcol}'>{arrow} {delta:+.1f}%</span><br>"
            f"<span style='font-size:11px'>"
            f"P10 <b>{fc['p10']:,.2f}</b>&nbsp;·&nbsp;"
            f"P50 <b>{fc['p50']:,.2f}</b>&nbsp;·&nbsp;"
            f"P90 <b>{fc['p90']:,.2f}</b></span>"
        )
        fig.add_annotation(
            text=txt, xref="paper", yref="paper",
            x=card_gap * i, y=1.052, xanchor="left", yanchor="bottom",
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
                    help="skip the random-forest outlook")
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

    print(f"CURE energy stats — {today}")
    print(f"  history {hist_start} .. {today}  "
          f"(display last {args.display_days}d)")
    print("Fetching:")
    series_list = gather(registry(), hist_start, end)

    if not any(s.data is not None for s in series_list):
        print("FATAL: no data source resolved; nothing to plot.",
              file=sys.stderr)
        return 1

    derive_daily_dubai(series_list)

    forecasts = {}
    if not args.no_forecast:
        print(f"Forecasting (recursive, {LOOKBACK}d lookback -> 1d step, "
              f"x{FORECAST_HORIZON}, {N_PATHS} paths):")
        panel = daily_panel(series_list)
        for key in ("wti", "gas"):
            try:
                fc = forecast_target(panel, key)
            except Exception as exc:                       # noqa: BLE001
                print(f"  ! {key}: {type(exc).__name__}: {exc}")
                fc = None
            if fc:
                forecasts[key] = fc
                print(f"  + {key:4s} spot {fc['spot']:.2f} -> "
                      f"P10 {fc['p10']:.2f} / P50 {fc['p50']:.2f} / "
                      f"P90 {fc['p90']:.2f}  (n={fc['n_train']})")
                print(f"       drivers: " + ", ".join(
                    f"{n} {v*100:.0f}%" for n, v in fc["top_drivers"][:3]))
            else:
                print(f"  - {key:4s} no forecast")

    print("Rendering...")
    fig = build_figure(series_list, forecasts, window_start,
                       args.display_days)
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
