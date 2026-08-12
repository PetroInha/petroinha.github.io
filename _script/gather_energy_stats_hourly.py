#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gather_energy_stats_hourly.py — hourly CURE energy dashboard.

The hourly counterpart of `gather_energy_stats.py`. Pulls hourly bars,
broadcasts the daily-only macro series onto the same grid, renders a
line-chart dashboard (no candles) and records a recursive 24-hour outlook.

Timezone
--------
Every series is carried in UTC internally — Yahoo already returns intraday
bars tz-aware in UTC, and the daily FRED series are pinned to UTC midnight
before broadcasting. The figure is drawn on a KST axis, because the trading
clock this feeds is KST.

Daily series are shifted forward one day before being broadcast: a figure
published for date D is not knowable during D, and without the shift every
hour of D would be trained on information from its own close.

Output
------
_images/energy_stats_hourly.html      not embedded in any page; pushed only
__datafile/energy_panel_hourly.csv    hourly archive
__datafile/forecast_log_hourly.csv    every hourly forecast, for scoring

Usage
-----
    py -3.13 _script/gather_energy_stats_hourly.py
    py -3.13 _script/gather_energy_stats_hourly.py --display-days 3 --open
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import os
import sys
import warnings
from typing import Optional

import numpy as np
import pandas as pd
import requests

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import energy_predictor_hourly as PH                         # noqa: E402

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                        # noqa: BLE001
        pass

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_HTML = os.path.join(ROOT, "_images", "energy_stats_hourly.html")
DATA_DIR = os.path.join(ROOT, "__datafile")
PANEL_CSV = os.path.join(DATA_DIR, "energy_panel_hourly.csv")
FORECAST_CSV = os.path.join(DATA_DIR, "forecast_log_hourly.csv")
TRADES_CSV = os.path.join(DATA_DIR, "backtest_trades_hourly.csv")

# Overnight trade shading: blue when the model went long, red when short.
LONG_FILL = "rgba(0,91,172,0.10)"
SHORT_FILL = "rgba(214,48,49,0.10)"

DISPLAY_DAYS = 7          # hourly window actually plotted
PLOT_DAYS = 30            # history handed to the figure (pannable)
HISTORY_PERIOD = "730d"   # Yahoo's ceiling for 1h bars
DAILY_LOOKBACK_DAYS = 900

KST = dt.timezone(dt.timedelta(hours=9))
PRIMARY = "#005BAC"
ACCENT = "#c0392b"
GRID = "#eef2f7"
UA = {"User-Agent": "Mozilla/5.0 (compatible; CURE-EnergyStats/1.0)"}

# key -> (yahoo ticker, label, colour, is_hero)
HOURLY_SERIES = [
    ("wti",   "CL=F",     "WTI ($/bbl)",        ACCENT,     True),
    ("brent", "BZ=F",     "Brent ($/bbl)",      "#1a7a4a",  False),
    ("gas",   "NG=F",     "Henry Hub ($/MMBtu)", PRIMARY,   True),
    ("rbob",  "RB=F",     "RBOB ($/gal)",       "#5b3cc4",  False),
    ("dxy",   "DX-Y.NYB", "DXY",                "#e8a33d",  False),
    ("sp500", "^GSPC",    "S&P 500",            PRIMARY,    False),
    ("xle",   "XLE",      "XLE ($)",            "#1a7a4a",  False),
    ("ovx",   "^OVX",     "OVX",                ACCENT,     False),
    ("eua",   "KRBN",     "Carbon (KRBN)",      "#1a7a4a",  False),
]

# Daily-only macro series, broadcast onto the hourly grid.
DAILY_SERIES = [
    ("ust2",     "DGS2",     "UST 2Y (%)",       "#7fb2e5"),
    ("ust10",    "DGS10",    "UST 10Y (%)",      PRIMARY),
    ("ust30",    "DGS30",    "UST 30Y (%)",      "#002F6C"),
    ("tips10",   "DFII10",   "TIPS 10Y (%)",     "#c0392b"),
    ("twdollar", "DTWEXBGS", "Broad TW USD",     "#8a6d00"),
]

