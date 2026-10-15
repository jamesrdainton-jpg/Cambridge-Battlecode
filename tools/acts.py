"""Summarise the DEBUG activity tallies ("ACTS" lines) from an arena run.

Usage: python tools/acts.py matches/arena/<run> [--round 400] [--team a]
"""
from __future__ import annotations

import argparse
import zipfile
from collections import Counter
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument("--round", type=int, default=400)
    parser.add_argument("--team", default="a")
    args = parser.parse_args()
    grand = Counter()
    for bundle in sorted(Path(args.run).glob("*.repl26a")):
        with zipfile.ZipFile(bundle) as z:
            text = z.read(f"team-{args.team}.stdout").decode(errors="replace").replace("\x00", "")
        totals = Counter()
        for line in text.splitlines():
            line = line.strip()
            if "ACTS" in line and line.startswith(f"r{args.round} "):
                for kv in line.split("ACTS", 1)[1].split():
                    k, v = kv.split("=")
                    totals[k] += int(v)
        grand.update(totals)
        print(f"{bundle.stem:14} " + " ".join(f"{k}={v}" for k, v in sorted(totals.items())))
    print(f"{'TOTAL':14} " + " ".join(f"{k}={v}" for k, v in sorted(grand.items())))


if __name__ == "__main__":
    main()
