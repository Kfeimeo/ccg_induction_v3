"""Stack (Lambek-product) incremental parser: forced reduction, cascade, push bound, dependencies."""
from ccg.category import parse as P, show
from ccg.stack_lattice import build_stack_lattice, step, Stack
from ccg.lattice import build_lattice, viterbi
from ccg.experiment import UniformModel
from ccg.deps import replay_stack
from ccg.synthetic import generate, gold_lexicon


def parse(words, cats, max_stack=3, cascade=True):
    supp = {w: [P(c)] for w, c in zip(words, cats)}
    lat = build_stack_lattice(words, supp, 4, 'S', max_stack, cascade)
    if not lat.accepted:
        return None, None
    path, p = viterbi(lat, UniformModel(supp), Stack(('S',)))
    heads, _ = replay_stack(words, path)
    return [tuple(e[3]) for e in path], heads


def test_pre_subject_adverb_with_standard_categories():
    rules, heads = parse('yeah i know'.split(), ['S/S', 'NP', 'S\\NP'])
    assert rules == [('PUSH',), ('PUSH',), ('BA', 'FA')]
    assert heads == [3, 3, 0]


def test_initial_pp_with_standard_categories():
    rules, heads = parse('in it norton observed'.split(), ['(S/S)/NP', 'NP', 'NP', 'S\\NP'])
    assert rules is not None and heads == [2, 4, 4, 0]


def test_embedded_subject_without_construction_specific_verb():
    rules, heads = parse('i think it is stupid'.split(), ['NP', '(S\\NP)/S', 'NP', '(S\\NP)/(N/N)', 'N/N'])
    assert rules is not None
    assert heads == [2, 0, 5, 5, 2]


def test_object_relative_with_standard_relativizer():
    rules, heads = parse('the man that i saw left'.split(), ['NP/N', 'N', '(NP\\NP)/(S/NP)', 'NP', '(S\\NP)/NP', 'S\\NP'])
    assert rules is not None
    assert heads == [2, 6, 5, 5, 2, 0]


def test_forced_reduction_blocks_vp_coordination():
    # "i sing and dance": i+sing must reduce to S, so the VP coordinator cannot see S\NP
    rules, _ = parse('i sing and dance'.split(), ['NP', 'S\\NP', '((S\\NP)\\(S\\NP))/(S\\NP)', 'S\\NP'])
    assert rules is None
    rules, heads = parse('i sing and dance'.split(), ['NP', 'S\\NP', '(S\\S)/(S\\NP)', 'S\\NP'])
    assert rules is not None


def test_stack_bound():
    words = 'a b c d'.split(); cats = ['NP', 'NP', 'NP', 'S']
    supp = {w: [P(c)] for w, c in zip(words, cats)}
    assert not build_stack_lattice(words, supp, 4, 'S', 3).accepted
    assert build_stack_lattice(words, supp, 4, 'S', 4).fail_pos == 5     # all pushed, no S alone at the end


def test_max_stack_one_equals_strict_left_branching():
    sents = generate(150, 3)
    gl = gold_lexicon()
    supp = {w: list(cs) for w, cs in gl.items()}
    for s in sents:
        a = build_lattice(s, supp, 4).accepted
        b = build_stack_lattice(s, supp, 4, 'S', 1).accepted
        assert a == b


def test_stack_never_loses_coverage_relative_to_left():
    sents = generate(150, 4)
    gl = gold_lexicon()
    supp = {w: list(cs) for w, cs in gl.items()}
    for s in sents:
        if build_lattice(s, supp, 4).accepted:
            assert build_stack_lattice(s, supp, 4, 'S', 3).accepted


def test_step_is_deterministic_push_or_reduce():
    succ = step(Stack((P('S/S'),)), P('NP'), 4, 3)
    assert [r for _, r in succ] == [('PUSH',)]
    succ = step(Stack((P('S/S'), P('NP'))), P('S\\NP'), 4, 3)
    assert [r for _, r in succ] == [('BA', 'FA')] and [show(st[0]) for st, _ in succ] == ['S']