HERO = ["wti", "gas"]


# --------------------------------------------------------------------------
# Fetching
# --------------------------------------------------------------------------

def fetch_hourly(ticker: str, period: str = HISTORY_PERIOD):
    """Hourly OHLC from Yahoo. The index comes back tz-aware in UTC."""
    import yfinance as yf
    df = yf.download(ticker, period=period, interval="1h", progress=False,
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
    idx = pd.DatetimeIndex(out.index)
    out.index = (idx.tz_localize("UTC") if idx.tz is None
                 else idx.tz_convert("UTC"))
    return out[~out.index.duplicated(keep="last")].sort_index().dropna(
        how="all")


def fetch_fred_daily(series_id: str, start: dt.date):
    """Daily FRED series, pinned to UTC midnight."""
    url = ("https://fred.stlouisfed.org/graph/fredgraph.csv"
           f"?id={series_id}&cosd={start:%Y-%m-%d}")
    r = requests.get(url, timeout=30, headers=UA)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    if df.shape[1] < 2:
        return None
    dcol, vcol = df.columns[0], df.columns[1]
    df[dcol] = pd.to_datetime(df[dcol], errors="coerce")
    df[vcol] = pd.to_numeric(df[vcol].replace(".", np.nan), errors="coerce")
    df = df.dropna(subset=[dcol, vcol])
    if df.empty:
        return None
    s = df.set_index(dcol)[vcol]
    s.index = s.index.normalize().tz_localize("UTC")
    return s.sort_index()


def gather_hourly() -> pd.DataFrame:
    """
    Build the wide hourly frame: native hourly series, then the daily ones
    broadcast across it.
    """
    frames, meta = [], []
    for key, ticker, label, colour, hero in HOURLY_SERIES:
        try:
            df = fetch_hourly(ticker)
        except Exception as exc:                             # noqa: BLE001
            print(f"  ! {key:9s} {type(exc).__name__}: "
                  f"{str(exc).splitlines()[0][:80]}")
            continue
        if df is None or df.empty:
            print(f"  - {key:9s} unavailable")
            continue
        cols = (["Open", "High", "Low", "Close"] if key in HERO
                else ["Close"])
        cols = [c for c in cols if c in df.columns]
        sub = df[cols].copy()
        sub.columns = [f"{key}_{c}" for c in cols]
        frames.append(sub)
        span = (df.index.max() - df.index.min()).days
        print(f"  + {key:9s} {len(df):>6d} bars over {span}d "
              f"({df.index.min():%Y-%m-%d} .. {df.index.max():%Y-%m-%d} UTC)")
        meta.append(key)

    if not frames:
        return pd.DataFrame()

    panel = pd.concat(frames, axis=1).sort_index()
    panel = panel[~panel.index.duplicated(keep="last")]

    # Broadcast the daily macro series across the hourly grid, shifted one
    # day so no hour sees a figure published at its own day's close.
    start = (panel.index.min() - pd.Timedelta(days=DAILY_LOOKBACK_DAYS)).date()
    for key, sid, label, colour in DAILY_SERIES:
        try:
            s = fetch_fred_daily(sid, start)
        except Exception as exc:                             # noqa: BLE001
            print(f"  ! {key:9s} {type(exc).__name__}")
            continue
        if s is None or s.empty:
            print(f"  - {key:9s} unavailable")
            continue
        shifted = s.copy()
        shifted.index = shifted.index + pd.Timedelta(days=1)
        panel[f"{key}_Close"] = shifted.reindex(
            panel.index.union(shifted.index)).ffill().reindex(panel.index)
        print(f"  + {key:9s} {len(s):>6d} daily obs -> broadcast (+1d lag)")

    return panel


# --------------------------------------------------------------------------
# Archive
# --------------------------------------------------------------------------

def load_hourly_cache() -> pd.DataFrame:
    if not os.path.exists(PANEL_CSV):
        return pd.DataFrame()
    try:
        df = pd.read_csv(PANEL_CSV, index_col=0)
        idx = pd.to_datetime(df.index, utc=True)
        df.index = idx
        return df[~df.index.duplicated(keep="last")].sort_index()
    except Exception as exc:                                 # noqa: BLE001
        print(f"  ! hourly cache unreadable ({type(exc).__name__})")
        return pd.DataFrame()


def save_hourly_cache(df: pd.DataFrame) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    out = df.sort_index().copy()
    out.index = out.index.tz_convert("UTC")
    out.to_csv(PANEL_CSV, index_label="timestamp_utc", float_format="%.6g")


def merge_cache(old: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    if old.empty:
        return new
    if new.empty:
        return old
    merged = new.combine_first(old)
    return merged[~merged.index.duplicated(keep="last")].sort_index()


def panel_from_cache(cache: pd.DataFrame) -> pd.DataFrame:
    """Close-only panel for the model, forward-filled onto the hourly grid."""
    cols = {c[:-6]: c for c in cache.columns if c.endswith("_Close")}
    if not cols:
        return pd.DataFrame()
    panel = cache[list(cols.values())].copy()
    panel.columns = list(cols.keys())
    panel = panel.apply(pd.to_numeric, errors="coerce")
    return panel.ffill().dropna(how="all")


# --------------------------------------------------------------------------
# Forecast log
# --------------------------------------------------------------------------

FORECAST_COLS = ["run_ts", "target", "step", "horizon_ts",
                 "p10", "p50", "p90", "spot", "source"]


def load_forecast_log() -> pd.DataFrame:
    if not os.path.exists(FORECAST_CSV):
        return pd.DataFrame(columns=FORECAST_COLS)
    try:
        df = pd.read_csv(FORECAST_CSV)
        for c in ("run_ts", "horizon_ts"):
            df[c] = pd.to_datetime(df[c], utc=True)
        for c in FORECAST_COLS:
            if c not in df.columns:
                df[c] = np.nan
        return df
    except Exception as exc:                                 # noqa: BLE001
        print(f"  ! hourly forecast log unreadable ({type(exc).__name__})")
        return pd.DataFrame(columns=FORECAST_COLS)


def record_forecasts(log: pd.DataFrame, forecasts: dict,
                     source: str = "live") -> pd.DataFrame:
    rows = []
    for key, fc in forecasts.items():
        t0 = pd.Timestamp(fc["asof"]).tz_convert("UTC")
        for i, (p10, p50, p90) in enumerate(
                zip(fc["path_p10"], fc["path_p50"], fc["path_p90"]), start=1):
            rows.append({
                "run_ts": t0, "target": key, "step": i,
                "horizon_ts": t0 + pd.Timedelta(hours=i),
                "p10": p10, "p50": p50, "p90": p90,
                "spot": fc["spot"], "source": source,
            })
    if not rows:
        return log
    combined = pd.concat([log, pd.DataFrame(rows)], ignore_index=True)
    combined = combined.drop_duplicates(subset=["run_ts", "target", "step"],
                                        keep="last")
    return combined.sort_values(["target", "run_ts", "step"])


def save_forecast_log(log: pd.DataFrame) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    out = log.copy()
    for c in ("run_ts", "horizon_ts"):
        out[c] = pd.to_datetime(out[c], utc=True).dt.strftime(
            "%Y-%m-%dT%H:%M:%S%z")
    if "source" not in out.columns:
        out["source"] = "live"
    out["source"] = out["source"].fillna("live")
    out[FORECAST_COLS].to_csv(FORECAST_CSV, index=False, float_format="%.6g")


# --------------------------------------------------------------------------
# Figure — lines only, no candles
# --------------------------------------------------------------------------

def build_figure(cache: pd.DataFrame, panel: pd.DataFrame, forecasts: dict,
                 plot_start, view_start, view_end, log=None,
                 trades: Optional[pd.DataFrame] = None):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    labels = {k: (lab, col) for k, _, lab, col, _ in HOURLY_SERIES}
    labels.update({k: (lab, col) for k, _, lab, col in DAILY_SERIES})

    context = [
        ("Brent & RBOB", ["brent", "rbob"]),
        ("Dollar & volatility · DXY / OVX", ["dxy", "ovx"]),
        ("Equities · S&P 500 / XLE", ["sp500", "xle"]),
        ("US Treasury curve (%)", ["ust2", "ust10", "ust30", "tips10"]),
        ("Broad TW USD", ["twdollar"]),
        ("Carbon (KRBN)", ["eua"]),
    ]
    context = [(t, [k for k in ks if k in panel.columns]) for t, ks in context]
    context = [(t, ks) for t, ks in context if ks]

    n_ctx_rows = (len(context) + 2) // 3
    full = [{"colspan": 6}] + [None] * 5
    specs = [list(full), list(full)]
    titles = ["원유 · WTI Crude (hourly)", "천연가스 · Henry Hub (hourly)"]
    placements = []
    idx = 0
    for _ in range(n_ctx_rows):
        row = [None] * 6
        for slot in range(3):
            col = slot * 2 + 1
            if idx < len(context):
                row[col - 1] = {"colspan": 2}
                titles.append(context[idx][0])
                placements.append((context[idx][1], len(specs) + 1, col))
                idx += 1
            else:
                row[col - 1] = {"colspan": 2}
                titles.append("")
        specs.append(row)

    px = [340, 300] + [230] * n_ctx_rows
    rows_px = sum(px)
    heights = [h / rows_px for h in px]
    vspace = 0.05

    fig = make_subplots(rows=len(specs), cols=6, specs=specs,
                        subplot_titles=titles, row_heights=heights,
                        vertical_spacing=vspace, horizontal_spacing=0.055)

    def to_kst(index):
        return index.tz_convert(KST)

    def clip(s):
        return s[s.index >= plot_start].dropna()

    # ---- hero rows: line, not candle (as specified) ----
    for key, row in (("wti", 1), ("gas", 2)):
        if key not in panel.columns:
            continue
        s = clip(panel[key])
        if s.empty:
            continue
        lab, col = labels.get(key, (key, PRIMARY))
        fig.add_trace(go.Scatter(
            x=to_kst(s.index), y=s.values, name=lab, mode="lines",
            line=dict(color=col, width=1.9), legend=f"legend{row}",
            showlegend=True,
            hovertemplate="%{x|%m-%d %H:%M} KST<br>"
                          f"<b>{lab}</b> %{{y:,.3f}}<extra></extra>",
        ), row=row, col=1)

        fc = forecasts.get(key)
        if fc:
            t0 = pd.Timestamp(fc["asof"]).tz_convert("UTC")
            steps = [t0 + pd.Timedelta(hours=i + 1)
                     for i in range(len(fc["path_p50"]))]
            xs = to_kst(pd.DatetimeIndex([t0] + steps))
            up = [fc["spot"]] + fc["path_p90"]
            dn = [fc["spot"]] + fc["path_p10"]
            mid = [fc["spot"]] + fc["path_p50"]
            fig.add_trace(go.Scatter(
                x=list(xs) + list(xs)[::-1], y=up + dn[::-1], fill="toself",
                mode="lines", line=dict(width=0),
                fillcolor="rgba(91,60,196,0.15)", hoverinfo="skip",
                name="24h P10–P90", legend=f"legend{row}", showlegend=True,
            ), row=row, col=1)
            fig.add_trace(go.Scatter(
                x=xs, y=mid, mode="lines",
                line=dict(color="#5b3cc4", width=2, dash="dash"),
                name="24h P50", legend=f"legend{row}", showlegend=True,
                hovertemplate="P50 %{y:,.3f}<extra></extra>",
            ), row=row, col=1)

    # ---- context panels ----
    for keys, row, col in placements:
        for key in keys:
            s = clip(panel[key])
            if s.empty:
                continue
            lab, colour = labels.get(key, (key, PRIMARY))
            fig.add_trace(go.Scatter(
                x=to_kst(s.index), y=s.values, name=lab, mode="lines",
                line=dict(color=colour, width=1.6), showlegend=False,
                hovertemplate=f"<b>{lab}</b> %{{y:,.3f}}<extra></extra>",
            ), row=row, col=col)
        key_txt = "  ".join(
            f"<span style='color:{labels.get(k,(k,PRIMARY))[1]}'>&#9632; "
            f"{labels.get(k,(k,PRIMARY))[0]}</span>" for k in keys)
        fig.add_annotation(text=key_txt, row=row, col=col,
                           xref="x domain", yref="y domain", x=0.01, y=0.99,
                           xanchor="left", yanchor="top", showarrow=False,
                           font=dict(size=9), bgcolor="rgba(255,255,255,0.72)",
                           borderpad=2)

    for i, t in enumerate(fig.layout.annotations[:len(titles)]):
        t.font.size = 14 if i < 2 else 11
        t.font.color = "#12395e" if i < 2 else "#44546a"

    fig.update_xaxes(showgrid=True, gridcolor=GRID, matches="x",
                     showspikes=True, spikemode="across", spikethickness=1,
                     spikecolor="#8b97a8", spikedash="dot")
    fig.layout.xaxis.matches = None
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False,
                     tickfont=dict(size=9.5))
    fig.update_xaxes(range=[view_start.tz_convert(KST),
                            view_end.tz_convert(KST)], row=1, col=1)

    # Fill the width make_subplots leaves unused on spanned columns.
    xa = [k for k in fig.layout if k.startswith("xaxis")]
    right = max(fig.layout[k].domain[1] for k in xa)
    if right < 0.999:
        for k in xa:
            d0, d1 = fig.layout[k].domain
            fig.layout[k].domain = (d0 / right, min(d1 / right, 1.0))

    _apply_view_yranges(fig, panel, placements, forecasts, view_start)
    # After the y-ranges are pinned, so band labels sit at a known height.
    equity = _add_trade_bands(fig, trades if trades is not None
                              else pd.DataFrame(), panel, view_start, to_kst)
    for k, r in equity.items():
        print(f"  overnight backtest — {k}: {r['equity']*100:.2f}% "
              f"over {r['n']} trades ({r['wins']} up)")
    _add_hero_legends(fig)

    stamp = dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    margin_t, margin_b = 165, 84
    usable = max(1.0 - (len(specs) - 1) * vspace, 0.35)
    fig.update_layout(
        height=int(round(rows_px / usable)) + margin_t + margin_b,
        margin=dict(l=58, r=48, t=margin_t, b=margin_b),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="-apple-system,BlinkMacSystemFont,Segoe UI,"
                         "Helvetica,Arial,sans-serif", size=11.5,
                  color="#25313f"),
        hovermode="x unified", dragmode="pan",
        title=dict(
            text=("<b>CURE Energy Market Monitor — hourly</b><br>"
                  "<span style='font-size:13px;color:#005BAC'>"
                  "<b>Prof. Honggeun Jo</b> · CURE, Inha University "
                  "— script &amp; methodology</span><br>"
                  f"<span style='font-size:12px;color:#6b7787'>Updated "
                  f"{stamp} &nbsp;·&nbsp; last {DISPLAY_DAYS} days hourly "
                  f"&nbsp;·&nbsp; all times KST (UTC+9)</span>"),
            x=0.0, xanchor="left", y=0.99, yanchor="top",
            font=dict(size=19, color="#002F6C")),
    )
    _add_outlook_header(fig, forecasts)
    fig.add_annotation(
        text=("<b>예측 결과에 대해 어떠한 책임도 지지 않습니다.</b> &nbsp;"
              "No responsibility is accepted for any forecast outcome."),
        xref="paper", yref="paper", x=0.0, y=-0.055, xanchor="left",
        yanchor="top", showarrow=False,
        font=dict(size=10.5, color="#8a6d00"))
    return fig


