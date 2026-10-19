"""Report on our platform games from match-group zips (nested zips, read in memory only).

Usage: python -I ourgames.py DIR [DIR ...]
For each game with a team-X.stdout: map, side, result (from STAT lines), gems at r100/200/300/400, both drafts,
our wards/locks (v10 places wards, v7 doesn't), deaths per team (replay inference), peak fuel, error lines.
"""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import io
import struct
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(_ROOT / "tools"))
import replay_decode as RD  # noqa: E402

ROOT = _ROOT


def games(paths):
    for d in paths:
        for f in sorted(Path(d).glob("*.zip")):
            z = zipfile.ZipFile(f)
            for n in sorted(z.namelist()):
                if not n.endswith(".zip"):
                    continue
                inner = zipfile.ZipFile(io.BytesIO(z.read(n)))
                names = inner.namelist()
                side = "a" if "team-a.stdout" in names else "b" if "team-b.stdout" in names else None
                files = {k: inner.read(k) for k in names}
                yield f"{Path(d).name}/{n[:2]}", side, files


def fuel_peak(fuel):
    vals = [struct.unpack_from("<q", fuel, o)[0] for o in range(13, len(fuel) - 7, 8)][8:]
    big = [i for i, v in enumerate(vals[:12]) if v > 1_500_000]
    normal = vals[(big[-1] + 1) if big else 0:]
    return max(normal) if normal else 0


def main():
    maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
    rows = []
    for label, side, files in games(sys.argv[1:]):
        if side is None:
            continue
        data = files["replay.repl26a"]
        g = RD.decode(data, maps)
        if "acts" not in g:
            print(label, g.get("error"))
            continue
        other = "b" if side == "a" else "a"
        out = files[f"team-{side}.stdout"].decode(errors="replace").replace("\x00", "")
        stats = [tuple(map(int, line.split()[1:4])) for line in out.splitlines() if line.startswith("STAT ")]
        errs = [line for line in out.splitlines() if line.strip() and not line.startswith("STAT ")]
        last = stats[-1] if stats else (0, 0, 0)

        def at(r):
            return next((f"{s[1]}-{s[2]}" for s in stats if s[0] >= r), "-")

        us = RD.summarise(g, side)
        them = RD.summarise(g, other)
        fuel = files.get(f"team-{side}.fuel", b"")
        win = last[1] > last[2] or (last[1] >= 1000)
        rows.append((g["map"], label, side, "WIN" if win else "LOSS", g["rounds"], last, at(100), at(200), at(300), at(400),
                     ",".join(g["champs"][side]), ",".join(g["champs"][other]), us["wards"], len(us["deaths"]),
                     len(them["deaths"]), them["recalls"], fuel_peak(fuel) / 1e6 if fuel else 0, len(errs), errs[:2]))
    rows.sort()
    print("| Map | Game | Side | Result | Rounds | Final | r100 | r200 | r300 | r400 | Our draft | Their draft | Our wards | Deaths us/them | Peak fuel | Errors |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5][1]}-{r[5][2]} | {r[6]} | {r[7]} | {r[8]} | {r[9]} | {r[10]} | {r[11]} | {r[12]} | {r[13]}/{r[14]}{'*' if r[15] > 300 else ''} | {r[16]:.2f}M | {r[17]} |")
    w = sum(r[3] == "WIN" for r in rows)
    print(f"\n{w}/{len(rows)} wins")
    for r in rows:
        if r[18]:
            print(r[1], r[18])


if __name__ == "__main__":
    main()
