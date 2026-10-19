# How to win more platform games: research report (2026-10-19)

Scope: research only. No competition bot (`bots/mybot`, `bots/v*`) was changed and nothing was submitted. Every probe is a throwaway copy under `bots/rs_*` (git-ignored), built by the scripts in [`tools/`](tools/) from a committed bot plus a recorded patch. Commands are in the appendix.

## 0. Read this first: the baseline is v10, not v8

The brief described v8 (DEVLOG rows 1–119) as the current bot. The unmerged branch `claude/adoring-fermat-jthwy1` (2026-10-18 evening) goes further. It froze v9–v11, picked **v10 = v8 + `FIGHT_SHIELD` + `WARDS` + `CAST_FIRST`** as the competition submission, and logged DEVLOG rows 120–134. v10 beat v8 55/68 (+13,016) and halved local deaths. All 30 of our platform games you uploaded are v10: they have our draft and place wards, which v7/v8 never did. This report therefore uses v10 as the baseline (copied into `bots/rs_v10` from that branch). It doesn't re-propose anything in rows 120–134 (`FIGHT_SHIELD`, `WARDS`, `CAST_FIRST`, `FIGHT_MEMO` 2/3, `RECALL_SAFE`, `CC_FIRST`, tribute 20/10, `FIGHT_GEM_EXTRA` 0.5, `FIGHT_ENGAGE` 1.1, `ALLY_RANGE` 5, `NEED_FRAC` 0.7, `SHOP_GOLD` 200 alone). **Merge that branch into `main`**: today `main` has no v9–v11, so anyone starting from `main` repeats the sprint.

## 1. Summary

**The platform verdict on v10: 13/30 wins (43%), no better than v7 (11/25, 44%).** v10's large local gains didn't transfer (section 6). The 30 v10 games and 20 pro-vs-pro games show where the gap is:

- **Economy, not fights.** Deaths are now even: we die 0.73 times per 100 rounds and our opponents 0.79. Contested pros finish faster than v10 does with no opponent on about half the maps. Examples: rows 350 vs 487 rounds, stampede ~500 vs 1,038, expanse 527 vs 794, interlock 508–574 vs 653.
- **We hoard gold.** Our income matches the pros', but ~400 gold per team sits unspent at any time, because champions only shop when below 75% health. This alone makes v10 score **0 gems on contest** against a passive opponent.
- **Boss maps** (contest, stampede, rows, monolith; 4 of 17 maps): **we're 1/7.** Pros farm the boss groups with ability casts from exactly 4 tiles. Our `MONOLITH_POKE` (off) has a bug that freezes pokers once the nearest camps die.
- **4-pick maps: 2/9.** It's our only all-melee draft (Vendetta, Varg, Ryth, Marcella).
- **Pros farm in packs** (3+ champions on one group for 76% of camp hits in rounds 0–99, versus 16% for us), draft Cassi & Issac for an extra body, and cast at camps twice as often.

**Local probes vs v10** (seeded, all 17 maps from both sides unless noted; adoption bar 40/68 with positive gems; one 68-game set moves by about ±4 wins from noise alone):

| Probe | vs v10 | Unopposed rounds to 1,000 (sum of 17 maps; v10 = 11,856) |
|---|---|---|
| Shop at ≥150 gold at any health | **42/68, +6,046** (20/34, 22/34); seeds 3,4: 37/68, +2,126 (21/34, 16/34) → **79/136, +8,172** | 10,696 (contest 2,000 → 941) |
| + poke fix (`rs_best`) | **43/68, +4,766** (21/34, 22/34); stampede 4/4, contest 0/4 | 10,629 (stampede 1,038 → 841) |
| 4-pick Vendetta, Varg, Ryth, **Tavi** (4-pick maps, seeds 1–8) | **41/64, +9,198** (every seed set 5/8 or 6/8, all gem-positive) | — |
| Pro-style proxy: pro draft + packs until r150 + poke fix + shopping (`rs_proxy`) | **45/68, +7,584** (22/34, 23/34) | **10,159** (stampede 624, contest 862) |
| Candidate: shopping + poke fix + Tavi 4-pick (`rs_cand`) | **41/68, +4,506** (19/34, 22/34); **vs the proxy 24/68, −6,008** | — |
| Packs until r150 only | 33/68, +1,422 (neutral) | 11,880 (−4% excluding contest) |
| 4-pick with Cassi & Issac / with Tavi for Varg | 17/32, +356 / 14/32, −1,686 | — |

### Ranked recommendations

