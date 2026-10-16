"""Draft: pick a fixed-priority roster, with an optional override per team size."""
import cambc
from cambc import ChampionDraft as CD

PRIORITY = (CD.VENDETTA, CD.VARG, CD.RYTH, CD.MARCELLA, CD.TAVI, CD.STELLAR, CD.VESPER_VALE,
            CD.CASSI_AND_ISSAC, CD.WILLOW, CD.REN, CD.PRISM)
# Team size -> priority list tried before PRIORITY (missing size = PRIORITY only).
BY_SIZE = {3: (CD.VENDETTA, CD.RYTH, CD.TAVI)}


def play():
    chosen = cambc.draft.current_draft(cambc.Team.ALLY)
    order = tuple(BY_SIZE.get(cambc.draft.team_size(), ())) + PRIORITY
    for pick in order:
        if pick not in chosen:
            cambc.draft.pick(pick)
            return
