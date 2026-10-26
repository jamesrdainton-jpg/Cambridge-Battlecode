"""How each side farms in platform games against strong teams: where champion-turns go, per side.

Usage: python -I research/2026-10-26/tools/farming.py replays/platform/match-group-*.zip [--rounds 300]
Per side (us = the side whose stdout is in the download), over the first N rounds of each game: share of champion-turns
spent hitting camps, hitting champions, moving only, channelling/idle (no action: recall, tribute, capture, waiting,
dead); camp hits per alive champion-turn; how many of the side's champions hit the same camp group in the same round
(team-up); gold spent; camp kinds hit; recalls and tributes per champion.
"""
from __future__ import annotations

import argparse
import io
import sys
import zipfile
from collections import Counter
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
                    if reps and any(x.endswith(".stdout") for x in names):
                        yield inner.read(reps[0]), "a" if "team-a.stdout" in names else "b"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--rounds", type=int, default=300)
    args = ap.parse_args()
    maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
    camp_group = {}
    for f in (ROOT / "research" / "2026-10-25" / "data" / "mapdumps").glob("*.txt"):
        for line in f.read_text().splitlines():
            if line.startswith("CAMPH"):
                _, h, kind, x, y, gid = line.split()
                camp_group[(f.stem, int(h))] = (kind, int(gid))
    stats = {s: Counter() for s in ("us", "them")}
    n = 0
    for data, ours in games(args.paths):
        g = R.parse(data, maps)
        if g is None:
            continue
        n += 1
        mp = g["map"]
        for side, t in (("us", ours), ("them", "b" if ours == "a" else "a")):
            st = stats[side]
            per_round_groups = Counter()
            for i, tl in enumerate(g["turns"][t]):
                for r, acts in tl:
                    if r > args.rounds:
                        break
                    st["turns"] += 1
                    kinds = Counter()
                    for sub, a in acts:
                        if sub == 2 or sub == 3:
                            tk = a[0] if sub == 2 else a[1]
                            tgt = a[1] if sub == 2 else a[2]
                            if tk == 2:
                                kinds["camp"] += 1
                                kg = camp_group.get((mp, tgt))
                                if kg:
                                    st[f"kind {kg[0]}"] += 1
                                    per_round_groups[(r, kg[1])] += 1
                            elif tk == 1:
                                kinds["champ"] += 1
                            else:
                                kinds["cast"] += 1
                        elif sub == 1:
                            kinds["move"] += 1
                        elif sub == 4:
                            st["recalls"] += 1
                        elif sub == 5:
                            st["tributes"] += 1
                        elif sub == 6:
                            st["gold spent"] += 30 * a[1]
                    if kinds["camp"]:
                        st["camp turns"] += 1
                        st["camp hits"] += kinds["camp"]
                    elif kinds["champ"]:
                        st["champion turns"] += 1
                    elif kinds["move"] or kinds["cast"]:
                        st["moving turns"] += 1
                    else:
                        st["idle turns"] += 1
            for (r, gid), k in per_round_groups.items():
                st["group-rounds"] += 1
                st["champion-hits in shared group-rounds"] += k
    print(f"{n} games, first {args.rounds} rounds")
    for side in ("us", "them"):
        st = stats[side]
        t = st["turns"] or 1
        alive = t - st["idle turns"] or 1
        kinds = {k[5:]: v for k, v in st.items() if k.startswith("kind ")}
        tot = sum(kinds.values()) or 1
        print(f"  {side:4s}: camp turns {100 * st['camp turns'] / t:.0f}%, champion turns {100 * st['champion turns'] / t:.0f}%, "
              f"moving {100 * st['moving turns'] / t:.0f}%, idle/channel/dead {100 * st['idle turns'] / t:.0f}%; "
              f"camp hits per active turn {st['camp hits'] / alive:.2f}; champions per camp group-round "
              f"{st['champion-hits in shared group-rounds'] / max(st['group-rounds'], 1):.2f}; gold spent/game {st['gold spent'] / n:.0f}; "
              f"recalls/game {st['recalls'] / n:.1f}, tributes/game {st['tributes'] / n:.1f}; camp kinds "
              + ", ".join(f"{k} {100 * v / tot:.0f}%" for k, v in sorted(kinds.items(), key=lambda kv: -kv[1])))


if __name__ == "__main__":
    main()
