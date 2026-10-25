"""Map survey probe: prints every camp group (kinds, gold, gems, respawn) plus map facts, during the draft."""
import cambc
from cambc import game_map

T = cambc.Team


def survey():
    w, h = game_map.width(), game_map.height()
    alt = len(game_map.altars().positions())
    bush = sum(bin(v).count("1") for v in game_map.bushes().export_linear_buffer())
    hole = sum(bin(v).count("1") for v in game_map.holes().export_linear_buffer())
    sp = game_map.spawn_region(T.ALLY).positions()
    esp = game_map.spawn_region(T.ENEMY).positions()
    print(f"SURVEY map {w}x{h} picks={cambc.draft.team_size()} altars={alt} bushes={bush} holes={hole} "
          f"spawn={sp[0].x},{sp[0].y} espawn={esp[0].x},{esp[0].y}")
    for g in game_map.camp_groups():
        kinds = "".join("wegGMO"[c.kind()] for c in g.camps())
        c0 = g.camps()[0].spawn_position()
        print(f"GROUP {kinds} gold={g.gold_value()} gems={g.gem_value()} respawn={g.max_respawn_timer()} at={c0.x},{c0.y} id={int(g)}")
        for c in g.camps():
            p = c.spawn_position()
            print(f"CAMPH {int(c)} {'wegGMO'[c.kind()]} {p.x} {p.y} {int(g)}")


def main():
    done = False
    while True:
        try:
            if cambc.is_draft():
                if not done:
                    survey()
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
