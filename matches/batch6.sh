#!/usr/bin/env bash
# Batch 6: locks without detours (lk2 = lk1 with LOCK_DETOUR 0) vs lk0 (no locks) and vs the starter.
cd "C:/Users/james/GitHub/Cambridge-Battlecode"
until grep -q "batch5 t30" matches/gauntlet.csv 2>/dev/null; do sleep 15; done
.venv/Scripts/python.exe tools/gauntlet.py lk2 --vs lk0,starter --seeds 1,2,3,4 --note "batch6 lk2 (locks, no detour)" 2>&1 | grep -v "^created"
echo BATCH6 DONE
