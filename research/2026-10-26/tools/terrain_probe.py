"""Terrain probe: prints the map as rows of characters during the draft (team-a.stdout of the replay bundle).

# wall, o hole, A altar, comma bush, . floor; camps by kind: w wolf, e elk, g gem cluster, G gold cluster, M monolith,
O golem. Run: mkdir -p bots/rs_terrain/src && cp research/2026-10-26/tools/terrain_probe.py bots/rs_terrain/src/main.py
then .venv/Scripts/cambc.exe run rs_terrain rs_terrain --map MAP --rounds 1 and read the ROW lines from team-a.stdout.
"""
import cambc
from cambc import game_map

T = cambc.Team


def dump():
    w, h = game_map.width(), game_map.height()
    walls, holes, bushes, altars = ({(q.x, q.y) for q in b.positions()} for b in
                                    (game_map.walls(), game_map.holes(), game_map.bushes(), game_map.altars()))
    camps = {}
    for g in game_map.camp_groups():
        for c in g.camps():
            p = c.spawn_position()
            camps[(p.x, p.y)] = "wegGMO"[c.kind()]
    for y in range(h):
        row = ""
        for x in range(w):
            v = (x, y)
            ch = "."
            if v in walls: ch = "#"
            elif v in holes: ch = "o"
            elif v in altars: ch = "A"
            elif v in bushes: ch = ","
            if (x, y) in camps: ch = camps[(x, y)]
            row += ch
        print("ROW", f"{y:2d}", row)


def main():
    done = False
    while True:
        try:
            if cambc.is_draft():
                if not done:
                    dump()
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
