#!/usr/bin/env bash
# Queue 59 (2026-10-27, cambc 4.0.0, 70 maps, C++): where does the NEED_FRAC trend stop? (0.55 / 0.45 / 0.35 / 0.25 =
# 140 / 161 / 164 / 173 vs cpp20; cpp21 = 0.25 submitted as platform v20). nf20 / nf15 = cpp20 with NEED_FRAC 0.20 / 0.15.
# Vs cpp20, seeds 1,2.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py nf20 --src cpp20 --set "params.h:NEED_FRAC = 0.55=>NEED_FRAC = 0.2"
$PY tools/variant.py nf15 --src cpp20 --set "params.h:NEED_FRAC = 0.55=>NEED_FRAC = 0.15"
$PY tools/gauntlet.py nf20 --vs cpp20 --seeds 1,2 --note "nf20 (cpp20 + NEED_FRAC 0.2) vs cpp20; queue 59; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py nf15 --vs cpp20 --seeds 1,2 --note "nf15 (cpp20 + NEED_FRAC 0.15) vs cpp20; queue 59; cambc 4.0.0, 70 maps, C++"
