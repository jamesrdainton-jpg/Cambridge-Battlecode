// Draft: a fixed priority list with an override per team size. C++ port of bots/mybot/src/draft.py (v13).
#pragma once
#include <cambc.h>

#include <algorithm>
#include <cstddef>
#include <map>
#include <vector>

namespace bot
{
// Map facts for the champion bots, worked out on the first draft turn and sent through draft memory (as draft.py).
// Byte 0, bit 0: no altar can be reached without killing a camp first (01boss-battle, 02guardians, 02the-pack).
inline std::byte analyse_map()
{
	using cambc::bitboard;
	bitboard block = cambc::map::walls() | cambc::map::holes() | cambc::map::altars() | cambc::map::spawn_region(cambc::team::enemy);
	bitboard camps;
	for (const auto& g : cambc::map::camp_groups())
		for (const auto& c : g.camps()) camps.set(c.spawn_position());
	bitboard approach;
	for (auto a : cambc::map::altars().positions()) approach.draw_chebyshev(a, 1);
	approach &= ~(block | camps);
	cambc::distance_field field;
	bitboard visited;
	field.compute(block | camps, cambc::map::spawn_region(cambc::team::ally), visited);
	for (auto p : approach.positions())
		if (field.get(p) < 65535) return std::byte{ 0 };
	return std::byte{ 1 };
}

inline void play_draft()
{
	static bool sent = false;
	if (!sent)
	{
		sent = true;
		try
		{
			cambc::draft_memory = { analyse_map() };
		}
		catch (const cambc::error&)
		{
		}
	}
	using D = cambc::champion_draft;
	static const std::vector<D> PRIORITY{ D::vendetta, D::varg, D::ryth, D::marcella, D::tavi, D::stellar, D::vesper_vale,
										  D::cassi_and_issac, D::willow, D::ren, D::prism };
	// cambc 3.0 strength draft on 4- and 5-pick maps (v13): 130/160 vs the 2.2.5 pro draft.
	static const std::map<std::uint32_t, std::vector<D>> BY_SIZE{
		{ 3, { D::vendetta, D::ryth, D::tavi } },
		{ 4, { D::vendetta, D::vesper_vale, D::tavi, D::marcella } },
		{ 5, { D::vendetta, D::vesper_vale, D::tavi, D::marcella, D::ryth } },
	};
	const auto chosen = cambc::draft::current_draft(cambc::team::ally);
	std::vector<D> order;
	auto it = BY_SIZE.find(cambc::draft::team_size());
	if (it != BY_SIZE.end()) order = it->second;
	order.insert(order.end(), PRIORITY.begin(), PRIORITY.end());
	for (auto pick : order)
	{
		if (std::find(chosen.begin(), chosen.end(), pick) == chosen.end())
		{
			cambc::draft::pick(pick);
			return;
		}
	}
}
} // namespace bot
