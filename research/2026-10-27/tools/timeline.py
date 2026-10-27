"""Per-champion timeline of one platform game: what each of our champions (and theirs) did in each window of rounds.

Usage: python -I research/2026-10-27/tools/timeline.py (replays/platform/match-group-ID.zip GAME | local.repl26a 1) [--window 25] [--until 600]
GAME is the 1-based position in the group. Per window and champion: last position, and counts of moves (m), camp hits
(c), champion hits (h), casts (x), recalls (R), tributes (T), gold spent (g), and D when a 55+ round gap (death) starts.
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zip")
    ap.add_argument("game", type=int)
    ap.add_argument("--window", type=int, default=25)
    ap.add_argument("--until", type=int, default=600)
    args = ap.parse_args()
    maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
    if args.zip.endswith(".repl26a"):  # a local replay bundle: "us" = team A
        inner = zipfile.ZipFile(args.zip)
        names = inner.namelist()
        ours = "a"
        g = R.parse(inner.read("replay.repl26a"), maps)
    else:
        with zipfile.ZipFile(args.zip) as z:
            name = sorted(n for n in z.namelist() if n.endswith(".zip"))[args.game - 1]
            inner = zipfile.ZipFile(io.BytesIO(z.read(name)))
            names = inner.namelist()
            ours = "a" if "team-a.stdout" in names else "b"
            g = R.parse(inner.read(next(n for n in names if n.endswith(".repl26a"))), maps)
    print(f"{g['map']} rounds {g['rounds']}, us = team {ours}")
    for t in (ours, "b" if ours == "a" else "a"):
        print(f"== {'us' if t == ours else 'them'}: {', '.join(g['champs'][t])}")
        for i, tl in enumerate(g["turns"][t]):
            rows = {}
            last_active, pos = None, None
            for r, acts in tl:
                if r > args.until:
                    break
                w = (r - 1) // args.window
                c = rows.setdefault(w, {"m": 0, "c": 0, "h": 0, "x": 0, "R": 0, "T": 0, "g": 0, "D": "", "p": None})
                active = False
                for sub, a in acts:
                    if sub == 1:
                        c["m"] += 1
                        pos = (a[0], a[1])
                        active = True
                    elif sub == 2:
                        c["c" if a[0] == 2 else "h"] += 1
                        active = True
                    elif sub == 3:
                        c["x"] += 1
                        active = True
                    elif sub == 4:
                        c["R"] += 1
                        active = True
                    elif sub == 5:
                        c["T"] += 1
                        active = True
                    elif sub == 6:
                        c["g"] += 30 * a[1]
                if active:
                    if last_active is not None and r - last_active >= 55:
                        rows.setdefault((last_active - 1) // args.window, c)["D"] += "D"
                    last_active = r
                c["p"] = pos
            line = []
            for w in range(0, (args.until - 1) // args.window + 1):
                c = rows.get(w)
                if not c:
                    line.append(" " * 14)
                    continue
                s = f"{c['D']}m{c['m']}c{c['c']}h{c['h']}" + (f"g{c['g']}" if c["g"] else "") + (f"T{c['T']}" if c["T"] else "")
                line.append(f"{s:14s}")
            print(f"  {g['champs'][t][i]:11s}", "".join(line[:12]))
            if len(line) > 12:
                print(f"  {'':11s}", "".join(line[12:24]))


if __name__ == "__main__":
    main()
