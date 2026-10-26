#!/usr/bin/env bash
# Queue 25 (2026-10-26, cambc 4.0.0, 70 maps): the v14 candidate on the new patch. All variants include the 00vault fix
# (DEVLOG 160); v13 does not, so expect about +2 games of 140 from 00vault alone.
#   z25a = mybot + BUILD_30 1 + FIGHT_PRIO (the 3.0.5 candidate: Treasure first, which 4.0 halved to +10% gold)
#   z25c = mybot + BUILD_30 3 + FIGHT_PRIO (Capture first: captures take 3 turns, not 5)
#   z25m = mybot + BUILD_30 4 + FIGHT_PRIO (Monster first: +15% camp damage)
#   z25p = mybot + BUILD_30 5 + FIGHT_PRIO (Prospector first: +25% of own cluster gold and gems)
#   c25a = cpp13 + BUILD_30 1 + FIGHT_PRIO (C++)
# Stage 1: each vs v13, seed 1. Stage 2 (separate script): the best build on seed 2 and C++ vs Python.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
F="bot.py:FIGHT_PRIO = False=>FIGHT_PRIO = True"
$PY $V z25a --set "bot.py:BUILD_30 = 0=>BUILD_30 = 1" --set "$F"
$PY $V z25c --set "bot.py:BUILD_30 = 0=>BUILD_30 = 3" --set "$F"
$PY $V z25m --set "bot.py:BUILD_30 = 0=>BUILD_30 = 4" --set "$F"
$PY $V z25p --set "bot.py:BUILD_30 = 0=>BUILD_30 = 5" --set "$F"
$PY $V c25a --src cpp13 --set "params.h:BUILD_30 = 0=>BUILD_30 = 1" --set "params.h:FIGHT_PRIO = false=>FIGHT_PRIO = true"
N="queue 25; cambc 4.0.0, 70 maps"
$PY tools/gauntlet.py z25a --vs v13 --seeds 1 --no-econ --note "z25a = BUILD_30 1 + FIGHT_PRIO vs v13; $N"
$PY tools/gauntlet.py z25c --vs v13 --seeds 1 --no-econ --note "z25c = BUILD_30 3 (Capture first) + FIGHT_PRIO vs v13; $N"
$PY tools/gauntlet.py z25m --vs v13 --seeds 1 --no-econ --note "z25m = BUILD_30 4 (Monster first) + FIGHT_PRIO vs v13; $N"
$PY tools/gauntlet.py z25p --vs v13 --seeds 1 --no-econ --note "z25p = BUILD_30 5 (Prospector first) + FIGHT_PRIO vs v13; $N"
$PY tools/gauntlet.py c25a --vs v13 --seeds 1 --no-econ --note "c25a = C++ + BUILD_30 1 + FIGHT_PRIO vs v13; $N"
