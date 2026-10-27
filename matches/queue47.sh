#!/usr/bin/env bash
# Queue 47 (2026-10-27, cambc 4.0.0, 70 maps, C++): TARGET_STATE (refresh the target group's state whenever a tile of it
# is in view; a stale "reward" on the far end of 00the-line's 23-camp group blocked its respawn for 1,700 rounds) with
# CAMP_AWAKE, on BUILD_30 6. ts6 vs b6 and vs c29b (v14), seeds 1,2; economy vs idle on all maps.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py ts6 --src cpp13 --set "params.h:BUILD_30 = 4=>BUILD_30 = 6" --set "params.h:CAMP_AWAKE = false=>CAMP_AWAKE = true" --set "params.h:TARGET_STATE = false=>TARGET_STATE = true"
$PY tools/gauntlet.py ts6 --vs b6 --seeds 1,2 --no-econ --note "ts6 (BUILD_30 6 + CAMP_AWAKE + TARGET_STATE) vs b6 (BUILD_30 6); queue 47; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py ts6 --vs c29b --seeds 1,2 --note "ts6 (BUILD_30 6 + CAMP_AWAKE + TARGET_STATE) vs c29b (v14) + economy; queue 47; cambc 4.0.0, 70 maps, C++"
