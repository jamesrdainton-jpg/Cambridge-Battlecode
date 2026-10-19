import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys
from pathlib import Path
sys.path.insert(0, str(_ROOT / "tools"))
sys.path.insert(0, str(_HERE))
from replay_profile import per_turn
from ourgames import games
ROOT = _ROOT
maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
def firsts(g, team):
    fb = ft = fh = None
    for champ, tl in zip(g["champs"][team], g["turns"][team]):
        for r, acts in tl:
            for s, a in acts:
                if s == 6 and (fb is None or r < fb): fb = r
                if s == 5 and (ft is None or r < ft): ft = r
                if s == 2 and a[0] == 2 and (fh is None or r < fh): fh = r
    return fb, ft, fh
rows = []
for label, side, f in games(sys.argv[1:]):
    if side is None: continue
    g = per_turn(f["replay.repl26a"], maps)
    out = f[f"team-{side}.stdout"].decode(errors="replace").replace("\x00", "")
    st = [tuple(map(int, l.split()[1:4])) for l in out.splitlines() if l.startswith("STAT ")]
    win = st[-1][1] > st[-1][2]
    o = "b" if side == "a" else "a"
    rows.append((win, firsts(g, side), firsts(g, o)))
import statistics as S
for name, i in (("first camp hit", 2), ("first item", 0), ("first tribute", 1)):
    us = [r[1][i] for r in rows if r[1][i]]; th = [r[2][i] for r in rows if r[2][i]]
    print(f"{name:15} median us r{S.median(us):.0f}  them r{S.median(th):.0f}")
