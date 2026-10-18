"""Decode cambc replays (format 2, cambc 2.2.x) into champion actions and summarise each team's play.

Usage: python tools/replay_decode.py FILE [FILE ...] [--team a|b] [--buys]
FILE is a .repl26a, a platform match download (.zip with replay.repl26a inside) or a match-group .zip
(zips inside). Files are read in memory only.

Format, validated turn by turn against traced games (DEVLOG experiments 96 and 110):
  magic "a62per", format byte at offset 10 (2 = cambc 2.2.2, 3 = cambc 2.2.5), the embedded map file, u32 record count, then records:
  04 00 <u32 pick> 00                 draft pick, alternating team A / team B (format 3: 04 01 <u32> ff, then 03 00)
  03 <u8 reason>                      end of one champion's turn
  00 <u8 action> <payload>            champion action:
     00 (unknown)       u32 (other teams only; maybe the CLI's "turn priority")
     01 move            i32 x, i32 y (destination)
     02 attack          u8 target kind, u32 target, 4 bytes
     03 cast            u8 slot, u32 target entity, 4 bytes, i32 x, i32 y (-1 when no tile)
     04 recall          (none)
     05 submit gems     i32 altar x, i32 altar y
     06 buy item        u32 item, u32 count
     07 cancel channel  (none; inferred: always followed by a move or recall)
     08 buy consumable  u32 consumable (2 = altar lock), u32 count
     09 use consumable  u8 consumable, i32 x, i32 y
     0a place ward      i32 x, i32 y (inferred from the payload and the SDK's place_ward)
     0b sell item       u32 item
Turn order: every round the teams alternate champion by champion in draft order (Cassi & Issac are two
champions), team A starts round 1 and the starting team swaps each round, and the larger team's extra
champions go last. Deaths are inferred: a champion that reappears more than 3 tiles from its last tile,
next to its team's starting tiles, without a recall shortly before.
"""
from __future__ import annotations

import argparse
import io
import struct
import zipfile
from collections import Counter
from pathlib import Path

from common import ROOT

PICKS = ["Ryth", "Vesper", "Vendetta", "Cassi&Issac", "Stellar", "Prism", "Marcella", "Willow", "Ren", "Varg", "Tavi"]
FAMILIES = ["Monster", "Power", "Durability", "Treasure", "Jungle", "Home", "Bruiser"]
ITEMS = [f"{fam} {stat} {kind}" for fam in FAMILIES for stat in ("S", "F", "H") for kind in ("shard", "emblem")]
PAYLOAD = {0: 4, 1: 8, 2: 9, 3: 17, 4: 0, 5: 8, 6: 8, 7: 0, 8: 8, 9: 9, 10: 8, 11: 4}


def replays(path: Path) -> list[tuple[str, bytes]]:
    if path.suffix == ".repl26a" and not path.read_bytes().startswith(b"PK"):
        return [(path.name, path.read_bytes())]  # a bare replay (arena bundles are zips with this suffix)
    out = []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name.endswith(".repl26a"):
                out.append((path.stem, z.read(name)))
            elif name.endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(z.read(name))) as inner:
                    out += [(f"{path.stem}/{name[:-4]}", inner.read(n)) for n in inner.namelist() if n.endswith(".repl26a")]
    return out


def decode(data: bytes, maps: dict[str, bytes]) -> dict:
    """Map name, drafts and per-champion actions [(round, action, args)] for each team."""
    name, mb = next(((n, b) for n, b in maps.items() if b in data), ("?", b""))
    if not mb or data[10] not in (2, 3):
        return {"map": name, "error": "unknown map" if not mb else f"replay format {data[10]} unsupported"}
    o = data.find(mb) + len(mb)
    count = struct.unpack_from("<I", data, o)[0]
    o += 4
    picks: list[int] = []
    turns: list[list] = []
    cur: list = []
    n = 0
    error = ""
    draft_end = False
    while n < count and o < len(data):
        tag = data[o]
        if tag == 4:
            picks.append(struct.unpack_from("<I", data, o + 2)[0])
            o += 7
            draft_end = data[10] >= 3  # format 3 ends every draft pick with its own end-of-turn record
        elif tag == 3:
            if not draft_end:
                turns.append(cur)
                cur = []
            draft_end = False
            o += 2
        elif tag == 0 and data[o + 1] in PAYLOAD:
            sub = data[o + 1]
            p = data[o + 2:o + 2 + PAYLOAD[sub]]
            if sub in (1, 5, 10):
                args = struct.unpack("<ii", p)
            elif sub in (6, 8):
                args = struct.unpack("<II", p)
            elif sub == 2:
                args = (p[0], struct.unpack_from("<I", p, 1)[0])
            elif sub == 3:
                args = (p[0], struct.unpack_from("<I", p, 1)[0]) + struct.unpack_from("<ii", p, 9)
            elif sub == 9:
                args = (p[0],) + struct.unpack_from("<ii", p, 1)
            else:
                args = ()
            cur.append((sub, args))
            o += 2 + PAYLOAD[sub]
        else:
            error = f"unknown record {data[o:o + 2].hex(' ')} after {n} of {count} records"
            break
        n += 1
    teams = {"a": picks[0::2], "b": picks[1::2]}
    champs = {t: [c for p in teams[t] for c in (("Cassi", "Issac") if p == 3 else (PICKS[p],))] for t in teams}
    acts = {t: [[] for _ in champs[t]] for t in teams}
    t, r = 0, 1
    while t < len(turns):
        first, second = ("a", "b") if r % 2 == 1 else ("b", "a")
        for k in range(max(len(champs["a"]), len(champs["b"]))):
            for team in (first, second):
                if k < len(champs[team]) and t < len(turns):
                    acts[team][k] += [(r, sub, args) for sub, args in turns[t]]
                    t += 1
        r += 1
    return {"map": name, "rounds": r - 1, "draft": teams, "champs": champs, "acts": acts, "error": error}


