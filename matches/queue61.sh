#!/usr/bin/env bash
# Queue 61 (2026-10-27, cambc 4.0.0, 70 maps, C++): fight thresholds and retargeting, last tuned on engine 2.x, re-tested
# on cpp21 (bigger squads changed the fights). fe11 / fe15 = cpp21 with FIGHT_ENGAGE 1.1 / 1.5 (was 1.3); fr11 = cpp21
# with FIGHT_RETREAT 1.1 (was 0.9); rt4 = cpp21 with RETARGET_EVERY 4 (was 8). Vs cpp21 (live v20), seeds 1,2.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py fe11 --src cpp21 --set "params.h:FIGHT_ENGAGE = 1.3=>FIGHT_ENGAGE = 1.1"
$PY tools/variant.py fe15 --src cpp21 --set "params.h:FIGHT_ENGAGE = 1.3=>FIGHT_ENGAGE = 1.5"
$PY tools/variant.py fr11 --src cpp21 --set "params.h:FIGHT_RETREAT = 0.9=>FIGHT_RETREAT = 1.1"
$PY tools/variant.py rt4 --src cpp21 --set "params.h:RETARGET_EVERY = 8=>RETARGET_EVERY = 4"
for v in fe11 fe15 fr11 rt4; do
  $PY tools/gauntlet.py $v --vs cpp21 --seeds 1,2 --note "$v vs cpp21; queue 61; cambc 4.0.0, 70 maps, C++"
done
