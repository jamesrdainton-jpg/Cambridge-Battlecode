#!/usr/bin/env bash
# Queue 49 (2026-10-27, cambc 4.0.0, 70 maps, C++): SEEK_HIDDEN (a living target group with no camp in view: go to the
# tiles beside its unseen cells; on 02gift-wrapping the survivors of a ring sat behind its wall core while our champions
# waited beside the dead side). Without UNSTICK (queue 48: tsu 135/280 vs ts6). tsk = BUILD_30 6 + CAMP_AWAKE +
# TARGET_STATE + SEEK_HIDDEN vs ts6 and vs c29b (v14), seeds 1,2; economy vs idle.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py tsk --src cpp13 --set "params.h:BUILD_30 = 4=>BUILD_30 = 6" --set "params.h:CAMP_AWAKE = false=>CAMP_AWAKE = true" --set "params.h:TARGET_STATE = false=>TARGET_STATE = true" --set "params.h:SEEK_HIDDEN = false=>SEEK_HIDDEN = true"
$PY tools/gauntlet.py tsk --vs ts6 --seeds 1,2 --no-econ --note "tsk (ts6 + SEEK_HIDDEN) vs ts6; queue 49; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py tsk --vs c29b --seeds 1,2 --note "tsk (BUILD_30 6 + CAMP_AWAKE + TARGET_STATE + SEEK_HIDDEN) vs c29b (v14) + economy; queue 49; cambc 4.0.0, 70 maps, C++"
