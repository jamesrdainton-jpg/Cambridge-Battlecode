// Tunables for the C++ port of bots/mybot (v13 logic plus the cambc 3.0 flags). Names and values mirror
// bots/mybot/src/bot.py so experiments can be translated one to one. tools/variant.py edits "NAME = value" here.
#pragma once

namespace bot
{
// Testing only: a non-zero SEED perturbs target scores by up to 2% so repeated matches diverge.
inline constexpr int SEED = 0;
inline constexpr bool DEBUG = false;

// Squads and targets.
inline constexpr int MIN_SQUAD = 1;
inline constexpr int RETARGET_EVERY = 8;
inline constexpr double NEED_FRAC = 0.55;
inline constexpr int WAIT_LIMIT = 0;
inline constexpr double BOSS_NEED_FRAC = 0.0;
inline constexpr int BOSS_WAIT = 0;
inline constexpr double GOLD_WEIGHT = 0.4;
inline constexpr int GOLD_TAPER = 500;
// Gold first in the opening (VS-TOP5-v14.md 2.3: the top teams open on wolves and gold clusters): until EARLY_UNTIL,
// gold is weighted EARLY_GOLD instead of GOLD_WEIGHT. 0 = off.
inline constexpr double EARLY_GOLD = 0.0;
inline constexpr int EARLY_UNTIL = 150;
// Maps where no altar can be reached without killing a camp first (play_draft() works it out and passes it through
// draft memory): target gold only and never walk to an altar; the round limit decides on lifetime gold (as bot.py).
inline constexpr bool LOCKED_GOLD = true;
inline constexpr double ENEMY_SIDE = 0.85;

// Fights.
inline constexpr double FIGHT_RETREAT = 0.9;
inline constexpr double FIGHT_ENGAGE = 1.3;
inline constexpr double FIGHT_GEM_EXTRA = 0.25;
inline constexpr int ALLY_RANGE = 7;
inline constexpr double LOW_HP_RETREAT = 0.25;
inline constexpr int LOW_HP_REACH = 2;
inline constexpr bool CAST_FIRST = true;
inline constexpr bool FIGHT_SHIELD = true;
inline constexpr bool IGNORE_SPAWN_CAMPERS = true;
inline constexpr int STAND_REACH = 0;
inline constexpr int FIGHT_COMMIT = 0;
inline constexpr bool HELP_CALLS = false;
inline constexpr bool FIGHT_PRIO = true;
inline constexpr int HELP_RANGE = 8;
// Enemy damage is multiplied by this in the fight ratio: we lose 93% of decided engagements vs the top 5, so the ratio
// over-rates us (unmodelled stuns, shields, dashes, turn order). 1.0 = off.
inline constexpr double FIGHT_RESPECT = 1.0;
// Heart of Ruin's dash as an attack: landed on camp clusters while farming, onto enemies to open a fight we want or to
// finish a champion, its damage counted in profiles; no travel dash within 6 tiles of the destination.
inline constexpr bool HOR_DASH = false;
// Step out of an enemy's reach instead of holding still when the ratio is between FIGHT_RETREAT and FIGHT_ENGAGE and
// nothing of ours can hit back (fight() used to return without acting).
inline constexpr bool HOLD_FIX = false;
// Print one "F ..." line per fight decision (bot.h tele()); printing only, no change to play.
inline constexpr bool TELEMETRY = false;

// Draft (draft.h): 0 = v13/v14 (3: Vendetta, Ryth, Tavi; 4: Vendetta, Vesper, Tavi, Marcella; 5: + Ryth);
// 1 = top-team consensus (3: Vendetta, Heart of Ruin, Vesper; 4: + Marcella; 5: + Ryth);
// 2 = Marcella core (3: Marcella, Vendetta, Heart of Ruin; 4: + Vesper; 5: + Ryth).
inline constexpr int DRAFT_SET = 0;

// Camps, captures, vision.
inline constexpr bool CLAIM_ON_KILL = true;
inline constexpr bool CAMP_TILE_FIX = true;
inline constexpr bool WARDS = true;

// Tributes, recalls, shopping.
inline constexpr int TRIBUTE_BIG = 30;
inline constexpr int TRIBUTE_MID = 15;
inline constexpr bool ALTAR_LOCKS = true;
inline constexpr bool RECALL_TRAVEL = true;
inline constexpr int RECALL_TURNS = 5;
inline constexpr int SHOP_GOLD = 150;
inline constexpr double SHOP_HP = 1.01;
inline constexpr bool SHOP_SAFE = true;
// Item builds: 0 = v13's (Monster, Power, Jungle, Durability), 1 = Treasure, Jungle, Bruiser stacks (the top teams'),
// 2 = Treasure, then Bruiser only; 3/4/5 = 1 opening with Capture, Monster or Prospector instead of Treasure (cambc 4.0).
inline constexpr int BUILD_30 = 4;
} // namespace bot
