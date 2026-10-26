"""How our champions die in platform games: warning time, numbers, and what they were doing.

Usage: python -I research/2026-10-26/tools/deaths.py replays/platform/match-group-*.zip
Deaths as in vspro.py (a gap of 55+ rounds without a move, attack, cast, recall or tribute; positions from move
records). For each of our deaths: rounds an enemy champion had been within 8 tiles, enemy and allied champions within 3
tiles at the death, how many enemies hit the victim in its last 5 rounds, and what the victim did in its last 5 turns.
"""
from __future__ import annotations

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


def cheb(p, q):
    return max(abs(p[0] - q[0]), abs(p[1] - q[1]))


def main():
    maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
    warn, enemies, allies, doing, hitters = Counter(), Counter(), Counter(), Counter(), Counter()
    n = early = 0
    for data, ours in games(sys.argv[1:]):
        g = R.parse(data, maps)
        if g is None:
            continue
        them = "b" if ours == "a" else "a"
        owner = {h: k for k, h in g["handle"].items()}
        pos = {}
        for t in (ours, them):
            pos[t] = []
            for tl in g["turns"][t]:
                p, cur = {}, None
                for r, acts in tl:
                    for sub, args in acts:
                        if sub == 1:
                            cur = (args[0], args[1])
                    p[r] = cur
                pos[t].append(p)

        def where(t, i, r):
            p = pos[t][i]
            while r > 0 and r not in p:
                r -= 1
            return p.get(r)

        hits = [(r, owner[tgt][1]) for i, tl in enumerate(g["turns"][them]) for r, acts in tl for sub, args in acts
                if (tgt := (args[1] if sub == 2 and args[0] == 1 else args[2] if sub == 3 and args[1] == 1 else None)) in owner
                and owner[tgt][0] == ours]
        for i, tl in enumerate(g["turns"][ours]):
            last = None
            acts_at = dict(tl)
            for r, acts in tl:
                if not any(s in (1, 2, 3, 4, 5) for s, _ in acts):
                    continue
                if last is not None and r - last >= 55:
                    d = last
                    at = where(ours, i, d)
                    if at:
                        n += 1
                        early += d <= 300
                        ens = [q for j in range(len(g["champs"][them])) if (q := where(them, j, d))]
                        enemies[min(sum(1 for q in ens if cheb(q, at) <= 3), 3)] += 1
                        als = [q for j in range(len(g["champs"][ours])) if j != i and (q := where(ours, j, d))]
                        allies[min(sum(1 for q in als if cheb(q, at) <= 3), 3)] += 1
                        w = 0
                        for rr in range(d, max(d - 30, 0), -1):
                            me = where(ours, i, rr)
                            if me and any((q := where(them, j, rr)) and cheb(q, me) <= 8 for j in range(len(g["champs"][them]))):
                                w += 1
                            else:
                                break
                        warn["0-2" if w <= 2 else "3-5" if w <= 5 else "6-10" if w <= 10 else "11+"] += 1
                        hitters[min(len({0 for hr, ti in hits if ti == i and d - 4 <= hr <= d + 1}), 1)] += 0
                        kinds = Counter()
                        for rr in range(d - 4, d + 1):
                            for sub, args in acts_at.get(rr, []):
                                if sub in (2, 3):
                                    tk = args[0] if sub == 2 else args[1]
                                    kinds["hit champion" if tk == 1 else "hit camp" if tk == 2 else "cast"] += 1
                                elif sub == 1:
                                    kinds["move"] += 1
                        doing["hit champion" if kinds["hit champion"] else "hit camp" if kinds["hit camp"] else
                              "moving only" if kinds["move"] else "nothing (channel/stunned)"] += 1
                last = r

    def pct(c):
        return ", ".join(f"{k}: {100 * v / n:.0f}%" for k, v in sorted(c.items(), key=str))

    print(f"{n} deaths of ours ({early} in the first 300 rounds)")
    print("rounds an enemy had been within 8 tiles:", pct(warn))
    print("enemy champions within 3 at death:", pct(enemies))
    print("our allies within 3 at death:", pct(allies))
    print("what our champion did in its last 5 turns:", pct(doing))


if __name__ == "__main__":
    main()