def load_trades() -> pd.DataFrame:
    """Backtested overnight trades, if run_backtest_hourly.py has produced any."""
    if not os.path.exists(TRADES_CSV):
        return pd.DataFrame()
    try:
        df = pd.read_csv(TRADES_CSV)
        for c in ("entry_ts", "exit_ts"):
            df[c] = pd.to_datetime(df[c], utc=True)
        return df.sort_values("entry_ts")
    except Exception as exc:                                 # noqa: BLE001
        print(f"  ! trades file unreadable ({type(exc).__name__})")
        return pd.DataFrame()


def _add_trade_bands(fig, trades: pd.DataFrame, panel: pd.DataFrame,
                     view_start, to_kst) -> dict:
    """
    Shade each backtested overnight hold on its contract's panel.

    Blue where the model went long, red where it went short, spanning exactly
    the position: 15:00 KST entry to the 09:00 KST unwind. The realised return
    is printed in the band, so a red block showing +2% reads immediately as a
    short that worked.
    """
    out = {}
    if trades.empty:
        return out
    for key, row, yname in (("wti", 1, "yaxis"), ("gas", 2, "yaxis2")):
        grp = trades[trades["target"] == key]
        grp = grp[grp["exit_ts"] >= view_start]
        if grp.empty or key not in panel.columns:
            continue
        try:
            lo, hi = fig.layout[yname].range
        except Exception:                                    # noqa: BLE001
            continue
        if lo is None or hi is None:
            continue

        for _, tr in grp.iterrows():
            long_side = str(tr["side"]).lower() == "long"
            fig.add_vrect(
                x0=to_kst(pd.DatetimeIndex([tr["entry_ts"]]))[0],
                x1=to_kst(pd.DatetimeIndex([tr["exit_ts"]]))[0],
                row=row, col=1, layer="below", line_width=0,
                fillcolor=LONG_FILL if long_side else SHORT_FILL)

            ret = float(tr["ret"]) * 100.0
            colour = "#1a7a4a" if ret >= 0 else "#c0392b"
            mid = tr["entry_ts"] + (tr["exit_ts"] - tr["entry_ts"]) / 2
            fig.add_annotation(
                x=to_kst(pd.DatetimeIndex([mid]))[0],
                y=lo + 0.93 * (hi - lo), row=row, col=1,
                showarrow=False, align="center",
                text=(f"<b>{'L' if long_side else 'S'}</b> "
                      f"<b style='color:{colour}'>{ret:+.2f}%</b>"),
                font=dict(size=10,
                          color=PRIMARY if long_side else "#c0392b"),
                bgcolor="rgba(255,255,255,0.78)", borderpad=2)

        eq = float(np.prod(1.0 + grp["ret"].values))
        out[key] = {"n": len(grp), "equity": eq,
                    "wins": int((grp["ret"] > 0).sum())}
        fig.add_annotation(
            x=to_kst(pd.DatetimeIndex([grp["entry_ts"].min()]))[0],
            y=lo + 0.06 * (hi - lo), row=row, col=1,
            xanchor="left", showarrow=False, align="left",
            text=(f"<b style='color:#c0392b'>{eq * 100:,.1f}%</b> "
                  f"<span style='font-size:9.5px;color:#8a5a55'>"
                  f"overnight 15:00→09:00 KST · {len(grp)} trades · "
                  f"{out[key]['wins']} up · no stop (market shut)</span>"),
            font=dict(size=13), bgcolor="rgba(255,255,255,0.80)",
            bordercolor="#e3c9c9", borderwidth=1, borderpad=4)
    return out


