// Prefix-state lattices (strict left-branching and stack systems): construction with backward
// pruning, forward-backward, Viterbi and the unpruned state-set searches used by the proposal
// steps.  Mirrors ccg/lattice.py, ccg/stack_lattice.py and the search helpers in ccg/mdl.py.
#pragma once
#include <cmath>
#include "core.h"
#include "scorer.h"

namespace ccg {

struct LEdge {
    Id prev;        // previous state (NONE at position 0)
    Id cat;         // word category
    Id rule;        // Rule (left) or rule-sequence id (stack)
    double w;       // 1 / n_applicable
    int prev_idx;   // index of prev in the previous layer (after finalisation; -1 at position 0)
};

struct Layer {
    std::vector<Id> states;                       // insertion order (Python dict order)
    std::vector<std::vector<LEdge>> edges;        // incoming edges per state
    std::unordered_map<Id, int> index;
    int add(Id st) {
        auto it = index.find(st);
        if (it != index.end()) return it->second;
        int i = (int)states.size();
        states.push_back(st);
        edges.emplace_back();
        index.emplace(st, i);
        return i;
    }
    int find(Id st) const { auto it = index.find(st); return it == index.end() ? -1 : it->second; }
    size_t size() const { return states.size(); }
};

struct Lattice {
    SysParams sys;
    std::vector<Id> words;
    Id goal_state = NONE;
    std::vector<Layer> layers;                    // k = 0..n-1 (position k+1); shorter after a failure
    bool accepted = false;
    int fail_pos = -1;
    std::vector<Id> fail_states;
    std::vector<int> unpruned_sizes, branch_counts;

