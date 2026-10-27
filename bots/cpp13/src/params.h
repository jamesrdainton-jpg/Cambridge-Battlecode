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
// META_CASSI: Cassi waits (up to 20 turns) outside camp reach until an ally is at the camp, and retreats at 50-60% health.
inline constexpr bool META_CASSI = false;
// TAVI_FOCUS: Tavi buys the focus build (her stun deals 1.6x focus since 4.0).
inline constexpr bool TAVI_FOCUS = false;
// DEATHBALL (radical, 2026-10-26): the whole team farms and fights as one group behind a leader (lowest alive slot):
// followers take the leader's target and regroup when more than BALL_RADIUS tiles away. Against the top 3 we died
// 6x as often as they did, mostly picked off alone, and they fight with ~1.6 champions.
inline constexpr bool DEATHBALL = false;
inline constexpr int BALL_RADIUS = 4;
// BALL_SIZE: squads of this many consecutive slots (2 = pairs; 99 = the whole team); BALL_UNTIL: only before this round.
inline constexpr int BALL_SIZE = 99;
inline constexpr int BALL_UNTIL = 2000;
// RECALL_TRICK: start a recall at the end of every turn and cancel it at the start of the next (Mite 90% and Trzy
// Kwaterki 76% of their turns end in a recall; Intercontinental Fish doesn't). Effect unknown: tested by results.
inline constexpr bool RECALL_TRICK = false;
inline constexpr double ENEMY_SIDE = 0.85;

// Fights.
inline constexpr double FIGHT_RETREAT = 0.9;
inline constexpr double FIGHT_ENGAGE = 1.3;
// Enemy damage multiplier in the fight ratio: the top teams' stuns, resets, shields and passives aren't in our estimate
// (platform games vs the top 3: 52% of our deaths came while fighting, 48% against a single enemy).
inline constexpr double ENEMY_DPS_MUL = 1.0;
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
// FIGHT2 (2026-10-27, platform deaths vs mid-ladder teams): count only allies who can fight now (alive, not channelling,
// within FIGHT2_ALLY tiles, above 30% health); add enemy burst (abilities assumed ready), stuns and Heart of Ruin's
// passive; keep counting enemies seen in the last FIGHT2_MEMORY rounds (bushes hide them); hysteresis between
// FIGHT2_ENGAGE and FIGHT2_RETREAT once we have hit a champion; step out of reach of stronger enemies instead of
// farming beside them; flee by the safest next step (the old path to spawn flipped between two tiles each turn);
// ranged champions caught by melee with no escape fight back; focus fire through shared memory bytes 6-7; leave a
// camp fight when health is below 3 turns of its damage.
inline constexpr bool FIGHT2 = false;
inline constexpr int FIGHT2_ALLY = 4;
inline constexpr double FIGHT2_ENGAGE = 1.1;
inline constexpr double FIGHT2_RETREAT = 0.8;
inline constexpr double FIGHT2_HORIZON = 6.0;
inline constexpr int FIGHT2_MEMORY = 3;

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
// 2 = Treasure, then Bruiser only; 3/4/5 = 1 opening with Capture, Monster or Prospector instead of Treasure (cambc 4.0);
// 6 = the stronger platform teams' order: Jungle, Durability H, Monster, then Bruiser H and Bruiser S/F in turn.
inline constexpr int BUILD_30 = 4;
} // namespace bot
