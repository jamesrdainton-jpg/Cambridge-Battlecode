#!/usr/bin/env bash
# Batch 7: recall-as-travel. rt1 (on) vs rt0 (off), 4 seeds both sides, plus economy for both.
cd "C:/Users/james/GitHub/Cambridge-Battlecode"
until grep -q "batch6 lk2" matches/gauntlet.csv 2>/dev/null; do sleep 15; done
.venv/Scripts/python.exe tools/gauntlet.py rt1 --vs rt0 --seeds 1,2,3,4 --note "batch7 rt1 (recall travel) vs rt0" 2>&1 | grep -v "^created"
.venv/Scripts/python.exe tools/gauntlet.py rt0 --vs starter --seeds 1,2,3,4 --note "batch7 rt0 economy reference" 2>&1 | grep -v "^created"
echo BATCH7 DONE
