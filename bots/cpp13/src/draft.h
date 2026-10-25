// Draft: a fixed priority list with an override per team size. C++ port of bots/mybot/src/draft.py (v13).
#pragma once
#include <cambc.h>

#include <algorithm>
#include <map>
#include <vector>

namespace bot
{
inline void play_draft()
{
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
