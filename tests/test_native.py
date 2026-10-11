"""The C++ extension (ccg._ccg_native) must reproduce the pure-Python reference implementations of
the three systems: left-branching lattice, stack lattice (max_stack = 2) and CKY (plain / Eisner
normal form) — lattice structure, Z, posteriors / E-step statistics, Viterbi derivations."""
import collections
import math
import pytest

from ccg import native as nat
from ccg import category as C
from ccg.category import parse as P
from ccg.synthetic import generate, gold_lexicon
from ccg.model import Lexicon, Model
from ccg.experiment import UniformModel
from ccg.em import PowerModel, e_step_py
from ccg import lattice as L
from ccg import stack_lattice as SL
from ccg import cky as K
from ccg.combine import combine, set_rules
from ccg.deps import DEFAULT_HEADMAP

pytestmark = pytest.mark.skipif(not nat.available, reason='native extension not built (scripts/build_native.ps1)')

GOLD = gold_lexicon()
SUPP = {w: list(cs) for w, cs in GOLD.items()}
SENTS = generate(250, 11)


def _noisy_support(seed):
    """Gold lexicon plus a few wrong categories per word: ambiguity, failures and SA/B rules."""
    import random
    rng = random.Random(seed)
    extra = [P(x) for x in ['NP', 'N', 'S\\NP', 'N/N', 'S\\S', '(S\\NP)/NP', 'NP/N', '(S\\S)/NP', '((S\\NP)/PP)/NP', '(S/S)/NP', 'S/S']]
    supp = {}
    for w, cs in GOLD.items():
        cands = list(cs)
        for c in rng.sample(extra, 2):
            if c not in cands:
                cands.append(c)
        supp[w] = sorted(cands, key=lambda c: (C.size(c), C.show(c)))
    return supp


def _gen_model(supp, sents, seed=0):
    lex = Lexicon({w: set(cs) for w, cs in supp.items()}, math.log2(len(supp)))
    m = Model(lex, 'generative', collections.Counter(w for s in sents for w in s))
    m.init_uniform()
    return m


def _layers_py(lat):
    out = []
    for layer in lat.states:
        out.append({st: [(e.prev, e.cat, e.nxt, e.rule, e.w) for e in edges] for st, edges in layer.items()})
    return out


def _close(a, b, rel=1e-9):
    return abs(a - b) <= rel * max(1.0, abs(a), abs(b))


# ------------------------------------------------------------------ rules
def test_combine_matches_python():
    cats = [P(x) for x in ['S', 'NP', 'N', 'S/NP', 'S\\NP', '(S\\NP)/NP', 'NP/N', 'N/N', 'S\\S', '(S\\S)/NP', '((S\\NP)/PP)/NP',
                           'S/(S\\NP)', '(S\\NP)\\(S\\NP)', '((S\\S)/(S\\NP))/NP', '(NP\\NP)/NP']]
    for sa in (True, False):
        set_rules(sa)
        for s in [None] + cats:
            for c in cats:
                assert nat._N.combine(s, c, 4) == list(combine(s, c, 4)), (s, c, sa)
    set_rules(True)


def test_step_matches_python():
    cats = [P(x) for x in ['S', 'NP', 'N', 'S/NP', 'S\\NP', '(S\\NP)/NP', 'NP/N', 'N/N', 'S\\S', '(S\\S)/NP', 'S/S', '(S/S)/NP']]
    stacks = [None] + [SL.Stack((a,)) for a in cats] + [SL.Stack((a, b)) for a in cats[:6] for b in cats[:6]]
    for st in stacks:
        for c in cats:
            for cascade in (True, False):
                got = nat._N.step(st, c, 4, 3, cascade)
                exp = SL.step(st, c, 4, 3, cascade)
                assert [(tuple(a), b) for a, b in got] == [(tuple(a), b) for a, b in exp], (st, c, cascade)
                assert all(isinstance(a, SL.Stack) for a, _ in got)


