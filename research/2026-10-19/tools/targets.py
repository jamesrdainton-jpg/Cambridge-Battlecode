"""Camp targets per team from replays, using camp handle dumps (CAMPH lines) per map.
Usage: python -I targets.py [--check] DIR...
Tracks champion positions from move records (start: first move's origin unknown, so position = last move dest).
"""
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

SP = _WORK
ROOT = _ROOT
CAMPS = {}
for f in (SP / "runs" / "dumps").glob("*.txt"):
    d = {}
    for line in f.read_text().splitlines():
        if line.startswith("CAMPH "):
            _, h, k, x, y, grp = line.split()
            d[int(h)] = (k, int(x), int(y), int(grp))
    CAMPS[f.stem] = d
RANGED = {"Cassi", "Stellar", "Prism", "Tavi", "Willow", "Vesper"}


def main():
    check = "--check" in sys.argv
    dirs = [a for a in sys.argv[1:] if not a.startswith("--")]
    maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
    dist_hist = Counter()
    kinds = defaultdict(Counter)
    unknown = 0
    for f in files(dirs):
        for label, data in RD.replays(f):
            g = per_turn(data, maps)
            if g is None:
                continue
            cm = CAMPS.get(g["map"], {})
            for team in "ab":
                tag = "us" if "Vendetta" in g["champs"][team] and "Marcella" in g["champs"][team] or g["champs"][team] == ["Vendetta", "Ryth", "Tavi"] else "other"
                for champ, tl in zip(g["champs"][team], g["turns"][team]):
                    pos = None
                    for r, acts in tl:
                        for sub, a in acts:
                            if sub == 1:
                                pos = (a[0], a[1])
                            elif (sub == 2 and a[0] == 2) or (sub == 3 and a[1] == 2):
                                h = a[1] if sub == 2 else a[2]
                                c = cm.get(h)
                                if c is None:
                                    unknown += 1
                                    continue
                                kinds[tag][c[0]] += 1
                                if pos and check:
                                    d = max(abs(pos[0] - c[1]), abs(pos[1] - c[2]))
                                    dist_hist[(champ in RANGED, "atk" if sub == 2 else "cast", min(d, 9))] += 1
    if check:
        for k in sorted(dist_hist):
            print(k, dist_hist[k])
    print("unknown camp ids:", unknown)
    for tag, c in kinds.items():
        t = sum(c.values())
        print(tag, t, {k: f"{100 * v / t:.0f}%" for k, v in c.most_common()})


if __name__ == "__main__":
    main()
