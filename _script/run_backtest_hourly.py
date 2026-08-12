#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_backtest_hourly.py — replay the KST overnight long/short.

The trade
---------
At **15:00 KST** (06:00 UTC) the hourly model is refitted on everything known
up to that bar and rolled forward one hour at a time. Whether its forecast for
**09:00 KST the next morning** (00:00 UTC, 18 hours out) is above or below the
15:00 price decides long or short. The position is entered at the 15:00 close
and unwound at the 09:00 close.
 
No stop-loss
------------
The position is held to the unwind, full stop. An intraday stop is not
modelled because it could not be acted on: the Korean market is shut from
15:30 KST until 09:00 the next morning, which is precisely the holding
window. Anything that happens to the price in between cannot be traded out
of, so scoring a 2% stop here would be scoring an exit that never existed.

No lookahead
------------
The panel is truncated at each 15:00 decision bar before the model sees it,
and that truncation is asserted on every trade. Everything the model touches —
features, CV folds, residuals, the simulation — is derived from that slice, so
nothing from the holding window can reach the fit. The rows are still
generated after the fact, so they are tagged `source=backtest` in the log.

One caveat, stated plainly: the *hyperparameters* come from a search run once
over the whole sample, which includes the replayed window. Refitting them per
trade would be both ruinously slow and less comparable, but it does mean the
model's settings — not its training data — were chosen with some sight of the
period being scored. Treat the result as slightly optimistic. To remove even
that, tune on a cut of history that ends before the window and pass the
resulting YAML in.

Usage
-----
    py -3.13 _script/run_backtest_hourly.py
    py -3.13 _script/run_backtest_hourly.py --days 14 --targets wti
    py -3.13 _script/run_backtest_hourly.py --dry-run
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

import gather_energy_stats_hourly as GH                      # noqa: E402
import energy_predictor_hourly as PH                         # noqa: E402

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                        # noqa: BLE001
        pass

KST = PH.KST
ENTRY_HOUR_UTC = PH.ENTRY_HOUR_UTC      # 06:00 UTC = 15:00 KST
EXIT_HOUR_UTC = PH.EXIT_HOUR_UTC        # 00:00 UTC = 09:00 KST


def decision_bars(panel: pd.DataFrame, target: str, days: int) -> list:
    """The last `days` bars that fall on the 15:00 KST decision hour."""
    idx = panel[target].dropna().index
    entries = idx[idx.hour == ENTRY_HOUR_UTC]
    return list(entries[-days:])


def exit_bar(index: pd.DatetimeIndex, entry_ts: pd.Timestamp):
    """The 09:00 KST bar on the morning after `entry_ts`, if it exists."""
    target_ts = (entry_ts.normalize() + pd.Timedelta(days=1)
                 + pd.Timedelta(hours=EXIT_HOUR_UTC))
    later = index[(index >= target_ts) & (index <= target_ts
                                          + pd.Timedelta(hours=3))]
    return later[0] if len(later) else None


def trade_return(cache: pd.DataFrame, target: str, long_side: bool,
                 entry_ts, exit_ts, entry_px: float) -> float:
    """
    Realised return of one overnight position, held to the unwind.

    No intraday stop is applied: the Korean market is closed from 15:30 KST
    until 09:00 the next morning, so there is no point in the holding window
    at which the position could actually be exited. Whatever the price does
    overnight is simply worn.
    """
    close = pd.to_numeric(cache[f"{target}_Close"], errors="coerce")
    exit_px = float(close.loc[exit_ts])
    raw = exit_px / entry_px - 1.0
    return raw if long_side else -raw


def backtest(cache: pd.DataFrame, panel: pd.DataFrame, targets: list,
             days: int, allow_tune: bool = False) -> tuple:
    rows, trades = [], []
    leak_checks = [0]           # counts truncations verified, for the report
    for target in targets:
        if target not in panel.columns:
            print(f"  ! {target}: not in the panel, skipping")
            continue
        entries = decision_bars(panel, target, days)
        if not entries:
            print(f"  ! {target}: no 15:00 KST bars found")
            continue
        print(f"\n{target}: replaying {len(entries)} overnight trades "
              f"({entries[0].tz_convert(KST):%Y-%m-%d %H:%M} .. "
              f"{entries[-1].tz_convert(KST):%Y-%m-%d %H:%M} KST)")

        t_start, done = time.time(), 0
        for entry_ts in entries:
            done += 1
            ex_ts = exit_bar(panel.index, entry_ts)
            if ex_ts is None:
                continue
            hours_out = int((ex_ts - entry_ts) / pd.Timedelta(hours=1))

            # The one line the whole backtest rests on. Everything the model
            # touches — features, CV folds, residuals, simulation — is derived
            # from `sub`, so cutting it here is what keeps the future out.
            sub = panel.loc[:entry_ts]
            if len(sub) and sub.index.max() > entry_ts:
                raise AssertionError(
                    f"leakage: panel truncated at {entry_ts} still holds "
                    f"{sub.index.max()}")
            leak_checks[0] += 1

            try:
                fc = PH.forecast_target(sub, target, horizon=max(hours_out, 1),
                                        verbose=(done == 1),
                                        allow_tune=allow_tune)
            except Exception as exc:                          # noqa: BLE001
                print(f"  ! {entry_ts.date()}: {type(exc).__name__}: {exc}")
                continue
            if not fc:
                continue

            entry_px = fc["spot"]
            pred_px = fc["path_p50"][hours_out - 1]
            long_side = pred_px > entry_px

            ret = trade_return(cache, target, long_side, entry_ts, ex_ts,
                               entry_px)

            t0 = pd.Timestamp(fc["asof"]).tz_convert("UTC")
            for i, (p10, p50, p90) in enumerate(
                    zip(fc["path_p10"], fc["path_p50"], fc["path_p90"]),
                    start=1):
                rows.append({
                    "run_ts": t0, "target": target, "step": i,
                    "horizon_ts": t0 + pd.Timedelta(hours=i),
                    "p10": p10, "p50": p50, "p90": p90,
                    "spot": entry_px, "source": "backtest"})

            trades.append({
                "target": target, "entry_ts": entry_ts, "exit_ts": ex_ts,
                "hours": hours_out, "side": "long" if long_side else "short",
                "entry_px": entry_px, "pred_px": pred_px,
                "exit_px": float(pd.to_numeric(
                    cache[f"{target}_Close"], errors="coerce").loc[ex_ts]),
                "ret": ret})

            if done % 5 == 0 or done == len(entries):
                rate = (time.time() - t_start) / done
                print(f"    {done:>3}/{len(entries)}  "
                      f"{entry_ts.tz_convert(KST):%m-%d %H:%M} KST  "
                      f"{'LONG ' if long_side else 'SHORT'} "
                      f"{entry_px:8.3f} -> {trades[-1]['exit_px']:8.3f}  "
                      f"{ret*100:+6.2f}%  ({rate:.1f}s/trade)")
        print(f"  {target}: {(time.time()-t_start)/60:.1f} min")
    print(f"\nleakage check: {leak_checks[0]} training sets verified to end "
          f"at or before their decision bar")
    return pd.DataFrame(rows), pd.DataFrame(trades)


