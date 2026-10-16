#!/usr/bin/env bash
# Resume queue (2026-10-16): unfinished batch 8 picks, batch 9 dE re-test, batch 10 gold weights.
cd "C:/Users/james/GitHub/Cambridge-Battlecode"
G=".venv/Scripts/python.exe tools/gauntlet.py"
for n in p5V p5C p5W; do
  $G $n --vs base8 --seeds 1,2,3,4 --maps corners,elkring,lanes,monolith --no-econ --note "batch8 $n" 2>&1 | grep -v "^created"
done
for n in p4T p4S p4C; do
  $G $n --vs base8 --seeds 1,2,3,4,5,6 --maps interlock,rows --no-econ --note "batch8 $n" 2>&1 | grep -v "^created"
done
$G dE --vs lk1 --seeds 9,10,11,12,13,14,15,16 --maps packs,collision,expanse --no-econ --note "batch9 dE retest" 2>&1 | grep -v "^created"
for n in gw0 gw075; do
  $G $n --vs gw1 --seeds 1,2,3,4 --note "batch10 $n vs gw1" 2>&1 | grep -v "^created"
done
echo QUEUE1 DONE
