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


def play():
    chosen = cambc.draft.current_draft(cambc.Team.ALLY)
    size = cambc.draft.team_size()
    by_size = PRO_BY_SIZE if size in PRO_DRAFT else BY_SIZE
    order = tuple(by_size.get(size, ())) + PRIORITY
    for pick in order:
        if pick not in chosen:
            cambc.draft.pick(pick)
            return
