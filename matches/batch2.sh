#!/usr/bin/env bash
# Batch 2: altar locks. lk0 = current bot without locks (but breaks enemy locks), lk1 = with locks.
cd "C:/Users/james/GitHub/Cambridge-Battlecode"
until grep -q "BATCH1 DONE" "C:/Users/james/AppData/Local/Temp/claude/c--Users-james-OneDrive-Documents-GitHub-Cambridge-Battlecode/432acbfa-12d4-4cf8-87f7-31f8a605609a/tasks/bl67i7z3l.output" 2>/dev/null; do sleep 10; done
.venv/Scripts/python.exe tools/gauntlet.py lk0 --vs v4 --seeds 1,2,3,4 --note "batch2 lk0 (no locks, in-range fixes)" 2>&1 | grep -v "^created"
.venv/Scripts/python.exe tools/gauntlet.py lk1 --vs lk0,v4 --seeds 1,2,3,4 --note "batch2 lk1 (altar locks)" 2>&1 | grep -v "^created"
echo BATCH2 DONE
