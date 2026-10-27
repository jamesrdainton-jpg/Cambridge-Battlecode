#!/usr/bin/env bash
# Queue 55 (2026-10-27, cambc 4.0.0, 70 maps, C++): economy settings tuned on engine 2.x, re-tested on top of cpp20
# (live v19). es10 = cpp20 with ENEMY_SIDE 1.0 (was 0.85: opponents put 20% of their camp hits on our side, we 10%);
# nf70 = cpp20 with NEED_FRAC 0.7 (smaller squads; Jungle's -30% camp damage came after the 0.55 tuning). Vs cpp20, seeds 1,2.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py es10 --src cpp20 --set "params.h:ENEMY_SIDE = 0.85=>ENEMY_SIDE = 1.0"
$PY tools/variant.py nf70 --src cpp20 --set "params.h:NEED_FRAC = 0.55=>NEED_FRAC = 0.7"
$PY tools/gauntlet.py es10 --vs cpp20 --seeds 1,2 --note "es10 (cpp20 + ENEMY_SIDE 1.0) vs cpp20; queue 55; cambc 4.0.0, 70 maps, C++"
$PY tools/gauntlet.py nf70 --vs cpp20 --seeds 1,2 --note "nf70 (cpp20 + NEED_FRAC 0.7) vs cpp20; queue 55; cambc 4.0.0, 70 maps, C++"
