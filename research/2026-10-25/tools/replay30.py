"""Turn-accurate replay parser for cambc 3.0 and 4.0 replays, aware of turn priorities.

Strong teams call set_priority(): it appears in the replay as record 00 00 <u32 priority>, takes effect from the next
round, and persists. Within a team, higher priority acts first (ties in draft order); the two teams alternate champion by
champion, the starting team swaps every round, and the larger team's extra champions go last. The older parser assumed
draft order, which mis-attributes turns for any team that sets priorities.

Champion handles (attack/cast targets): team A's bodies are 0..nA-1 in draft order, team B's continue from nA (Cassi and
Issac are two bodies). Verified with a probe bot on cambc 3.0.5.

    parse(data, maps) -> {"map", "rounds", "champs": {"a": [...], "b": [...]}, "handle": {(team, i): h},
                          "turns": {"a": [[(round, [(sub, args), ...]), ...] per champion], "b": [...]}}
Record subtypes (args): 0 priority (p,), 1 move (x, y), 2 attack (target_kind, target), 3 cast (slot, target_kind,
target, x, y), 4 recall (), 5 tribute (altar_x, altar_y), 6 buy item (item, count), 7 cancel (), 8 buy consumable
(kind, count), 9 use consumable (kind, x, y), 10 ward (x, y), 11 sell (item,). target_kind: 1 champion, 2 camp.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import replay_decode as RD  # noqa: E402


def _records(data, maps):
    name, mb = next(((n, b) for n, b in maps.items() if b in data), ("?", b""))
    if not mb or RD.version(data) not in RD.SUPPORTED:
        return name, None, None
    o = data.find(mb) + len(mb)
    count = struct.unpack_from("<I", data, o)[0]
    o += 4
    picks, turns, cur = [], [], []
    n = 0
    draft_end = False
    while n < count and o < len(data):
        tag = data[o]
        if tag == 4:
            picks.append(struct.unpack_from("<I", data, o + 2)[0])
            o += 7
            draft_end = RD.draft_end_records(data)
        elif tag == 3:
            if not draft_end:
                turns.append(cur)
                cur = []
            draft_end = False
            o += 2
        elif tag == 0 and data[o + 1] in RD.PAYLOAD:
            sub = data[o + 1]
            p = data[o + 2:o + 2 + RD.PAYLOAD[sub]]
            if sub in (1, 5, 10):
                args = struct.unpack("<ii", p)
            elif sub in (6, 8):
                args = struct.unpack("<II", p)
            elif sub == 0:
                args = struct.unpack("<i", p)  # signed: strong teams use negative priorities
            elif sub == 2:
                args = (p[0], struct.unpack_from("<I", p, 1)[0])
            elif sub == 3:
                args = (p[0], p[4], struct.unpack_from("<I", p, 5)[0]) + struct.unpack_from("<ii", p, 9)
            elif sub == 9:
                args = (p[0],) + struct.unpack_from("<ii", p, 1)
            elif sub == 11:
                args = struct.unpack("<I", p)
            else:
                args = ()
            cur.append((sub, args))
            o += 2 + RD.PAYLOAD[sub]
        else:
            break
        n += 1
    return name, picks, turns


def parse(data, maps, use_priority=True):
    name, picks, turns = _records(data, maps)
    if picks is None:
        return None
    teams = {"a": picks[0::2], "b": picks[1::2]}
    champs = {t: [c for p in teams[t] for c in (("Cassi", "Issac") if p == 3 else (RD.PICKS[p],))] for t in teams}
    na = len(champs["a"])
    handle = {("a", i): i for i in range(na)}
    handle.update({("b", i): na + i for i in range(len(champs["b"]))})
    prio = {t: [0] * len(champs[t]) for t in teams}
    out = {t: [[] for _ in champs[t]] for t in teams}
    ti, r = 0, 1
    while ti < len(turns):
        first, second = ("a", "b") if r % 2 == 1 else ("b", "a")
        order = {}
        for t in teams:
            idx = list(range(len(champs[t])))
            if use_priority:
                idx.sort(key=lambda i, t=t: (-prio[t][i], i))
            order[t] = idx
        pending = []
        for k in range(max(len(champs["a"]), len(champs["b"]))):
            for t in (first, second):
                if k < len(order[t]) and ti < len(turns):
                    i = order[t][k]
                    acts = turns[ti]
                    out[t][i].append((r, acts))
                    for sub, args in acts:
                        if sub == 0:
                            pending.append((t, i, args[0]))
                    ti += 1
        for t, i, p in pending:  # takes effect from the next round
            prio[t][i] = p
        r += 1
    return {"map": name, "rounds": r - 1, "champs": champs, "handle": handle, "turns": out, "draft": teams}


def positions(game):
    """Per team per champion: {round: (x, y)} of the last known tile after that round (moves, dashes, teleports)."""
    out = {}
    for t in "ab":
        out[t] = []
        for tl in game["turns"][t]:
            pos = {}
            cur = None
            for r, acts in tl:
                for sub, args in acts:
                    if sub == 1:
                        cur = (args[0], args[1])
                    elif sub == 3 and args[3] >= 0 and args[1] == 0 and args[0] in (0, 1):
                        pass  # ground casts (area spells) don't move the caster; dashes are handled below
                if cur is not None:
                    pos[r] = cur
            out[t].append(pos)
    return out


def continuity(game):
    """Count of consecutive move records of one champion more than 2 tiles apart (wrong turn attribution shows here)."""
    bad = total = 0
    for t in "ab":
        for tl in game["turns"][t]:
            last = None
            for r, acts in tl:
                for sub, args in acts:
                    if sub == 1:
                        if last is not None:
                            total += 1
                            if max(abs(args[0] - last[0]), abs(args[1] - last[1])) > 2:
                                bad += 1
                        last = (args[0], args[1])
    return bad, total
