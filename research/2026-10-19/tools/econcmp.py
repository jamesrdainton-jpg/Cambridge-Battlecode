"""Per-game economy comparison, our team vs opponent, for our platform games (with stdout).
Usage: python -I econcmp.py DIR..."""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(_ROOT / "tools"))
sys.path.insert(0, str(_HERE))
import replay_decode as RD
from replay_profile import per_turn
from ourgames import games
from targets import CAMPS
ROOT = _ROOT
maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
HP = {"w": 1350, "e": 2400, "g": 500, "G": 500, "M": 20000}
GEMS = {"w": 22, "e": 36, "g": 24, "G": 0, "M": 200}
tot = {"us": Counter(), "them": Counter()}
print(f"{'map':11} {'res':4} {'r':>5} | {'bodies':>6} {'hits/100r':>9} {'casts/100r':>10} {'gold@150':>8} {'gold@300':>8} {'deaths':>6} {'gemHP%':>6} | same for opponent | gems@300")
for label, side, f in games(sys.argv[1:]):
    if side is None:
        continue
    g = per_turn(f["replay.repl26a"], maps)
    out = f[f"team-{side}.stdout"].decode(errors="replace").replace("\x00", "")
    stats = [tuple(map(int, l.split()[1:4])) for l in out.splitlines() if l.startswith("STAT ")]
    last = stats[-1]
    win = last[1] > last[2]
    at300 = next((s for s in stats if s[0] >= 300), last)
    cm = CAMPS[g["map"]]
    rowp = []
    dec = RD.decode(f["replay.repl26a"], maps)
    for team, who in ((side, "us"), ("b" if side == "a" else "a", "them")):
        c = Counter()
        c["bodies"] = len(g["champs"][team])
        for champ, tl in zip(g["champs"][team], g["turns"][team]):
            for r, acts in tl:
                for sub, a in acts:
                    if r > 300:
                        continue
                    if sub == 2 and a[0] == 2:
                        c["hits"] += 1
                        k = cm.get(a[1], ("?",))[0]
                        c["hp_" + k] += 1
                    elif sub == 3 and a[1] == 2:
                        c["casts"] += 1
                    elif sub == 6:
                        if r <= 150:
                            c["g150"] += 30 * a[1]
                        c["g300"] += 30 * a[1]
                    elif sub == 8:
                        if r <= 150:
                            c["g150"] += 10 * a[1]
                        c["g300"] += 10 * a[1]
        sm = RD.summarise(dec, team)
        c["deaths"] = sum(1 for r, _ in sm["deaths"] if r <= 300)
        gem_hits = sum(c["hp_" + k] for k in "weg")
        c["gemhp"] = round(100 * c["hp_g"] / max(1, gem_hits))
        tot[who].update(c)
        tot[who]["games"] += 1
        tot[who]["wins"] += win if who == "us" else not win
        rowp.append(f"{c['bodies']:6} {c['hits']/3:9.0f} {c['casts']/3:10.0f} {c['g150']:8} {c['g300']:8} {c['deaths']:6} {c['gemhp']:6}")
    print(f"{g['map']:11} {'W' if win else 'L':4} {g['rounds']:5} | {rowp[0]} | {rowp[1]} | {at300[1]}-{at300[2]}")
for who in ("us", "them"):
    t = tot[who]
    n = t["games"]
    print(f"{who:5} avg: bodies {t['bodies']/n:.2f}, camp hits/100r {t['hits']/n/3:.0f}, casts on camps/100r {t['casts']/n/3:.0f}, gold spent by r150 {t['g150']/n:.0f}, by r300 {t['g300']/n:.0f}, deaths by r300 {t['deaths']/n:.1f}")
