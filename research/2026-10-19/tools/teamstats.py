"""Per-team stats from any replays (rounds 1..R): bodies, camp hits and casts per 100 rounds per champion,
gold spent by r150/r300, cast share, hits by camp kind, and the game's finish round.
Usage: python -I teamstats.py [--team a] [--label X] DIR..."""
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
args = sys.argv[1:]
team_only = None; label = None
if "--team" in args:
    i = args.index("--team"); team_only = args[i + 1]; del args[i:i + 2]
if "--label" in args:
    i = args.index("--label"); label = args[i + 1].split(","); del args[i:i + 2]
R = 300
agg = Counter(); n = 0; kinds = Counter(); per_champ = defaultdict(Counter); bymap = defaultdict(list)
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
            n += 1
            c = Counter()
            c["bodies"] = len(g["champs"][team])
            for champ, tl in zip(g["champs"][team], g["turns"][team]):
                for r, acts in tl:
                    if r > R:
                        continue
                    for sub, a in acts:
                        if sub == 2 and a[0] == 2:
                            c["hits"] += 1; per_champ[champ]["hits"] += 1
                            kinds[cm.get(a[1], ("?",))[0]] += 1
                        elif sub == 3 and a[1] == 2:
                            c["casts"] += 1; per_champ[champ]["casts"] += 1
                        elif sub == 3:
                            per_champ[champ]["casts_other"] += 1
                        elif sub == 6:
                            c["g300"] += 30 * a[1]
                            if r <= 150:
                                c["g150"] += 30 * a[1]
                        elif sub == 8:
                            c["g300"] += 10 * a[1]
                            if r <= 150:
                                c["g150"] += 10 * a[1]
                        elif sub == 4:
                            c["recalls"] += 1
                    per_champ[champ]["turns"] += 1
            agg.update(c)
            bymap[g["map"]].append(g["rounds"])
print(f"{n} team-games (rounds 1-{R})")
print(f"  bodies {agg['bodies']/n:.2f}; per team per 100 rounds: camp hits {agg['hits']/n/(R/100):.0f}, camp casts {agg['casts']/n/(R/100):.0f}; "
      f"gold spent by r150 {agg['g150']/n:.0f}, by r300 {agg['g300']/n:.0f}")
t = sum(kinds.values())
print("  camp hits by kind:", {k: f"{100*v/t:.0f}%" for k, v in kinds.most_common()})
print("  per champion (per 100 turns): " + "; ".join(f"{k} hits {100*v['hits']/v['turns']:.0f} casts {100*v['casts']/v['turns']:.1f}+{100*v['casts_other']/v['turns']:.1f}" for k, v in sorted(per_champ.items(), key=lambda kv: -kv[1]['turns'])))
print("  finish rounds by map:", {m: sorted(v) for m, v in sorted(bymap.items())})
