# Why we lose to the top teams (2026-10-25)

Written for the team. Companion to [REPORT.md](REPORT.md) (the engine 3.0 switch). Evidence: 25 games of v13 against
the ladder's top 5 — Intercontinental Fish (#1), Mite (#2), Claudus Maximus (#3), willow best girl (#4) and prism best
girl (#5), one 5-game group each, queued on 2026-10-25 — decoded turn by turn, plus local tests. Every number comes from
the tools in [tools/](tools/) (commands at the end).

## 1. Summary

- **v13 won 1 of 25.** Mean gems at round 200: 32 against 71; at round 500: 102 against 291.
- **The losing chain is a snowball that starts in the first 100 rounds:**
  1. The top teams buy items early and often (11.4 shopping visits a game by round 300; we make 5.1). Their first purchase
     is a **Treasure emblem** (+20% gold for that champion all game; +53% on Vesper), then **Bruiser** emblems, which give
     7 shards' worth of stats per 150 gold (Power gives 6).
  2. With items, they pick off our champions, who have none: **in 89% of our deaths the killer had spent more on items
     than our champion; in 81% at least twice as much. In the first 300 rounds our dying champion's median spending was 0
     gold, its killer's 210.** Only 8 of our 204 one-on-one deaths happened at roughly even items.
  3. Dead champions don't farm: in the first 300 rounds our champions are **dead 20% of the time (theirs 6%)** and hit
     camps on 14% of turns (theirs 24%). Each kill also hands them 100 gold and the gems we carry (5.0 kills a game by
     round 300 = 500 gold).
  4. So by round 300 they have spent **1,712 gold against our 563**, and by round 500 **3,765 against 927**. The next fight
     is even more lopsided: over the 25 games they won **218 engagements to our 23**, and we died **1.81 times per 100
     rounds against their 0.27**.
- **Fight micro is a symptom more than the cause.** 55% of our deaths are one-on-one, 68% happen with an ally within 3
  tiles, 38% of dying champions never hit back and 42% die walking away. But making champions stand and fight
  (`STAND_REACH`) loses badly locally (28/80), and help calls and commitment are neutral: when you're out-itemed 2:1,
  standing your ground just dies faster. The fix is to not be out-itemed.
- **They also order their turns.** All five call `set_priority` every round (three use negative priorities), choosing which
  of their champions acts first. We never did. Locally, priority-while-fighting is slightly positive (41/80, +3,414).
- **What we changed:** the top teams' build (`BUILD_30` 1: Treasure, Jungle, Bruiser, Durability, then Bruiser stacks)
  beats v13 **99/160, +21,031** and farms 4% faster. Results of the follow-ups are in section 4.

## 2. Evidence

### 2.1 Fights and deaths (25 games, 24,839 rounds)

| | Us | Top 5 |
|---|---|---|
| Deaths per team per 100 rounds (strict count) | **1.81** | **0.27** |
| Deaths in the first 300 rounds (all games) | 125 | 35 |
| Engagements started | 152 | 260 |
| Engagements won (fewer deaths) | **23** | **218** |
| Champions per engagement | 1.44 | 1.72 |

Who hits our dying champions: Heart of Ruin 148, Vesper 129, Marcella 97, Vendetta 95, Prism 46, Ryth 30, Tavi 27.

Our 368 deaths to champions: 55% to a single enemy champion; 68% with an ally within 3 tiles; 38% never hit back in their
last 6 rounds; 42% were moving away from the attacker; only 20% were farming when first hit; 78% happened in our half of
the map (they come to us).

Two typical deaths, traced turn by turn (monolith vs Claudus Maximus):
- **Round 70:** our Vendetta (stronger on paper than the enemy Tavi) lands one combo, then steps back and forth for three
  turns while Tavi stuns and shoots it from range 3, and dies.
- **Round 255:** our Vesper, alone, retreats in a straight line for 7 turns while Heart of Ruin hits it, shields and then
  dashes onto it (landing damage and a stun). Our nearest allies were 5–7 tiles away.

### 2.2 Items at the moment of death

| Killer's item spending vs our dying champion's | Deaths |
|---|---|
| Killer spent at least 2× as much | **299 (81%)** |
| 1.25–2× | 21 |
| About even (0.8–1.25×) | 18 |
| Our champion spent more | 30 |

First 300 rounds (105 deaths): median spending of our dying champion **0**, of the best-equipped killer **210**.

### 2.3 How the first 300 rounds are spent

| Share of champion-turns | Us | Top 5 |
|---|---|---|
| Dead | **20%** | 6% |
| Hitting camps | 14% | **24%** |
| Walking | 50% | 49% |
| Channels, captures, waiting | 12% | 12% |
| Hitting champions | 3% | 4% |
| Shopping visits per game | 5.1 | 11.4 |
| Gold spent by round 100 / 200 / 300 | 145 / 344 / 524 | 288 / 965 / 1,684 |
| Camp kinds hit | elks 52%, wolves 30% | wolves 48%, elks 36% |

### 2.4 Their builds (shards bought, all 25 games)

| Champion | Main items |
|---|---|
| Vesper (2,283) | Bruiser S 55%, Bruiser H 19%, Power S 8% |
| Marcella (1,609) | Bruiser S 56%, Bruiser H 15%, Bruiser F 12% |
| Heart of Ruin (1,341) | Bruiser F 46%, Bruiser H 29%, Jungle F 7% |
| Vendetta (1,184) | Bruiser S 49%, Bruiser H 26% |
| Prism (457) | Bruiser F 44%, Bruiser H 23% |

Typical order (Claudus Maximus's Vesper on monolith): Treasure S ×5 at round 32 → Jungle S ×5 (r104) → Monster S ×5 →
Durability H ×5 (r145) → Bruiser S ×10 (r173) → Bruiser H ×5 (r329). The #1 team, Intercontinental Fish, used Monster,
Jungle and Power instead in the game checked, so builds alone aren't the whole story.

### 2.5 Drafts

| Team | 5-pick | 3-pick |
|---|---|---|
| Intercontinental Fish | Vesper, Vendetta, Heart of Ruin, Varg, Cassi & Issac | Vesper, Heart of Ruin, Marcella |
| Mite | Vesper, Vendetta, Heart of Ruin, Tavi, Marcella | — |
| Claudus Maximus | Vesper, Heart of Ruin, Vendetta, Tavi/Ryth, Marcella | — |
| willow best girl | Prism, Vesper, Marcella, Willow, Heart of Ruin | Prism, Vesper, Heart of Ruin |
| prism best girl | Prism, Vesper, Marcella, Ryth, Heart of Ruin | — |

All five take Vesper and Heart of Ruin. v13 drafts Vendetta, Vesper, Tavi, Marcella, Ryth.

### 2.6 A tooling fix that matters for any replay analysis

All five teams call `set_priority` every round; the replay records it as `00 00 <i32>`. Within a team, higher priority acts
first from the next round, so a parser that assumes draft order assigns their turns to the wrong champions (7–9% of their
moves looked like teleports). Priorities are **signed** (three teams use negative values). `tools/replay30.py` orders
turns by signed priority; unexplained jumps fall to 0.14–0.36% (ours: 0.00%).

## 3. Local tests (cambc 3.0.5, all 40 maps, seeded, both sides)

| Change | Result | Verdict |
|---|---|---|
| `BUILD_30` 1: Treasure, Jungle H, Bruiser, Durability H, then Bruiser stacks | vs v13 **99/160, +21,031**; economy 48,839 (v13 50,783) | **Adopt** |
| `BUILD_30` 2: Treasure, then Bruiser only | vs v13 80/160, −3,287 | No |
| All fight changes together (stand 3, commit 3, help, priority) | smoke test vs v13 3/8; fragment 37–42 deaths vs 5–11 | No |
| `FIGHT_PRIO` (act first while fighting) | vs the build base 41/80, +3,414 | Neutral-positive; PRIO_SEED2 |
| `HELP_CALLS` (shared-memory call; allies within 8 come) | 38/80, −582 | Neutral |
| `STAND_REACH` 2 (fight back when an enemy is within 2) | **28/80, −16,125** | No |
| `FIGHT_COMMIT` 3 | 38/80, +440 | Neutral |
| ECONOMY_ROWS | | |

Caveat: local opponents are our own bots. A change that only matters against strong teams (for example turn priority)
can't show up fully here; only scrimmages against the top teams can confirm it, and those play whatever is uploaded.

## 4. What to do

1. **Upload the next version with the top teams' build** (and any economy change that tests well), then scrimmage the top
   5 again with `cambc match-groups create TEAM_ID` (quota: 50 groups per window). Compare with this document's numbers:
   deaths per 100 rounds, item spending at death, dead share of the opening.
2. **Survive the opening.** Our champions die item-less in the first 300 rounds. Options to test next: shop in smaller
   batches early, value gold higher early, keep champions in pairs until their first emblem, and treat an enemy that has
   out-spent us as a reason to retreat earlier (needs enemy item estimates: their stats are visible, so compare
   `max_health()` and `strength()` with base values).
3. **Then fights**: focus fire and turn priority on top of an even item count. Standing to fight while out-itemed loses.
4. **C++:** the port (`bots/cpp13`) is done; see CPP_LINE.

## Appendix: commands

```
# platform games (match-group zips in replays/platform; read with python -I)
python -I research/2026-10-25/tools/vspro.py replays/platform/match-group-<id>-*.zip [--json out.json]
# list / download our matches and queue scrimmages (needs cambc login)
cambc matches list --team me --limit 40 [--json]
cambc match-groups show <GROUP_ID>
cambc match-groups create <TEAM_ID> --maps a,b,c,d,e
cambc ladder --limit 30
# local tests
bash matches/queue18.sh   # builds;  bash matches/queue19.sh  # fight flags;  bash matches/queue21.sh  # economy
```
