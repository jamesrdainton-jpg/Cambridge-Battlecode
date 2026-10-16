"""Summarise platform match downloads (replays/platform/*.zip): map, result, gem curve, stalls, drafts, fuel.

Usage: python tools/platform_report.py [--dir replays/platform]

Each download is one game: our team's stdout (STAT lines), a .fuel file (fuel per champion turn) and the
replay. The map is found by matching its bytes inside the replay against maps/. Drafts are decoded from the
pick records that follow the map (6 bytes each in replay format 1, 7 bytes in format 2, alternating team A
and B). Files are read in memory only; nothing is extracted or executed.
"""
from __future__ import annotations

import argparse
import struct
import zipfile
from pathlib import Path

from common import ROOT

NAMES = ["Ryth", "Vesper", "Vendetta", "Cassi&Issac", "Stellar", "Prism", "Marcella", "Willow", "Ren", "Varg", "Tavi"]


def drafts(data: bytes, map_bytes: bytes) -> tuple[list[int], list[int]]:
    o = data.find(map_bytes) + len(map_bytes) + 4
    rec = 6 if data[10] == 1 else 7
    picks = []
    while o + 6 <= len(data) and data[o] == 4 and data[o + 1] == 0:
        picks.append(struct.unpack_from("<I", data, o + 2)[0])
        o += rec
    return picks[0::2], picks[1::2]


def fuel_peak(fuel: bytes) -> int:
    """Highest fuel used in one normal champion turn (skips the 8 limit values, draft and first turns)."""
    vals = [struct.unpack_from("<q", fuel, o)[0] for o in range(13, len(fuel) - 7, 8)][8:]
    big = [i for i, v in enumerate(vals[:12]) if v > 1_500_000]
    normal = vals[(big[-1] + 1) if big else 0:]
    return max(normal) if normal else 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=str(ROOT / "replays" / "platform"))
    args = parser.parse_args()
    maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
    rows = []
    for p in sorted(Path(args.dir).glob("*.zip")):
        z = zipfile.ZipFile(p)
        side = "a" if "team-a.stdout" in z.namelist() else "b"
        data = z.read("replay.repl26a")
        found = [(n, b) for n, b in maps.items() if b in data]
        name, mb = found[0] if found else ("?", b"")
        a, b = drafts(data, mb) if mb else ([], [])
        ours, theirs = (a, b) if side == "a" else (b, a)
        out = z.read(f"team-{side}.stdout").decode(errors="replace").replace(chr(0), "")
        stats = [tuple(map(int, line.split()[1:4])) for line in out.splitlines() if line.startswith("STAT ")]
        errors = sum(1 for line in out.splitlines() if line.strip() and not line.startswith("STAT "))
        last = stats[-1] if stats else (0, 0, 0)

        def at(r: int, stats: list = stats) -> str:
            return next((f"{s[1]}-{s[2]}" for s in stats if s[0] >= r), "-")

        flat = (0, 0, 0)
        if stats:
            start_r, start_g = stats[0][0], stats[0][1]
            for s in stats[1:]:
                if s[1] != start_g:
                    start_r, start_g = s[0], s[1]
                elif s[0] - start_r > flat[0]:
                    flat = (s[0] - start_r, start_r, start_g)
        fuel = z.read(f"team-{side}.fuel") if f"team-{side}.fuel" in z.namelist() else b""
        rows.append((name, p.stem[6:14], "WIN" if last[1] > last[2] else "LOSS", last, at(200), at(400), flat,
                     ",".join(NAMES[x] for x in ours), ",".join(NAMES[x] for x in theirs),
                     fuel_peak(fuel) if fuel else 0, errors))
    rows.sort()
    print("| Map | Game | Result | Final (round: us-them) | r200 | r400 | Longest flat (us) | Our draft | Their draft "
          "| Peak fuel | Error lines |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r[0]} | {r[1]} | {r[2]} | r{r[3][0]}: {r[3][1]}-{r[3][2]} | {r[4]} | {r[5]} | "
              f"{r[6][0]} rounds at {r[6][2]} from r{r[6][1]} | {r[7]} | {r[8]} | {r[9] / 1e6:.2f}M | {r[10]} |")
    wins = sum(r[2] == "WIN" for r in rows)
    print(f"\n{wins}/{len(rows)} wins")


if __name__ == "__main__":
    main()
