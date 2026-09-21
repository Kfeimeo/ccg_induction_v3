"""The fixed formal system: strictly left-branching combination of a prefix state σ
with the category c of the next word.

Rules (σ left, c right):
  FA : X/Y, Y        => X
  BA : Y, X\\Y        => X
  B> : X/Y, Y/Z      => X/Z
  B< : Y\\Z, X\\Y      => X\\Z
  SA : A, X[Γ,(\\A),Δ] => X[Γ,Δ]   (A fills a *non-outermost* backward slot on c's spine;
                                    the outermost one is BA.  If several inner slots
                                    match, the outermost of them is taken and the
                                    event is recorded.)
  LEX: ε, c          => c         (sentence-initial)

Nothing else: no type-raising, no forward SA, no CAL, no argument permutation, no
unary rules, no punctuation rules.  A result whose slash depth exceeds max_depth is
discarded (state complexity bound).
"""
from __future__ import annotations
from functools import lru_cache
from typing import List, Optional, Tuple
from . import category as C

RULES = ('LEX', 'FA', 'BA', 'B>', 'B<', 'SA')

# ambiguity statistics (SA slot not unique); reset via reset_stats()
STATS = {'sa_ambiguous': 0, 'sa_applied': 0, 'combine_calls': 0}


def reset_stats():
    for k in STATS:
        STATS[k] = 0


def sa_matches(sigma: C.Cat, c: C.Cat) -> List[int]:
    """Indices (innermost-first) of backward slots on c's spine equal to sigma."""
    _, slots = C.spine(c)
    return [i for i, (sl, a) in enumerate(slots) if sl == C.BWD and a == sigma]


@lru_cache(maxsize=None)
def _combine_cached(sigma: Optional[C.Cat], c: C.Cat, max_depth: int) -> Tuple[Tuple[C.Cat, str], ...]:
    out: List[Tuple[C.Cat, str]] = []
    if sigma is None:
        out.append((c, 'LEX'))
        return tuple(out)
    seen = set()

    def add(res, rule):
        if C.depth(res) > max_depth:
            return
        if res in seen:
            return
        seen.add(res)
        out.append((res, rule))

    # FA
    if not C.is_atom(sigma) and sigma[1] == C.FWD and sigma[2] == c:
        add(sigma[0], 'FA')
    # BA
    if not C.is_atom(c) and c[1] == C.BWD and c[2] == sigma:
        add(c[0], 'BA')
    # B>
    if (not C.is_atom(sigma) and sigma[1] == C.FWD and not C.is_atom(c)
            and c[1] == C.FWD and c[0] == sigma[2]):
        add((sigma[0], C.FWD, c[2]), 'B>')
    # B<
    if (not C.is_atom(sigma) and sigma[1] == C.BWD and not C.is_atom(c)
            and c[1] == C.BWD and c[2] == sigma[0]):
        add((c[0], C.BWD, sigma[2]), 'B<')
    # SA (inner backward slots only)
    if not C.is_atom(c):
        target, slots = C.spine(c)
        matches = sa_matches(sigma, c)
        inner = [i for i in matches if i < len(slots) - 1]
        if inner:
            i = inner[-1]  # outermost among inner matches
            new_slots = slots[:i] + slots[i + 1:]
            add(C.build(target, new_slots), 'SA')
    return tuple(out)


def combine(sigma: Optional[C.Cat], c: C.Cat, max_depth: int = 4) -> Tuple[Tuple[C.Cat, str], ...]:
    """All (result, rule) pairs, deduplicated by result category."""
    STATS['combine_calls'] += 1
    return _combine_cached(sigma, c, max_depth)


def record_sa_stats(sigma: Optional[C.Cat], c: C.Cat, rule: str):
    """Called on Viterbi derivations to count SA applications / ambiguous slot matches."""
    if rule == 'SA':
        STATS['sa_applied'] += 1
        if len(sa_matches(sigma, c)) > 1:
            STATS['sa_ambiguous'] += 1


def typecheck(cats: List[C.Cat], max_depth: int = 4, goal: C.Cat = 'S') -> bool:
    """Does the category sequence admit an accepting left-branching derivation?"""
    states = {None}
    for c in cats:
        nxt = set()
        for s in states:
            for r, _ in combine(s, c, max_depth):
                nxt.add(r)
        states = nxt
        if not states:
            return False
    return goal in states


def viterbi_rules(cats: List[C.Cat], max_depth: int = 4, goal: C.Cat = 'S'):
    """Return one accepting (state, rule) path for a category sequence, or None."""
    back = [dict() for _ in cats]
    states = {None}
    for k, c in enumerate(cats):
        nxt = {}
        for s in states:
            for r, rule in combine(s, c, max_depth):
                if r not in nxt:
                    nxt[r] = (s, rule)
        back[k] = nxt
        states = set(nxt)
        if not states:
            return None
    if goal not in states:
        return None
    path = []
    cur = goal
    for k in range(len(cats) - 1, -1, -1):
        prev, rule = back[k][cur]
        path.append((prev, cur, rule))
        cur = prev
    path.reverse()
    return path
