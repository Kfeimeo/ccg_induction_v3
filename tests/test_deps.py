"""Head mapping on hand-built derivations (gold = UD conventions)."""
from ccg.category import parse as P
from ccg.combine import viterbi_rules
from ccg.deps import replay, raw_heads


def heads_for(words, cats):
    path = viterbi_rules([P(c) for c in cats])
    assert path is not None, 'no derivation'
    full = [(prev, P(c), nxt, rule) for (prev, nxt, rule), c in zip(path, cats)]
    return replay(words, full)[0], [r for _, _, r in path]


def test_transitive():
    h, rules = heads_for('john loves mary'.split(), ['NP', '(S\\NP)/NP', 'NP'])
    assert rules == ['LEX', 'SA', 'FA']
    assert h == [2, 0, 2]


def test_det_flip():
    h, _ = heads_for('the dog barks'.split(), ['NP/N', 'N', 'S\\NP'])
    assert h == [2, 3, 0]


def test_aux_chain():
    h, _ = heads_for('john has been eating'.split(), ['NP', '(S\\NP)/(S\\NP)', '(S\\NP)/(S\\NP)', 'S\\NP'])
    assert h == [4, 4, 4, 0]


def test_copula_adj_and_degree():
    h, _ = heads_for('john is very happy'.split(), ['NP', '(S\\NP)/(N/N)', '(N/N)/(N/N)', 'N/N'])
    assert h == [4, 4, 4, 0]


def test_pp_argument_case_flip():
    h, _ = heads_for('john sat in the park'.split(), ['NP', '(S\\NP)/PP', 'PP/NP', 'NP/N', 'N'])
    assert h == [2, 0, 5, 5, 2]


def test_s_postmodifier_pp():
    h, _ = heads_for('john slept in the park'.split(), ['NP', 'S\\NP', '(S\\S)/NP', 'NP/N', 'N'])
    assert h == [2, 0, 5, 5, 2]


def test_initial_interjection_takes_subject():
    h, _ = heads_for('yeah i know'.split(), ['(S/(S\\NP))/NP', 'NP', 'S\\NP'])
    assert h == [3, 3, 0]


def test_initial_pp_takes_subject():
    h, _ = heads_for('in it norton observed'.split(), ['((S/(S\\NP))/NP)/NP', 'NP', 'NP', 'S\\NP'])
    assert h == [2, 4, 4, 0]


def test_subject_relative():
    h, _ = heads_for('the man who left smiled'.split(), ['NP/N', 'N', '(NP\\NP)/(S\\NP)', 'S\\NP', 'S\\NP'])
    assert h == [2, 5, 4, 2, 0]


def test_object_relative_construction_specific():
    h, _ = heads_for('the joke that i told works'.split(), ['NP/N', 'N', '((NP\\NP)/((S\\NP)/NP))/NP', 'NP', '(S\\NP)/NP', 'S\\NP'])
    # UD: joke->works (nsubj), told->joke (acl:relcl), that->told (obj), i->told (nsubj)
    assert h == [2, 6, 5, 5, 2, 0]


def test_coordination_np():
    h, _ = heads_for('cats and dogs sleep'.split(), ['NP', '(NP\\NP)/NP', 'NP', 'S\\NP'])
    assert h == [4, 3, 1, 0]


def test_zero_complementizer_ccomp():
    h, _ = heads_for('i think it is stupid'.split(), ['NP', '((S\\NP)/(S\\NP))/NP', 'NP', '(S\\NP)/(N/N)', 'N/N'])
    # UD: think root; i->think; stupid->think (ccomp); it->stupid; is->stupid
    assert h == [2, 0, 5, 5, 2]


def test_object_control():
    h, _ = heads_for('i let it go'.split(), ['NP', '((S\\NP)/(S\\NP))/NP', 'NP', 'S\\NP'])
    assert h == [2, 0, 2, 2]


def test_subordinate_final():
    h, _ = heads_for('i cried when it rained'.split(), ['NP', 'S\\NP', '((S\\S)/(S\\NP))/NP', 'NP', 'S\\NP'])
    # UD: cried root; when->rained (mark); it->rained; rained->cried (advcl)
    assert h == [2, 0, 5, 5, 2]


def test_possessive():
    h, _ = heads_for("john 's dog barks".split(), ['NP', '(NP/N)\\NP', 'N', 'S\\NP'])
    assert h == [3, 1, 4, 0]


def test_noun_pp_complement():
    h, _ = heads_for('a lot of fun is here'.split(), ['NP/N', 'N/PP', 'PP/NP', 'NP', '(S\\NP)/PP', 'PP'])
    # UD: here root (cop analysis): lot->here (nsubj), a->lot, of->fun, fun->lot, is->here
    assert h == [2, 6, 4, 2, 6, 0]


def test_tr_subject_lexical():
    h, _ = heads_for('the dog barks'.split(), ['(S/(S\\NP))/N', 'N', 'S\\NP'])
    assert h == [2, 3, 0]


def test_raw_heads_are_functor_to_argument():
    path = viterbi_rules([P('NP/N'), P('N'), P('S\\NP')])
    full = [(prev, c, nxt, rule) for (prev, nxt, rule), c in zip(path, [P('NP/N'), P('N'), P('S\\NP')])]
    assert raw_heads('the dog barks'.split(), full) == [3, 1, 0]


def test_every_word_has_one_head():
    for words, cats in [('i do n\'t know'.split(), ['NP', '(S\\NP)/(S\\NP)', '(S\\NP)/(S\\NP)', 'S\\NP']),
                        ('so i saw them'.split(), ['(S/(S\\NP))/NP', 'NP', '(S\\NP)/NP', 'NP'])]:
        h, _ = heads_for(words, cats)
        assert h.count(0) == 1
        assert all(0 <= x <= len(words) for x in h)


def test_pre_subject_modifier_cannot_feed_arity3_verb():
    # B> needs the verb's result to be exactly S\NP: (S/(S\NP))/NP + NP -> S/(S\NP); then
    # ((S\NP)/PP)/NP has result (S\NP)/PP != S\NP and generalized composition is not a rule.
    assert viterbi_rules([P('(S/(S\\NP))/NP'), P('NP'), P('((S\\NP)/PP)/NP'), P('NP'), P('PP')]) is None
