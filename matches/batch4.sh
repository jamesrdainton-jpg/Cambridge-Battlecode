#!/usr/bin/env bash
# Batch 4: one-constant sweeps vs base5 (= mybot after the constants refactor), 4 seeds both sides.
cd "C:/Users/james/GitHub/Cambridge-Battlecode"
until grep -q "batch3 draft dE" matches/gauntlet.csv 2>/dev/null; do sleep 15; done
for n in fA fB gw1 gw2 es1; do
  .venv/Scripts/python.exe tools/gauntlet.py $n --vs base5 --seeds 1,2,3,4 --note "batch4 $n" 2>&1 | grep -v "^created"
done
echo BATCH4 DONE
