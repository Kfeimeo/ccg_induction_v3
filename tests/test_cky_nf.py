"""Eisner (1996) normal form in the CKY contrast: one derivation per reading, no loss of coverage."""
import collections
from ccg.category import parse as P
from ccg.cky import Chart, count_derivations, CKYModel, inside_outside, viterbi_tree, tree_heads
from ccg.model import Lexicon
from ccg.deps import DEFAULT_HEADMAP
from ccg.synthetic import generate, gold_lexicon


def test_composition_vs_application_ambiguity_removed():
    # a: S/N, b: N/NP, c: NP  -> FA(a, FA(b,c)) and FA(B>(a,b), c) without NF; one with NF
    supp = {'a': [P('S/N')], 'b': [P('N/NP')], 'c': [P('NP')]}
    assert count_derivations(Chart('a b c'.split(), supp)) == 2
    assert count_derivations(Chart('a b c'.split(), supp, nf=True)) == 1


def test_backward_modifier_ambiguity_removed_but_sentence_parses():
    # the man ate quickly: [[the man] ate] quickly  vs  [the man] [ate quickly] (B<)
    supp = {'the': [P('NP/N')], 'man': [P('N')], 'ate': [P('S\\NP')], 'quickly': [P('S\\S')]}
    words = 'the man ate quickly'.split()
    assert count_derivations(Chart(words, supp)) == 2
    nf = Chart(words, supp, nf=True)
    assert nf.accepted and count_derivations(nf) == 1


def test_composition_still_available_when_needed():
    # modifier between subject-raised functor and verb needs B>: S/(S\NP) + (S\NP)/(S\NP) + S\NP
    supp = {'he': [P('S/(S\\NP)')], 'always': [P('(S\\NP)/(S\\NP)')], 'runs': [P('S\\NP')]}
    assert Chart('he always runs'.split(), supp, nf=True).accepted


def test_gold_synthetic_lexicon_fully_parses_under_nf():
    sents = generate(200, 0)
    gl = gold_lexicon()
    supp = {w: list(cs) for w, cs in gl.items()}
    ok_nf = sum(1 for s in sents if Chart(s, supp, nf=True).accepted)
    ok = sum(1 for s in sents if Chart(s, supp).accepted)
    assert ok == ok_nf == len(sents)
    # NF never has more derivations than the unconstrained chart
    assert all(count_derivations(Chart(s, supp, nf=True)) <= count_derivations(Chart(s, supp)) for s in sents[:50])


def test_inside_outside_and_heads_under_nf():
    sents = generate(30, 1)
    gl = gold_lexicon()
    supp = {w: list(cs) for w, cs in gl.items()}
    lex = Lexicon({w: set(cs) for w, cs in gl.items()}, 4.3)
    m = CKYModel(lex, collections.Counter(w for s in sents for w in s)); m.init_uniform()
    for s in sents:
        ch = Chart(s, supp, nf=True)
        Z, ep, lp = inside_outside(ch, m)
        assert 0 < Z <= 1.0
        per_pos = collections.defaultdict(float)
        for k, c, post in lp:
            per_pos[k] += post
        assert all(abs(per_pos[k] - 1.0) < 1e-6 for k in range(len(s)))
        p, t = viterbi_tree(ch, m)
        heads = tree_heads(t, s, DEFAULT_HEADMAP)
        assert heads.count(0) == 1
