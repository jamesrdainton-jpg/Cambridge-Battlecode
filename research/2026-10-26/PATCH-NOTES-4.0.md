# Balance patch: platform engine 2.0.0 / cambc CLI 4.0.0 (2026-10-26)

Pasted by the user on 2026-10-26. Previous patch: [../2026-10-25/PATCH-NOTES-3.0.md](../2026-10-25/PATCH-NOTES-3.0.md).
The values the engine actually uses, read with the rules probe, are in the next section.

## Values measured from the engine (cambc 4.0.0 vs 3.0.5)

Measured with `research/2026-10-25/tools/rules_probe.py` under cambc 4.0.0 and compared with the same probe under 3.0.5.
Every champion and emblem change in the notes below matches the engine. **Game constants (kill gold 100, ward cooldown 10,
altar lock 5 hits, respawn 60, capture 5) and camp stats are unchanged.** The item list grew from 42 to 84 types (the
seven new families × 3 stats × shard/emblem); existing item names are unchanged.

| Champion | 3.0.5: HP / strength / focus (growth per shard); ability modifiers | **4.0.0** | Changed |
|---|---|---|---|
| Ryth | 1200 (+100) / 45 (+5) / 100 (+10); AoeDamage 1.0x | **1200 (+100) / 45 (+4.5) / 100 (+10); AoeDamage 1.0x** | yes |
| Vesper Vale | 1000 (+100) / 55 (+5) / 100 (+10) | **1000 (+100) / 45 (+5) / 100 (+10)** | yes |
| Vendetta | 1000 (+100) / 70 (+6) / 100 (+10) | 1000 (+100) / 70 (+6) / 100 (+10) |  |
| Cassi | 600 (+65) / 30 (+3) / 70 (+13); Damage 2.0x | **600 (+65) / 30 (+3) / 100 (+13); Damage 2.0x** | yes |
| Issac | 900 (+80) / 40 (+3) / 100 (+10) | **900 (+80) / 45 (+3) / 100 (+10)** | yes |
| Stellar | 650 (+65) / 30 (+3.5) / 70 (+7); Damage 2.0x, AoeDamage 1.4x | **650 (+65) / 30 (+3.5) / 70 (+8.5); Damage 2.0x, AoeDamage 1.4x** | yes |
| Prism | 700 (+60) / 35 (+2.5) / 80 (+8); Cc 1.5x, AoeDamage 1.0x | **700 (+65) / 35 (+2.5) / 80 (+8); Cc 1.5x, AoeDamage 1.0x** | yes |
| Marcella | 1200 (+100) / 45 (+5) / 60 (+15); Damage 2.0x | **1200 (+100) / 45 (+4.5) / 60 (+14); Damage 2.0x** | yes |
| Willow | 700 (+50) / 55 (+3) / 120 (+5); Heal 3.0x | **700 (+50) / 55 (+3) / 140 (+5); Heal 3.0x** | yes |
| Ren | 900 (+100) / 35 (+5) / 100 (+9); Cc 0.75x | **900 (+100) / 35 (+5) / 100 (+9); Cc 1.1x** | yes |
| Varg | 1000 (+100) / 40 (+5) / 100 (+10); Shield 2.5x | **1000 (+100) / 45 (+5) / 100 (+10); Shield 2.5x** | yes |
| Tavi | 900 (+75) / 45 (+5) / 110 (+10); Cc 1.4x | **900 (+75) / 45 (+5) / 110 (+10); Cc 1.6x** | yes |
| Heart Of Ruin | 1000 (+100) / 30 (+3.5) / 100 (+12); Shield 1.5x, Dash 1.5x | **1000 (+100) / 30 (+3) / 100 (+10); Shield 1.5x, Dash 1.5x** | yes |

| Emblem family (5 shards = 150 gold unless noted) | Stats when complete | 3.0.5 passive | **4.0.0 passive** |
|---|---|---|---|
| Monster | 5 shards of the stat | +10% damage to camps | **+15%** |
| Power | 6 shards of the stat | none | none |
| Durability | 5 shards | 10% less damage taken | 10% |
| Treasure | 5 shards | +20% gold | **+10%** |
| Jungle | 5 shards | 30% less damage from camps | 30% |
| Home | 5 shards | recall 50% shorter | 50% |
| Bruiser | 5 of the stat + 1 of each other (7) | none | none |
| **Tribute** (new) | 5 shards | — | tribute time −33% |
| **Capture** (new) | 5 shards | — | capture in 3 turns (was 5) |
| **Prospector** (new) | 5 shards | — | +25% of own share of cluster gold and gems |
| **Hunter** (new) | 5 shards | — | +50 gold per champion kill |
| **Skirmish** (new) | 5 shards | — | +5% damage to champions |
| **Greed** (new) | **25 shards (750 gold) → 35 shards of the stat** | — | none |
| **Collectors** (new) | 5 shards | — | +1% damage per unique completed emblem family |

