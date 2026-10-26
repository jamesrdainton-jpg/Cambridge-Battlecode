# Handover — Cambridge Battlecode 2026 bot

State as of **2026-10-26** (patch 4.0, v14; DEVLOG rows 158–162). Before that, **2026-10-25** (engine 3.0 diagnosis, v13; DEVLOG rows 143 onwards; report: [research/2026-10-25/REPORT.md](research/2026-10-25/REPORT.md)). Before that: v12 from the 2026-10-19 research report (rows 135–142), the 2026-10-18 sprint (rows 120–134) and the 2026-10-16 platform-data session (rows 82–109). The full history of every experiment is in [DEVLOG.md](DEVLOG.md).

**Team rule:** more than one person works on this repo, each on their own computer, so every result must be reproducible on a different computer from a git commit. Commit code before testing it, record the commit and the exact command, keep queue scripts and `matches\gauntlet.csv` in git, and use the pinned cambc with the committed maps. Details are in the "Team rule" section near the top of DEVLOG.md.

## 2026-10-26 (afternoon): patch 4.0; v14 released

- **Platform moved to engine 2.0.0 / cambc CLI 4.0.0** (patch notes and engine-measured stats: [research/2026-10-26/PATCH-NOTES-4.0.md](research/2026-10-26/PATCH-NOTES-4.0.md)); the repo is on cambc 4.0.0 with the **70-map pool**. Treasure was halved (+10% gold); seven new emblem families.
- **v14** (`bots/v14`, ZIP `submissions/cambridge-bot-2026-10-26.zip`, hash `ff8acacbefc7`; **upload it**): Monster-first build (`BUILD_30` 4; queue 25: Monster 97/140 vs v13, Treasure 86, Capture 87, Prospector 87), turn priority while fighting, **00vault fix** (both bots used to stall at the walled 343-gem vault: they refused to stand on dead camp tiles), and **gold mode** on 01boss-battle, 02guardians and 02the-pack, where no altar can be reached without killing a monolith or a 48-wolf ring and the round limit decides on lifetime gold (19/24 vs without). DEVLOG 160–162.
- **C++** (`bots/cpp13`, same defaults as v14): fuel-capped turns now 0.02%; queue 25: 82/140 vs v13 against 86/140 for the same flags in Python (noise level). **Unfinished:** the C++ vs Python head-to-head (`c26g` vs `z26g`, queue 26) and the seed-2 check; if C++ is at least equal, release it with `tools/release.py --src cpp13 --verify` (freeze as a new folder first). Queue 27 (`matches/queue27.sh`, draft after the Vesper nerf) is ready to run.
- **Replay parsers** read the header version (u16 major/minor at offsets 8/10; 4.0 = (2,0)). Terrain probe: `research/2026-10-26/tools/terrain_probe.py`.
- **Next:** upload v14, scrimmage the top 5 and compare with VS-TOP5.md; contest big captures (on 00vault our champions clear the vault and the enemy captures it); fights.

## 2026-10-26: why we lose to the top teams; v14 in progress; C++ port

