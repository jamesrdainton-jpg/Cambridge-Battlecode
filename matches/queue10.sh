#!/usr/bin/env bash
# Queue 10 (2026-10-18, cambc 2.2.5, 17 maps), each one change of mybot vs v7, seeds 1,2 + economy:
#   cf1  CAST_FIRST: ranged champions cast walking-exclusive abilities before their basic attack (our Tavi cast at
#        camps 0.11 times per basic attack, pros' ranged champions 0.18-0.25; cf1's Tavi 0.20 in a smoke test)
#   fix1 IGNORE_SPAWN_CAMPERS + CAMP_TILE_FIX together (map-specific bug fixes on rushbait-v2 and contest)
# Reproduce: check out the commit in each gauntlet.csv line, then run this.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || PY=.venv/bin/python
V="$PY tools/variant.py"
G="$PY tools/gauntlet.py"
$V cf1 --set "bot.py:CAST_FIRST = False=>CAST_FIRST = True" || exit 1
$V fix1 --set "bot.py:IGNORE_SPAWN_CAMPERS = False=>IGNORE_SPAWN_CAMPERS = True" --set "bot.py:CAMP_TILE_FIX = False=>CAMP_TILE_FIX = True" || exit 1
for n in cf1 fix1; do
  $G $n --vs v7 --seeds 1,2 --note "queue10 $n vs v7" 2>&1 | grep -v "^created"
done
echo QUEUE10 DONE
