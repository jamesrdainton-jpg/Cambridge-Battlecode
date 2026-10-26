"""Usage: python -I research/2026-10-26/tools/deathwin.py replays/platform/<dir>/match-group-*.zip
Our deaths to champions: rounds from the first enemy hit (in the 30 rounds before death) to death, enemy hits taken,
what the victim did in that window (camp hits, champion hits, moves), and whether it was hitting a camp when first hit.
Deaths are inferred as in vspro.py; those with no enemy champion hit in the 30 rounds before are skipped."""
import io
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research/2026-10-25/tools"))
import replay30 as R
import vspro

span = Counter()
doing = Counter()
hits_taken = []
fought_back = Counter()
for zp in sys.argv[1:]:
    outer = zipfile.ZipFile(zp)
    for n in sorted(outer.namelist()):
        inner = zipfile.ZipFile(io.BytesIO(outer.read(n)))
        side = "a" if "team-a.stdout" in inner.namelist() else "b"
        other = "b" if side == "a" else "a"
        g = R.parse(inner.read("replay.repl26a"), vspro.MAPS)
        deaths = []  # as vspro.py: a gap of 55+ rounds without move/attack/cast/recall/tribute is a death at its start
        for i, tl in enumerate(g["turns"][side]):
            last = None
            for r, acts in tl:
                if any(s in (1, 2, 3, 4, 5) for s, _ in acts):
                    if last is not None and r - last >= 55:
                        deaths.append({"index": i, "round": last})
                    last = r
        for d in deaths:
            i, r0 = d["index"], d["round"]
            h = g["handle"][(side, i)]
            enemy_hits = []
            for tl in g["turns"][other]:
                for r, acts in tl:
                    if r0 - 30 <= r <= r0:
                        for s, a in acts:
                            if (s == 2 and a[0] == 1 and a[1] == h) or (s == 3 and a[1] == 1 and a[2] == h):
                                enemy_hits.append(r)
            if not enemy_hits:
                continue
            first = min(enemy_hits)
            w = r0 - first
            span["0-1" if w <= 1 else "2-3" if w <= 3 else "4-7" if w <= 7 else "8+"] += 1
            hits_taken.append(len(enemy_hits))
            camp = champ = moves = 0
            at_first = "other"
            for r, acts in g["turns"][side][i]:
                if first - 3 <= r < first and any(s == 2 and a[0] == 2 for s, a in acts):
                    at_first = "farming"
                if first <= r <= r0:
                    for s, a in acts:
                        camp += s == 2 and a[0] == 2
                        champ += (s == 2 and a[0] == 1) or (s == 3 and a[1] == 1)
                        moves += s == 1
            doing[at_first] += 1
            fought_back["hit back" if champ else "never hit back"] += 1
            fought_back["moved away (any move)" if moves else "never moved"] += 1
print("rounds from first enemy hit to death:", dict(span))
print("before the first hit:", dict(doing))
print(dict(fought_back))
hits_taken.sort()
print("enemy hits taken: median", hits_taken[len(hits_taken) // 2], "n", len(hits_taken))
