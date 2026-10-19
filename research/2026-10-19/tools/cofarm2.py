"""Grouped-farming share by round window and by map (pros), plus the mean distance between teammates.
Usage: python -I cofarm2.py DIR..."""
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
label = None
args = sys.argv[1:]
if "--label" in args:
    i = args.index("--label"); label = args[i+1].split(","); del args[i:i+2]
team_only = None
if "--team" in args:
    i = args.index("--team"); team_only = args[i+1]; del args[i:i+2]
by_round = defaultdict(Counter); by_map = defaultdict(Counter); near = defaultdict(list)
for f in files(args):
    for lab, data in RD.replays(f):
        g = per_turn(data, maps)
        if g is None:
            continue
        cm = CAMPS[g["map"]]
        for team in "ab":
            if team_only and team != team_only:
                continue
            if label and not all(x in g["champs"][team] for x in label):
                continue
            buckets = defaultdict(lambda: defaultdict(int))
            pos = defaultdict(dict)
            for champ, tl in zip(g["champs"][team], g["turns"][team]):
                for r, acts in tl:
                    for sub, a in acts:
                        if sub == 1:
                            pos[champ][r] = (a[0], a[1])
                        if (sub == 2 and a[0] == 2) or (sub == 3 and a[1] == 2):
                            h = a[1] if sub == 2 else a[2]
                            c = cm.get(h)
                            if c:
                                buckets[(c[3], r // 10)][champ] += 1
            for (grp, b), ch in buckets.items():
                n = min(len(ch), 3)
                w = sum(ch.values())
                by_round[min(b // 10, 6)][n] += w
                by_map[g["map"]][n] += w
            # mean number of teammates within 4 tiles, sampled every 10 rounds 50..400
            champs = list(pos)
            for r in range(50, 401, 10):
                cur = {}
                for c in champs:
                    rr = max((x for x in pos[c] if x <= r), default=None)
                    if rr is not None and r - rr < 15:
                        cur[c] = pos[c][rr]
                for c, p in cur.items():
                    near[g["map"]].append(sum(1 for o, q in cur.items() if o != c and max(abs(p[0]-q[0]), abs(p[1]-q[1])) <= 4))
def show(c):
    t = sum(c.values())
    return f"solo {100*c[1]/t:3.0f}%  pair {100*c[2]/t:3.0f}%  3+ {100*c[3]/t:3.0f}%"
print("by round window (x100):")
for k in sorted(by_round):
    print(f"  r{k*100}-{k*100+99}: {show(by_round[k])}")
print("by map: (mean teammates within 4 tiles, rounds 50-400)")
for m in sorted(by_map):
    v = near[m]
    print(f"  {m:12} {show(by_map[m])}   near4={sum(v)/max(1,len(v)):.2f}")
