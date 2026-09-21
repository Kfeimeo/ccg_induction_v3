"""Prefix-state lattice for a sentence, forward-backward, Viterbi and the failure log.

A lattice stores, for each position k = 1..n, the set of reachable prefix-state
categories and the edges (prev_state, cat, next_state, rule, 1/n_applicable).  The
probability of a derivation is  Π_k P(c_k | w_k) · 1/n_app(σ_{k-1}, c_k)   where n_app is
the number of distinct results of combine(σ_{k-1}, c_k)  (uniform choice among
applicable rules, so that Σ over derivations ≤ 1).

The model quantity used everywhere is  P(accept | w) = Σ_{accepting derivations} P(deriv).
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from . import category as C
from .combine import combine

GOAL = 'S'


@dataclass
class Edge:
    prev: Optional[C.Cat]
    cat: C.Cat
    nxt: C.Cat
    rule: str
    w: float  # 1 / n_applicable


@dataclass
class Lattice:
    words: List[str]
    states: List[Dict[C.Cat, List[Edge]]]   # states[k] : next_state -> incoming edges, k=0..n-1 (position k+1)
    accepted: bool
    fail_pos: int = -1                        # 1-based position of first failure (n+1 => no S at end)
    fail_states: Tuple[C.Cat, ...] = ()       # σ_{k-1} candidates at failure
    unpruned_sizes: List[int] = field(default_factory=list)
    branch_counts: List[int] = field(default_factory=list)  # successors per (σ, w_k)

    @property
    def n(self):
        return len(self.words)


def build_lattice(words: List[str], support: Dict[str, List[C.Cat]], max_depth: int = 4,
                  goal: C.Cat = GOAL, beam: int = 0) -> Lattice:
    """Forward expansion then backward pruning to accepting states.

    support[w] = candidate categories of word w (must be non-empty for all words).
    beam: if > 0, cap the number of live states per position keeping a diversity
    quota per target atom (no pure α truncation exists here: pruning is structural,
    not probability based; see report).
    """
    n = len(words)
    layers: List[Dict[C.Cat, List[Edge]]] = []
    prev_states: List[Optional[C.Cat]] = [None]
    unpruned, branch = [], []
    fail_pos = -1
    for k, w in enumerate(words):
        layer: Dict[C.Cat, List[Edge]] = {}
        cands = support.get(w, [])
        for s in prev_states:
            for c in cands:
                res = combine(s, c, max_depth)
                branch.append(len(res))
                if not res:
                    continue
                wt = 1.0 / len(res)
                for r, rule in res:
                    layer.setdefault(r, []).append(Edge(s, c, r, rule, wt))
        if beam and len(layer) > beam:
            layer = _diversity_beam(layer, beam)
        unpruned.append(len(layer))
        layers.append(layer)
        if not layer:
            fail_pos = k + 1
            break
        prev_states = list(layer.keys())
    lat = Lattice(words, layers, accepted=False, unpruned_sizes=unpruned, branch_counts=branch)
    if fail_pos != -1:
        lat.fail_pos = fail_pos
        lat.fail_states = tuple(layers[fail_pos - 2].keys()) if fail_pos >= 2 else ()
        return lat
    if goal not in layers[-1]:
        lat.fail_pos = n + 1
        lat.fail_states = tuple(layers[-1].keys())
        return lat
    # backward pruning
    alive = {goal}
    for k in range(n - 1, -1, -1):
        layer = layers[k]
        new_layer: Dict[C.Cat, List[Edge]] = {}
        prev_alive = set()
        for st in alive:
            edges = layer.get(st)
            if edges:
                new_layer[st] = edges
                for e in edges:
                    prev_alive.add(e.prev)
        layers[k] = new_layer
        alive = prev_alive
    lat.accepted = True
    return lat


def _diversity_beam(layer, beam):
    # keep a quota per target atom, then fill by smallest size (structural, not α-based)
    by_target: Dict[str, list] = {}
    for st in layer:
        by_target.setdefault(C.spine(st)[0], []).append(st)
    keep = set()
    quota = max(1, beam // max(1, len(by_target)))
    for t, sts in by_target.items():
        sts.sort(key=C.size)
        keep.update(sts[:quota])
    rest = sorted((s for s in layer if s not in keep), key=C.size)
    for s in rest:
        if len(keep) >= beam:
            break
        keep.add(s)
    return {s: layer[s] for s in layer if s in keep}


def forward_backward(lat: Lattice, theta: Dict[str, Dict[C.Cat, float]], goal: C.Cat = GOAL):
    """Return (Z, expected counts {(k, cat): posterior}, edge posteriors list).

    theta[w][c] = P(c|w).  Z = P(accept | words).
    """
    if not lat.accepted:
        return 0.0, {}, []
    n = lat.n
    alpha: List[Dict[Optional[C.Cat], float]] = [{None: 1.0}]
    for k in range(n):
        th = theta[lat.words[k]]
        a: Dict[C.Cat, float] = {}
        for st, edges in lat.states[k].items():
            tot = 0.0
            for e in edges:
                ap = alpha[k].get(e.prev, 0.0)
                if ap:
                    tot += ap * th.get(e.cat, 0.0) * e.w
            if tot:
                a[st] = tot
        alpha.append(a)
    Z = alpha[n].get(goal, 0.0)
    if Z <= 0.0:
        return 0.0, {}, []
    beta: List[Dict[Optional[C.Cat], float]] = [dict() for _ in range(n + 1)]
    beta[n] = {goal: 1.0}
    counts: Dict[Tuple[int, C.Cat], float] = {}
    edge_post = []
    for k in range(n - 1, -1, -1):
        th = theta[lat.words[k]]
        b: Dict[Optional[C.Cat], float] = {}
        for st, edges in lat.states[k].items():
            bn = beta[k + 1].get(st, 0.0)
            if not bn:
                continue
            for e in edges:
                ap = alpha[k].get(e.prev, 0.0)
                if not ap:
                    continue
                p = th.get(e.cat, 0.0) * e.w
                if not p:
                    continue
                b[e.prev] = b.get(e.prev, 0.0) + p * bn
                post = ap * p * bn / Z
                counts[(k, e.cat)] = counts.get((k, e.cat), 0.0) + post
                edge_post.append((k, e, post))
        beta[k] = b
    return Z, counts, edge_post


def viterbi(lat: Lattice, theta: Dict[str, Dict[C.Cat, float]], goal: C.Cat = GOAL):
    """Best derivation: list of (prev_state, cat, next_state, rule) per position, and its prob."""
    if not lat.accepted:
        return None, 0.0
    n = lat.n
    best: List[Dict[Optional[C.Cat], Tuple[float, Optional[Edge]]]] = [{None: (1.0, None)}]
    for k in range(n):
        th = theta[lat.words[k]]
        layer: Dict[C.Cat, Tuple[float, Optional[Edge]]] = {}
        for st, edges in lat.states[k].items():
            bp, be = 0.0, None
            for e in edges:
                pv = best[k].get(e.prev)
                if pv is None:
                    continue
                p = pv[0] * th.get(e.cat, 0.0) * e.w
                if p > bp:
                    bp, be = p, e
            if be is not None:
                layer[st] = (bp, be)
        best.append(layer)
    if goal not in best[n]:
        return None, 0.0
    p, e = best[n][goal]
    path = []
    cur = goal
    for k in range(n - 1, -1, -1):
        _, e = best[k + 1][cur]
        path.append((e.prev, e.cat, e.nxt, e.rule))
        cur = e.prev
    path.reverse()
    return path, p


def failure_record(lat: Lattice, support: Dict[str, List[C.Cat]]) -> Optional[dict]:
    """§3.4 failure log entry for a sentence with zero likelihood."""
    if lat.accepted:
        return None
    k = lat.fail_pos
    n = lat.n
    rec = {
        'sentence': ' '.join(lat.words),
        'fail_pos': k,
        'sigma_prev': [C.show(s) for s in lat.fail_states][:20],
        'n_sigma_prev': len(lat.fail_states),
    }
    if k <= n:
        rec['word'] = lat.words[k - 1]
        rec['word_cats'] = [C.show(c) for c in support.get(lat.words[k - 1], [])]
    else:
        rec['word'] = '<END>'
        rec['word_cats'] = []
    return rec


def lattice_stats(lat: Lattice) -> dict:
    live = [len(l) for l in lat.states if l]
    return {
        'Q_unpruned_mean': (sum(lat.unpruned_sizes) / len(lat.unpruned_sizes)) if lat.unpruned_sizes else 0.0,
        'Q_unpruned_max': max(lat.unpruned_sizes) if lat.unpruned_sizes else 0,
        'Q_live_mean': (sum(live) / len(live)) if live else 0.0,
        'b_mean': (sum(lat.branch_counts) / len(lat.branch_counts)) if lat.branch_counts else 0.0,
        'n_edges': sum(len(es) for l in lat.states for es in l.values()),
    }
