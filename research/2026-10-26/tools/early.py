"""Usage: python -I research/2026-10-26/tools/early.py replays/platform/<dir>/match-group-*.zip
Early game per side: camp hits by camp kind in rounds 1-100 and 101-300, first buy round, shards by r100/r200."""
import io
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research/2026-10-25/tools"))
import replay30 as R

MAPS = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
KIND = {}
for f in (ROOT / "research/2026-10-25/data/mapdumps").glob("*.txt"):
    KIND[f.stem] = {int(h): k for _, h, k, x, y, gi in (l.split() for l in f.read_text(errors="replace").splitlines() if l.startswith("CAMPH"))}
hits = defaultdict(Counter); buys = defaultdict(list); shards = defaultdict(Counter); ngames = Counter()
for zp in sys.argv[1:]:
    outer = zipfile.ZipFile(zp)
    for n in sorted(outer.namelist()):
        inner = zipfile.ZipFile(io.BytesIO(outer.read(n)))
        side = "a" if "team-a.stdout" in inner.namelist() else "b"
        g = R.parse(inner.read("replay.repl26a"), MAPS)
        km = KIND.get(g["map"], {})
        for t in "ab":
            who = "us" if t == side else "them"
            ngames[who] += 1
            first = 9999
            for tl in g["turns"][t]:
                for r, acts in tl:
                    for s, a in acts:
                        ph = "r1-100" if r <= 100 else "r101-300" if r <= 300 else None
                        if s == 2 and a[0] == 2 and ph:
                            hits[(who, ph)][km.get(a[1], "?")] += 1
                        if s == 3 and a[1] == 2 and ph:
                            hits[(who, ph)]["cast:" + km.get(a[2], "?")] += 1
                        if s == 6:
                            first = min(first, r)
                            for lim in (100, 200, 300):
                                if r <= lim: shards[who][lim] += a[1]
            buys[who].append(first)
for k in sorted(hits):
    print(k, {x: round(v / ngames[k[0]], 1) for x, v in hits[k].most_common()})
for who in buys:
    b = sorted(buys[who]); print(who, "first buy median", b[len(b)//2], "shards/game by r100,200,300:", [round(shards[who][l]/ngames[who],1) for l in (100,200,300)])
