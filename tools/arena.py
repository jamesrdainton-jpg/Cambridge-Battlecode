"""Play bots against each other on every map, from both sides, using cambc run-batch.

Usage: python tools/arena.py BOT_A BOT_B [--maps a,b,c] [--jobs N] [--rounds N] [--repeat N] [--logs]

Prints one line per game and a summary. Bots that print "STAT <round> <ally_gems> <enemy_gems>"
lines get their latest gem totals reported. Replay bundles (which hold each team's stdout) are kept
under matches/arena/<BOT_A>-vs-<BOT_B>/.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from common import find_cambc

ROOT = Path(__file__).resolve().parent.parent
CAMBC = find_cambc()
RESULT = re.compile(r"\[\+\]\s+(.*?)\s{2,}(\S+) vs (\S+)\s+(\S+)\s+Round (\d+)/\d+")


def all_maps() -> list[str]:
    return sorted(p.stem for p in (ROOT / "maps").glob("*.map26a"))


def team_stdout(bundle: Path, team: str) -> str:
    try:
        with zipfile.ZipFile(bundle) as z:
            return z.read(f"team-{team}.stdout").decode(errors="replace").replace("\x00", "")
    except (OSError, KeyError, zipfile.BadZipFile):
        return ""


def last_stat(text: str):
    found = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("STAT "):
            parts = line.split()
            if len(parts) >= 4:
                found = (int(parts[1]), int(parts[2]), int(parts[3]))
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bot_a")
    parser.add_argument("bot_b")
    parser.add_argument("--maps", default="")
    parser.add_argument("--jobs", type=int, default=18)
    parser.add_argument("--rounds", type=int, default=0)
    parser.add_argument("--one-side", action="store_true", help="only play BOT_A as team A")
    parser.add_argument("--logs", action="store_true", help="print error lines from bot stdout")
    parser.add_argument("--tag", default="")
    args = parser.parse_args()

    maps = args.maps.split(",") if args.maps else all_maps()
    name = f"{args.bot_a}-vs-{args.bot_b}{args.tag}"
    base = ROOT / "matches" / "arena" / name
    shutil.rmtree(base, ignore_errors=True)
    base.mkdir(parents=True, exist_ok=True)
    for old in base.glob("*.repl26a"):
        old.unlink()

    games = []
    for m in maps:
        games.append((args.bot_a, args.bot_b, m, f"{m}-1.repl26a"))
        if not args.one_side:
            games.append((args.bot_b, args.bot_a, m, f"{m}-2.repl26a"))
    manifest = base / "manifest.txt"
    manifest.write_text("".join(f"../../../bots/{a} ../../../bots/{b} ../../../maps/{m}.map26a {r}\n"
                                for a, b, m, r in games))
    cmd = [str(CAMBC), "run-batch", str(manifest), "--jobs", str(args.jobs), "--color", "never"]
    if args.rounds:
        cmd += ["--rounds", str(args.rounds)]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out = proc.stdout + proc.stderr
    (base / "batch.log").write_text(out)

    results = {}
    for line in out.splitlines():
        m = RESULT.search(line)
        if m:
            status, a, b, mp, rnd = m.groups()
            results.setdefault((a, b, mp), (status, int(rnd)))

    wins = {args.bot_a: 0, args.bot_b: 0}
    gems = {args.bot_a: 0, args.bot_b: 0}
    total = 0
    for a, b, mp, replay in games:
        bundle = base / replay
        status, rnd = results.get((a, b, mp), ("MISSING", 0))
        winner = None
        if "TEAM A WIN" in status:
            winner = a
        elif "TEAM B WIN" in status:
            winner = b
        if winner:
            wins[winner] += 1
        total += 1
        out_a, out_b = team_stdout(bundle, "a"), team_stdout(bundle, "b")
        sa, sb = last_stat(out_a), last_stat(out_b)
        gem_txt = ""
        if sa:
            gem_txt = f"gems~{sa[1]}-{sa[2]}@{sa[0]}"
            gems[a] += sa[1]
            gems[b] += sa[2]
        elif sb:
            gem_txt = f"gems~{sb[2]}-{sb[1]}@{sb[0]}"
            gems[a] += sb[2]
            gems[b] += sb[1]
        errs = sum(1 for line in (out_a + out_b).splitlines() if "error" in line.lower())
        print(f"{mp:10} A={a:<9} B={b:<9} {status:<22} round={rnd:>4} {gem_txt:<22} errlines={errs}")
        if args.logs:
            for side, text in (("a", out_a), ("b", out_b)):
                shown = 0
                for line in text.splitlines():
                    low = line.lower()
                    if ("error" in low or "traceback" in low or "File " in line) and shown < 12:
                        print(f"    [{side}] {line.strip()[:240]}")
                        shown += 1
    print()
    for bot in (args.bot_a, args.bot_b):
        print(f"{bot:<12} wins {wins[bot]:>2}/{total}  gems(sum of STAT) {gems[bot]:>6}")


if __name__ == "__main__":
    main()