- **v13 went 1/25 against the ladder's top 5** (Intercontinental Fish, Mite, Claudus Maximus, willow best girl, prism best girl; groups queued 2026-10-25). Full analysis: [research/2026-10-25/VS-TOP5.md](research/2026-10-25/VS-TOP5.md). In short: they buy items early (Treasure first, then Bruiser stacks), pick off our item-less champions (in 89% of our deaths the killer had out-spent our champion on items; in the first 300 rounds our dying champion's median spending was 0 gold vs 210), our champions spend 20% of the opening dead (theirs 6%), and the gold gap snowballs (1,712 vs 563 spent by round 300). They won 218 engagements to our 23. All five order their turns with `set_priority` every round.
- **The CLI is logged in** (session lasts 7 days): `cambc matches list --team me`, `cambc match-groups show/download`, `cambc match-groups create TEAM_ID --maps ...` (quota 50 groups per window), `cambc ladder`. Scrimmages play whatever is uploaded, so test a new version against the top teams after uploading it. We are "Opus 5.5" (team id `cd168e4d-…`).
- **Replay tooling for 3.0:** `research/2026-10-25/tools/replay30.py` orders turns by **signed** `set_priority` (the old draft-order parser mis-assigns strong teams' turns); `vspro.py` reports deaths with killers, engagements, spending, territory per game and in aggregate.
- **Adopted for v14** (on top of v13; DEVLOG 152–156): `BUILD_30` 1 (Treasure, Jungle H, Bruiser, Durability H, then Bruiser stacks): **99/160, +21,031 vs v13**; `FIGHT_PRIO` (champions that fought act first next round): **87/160, +12,116**. Tested and not adopted: standing to fight when trapped (28/80), help calls (38/80), fight commitment (38/80), shopping at 90 gold (38/80), double gold weight (39/80), the lean Bruiser-only build (80/160).
- **C++ port** (the user's request): `bots/cpp13` = v13 in C++ (tunables in `src/params.h`; `tools/variant.py`, `gauntlet.py` and `release.py` handle C++ bots). First parity 72/160 vs v13 (fuel-capped turns); fixed C++-specific fuel costs (exceptions ~4k fuel each in wasm; field exports). **Queue 22 re-tests parity; queue 23 plays the v14 candidate in C++ (`cpp14`) and Python (`py14`) vs v13 and head to head.** Release whichever is stronger (C++ if equal, as the user prefers). `.vscode/settings.json` gets a machine path added by C++ builds: don't commit it.
- **Next:** release v14, upload, then scrimmage the top 5 and compare deaths per 100 rounds, item spending at death and the dead share of the opening with VS-TOP5.md.

## 2026-10-25: the platform moved to engine 3.0; upload v13

- **What happened.** On 2026-10-20 the platform switched to **cambc 3.0** (3.0.5 since 10-22): a big balance patch, a new camp (**golem**), a new champion (**Heart of Ruin**) and a **40-map pool** (all 17 old maps edited, 23 new). Our v12 (19 Oct) was built for 2.2.5. It **crashes at round 1 on every map with a golem** (6 of 40) and its heuristics and draft are tuned for the old rules. Rating: peak 1,627 (#158) around the switch, ~1,430 (#487 of 788) on 25 Oct. Patch notes and engine-measured numbers: [research/2026-10-25/PATCH-NOTES-3.0.md](research/2026-10-25/PATCH-NOTES-3.0.md). **`GameRules.md` is out of date** for every number in it.
- **The repo is on cambc 3.0.5 now.** `requirements-dev.txt`, `cambc.toml`, `sdk/`, `cmake/` and `maps/` (the 40 platform maps as `cambc maps pull` names them, e.g. `00contest`, `01boss-battle`) were upgraded; the old 17 maps are in `maps/archive-2.2.5/`. **Teammates: `pip install -r requirements-dev.txt`.** Results before DEVLOG row 144 are on the old rules and can't be compared with new ones. `tools/repro_check.py`'s reference is still the 2.2.5 one (regenerate it with `--write` on a quiet machine and commit).
- **v13 = v12 + three changes** (`bots/v13`, commit `485355a`; `mybot` = v13 with DEBUG on; DEVLOG 145–151):
  1. **Camp stats from the engine** (`world.learn_camp`): health, strength and range per camp kind from `Camp.base_stats()`. Fixes the golem crash, the stale cluster health (500 → 120) and danger zones (elk and golem reach 4, monolith 5). A camp listed in vision whose health can't be read is skipped instead of failing the turn.
  2. **No squad waiting** (`WAIT_LIMIT` 0). With camp state read correctly, champions waited for partners on 11–12% of all turns; v12 only escaped that by accident.
  3. **3.0 draft on 4- and 5-pick maps** (`draft.py` `BY_SIZE`): 4 = Vendetta, Vesper, Tavi, Marcella; 5 = + Ryth; `PRO_DRAFT` off (the 2.2.5 pro draft's Cassi & Issac, Stellar and Ren were nerfed). 3-pick maps keep Vendetta, Ryth, Tavi. No early packs follow from this (packs only ran with Cassi & Issac or Stellar).
  - **Results on 3.0.5, all 40 maps, seeds 1,2:** changes 1+2 vs v12 **102/160, +30,718** (golem maps 24/24; the stats fix with the old 40-turn wait was only 82/160, with a 10-turn wait 79/160). Change 3 vs the pro draft **130/160, +51,508**, and vs our old 4–5-pick draft 103/160, +17,688. **v13 vs v12: 141/160, +78,724 gems (71/80 and 70/80; no map lost overall, 26 of 40 maps won 4/4).**
- **Upload ZIP:** `submissions/cambridge-bot-latest.zip` = `cambridge-bot-2026-10-25.zip`, content hash `e2f2efbe4ce8`, built from `bots/v13` (commit `485355a`) with DEBUG off; 6/6 wins vs the starter on 00packs, 00lanes and 00monolith (cambc 3.0.5), no error lines; 0 `bot error` lines in its 200 games vs v12 and idle. Committed, so it can be downloaded from GitHub; rebuild anywhere with `tools/release.py --src v13`.
- **Tested and rejected:** boss raids by lowering the squad-size bar for monoliths and golems (`BOSS_NEED_FRAC` 1.0 + `BOSS_WAIT` 40: **31/80, −5,367** vs the base; loses on nearly every boss map). Also tested: the strong teams' own draft (Vesper, Heart of Ruin, Vendetta, + Cassi & Issac, + Marcella) 53/80 vs the base, below the strength draft (our logic only uses Heart of Ruin's dash for travel); a 10-turn squad wait (79/160 vs v12).
- **What the platform shows** (25 of our games, 20 of other teams', [report section 3](research/2026-10-25/REPORT.md)): strong teams draft **Vesper 97%, Heart of Ruin 95%, Vendetta 80%, Marcella 60%** (Stellar 0%); they spend **1,365 gold by round 300 (us 740)**, hit a boss in **13 of 20** boss-map games (us 2 of 6), and die **0.37** times per 100 rounds (us 0.90). On **01boss-battle the only altar is sealed** behind a monolith: nobody tributes until it dies (every game there so far ended 0–0).
- **Next steps, ranked** (details in the report, section 5): (1) upload v13; (2) **stay current**: check `pip index versions cambc` against `requirements-dev.txt` at the start of every session, pull maps with the current CLI, rerun `research/2026-10-25/tools/rules_probe.py` and diff; (3) **log in** (`cambc login`, interactive, 7-day session) so the CLI can pull the top teams' games (`cambc matches list --team NAME`) and queue scrimmages against teams just above us (`cambc match-groups create TEAM_ID --maps ...`); (4) **economy first**: more gold early (Vesper's +33%, gold clusters at 120 HP, Marcella's 2 gold per gem tributed), then (5) boss timing designed from real team damage and the strong teams' replays, (6) fights against stun-and-burst 3.0 drafts (Heart of Ruin's dash stuns radius 1 around a tile 2 away).
- **Future (the user's request): try converting the bot to C++ for efficiency.** Measured first ([report section 7](research/2026-10-25/REPORT.md), benchmark in `research/2026-10-25/tools/fuel_bench/`): in the cambc fuel model C++ fits about **1.3–2× more of our kind of logic per turn** than Python, and engine calls (distance fields, `camp_groups()`) cost the same share of a turn in both languages, because Python gets 25× the fuel. The gain is real but modest: worth it for heavier search (fight look-ahead, route planning) and for the 100×100 maps where our Python bot hits its 2.5M cap (big-world, ambush). Suggested path: close the strategy gaps first, then port one hot path (target scoring or fight evaluation) and measure before porting everything. The C++ toolchain already works (`cambc init` configured wasi-sdk 33; template in `sdk/templates/cpp`).

## The bot submitted on 2026-10-19: v12 (superseded by v13 above)

- **Upload ZIP then: `submissions/cambridge-bot-2026-10-19.zip`** = **v12**: content hash `7c7fa17be827`, built from commit `826b5cc` with DEBUG off, verified 6/6 vs the starter on cambc 2.2.5 with no error lines. Rebuild with `tools/release.py --src v12` (on cambc 2.2.5 and the archived maps; on 3.0 it crashes on golem maps)
- **v12 = v10 + three changes** (all in `bots/mybot` as flags; v12 = mybot with DEBUG off):
  1. **Spend gold as it comes in:** shop whenever carrying 150+ gold at any health (`SHOP_GOLD` 150, `SHOP_HP` 1.01), only while the build has stages left (a final Power 60 stage was added), and never start a shopping recall while hurt, next to an enemy or in a camp's reach (`SHOP_SAFE`). v10 hoarded ~400 gold per team and scored 0 gems on contest.
  2. **Pro draft on 4- and 5-pick maps** (`draft.py` `PRO_DRAFT = (4, 5)`: Cassi & Issac, Stellar, Ren, + Ryth, + Varg), with **pack farming until round 150** for that draft only (`PACK_UNTIL` 150, `PACK_PRO_ONLY`). 3-pick maps keep Vendetta, Ryth, Tavi (platform 5/6 with it); packs with our draft lost 8/32.
  3. **`CLAIM_ON_KILL`:** a melee champion that kills a group's last camp steps onto its spawn tile in the same turn, so an enemy can't take the capture.
- **Local results** (seeded, every map from both sides):
  - **v12 vs v10 (gauntlet, seeds 1,2): 45/68, +11,138**; economy 10,504 (v10 11,623). 3-pick maps 10/16, 4-pick 12/16, 5-pick 23/36; contest 4/4 (v10 scored 0 gems there unopposed).
  - The shopping package vs v10: 44/68, +6,728. The pro draft vs our draft on the 13 maps where they differ: 33/52, +4,996 (contest, rows, stampede 4/4).
- **Switched off after testing:** boss poking (`MONOLITH_POKE`, with the fixed poke ring, capture step and shared poke health): 3/16 vs v10 on contest + stampede, against 10/16 with it off. The chase check (`research/2026-10-19/patches/chase.py`) was neutral (34/68, +36).
- **Previous submission:** v10 (`cambridge-bot-2026-10-18-2.zip`, hash `43c90c9220c2`): 13/30 on the platform on 2026-10-18.
- **After a day of platform games:** download them and run the report's scripts (`research/2026-10-19/tools/ourgames.py`, `teamstats.py`, `deaths2.py`) to see whether the economy gap closed and how the pro draft does on 4- and 5-pick maps. The weak maps for the pro draft locally are corners, monolith and pilgrimage (1/4 each vs our draft).

## Where everything is

- **Project folder:** on James's PC, `C:\Users\james\GitHub\Cambridge-Battlecode`. Teammates work in their own clones.
- **Git:** remote `origin` = `https://github.com/jamesrdainton-jpg/Cambridge-Battlecode.git`. Several people commit and push, so pull before starting. Experiment bots, caches, the venv, replays and `submissions/` stay out of git; results, queue scripts and logs in `matches/` are tracked. Keep the repo private during the competition.
- **Engine: cambc 2.2.2** (upgraded 2026-10-16; the platform runs a 2.2.x engine). **Teammates must upgrade:** `pip install -r requirements-dev.txt`, then run `tools\repro_check.py`. It must print `REPRODUCED` (34 reference games) before your numbers are comparable.
- **Maps:** `maps\` is the platform's current **17-map pool**: 8 maps are new (ambush, contest, eight, fragment, pilgrimage, rushbait-v2, stampede, swirl) and 6 were updated. Every result before DEVLOG row 82 was on the old engine and the old 9 maps.
- **Avast:** exclude `battlecode.co.uk` in Avast's Web Shield, or `cambc maps pull` / `login` / `submit` fail.

## Previous submission: v10 (competition, 2026-10-18 evening)

- **Upload ZIP: `submissions/cambridge-bot-latest.zip`**, which is **v10**: content hash `43c90c9220c2`, built from commit `36013cc` with DEBUG off, and verified 6/6 vs the starter on cambc 2.2.5 with no error lines. `submissions/` is normally ignored, but this one ZIP is **committed on branch `claude/adoring-fermat-jthwy1`**, so it can be downloaded from GitHub. It is the same file as `cambridge-bot-2026-10-18-2.zip`. Rebuild it anywhere with `tools/release.py --src v10` (or `--src mybot`, which now equals v10 apart from DEBUG); the content hash comes out the same.
- **v10 = v8 + `FIGHT_SHIELD` + `WARDS` + `CAST_FIRST`** (v8 = v7 + `IGNORE_SPAWN_CAMPERS` + `CAMP_TILE_FIX`).
  - **vs v8: 55/68, +13,016** (seeds 1,2) and 24/34, +6,020 (seed 3). It farms faster too: economy 11,623 vs ~12,100.
  - **vs `meta`** (the strong teams' draft): **33/34, +11,258** (seed 3; v11 went 31/34 on the same seed); the partial seed-1 run went 18 of 22.
  - Our champions died **283 times vs v8's 552** in the 68 games.
- **Why not v11** (v10 + `FIGHT_MEMO` 2):
  - Against v10 it is only 108/204 (seeds 1–6: 42, 32, 34 of 68) and +5,644 gems, which is not significant.
  - On seed 3 it did worse than v10 against the two other opponents: vs v8 19/34 against v10's 24/34. It beat `meta` 58/68 on seeds 1,2.
  - It is frozen in `bots/v11` for later testing.
- **When the user asks for the latest bot:** run `.venv\Scripts\python.exe tools\release.py --verify` (leave out `--verify` while a batch runs) and give the ZIP's full path. The steps are in "Latest bot" at the top of DEVLOG.md.
- **Working copy (now):** `bots/mybot/src` (DEBUG on) = v12 plus switched-off flags (`MONOLITH_POKE`, `POKE_AVOID_ENEMY`, ...). **Frozen versions:** `bots/v1`–`v12`; v12 is the baseline for new tests.
- **This machine runs one batch at a time.** Two `run-batch` processes at 18 jobs each run a 15 GB machine out of memory, and the killed games count as losses (DEVLOG 124). Always check `batch.log` for `FAILED` lines.

### Competition sprint results (DEVLOG rows 120–132)

| Flag | What it does | Result | Status |
|---|---|---|---|
| `FIGHT_SHIELD` | Varg casts its self-shield in fights (`support()` only ran while farming) | 40/68, +5,246 vs v8 | **in v10** |
| `WARDS` + `CAST_FIRST` | On top of the shield: wards on bushes near the target; ranged champions cast before the basic attack | 55/68, +13,016 vs v8 (with the shield) | **in v10** |
| `FIGHT_MEMO` 2 | Fight on the lowest strength ratio of the last 2 rounds (stops chase/flee flip-flops) | 108/204, +5,644 vs v10 (seeds 1–6) | off (v11) |
| `FIGHT_MEMO` 3 | Same, 3 rounds | 27/68, −3,538 vs v11 | off |
| `RECALL_SAFE` 4 | No recall within 4 rounds of an enemy within 10 tiles | 15 of 30 valid games vs v10 | off |
| `CC_FIRST` | Ryth and Tavi stun champions before the basic attack | 34/68, +1,564 vs v10 | off |
| `TRIBUTE_BIG/MID` 20/10 | Bank gems sooner | 35/68, +916 vs v10 | off (30/15) |
| `FIGHT_GEM_EXTRA` 0.5 | Gem carriers more cautious | 36/68, +118 vs v11 | off (0.25) |
| `FIGHT_ENGAGE` 1.1 | Chase sooner | 37/68, −1,074 vs v11 | off (1.3) |
| `ALLY_RANGE` 5 | Count fewer allies in the ratio | 26/68, −4,112 vs v11 | off (7) |
| `NEED_FRAC` 0.7 | Fewer champions per camp | 34/68, +190 vs v11; economy 11,304 (faster) | off (0.55) |
| `SHOP_GOLD` 200 | Shop sooner | 32/68, +782 vs v11 | off (300) |

Cloud sessions A–D ran some of these on their own machines; their `gauntlet.csv` rows are on branches `claude/sprint-a-fight-thresholds`, `claude/sprint-b-fight-memory`, `claude/sprint-c-confirm-v11` and `claude/sprint-d-economy`.

### Older flags in `mybot` (tested vs v6; `IGNORE_SPAWN_CAMPERS` and `CAMP_TILE_FIX` are now on, `WARDS` is on in v10)

| Flag | What it does | Result vs v6 (68 games unless noted) |
|---|---|---|
| `IGNORE_SPAWN_CAMPERS` | Ignore enemies standing in their own spawn unless we're hurt | 33/68, +196. Fixes **0 gems on rushbait-v2** against spawn-sitters (now wins by round 655) |
| `CAMP_TILE_FIX` | Melee approach avoids camp spawn tiles | 35/68, +1,080. Fixes a **1,700-turn step-on/step-off loop on contest** (contest vs idle: 400 gems → win at round 1,619) |
| `MONOLITH_POKE` | Poke too-strong groups from range 4 with abilities (line-of-sight ring) | 34/68, −1,250. Contest vs idle → win at round 1,851. Clashes with `CAMP_TILE_FIX` on contest |
| `STANDOFF_TURNS` + `TEAM_STALL_ROUNDS` | Stand-off breaker only after 150 rounds of flat team gems | 34/68, +1,086 |
| `WARDS` | Ward bush tiles near our target, as pros do | 71/136, **+9,816**: consistently more gems, not more wins |
| `POWER_FIRST` | Power emblem instead of Monster first | 35/68, −1,608 |
| `TELEMETRY` | Death and activity lines with DEBUG off (printing only) | not needed now that replays decode fully |

The first two are real bug fixes on single maps. A 68-game gauntlet can't see them (each moves the score by ~2 games, inside the ±4 noise). Adopting them as insurance is a judgement call that was not made this session.

## What the platform data shows (DEVLOG rows 82–104)

- **Our 15 games: 6 wins.** We fall behind on gems by round 200 in most losses. **79% of our deaths come from enemy champions**, not camps (fragment 17 in 2 games, interlock 10 in one), and every kill hands them our carried gems.
- **110 pro team-games**, decoded:
  - **Draft:** Cassi & Issac 94%, Stellar 92%, Ren 72%, Varg 70%, Tavi 51%, Ryth 47%. **Vendetta (our first pick) 7%, Marcella 2%.**
  - **Gold:** pros spend **2.4× our gold by round 150** (776 vs 321 per team) and buy their first items at round ~47 (us 71). Items are Power F/S 29% each, Bruiser and Durability H; almost no Monster.
  - **Vision:** 77% ward constantly, 71% of wards on bush tiles near camps and altars.
  - **Other:** almost no altar locks; they recall 5.5 times per 100 rounds and tribute every 24 rounds.
- **With our logic the pro draft loses** (v6 beat `bots/meta` 48/68; Cassi & Issac as 5th pick 31/68). Pros' Stellar/Cassi play is something our bot doesn't do. They probably poke camps from range 4 with focus builds, while our ranged champions stand at range 3, inside camp range.

## Settled by testing (don't redo without a new reason)

- **Spread out** with our draft: pairs and whole-team squads lose, and early packs lost 8/32 on 3-pick maps (DEVLOG 138). The pro draft farms in packs until round 150 (v12).
- **Fight thresholds.** Retreat below 0.9, engage at 1.3 (old engine; real matches now suggest revisiting fights, see next steps).
- **Gold:** 0.4 fading by round 500 beats 0.15 (v7). Shopping at 150 gold at any health was neutral vs v6 (sh1 33/68) but wins vs v10 once it stops when the build is finished (v12: 44/68, +6,728; DEVLOG 136–137).
- **Draft:** 3 picks Vendetta, Ryth, Tavi. On 4- and 5-pick maps the pro draft (Cassi & Issac, Stellar, Ren, + Ryth, + Varg) with early packs now beats our draft (25/32 and 40/72; DEVLOG 138, 140). The older "pro draft loses with our logic" results (v6, v7) predate prompt shopping.
- **Boss poking** (`MONOLITH_POKE`, even with the fixed ring, capture step and shared poke health) loses contested boss maps: 3/16 vs 10/16 with it off (DEVLOG 139).
- **Squad sizing and items.** `NEED_FRAC` 0.55. Wait 40 turns for the squad (60 and 15 are worse). Jungle-first, Jungle-aware sizing, `GEM_HUNT` and Power-first are neutral or worse.

## How to run things (from the project folder)

```
pip index versions cambc                                                # FIRST: is the platform on a newer engine than requirements-dev.txt?
.venv\Scripts\python.exe tools\gauntlet.py mybot --vs v13 --seeds 1,2   # 160 games + 40 economy games on the 40 maps, ~15 min
.venv\Scripts\python.exe tools\arena.py mybot v13 --maps 00contest      # one map, both sides (maps are named as `cambc maps pull` names them)
.venv\Scripts\python.exe tools\variant.py NAME --set "bot.py:OLD=>NEW"  # A/B copy with a changed constant (always DEBUG off)
.venv\Scripts\python.exe research\2026-10-25\tools\permap.py RUN...     # per-map table of arena runs in matches\arena
.venv\Scripts\python.exe tools\release.py --src v13 --verify            # build + verify the upload ZIP
.venv\Scripts\python.exe -I research\2026-10-25\tools\games30.py replays\platform\match-group-*.zip   # platform games on 3.0
.venv\Scripts\python.exe tools\replay_decode.py FILE... [--buys]        # any replay: per-team tributes, deaths, buys, wards
```

On Mac/Linux use `.venv/bin/python` and `.venv/bin/cambc`. **Testing standard on the 40 maps:** seeds 1,2 = 160 games; adopt at ~88/160 with positive gems (one seed set of 80 moves by about ±5 games from noise alone); screen with one seed, confirm with the other. Don't edit `bots\` while a queue runs (the commit column in `gauntlet.csv` turns `+dirty`), and don't `git pull --rebase` while a queue is writing `gauntlet.csv` (stash or commit first). Platform downloads go in `replays\platform\` (not in git). `tools/repro_check.py`'s reference is from 2.2.5 and needs regenerating on 3.0.5 (`--write`, on a quiet machine).

Nothing is queued or running.

## Paused 2026-10-18 ~16:30 (superseded by the evening sprint above; kept for the agent briefs)

Since the v7 release: upgraded to **cambc 2.2.5** (platform replays are now format 3; game play is identical to 2.2.2). Analysed v7's 25 platform games: **11/25 wins**, the early gold gap mostly closed, 3-pick maps 2/7, and 80% of our deaths are to champions in small fights (DEVLOG rows 110–119). New flags in `mybot`, all off and all neutral vs v7 so far:
- `CAST_FIRST`: ranged champions cast before their basic attack, fixing Tavi's skipped stun (30/68, +644).
- `ALLY_RANGE` / `LOW_HP_RETREAT` / `LOW_HP_REACH`: worse.
- The bug-fix package `IGNORE_SPAWN_CAMPERS` + `CAMP_TILE_FIX`: 32/68, +828, economy 12,118 vs v7's ~13,300–14,200. This is a candidate to include as insurance; it's the user's call.

**Resume plan:** relaunch three agents in git worktrees (briefs below), run their flags through 68-game gauntlets vs v7 one at a time, merge winners, freeze v8, release. Each agent runs tools with the main repo's venv (`export PATH="/c/Users/james/GitHub/Cambridge-Battlecode/.venv/Scripts:$PATH"`, python at `.venv/Scripts/python.exe`), keeps smoke tests to ≤16 games with `--jobs 3`, never runs `gauntlet.py`, puts every change behind an off-by-default flag, and commits on its own branch.
1. **Fights:** cut deaths to enemy champions (80% of deaths; 72% with an ally within 6 tiles; 49% to one attacker). Pros stack stuns (Cassi, Ren, Tavi, Prism) and Stellar burst; our Lanchester ratio ignores stuns. Varg's shield is cast 0.10 per basic attack vs pros' 0.18. Test vs `v7` and `meta`; measure deaths with `tools/replay_decode.py`.
2. **Pro composition:** make Cassi & Issac drafts beat v7, starting on 3-pick maps. Suspected blocker: squad sizing (`NEED_FRAC`) makes weak champions wait for partners even for one wolf, while pros farm with them solo.
3. **Economy:** measure where turns go (DEBUG `ACTS` lines vs `idle`) and cut the biggest waste; the target is rounds-to-1000 per map with no head-to-head loss.

## What to do next

0. **After the competition:** download the platform games and check deaths with `tools/replay_decode.py`. v10 halved our deaths against v8 locally (283 vs 552), so see whether that holds against real teams. The fight path still never calls `support()` for heals (we draft no healer), and FIGHT_MEMO 2 is a candidate that needs more seeds (it is neutral-to-positive head-to-head and worse vs v8 on seed 3).

1. **Fights against stun-heavy teams.** 79% of our platform deaths are to champions. Pros stack stuns (Cassi, Ren, Tavi, Prism) and Stellar burst; our fight ratio (HP × damage) ignores stuns. Likely gains: more caution against stun-heavy enemy drafts, and banking gems before contested areas. Testing against v7 alone won't show this, so first build an opponent that fights like the pros (focus up, stun then burst).
2. **Play ability champions properly.** Ranged champions with damaging abilities should stand at range 4 (camps hit at 3) and cast; build focus. That's what the pros' Power F builds suggest. Then re-test the pro draft (Cassi & Issac, Stellar, Ren), which brings an extra champion.
3. **Map-specific fixes** (`IGNORE_SPAWN_CAMPERS`, `CAMP_TILE_FIX`, `MONOLITH_POKE`): decide whether to adopt as insurance, or measure them on their own maps with many seeds.
4. **Wards** add +70 gems a game on average without extra wins. They may pay off against pros, where vision of bushes matters more than against v6.
5. **After submitting v7:** download our new platform games into `replays\platform\`, then run `tools\platform_report.py` and `tools\replay_decode.py` to see whether early gold closed the item gap.
