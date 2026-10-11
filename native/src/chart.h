// CKY contrast system (ccg/cky.py): hypergraph of all binary derivations under a support, with the
// optional Eisner (1996) normal form; inside-outside, Viterbi tree and derivation counting.
#pragma once
#include <cmath>
#include "core.h"
#include "scorer.h"

namespace ccg {

struct CNode { Id cat; uint8_t tag; };
struct CEdge {
    bool lex;        // LEX edge (leaf) or BIN edge
    Id word;         // LEX
    int k, l, r;     // BIN: split point and node indices in cells (i,k) and (k,j)
    uint8_t rule;
    double w;        // 1 / n_results
};
struct Cell {
    std::vector<CNode> nodes;
    std::vector<std::vector<CEdge>> edges;
    std::unordered_map<uint32_t, int> index;
    static uint32_t key(Id cat, uint8_t tag) { return (uint32_t(cat) << 2) | tag; }
    int add(Id cat, uint8_t tag, bool* created = nullptr) {
        uint32_t k = key(cat, tag);
        auto it = index.find(k);
        if (it != index.end()) { if (created) *created = false; return it->second; }
        int i = (int)nodes.size();
        nodes.push_back(CNode{cat, tag});
        edges.emplace_back();
        index.emplace(k, i);
        if (created) *created = true;
        return i;
    }
    size_t size() const { return nodes.size(); }
};

struct Chart {
    int n = 0;
    bool nf = false;
    int max_depth = 4;
    Id goal = NONE;
    std::vector<Id> words;
    std::vector<Cell> cells;     // (i, j) -> cells[i * (n + 1) + j]
    std::vector<int> roots;      // node indices in cell (0, n)
    bool accepted = false;

