"""Per-map results of one or more arena runs (matches/arena/<run>), from the first-named bot's point of view.

Usage: python research/2026-10-25/tools/permap.py RUN [RUN ...]
       e.g. permap.py x13a_s1-vs-v12_s1 x13a_s2-vs-v12_s2
Prints, per map: wins/games for the run's first bot, its gem margin (from STAT lines), and the mean finishing round.
"""
from __future__ import annotations

import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RESULT = re.compile(r"\[\+\]\s+(.*?)\s{2,}(\S+) vs (\S+)\s+(\S+)\s+Round (\d+)")


def stat(bundle: Path, team: str):
    try:
        text = zipfile.ZipFile(bundle).read(f"team-{team}.stdout").decode(errors="replace").replace("\x00", "")
    except (KeyError, FileNotFoundError, zipfile.BadZipFile):
        return None
    rows = [line.split() for line in text.splitlines() if line.startswith("STAT ")]
    return tuple(map(int, rows[-1][1:4])) if rows else None


def main() -> None:
    per = defaultdict(lambda: [0, 0, 0, 0])  # wins, games, gem margin, rounds
    for run in sys.argv[1:]:
        base = ROOT / "matches" / "arena" / run
        me = run.split("-vs-")[0]
        log = (base / "batch.log").read_text(errors="replace")
        for line in log.splitlines():
            m = RESULT.search(line)
            if not m:
                continue
            status, a, b, mp, rnd = m.groups()
            side = "a" if a == me else "b"
            bundle = base / f"{mp}-{1 if side == 'a' else 2}.repl26a"
            won = ("TEAM A WIN" in status and side == "a") or ("TEAM B WIN" in status and side == "b")
            margin = 0
            sa, sb = stat(bundle, "a"), stat(bundle, "b")
            if sa:
                margin = (sa[1] - sa[2]) if side == "a" else (sa[2] - sa[1])
            elif sb:
                margin = (sb[2] - sb[1]) if side == "a" else (sb[1] - sb[2])
            p = per[mp]
            p[0] += won
            p[1] += 1
            p[2] += margin
            p[3] += int(rnd)
    tw = tg = 0
    print(f"{'map':24} wins   gem margin  mean round")
    for mp in sorted(per):
        w, g, mg, r = per[mp]
        tw += w
        tg += g
        print(f"{mp:24} {w:>2}/{g:<2} {mg:>+11}  {r // max(1, g):>10}")
    print(f"{'total':24} {tw}/{tg}")


if __name__ == "__main__":
    main()
