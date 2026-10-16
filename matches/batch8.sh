#!/usr/bin/env bash
# Batch 8: 5th pick (5-pick maps) and 4th pick (4-pick maps) alternatives vs base8, 4 seeds.
cd "C:/Users/james/GitHub/Cambridge-Battlecode"
until grep -q "BATCH7 DONE" "C:/Users/james/AppData/Local/Temp/claude/c--Users-james-OneDrive-Documents-GitHub-Cambridge-Battlecode/432acbfa-12d4-4cf8-87f7-31f8a605609a/tasks/bh1vi2p31.output" 2>/dev/null; do sleep 15; done
for n in p5S p5V p5C p5W; do
  .venv/Scripts/python.exe tools/gauntlet.py $n --vs base8 --seeds 1,2,3,4 --maps corners,elkring,lanes,monolith --no-econ --note "batch8 $n" 2>&1 | grep -v "^created"
done
for n in p4T p4S p4C; do
  .venv/Scripts/python.exe tools/gauntlet.py $n --vs base8 --seeds 1,2,3,4,5,6 --maps interlock,rows --no-econ --note "batch8 $n" 2>&1 | grep -v "^created"
done
echo BATCH8 DONE
