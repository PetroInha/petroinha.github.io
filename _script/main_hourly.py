#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main_hourly.py — run the hourly dashboard once an hour, then push.

Each cycle regenerates `_images/energy_stats_hourly.html` from fresh hourly
bars and commits the result. Optionally refreshes the overnight backtest too.

Scheduling
----------
Wakes a little after the top of each hour, so the exchange bar for that hour
has actually been published before we ask for it. Set `--minute` to move that
offset.

Interpreter
-----------
Child processes are launched with `sys.executable`, i.e. whichever Python is
running this file. Hard-coding "python" is unreliable on Windows, where it may
resolve to the Microsoft Store stub and fail silently every cycle.

Usage
-----
    py -3.13 _script/main_hourly.py
    py -3.13 _script/main_hourly.py --minute 5 --with-backtest
    py -3.13 _script/main_hourly.py --once            # one cycle, then exit
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KST = dt.timezone(dt.timedelta(hours=9))

GATHER = os.path.join(HERE, "gather_energy_stats_hourly.py")
BACKTEST = os.path.join(HERE, "run_backtest_hourly.py")
PUSH = os.path.join(HERE, "git_push_energy_stats.py")

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                        # noqa: BLE001
        pass


def log(msg: str) -> None:
    now = dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")
    print(f"[{now}] {msg}", flush=True)


def run(script: str, *args: str) -> int:
    """Run a sibling script with this interpreter, streaming its output."""
    cmd = [sys.executable, "-u", script, *args]
    log(f"$ {os.path.basename(script)} {' '.join(args)}")
    try:
        return subprocess.run(cmd, cwd=ROOT).returncode
    except Exception as exc:                                 # noqa: BLE001
        log(f"  ! {type(exc).__name__}: {exc}")
        return 1


def cycle(with_backtest: bool, backtest_days: int, push: bool) -> bool:
    """One pass. Returns True if the dashboard regenerated successfully."""
    rc = run(GATHER)
    if rc != 0:
        log(f"  gather failed (exit {rc}); skipping push this cycle")
        return False

    if with_backtest:
        rc_bt = run(BACKTEST, "--days", str(backtest_days))
        if rc_bt != 0:
            log(f"  backtest failed (exit {rc_bt}); continuing anyway")
        else:
            # Redraw so the refreshed trade bands land in the published page.
            run(GATHER)

    if push:
        rc_push = run(PUSH)
        if rc_push != 0:
            log(f"  push failed (exit {rc_push}); the commit may still be "
                f"local — check `git status`")
    return True


def seconds_until_next(minute: int) -> float:
    """Seconds until `minute` past the next hour."""
    now = dt.datetime.now(dt.timezone.utc)
    target = now.replace(minute=minute, second=0, microsecond=0)
    if target <= now:
        target += dt.timedelta(hours=1)
    return (target - now).total_seconds()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--minute", type=int, default=3,
                    help="minutes past the hour to run (default 3, giving "
                         "the exchange time to publish the bar)")
    ap.add_argument("--once", action="store_true",
                    help="run a single cycle and exit")
    ap.add_argument("--with-backtest", action="store_true",
                    help="refresh the overnight backtest each cycle")
    ap.add_argument("--backtest-days", type=int, default=7)
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--run-now", action="store_true",
                    help="run immediately instead of waiting for the hour")
    args = ap.parse_args(argv)

    push = not args.no_push
    log(f"hourly scheduler up — interpreter {sys.executable}")
    log(f"  run at :{args.minute:02d} past each hour | "
        f"backtest={'on' if args.with_backtest else 'off'} | "
        f"push={'on' if push else 'off'}")

    if args.once:
        cycle(args.with_backtest, args.backtest_days, push)
        return 0

    if args.run_now:
        cycle(args.with_backtest, args.backtest_days, push)

    while True:
        wait = seconds_until_next(args.minute)
        log(f"sleeping {wait/60:.1f} min until the next run")
        try:
            time.sleep(wait)
        except KeyboardInterrupt:
            log("interrupted — stopping")
            return 0
        try:
            cycle(args.with_backtest, args.backtest_days, push)
        except KeyboardInterrupt:
            log("interrupted — stopping")
            return 0
        except Exception as exc:                             # noqa: BLE001
            # A bad cycle must not kill the loop; the next hour gets a turn.
            log(f"  ! cycle raised {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
