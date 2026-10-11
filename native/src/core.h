// Core data structures of the C++ port: category / stack / word interning and the fixed rule
// systems (strict left-branching combine, stack step, CKY combine_pair).  Mirrors ccg/category.py,
// ccg/combine.py, ccg/stack_lattice.py::step and ccg/cky.py::combine_pair exactly (same rule
// order, same deduplication, same depth bound), so that results are identical to the Python code.
#pragma once
#include <algorithm>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

namespace ccg {

using Id = int32_t;
constexpr Id NONE = -1;      // epsilon state (sentence start)
constexpr Id NOMATCH = -2;   // a state object that can never equal a lattice state

enum Slash : uint8_t { ATOM = 0, FWD = 1, BWD = 2 };
enum Rule : uint8_t { R_LEX = 0, R_FA = 1, R_BA = 2, R_FC = 3, R_BC = 4, R_SA = 5, R_PUSH = 6 };
enum Tag : uint8_t { T_O = 0, T_FC = 1, T_BC = 2 };
enum Kind : uint8_t { K_LEFT = 0, K_STACK = 1 };

inline const char* rule_name(uint8_t r) {
    static const char* names[] = {"LEX", "FA", "BA", "B>", "B<", "SA", "PUSH"};
    return names[r];
}
inline const char* tag_name(uint8_t t) {
    static const char* names[] = {"O", "FC", "BC"};
    return names[t];
}
inline uint8_t tag_of_rule(uint8_t r) { return r == R_FC ? T_FC : r == R_BC ? T_BC : T_O; }

// ----------------------------------------------------------------------------- hashing helpers
inline uint64_t pack2(Id a, Id b) { return (uint64_t(uint32_t(a)) << 32) | uint64_t(uint32_t(b)); }
struct U64Hash {
    size_t operator()(uint64_t x) const noexcept {
        x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; x ^= x >> 33;
        return size_t(x);
    }
};
struct Key128 {
    uint64_t a, b;
    bool operator==(const Key128& o) const noexcept { return a == o.a && b == o.b; }
};
struct Key128Hash {
    size_t operator()(const Key128& k) const noexcept { U64Hash h; return h(k.a * 0x9E3779B97F4A7C15ULL ^ h(k.b)); }
};
struct VecHash {
    template <class V> size_t operator()(const V& v) const noexcept {
        uint64_t h = 1469598103934665603ULL;
        for (auto x : v) { h ^= uint64_t(uint32_t(x)) + 0x9e3779b9ULL; h *= 1099511628211ULL; }
        return size_t(h);
    }
};

// Insertion-ordered accumulator (mirrors Python dict insertion order for the E-step statistics).
template <class K, class H> struct Acc {
    std::unordered_map<K, size_t, H> idx;
    std::vector<std::pair<K, double>> items;
    void add(const K& k, double v) {
        auto it = idx.find(k);
        if (it == idx.end()) { idx.emplace(k, items.size()); items.emplace_back(k, v); }
        else items[it->second].second += v;
    }
    void clear() { idx.clear(); items.clear(); }
};

// ----------------------------------------------------------------------------- categories
struct CatInfo {
    Id res = NONE, arg = NONE;
    Slash slash = ATOM;
    int depth = 0, size = 1, arity = 0;
    Id target = NONE;                              // spine target atom
    std::string name;                              // atoms only
    std::vector<std::pair<Slash, Id>> slots;       // spine slots, innermost first
};

class CatTable {
public:
    std::vector<CatInfo> cats;
    std::unordered_map<std::string, Id> atom_ids;
    std::unordered_map<uint64_t, Id, U64Hash> complex_ids;

