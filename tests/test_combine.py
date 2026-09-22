import pytest
from ccg.category import parse, show, depth, arity, size, spine, build, enumerate_categories
from ccg.combine import combine, typecheck, sa_matches, viterbi_rules

P = parse


def results(sigma, c, md=4):
    return {(show(r), rule) for r, rule in combine(sigma, c, md)}


def test_parse_show_roundtrip():
    for s in ['S', 'NP', 'S\\NP', '(S\\NP)/NP', '((S\\NP)/NP)/NP', '(S\\NP)/(S\\NP)',
              '(NP\\NP)/((S\\NP)/NP)', 'S[dcl]', '(S[dcl]\\NP)/S[b]']:
        assert show(P(s)) == s


def test_depth_arity_size():
    assert depth(P('S')) == 0
    assert depth(P('S\\NP')) == 1
    assert depth(P('(S\\NP)/NP')) == 2
    assert depth(P('(S\\NP)/(S\\NP)')) == 2
    assert depth(P('((S\\NP)/NP)/NP')) == 3
    assert arity(P('((S\\NP)/NP)/NP')) == 3
    assert arity(P('(S\\NP)/(S\\NP)')) == 2
    assert size(P('(S\\NP)/NP')) == 5
    t, slots = spine(P('((S\\NP)/NP)/PP'))
    assert t == 'S' and slots == (('\\', 'NP'), ('/', 'NP'), ('/', 'PP'))
    assert build(t, slots) == P('((S\\NP)/NP)/PP')


# --- FA -------------------------------------------------------------------
def test_fa_positive():
    assert results(P('NP/N'), P('N')) == {('NP', 'FA')}
    assert results(P('S/(S\\NP)'), P('S\\NP')) == {('S', 'FA')}


def test_fa_negative():
    assert results(P('NP/N'), P('NP')) == set()          # wrong argument
    assert results(P('NP\\N'), P('N')) == set()          # wrong direction
    assert results(P('NP'), P('N')) == set()             # atom + atom


# --- BA -------------------------------------------------------------------
def test_ba_positive():
    assert results(P('NP'), P('S\\NP')) == {('S', 'BA')}
    assert results(P('S\\NP'), P('(S\\NP)\\(S\\NP)')) == {('S\\NP', 'BA')}


def test_ba_negative():
    assert results(P('N'), P('S\\NP')) == set()
    assert results(P('NP'), P('S/NP')) == set()          # forward slash: not BA (and no FA)


# --- B> -------------------------------------------------------------------
def test_fc_positive():
    assert results(P('S/(S\\NP)'), P('(S\\NP)/NP')) == {('S/NP', 'B>')}
    assert results(P('NP/N'), P('N/N')) == {('NP/N', 'B>')}


def test_fc_negative():
    assert results(P('S/(S\\NP)'), P('(S\\NP)\\NP')) == set()  # mixed direction (no B>)
    assert results(P('S/NP'), P('N/N')) == set()              # Y mismatch
    assert results(P('S\\NP'), P('NP/N')) == set()             # sigma backward


# --- B< -------------------------------------------------------------------
def test_bc_positive():
    assert results(P('NP\\NP'), P('S\\NP')) == {('S\\NP', 'B<')}
    assert results(P('(S\\NP)\\NP'), P('S\\(S\\NP)')) == {('S\\NP', 'B<')}


def test_bc_negative():
    assert results(P('NP\\NP'), P('S/NP')) == set()
    assert results(P('NP/NP'), P('S\\NP')) == set()
    assert results(P('NP\\N'), P('S\\N')) == set()   # Y mismatch (c wants N, sigma yields NP)


def test_bc_actual():
    assert results(P('NP\\N'), P('S\\NP')) == {('S\\N', 'B<')}


# --- SA -------------------------------------------------------------------
def test_sa_positive_transitive():
    # NP, (S\NP)/NP => S/NP   (subject fills the inner backward slot)
    assert results(P('NP'), P('(S\\NP)/NP')) == {('S/NP', 'SA')}


def test_sa_positive_ditransitive():
    assert results(P('NP'), P('((S\\NP)/NP)/NP')) == {('(S/NP)/NP', 'SA')}


def test_sa_outermost_is_ba_not_sa():
    # NP, S\NP: the only matching slot is outermost -> BA, and no separate SA transition
    assert results(P('NP'), P('S\\NP')) == {('S', 'BA')}


def test_sa_negative():
    assert results(P('NP'), P('(S/NP)/NP')) == set()       # no backward slot
    assert results(P('N'), P('(S\\NP)/NP')) == set()       # wrong atom
    assert results(P('NP'), P('S/(S\\NP)')) == set()       # \NP is inside the argument, not on the spine


def test_sa_ambiguous_takes_outermost_inner():
    c = P('(((S\\NP)\\NP)/NP)')
    # inner backward slots: idx0 (\NP), idx1 (\NP); outermost slot idx2 (/NP)
    assert sa_matches(P('NP'), c) == [0, 1]
    assert results(P('NP'), c) == {('(S\\NP)/NP', 'SA')}


def test_sa_and_ba_both_apply_with_different_results():
    c = P('((S\\NP)/NP)\\NP')
    r = results(P('NP'), c)
    assert ('(S\\NP)/NP', 'BA') in r
    assert ('(S/NP)\\NP', 'SA') in r


def test_depth_bound():
    sigma = P('S/NP')
    c = P('NP/((((S\\NP)/NP)/NP)/NP)')     # argument of depth 4 -> result depth 5
    r5 = results(sigma, c, 5)
    r4 = results(sigma, c, 4)
    assert r5 == {('S/((((S\\NP)/NP)/NP)/NP)', 'B>')}
    assert r4 == set()


def test_no_forbidden_rules():
    # no type raising: NP alone never becomes S/(S\NP)
    assert results(P('NP'), P('NP')) == set()
    # no forward SA: X/A with A on the left cannot fill
    assert results(P('NP'), P('(S/NP)/NP')) == set()
    # no crossed composition
    assert results(P('S/(S\\NP)'), P('(S\\NP)\\NP')) == set()


def test_typecheck_sentences():
    tv = P('(S\\NP)/NP')
    assert typecheck([P('NP'), tv, P('NP')])                       # John loves Mary
    assert typecheck([P('NP/N'), P('N'), P('S\\NP')])               # the dog barks
    assert typecheck([P('NP/N'), P('N/N'), P('N'), tv, P('NP/N'), P('N')])  # the big dog chased the cat
    assert not typecheck([tv, P('NP'), P('NP')])
    assert not typecheck([P('NP'), P('NP'), tv])
    assert not typecheck([P('NP'), tv])                            # incomplete


def test_viterbi_rules_path():
    path = viterbi_rules([P('NP'), P('(S\\NP)/NP'), P('NP')])
    assert [r for _, _, r in path] == ['LEX', 'SA', 'FA']


def test_enumeration_bounds():
    cats = enumerate_categories(['S', 'N', 'NP'], max_arity=3, max_depth=3, max_slashes=4, max_complex_args=1)
    assert all(arity(c) <= 3 and depth(c) <= 3 for c in cats)
    assert P('((S\\NP)/NP)/NP') in cats
    assert P('(S\\NP)/(S\\NP)') in cats
    assert P('((S\\NP)/(S\\NP))/NP') in cats
