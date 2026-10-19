"""Run bot pairings with cambc run-batch (large log limit) and print results.

Usage: python runner.py OUTNAME A B [--maps m1,m2] [--one-side] [--jobs 4] [--rounds N]
Replays go to matches/research/runs/OUTNAME/ (or $RS_WORK/runs/OUTNAME/). Prints one line per game plus totals (wins, STAT gems).
"""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import argparse
import re
import subprocess
import zipfile
from pathlib import Path

ROOT = _ROOT
SP = _WORK
RESULT = re.compile(r"\[\+\]\s+(.*?)\s{2,}(\S+) vs (\S+)\s+(\S+)\s+Round (\d+)/\d+")


def stdout(bundle, team):
    try:
        with zipfile.ZipFile(bundle) as z:
            return z.read(f"team-{team}.stdout").decode(errors="replace").replace("\x00", "")
    except Exception:
        return ""


def last_stat(text):
    found = None
    for line in text.splitlines():
        if line.startswith("STAT "):
            p = line.split()
            found = (int(p[1]), int(p[2]), int(p[3]))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--maps", default="")
    ap.add_argument("--one-side", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--rounds", type=int, default=0)
    args = ap.parse_args()
    maps = args.maps.split(",") if args.maps else sorted(p.stem for p in (ROOT / "maps").glob("*.map26a"))
    base = SP / "runs" / args.out
    base.mkdir(parents=True, exist_ok=True)
    for old in base.glob("*.repl26a"):
        old.unlink()
    games = []
    for m in maps:
        games.append((args.a, args.b, m, f"{m}-1.repl26a"))
        if not args.one_side:
            games.append((args.b, args.a, m, f"{m}-2.repl26a"))
    man = base / "manifest.txt"
    man.write_text("".join(f"{ROOT}/bots/{a} {ROOT}/bots/{b} {ROOT}/maps/{m}.map26a {base}/{r}\n" for a, b, m, r in games))
    cmd = [str(ROOT / ".venv/bin/cambc"), "run-batch", str(man), "--jobs", str(args.jobs), "--color", "never",
           "--log-limit", "40000000"]
    if args.rounds:
        cmd += ["--rounds", str(args.rounds)]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out = proc.stdout + proc.stderr
    (base / "batch.log").write_text(out)
    res = {}
    for line in out.splitlines():
        m = RESULT.search(line)
        if m:
            st, a, b, mp, rnd = m.groups()
            res.setdefault((Path(a).name, Path(b).name, mp), (st, int(rnd)))
    wins = {args.a: 0, args.b: 0}
    gems = {args.a: 0, args.b: 0}
    lines = []
    for a, b, m, r in games:
        st, rnd = res.get((a, b, m), ("MISSING", 0))
        w = a if "TEAM A WIN" in st else b if "TEAM B WIN" in st else None
        if w:
            wins[w] += 1
        sa, sb = last_stat(stdout(base / r, "a")), last_stat(stdout(base / r, "b"))
        ga = gb = 0
        if sa:
            ga, gb = sa[1], sa[2]
        elif sb:
            ga, gb = sb[2], sb[1]
        gems[a] += ga
        gems[b] += gb
        lines.append(f"{m:12} A={a:<12} B={b:<12} {st:<22} round={rnd:>4} gems {ga}-{gb}")
    print("\n".join(lines))
    for k in (args.a, args.b):
        print(f"{k:<14} wins {wins[k]}/{len(games)} gems {gems[k]}")


if __name__ == "__main__":
    main()
