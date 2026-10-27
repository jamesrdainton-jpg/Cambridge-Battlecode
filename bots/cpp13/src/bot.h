// Champion brain: shop, fight, tribute, farm. One instance per champion.
// C++ port of bots/mybot/src/bot.py (v13 code paths plus the cambc 3.0 flags in params.h). Function names match the
// Python so the two can be compared side by side. Code paths v13 never runs (boss poking, the stand-off breaker,
// telemetry, pack farming, debug logging) are not ported.
#pragma once
#include <cambc.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <string>
#include <tuple>
#include <type_traits>
#include <variant>
#include <vector>

#include "params.h"
#include "world.h"

namespace bot
{
using cambc::champion;
using cambc::team;

enum AbKind : int { K_NONE = 0, K_RESET = 1, K_DAMAGE = 2, K_AOE = 3, K_CC = 4, K_HEAL = 5, K_DASH = 6, K_SHIELD = 7 };

struct AbInfo
{
	int kind{ K_NONE };
	double modifier{ 0 }, range{ 0 }, radius{ 0 };
	int duration{ 0 };  // stun turns (Heart of Ruin's dash)
	bool exclusive{ false };
};

inline AbInfo read_ability(const cambc::ability& ab)
{
	AbInfo r;
	const auto& inf = ab.info();
	if (!inf) return r;
	std::visit(
		[&](const auto& v) {
			using T = std::decay_t<decltype(v)>;
			r.exclusive = v.exclusive_with_movement;
			if constexpr (std::is_same_v<T, cambc::ability_attack_reset>) r.kind = K_RESET;
			else if constexpr (std::is_same_v<T, cambc::ability_damage>) { r.kind = K_DAMAGE; r.modifier = v.modifier; r.range = v.range; }
			else if constexpr (std::is_same_v<T, cambc::ability_aoe_damage>) { r.kind = K_AOE; r.modifier = v.modifier; r.range = v.range; }
			else if constexpr (std::is_same_v<T, cambc::ability_cc>) { r.kind = K_CC; r.modifier = v.modifier; r.range = v.range; }
			else if constexpr (std::is_same_v<T, cambc::ability_heal>) { r.kind = K_HEAL; r.modifier = v.modifier; r.range = v.range; }
			else if constexpr (std::is_same_v<T, cambc::ability_dash>) { r.kind = K_DASH; r.modifier = v.modifier; r.range = v.range; r.radius = v.radius; r.duration = v.duration; }
			else if constexpr (std::is_same_v<T, cambc::ability_shield>) { r.kind = K_SHIELD; r.modifier = v.modifier; r.range = v.range; }
		},
		*inf);
	return r;
}

// Champion damage profile per type: strength multiplier, focus-per-turn multiplier, attack range. FIGHT2 also uses the
// burst of all abilities at once (focus and strength multipliers), the number of stuns, the reach of a threat next turn
// (move + dash + attack or the longest ability) and Heart of Ruin's missing-health passive.
struct Profile
{
	double str_mul{ 1.0 }, foc_mul{ 0.0 };
	int rng{ 1 };
	double burst_foc{ 0.0 }, burst_str{ 0.0 };
	int stuns{ 0 }, reach{ 2 };
	bool dash{}, hor{};
};

inline const Profile& profile(cambc::champion_type kind)
{
	static std::array<std::optional<Profile>, 16> cache{};
	int k = static_cast<int>(kind);
	if (k < 0 || k >= 16) k = 0;
	if (!cache[k])
	{
		Profile p;
		champion d{ kind };
		int ab_reach = 0;
		for (const auto& ab : d.abilities())
		{
			AbInfo i = read_ability(ab);
			if (i.kind == K_RESET)
			{
				p.str_mul += 0.125;
				p.burst_str += 1.0;
			}
			else if (i.kind == K_DAMAGE || i.kind == K_AOE || i.kind == K_CC)
			{
				p.foc_mul += i.modifier / 8.0;
				p.burst_foc += i.modifier;
				ab_reach = std::max(ab_reach, static_cast<int>(i.range + i.radius));
			}
			if (i.kind == K_CC || (i.kind == K_DASH && i.duration > 0)) ++p.stuns;
			if (i.kind == K_DASH)
			{
				p.dash = true;
				p.burst_foc += i.modifier;  // Heart of Ruin's landing damage
			}
		}
		p.rng = d.base_stats().base_attack_range;
		p.reach = std::max(p.rng + 1 + (p.dash ? 2 : 0) + (kind == cambc::champion_type::heart_of_ruin ? 1 : 0), ab_reach);
		p.hor = d.passive() == cambc::passive_type::missing_health_damage;
		cache[k] = p;
	}
	return *cache[k];
}

struct Stage
{
	cambc::item_type shard, emblem;
	int need;
};

inline std::vector<Stage> build_for(cambc::champion_type kind)
{
	using I = cambc::item_type;
	bool focus = kind == cambc::champion_type::stellar || kind == cambc::champion_type::prism || kind == cambc::champion_type::cassi ||
				 (META_BUILD && kind == cambc::champion_type::heart_of_ruin) ||
				 (TAVI_FOCUS && kind == cambc::champion_type::tavi);
	const Stage MS{ I::monster_shard_of_strength, I::monster_emblem_of_strength, 0 }, MF{ I::monster_shard_of_focus, I::monster_emblem_of_focus, 0 };
	const Stage PS{ I::power_shard_of_strength, I::power_emblem_of_strength, 0 }, PF{ I::power_shard_of_focus, I::power_emblem_of_focus, 0 };
	const Stage PH{ I::power_shard_of_health, I::power_emblem_of_health, 0 }, JH{ I::jungle_shard_of_health, I::jungle_emblem_of_health, 0 };
	const Stage DH{ I::durability_shard_of_health, I::durability_emblem_of_health, 0 };
	const Stage TS{ I::treasure_shard_of_strength, I::treasure_emblem_of_strength, 0 }, TF{ I::treasure_shard_of_focus, I::treasure_emblem_of_focus, 0 };
	const Stage BS{ I::bruiser_shard_of_strength, I::bruiser_emblem_of_strength, 0 }, BF{ I::bruiser_shard_of_focus, I::bruiser_emblem_of_focus, 0 };
	const Stage BH{ I::bruiser_shard_of_health, I::bruiser_emblem_of_health, 0 };
	const Stage CS{ I::capture_shard_of_strength, I::capture_emblem_of_strength, 0 }, CF{ I::capture_shard_of_focus, I::capture_emblem_of_focus, 0 };
	const Stage RS{ I::prospector_shard_of_strength, I::prospector_emblem_of_strength, 0 }, RF{ I::prospector_shard_of_focus, I::prospector_emblem_of_focus, 0 };
	auto at = [](Stage s, int n) { s.need = n; return s; };
	if (BUILD_30 == 6)
	{
		// The stronger platform teams' order (research/2026-10-27/tools/builds.py, 30 panel games, 2026-10-27): Jungle,
		// Durability H, Monster, then Bruiser H and Bruiser of the main stat in turn; Marcella, Heart of Ruin and Ren
		// build focus there too.
		bool f = focus || kind == cambc::champion_type::marcella || kind == cambc::champion_type::heart_of_ruin ||
				 kind == cambc::champion_type::ren;
		const Stage JS{ I::jungle_shard_of_strength, I::jungle_emblem_of_strength, 0 }, JF{ I::jungle_shard_of_focus, I::jungle_emblem_of_focus, 0 };
		const Stage& J = f ? JF : JS;
		const Stage& M6 = f ? MF : MS;
		const Stage& B6 = f ? BF : BS;
		return { at(J, 5), at(DH, 5), at(M6, 5), at(BH, 5), at(B6, 5), at(BH, 10), at(B6, 10), at(BH, 20), at(B6, 20), at(BH, 30), at(B6, 30), at(B6, 60) };
	}
	const Stage& M = focus ? MF : MS;
	const Stage& P = focus ? PF : PS;
	const Stage& T = focus ? TF : TS;
	const Stage& B = focus ? BF : BS;
	if (BUILD_30 == 1 || BUILD_30 >= 3)
	{
		// cambc 4.0: 3/4/5 open with Capture, Monster or Prospector instead of Treasure (see BUILD30_FIRST in bot.py).
		const Stage& first = BUILD_30 == 3 ? (focus ? CF : CS) : BUILD_30 == 4 ? M : BUILD_30 == 5 ? (focus ? RF : RS) : T;
		return { at(first, 5), at(JH, 5), at(B, 5), at(DH, 5), at(B, 10), at(BH, 5), at(B, 20), at(BH, 10), at(B, 30), at(BH, 20), at(B, 60) };
	}
	if (BUILD_30 == 2)
		return { at(T, 5), at(B, 5), at(BH, 5), at(B, 10), at(BH, 10), at(B, 20), at(BH, 20), at(B, 60) };
	return { at(M, 5), at(P, 5), at(JH, 5), at(P, 10), at(DH, 5), at(P, 30), at(PH, 30), at(P, 60) };
}

// A visible enemy champion: (unit, position, health, attack range, dps, distance, carried gems), as in bot.py.
struct Near
{
	champion e;
	vec2 p;
	double hp;
	int rng;
	double dps;
	int d;
	int gems;
	bool stunned{};
	int reach{ 2 };  // FIGHT2: tiles it can threaten next turn
};

// A visible camp of a known group: (camp, group index, kind, spawn cell, health, index in the group).
struct CampInfo
{
	cambc::camp c;
	int g;
	int k;
	vec2 p;
	double hp;
	int li;
};

struct Scored
{
	double score;
	int g;
	int need;
	bool via;
};

class Bot
{
public:
	Bot() : me{ cambc::self() }, abilities{ cambc::self().abilities() }
	{
		handle = static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(me));
		kind = me.champion_name();
		auto stats = me.base_stats();
		ranged = stats.base_attack_range > 1;
		rng = stats.base_attack_range;
		for (const auto& c : cambc::champions(team::ally)) ally_handles.push_back(static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(c)));
		std::sort(ally_handles.begin(), ally_handles.end());
		auto it = std::find(ally_handles.begin(), ally_handles.end(), handle);
		slot = it != ally_handles.end() ? static_cast<int>(it - ally_handles.begin()) : 0;
		n_allies = static_cast<int>(ally_handles.size());
		for (int i = 0; i < 2; ++i) ab[i] = read_ability(abilities[static_cast<std::size_t>(i)]);
		build = build_for(kind);
		splash = me.passive() == cambc::passive_type::splash_attack;
		for (int i = 0; i < 2; ++i)
			if (ab[i].kind == K_AOE) aoe_mod += ab[i].modifier / 8.0;
		remote_shop = kind == cambc::champion_type::tavi;
		for (int i = 0; i < 2; ++i)
			if (ab[i].kind == K_DASH && ab[i].radius > 0 && ab[i].duration > 0) stun_dash = i;
		fragile = META_CASSI && kind == cambc::champion_type::cassi;
		if (META_PAIR && kind == cambc::champion_type::cassi)
		{
			for (const auto& c : cambc::champions(team::ally))
			{
				if (c.champion_name() != cambc::champion_type::issac) continue;
				auto h = static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(c));
				auto at = std::find(ally_handles.begin(), ally_handles.end(), h);
				if (at != ally_handles.end()) partner_slot = static_cast<int>(at - ally_handles.begin());
			}
		}
		locked = LOCKED_GOLD && cambc::draft_memory.size() > 0 && (static_cast<unsigned>(cambc::draft_memory[0]) & 1u) != 0;
		const auto& af = world.altar_field();
		for (auto& g : world.groups) g.near_altar = af.get(g.anchor);
		spawn_dist = world.spawn_field().export_linear_buffer();
		spawn_altar = af.get(world.spawn_center);
	}

	void turn()
	{
		act = "?";
		if (RECALL_TRICK && trick_recall)
		{
			// Started at the end of last turn only to be standing in a recall (as Mite and Trzy Kwaterki do every turn).
			trick_recall = false;
			try
			{
				if (me.state().contains(cambc::champion_state::recalling)) me.cancel_recall();  // damage may have ended it
			}
			catch (const std::exception&)
			{
			}
		}
		_turn();
		if (WARDS && act != "dead" && act != "recall" && act != "submit" && act != "tp" && act != "?") ward_bush();
		if (RECALL_TRICK && act != "dead" && act != "recall" && act != "submit" && act != "tp" && act != "go_recall" &&
			act != "recall_travel")
		{
			try
			{
				me.recall();
				trick_recall = true;
			}
			catch (const cambc::error&)
			{
			}
		}
	}

	void end()
	{
		try
		{
			last_hp = me.health();
		}
		catch (...)
		{
		}
	}

