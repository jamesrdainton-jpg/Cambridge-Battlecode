#!/usr/bin/env bash
# Batch 1: cluster targeting, caution window, tribute thresholds (each vs v4, 4 seeds both sides).
cd "C:/Users/james/GitHub/Cambridge-Battlecode"
F="C:/Users/james/AppData/Local/Temp/claude/c--Users-james-OneDrive-Documents-GitHub-Cambridge-Battlecode/432acbfa-12d4-4cf8-87f7-31f8a605609a/tasks/bp4x7hagv.output"
until grep -q "squad variant sqall" "$F" 2>/dev/null; do sleep 5; done
for n in cl cw40 tbig tsmall; do
  .venv/Scripts/python.exe tools/gauntlet.py $n --vs v4 --seeds 1,2,3,4 --note "batch1 $n" 2>&1 | grep -v "^created"
done
echo BATCH1 DONE
