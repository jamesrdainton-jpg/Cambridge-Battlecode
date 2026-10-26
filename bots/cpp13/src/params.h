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
// Maps where no altar can be reached without killing a camp first (play_draft() works it out and passes it through
// draft memory): target gold only and never walk to an altar; the round limit decides on lifetime gold (as bot.py).
inline constexpr bool LOCKED_GOLD = true;
// Meta champions (2026-10-26, the user's request): play Heart of Ruin's stun-dash in fights and on camps, value stunned
// enemies, let pure stuns (Cassi) hit camps, shield whenever hurt. META_DRAFT (draft.h): 0 = v14's; 1 = the top teams'
// core (Heart of Ruin, Vesper, Vendetta; + Cassi & Issac; + Marcella); 2 = core + Tavi (stun buffed in 4.0) at 4, + Cassi &
// Issac at 5; 3 = v14's with Heart of Ruin for Marcella at 4 and for Ryth at 5.
inline constexpr bool META_PLAY = false;
inline constexpr int META_DRAFT = 0;
// META_BUILD: Heart of Ruin buys the focus build (Bruiser F/H, as the top teams); META_PAIR: Cassi takes Issac's target.
inline constexpr bool META_BUILD = false;
inline constexpr bool META_PAIR = false;
// META_STUN_COMMIT (needs META_PLAY): champions within 4 of a stunned enemy engage it whatever the fight ratio.
inline constexpr bool META_STUN_COMMIT = false;
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
