#!/usr/bin/env bash
# Queue 6 (2026-10-16, cambc 2.2.2, 17-map pool; 2 seeds = 68 games + economy): behaviours copied from strong
# platform teams (DEVLOG experiment 97), each as one change of mybot vs v6:
#   wd1 wards on bush tiles near our target   pw1 Power emblem first instead of Monster
#   gt1 more weight on gold early (0.4, fading by round 500)   sh1 recall to shop at 150 gold at any health
#   dc5 Cassi & Issac as the 5th pick on 5-pick maps (an extra champion; strong teams almost always take it)
# Reproduce: check out the commit in each gauntlet.csv line, then run this.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || PY=.venv/bin/python
V="$PY tools/variant.py"
G="$PY tools/gauntlet.py"
$V wd1 --set "bot.py:WARDS = False=>WARDS = True" || exit 1
$V pw1 --set "bot.py:POWER_FIRST = False=>POWER_FIRST = True" || exit 1
$V gt1 --set "bot.py:GOLD_WEIGHT = 0.15=>GOLD_WEIGHT = 0.4" --set "bot.py:GOLD_TAPER = 1200=>GOLD_TAPER = 500" || exit 1
$V sh1 --set "bot.py:SHOP_GOLD = 300=>SHOP_GOLD = 150" --set "bot.py:SHOP_HP = 0.75=>SHOP_HP = 1.01" || exit 1
$V dc5 --set "draft.py:BY_SIZE = {3: (CD.VENDETTA, CD.RYTH, CD.TAVI)}=>BY_SIZE = {3: (CD.VENDETTA, CD.RYTH, CD.TAVI), 5: (CD.VENDETTA, CD.VARG, CD.RYTH, CD.MARCELLA, CD.CASSI_AND_ISSAC)}" || exit 1
for n in wd1 pw1 gt1 sh1 dc5; do
  $G $n --vs v6 --seeds 1,2 --note "queue6 $n vs v6" 2>&1 | grep -v "^created"
done
echo QUEUE6 DONE
