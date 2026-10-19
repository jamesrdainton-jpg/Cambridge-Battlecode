"""Robust death count: a champion with >= 55 consecutive rounds without move/attack/cast/recall/tribute records,
followed by activity (respawn). Also counts deaths per 100 rounds per team.
Usage: python -I deaths2.py [--label X] [--team a] DIR..."""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(_ROOT / "tools"))
sys.path.insert(0, str(_HERE))
import replay_decode as RD
from replay_profile import per_turn, files
ROOT = _ROOT
maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
args = sys.argv[1:]; label = team_only = None
if "--label" in args:
    i = args.index("--label"); label = args[i+1].split(","); del args[i:i+2]
if "--team" in args:
    i = args.index("--team"); team_only = args[i+1]; del args[i:i+2]
tot_d = 0; tot_r = 0; n = 0; per = []
for f in files(args):
    for lab, data in RD.replays(f):
        g = per_turn(data, maps)
        if g is None:
            continue
        for team in "ab":
            if team_only and team != team_only:
                continue
            if label and not all(x in g["champs"][team] for x in label):
                continue
            d = 0
            seen = set()
            for champ, tl in zip(g["champs"][team], g["turns"][team]):
                last = None
                for r, acts in tl:
                    if any(s in (1, 2, 3, 4, 5) for s, _ in acts):
                        if last is not None and r - last >= 55:
                            # C&I die together: count the pair once
                            key = (r // 5, "CI") if champ in ("Cassi", "Issac") else (r, champ)
                            if key not in seen:
                                seen.add(key)
                                d += 1
                        last = r
            n += 1
            tot_d += d
            tot_r += g["rounds"]
            per.append((g["map"], d, g["rounds"]))
print(f"{n} team-games: deaths {tot_d}, per team per 100 rounds {100 * tot_d / max(1, tot_r):.2f}")
