"""Per-game fuel use of our champions in platform match groups (team-X.fuel: i64 fuel per champion turn)."""
import io, struct, sys, zipfile
from pathlib import Path
allv = []
for zp in sys.argv[1:]:
    z = zipfile.ZipFile(zp)
    for n in sorted(z.namelist()):
        if not n.endswith(".zip"):
            continue
        inner = zipfile.ZipFile(io.BytesIO(z.read(n)))
        side = next((s for s in "ab" if f"team-{s}.fuel" in inner.namelist()), None)
        if not side:
            continue
        fuel = inner.read(f"team-{side}.fuel")
        vals = [struct.unpack_from("<q", fuel, o)[0] for o in range(13, len(fuel) - 7, 8)]
        body = [v for v in vals[40:] if 0 <= v < 3_000_000]  # skip draft/first turns
        if not body:
            print(Path(zp).name[12:20], n[:2], "no turns"); continue
        body.sort()
        p50 = body[len(body)//2]; p99 = body[int(len(body)*0.99)]; mx = body[-1]
        over2 = sum(v > 2_000_000 for v in body)
        allv += body
        print(f"{Path(zp).name[12:20]}/{n[:2]} turns={len(body)} median={p50/1e6:.2f}M p99={p99/1e6:.2f}M max={mx/1e6:.2f}M turns>2.0M={over2}")
allv.sort()
print(f"ALL turns={len(allv)} median={allv[len(allv)//2]/1e6:.2f}M p90={allv[int(len(allv)*.9)]/1e6:.2f}M p99={allv[int(len(allv)*.99)]/1e6:.2f}M max={allv[-1]/1e6:.2f}M")
