# Strategy notes (2026-10-20)

How this session thought about the game, what the evidence says, and what to do next. The experiment record is in
DEVLOG rows 143 onwards; this file is the reasoning behind them, written so it can be checked rather than trusted.

## 1. The game is a throughput race, not a supply race

Each map's camps could sustain far more gems than either team collects. If every group were captured the moment it
respawned, packs would yield ~7.9 gems a round, swirl ~28, lanes ~18; the teams that beat us on the platform reach
1,000 at about 1.5–3 a round. Fragment (3.4 a round for the whole map) is the only map where respawn timers bind.

So the rate is set by the champions, roughly

    rounds to 1,000  ≈  camp health that holds 1,000 gems  ÷  (team damage × share of turns spent hitting × gem yield)

- **Camp health per gem** differs a lot: gem clusters ~21 HP per gem, wolves and elks ~61–67, monoliths ~100.
- **Share of turns spent hitting**: v12 unopposed spends ~31% of champion-turns at a target group (DEBUG activity
  tallies; that includes moving into range), while walking, waiting at respawns and idling take 42%, and 60–68% on
  ambush, contest, pilgrimage and stampede. Turns that actually hit a camp were ~17% for us and ~20% for strong teams
  in the 2026-10-19 replay analysis, so they aren't faster by hitting more often; they get more gems per hit.
- **Gem yield per hit** is where the strong teams win: area casts on clustered camps (Stellar's 1.4× focus hits up to
  9 camps; Varg's splash), poking from range 4 (camps reach 3, so the caster takes no damage and never recalls for
  health), and more bodies (Cassi & Issac are two champions for one pick).

## 2. What the bot did wrong, in that frame

| Problem | Effect | Fix (flag) |
|---|---|---|
| Groups that need more champions than we have are skipped outright, poke off | Stampede's only gems (one 12-camp group, 360 gems) untouched until items allow tanking: 1,035 rounds unopposed vs ~500 for strong teams *contested* | Sieges: `MONOLITH_POKE` + `AOE_POKE` (poke cost counts camps an area cast hits) + `POKE_SMART` (reach from damaging camps only, single casts on damaging camps, basic attacks between casts) |
| Melee splash target boxed in by its own group | Varg froze next to monolith's Monolith (surrounded by 8 gem clusters) | `MELEE_REACH` |
| Expired squad wait reset on the same turn | A champion whose attack didn't wake the group waited 40 more turns, repeatedly | `WAIT_FIX` |
| Pack lead costs a walk for `need` champions but six follow | The whole team walked 63 tiles as one unit on pilgrimage | `PACK_WALK_ALL` |
| Damage-free stun never used on camps | Cassi's stun wasted while farming | `STUN_CAMPS` |
| Fuel at the per-turn cap on ambush (2.48M of 2.5M) | Over-cap turns are suspended | `FAST_WALK`, `FAST_SCORE` (2.20M peak) |
| Cassi & Issac counted as two separate bodies in fights | We under-rated fights against the 94%-popular pair and their double bag | `PAIR_KILL` |

## 3. Mechanics established this session (probe bots, cambc 2.2.5)

1. Stuns work on camps: a stunned camp skips its next attack.
2. A camp's stun buff (`Unit.buffs()`) has duration 2 on the cast round and 1 on the next round, by when the skip
   has already happened.
3. A camp keeps attacking a champion that stays in its reach after a single hit (12+ rounds observed). It sleeps only
   after 2 rounds with nobody in reach. "Awake = hit in the last 2 rounds" is wrong (flag `AWAKE_RECENT`, kept off on
   its own; `AWAKE_NEAR` adds the reach condition).

## 4. What we still can't see

- **The platform.** Local wins didn't transfer before (v10 beat v8 55/68 locally; platform 13/30, same as v7). This
  session couldn't reach the platform (network policy), so nothing here is verified against real opponents.
- **Contested sieges.** Poking drains a boss for ~100 rounds; an opponent that walks in at the end captures it. The
  2026-10-19 report saw exactly this (poking lost contest 0/4 to v10). The siege code has a closing step
  (`POKE_CLOSE`, shared boss health `POKE_SHARE`) but whether it wins those races against strong teams is unknown.

## 5. What to do next, in order

1. **Get platform data flowing.** Either allow `2026a.battlecode.co.uk` in the cloud environment's network settings,
   or download a day of v13 games into `replays/platform/` and run `research/2026-10-19/tools/ourgames.py`,
   `teamstats.py`, `deaths2.py`. Compare per map class (boss maps, 4-pick, 3-pick) with v12's day.
2. **Judge v13 on boss maps first** (contest, stampede, rows, monolith; v10 went 1/7). If sieges get robbed there,
   the first thing to try is `POKE_AVOID_ENEMY` or closing earlier (`POKE_CLOSE_FRAC` 0.3 → 0.5).
3. **Map-aware draft.** The draft phase sees the whole map with 10× fuel. A rule keyed on the share of gems in groups
   too strong to tank (and their area-cast coverage) could pick Stellar/Prism exactly where sieges pay.
4. **Keep the economy benchmark as the first gate** (`tools/lab.py econ`, 2 seeds ≈ 15 min for one bot). It is
   opponent-independent, and its noise is known: ~70 rounds on the 17-map sum for a 2-seed mean, 5–55 per map.
