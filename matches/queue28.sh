#!/usr/bin/env bash
# Queue 28 (2026-10-26, cambc 4.0.0, 70 maps, 4-core Linux cloud machine): C++ only from now on. Each change from
# VS-TOP5-v14.md alone on cpp13 (= cpp14 = v14 in C++ with the new flags off), vs the frozen cpp14, seed 1, 140 games.
#   zh1 = HOR_DASH + DRAFT_SET 1 (top-5 consensus draft: Vendetta, Heart of Ruin, Vesper, + Marcella, + Ryth)
#   zd1 = DRAFT_SET 1 alone (the same draft with the dash used only for walking: how much the code matters)
#   zh2 = HOR_DASH + DRAFT_SET 2 (Marcella core)
#   zg  = EARLY_GOLD 1.5 until round 150
#   zr  = FIGHT_RESPECT 1.5 (expected to lose locally: our own bot over-rates itself the same way; for the platform)
# Local results only screen for regressions: the verdict is a scrimmage against the top 5 (VS-TOP5-v14.md 4).
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
V=tools/variant.py
H="params.h:HOR_DASH = false=>HOR_DASH = true"
$PY $V zh1 --src cpp13 --set "$H" --set "params.h:DRAFT_SET = 0=>DRAFT_SET = 1" >/dev/null
$PY $V zd1 --src cpp13 --set "params.h:DRAFT_SET = 0=>DRAFT_SET = 1" >/dev/null
$PY $V zh2 --src cpp13 --set "$H" --set "params.h:DRAFT_SET = 0=>DRAFT_SET = 2" >/dev/null
$PY $V zg --src cpp13 --set "params.h:EARLY_GOLD = 0.0=>EARLY_GOLD = 1.5" >/dev/null
$PY $V zr --src cpp13 --set "params.h:FIGHT_RESPECT = 1.0=>FIGHT_RESPECT = 1.5" >/dev/null
N="queue 28; cambc 4.0.0, 70 maps"
J="--jobs ${JOBS:-6}"
$PY tools/gauntlet.py zh1 --vs cpp14 --seeds 1 --no-econ $J --note "zh1 = HOR_DASH + DRAFT_SET 1 vs cpp14; $N"
$PY tools/gauntlet.py zd1 --vs cpp14 --seeds 1 --no-econ $J --note "zd1 = DRAFT_SET 1 vs cpp14; $N"
$PY tools/gauntlet.py zh2 --vs cpp14 --seeds 1 --no-econ $J --note "zh2 = HOR_DASH + DRAFT_SET 2 vs cpp14; $N"
$PY tools/gauntlet.py zg --vs cpp14 --seeds 1 --no-econ $J --note "zg = EARLY_GOLD 1.5 to r150 vs cpp14; $N"
$PY tools/gauntlet.py zr --vs cpp14 --seeds 1 --no-econ $J --note "zr = FIGHT_RESPECT 1.5 vs cpp14; $N"
echo QUEUE28 DONE
