// nanobind module _ccg_native: Python-facing API of the C++ port.  Categories cross the boundary
// as the project's nested tuples / strings, parser states as categories (left system) or
// ccg.stack_lattice.Stack tuples (stack system), models as parameter dictionaries copied into
// Scorer tables by ccg/native.py.
#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include "core.h"
#include "scorer.h"
#include "lattice.h"
#include "chart.h"

namespace nb = nanobind;
using namespace nb::literals;
using namespace ccg;

// ------------------------------------------------------------------ Python object caches (never freed)
struct PyCache {
    std::vector<nb::object> cats, stacks, seqs, words;
    nb::object rules[7], tags[3], slashes[3], sides[2];
    nb::object stack_cls;
};
static PyCache& PC() { static PyCache* c = new PyCache(); return *c; }

static void dset(nb::dict& d, nb::handle k, nb::handle v) {
    if (PyDict_SetItem(d.ptr(), k.ptr(), v.ptr()) != 0) throw nb::python_error();
}

template <class F> static void for_each(nb::handle iterable, F&& f) {
    PyObject* it = PyObject_GetIter(iterable.ptr());
    if (!it) throw nb::python_error();
    nb::object guard = nb::steal(it);
    while (PyObject* item = PyIter_Next(it)) {
        nb::object o = nb::steal(item);
        f(nb::handle(o));
    }
    if (PyErr_Occurred()) throw nb::python_error();
}

// ------------------------------------------------------------------ categories
static Id cat_from_py(nb::handle h) {
    PyObject* p = h.ptr();
    if (PyUnicode_Check(p)) {
        Py_ssize_t n; const char* s = PyUnicode_AsUTF8AndSize(p, &n);
        if (!s) throw nb::python_error();
        return T().cats.atom(std::string(s, (size_t)n));
    }
    if (PyTuple_Check(p) && PyTuple_GET_SIZE(p) == 3) {
        PyObject* sl = PyTuple_GET_ITEM(p, 1);
        if (PyUnicode_Check(sl)) {
            Py_ssize_t n; const char* s = PyUnicode_AsUTF8AndSize(sl, &n);
            if (s && n == 1 && (s[0] == '/' || s[0] == '\\')) {
                Id res = cat_from_py(PyTuple_GET_ITEM(p, 0));
                Id arg = cat_from_py(PyTuple_GET_ITEM(p, 2));
                return T().cats.make(res, s[0] == '/' ? FWD : BWD, arg);
            }
        }
    }
    throw nb::type_error("expected a category: str or (result, slash, argument) tuple");
}

static bool is_cat_like(nb::handle h) {
    PyObject* p = h.ptr();
    if (PyUnicode_Check(p)) return true;
    if (PyTuple_Check(p) && PyTuple_GET_SIZE(p) == 3) {
        PyObject* sl = PyTuple_GET_ITEM(p, 1);
        if (PyUnicode_Check(sl)) {
            Py_ssize_t n; const char* s = PyUnicode_AsUTF8AndSize(sl, &n);
            return s && n == 1 && (s[0] == '/' || s[0] == '\\');
        }
    }
    return false;
}

static nb::object cat_to_py(Id c) {
    auto& cache = PC().cats;
    if ((size_t)c >= cache.size()) cache.resize(T().cats.cats.size());
    if (cache[c].is_valid()) return cache[c];
    const CatInfo& ci = T().cats[c];
    nb::object o;
    if (ci.slash == ATOM) o = nb::str(ci.name.c_str(), ci.name.size());
    else {
        nb::object r = cat_to_py(ci.res), a = cat_to_py(ci.arg);
        o = nb::make_tuple(r, PC().slashes[ci.slash], a);
    }
    PC().cats[c] = o;
    return o;
}

static nb::object stack_to_py(Id s) {
    auto& cache = PC().stacks;
    if ((size_t)s >= cache.size()) cache.resize(T().stacks.size());
    if (cache[s].is_valid()) return cache[s];
    const auto& v = T().stacks.get(s);
    nb::list items;
    for (Id c : v) items.append(cat_to_py(c));
    nb::object t = nb::steal(PyList_AsTuple(items.ptr()));
    nb::object o = PC().stack_cls.is_valid() ? PC().stack_cls(t) : t;
    PC().stacks[s] = o;
    return o;
}

static nb::object state_to_py(Kind k, Id s) {
    if (s == NONE || s == NOMATCH) return nb::none();
    return k == K_LEFT ? cat_to_py(s) : stack_to_py(s);
}

static Id state_from_py(Kind k, nb::handle h) {
    if (h.is_none()) return NONE;
    if (k == K_LEFT) return cat_from_py(h);
    if (is_cat_like(h)) return NOMATCH;      // a bare category never equals a stack state
    PyObject* p = h.ptr();
    if (!PyTuple_Check(p)) throw nb::type_error("expected a stack state (tuple of categories) or None");
    Py_ssize_t n = PyTuple_GET_SIZE(p);
    std::vector<Id> v; v.reserve((size_t)n);
    for (Py_ssize_t i = 0; i < n; ++i) v.push_back(cat_from_py(PyTuple_GET_ITEM(p, i)));
    return T().stacks.intern(v);
}

