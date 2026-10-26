# cambc 3.0 balance patches (platform, from 20 Oct 2026)

`GameRules.md` at the repo root is the handbook as of 14 Oct (engine 2.1/2.2) and is **out of date** for every number below.
The platform switched to engine 3.0 when `cambc` 3.0.0 was published (PyPI, 2026-10-20 02:50 UTC); 3.0.5 followed on 2026-10-22.

## Final values on cambc 3.0.5, read from the engine

Measured with a probe bot that prints `constants`, `Champion.design(k)` for every champion and `camp_design(k)` for every
camp kind, under 2.2.5 and 3.0.5 (`research/2026-10-25/tools/rules_probe.py`). Every value matches the latest patch notes below.

| | 2.2.5 | **3.0.5** |
|---|---|---|
| Kill gold | 50 | **100** |
| Ward cooldown (rounds between placements) | 1 | **10** |
| Altar lock hits to clear | 3 | **5** |
| Wolf: gems / gold / range | 22 / 90 / 3 | **4 / 40** / 3 |
| Elk: gems / gold / range | 36 / 160 / 3 | **15 / 90 / 4** |
| Gem cluster: HP / gems | 500 / 24 | **120 / 7** |
| Gold cluster: HP / gold | 500 / 35 | **120 / 20** |
| Monolith: range (HP 20,000, strength 200, 200 gems, 300 gold unchanged) | 3 | **5** |
| **Golem (new camp kind 5)** | — | **5,000 HP, 120 strength, range 4, 160 gold, 36 gems, respawn 80** |

| Champion | 2.2.5 (HP / str / focus, growth per shard) | **3.0.5** |
|---|---|---|
| Ryth | 1200 / 50 / 100 | 1200 / **45** / 100 |
| Vesper Vale | 900 / 45 / 100, gold +20% | **1000 / 55** / 100, gold **+33%** |
| Vendetta | 800 / 70 / 100, str +5 | **1000** / 70 / 100, str **+6** |
| Cassi | 700 / 30 / 70 (+71.25 / +3.5 / +15) | **600** / 30 / 70 (**+65 / +3 / +13**) |
| Issac | 900 / 40 / 100 (+95 / +4.75 / +10) | 900 / 40 / 100 (**+80 / +3** / +10) |
| Stellar | 750 / 35 / 100 (+75 / +3.5 / +10) | **650 / 30 / 70 (+65 / +3.5 / +7)** |
| Prism | 700 / 35 / 80, 0.2 focus per carried gem | 700 / 35 / 80 (**+60 / +2.5 / +8**), **1.5 focus per carried gem** |
| Marcella | 1200 / 45 / 50 (+10 focus) | 1200 / 45 / **60 (+15 focus)**, **+2 gold per gem tributed** |
| Willow | 700 / 45 / 105 | 700 / **55 / 120** |
| Ren | 900 / 40 / 100 (+10 focus), stun 1.25× focus | 900 / **35** / 100 (**+9**), stun **0.75×** |
| Varg | 1000 / 50 / 100 | 1000 / **40** / 100 |
| Tavi | 750 / 35 / 100, stun 2.2× focus | **900 / 45 / 110**, stun **1.4×** |
| **Heart of Ruin (new, draft pick 11, champion type 12)** | — | melee, **1000 / 30 / 100 (+100 / +3.5 / +12)**; passive up to **+50% damage at 0% health** (all damage); S1 self-shield 1.5× focus for 5 turns; S2 2-tile dash that deals **1.5× focus and stuns for 1 turn in radius 1** on landing |

Items and consumables are unchanged. New SDK calls: `Camp.is_golem()`, `vision.awake_camp_tiles()` / `asleep_camp_tiles()`,
`vision.in_vision()`, `Ward.owner()`, `DistanceField.copy_from()`; `AbilityDash` gained `radius`, `modifier`, `duration`.

## Patch notes as published (most recent first; pasted by the user on 2026-10-25)

### Latest patch

Stellar
- Health: 750 → 650
- Health per shard: 75 → 65
- Focus: 85 → 70
- Focus per shard: 9 → 7

Heart of Ruin
- Strength: 40 → 30
- Strength per shard: 4 → 3.5
- Dash landing damage (S2): 1.75 × Focus → 1.5 × Focus

Ren
- Stun damage (S1): 1.25 × Focus → 0.75 × Focus

> Focus champions have a lot of front loaded damage, which has been hard to play around. These champions also have extremely high pick rates all across the board and so we are lowering their output.

Vesper Vale
- Health: 900 → 1000
- Strength: 50 → 55

Vendetta
- Health: 800 → 1000

Tavi
- Health: 750 → 900
- Focus: 100 → 110

> Strength champions are struggling to endure the amount of burst in the game, so we are giving them a bit more health to help them through early game combats

Prism
- Passive focus per gem: 1 → 1.5

> Prism has not seen any usage in higher ranked play, hopefully these changes will encourage teams to build a specialist strategy around them

### Emergency patch

Heart of Ruin — emergency nerf due to near 100% usage rates in top ladder:
- Strength per shard: 5 → 4
- Focus per shard: 15 → 12

**Important ladder change.** Previously, new patches that caused compilation errors would remove your bot from matchmaking and you could essentially freeze your elo. This has now been changed such that your team will be marked as having an out of date submission ("invalid bot") and you will have a grace period for 24 hours to patch it before you will start auto losing ranked matches. The site will alert you if you are in this situation and need to submit a new bot.

