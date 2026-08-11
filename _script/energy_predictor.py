#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
energy_predictor.py — forecasting engine for the CURE energy dashboard.

Everything model-shaped lives here so the dashboard script stays about
fetching and drawing: feature construction, hyperparameter tuning, fitting,
and the recursive Monte-Carlo rollout.

Scheme
------
Predict ONE day ahead from the target's trailing 14 sessions plus the current
cross-market state, then apply that one-day model recursively to reach a week.
Uncertainty comes from resampling the model's own walk-forward residuals along
each simulated path, so it compounds with horizon instead of being assumed.

Model
-----
LightGBM (`LGBMRegressor`). Hyperparameters are tuned by randomised search over
a purged, gapped `TimeSeriesSplit` — every validation fold is strictly later
than its training fold, and a `LOOKBACK`-day gap sits between them so the
trailing-window features of a validation row cannot overlap training rows.
Search is scored on directional accuracy, which is what the dashboard actually
reports, rather than on an R² that hovers near zero for daily returns.

Tuned parameters are cached in `__datafile/__lightgbm__.yaml`, per target, with
the date they were found. A cache younger than a week is reused; older than
that and the search runs again and overwrites it.

Usage
-----
    import energy_predictor as P
    fc = P.forecast_target(panel, "wti")            # cached params
    fc = P.forecast_target(panel, "wti", retune=True)

    py -3.13 _script/energy_predictor.py --tune wti gas    # tune only
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

METHOD = "lightgbm"
LOOKBACK = 14            # trading days of own history feeding one prediction
FORECAST_HORIZON = 5     # recursive one-day steps (~1 week)
N_PATHS = 2000           # Monte-Carlo paths for the recursive fan
RANDOM_STATE = 42

RETUNE_AFTER_DAYS = 7    # cached hyperparameters older than this are refreshed
CV_SPLITS = 5
SEARCH_ITER = 40         # randomised-search candidates
MIN_TRAIN_ROWS = 250


def params_path(method: str = METHOD) -> str:
    return os.path.join(DATA_DIR, f"__{method}__.yaml")


# --------------------------------------------------------------------------
# Features
# --------------------------------------------------------------------------

TARGET_FEAT_NAMES = ([f"r_lag{i}" for i in range(LOOKBACK)]
                     + ["r_sum5", "r_sum14", "lvl_z", "vol_z"])


