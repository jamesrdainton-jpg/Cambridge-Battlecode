"""How many champions hit the same camp group together (hits within a 10-round bucket), per team type.
Usage: python -I cofarm.py [--team a] [--label X] DIR..."""
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
args = sys.argv[1:]; team_only = label = None
if "--team" in args:
    i = args.index("--team"); team_only = args[i+1]; del args[i:i+2]
if "--label" in args:
    i = args.index("--label"); label = args[i+1].split(","); del args[i:i+2]
by_kind = defaultdict(Counter)  # group kind string -> champs-per-bucket histogram weighted by hits
ci_sep = []
for f in files(args):
    for lab, data in RD.replays(f):
        g = per_turn(data, maps)
        if g is None:
            continue
        cm = CAMPS[g["map"]]
        gkind = defaultdict(str)
        for h, c in cm.items():
            gkind[c[3]] += c[0]
        for team in "ab":
            if team_only and team != team_only:
                continue
            if label and not all(x in g["champs"][team] for x in label):
                continue
            buckets = defaultdict(lambda: defaultdict(int))
            pos = {}
            for champ, tl in zip(g["champs"][team], g["turns"][team]):
                for r, acts in tl:
                    for sub, a in acts:
                        if sub == 1:
                            pos.setdefault(champ, {})[r] = (a[0], a[1])
                        if (sub == 2 and a[0] == 2) or (sub == 3 and a[1] == 2):
                            h = a[1] if sub == 2 else a[2]
                            c = cm.get(h)
                            if c:
                                buckets[(c[3], r // 10)][champ] += 1
            for (grp, b), ch in buckets.items():
                k = "".join(sorted(set(gkind[grp])))
                n = len(ch)
                by_kind[k][min(n, 4)] += sum(ch.values())
            if "Cassi" in pos and "Issac" in pos:
                for r in range(50, 400, 10):
                    pc = max((rr for rr in pos["Cassi"] if rr <= r), default=None)
                    pi = max((rr for rr in pos["Issac"] if rr <= r), default=None)
                    if pc and pi:
                        a, b2 = pos["Cassi"][pc], pos["Issac"][pi]
                        ci_sep.append(max(abs(a[0]-b2[0]), abs(a[1]-b2[1])))
tot = Counter()
for k, c in by_kind.items():
    tot.update(c)
def show(c):
    t = sum(c.values())
    return " ".join(f"{n}:{100*c[n]/t:.0f}%" for n in sorted(c)) + f" (n={t})"
print("share of camp hits by number of teammates hitting the same group in that 10-round window:", show(tot))
for k in sorted(by_kind, key=lambda k: -sum(by_kind[k].values()))[:8]:
    print(f"  group kinds {k:6}: {show(by_kind[k])}")
if ci_sep:
    ci_sep.sort()
    print(f"Cassi-Issac distance: median {ci_sep[len(ci_sep)//2]}, <=3: {100*sum(d<=3 for d in ci_sep)/len(ci_sep):.0f}%")
