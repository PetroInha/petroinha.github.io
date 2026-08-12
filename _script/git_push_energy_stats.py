#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
git_push_energy_stats.py — commit and push the regenerated dashboard.

Stages `_images/energy_stats.html` (plus the EnergyInsight page if it moved),
commits with a timestamped message, and pushes to the current branch.

Usage
-----
    py -3.13 _script/git_push_energy_stats.py
    py -3.13 _script/git_push_energy_stats.py --dry-run
    py -3.13 _script/git_push_energy_stats.py --message "manual refresh"
    py -3.13 _script/git_push_energy_stats.py --regenerate

Note on `git add -f`
--------------------
This repository's .gitignore contains a blanket `_*` rule, which matches
`_images/`. The existing images predate that rule so they stay tracked, but a
*newly created* file under `_images/` would be silently ignored. The dashboard
is therefore force-added on purpose — without `-f` this script would report
"nothing to commit" forever while the site never updates.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = [
    os.path.join("_images", "energy_stats.html"),
    "i_7_energy_stats.markdown",
    # The archive and the forecast log are the point of the whole exercise:
    # they accumulate across runs, and the track record is only meaningful if
    # past calls survive. Committing them keeps that history durable.
    os.path.join("__datafile", "energy_panel.csv"),
    os.path.join("__datafile", "forecast_log.csv"),
    # Tuned hyperparameters, so a fresh checkout does not have to re-search
    # and every machine forecasts with the same settings.
    os.path.join("__datafile", "__lightgbm__.yaml"),

    # Hourly dashboard. Deliberately not embedded in any page — it is pushed
    # so the file and its history live on GitHub, nothing more.
    os.path.join("_images", "energy_stats_hourly.html"),
    os.path.join("__datafile", "energy_panel_hourly.csv"),
    os.path.join("__datafile", "forecast_log_hourly.csv"),
    os.path.join("__datafile", "backtest_trades_hourly.csv"),
    os.path.join("__datafile", "__lightgbm_hourly__.yaml"),
]
KST = dt.timezone(dt.timedelta(hours=9))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                      # noqa: BLE001
        pass


def git(*args: str, check: bool = True, capture: bool = True):
    """Run a git command inside the repo root."""
    proc = subprocess.run(
        ["git", *args], cwd=ROOT, check=False,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        text=True, encoding="utf-8", errors="replace",
    )
    if check and proc.returncode != 0:
        out = (proc.stdout or "").strip()
        raise RuntimeError(f"git {' '.join(args)} failed "
                           f"({proc.returncode}):\n{out}")
    return proc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--message", "-m", default=None,
                    help="override the commit message")
    ap.add_argument("--branch", default=None,
                    help="branch to push (default: current)")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--dry-run", action="store_true",
                    help="stage and show the diff, but do not commit or push")
    ap.add_argument("--regenerate", action="store_true",
                    help="run gather_energy_stats.py first")
    args = ap.parse_args(argv)

    if args.regenerate:
        script = os.path.join(ROOT, "_script", "gather_energy_stats.py")
        print(f"Regenerating via {script} ...")
        rc = subprocess.run([sys.executable, script], cwd=ROOT).returncode
        if rc != 0:
            print("Generation failed; nothing pushed.", file=sys.stderr)
            return rc

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print(f"Not a git repository: {ROOT}", file=sys.stderr)
        return 1

    present = [t for t in TARGETS if os.path.exists(os.path.join(ROOT, t))]
    if not present:
        print("Nothing to push — no dashboard file found. "
              "Run gather_energy_stats.py first (or pass --regenerate).",
              file=sys.stderr)
        return 1

    branch = args.branch or git("rev-parse", "--abbrev-ref",
                                "HEAD").stdout.strip()
    print(f"Repository : {ROOT}")
    print(f"Branch     : {branch}")
    print(f"Staging    : {', '.join(present)}")

    # -f is required: the repo's `_*` ignore rule covers _images/.
    git("add", "-f", *present)

    staged = git("diff", "--cached", "--stat").stdout.strip()
    if not staged:
        print("No staged changes — the dashboard is byte-identical to HEAD. "
              "Nothing to commit.")
        return 0
    print("Staged changes:")
    print(staged)

    if args.dry_run:
        print("\n--dry-run: stopping before commit. "
              "Unstage with `git reset HEAD`.")
        return 0

    stamp = dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    message = args.message or (
        f"update energy market dashboard ({stamp})\n\n"
        "Regenerated _images/energy_stats.html from "
        "_script/gather_energy_stats.py."
    )

    git("commit", "-m", message)
    print(git("log", "-1", "--oneline").stdout.strip())

    print(f"Pushing to {args.remote}/{branch} ...")
    push = git("push", args.remote, f"HEAD:{branch}", check=False)
    print((push.stdout or "").strip())
    if push.returncode != 0:
        print("Push failed. The commit is still local; fix the remote "
              "and re-run `git push`.", file=sys.stderr)
        return push.returncode

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
