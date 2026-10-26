"""How strong teams use the meta champions' abilities, from platform match downloads (our games against them).

Usage: python -I research/2026-10-26/tools/meta_usage.py replays/platform/match-group-*.zip
For the opponents' champions (our side is the one whose stdout is in the download): every ability cast with its slot,
target kind (champion / camp / tile) and, for tile casts, how many of our champions stood within 1 of the landing tile;
basic attacks on champions; and focus fire (rounds where 2+ of their champions hit our champions: same target or not).
"""
from __future__ import annotations

import io
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "research" / "2026-10-25" / "tools"))
import replay30 as R  # noqa: E402


def games(paths):
    for path in paths:
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                if not name.endswith(".zip"):
                    continue
                with zipfile.ZipFile(io.BytesIO(z.read(name))) as inner:
                    names = inner.namelist()
                    reps = [x for x in names if x.endswith(".repl26a")]
                    if not reps or not any(x.endswith(".stdout") for x in names):
                        continue  # not one of our games (no stdout of ours inside)
                    ours = "a" if "team-a.stdout" in names else "b"
                    yield inner.read(reps[0]), ours


def main():
    maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
    casts = Counter()
    landing = defaultdict(Counter)  # (champ, slot) -> our champions within 1 of the landing tile
    hits = Counter()
    focus = Counter()
    n = 0
    for data, ours in games(sys.argv[1:]):
        g = R.parse(data, maps)
        if g is None:
            continue
        n += 1
        them = "b" if ours == "a" else "a"
        pos = R.positions(g)
        our_handles = {g["handle"][(ours, i)] for i in range(len(g["champs"][ours]))}
        per_round = defaultdict(list)  # round -> champion targets hit by them
        for i, tl in enumerate(g["turns"][them]):
            c = g["champs"][them][i]
            for r, acts in tl:
                for sub, args in acts:
                    if sub == 3:
                        slot, kind, target, x, y = args
                        what = {1: "champ", 2: "camp"}.get(kind, "tile")
                        if kind == 1 and target not in our_handles:
                            what = "ally"
                        casts[(c, slot, what)] += 1
                        if what == "tile" and x >= 0:
                            near = sum(1 for j in range(len(g["champs"][ours]))
                                       if (p := pos[ours][j].get(r - 1)) and max(abs(p[0] - x), abs(p[1] - y)) <= 1)
                            landing[(c, slot)][min(near, 3)] += 1
                        if kind == 1 and target in our_handles:
                            per_round[r].append(target)
                    elif sub == 2 and args[0] == 1 and args[1] in our_handles:
                        hits[c] += 1
                        per_round[r].append(args[1])
        for r, ts in per_round.items():
            if len(ts) >= 2:
                focus["same target" if len(set(ts)) == 1 else "split"] += 1
        their_handles = {g["handle"][(them, i)] for i in range(len(g["champs"][them]))}
        mine = defaultdict(list)
        for tl in g["turns"][ours]:
            for r, acts in tl:
                for sub, args in acts:
                    if (sub == 2 and args[0] == 1 and args[1] in their_handles) or (sub == 3 and args[1] == 1 and args[2] in their_handles):
                        mine[r].append(args[1] if sub == 2 else args[2])
        for r, ts in mine.items():
            if len(ts) >= 2:
                focus["ours: same target" if len(set(ts)) == 1 else "ours: split"] += 1
    print(f"{n} games")
    print("casts by (champion, slot, target):")
    for (c, slot, what), k in sorted(casts.items()):
        print(f"  {c:12s} slot {slot} {what:6s} {k:6d}")
    print("tile casts: our champions within 1 of the landing tile (0, 1, 2, 3+):")
    for (c, slot), cnt in sorted(landing.items()):
        tot = sum(cnt.values())
        print(f"  {c:12s} slot {slot}: " + ", ".join(f"{k}: {100 * cnt[k] / tot:.0f}%" for k in range(4)) + f"  (n={tot})")
    print("basic attacks on our champions:", dict(hits))
    print("rounds with 2+ of their hits on our champions:", dict(focus))


if __name__ == "__main__":
    main()
