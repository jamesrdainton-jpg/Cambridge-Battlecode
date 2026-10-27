#!/usr/bin/env bash
# Queue 40 (2026-10-27, cambc 4.0.0, 70 maps, C++): separate the meta item build (BUILD_30 6) from FIGHT2, and FIGHT2
# thresholds. All vs c29b (v14). b6 = v14 + BUILD_30 6; f2b = + FIGHT2 (seed 2); f2c = f2b with engage 1.0 / retreat
# 0.7; f2d = f2b with engage 1.3 / retreat 0.9; f2e = f2b with allies counted within 6.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py b6 --src cpp13 --set "params.h:BUILD_30 = 4=>BUILD_30 = 6"
$PY tools/gauntlet.py b6 --vs c29b --seeds 1,2 --no-econ --note "b6 (BUILD_30 6) vs c29b (v14); queue 40; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py f2b --vs c29b --seeds 2 --no-econ --note "f2b (FIGHT2 + BUILD_30 6) vs c29b (v14) seed 2; queue 40; cambc 4.0.0, 70 maps, C++"
B6F2=(--set "params.h:FIGHT2 = false=>FIGHT2 = true" --set "params.h:BUILD_30 = 4=>BUILD_30 = 6")
$PY tools/variant.py f2c --src cpp13 "${B6F2[@]}" --set "params.h:FIGHT2_ENGAGE = 1.1=>FIGHT2_ENGAGE = 1.0" --set "params.h:FIGHT2_RETREAT = 0.8=>FIGHT2_RETREAT = 0.7"
$PY tools/gauntlet.py f2c --vs c29b --seeds 1,2 --no-econ --note "f2c (f2b, engage 1.0 retreat 0.7) vs c29b (v14); queue 40; cambc 4.0.0, 70 maps, C++"
$PY tools/variant.py f2d --src cpp13 "${B6F2[@]}" --set "params.h:FIGHT2_ENGAGE = 1.1=>FIGHT2_ENGAGE = 1.3" --set "params.h:FIGHT2_RETREAT = 0.8=>FIGHT2_RETREAT = 0.9"
$PY tools/gauntlet.py f2d --vs c29b --seeds 1,2 --no-econ --note "f2d (f2b, engage 1.3 retreat 0.9) vs c29b (v14); queue 40; cambc 4.0.0, 70 maps, C++"
$PY tools/variant.py f2e --src cpp13 "${B6F2[@]}" --set "params.h:FIGHT2_ALLY = 4=>FIGHT2_ALLY = 6"
$PY tools/gauntlet.py f2e --vs c29b --seeds 1,2 --no-econ --note "f2e (f2b, allies within 6) vs c29b (v14); queue 40; cambc 4.0.0, 70 maps, C++"
