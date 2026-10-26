"""Fuel benchmark (Python): one measurement per gameplay turn (turns 3-7), same work as bench_cpp."""
import cambc
from cambc import game_map, vision, DistanceField, Bitboard, Team

ARR = [1] * 64
X = [12345]


def bench(step):
    f = cambc.fuel_remaining
    f0 = f()
    if step == 0:
        x = X[0]
        arr = ARR
        for _ in range(2000):
            x = (x * 1103515245 + 12345) & 0xFFFFFFFF
            arr[x & 63] += x >> 16
        X[0] = x
        print(f"BENCH py loop2000={f0 - f()}", flush=True)
    elif step == 1:
        walls = game_map.walls() | game_map.holes()
        roots = game_map.spawn_region(Team.ALLY)
        field = DistanceField()
        g0 = f()
        field.compute(walls, roots, Bitboard())
        print(f"BENCH py dfield={g0 - f()}", flush=True)
    elif step == 2:
        groups = game_map.camp_groups()
        print(f"BENCH py camp_groups={f0 - f()} n={len(groups)}", flush=True)
    elif step == 3:
        camps = vision.camps()
        print(f"BENCH py vision_camps={f0 - f()} n={len(camps)}", flush=True)
    elif step == 4:
        me = cambc.me()
        sx = 0
        for _ in range(100):
            sx += me.position().x
        print(f"BENCH py position100={f0 - f()}", flush=True)
    elif step == 5:
        gs = [((i * 37) % 100, (i * 53) % 100, 7 + i, 20 * i, 120 + 50 * i, i % 3) for i in range(24)]
        g0 = f()
        best = -1.0
        bi = -1
        for p in range(50):
            for i in range(24):
                gx, gy, gems, gold, hp, dps = gs[i]
                dx = gx - p
                dy = gy - 2 * p
                if dx < 0:
                    dx = -dx
                if dy < 0:
                    dy = -dy
                d = dx if dx > dy else dy
                cost = d + hp / (60.0 + dps) + 5.0
                v = (gems + 0.4 * gold) / (cost + 5.0)
                if v > best:
                    best = v
                    bi = i
        print(f"BENCH py score1200={g0 - f()} bi={bi}", flush=True)
    elif step == 6:
        W = H = 15
        dist = [65535] * (W * H)
        q = [0]
        dist[0] = 0
        g0 = f()
        h = 0
        while h < len(q):
            c = q[h]
            h += 1
            cx = c % W
            cy = c // W
            dc = dist[c] + 1
            for dy in (-1, 0, 1):
                ny = cy + dy
                if ny < 0 or ny >= H:
                    continue
                for dx in (-1, 0, 1):
                    nx = cx + dx
                    if (dx or dy) and 0 <= nx < W:
                        n = ny * W + nx
                        if dist[n] == 65535:
                            dist[n] = dc
                            q.append(n)
        print(f"BENCH py bfs15x15={g0 - f()} visited={h} of {W * H}", flush=True)


def main():
    turn = 0
    while True:
        try:
            if cambc.is_draft():
                taken = cambc.draft.current_draft(Team.ALLY)
                for k in range(11):
                    if k not in taken:
                        cambc.draft.pick(k)
                        break
            else:
                turn += 1
                if 3 <= turn <= 9:
                    bench(turn - 3)
        except Exception as e:  # noqa: BLE001
            print("bench error", repr(e))
        cambc.end_turn()


main()
