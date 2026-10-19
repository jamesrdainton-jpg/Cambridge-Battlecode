"""Calibration at contact: per engagement, the ratio at the first snapshot with an enemy within 4 tiles.
Usage: python contact.py RUN BOT"""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys
sys.path.insert(0, str(_HERE))
from analyze import load, lines_of
from collections import Counter, defaultdict
B = [0, 0.5, 0.9, 1.3, 2.0, 4.0, 1e9]
def bk(r):
    for i in range(len(B) - 1):
        if B[i] <= r < B[i + 1]:
            return i
run, bot = sys.argv[1], sys.argv[2]
tab = defaultdict(Counter); dec = defaultdict(Counter); dec_death = Counter(); nd = 0; deaths_total = 0
solo = defaultdict(Counter)
for g in load(run):
    for side, other in (("a", "b"), ("b", "a")):
        if g[side] != bot:
            continue
        ours = [(int(p[2]), p[3]) for p in lines_of(g["text"][side], "D")]
        theirs = [(int(p[2]), p[3]) for p in lines_of(g["text"][other], "D")]
        deaths_total += len(ours)
        eng = defaultdict(list)
        for p in lines_of(g["text"][side], "F"):
            r, name = int(p[2]), p[3]
            near = [t.split(":") for t in p[13:]]
            snap = {"r": r, "ratio": float(p[4]), "hp": float(p[5]) / float(p[6]), "act": p[11],
                    "allies": int(p[12].split("=")[1]), "dmin": min([int(x[1]) for x in near] or [99]),
                    "kinds": {x[0] for x in near}, "n": len(near)}
            L = eng[name]
            if L and r - L[-1][-1]["r"] <= 2:
                L[-1].append(snap)
            else:
                L.append([snap])
        for name, eps in eng.items():
            for ep in eps:
                c = next((s for s in ep if s["dmin"] <= 4), None)
                if c is None:
                    continue
                s0, e0 = ep[0]["r"], ep[-1]["r"]
                died = any(n == name and s0 <= r <= e0 + 6 for r, n in ours)
                kinds = set().union(*[s["kinds"] for s in ep])
                kill = any(n in kinds and s0 <= r <= e0 + 6 for r, n in theirs)
                i = bk(c["ratio"])
                tab[i]["n"] += 1; tab[i]["died"] += died; tab[i]["kill"] += kill
                key = ("1v1" if c["n"] == 1 and c["allies"] == 0 else "outnumbered" if c["n"] > c["allies"] + 1 else "even/ahead")
                solo[key]["n"] += 1; solo[key]["died"] += died; solo[key]["kill"] += kill
                d = c["act"].split("/")[1] if "/" in c["act"] else "-"
                dec[i][d] += 1
                if died:
                    nd += 1
                    dec_death[d] += 1
print(f"{bot}: deaths {deaths_total}, of which within a contact engagement: {nd}")
print(f"{'ratio@contact':>14} {'n':>5} {'died%':>6} {'kill%':>6}  decision at contact")
for i in range(len(B) - 1):
    t = tab.get(i)
    if not t:
        continue
    lab = f"{B[i]}-{B[i+1] if B[i+1] < 1e8 else 'inf'}"
    print(f"{lab:>14} {t['n']:5} {100*t['died']/t['n']:6.1f} {100*t['kill']/t['n']:6.1f}  {dict(dec[i].most_common())}")
print("by situation at contact:", {k: (v['n'], f"died {100*v['died']/v['n']:.0f}%", f"kill {100*v['kill']/v['n']:.0f}%") for k, v in solo.items()})
print("decision at contact for engagements we died in:", dict(dec_death))
