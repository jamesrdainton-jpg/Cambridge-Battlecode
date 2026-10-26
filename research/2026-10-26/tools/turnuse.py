"""Usage: python -I research/2026-10-26/tools/acts.py replays/platform/<dir>/match-group-*.zip
Turn use per side: share of champion-turns with a hit (attack or offensive cast on camp/champion), move only,
nothing (dead, recalling, tributing, waiting). HoR dash landings: camp spawn tiles within 1."""
import io
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research/2026-10-25/tools"))
import replay30 as R

MAPS = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
CAMPS = {}
for f in (ROOT / "research/2026-10-25/data/mapdumps").glob("*.txt"):
    CAMPS[f.stem] = [(int(x), int(y)) for _, h, k, x, y, gi in (l.split() for l in f.read_text(errors="replace").splitlines() if l.startswith("CAMPH"))]
use = defaultdict(Counter)
dash = Counter()
first_hit = defaultdict(list)
for zp in sys.argv[1:]:
    outer = zipfile.ZipFile(zp)
    for n in sorted(outer.namelist()):
        inner = zipfile.ZipFile(io.BytesIO(outer.read(n)))
        side = "a" if "team-a.stdout" in inner.namelist() else "b"
        g = R.parse(inner.read("replay.repl26a"), MAPS)
        camps = CAMPS.get(g["map"], [])
        for t in "ab":
            who = "us" if t == side else "them"
            for i, name in enumerate(g["champs"][t]):
                fh = None
                for r, acts in g["turns"][t][i]:
                    subs = {s for s, _ in acts}
                    hit = any(s == 2 or (s == 3 and a[1] in (1, 2)) for s, a in acts)
                    if hit:
                        use[who]["hit"] += 1
                        if fh is None: fh = r
                    elif 1 in subs: use[who]["move"] += 1
                    elif subs & {4, 5}: use[who]["recall/tribute"] += 1
                    elif subs - {0, 6, 8, 10}: use[who]["other"] += 1
                    else: use[who]["nothing"] += 1
                    if name == "HeartOfRuin":
                        for s, a in acts:
                            if s == 3 and a[0] == 1 and a[3] >= 0:
                                nc = sum(1 for (x, y) in camps if max(abs(x - a[3]), abs(y - a[4])) <= 1)
                                dash["dashes"] += 1
                                dash["camps_in_r1_total"] += nc
                                dash["lands_on_camps"] += nc > 0
                                dash["2+camps"] += nc >= 2
                first_hit[who].append(fh if fh else 9999)
for who, c in use.items():
    tot = sum(c.values())
    print(who, "  ".join(f"{k} {100*v/tot:.0f}%" for k, v in c.most_common()), f"(n={tot})")
    fh = sorted(first_hit[who]); print("   median first hit round", fh[len(fh)//2])
print("HoR dashes", dict(dash), "maps with camp dumps:", sum(1 for _ in CAMPS))