| # | Change | Why | Confidence |
|---|---|---|---|
| 1 | **Shop whenever carrying ≥150 gold, at any health** (`SHOP_HP` 1.01, `SHOP_GOLD` 150; two existing constants) | Same income as the pros, ~400 gold idle; contest 0 → win; 79/136, +8,172 vs v10 over seeds 1–4 | Medium–high: strong mechanism, borderline self-play confirmation (run seeds 5–8 as for `gt1`) |
| 2 | **4-pick draft: Tavi instead of Marcella** | Platform 2/9 (v6 1/4); 41/64, +9,198 locally on the 4-pick maps, every seed set positive | **High** |
| 3 | **Fix the poke ring, turn boss poking on, and add a capture step** (ring from live camps; aim area casts at the densest tile; when the boss is low or enemies come near, go in and hold its tiles) | 1/7 on boss maps; pros poke from exactly 4; stampede 4/4 vs v10. Without the capture step v10 steals the poked monoliths (contest 0/4), as an opponent did on the platform | High for the bug and stampede; contest needs the capture step |
| 4 | **Move towards the pro style: pro draft (Cassi & Issac, Stellar, Ren, then Ryth, then Varg) + early packs, on top of #1 and #3; use it as the new sparring partner** | The strongest local configuration measured: the proxy beats v10 45/68 (+7,584) **and** the our-draft candidate 44/68 (+6,008). It matches the platform pros' draft and grouping. Weak spot: fights on small contested maps (fragment, pilgrimage), where it dies 2–3× as often | Medium: strongest local evidence, but local wins have failed to transfer before. Settle it with a platform A/B |
| 5 | **Fights: stop chasing single enemies into their team; retreat towards allies** | 40–48% of local contact deaths follow a chase; in 2/3 of those, more enemies appeared | Medium (deaths are no longer the main gap) |
| 6 | **Early pack farming** as an option to re-test against the proxy | Pros pack; neutral vs v10 | Low–medium |
| 7 | Smaller items: react to unseen damage, cap respawn idling, fuel headroom on ambush, value Cassi & Issac as one kill | Section 5 | — |

**Suggested order:**
1. Merge the sprint branch.
2. Adopt #2 now: a one-line draft change, and the most consistent result.
3. Adopt #1 once seeds 5–8 confirm it. It's at 79/136, the same position as `gt1` at DEVLOG 106.
4. Add #3 with the capture step.
5. Then run a **platform A/B**, one day each:
   - **v12** = v10 + #1 + #2 + #3 (our draft; locally 41/68 vs v10 without the capture step).
   - **v13** = v12's fixes + #4's pro draft and early packs (the proxy: 45/68 vs v10, 44/68 vs the v12-like candidate).
   Compare per map class with this report's scripts.
6. Make the proxy the second gauntlet opponent before tuning further.

## 2. Platform evidence (30 v10 games + 20 pro-vs-pro games, 2026-10-18)

Data: six match groups of our games (g4, g6–g10: 30 games with our stdout and fuel) and four of other teams' games (g1–g3, g5: 20 games, mostly pro-meta drafts). The replays were read in memory only. Before relying on it, the decoder's turn attribution for 6-champion teams was checked against the instrumentation log of a local 6v6 game: 8,534 turns agree, 0 disagree. `replay_decode.py`'s inferred deaths are unreliable for some pro teams (101 deaths in 532 rounds for 6 champions is impossible with a 60-round respawn; some bots start and cancel a recall every turn). So deaths here use a stricter rule: 55+ rounds with no move, attack or cast, then activity again. It agrees with the local death logs.

### 2.1 Results by map

| Map | Picks | Boss gems | Our results (final gems us-them, round) |
|---|---|---|---|
| ambush | 5 |  | L 606-986 (r706); L 640-956 (r701) |
| collision | 3 |  | L 352-968 (r824); W 948-564 (r1053) |
| contest | 5 | yes | L 400-600 (r2000); W 800-0 (r1371); L 200-800 (r2000) |
| corners | 5 |  | L 306-908 (r486); W 990-538 (r663) |
| eight | 5 |  | W 744-534 (r707) |
| elkring | 5 |  | W 954-756 (r615); W 972-468 (r557) |
| expanse | 3 |  | W 988-600 (r834) |
| fragment | 3 |  | W 996-658 (r1060) |
| interlock | 4 |  | L 840-938 (r977); L 430-870 (r694); L 668-812 (r672) |
| lanes | 5 |  | L 904-986 (r550) |
| monolith | 5 | yes | L 490-966 (r467); L 556-988 (r484) |
| packs | 3 |  | W 984-452 (r555); W 932-544 (r641) |
| pilgrimage | 5 |  | W 960-612 (r1087) |
| rows | 4 | yes | L 594-990 (r352) |
| rushbait-v2 | 4 |  | L 886-986 (r1001); L 658-972 (r683); W 894-634 (r1024) |
| stampede | 5 | yes | L 360-720 (r1299) |
| swirl | 4 |  | W 956-556 (r943); L 284-970 (r589) |