**Map pool:** `cambc maps pull` with CLI 4.0.0 gives **70 maps**: our 40 unchanged, plus 30 new (`00anvil`, `00breadcrumbs`,
`00crater`, `00dunes`, `00galaxy`, `00oasis`, `00quarry`, `00ribs`, `00the-line`, `00vault`, fifteen `02…` maps —
`02arena`, `02crossing`, `02cuts`, `02famine`, `02fields`, `02geodes`, `02gift-wrapping`, `02guardians`, `02harvest`,
`02stalactites`, `02tangle`, `02the-pack`, `02the-pond`, `02treasure-box`, `02uncharted-lands` — and
`adgato-gemcombat1`–`5`).

## Patch notes as published

### Champions

Ryth
- Strength per shard: 5 → 4.5

Vesper Vale
- Strength: 55 → 45

Cassi
- Focus: 70 → 100

Issac
- Strength: 40 → 45

Stellar
- Focus per shard: 7 → 8.5

Prism
- Health per shard: 60 → 65

Marcella
- Strength per shard: 5 → 4.5
- Focus per shard: 15 → 14

Willow
- Focus: 120 → 140

Ren
- Stun damage (S1): 0.75 × Focus → 1.1 × Focus

Varg
- Strength: 40 → 45

Tavi
- Stun damage (S2): 1.4 × Focus → 1.6 × Focus

Heart of Ruin
- Strength per shard: 3.5 → 3
- Focus per shard: 12 → 10

### Emblems

- **Treasure emblem:** bonus gold 20% → **10%**.
- **Monster emblem:** bonus damage to camps 10% → **15%**.

New emblem families:
- **Tribute emblem:** tribute time reduced by 33% (rounded up, minimum one turn).
- **Capture emblem:** capture time 5 → 3 turns. Applies when at least one allied capturer owns a Capture emblem as the
  capture begins.
- **Prospector emblem:** +25% gold and gems from clusters. Only the Gold Cluster and Gem Cluster parts of a camp group's
  rewards count. Sharing rewards: each capturer who owns a Prospector emblem receives 25% of their own share as an extra
  reward, rounded down separately for gold and gems; capturers without one get only their normal share. Example: 20
  cluster gold shared by two allies gives each 10 base gold; a Prospector holder gains 2 extra gold; if both own it, both
  gain 2.
- **Hunter emblem:** +50 gold per champion kill, awarded to the champion who gets the kill, before gold-income bonuses.
- **Skirmish emblem:** 5% more damage to champions.
- **Greed emblem:** no passive. Combines at 25 shards (750 gold) and gives 35 shards' worth of stat points.
- **Collectors emblem:** +1% bonus damage per unique completed emblem family owned (counts itself; stat variants and
  duplicate copies of a family count once; shards don't count).

### System changes

- Draft first-turn fuel limit ×10.
- **CLI 4.0.0:**
  - Unranked match groups against an opponent's historical bot version, using a previous match-group UUID or website
    link: `cambc match-groups create OPPONENT_TEAM_UUID --source-group MATCH_GROUP_UUID_OR_LINK`.
  - List our submitted versions and change which one is live: `cambc submissions list`,
    `cambc submissions list --before 10 --json`, `cambc submissions activate 7`, `cambc submissions activate latest`.

### Breaking SDK details

- This patch uses **engine 2.0.0 and CLI 4.0.0**. Update the local CLI and rebuild bots with the updated SDK before
  testing against the new engine.
- The item backpack expanded from **42 to 84 item types**. Custom WASM bindings: `env.champion_items` keeps its name and
  arguments but now writes 84 little-endian u32 counts (336 bytes).
- **Camp capture state:** the SDKs expose capture progress alongside the camp-group state query, with `timer` and
  `state` fields:

| State | Meaning |
|---|---|
| Ally capturing | You or an ally are capturing the group. |
| Contested | Both teams are present, blocking capture. |
| Enemy capturing | The opposing team is capturing the group. |
| Capture available | The group's reward is available, but no one is capturing. |
| No capture available | The camp group is still alive or waiting to respawn. |

  While either team is capturing, `timer` is the remaining capture countdown (including the shorter one from a Capture
  emblem); otherwise it returns the normal maximum of 5 turns. The group must be in current vision to read its capture
  state, but the capturing champion need not be.
- **Item enum helper:** select an item by family and stat instead of by one of the 84 names:

| Language | Helper |
|---|---|
| C++ | `cambc::get_item_enum(item_family family, item_stat stat, bool shard = true)` |
| Python | `cambc.get_item_enum(family: ItemFamily, stat: ItemStat, shard: bool = True)` |
| Rust | `cambc::get_item_enum(family: ItemFamily, stat: ItemStat, shard: bool)` |
| OCaml | `Cambc.get_item_enum : ?shard:bool -> Item_family.t -> Item_stat.t -> Item.t` |
