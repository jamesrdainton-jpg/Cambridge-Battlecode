"""Draft: pick a fixed-priority roster, with an optional override per team size."""
import cambc
from cambc import ChampionDraft as CD

PRIORITY = (CD.STELLAR, CD.CASSI_AND_ISSAC, CD.VARG, CD.RYTH, CD.REN, CD.MARCELLA, CD.TAVI, CD.VENDETTA, CD.PRISM, CD.WILLOW, CD.VESPER_VALE,)
# Team size -> priority list tried before PRIORITY (missing size = PRIORITY only).
BY_SIZE = {}


def play():
    chosen = cambc.draft.current_draft(cambc.Team.ALLY)
    order = tuple(BY_SIZE.get(cambc.draft.team_size(), ())) + PRIORITY
    for pick in order:
        if pick not in chosen:
            cambc.draft.pick(pick)
            return
