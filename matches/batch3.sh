#!/usr/bin/env bash
# Batch 3: draft for 3-pick maps. Each variant vs lk1 (default draft), 8 seeds, 3-pick maps only.
cd "C:/Users/james/GitHub/Cambridge-Battlecode"
until grep -q "batch2 lk1" matches/gauntlet.csv 2>/dev/null; do sleep 15; done
for n in dA dB dC dD dE; do
  .venv/Scripts/python.exe tools/gauntlet.py $n --vs lk1 --seeds 1,2,3,4,5,6,7,8 --maps packs,collision,expanse --no-econ --note "batch3 draft $n" 2>&1 | grep -v "^created"
done
echo BATCH3 DONE
