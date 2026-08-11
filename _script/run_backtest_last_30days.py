#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_backtest_last_30days.py — seed the forecast track record.

Replays the recursive random-forest forecast over the most recent trading
days using only the archive that already exists, and writes the results into
__datafile/forecast_log.csv alongside the live calls. That gives the dashboard
a populated scorecard immediately instead of one star per day from a standing
start; live runs then accumulate on top of it.

No lookahead
------------
For each as-of date the panel is truncated to that date before anything else
happens, so the model is fitted, validated and simulated on data that existed
at the time. It never sees the bar it is predicting. What it is *not* is a
live call: these rows are generated after the fact, so they are tagged
`source=backtest` in the log and the page says so. A genuinely live record can
only accrue with time.

Usage
-----
    py -3.13 _script/run_backtest_last_30days.py
    py -3.13 _script/run_backtest_last_30days.py --days 60
    py -3.13 _script/run_backtest_last_30days.py --targets wti --dry-run
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gather_energy_stats as G                              # noqa: E402

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                        # noqa: BLE001
        pass


def build_panel() -> pd.DataFrame:
    """Rebuild the model panel from the archive, exactly as a live run does."""
    cache = G.load_panel_cache()
    if cache.empty:
        raise SystemExit(
            f"No archive at {G.PANEL_CSV}. Run gather_energy_stats.py first.")
    series_list = G.registry()
    G.hydrate_from_cache(series_list, cache)
    panel = G.daily_panel(series_list)
    if panel.empty:
        raise SystemExit("Archive produced an empty panel.")
    return panel


def backtest(panel: pd.DataFrame, targets: list, days: int,
             horizon: int = G.FORECAST_HORIZON) -> pd.DataFrame:
    """
    Walk the last `days` trading days, refitting at each one.

    Returns forecast-log rows. Each as-of date costs a full model fit plus a
    Monte-Carlo rollout, so this is minutes of work, not seconds.
    """
    rows = []
    for target in targets:
        if target not in panel.columns:
            print(f"  ! {target}: not in the archive, skipping")
            continue
        dates = panel[target].dropna().index
        asof_dates = list(dates[-days:])
        print(f"\n{target}: replaying {len(asof_dates)} days "
              f"({asof_dates[0].date()} .. {asof_dates[-1].date()})")

        t_start = time.time()
        done = ok = 0
        for asof in asof_dates:
            # The single line that keeps this honest: nothing after `asof`
            # is visible to the fit, the validation, or the simulation.
            sub = panel.loc[:asof]
            done += 1
            try:
                fc = G.forecast_target(sub, target, horizon=horizon)
            except Exception as exc:                          # noqa: BLE001
                print(f"  ! {asof.date()}: {type(exc).__name__}: {exc}")
                continue
            if not fc:
                continue
            ok += 1
            t0 = pd.Timestamp(fc["asof"]).normalize()
            for i, (p10, p50, p90) in enumerate(
                    zip(fc["path_p10"], fc["path_p50"], fc["path_p90"]),
                    start=1):
                rows.append({
                    "run_date": t0, "target": target, "step": i,
                    "horizon_date": (t0 + pd.tseries.offsets.BDay(i)
                                     ).normalize(),
                    "p10": p10, "p50": p50, "p90": p90,
                    "spot": fc["spot"], "source": "backtest",
                })
            if done % 5 == 0 or done == len(asof_dates):
                rate = (time.time() - t_start) / done
                left = rate * (len(asof_dates) - done)
                print(f"    {done:>3}/{len(asof_dates)}  "
                      f"{asof.date()}  spot {fc['spot']:.2f} -> "
                      f"P50 {fc['path_p50'][0]:.2f}  "
                      f"({rate:.1f}s/day, ~{left/60:.1f} min left)")
        print(f"  {target}: {ok}/{len(asof_dates)} days produced a forecast "
              f"in {(time.time()-t_start)/60:.1f} min")
    return pd.DataFrame(rows)


def summarise(log: pd.DataFrame, panel: pd.DataFrame, targets: list) -> None:
    """Print the directional scorecard the dashboard will show."""
    print("\nScorecard (next-day direction, treated as a daily long/short):")
    for target in targets:
        if target not in panel.columns:
            continue
        scored = G.score_predictions(log[log["target"] == target],
                                     panel[target].dropna())
        st = G.directional_stats(scored)
        if not st:
            print(f"  {target:4s} no scored calls yet")
            continue
        print(f"  {target:4s} n={st['n']:<4d} hit={st['hit_rate']*100:5.1f}%  "
              f"F1={st['f1']:.3f}  precision={st['precision']:.3f}  "
              f"recall={st['recall']:.3f}  MAE={st['mae_pct']:.2f}%")
        print(f"       up-called-right {st['tp']}, up-called-wrong {st['fp']}, "
              f"down-called-right {st['tn']}, down-called-wrong {st['fn']}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=30,
                    help="trading days to replay (default 30)")
    ap.add_argument("--targets", nargs="+", default=["wti", "gas"])
    ap.add_argument("--horizon", type=int, default=G.FORECAST_HORIZON)
    ap.add_argument("--dry-run", action="store_true",
                    help="compute and summarise without writing the log")
    args = ap.parse_args(argv)

    print(f"CURE backtest — {dt.date.today()}")
    panel = build_panel()
    print(f"  panel: {len(panel)} business days, "
          f"{panel.index.min().date()} .. {panel.index.max().date()}, "
          f"{len(panel.columns)} series")

    new = backtest(panel, args.targets, args.days, args.horizon)
    if new.empty:
        print("No backtest rows produced.", file=sys.stderr)
        return 1

    log = G.load_forecast_log()
    before = len(log)

    # A live call is a real prediction made before the fact and must never be
    # overwritten by a replay of the same day. Stale backtest rows, on the
    # other hand, are regenerated: drop them, then let the live rows land last
    # so `keep="last"` resolves any collision in their favour.
    if "source" in log.columns and not log.empty:
        live = log[log["source"].fillna("live") != "backtest"]
    else:
        live = log
    n_live, n_dropped = len(live), before - len(live)

    combined = pd.concat([new, live], ignore_index=True)
    combined = combined.drop_duplicates(subset=["run_date", "target", "step"],
                                        keep="last")
    combined = combined.sort_values(["target", "run_date", "step"])
    print(f"\nlog: {n_live} live row(s) kept, {n_dropped} stale backtest "
          f"row(s) replaced, {len(new)} new backtest row(s)")

    summarise(combined, panel, args.targets)

    if args.dry_run:
        print(f"\n--dry-run: {len(new)} rows computed, log left at "
              f"{before} rows.")
        return 0

    G.save_forecast_log(combined)
    print(f"\nforecast log: {G.FORECAST_CSV}  "
          f"{before} -> {len(combined)} rows "
          f"(+{len(combined)-before})")
    print("Re-run gather_energy_stats.py to redraw the dashboard.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
