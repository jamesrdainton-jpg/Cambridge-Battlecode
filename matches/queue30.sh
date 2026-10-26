#!/usr/bin/env bash
# Queue 30 (2026-10-26, cambc 4.0.0, 70 maps, 4-core Linux cloud machine): the exact release candidate before freezing.
# Queue 29: zm4 (HOR_DASH + DRAFT_SET 4) 149/280 +9,309; zg (EARLY_GOLD 1.5) seeds 1+2 148/280 +6,696; zho (HOLD_FIX)
# 137/280 -1,835; zc (all four + TELEMETRY) 144/280 +7,262.
#   z15 = HOR_DASH + DRAFT_SET 4 + EARLY_GOLD 1.5 + TELEMETRY (HOLD_FIX off), seeds 1,2 vs cpp14
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py z15 --src cpp13 --set "params.h:HOR_DASH = false=>HOR_DASH = true" --set "params.h:DRAFT_SET = 0=>DRAFT_SET = 4" \
  --set "params.h:EARLY_GOLD = 0.0=>EARLY_GOLD = 1.5" --set "params.h:TELEMETRY = false=>TELEMETRY = true" >/dev/null
$PY tools/gauntlet.py z15 --vs cpp14 --seeds 1,2 --no-econ --jobs ${JOBS:-6} --note "z15 = HOR_DASH + DRAFT_SET 4 + EARLY_GOLD 1.5 + TELEMETRY vs cpp14 (release candidate); queue 30; cambc 4.0.0, 70 maps"
echo QUEUE30 DONE
