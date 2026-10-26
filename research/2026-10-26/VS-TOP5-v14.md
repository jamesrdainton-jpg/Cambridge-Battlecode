# v14 against the top 5, and why their drafts differ from ours (2026-10-26)

Written for the team. Follows [../2026-10-25/VS-TOP5.md](../2026-10-25/VS-TOP5.md) (v13, 1/25). Evidence: 25 games of
v14 against the ladder's top 5 (five 5-game groups the user queued on 2026-10-26 and uploaded; copies in
`replays/platform/v14-top5/`, not in git), decoded with the tools at the end, plus the five teams' champion pick rates
over their last 50 games, from screenshots of the platform the user took. Confidence is given per claim.

| Group | Opponent (from the screenshot whose picks match the drafts; two are inferred) | v14 |
|---|---|---|
| `62261d14` | Intercontinental Fish (Vesper, Vendetta, Heart of Ruin, Cassi & Issac, + Ren/Marcella) | 0/5 |
| `858b2950` | Mite (Vesper, Vendetta, Heart of Ruin, + Tavi/Cassi & Issac, Marcella) | 0/5 |
| `99d38033` | probably Claudus Maximus (Marcella, Vendetta, Ryth, Vesper, + Varg/Heart of Ruin) | 0/5 |
| `c6d986c8` | probably willow best girl (Prism, Vendetta, Marcella, Willow, Heart of Ruin) | 0/5 |
| `1622b16a` | prism best girl (Prism, Vesper, Marcella, Ryth, Heart of Ruin) | 0/5 |

## 1. Summary

- **v14 went 0/25** (v13: 1/25). Mean gems at round 300: 90 against 185; at round 600: 165 against 431.
- **Deaths are still the main loss**, and they got only slightly better: 1.61 per 100 rounds against their 0.18 (v13:
  1.81 against 0.27). A death costs 60 rounds, so **our champions spent ~22% of the game dead (theirs ~2%)**, hand over
  100 gold and the gems they carry, and that pays for the next fight. We won 14 of the 197 engagements that had a winner.
- **The item gap did not close; it widened.** Gold spent by round 300: **447 against 1,408** (v13: 563 against 1,712).
  They buy their first shard at round 63 (we at 88) and own **8.2 shards at round 100, 24 at 200, 46 at 300; we own 2.7,
  9 and 14.** Monster-first (v14's build) did not fix the early economy; it only farms faster locally.
- **Their drafts are not "completely different" from ours**: three of our five picks (Vendetta, Vesper Vale, Marcella)
  are their three most common after Heart of Ruin. The real differences are **Heart of Ruin (84% of their games, 0% of
  ours)**, **Tavi (10% vs 100%)** and our 3-pick draft (section 3).
- **The draft is not why we lose (high confidence).** The same champions die about ten times as often in our hands:
  Vendetta 3.6 deaths a game for us vs 0.3 for them, Vesper 2.2 vs 0.33, Marcella 3.0 vs 0.35. Our deaths are spread
  evenly over all five of our champions (2.2–3.6 a game). Swapping picks alone would leave most of these games lost.

## 2. Evidence

### 2.1 Where the turns go (`turnuse.py`)

| Share of champion-turns | Us | Top 5 |
|---|---|---|
| Hitting a camp or champion | **14%** | **22%** |
| Moving only | 52% | 58% |
| Nothing (dead, channelling, waiting) | **33%** | **13%** |
| Starting a recall or tribute | 1% | 6% |

345 deaths × 60 rounds ≈ 20,700 of our 94,249 champion-turns (22%) are dead turns; theirs 38 × 60 ≈ 2%. With dead turns
removed, they still hit on ~22% of living turns against our ~18%. **Most of the farming gap is deaths, not pathing.**

### 2.2 How we die (`deathwin.py`, 278 deaths with an enemy champion hit in the 30 rounds before)

- **Slow deaths, not ambushes:** from the first enemy hit to death took 0–1 rounds in 52 deaths, 2–3 in 40, 4–7 in 64,
  **8+ in 122**. Median hits taken: 6.
- Only 29 of 278 were hitting a camp just before the first enemy hit. 188 hit back, 270 moved in the window.
- 168 of 291 deaths to champions were one-on-one; 225 were **in our own half**.
- Reading: our champions take fights (or stay in them) that they lose 93% of the time. **Our fight estimate is biased in
  their favour.** Things it doesn't model, all common in their drafts: area stuns (Heart of Ruin's dash, Ryth), Marcella's
  stunning attack and **stun immunity** (our Tavi and Ryth stuns do nothing to her; she is in 75% of their games),
  self-shields (Heart of Ruin 1.5× focus every 8 turns), Heart of Ruin's up to +50% damage when hurt, dashes that catch a
  retreating champion (Vesper, Vendetta, Heart of Ruin all dash), and turn order (they set priority every round).

### 2.3 Early economy (`early.py`, per team per game)

| Camp hits, rounds 1–100 | Wolf | Elk | Gem cluster | Gold cluster | Boss |
|---|---|---|---|---|---|
| Us | 24.0 | 31.2 | 14.2 | 6.8 | 4.2 |
| Top 5 | **42.6** | 30.3 | 15.0 | **13.3** | 2.8 |

They open on **wolves and gold clusters**, the safest gold: a gold cluster is 20 gold for 120 health and never hits
back; a wolf 40 gold and 4 gems for 1,350 health at 20 strength. We open on elks (60 strength) and bosses. Gems at
round 100 are level (30 vs 33); gold is not.

### 2.4 How they use the kits (`kits.py`, per 100 champion-turns)

