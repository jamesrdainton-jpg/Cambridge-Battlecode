#!/usr/bin/env bash
# Batch 10: gold weight 0 and 0.075 vs gw1 (0.15), 4 seeds both sides + economy.
cd "C:/Users/james/GitHub/Cambridge-Battlecode"
until grep -q "BATCH9 DONE" "C:/Users/james/AppData/Local/Temp/claude/c--Users-james-OneDrive-Documents-GitHub-Cambridge-Battlecode/432acbfa-12d4-4cf8-87f7-31f8a605609a/tasks/bttixt3bv.output" 2>/dev/null; do sleep 15; done
for n in gw0 gw075; do
  .venv/Scripts/python.exe tools/gauntlet.py $n --vs gw1 --seeds 1,2,3,4 --note "batch10 $n vs gw1" 2>&1 | grep -v "^created"
done
echo BATCH10 DONE
