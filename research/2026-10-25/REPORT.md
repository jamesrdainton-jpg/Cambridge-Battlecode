# Why we started losing, and how to win again (2026-10-25)

Written for the team. Evidence: 25 of our platform games and 20 games between other teams downloaded on 2026-10-25,
probes of the 2.2.5 and 3.0.5 engines, and local gauntlets on the new engine and maps. Every number can be reproduced
with the commands in the appendix. DEVLOG rows 143 onwards log each step.

## 1. Summary

- **The game changed under us.** The platform moved to engine 3.0 on 20 Oct: a large balance patch, a new camp (the golem), a
  new champion (Heart of Ruin) and a 40-map pool in which all 17 of our old maps were edited. Our last upload, v12 (19 Oct),
  was built and tested on 2.2.5 and the old 17 maps. Its rating peaked at 1,627 (#158) around 20 Oct, when the platform
  switched, and has slid to about 1,430 (#487 of 788) since, with no new upload.
- **Five causes, in order of how much they cost us:**
  1. **A crash on every map with a golem** (6 of 40 maps, so about 15% of games are automatic losses). v12 indexed a 5-entry
     camp table by camp kind; the golem is kind 5. 3 of our 25 sampled games were these crashes.
  2. **Heuristics tuned for the old economy.** Camps now pay 3–6× fewer gems. Once camp state is read correctly, our squad
     logic makes champions wait for partners 11–12% of all turns, which the new economy can't afford.
  3. **A draft built on the champions the patch nerfed** (Stellar, Ren, Varg, Ryth, Cassi & Issac). The strong teams draft
     Vesper (97% of their drafts), Heart of Ruin (95%), Vendetta (80%) and Marcella (60%).
  4. **We lose fights.** We die 0.90 times per 100 rounds against our opponents' 0.74; the strong teams die only 0.37. Against
     one 3.0-meta team we died 83 times to their 3 over 5 games. Each death now pays the killer 100 gold (was 50) plus our gems.
  5. **We ignore bosses.** A monolith still pays 200 gems (50 wolves' worth) and 16 of the 40 maps have them. Strong teams hit a
     boss in 13 of 20 boss-map games (median first hit round 512); we did in 2 of 6 (rounds 804 and 1,092). One game ended 0–0.
- **Fixed today and ready to upload (v13):** camp stats read from the engine (no more crash, correct camp state and ranges),
  no squad waiting, and a 3.0 draft on 4- and 5-pick maps (Vendetta, Vesper, Tavi, Marcella, + Ryth). **v13 vs v12 on the 3.0
  engine, all 40 maps: 141/160, +78,724 gems (71/80 and 70/80; no map lost overall, 26 of 40 maps won 4/4).** The steps: the camp fix with no waiting beat v12 102/160 (+30,718); the new draft then beat
  the 2.2.5 draft 130/160 (+51,508). Upload it now: see section 6.
- **Next:** a process that catches the next patch on day one, scrimmages against the teams above us, more gold early, boss
  raids timed on real team strength, and fights against stun-and-burst drafts (section 5).
- **What other games teach** (section 4): the closest relatives are Pokémon UNITE and Heroes of the Storm's gem maps (carry,
  channel to bank, lose it all on death), MOBA jungling (camp routes, boss timing, invades) and the Halite programming contests
  (carry-and-bank economics). Battlecode postmortems add the process lesson: scrimmage the teams above you and copy what works.
- **C++:** noted as future work, with a measured expectation. In the cambc fuel model C++ fits only about **1.3–2× more of our
  kind of logic per turn** than Python, and engine calls cost the same share in both (section 7).

## 2. Timeline: the rating chart against what happened

| When | Event | Rating (chart) |
|---|---|---|
| 15–16 Oct | Platform versions v1–v3 (our releases of 15–16 Oct) | ~1,500–1,550 |
| 18 Oct | v4–v7 (our v7 and v10) | ~1,520–1,580 |
| 19 Oct, ~13:15 UTC | **v8 = our v12** (prompt shopping, pro draft, capture on kill) | rises to the season peak **1,627 (#158)** around 20 Oct |
| **20 Oct, 02:50 UTC** | **cambc 3.0.0 published**; the platform switches to 3.0 (3.0.5 by 22 Oct; patch notes in [PATCH-NOTES-3.0.md](PATCH-NOTES-3.0.md)) | the decline starts |
| 21–25 Oct | no upload; v12 keeps playing 3.0 games | ~1,420–1,450; **#487 of 788**; ranked 684–721 (49%) over the season |

The dashed line on the chart is the ladder position (right axis). It fell faster than the rating because the field kept
improving and growing while our bot stood still.

## 3. Evidence

### 3.1 What 3.0 changed (engine-measured; full tables in [PATCH-NOTES-3.0.md](PATCH-NOTES-3.0.md))

- **Camps pay far less:** wolf 22 → 4 gems, elk 36 → 15, gem cluster 24 → 7 (and 500 → 120 HP). The monolith still pays
  200 gems and 300 gold. **New golem:** 5,000 HP, 120 strength, range 4, 36 gems, 160 gold, respawn 80.
- **Camps reach further:** elk and golem 4, monolith 5. Abilities reach 4, so the "poke from range 4" trick the strong teams
  used on bosses in 2.2.5 is gone (the patch notes say so: it was "cheese").
- **Fights pay more:** kill gold 50 → 100. Heart of Ruin (new) dashes 2 tiles and stuns everything within 1 of where it lands.
- **Wards** can only move every 10 rounds (was every round); altar locks take 5 hits (was 3).
- **Map pool:** 40 maps. 6 have golems; 16 have monoliths, holding 31–100% of those maps' gems
  ([data/map-survey.md](data/map-survey.md)). Most maps hold only 70–850 gems in total, so reaching 1,000 means farming the
  map many times over; many games now reach round 2,000 and are decided on tributed gems.

### 3.2 Our 25 games and 20 games between other teams

Decoded with [tools/games30.py](tools/games30.py); per-game tables in [data/](data/).

- **Our results: 14 wins, 11 losses** (counting a 0–0 draw at round 2,000 on boss-battle, decided on gold, as a loss). 3 losses
  were crashes at round 1 (lost-world, quadrants, split). On 3-pick maps our draft (Vendetta, Ryth, Tavi) went 5/6; on 4- and 5-pick maps
  the 2.2.5 "pro draft" (Cassi & Issac, Stellar, Ren, Ryth, Varg) went 9/16 outside the crashes.
- **Games are longer, and ours longest:** our games mostly end between rounds 1,200 and 2,000; the strong teams' games end
  between rounds 575 and 1,400 (2.2.5 games ended around 400–1,000).

| | Us | Our opponents | Strong teams (the other 20 games) |
|---|---|---|---|
| Most-drafted champions | Ryth 100%, Stellar, Ren, Cassi & Issac 72% | Vendetta 80%, Ryth 72%, Varg 56% | **Vesper 97%, Heart of Ruin 95%, Vendetta 80%, Marcella 60%**, Cassi & Issac 42% |
| Gold spent by round 300 (median) | 740 | 440 | **1,365** |
| First item (median round) | 74 | 95 | 56 |
| Deaths per team per 100 rounds (strict count) | **0.90** | 0.74 | **0.37** |
| Boss-map games in which the team hit a monolith or golem | 2 of 6 | 2 of 8 | **13 of 20** (median first hit round 512) |

- **Fights.** Against the team that drafted Heart of Ruin, Marcella, Vesper, Prism and Ryth we died 25, 25, 9, 14 and 10 times
  in five games; they died 2, 0, 0, 1 and 0 times. Every death hands over 100 gold and our carried gems.
- **Fuel is fine except on 100×100 maps.** Median 0.64M of the 2.5M per turn; on big-world 1,387 turns went over 2.0M and many
  hit the cap ([tools/fuel30.py](tools/fuel30.py)).

### 3.3 Local tests on 3.0.5 and the 40 maps

Commands are in the appendix; results are in `matches/gauntlet.csv` and DEVLOG rows 145 onwards.

| Bot | vs v12 (seeds 1,2; 160 games) | Notes |
|---|---|---|
| `x13a`: camp stats from the engine (crash fix, true camp state, camp ranges) | 82/160, +674 | Golem maps 24/24; the other 34 maps only 58/136 |
| `x13b`: `x13a` + no squad waiting (`WAIT_LIMIT` 0) | **102/160, +30,718** | Golem maps 24/24; other maps 78/136 |
| `x13c`: `x13a` + `WAIT_LIMIT` 10 | 79/160, +2,491 | Even a short wait loses |
| `x14b` / `x14c`: base (= `x13b` behaviour) + boss raids by squad sizing (`BOSS_NEED_FRAC` 1.0 / 1.5, gather 40 turns) | vs the base, seed 1: 31/80, −5,367 / 30/80, −10,895 | Lose on nearly every boss map; the team commits before it is strong enough |
| `x14d`: base + the strong teams' draft at every size (Vesper, Heart of Ruin, Vendetta; + Cassi & Issac; + Marcella) | vs the base, seed 1: 53/80, +9,946 | Better than the 2.2.5 draft, but our logic doesn't use Heart of Ruin's dash |
| **`x14e`**: base + 4 = Vendetta, Vesper, Tavi, Marcella; 5 = + Ryth | vs the base, seed 1: **65/80, +27,518** (4-pick 15/16, 5-pick 44/52) | The buffed strength champions |
| **`x14f`**: base without the pro draft (4 = Vendetta, Varg, Ryth, Tavi; 5 = + Marcella) | vs the base, seed 1: **65/80, +21,305** (4-pick 14/16, 5-pick 45/52) | |
| `y15e` (= `x14e` with the camp-vision guard) vs `y15a` (the pro-draft base), seed 2 | **65/80, +23,990** (seeds 1+2: **130/160, +51,508**) | Confirmed |
| `y15f` (= `x14f`) vs `y15a`, seed 2 | 60/80, +19,774 (seeds 1+2: 125/160) | |
| **`y15e` vs `y15f`**, seeds 1,2 | **103/160, +17,688**; unopposed economy 50,720 rounds summed over 40 maps (`x13a` 63,921) | The strength draft wins; adopted in v13 |
| **v13 vs v12**, seeds 1,2 | **141/160, +78,724 gems (71/80 and 70/80; no map lost overall, 26 of 40 maps won 4/4)** | The release candidate |

**Why waiting hurt.** With DEBUG activity counts on eight, packs, fragment and rushbait-v2, the fixed bot waited for its squad
on 10.8–12.4% of champion-turns against v12's 0.9–1.2%, and hit camps on 20–22% of turns against v12's 25–28%. v12 only
escaped the wait by accident: it believed gem clusters had 500 HP, so every visible 120-HP cluster looked "damaged", every group
containing one looked awake, and awake groups skip the squad wait. Since the 3.0 maps put clusters in most groups, v12 almost
never waited, and that turned out to be right for the new economy.

## 4. What similar games teach, and what applies to us

This game is a MOBA's jungle (neutral camps, items bought at base, recall, wards, bushes, boss monsters) with one unusual rule:
**the score is carried, banked by a channel at an altar, and lost to whoever kills you.** These games share most of that:

| Game | What it shares | What winning players or bots do | What it means for us |
|---|---|---|---|
| **Pokémon UNITE** ([Bulbapedia: goal zone](https://bulbapedia.bulbagarden.net/wiki/Goal_zone), [GadgetMatch](https://www.gadgetmatch.com/pokemon-unite-how-to-win/), [GameWith](https://gamewith.net/pokemon-unite/article/show/19605)) — the closest relative | Points come from wild Pokémon, are carried, and are scored by a channel that takes longer the more you carry; damage interrupts it; a knocked-out player loses points; a late legendary boss swings games | Score in small batches rather than hoarding (shorter channel, less to lose); go for players visibly carrying many points; plan around the boss (force it when behind, slow-play it when ahead); scoring is faster with teammates nearby | Bank before fights and before walking into contested ground; make carriers (ours and theirs) a fight-value term; treat the monolith as the game's swing objective |
| **Heroes of the Storm, Tomb of the Spider Queen / Blackheart's Bay** ([Liquipedia](https://liquipedia.net/heroes/Tomb_of_the_Spider_Queen), [Icy Veins](https://icy-veins.com/heroes/tomb-of-the-spider-queen-map-guide), [PC Gamer](https://pcgamer.com/hots-spider-queen-guide)) | Gems from camps and kills, turned in by an interruptible channel at altars; gems drop on death | Turn in before you die; fight over the turn-in area; keep the team close to the altars | Our tribute thresholds should depend on threat, not only on carried gems; altar approaches are where fights happen, so ward them |
| **League of Legends / Dota 2 jungling** ([WeCoach](https://wecoach.gg/de/blog/article/how-to-play-jungle-in-league-of-legends), [Mobalytics](https://mobalytics.gg/blog/low-elo-to-diamond-jungler-part-2/), [TheSpike](https://www.thespike.gg/league-of-legends/beginner-guides/how-to-jungle-guide), [Roshan control](https://www.fragster.de/en/learn-dota-2-roshan-control/), [esports.net timers](https://www.esports.net/news/dota/dota-2-timers/)) | Neutral camps on timers, items from base, recall, wards, a boss pit | Efficient clear routes; take the boss (Baron, Roshan) right after winning a fight or while enemies are dead or far away, with vision of the pit; invade the enemy's camps when ahead; time recalls to item breakpoints | Boss raids: when enemies are dead or far, go as a team; ward the boss before starting; with kill gold at 100 the patch explicitly rewards invades and contesting camps |
| **Halite III / IV** (Two Sigma; [Halite III bots](https://github.com/dhallstr/Halite-3-bot), [stefank0's commit notes](https://github.com/stefank0/halite3/commit/104dad0f69063b2a3df89d3da712eb8acd226400), [Wikipedia](https://en.wikipedia.org/wiki/Halite_AI_Programming_Competition)) — a programming contest | Ships mine, carry and must return to bank; in Halite IV carried halite can be stolen | Score targets by yield per turn *including the trip back*; return when nearly full **or** when the next target is worth little relative to what you carry, and commit to the return once decided; in IV, hunt loaded enemy ships and guard your dropoffs | Our target score already includes the altar trip; add "carried value vs next target" to the tribute decision and keep the decision sticky; hunt loaded enemy carriers |
| **MIT Battlecode** (postmortems: [2026 2nd place](https://battlecode.org/assets/files/postmortem-2026-generalized-strokes-theorem.pdf), [2025 The Kragle](https://battlecode.org/assets/files/postmortem-2025-the-kragle.pdf), [2025 just woke up](https://battlecode.org/assets/files/postmortem-2025-just-woke-up.pdf), [2024 Cout for Clout](https://battlecode.org/assets/files/postmortem-2024-cout-for-clout.pdf), [2023 Don't @ Me](https://battlecode.org/assets/files/postmortem-2023-dont-at-me.pdf), [2022 5 Musketeers](https://battlecode.org/assets/files/postmortem-2022-5-musketeers.pdf)) — the same kind of competition | Bots on a ladder, mid-season balance patches, compute limits | "Queue scrims against teams above us on the leaderboard, reverse engineer their macro, copy whatever strategy we gleaned, and if it made us better then we would keep it" (2026). "Other teams beat your bot for a reason, and the easiest way to improve is to copy what they do better than you" (2025). One team scripted scrimmages against the top 20. Strong strategies get nerfed quickly, so adapt to each patch. A week without development "was a massive blow". Winners spent more time reviewing games than writing code | Our biggest loss was process: six days on a stale engine. Log in, pull top teams' games daily, scrimmage teams just above us (`cambc match-groups create`), and check for engine releases (section 5) |

## 5. Recommendations, ranked

| # | Change | Why | Status |
|---|---|---|---|
| 1 | **Upload v13** | Removes 15% automatic losses and the pro-draft liability; 141/160, +78,724 gems vs v12 locally | Ready: section 6 |
| 2 | **Stay current with the platform.** Once a day: check for a new `cambc` (`pip index versions cambc`), pull maps with the current CLI, run the rules probe and diff, rerun the gauntlet | Six days of a stale bot cost ~200 rating points; the next patch will move numbers again (Heart of Ruin already had an emergency nerf) | Process; tools in `research/2026-10-25/tools/` |
| 3 | **Scrimmage and copy.** `cambc login` once a week (7-day session). Then `cambc ladder` for the teams above us, `cambc matches list --team NAME` and `download` for their games, `cambc match-groups create TEAM_ID --maps a,b,c,d,e` for 5-game scrimmages, and `tools/games30.py` to compare drafts, spending, boss timing and deaths | Every Battlecode postmortem above says this is how macro improves; our local opponents share our blind spots | Needs the login (interactive, so a person must do it) |
| 4 | **3.0 draft** | Our 4–5-pick draft is the nerfed 2.2.5 meta; strong teams take Vesper, Heart of Ruin, Vendetta, Marcella | **Done in v13**: 4 = Vendetta, Vesper, Tavi, Marcella; 5 = + Ryth (130/160 vs the 2.2.5 draft, 103/160 vs our old 4–5-pick draft). The strong teams' own draft with Heart of Ruin did worse for us (53/80): our logic only uses its dash to travel, not to land on enemies |
| 5 | **Boss raids.** Size squads for monolith and golem groups with a higher damage tolerance, gather before engaging (no trickling in), rotate the tank via the low-health retreat, claim on kill. Go when enemies are dead or far away, as MOBA teams take Baron or Roshan | Monolith = 200 gems ≈ 4× the gems per team-round of normal farming (our team farms ~0.6 gems a round unopposed); strong teams hit bosses in 13/20 boss-map games | Tried: lowering the squad-size bar for bosses loses (31/80 and 30/80). Needs a design that times raids on real team damage and enemy positions, informed by the strong teams' replays |
| 6 | **Fights against 3.0 drafts.** Count stuns and Heart of Ruin's dash (threat radius 3) in the fight ratio; bank gems before contested ground; value enemy carriers higher (100 gold + their gems) | Deaths 0.90 vs 0.74 per 100 rounds, and 83 to 3 against one 3.0-meta team | Not started |
| 7 | **Wards** every 10 rounds now: place them at boss pits and altar approaches instead of re-placing each turn | Ward cooldown 1 → 10 | Not started |
| 8 | **C++ port** (future) | 1.3–2× more logic per turn; only matters for heavier search or the 100×100 maps | Noted in HANDOFF (section 7) |

## 6. The bot to upload: v13

- **File:** `submissions/cambridge-bot-latest.zip` (on James's PC:
  `C:\Users\james\GitHub\Cambridge-Battlecode\submissions\cambridge-bot-latest.zip`), the same file as
  `submissions/cambridge-bot-2026-10-25.zip`. Content hash `e2f2efbe4ce8`, built from `bots/v13` (commit `485355a`) with DEBUG off.
  It is committed, so teammates can download it from GitHub; `tools/release.py --src v13` rebuilds the identical file anywhere.
- **What it is:** v12 + (1) camp stats from the engine, (2) no squad waiting, (3) the 3.0 strength draft on 4- and 5-pick maps.
  3-pick maps keep Vendetta, Ryth, Tavi (5/6 on the platform under 3.0).
- **Checks:** 6/6 wins vs the starter on 00packs, 00lanes and 00monolith (cambc 3.0.5), no error lines; 0 `bot error` lines in its 200 games vs v12 and idle.
- **How to upload:** the platform's submission page, or `.venv\Scripts\cambc.exe submit release` after `cambc login`.
- **After a day of games:** download them into `replays\platform\` and run `research/2026-10-25/tools/games30.py` on the new
  match groups. Look for: no `bot error` lines, wins on the golem maps, our deaths per 100 rounds, and the 4–5-pick results.

## 7. Note for later: converting the bot to C++

The idea is to get more done per turn. Measured on cambc 3.0.5 in release mode
([tools/fuel_bench](tools/fuel_bench/README.md)), as a share of one turn's fuel (C++ gets 100,000 per turn, Python 2,500,000):

| Work | C++ | Python |
|---|---|---|
| Scoring loop shaped like ours (records, divisions, comparisons) | 16% | 33% |
| Hand-written 8-way BFS on a 15×15 grid | 11% | 14% |
| 100 `position()` reads | 8% | 11% |
| Plain arithmetic loop | 45% | 25% |
| SDK distance field over a 100×100 map | 30% | 30% |
| `camp_groups()` | 25% | 32% |

- **Expected gain: about 1.3–2× more of our kind of logic per turn**, not the 25× the raw fuel numbers suggest, because the
  engine gives Python 25 times the fuel and charges engine calls in proportion.
- **What it would buy:** headroom on the 100×100 maps (big-world, ambush), where our Python bot hits the 2.5M cap, and room
  for heavier logic such as fight look-ahead or multi-turn route planning.
- **What it would cost:** a rewrite of ~2,100 lines against a different API (`sdk/cpp/cambc.h`), with every behaviour
  re-validated by gauntlet. The toolchain already works on James's PC (`cambc init` configured wasi-sdk 33).
- **Suggested path:** do it after the strategy gaps above are closed. Start by porting one hot path behind the same
  interface (target scoring or fight evaluation), measure with the benchmark bots, then decide. Rust has the same limit as C++.

## Appendix: how to reproduce

All from the repo root on cambc 3.0.5 (`pip install -r requirements-dev.txt`). On Mac/Linux use `.venv/bin/python`.
Platform downloads go in `replays/platform/` (not in git); read them with `python -I`, since they are untrusted data.

```
# Engine and map facts
pip index versions cambc                                             # is the platform on a newer engine than our pin?
mkdir -p bots/rs_rules/src && cp research/2026-10-25/tools/rules_probe.py bots/rs_rules/src/main.py
.venv/Scripts/cambc.exe run rs_rules rs_rules --map 00packs --rounds 1  # constants, all champion and camp designs (team-a.stdout)
mkdir -p bots/rs_survey/src && cp research/2026-10-25/tools/survey_probe.py bots/rs_survey/src/main.py
#   run rs_survey on every map for 1 round (run-batch manifest), save each team-a.stdout as research/2026-10-25/data/mapdumps/MAP.txt
.venv/Scripts/python.exe research/2026-10-25/tools/survey_table.py   # data/map-survey.md: gems, boss share, golems per map

# Platform games (match-group zips)
.venv/Scripts/python.exe -I research/2026-10-25/tools/games30.py replays/platform/match-group-*.zip   # drafts, hits by camp kind, spending, boss timing
.venv/Scripts/python.exe -I research/2026-10-25/tools/fuel30.py replays/platform/match-group-*.zip    # our fuel per turn
.venv/Scripts/python.exe -I research/2026-10-25/tools/extract_maps.py OUTDIR replays/platform/match-group-*.zip  # maps embedded in replays
.venv/Scripts/python.exe -I tools/replay_decode.py replays/platform/match-group-*.zip                 # per-team summary (knows Heart of Ruin)

# Local tests (DEVLOG rows 145-150)
.venv/Scripts/python.exe tools/variant.py x13a                                   # mybot with DEBUG off
.venv/Scripts/python.exe tools/gauntlet.py x13a --vs v12 --seeds 1,2            # 160 games on the 40 maps + economy
bash matches/queue15.sh                                                          # squad-wait variants vs v12
bash matches/queue16.sh                                                          # boss raids and 3.0 drafts vs the base
.venv/Scripts/python.exe research/2026-10-25/tools/permap.py x13b_s1-vs-v12_s1 x13b_s2-vs-v12_s2   # per-map table of a run

# Fuel benchmark (C++ vs Python): see research/2026-10-25/tools/fuel_bench/README.md
```

Machine: James's PC (Windows 11, 22 logical cores, one batch at a time). A 160-game gauntlet on the 40 maps took ~12 minutes.
