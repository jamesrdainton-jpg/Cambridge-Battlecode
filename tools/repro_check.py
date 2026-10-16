"""Check that this computer reproduces the team's reference games exactly.

Usage: python tools/repro_check.py [--write]

Plays v5 vs v4 on every map from both sides (18 games, about a minute, via tools/arena.py) and compares
each game's winner, final round and gem totals with tools/repro_reference.txt. Games are deterministic,
so any difference means this computer's setup differs (cambc version, maps, SDK or bot code) and its
results can't be compared with the team's. Don't run it while a batch is running.

--write replaces the reference with this computer's games. Only do that deliberately (for example after
everyone has upgraded cambc) and commit the new reference.
"""
from __future__ import annotations

import argparse
import subprocess
import sys

from common import ROOT, git_commit

REFERENCE = ROOT / "tools" / "repro_reference.txt"
BOT_A, BOT_B = "v5", "v4"


def play() -> list[str]:
    out = subprocess.run([sys.executable, str(ROOT / "tools" / "arena.py"), BOT_A, BOT_B, "--tag=-repro"],
                         cwd=ROOT, check=False, capture_output=True, text=True).stdout
    # arena.py prints one line per game: map, sides, result, final round, gem totals, error-line count.
    return [" ".join(line.split()) for line in out.splitlines() if "round=" in line]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="replace the reference with this computer's games")
    args = parser.parse_args()
    games = play()
    if len(games) != 18 or any("MISSING" in g for g in games):
        raise SystemExit(f"only {sum('MISSING' not in g for g in games)} of 18 games finished; "
                         "is a batch running, or is cambc missing?")
    if args.write:
        REFERENCE.write_text(f"# {BOT_A} vs {BOT_B}, every map from both sides; written at commit "
                             f"{git_commit('bots', 'maps')}\n" + "\n".join(games) + "\n")
        print(f"wrote {len(games)} reference games to {REFERENCE}")
        return
    want = [line for line in REFERENCE.read_text().splitlines() if line and not line.startswith("#")]
    diffs = [(w, g) for w, g in zip(want, games) if w != g]
    if not diffs and len(want) == len(games):
        print(f"REPRODUCED: all {len(games)} reference games are identical on this computer")
        return
    print(f"MISMATCH in {len(diffs)} of {len(want)} games, so this computer's results aren't comparable:")
    for w, g in diffs:
        print(f"  expected: {w}\n  got:      {g}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
