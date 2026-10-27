"""How many champion-turns each side spends bouncing between two tiles (A, B, A, B, ... for 6+ moves in a row).

Usage: python -I research/2026-10-27/tools/oscillation.py replays/platform/match-group-*.zip
Per game and side: rounds spent in such bounces (our go() flipped between a soft-avoid and a hard path, 2026-10-27).
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "research" / "2026-10-25" / "tools"))
import replay30 as R  # noqa: E402


def bounce_rounds(tl):
    moves = [(r, (a[0], a[1])) for r, acts in tl for sub, a in acts if sub == 1]
    total, run = 0, 0
    for k in range(2, len(moves)):
        if moves[k][1] == moves[k - 2][1] and moves[k][1] != moves[k - 1][1] and moves[k][0] - moves[k - 1][0] <= 2:
            run += 1
        else:
            if run >= 4:
                total += run + 2
            run = 0
    if run >= 4:
        total += run + 2
    return total


def main():
    maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
    tot = {"us": 0, "them": 0}
    for path in sys.argv[1:]:
        with zipfile.ZipFile(path) as z:
            for name in sorted(n for n in z.namelist() if n.endswith(".zip")):
                inner = zipfile.ZipFile(io.BytesIO(z.read(name)))
                names = inner.namelist()
                if not any(x.endswith(".stdout") for x in names):
                    continue
                ours = "a" if "team-a.stdout" in names else "b"
                g = R.parse(inner.read(next(n for n in names if n.endswith(".repl26a"))), maps)
                if g is None:
                    continue
                row = {}
                for side, t in (("us", ours), ("them", "b" if ours == "a" else "a")):
                    row[side] = sum(bounce_rounds(tl) for tl in g["turns"][t])
                    tot[side] += row[side]
                if row["us"] >= 30 or row["them"] >= 30:
                    print(f"{Path(path).name[12:20]}/{name[:2]} {g['map']:22s} bouncing rounds us {row['us']:4d} them {row['them']:4d}")
    print(f"total bouncing champion-rounds: us {tot['us']} them {tot['them']}")


if __name__ == "__main__":
    main()
