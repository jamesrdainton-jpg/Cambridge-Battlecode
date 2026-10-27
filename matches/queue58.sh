#!/usr/bin/env bash
# Queue 58 (2026-10-27, cambc 4.0.0, 70 maps, C++): queue 57 was killed by a session restart during nf35's economy games
# (its head to head had finished: nf35 164/280, +26,426; 83, 81 vs cpp20; no row written). Rerun nf35 for the row, plus
# nf25 = cpp20 with NEED_FRAC 0.25 (where does the trend stop?) and ne35 = cpp20 with NEED_FRAC 0.35 + ENEMY_SIDE 0.7.
# Vs cpp20 (live v19), seeds 1,2.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py nf35 --src cpp20 --set "params.h:NEED_FRAC = 0.55=>NEED_FRAC = 0.35"
$PY tools/variant.py nf25 --src cpp20 --set "params.h:NEED_FRAC = 0.55=>NEED_FRAC = 0.25"
$PY tools/variant.py ne35 --src cpp20 --set "params.h:NEED_FRAC = 0.55=>NEED_FRAC = 0.35" --set "params.h:ENEMY_SIDE = 0.85=>ENEMY_SIDE = 0.7"
$PY tools/gauntlet.py nf35 --vs cpp20 --seeds 1,2 --note "nf35 (cpp20 + NEED_FRAC 0.35) vs cpp20; queue 58 (rerun of 57); cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py nf25 --vs cpp20 --seeds 1,2 --note "nf25 (cpp20 + NEED_FRAC 0.25) vs cpp20; queue 58; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py ne35 --vs cpp20 --seeds 1,2 --note "ne35 (cpp20 + NEED_FRAC 0.35 + ENEMY_SIDE 0.7) vs cpp20; queue 58; cambc 4.0.0, 70 maps, C++"
