#!/usr/bin/env bash
# Queue 11 (2026-10-18, cambc 2.2.5, 17 maps), mybot (= v8 flags) variants vs v8, DEBUG off, seeds 1,2 + economy:
#   fs1  FIGHT_SHIELD: Varg casts its self-shield in fights (support() only ran while farming)
#   all1 FIGHT_SHIELD + WARDS + CAST_FIRST (each neutral-to-positive alone vs v6/v7)
# Reproduce: check out the commit in each gauntlet.csv line, then run this.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || PY=.venv/bin/python
V="$PY tools/variant.py"
G="$PY tools/gauntlet.py"
OFF="bot.py:DEBUG = True=>DEBUG = False"
$V fs1 --set "$OFF" --set "bot.py:FIGHT_SHIELD = False=>FIGHT_SHIELD = True" || exit 1
$V all1 --set "$OFF" --set "bot.py:FIGHT_SHIELD = False=>FIGHT_SHIELD = True" --set "bot.py:WARDS = False=>WARDS = True" \
  --set "bot.py:CAST_FIRST = False=>CAST_FIRST = True" || exit 1
for n in fs1 all1; do
  $G $n --vs v8 --seeds 1,2 --note "queue11 $n vs v8" 2>&1 | grep -v "^created"
done
echo QUEUE11 DONE