def summarise(trades: pd.DataFrame) -> None:
    if trades.empty:
        print("\nNo trades to summarise.")
        return
    print("\nOvernight long/short — enter 15:00 KST, exit 09:00 KST next day")
    for target, grp in trades.groupby("target"):
        eq = float(np.prod(1.0 + grp["ret"].values))
        wins = int((grp["ret"] > 0).sum())
        n = len(grp)
        print(f"\n  {target}  {n} trades  "
              f"({grp['entry_ts'].min().tz_convert(KST):%Y-%m-%d} .. "
              f"{grp['entry_ts'].max().tz_convert(KST):%Y-%m-%d} KST)")
        print(f"     hit rate      {wins}/{n} = {wins/n*100:.1f}%")
        print(f"     equity        {eq*100:.2f}%  "
              f"(best {grp['ret'].max()*100:+.2f}%, "
              f"worst {grp['ret'].min()*100:+.2f}%)")
        print(f"     mean per trade {grp['ret'].mean()*100:+.3f}% "
              f"(sd {grp['ret'].std()*100:.3f}%)")
        print(f"     sides         {int((grp['side']=='long').sum())} long, "
              f"{int((grp['side']=='short').sum())} short")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=30,
                    help="overnight trades to replay (default 30, ~a month)")
    ap.add_argument("--targets", nargs="+", default=["wti", "gas"])
    ap.add_argument("--allow-tune", action="store_true",
                    help="permit a hyperparameter search inside the replay "
                         "loop; off by default so every trade uses the same "
                         "cached settings")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--trades-csv", default=os.path.join(
        GH.DATA_DIR, "backtest_trades_hourly.csv"))
    args = ap.parse_args(argv)

    print(f"CURE hourly backtest — {dt.date.today()}")
    cache = GH.load_hourly_cache()
    if cache.empty:
        print(f"No archive at {GH.PANEL_CSV}. "
              "Run gather_energy_stats_hourly.py first.", file=sys.stderr)
        return 1
    panel = GH.panel_from_cache(cache)
    print(f"  panel: {len(panel)} hourly rows, "
          f"{panel.index.min()} .. {panel.index.max()} UTC")
    print(f"  entry {ENTRY_HOUR_UTC:02d}:00 UTC = 15:00 KST | "
          f"exit {EXIT_HOUR_UTC:02d}:00 UTC = 09:00 KST next day")

    print(f"  hyperparameters: cached, no search during replay"
          if not args.allow_tune else "  hyperparameters: search permitted")
    new, trades = backtest(cache, panel, args.targets, args.days,
                           allow_tune=args.allow_tune)
    summarise(trades)

    if args.dry_run:
        print(f"\n--dry-run: {len(new)} forecast rows, {len(trades)} trades; "
              "nothing written.")
        return 0

    if not trades.empty:
        os.makedirs(GH.DATA_DIR, exist_ok=True)
        out = trades.copy()
        # ISO-8601 UTC so the dashboard can parse these back unambiguously,
        # plus a KST rendering for anyone reading the file directly.
        for c in ("entry_ts", "exit_ts"):
            ts = pd.to_datetime(out[c], utc=True)
            out[f"{c}_kst"] = ts.dt.tz_convert(KST).dt.strftime(
                "%Y-%m-%d %H:%M")
            out[c] = ts.dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        cols = ["target", "entry_ts", "exit_ts", "entry_ts_kst",
                "exit_ts_kst", "hours", "side", "entry_px", "pred_px",
                "exit_px", "ret"]
        out[cols].to_csv(args.trades_csv, index=False, float_format="%.6g")
        print(f"\ntrades: {args.trades_csv} ({len(out)} rows)")

    if not new.empty:
        log = GH.load_forecast_log()
        before = len(log)
        if "source" in log.columns and not log.empty:
            live = log[log["source"].fillna("live") != "backtest"]
        else:
            live = log
        combined = pd.concat([new, live], ignore_index=True)
        combined = combined.drop_duplicates(
            subset=["run_ts", "target", "step"], keep="last")
        combined = combined.sort_values(["target", "run_ts", "step"])
        GH.save_forecast_log(combined)
        print(f"forecast log: {GH.FORECAST_CSV}  "
              f"{before} -> {len(combined)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
