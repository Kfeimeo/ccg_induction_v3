"""Contrast system (§6): the same lexicon model and MDL objective, but derivations are
arbitrary binary trees (CKY, inside-outside) with FA, BA, B>, B< between any adjacent
constituents and SA with a lexical right item.  Generative model:
    P(tree) = Π_nodes P(expansion | parent category) · Π_leaves P(w | c),
expansion = (rule, left cat, right cat); root category is S.
"""
from __future__ import annotations
import math
import time
from typing import Dict, List, Optional, Set, Tuple
from . import category as C
from .combine import combine, sa_matches
from .model import Lexicon, Model


def combine_pair(left: C.Cat, right: C.Cat, right_lexical: bool, max_depth: int):
    """Binary combination of two constituents (left, right)."""
    out, seen = [], set()

    def add(res, rule):
        if C.depth(res) > max_depth or res in seen:
            return
        seen.add(res)
        out.append((res, rule))
    if not C.is_atom(left) and left[1] == C.FWD and left[2] == right:
        add(left[0], 'FA')
    if not C.is_atom(right) and right[1] == C.BWD and right[2] == left:
        add(right[0], 'BA')
    if (not C.is_atom(left) and left[1] == C.FWD and not C.is_atom(right) and right[1] == C.FWD and right[0] == left[2]):
        add((left[0], C.FWD, right[2]), 'B>')
    if (not C.is_atom(left) and left[1] == C.BWD and not C.is_atom(right) and right[1] == C.BWD and right[2] == left[0]):
        add((right[0], C.BWD, left[2]), 'B<')
    if right_lexical and not C.is_atom(right):
        target, slots = C.spine(right)
        inner = [i for i in sa_matches(left, right) if i < len(slots) - 1]
        if inner:
            i = inner[-1]
            add(C.build(target, slots[:i] + slots[i + 1:]), 'SA')
    return out


class Chart:
    """Hypergraph of all derivations of a sentence under a support."""

    def __init__(self, words, support, max_depth=4, goal='S'):
        self.words = words
        n = len(words)
        self.n = n
        # cell[(i,j)] : cat -> list of (kind, payload): ('LEX', word) or ('BIN', k, lc, rc, rule, w)
        self.cell: Dict[Tuple[int, int], Dict[C.Cat, list]] = {}
        for i, w in enumerate(words):
            self.cell[(i, i + 1)] = {c: [('LEX', w)] for c in support.get(w, [])}
        for span in range(2, n + 1):
            for i in range(0, n - span + 1):
                j = i + span
                d: Dict[C.Cat, list] = {}
                for k in range(i + 1, j):
                    L, R = self.cell.get((i, k), {}), self.cell.get((k, j), {})
                    if not L or not R:
                        continue
                    rlex = (j - k == 1)
                    for lc in L:
                        for rc in R:
                            res = combine_pair(lc, rc, rlex, max_depth)
                            if not res:
                                continue
                            wgt = 1.0 / len(res)
                            for r, rule in res:
                                d.setdefault(r, []).append(('BIN', k, lc, rc, rule, wgt))
                self.cell[(i, j)] = d
        self.accepted = goal in self.cell.get((0, n), {})
        self.goal = goal
        if self.accepted:
            self._prune()

    def _prune(self):
        """Keep only nodes reachable from the root."""
        n = self.n
        alive: Set[Tuple[int, int, C.Cat]] = set()
        stack = [(0, n, self.goal)]
        while stack:
            node = stack.pop()
            if node in alive:
                continue
            alive.add(node)
            i, j, c = node
            for e in self.cell[(i, j)][c]:
                if e[0] == 'BIN':
                    _, k, lc, rc, _, _ = e
                    stack.append((i, k, lc)); stack.append((k, j, rc))
        for (i, j), d in self.cell.items():
            for c in list(d):
                if (i, j, c) not in alive:
                    del d[c]

    def n_edges(self):
        return sum(len(es) for d in self.cell.values() for es in d.values())


