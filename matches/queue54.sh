#!/usr/bin/env bash
# Queue 54 (2026-10-27, cambc 4.0.0, 70 maps, C++): more gold after queue 53 (GOLD_TAPER 2000: 157/280 vs cpp19).
# gtc = cpp19 with no fade (GOLD_TAPER 100000: 0.4 all game); gw6 = cpp19 with GOLD_TAPER 2000 and GOLD_WEIGHT 0.6.
# Both vs cpp19 (live v18), seeds 1,2, + economy.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
FIX=(--set "params.h:CAMP_AWAKE = false=>CAMP_AWAKE = true" --set "params.h:TARGET_STATE = false=>TARGET_STATE = true" --set "params.h:SEEK_HIDDEN = false=>SEEK_HIDDEN = true" --set "params.h:LOCKED_OPEN = false=>LOCKED_OPEN = true" --set "params.h:BUILD_30 = 4=>BUILD_30 = 6")
$PY tools/variant.py gtc --src cpp13 "${FIX[@]}" --set "params.h:GOLD_TAPER = 500=>GOLD_TAPER = 100000"
$PY tools/variant.py gw6 --src cpp13 "${FIX[@]}" --set "params.h:GOLD_TAPER = 500=>GOLD_TAPER = 2000" --set "params.h:GOLD_WEIGHT = 0.4=>GOLD_WEIGHT = 0.6"
$PY tools/gauntlet.py gtc --vs cpp19 --seeds 1,2 --note "gtc (cpp19 + GOLD_TAPER 100000, no fade) vs cpp19; queue 54; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py gw6 --vs cpp19 --seeds 1,2 --note "gw6 (cpp19 + GOLD_TAPER 2000 + GOLD_WEIGHT 0.6) vs cpp19; queue 54; cambc 4.0.0, 70 maps, C++"
