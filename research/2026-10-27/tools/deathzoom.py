"""Round-by-round view of the rounds before each of our deaths in one platform game.

Usage: python -I research/2026-10-27/tools/deathzoom.py replays/platform/match-group-ID.zip GAME [--before 12] [--max 6]
For each death of ours (vspro's rule: a 55+ round gap in actions), prints the last rounds: every champion within 9
tiles of the victim, its position, and what it did (move, hit X, cast slot at X or a tile, recall, tribute).
Lower-case names are ours, upper-case theirs; * marks the victim.
"""
from __future__ import annotations

import argparse
import io
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "research" / "2026-10-25" / "tools"))
import replay30 as R  # noqa: E402


def cheb(p, q):
    return max(abs(p[0] - q[0]), abs(p[1] - q[1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zip")
    ap.add_argument("game", type=int)
    ap.add_argument("--before", type=int, default=12)
    ap.add_argument("--max", type=int, default=6)
    args = ap.parse_args()
    maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
    with zipfile.ZipFile(args.zip) as z:
        name = sorted(n for n in z.namelist() if n.endswith(".zip"))[args.game - 1]
        inner = zipfile.ZipFile(io.BytesIO(z.read(name)))
        names = inner.namelist()
        ours = "a" if "team-a.stdout" in names else "b"
        g = R.parse(inner.read(next(n for n in names if n.endswith(".repl26a"))), maps)
    them = "b" if ours == "a" else "a"
    owner = {h: k for k, h in g["handle"].items()}

    def label(t, i):
        n = g["champs"][t][i][:4]
        return n.lower() if t == ours else n.upper()

    pos, acts_at, dead = {}, {}, {}
    for t in (ours, them):
        for i, tl in enumerate(g["turns"][t]):
            p, cur = {}, None
            a = {}
            gaps, last = [], None
            for r, acts in tl:
                for sub, args_ in acts:
                    if sub == 1:
                        cur = (args_[0], args_[1])
                p[r] = cur
                a[r] = acts
                if any(s in (1, 2, 3, 4, 5) for s, _ in acts):
                    if last is not None and r - last >= 55:
                        gaps.append((last + 1, r - 1))  # dead (or channelling a long time) in between
                    last = r
            pos[(t, i)] = p
            acts_at[(t, i)] = a
            dead[(t, i)] = gaps

    def where(k, r):
        p = pos[k]
        while r > 0 and r not in p:
            r -= 1
        return p.get(r)

    def describe(acts):
        out = []
        for sub, a in acts:
            if sub == 2:
                tgt = owner.get(a[1])
                out.append(f"hit {label(*tgt)}" if a[0] == 1 and tgt else "camp")
            elif sub == 3:
                tgt = owner.get(a[2]) if a[1] == 1 else None
                out.append(f"cast{a[0]}>{label(*tgt)}" if tgt else (f"cast{a[0]}@{a[3]},{a[4]}" if a[1] == 0 else f"cast{a[0]}>camp"))
            elif sub == 4:
                out.append("RECALL")
            elif sub == 7:
                out.append("cancel")
            elif sub == 5:
                out.append("TRIB")
            elif sub == 6:
                out.append(f"buy{a[1]}")
        return " ".join(out)

    print(f"{g['map']} rounds {g['rounds']}; us = {ours}: {g['champs'][ours]}; them: {g['champs'][them]}")
    shown = 0
    for i, tl in enumerate(g["turns"][ours]):
        last = None
        for r, acts in tl:
            if not any(s in (1, 2, 3, 4, 5) for s, _ in acts):
                continue
            if last is not None and r - last >= 55 and shown < args.max:
                shown += 1
                d = last
                me = where((ours, i), d)
                print(f"\n--- {g['champs'][ours][i]} dies ~r{d} at {me}")
                for rr in range(d - args.before, d + 1):
                    cells = []
                    for t in (ours, them):
                        for j in range(len(g["champs"][t])):
                            q = where((t, j), rr)
                            if any(lo <= rr <= hi for lo, hi in dead[(t, j)]) and (t, j) != (ours, i):
                                continue
                            if q and me and cheb(q, me) <= 9:
                                star = "*" if (t, j) == (ours, i) else ""
                                txt = describe(acts_at[(t, j)].get(rr, []))
                                cells.append(f"{star}{label(t, j)}{q}{(' ' + txt) if txt else ''}")
                    print(f"  r{rr}: " + " | ".join(cells))
            last = r


if __name__ == "__main__":
    main()
