"""Why we lose ranked games: one line per loss with a cause tag, and wins vs losses compared.

Usage: python -I research/2026-10-27/tools/ranked.py [--since 2026-10-27T12] [--until ...] [--pages 2] [--no-fetch]
Lists our ranked matches (cambc matches list --team me --kind ranked), downloads missing replays to replays/ranked/
(one zip per match: replay + our stdout), and analyses each with research/2026-10-25/tools/vspro.py.
Times are UTC. Tags: CLOSE (a tiebreak, or 900+ gems at our last STAT line), FIGHT (we died 3+ more times than they did),
FARM (they hit camps 25%+ more often), SPEND (they spent 30%+ more gold by round 500), LATE (our first tribute came
150+ rounds after theirs), BEHIND300 (100+ gems behind at round 300), COMEBACK (ahead at round 500, lost).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research" / "2026-10-25" / "tools"))
import vspro as V  # noqa: E402

US = "cd168e4d"
OUT = ROOT / "replays" / "ranked"
NAMES = ["Ryth", "Vesper", "Vendetta", "C&I", "Stellar", "Prism", "Marcella", "Willow", "Ren", "Varg", "Tavi", "HoR"]


def cambc(*args):
    return subprocess.run(["cambc", *args], capture_output=True, text=True, encoding="utf-8").stdout


def matches(pages):
    out, cur = [], None
    for _ in range(pages):
        d = json.loads(cambc("matches", "list", "--team", "me", "--kind", "ranked", "--limit", "100", "--json",
                             *(["--cursor", cur] if cur else [])))
        out += d["matches"]
        cur = d.get("nextCursor")
        if not cur:
            break
    return [m for m in out if m["status"] == "finished"]


def load(path):
    inner = zipfile.ZipFile(path)
    names = inner.namelist()
    side = "a" if "team-a.stdout" in names else "b" if "team-b.stdout" in names else None
    stats = []
    if side:
        out = inner.read(f"team-{side}.stdout").decode(errors="replace").replace("\x00", "")
        stats = [tuple(map(int, line.split()[1:4])) for line in out.splitlines() if line.startswith("STAT ")]
    return side, stats, inner.read("replay.repl26a")


def tags(a, end):
    me, opp = a["me"], a["opp"]
    f = a["final"]
    t = []
    dm = sum(d["team"] == me for d in a["deaths"])
    do = sum(d["team"] == opp for d in a["deaths"])
    if end.startswith("tiebreak") or (f and f[1] >= 900):  # our last STAT line comes before the final tributes
        t.append("CLOSE")
    if dm >= do + 3:
        t.append("FIGHT")
    if a["camp_hits"][opp] > 1.25 * max(1, a["camp_hits"][me]):
        t.append("FARM")
    if a["spend"][opp][500] > 1.3 * max(1, a["spend"][me][500]):
        t.append("SPEND")
    fu, ft = a["first_tribute"].get(me), a["first_tribute"].get(opp)
    if ft and (fu is None or fu > ft + 150):
        t.append("LATE")
    tl = a["timeline"]
    if 300 in tl and tl[300][1] - tl[300][0] >= 100:
        t.append("BEHIND300")
    if 500 in tl and tl[500][0] > tl[500][1]:
        t.append("COMEBACK")
    return t, dm, do


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="")
    ap.add_argument("--until", default="9999")
    ap.add_argument("--pages", type=int, default=2)
    ap.add_argument("--no-fetch", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    idx = OUT / "index.json"
    known = {m["matchId"]: m for m in json.loads(idx.read_text(encoding="utf-8"))} if idx.exists() else {}
    if not args.no_fetch:
        for m in matches(args.pages):
            known[m["matchId"]] = m
        idx.write_text(json.dumps(list(known.values())), encoding="utf-8")
    ms = sorted((m for m in known.values() if args.since <= m["createdAt"] < args.until), key=lambda m: m["createdAt"])
    rows = []
    for m in ms:
        us = next(t for t in m["teams"] if t["teamId"].startswith(US))
        op = next(t for t in m["teams"] if not t["teamId"].startswith(US))
        path = OUT / f"{m['matchId'][:8]}.bin"
        if not path.exists():
            cambc("matches", "download", m["matchId"], "-o", str(path))
        if not path.exists():
            continue
        a = V.analyse(m["matchId"][:8], *load(path))
        if a:
            rows.append((m, us, op, a))
    agg = {True: defaultdict(float), False: defaultdict(float)}
    tagc = Counter()
    print("time  map                    opponent              W  final     r300     r500  deaths  eng won  spent500   camps    trib1     tags")
    for m, us, op, a in rows:
        me, opp = a["me"], a["opp"]
        win = us["result"] == "win"
        t, dm, do = tags(a, m["endReason"])
        eng = a["engagements"]
        won = Counter()
        for e in eng:
            if e["deaths"][me] != e["deaths"][opp]:
                won["us" if e["deaths"][me] < e["deaths"][opp] else "them"] += 1
        g = agg[win]
        g["n"] += 1
        g["deaths_us"] += dm
        g["deaths_them"] += do
        g["eng_us"] += won["us"]
        g["eng_them"] += won["them"]
        g["spend_us"] += a["spend"][me][500]
        g["spend_them"] += a["spend"][opp][500]
        g["camps_us"] += a["camp_hits"][me]
        g["camps_them"] += a["camp_hits"][opp]
        g["rounds"] += a["rounds"]
        if not win:
            for x in t:
                tagc[x] += 1
            f = a["final"] or (0, 0, 0)
            tl = a["timeline"]
            r3 = "%d-%d" % tl[300] if 300 in tl else "-"
            r5 = "%d-%d" % tl[500] if 500 in tl else "-"
            fu, ft = a["first_tribute"].get(me), a["first_tribute"].get(opp)
            print(f"{m['createdAt'][11:16]} {m['map'][:22]:22} {op['name'][:20]:20} {'W' if win else 'L'} "
                  f"{f[1]:4}-{f[2]:<4} {r3:>8} {r5:>8}  {dm:2}-{do:<2}   {won['us']:2}-{won['them']:<2}  "
                  f"{a['spend'][me][500]:4}-{a['spend'][opp][500]:<4} {a['camp_hits'][me]:4}-{a['camp_hits'][opp]:<4} "
                  f"{fu or '-'}/{ft or '-'}  {' '.join(t)}  [{m['matchId'][:8]} {us['side']}]")
    print(f"\nloss tags: {dict(tagc.most_common())}")
    for win in (True, False):
        g = agg[win]
        n = max(1, g["n"])
        rr = max(1, g["rounds"]) / 100
        print(f"{'WINS  ' if win else 'LOSSES'} n={int(g['n'])}: deaths/100r us {g['deaths_us'] / rr:.2f} them {g['deaths_them'] / rr:.2f}; "
              f"engagements won us {g['eng_us'] / n:.1f} them {g['eng_them'] / n:.1f}; spent by r500 us {g['spend_us'] / n:.0f} "
              f"them {g['spend_them'] / n:.0f}; camp hits us {g['camps_us'] / n:.0f} them {g['camps_them'] / n:.0f}")


if __name__ == "__main__":
    main()
