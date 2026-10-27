"""Probe: print a map as text on the first game turn (team A's first champion only).

Copy to bots/probe_map/src/main.py and run `cambc run probe_map idle --map NAME --rounds 1`; the grid is in
team-a.stdout. Legend: # wall, o hole, A altar, S our spawn, E enemy spawn, " bush, c camp spawn tile, . floor.
"""
import cambc
from cambc import Team, Vec2, game_map

done = False
while True:
    try:
        if cambc.is_draft():
            taken = cambc.draft.current_draft(Team.ALLY)
            for k in range(11):
                if k not in taken:
                    cambc.draft.pick(k)
                    break
        elif not done:
            done = True
            w, h = game_map.width(), game_map.height()
            walls, holes, altars = game_map.walls(), game_map.holes(), game_map.altars()
            bushes = game_map.bushes()
            mine, theirs = game_map.spawn_region(Team.ALLY), game_map.spawn_region(Team.ENEMY)
            camps = set()
            for g in game_map.camp_groups():
                for c in g.camps():
                    p = c.spawn_position()
                    camps.add((p.x, p.y))
            print("MAP", w, h)
            for y in range(h):
                row = []
                for x in range(w):
                    v = Vec2(x, y)
                    ch = "."
                    if walls.is_set(v):
                        ch = "#"
                    elif holes.is_set(v):
                        ch = "o"
                    elif altars.is_set(v):
                        ch = "A"
                    elif mine.is_set(v):
                        ch = "S"
                    elif theirs.is_set(v):
                        ch = "E"
                    elif (x, y) in camps:
                        ch = "c"
                    elif bushes.is_set(v):
                        ch = '"'
                    row.append(ch)
                print(f"{y:3d} " + "".join(row))
    except Exception as e:
        print("probe error", repr(e))
    cambc.end_turn()
