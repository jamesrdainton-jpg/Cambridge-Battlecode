"""Dispatch draft and gameplay; a failed turn is logged and still yields."""
import cambc
import draft

ERRORS = [0]


def main():
    bot = None
    while True:
        try:
            if cambc.is_draft():
                draft.play()
            else:
                if bot is None:
                    from bot import Bot, DEBUG
                    f0 = cambc.fuel_remaining()
                    bot = Bot()
                    if DEBUG:
                        print(f"INIT fuel used {f0 - cambc.fuel_remaining()} of {f0}")
                bot.turn()
                bot.end()
        except Exception as error:
            ERRORS[0] += 1
            if ERRORS[0] <= 20:
                import traceback
                print(f"bot error r{cambc.round_number()}: {error!r}")
                traceback.print_exc()
        cambc.end_turn()


if __name__ == "__main__":
    main()
