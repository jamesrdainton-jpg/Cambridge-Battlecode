#!/usr/bin/env bash
# Queue 28 (2026-10-26, cambc 4.0.0, 70 maps, C++ main bot): the top teams' drafts in our bot.
#   c28b = cpp13 (v14: 3 = Vendetta, Ryth, Tavi; 4 = Vendetta, Vesper, Tavi, Marcella; 5 = + Ryth)
#   c28i = Intercontinental Fish / Mite style: 3 = Heart of Ruin, Vesper, Vendetta; 4 = + Cassi & Issac; 5 = + Marcella
#   c28t = Trzy Kwaterki style: 3 = Marcella, Ryth, Vendetta; 4 = + Vesper; 5 = + Heart of Ruin
# Each vs c28b, seeds 1,2. Caveat: self-play; the draft's value against the top teams depends on fight code we don't have.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
D3="draft.h:{ 3, { D::vendetta, D::ryth, D::tavi } }"
D4="draft.h:{ 4, { D::vendetta, D::vesper_vale, D::tavi, D::marcella } }"
D5="draft.h:{ 5, { D::vendetta, D::vesper_vale, D::tavi, D::marcella, D::ryth } }"
$PY $V c28b --src cpp13
$PY $V c28i --src cpp13 --set "$D3=>{ 3, { D::heart_of_ruin, D::vesper_vale, D::vendetta } }" \
    --set "$D4=>{ 4, { D::heart_of_ruin, D::vesper_vale, D::vendetta, D::cassi_and_issac } }" \
    --set "$D5=>{ 5, { D::heart_of_ruin, D::vesper_vale, D::vendetta, D::cassi_and_issac, D::marcella } }"
$PY $V c28t --src cpp13 --set "$D3=>{ 3, { D::marcella, D::ryth, D::vendetta } }" \
    --set "$D4=>{ 4, { D::marcella, D::ryth, D::vendetta, D::vesper_vale } }" \
    --set "$D5=>{ 5, { D::marcella, D::ryth, D::vendetta, D::vesper_vale, D::heart_of_ruin } }"
N="queue 28; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py c28i --vs c28b --seeds 1,2 --no-econ --note "c28i (Intercontinental/Mite draft) vs c28b (v14 draft); $N"
$PY tools/gauntlet.py c28t --vs c28b --seeds 1,2 --no-econ --note "c28t (Trzy Kwaterki draft) vs c28b (v14 draft); $N"