(Our v12 compiles, so it was never marked invalid: it crashes at run time, only on maps with a golem, and loses those games.)

### 3.0 patch (first)

Cassi
- Health: 700 → 600
- Health per shard: 71.25 → 65
- Strength per shard: 3.5 → 3
- Focus per shard: 15 → 13

Issac
- Health per shard: 95 → 80
- Strength per shard: 4.75 → 3

> We felt that Cassi and Issac was overly picked on every map and thus are toning them down a little. We wish to keep their niche of having the highest base stats (combined) in the early game, but heavily reduce their scaling into mid-late game.

Stellar
- Focus: 100 → 85
- Strength: 35 → 30
- Focus per shard: 10 → 9

> Stellar was the premier ranged DPS overshadowing many of the other champions and so we are toning her down.

Varg
- Strength: 50 → 40

> Varg has had a ton of presence across all maps thanks to his AoE attacks, however he was too good at clearing single camps with his high base strength. We are toning this down whilst hopefully keeping his niche for large camp groups.

Ren
- Strength: 40 → 35
- Focus per shard: 10 → 9

> Ren is a champion that can generally do everything as long as he had the stats, we felt that he was able to come online too early and thus are reducing his scaling slightly.

Ryth
- Strength: 50 → 45

> Like Varg, has had a ton of presence with his high base strength and AoE damaging ability (S1). We wish to tone down his single target damage a little.

Marcella
- Passive: gain 2 gold per gem tributed, and stun immunity
- Focus: 50 → 60
- Focus per shard: 10 → 15

> Marcella lacked presence due to her simple kit, with this buff and change to her passive we hope to bring her presence up this week!

Willow
- Strength: 45 → 55
- Focus: 105 → 120

> As the only healer in the game, Willow holds a special role but simply was not efficient to build items on. We are going to lean into this and push Willow towards early game power and sustain to help other weaker early game champions scale or push tempo with the ability to stay on the map for longer.

Vesper Vale
- Passive bonus gold: 20% → 33%
- Strength: 45 → 50

> Vesper vale has been one of the weaker champions in the game, we have decided to buff her early game power and gold income to help her hit her power spikes sooner.

Vendetta
- Strength per shard: 5 → 6

> We think that vendetta is in a decent spot, but struggles to scale well with items and thus are giving her a little nudge.

Prism
- Passive focus per gem: 0.2 → 1
- Health per shard: 75 → 60
- Strength per shard: 3.5 → 2.5
- Focus per shard: 10 → 8

> Prism saw very little play, only really used with Stellar to cheese camps from out of their range as he has 2 ranged damaging abilities. By increasing his gem scaling and reducing his stat scaling we hope to bring prism into his intended playstyle as a high risk mage.

Tavi
- Stun damage (S2): 2.2 × Focus → 1.4 × Focus
- Strength: 35 → 45

> Tavi was incredibly strong last patch due to their high damage multipler and we intend to tone this down shifting them more into a strength focussed character.

Heart of Ruin (new, "our 12th and final champion"), melee
- Passive: increases damage dealt by up to 50% based on missing % health (50% bonus at 0% health, 25% at 50%, 0% at 100%). Applies to all damage sources (abilities and basic attack).
- Health 1000 (+100 per shard), Strength 40 (+5 per shard), Focus 100 (+15 per shard) — later nerfed, see above.
- S1: shield self for 1.5 × Focus for 5 turns.
- S2: 2-tile range dash. Upon landing, deals 1.75 × Focus and stuns enemies/camps for 1 turn within Chebyshev radius 1 of the landing tile (later 1.5 ×).

Camp changelog
- Wolf: gems 22 → 4; gold 90 → 40
- Elk: gems 36 → 15; gold 160 → 90; range 3 → 4
- Gem cluster: health 500 → 120; gems 24 → 7
- Gold cluster: health 500 → 120; gold 35 → 20
- Monolith: range 3 → 5

> We felt that games were ending way to quickly, and so are toning down gold and gem income per camp. The listed numbers are so low as we plan to alter the value of camp groups through the use of Gem and Gold clusters as we can add clusters to increase the groups gem or gold value without increasing clear difficulty by much.
>
> We've noticed some camps getting cheesed by Stellar, Prism, Ryth and other champions that have long ranged damage and have thus decided to increase the range of some camps to nerf this form of farming.

Golem (new): health 5000, strength 120, range 4, gold 160, gems 36, respawn 80 rounds.

> Monolith has been very difficult to fight and often too hard to work towards on some maps, so we are adding Golem as a bridge between the regular camps and Monolith.

Kill reward: gold 50 → 100.

> We want to incentivise more aggressive strategies such as invades and contesting camps, and to do this we are raising the kill reward.

Wards: cooldown 1 → 10.

> We found that being able to ward every round allowed champions to essentially sweep bushes very quickly which is not intended. By increasing the ward cooldown placement has to have a little more thought behind it.

Altar lock HP: 3 → 5.

> Many champions have a form of attack reset which lets them clear altar locks incredibly quickly. We hope to remedy this by increasing altar lock hp slightly.

Breaking SDK details: with the new balance patch, the SDK has new enum values for the new camps and champions, and the dash ability data structure gained fields (`AbilityDash`). Old submissions that relied on these patterns will now fail to compile. The teams with these submissions will be removed from matchmaking until they upload a new working submission.