- By pick count: **3-pick 5/6, 4-pick 2/9, 5-pick 6/15.** Boss maps 1/7.
- By opponent: against pro-meta drafts (Cassi & Issac + Stellar) **6/17**; against everything else 7/13.
- Even our wins are slow (r555–1,087). Opponents who beat us reach 1,000 by r352–700.

### 2.2 Where the gap is: rounds 1–300, per team

| | Bodies | Camp hits per 100 rounds | Camp casts per 100 rounds | Gold spent by r150 | Gold spent by r300 | Deaths per 100 rounds |
|---|---|---|---|---|---|---|
| Pros (in pro-vs-pro games, so contested) | 5.30 | 112 | **17** | **816** | **1,865** | 0.28 |
| v10 local, unopposed | 4.29 | 114 | 8 | 480 | 1,411 | — |
| v10 on the platform | 4.35 | 89 | 6 | 390 | 1,153 | 0.73 |
| Our platform opponents | 4.90 | 93 | 11 | 472 | 1,280 | 0.79 |

- **Finish rounds, pros contested vs v10 unopposed:** rows 350/351 vs 487; monolith 453 vs 544; stampede 475/517 vs 1,038; interlock 508/574 vs 653; rushbait-v2 545/570 vs 660; fragment 516 vs 599; pilgrimage 573 vs 678; expanse 527 vs 794. About equal on elkring, packs, eight and corners.
- **Raw camp damage isn't the gap.** Estimated from base stats, items bought and ability modifiers (area and splash extra targets not counted), v10 unopposed deals ~9,850 single-target camp damage per 100 rounds, contested pros ~8,600. Pros get more gems per damage from more bodies, boss poking and area hits on clustered camps.
- **Turn use is similar.** Share of champion-turns that hit a camp: us 16.8%, our opponents 16.6%, pros 19.6%. Casting per basic attack is now also similar (v10's Tavi and Marcella 0.19, pros' ranged champions 0.18–0.24), because `CAST_FIRST` fixed Tavi.
- **Openings are similar** (median first camp hit r6 vs r10, first item r60 vs r62, first tribute r62 vs r72). The gap opens after round ~150.

### 2.3 Gold: same income, slower spending

Measured locally on v10 vs idle (instrumented copy that logs carried gold), compared with the pros' spending from replays:

| | Earned by r150 | Spent by r150 | Unspent at r150 | Earned by r300 | Spent by r300 |
|---|---|---|---|---|---|
| v10, unopposed | ~873 | 480 | 393 | ~1,900 | 1,423 |
| v10 vs v10 | ~688 | 383 | 305 | ~1,413 | 1,064 |
| Pros (spent only) | | 816 | | | 1,865 |

- 35% of alive champion-turns carry ≥150 unspent gold (19% carry ≥300). Tavi, who shops remotely, is the exception at 0%.
- Cause: `maybe_recall()` shops only with ≥300 gold **and** below 75% health (`SHOP_HP`). A champion farming damage-free camps never meets that condition.
- **Contest exposes it completely.** Its only gems are two monoliths, which the team can only kill once it has bought items. v10 vs idle scored **0 gems in 2,000 rounds**; Vendetta was carrying 1,738 gold at its base 800 HP at round 1,000. v8 scored 800 only because Ryth happened to get hurt, recalled and bought, which unlocked the monolith. v10's `CAST_FIRST` + `WARDS` changed that luck. On the platform, contest went 1/3, with our gems flat at 0 for 400+ rounds in every game.

### 2.4 Boss maps

- **Four maps lock most of their gems in strong groups:** contest (two lone monoliths, 100% of gems), stampede (one group of 6 elks + 6 gem clusters, 100%), rows (Monolith-Monolith + 2 gem clusters, 448 gems, 53%), monolith (two monolith + 8 gem-cluster groups, 392 gems each, 63%).
- **Pros cast at them from exactly 4 tiles.** On stampede 74 of ~80 located hits were casts at distance 4, by Ren, Cassi, Prism, Tavi and Issac. On rows, Stellar and Prism poked the central monoliths from 4 tiles over rounds 158–302.
- **We hit them late or at a cost.** On stampede our first hit on the elk group was round 773; the opponent started at 209 and won 720–360. On contest we tank the monoliths with basic attacks (200 damage per hit). In one game the opponent captured 600 gems without hitting a boss once, so it captured what we killed.
- **`MONOLITH_POKE` (off) has a freeze bug.** The poke ring is computed once from all of the group's cells, dead or alive. On stampede, Tavi killed the gem cluster 4 tiles from its ring tile; the next live camp was 5 away. Its tile still counted as "on the ring", so `go()` refused to move and Tavi stood there for hundreds of turns. In 2,644 poke turns the team cast 54 times, where cooldowns allowed about 8× more. This explains why `MONOLITH_POKE` tested neutral and made stampede slower.

