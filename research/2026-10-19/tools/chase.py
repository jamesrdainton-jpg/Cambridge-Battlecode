"""For engagements whose decision at contact was chase (or ret), describe the deaths.
Usage: python chase.py RUN BOT [chase|ret]"""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys
sys.path.insert(0, str(_HERE))
from analyze import load, lines_of
from collections import Counter, defaultdict
run, bot, want = sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "chase"
champ = Counter(); grew = Counter(); enemies_c = Counter(); hpfrac = []; n = 0; dur = []; allies_c = Counter(); first_hit = Counter()
for g in load(run):
    for side in "ab":
        if g[side] != bot:
            continue
        D = [(int(p[2]), p[3]) for p in lines_of(g["text"][side], "D")]
        eng = defaultdict(list)
        for p in lines_of(g["text"][side], "F"):
            r, name = int(p[2]), p[3]
            near = [t.split(":") for t in p[13:]]
            s = {"r": r, "ratio": float(p[4]), "hp": float(p[5]) / float(p[6]), "dec": p[11].split("/")[-1],
                 "allies": int(p[12].split("=")[1]), "near": near, "dmin": min([int(x[1]) for x in near] or [99])}
            L = eng[name]
            if L and r - L[-1][-1]["r"] <= 2:
                L[-1].append(s)
            else:
                L.append([s])
        for name, eps in eng.items():
            for ep in eps:
                c = next((s for s in ep if s["dmin"] <= 4), None)
                if c is None or c["dec"] != want:
                    continue
                died = next((r for r, nm in D if nm == name and ep[0]["r"] <= r <= ep[-1]["r"] + 6), None)
                if died is None:
                    continue
                n += 1
                champ[name] += 1
                n0 = len(c["near"]); nmax = max(len(s["near"]) for s in ep)
                grew["more enemies appeared" if nmax > n0 else "same enemies"] += 1
                enemies_c[n0] += 1
                allies_c[c["allies"]] += 1
                hpfrac.append(c["hp"])
                dur.append(died - c["r"])
print(f"{bot} {run}: {n} deaths after '{want}' at contact")
print(" by champion:", dict(champ.most_common()))
print(" enemies at contact:", dict(sorted(enemies_c.items())), " allies within 7 at contact:", dict(sorted(allies_c.items())))
print(" ", dict(grew))
hpfrac.sort(); dur.sort()
if n:
    print(f"  our health at contact: median {hpfrac[n//2]:.2f}, <50%: {sum(h < 0.5 for h in hpfrac)}")
    print(f"  rounds from contact to death: median {dur[n//2]}, quartiles {dur[n//4]}..{dur[3*n//4]}")
