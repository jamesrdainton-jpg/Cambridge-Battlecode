#!/usr/bin/env bash
# Queue 16 (2026-10-25, cambc 3.0.5, 40 maps): screen boss raids and 3.0 drafts against the v13 candidate.
# Base x14a = mybot (WAIT_LIMIT 0; BOSS_NEED_FRAC and BOSS_WAIT off) with DEBUG off, i.e. x13b's behaviour.
# Seed 1 only (80 games each) for screening; confirm winners with seed 2.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
$PY $V x14a
# Boss raids: size monolith/golem squads at a higher damage tolerance and gather before engaging.
$PY $V x14b --set "bot.py:BOSS_NEED_FRAC = 0.0=>BOSS_NEED_FRAC = 1.0" --set "bot.py:BOSS_WAIT = 0=>BOSS_WAIT = 40"
$PY $V x14c --set "bot.py:BOSS_NEED_FRAC = 0.0=>BOSS_NEED_FRAC = 1.5" --set "bot.py:BOSS_WAIT = 0=>BOSS_WAIT = 40"
# Drafts (3-pick maps keep Vendetta, Ryth, Tavi unless noted).
# x14d: the strong teams' 3.0 draft at every size: Vesper, Heart of Ruin, Vendetta; + Cassi & Issac; + Marcella.
$PY $V x14d --set "draft.py:PRO_DRAFT = (4, 5)=>PRO_DRAFT = (3, 4, 5)" \
  --set "draft.py:PRO_BY_SIZE = {=>PRO_BY_SIZE = {3: (CD.VESPER_VALE, CD.HEART_OF_RUIN, CD.VENDETTA), 4: (CD.VESPER_VALE, CD.HEART_OF_RUIN, CD.VENDETTA, CD.CASSI_AND_ISSAC), 5: (CD.VESPER_VALE, CD.HEART_OF_RUIN, CD.VENDETTA, CD.CASSI_AND_ISSAC, CD.MARCELLA)}; _OLD_PRO = {"
# x14e: strength champions the patch buffed, no Heart of Ruin: 4 = Vendetta, Vesper, Tavi, Marcella; 5 = + Ryth.
$PY $V x14e --set "draft.py:PRO_BY_SIZE = {=>PRO_BY_SIZE = {4: (CD.VENDETTA, CD.VESPER_VALE, CD.TAVI, CD.MARCELLA), 5: (CD.VENDETTA, CD.VESPER_VALE, CD.TAVI, CD.MARCELLA, CD.RYTH)}; _OLD_PRO = {"
# x14f: drop the 2.2.5 pro draft: 4 = Vendetta, Varg, Ryth, Tavi; 5 = Vendetta, Varg, Ryth, Marcella, Tavi.
$PY $V x14f --set "draft.py:PRO_DRAFT = (4, 5)=>PRO_DRAFT = ()"
for X in x14b x14c x14d x14e x14f; do
  $PY tools/gauntlet.py $X --vs x14a --seeds 1 --no-econ --note "$X vs x14a (base: WAIT_LIMIT 0); queue 16 screening; cambc 3.0.5, 40 maps"
done
