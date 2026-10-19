"""Compare decoded per-champion turns (hit/move) with the instrumented I T lines for team a.
Usage: python -I validate6.py RUN MAP"""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys, zipfile
from pathlib import Path
sys.path.insert(0, str(_ROOT / "tools"))
sys.path.insert(0, str(_HERE))
from replay_profile import per_turn
ROOT = _ROOT
SP = _WORK
maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
run, mp = sys.argv[1], sys.argv[2]
f = next((SP / "runs" / run).glob(f"{mp}-1.repl26a"))
z = zipfile.ZipFile(f)
g = per_turn(z.read("replay.repl26a"), maps)
text = z.read("team-a.stdout").decode(errors="replace").replace("\x00", "")
log = {}
for line in text.splitlines():
    p = line.split()
    if line.startswith("I T "):
        log[(int(p[2]), p[3].capitalize())] = p[5]
names = {"Cassi": "Cassi", "Issac": "Issac"}
agree = dis = 0
ex = []
for champ, tl in zip(g["champs"]["a"], g["turns"]["a"]):
    for r, acts in tl:
        k = (r, champ)
        if k not in log:
            continue
        sub = log[k]
        hit = any(s == 2 for s, _ in acts)
        moved = any(s == 1 for s, _ in acts)
        lh = "h" in sub
        lm = "m" in sub
        if hit == lh and (moved == lm or not moved):
            agree += 1
        else:
            dis += 1
            if len(ex) < 5:
                ex.append((k, sub, acts))
print(g["champs"], f"agree {agree} disagree {dis}", ex)
