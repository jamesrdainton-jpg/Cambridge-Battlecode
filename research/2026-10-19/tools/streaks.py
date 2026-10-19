import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys
sys.path.insert(0, sys.argv[0].rsplit('/',1)[0])
from analyze import load, lines_of
from collections import Counter, defaultdict
run, bot = sys.argv[1], sys.argv[2]
want = sys.argv[3] if len(sys.argv) > 3 else "farm:-"
games = load(run)
per_map = Counter(); streaks = []
for g in games:
    for side in ("a","b"):
        if g[side] != bot: continue
        cur = {}
        for p in lines_of(g["text"][side], "T"):
            r, name, act, sub = int(p[2]), p[3], p[4], p[5]
            key = act + ":" + sub
            if key == want:
                per_map[g["map"]] += 1
                s = cur.get(name)
                if s and s[1] == r - 1 and s[3] == (p[9], p[10]):
                    s[1] = r; s[2] += 1
                else:
                    s = cur[name] = [r, r, 1, (p[9], p[10]), g["map"], name]
                    streaks.append(s)
print("per map", per_map.most_common())
lens = Counter(min(s[2], 50) for s in streaks)
print("streak length histogram (capped 50):", sorted(lens.items()))
long = sorted(streaks, key=lambda s: -s[2])[:25]
for s in long:
    print(f"  {s[4]:12} {s[5]:9} r{s[0]}-{s[1]} len={s[2]} at {s[3]}")