static nb::object seq_to_py(Id seq) {
    auto& cache = PC().seqs;
    if ((size_t)seq >= cache.size()) cache.resize(T().seqs.size());
    if (cache[seq].is_valid()) return cache[seq];
    const auto& v = T().seqs.get(seq);
    nb::list items;
    for (uint8_t r : v) items.append(PC().rules[r]);
    nb::object t = nb::steal(PyList_AsTuple(items.ptr()));
    PC().seqs[seq] = t;
    return t;
}

static nb::object rule_to_py(Kind k, Id rule) { return k == K_LEFT ? PC().rules[rule] : seq_to_py(rule); }

static uint8_t rule_from_py(nb::handle h) {
    if (!PyUnicode_Check(h.ptr())) throw nb::type_error("rule must be a str");
    Py_ssize_t n; const char* s = PyUnicode_AsUTF8AndSize(h.ptr(), &n);
    std::string r(s, (size_t)n);
    for (uint8_t i = 0; i < 7; ++i) if (r == rule_name(i)) return i;
    throw nb::value_error(("unknown rule " + r).c_str());
}

// ------------------------------------------------------------------ words, support
static Id word_from_py(nb::handle h) {
    if (!PyUnicode_Check(h.ptr())) throw nb::type_error("word must be a str");
    Py_ssize_t n; const char* s = PyUnicode_AsUTF8AndSize(h.ptr(), &n);
    if (!s) throw nb::python_error();
    return T().words.intern(std::string(s, (size_t)n));
}

static nb::object word_to_py(Id w) {
    auto& cache = PC().words;
    if ((size_t)w >= cache.size()) cache.resize(T().words.words.size());
    if (cache[w].is_valid()) return cache[w];
    const std::string& s = T().words.get(w);
    cache[w] = nb::str(s.c_str(), s.size());
    return cache[w];
}

struct SentIn { std::vector<Id> words; Cands cands; };

static SentIn sentence_input(nb::handle words, nb::handle support) {
    if (!PyDict_Check(support.ptr())) throw nb::type_error("support must be a dict {word: [categories]}");
    SentIn s;
    for_each(words, [&](nb::handle w) {
        s.words.push_back(word_from_py(w));
        PyObject* v = PyDict_GetItemWithError(support.ptr(), w.ptr());
        if (!v && PyErr_Occurred()) throw nb::python_error();
        std::vector<Id> cs;
        if (v) for_each(v, [&](nb::handle c) { cs.push_back(cat_from_py(c)); });
        s.cands.push_back(std::move(cs));
    });
    return s;
}

static SysParams sys_params(int kind, int max_depth, int max_stack, bool cascade) {
    SysParams p;
    p.kind = kind == 0 ? K_LEFT : K_STACK;
    p.max_depth = max_depth; p.max_stack = max_stack; p.cascade = cascade;
    return p;
}

// nested dict builder: outer key (integer) -> inner dict
struct Nested {
    nb::dict root;
    std::unordered_map<uint64_t, nb::dict, U64Hash> inner;
    nb::dict& get(uint64_t key, nb::object pykey) {
        auto it = inner.find(key);
        if (it != inner.end()) return it->second;
        nb::dict d;
        dset(root, pykey, d);
        return inner.emplace(key, d).first->second;
    }
};

// ------------------------------------------------------------------ lattices
struct PyLattice { Lattice L; nb::object words_py; };

struct PyScorer { Scorer sc; nb::object tt_ref; };

static PyLattice build_lattice_py(nb::handle words, nb::handle support, int max_depth, nb::handle goal, int kind, int max_stack, bool cascade) {
    SysParams p = sys_params(kind, max_depth, max_stack, cascade);
    SentIn s = sentence_input(words, support);
    PyLattice pl;
    pl.L = build_lattice(p, s.words, s.cands, cat_from_py(goal));
    pl.words_py = nb::steal(PySequence_List(words.ptr()));
    if (!pl.words_py.is_valid()) throw nb::python_error();
    return pl;
}

static nb::object edge_to_py(const Lattice& L, const LEdge& e, Id nxt) {
    Kind k = L.sys.kind;
    return nb::make_tuple(state_to_py(k, e.prev), cat_to_py(e.cat), state_to_py(k, nxt), rule_to_py(k, e.rule), e.w);
}

static nb::object forward_backward_full_py(const PyLattice& pl, const PyScorer& ps, nb::handle goal) {
    const Lattice& L = pl.L;
    Id g = state_from_py(L.sys.kind, goal);
    nb::dict counts;
    nb::list edges;
    Acc<uint64_t, U64Hash> cnt;
    std::vector<std::tuple<int, const LEdge*, Id, double>> ev;
    double Zv = forward_backward(L, ps.sc, g, [&](int k, const LEdge& e, int si, double post) {
        cnt.add(pack2(k, e.cat), post);
        ev.emplace_back(k, &e, L.layers[k].states[si], post);
    });
    if (Zv <= 0.0) return nb::make_tuple(0.0, counts, edges);
    for (auto& [key, v] : cnt.items) dset(counts, nb::make_tuple((int)(key >> 32), cat_to_py((Id)(uint32_t)key)), nb::float_(v));
    for (auto& [k, e, nxt, post] : ev) edges.append(nb::make_tuple(k, edge_to_py(L, *e, nxt), post));
    return nb::make_tuple(Zv, counts, edges);
}