# ------------------------------------------------------------------ left-branching lattice
@pytest.mark.parametrize('seed', [0, 1])
def test_left_lattice_structure_and_probabilities(seed):
    supp = _noisy_support(seed)
    m = _gen_model(supp, SENTS, seed)
    um = UniformModel(supp)
    n_acc = 0
    for s in SENTS:
        a = L.build_lattice(s, supp, 4)
        b = L.build_lattice_py(s, supp, 4)
        assert nat.is_native_lattice(a)
        assert (a.accepted, a.fail_pos, tuple(a.unpruned_sizes), tuple(a.branch_counts)) == (b.accepted, b.fail_pos, tuple(b.unpruned_sizes), tuple(b.branch_counts))
        assert set(a.fail_states) == set(b.fail_states)
        if not a.accepted:
            continue
        n_acc += 1
        assert a.layers_py() == _layers_py(b)
        for model in (m, um, PowerModel(m, 1.7)):
            Za, cnt_a, ed_a = L.forward_backward(a, model)
            Zb, cnt_b, ed_b = L.forward_backward_py(b, model)
            assert _close(Za, Zb) and _close(L.Z(a, model), Zb)
            assert set(cnt_a) == set(cnt_b) and all(_close(cnt_a[k], cnt_b[k]) for k in cnt_b)
            assert len(ed_a) == len(ed_b)
            pa, ppa = L.viterbi(a, model)
            pb, ppb = L.viterbi_py(b, model)
            assert pa == pb and _close(ppa, ppb)
    assert n_acc > 50


def test_left_e_step_matches_python():
    supp = _noisy_support(3)
    m = _gen_model(supp, SENTS)
    lats_n = [L.build_lattice(s, supp, 4) for s in SENTS]
    lats_p = [L.build_lattice_py(s, supp, 4) for s in SENTS]
    for beta, hard in [(1.0, False), (1.5, False), (1.0, True)]:
        from ccg.em import e_step
        sa = e_step(lats_n, m, 'S', beta, hard)
        sb = e_step_py(lats_p, m, 'S', beta, hard)
        assert sa['parsed'] == sb['parsed'] and _close(sa['ll'], sb['ll']) and _close(sa['n_stop'], sb['n_stop']) and _close(sa['n_cont'], sb['n_cont'])
        for key in ('n_sc', 'n_cw', 'theta_counts', 'ctx_cat', 'ctx_key'):
            assert set(sa[key]) == set(sb[key]), key
            for k, d in sb[key].items():
                assert set(sa[key][k]) == set(d), (key, k)
                assert all(_close(sa[key][k][kk], v) for kk, v in d.items()), (key, k)
    # one M-step on the native statistics keeps the likelihood non-decreasing
    m2 = m.copy()
    s0 = L.Z(lats_n[0], m2)
    from ccg.em import em
    hist, _ = em(lats_n, m2, 3, 1e-6)
    assert hist[-1] >= hist[0] - 1e-9


def test_dev_model_alias_and_scorer_cache():
    from ccg.induce import DevModel
    supp = _noisy_support(5)
    m = _gen_model(supp, SENTS)
    key_of = {w: w for w in supp}
    key_of['doggo'] = 'dog'
    supp2 = dict(supp); supp2['doggo'] = supp['dog']
    dm = DevModel(m, key_of)
    s = ['the', 'doggo', 'sleeps']
    a = L.build_lattice(s, supp2, 4); b = L.build_lattice_py(s, supp2, 4)
    assert a.accepted and _close(L.Z(a, dm), L.forward_backward_py(b, dm)[0])
    # the scorer is cached per model version and rebuilt after a parameter change
    sc1 = nat.scorer_for(m, nat.LEFT); sc2 = nat.scorer_for(m, nat.LEFT)
    assert sc1 is sc2
    m.add_entry('the', P('S/S'))
    assert nat.scorer_for(m, nat.LEFT) is not sc1
    assert _close(L.Z(a, m), L.forward_backward_py(b, m)[0])