class CKYModel:
    """P(expansion | parent) with Witten-Bell smoothing over the parent's expansions; P(w|c) as Model."""

    def __init__(self, lex: Lexicon, word_counts, beta=1.0, emit_gamma=0.01, goal='S'):
        self.base = Model(lex, 'generative', word_counts, beta, emit_gamma, 0.01, goal)
        self.lex = lex
        self.goal = goal
        self.kind = 'generative'
        self.n_pe: Dict[C.Cat, Dict[tuple, float]] = {}   # n(parent, expansion)
        self.n_lex: Dict[C.Cat, float] = {}                 # n(parent used as leaf)
        self.beta = beta
        self.fit()

    def init_uniform(self, theta0=None):
        self.base.init_uniform(theta0)
        self.fit()

    def fit(self):
        self.base.fit()
        self.pe, self.lam, self.plex = {}, {}, {}
        for p, d in self.n_pe.items():
            n = sum(d.values()) + self.n_lex.get(p, 0.0)
            if n <= 0:
                continue
            self.pe[p] = {e: v / n for e, v in d.items()}
            self.plex[p] = self.n_lex.get(p, 0.0) / n
            self.lam[p] = n / (n + self.beta)

    def exp_p(self, parent, exp) -> float:
        lam = self.lam.get(parent, 0.0)
        # backoff: uniform over a nominal 100 expansions
        return lam * self.pe.get(parent, {}).get(exp, 0.0) + (1 - lam) * 0.01

    def lex_p(self, parent, word) -> float:
        lam = self.lam.get(parent, 0.0)
        pl = lam * self.plex.get(parent, 0.0) + (1 - lam) * 0.5
        return pl * self.base.emit.get(parent, {}).get(word, 0.0)

    @property
    def theta(self):
        return self.base.theta

    def entropy(self, w):
        return self.base.entropy(w)

    def copy(self):
        m = CKYModel(self.lex.copy(), self.base.word_counts, self.beta, self.base.emit_gamma, self.goal)
        m.base = self.base.copy()
        m.lex = m.base.lex
        m.n_pe = {p: dict(d) for p, d in self.n_pe.items()}
        m.n_lex = dict(self.n_lex)
        m.fit()
        return m

    def remove_entry(self, w, c):
        self.base.remove_entry(w, c); self.lex = self.base.lex; self.fit()

    def add_entry(self, w, c, mass=0.2):
        self.base.add_entry(w, c, mass); self.lex = self.base.lex; self.fit()

    def merge_cats(self, c1, c2):
        self.base.merge_cats(c1, c2); self.lex = self.base.lex
        d1 = self.n_pe.pop(c1, {}); d2 = self.n_pe.setdefault(c2, {})
        for e, v in d1.items():
            d2[e] = d2.get(e, 0.0) + v
        self.n_lex[c2] = self.n_lex.get(c2, 0.0) + self.n_lex.pop(c1, 0.0)
        self.fit()

    @property
    def word_counts(self):
        return self.base.word_counts


def inside_outside(chart: Chart, model: CKYModel):
    """Return Z, expansion posteriors [(parent, exp, post)], leaf posteriors [(k, cat, post)]."""
    if not chart.accepted:
        return 0.0, [], []
    n = chart.n
    inside: Dict[Tuple[int, int, C.Cat], float] = {}
    for span in range(1, n + 1):
        for i in range(0, n - span + 1):
            j = i + span
            for c, edges in chart.cell.get((i, j), {}).items():
                tot = 0.0
                for e in edges:
                    if e[0] == 'LEX':
                        tot += model.lex_p(c, e[1])
                    else:
                        _, k, lc, rc, rule, w = e
                        tot += model.exp_p(c, (rule, lc, rc)) * w * inside.get((i, k, lc), 0.0) * inside.get((k, j, rc), 0.0)
                if tot:
                    inside[(i, j, c)] = tot
    Z = inside.get((0, n, chart.goal), 0.0)
    if Z <= 0:
        return 0.0, [], []
    outside: Dict[Tuple[int, int, C.Cat], float] = {(0, n, chart.goal): 1.0}
    exp_post, leaf_post = [], []
    for span in range(n, 0, -1):
        for i in range(0, n - span + 1):
            j = i + span
            for c, edges in chart.cell.get((i, j), {}).items():
                o = outside.get((i, j, c), 0.0)
                if not o:
                    continue
                for e in edges:
                    if e[0] == 'LEX':
                        p = model.lex_p(c, e[1])
                        leaf_post.append((i, c, o * p / Z))
                    else:
                        _, k, lc, rc, rule, w = e
                        li, ri = inside.get((i, k, lc), 0.0), inside.get((k, j, rc), 0.0)
                        p = model.exp_p(c, (rule, lc, rc)) * w
                        if not (li and ri and p):
                            continue
                        post = o * p * li * ri / Z
                        exp_post.append((c, (rule, lc, rc), post))
                        outside[(i, k, lc)] = outside.get((i, k, lc), 0.0) + o * p * ri
                        outside[(k, j, rc)] = outside.get((k, j, rc), 0.0) + o * p * li
    return Z, exp_post, leaf_post


