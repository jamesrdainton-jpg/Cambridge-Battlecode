#!/usr/bin/env bash
# Batch 5: tribute thresholds on the current bot vs base5 (60/30), 4 seeds both sides.
cd "C:/Users/james/GitHub/Cambridge-Battlecode"
until grep -q "batch4 es1" matches/gauntlet.csv 2>/dev/null; do sleep 15; done
for n in t45 t30; do
  .venv/Scripts/python.exe tools/gauntlet.py $n --vs base5 --seeds 1,2,3,4 --note "batch5 $n" 2>&1 | grep -v "^created"
done
echo BATCH5 DONE