static nb::object viterbi_py(const PyLattice& pl, const PyScorer& ps, nb::handle goal) {
    const Lattice& L = pl.L;
    ViterbiPath vp = viterbi(L, ps.sc, state_from_py(L.sys.kind, goal));
    if (!vp.ok) return nb::make_tuple(nb::none(), 0.0);
    nb::list path;
    Kind k = L.sys.kind;
    for (int i = 0; i < L.n(); ++i) {
        const LEdge& e = *vp.edges[i];
        path.append(nb::make_tuple(state_to_py(k, e.prev), cat_to_py(e.cat), state_to_py(k, vp.states[i]), rule_to_py(k, e.rule)));
    }
    return nb::make_tuple(path, vp.prob);
}

static nb::dict e_step_py(nb::handle lats, const PyScorer& ps, nb::handle plain, nb::handle goal, bool hard) {
    Acc<uint64_t, U64Hash> n_sc, n_cw;          // (prev, cat), (cat, word)
    Acc<Key128, Key128Hash> ctx_key;            // (word, cat), prev
    double n_stop = 0, n_cont = 0, ll = 0;
    int parsed = 0;
    Kind kind = K_LEFT;
    bool kind_set = false;
    Id g = NONE;
    const PyScorer* pplain = plain.is_none() ? nullptr : &nb::cast<const PyScorer&>(plain);
    for_each(lats, [&](nb::handle item) {
        const PyLattice& pl = nb::cast<const PyLattice&>(item);
        const Lattice& L = pl.L;
        if (!kind_set) { kind = L.sys.kind; g = state_from_py(kind, goal); kind_set = true; }
        if (!L.accepted) return;
        auto acc = [&](int k, const LEdge& e, double post) {
            Id word = L.words[k];
            n_sc.add(pack2(e.prev, e.cat), post);
            n_cw.add(pack2(e.cat, word), post);
            ctx_key.add(Key128{pack2(word, e.cat), uint64_t(uint32_t(e.prev))}, post);
            if (e.prev == g) n_cont += post;
        };
        double Zv;
        if (hard) {
            ViterbiPath vp = viterbi(L, ps.sc, g);
            if (!vp.ok) return;
            Zv = Z(L, ps.sc, g);
            if (Zv <= 0.0) return;
            for (int k = 0; k < L.n(); ++k) acc(k, *vp.edges[k], 1.0);
        } else if (pplain) {
            Zv = Z(L, pplain->sc, g);            // log-likelihood under the untempered model
            if (Zv <= 0.0) return;
            double Zt = forward_backward(L, ps.sc, g, [&](int k, const LEdge& e, int, double post) { acc(k, e, post); });
            if (Zt <= 0.0) return;
        } else {
            Zv = forward_backward(L, ps.sc, g, [&](int k, const LEdge& e, int, double post) { acc(k, e, post); });
            if (Zv <= 0.0) return;
        }
        ++parsed;
        ll += std::log(Zv);
        n_stop += 1.0;
    });
    Nested d_n_sc, d_ctx_cat, d_n_cw, d_theta, d_ctx_key;
    for (auto& [key, v] : n_sc.items) {
        Id prev = (Id)(uint32_t)(key >> 32), cat = (Id)(uint32_t)key;
        nb::object pp = state_to_py(kind, prev), pc = cat_to_py(cat), pv = nb::float_(v);
        dset(d_n_sc.get(uint64_t(uint32_t(prev)), pp), pc, pv);
        dset(d_ctx_cat.get(uint64_t(uint32_t(cat)), pc), pp, pv);
    }
    for (auto& [key, v] : n_cw.items) {
        Id cat = (Id)(uint32_t)(key >> 32), word = (Id)(uint32_t)key;
        nb::object pc = cat_to_py(cat), pw = word_to_py(word), pv = nb::float_(v);
        dset(d_n_cw.get(uint64_t(uint32_t(cat)), pc), pw, pv);
        dset(d_theta.get(uint64_t(uint32_t(word)), pw), pc, pv);
    }
    for (auto& [key, v] : ctx_key.items) {
        Id word = (Id)(uint32_t)(key.a >> 32), cat = (Id)(uint32_t)key.a, prev = (Id)(uint32_t)key.b;
        nb::dict& inner = d_ctx_key.get(key.a, nb::make_tuple(word_to_py(word), cat_to_py(cat)));
        dset(inner, state_to_py(kind, prev), nb::float_(v));
    }
    nb::dict out;
    out["n_sc"] = d_n_sc.root; out["n_cw"] = d_n_cw.root; out["theta_counts"] = d_theta.root;
    out["n_stop"] = n_stop; out["n_cont"] = n_cont; out["ll"] = ll; out["parsed"] = parsed;
    out["ctx_cat"] = d_ctx_cat.root; out["ctx_key"] = d_ctx_key.root;
    return out;
}

