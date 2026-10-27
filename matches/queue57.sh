#!/usr/bin/env bash
# Queue 57 (2026-10-27, cambc 4.0.0, 70 maps, C++): after queue 56 (NEED_FRAC 0.45 161/280, ENEMY_SIDE 0.7 150/280 vs
# cpp20). nf35 = cpp20 with NEED_FRAC 0.35 (even bigger squads); ne = cpp20 with NEED_FRAC 0.45 + ENEMY_SIDE 0.7.
# Vs cpp20 (live v19), seeds 1,2.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py nf35 --src cpp20 --set "params.h:NEED_FRAC = 0.55=>NEED_FRAC = 0.35"
$PY tools/variant.py ne --src cpp20 --set "params.h:NEED_FRAC = 0.55=>NEED_FRAC = 0.45" --set "params.h:ENEMY_SIDE = 0.85=>ENEMY_SIDE = 0.7"
$PY tools/gauntlet.py nf35 --vs cpp20 --seeds 1,2 --note "nf35 (cpp20 + NEED_FRAC 0.35) vs cpp20; queue 57; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py ne --vs cpp20 --seeds 1,2 --note "ne (cpp20 + NEED_FRAC 0.45 + ENEMY_SIDE 0.7) vs cpp20; queue 57; cambc 4.0.0, 70 maps, C++"
