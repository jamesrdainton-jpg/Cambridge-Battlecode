"""Unspent gold from instrumented T lines (field 11 = carried gold).
Usage: python gold.py RUN BOT"""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys
from collections import defaultdict

sys.path.insert(0, str(_HERE))
from analyze import load, lines_of  # noqa: E402

run, bot = sys.argv[1], sys.argv[2]
CHECK = (100, 200, 300, 400, 500)
rows = []
tot_turns = 0
rich_turns = 0  # champion-turns alive carrying >= 150 gold
rich300 = 0
per_champ = defaultdict(lambda: [0, 0])
for g in load(run):
    for side in "ab":
        if g[side] != bot:
            continue
        at = defaultdict(dict)
        for p in lines_of(g["text"][side], "T"):
            if len(p) < 12 or p[4] == "dead":
                continue
            r, name, gold = int(p[2]), p[3], int(p[11])
            tot_turns += 1
            per_champ[name][0] += 1
            if gold >= 150:
                rich_turns += 1
                per_champ[name][1] += 1
            if gold >= 300:
                rich300 += 1
            for c in CHECK:
                if r <= c:
                    at[c][name] = gold
        team = {c: sum(at[c].values()) for c in CHECK}
        rows.append((g["map"], g["round"], team))
print(f"{bot} {run}: alive champion-turns carrying >=150 gold: {100 * rich_turns / max(1, tot_turns):.1f}%, >=300: {100 * rich300 / max(1, tot_turns):.1f}%")
print("  by champion (% of alive turns with >=150 gold):", {k: f"{100 * v[1] / v[0]:.0f}%" for k, v in per_champ.items()})
print("  team unspent gold at rounds " + " ".join(map(str, CHECK)))
for m, rnd, team in sorted(rows):
    print(f"  {m:12} r{rnd:<5} " + " ".join(f"{team[c]:5}" for c in CHECK))
