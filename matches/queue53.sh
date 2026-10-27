#!/usr/bin/env bash
# Queue 53 (2026-10-27, cambc 4.0.0, 70 maps, C++): gold for longer. The teams that beat v18 spend 2.2x our gold over a
# game; we value gold at 0.4 fading to 0.06 by round 425 (GOLD_TAPER 500, adopted on engine 2.2 for v7). gt10 / gt20 =
# cpp19 with GOLD_TAPER 1000 / 2000. Both vs cpp19 (live v18), seeds 1,2, + economy.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
FIX=(--set "params.h:CAMP_AWAKE = false=>CAMP_AWAKE = true" --set "params.h:TARGET_STATE = false=>TARGET_STATE = true" --set "params.h:SEEK_HIDDEN = false=>SEEK_HIDDEN = true" --set "params.h:LOCKED_OPEN = false=>LOCKED_OPEN = true" --set "params.h:BUILD_30 = 4=>BUILD_30 = 6")
$PY tools/variant.py gt10 --src cpp13 "${FIX[@]}" --set "params.h:GOLD_TAPER = 500=>GOLD_TAPER = 1000"
$PY tools/variant.py gt20 --src cpp13 "${FIX[@]}" --set "params.h:GOLD_TAPER = 500=>GOLD_TAPER = 2000"
$PY tools/gauntlet.py gt10 --vs cpp19 --seeds 1,2 --note "gt10 (cpp19 + GOLD_TAPER 1000) vs cpp19; queue 53; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py gt20 --vs cpp19 --seeds 1,2 --note "gt20 (cpp19 + GOLD_TAPER 2000) vs cpp19; queue 53; cambc 4.0.0, 70 maps, C++"
