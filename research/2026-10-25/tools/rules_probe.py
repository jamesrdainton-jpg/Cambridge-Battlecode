"""Rules probe: dumps engine constants, champion designs, items, consumables and camp designs during the draft."""
import cambc
from cambc import constants

T = cambc.Team


def safe(fn):
    try:
        return fn()
    except Exception as e:  # noqa: BLE001
        return f"ERR {e!r}"


def dump_static():
    print("CONSTANTS", {n: getattr(constants, n) for n in constants._SETTINGS})
    pa = constants.passive_abilities
    print("PASSIVES", {k: getattr(pa, k) for k in dir(pa) if k.isupper()})
    for kind in range(16):
        d = safe(lambda: cambc.Champion.design(kind))
        if isinstance(d, str):
            break
        s = d.base_stats()
        print("CHAMP", kind, safe(lambda: cambc.ChampionType.to_string(kind)), safe(lambda: cambc.PassiveType.to_string(d.passive())),
              {k: getattr(s, k) for k in dir(s) if not k.startswith("_")})
        for a in d.abilities():
            inf = a.info()
            print("   ", type(inf).__name__, {k: getattr(inf, k) for k in dir(inf) if not k.startswith("_")})
    for i in range(cambc.ItemType.COUNT):
        it = cambc.ItemType(i)
        inf = it.info()
        print("ITEM", it.name, inf.cost, inf.combine_count, inf.result, inf.health_points, inf.strength_points,
              inf.focus_points, inf.passive, inf.passive_magnitude, inf.purchasable)
    for i in range(cambc.ConsumableType.COUNT):
        c = cambc.ConsumableType(i)
        print("CONS", c.name, c.cost(), c.carry_limit())
    for k in range(8):
        d = safe(lambda: cambc._bc.camp_design(k))
        if isinstance(d, str) and d.startswith("ERR"):
            print("CAMP", k, d)
            break
        print("CAMP", k, safe(lambda: cambc.CampType.to_string(k)), d)


def main():
    done = False
    while True:
        try:
            if cambc.is_draft():
                if not done:
                    dump_static()
                    done = True
                taken = cambc.draft.current_draft(T.ALLY)
                for k in range(11):
                    if k not in taken:
                        cambc.draft.pick(k)
                        break
        except Exception as e:  # noqa: BLE001
            print("probe error", repr(e))
        cambc.end_turn()


main()
