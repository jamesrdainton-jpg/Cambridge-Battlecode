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

| Problem | Effect | Fix (flag) | Verdict |
|---|---|---|---|
| Groups that need more champions than we have are skipped outright, poke off | Stampede's only gems (one 12-camp group, 360 gems) untouched until items allow tanking: 1,035 rounds unopposed vs ~500 for strong teams *contested* | Sieges: `MONOLITH_POKE` + `AOE_POKE` (poke cost counts camps an area cast hits) + `POKE_SMART` (reach from damaging camps only, single casts on damaging camps, basic attacks between casts) | **In v13 on stampede only** (`SIEGE_SHARE` 0.9 + `SIEGE_COV` 2.0); everywhere it lost contested games |
| Melee splash target boxed in by its own group | Varg froze next to monolith's Monolith (surrounded by 8 gem clusters) | `MELEE_REACH` | **In v13** |
| Expired squad wait reset on the same turn | A champion whose attack didn't wake the group waited 40 more turns, repeatedly | `WAIT_FIX` | **In v13** |
| Pack lead costs a walk for `need` champions but six follow | The whole team walked 63 tiles as one unit on pilgrimage | `PACK_WALK_ALL` | Off: pulled the pack into contested centres |
| Damage-free stun never used on camps | Cassi's stun wasted while farming | `STUN_CAMPS` | Off, untested on its own |
| Fuel at the per-turn cap on ambush (2.48M of 2.5M) | Over-cap turns are suspended | `FAST_WALK`, `FAST_SCORE` (2.20M peak) | Off: suspected in elkring 0/4; worth retesting alone |
| Cassi & Issac counted as two separate bodies in fights | We under-rated fights against the 94%-popular pair and their double bag | `PAIR_KILL` | Off: lost games |

## 3. Mechanics established this session (probe bots, cambc 2.2.5)

1. Stuns work on camps: a stunned camp skips its next attack.
2. A camp's stun buff (`Unit.buffs()`) has duration 2 on the cast round and 1 on the next round, by when the skip
   has already happened.
3. A camp keeps attacking a champion that stays in its reach after a single hit (12+ rounds observed). It sleeps only
   after 2 rounds with nobody in reach. "Awake = hit in the last 2 rounds" is wrong (flag `AWAKE_RECENT`, kept off on
   its own; `AWAKE_NEAR` adds the reach condition).

## 4. The session's main lesson: faster alone is not stronger together

The best economy package (`zL`: fixes, strict squad wait, need-sized walk costs, live camp damage, camp stuns, Cassi &
Issac valuation, sieges everywhere) reached 1,000 gems **8.5% faster unopposed** than v12, and then **lost to v12
28/68 (−5,176 gems)**. The layer ablation and traces explain most of it:

- **Where champions stand decides fights.** On swirl the pack, now preferring near targets, walked into the contested
  centre at round 8 and lost three champions by round 18. Pokers standing alone at range 4 of a boss for 100 rounds
  are easy kills; a strict squad wait leaves champions idle beside camps. None of that costs anything unopposed.
- **Sieges are robbed when there is anything else to do.** Every contest test lost (0/4, 1/4, 0/4): the opponent
  walks in and finishes a poked monolith. Sieges only win where nothing else gives gems and the boss group is clustered
  for area casts (stampede 4/4 on seeds 1,2 and 8/8 on seeds 3–6; v12 scores 0 there).
- **Fight-ratio tweaks are fragile.** Counting Cassi & Issac at the weaker one's health sounded right and lost games
  (removing it: 5/28 → 10/28 on seven maps).
- **Fixes that only change what was clearly broken are safe**: `MELEE_REACH` + `WAIT_FIX` played the identical games to
  v12 on six of seven maps and won both pilgrimage games on seeds 1,2; on seeds 3–6 pilgrimage and monolith
  were 4/8 each (mostly identical games), so they are correctness fixes, not a measured gain (DEVLOG 155).

So the gate for any change is head to head, and the economy benchmark only says whether a change is worth a
head-to-head. Changes that move champions around the map need the most suspicion.

## 5. What we still can't see

- **The platform.** Local wins didn't transfer before (v10 beat v8 55/68 locally; platform 13/30, same as v7). This
  session couldn't reach the platform (network policy), so nothing here is verified against real opponents.
- **Contested sieges.** Poking drains a boss for ~100 rounds; an opponent that walks in at the end captures it. The
  2026-10-19 report saw exactly this (poking lost contest 0/4 to v10). The siege code has a closing step
  (`POKE_CLOSE`, shared boss health `POKE_SHARE`) but whether it wins those races against strong teams is unknown.

## 6. What to do next, in order

1. **Get platform data flowing.** Either allow `2026a.battlecode.co.uk` in the cloud environment's network settings,
   or download a day of v13 games into `replays/platform/` and run `research/2026-10-19/tools/ourgames.py`,
   `teamstats.py`, `deaths2.py`. Compare per map class (boss maps, 4-pick, 3-pick) with v12's day.
2. **Judge v13 on stampede and monolith first** (v10 went 1/7 on the four boss maps). If strong platform teams also
   poke stampede, the race is on capture security: closing earlier (`POKE_CLOSE_FRAC` 0.3 → 0.5) is the next test.
3. **Make sieges safe to use elsewhere** before widening `SIEGE_SHARE`: the poker should not stand alone (poke only
   with an ally within ~6 tiles, or retreat to the squad when an enemy is seen), and the team should converge for the
   kill. Test against v12 *and* `proxy` (v12 + poke + pro draft everywhere, `tools/variant.py proxy ...`).
4. **Map-aware draft.** The draft phase sees the whole map with 10× fuel. A rule keyed on the share of gems in groups
   too strong to tank (and their area-cast coverage) could pick Stellar/Prism exactly where sieges pay.
5. **Keep the economy benchmark as a first filter, never the verdict** (`tools/lab.py econ`, 2 seeds ≈ 15 min for one bot). It is
   opponent-independent, and its noise is known: ~70 rounds on the 17-map sum for a 2-seed mean, 5–55 per map.
