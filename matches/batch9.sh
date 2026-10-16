#!/usr/bin/env bash
# Batch 9: re-test the dE draft (Vendetta, Ryth, Tavi on 3-pick maps) with fresh seeds 9-16.
cd "C:/Users/james/GitHub/Cambridge-Battlecode"
until grep -q "BATCH8 DONE" "C:/Users/james/AppData/Local/Temp/claude/c--Users-james-OneDrive-Documents-GitHub-Cambridge-Battlecode/432acbfa-12d4-4cf8-87f7-31f8a605609a/tasks/bxkvbvq79.output" 2>/dev/null; do sleep 15; done
.venv/Scripts/python.exe tools/gauntlet.py dE --vs lk1 --seeds 9,10,11,12,13,14,15,16 --maps packs,collision,expanse --no-econ --note "batch9 dE retest" 2>&1 | grep -v "^created"
echo BATCH9 DONE
