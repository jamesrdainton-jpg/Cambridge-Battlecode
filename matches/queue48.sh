#!/usr/bin/env bash
# Queue 48 (2026-10-27, cambc 4.0.0, 70 maps, C++): UNSTICK on top of CAMP_AWAKE + TARGET_STATE (the go() bounce at the
# edge of avoid zones also parks champions on a dead group's spawn tiles, which blocks its respawn: 01yellow-brick-road
# stalled at 339 gems without it, 978 by r888 with it). tsu = BUILD_30 6 + CAMP_AWAKE + TARGET_STATE + UNSTICK vs ts6
# and vs c29b (v14), seeds 1,2; economy vs idle.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py tsu --src cpp13 --set "params.h:BUILD_30 = 4=>BUILD_30 = 6" --set "params.h:CAMP_AWAKE = false=>CAMP_AWAKE = true" --set "params.h:TARGET_STATE = false=>TARGET_STATE = true" --set "params.h:UNSTICK = false=>UNSTICK = true"
$PY tools/gauntlet.py tsu --vs ts6 --seeds 1,2 --no-econ --note "tsu (ts6 + UNSTICK) vs ts6 (BUILD_30 6 + CAMP_AWAKE + TARGET_STATE); queue 48; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py tsu --vs c29b --seeds 1,2 --note "tsu (BUILD_30 6 + CAMP_AWAKE + TARGET_STATE + UNSTICK) vs c29b (v14) + economy; queue 48; cambc 4.0.0, 70 maps, C++"
