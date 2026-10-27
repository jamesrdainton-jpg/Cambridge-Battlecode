#!/usr/bin/env bash
# Queue 51 (2026-10-27, cambc 4.0.0, 70 maps, C++): FIGHT2 (allies within 6; cut our platform deaths by 27%) on top of
# the fixed economy, and the exact platform candidate cpp19 (= tsk + LOCKED_OPEN) as a sanity check. Seeds 1,2.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py tkf --src cpp13 --set "params.h:BUILD_30 = 4=>BUILD_30 = 6" --set "params.h:CAMP_AWAKE = false=>CAMP_AWAKE = true" --set "params.h:TARGET_STATE = false=>TARGET_STATE = true" --set "params.h:SEEK_HIDDEN = false=>SEEK_HIDDEN = true" --set "params.h:FIGHT2 = false=>FIGHT2 = true" --set "params.h:FIGHT2_ALLY = 4=>FIGHT2_ALLY = 6"
$PY tools/gauntlet.py tkf --vs tsk --seeds 1,2 --no-econ --note "tkf (tsk + FIGHT2 allies 6) vs tsk; queue 51; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py cpp19 --vs tsk --seeds 1,2 --no-econ --note "cpp19 (tsk + LOCKED_OPEN) vs tsk; queue 51; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py tkf --vs c29b --seeds 1,2 --no-econ --note "tkf (tsk + FIGHT2 allies 6) vs c29b (v14); queue 51; cambc 4.0.0, 70 maps, C++"
