"""Usage: python -I research/2026-10-26/tools/kits.py replays/platform/<dir>/match-group-*.zip
Per champion type, per side (us/them): turns alive-ish, casts per slot by target kind, champion attacks,
and for ground casts (dashes/area spells) how many enemy champions were within 1 tile of the target tile."""
import io
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research/2026-10-25/tools"))
import replay30 as R

MAPS = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
stats = defaultdict(Counter)
for zp in sys.argv[1:]:
    outer = zipfile.ZipFile(zp)
    for n in sorted(outer.namelist()):
        inner = zipfile.ZipFile(io.BytesIO(outer.read(n)))
        names = inner.namelist()
        side = "a" if "team-a.stdout" in names else "b"
        rep = next(x for x in names if x.endswith((".repl26a", "replay")))
        g = R.parse(inner.read(rep), MAPS)
        if not g: continue
        pos = R.positions(g)
        hmap = {h: k for k, h in g["handle"].items()}
        for t in "ab":
            who = "us" if t == side else "them"
            other = "b" if t == "a" else "a"
            for i, name in enumerate(g["champs"][t]):
                c = stats[(who, name)]
                c["games"] += 1
                for r, acts in g["turns"][t][i]:
                    c["turns"] += 1
                    for sub, args in acts:
                        if sub == 2:
                            c["atk_champ" if args[0] == 1 else "atk_camp" if args[0] == 2 else "atk_other"] += 1
                        elif sub == 3:
                            slot, tk, tgt, x, y = args
                            if tk == 1:
                                c[f"s{slot}_champ"] += 1
                            elif tk == 2:
                                c[f"s{slot}_camp"] += 1
                            elif x >= 0:
                                near = 0
                                for j, pj in enumerate(pos[other]):
                                    p = pj.get(r) or pj.get(r - 1)
                                    if p and max(abs(p[0] - x), abs(p[1] - y)) <= 1:
                                        near += 1
                                c[f"s{slot}_ground"] += 1
                                if near: c[f"s{slot}_ground_hits_champ"] += 1
                            else:
                                c[f"s{slot}_self"] += 1
for (who, name), c in sorted(stats.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    t = max(1, c["turns"]) / 100
    keys = sorted(k for k in c if k not in ("games", "turns"))
    print(f"{name:12} {who:4} games {c['games']:3}  per 100 turns: " + "  ".join(f"{k} {c[k]/t:.1f}" for k in keys))
