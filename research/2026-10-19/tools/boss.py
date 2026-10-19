"""How teams attack boss camps (monoliths, stampede's elk group) in replays.
Usage: python -I boss.py DIR...   Prints per game/team: rounds of first/last boss hit, hits/casts by champion and distance."""
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
BOSS_MAPS = {"monolith", "rows", "contest", "stampede"}
for f in files(sys.argv[1:]):
    for label, data in RD.replays(f):
        g = per_turn(data, maps)
        if g is None or g["map"] not in BOSS_MAPS:
            continue
        cm = CAMPS[g["map"]]
        boss_groups = {c[3] for h, c in cm.items() if c[0] == "M"} or {c[3] for h, c in cm.items() if c[0] == "e"}
        if g["map"] == "stampede":
            boss_groups = {c[3] for h, c in cm.items() if c[0] == "e"}
        print(f"== {label[-40:]} {g['map']} rounds={g['rounds']}")
        for team in "ab":
            hits = Counter(); dist = Counter(); rounds = []; per_round = defaultdict(set); mono_hits = Counter()
            for champ, tl in zip(g["champs"][team], g["turns"][team]):
                pos = None
                for r, acts in tl:
                    for sub, a in acts:
                        if sub == 1:
                            pos = (a[0], a[1])
                        elif (sub == 2 and a[0] == 2) or (sub == 3 and a[1] == 2):
                            h = a[1] if sub == 2 else a[2]
                            c = cm.get(h)
                            if c and c[3] in boss_groups:
                                kind = "atk" if sub == 2 else "cast"
                                hits[(champ, kind)] += 1
                                rounds.append(r)
                                per_round[r // 10].add(champ)
                                if c[0] in "Me":
                                    mono_hits[kind] += 1
                                    if pos:
                                        dist[(kind, max(abs(pos[0]-c[1]), abs(pos[1]-c[2])))] += 1
            if not rounds:
                print(f"  {team} {','.join(g['champs'][team])}: no boss hits")
                continue
            rounds.sort()
            # attack windows: clusters of hits separated by >30 rounds
            wins = []
            s = rounds[0]; p = rounds[0]
            for r in rounds[1:]:
                if r - p > 30:
                    wins.append((s, p)); s = r
                p = r
            wins.append((s, p))
            maxc = max(len(v) for v in per_round.values())
            print(f"  {team} {','.join(g['champs'][team])}: boss hits {sum(hits.values())} windows {wins} max champs/10r {maxc}")
            print(f"     by champ: {dict(hits.most_common())}")
            print(f"     on M/elk by distance: {dict(sorted(dist.items()))}")
