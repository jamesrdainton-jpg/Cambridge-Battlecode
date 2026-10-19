"""HP lost on turns with no visible enemy (no I F line) and not in camp mode, per run.
Usage: python unseen.py RUN BOT"""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys
sys.path.insert(0, str(_HERE))
from analyze import load, lines_of
from collections import Counter, defaultdict
run, bot = sys.argv[1], sys.argv[2]
loss = Counter(); turns = Counter(); bymap = Counter(); deaths_after = 0; deaths = 0; streak_deaths = Counter()
for g in load(run):
    for side in "ab":
        if g[side] != bot:
            continue
        T = lines_of(g["text"][side], "T")
        Fr = {(int(p[2]), p[3]) for p in lines_of(g["text"][side], "F")}
        D = [(int(p[2]), p[3]) for p in lines_of(g["text"][side], "D")]
        last = {}
        hits = defaultdict(list)
        for p in T:
            r, name, act = int(p[2]), p[3], p[4]
            if act == "dead":
                last.pop(name, None)
                continue
            hp = float(p[6])
            prev = last.get(name)
            last[name] = (r, hp, act)
            if prev is None or prev[0] != r - 1 or hp >= prev[1] - 0.5:
                continue
            seen = (r, name) in Fr or (r - 1, name) in Fr
            key = ("seen enemy" if seen else "camp mode" if act in ("camp", "wait") or prev[2] in ("camp", "wait") else f"unseen:{act}")
            loss[key] += prev[1] - hp
            turns[key] += 1
            if key.startswith("unseen"):
                bymap[g["map"]] += prev[1] - hp
                hits[name].append(r)
        for r, name in D:
            deaths += 1
            if any(r - 10 <= x <= r for x in hits[name]):
                deaths_after += 1
tot = sum(loss.values())
print(f"{bot} in {run}: HP lost {tot:.0f}")
for k, v in sorted(loss.items(), key=lambda kv: -kv[1]):
    print(f"  {k:22} {v:9.0f} ({100*v/tot:4.1f}%) over {turns[k]} turns")
print("unseen-damage HP by map:", {k: int(v) for k, v in bymap.most_common()})
print(f"deaths with unseen damage in the 10 rounds before: {deaths_after}/{deaths}")