### 2.5 Pros farm in packs

Share of camp hits by how many teammates hit the same group in the same 10-round window:

| | Solo | Pair | 3+ |
|---|---|---|---|
| Pros, rounds 0–99 | 11% | 13% | **76%** |
| Pros, rounds 200–299 | 21% | 32% | 47% |
| Pros, all rounds | 19% | 24% | 57% |
| v10 unopposed | 62% | 29% | 9% |
| v10 platform | 67% | 25% | 8% |

- Pros' mean number of teammates within 4 tiles (rounds 50–400): 1.1–2.2 on most maps; v10: 0.2–0.7. Pros pack hardest on small maps (corners, eight, elkring, fragment, rows: 72–80% of hits by 3+) and least on big ones (expanse 22%, stampede 25%). Even single wolves get 3–4 pro champions.
- **Drafts:** 3 picks Cassi & Issac + Ren + Stellar; 4 picks + Ryth; 5 picks + Varg. Cassi & Issac are not paired (median 7 tiles apart).
- **Deaths:** pros vs pros die only 0.28 times per 100 rounds per team; games against us run at about 0.75 on both sides. Pros mostly avoid fighting each other. Against us, deaths are even; in our losses we die a little more (58 vs 48 by round 500 over 17 losses).

## 3. Local measurements (v8 and v10, instrumented copies)

The instrumented copies print one line per champion turn (activity, hit/cast/move, health, gems, gold) plus fight snapshots and deaths. They play identical games to the plain bots on 3 of 4 test maps; on lanes, where fuel is at the cap, the extra printing shifts timing.

### 3.1 Where the turns go

| Share of champion-turns | v10 vs idle (16 maps, contest excluded) | v10 vs v11 (34 games) | Pros (platform replays) |
|---|---|---|---|
| Moving | 54% | 56% | 49% |
| Hitting camps | 20% | 13% | 20% |
| Hitting champions | 0% | 2.5% | 2.5% |
| No action (capturing, channelling, waiting, dead) | 21% | 24% | 24% |

- **Unopposed** (v8 activity labels): walking to targets 34%, walking to altars 8%, standing at a respawning target 7.8%, waiting for a squad 4.7%, capturing 5.7%, recall and walk home 6.3%.
- **Contested** (v8 vs v7): dead 11.7% of champion-turns, fight mode 12.3% (only ~2.6% of all turns deal damage in fights; most fight turns are walking, i.e. retreats and chases).
- **Respawn idling:** scoring lets a champion walk to a group that respawns within 25 rounds and stand there, in 26-round streaks. That's 7.8% of turns unopposed, concentrated on sparse maps (contest, stampede, pilgrimage).

### 3.2 Fight-ratio calibration

The fight ratio is

$$\text{ratio}=\frac{\sum_{\text{us}} HP \cdot \sum_{\text{us}} DPS}{\sum_{\text{them}} HP \cdot \sum_{\text{them}} DPS}$$

with home/away modifiers. Each champion's fight snapshots were grouped into engagements, and the ratio at contact (first snapshot with an enemy within 4 tiles) compared with the outcome over the next 6 rounds.

| Ratio at contact | v10 vs v11: died | killed | v10 vs meta: died | killed |
|---|---|---|---|---|
| < 0.5 | 26% | 18% | 24% | 23% |
| 0.5–0.9 | 12% | 17% | 18% | 38% |
| 0.9–1.3 | 21% | 26% | 3% | 41% |
| 1.3–2 | 21% | 31% | 9% | 50% |
| 2–4 | 19% | 33% | 11% | 54% |
| > 4 | 10% | 47% | 8% | 69% |

- The ratio predicts at contact (death rate falls and kill rate rises with it), but champions still die 10–21% of the time at ratios the model rates as favourable.
- **What happened at contact, for engagements where we died:** v10 vs v11: chase 73, retreat 67, hold 11, other 32; v10 vs meta: chase 45, retreat 34, other 14.
- **Chase deaths:** 50 of 73 chased a single visible enemy, and in 47 of 73 more enemies appeared during the chase. Vendetta accounts for 31 (her dash makes her the main chaser). The ratio counts only visible enemies, although the draft tells us exactly how many the enemy has.
- **Retreat deaths:** 39 of 67 had no ally within 7 tiles and were caught by the same enemies (49 of 67). The retreat heads for spawn, not towards allies, and never fights back when it can't escape. Pursuers walk at the same speed and stun or deal damage from 4 tiles.
- v10 vs meta: 28/34, with deaths 110 against meta's 476 (Cassi & Issac died together 108 times). `meta` is much weaker than the real pros.

### 3.3 Damage from unseen attackers