def _y_range(chunks, pad=0.07):
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


def _apply_view_yranges(fig, panel, placements, forecasts, view_start):
    """Scale each panel to the opening view, not to all loaded history."""
    for key, row in (("wti", 1), ("gas", 2)):
        if key not in panel.columns:
            continue
        s = panel[key]
        chunks = [s[s.index >= view_start].dropna().values]
        fc = forecasts.get(key)
        if fc:
            chunks += [fc["path_p10"], fc["path_p90"], [fc["spot"]]]
        rng = _y_range(chunks)
        if rng:
            fig.update_yaxes(range=rng, row=row, col=1)

    for keys, row, col in placements:
        chunks = []
        for key in keys:
            s = panel[key]
            chunks.append(s[s.index >= view_start].dropna().values)
        rng = _y_range(chunks)
        if rng:
            fig.update_yaxes(range=rng, row=row, col=col)


def _add_hero_legends(fig):
    try:
        r1 = tuple(fig.get_subplot(1, 1).yaxis.domain)
        r2 = tuple(fig.get_subplot(2, 1).yaxis.domain)
    except Exception:                                        # noqa: BLE001
        r1, r2 = (0.78, 1.0), (0.55, 0.75)
    common = dict(xanchor="left", yanchor="top", x=0.006, orientation="v",
                  bgcolor="rgba(255,255,255,0.88)", bordercolor="#c9d6e6",
                  borderwidth=1, font=dict(size=10), itemsizing="constant")
    fig.update_layout(
        showlegend=True,
        legend1=dict(title=dict(text="<b>Crude oil</b>",
                                font=dict(size=10, color=PRIMARY)),
                     y=r1[1] - 0.004, **common),
        legend2=dict(title=dict(text="<b>Natural gas</b>",
                                font=dict(size=10, color=PRIMARY)),
                     y=r2[1] - 0.004, **common))


