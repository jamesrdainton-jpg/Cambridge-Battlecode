#!/usr/bin/env bash
# Queue 52 (2026-10-27, cambc 4.0.0, 70 maps, C++): Strength item builds (DEVLOG 187: the teams that beat v18 own ~2.7x our
# Strength at r800 and the same Health). s10 = cpp19 with BUILD_30 10 (Strength tail: Bruiser and Power of the main stat,
# no Bruiser H); s11 = cpp19 with BUILD_30 11 (10 with Treasure first). Both vs cpp19 (live v18), seeds 1,2, + economy.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
FIX=(--set "params.h:CAMP_AWAKE = false=>CAMP_AWAKE = true" --set "params.h:TARGET_STATE = false=>TARGET_STATE = true" --set "params.h:SEEK_HIDDEN = false=>SEEK_HIDDEN = true" --set "params.h:LOCKED_OPEN = false=>LOCKED_OPEN = true")
$PY tools/variant.py s10 --src cpp13 "${FIX[@]}" --set "params.h:BUILD_30 = 4=>BUILD_30 = 10"
$PY tools/variant.py s11 --src cpp13 "${FIX[@]}" --set "params.h:BUILD_30 = 4=>BUILD_30 = 11"
$PY tools/gauntlet.py s10 --vs cpp19 --seeds 1,2 --note "s10 (cpp19 + BUILD_30 10, Strength tail) vs cpp19; queue 52; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py s11 --vs cpp19 --seeds 1,2 --note "s11 (cpp19 + BUILD_30 11, Treasure + Strength tail) vs cpp19; queue 52; cambc 4.0.0, 70 maps, C++"
