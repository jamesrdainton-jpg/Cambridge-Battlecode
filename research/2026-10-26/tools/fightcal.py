"""Usage: python -I research/2026-10-26/tools/fightcal.py FILE...   (platform match-group zips or local replay bundles)
Calibrates our fight ratio from TELEMETRY lines ("F round slot kind tag ratio*100 hp% enemies allies gap gems", printed
by bots/cpp13 with TELEMETRY on): for each decision, did that champion die in the next 10 rounds? Deaths are inferred
from the replay as in vspro.py (55+ rounds without move/attack/cast/recall/tribute). Slot i is our i-th champion in draft
order (Cassi and Issac are two). If the ratio were calibrated, fights we take at ratio >= 1.3 would rarely end in death.
"""
import io
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research/2026-10-25/tools"))
import replay30 as R

MAPS = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
BUCKETS = [(0, 50), (50, 90), (90, 130), (130, 200), (200, 400), (400, 10**9)]
TAGS = {"K": "kill hit", "D": "dash kill", "R": "retreat", "H": "hit in range", "C": "cast", "X": "dash engage",
        "E": "engage/chase", "S": "hold", "O": "step out (HOLD_FIX)", "Z": "escape camps", "F": "stand"}


def bundles(paths):
    for fp in paths:
        z = zipfile.ZipFile(fp)
        names = z.namelist()
        if "replay.repl26a" in names:
            yield z
            continue
        for n in sorted(names):
            if n.endswith(".zip"):
                yield zipfile.ZipFile(io.BytesIO(z.read(n)))


def main():
    seen = Counter()
    died = Counter()
    by_tag = Counter()
    by_tag_died = Counter()
    games = 0
    for z in bundles(sys.argv[1:]):
        names = z.namelist()
        for side in ("a", "b"):
            if f"team-{side}.stdout" not in names:
                continue
            text = z.read(f"team-{side}.stdout").decode(errors="replace").replace("\x00", "")
            lines = [ln.split() for ln in text.splitlines() if ln.startswith("F ")]
            if not lines:
                continue
            g = R.parse(z.read("replay.repl26a"), MAPS)
            if g is None:
                continue
            games += 1
            deaths = defaultdict(list)
            for i, tl in enumerate(g["turns"][side]):
                last = None
                for r, acts in tl:
                    if any(s in (1, 2, 3, 4, 5) for s, _ in acts):
                        if last is not None and r - last >= 55:
                            deaths[i].append(last)
                        last = r
            for p in lines:
                r, slot, tag, ratio = int(p[1]), int(p[2]), p[4], int(p[5])
                dead = any(r <= d <= r + 10 for d in deaths[slot])
                b = next(b for b in BUCKETS if b[0] <= ratio < b[1])
                seen[b] += 1
                died[b] += dead
                by_tag[tag] += 1
                by_tag_died[tag] += dead
    print(f"{games} team-games with telemetry")
    print("ratio x100     decisions  died within 10 rounds")
    for b in BUCKETS:
        if seen[b]:
            print(f"{b[0]:>5}-{b[1] if b[1] < 10**9 else '':<6} {seen[b]:>9}  {100 * died[b] / seen[b]:5.1f}%")
    print("by decision:")
    for t, n in by_tag.most_common():
        print(f"  {t} {TAGS.get(t, '?'):22} {n:>6}  {100 * by_tag_died[t] / n:5.1f}%")


if __name__ == "__main__":
    main()