# ------------------------------------------------------------------ stack lattice (max_stack = 2)
@pytest.mark.parametrize('max_stack', [2, 3])
def test_stack_lattice_matches_python(max_stack):
    supp = _noisy_support(7)
    m = _gen_model(supp, SENTS)
    gs = SL.goal_state('S')
    n_acc = 0
    for s in SENTS:
        a = SL.build_stack_lattice(s, supp, 4, 'S', max_stack)
        b = SL.build_stack_lattice_py(s, supp, 4, 'S', max_stack)
        assert (a.accepted, a.fail_pos, tuple(a.unpruned_sizes), tuple(a.branch_counts)) == (b.accepted, b.fail_pos, tuple(b.unpruned_sizes), tuple(b.branch_counts))
        assert set(a.fail_states) == set(b.fail_states)
        assert all(st is None or isinstance(st, SL.Stack) for st in a.fail_states)
        if not a.accepted:
            continue
        n_acc += 1
        assert a.layers_py() == _layers_py(b)
        Za, cnt_a, _ = L.forward_backward(a, m, gs)
        Zb, cnt_b, _ = L.forward_backward_py(b, m, gs)
        assert _close(Za, Zb)
        assert set(cnt_a) == set(cnt_b) and all(_close(cnt_a[k], cnt_b[k]) for k in cnt_b)
        pa, ppa = L.viterbi(a, m, gs); pb, ppb = L.viterbi_py(b, m, gs)
        assert pa == pb and _close(ppa, ppb)
        assert all(isinstance(e[2], SL.Stack) for e in pa)
    assert n_acc > 50
    # E-step with stack states as transition contexts
    lats_n = [SL.build_stack_lattice(s, supp, 4, 'S', max_stack) for s in SENTS[:80]]
    lats_p = [SL.build_stack_lattice_py(s, supp, 4, 'S', max_stack) for s in SENTS[:80]]
    from ccg.em import e_step
    sa = e_step(lats_n, m, gs); sb = e_step_py(lats_p, m, gs)
    assert sa['parsed'] == sb['parsed'] and _close(sa['ll'], sb['ll']) and _close(sa['n_cont'], sb['n_cont'])
    assert set(sa['n_sc']) == set(sb['n_sc'])
    for k, d in sb['n_sc'].items():
        assert all(_close(sa['n_sc'][k][c], v) for c, v in d.items())
    m2 = m.copy(); m2.set_counts(sa['n_sc'], sa['n_cw'], sa['n_stop'], sa['n_cont'], sa['theta_counts'])
    m3 = m.copy(); m3.set_counts(sb['n_sc'], sb['n_cw'], sb['n_stop'], sb['n_cont'], sb['theta_counts'])
    for a, b in zip(lats_n[:20], lats_p[:20]):
        assert _close(L.Z(a, m2, gs), L.forward_backward_py(b, m3, gs)[0])


# ------------------------------------------------------------------ search helpers (proposal steps)
def test_search_helpers_match_python():
    from ccg.mdl import MDLTrainer
    from ccg.stack_trainer import StackTrainer
    supp = _noisy_support(9)
    m = _gen_model(supp, SENTS)
    pool = C.filter_pool(C.enumerate_categories(['S', 'N', 'NP'], 3, 3, 4, 1))
    for cls, cfg in ((MDLTrainer, {}), (StackTrainer, {'max_stack': 2})):
        tr = cls(SENTS[:30], m.copy(), pool, dict(cfg, em_iters=1, max_outer_iters=0), 4, 'S', log=lambda *_: None)
        nat_avail = nat.available
        for s in SENTS[:40]:
            for k in range(len(s)):
                F = tr.forward_states(s, k, supp)
                nat.available = False
                F_py = tr.forward_states(s, k, supp)
                nat.available = nat_avail
                assert F == F_py, (s, k)
                for sigma in list(F)[:5]:
                    for c in supp[s[k]]:
                        got = tr.successors(sigma, c)
                        nat.available = False
                        exp = tr.successors(sigma, c)
                        nat.available = nat_avail
                        assert got == exp
                        r1 = tr.oracle_check(s, F, c, k + 1, supp)
                        nat.available = False
                        r2 = tr.oracle_check(s, F, c, k + 1, supp)
                        nat.available = nat_avail
                        assert r1 == r2
                # batched oracle (memoised suffix reachability) == per-candidate checks, same order
                cands = [c for cs in supp.values() for c in cs][:40]
                if F:
                    got = tr.oracle_filter(s, F, cands, k + 1, supp)
                    got1 = tr.oracle_filter(s, F, cands, k + 1, supp, first_only=True)
                    nat.available = False
                    exp = tr.oracle_filter(s, F, cands, k + 1, supp)
                    nat.available = nat_avail
                    assert got == exp and got1 == exp[:1], (s, k)


