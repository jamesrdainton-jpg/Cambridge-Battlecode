"""Print the fight snapshots before deaths whose ratio at contact was >= LO.
Usage: python deathtrace.py RUN BOT LO [N]"""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys
sys.path.insert(0, str(_HERE))
from analyze import load, lines_of
run, bot, lo = sys.argv[1], sys.argv[2], float(sys.argv[3])
N = int(sys.argv[4]) if len(sys.argv) > 4 else 8
shown = 0
for g in load(run):
    for side, other in (("a", "b"), ("b", "a")):
        if g[side] != bot or shown >= N:
            continue
        F = lines_of(g["text"][side], "F")
        T = lines_of(g["text"][side], "T")
        for p in lines_of(g["text"][side], "D"):
            r, name = int(p[2]), p[3]
            snaps = [q for q in F if q[3] == name and r - 14 <= int(q[2]) < r]
            c = next((q for q in snaps if min([int(t.split(':')[1]) for t in q[13:]] or [99]) <= 4), None)
            if c is None or float(c[4]) < lo or shown >= N:
                continue
            shown += 1
            print(f"--- {g['map']} {name} died r{r} (bot side {side})")
            turns = {int(q[2]): q for q in T if q[3] == name and r - 14 <= int(q[2]) < r}
            for rr in sorted(turns):
                q = turns[rr]
                f = next((s for s in snaps if int(s[2]) == rr), None)
                fx = f"ratio={f[4]} {f[11]} {f[12]} {' '.join(f[13:])}" if f else ""
                print(f"   r{rr} {q[4]:9} {q[5]:3} hp={q[6]}/{q[7]} at {q[9]},{q[10]}  {fx}")
