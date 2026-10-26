"""Draft: pick a fixed-priority roster, with an optional override per team size."""
import cambc
from cambc import ChampionDraft as CD

PRIORITY = (CD.VENDETTA, CD.VARG, CD.RYTH, CD.MARCELLA, CD.TAVI, CD.STELLAR, CD.VESPER_VALE,
            CD.CASSI_AND_ISSAC, CD.WILLOW, CD.REN, CD.PRISM)
# Team size -> priority list tried before PRIORITY (missing size = PRIORITY only). Since cambc 3.0 the 4- and 5-pick
# drafts use strength champions the patch buffed (Vendetta 1,000 HP, Vesper +33% gold, Tavi 900 HP, Marcella 2 gold per
# gem tributed): 130/160 vs the 2.2.5 pro draft below and 103/160 vs Vendetta, Varg, Ryth, Tavi (+ Marcella) (DEVLOG 149-150).
BY_SIZE = {3: (CD.VENDETTA, CD.RYTH, CD.TAVI), 4: (CD.VENDETTA, CD.VESPER_VALE, CD.TAVI, CD.MARCELLA),
           5: (CD.VENDETTA, CD.VESPER_VALE, CD.TAVI, CD.MARCELLA, CD.RYTH)}
# The strong platform teams' 2.2.5 draft by team size (Cassi & Issac, Stellar, Ren, then Ryth, then Varg), used instead of
# BY_SIZE for the team sizes listed in PRO_DRAFT (() = off). Off since cambc 3.0 nerfed those champions.
PRO_DRAFT = ()
PRO_BY_SIZE = {3: (CD.CASSI_AND_ISSAC, CD.STELLAR, CD.REN), 4: (CD.CASSI_AND_ISSAC, CD.STELLAR, CD.REN, CD.RYTH),
               5: (CD.CASSI_AND_ISSAC, CD.STELLAR, CD.REN, CD.RYTH, CD.VARG)}


# Map facts for the champion bots, worked out on the first draft turn (Python gets 250M fuel there since cambc 4.0) and
# sent through draft memory. Byte 0, bit 0: no altar can be reached without killing a camp first (01boss-battle and
# 02guardians put the only altar between two monoliths, 02the-pack inside a ring of 48 wolves). Nobody can tribute there
# until a boss falls, so the round limit decides on lifetime gold earned (bot.py LOCKED_GOLD).
SENT = [False]


def analyse():
    from cambc import game_map, Bitboard, DistanceField, Team
    block = game_map.walls() | game_map.holes() | game_map.altars() | game_map.spawn_region(Team.ENEMY)
    camps = Bitboard()
    for g in game_map.camp_groups():
        for c in g.camps():
            camps.set(c.spawn_position())
    approach = Bitboard()
    for a in game_map.altars().positions():
        approach.draw_chebyshev(a, 1)
    approach &= ~(block | camps)
    field = DistanceField()
    field.compute(block | camps, game_map.spawn_region(Team.ALLY), Bitboard())
    for p in approach.positions():
        d = field.get(p)
        if d is not None and d < 65535:
            return bytes([0])
    return bytes([1])


def play():
    if not SENT[0]:
        SENT[0] = True
        try:
            cambc.draft_memory.submit(analyse())
        except Exception as error:  # noqa: BLE001 - the picks matter more
            print(f"draft analysis failed: {error!r}")
    chosen = cambc.draft.current_draft(cambc.Team.ALLY)
    size = cambc.draft.team_size()
    by_size = PRO_BY_SIZE if size in PRO_DRAFT else BY_SIZE
    order = tuple(by_size.get(size, ())) + PRIORITY
    for pick in order:
        if pick not in chosen:
            cambc.draft.pick(pick)
            return