    Id atom(const std::string& name) {
        auto it = atom_ids.find(name);
        if (it != atom_ids.end()) return it->second;
        Id id = (Id)cats.size();
        CatInfo ci; ci.name = name; ci.target = id;
        cats.push_back(std::move(ci));
        atom_ids.emplace(name, id);
        return id;
    }
    Id make(Id res, Slash s, Id arg) {
        uint64_t key = (uint64_t(uint32_t(res)) << 33) | (uint64_t(s) << 31) | uint64_t(uint32_t(arg));
        auto it = complex_ids.find(key);
        if (it != complex_ids.end()) return it->second;
        CatInfo ci;
        ci.res = res; ci.arg = arg; ci.slash = s;
        ci.depth = 1 + std::max(cats[res].depth, cats[arg].depth);
        ci.size = 1 + cats[res].size + cats[arg].size;
        ci.arity = cats[res].arity + 1;
        ci.target = cats[res].target;
        ci.slots = cats[res].slots;
        ci.slots.emplace_back(s, arg);
        Id id = (Id)cats.size();
        cats.push_back(std::move(ci));
        complex_ids.emplace(key, id);
        return id;
    }
    // category.build(target, slots) with slot `skip` removed (skip < 0: keep all)
    Id build(Id target, const std::vector<std::pair<Slash, Id>>& slots, int skip) {
        Id c = target;
        for (size_t i = 0; i < slots.size(); ++i) {
            if ((int)i == skip) continue;
            c = make(c, slots[i].first, slots[i].second);
        }
        return c;
    }
    bool is_atom(Id c) const { return cats[c].slash == ATOM; }
    int depth(Id c) const { return cats[c].depth; }
    const CatInfo& operator[](Id c) const { return cats[c]; }
    std::string show(Id c) const {
        const CatInfo& ci = cats[c];
        if (ci.slash == ATOM) return ci.name;
        std::string rs = is_atom(ci.res) ? show(ci.res) : "(" + show(ci.res) + ")";
        std::string as = is_atom(ci.arg) ? show(ci.arg) : "(" + show(ci.arg) + ")";
        return rs + (ci.slash == FWD ? "/" : "\\") + as;
    }
};

// ----------------------------------------------------------------------------- stacks, rule sequences, words
template <class Elem> class SeqTable {
public:
    std::vector<std::vector<Elem>> seqs;
    std::unordered_map<std::vector<Elem>, Id, VecHash> ids;
    Id intern(const std::vector<Elem>& v) {
        auto it = ids.find(v);
        if (it != ids.end()) return it->second;
        Id id = (Id)seqs.size();
        seqs.push_back(v);
        ids.emplace(v, id);
        return id;
    }
    const std::vector<Elem>& get(Id id) const { return seqs[id]; }
    size_t size() const { return seqs.size(); }
};
using StackTable = SeqTable<Id>;
using RuleSeqTable = SeqTable<uint8_t>;

class WordTable {
public:
    std::vector<std::string> words;
    std::unordered_map<std::string, Id> ids;
    Id intern(const std::string& w) {
        auto it = ids.find(w);
        if (it != ids.end()) return it->second;
        Id id = (Id)words.size();
        words.push_back(w);
        ids.emplace(w, id);
        return id;
    }
    const std::string& get(Id id) const { return words[id]; }
};

struct Tables {
    CatTable cats;
    StackTable stacks;
    RuleSeqTable seqs;
    WordTable words;
    bool sa_enabled = true;       // combine.RULES_ON['SA']
};
inline Tables& T() { static Tables* t = new Tables(); return *t; }

// ----------------------------------------------------------------------------- combine (left system)
struct Res {
    int n = 0;
    Id cat[6];
    uint8_t rule[6];
    void add(Id c, uint8_t r, int max_depth) {
        if (T().cats.depth(c) > max_depth) return;
        for (int i = 0; i < n; ++i) if (cat[i] == c) return;
        cat[n] = c; rule[n] = r; ++n;
    }
};

// Index (innermost-first) of the outermost *inner* backward slot of c equal to sigma, or -1.
inline int sa_inner_slot(Id sigma, const CatInfo& c) {
    int best = -1;
    int m = (int)c.slots.size() - 1;      // the outermost slot (index m) is BA, not SA
    for (int i = 0; i < m; ++i)
        if (c.slots[i].first == BWD && c.slots[i].second == sigma) best = i;
    return best;
}

inline Res combine_uncached(Id sigma, Id c, int max_depth, bool sa) {
    Res r;
    if (sigma == NONE) { r.cat[0] = c; r.rule[0] = R_LEX; r.n = 1; return r; }
    CatTable& ct = T().cats;
    CatInfo S = ct[sigma];      // copies: make() may reallocate the table
    CatInfo Cc = ct[c];
    if (S.slash == FWD && S.arg == c) r.add(S.res, R_FA, max_depth);
    if (Cc.slash == BWD && Cc.arg == sigma) r.add(Cc.res, R_BA, max_depth);
    if (S.slash == FWD && Cc.slash == FWD && Cc.res == S.arg) r.add(ct.make(S.res, FWD, Cc.arg), R_FC, max_depth);
    if (S.slash == BWD && Cc.slash == BWD && Cc.arg == S.res) r.add(ct.make(Cc.res, BWD, S.arg), R_BC, max_depth);
    if (sa && Cc.slash != ATOM) {
        int i = sa_inner_slot(sigma, Cc);
        if (i >= 0) r.add(ct.build(Cc.target, Cc.slots, i), R_SA, max_depth);
    }
    return r;
}

inline const Res& combine(Id sigma, Id c, int max_depth, bool sa) {
    static auto* memo = new std::unordered_map<Key128, Res, Key128Hash>();
    Key128 key{pack2(sigma, c), (uint64_t(max_depth) << 1) | uint64_t(sa)};
    auto it = memo->find(key);
    if (it != memo->end()) return it->second;
    Res r = combine_uncached(sigma, c, max_depth, sa);
    return memo->emplace(key, r).first->second;
}

// ----------------------------------------------------------------------------- combine_pair (CKY)
inline const Res& combine_pair(Id left, Id right, bool right_lexical, int max_depth, uint8_t ltag, uint8_t rtag, bool nf) {
    static auto* memo = new std::unordered_map<Key128, Res, Key128Hash>();
    Key128 key{pack2(left, right), (uint64_t(max_depth) << 8) | (uint64_t(right_lexical) << 5) | (uint64_t(ltag) << 3) | (uint64_t(rtag) << 1) | uint64_t(nf)};
    auto it = memo->find(key);
    if (it != memo->end()) return it->second;
    Res r;
    CatTable& ct = T().cats;
    CatInfo L = ct[left];
    CatInfo R = ct[right];
    bool fwd_ok = !(nf && ltag == T_FC);
    bool bwd_ok = !(nf && rtag == T_BC);
    if (fwd_ok && L.slash == FWD && L.arg == right) r.add(L.res, R_FA, max_depth);
    if (bwd_ok && R.slash == BWD && R.arg == left) r.add(R.res, R_BA, max_depth);
    if (fwd_ok && L.slash == FWD && R.slash == FWD && R.res == L.arg) r.add(ct.make(L.res, FWD, R.arg), R_FC, max_depth);
    if (bwd_ok && L.slash == BWD && R.slash == BWD && R.arg == L.res) r.add(ct.make(R.res, BWD, L.arg), R_BC, max_depth);
    if (right_lexical && R.slash != ATOM) {
        int i = sa_inner_slot(left, R);
        if (i >= 0) r.add(ct.build(R.target, R.slots, i), R_SA, max_depth);
    }
    return memo->emplace(key, r).first->second;
}

// ----------------------------------------------------------------------------- stack step
using StepOut = std::vector<std::pair<Id, Id>>;   // (stack id, rule-sequence id)

inline void cascade_rec(std::vector<Id> stack, std::vector<uint8_t> rules, int max_depth, StepOut& out) {
    Tables& t = T();
    if (stack.size() < 2) { out.emplace_back(t.stacks.intern(stack), t.seqs.intern(rules)); return; }
    Id below = stack[stack.size() - 2], top = stack.back();
    Res res = combine(below, top, max_depth, false);     // SA off: the right item is derived
    if (res.n == 0) { out.emplace_back(t.stacks.intern(stack), t.seqs.intern(rules)); return; }
    for (int i = 0; i < res.n; ++i) {
        std::vector<Id> ns(stack.begin(), stack.end() - 2);
        ns.push_back(res.cat[i]);
        std::vector<uint8_t> nr = rules;
        nr.push_back(res.rule[i]);
        cascade_rec(std::move(ns), std::move(nr), max_depth, out);
    }
}

inline const StepOut& step(Id stack, Id c, int max_depth, int max_stack, bool cascade, bool sa) {
    static auto* memo = new std::unordered_map<Key128, StepOut, Key128Hash>();
    Key128 key{pack2(stack, c), (uint64_t(max_depth) << 16) | (uint64_t(max_stack) << 8) | (uint64_t(cascade) << 1) | uint64_t(sa)};
    auto it = memo->find(key);
    if (it != memo->end()) return it->second;
    Tables& t = T();
    StepOut out;
    if (stack == NONE) {
        out.emplace_back(t.stacks.intern(std::vector<Id>{c}), t.seqs.intern(std::vector<uint8_t>{R_PUSH}));
        return memo->emplace(key, std::move(out)).first->second;
    }
    std::vector<Id> st = t.stacks.get(stack);
    Res res = combine(st.back(), c, max_depth, sa);
    if (res.n == 0) {
        if ((int)st.size() < max_stack) {
            st.push_back(c);
            out.emplace_back(t.stacks.intern(st), t.seqs.intern(std::vector<uint8_t>{R_PUSH}));
        }
        return memo->emplace(key, std::move(out)).first->second;
    }
    StepOut raw;
    for (int i = 0; i < res.n; ++i) {
        std::vector<Id> base = st;
        base.back() = res.cat[i];
        std::vector<uint8_t> rules{res.rule[i]};
        if (cascade) cascade_rec(std::move(base), std::move(rules), max_depth, raw);
        else raw.emplace_back(t.stacks.intern(base), t.seqs.intern(rules));
    }
    std::unordered_set<Id> seen;
    for (auto& p : raw) if (seen.insert(p.first).second) out.push_back(p);
    return memo->emplace(key, std::move(out)).first->second;
}

// ----------------------------------------------------------------------------- unified successor function
struct SysParams {
    Kind kind = K_LEFT;
    int max_depth = 4;
    int max_stack = 1;
    bool cascade = true;
};

// Successors of `state` on word category c: (next state, rule id).  rule id is a Rule for the left
// system and a rule-sequence id for the stack system.
inline void successors(const SysParams& p, Id state, Id c, StepOut& out) {
    out.clear();
    if (p.kind == K_LEFT) {
        const Res& r = combine(state, c, p.max_depth, T().sa_enabled);
        for (int i = 0; i < r.n; ++i) out.emplace_back(r.cat[i], r.rule[i]);
    } else {
        const StepOut& s = step(state, c, p.max_depth, p.max_stack, p.cascade, T().sa_enabled);
        out.insert(out.end(), s.begin(), s.end());
    }
}

inline Id goal_state_of(const SysParams& p, Id goal_cat) {
    return p.kind == K_LEFT ? goal_cat : T().stacks.intern(std::vector<Id>{goal_cat});
}

}  // namespace ccg
