"""Analyse cambc 3.0 platform match groups (in memory). Usage: python -I research/2026-10-25/tools/games30.py ZIP...
Per game: map, rounds, drafts, our side and STAT result, and per team: tributes, deaths (decoder inference), camp hits by
camp kind (w e g G M O), champion hits, casts by target, gold spent by r300/r1000/end, first buy, wards, locks, boss windows."""
import io, re, sys, zipfile, struct, json
from collections import Counter, defaultdict
from pathlib import Path

repo = Path(__file__).resolve().parents[3]
pool = repo / "maps"
dumps = repo / "research" / "2026-10-25" / "data" / "mapdumps"
OUT = repo / "matches" / "research"
sys.path.insert(0, str(repo / "tools"))
import replay_decode as RD  # noqa: E402
RD.PICKS = RD.PICKS + ["HeartOfRuin"]
maps = {p.stem[2:]: p.read_bytes() for p in pool.glob("*.map26a")}
camps = {}
for t in dumps.glob("*.txt"):
    cm = {}
    for line in t.read_text().splitlines():
        if line.startswith("CAMPH"):
            _, h, k, x, y, g = line.split()
            cm[int(h)] = (k, int(x), int(y), int(g))
    camps[t.stem[2:]] = cm
COST = lambda item: 30  # every purchasable shard costs 30; emblems combine automatically
rows = []
out_json = []
for zp in sys.argv[1:]:
    z = zipfile.ZipFile(zp)
    gid = Path(zp).name[12:20]
    for n in sorted(z.namelist()):
        if not n.endswith(".zip"):
            continue
        inner = zipfile.ZipFile(io.BytesIO(z.read(n)))
        names = inner.namelist()
        data = inner.read("replay.repl26a")
        side = "a" if "team-a.stdout" in names else "b" if "team-b.stdout" in names else None
        g = RD.decode(data, maps)
        label = f"{gid}/{n[:2]}"
        if "acts" not in g:
            print(label, g.get("map"), g.get("error")); continue
        res = ""
        if side:
            out = inner.read(f"team-{side}.stdout").decode(errors="replace").replace("\x00", "")
            st = [tuple(map(int, l.split()[1:4])) for l in out.splitlines() if l.startswith("STAT ")]
            crash = sum(1 for l in out.splitlines() if l.startswith("bot error"))
            if st:
                last = st[-1]
                res = f"us {last[1]}-{last[2]} @r{last[0]}"
            else:
                res = f"CRASH x{crash}"
        cm = camps.get(g["map"], {})
        info = {"label": label, "map": g["map"], "rounds": g["rounds"], "side": side, "res": res, "err": g["error"], "teams": {}}
        for team in "ab":
            hits = Counter(); champhits = 0; casts = Counter(); spent = Counter(); first_buy = None
            boss_rounds = []; tributes = []; wards = 0; locks = 0; recalls = 0; dist = Counter(); deaths = 0
            for champ, acts in zip(g["champs"][team], g["acts"][team]):
                pos = None
                for r, sub, a in acts:
                    if sub == 1:
                        pos = a
                    elif sub == 2:
                        if a[0] == 2:
                            c = cm.get(a[1]); k = c[0] if c else "?"
                            hits[k] += 1
                            if k in "MO":
                                boss_rounds.append(r)
                                if pos: dist[max(abs(pos[0]-c[1]), abs(pos[1]-c[2]))] += 1
                        elif a[0] == 1:
                            champhits += 1
                    elif sub == 3:
                        tk = a[1]
                        if tk == 2:
                            c = cm.get(a[2]); k = c[0] if c else "?"
                            casts["camp:" + k] += 1
                            if k in "MO":
                                boss_rounds.append(r)
                        else:
                            casts[{0: "none", 1: "champ"}.get(tk, str(tk))] += 1
                    elif sub == 4:
                        recalls += 1
                    elif sub == 5:
                        tributes.append(r)
                    elif sub == 6:
                        cost = 30 * a[1]
                        for lim in (300, 1000, 9999):
                            if r <= lim: spent[lim] += cost
                        first_buy = r if first_buy is None else min(first_buy, r)
                    elif sub == 8:
                        for lim in (300, 1000, 9999):
                            if r <= lim: spent[lim] += 10 * a[1]
                    elif sub == 9 and a[0] == 2:
                        locks += 1
                    elif sub == 10:
                        wards += 1
            sm = RD.summarise(g, team)
            boss_rounds.sort()
            info["teams"][team] = dict(draft=g["champs"][team], tributes=len(tributes), first_trib=tributes[0] if tributes else None,
                                       deaths=len(sm["deaths"]), hits=dict(hits), champhits=champhits, casts=dict(casts),
                                       spent=dict(spent), first_buy=first_buy, wards=wards, locks=locks, recalls=recalls,
                                       boss_first=boss_rounds[0] if boss_rounds else None, boss_n=len(boss_rounds),
                                       boss_dist=dict(sorted(dist.items())))
        out_json.append(info)
        print(f"\n== {label} {g['map']} r{g['rounds']} ours={side} {res} {('ERR ' + g['error']) if g['error'] else ''}")
        for team in "ab":
            t = info["teams"][team]
            tag = "US " if team == side else "   "
            print(f"  {tag}{team} {','.join(t['draft'])}")
            print(f"       trib {t['tributes']} (first r{t['first_trib']}) deaths {t['deaths']} recalls {t['recalls']} hits {t['hits']} champhits {t['champhits']} casts {t['casts']}")
            print(f"       spent r300 {t['spent'].get(300,0)} r1000 {t['spent'].get(1000,0)} end {t['spent'].get(9999,0)} first_buy r{t['first_buy']} wards {t['wards']} locks {t['locks']} boss first r{t['boss_first']} n={t['boss_n']} dist {t['boss_dist']}")
OUT.mkdir(parents=True, exist_ok=True)
json.dump(out_json, open(OUT / "games30.json", "w"), indent=1)