    int n() const { return (int)words.size(); }
    size_t n_edges() const {
        size_t s = 0;
        for (auto& l : layers) for (auto& es : l.edges) s += es.size();
        return s;
    }
};

using Cands = std::vector<std::vector<Id>>;       // candidate categories per position

inline Lattice build_lattice(const SysParams& p, const std::vector<Id>& words, const Cands& cands, Id goal_cat) {
    Lattice L;
    L.sys = p;
    L.words = words;
    L.goal_state = goal_state_of(p, goal_cat);
    int n = (int)words.size();
    std::vector<Id> prev{NONE};
    StepOut succ;
    for (int k = 0; k < n; ++k) {
        Layer layer;
        for (Id s : prev) {
            for (Id c : cands[k]) {
                successors(p, s, c, succ);
                L.branch_counts.push_back((int)succ.size());
                if (succ.empty()) continue;
                double wt = 1.0 / (double)succ.size();
                for (auto& [st, rule] : succ) {
                    int idx = layer.add(st);
                    layer.edges[idx].push_back(LEdge{s, c, rule, wt, -1});
                }
            }
        }
        L.unpruned_sizes.push_back((int)layer.size());
        L.layers.push_back(std::move(layer));
        if (L.layers.back().states.empty()) { L.fail_pos = k + 1; break; }
        prev = L.layers.back().states;
    }
    if (L.fail_pos != -1) {
        if (L.fail_pos >= 2) L.fail_states = L.layers[L.fail_pos - 2].states;
        return L;
    }
    if (L.layers[n - 1].find(L.goal_state) < 0) {
        L.fail_pos = n + 1;
        L.fail_states = L.layers[n - 1].states;
        return L;
    }
    // backward pruning to states on an accepting path
    std::unordered_set<Id> alive{L.goal_state};
    for (int k = n - 1; k >= 0; --k) {
        Layer& old = L.layers[k];
        Layer nl;
        std::unordered_set<Id> prev_alive;
        for (size_t i = 0; i < old.states.size(); ++i) {
            if (!alive.count(old.states[i])) continue;
            int idx = nl.add(old.states[i]);
            nl.edges[idx] = std::move(old.edges[i]);
            for (auto& e : nl.edges[idx]) prev_alive.insert(e.prev);
        }
        L.layers[k] = std::move(nl);
        alive = std::move(prev_alive);
    }
    for (int k = 0; k < n; ++k)
        for (auto& es : L.layers[k].edges)
            for (auto& e : es) e.prev_idx = k == 0 ? -1 : L.layers[k - 1].find(e.prev);
    L.accepted = true;
    return L;
}

// ----------------------------------------------------------------------------- forward-backward
inline void forward(const Lattice& L, const Scorer& sc, std::vector<std::vector<double>>& alpha) {
    int n = L.n();
    alpha.assign(n, {});
    for (int k = 0; k < n; ++k) {
        const Layer& layer = L.layers[k];
        Id word = L.words[k];
        alpha[k].assign(layer.size(), 0.0);
        for (size_t i = 0; i < layer.size(); ++i) {
            double tot = 0.0;
            for (const LEdge& e : layer.edges[i]) {
                double ap = k == 0 ? 1.0 : alpha[k - 1][e.prev_idx];
                if (ap != 0.0) tot += ap * sc.w(e.prev, e.cat, word) * e.w;
            }
            alpha[k][i] = tot;
        }
    }
}

inline double Z_from_alpha(const Lattice& L, const Scorer& sc, Id goal, const std::vector<std::vector<double>>& alpha) {
    int g = L.layers[L.n() - 1].find(goal);
    if (g < 0) return 0.0;
    return alpha[L.n() - 1][g] * sc.final_weight();
}

inline double Z(const Lattice& L, const Scorer& sc, Id goal) {
    if (!L.accepted) return 0.0;
    std::vector<std::vector<double>> alpha;
    forward(L, sc, alpha);
    return Z_from_alpha(L, sc, goal, alpha);
}

// on_edge(k, edge, state index, posterior); returns Z (0 if not accepted / zero probability).
template <class F> double forward_backward(const Lattice& L, const Scorer& sc, Id goal, F&& on_edge) {
    if (!L.accepted) return 0.0;
    int n = L.n();
    std::vector<std::vector<double>> alpha;
    forward(L, sc, alpha);
    double Zv = Z_from_alpha(L, sc, goal, alpha);
    if (Zv <= 0.0) return 0.0;
    std::vector<double> beta_next(L.layers[n - 1].size(), 0.0);
    beta_next[L.layers[n - 1].find(goal)] = sc.final_weight();
    for (int k = n - 1; k >= 0; --k) {
        const Layer& layer = L.layers[k];
        Id word = L.words[k];
        std::vector<double> beta_prev(k == 0 ? 1 : L.layers[k - 1].size(), 0.0);
        for (size_t i = 0; i < layer.size(); ++i) {
            double bn = beta_next[i];
            if (bn == 0.0) continue;
            for (const LEdge& e : layer.edges[i]) {
                double ap = k == 0 ? 1.0 : alpha[k - 1][e.prev_idx];
                if (ap == 0.0) continue;
                double p = sc.w(e.prev, e.cat, word) * e.w;
                if (p == 0.0) continue;
                beta_prev[k == 0 ? 0 : e.prev_idx] += p * bn;
                on_edge(k, e, (int)i, ap * p * bn / Zv);
            }
        }
        beta_next = std::move(beta_prev);
    }
    return Zv;
}

// ----------------------------------------------------------------------------- Viterbi
struct ViterbiPath {
    bool ok = false;
    double prob = 0.0;
    std::vector<const LEdge*> edges;    // one per position
    std::vector<Id> states;             // next state per position
};

inline ViterbiPath viterbi(const Lattice& L, const Scorer& sc, Id goal) {
    ViterbiPath out;
    if (!L.accepted) return out;
    int n = L.n();
    std::vector<std::vector<double>> bp(n);
    std::vector<std::vector<int>> be(n);
    for (int k = 0; k < n; ++k) {
        const Layer& layer = L.layers[k];
        Id word = L.words[k];
        bp[k].assign(layer.size(), 0.0);
        be[k].assign(layer.size(), -1);
        for (size_t i = 0; i < layer.size(); ++i) {
            double best = 0.0; int bidx = -1;
            const auto& es = layer.edges[i];
            for (size_t j = 0; j < es.size(); ++j) {
                const LEdge& e = es[j];
                double pv;
                if (k == 0) pv = 1.0;
                else { if (be[k - 1][e.prev_idx] < 0) continue; pv = bp[k - 1][e.prev_idx]; }
                double p = pv * sc.w(e.prev, e.cat, word) * e.w;
                if (p > best) { best = p; bidx = (int)j; }
            }
            bp[k][i] = best; be[k][i] = bidx;
        }
    }
    int g = L.layers[n - 1].find(goal);
    if (g < 0 || be[n - 1][g] < 0) return out;
    out.ok = true;
    out.prob = bp[n - 1][g] * sc.final_weight();
    out.edges.resize(n); out.states.resize(n);
    int cur = g;
    for (int k = n - 1; k >= 0; --k) {
        const LEdge& e = L.layers[k].edges[cur][be[k][cur]];
        out.edges[k] = &e;
        out.states[k] = L.layers[k].states[cur];
        cur = e.prev_idx;
    }
    return out;
}

// ----------------------------------------------------------------------------- unpruned state-set search (mdl.py)
inline void expand(const SysParams& p, std::unordered_set<Id>& states, const std::vector<Id>& cands) {
    std::unordered_set<Id> nxt;
    StepOut succ;
    for (Id st : states)
        for (Id c : cands) {
            successors(p, st, c, succ);
            for (auto& [r, _] : succ) nxt.insert(r);
        }
    states = std::move(nxt);
}

// prefix states after words[:upto]
inline std::unordered_set<Id> forward_states(const SysParams& p, const Cands& cands, int upto) {
    std::unordered_set<Id> states{NONE};
    for (int k = 0; k < upto; ++k) {
        expand(p, states, cands[k]);
        if (states.empty()) break;
    }
    return states;
}

inline bool suffix_completes(const SysParams& p, const Cands& cands, std::unordered_set<Id> states, int k, Id goal_state) {
    for (int j = k; j < (int)cands.size(); ++j) {
        expand(p, states, cands[j]);
        if (states.empty()) return false;
    }
    return states.count(goal_state) > 0;
}

// Memoised suffix reachability for one sentence / support: completes(s, j) == "from state s after
// words[:j], can the goal be reached at the end?" (the same existential question suffix_completes
// answers for a set, shared across the candidate categories of an oracle step).
struct SuffixOracle {
    const SysParams& p;
    const Cands& cands;
    Id goal_state;
    std::unordered_map<uint64_t, bool, U64Hash> memo;    // (state, j) -> completes
    StepOut succ;
    SuffixOracle(const SysParams& p_, const Cands& c_, Id g) : p(p_), cands(c_), goal_state(g) {}
    bool completes(Id s, int j) {
        if (j == (int)cands.size()) return s == goal_state;
        uint64_t key = pack2(s, j);
        auto it = memo.find(key);
        if (it != memo.end()) return it->second;
        bool ok = false;
        std::vector<Id> next;
        for (Id c : cands[j]) {
            successors(p, s, c, succ);
            for (auto& [r, _] : succ) next.push_back(r);
        }
        for (Id r : next) if (completes(r, j + 1)) { ok = true; break; }
        memo.emplace(key, ok);
        return ok;
    }
    bool any_completes(const std::vector<Id>& states, int j) {
        for (Id s : states) if (completes(s, j)) return true;
        return false;
    }
};

}  // namespace ccg