def summarise(game: dict, team: str) -> dict:
    """Per-team strategy numbers: tributes, recalls, deaths, purchases, attacks, casts."""
    s = Counter()
    buys: list[tuple[int, str, str, int]] = []
    tributes: list[int] = []
    deaths: list[tuple[int, str]] = []
    first_moves = [next((a for r, sub, a in acts if sub == 1), None) for acts in game["acts"][team]]
    home = [m for m in first_moves if m]
    for champ, acts in zip(game["champs"][team], game["acts"][team], strict=True):
        last = None
        last_recall = -100
        for r, sub, a in acts:
            s[sub] += 1
            if sub == 1:
                if last and max(abs(a[0] - last[0]), abs(a[1] - last[1])) > 3 and r - last_recall > 12 \
                        and any(max(abs(a[0] - h[0]), abs(a[1] - h[1])) <= 2 for h in home):
                    deaths.append((r, champ))
                last = a
            elif sub == 2:
                s["attack_champion" if a[0] == 1 else "attack_camp" if a[0] == 2 else f"attack_kind{a[0]}"] += 1
            elif sub == 4:
                last_recall = r
            elif sub == 5:
                tributes.append(r)
            elif sub == 6:
                buys.append((r, champ, ITEMS[a[0]] if a[0] < len(ITEMS) else f"item{a[0]}", a[1]))
            elif sub == 8:
                buys.append((r, champ, "altar lock" if a[0] == 2 else f"consumable{a[0]}", a[1]))
            elif sub == 10:
                s["wards"] += 1
            elif sub == 9:
                s["lock placed" if a[0] == 2 else f"consumable{a[0]} used"] += 1
    tributes.sort()
    gaps = [b - a for a, b in zip(tributes, tributes[1:], strict=False)]
    return {"tributes": len(tributes), "first_tribute": tributes[0] if tributes else None,
            "tribute_gap": round(sum(gaps) / len(gaps), 1) if gaps else None, "recalls": s[4],
            "deaths": deaths, "attack_camp": s["attack_camp"], "attack_champion": s["attack_champion"],
            "casts": s[3], "moves": s[1], "buys": buys, "locks": s["lock placed"], "wards": s["wards"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    parser.add_argument("--buys", action="store_true", help="list every purchase")
    args = parser.parse_args()
    maps = {p.stem: p.read_bytes() for p in (ROOT / "maps").glob("*.map26a")}
    for f in args.files:
        for label, data in replays(Path(f)):
            game = decode(data, maps)
            if "acts" not in game:
                print(f"{label}: {game['map']} {game['error']}")
                continue
            print(f"\n{label}: {game['map']}, {game['rounds']} rounds{' (' + game['error'] + ')' if game['error'] else ''}")
            for team in ("a", "b"):
                sm = summarise(game, team)
                print(f"  {team.upper()} {', '.join(game['champs'][team])}")
                print(f"    tributes {sm['tributes']} (first r{sm['first_tribute']}, every {sm['tribute_gap']} rounds), "
                      f"recalls {sm['recalls']}, deaths {len(sm['deaths'])} {[r for r, _ in sm['deaths']][:12]}, "
                      f"attacks camp/champion {sm['attack_camp']}/{sm['attack_champion']}, casts {sm['casts']}, "
                      f"locks {sm['locks']}, wards {sm['wards']}")
                if args.buys:
                    for r, champ, item, k in sm["buys"]:
                        print(f"      r{r:<5} {champ:9} {item} x{k}")


if __name__ == "__main__":
    main()
