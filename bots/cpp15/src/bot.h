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
			else if constexpr (std::is_same_v<T, cambc::ability_dash>) { r.kind = K_DASH; r.modifier = v.modifier; r.range = v.range; r.radius = v.radius; }
			else if constexpr (std::is_same_v<T, cambc::ability_shield>) { r.kind = K_SHIELD; r.modifier = v.modifier; r.range = v.range; }
		},
		*inf);
	return r;
}

// Champion damage profile per type: strength multiplier, focus-per-turn multiplier, attack range.
struct Profile
{
	double str_mul{ 1.0 }, foc_mul{ 0.0 };
	int rng{ 1 };
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
		for (const auto& ab : d.abilities())
		{
			AbInfo i = read_ability(ab);
			if (i.kind == K_RESET) p.str_mul += 0.125;
			else if (i.kind == K_DAMAGE || i.kind == K_AOE || i.kind == K_CC) p.foc_mul += i.modifier / 8.0;
			else if (HOR_DASH && i.kind == K_DASH) p.foc_mul += i.modifier / 8.0;  // Heart of Ruin's landing damage
		}
		p.rng = d.base_stats().base_attack_range;
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
	bool focus = kind == cambc::champion_type::stellar || kind == cambc::champion_type::prism || kind == cambc::champion_type::cassi;
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
		locked = LOCKED_GOLD && cambc::draft_memory.size() > 0 && (static_cast<unsigned>(cambc::draft_memory[0]) & 1u) != 0;
		const auto& af = world.altar_field();
		for (auto& g : world.groups) g.near_altar = af.get(g.anchor);
		spawn_dist = world.spawn_field().export_linear_buffer();
		spawn_altar = af.get(world.spawn_center);
	}

	void turn()
	{
		act = "?";
		_turn();
		if (WARDS && act != "dead" && act != "recall" && act != "submit" && act != "tp" && act != "?") ward_bush();
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
	// TELEMETRY: the last fight decision (tag, ratio, enemies in view, closest reach gap), printed by tele().
	char ftag{}, ftag_last{};
	double fratio{};
	int fnear{}, fclose{}, tele_round{ -100 };
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
		if (allow_dash && here >= 3 && (here > 6 || !damaging_dash()) && can_cast && dash_slot >= 0)
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
		if (!enemies.empty() && fight())
		{
			if (TELEMETRY) tele();
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
				near.push_back(Near{ e, ep, ehp, prof.rng, dps, d, eg });
			}
			catch (const cambc::error&)
			{
				continue;
			}
		}
		if (near.empty()) return false;
		ftag = 0;
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
				if (escape(&zone)) return tag('Z');
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
		double ratio = (our_hp * our_dps) / std::max(1.0, their_hp * their_dps * FIGHT_RESPECT);
		int home = world.spawn_field().get(pos);
		if (home <= 6) ratio *= 1.4;
		if (cheb(pos, world.enemy_spawn_center) <= 7) ratio *= 0.6;
		int closest = 999;
		for (const auto& x : near) closest = std::min(closest, x.d - x.rng);
		fratio = ratio;
		fnear = static_cast<int>(near.size());
		fclose = closest;
		double frac = hp / max_hp;
		double burst_dmg = burst();
		for (auto& x : near)
		{
			if (x.d <= rng && x.hp <= burst_dmg)
			{
				hit_champion(x.e, x.p);
				return tag('K');
			}
		}
		if (dash_ready())
		{
			for (auto& x : near)
			{
				if (x.d > ab[dash_slot].range + ab[dash_slot].radius || x.hp > dash_damage() + (can_attack ? strength_now : 0.0)) continue;
				auto l = dash_landing({ x.p }, x.p, 1);
				if (l && dash_to(*l))
				{
					if (cheb(x.p, pos) <= rng) hit_champion(x.e, x.p);
					return tag('D');
				}
			}
		}
		if (FIGHT_SHIELD) shield_up(closest);
		double extra = gems >= 20 ? FIGHT_GEM_EXTRA : 0.0;
		double retreat_at = FIGHT_RETREAT + extra, engage_at = FIGHT_ENGAGE + extra;
		if (ratio < retreat_at || (frac < LOW_HP_RETREAT && closest <= LOW_HP_REACH))
		{
			if ((STAND_REACH != 0 || FIGHT_COMMIT != 0 || HELP_CALLS) && fight30_stand(near, frac)) return tag('F');
			if (!ranged && can_attack)
			{
				const Near* weakest = nullptr;
				for (const auto& x : near)
					if (x.d <= rng && (!weakest || x.hp < weakest->hp)) weakest = &x;
				if (weakest) basic_attack_champion(weakest->e);
			}
			retreat(near);
			return tag('R');
		}
		const Near* best = &near[0];
		double best_v = -1.0;
		for (const auto& x : near)
		{
			double v = (100.0 + 2.0 * x.gems) / (x.hp + 50.0);
			if (x.d <= rng) v *= 2.0;
			v /= 1.0 + 0.1 * x.d;
			if (v > best_v)
			{
				best_v = v;
				best = &x;
			}
		}
		bool engage = ratio >= engage_at || (FIGHT_COMMIT != 0 && now < commit_until);
		if (best->d <= rng)
		{
			hit_champion(best->e, best->p);
			return tag('H');
		}
		const Near* weakest = nullptr;
		for (const auto& x : near)
			if (x.d <= rng && (!weakest || x.hp < weakest->hp)) weakest = &x;
		if (weakest && can_attack && (!ranged || !engage))
		{
			if (basic_attack_champion(weakest->e)) use_reset_champion(weakest->e);
		}
		if (cast_offense_champion(best->e, best->p) && !engage) return tag('C');
		if (engage && best->d <= 5 && cheb(best->p, world.enemy_spawn_center) > 3)
		{
			if (dash_ready() && best->d <= ab[dash_slot].range + ab[dash_slot].radius)
			{
				std::vector<vec2> tiles;
				for (const auto& x : near) tiles.push_back(x.p);
				auto l = dash_landing(tiles, best->p, 1);
				if (l && dash_to(*l) && cheb(best->p, pos) <= rng)
				{
					basic_attack_champion(best->e);
					use_reset_champion(best->e);
					return tag('X');
				}
			}
			bitboard roots;
			roots.draw_chebyshev(best->p, static_cast<float>(rng));
			go(roots, true);
			if (cheb(best->p, pos) <= rng)
			{
				basic_attack_champion(best->e);
				use_reset_champion(best->e);
			}
			return tag('E');
		}
		if (!engage && closest <= 2)
		{
			// HOLD_FIX: holding still inside an enemy's reach with nothing of ours in range just takes free hits (a melee
			// champion facing a ranged one between the retreat and engage ratios); step out of their reach instead.
			if (HOLD_FIX && closest <= 0 && !weakest)
			{
				retreat(near);
				return tag('O');
			}
			return tag('S');
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

	bool tag(char c)
	{
		ftag = c;
		return true;
	}

	// One line per fight decision, throttled (a new tag, or 4 rounds since the last line):
	// "F round slot kind tag ratio*100 hp% enemies allies-in-range reach-gap gems". Platform stdout is kept in the
	// match download, so scrimmages against the top teams show which ratios we die at.
	void tele()
	{
		if (!ftag || (ftag == ftag_last && now - tele_round < 4)) return;
		ftag_last = ftag;
		tele_round = now;
		int al = allies_near(pos, ALLY_RANGE);
		std::cout << "F " << now << ' ' << slot << ' ' << static_cast<int>(kind) << ' ' << ftag << ' ' << static_cast<int>(fratio * 100) << ' '
				  << static_cast<int>(100 * hp / max_hp) << ' ' << fnear << ' ' << al << ' ' << fclose << ' ' << gems << '\n';
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

	// Heart of Ruin (HOR_DASH): its dash lands for focus x modifier damage and a stun on everything within its radius,
	// every 8 turns. The top teams cast it nearly every cooldown, mostly onto camp clusters (VS-TOP5-v14.md 2.4).
	bool damaging_dash() const { return HOR_DASH && dash_slot >= 0 && ab[dash_slot].modifier > 0; }

	bool dash_ready()
	{
		if (!damaging_dash() || !can_cast || (ab[dash_slot].exclusive && !can_move)) return false;
		return abilities[static_cast<std::size_t>(dash_slot)].cooldown() == 0;
	}

	double dash_damage() const { return damaging_dash() ? focus_now * ab[dash_slot].modifier : 0.0; }

	// Free landing tile within dash range with the most targets inside the landing radius (at least min_hits), ties to
	// the tile nearest `prefer`. A 2-tile dash needs a free tile in between.
	std::optional<vec2> dash_landing(const std::vector<vec2>& targets, vec2 prefer, int min_hits)
	{
		const AbInfo& info = ab[dash_slot];
		int r = static_cast<int>(info.range), rad = static_cast<int>(info.radius);
		bitboard bad = world.block | occ | world.all_camp_tiles;
		std::optional<vec2> best;
		int best_n = min_hits - 1, best_d = 999;
		for (int dx = -r; dx <= r; ++dx)
		{
			for (int dy = -r; dy <= r; ++dy)
			{
				vec2 l{ pos.x + dx, pos.y + dy };
				if ((dx == 0 && dy == 0) || l.x < 0 || l.y < 0 || l.x >= world.w || l.y >= world.h || bad.is_set(l)) continue;
				if (cheb(l, pos) >= 2)
				{
					bool step = false;
					for (int sx = -1; sx <= 1 && !step; ++sx)
						for (int sy = -1; sy <= 1 && !step; ++sy)
						{
							vec2 s{ pos.x + sx, pos.y + sy };
							step = (sx || sy) && cheb(s, l) <= 1 && s.x >= 0 && s.y >= 0 && s.x < world.w && s.y < world.h &&
								   !(world.block | occ).is_set(s);
						}
					if (!step) continue;
				}
				int n = 0;
				for (const auto& t : targets) n += cheb(t, l) <= rad;
				int d = cheb(l, prefer);
				if (n > best_n || (n == best_n && best && d < best_d))
				{
					best_n = n;
					best_d = d;
					best = l;
				}
			}
		}
		return best;
	}

	bool dash_to(vec2 l)
	{
		try
		{
			if (abilities[static_cast<std::size_t>(dash_slot)].use(l))
			{
				pos = l;
				can_cast = false;
				if (ab[dash_slot].exclusive) can_move = false;
				return true;
			}
		}
		catch (const cambc::error&)
		{
		}
		return false;
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
			if (k == K_CC && info.modifier == 0 && !is_champion) continue;
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
			if (k == K_SHIELD && hp < 0.85 * max_hp && taking_damage())
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

	bool want_tribute()
	{
		if (locked) return false;
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
		double dps = dps_now;
		double gold_w = EARLY_GOLD > 0 && now < EARLY_UNTIL ? EARLY_GOLD : GOLD_WEIGHT * std::max(0.15, 1.0 - static_cast<double>(now) / GOLD_TAPER);
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
			double value = locked ? g.gold : g.gems + gold_w * g.gold;
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

	void farm()
	{
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
			if (gems > 0 && !locked)
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
		if (need > 1 && !is_awake)
		{
			claims();
			int present = std::max(ready[g.idx], allies_near(cp, 5)) + 1;
			if (present < need && wait_turns < (g.boss ? BOSS_WAIT : WAIT_LIMIT))
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
		if (hp < 0.35 * max_hp && taking_damage() && (g.dps > 0 || !zones.empty()))
		{
			if (ranged && d <= 4) cast_offense(camp, cp, false);
			if (!escape(nullptr)) step_away(cp, 4);
			return;
		}
		if (dash_ready() && d <= 4)
		{
			std::vector<vec2> tiles;
			for (const auto& x : alive) tiles.push_back(x.p);
			auto l = dash_landing(tiles, cp, 1);
			if (l && dash_to(*l)) d = cheb(cp, pos);
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
