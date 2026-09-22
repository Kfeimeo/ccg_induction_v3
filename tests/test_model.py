"""Model / EM / MDL sanity tests on the synthetic grammar."""
import collections, math
from ccg.synthetic import generate, gold_lexicon
from ccg.model import Lexicon, Model
from ccg.lattice import build_lattice, forward_backward
from ccg.em import em, data_bits
from ccg import category as C


def _setup(kind):
    sents = generate(120, 0)
    gl = gold_lexicon()
    lex = Lexicon({w: set(cs) for w, cs in gl.items()}, math.log2(20))
    counts = collections.Counter(w for s in sents for w in s)
    m = Model(lex, kind, dict(counts))
    m.init_uniform()
    lats = [build_lattice(s, lex.support_lists(), 4) for s in sents]
    return sents, m, lats


def test_generative_probabilities_are_bounded():
    sents, m, lats = _setup('generative')
    for lat in lats:
        Z, _, _ = forward_backward(lat, m)
        assert 0 < Z <= 1.0


def test_em_increases_likelihood():
    sents, m, lats = _setup('generative')
    hist, _ = em(lats, m, 8, 1e-6)
    assert len(hist) >= 2
    assert all(b >= a - 1e-6 for a, b in zip(hist, hist[1:]))


def test_conditional_accept_prob_le_one():
    sents, m, lats = _setup('conditional')
    for lat in lats:
        Z, _, _ = forward_backward(lat, m)
        assert 0 < Z <= 1.0 + 1e-9


def test_posteriors_sum_to_one_per_position():
    sents, m, lats = _setup('generative')
    for lat in lats[:20]:
        Z, cnt, _ = forward_backward(lat, m)
        per_pos = collections.defaultdict(float)
        for (k, c), v in cnt.items():
            per_pos[k] += v
        for k in range(lat.n):
            assert abs(per_pos[k] - 1.0) < 1e-6


def test_remove_and_add_entry_keep_distributions_normalised():
    sents, m, lats = _setup('generative')
    m.add_entry('john', C.parse('N'), 0.3)
    for c, d in m.emit.items():
        assert abs(sum(d.values()) - 1.0) < 1e-9
    m.remove_entry('john', C.parse('N'))
    assert C.parse('N') not in m.lex.support['john']
    for c, d in m.emit.items():
        assert abs(sum(d.values()) - 1.0) < 1e-9


def test_rename_substitute():
    c = C.parse('((S\\NP)/NP)/NP')
    assert C.show(C.substitute(c, C.parse('NP'), 'N')) == '((S\\N)/N)/N'
    assert C.has_standard_slots(C.parse('((S\\NP)/NP)/NP'))
    assert not C.has_standard_slots(C.parse('(S/NP)\\NP'))
