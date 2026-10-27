#!/usr/bin/env bash
# Queue 60 (2026-10-27, cambc 4.0.0, 70 maps, C++): settings that may interact with cpp21's bigger squads (NEED_FRAC 0.25;
# panel 19/30). wl10 = cpp21 with WAIT_LIMIT 10 (wait outside reach for the squad before waking a camp; 0 since engine
# 3.0); es10b = cpp21 with ENEMY_SIDE 1.0 (lost on cpp20's small squads, queue 55). Vs cpp21 (live v20), seeds 1,2.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py wl10 --src cpp21 --set "params.h:WAIT_LIMIT = 0=>WAIT_LIMIT = 10"
$PY tools/variant.py es10b --src cpp21 --set "params.h:ENEMY_SIDE = 0.85=>ENEMY_SIDE = 1.0"
$PY tools/gauntlet.py wl10 --vs cpp21 --seeds 1,2 --note "wl10 (cpp21 + WAIT_LIMIT 10) vs cpp21; queue 60; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py es10b --vs cpp21 --seeds 1,2 --note "es10b (cpp21 + ENEMY_SIDE 1.0) vs cpp21; queue 60; cambc 4.0.0, 70 maps, C++"
