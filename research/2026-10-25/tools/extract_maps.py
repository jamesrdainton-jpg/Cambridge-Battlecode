"""Extract embedded map files from platform replays (in memory; writes map bytes only).

Usage: python -I research/2026-10-25/tools/extract_maps.py OUTDIR ZIP...
Map = bytes from offset 14 up to the u32 record count that precedes the first draft record (04 01 <u32 pick> ff 03 00).
"""
import hashlib, io, struct, sys, zipfile
from pathlib import Path

repo = Path(__file__).resolve().parents[3]
out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
known = {p.read_bytes(): p.stem for p in (repo / "maps").glob("*.map26a")}

def map_end(d):
    o = 14 + 40
    while True:
        o = d.find(b"\x04\x01", o + 1)
        if o < 0:
            return None
        pick = struct.unpack_from("<I", d, o + 2)[0]
        if pick < 11 and d[o + 6] == 0xFF and d[o + 7:o + 9] == b"\x03\x00":
            cnt = struct.unpack_from("<I", d, o - 4)[0]
            if 0 < cnt < len(d):
                return o - 4

seen = {}
for zp in sys.argv[2:]:
    z = zipfile.ZipFile(zp)
    for n in sorted(z.namelist()):
        if not n.endswith(".zip"):
            continue
        inner = zipfile.ZipFile(io.BytesIO(z.read(n)))
        d = inner.read("replay.repl26a")
        e = map_end(d)
        if e is None:
            print(Path(zp).name[12:20], n[:2], "no map end found"); continue
        mb = d[14:e]
        h = hashlib.sha1(mb).hexdigest()[:8]
        name = known.get(mb)
        w, hgt = struct.unpack_from("<HH", mb, 0x4a); picks = mb[0x49]
        if h not in seen:
            seen[h] = (name, len(mb), w, hgt, picks)
            (out / f"{name or 'new-' + h}.map26a").write_bytes(mb)
        print(Path(zp).name[12:20], n[:2], f"map={name or 'new-' + h} len={len(mb)} hdr={mb[0x44:0x4e].hex(' ')} {w}x{hgt} picks={picks}")
print("\nunique maps:", len(seen))
for h, v in seen.items():
    print(" ", h, v)
