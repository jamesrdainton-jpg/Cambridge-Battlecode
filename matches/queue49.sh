#!/usr/bin/env bash
# Queue 49 (2026-10-27, cambc 4.0.0, 70 maps, C++): SEEK_HIDDEN (a living target group with no camp in view: go to the
# tiles beside its unseen cells; on 02gift-wrapping the survivors of a ring sat behind its wall core while our champions
# waited beside the dead side). tsh = BUILD_30 6 + CAMP_AWAKE + TARGET_STATE + UNSTICK + SEEK_HIDDEN vs ts6 and vs c29b
# (v14), seeds 1,2; economy vs idle.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py tsh --src cpp13 --set "params.h:BUILD_30 = 4=>BUILD_30 = 6" --set "params.h:CAMP_AWAKE = false=>CAMP_AWAKE = true" --set "params.h:TARGET_STATE = false=>TARGET_STATE = true" --set "params.h:UNSTICK = false=>UNSTICK = true" --set "params.h:SEEK_HIDDEN = false=>SEEK_HIDDEN = true"
$PY tools/gauntlet.py tsh --vs ts6 --seeds 1,2 --no-econ --note "tsh (ts6 + UNSTICK + SEEK_HIDDEN) vs ts6; queue 49; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py tsh --vs c29b --seeds 1,2 --note "tsh (BUILD_30 6 + CAMP_AWAKE + TARGET_STATE + UNSTICK + SEEK_HIDDEN) vs c29b (v14) + economy; queue 49; cambc 4.0.0, 70 maps, C++"
