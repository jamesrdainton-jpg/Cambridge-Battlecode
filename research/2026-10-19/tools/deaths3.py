"""Per game deaths (robust rule) for our team vs the opponent, from our platform match groups (stdout side = us)."""
import os as _os
from pathlib import Path as _Path
_HERE = _Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_WORK = _Path(_os.environ.get("RS_WORK", str(_ROOT / "matches" / "research")))
import sys
from pathlib import Path
sys.path.insert(0, str(_ROOT / "tools"))
sys.path.insert(0, str(_HERE))
from replay_profile import per_turn
from ourgames import games
ROOT = _ROOT
maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
def deaths(g, team, upto=10**9):
    d = 0; seen = set()
    for champ, tl in zip(g["champs"][team], g["turns"][team]):
        last = None
        for r, acts in tl:
            if r > upto:
                break
            if any(s in (1, 2, 3, 4, 5) for s, _ in acts):
                if last is not None and r - last >= 55:
                    key = (r // 5, "CI") if champ in ("Cassi", "Issac") else (r, champ)
                    if key not in seen:
                        seen.add(key); d += 1
                last = r
    return d
U = T = R = 0; W = []
for label, side, f in games(sys.argv[1:]):
    if side is None:
        continue
    g = per_turn(f["replay.repl26a"], maps)
    out = f[f"team-{side}.stdout"].decode(errors="replace").replace("\x00", "")
    st = [tuple(map(int, l.split()[1:4])) for l in out.splitlines() if l.startswith("STAT ")]
    win = st[-1][1] > st[-1][2]
    other = "b" if side == "a" else "a"
    u, t = deaths(g, side, 500), deaths(g, other, 500)
    U += u; T += t; R += min(500, g["rounds"])
    W.append((win, u, t, g["map"]))
print(f"rounds 1-500: our deaths {U}, opponents' {T} over {len(W)} games ({100*U/R:.2f} vs {100*T/R:.2f} per 100 rounds)")
for w in (True, False):
    sub = [x for x in W if x[0] == w]
    print(f"  {'wins' if w else 'losses'} ({len(sub)}): our deaths {sum(x[1] for x in sub)}, theirs {sum(x[2] for x in sub)}")