- **Heart of Ruin dashes 9.8 times per 100 turns: nearly every time the 8-turn cooldown allows.** 38% of dashes land next
  to camp tiles (30% next to two or more): the landing hits everything within 1 tile for 1.5× focus and stuns it, so
  it is a free area attack that also stops the camps hitting back. 9% land next to one of our champions (engages). It
  shields itself 3.9 times per 100 turns.
- Their Vendetta, Vesper and Ryth hit camps on about twice as many turns as ours (Vendetta 23.0 vs 11.0, Ryth 24.4 vs
  9.7, Vesper 24.3 vs 17.0); champion hits are similar (4.3 vs 3.1). That is mostly deaths (2.1).
- Our bot uses Heart of Ruin's dash only to walk faster: `profile()` ignores dash damage, and `fight()` and `farm()`
  never aim it.

## 3. Why their picks differ from ours

Pick rates over each team's last 50 games (screenshots), averaged over the five teams:

| Champion | Top 5 (mean) | Fish | Mite | Claudus? | willow? | prism | v14 |
|---|---|---|---|---|---|---|---|
| Heart of Ruin | **84%** | 100 | 100 | 36 | 98 | 86 | **never** |
| Vendetta | 80% | 90 | 100 | 100 | 90 | 18 | always |
| Vesper Vale | 76% | 100 | 100 | 82 | 10 | 86 | 4–5 picks |
| Marcella | 75% | 44 | 50 | 100 | 100 | 82 | 4–5 picks |
| Prism | 38% | 0 | 0 | 0 | 88 | 100 | never |
| Ryth | 32% | 0 | 0 | 100 | 0 | 62 | 3 and 5 picks |
| Cassi & Issac | 26% | 88 | 40 | 0 | 0 | 0 | never |
| Willow | 12% | 2 | 0 | 0 | 62 | 0 | never |
| Tavi | **10%** | 0 | 50 | 0 | 2 | 0 | **always** |
| Varg, Ren, Stellar | 0–6% | | | | | | never |

**Why they pick what they pick** (inferred from the kits, the replays and the patch notes; medium confidence):

1. **Gold decides fights, and fights decide games.** Kill gold is 100 and items stack without limit, so the teams pick
   for gold income and for winning fights: **Vesper** (+33% of all gold, kill gold included), **Marcella** (+2 gold per
   gem she tributes, 1,200 health, immune to stuns) and **Cassi & Issac** (two bodies, two gold incomes, for one pick).
2. **Heart of Ruin is the best champion in the game, and the developers say so**: it was nerfed twice in 3.0 (the emergency patch
   names "near 100% usage rates in top ladder") and again in 4.0, and it is still in 84% of top drafts. Every 8 turns its dash is a
   2-tile gap-closer that deals 1.5× focus to everything within 1 tile and stuns it: on camps that is area farming
   with no damage taken back; on champions it catches a retreating enemy and stuns it for the team's follow-up. Add a
   self-shield and up to +50% damage when hurt, and it farms and duels well.
3. **Mobility.** Vesper, Vendetta and Heart of Ruin all dash, so they choose which fights happen and catch champions
   that walk away. 270 of our 278 dying champions were moving when they died.
4. **Tavi and stun champions are weak into Marcella.** Tavi's 4.0 strengths are a ranged stun (1.6× focus) and buying
   shards in the field. Marcella ignores stuns, and three of the five teams field her in 82–100% of games. Tavi has
   900 health, no dash, and its field shopping matters less once you recall to heal anyway.
5. **Map-dependent seconds:** Prism (1.5 focus per carried gem: a big-bag farmer), Ryth (area stun, 1,200 health),
   Willow (heals) appear where a team's play suits them; no consensus.

**Why our picks differ** (high confidence): our draft was chosen by local head-to-heads **against our own bot**
(DEVLOG 150: the strength draft 130/160 vs the old pro draft; the top teams' own draft only 53/80 vs it). A self-play
test can only reward what our code knows how to use. Our code never aims Heart of Ruin's dash, doesn't value
mobility, and doesn't model stun immunity, so the top teams' draft looked worse than ours locally. The test measured
our code, not the champions.

## 4. What to do about it (ranked)

1. **Stop dying.** It's worth more than anything else here (22% of champion time, 100 gold a death to them). The fight
   estimate needs to respect what it doesn't model: count stuns and shields, count enemy dashes as reach, and retreat
   earlier when the enemy has out-spent us. **This can't be judged locally**: our own bot fights the same wrong way, so
   being more careful against it looks like lost fights. It needs platform scrimmages.
2. **Gold first in the opening:** wolves and gold clusters before elks, first shard by round ~60.
3. **Draft Heart of Ruin, drop Tavi** — but only together with code that uses the dash: area dash onto camp clusters
   while farming, and dash-stun onto an enemy we are already beating. Our 3-pick draft (Vendetta, Ryth, Tavi) should
   become Vendetta, Heart of Ruin + one of Vesper/Marcella.
4. **Test against something other than ourselves.** Local gauntlets now only screen for regressions; the verdict
   is a scrimmage group against two or three of the top 5 after uploading (`cambc match-groups create TEAM_ID --maps
   ...`, quota 50 groups per window), compared with the numbers in this file (deaths per 100 rounds, gold by r300,
   engagements won).

## 5. Commands

```
python -I research/2026-10-25/tools/vspro.py replays/platform/v14-top5/*.zip      # per game + aggregate
python -I research/2026-10-26/tools/turnuse.py replays/platform/v14-top5/*.zip    # turn use, Heart of Ruin dash landings
python -I research/2026-10-26/tools/deathwin.py replays/platform/v14-top5/*.zip   # how our champions die
python -I research/2026-10-26/tools/early.py replays/platform/v14-top5/*.zip      # opening camp choice and shards
python -I research/2026-10-26/tools/kits.py replays/platform/v14-top5/*.zip       # ability use per champion
```