- HP lost while no enemy is visible, outside camp fights: 2–3% of all HP lost in contested games, versus 0.4% unopposed (the camp-only baseline). It's concentrated on swirl and contest.
- Traces show champions standing still in farm mode losing ~95 HP a turn for 9 turns before recalling too late. `fight()` needs a visible enemy, so the bot never reacts to damage it can't see.

## 4. Recommendations in detail

### 4.1 Spend gold as it comes in (rank 1)

- **Change:** `SHOP_HP = 1.01` and `SHOP_GOLD = 150`. Both constants already exist, so this is two constants and no new code. The trigger is in `maybe_recall()`: `shop = not remote_shop and gems == 0 and gold >= SHOP_GOLD and frac < SHOP_HP`.
- **Evidence:** sections 2.2–2.3; contest goes from 0 gems to a win at round 941 unopposed.
- **Probe `rs_shop150` (v10 + the two constants):**
  - Unopposed: 10,696 rounds summed over 17 maps vs v10's 11,856. Contest 2,000 → 941; the other 16 maps 9,856 → 9,755.
  - **vs v10, seeds 1,2: 42/68, +6,046** (20/34 +3,336; 22/34 +2,710). **Seeds 3,4: 37/68, +2,126** (21/34 +2,400; 16/34 −274). **Seeds 1–4: 79/136 (58%), +8,172.** Seeds 5–8 should decide it, as they did for `gt1`.
- **Possible refinements, not tested:**
  - Shop on any spawn visit, which recall travel already makes.
  - Let champions carrying gems shop when spawn is on the way to an altar (today `gems == 0` is required).
  - Buy while dead (already done).
- **Risk:** more recall trips. The 150 threshold is one emblem's worth (5 × 30). The head-to-head says the trips pay for themselves.

### 4.2 Fix the poke ring and turn boss poking on (rank 3)

- **Bug:** `poke_ring()` caches tiles 4 from *any* cell of the group, dead camps included, and `go()` returns without moving when the champion already stands on a root tile. A poker whose nearest camps have died stands still forever (traced on stampede).
- **Fix (probe `rs_poke2`, in `poke_group()`):**
  - Rebuild the ring each turn from the visible live camps: within 4 of a live camp, outside every live camp's 3-tile reach, minus the current tile.
  - Aim area casts at the in-range tile covering the most live camps, not at the lowest-HP camp.
  - Turn `MONOLITH_POKE` on.
- **Unopposed result (rounds to 1,000):**

| | stampede | contest | other maps |
|---|---|---|---|
| v10 | 1,038 | 2,000 | — |
| old `MONOLITH_POKE` | 1,316 | 1,555 | — |
| `rs_poke2` | 969 | 1,555 | unchanged |
| `rs_poke2` + shopping | **841** | **972** | — |

- **Combined head-to-head:** `rs_best` (poke fix + shopping) vs v10: **43/68, +4,766** (21/34, 22/34). Stampede 4/4, but **contest 0/4**, where shopping alone was 2/4. The cause is a stolen capture: as our pokes drain the monolith, v10's squad-size estimate falls until its 5 champions walk in, finish it and capture, while our pokers stand 4 tiles out off the capture tiles. An opponent did the same to us on the platform (600 contest gems with no boss hits). **Boss poking needs a closing step:** once the boss's HP is low enough for the champions present to finish it, or enemies come within ~8 tiles, the pokers go in and occupy the group's tiles to capture or contest.
- **Not solved:** rows and monolith. Their poke cost per gem is too high for our casters (Ryth, Marcella, Tavi), so the bot never chooses to poke there. See 4.4.
- **Also worth doing:**
  - Count area damage × coverage in the poke cost. The probe that did this (`rs_aoe`) broke swirl through a target-need state bug, so that change needs care.
  - Start boss poking early: the pros begin around round 40–200, we began at round 773.

### 4.3 4-pick draft: Tavi instead of Marcella (rank 2)

- **Evidence:** platform 2/9 on 4-pick maps with Vendetta, Varg, Ryth, Marcella. That's the only draft of ours without Tavi, who never hoards gold and gives ranged poke. v6 was 1/4 there.
- **Local, on the four 4-pick maps vs v10, seeds 1–4 (32 games each):**

| 4-pick draft | Result |
|---|---|
| Vendetta, Varg, Ryth, **Tavi** | **20/32, +3,430** (5/8 on every seed set, gems positive on all four) |
| Vendetta, Varg, Ryth, **Cassi & Issac** | 17/32, +356 |
| Vendetta, Ryth, **Tavi, Marcella** (Varg out) | 14/32, −1,686 |

