"""Category data structures.

A category is either an atom (str, e.g. 'S', 'NP', 'S[dcl]') or a tuple
(result, slash, argument) with slash in {'/', '\\'}.

Conventions
-----------
* depth(atom) = 0, depth(X|Y) = 1 + max(depth X, depth Y)   (slash nesting depth)
* arity(c)    = number of slots on the spine (outermost result chain)
* size(c)     = number of symbols = #atoms + #slashes            (used for the prior 2^-|c|)
* spine(c)    = (target atom, [(slash, arg), ...]) innermost slot first
"""
from __future__ import annotations
from functools import lru_cache
from typing import Iterable, List, Tuple, Union

FWD = '/'
BWD = '\\'
Cat = Union[str, tuple]


def is_atom(c: Cat) -> bool:
    return isinstance(c, str)


def make(result: Cat, slash: str, arg: Cat) -> Cat:
    assert slash in (FWD, BWD)
    return (result, slash, arg)


def result(c: Cat) -> Cat:
    return c[0]


def slash(c: Cat) -> str:
    return c[1]


def arg(c: Cat) -> Cat:
    return c[2]


@lru_cache(maxsize=None)
def depth(c: Cat) -> int:
    if is_atom(c):
        return 0
    return 1 + max(depth(c[0]), depth(c[2]))


@lru_cache(maxsize=None)
def arity(c: Cat) -> int:
    n = 0
    while not is_atom(c):
        n += 1
        c = c[0]
    return n


@lru_cache(maxsize=None)
def size(c: Cat) -> int:
    if is_atom(c):
        return 1
    return 1 + size(c[0]) + size(c[2])


@lru_cache(maxsize=None)
def n_slashes(c: Cat) -> int:
    if is_atom(c):
        return 0
    return 1 + n_slashes(c[0]) + n_slashes(c[2])


@lru_cache(maxsize=None)
def spine(c: Cat) -> Tuple[str, Tuple[Tuple[str, Cat], ...]]:
    """Return (target atom, slots innermost-first)."""
    slots = []
    while not is_atom(c):
        slots.append((c[1], c[2]))
        c = c[0]
    slots.reverse()
    return c, tuple(slots)


def build(target: Cat, slots: Iterable[Tuple[str, Cat]]) -> Cat:
    """Inverse of spine(): slots innermost-first."""
    c = target
    for s, a in slots:
        c = (c, s, a)
    return c


@lru_cache(maxsize=None)
def show(c: Cat) -> str:
    if is_atom(c):
        return c
    r, s, a = c
    rs = show(r) if is_atom(r) or _is_left_chain(r) else '(' + show(r) + ')'
    as_ = show(a) if is_atom(a) else '(' + show(a) + ')'
    return rs + s + as_


def _is_left_chain(c: Cat) -> bool:
    # Results are printed without parentheses only when they are atomic; we always
    # parenthesise complex results for readability: (S\NP)/NP.
    return False


def parse(s: str) -> Cat:
    """Parse a category string like '(S\\NP)/NP' or 'S[dcl]'."""
    s = s.replace(' ', '')
    pos = 0

    def peek():
        return s[pos] if pos < len(s) else None

    def parse_atom():
        nonlocal pos
        start = pos
        while pos < len(s) and (s[pos].isalnum() or s[pos] in '[]_:-'):
            pos += 1
        if start == pos:
            raise ValueError(f'bad category {s!r} at {pos}')
        return s[start:pos]

    def parse_primary():
        nonlocal pos
        if peek() == '(':
            pos += 1
            c = parse_expr()
            if peek() != ')':
                raise ValueError(f'missing ) in {s!r}')
            pos += 1
            return c
        return parse_atom()

    def parse_expr():
        nonlocal pos
        c = parse_primary()
        while peek() in (FWD, BWD):
            sl = s[pos]
            pos += 1
            a = parse_primary()
            c = (c, sl, a)
        return c

    c = parse_expr()
    if pos != len(s):
        raise ValueError(f'trailing input in {s!r}')
    return c


def atoms_of(c: Cat) -> List[str]:
    if is_atom(c):
        return [c]
    return atoms_of(c[0]) + atoms_of(c[2])


def rename_atoms(c: Cat, mapping: dict) -> Cat:
    if is_atom(c):
        return mapping.get(c, c)
    return (rename_atoms(c[0], mapping), c[1], rename_atoms(c[2], mapping))


def substitute(c: Cat, x: Cat, y: Cat) -> Cat:
    """Replace every occurrence of sub-category x in c by y."""
    if c == x:
        return y
    if is_atom(c):
        return c
    return (substitute(c[0], x, y), c[1], substitute(c[2], x, y))


def enumerate_categories(atoms: List[str], max_arity: int = 3, max_depth: int = 3,
                         max_slashes: int = 5, max_complex_args: int = 2,
                         arg_max_arity: int = 2) -> List[Cat]:
    """Enumerate the category space over `atoms`.

    Constraints (see report §"默认值"): arity <= max_arity, slash-nesting depth <= max_depth,
    total slashes <= max_slashes, at most max_complex_args non-atomic arguments,
    arguments themselves have arity <= arg_max_arity and atomic arguments.
    """
    # argument pool: atoms + categories with atomic args and arity <= arg_max_arity
    pool = list(atoms)
    layer = list(atoms)
    for _ in range(arg_max_arity):
        new = []
        for r in layer:
            for sl in (FWD, BWD):
                for a in atoms:
                    new.append((r, sl, a))
        pool.extend(new)
        layer = new
    out = []
    seen = set()

    def rec(c, ar, ncomplex):
        if c in seen:
            return
        seen.add(c)
        out.append(c)
        if ar >= max_arity:
            return
        for sl in (FWD, BWD):
            for a in pool:
                comp = 0 if is_atom(a) else 1
                if ncomplex + comp > max_complex_args:
                    continue
                nc = (c, sl, a)
                if depth(nc) > max_depth or n_slashes(nc) > max_slashes:
                    continue
                rec(nc, ar + 1, ncomplex + comp)

    for a in atoms:
        rec(a, 0, 0)
    out.sort(key=lambda c: (size(c), show(c)))
    return out


def prior_logprob2(c: Cat) -> float:
    """log2 P(c) with P(c) ∝ 2^-|c| (unnormalised)."""
    return -float(size(c))


def is_type_raised(c: Cat) -> bool:
    """X/(X\\Y) or X\\(X/Y) anywhere in the category."""
    if is_atom(c):
        return False
    r, s, a = c
    if not is_atom(a) and a[0] == r and a[1] != s:
        return True
    return is_type_raised(r) or is_type_raised(a)


def has_standard_slots(c: Cat) -> bool:
    """Standard English slot order: on every spine, all backward slots are inner to all
    forward slots, i.e. (X\\Y)/Z shapes only (no (X/Z)\\Y).  Applied recursively to arguments."""
    if is_atom(c):
        return True
    _, slots = spine(c)
    seen_fwd = False
    for sl, a in slots:
        if sl == FWD:
            seen_fwd = True
        elif seen_fwd:
            return False
        if not has_standard_slots(a):
            return False
    return True


def filter_pool(pool, forbid_tr: bool = True, standard_slots: bool = True):
    out = pool
    if forbid_tr:
        out = [c for c in out if not is_type_raised(c)]
    if standard_slots:
        out = [c for c in out if has_standard_slots(c)]
    return out
