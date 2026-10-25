#!/usr/bin/env bash
# Queue 23 (2026-10-25, cambc 3.0.5, 40 maps): the v14 candidate in both languages.
#   cpp14 = bots/cpp13 + BUILD_30 1 + FIGHT_PRIO (C++)      py14 = bots/mybot + BUILD_30 1 + FIGHT_PRIO (Python)
# vs v13 (seeds 1,2, economy), and head to head (seeds 1,2).
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
$PY $V cpp14 --src cpp13 --set "params.h:BUILD_30 = 0=>BUILD_30 = 1" --set "params.h:FIGHT_PRIO = false=>FIGHT_PRIO = true"
$PY $V py14 --set "bot.py:BUILD_30 = 0=>BUILD_30 = 1" --set "bot.py:FIGHT_PRIO = False=>FIGHT_PRIO = True"
$PY tools/gauntlet.py cpp14 --vs v13 --seeds 1,2 --note "cpp14 = C++ port + BUILD_30 1 + FIGHT_PRIO vs v13; cambc 3.0.5, 40 maps"
$PY tools/gauntlet.py cpp14 --vs py14 --seeds 1,2 --no-econ --note "cpp14 vs py14 (same flags, C++ vs Python); cambc 3.0.5, 40 maps"