- **Seeds 5–8 confirmation: 21/32, +5,768** (5, 5, 5, 6 of 8). Seeds 1–8 together: **41/64 (64%), +9,198**. Interlock 12/16, swirl 13/16, rows 8/16, rushbait-v2 8/16.
- **Change:** `draft.py` `BY_SIZE[4] = (VENDETTA, VARG, RYTH, TAVI)`.
- **Risk:** low. The other draft sizes are untouched.

### 4.4 Draft for boss maps (part of rank 4)

- **Idea:** the draft phase sees the whole map, with 10× fuel on the first draft turn. When more than about half of the map's gems sit in groups too strong to fight (rows, monolith, contest, stampede), pick Stellar and/or Prism. Their area abilities hit up to 9 camps of a 3×3 block per cast from 4 tiles.
- **Evidence:** pros poke rows' Monolith-Monolith group with Stellar + Prism; with our casters the poke never pays.
- **Change:** a `draft.py` rule keyed on the share of gems in strong groups, plus the poke fix (4.2).
- **Test:** unopposed and vs v10 on the four boss maps (seeds 1–8), then the platform.

### 4.5 Towards the pro style: draft and early packs (rank 4)

- **Probe `rs_proxy`:** v10 + pro draft by size (3: Cassi & Issac, Stellar, Ren; 4: + Ryth; 5: + Varg) + packs until round 150 + poke fix + shopping.
- **Unopposed: the fastest variant tested.** 10,159 rounds summed (v10 11,856). Stampede 624 against the pros' contested ~500; contest 862; expanse 691; rushbait-v2 623.
- **vs v10: 45/68, +7,584** (22/34, 23/34).
  - 4/4 on ambush, eight, expanse, packs, rows, rushbait-v2 and stampede.
  - 0/4 on fragment and pilgrimage; 1/4 on contest, lanes and monolith.
  - `rs_best` (our draft, same fixes) did better on fragment, pilgrimage, monolith and interlock.
  - **Why it loses fragment and pilgrimage:** fights. On fragment the proxy died 20–27 times per game against v10's 9–14; on pilgrimage 10–16 against 6–8. With our fight code the pro draft's fragile bodies get picked off on small contested maps: Cassi & Issac die as a pair, and Stellar and Cassi have 700–750 HP. Where fights are rare (rows, rushbait-v2: 0–6 deaths a side) its economy wins. So the pro draft needs better fight play (4.6, and the Cassi & Issac targeting note in 5) before it can be used everywhere.
- **Two uses:**
  1. As the second gauntlet opponent (section 6).
  2. As evidence for a **map-aware draft**: pro draft on rows, rushbait-v2, eight, packs and expanse; our draft on fragment, pilgrimage, monolith and interlock. Re-test with more seeds before trusting per-map splits from 4 games each.
- **The conservative candidate `rs_cand`** (our draft + shopping + poke fix + Tavi 4-pick) vs the proxy: **24/68, −6,008**. The candidate wins only fragment and monolith (4/4 each) and loses eight, packs and rows 0/4. vs v10 it is 41/68 (+4,506), within noise of `rs_best`.
- Confirmation (proxy vs v10, seeds 3,4) and a no-packs ablation (pro draft + fixes without packs, vs the proxy): PENDING.

### 4.6 Fights: stop chasing into the enemy team (rank 5)

- **Evidence:** section 3.2.
- **Changes to try, behind flags:**
  - **Phantom enemies.** When fewer enemies are visible than the enemy roster (known from the draft), and the enemy we chase is moving towards where we last saw its teammates, or towards their side, add the missing enemies' average strength to their side of the chase decision only. Retreat stays as now.
  - **Chase leash.** Don't chase more than ~4 tiles beyond the contact point, or past our own allies' support range, unless the target dies within 2 turns of burst.
  - **Retreat towards allies.** When an ally is within 8 tiles and closer than spawn, retreat to them. When pursuers are as fast as us (melee with dash, or stuns at range 4) and we're far from spawn, fight back instead of fleeing.
- **Test:** vs v10 and vs `rs_proxy`; measure chase deaths with `tools/chase.py`.
- **Expected gain is modest:** platform deaths are already even (0.73 vs 0.79 per 100 rounds).

### 4.7 Early pack farming (rank 6)

- **Probe `rs_pack150`:** before round 150 every champion takes the group claimed by the lowest-slot ally, and scoring ignores claims.
- **Result:** 73% of early hits by 3+ teammates (pros 76%). Unopposed 4% slower; **vs v10 33/68, +1,422 (neutral).**
- It may matter against pro packs, which self-play can't show. Keep it as a component of `rs_proxy` and re-test it against the proxy.

## 5. Smaller findings and ideas

