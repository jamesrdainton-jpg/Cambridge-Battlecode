#!/usr/bin/env bash
# Queue 50 (2026-10-27, cambc 4.0.0, 70 maps, C++): TILE_PASS (standing on a camp spawn tile, take the direct path; the
# narrow part of UNSTICK, which lost head to head) on top of tsk (= cpp19 without LOCKED_OPEN). tkp vs tsk and vs c29b
# (v14), seeds 1,2; economy vs idle.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py tkp --src cpp13 --set "params.h:BUILD_30 = 4=>BUILD_30 = 6" --set "params.h:CAMP_AWAKE = false=>CAMP_AWAKE = true" --set "params.h:TARGET_STATE = false=>TARGET_STATE = true" --set "params.h:SEEK_HIDDEN = false=>SEEK_HIDDEN = true" --set "params.h:TILE_PASS = false=>TILE_PASS = true"
$PY tools/gauntlet.py tkp --vs tsk --seeds 1,2 --no-econ --note "tkp (tsk + TILE_PASS) vs tsk; queue 50; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py tkp --vs c29b --seeds 1,2 --note "tkp (BUILD_30 6 + CAMP_AWAKE + TARGET_STATE + SEEK_HIDDEN + TILE_PASS) vs c29b (v14) + economy; queue 50; cambc 4.0.0, 70 maps, C++"
