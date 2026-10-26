#!/usr/bin/env bash
# Queue 17 (2026-10-25, cambc 3.0.5, 40 maps): confirm the two winning drafts of queue 16 on seed 2 and play them
# head to head. All variants come from mybot at commit cda0be7 (WAIT_LIMIT 0, camp-vision guard), DEBUG off.
#   y15a = mybot (2.2.5 pro draft at 4-5 picks: Cassi & Issac, Stellar, Ren, Ryth, Varg)
#   y15e = 4 = Vendetta, Vesper, Tavi, Marcella; 5 = + Ryth (queue 16: 65/80, +27,518)
#   y15f = PRO_DRAFT off: 4 = Vendetta, Varg, Ryth, Tavi; 5 = Vendetta, Varg, Ryth, Marcella, Tavi (65/80, +21,305)
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
$PY $V y15a
$PY $V y15e --set "draft.py:PRO_BY_SIZE = {=>PRO_BY_SIZE = {4: (CD.VENDETTA, CD.VESPER_VALE, CD.TAVI, CD.MARCELLA), 5: (CD.VENDETTA, CD.VESPER_VALE, CD.TAVI, CD.MARCELLA, CD.RYTH)}; _OLD_PRO = {"
$PY $V y15f --set "draft.py:PRO_DRAFT = (4, 5)=>PRO_DRAFT = ()"
$PY tools/gauntlet.py y15e --vs y15a --seeds 2 --no-econ --note "y15e vs y15a seed 2 (queue 17 confirmation); cambc 3.0.5, 40 maps"
$PY tools/gauntlet.py y15f --vs y15a --seeds 2 --no-econ --note "y15f vs y15a seed 2 (queue 17 confirmation); cambc 3.0.5, 40 maps"
$PY tools/gauntlet.py y15e --vs y15f --seeds 1,2 --note "y15e vs y15f head to head (queue 17), with economy; cambc 3.0.5, 40 maps"
