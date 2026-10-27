#!/usr/bin/env bash
# Queue 56 (2026-10-27, cambc 4.0.0, 70 maps, C++): the other direction after queue 55 (ENEMY_SIDE 1.0 128/280,
# NEED_FRAC 0.7 119/280 vs cpp20). nf45 = cpp20 with NEED_FRAC 0.45 (bigger squads); es70 = cpp20 with ENEMY_SIDE 0.7.
# Vs cpp20 (live v19), seeds 1,2.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py nf45 --src cpp20 --set "params.h:NEED_FRAC = 0.55=>NEED_FRAC = 0.45"
$PY tools/variant.py es70 --src cpp20 --set "params.h:ENEMY_SIDE = 0.85=>ENEMY_SIDE = 0.7"
$PY tools/gauntlet.py nf45 --vs cpp20 --seeds 1,2 --note "nf45 (cpp20 + NEED_FRAC 0.45) vs cpp20; queue 56; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py es70 --vs cpp20 --seeds 1,2 --note "es70 (cpp20 + ENEMY_SIDE 0.7) vs cpp20; queue 56; cambc 4.0.0, 70 maps, C++"
