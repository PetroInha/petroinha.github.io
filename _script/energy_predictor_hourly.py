#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
energy_predictor_hourly.py — hourly forecasting engine.

The hourly sibling of `energy_predictor.py`. Same shape — predict ONE step
ahead, then apply that model recursively — but the step is an hour and the
horizon is 24 of them.

Timezone
--------
Everything is UTC internally. Yahoo returns intraday bars tz-aware in UTC
already, and the daily series are pinned to UTC midnight before broadcasting,
so no series can silently sit an offset away from another. KST is applied only
for display and for the trading clock (KST = UTC+9).

Model
-----
LightGBM, tuned separately from the daily model — different sampling rate,
different autocorrelation, so the daily hyperparameters do not transfer.
Cached in `__datafile/__lightgbm_hourly__.yaml`, reused for a week.

Usage
-----
    import energy_predictor_hourly as PH
    fc = PH.forecast_target(panel, "wti")

    py -3.13 _script/energy_predictor_hourly.py --tune wti gas
"""

from __future__ import annotations

import argparse
import datetime as dt
import math
import os
import sys
import warnings
from typing import Optional

import numpy as np
import pandas as pd
import yaml

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from energy_predictor import exog_features                   # noqa: E402

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                        # noqa: BLE001
        pass

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "__datafile")

METHOD = "lightgbm_hourly"
LOOKBACK = 24            # hours of own history feeding one prediction
FORECAST_HORIZON = 24    # recursive one-hour steps
N_PATHS = 1500
RANDOM_STATE = 42

# Rolling windows, in hours. Roughly a working week, a day and ten days —
# the hourly analogues of the daily model's 60/20/120-session windows.
VOL_WIN = 120
SHORT_VOL = 24
LONG_VOL = 240
LVL_WIN = 120

RETUNE_AFTER_DAYS = 7
CV_SPLITS = 5
SEARCH_ITER = 30
MIN_TRAIN_ROWS = 600

KST = dt.timezone(dt.timedelta(hours=9))
ENTRY_HOUR_UTC = 6       # 15:00 KST — the long/short decision
EXIT_HOUR_UTC = 0        # 09:00 KST next day — the unwind


def params_path(method: str = METHOD) -> str:
    return os.path.join(DATA_DIR, f"__{method}__.yaml")


# --------------------------------------------------------------------------
# Features
# --------------------------------------------------------------------------

TARGET_FEAT_NAMES = ([f"r_lag{i}" for i in range(LOOKBACK)]
                     + ["r_sum6", "r_sum24", "lvl_z", "vol_z", "hour_sin",
                        "hour_cos"])


def target_block_pandas(price: pd.Series) -> pd.DataFrame:
    """
    Own-history features for every timestamp.

    Two extras over the daily version: an hour-of-day sine/cosine pair, since
    intraday liquidity and volatility are strongly diurnal and the model would
    otherwise have no idea whether a bar is a thin Asian-hours print or the
    US open.
    """
    p = price.astype(float)
    r = np.log(p).diff()
    vol = r.rolling(VOL_WIN, min_periods=VOL_WIN).std().replace(0, np.nan)
    feats = {f"r_lag{i}": r.shift(i) / vol for i in range(LOOKBACK)}
    feats["r_sum6"] = r.rolling(6).sum() / (vol * math.sqrt(6))
    feats["r_sum24"] = r.rolling(24).sum() / (vol * math.sqrt(24))
    feats["lvl_z"] = ((p - p.rolling(LVL_WIN, min_periods=LVL_WIN).mean())
                      / p.rolling(LVL_WIN, min_periods=LVL_WIN)
                      .std().replace(0, np.nan))
    feats["vol_z"] = (r.rolling(SHORT_VOL, min_periods=SHORT_VOL).std()
                      / r.rolling(LONG_VOL, min_periods=LONG_VOL)
                      .std().replace(0, np.nan))
    hours = p.index.tz_convert("UTC").hour.values.astype(float)
    feats["hour_sin"] = pd.Series(np.sin(2 * np.pi * hours / 24), index=p.index)
    feats["hour_cos"] = pd.Series(np.cos(2 * np.pi * hours / 24), index=p.index)
    out = pd.DataFrame(feats, index=p.index)[TARGET_FEAT_NAMES]
    return out.replace([np.inf, -np.inf], np.nan)


def target_block_numpy(paths: np.ndarray, hours: np.ndarray) -> np.ndarray:
    """
    Same features as `target_block_pandas`, evaluated at the final column of
    each row. `hours` is the UTC hour each path's next bar falls on.
    """
    lp = np.log(paths)
    r = np.diff(lp, axis=1)
    vol = r[:, -VOL_WIN:].std(axis=1, ddof=1)
    vol = np.where(vol == 0, np.nan, vol)[:, None]

    cols = [r[:, -1 - i][:, None] / vol for i in range(LOOKBACK)]
    cols.append(r[:, -6:].sum(axis=1)[:, None] / (vol * math.sqrt(6)))
    cols.append(r[:, -24:].sum(axis=1)[:, None] / (vol * math.sqrt(24)))

    win = paths[:, -LVL_WIN:]
    sd = win.std(axis=1, ddof=1)
    cols.append(((paths[:, -1] - win.mean(axis=1))
                 / np.where(sd == 0, np.nan, sd))[:, None])

    short = r[:, -SHORT_VOL:].std(axis=1, ddof=1)
    long = r[:, -LONG_VOL:].std(axis=1, ddof=1)
    cols.append((short / np.where(long == 0, np.nan, long))[:, None])

    cols.append(np.sin(2 * np.pi * hours / 24)[:, None])
    cols.append(np.cos(2 * np.pi * hours / 24)[:, None])
    return np.hstack(cols)


def assert_blocks_agree(price: pd.Series) -> None:
    """Keep the pandas and numpy feature paths provably identical."""
    pdf = target_block_pandas(price).dropna()
    if pdf.empty:
        return
    last = pdf.index[-1]
    hist = price.loc[:last].values[None, :]
    hr = np.array([pd.Timestamp(last).tz_convert("UTC").hour], dtype=float)
    npy = target_block_numpy(hist, hr)[0]
    ref = pdf.iloc[-1].values
    bad = ~np.isclose(npy, ref, rtol=1e-8, atol=1e-10, equal_nan=True)
    if bad.any():
        names = np.array(TARGET_FEAT_NAMES)[bad]
        raise RuntimeError(
            "hourly feature implementations disagree on "
            f"{list(names)}: numpy={npy[bad]} vs pandas={ref[bad]}")


def build_design(panel: pd.DataFrame, target: str):
    """Assemble (X, y, price, exog_last). y is the next-hour log return."""
    price = panel[target].astype(float).dropna()
    if len(price) < MIN_TRAIN_ROWS + LONG_VOL:
        return None
    assert_blocks_agree(price)

    tgt = target_block_pandas(price)
    exo = exog_features(panel, exclude=target).reindex(price.index)
    exo_ok = [c for c in exo.columns if exo[c].notna().mean() >= 0.70]

    y = np.log(price.shift(-1) / price)
    data = tgt.join(exo[exo_ok]).join(y.rename("__y__")).dropna()
    if len(data) < MIN_TRAIN_ROWS:
        return None

    X = data.drop(columns="__y__")
    exog_cols = [c for c in X.columns if c not in TARGET_FEAT_NAMES]
    exog_last = (exo[exo_ok].ffill().reindex(price.index[-1:])
                 .reindex(columns=exog_cols).iloc[0].astype(float).values)
    exog_last = np.nan_to_num(exog_last, nan=0.0, posinf=0.0, neginf=0.0)
    return X, data["__y__"], price, exog_last


# --------------------------------------------------------------------------
# Model + tuning
# --------------------------------------------------------------------------

DEFAULT_PARAMS = {
    "n_estimators": 400, "learning_rate": 0.03, "num_leaves": 15,
    "max_depth": 4, "min_child_samples": 60, "subsample": 0.8,
    "subsample_freq": 1, "colsample_bytree": 0.7,
    "reg_alpha": 0.1, "reg_lambda": 1.0,
}

SEARCH_SPACE = {
    "n_estimators": [200, 400, 600, 900],
    "learning_rate": [0.01, 0.02, 0.03, 0.05],
    "num_leaves": [7, 15, 31, 63],
    "max_depth": [3, 4, 6, -1],
    "min_child_samples": [20, 40, 60, 100, 200],
    "subsample": [0.6, 0.7, 0.8, 1.0],
    "colsample_bytree": [0.5, 0.6, 0.7, 1.0],
    "reg_alpha": [0.0, 0.1, 1.0],
    "reg_lambda": [0.0, 1.0, 5.0],
}


def make_model(params: Optional[dict] = None, **overrides):
    from lightgbm import LGBMRegressor
    p = dict(DEFAULT_PARAMS)
    p.update(params or {})
    p.update(overrides)
    p.setdefault("subsample_freq", 1)
    return LGBMRegressor(objective="regression", random_state=RANDOM_STATE,
                         n_jobs=-1, verbose=-1, **p)


def direction_score(estimator, X, y) -> float:
    pred = np.asarray(estimator.predict(X), dtype=float)
    yv = np.asarray(y, dtype=float)
    mask = yv != 0
    if not mask.any():
        return 0.0
    return float(np.mean((pred[mask] > 0) == (yv[mask] > 0)))


def cv_splitter(n_splits: int = CV_SPLITS):
    """
    Forward-chaining splits with a LOOKBACK-hour gap, so a validation row's
    24-hour trailing window cannot overlap bars the model trained on.
    """
    from sklearn.model_selection import TimeSeriesSplit
    return TimeSeriesSplit(n_splits=n_splits, gap=LOOKBACK)


def tune(X: pd.DataFrame, y: pd.Series, n_iter: int = SEARCH_ITER,
         verbose: bool = True) -> dict:
    from sklearn.model_selection import RandomizedSearchCV
    search = RandomizedSearchCV(
        estimator=make_model(), param_distributions=SEARCH_SPACE,
        n_iter=n_iter, scoring=direction_score, cv=cv_splitter(),
        random_state=RANDOM_STATE, n_jobs=1, refit=False, error_score=0.0)
    search.fit(X, y)
    best = dict(DEFAULT_PARAMS)
    best.update(search.best_params_)
    if verbose:
        print(f"      tuned: direction accuracy {search.best_score_:.4f} "
              f"over {n_iter} candidates")
    return {"params": best, "score": float(search.best_score_)}


# --------------------------------------------------------------------------
# Hyperparameter cache
# --------------------------------------------------------------------------

def load_param_file(method: str = METHOD) -> dict:
    path = params_path(method)
    if not os.path.exists(path):
        return {"method": method, "targets": {}}
    try:
        with open(path, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}
        doc.setdefault("method", method)
        doc.setdefault("targets", {})
        return doc
    except Exception as exc:                                 # noqa: BLE001
        print(f"      ! {os.path.basename(path)} unreadable "
              f"({type(exc).__name__}); retuning")
        return {"method": method, "targets": {}}


def save_param_file(doc: dict, method: str = METHOD) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    doc["method"] = method
    doc["updated_at"] = dt.date.today().isoformat()
    with open(params_path(method), "w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(doc, fh, sort_keys=False, allow_unicode=True,
                       default_flow_style=False)


def _is_stale(entry: dict) -> bool:
    if not entry or "params" not in entry:
        return True
    stamp = entry.get("tuned_at")
    if not stamp:
        return True
    try:
        tuned = dt.date.fromisoformat(str(stamp))
    except ValueError:
        return True
    return (dt.date.today() - tuned).days > RETUNE_AFTER_DAYS


def get_params(target: str, X: pd.DataFrame, y: pd.Series,
               method: str = METHOD, retune: bool = False,
               verbose: bool = True, allow_tune: bool = True) -> dict:
    """
    Cached hyperparameters, tuning only when needed and permitted.

    `allow_tune=False` forbids the search outright. The backtest sets it: a
    search launched inside the replay loop would fit hyperparameters hundreds
    of times over, and — worse — would do it on whatever slice of history that
    trade happened to see, making the runs incomparable.
    """
    doc = load_param_file(method)
    entry = doc.get("targets", {}).get(target)
    if not retune and not _is_stale(entry):
        if verbose:
            print(f"      params: cached from {entry['tuned_at']} "
                  f"(direction {entry.get('cv_score', float('nan')):.4f})")
        return entry["params"]

    if not allow_tune:
        if entry and "params" in entry:
            if verbose:
                print(f"      params: stale cache from "
                      f"{entry.get('tuned_at')} reused (tuning disabled)")
            return entry["params"]
        raise RuntimeError(
            f"No cached hyperparameters for '{target}' in "
            f"{os.path.basename(params_path(method))} and tuning is "
            f"disabled. Run: py -3.13 _script/energy_predictor_hourly.py "
            f"--tune {target}")

    if verbose:
        why = ("forced" if retune else "no cache" if not entry
               else f"cache from {entry.get('tuned_at')} older than "
                    f"{RETUNE_AFTER_DAYS}d")
        print(f"      tuning {method} for {target} ({why})...")
    result = tune(X, y, verbose=verbose)
    doc.setdefault("targets", {})[target] = {
        "tuned_at": dt.date.today().isoformat(),
        "cv_score": result["score"],
        "cv": {"splits": CV_SPLITS, "gap_hours": LOOKBACK,
               "scoring": "directional_accuracy",
               "scheme": "forward-chaining TimeSeriesSplit"},
        "n_samples": int(len(X)), "n_features": int(X.shape[1]),
        "search_iter": SEARCH_ITER,
        "params": result["params"],
    }
    save_param_file(doc, method)
    return result["params"]


# --------------------------------------------------------------------------
# Recursive simulation
# --------------------------------------------------------------------------

def simulate_paths(model, price: pd.Series, exog_last: np.ndarray,
                   resid: np.ndarray, horizon: int, n_paths: int,
                   step_hours: np.ndarray,
                   seed: int = RANDOM_STATE) -> np.ndarray:
    """
    Roll the one-hour model forward `horizon` times.

    `step_hours` gives the UTC hour of each future bar so the diurnal features
    stay truthful as the path advances — without it every simulated hour would
    look like the hour the forecast was made.
    """
    rng = np.random.default_rng(seed)
    hist = price.dropna().values.astype(float)
    tail = hist[-(LONG_VOL + LOOKBACK + 10):]
    paths = np.repeat(tail[None, :], n_paths, axis=0)
    exog = np.tile(exog_last, (n_paths, 1))

    out = np.empty((n_paths, horizon))
    for h in range(horizon):
        hrs = np.full(n_paths, float(step_hours[h]))
        feats = target_block_numpy(paths, hrs)
        X = np.nan_to_num(np.hstack([feats, exog]), nan=0.0,
                          posinf=0.0, neginf=0.0)
        mu = model.predict(X)
        eps = rng.choice(resid, size=n_paths, replace=True)
        nxt = paths[:, -1] * np.exp(mu + eps)
        paths = np.hstack([paths, nxt[:, None]])
        out[:, h] = nxt
    return out


def forecast_target(panel: pd.DataFrame, target: str,
                    horizon: int = FORECAST_HORIZON,
                    method: str = METHOD, retune: bool = False,
                    verbose: bool = True,
                    allow_tune: bool = True) -> Optional[dict]:
    """
    Fit the one-hour model and roll it into a 24-hour P10/P50/P90 fan.

    Everything downstream is derived from `panel` alone, so truncating the
    panel before calling this is sufficient to keep the future out: features,
    validation folds, residuals and the simulation all read from it and
    nothing else.
    """
    if target not in panel.columns:
        return None
    built = build_design(panel, target)
    if built is None:
        return None
    X, y, price, exog_last = built

    params = get_params(target, X, y, method=method, retune=retune,
                        verbose=verbose, allow_tune=allow_tune)

    oos_true, oos_pred = [], []
    for tr, te in cv_splitter().split(X):
        m = make_model(params)
        m.fit(X.iloc[tr], y.iloc[tr])
        oos_true.append(y.iloc[te].values)
        oos_pred.append(m.predict(X.iloc[te]))
    oos_true = np.concatenate(oos_true)
    oos_pred = np.concatenate(oos_pred)
    resid = oos_true - oos_pred
    mask = oos_true != 0
    dir_acc = (float(np.mean((oos_pred[mask] > 0) == (oos_true[mask] > 0)))
               if mask.any() else float("nan"))

    model = make_model(params)
    model.fit(X, y)

    t0 = price.index[-1]
    steps = [t0 + pd.Timedelta(hours=i + 1) for i in range(horizon)]
    step_hours = np.array([t.tz_convert("UTC").hour for t in steps],
                          dtype=float)

    sims = simulate_paths(model, price, exog_last, resid, horizon, N_PATHS,
                          step_hours)
    q10, q50, q90 = np.percentile(sims, [10, 50, 90], axis=0)

    imp = pd.Series(model.feature_importances_, index=X.columns)
    by_series = {}
    for name, val in imp.items():
        base = "own history" if name in TARGET_FEAT_NAMES \
            else name.rsplit("_", 1)[0]
        by_series[base] = by_series.get(base, 0.0) + float(val)
    total = sum(by_series.values()) or 1.0
    top = sorted(((k, v / total) for k, v in by_series.items()),
                 key=lambda kv: -kv[1])[:5]

    return {
        "spot": float(price.iloc[-1]),
        "p10": float(q10[-1]), "p50": float(q50[-1]), "p90": float(q90[-1]),
        "path_p10": q10.tolist(), "path_p50": q50.tolist(),
        "path_p90": q90.tolist(),
        "steps": [t.isoformat() for t in steps],
        "n_train": int(len(X)), "resid_sd": float(np.std(resid)),
        "oos_direction": dir_acc, "top_drivers": top,
        "method": method, "asof": t0,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tune", nargs="+", metavar="TARGET",
                    default=["wti", "gas"])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

    import gather_energy_stats_hourly as GH
    cache = GH.load_hourly_cache()
    if cache.empty:
        print(f"No archive at {GH.PANEL_CSV}.", file=sys.stderr)
        return 1
    panel = GH.panel_from_cache(cache)
    print(f"Tuning {METHOD} — panel {len(panel)} hourly rows, "
          f"{len(panel.columns)} series")
    for target in args.tune:
        built = build_design(panel, target)
        if built is None:
            print(f"  - {target}: insufficient data")
            continue
        X, y = built[0], built[1]
        print(f"  {target}: {len(X)} rows x {X.shape[1]} features")
        get_params(target, X, y, retune=args.force)
    print(f"\nWrote {params_path()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
