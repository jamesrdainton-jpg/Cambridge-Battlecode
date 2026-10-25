// Fuel benchmark (C++): one measurement per gameplay turn (turns 3-7), same work as bench_py.
#include <cambc.h>
#include <cstdint>
#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdlib>

static std::vector<std::uint32_t> arr(64, 1);
static std::uint32_t x = 12345;

static void bench(int step) {
    using namespace cambc;
    auto f0 = fuel_remaining();
    std::uint64_t f1 = 0;
    long chk = 0;
    if (step == 0) {
        for (int i = 0; i < 2000; ++i) { x = x * 1103515245u + 12345u; arr[x & 63] += x >> 16; }
        f1 = fuel_remaining(); chk = arr[x & 63];
        std::cout << "BENCH cpp loop2000=" << (f0 - f1);
    } else if (step == 1) {
        auto walls = map::walls() | map::holes();
        const auto& roots = map::spawn_region(team::ally);
        distance_field field; bitboard visited;
        auto g0 = fuel_remaining();
        field.compute(walls, roots, visited);
        f1 = fuel_remaining(); chk = field.get(self().position());
        std::cout << "BENCH cpp dfield=" << (g0 - f1);
    } else if (step == 2) {
        auto groups = map::camp_groups();
        f1 = fuel_remaining(); chk = (long)groups.size();
        std::cout << "BENCH cpp camp_groups=" << (f0 - f1);
    } else if (step == 3) {
        auto camps = vision::camps();
        f1 = fuel_remaining(); chk = (long)camps.size();
        std::cout << "BENCH cpp vision_camps=" << (f0 - f1);
    } else if (step == 4) {
        auto& me = self();
        for (int i = 0; i < 100; ++i) chk += me.position().x;
        f1 = fuel_remaining();
        std::cout << "BENCH cpp position100=" << (f0 - f1);
    } else if (step == 5) {
        // Scoring-style loop: 24 records with fields, a score per record, best kept; 50 passes.
        struct G { int x, y, gems, gold, hp, dps; };
        std::vector<G> gs;
        for (int i = 0; i < 24; ++i) gs.push_back({(i * 37) % 100, (i * 53) % 100, 7 + i, 20 * i, 120 + 50 * i, i % 3});
        double best = -1; int bi = -1;
        for (int pass = 0; pass < 50; ++pass)
            for (int i = 0; i < 24; ++i) {
                const G& g = gs[i];
                int d = std::max(std::abs(g.x - pass), std::abs(g.y - 2 * pass));
                double cost = d + g.hp / (60.0 + g.dps) + 5.0;
                double v = (g.gems + 0.4 * g.gold) / (cost + 5.0);
                if (v > best) { best = v; bi = i; }
            }
        f1 = fuel_remaining(); chk = bi;
        std::cout << "BENCH cpp score1200=" << (f0 - f1);
    } else if (step == 6) {
        // Pure-language BFS over a 100x100 grid (no SDK distance field), 8 directions.
        const int W = 15, H = 15;
        std::vector<std::uint16_t> dist(W * H, 65535);
        std::vector<int> q; q.reserve(W * H);
        dist[0] = 0; q.push_back(0);
        for (std::size_t h = 0; h < q.size(); ++h) {
            int c = q[h], cx = c % W, cy = c / W;
            for (int dy = -1; dy <= 1; ++dy) for (int dx = -1; dx <= 1; ++dx) {
                int nx = cx + dx, ny = cy + dy;
                if ((dx || dy) && nx >= 0 && ny >= 0 && nx < W && ny < H && dist[ny * W + nx] == 65535) {
                    dist[ny * W + nx] = dist[c] + 1; q.push_back(ny * W + nx);
                }
            }
        }
        f1 = fuel_remaining(); chk = dist[W * H - 1];
        std::cout << "BENCH cpp bfs15x15=" << (f0 - f1);
    }
    std::cout << " chk=" << chk << " start=" << f0 << std::endl;
}

int main() {
    int turn = 0;
    while (true) {
        try {
            if (cambc::is_draft()) {
                const auto chosen = cambc::draft::current_draft(cambc::team::ally);
                for (int i = 0; i < 11; ++i) {
                    auto pick = static_cast<cambc::champion_draft>(i);
                    bool taken = false;
                    for (auto c : chosen) taken = taken || c == pick;
                    if (!taken) { cambc::draft::pick(pick); break; }
                }
            } else {
                ++turn;
                if (turn >= 3 && turn <= 9) bench(turn - 3);
            }
        } catch (const std::exception& e) {
            std::cout << "bench error: " << e.what() << std::endl;
        }
        cambc::end_turn();
    }
}