    Cell& cell(int i, int j) { return cells[i * (n + 1) + j]; }
    const Cell& cell(int i, int j) const { return cells[i * (n + 1) + j]; }
    size_t n_edges() const {
        size_t s = 0;
        for (auto& c : cells) for (auto& es : c.edges) s += es.size();
        return s;
    }
    int n_cells() const { return n * (n + 1) / 2; }
};

inline void prune_chart(Chart& ch) {
    int n = ch.n;
    std::vector<std::vector<char>> alive(ch.cells.size());
    for (size_t c = 0; c < ch.cells.size(); ++c) alive[c].assign(ch.cells[c].size(), 0);
    struct Item { int i, j, idx; };
    std::vector<Item> stack;
    for (int r : ch.roots) stack.push_back({0, n, r});
    while (!stack.empty()) {
        Item it = stack.back(); stack.pop_back();
        char& a = alive[it.i * (n + 1) + it.j][it.idx];
        if (a) continue;
        a = 1;
        for (const CEdge& e : ch.cell(it.i, it.j).edges[it.idx])
            if (!e.lex) { stack.push_back({it.i, e.k, e.l}); stack.push_back({e.k, it.j, e.r}); }
    }
    // compact every cell, remembering old -> new indices
    std::vector<std::vector<int>> remap(ch.cells.size());
    for (size_t c = 0; c < ch.cells.size(); ++c) {
        Cell& old = ch.cells[c];
        remap[c].assign(old.size(), -1);
        Cell nc;
        for (size_t i = 0; i < old.size(); ++i) {
            if (!alive[c][i]) continue;
            int ni = nc.add(old.nodes[i].cat, old.nodes[i].tag);
            nc.edges[ni] = std::move(old.edges[i]);
            remap[c][i] = ni;
        }
        ch.cells[c] = std::move(nc);
    }
    for (int i = 0; i < n; ++i)
        for (int j = i + 1; j <= n; ++j)
            for (auto& es : ch.cell(i, j).edges)
                for (auto& e : es)
                    if (!e.lex) { e.l = remap[i * (n + 1) + e.k][e.l]; e.r = remap[e.k * (n + 1) + j][e.r]; }
    for (int& r : ch.roots) r = remap[0 * (n + 1) + n][r];
}

inline Chart build_chart(const std::vector<Id>& words, const Cands& cands, int max_depth, Id goal, bool nf) {
    Chart ch;
    ch.n = (int)words.size();
    ch.nf = nf; ch.max_depth = max_depth; ch.goal = goal; ch.words = words;
    int n = ch.n;
    ch.cells.assign((n + 1) * (n + 1), Cell{});
    for (int i = 0; i < n; ++i) {
        Cell& c = ch.cell(i, i + 1);
        for (Id cat : cands[i]) {
            bool created;
            int idx = c.add(cat, T_O, &created);
            if (created) c.edges[idx].push_back(CEdge{true, words[i], 0, 0, 0, R_LEX, 1.0});
        }
    }
    for (int span = 2; span <= n; ++span) {
        for (int i = 0; i + span <= n; ++i) {
            int j = i + span;
            Cell& d = ch.cell(i, j);
            for (int k = i + 1; k < j; ++k) {
                const Cell& L = ch.cell(i, k);
                const Cell& R = ch.cell(k, j);
                if (L.size() == 0 || R.size() == 0) continue;
                bool rlex = (j - k == 1);
                for (size_t li = 0; li < L.size(); ++li) {
                    for (size_t ri = 0; ri < R.size(); ++ri) {
                        const CNode ln = L.nodes[li];
                        const CNode rn = R.nodes[ri];
                        Res res = combine_pair(ln.cat, rn.cat, rlex, max_depth, ln.tag, rn.tag, nf);
                        if (res.n == 0) continue;
                        double wgt = 1.0 / res.n;
                        for (int t = 0; t < res.n; ++t) {
                            uint8_t tag = nf ? tag_of_rule(res.rule[t]) : T_O;
                            int idx = d.add(res.cat[t], tag);
                            d.edges[idx].push_back(CEdge{false, NONE, k, (int)li, (int)ri, res.rule[t], wgt});
                        }
                    }
                }
            }
        }
    }
    const Cell& top = ch.cell(0, n);
    for (size_t i = 0; i < top.size(); ++i) if (top.nodes[i].cat == goal) ch.roots.push_back((int)i);
    ch.accepted = !ch.roots.empty();
    if (ch.accepted) prune_chart(ch);
    return ch;
}

// ----------------------------------------------------------------------------- inside-outside
using Table = std::vector<std::vector<double>>;    // per cell, per node

inline double inside_pass(const Chart& ch, const CKYScorer& sc, Table& inside) {
    int n = ch.n;
    inside.assign(ch.cells.size(), {});
    for (size_t c = 0; c < ch.cells.size(); ++c) inside[c].assign(ch.cells[c].size(), 0.0);
    for (int span = 1; span <= n; ++span)
        for (int i = 0; i + span <= n; ++i) {
            int j = i + span;
            const Cell& cell = ch.cell(i, j);
            auto& in = inside[i * (n + 1) + j];
            for (size_t nd = 0; nd < cell.size(); ++nd) {
                Id c = cell.nodes[nd].cat;
                double tot = 0.0;
                for (const CEdge& e : cell.edges[nd]) {
                    if (e.lex) tot += sc.lex_p(c, e.word);
                    else tot += sc.exp_p(c, e.rule, ch.cell(i, e.k).nodes[e.l].cat, ch.cell(e.k, j).nodes[e.r].cat) * e.w
                                * inside[i * (n + 1) + e.k][e.l] * inside[e.k * (n + 1) + j][e.r];
                }
                in[nd] = tot;
            }
        }
    double Zv = 0.0;
    for (int r : ch.roots) Zv += inside[0 * (n + 1) + n][r];
    return Zv;
}

inline double cky_Z(const Chart& ch, const CKYScorer& sc) {
    if (!ch.accepted) return 0.0;
    Table inside;
    return inside_pass(ch, sc, inside);
}

// on_exp(parent cat, rule, lcat, rcat, post); on_leaf(position, cat, post).  Returns Z.
template <class FE, class FL> double inside_outside(const Chart& ch, const CKYScorer& sc, FE&& on_exp, FL&& on_leaf) {
    if (!ch.accepted) return 0.0;
    int n = ch.n;
    Table inside;
    double Zv = inside_pass(ch, sc, inside);
    if (Zv <= 0.0) return 0.0;
    Table outside(ch.cells.size());
    for (size_t c = 0; c < ch.cells.size(); ++c) outside[c].assign(ch.cells[c].size(), 0.0);
    for (int r : ch.roots) outside[0 * (n + 1) + n][r] = 1.0;
    for (int span = n; span >= 1; --span)
        for (int i = 0; i + span <= n; ++i) {
            int j = i + span;
            const Cell& cell = ch.cell(i, j);
            for (size_t nd = 0; nd < cell.size(); ++nd) {
                Id c = cell.nodes[nd].cat;
                double o = outside[i * (n + 1) + j][nd];
                if (o == 0.0) continue;
                for (const CEdge& e : cell.edges[nd]) {
                    if (e.lex) { on_leaf(i, c, o * sc.lex_p(c, e.word) / Zv); continue; }
                    int lc = i * (n + 1) + e.k, rc = e.k * (n + 1) + j;
                    Id lcat = ch.cell(i, e.k).nodes[e.l].cat, rcat = ch.cell(e.k, j).nodes[e.r].cat;
                    double li = inside[lc][e.l], ri = inside[rc][e.r];
                    double p = sc.exp_p(c, e.rule, lcat, rcat) * e.w;
                    if (!(li != 0.0 && ri != 0.0 && p != 0.0)) continue;
                    on_exp(c, e.rule, lcat, rcat, o * p * li * ri / Zv);
                    outside[lc][e.l] += o * p * ri;
                    outside[rc][e.r] += o * p * li;
                }
            }
        }
    return Zv;
}

// ----------------------------------------------------------------------------- Viterbi tree
struct BestTable { Table p; std::vector<std::vector<int>> e; };

inline bool viterbi_chart(const Chart& ch, const CKYScorer& sc, BestTable& best, int& root, double& prob) {
    if (!ch.accepted) return false;
    int n = ch.n;
    best.p.assign(ch.cells.size(), {}); best.e.assign(ch.cells.size(), {});
    for (size_t c = 0; c < ch.cells.size(); ++c) { best.p[c].assign(ch.cells[c].size(), 0.0); best.e[c].assign(ch.cells[c].size(), -1); }
    for (int span = 1; span <= n; ++span)
        for (int i = 0; i + span <= n; ++i) {
            int j = i + span;
            const Cell& cell = ch.cell(i, j);
            for (size_t nd = 0; nd < cell.size(); ++nd) {
                Id c = cell.nodes[nd].cat;
                double bp = 0.0; int bidx = -1;
                const auto& es = cell.edges[nd];
                for (size_t q = 0; q < es.size(); ++q) {
                    const CEdge& e = es[q];
                    double p;
                    if (e.lex) p = sc.lex_p(c, e.word);
                    else {
                        int lc = i * (n + 1) + e.k, rc = e.k * (n + 1) + j;
                        if (best.e[lc][e.l] < 0 || best.e[rc][e.r] < 0) continue;
                        p = sc.exp_p(c, e.rule, ch.cell(i, e.k).nodes[e.l].cat, ch.cell(e.k, j).nodes[e.r].cat) * e.w
                            * best.p[lc][e.l] * best.p[rc][e.r];
                    }
                    if (p > bp) { bp = p; bidx = (int)q; }
                }
                best.p[i * (n + 1) + j][nd] = bp;
                best.e[i * (n + 1) + j][nd] = bidx;
            }
        }
    root = -1; prob = 0.0;
    bool first = true;
    for (int r : ch.roots) {
        int c = 0 * (n + 1) + n;
        if (best.e[c][r] < 0) continue;
        if (first || best.p[c][r] > prob) { prob = best.p[c][r]; root = r; first = false; }
    }
    return root >= 0;
}

inline uint64_t count_derivations(const Chart& ch) {
    if (!ch.accepted) return 0;
    int n = ch.n;
    std::vector<std::vector<uint64_t>> cnt(ch.cells.size());
    for (size_t c = 0; c < ch.cells.size(); ++c) cnt[c].assign(ch.cells[c].size(), 0);
    for (int span = 1; span <= n; ++span)
        for (int i = 0; i + span <= n; ++i) {
            int j = i + span;
            const Cell& cell = ch.cell(i, j);
            for (size_t nd = 0; nd < cell.size(); ++nd) {
                uint64_t tot = 0;
                for (const CEdge& e : cell.edges[nd])
                    tot += e.lex ? 1 : cnt[i * (n + 1) + e.k][e.l] * cnt[e.k * (n + 1) + j][e.r];
                cnt[i * (n + 1) + j][nd] = tot;
            }
        }
    uint64_t s = 0;
    for (int r : ch.roots) s += cnt[0 * (n + 1) + n][r];
    return s;
}

}  // namespace ccg
