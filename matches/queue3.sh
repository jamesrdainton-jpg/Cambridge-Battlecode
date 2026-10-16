#!/usr/bin/env bash
# Queue 3 (2026-10-16): the stand-off breaker (so1 = mybot with STANDOFF_TURNS 12) vs v5 and v4, then the
# squad-wait follow-up (WAIT_LIMIT 40 with fresh seeds 5-8, and 60) and two settings never tested head-to-head
# on current code (CAUTION_WINDOW 40, SHOP_GOLD 200). Those variants switch the stand-off breaker off, so each
# is v5 plus one change (STANDOFF_TURNS 0 reproduces v5's games exactly).
# Reproduce: check out bots/mybot and bots/v5 as at the commit in each gauntlet.csv line, then run this.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || PY=.venv/bin/python
V="$PY tools/variant.py"
G="$PY tools/gauntlet.py"
OFF="bot.py:STANDOFF_TURNS = 12=>STANDOFF_TURNS = 0"
$V so1 || exit 1
$V wl40 --set "$OFF" --set "bot.py:WAIT_LIMIT = 25=>WAIT_LIMIT = 40" || exit 1
$V wl60 --set "$OFF" --set "bot.py:WAIT_LIMIT = 25=>WAIT_LIMIT = 60" || exit 1
$V cw40 --set "$OFF" --set "bot.py:CAUTION_WINDOW = 0=>CAUTION_WINDOW = 40" || exit 1
$V sg200 --set "$OFF" --set "bot.py:SHOP_GOLD = 300=>SHOP_GOLD = 200" || exit 1
$G so1 --vs v5,v4 --seeds 1,2,3,4 --note "queue3 so1 stand-off breaker vs v5 and v4" 2>&1 | grep -v "^created"
$G wl40 --vs v5 --seeds 5,6,7,8 --note "queue3 wl40 confirm (seeds 5-8)" 2>&1 | grep -v "^created"
for n in wl60 cw40 sg200; do
  $G $n --vs v5 --seeds 1,2,3,4 --note "queue3 $n vs v5" 2>&1 | grep -v "^created"
done
echo QUEUE3 DONE
