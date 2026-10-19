"""Distance from caster to camp for targeted casts and basic attacks, by champion (excluding boss maps).
Usage: python -I castrange.py [--label X] DIR..."""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(_ROOT / "tools"))
sys.path.insert(0, str(_HERE))
import replay_decode as RD
from replay_profile import per_turn, files
from targets import CAMPS
ROOT = _ROOT
maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
args = sys.argv[1:]; label = None
if "--label" in args:
    i = args.index("--label"); label = args[i+1].split(","); del args[i:i+2]
cast = defaultdict(Counter); atk = defaultdict(Counter)
for f in files(args):
    for lab, data in RD.replays(f):
        g = per_turn(data, maps)
        if g is None or g["map"] in ("stampede", "rows", "contest", "monolith"):
            continue
        cm = CAMPS[g["map"]]
        for team in "ab":
            if label and not all(x in g["champs"][team] for x in label):
                continue
            for champ, tl in zip(g["champs"][team], g["turns"][team]):
                pos = None
                for r, acts in tl:
                    for sub, a in acts:
                        if sub == 1:
                            pos = (a[0], a[1])
                        elif pos and sub == 3 and a[1] == 2 and a[2] in cm:
                            c = cm[a[2]]
                            cast[champ][min(max(abs(pos[0]-c[1]), abs(pos[1]-c[2])), 6)] += 1
                        elif pos and sub == 2 and a[0] == 2 and a[1] in cm:
                            c = cm[a[1]]
                            atk[champ][min(max(abs(pos[0]-c[1]), abs(pos[1]-c[2])), 6)] += 1
for champ in sorted(cast, key=lambda c: -sum(cast[c].values())):
    c = cast[champ]; t = sum(c.values())
    a = atk[champ]; ta = sum(a.values())
    print(f"  {champ:9} casts on camps n={t:5} " + " ".join(f"d{k}:{100*v/t:.0f}%" for k, v in sorted(c.items())) +
          f"  | basic attacks n={ta}, casts per basic attack {t/max(1,ta):.2f}")
