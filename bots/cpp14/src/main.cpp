// Dispatch draft and gameplay; a failed turn is logged and still yields. C++ port of bots/mybot/src/main.py.
#include <cambc.h>

#include <iostream>
#include <memory>

#include "bot.h"
#include "draft.h"

int main()
{
	std::unique_ptr<bot::Bot> b;
	int errors = 0;
	while (true)
	{
		try
		{
			if (cambc::is_draft())
				bot::play_draft();
			else
			{
				if (!b) b = std::make_unique<bot::Bot>();
				b->turn();
				b->end();
			}
		}
		catch (const std::exception& error)
		{
			if (++errors <= 20) std::cout << "bot error r" << cambc::round_number() << ": " << error.what() << std::endl;
		}
		catch (...)
		{
			if (++errors <= 20) std::cout << "bot error r" << cambc::round_number() << ": unknown" << std::endl;
		}
		cambc::end_turn();
	}
}
