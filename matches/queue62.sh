#!/usr/bin/env bash
# Queue 62 (2026-10-27, cambc 4.0.0, 70 maps, C++): economy settings not re-tested on engine 4.0, on cpp21 (champions now
# carry more gold). tb20 = TRIBUTE_BIG/MID 20/10 (bank sooner; was 30/15); tb45 = 45/20 (fewer altar trips);
# gw3 = GOLD_WEIGHT 0.3 (was 0.4); sg300 = SHOP_GOLD 300 (fewer shopping trips; was 150). Vs cpp21 (live v20), seeds 1,2.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe; [ -x "$PY" ] || PY=.venv/bin/python
$PY tools/variant.py tb20 --src cpp21 --set "params.h:TRIBUTE_BIG = 30=>TRIBUTE_BIG = 20" --set "params.h:TRIBUTE_MID = 15=>TRIBUTE_MID = 10"
$PY tools/variant.py tb45 --src cpp21 --set "params.h:TRIBUTE_BIG = 30=>TRIBUTE_BIG = 45" --set "params.h:TRIBUTE_MID = 15=>TRIBUTE_MID = 20"
$PY tools/variant.py gw3 --src cpp21 --set "params.h:GOLD_WEIGHT = 0.4=>GOLD_WEIGHT = 0.3"
$PY tools/variant.py sg300 --src cpp21 --set "params.h:SHOP_GOLD = 150=>SHOP_GOLD = 300"
for v in tb20 tb45 gw3 sg300; do
  $PY tools/gauntlet.py $v --vs cpp21 --seeds 1,2 --note "$v vs cpp21; queue 62; cambc 4.0.0, 70 maps, C++"
done