// ------------------------------------------------------------------ search helpers (mdl.py)
static nb::list successors_py(nb::handle state, nb::handle c, int kind, int max_depth, int max_stack, bool cascade) {
    SysParams p = sys_params(kind, max_depth, max_stack, cascade);
    StepOut out;
    successors(p, state_from_py(p.kind, state), cat_from_py(c), out);
    nb::list res;
    for (auto& [st, _] : out) res.append(state_to_py(p.kind, st));
    return res;
}

static nb::set states_to_pyset(Kind k, const std::unordered_set<Id>& states) {
    nb::set s;
    for (Id st : states) s.add(state_to_py(k, st));
    return s;
}

static nb::set forward_states_py(nb::handle words, int upto, nb::handle support, int kind, int max_depth, int max_stack, bool cascade) {
    SysParams p = sys_params(kind, max_depth, max_stack, cascade);
    SentIn s = sentence_input(words, support);
    return states_to_pyset(p.kind, forward_states(p, s.cands, upto));
}

static std::unordered_set<Id> states_from_py(Kind k, nb::handle states) {
    std::unordered_set<Id> out;
    for_each(states, [&](nb::handle h) { out.insert(state_from_py(k, h)); });
    return out;
}

static bool suffix_completes_py(nb::handle words, nb::handle states, int k, nb::handle support, nb::handle goal, int kind, int max_depth, int max_stack, bool cascade) {
    SysParams p = sys_params(kind, max_depth, max_stack, cascade);
    SentIn s = sentence_input(words, support);
    return suffix_completes(p, s.cands, states_from_py(p.kind, states), k, goal_state_of(p, cat_from_py(goal)));
}

// starts = successors of every state in F on c; suffix from position k must reach the goal
static bool oracle_check_py(nb::handle words, nb::handle F, nb::handle c, int k, nb::handle support, nb::handle goal, int kind, int max_depth, int max_stack, bool cascade) {
    SysParams p = sys_params(kind, max_depth, max_stack, cascade);
    Id cid = cat_from_py(c);
    std::unordered_set<Id> starts;
    StepOut succ;
    for_each(F, [&](nb::handle h) {
        successors(p, state_from_py(p.kind, h), cid, succ);
        for (auto& [st, _] : succ) starts.insert(st);
    });
    if (starts.empty()) return false;
    SentIn s = sentence_input(words, support);
    return suffix_completes(p, s.cands, std::move(starts), k, goal_state_of(p, cat_from_py(goal)));
}

// Batched oracle: the candidates (indices into `cands`) whose successors from F complete the suffix
// from position k.  first_only stops at the first hit.  Equivalent to oracle_check per candidate.
static nb::list oracle_filter_py(nb::handle words, nb::handle F, nb::handle cands, int k, nb::handle support, nb::handle goal,
                                 int kind, int max_depth, int max_stack, bool cascade, bool first_only) {
    SysParams p = sys_params(kind, max_depth, max_stack, cascade);
    SentIn s = sentence_input(words, support);
    std::vector<Id> states;
    for_each(F, [&](nb::handle h) { states.push_back(state_from_py(p.kind, h)); });
    std::vector<Id> cs;
    for_each(cands, [&](nb::handle h) { cs.push_back(cat_from_py(h)); });
    SuffixOracle oracle(p, s.cands, goal_state_of(p, cat_from_py(goal)));
    nb::list out;
    StepOut succ;
    std::vector<Id> starts;
    std::unordered_set<Id> seen;
    for (size_t i = 0; i < cs.size(); ++i) {
        starts.clear(); seen.clear();
        for (Id st : states) {
            successors(p, st, cs[i], succ);
            for (auto& [r, _] : succ) if (seen.insert(r).second) starts.push_back(r);
        }
        if (starts.empty() || !oracle.any_completes(starts, k)) continue;
        out.append((int)i);
        if (first_only) break;
    }
    return out;
}

// ------------------------------------------------------------------ CKY
struct PyChart { Chart ch; nb::object words_py; };

static nb::object node_to_py(const CNode& nd) { return nb::make_tuple(cat_to_py(nd.cat), PC().tags[nd.tag]); }

static nb::object build_tree(const Chart& ch, const BestTable& best, int i, int j, int nd) {
    int n = ch.n;
    const Cell& cell = ch.cell(i, j);
    const CEdge& e = cell.edges[nd][best.e[i * (n + 1) + j][nd]];
    Id c = cell.nodes[nd].cat;
    if (e.lex) return nb::make_tuple(cat_to_py(c), i, word_to_py(e.word));
    return nb::make_tuple(cat_to_py(c), i, j, PC().rules[e.rule], build_tree(ch, best, i, e.k, e.l), build_tree(ch, best, e.k, j, e.r));
}

static nb::object viterbi_tree_py(const PyChart& pc, const CKYScorer& sc) {
    BestTable best; int root; double prob;
    if (!viterbi_chart(pc.ch, sc, best, root, prob)) return nb::make_tuple(0.0, nb::none());
    return nb::make_tuple(prob, build_tree(pc.ch, best, 0, pc.ch.n, root));
}

static nb::object exp_to_py(uint8_t rule, Id l, Id r) { return nb::make_tuple(PC().rules[rule], cat_to_py(l), cat_to_py(r)); }