- **Unseen attackers (bushes).** 2–3% of HP lost; swirl and contest. When health drops for two turns with no visible enemy and no awake camp in range, step away from the nearest bush tiles, or put the ward on the nearest bush within 2 (wards are already on in v10). Cheap; test on swirl and contest.
- **Respawn idling.** Scoring allows walking to a group that respawns within 25 rounds and standing there (`wait > 25: continue` in `score_groups`). That's 7.8% of unopposed turns, mostly contest, stampede and pilgrimage. Try a cap of ~10 rounds, or farm something within ~6 tiles while waiting.
- **Fuel headroom.** On ambush, 120–193 turns a game exceed 2.0M fuel and the peak was 2.496M against the 2.5M cap. Every champion's first turn hits the 5M cap (lanes, ambush; earlier also corners and swirl). Any heavier per-turn logic (fight look-ahead, route planning) must first get cheaper on big maps. This is where the "bitmaps" (bitboard) suggestion fits: whole-map bit operations for danger zones, reach and vision. The bot already uses the SDK's `Bitboard`/`DistanceField`, so the gain would be fuel headroom for new logic, not wins by itself. Draft-phase precomputation passed through the 1,024-byte draft memory could also move first-turn set-up out of the 5M turn.
- **Cassi & Issac are one kill.** Opponents draft them 94% of the time; killing either kills both and drops both bags. `fight()`'s target value treats them as two champions; give each the pair's value (both bags, two bodies). Untested.
- **`submit failed Champion cannot act`.** These lines in 4 platform games are stunned champions trying to tribute. Harmless.
- **Not analysed this session:** teleport crystals and dashes over holes as map shortcuts; turn priority (`set_priority`); Ren's retaliation against camps.


## 6. Why local wins didn't transfer, and what to test against instead

- **v10 beat v8 55/68 and `meta` 33/34 locally, yet its platform record (13/30) matches v7's (11/25).** Its local gains came from fights against our own lineage. On the platform, deaths were never the main gap once v7's early-gold fix landed, and v10's fight fixes left the economy gap untouched.
- **Our local opponents share our blind spots.** They hoard gold, don't poke bosses, farm solo, and draft without Cassi & Issac (except `meta`, which plays them with v6 logic and loses 28/34).
- **A gain that only matters against pro-style play can't show up in self-play.** DEVLOG row 95 already said this for map-specific fixes; it's true for style changes too. Pack farming is neutral against v10 (33/68) but may matter against packs.

**Proposal:**
1. **Keep the 68-game gauntlet vs the frozen baseline** as a no-regression check. Positive gems and no worse than ~32/68 counts as a pass.
2. **Add a pro-style opponent built from our own code:** `rs_proxy` = v10 + pro draft by size (Cassi & Issac, Stellar, Ren, then Ryth, then Varg) + packs until round 150 + fixed boss poke + prompt shopping. It already beats v10 45/68 (+7,584), so it is a stronger sparring partner than v10 or `meta`. Treat a variant's score against it as the main signal. As each pro behaviour is understood better, add it to the proxy.
3. **Use the platform as the final judge per map class** (boss maps, 4-pick maps), and keep this report's scripts as the standard analysis. `ourgames.py` gives results and gem curves, `teamstats.py` / `damage.py` the economy, `boss.py` boss handling, `cofarm2.py` grouping, `deaths2.py` deaths.
4. Keep each submission for a full day of platform games, so the 25–30 games are comparable.

## 7. "Settled" items reopened, and why

| DEVLOG verdict | New reason | Status |
|---|---|---|
| `sh1` "shop at 150 gold at any health": neutral (33/68 vs v6) | Platform: same income as pros but ~400 gold idle; the contest 0-gem failure in v10 | **79/136, +8,172 vs v10** (seeds 1–4) |
| `MONOLITH_POKE`: neutral, "clashes with `CAMP_TILE_FIX`" (rows 89–92) | Freeze bug in the cached poke ring; platform 1/7 on boss maps; pros poke at distance 4 | Fixed in the probe: stampede 1,038 → 841 unopposed (with shopping); with shopping vs v10 **43/68**; needs a capture step on contest |
| "Spread out; pairs and squads lose" (rows 22–23) | Pros farm in packs (76% of early hits by 3+). The old test forced `MIN_SQUAD` through the wait-for-squad logic, on the old engine and maps, against v4 | Early packs neutral vs v10 (33/68), −4% unopposed. Not adopted; test against the proxy |
| "Marcella 4th" (rows 52–53, old engine, self-play) | 4-pick maps 2/9 (v10) and 1/4 (v6) on the platform; the only draft without Tavi | **Tavi 4th: 41/64, +9,198 vs v10** on the 4-pick maps (seeds 1–8) |
| "The pro draft and Cassi & Issac lose with our logic" (rows 87, 103, 115) | Those tests had no shopping or poke fix, and v6/v7 fight code | **Pro-style proxy 45/68, +7,584 vs v10** (pro draft + packs + poke fix + shopping). Cassi & Issac alone as the 4th pick: 17/32 |

