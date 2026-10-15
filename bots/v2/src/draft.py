"""Draft: pick a fixed-priority roster that suits most maps."""
import cambc
from cambc import ChampionDraft as CD

PRIORITY = (CD.VENDETTA, CD.VARG, CD.RYTH, CD.TAVI, CD.STELLAR, CD.VESPER_VALE, CD.MARCELLA,
            CD.CASSI_AND_ISSAC, CD.WILLOW, CD.REN, CD.PRISM)


def play():
    chosen = cambc.draft.current_draft(cambc.Team.ALLY)
    for pick in PRIORITY:
        if pick not in chosen:
            cambc.draft.pick(pick)
            return