static nb::object inside_outside_py(const PyChart& pc, const CKYScorer& sc) {
    nb::list ep, lp;
    double Zv = inside_outside(pc.ch, sc,
        [&](Id parent, uint8_t rule, Id l, Id r, double post) { ep.append(nb::make_tuple(cat_to_py(parent), exp_to_py(rule, l, r), post)); },
        [&](int i, Id c, double post) { lp.append(nb::make_tuple(i, cat_to_py(c), post)); });
    if (Zv <= 0.0) return nb::make_tuple(0.0, nb::list(), nb::list());
    return nb::make_tuple(Zv, ep, lp);
}

static nb::dict cky_e_step_py(nb::handle charts, const CKYScorer& sc) {
    Acc<Key128, Key128Hash> n_pe;        // (parent, rule), (l, r)
    Acc<Key128, Key128Hash> ctx_cat;     // (cat, parent), side
    Acc<uint64_t, U64Hash> n_cw;         // (cat, word)
    Acc<Key128, Key128Hash> ctx_key;     // (word, cat), k
    Acc<uint64_t, U64Hash> n_lex;        // cat
    double ll = 0; int parsed = 0;
    for_each(charts, [&](nb::handle item) {
        const PyChart& pc = nb::cast<const PyChart&>(item);
        const Chart& ch = pc.ch;
        double Zv = inside_outside(ch, sc,
            [&](Id parent, uint8_t rule, Id l, Id r, double post) {
                n_pe.add(Key128{pack2(parent, rule), pack2(l, r)}, post);
                ctx_cat.add(Key128{pack2(l, parent), 0}, post);
                ctx_cat.add(Key128{pack2(r, parent), 1}, post);
            },
            [&](int i, Id c, double post) {
                Id w = ch.words[i];
                n_lex.add(uint64_t(uint32_t(c)), post);
                n_cw.add(pack2(c, w), post);
                ctx_key.add(Key128{pack2(w, c), uint64_t(i)}, post);
            });
        if (Zv <= 0.0) return;
        ++parsed; ll += std::log(Zv);
    });
    Nested d_pe, d_ctx_cat, d_n_cw, d_theta, d_ctx_key;
    nb::dict d_n_lex;
    for (auto& [key, v] : n_pe.items) {
        Id parent = (Id)(uint32_t)(key.a >> 32); uint8_t rule = (uint8_t)(uint32_t)key.a;
        Id l = (Id)(uint32_t)(key.b >> 32), r = (Id)(uint32_t)key.b;
        dset(d_pe.get(uint64_t(uint32_t(parent)), cat_to_py(parent)), exp_to_py(rule, l, r), nb::float_(v));
    }
    for (auto& [key, v] : ctx_cat.items) {
        Id cat = (Id)(uint32_t)(key.a >> 32), parent = (Id)(uint32_t)key.a;
        dset(d_ctx_cat.get(uint64_t(uint32_t(cat)), cat_to_py(cat)), nb::make_tuple(cat_to_py(parent), PC().sides[key.b]), nb::float_(v));
    }
    for (auto& [key, v] : n_lex.items) dset(d_n_lex, cat_to_py((Id)(uint32_t)key), nb::float_(v));
    for (auto& [key, v] : n_cw.items) {
        Id cat = (Id)(uint32_t)(key >> 32), word = (Id)(uint32_t)key;
        nb::object pc = cat_to_py(cat), pw = word_to_py(word), pv = nb::float_(v);
        dset(d_n_cw.get(uint64_t(uint32_t(cat)), pc), pw, pv);
        dset(d_theta.get(uint64_t(uint32_t(word)), pw), pc, pv);
    }
    for (auto& [key, v] : ctx_key.items) {
        Id word = (Id)(uint32_t)(key.a >> 32), cat = (Id)(uint32_t)key.a;
        dset(d_ctx_key.get(key.a, nb::make_tuple(word_to_py(word), cat_to_py(cat))), nb::int_((int)key.b), nb::float_(v));
    }
    nb::dict out;
    out["n_pe"] = d_pe.root; out["n_lex"] = d_n_lex; out["n_cw"] = d_n_cw.root; out["theta_counts"] = d_theta.root;
    out["ll"] = ll; out["parsed"] = parsed; out["ctx_cat"] = d_ctx_cat.root; out["ctx_key"] = d_ctx_key.root;
    return out;
}