def viterbi_tree(chart: Chart, model: CKYModel):
    """Best tree: returns (prob, tree) with tree = (cat, i, j, rule, left, right) or (cat, i, word)."""
    if not chart.accepted:
        return 0.0, None
    n = chart.n
    best: Dict[Tuple[int, int, C.Cat], Tuple[float, tuple]] = {}
    for span in range(1, n + 1):
        for i in range(0, n - span + 1):
            j = i + span
            for c, edges in chart.cell.get((i, j), {}).items():
                bp, bt = 0.0, None
                for e in edges:
                    if e[0] == 'LEX':
                        p = model.lex_p(c, e[1])
                        t = (c, i, e[1])
                    else:
                        _, k, lc, rc, rule, w = e
                        l, r = best.get((i, k, lc)), best.get((k, j, rc))
                        if not l or not r:
                            continue
                        p = model.exp_p(c, (rule, lc, rc)) * w * l[0] * r[0]
                        t = (c, i, j, rule, l[1], r[1])
                    if p > bp:
                        bp, bt = p, t
                if bt is not None:
                    best[(i, j, c)] = (bp, bt)
    return best.get((0, n, chart.goal), (0.0, None))


def tree_heads(tree, words, headmap) -> List[int]:
    """Dependencies from a binary tree via the same head-mapping module: events (f, slot, a)."""
    from .deps import resolve_heads
    events = []
    lexcat = [None] * len(words)

    def walk(t):
        """returns (head word, owners innermost-first, cat)"""
        if len(t) == 3:
            c, i, _ = t
            lexcat[i] = c
            return i, tuple((i, s) for s in range(C.arity(c))), c
        c, i, j, rule, l, r = t
        hl, ol, cl = walk(l)
        hr, orr, cr = walk(r)
        if rule == 'FA':
            f, s = ol[-1]; events.append((f, s, hr)); return hl, ol[:-1], c
        if rule == 'BA':
            f, s = orr[-1]; events.append((f, s, hl)); return hr, orr[:-1], c
        if rule == 'B>':
            f, s = ol[-1]; events.append((f, s, hr)); return hl, ol[:-1] + (orr[-1],), c
        if rule == 'B<':
            f, s = orr[-1]; events.append((f, s, hl)); return hr, orr[:-1] + (ol[-1],), c
        if rule == 'SA':
            _, slots = C.spine(cr)
            m = [q for q in sa_matches(cl, cr) if q < len(slots) - 1]
            q = m[-1]
            events.append((hr, q, hl))
            return hr, tuple(o for o in orr if o[1] != q), c
        raise ValueError(rule)
    h, _, _ = walk(tree)
    return resolve_heads(words, lexcat, events, h, headmap)


def tree_spans(tree) -> set:
    out = set()

    def walk(t):
        if len(t) == 3:
            return
        c, i, j, rule, l, r = t
        out.add((i, j - 1))
        walk(l); walk(r)
    walk(tree)
    return out
