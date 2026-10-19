"""Gold earned vs spent vs carried for an instrumented run with gold in T lines (team a, unopposed runs).
Usage: python -I earned.py RUN BOT"""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(_ROOT / "tools"))
sys.path.insert(0, str(_HERE))
import replay_decode as RD
from analyze import load, lines_of
from replay_profile import per_turn
ROOT = _ROOT
maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
run, bot = sys.argv[1], sys.argv[2]
tot = defaultdict(float); n = 0
for g in load(run):
    for side in "ab":
        if g[side] != bot:
            continue
        n += 1
        data = open(g["replay"], "rb").read()
        import zipfile, io
        rep = zipfile.ZipFile(g["replay"]).read("replay.repl26a")
        pt = per_turn(rep, maps)
        for R in (150, 300):
            spent = 0
            for champ, tl in zip(pt["champs"][side], pt["turns"][side]):
                for r, acts in tl:
                    if r > R:
                        break
                    for sub, a in acts:
                        if sub == 6:
                            spent += 30 * a[1]
                        elif sub == 8:
                            spent += 10 * a[1]
            carried = {}
            for p in lines_of(g["text"][side], "T"):
                if int(p[2]) <= R and p[4] != "dead" and len(p) > 11:
                    carried[p[3]] = int(p[11])
            tot[f"spent{R}"] += spent
            tot[f"carried{R}"] += sum(carried.values())
for R in (150, 300):
    s, c = tot[f"spent{R}"] / n, tot[f"carried{R}"] / n
    print(f"by r{R}: spent {s:.0f}, carried unspent {c:.0f}, earned ~{s + c:.0f} per team ({n} games)")
