// Static map data, cached once per champion, plus what this champion knows about camp groups.
// C++ port of bots/mybot/src/world.py.
#pragma once
#include <cambc.h>

#include <algorithm>
#include <cstdint>
#include <map>
#include <optional>
#include <unordered_map>
#include <utility>
#include <vector>

namespace bot
{
using cambc::bitboard;
using cambc::distance_field;
using cambc::vec2;

inline constexpr std::uint16_t UNREACHED = 65535;
enum Status : int { ALIVE = 0, REWARD = 1, RESPAWN = 2 };

inline int cheb(vec2 a, vec2 b)
{
	int dx = a.x - b.x, dy = a.y - b.y;
	if (dx < 0) dx = -dx;
	if (dy < 0) dy = -dy;
	return dx > dy ? dx : dy;
}

inline std::uint32_t camp_handle(const cambc::camp& c) { return static_cast<std::uint32_t>(static_cast<cambc::handle_camp_t>(c)); }

// Camp health, strength and attack range per camp kind, read from the engine's camp designs the first time a kind is
// seen (cambc 3.0 changed them and added the golem, kind 5).
struct CampStat
{
	float hp{ 5000 }, str{ 120 };
	int rng{ 4 };
};

inline std::array<std::optional<CampStat>, 16>& camp_stats()
{
	static std::array<std::optional<CampStat>, 16> table{};
	return table;
}

inline int learn_camp(const cambc::camp& c)
{
	int k = static_cast<int>(c.kind());
	auto& t = camp_stats();
	if (k < 0 || k >= static_cast<int>(t.size())) return 0;
	if (!t[k])
	{
		CampStat s;
		try
		{
			auto b = c.base_stats();
			s.hp = b.base_health;
			s.str = b.base_strength;
			s.rng = b.base_attack_range;
		}
		catch (...)
		{
		}
		t[k] = s;
	}
	return k;
}

inline const CampStat& stat(int k) { return *camp_stats()[k]; }

struct Group
{
	int idx;
	cambc::map::camp_group obj;
	int gold, gems, respawn;
	std::vector<int> kinds;
	std::vector<std::uint32_t> handles;
	std::vector<vec2> cells;
	bitboard tiles;
	vec2 anchor{};
	int ax{}, ay{}, lin{};
	std::unordered_map<std::uint32_t, vec2> cell_of;
	std::unordered_map<std::uint32_t, std::vector<std::uint32_t>> nbrs;
	double cluster{};
	bool enemy_side{};
	double hp_max{}, hp_now{}, dps{};
	int rng{};
	bool boss{};
	int status{ ALIVE }, alive_at{}, seen{ -1 };
	std::unordered_map<std::uint32_t, double> hp;  // last seen health per camp handle (missing = full)
	int near_altar{ UNREACHED };

	Group(int i, const cambc::map::camp_group& g)
		: idx{ i }, obj{ g }, gold{ static_cast<int>(g.gold_value()) }, gems{ static_cast<int>(g.gem_value()) },
		  respawn{ g.max_respawn_timer() }
	{
		for (const auto& c : g.camps())
		{
			int k = learn_camp(c);
			vec2 p = c.spawn_position();
			const auto& s = stat(k);
			if (s.str > 0 && s.rng > rng) rng = s.rng;
			if (s.hp >= 5000) boss = true;
			kinds.push_back(k);
			handles.push_back(camp_handle(c));
			cells.push_back(p);
			tiles.set(p);
			hp_max += s.hp;
			dps += s.str;
		}
		anchor = cells.front();
		ax = anchor.x;
		ay = anchor.y;
		for (std::size_t i = 0; i < handles.size(); ++i) cell_of[handles[i]] = cells[i];
		std::size_t n = handles.size();
		double total = 0;
		for (std::size_t i = 0; i < n; ++i)
		{
			std::vector<std::uint32_t> near;
			if (n > 1)
			{
				for (std::size_t j = 0; j < n; ++j)
					if (j != i && std::abs(cells[j].x - cells[i].x) <= 1 && std::abs(cells[j].y - cells[i].y) <= 1)
						near.push_back(handles[j]);
				total += static_cast<double>(near.size());
			}
			nbrs[handles[i]] = std::move(near);
		}
		cluster = total / static_cast<double>(n);
		hp_now = hp_max;
	}

	void refresh_hp()
	{
		double total = 0;
		for (std::size_t i = 0; i < handles.size(); ++i)
		{
			auto it = hp.find(handles[i]);
			total += it != hp.end() ? it->second : stat(kinds[i]).hp;
		}
		hp_now = total;
	}

	void reset_hp()
	{
		hp.clear();
		hp_now = hp_max;
	}
};

struct World
{
	int w, h;
	bitboard walls, bushes, my_spawn, enemy_spawn, block, altars, altar_approach, all_camp_tiles;
	std::vector<vec2> altar_list, spawn_tiles;
	vec2 spawn_center{}, enemy_spawn_center{};
	std::vector<Group> groups;
	std::unordered_map<std::uint32_t, int> camp_group;  // camp handle -> group index
	std::map<std::pair<int, int>, std::vector<int>> buckets;  // 10x10 buckets of group indices
	std::optional<distance_field> altar_f, spawn_f;

	World()
		: w{ cambc::map::width() }, h{ cambc::map::height() }, walls{ cambc::map::walls() }, bushes{ cambc::map::bushes() },
		  my_spawn{ cambc::map::spawn_region(cambc::team::ally) }, enemy_spawn{ cambc::map::spawn_region(cambc::team::enemy) }
	{
		altars = cambc::map::altars();
		block = walls | cambc::map::holes() | altars | enemy_spawn;
		altar_list = altars.positions();
		bitboard approach;
		for (auto a : altar_list) approach.draw_chebyshev(a, 1);
		altar_approach = approach & ~block;
		spawn_tiles = my_spawn.positions();
		spawn_center = spawn_tiles[spawn_tiles.size() / 2];
		auto esp = enemy_spawn.positions();
		enemy_spawn_center = esp[esp.size() / 2];
		auto raw = cambc::map::camp_groups();
		groups.reserve(raw.size());
		for (std::size_t i = 0; i < raw.size(); ++i) groups.emplace_back(static_cast<int>(i), raw[i]);
		for (auto& g : groups)
		{
			buckets[{ g.ax / 10, g.ay / 10 }].push_back(g.idx);
			g.lin = g.ay * w + g.ax;
			all_camp_tiles |= g.tiles;
			int de = cheb(g.anchor, enemy_spawn_center);
			int dm = cheb(g.anchor, spawn_center);
			g.enemy_side = de < dm;
			for (auto hdl : g.handles) camp_group[hdl] = g.idx;
		}
	}

	const distance_field& altar_field()
	{
		if (!altar_f)
		{
			altar_f.emplace();
			bitboard visited;
			altar_f->compute(block, altar_approach, visited);
		}
		return *altar_f;
	}

	const distance_field& spawn_field()
	{
		if (!spawn_f)
		{
			spawn_f.emplace();
			bitboard visited;
			spawn_f->compute(block, my_spawn, visited);
		}
		return *spawn_f;
	}
};
} // namespace bot
