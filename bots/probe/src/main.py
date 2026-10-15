"""Probe bot: dumps map, constants and champion designs during the draft."""
import cambc
from cambc import game_map, constants

T = cambc.Team


def dump():
    w, h = game_map.width(), game_map.height()
    print(f"MAP {w}x{h} symmetry={game_map.symmetry()} draft_rounds={cambc.draft.team_size()} fuel={cambc.fuel_remaining()}")
    layers = [(game_map.bushes(), 34), (game_map.spawn_region(T.ENEMY), 69), (game_map.spawn_region(T.ALLY), 83),
              (game_map.altars(), 65), (game_map.holes(), 111), (game_map.walls(), 35)]
    grid = bytearray(b"." * (w * h))
    for board, ch in layers:
        for j, v in enumerate(board.export_linear_buffer()):
            if v:
                for b in range(8):
                    if v >> b & 1:
                        grid[j * 8 + b] = ch
    for g in game_map.camp_groups():
        for c in g.camps():
            sp = c.spawn_position()
            grid[sp.y * w + sp.x] = ord("wegGM"[c.kind()])
    print("\n".join(grid[y * w:(y + 1) * w].decode() for y in range(h - 1, -1, -1)))
    print("altars:", [(p.x, p.y) for p in game_map.altars().positions()])
    print("ally spawn:", [(p.x, p.y) for p in game_map.spawn_region(T.ALLY).positions()])
    print("enemy spawn:", [(p.x, p.y) for p in game_map.spawn_region(T.ENEMY).positions()])
    for g in game_map.camp_groups():
        kinds = ["wegGM"[c.kind()] for c in g.camps()]
        pos = [(c.spawn_position().x, c.spawn_position().y) for c in g.camps()]
        print(f"group {int(g)} gold={g.gold_value()} gems={g.gem_value()} respawn={g.max_respawn_timer()} {''.join(kinds)} {pos}")
    print("fuel after dump", cambc.fuel_remaining(), flush=True)


def dump_static():
    print("CONSTANTS", {n: getattr(constants, n) for n in constants._SETTINGS})
    for kind in range(12):
        d = cambc.Champion.design(kind)
        s = d.base_stats()
        ab = [a.info() for a in d.abilities()]
        print("CHAMP", cambc.ChampionType.to_string(kind), cambc.PassiveType.to_string(d.passive()),
              f"hp={s.base_health}+{s.health_growth} str={s.base_strength}+{s.strength_growth} "
              f"foc={s.base_focus}+{s.focus_growth} range={s.base_attack_range} vis={s.vision_radius} "
              f"move={s.base_move_speed} campmul={s.camp_damage_multiplier}")
        for a in ab:
            print("   ", type(a).__name__, {k: getattr(a, k) for k in dir(a) if not k.startswith("_")})
    for i in range(cambc.ItemType.COUNT):
        it = cambc.ItemType(i)
        inf = it.info()
        print("ITEM", it.name, inf.cost, inf.combine_count, inf.result, inf.health_points, inf.strength_points,
              inf.focus_points, inf.passive, inf.passive_magnitude, inf.purchasable)
    for i in range(cambc.ConsumableType.COUNT):
        c = cambc.ConsumableType(i)
        print("CONS", c.name, c.cost(), c.carry_limit())
    for k in range(5):
        print("CAMP", cambc.CampType.to_string(k), cambc._bc.camp_design(k))


def main():
    done = False
    while True:
        try:
            if cambc.is_draft():
                if not done:
                    import sys
                    dump()
                    pass
                    done = True
                taken = cambc.draft.current_draft(T.ALLY)
                for k in range(11):
                    if k not in taken:
                        cambc.draft.pick(k)
                        break
        except Exception as e:
            print("probe error", repr(e))
        cambc.end_turn()


main()