# ------------------------------------------------------------------ CKY
def _cky_model(supp, sents):
    lex = Lexicon({w: set(cs) for w, cs in supp.items()}, 4.3)
    m = K.CKYModel(lex, collections.Counter(w for s in sents for w in s))
    m.init_uniform()
    return m


@pytest.mark.parametrize('nf', [False, True])
def test_chart_matches_python(nf):
    supp = _noisy_support(13)
    m = _cky_model(supp, SENTS)
    n_acc = 0
    for s in SENTS[:150]:
        a = K.Chart(s, supp, 4, 'S', nf)
        b = K.ChartPy(s, supp, 4, 'S', nf)
        assert nat.is_native_chart(a)
        assert a.accepted == b.accepted and a.n_cells == b.n_cells
        assert sorted(a.cell_sizes()) == sorted(b.cell_sizes())
        assert K.count_derivations(a) == K.count_derivations_py(b)
        for k in range(len(s) + 1):
            assert set(a.cats_ending_at(k)) == set(b.cats_ending_at(k))
            assert set(a.cats_starting_at(k)) == set(b.cats_starting_at(k))
        if not a.accepted:
            continue
        n_acc += 1
        assert set(a.roots) == set(b.roots)
        cells = a.cells_py()
        for (i, j), d in b.cell.items():
            da = cells[(i, j)]
            assert set(da) == set(d)
            for nd, edges in d.items():
                assert len(da[nd]) == len(edges)
                for ea, eb in zip(da[nd], edges):
                    assert ea[0] == eb[0]
                    if ea[0] == 'BIN':
                        assert ea[1:5] == tuple(eb[1:5]) and _close(ea[5], eb[5])
        Za, ep_a, lp_a = K.inside_outside(a, m)
        Zb, ep_b, lp_b = K.inside_outside_py(b, m)
        assert _close(Za, Zb) and _close(K.cky_Z(a, m), Zb)
        assert len(ep_a) == len(ep_b) and len(lp_a) == len(lp_b)
        agg_a = collections.Counter(); agg_b = collections.Counter()
        for p, e, post in ep_a: agg_a[(p, e)] += post
        for p, e, post in ep_b: agg_b[(p, e)] += post
        assert set(agg_a) == set(agg_b) and all(_close(agg_a[k], agg_b[k]) for k in agg_b)
        pa, ta = K.viterbi_tree(a, m); pb, tb = K.viterbi_tree_py(b, m)
        assert _close(pa, pb) and ta == tb
        assert K.tree_heads(ta, s, DEFAULT_HEADMAP) == K.tree_heads(tb, s, DEFAULT_HEADMAP)
    assert n_acc > 30


def test_cky_e_step_matches_python():
    from ccg.cky_trainer import CKYTrainer
    supp = _noisy_support(17)
    m = _cky_model(supp, SENTS)
    pool = C.filter_pool(C.enumerate_categories(['S', 'N', 'NP'], 3, 3, 4, 1))
    for nf in (False, True):
        tr = CKYTrainer(SENTS[:100], m.copy(), pool, {'em_iters': 1, 'max_outer_iters': 0, 'normal_form': nf}, 4, 'S', log=lambda *_: None)
        tr.rebuild()
        sa = tr.e_step()
        tr_py = CKYTrainer(SENTS[:100], m.copy(), pool, {'em_iters': 1, 'max_outer_iters': 0, 'normal_form': nf}, 4, 'S', log=lambda *_: None)
        tr_py.lats = [K.ChartPy(s, supp, 4, 'S', nf) for s in SENTS[:100]]
        tr_py.set_active(None)
        sb = tr_py.e_step()
        assert sa['parsed'] == sb['parsed'] and _close(sa['ll'], sb['ll'])
        for key in ('n_pe', 'n_lex', 'n_cw', 'theta_counts', 'ctx_cat', 'ctx_key'):
            assert set(sa[key]) == set(sb[key]), key
            for k, d in sb[key].items():
                if isinstance(d, dict):
                    assert set(sa[key][k]) == set(d), (key, k)
                    assert all(_close(sa[key][k][kk], v) for kk, v in d.items()), (key, k)
                else:
                    assert _close(sa[key][k], d), (key, k)