private:
	World world;
	champion& me;
	std::uint32_t handle{};
	cambc::champion_type kind{};
	bool ranged{};
	int rng{ 1 };
	std::vector<std::uint32_t> ally_handles;
	int slot{}, n_allies{ 1 };
	std::array<cambc::ability, 2> abilities;
	AbInfo ab[2];
	std::vector<Stage> build;
	std::size_t build_done{};
	std::optional<vec2> ward_at;
	bool splash{};
	double aoe_mod{};
	bool remote_shop{};
	bool locked{};  // no altar reachable without killing a camp (draft memory; LOCKED_GOLD)
	int stun_dash{ -1 };  // META_PLAY: slot of a dash that damages and stuns around its landing tile (Heart of Ruin)
	bool cc_camp_ok{};    // META_PLAY: a pure stun may target the camp being attacked (it hits back)
	int partner_slot{ -1 };  // META_PAIR: Cassi's partner Issac (shared-memory slot); she takes his target
	bool trick_recall{};     // RECALL_TRICK: a recall we started at the end of last turn, to cancel now
	bool fragile{};          // META_CASSI: Cassi (600 HP) waits for a tank at camps and leaves fights at half health
	// FIGHT2: enemy champions as last seen (they stay a threat for FIGHT2_MEMORY rounds after a bush hides them).
	struct Ghost
	{
		std::uint32_t h;
		vec2 p;
		int round;
		double hp, dps, burst;
		int reach;
	};
	std::vector<Ghost> ghosts;
	int last_champ_hit{ -100 };  // FIGHT2: round we last hit an enemy champion (hysteresis)
	int open_checked{ -100 };    // LOCKED_OPEN: last altar reachability check, and its answer
	bool open_now{};
	int target{ -1 };
	int target_round{ -100 };
	std::optional<double> last_hp;
	int idle_turns{}, wait_turns{};
	bool has_lock{};
	std::set<std::pair<int, int>> locked_altars;
	int enemy_seen{ -1000 };
	std::map<std::uint32_t, cambc::champion_type> kinds;
	int target_need{ 1 };
	bool target_via{};
	std::vector<std::uint16_t> spawn_dist;
	int spawn_altar{ UNREACHED };
	int commit_until{ -1 };
	std::optional<int> help_last;
	std::optional<vec2> help_call, my_call;
	int prio{};
	std::optional<vec2> aoe_pos;
	int choice_round{ -1 };
	std::vector<Scored> choice;
	std::vector<CampInfo> camp_info;
	std::set<int> awake;
	std::map<int, bitboard> zones;
	std::map<int, int> ready;
	// Per turn.
	std::string act;
	int now{};
	vec2 pos{};
	double hp{}, max_hp{ 1 };
	int gems{}, gold{};
	double strength_now{}, focus_now{}, dps_now{};
	bool at_spawn{};
	int dash_slot{ -1 };
	bitboard occ;
	std::vector<champion> enemies, allies;
	std::vector<cambc::camp> camps;
	bool can_move{}, can_attack{}, can_cast{};

	Group& G(int i) { return world.groups[static_cast<std::size_t>(i)]; }

	static std::string name_of(cambc::champion_type k)
	{
		auto s = cambc::to_string(k);
		auto dot = s.rfind(':');
		return dot == std::string::npos ? s : s.substr(dot + 1);
	}

	void log(const std::string& msg) { std::cout << "r" << now << " " << name_of(kind) << " " << msg << std::endl; }

	bitboard occupancy()
	{
		bitboard o = cambc::vision::champion_tiles() | cambc::vision::camp_tiles() | cambc::vision::teleport_tiles();
		o.set(pos, false);
		return o;
	}

	// Walk one step (plus a dash if available) towards the root tiles, steering clear of the avoid tiles when possible.
	bool go(const bitboard& roots_in, bool allow_dash = true, const bitboard* avoid = nullptr)
	{
		if (!can_move) return false;
		bitboard roots = roots_in & ~occ;
		if (roots.is_empty() || roots.is_set(pos)) return false;
		bitboard walls = world.block | occ;
		distance_field field;
		bitboard visited, stop_at;
		stop_at.set(pos);
		int here = UNREACHED;
		// compute_to stops once our tile is reached: every tile nearer the roots is already final, so the step and the
		// dash below are the same as with a full-map search, for a fraction of the fuel (a full 100x100 search is ~30%
		// of a C++ turn; the C++ port hit its fuel cap on 14% of big-world turns before this).
		if (avoid && !avoid->is_empty())
		{
			bitboard soft = walls | (*avoid & ~roots);
			soft.set(pos, false);
			field.compute_to(soft, roots, stop_at, visited);
			here = field.get(pos);
		}
		if (here >= UNREACHED)
		{
			field.compute_to(walls, roots, stop_at, visited);
			here = field.get(pos);
		}
		if (here >= UNREACHED) return false;
		if (allow_dash && here >= 3 && can_cast && dash_slot >= 0 && !(META_PLAY && dash_slot == stun_dash && now - enemy_seen < 10))
		{
			const auto& dab = abilities[static_cast<std::size_t>(dash_slot)];
			if (dab.cooldown() == 0)
			{
				auto d1 = field.next_move_from(pos);
				if (d1)
				{
					vec2 p1 = pos + *d1;
					auto d2 = field.next_move_from(p1);
					if (d2)
					{
						vec2 p2 = p1 + *d2;
						try
						{
							if (dab.use(p2))
							{
								pos = p2;
								can_cast = false;
								here = field.get(p2);
								if (here == 0) return true;
							}
						}
						catch (const cambc::error&)
						{
						}
					}
				}
			}
		}
		auto step = field.next_move_from(pos);
		if (!step) return false;
		vec2 dest = pos + *step;
		bool ok = false;
		try
		{
			ok = me.move_absolute(dest);
		}
		catch (const cambc::error&)
		{
			return false;
		}
		if (ok)
		{
			pos = dest;
			can_move = false;
			if (ranged) can_attack = false;
		}
		return ok;
	}

	void ward_bush()
	{
		if (ward_at && cheb(*ward_at, pos) <= 4) return;
		bitboard near;
		near.draw_chebyshev(pos, 2);
		near &= world.bushes;
		if (near.is_empty()) return;
		vec2 focus = target >= 0 ? G(target).anchor : world.enemy_spawn_center;
		std::optional<vec2> best;
		int best_d = 999;
		for (auto p : near.positions())
		{
			int d = cheb(p, focus);
			if (d < best_d)
			{
				best_d = d;
				best = p;
			}
		}
		try
		{
			if (best && me.place_ward(*best)) ward_at = best;
		}
		catch (const cambc::error&)
		{
		}
	}

	void _turn()
	{
		now = static_cast<int>(cambc::round_number());
		cc_camp_ok = false;
		if (slot == 0 && now % 25 == 0)
			std::cout << "STAT " << now << " " << cambc::global_submitted_gems(team::ally) << " " << cambc::global_submitted_gems(team::enemy) << std::endl;
		auto st = me.state();
		can_move = st.contains(cambc::champion_state::can_move);
		can_attack = st.contains(cambc::champion_state::can_attack);
		can_cast = st.contains(cambc::champion_state::can_cast);
		if (!st.contains(cambc::champion_state::alive))
		{
			at_spawn = false;
			if (target >= 0)
			{
				target = -1;
				claim(-1);
			}
			shop(true);
			act = "dead";
			return;
		}
		if (st.contains(cambc::champion_state::recalling) || st.contains(cambc::champion_state::submitting_gems) ||
			st.contains(cambc::champion_state::teleporting))
		{
			act = st.contains(cambc::champion_state::recalling) ? "recall" : (st.contains(cambc::champion_state::submitting_gems) ? "submit" : "tp");
			return;
		}
		pos = me.position();
		hp = me.health();
		max_hp = me.max_health();
		gems = static_cast<int>(me.gem_count());
		gold = static_cast<int>(me.gold_count());
		const auto& prof = profile(kind);
		strength_now = me.strength();
		focus_now = me.focus();
		dps_now = strength_now * prof.str_mul + focus_now * prof.foc_mul;
		at_spawn = world.my_spawn.is_set(pos);
		dash_slot = -1;
		for (int i = 0; i < 2; ++i)
			if (ab[i].kind == K_DASH) dash_slot = i;
		if (at_spawn || remote_shop) shop(false);
		occ = occupancy();
		enemies = cambc::champions(team::enemy);
		allies.clear();
		for (const auto& a : cambc::champions(team::ally))
			if (static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(a)) != handle) allies.push_back(a);
		camps = cambc::vision::camps();
		if (has_lock) place_lock();
		update_knowledge();
		if (HELP_CALLS) help_call = read_help();
		if (!enemies.empty() && (FIGHT2 ? fight2() : fight()))
		{
			act = "fight";
			if (FIGHT_PRIO) set_prio(10);
			return;
		}
		if (FIGHT_PRIO) set_prio(0);
		if (HELP_CALLS && answer_help())
		{
			act = "help";
			return;
		}
		if (maybe_recall())
		{
			act = "go_recall";
			return;
		}
		if (gems > 0 && want_tribute())
		{
			act = "to_altar";
			tribute();
			return;
		}
		act = "farm";
		farm();
	}

	// ------------------------------------------------------------------ shop
	void shop(bool dead)
	{
		int g = static_cast<int>(me.gold_count());
		if (ALTAR_LOCKS && g >= 10 && (dead || at_spawn))
		{
			try
			{
				has_lock = me.consumables()[cambc::consumable_type::altar_lock].count() > 0;
				if (!has_lock && me.can_buy(cambc::consumable_type::altar_lock))
				{
					me.buy(cambc::consumable_type::altar_lock);
					has_lock = true;
					g -= 10;
				}
			}
			catch (const cambc::error&)
			{
			}
		}
		if (g < 30) return;
		std::optional<cambc::enum_map<cambc::item_type>> counts;
		while (build_done < build.size())
		{
			const Stage& s = build[build_done];
			if (!counts) counts = me.item_count();
			int owned = static_cast<int>((*counts)[s.shard]) + 5 * static_cast<int>((*counts)[s.emblem]);
			if (owned >= s.need)
			{
				++build_done;
				continue;
			}
			if (g < 30) break;
			int n = std::min(s.need - owned, g / 30);
			try
			{
				me.buy(s.shard, static_cast<std::uint32_t>(n));
			}
			catch (const cambc::error& e)
			{
				log(std::string("buy failed ") + e.what());
				++build_done;
				continue;
			}
			g -= 30 * n;
			counts = me.item_count();
		}
	}

	// ------------------------------------------------------------------ knowledge
	void update_knowledge()
	{
		std::set<int> seen;
		camp_info.clear();
		awake.clear();
		for (const auto& c : camps)
		{
			std::uint32_t h = camp_handle(c);
			if (h >= world.camp_g.size() || world.camp_g[h] < 0) continue;
			Group& g = G(world.camp_g[h]);
			int li = world.camp_li[h];
			double chp;
			try
			{
				chp = c.health();
			}
			catch (const cambc::error&)
			{
				continue;  // listed in vision but not readable this turn (cambc 3.0 quirk)
			}
			int k = g.kinds[li];  // known since the first turn: saves an engine call per visible camp
			camp_info.push_back(CampInfo{ c, g.idx, k, g.cells[li], chp, li });
			if (g.hp[li] != chp)
			{
				g.hp[li] = chp;
				g.refresh_hp();
			}
			if (chp < stat(k).hp) awake.insert(g.idx);
			g.status = ALIVE;
			g.seen = now;
			seen.insert(g.idx);
		}
		zones.clear();
		if (!awake.empty())
		{
			for (const auto& ci : camp_info)
			{
				if (awake.count(ci.g) && stat(ci.k).str > 0) zones[ci.g].draw_chebyshev(ci.p, static_cast<float>(stat(ci.k).rng));
			}
		}
		std::optional<bitboard> vis;
		int px = pos.x, py = pos.y, bx = px / 10, by = py / 10;
		for (int gx = bx - 1; gx <= bx + 1; ++gx)
			for (int gy = by - 1; gy <= by + 1; ++gy)
			{
				auto bit = world.buckets.find({ gx, gy });
				if (bit == world.buckets.end()) continue;
				for (int gi : bit->second)
				{
					Group& g = G(gi);
					if (seen.count(gi)) continue;
					int dx = g.ax - px, dy = g.ay - py;
					if (dx > 9 || dx < -9 || dy > 9 || dy < -9) continue;
					if (g.status == RESPAWN && now < g.alive_at - 2) continue;
					if (!vis) vis = cambc::vision::visible_tiles();
					if ((*vis & g.tiles).is_empty()) continue;
					cambc::map::camp_group_state state;
					try
					{
						state = g.obj.state();
					}
					catch (const cambc::error&)
					{
						continue;
					}
					g.seen = now;
					if (auto r = std::get_if<cambc::map::camp_group_respawning>(&state))
					{
						g.status = RESPAWN;
						g.alive_at = now + r->timer;
						g.reset_hp();
					}
					else if (std::holds_alternative<cambc::map::camp_group_reward_available>(state))
						g.status = REWARD;
					else
						g.status = ALIVE;
				}
			}
	}

	// ------------------------------------------------------------------ combat
	bool taking_damage() const { return last_hp && hp < *last_hp; }

	bool fight()
	{
		std::vector<Near> near;
		const bitboard* campers = (IGNORE_SPAWN_CAMPERS && !taking_damage()) ? &world.enemy_spawn : nullptr;
		for (auto& e : enemies)
		{
			vec2 ep;
			try
			{
				// Out-of-vision enemies throw on position(); C++ exceptions cost ~4k fuel each in wasm, so ask first.
				if (!e.is_visible()) continue;
				ep = e.position();
			}
			catch (const cambc::error&)
			{
				continue;
			}
			if (campers && campers->is_set(ep)) continue;
			int d = cheb(ep, pos);
			if (d <= 10) enemy_seen = now;
			if (d > 9) continue;
			try
			{
				std::uint32_t h = static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(e));
				auto kit = kinds.find(h);
				if (kit == kinds.end()) kit = kinds.emplace(h, e.champion_name()).first;
				double ehp = e.health();
				const auto& prof = profile(kit->second);
				double dps = e.strength() * prof.str_mul + e.focus() * prof.foc_mul;
				int eg = static_cast<int>(e.gem_count());
				bool stunned = META_PLAY && e.restrictions().contains(cambc::buff_restrictions::attack);
				if (stunned) dps *= 0.3;  // loses its next turn
				near.push_back(Near{ e, ep, ehp, prof.rng, dps, d, eg, stunned });
			}
			catch (const cambc::error&)
			{
				continue;
			}
		}
		if (near.empty()) return false;
		int dmin = 999;
		for (const auto& x : near) dmin = std::min(dmin, x.d);
		if (HELP_CALLS && dmin <= 4) call_help();
		if (!zones.empty() && taking_damage() && hp < 0.5 * max_hp)
		{
			auto dz = danger(-1);
			if (dmin > 4 && dz && dz->is_set(pos))
			{
				bitboard zone;
				for (const auto& x : near) zone.draw_chebyshev(x.p, static_cast<float>(x.rng + 1));
				if (escape(&zone)) return true;
			}
		}
		double our_hp = hp, our_dps = dps_now;
		for (auto& a : allies)
		{
			try
			{
				if (!a.is_visible()) continue;
				vec2 ap = a.position();
				if (cheb(ap, pos) > ALLY_RANGE) continue;
				double ahp = a.health();
				const auto& prof = profile(a.champion_name());
				double adps = a.strength() * prof.str_mul + a.focus() * prof.foc_mul;
				our_hp += ahp;
				our_dps += adps;
			}
			catch (const cambc::error&)
			{
			}
		}
		double their_hp = 0, their_dps = 0;
		for (const auto& x : near)
		{
			double w = x.d <= 7 ? 1.0 : 0.5;
			their_hp += w * x.hp;
			their_dps += w * x.dps;
		}
		double ratio = (our_hp * our_dps) / std::max(1.0, their_hp * their_dps * ENEMY_DPS_MUL);
		int home = world.spawn_field().get(pos);
		if (home <= 6) ratio *= 1.4;
		if (cheb(pos, world.enemy_spawn_center) <= 7) ratio *= 0.6;
		int closest = 999;
		for (const auto& x : near) closest = std::min(closest, x.d - x.rng);
		double frac = hp / max_hp;
		double burst_dmg = burst();
		for (auto& x : near)
		{
			if (x.d <= rng && x.hp <= burst_dmg)
			{
				hit_champion(x.e, x.p);
				return true;
			}
		}
		if (FIGHT_SHIELD) shield_up(closest);
		double extra = gems >= 20 ? FIGHT_GEM_EXTRA : 0.0;
		double retreat_at = FIGHT_RETREAT + extra, engage_at = FIGHT_ENGAGE + extra;
		if (ratio < retreat_at || (frac < (fragile ? 0.5 : LOW_HP_RETREAT) && closest <= LOW_HP_REACH))
		{
			if ((STAND_REACH != 0 || FIGHT_COMMIT != 0 || HELP_CALLS) && fight30_stand(near, frac)) return true;
			if (!ranged && can_attack)
			{
				const Near* weakest = nullptr;
				for (const auto& x : near)
					if (x.d <= rng && (!weakest || x.hp < weakest->hp)) weakest = &x;
				if (weakest) basic_attack_champion(weakest->e);
			}
			retreat(near);
			return true;
		}
		const Near* best = &near[0];
		double best_v = -1.0;
		for (const auto& x : near)
		{
			double v = (100.0 + 2.0 * x.gems) / (x.hp + 50.0);
			if (x.d <= rng) v *= 2.0;
			if (x.stunned) v *= 1.5;
			v /= 1.0 + 0.1 * x.d;
			if (v > best_v)
			{
				best_v = v;
				best = &x;
			}
		}
		bool engage = ratio >= engage_at || (FIGHT_COMMIT != 0 && now < commit_until);
		if (META_STUN_COMMIT && best->stunned && best->d <= 4 && frac >= LOW_HP_RETREAT) engage = true;  // pile onto a stunned enemy
		if (META_PLAY && stun_dash >= 0 && (engage || best->hp <= 2 * burst_dmg))
		{
			std::vector<vec2> tg;
			for (const auto& x : near)
				if (x.d <= 3) tg.push_back(x.p);
			if (dash_stun(tg, 1, best->p))
			{
				const Near* hitme = cheb(best->p, pos) <= rng ? best : nullptr;
				for (const auto& x : near)
					if (!hitme && cheb(x.p, pos) <= rng) hitme = &x;
				if (hitme) hit_champion(hitme->e, hitme->p);
				return true;
			}
		}
		if (best->d <= rng)
		{
			hit_champion(best->e, best->p);
			return true;
		}
		const Near* weakest = nullptr;
		for (const auto& x : near)
			if (x.d <= rng && (!weakest || x.hp < weakest->hp)) weakest = &x;
		if (weakest && can_attack && (!ranged || !engage))
		{
			if (basic_attack_champion(weakest->e)) use_reset_champion(weakest->e);
		}
		if (cast_offense_champion(best->e, best->p) && !engage) return true;
		if (engage && best->d <= 5 && cheb(best->p, world.enemy_spawn_center) > 3)
		{
			bitboard roots;
			roots.draw_chebyshev(best->p, static_cast<float>(rng));
			go(roots, true);
			if (cheb(best->p, pos) <= rng)
			{
				basic_attack_champion(best->e);
				use_reset_champion(best->e);
			}
			return true;
		}
		if (!engage && closest <= 2) return true;
		return false;
	}

	// ------------------------------------------------------------------ FIGHT2
	// Damage over a short fight: sustained damage plus a share of the burst of all abilities (assumed ready unless
	// burst_scale says otherwise) and a turn of an average champion per stun, scaled by Heart of Ruin's passive.
	static double power_dps(const Profile& prof, double str, double foc, double h, double mh, double burst_scale)
	{
		double dps = str * prof.str_mul + foc * prof.foc_mul;
		dps += burst_scale * (foc * prof.burst_foc + str * prof.burst_str + 60.0 * prof.stuns) / FIGHT2_HORIZON;
		if (prof.hor && mh > 0) dps *= 1.0 + 0.5 * std::max(0.0, 1.0 - h / mh);
		return dps;
	}

	// Our own fighting damage: exact burst from the abilities that are off cooldown now.
	double my_power()
	{
		const auto& prof = profile(kind);
		double ready = 0;
		for (int i = 0; i < 2; ++i)
		{
			if (abilities[static_cast<std::size_t>(i)].cooldown() != 0) continue;
			int k = ab[i].kind;
			if (k == K_DAMAGE || k == K_AOE || k == K_CC || k == K_DASH) ready += focus_now * ab[i].modifier;
			if (k == K_RESET) ready += strength_now;
			if (k == K_CC || (k == K_DASH && ab[i].duration > 0)) ready += 60.0;
		}
		double dps = dps_now + ready / FIGHT2_HORIZON;
		if (prof.hor) dps *= 1.0 + 0.5 * std::max(0.0, 1.0 - hp / max_hp);
		return dps;
	}

	bool fight2()
	{
		std::vector<Near> near;
		const bitboard* campers = (IGNORE_SPAWN_CAMPERS && !taking_damage()) ? &world.enemy_spawn : nullptr;
		double their_hp = 0, their_dps = 0;
		std::vector<std::uint32_t> seen_now;
		for (auto& e : enemies)
		{
			vec2 ep;
			try
			{
				if (!e.is_visible()) continue;
				ep = e.position();
			}
			catch (const cambc::error&)
			{
				continue;
			}
			if (campers && campers->is_set(ep)) continue;
			int d = cheb(ep, pos);
			if (d <= 10) enemy_seen = now;
			if (d > 9) continue;
			try
			{
				std::uint32_t h = static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(e));
				auto kit = kinds.find(h);
				if (kit == kinds.end()) kit = kinds.emplace(h, e.champion_name()).first;
				const auto& prof = profile(kit->second);
				double ehp = e.health();
				double dps = power_dps(prof, e.strength(), e.focus(), ehp, e.max_health(), 1.0);
				bool stunned = e.restrictions().contains(cambc::buff_restrictions::attack);
				if (stunned) dps *= 0.75;  // loses its next turn
				int eg = static_cast<int>(e.gem_count());
				near.push_back(Near{ e, ep, ehp, prof.rng, dps, d, eg, stunned, prof.reach });
				seen_now.push_back(h);
				double w = d <= 7 ? 1.0 : 0.6;
				their_hp += w * ehp;
				their_dps += w * dps;
				auto git = std::find_if(ghosts.begin(), ghosts.end(), [&](const Ghost& g) { return g.h == h; });
				if (git == ghosts.end())
					ghosts.push_back(Ghost{ h, ep, now, ehp, dps, 0.0, prof.reach });
				else
					*git = Ghost{ h, ep, now, ehp, dps, 0.0, prof.reach };
			}
			catch (const cambc::error&)
			{
				continue;
			}
		}
		// Enemies that just slipped out of sight (into a bush) still count, at a discount.
		for (auto it = ghosts.begin(); it != ghosts.end();)
		{
			if (now - it->round > FIGHT2_MEMORY)
			{
				it = ghosts.erase(it);
				continue;
			}
			if (it->round != now && cheb(it->p, pos) <= 7)
			{
				their_hp += 0.6 * it->hp;
				their_dps += 0.6 * it->dps;
			}
			++it;
		}
		if (near.empty()) return false;
		int dmin = 999;
		for (const auto& x : near) dmin = std::min(dmin, x.d);
		if (!zones.empty() && taking_damage() && hp < 0.5 * max_hp)
		{
			auto dz = danger(-1);
			if (dmin > 4 && dz && dz->is_set(pos))
			{
				bitboard zone;
				for (const auto& x : near) zone.draw_chebyshev(x.p, static_cast<float>(x.rng + 1));
				if (escape(&zone)) return true;
			}
		}
		// Only allies who can fight now: alive, not channelling, close, and not about to run themselves.
		double our_hp = hp, our_dps = my_power();
		for (auto& a : allies)
		{
			try
			{
				if (!a.is_visible()) continue;
				vec2 ap = a.position();
				if (cheb(ap, pos) > FIGHT2_ALLY) continue;
				auto st = a.state();
				if (!st.contains(cambc::champion_state::alive) || st.contains(cambc::champion_state::recalling) ||
					st.contains(cambc::champion_state::submitting_gems) || st.contains(cambc::champion_state::teleporting))
					continue;
				double ahp = a.health(), amax = a.max_health();
				if (ahp < 0.3 * amax) continue;
				our_hp += ahp;
				our_dps += power_dps(profile(a.champion_name()), a.strength(), a.focus(), ahp, amax, 0.5);
			}
			catch (const cambc::error&)
			{
			}
		}
		double ratio = (our_hp * our_dps) / std::max(1.0, their_hp * their_dps * ENEMY_DPS_MUL);
		int home = world.spawn_field().get(pos);
		if (home <= 6) ratio *= 1.4;
		if (cheb(pos, world.enemy_spawn_center) <= 7) ratio *= 0.6;
		int closest = 999;
		bool threatened = false;
		for (const auto& x : near)
		{
			closest = std::min(closest, x.d - x.rng);
			if (x.d <= x.reach) threatened = true;
		}
		double frac = hp / max_hp;
		double burst_dmg = burst();
		for (auto& x : near)
		{
			if (x.d <= rng && x.hp <= burst_dmg)
			{
				hit_champion(x.e, x.p);
				return true;
			}
		}
		if (FIGHT_SHIELD) shield_up(closest);
		double extra = gems >= 20 ? FIGHT_GEM_EXTRA : 0.0;
		bool committed = now - last_champ_hit <= 2;
		double retreat_at = FIGHT2_RETREAT + extra;
		double engage_at = (committed ? FIGHT2_RETREAT : FIGHT2_ENGAGE) + extra;
		if (ratio < retreat_at || (frac < (fragile ? 0.5 : LOW_HP_RETREAT) && closest <= LOW_HP_REACH))
		{
			retreat2(near);
			return true;
		}
		const Near* weakest = nullptr;
		for (const auto& x : near)
			if (x.d <= rng && (!weakest || x.hp < weakest->hp)) weakest = &x;
		if (ratio < engage_at)
		{
			// Not strong enough to start a fight: hit back what is in range, and don't farm inside a stronger enemy's
			// reach (74% of our platform deaths came after 11+ rounds near an enemy).
			if (threatened && ratio < 1.0)
			{
				retreat2(near);
				return true;
			}
			if (weakest && can_attack && !ranged)
			{
				if (basic_attack_champion(weakest->e)) use_reset_champion(weakest->e);
			}
			else if (weakest && ranged)
				hit_champion(weakest->e, weakest->p);
			return closest <= 2;
		}
		// Engage: focus the champion our others are hitting (shared memory bytes 6-7: handle, round).
		int focus_h = -1;
		if (!HELP_CALLS)
		{
			try
			{
				int fr = static_cast<std::uint8_t>(cambc::shared_memory[7]);
				if (fr == (now & 255) || fr == ((now - 1) & 255)) focus_h = static_cast<std::uint8_t>(cambc::shared_memory[6]);
			}
			catch (...)
			{
			}
		}
		const Near* best = &near[0];
		double best_v = -1.0;
		for (const auto& x : near)
		{
			double v = (100.0 + 2.0 * x.gems) / (x.hp + 50.0);
			if (x.d <= rng) v *= 2.0;
			if (x.stunned) v *= 1.5;
			if (focus_h >= 0 && x.d <= rng + 1 &&
				static_cast<int>(static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(x.e)) & 255) == focus_h)
				v *= 2.0;
			v /= 1.0 + 0.1 * x.d;
			if (v > best_v)
			{
				best_v = v;
				best = &x;
			}
		}
		if (!HELP_CALLS)
		{
			try
			{
				cambc::shared_memory[6] = static_cast<std::uint8_t>(static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(best->e)) & 255);
				cambc::shared_memory[7] = static_cast<std::uint8_t>(now & 255);
			}
			catch (...)
			{
			}
		}
		if (META_PLAY && stun_dash >= 0)
		{
			std::vector<vec2> tg;
			for (const auto& x : near)
				if (x.d <= 3) tg.push_back(x.p);
			if (dash_stun(tg, 1, best->p))
			{
				const Near* hitme = cheb(best->p, pos) <= rng ? best : nullptr;
				for (const auto& x : near)
					if (!hitme && cheb(x.p, pos) <= rng) hitme = &x;
				if (hitme) hit_champion(hitme->e, hitme->p);
				return true;
			}
		}
		if (best->d <= rng)
		{
			hit_champion(best->e, best->p);
			return true;
		}
		if (weakest && can_attack && !ranged)
		{
			if (basic_attack_champion(weakest->e)) use_reset_champion(weakest->e);
		}
		cast_offense_champion(best->e, best->p);
		if (best->d <= 5 && cheb(best->p, world.enemy_spawn_center) > 3)
		{
			bitboard roots;
			roots.draw_chebyshev(best->p, static_cast<float>(rng));
			go(roots, true);
			if (cheb(best->p, pos) <= rng)
			{
				basic_attack_champion(best->e);
				use_reset_champion(best->e);
			}
			return true;
		}
		return closest <= 2;
	}

	void retreat2(const std::vector<Near>& near)
	{
		const Near* weakest = nullptr;
		for (const auto& x : near)
			if (x.d <= rng && (!weakest || x.hp < weakest->hp)) weakest = &x;
		// A melee champion can attack and then move: hit on the way out.
		if (!ranged && can_attack && weakest)
		{
			if (basic_attack_champion(weakest->e)) use_reset_champion(weakest->e);
		}
		if (at_spawn) return;
		// A ranged champion caught by melee with no dash, far from home: running only gives free hits, so shoot back.
		if (ranged && weakest)
		{
			bool melee_on_me = false;
			for (const auto& x : near)
				if (x.d <= 1 && x.rng <= 1) melee_on_me = true;
			bool dash_ready = dash_slot >= 0 && can_cast && abilities[static_cast<std::size_t>(dash_slot)].cooldown() == 0;
			if (melee_on_me && !dash_ready && world.spawn_field().get(pos) > 4)
			{
				hit_champion(weakest->e, weakest->p);
				return;
			}
		}
		int far = 999;
		for (const auto& x : near) far = std::min(far, x.d);
		auto camps_zone = danger(-1);
		bool in_camp = camps_zone && camps_zone->is_set(pos);
		if (far >= 8 && !in_camp && world.spawn_field().get(pos) > 8 && try_recall()) return;
		flee2(near, camps_zone ? &*camps_zone : nullptr);
	}

	// Step (or dash) to the neighbouring tile least inside the enemies' reach, then nearest home. No path is kept, so it
	// can't flip between two routes as the old retreat did when the soft-avoid path changed each turn.
	bool flee2(const std::vector<Near>& near, const bitboard* camp_zone)
	{
		if (!can_move) return false;
		const auto& sf = world.spawn_field();
		int here_sd = sf.get(pos);
		auto score = [&](vec2 t) {
			double threat = 0;
			int dclose = 99;
			for (const auto& x : near)
			{
				int d = cheb(t, x.p);
				threat += x.dps * std::max(0, x.reach + 1 - d);
				dclose = std::min(dclose, d);
			}
			for (const auto& g : ghosts)
				if (g.round != now) threat += 0.5 * g.dps * std::max(0, g.reach + 1 - cheb(t, g.p));
			int sd = sf.get(t);
			double s = -threat / 40.0 + 0.6 * (static_cast<double>(here_sd) - sd) + 0.2 * std::min(dclose, 8);
			if (camp_zone && camp_zone->is_set(t)) s -= 5.0;
			return s;
		};
		vec2 best = pos;
		double best_s = score(pos);
		bool best_dash = false;
		for (int dx = -1; dx <= 1; ++dx)
			for (int dy = -1; dy <= 1; ++dy)
			{
				if (dx == 0 && dy == 0) continue;
				vec2 t{ pos.x + dx, pos.y + dy };
				if (t.x < 0 || t.y < 0 || t.x >= world.w || t.y >= world.h) continue;
				if (world.block.is_set(t) || occ.is_set(t) || sf.get(t) >= UNREACHED) continue;
				double s = score(t);
				if (s > best_s)
				{
					best_s = s;
					best = t;
				}
			}
		if (dash_slot >= 0 && can_cast && abilities[static_cast<std::size_t>(dash_slot)].cooldown() == 0)
		{
			double step_best = best_s;
			for (int dx = -2; dx <= 2; ++dx)
				for (int dy = -2; dy <= 2; ++dy)
				{
					if (std::max(std::abs(dx), std::abs(dy)) != 2) continue;
					vec2 t{ pos.x + dx, pos.y + dy };
					if (t.x < 0 || t.y < 0 || t.x >= world.w || t.y >= world.h) continue;
					if (world.block.is_set(t) || occ.is_set(t) || sf.get(t) >= UNREACHED) continue;
					bool path = false;
					for (int mx = -1; mx <= 1 && !path; ++mx)
						for (int my = -1; my <= 1 && !path; ++my)
						{
							vec2 m{ pos.x + mx, pos.y + my };
							if (m.x < 0 || m.y < 0 || m.x >= world.w || m.y >= world.h) continue;
							if ((mx != 0 || my != 0) && cheb(m, t) == 1 && !world.walls.is_set(m) && !occ.is_set(m)) path = true;
						}
					if (!path) continue;
					double s = score(t);
					if (s > best_s && s > step_best + 1.0)
					{
						best_s = s;
						best = t;
						best_dash = true;
					}
				}
		}
		if (best == pos) return false;
		if (best_dash)
		{
			try
			{
				if (abilities[static_cast<std::size_t>(dash_slot)].use(best))
				{
					pos = best;
					can_cast = false;
					return true;
				}
			}
			catch (const cambc::error&)
			{
			}
			return false;
		}
		try
		{
			if (me.move_absolute(best))
			{
				pos = best;
				can_move = false;
				if (ranged) can_attack = false;
				return true;
			}
		}
		catch (const cambc::error&)
		{
		}
		return false;
	}

	bool fight30_stand(const std::vector<Near>& near, double frac)
	{
		int dmin = 999;
		for (const auto& x : near) dmin = std::min(dmin, x.d);
		bool committed = FIGHT_COMMIT != 0 && now < commit_until && frac >= 0.25;
		bool trapped = STAND_REACH != 0 && dmin <= STAND_REACH;
		bool helping = HELP_CALLS && help_call && (!my_call || *help_call != *my_call) && cheb(*help_call, pos) <= 3 && frac >= 0.5;
		if (!(committed || trapped || helping)) return false;
		const Near* weakest = nullptr;
		for (const auto& x : near)
			if (x.d <= rng && (!weakest || x.hp < weakest->hp)) weakest = &x;
		if (weakest)
		{
			hit_champion(weakest->e, weakest->p);
			return true;
		}
		const Near* tgt = &near[0];
		for (const auto& x : near)
			if (x.d < tgt->d || (x.d == tgt->d && x.hp < tgt->hp)) tgt = &x;
		if (!ranged || tgt->d <= rng + 1)
		{
			bitboard roots;
			roots.draw_chebyshev(tgt->p, static_cast<float>(rng));
			go(roots, !ranged);
			if (cheb(tgt->p, pos) <= rng && basic_attack_champion(tgt->e)) use_reset_champion(tgt->e);
			return true;
		}
		return false;
	}

	void call_help()
	{
		try
		{
			cambc::shared_memory[6] = static_cast<std::uint8_t>(pos.x + 1);
			cambc::shared_memory[7] = static_cast<std::uint8_t>((pos.y & 127) | ((now & 1) << 7));
			my_call = pos;
		}
		catch (...)
		{
		}
	}

	std::optional<vec2> read_help()
	{
		int x, v;
		try
		{
			x = static_cast<std::uint8_t>(cambc::shared_memory[6]);
			v = static_cast<std::uint8_t>(cambc::shared_memory[7]);
		}
		catch (...)
		{
			return std::nullopt;
		}
		auto last = help_last;
		help_last = v;
		if (x == 0 || (last && *last == v)) return std::nullopt;
		return vec2{ x - 1, v & 127 };
	}

	bool answer_help()
	{
		if (!help_call || (my_call && *help_call == *my_call) || gems >= 40 || hp < 0.5 * max_hp) return false;
		int d = cheb(*help_call, pos);
		if (d <= 1 || d > HELP_RANGE) return false;
		bitboard roots;
		roots.draw_chebyshev(*help_call, 1);
		roots &= ~world.block;
		auto dz = danger(-1);
		return go(roots, true, dz ? &*dz : nullptr);
	}

	void set_prio(int p)
	{
		if (p == prio) return;
		try
		{
			me.set_priority(p);
			prio = p;
		}
		catch (const cambc::error&)
		{
		}
	}

	void shield_up(int closest)
	{
		if (!can_cast || (closest > 1 && !taking_damage())) return;
		for (int i = 0; i < 2; ++i)
		{
			if (ab[i].kind == K_SHIELD && abilities[static_cast<std::size_t>(i)].cooldown() == 0)
			{
				try
				{
					if (abilities[static_cast<std::size_t>(i)].use()) can_cast = false;
				}
				catch (const cambc::error&)
				{
				}
				return;
			}
		}
	}

	double burst()
	{
		double total = can_attack ? strength_now : 0.0;
		if (can_cast)
		{
			for (int i = 0; i < 2; ++i)
			{
				int k = ab[i].kind;
				if ((k == K_DAMAGE || k == K_AOE || k == K_CC) && abilities[static_cast<std::size_t>(i)].cooldown() == 0)
				{
					total += focus_now * ab[i].modifier;
					break;
				}
				if (k == K_RESET && can_attack && abilities[static_cast<std::size_t>(i)].cooldown() == 0)
				{
					total += strength_now;
					break;
				}
			}
		}
		return total;
	}

	void retreat(const std::vector<Near>& near)
	{
		if (at_spawn) return;
		bitboard zone;
		for (const auto& x : near) zone.draw_chebyshev(x.p, static_cast<float>(x.rng + 1));
		auto camps_zone = danger(-1);
		bool in_camp_range = camps_zone && camps_zone->is_set(pos);
		if (in_camp_range && taking_damage() && escape(&zone)) return;
		int far = 999;
		for (const auto& x : near) far = std::min(far, x.d);
		if (far >= 8 && !in_camp_range)
		{
			int sd = world.spawn_field().get(pos);
			if (sd > 8 && try_recall()) return;  // as bot.py: an unreached spawn (65535) also recalls
		}
		if (camps_zone) zone |= *camps_zone;
		if (go(world.my_spawn, true, &zone)) return;
		if (!in_camp_range)
		{
			for (const auto& x : near)
				if (x.d - x.rng <= 1) return;
			try_recall();
		}
	}

	bool try_recall()
	{
		try
		{
			me.recall();
		}
		catch (const cambc::error&)
		{
			return false;
		}
		target = -1;
		claim(-1);
		return true;
	}

	bool basic_attack_unit(const cambc::unit& u)
	{
		if (!can_attack) return false;
		try
		{
			me.attack(u);
		}
		catch (const cambc::error&)
		{
			return false;
		}
		can_attack = false;
		if (ranged) can_move = false;
		return true;
	}
	bool basic_attack_champion(const champion& c) { return basic_attack_unit(c); }

	template <typename U> void use_reset(const U& u)
	{
		for (int i = 0; i < 2; ++i)
		{
			if (ab[i].kind == K_RESET && can_cast && !can_attack)
			{
				const auto& a = abilities[static_cast<std::size_t>(i)];
				if (a.cooldown() == 0)
				{
					try
					{
						if (!u.is_visible() || u.health() <= 0) return;
						if (cheb(u.position(), pos) > rng) return;
						a.use();
					}
					catch (const cambc::error&)
					{
						return;
					}
					can_cast = false;
					can_attack = true;
					basic_attack_unit(u);
					return;
				}
			}
		}
	}
	void use_reset_champion(const champion& c) { use_reset(c); }

	// Cast damage/stun abilities at a unit in range. Returns true if something was cast.
	template <typename U> bool cast_offense(const U& u, vec2 upos, bool is_champion)
	{
		if (!can_cast) return false;
		int d = cheb(upos, pos);
		for (int i = 0; i < 2; ++i)
		{
			int k = ab[i].kind;
			if (k != K_DAMAGE && k != K_AOE && k != K_CC) continue;
			const AbInfo& info = ab[i];
			if (d > info.range) continue;
			if (info.exclusive && !can_move) continue;
			if (k == K_CC && info.modifier == 0 && !is_champion && !cc_camp_ok) continue;
			const auto& a = abilities[static_cast<std::size_t>(i)];
			if (a.cooldown() != 0) continue;
			bool ok = false;
			try
			{
				if (k == K_AOE)
				{
					vec2 t = upos;
					if (!is_champion && aoe_pos && cheb(*aoe_pos, pos) <= info.range) t = *aoe_pos;
					ok = a.use(t);
				}
				else
					ok = a.use(u);
			}
			catch (const cambc::error&)
			{
				continue;
			}
			if (ok)
			{
				can_cast = false;
				if (info.exclusive) can_move = false;
				return true;
			}
		}
		return false;
	}
	bool cast_offense_champion(const champion& c, vec2 p) { return cast_offense(c, p, true); }

	template <typename U> void hit(const U& u, vec2 upos, bool is_champion)
	{
		if (FIGHT_COMMIT != 0 && is_champion) commit_until = now + FIGHT_COMMIT;
		if (is_champion) last_champ_hit = now;
		if (CAST_FIRST && ranged)
		{
			cast_offense(u, upos, is_champion);
			basic_attack_unit(u);
			use_reset(u);
		}
		else
		{
			basic_attack_unit(u);
			use_reset(u);
			cast_offense(u, upos, is_champion);
		}
	}
	void hit_champion(const champion& c, vec2 p) { hit(c, p, true); }

	void support()
	{
		if (!can_cast) return;
		for (int i = 0; i < 2; ++i)
		{
			int k = ab[i].kind;
			const auto& a = abilities[static_cast<std::size_t>(i)];
			if (k == K_SHIELD && hp < (META_PLAY ? 1.0 : 0.85) * max_hp && taking_damage())
			{
				if (a.cooldown() == 0)
				{
					try
					{
						if (a.use())
						{
							can_cast = false;
							return;
						}
					}
					catch (const cambc::error&)
					{
					}
				}
			}
			else if (k == K_HEAL && a.cooldown() == 0)
			{
				const champion* best = nullptr;
				double best_missing = 0;
				for (auto& al : allies)
				{
					try
					{
						if (!al.is_visible() || cheb(al.position(), pos) > 4) continue;
						double missing = al.max_health() - al.health();
						if (missing > 150 && (!best || missing > best_missing))
						{
							best = &al;
							best_missing = missing;
						}
					}
					catch (const cambc::error&)
					{
					}
				}
				if (best)
				{
					try
					{
						if (a.use(*best))
						{
							can_cast = false;
							return;
						}
					}
					catch (const cambc::error&)
					{
					}
				}
			}
		}
	}

	void place_lock()
	{
		for (auto a : world.altar_list)
		{
			if (std::abs(a.x - pos.x) > 2 || std::abs(a.y - pos.y) > 2) continue;
			try
			{
				if (cambc::vision::has_altar_lock(a))
				{
					locked_altars.insert({ a.x, a.y });
					continue;
				}
				if (me.consumables()[cambc::consumable_type::altar_lock].use(a))
				{
					has_lock = false;
					locked_altars.insert({ a.x, a.y });
					return;
				}
			}
			catch (const cambc::error&)
			{
				has_lock = false;
				return;
			}
		}
	}

	// ------------------------------------------------------------------ recall / tribute
	bool maybe_recall()
	{
		if (at_spawn) return false;
		double frac = hp / max_hp;
		int sd = world.spawn_field().get(pos);
		if (frac < 0.35 && taking_damage())
		{
			if (escape(nullptr)) return true;
			if (frac < 0.3)
			{
				auto dz = danger(-1);
				go(world.my_spawn, true, dz ? &*dz : nullptr);
				return true;
			}
		}
		bool shop_trip = !remote_shop && gems == 0 && build_done < build.size() && gold >= SHOP_GOLD && frac < SHOP_HP;
		if (frac < 0.3 || shop_trip)
		{
			if (sd < UNREACHED && sd <= 6)
			{
				go(world.my_spawn);
				return true;
			}
			if (frac >= 0.3 && SHOP_SAFE)
			{
				if (taking_damage() || enemy_seen == now) return false;
				auto dz = danger(-1);
				if (dz && dz->is_set(pos)) return false;
			}
			if (enemy_seen == now && frac < 0.5)
			{
				auto dz = danger(-1);
				go(world.my_spawn, true, dz ? &*dz : nullptr);
				return true;
			}
			return try_recall();
		}
		return false;
	}

	// LOCKED_OPEN: can we walk to an altar now, past every group not known to be dead? Checked every 10 rounds.
	bool altar_open()
	{
		if (now - open_checked < 10) return open_now;
		open_checked = now;
		bitboard walls = world.block;
		for (const auto& g : world.groups)
			if (g.status == ALIVE || (g.status == RESPAWN && now >= g.alive_at)) walls |= g.tiles;
		walls.set(pos, false);
		bitboard roots = world.altar_approach & ~walls;
		bitboard visited, stop;
		stop.set(pos);
		distance_field f;
		f.compute_to(walls, roots, stop, visited);
		open_now = f.get(pos) < UNREACHED;
		return open_now;
	}

	bool want_tribute()
	{
		if (locked && !(LOCKED_OPEN && gems >= 10 && altar_open())) return false;
		if (gems + static_cast<int>(cambc::global_submitted_gems(team::ally)) >= 1000) return true;
		if (now >= 1940) return true;
		if (target >= 0 && G(target).status == REWARD && G(target).tiles.is_set(pos)) return false;
		int d = world.altar_field().get(pos);
		if (d >= UNREACHED) return false;
		if (gems >= TRIBUTE_BIG) return true;
		if (gems >= TRIBUTE_MID && d <= 12) return true;
		if (d <= 4) return true;
		if (hp < 0.4 * max_hp && gems >= 15) return true;
		if (idle_turns >= 3) return true;
		return false;
	}

	void tribute()
	{
		std::optional<cambc::altar_lock> locked;
		for (auto a : world.altar_list)
		{
			if (cheb(a, pos) > 1) continue;
			try
			{
				if (cambc::vision::has_altar_lock(a))
				{
					auto lock = cambc::vision::altar_lock_at(a);
					if (lock.is_enemy())
					{
						locked = lock;
						continue;
					}
				}
			}
			catch (const cambc::error&)
			{
			}
			try
			{
				me.submit_gems(a);
				return;
			}
			catch (const cambc::error& e)
			{
				log(std::string("submit failed ") + e.what());
			}
		}
		if (RECALL_TRAVEL && !at_spawn && enemy_seen != now)
		{
			int d = world.altar_field().get(pos);
			if (spawn_altar + RECALL_TURNS + 3 < d && try_recall())
			{
				act = "recall_travel";
				return;
			}
		}
		if (locked && can_attack)
		{
			try
			{
				me.attack(*locked);
				can_attack = false;
				if (ranged) can_move = false;
				return;
			}
			catch (const cambc::error&)
			{
			}
		}
		auto dz = danger(-1);
		go(world.altar_approach, true, dz ? &*dz : nullptr);
	}

	// ------------------------------------------------------------------ farming
	std::map<int, std::vector<int>> claims()
	{
		std::map<int, std::vector<int>> out;
		ready.clear();
		for (int i = 0; i < std::min(n_allies, 6); ++i)
		{
			if (i == slot) continue;
			int v = static_cast<std::uint8_t>(cambc::shared_memory[static_cast<std::size_t>(i)]);
			if (v != 255)
			{
				int g = v & 127;
				out[g].push_back(i);
				if (v & 128) ready[g] += 1;
			}
		}
		return out;
	}

	void claim(int g, bool is_ready = false)
	{
		try
		{
			cambc::shared_memory[static_cast<std::size_t>(slot)] = static_cast<std::uint8_t>(g < 0 ? 255 : ((g & 127) | (is_ready ? 128 : 0)));
		}
		catch (...)
		{
		}
	}

	int choose_target(int exclude = -1)
	{
		if (partner_slot >= 0)
		{
			int v = 255;
			try
			{
				v = static_cast<std::uint8_t>(cambc::shared_memory[static_cast<std::size_t>(partner_slot)]);
			}
			catch (...)
			{
			}
			int g = v == 255 ? -1 : (v & 127);
			if (g >= 0 && g < static_cast<int>(world.groups.size()) && g != exclude && G(g).status != RESPAWN)
			{
				target_need = 1;
				target_via = false;
				return g;
			}
		}
		if (choice_round != now)
		{
			choice = score_groups();
			choice_round = now;
		}
		int best = -1;
		double best_score = 0.0;
		int best_need = 1;
		bool best_via = false;
		for (const auto& s : choice)
		{
			if (s.g != exclude && s.score > best_score)
			{
				best_score = s.score;
				best = s.g;
				best_need = s.need;
				best_via = s.via;
			}
		}
		target_need = best_need;
		target_via = best_via;
		return best;
	}

	std::vector<Scored> score_groups()
	{
		distance_field field;
		bitboard roots, visited;
		roots.set(pos);
		field.compute(world.block, roots, visited);
		// Per-group get() calls (~80 fuel each) instead of exporting the whole field (10,000 values on 100x100).
		auto cl = claims();
		if (DEATHBALL && BALL_SIZE >= n_allies && now < BALL_UNTIL) cl.clear();  // followers claim the leader's target
		double dps = dps_now;
		double gold_w = GOLD_WEIGHT * std::max(0.15, 1.0 - static_cast<double>(now) / GOLD_TAPER);
		double need_k = 1.0 / (NEED_FRAC * max_hp * dps);
		double boss_k = BOSS_NEED_FRAC > 0 ? 1.0 / (BOSS_NEED_FRAC * max_hp * dps) : need_k;
		double cluster_dps = 0.7 * (splash ? strength_now : 0.0) + 0.7 * focus_now * aoe_mod;
		int squad = MIN_SQUAD < n_allies ? MIN_SQUAD : n_allies;
		bool recall_ok = RECALL_TRAVEL && !at_spawn && enemy_seen != now;
		int margin = RECALL_TURNS + 3;
		std::vector<Scored> out;
		for (auto& g : world.groups)
		{
			int status = g.status;
			if (status == RESPAWN)
			{
				if (now >= g.alive_at)
				{
					g.status = status = ALIVE;
					g.reset_hp();
				}
				else if (g.alive_at - now > 120)
					continue;
			}
			int d = field.get(g.anchor);
			bool via = false;
			if (recall_ok)
			{
				int dr = spawn_dist[static_cast<std::size_t>(g.lin)] + margin;
				if (dr < d)
				{
					d = dr - 3;
					via = true;
				}
			}
			if (d >= 65535) continue;
			int wait = 0;
			if (status == RESPAWN)
			{
				wait = g.alive_at - now - d;
				if (wait > 25) continue;
				if (wait < 0) wait = 0;
			}
			auto sit = cl.find(g.idx);
			int others = sit != cl.end() ? static_cast<int>(sit->second.size()) : 0;
			double hp_left;
			int need = 1;
			if (status == REWARD)
				hp_left = 0;
			else
			{
				hp_left = status == ALIVE ? g.hp_now : g.hp_max;
				if (g.dps > 0)
				{
					need = static_cast<int>(std::sqrt(g.dps * hp_left * (g.boss ? boss_k : need_k)) + 0.999);
					if (need > n_allies) continue;  // too strong to fight (boss poking is not ported)
					if (need < 1) need = 1;
				}
				if (0 < need && need < squad) need = squad;
			}
			int kk = std::max(others + 1, need);
			double gdps = cluster_dps > 0 ? dps + cluster_dps * g.cluster : dps;
			double cost = kk * (d + wait) + hp_left / gdps + (locked ? 5.0 : 5 + 0.5 * g.near_altar + g.gems / 10.0);
			if (others + 1 < need) cost += 4 * (need - others - 1);
			double value = locked ? g.gold + (LOCKED_OPEN ? 0.5 * g.gems : 0.0) : g.gems + gold_w * g.gold;
			if (need && others >= need)
				value *= 0.5;
			else if (need > 1 && sit != cl.end() && !sit->second.empty() && *std::min_element(sit->second.begin(), sit->second.end()) < slot)
				value *= 1.2;
			if (g.enemy_side) value *= ENEMY_SIDE;
			if (g.idx == target) value *= 1.1;
			double score = value / (cost + 5);
			if (SEED)
			{
				std::int64_t hsh = (static_cast<std::int64_t>(SEED) * 2654435761LL + g.idx * 40503LL + slot * 9973LL + (now / 50) * 7919LL) % 1000;
				score *= 0.98 + 0.04 * (static_cast<double>(hsh) / 1000.0);
			}
			out.push_back(Scored{ score, g.idx, need, via });
		}
		return out;
	}

	// DEATHBALL: the leader is the lowest slot whose champion is alive and in view (ourselves included).
	int ball_leader(std::optional<vec2>& lpos)
	{
		int first = BALL_SIZE >= n_allies ? 0 : slot / BALL_SIZE * BALL_SIZE;  // squads of BALL_SIZE consecutive slots
		int last = std::min(n_allies, first + BALL_SIZE);
		for (int s = first; s < last; ++s)
		{
			if (s == slot)
			{
				lpos = pos;
				return s;
			}
			std::uint32_t h = ally_handles[static_cast<std::size_t>(s)];
			for (auto& a : allies)
			{
				if (static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(a)) != h) continue;
				try
				{
					if (a.is_visible())
					{
						lpos = a.position();
						return s;
					}
				}
				catch (const cambc::error&)
				{
				}
			}
		}
		lpos = pos;
		return slot;
	}

	// DEATHBALL: followers take the leader's target and regroup when more than BALL_RADIUS away. Returns true if moved.
	bool follow_ball()
	{
		std::optional<vec2> lp;
		int lead = ball_leader(lp);
		if (lead == slot || !lp) return false;
		int v = 255;
		try
		{
			v = static_cast<std::uint8_t>(cambc::shared_memory[static_cast<std::size_t>(lead)]);
		}
		catch (...)
		{
		}
		int lg = v == 255 ? -1 : (v & 127);
		if (lg >= 0 && lg < static_cast<int>(world.groups.size()) && G(lg).status != RESPAWN)
		{
			target = lg;
			target_round = now;
		}
		if (cheb(*lp, pos) <= BALL_RADIUS) return false;
		bitboard roots;
		roots.draw_chebyshev(*lp, 2);
		roots &= ~world.block;
		act = "ball";
		return go(roots, true);
	}

	void farm()
	{
		if (DEATHBALL && now < BALL_UNTIL && follow_ball()) return;
		int g = target;
		if (g >= 0 && G(g).status == RESPAWN && now >= G(g).alive_at)
		{
			G(g).status = ALIVE;
			G(g).reset_hp();
		}
		if (g >= 0 && (G(g).status == RESPAWN || now - target_round >= RETARGET_EVERY))
		{
			g = choose_target();
			target_round = now;
		}
		else if (g < 0)
		{
			g = choose_target();
			target_round = now;
		}
		if (g != target) wait_turns = 0;
		target = g;
		claim(g);
		if (g < 0)
		{
			act = "idle";
			++idle_turns;
			if (gems > 0 && (!locked || (LOCKED_OPEN && altar_open())))
				tribute();
			else
				go(world.altar_approach);
			return;
		}
		idle_turns = 0;
		support();
		Group& grp = G(g);
		std::vector<CampInfo> alive;
		alive.reserve(camp_info.size());
		for (const auto& ci : camp_info)
			if (ci.g == g) alive.push_back(ci);
		// A dead camp's tile of the target can't block a respawn before the capture, so stay on it while camps live:
		// 00vault's inner camps can only be reached across the outer ones' tiles.
		if (world.all_camp_tiles.is_set(pos) && !((grp.status == REWARD || !alive.empty()) && grp.tiles.is_set(pos)))
			step_off();
		if (!alive.empty())
		{
			act = "camp";
			attack_group(grp, alive);
			return;
		}
		if (grp.status == REWARD)
		{
			if (grp.tiles.is_set(pos))
			{
				act = "capture";
				return;
			}
			for (auto& a : allies)
			{
				try
				{
					if (a.is_visible() && grp.tiles.is_set(a.position()))
					{
						target = choose_target(g);
						claim(target);
						return;
					}
				}
				catch (const cambc::error&)
				{
				}
			}
			bitboard free = grp.tiles & ~occ;
			if (free.is_empty())
			{
				target = -1;
				return;
			}
			go(free);
			return;
		}
		if (target_via && !at_spawn && enemy_seen != now && gems == 0)
		{
			if (try_recall())
			{
				target = g;
				claim(g);
				act = "recall_travel";
				return;
			}
		}
		bitboard roots;
		for (auto c : grp.cells) roots.draw_chebyshev(c, 1);
		roots &= ~(world.block | world.all_camp_tiles);
		auto dz = danger(g);
		if (!go(roots, true, dz ? &*dz : nullptr) && cheb(grp.anchor, pos) <= 2) grp.status = ALIVE;
	}

	void attack_group(Group& g, const std::vector<CampInfo>& alive)
	{
		bool is_awake = awake.count(g.idx) > 0;
		std::vector<char> live(g.cells.size(), 0);
		for (const auto& x : alive) live[x.li] = 1;
		const CampInfo* best = nullptr;
		std::tuple<int, double, int> best_key{};
		std::optional<vec2> aoe;
		int aoe_n = -1;
		for (const auto& x : alive)
		{
			int n = 0;
			for (int j : g.near[x.li]) n += live[j];
			if (n > aoe_n)
			{
				aoe_n = n;
				aoe = x.p;
			}
			std::tuple<int, double, int> key{ splash ? -n : 0, x.hp, cheb(x.p, pos) };
			if (!best || key < best_key)
			{
				best_key = key;
				best = &x;
			}
		}
		if (!best) return;
		const cambc::camp& camp = best->c;
		vec2 cp = best->p;
		aoe_pos = aoe;
		int d = cheb(cp, pos);
		int need = target_need;
		if (fragile && g.dps > 0) need = std::max(need, 2);  // META_CASSI: let a sturdier ally take the camp hits
		if (need > 1 && !is_awake)
		{
			claims();
			int present = std::max(ready[g.idx], allies_near(cp, 5)) + 1;
			if (present < need && wait_turns < (fragile ? 20 : g.boss ? BOSS_WAIT : WAIT_LIMIT))
			{
				++wait_turns;
				act = "wait";
				claim(g.idx, d <= 6);
				int reach = g.rng > 0 ? g.rng : 3;
				if (d > reach) cast_offense(camp, cp, false);
				if (d <= reach)
					step_away(cp, reach + 1);
				else if (d > reach + 1)
				{
					bitboard roots, inner;
					roots.draw_chebyshev(cp, static_cast<float>(reach + 1));
					inner.draw_chebyshev(cp, static_cast<float>(reach));
					roots &= ~(inner | world.block | world.all_camp_tiles);
					go(roots);
				}
				return;
			}
		}
		wait_turns = 0;
		claim(g.idx, true);
		cc_camp_ok = META_PLAY && stat(best->k).str > 0;
		if (META_PLAY && stun_dash >= 0 && d <= 3)
		{
			std::vector<vec2> tg;
			bool strong = false;
			for (const auto& x : alive)
				if (stat(x.k).str > 0)
				{
					tg.push_back(x.p);
					if (stat(x.k).str >= 60) strong = true;
				}
			if (dash_stun(tg, strong ? 1 : 2, cp)) d = cheb(cp, pos);
		}
		double leave_hp = (fragile ? 0.6 : 0.35) * max_hp;
		if (FIGHT2)
		{
			// Leave with three turns of the awake camps' damage in hand (an elk trio hits for 180 a turn): camps never
			// heal, so coming back later costs only the walk.
			double camp_in = 0;
			for (const auto& x : alive)
				if (awake.count(x.g) && stat(x.k).str > 0 && cheb(x.p, pos) <= stat(x.k).rng) camp_in += stat(x.k).str;
			leave_hp = std::max(leave_hp, 3.0 * camp_in);
		}
		if (hp < leave_hp && taking_damage() && (g.dps > 0 || !zones.empty()))
		{
			if (ranged && d <= 4) cast_offense(camp, cp, false);
			if (!escape(nullptr)) step_away(cp, 4);
			return;
		}
		if (d <= rng)
		{
			hit(camp, cp, false);
			if (CLAIM_ON_KILL && alive.size() == 1 && !ranged && can_move) claim_tile(camp, cp);
			return;
		}
		cast_offense(camp, cp, false);
		if (can_attack)
		{
			for (const auto& x : alive)
			{
				if (&x != best && cheb(x.p, pos) <= rng)
				{
					if (basic_attack_unit(x.c)) use_reset(x.c);
					break;
				}
			}
		}
		bitboard roots;
		roots.draw_chebyshev(cp, static_cast<float>(rng));
		if (ranged)
		{
			bitboard inner;
			inner.draw_chebyshev(cp, static_cast<float>(rng - 1));
			bitboard ring = roots & ~(inner | world.block | world.all_camp_tiles);
			if (!ring.is_empty()) roots = ring;
		}
		roots &= ~world.block;
		auto dz = danger(g.idx);
		std::optional<bitboard> avoid = dz;
		if (CAMP_TILE_FIX)
		{
			bitboard off = roots & ~world.all_camp_tiles;
			if (!off.is_empty()) roots = off;
			bitboard spawns = world.all_camp_tiles & ~g.tiles;  // walk across the target's dead camps (see step_off() above)
			if (avoid)
				*avoid |= spawns;
			else
				avoid = spawns;
		}
		go(roots, true, avoid ? &*avoid : nullptr);
		if (cheb(cp, pos) <= rng)
		{
			basic_attack_unit(camp);
			use_reset(camp);
		}
	}

	// META_PLAY: Heart of Ruin's dash damages and stuns everything within 1 of where she lands. Land where it hits the
	// most of `targets` (at least min_hits; ties go nearer `prefer`). Returns true if she dashed.
	bool dash_stun(const std::vector<vec2>& targets, int min_hits, vec2 prefer)
	{
		if (!META_PLAY || stun_dash < 0 || !can_cast || targets.empty()) return false;
		const auto& a = abilities[static_cast<std::size_t>(stun_dash)];
		if (a.cooldown() != 0) return false;
		int reach = static_cast<int>(ab[stun_dash].range);
		std::optional<vec2> best;
		int best_n = 0, best_d = 99;
		for (int dx = -reach; dx <= reach; ++dx)
			for (int dy = -reach; dy <= reach; ++dy)
			{
				if (dx == 0 && dy == 0) continue;
				vec2 t{ pos.x + dx, pos.y + dy };
				if (t.x < 0 || t.y < 0 || t.x >= world.w || t.y >= world.h) continue;
				if (world.block.is_set(t) || occ.is_set(t)) continue;
				if (std::max(std::abs(dx), std::abs(dy)) == 2)
				{
					bool path = false;  // a middle tile next to both ends that isn't a wall (holes can be crossed)
					for (int mx = -1; mx <= 1 && !path; ++mx)
						for (int my = -1; my <= 1 && !path; ++my)
						{
							vec2 m{ pos.x + mx, pos.y + my };
							if (m.x < 0 || m.y < 0 || m.x >= world.w || m.y >= world.h) continue;  // off-map reads raise engine error 5
							if ((mx != 0 || my != 0) && cheb(m, t) == 1 && !world.walls.is_set(m) && !occ.is_set(m)) path = true;
						}
					if (!path) continue;
				}
				int n = 0;
				for (auto q : targets)
					if (cheb(q, t) <= 1) ++n;
				int dd = cheb(prefer, t);
				if (n > best_n || (n == best_n && n > 0 && dd < best_d))
				{
					best_n = n;
					best_d = dd;
					best = t;
				}
			}
		if (!best || best_n < min_hits) return false;
		try
		{
			if (a.use(*best))
			{
				pos = *best;
				can_cast = false;
				return true;
			}
		}
		catch (const cambc::error&)
		{
		}
		return false;
	}

	void claim_tile(const cambc::camp& camp, vec2 cp)
	{
		try
		{
			if (camp.is_visible() && camp.health() > 0) return;
			if (me.move_absolute(cp))
			{
				pos = cp;
				can_move = false;
			}
		}
		catch (const cambc::error&)
		{
		}
	}

	int allies_near(vec2 p, int r)
	{
		int n = 0;
		for (auto& a : allies)
		{
			try
			{
				if (a.is_visible() && cheb(a.position(), p) <= r) ++n;
			}
			catch (const cambc::error&)
			{
			}
		}
		return n;
	}

	// Tiles in range of awake camps, except those of the excluded group.
	std::optional<bitboard> danger(int exclude)
	{
		std::optional<bitboard> out;
		for (auto& [idx, z] : zones)
		{
			if (idx == exclude) continue;
			if (!out)
				out = z;
			else
				*out |= z;
		}
		return out;
	}

	// Get out of range of every awake camp (used when hurt), steering clear of avoid tiles.
	bool escape(const bitboard* avoid)
	{
		auto d = danger(-1);
		if (!d || !d->is_set(pos)) return false;
		bitboard roots;
		roots.draw_chebyshev(pos, 8);
		roots &= ~(*d | world.block | world.all_camp_tiles);
		if (avoid)
		{
			bitboard safe = roots & ~*avoid;
			if (!safe.is_empty()) roots = safe;
		}
		return go(roots, true, avoid);
	}

	void step_off()
	{
		bitboard roots;
		roots.draw_chebyshev(pos, 2);
		roots &= ~(world.block | world.all_camp_tiles);
		go(roots, false);
	}

	void step_away(vec2 danger_pos, int dist)
	{
		bitboard roots, inner;
		roots.draw_chebyshev(pos, 3);
		inner.draw_chebyshev(danger_pos, static_cast<float>(dist - 1));
		roots &= ~(inner | world.block | world.all_camp_tiles);
		go(roots, false);
	}
};
} // namespace bot