def _add_outlook_header(fig, forecasts: dict):
    if not forecasts:
        return
    names = {"wti": "WTI Crude ($/bbl)", "gas": "Henry Hub ($/MMBtu)"}
    fig.add_annotation(
        text="<b>NEXT 24 HOURS &nbsp;·&nbsp; P10 / P50 / P90</b>",
        xref="paper", yref="paper", x=0.0, y=1.075, xanchor="left",
        yanchor="bottom", showarrow=False, font=dict(size=11, color=PRIMARY))
    for i, (key, fc) in enumerate(forecasts.items()):
        delta = (fc["p50"] / fc["spot"] - 1.0) * 100.0
        arrow = "▲" if delta >= 0 else "▼"
        dcol = "#1a7a4a" if delta >= 0 else "#c0392b"
        fig.add_annotation(
            text=(f"<b>{names.get(key, key)}</b>&nbsp;&nbsp;"
                  f"spot <b>{fc['spot']:,.3f}</b>&nbsp;&nbsp;"
                  f"<span style='color:{dcol}'>{arrow} {delta:+.2f}%</span>"
                  f"<br><span style='font-size:11px'>"
                  f"+24h &nbsp;P10 <b>{fc['p10']:,.3f}</b>&nbsp;·&nbsp;"
                  f"P50 <b>{fc['p50']:,.3f}</b>&nbsp;·&nbsp;"
                  f"P90 <b>{fc['p90']:,.3f}</b></span>"),
            xref="paper", yref="paper", x=0.46 * i, y=1.048,
            xanchor="left", yanchor="bottom", showarrow=False, align="left",
            font=dict(size=12, color="#25313f"),
            bgcolor="rgba(245,248,252,0.95)", bordercolor="#c9d6e6",
            borderwidth=1, borderpad=10)


