"""Item build orders per champion in platform games: what the other team buys, in order, and how it compares with us.

Usage: python -I research/2026-10-27/tools/builds.py replays/platform/match-group-*.zip [--side them|us] [--until 800]
Per champion type: how often each emblem family/stat is the 1st, 2nd, 3rd... completed (5 shards of one item), the
mean shards of each kind owned at rounds 200/400/800, and a few sample sequences. Item ids: 14 families x 3 stats x
(shard, emblem), in the SDK's order (cambc 4.0).
"""
from __future__ import annotations

import argparse
import io
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "research" / "2026-10-25" / "tools"))
import replay30 as R  # noqa: E402

FAM = ["Monster", "Power", "Durability", "Treasure", "Jungle", "Home", "Bruiser", "Tribute", "Capture", "Prospector",
       "Hunter", "Skirmish", "Greed", "Collectors"]
STATS = ["S", "F", "H"]


def item_name(i):
    fam, rest = divmod(i, 6)
    stat, _emblem = divmod(rest, 2)
    return f"{FAM[fam] if fam < len(FAM) else fam} {STATS[stat]}"


def games(paths):
    for path in paths:
        with zipfile.ZipFile(path) as z:
            for name in sorted(z.namelist()):
                if not name.endswith(".zip"):
                    continue
                with zipfile.ZipFile(io.BytesIO(z.read(name))) as inner:
                    names = inner.namelist()
                    reps = [x for x in names if x.endswith(".repl26a")]
                    if reps and any(x.endswith(".stdout") for x in names):
                        yield inner.read(reps[0]), "a" if "team-a.stdout" in names else "b"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--side", default="them")
    ap.add_argument("--until", type=int, default=800)
    args = ap.parse_args()
    maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
    order = defaultdict(lambda: defaultdict(Counter))  # champ -> k-th completed -> item
    owned = defaultdict(lambda: defaultdict(Counter))  # champ -> round mark -> item -> shards
    count = Counter()
    samples = defaultdict(list)
    for data, ours in games(args.paths):
        g = R.parse(data, maps)
        if g is None:
            continue
        t = ours if args.side == "us" else ("b" if ours == "a" else "a")
        for i, tl in enumerate(g["turns"][t]):
            champ = g["champs"][t][i]
            count[champ] += 1
            shards = Counter()
            done = []
            marks = [200, 400, 800]
            for r, acts in tl:
                while marks and r > marks[0]:
                    for k, v in shards.items():
                        owned[champ][marks[0]][k] += v
                    marks.pop(0)
                if r > args.until:
                    break
                for sub, a in acts:
                    if sub == 6:
                        name = item_name(a[0])
                        before = shards[name]
                        shards[name] += a[1]
                        for m in range(before // 5 + 1, shards[name] // 5 + 1):
                            done.append(name)
            for m in marks:
                for k, v in shards.items():
                    owned[champ][m][k] += v
            for k, name in enumerate(done[:6]):
                order[champ][k][name] += 1
            if len(samples[champ]) < 4:
                samples[champ].append(" > ".join(done[:8]))
    for champ in sorted(count, key=lambda c: -count[c]):
        n = count[champ]
        print(f"\n== {champ} ({n} games, side {args.side})")
        for k in range(6):
            c = order[champ][k]
            if c:
                print(f"  emblem #{k + 1}: " + ", ".join(f"{it} {100 * v / n:.0f}%" for it, v in c.most_common(4)))
        for m in (200, 400, 800):
            c = owned[champ][m]
            if c:
                print(f"  shards owned at r{m} (mean): " + ", ".join(f"{it} {v / n:.1f}" for it, v in c.most_common(6)))
        for s in samples[champ]:
            print(f"    e.g. {s}")


if __name__ == "__main__":
    main()