// ------------------------------------------------------------------ module
NB_MODULE(_ccg_native, m) {
    m.doc() = "C++ port of the CCG induction parsers (left-branching lattice, stack lattice, CKY chart)";
    PyCache& pc = PC();
    for (int i = 0; i < 7; ++i) pc.rules[i] = nb::str(rule_name(i));
    for (int i = 0; i < 3; ++i) pc.tags[i] = nb::str(tag_name(i));
    pc.slashes[FWD] = nb::str("/"); pc.slashes[BWD] = nb::str("\\"); pc.slashes[ATOM] = nb::none();
    pc.sides[0] = nb::str("L"); pc.sides[1] = nb::str("R");

    m.attr("LEFT") = 0;
    m.attr("STACK") = 1;
    m.def("set_stack_class", [](nb::object cls) { PC().stack_cls = cls; PC().stacks.clear(); });
    m.def("set_rules", [](bool sa) { T().sa_enabled = sa; }, "sa"_a);
    m.def("sa_enabled", []() { return T().sa_enabled; });
    m.def("show", [](nb::handle c) { return T().cats.show(cat_from_py(c)); });
    m.def("intern_sizes", []() { return nb::make_tuple(T().cats.cats.size(), T().stacks.size(), T().words.words.size()); });

    m.def("combine", [](nb::handle sigma, nb::handle c, int max_depth) {
        const Res& r = combine(sigma.is_none() ? NONE : cat_from_py(sigma), cat_from_py(c), max_depth, T().sa_enabled);
        nb::list out;
        for (int i = 0; i < r.n; ++i) out.append(nb::make_tuple(cat_to_py(r.cat[i]), PC().rules[r.rule[i]]));
        return out;
    }, "sigma"_a.none(), "c"_a, "max_depth"_a = 4);
    m.def("step", [](nb::handle stack, nb::handle c, int max_depth, int max_stack, bool cascade) {
        Id st = state_from_py(K_STACK, stack);
        if (st != NONE && T().stacks.get(st).empty()) st = NONE;
        const StepOut& s = step(st, cat_from_py(c), max_depth, max_stack, cascade, T().sa_enabled);
        nb::list out;
        for (auto& [ns, seq] : s) out.append(nb::make_tuple(stack_to_py(ns), seq_to_py(seq)));
        return out;
    }, "stack"_a.none(), "c"_a, "max_depth"_a = 4, "max_stack"_a = 3, "cascade"_a = true);
    m.def("combine_pair", [](nb::handle left, nb::handle right, bool right_lexical, int max_depth, const std::string& ltag, const std::string& rtag, bool nf) {
        uint8_t lt = ltag == "FC" ? T_FC : ltag == "BC" ? T_BC : T_O;
        uint8_t rt = rtag == "FC" ? T_FC : rtag == "BC" ? T_BC : T_O;
        const Res& r = combine_pair(cat_from_py(left), cat_from_py(right), right_lexical, max_depth, lt, rt, nf);
        nb::list out;
        for (int i = 0; i < r.n; ++i) out.append(nb::make_tuple(cat_to_py(r.cat[i]), PC().rules[r.rule[i]]));
        return out;
    }, "left"_a, "right"_a, "right_lexical"_a, "max_depth"_a, "ltag"_a = "O", "rtag"_a = "O", "nf"_a = false);

    // ---- models
    nb::class_<TransTable>(m, "TransTable")
        .def("__init__", [](TransTable* t, nb::dict trans, nb::dict lam, int kind) {
            new (t) TransTable();
            Kind k = kind == 0 ? K_LEFT : K_STACK;
            for (auto [s, d] : trans) {
                Id st = state_from_py(k, s);
                for (auto [c, p] : nb::borrow<nb::dict>(d)) t->trans[pack2(st, cat_from_py(c))] = nb::cast<double>(p);
            }
            for (auto [s, v] : lam) t->lam[state_from_py(k, s)] = nb::cast<double>(v);
        }, "trans"_a, "lam"_a, "kind"_a)
        .def("__len__", [](const TransTable& t) { return t.trans.size(); });

    nb::class_<PyScorer>(m, "Scorer")
        .def("__init__", [](PyScorer* s, int kind) { new (s) PyScorer(); s->sc.kind = kind == 0 ? K_LEFT : K_STACK; }, "kind"_a)
        .def("set_generative", [](PyScorer& s, nb::dict emit, nb::dict bo, nb::object tt, double stop_p, nb::handle goal) {
            s.sc.conditional = false;
            s.sc.emit.clear(); s.sc.bo.clear();
            for (auto [c, d] : emit) {
                Id cid = cat_from_py(c);
                for (auto [w, p] : nb::borrow<nb::dict>(d)) s.sc.emit[pack2(cid, word_from_py(w))] = nb::cast<double>(p);
            }
            for (auto [c, p] : bo) s.sc.bo[cat_from_py(c)] = nb::cast<double>(p);
            TransTable& t = nb::cast<TransTable&>(tt);
            s.tt_ref = tt;
            s.sc.tt = std::shared_ptr<TransTable>(&t, [](TransTable*) {});
            s.sc.stop_p = stop_p;
            s.sc.has_goal = s.sc.kind == K_LEFT && !goal.is_none();
            s.sc.model_goal = s.sc.has_goal ? cat_from_py(goal) : NONE;
        }, "emit"_a, "bo"_a, "trans"_a, "stop_p"_a, "goal"_a.none())
        .def("set_conditional", [](PyScorer& s, nb::dict theta) {
            s.sc.conditional = true;
            s.sc.theta.clear();
            for (auto [w, d] : theta) {
                Id wid = word_from_py(w);
                for (auto [c, p] : nb::borrow<nb::dict>(d)) s.sc.theta[pack2(wid, cat_from_py(c))] = nb::cast<double>(p);
            }
        }, "theta"_a)
        .def("set_alias", [](PyScorer& s, nb::dict key_of) {
            s.sc.alias.clear();
            for (auto [w, k] : key_of) s.sc.alias[word_from_py(w)] = word_from_py(k);
        }, "key_of"_a)
        .def_prop_rw("beta", [](const PyScorer& s) { return s.sc.beta; }, [](PyScorer& s, double b) { s.sc.beta = b; })
        .def("w", [](const PyScorer& s, nb::handle prev, nb::handle c, nb::handle word) {
            return s.sc.w(state_from_py(s.sc.kind, prev), cat_from_py(c), word_from_py(word));
        }, "prev"_a.none(), "c"_a, "word"_a)
        .def("final_weight", [](const PyScorer& s) { return s.sc.final_weight(); });

    nb::class_<CKYScorer>(m, "CKYScorer")
        .def("__init__", [](CKYScorer* s, nb::dict pe, nb::dict lam, nb::dict plex, nb::dict emit) {
            new (s) CKYScorer();
            for (auto [par, d] : pe) {
                Id p = cat_from_py(par);
                for (auto [exp, v] : nb::borrow<nb::dict>(d)) {
                    nb::tuple e = nb::borrow<nb::tuple>(exp);
                    s->pe[Key128{pack2(p, rule_from_py(e[0])), pack2(cat_from_py(e[1]), cat_from_py(e[2]))}] = nb::cast<double>(v);
                }
            }
            for (auto [c, v] : lam) s->lam[cat_from_py(c)] = nb::cast<double>(v);
            for (auto [c, v] : plex) s->plex[cat_from_py(c)] = nb::cast<double>(v);
            for (auto [c, d] : emit) {
                Id cid = cat_from_py(c);
                for (auto [w, p] : nb::borrow<nb::dict>(d)) s->emit[pack2(cid, word_from_py(w))] = nb::cast<double>(p);
            }
        }, "pe"_a, "lam"_a, "plex"_a, "emit"_a)
        .def("exp_p", [](const CKYScorer& s, nb::handle parent, nb::handle exp) {
            nb::tuple e = nb::borrow<nb::tuple>(exp);
            return s.exp_p(cat_from_py(parent), rule_from_py(e[0]), cat_from_py(e[1]), cat_from_py(e[2]));
        })
        .def("lex_p", [](const CKYScorer& s, nb::handle parent, nb::handle word) { return s.lex_p(cat_from_py(parent), word_from_py(word)); });

    // ---- lattices
    nb::class_<PyLattice>(m, "Lattice")
        .def_prop_ro("words", [](const PyLattice& l) { return l.words_py; })
        .def_prop_ro("n", [](const PyLattice& l) { return l.L.n(); })
        .def_prop_ro("accepted", [](const PyLattice& l) { return l.L.accepted; })
        .def_prop_ro("fail_pos", [](const PyLattice& l) { return l.L.fail_pos; })
        .def_prop_ro("kind", [](const PyLattice& l) { return (int)l.L.sys.kind; })
        .def_prop_ro("max_depth", [](const PyLattice& l) { return l.L.sys.max_depth; })
        .def_prop_ro("max_stack", [](const PyLattice& l) { return l.L.sys.max_stack; })
        .def_prop_ro("goal_state", [](const PyLattice& l) { return state_to_py(l.L.sys.kind, l.L.goal_state); })
        .def_prop_ro("fail_states", [](const PyLattice& l) {
            nb::list out;
            for (Id s : l.L.fail_states) out.append(state_to_py(l.L.sys.kind, s));
            return nb::steal(PyList_AsTuple(out.ptr()));
        })
        .def_prop_ro("unpruned_sizes", [](const PyLattice& l) { nb::list o; for (int x : l.L.unpruned_sizes) o.append(x); return o; })
        .def_prop_ro("branch_counts", [](const PyLattice& l) { nb::list o; for (int x : l.L.branch_counts) o.append(x); return o; })
        .def("n_edges", [](const PyLattice& l) { return l.L.n_edges(); })
        .def("live_sizes", [](const PyLattice& l) { nb::list o; for (auto& la : l.L.layers) if (la.size()) o.append(la.size()); return o; })
        .def("layers_py", [](const PyLattice& l) {
            // debugging / tests: list over positions of {next_state: [(prev, cat, nxt, rule, w), ...]}
            nb::list out;
            Kind k = l.L.sys.kind;
            for (auto& la : l.L.layers) {
                nb::dict d;
                for (size_t i = 0; i < la.size(); ++i) {
                    nb::list es;
                    for (auto& e : la.edges[i]) es.append(edge_to_py(l.L, e, la.states[i]));
                    dset(d, state_to_py(k, la.states[i]), es);
                }
                out.append(d);
            }
            return out;
        });

    m.def("build_lattice", &build_lattice_py, "words"_a, "support"_a, "max_depth"_a, "goal"_a, "kind"_a, "max_stack"_a, "cascade"_a);
    m.def("Z", [](const PyLattice& l, const PyScorer& s, nb::handle goal) { return Z(l.L, s.sc, state_from_py(l.L.sys.kind, goal)); }, "lat"_a, "scorer"_a, "goal"_a);
    m.def("forward_backward", &forward_backward_full_py, "lat"_a, "scorer"_a, "goal"_a);
    m.def("viterbi", &viterbi_py, "lat"_a, "scorer"_a, "goal"_a);
    m.def("e_step", &e_step_py, "lats"_a, "scorer"_a, "plain"_a.none(), "goal"_a, "hard"_a);
    m.def("successors", &successors_py, "state"_a.none(), "c"_a, "kind"_a, "max_depth"_a, "max_stack"_a, "cascade"_a);
    m.def("forward_states", &forward_states_py, "words"_a, "upto"_a, "support"_a, "kind"_a, "max_depth"_a, "max_stack"_a, "cascade"_a);
    m.def("suffix_completes", &suffix_completes_py, "words"_a, "states"_a, "k"_a, "support"_a, "goal"_a, "kind"_a, "max_depth"_a, "max_stack"_a, "cascade"_a);
    m.def("oracle_check", &oracle_check_py, "words"_a, "F"_a, "c"_a, "k"_a, "support"_a, "goal"_a, "kind"_a, "max_depth"_a, "max_stack"_a, "cascade"_a);
    m.def("oracle_filter", &oracle_filter_py, "words"_a, "F"_a, "cands"_a, "k"_a, "support"_a, "goal"_a, "kind"_a, "max_depth"_a, "max_stack"_a, "cascade"_a, "first_only"_a = false);

    // ---- CKY
    nb::class_<PyChart>(m, "Chart")
        .def("__init__", [](PyChart* pc, nb::handle words, nb::handle support, int max_depth, nb::handle goal, bool nf) {
            new (pc) PyChart();
            SentIn s = sentence_input(words, support);
            pc->ch = build_chart(s.words, s.cands, max_depth, cat_from_py(goal), nf);
            pc->words_py = nb::steal(PySequence_List(words.ptr()));
            if (!pc->words_py.is_valid()) throw nb::python_error();
        }, "words"_a, "support"_a, "max_depth"_a = 4, "goal"_a = "S", "nf"_a = false)
        .def_prop_ro("words", [](const PyChart& c) { return c.words_py; })
        .def_prop_ro("n", [](const PyChart& c) { return c.ch.n; })
        .def_prop_ro("nf", [](const PyChart& c) { return c.ch.nf; })
        .def_prop_ro("goal", [](const PyChart& c) { return cat_to_py(c.ch.goal); })
        .def_prop_ro("accepted", [](const PyChart& c) { return c.ch.accepted; })
        .def_prop_ro("n_cells", [](const PyChart& c) { return c.ch.n_cells(); })
        .def_prop_ro("roots", [](const PyChart& c) { nb::list o; for (int r : c.ch.roots) o.append(node_to_py(c.ch.cell(0, c.ch.n).nodes[r])); return o; })
        .def("n_edges", [](const PyChart& c) { return c.ch.n_edges(); })
        .def("cell_sizes", [](const PyChart& c) {
            nb::list o;
            for (int i = 0; i < c.ch.n; ++i) for (int j = i + 1; j <= c.ch.n; ++j) o.append(c.ch.cell(i, j).size());
            return o;
        })
        .def("cats_ending_at", [](const PyChart& c, int k) {
            std::unordered_set<Id> seen; nb::list o;
            for (int a = 0; a < k; ++a) for (auto& nd : c.ch.cell(a, k).nodes) if (seen.insert(nd.cat).second) o.append(cat_to_py(nd.cat));
            return o;
        }, "k"_a)
        .def("cats_starting_at", [](const PyChart& c, int k) {
            std::unordered_set<Id> seen; nb::list o;
            for (int b = k + 1; b <= c.ch.n; ++b) for (auto& nd : c.ch.cell(k, b).nodes) if (seen.insert(nd.cat).second) o.append(cat_to_py(nd.cat));
            return o;
        }, "k"_a)
        .def("cells_py", [](const PyChart& c) {
            // debugging / tests: {(i, j): {(cat, tag): [('LEX', word) | ('BIN', k, lnode, rnode, rule, w)]}}
            nb::dict out;
            const Chart& ch = c.ch;
            for (int i = 0; i < ch.n; ++i) for (int j = i + 1; j <= ch.n; ++j) {
                nb::dict d;
                const Cell& cell = ch.cell(i, j);
                for (size_t nd = 0; nd < cell.size(); ++nd) {
                    nb::list es;
                    for (auto& e : cell.edges[nd]) {
                        if (e.lex) es.append(nb::make_tuple("LEX", word_to_py(e.word)));
                        else es.append(nb::make_tuple("BIN", e.k, node_to_py(ch.cell(i, e.k).nodes[e.l]), node_to_py(ch.cell(e.k, j).nodes[e.r]), PC().rules[e.rule], e.w));
                    }
                    dset(d, node_to_py(cell.nodes[nd]), es);
                }
                dset(out, nb::make_tuple(i, j), d);
            }
            return out;
        });
    m.def("cky_Z", [](const PyChart& c, const CKYScorer& s) { return cky_Z(c.ch, s); }, "chart"_a, "scorer"_a);
    m.def("inside_outside", &inside_outside_py, "chart"_a, "scorer"_a);
    m.def("viterbi_tree", &viterbi_tree_py, "chart"_a, "scorer"_a);
    m.def("count_derivations", [](const PyChart& c) { return count_derivations(c.ch); }, "chart"_a);
    m.def("cky_e_step", &cky_e_step_py, "charts"_a, "scorer"_a);
}