PAGE_CSS = """
html,body{margin:0;padding:0;background:#fff;overflow-x:hidden;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
  color:#25313f;}
.wrap{max-width:1480px;margin:0 auto;padding:14px 16px 22px;}
.wrap .plotly-graph-div{width:100%;}
"""


def build_html(fig) -> str:
    div = fig.to_html(full_html=False, include_plotlyjs="cdn",
                      config={"displaylogo": False, "responsive": True,
                              "scrollZoom": True,
                              "modeBarButtonsToRemove": ["lasso2d",
                                                         "select2d"]})
    return (f'<!doctype html>\n<html lang="en">\n<head>\n'
            f'<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width,'
            f'initial-scale=1">\n<title>CURE Energy Monitor — hourly</title>\n'
            f"<style>{PAGE_CSS}</style>\n</head>\n<body>\n"
            f'<div class="wrap">\n{div}\n</div>\n</body>\n</html>\n')


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--display-days", type=int, default=DISPLAY_DAYS)
    ap.add_argument("--plot-days", type=int, default=PLOT_DAYS)
    ap.add_argument("--out", default=OUT_HTML)
    ap.add_argument("--no-forecast", action="store_true")
    ap.add_argument("--retune", action="store_true")
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args(argv)

    now = pd.Timestamp.now(tz="UTC")
    print(f"CURE energy stats (hourly) — {now:%Y-%m-%d %H:%M} UTC "
          f"/ {now.tz_convert(KST):%H:%M} KST")

    cache = pd.DataFrame() if args.no_cache else load_hourly_cache()
    if not cache.empty:
        print(f"  archive: {len(cache)} rows, {cache.index.min()} .. "
              f"{cache.index.max()}")

    print("Fetching hourly:")
    fresh = gather_hourly()
    cache = merge_cache(cache, fresh)
    if cache.empty:
        print("FATAL: no hourly data.", file=sys.stderr)
        return 1
    if not args.no_cache:
        save_hourly_cache(cache)
        print(f"  archive saved: {PANEL_CSV} "
              f"({len(cache)} rows, {len(cache.columns)} cols)")

    panel = panel_from_cache(cache)
    print(f"  panel: {len(panel)} hourly rows x {len(panel.columns)} series")

    forecasts = {}
    if not args.no_forecast:
        print(f"Forecasting ({PH.METHOD}, {PH.LOOKBACK}h lookback -> 1h step, "
              f"x{PH.FORECAST_HORIZON}, {PH.N_PATHS} paths):")
        for key in HERO:
            try:
                fc = PH.forecast_target(panel, key, retune=args.retune)
            except Exception as exc:                         # noqa: BLE001
                print(f"  ! {key}: {type(exc).__name__}: {exc}")
                fc = None
            if fc:
                forecasts[key] = fc
                print(f"  + {key:4s} spot {fc['spot']:.3f} -> +24h "
                      f"P10 {fc['p10']:.3f} / P50 {fc['p50']:.3f} / "
                      f"P90 {fc['p90']:.3f}  (n={fc['n_train']}, "
                      f"oos dir {fc['oos_direction']:.3f})")
            else:
                print(f"  - {key:4s} no forecast")

    log = load_forecast_log()
    if forecasts and not args.no_cache:
        log = record_forecasts(log, forecasts)
        save_forecast_log(log)
        print(f"  forecast log: {FORECAST_CSV} ({len(log)} rows)")

    last = panel.index.max()
    view_start = last - pd.Timedelta(days=args.display_days)
    view_end = last + pd.Timedelta(hours=PH.FORECAST_HORIZON + 2)
    plot_start = last - pd.Timedelta(days=args.plot_days)

    print("Rendering...")
    trades = load_trades()
    if not trades.empty:
        print(f"  trades: {len(trades)} backtested overnight positions")
    fig = build_figure(cache, panel, forecasts, plot_start, view_start,
                       view_end, log=log, trades=trades)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(build_html(fig))
    print(f"Wrote {args.out} "
          f"({os.path.getsize(args.out)/1024:,.0f} KB, "
          f"figure {int(fig.layout.height)}px)")

    if args.open:
        import webbrowser
        webbrowser.open("file://" + os.path.abspath(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