## Appendix: how to reproduce

All tools are in [`tools/`](tools/). Outputs go to `matches/research/` (git-ignored), or to `$RS_WORK` if set. Probes are built from committed bots plus the patch scripts, so a variant is defined by its source bot plus the command.

```
# v10/v11 live on branch claude/adoring-fermat-jthwy1 until it is merged; copy them as throwaway bots:
for v in v10 v11; do mkdir -p bots/rs_$v/src; for f in bot.py world.py draft.py main.py; do
  git show origin/claude/adoring-fermat-jthwy1:bots/$v/src/$f > bots/rs_$v/src/$f; done; done
T=research/2026-10-19/tools; PY=.venv/bin/python
$PY $T/instrument.py rs_v10 rs_v10i                     # printing-only instrumentation (I T / I F / I D lines)
$PY $T/instrument.py rs_v10 rs_shop150 --set "bot.py:SHOP_HP = 0.75=>SHOP_HP = 1.01" --set "bot.py:SHOP_GOLD = 300=>SHOP_GOLD = 150"
$PY $T/mkpoke2.py rs_v10 rs_poke2                       # poke-ring fix + area aim, MONOLITH_POKE on
$PY $T/mkpack.py rs_v10 rs_pack150 150                  # early pack farming
$PY $T/mkproxy.py rs_v10 rs_best --poke --set "bot.py:SHOP_HP = 0.75=>SHOP_HP = 1.01" --set "bot.py:SHOP_GOLD = 300=>SHOP_GOLD = 150"
$PY $T/mkproxy.py rs_v10 rs_proxy --pack 150 --poke --set "bot.py:SHOP_HP = 0.75=>SHOP_HP = 1.01" \
    --set "bot.py:SHOP_GOLD = 300=>SHOP_GOLD = 150" \
    --set "draft.py:BY_SIZE = {3: (CD.VENDETTA, CD.RYTH, CD.TAVI)}=>BY_SIZE = {3: (CD.CASSI_AND_ISSAC, CD.STELLAR, CD.REN), 4: (CD.CASSI_AND_ISSAC, CD.STELLAR, CD.REN, CD.RYTH), 5: (CD.CASSI_AND_ISSAC, CD.STELLAR, CD.REN, CD.RYTH, CD.VARG)}"
$PY $T/instrument.py rs_v10 rs_d4t --set "draft.py:BY_SIZE = {3: (CD.VENDETTA, CD.RYTH, CD.TAVI)}=>BY_SIZE = {3: (CD.VENDETTA, CD.RYTH, CD.TAVI), 4: (CD.VENDETTA, CD.VARG, CD.RYTH, CD.TAVI)}"
$PY $T/runner.py econ_X rs_X idle --one-side            # unopposed economy, 17 maps
$PY $T/h2h.py h2h_X rs_X rs_v10i --seeds 1,2            # 68 seeded games vs instrumented v10 (both sides pay the printing)
$PY $T/econtable.py econ_v10 econ_X ...                 # rounds-to-1000 table
# map dumps (camp handles for replay analysis)
$PY $T/mk_mapdump.py && $PY $T/runner.py dumps rs_mapdump idle --one-side --rounds 1 && $PY $T/mk_mapdump.py --extract
# platform replays (match-group zips, read in memory only; run Python with -I)
$PY -I $T/ourgames.py DIR...      # our games: result, gem curve, drafts, deaths, fuel
$PY -I $T/teamstats.py DIR...     # bodies, hits, casts, gold spent, finish rounds
$PY -I $T/damage.py DIR...        # estimated camp damage
$PY -I $T/boss.py DIR...          # how teams attack boss groups
$PY -I $T/cofarm2.py DIR...       # pack farming by round and map
$PY -I $T/deaths2.py DIR...       # robust death counts
# local instrumented runs
$PY $T/analyze.py RUN --acts --deaths;  $PY $T/contact.py RUN BOT;  $PY $T/chase.py RUN BOT chase|ret;  $PY $T/gold.py RUN BOT
```

Machine: 4-core Linux cloud container, cambc 2.2.5, `tools/repro_check.py` REPRODUCED (34/34). A 68-game head-to-head took ~26 minutes at 4 jobs.

Caveats:
- All probes are instrumented copies (printing only) played against instrumented v10, so both sides pay the same printing fuel. An adopted change should still be re-run on plain code with `tools/gauntlet.py`, as the team rule requires.
- The platform sample is one day: 30 of our games and 20 pro games. Per-map counts (1–3 games) are anecdotes; the per-class patterns (4-pick 2/9, boss maps 1/7) and the per-team economy numbers are the evidence.
- The derived tables are in [`data/`](data/). The replays aren't in git: re-download them, or ask for them, to re-run the analysis.