def exog_features(panel: pd.DataFrame, exclude: str) -> pd.DataFrame:
    """
    Cross-market state: short/medium momentum and a level z-score for every
    series other than the forecast target. Differences (not log returns) keep
    yield and real-rate series — which can be zero or negative — well defined.

    Held frozen through the recursion (see `simulate_paths`).
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
    r = np.diff(lp, axis=1)
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


def assert_blocks_agree(price: pd.Series) -> None:
    """
    Guard against the two feature implementations drifting apart. The pandas
    one builds the training matrix; the numpy one runs inside the recursion on
    simulated paths. If they diverge the model predicts from features it was
    never trained on, and nothing else would reveal it.
    """
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


def build_design(panel: pd.DataFrame, target: str):
    """
    Assemble the training set for one target. y is the next-day log return.

    Returns (X, y, price, exog_last). `exog_last` is the cross-market state on
    the *last price date*, which is deliberately one day later than the final
    training row: y needs tomorrow's price, so the last row X can be fitted on
    is T-1, while the forecast has to start from what is known at T.
    """
    price = panel[target].astype(float).dropna()
    if len(price) < 400:
        return None
    assert_blocks_agree(price)

    tgt = target_block_pandas(price)
    exo = exog_features(panel, exclude=target).reindex(price.index)
    # Drop predictors that are still mostly empty before the row-wise dropna,
    # so one sparse column cannot take the whole training set with it.
    exo_ok = [c for c in exo.columns if exo[c].notna().mean() >= 0.70]

    y = np.log(price.shift(-1) / price)
    data = tgt.join(exo[exo_ok]).join(y.rename("__y__")).dropna()
    if len(data) < MIN_TRAIN_ROWS:
        return None

    X = data.drop(columns="__y__")
    exog_last = (exo[exo_ok].ffill().reindex(price.index[-1:])
                 .reindex(columns=[c for c in X.columns
                                   if c not in TARGET_FEAT_NAMES])
                 .iloc[0].astype(float).values)
    exog_last = np.nan_to_num(exog_last, nan=0.0, posinf=0.0, neginf=0.0)
    return X, data["__y__"], price, exog_last


# --------------------------------------------------------------------------
# Model + tuning
# --------------------------------------------------------------------------

DEFAULT_PARAMS = {
    "n_estimators": 400,
    "learning_rate": 0.03,
    "num_leaves": 15,
    "max_depth": 4,
    "min_child_samples": 30,
    "subsample": 0.8,
    "subsample_freq": 1,
    "colsample_bytree": 0.7,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
}

SEARCH_SPACE = {
    "n_estimators": [200, 300, 400, 600, 800],
    "learning_rate": [0.01, 0.02, 0.03, 0.05, 0.08],
    "num_leaves": [7, 15, 31, 63],
    "max_depth": [3, 4, 5, 6, -1],
    "min_child_samples": [10, 20, 30, 50, 80],
    "subsample": [0.6, 0.7, 0.8, 0.9, 1.0],
    "colsample_bytree": [0.5, 0.6, 0.7, 0.8, 1.0],
    "reg_alpha": [0.0, 0.1, 0.5, 1.0],
    "reg_lambda": [0.0, 0.5, 1.0, 5.0],
}


def make_model(params: Optional[dict] = None, **overrides):
    """A LightGBM regressor with the quiet, deterministic settings we want."""
    from lightgbm import LGBMRegressor
    p = dict(DEFAULT_PARAMS)
    p.update(params or {})
    p.update(overrides)
    p.setdefault("subsample_freq", 1)
    return LGBMRegressor(
        objective="regression", random_state=RANDOM_STATE,
        n_jobs=-1, verbose=-1, **p)


def direction_score(estimator, X, y) -> float:
    """
    Fraction of days whose *sign* the model gets right.

    Tuned on this rather than R² because daily-return R² sits around zero and
    barely separates candidates, while direction is what the dashboard scores
    and what a long/short would trade.
    """
    pred = np.asarray(estimator.predict(X), dtype=float)
    yv = np.asarray(y, dtype=float)
    mask = yv != 0
    if not mask.any():
        return 0.0
    return float(np.mean((pred[mask] > 0) == (yv[mask] > 0)))


def cv_splitter(n_splits: int = CV_SPLITS):
    """
    Forward-chaining splits with a gap.

    Every validation fold is strictly later than its training fold, and a
    LOOKBACK-day gap separates them: the features of a validation row look
    back 14 sessions, so without the gap those windows would overlap rows the
    model trained on and the score would flatter itself.
    """
    from sklearn.model_selection import TimeSeriesSplit
    return TimeSeriesSplit(n_splits=n_splits, gap=LOOKBACK)


def tune(X: pd.DataFrame, y: pd.Series, n_iter: int = SEARCH_ITER,
         verbose: bool = True) -> dict:
    """Randomised search over SEARCH_SPACE; returns the best parameter set."""
    from sklearn.model_selection import RandomizedSearchCV

    search = RandomizedSearchCV(
        estimator=make_model(),
        param_distributions=SEARCH_SPACE,
        n_iter=n_iter, scoring=direction_score, cv=cv_splitter(),
        random_state=RANDOM_STATE, n_jobs=1, refit=False, error_score=0.0,
    )
    search.fit(X, y)
    best = dict(DEFAULT_PARAMS)
    best.update(search.best_params_)
    if verbose:
        print(f"      tuned: direction accuracy {search.best_score_:.4f} "
              f"over {n_iter} candidates")
    return {"params": best, "score": float(search.best_score_)}


# --------------------------------------------------------------------------
# Hyperparameter cache — __datafile/__<method>__.yaml
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
    """True when the cached tuning is missing, undated, or over a week old."""
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
               verbose: bool = True) -> dict:
    """
    Cached hyperparameters for one target, tuning only when needed.

    Reused while under a week old; refreshed and rewritten once past that, so
    the model tracks a drifting market without paying for a search every run.
    """
    doc = load_param_file(method)
    entry = doc.get("targets", {}).get(target)

    if not retune and not _is_stale(entry):
        if verbose:
            print(f"      params: cached from {entry['tuned_at']} "
                  f"(direction {entry.get('cv_score', float('nan')):.4f})")
        return entry["params"]

    if verbose:
        why = ("forced" if retune else
               "no cache" if not entry else
               f"cache from {entry.get('tuned_at')} older than "
               f"{RETUNE_AFTER_DAYS}d")
        print(f"      tuning {method} for {target} ({why})...")

    result = tune(X, y, verbose=verbose)
    doc.setdefault("targets", {})[target] = {
        "tuned_at": dt.date.today().isoformat(),
        "cv_score": result["score"],
        "cv": {"splits": CV_SPLITS, "gap_days": LOOKBACK,
               "scoring": "directional_accuracy",
               "scheme": "forward-chaining TimeSeriesSplit"},
        "n_samples": int(len(X)),
        "n_features": int(X.shape[1]),
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
                   seed: int = RANDOM_STATE) -> np.ndarray:
    """
    Roll the one-day model forward `horizon` times.

    Each step predicts tomorrow's log return from the trailing 14 days, adds a
    residual drawn from the model's own out-of-sample error distribution, and
    appends the resulting price so the next step sees it.

    The exogenous block is held at its last observed value: the dollar, the
    curve and volatility are not themselves forecast, so the fan answers
    "where does this contract drift if the rest of the market stands still".
    """
    rng = np.random.default_rng(seed)
    hist = price.dropna().values.astype(float)
    tail = hist[-260:]
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


# --------------------------------------------------------------------------
# Public entry point
# --------------------------------------------------------------------------

def forecast_target(panel: pd.DataFrame, target: str,
                    horizon: int = FORECAST_HORIZON,
                    method: str = METHOD, retune: bool = False,
                    verbose: bool = True) -> Optional[dict]:
    """
    Fit the one-day model and roll it forward into a P10/P50/P90 fan.

    Returns None when the panel cannot support a fit; callers treat that as
    "no forecast" rather than an error.
    """
    if target not in panel.columns:
        return None
    built = build_design(panel, target)
    if built is None:
        return None
    X, y, price, exog_last = built

    params = get_params(target, X, y, method=method, retune=retune,
                        verbose=verbose)

    # Walk-forward residuals of the one-day model. These are what the
    # recursion resamples, so the fan widens with horizon on its own.
    # Truths and predictions are collected together rather than reconstructed
    # from the residual tail, so the pairing cannot silently misalign.
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

    sims = simulate_paths(model, price, exog_last, resid, horizon, N_PATHS)
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
        "path_p10": q10.tolist(),
        "path_p50": q50.tolist(),
        "path_p90": q90.tolist(),
        "n_train": int(len(X)),
        "resid_sd": float(np.std(resid)),
        "oos_direction": dir_acc,
        "top_drivers": top,
        "method": method,
        "asof": price.index[-1],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tune", nargs="+", metavar="TARGET",
                    default=["wti", "gas"],
                    help="targets to tune (default: wti gas)")
    ap.add_argument("--force", action="store_true",
                    help="retune even if the cache is fresh")
    args = ap.parse_args(argv)

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import gather_energy_stats as G

    cache = G.load_panel_cache()
    if cache.empty:
        print(f"No archive at {G.PANEL_CSV}.", file=sys.stderr)
        return 1
    series_list = G.registry()
    G.hydrate_from_cache(series_list, cache)
    panel = G.daily_panel(series_list)

    print(f"Tuning {METHOD} — panel {len(panel)} rows, "
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
