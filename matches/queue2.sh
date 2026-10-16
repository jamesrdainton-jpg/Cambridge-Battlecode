#!/usr/bin/env bash
# Queue 2 (2026-10-16): v5 vs v4 (cumulative), Jungle build flags, squad-size / wait / gem-hunt sweeps,
# 4th-pick Cassi & Issac re-test. Every variant is mybot with one change (DEBUG off), judged vs v5.
# Reproduce: bots/mybot and bots/v5 as at commit d3f40a6 (mybot unchanged since 85be59a), then run this.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || PY=.venv/bin/python
V="$PY tools/variant.py"
G="$PY tools/gauntlet.py"
$V tj1 --set "bot.py:TANK_JUNGLE_FIRST = False=>TANK_JUNGLE_FIRST = True" || exit 1
$V ja1 --set "bot.py:JUNGLE_AWARE = False=>JUNGLE_AWARE = True" || exit 1
$V nf45 --set "bot.py:NEED_FRAC = 0.55=>NEED_FRAC = 0.45" || exit 1
$V nf65 --set "bot.py:NEED_FRAC = 0.55=>NEED_FRAC = 0.65" || exit 1
$V wl15 --set "bot.py:WAIT_LIMIT = 25=>WAIT_LIMIT = 15" || exit 1
$V wl40 --set "bot.py:WAIT_LIMIT = 25=>WAIT_LIMIT = 40" || exit 1
$V gh2 --set "bot.py:GEM_HUNT = 0.0=>GEM_HUNT = 0.2" || exit 1
$V p4C2 --set "draft.py:BY_SIZE = {3: (CD.VENDETTA, CD.RYTH, CD.TAVI)}=>BY_SIZE = {3: (CD.VENDETTA, CD.RYTH, CD.TAVI), 4: (CD.VENDETTA, CD.VARG, CD.RYTH, CD.CASSI_AND_ISSAC)}" || exit 1
$G v5 --vs v4 --seeds 1,2,3,4 --note "queue2 v5 vs v4 (cumulative)" 2>&1 | grep -v "^created"
for n in tj1 ja1 nf45 nf65 wl15 wl40 gh2; do
  $G $n --vs v5 --seeds 1,2,3,4 --note "queue2 $n vs v5" 2>&1 | grep -v "^created"
done
$G p4C2 --vs v5 --seeds 7,8,9,10,11,12,13,14,15,16,17,18 --maps interlock,rows --no-econ --note "queue2 p4C2 4th-pick retest" 2>&1 | grep -v "^created"
echo QUEUE2 DONE
