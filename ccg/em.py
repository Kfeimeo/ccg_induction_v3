"""Inner loop: EM over cached prefix-state lattices (generative or conditional model)."""
from __future__ import annotations
import math
from typing import Dict, List, Optional, Tuple
from . import category as C
from .lattice import Lattice, Edge, build_lattice, forward_backward, viterbi
from .model import Model


def data_bits(lats: List[Lattice], model: Model, escape_bits_per_word: float, goal='S') -> Tuple[float, int, float]:
    """L(D|M) in bits, number of parsed sentences, log-likelihood (nats) of parsed sentences.
    Unparsed sentences cost n · escape_bits_per_word (explicit coding), keeping MDL finite."""
    total, parsed, ll = 0.0, 0, 0.0
    for lat in lats:
        Z, _, _ = forward_backward(lat, model, goal)
        if Z > 0:
            total += -math.log2(Z)
            ll += math.log(Z)
            parsed += 1
        else:
            total += lat.n * escape_bits_per_word
    return total, parsed, ll


class PowerModel:
    """Tempered model: edge weights raised to the power beta (annealed / sharpened E-step)."""

    def __init__(self, base, beta):
        self.base, self.beta, self.kind = base, beta, base.kind

    def w(self, prev, c, word):
        x = self.base.w(prev, c, word)
        return x ** self.beta if x > 0 else 0.0

    def final_weight(self):
        return self.base.final_weight() ** self.beta


def e_step(lats: List[Lattice], model: Model, goal='S', beta: float = 1.0, hard: bool = False):
    """Expected counts.  beta != 1 tempers the posteriors (edge weights ^ beta); hard=True uses
    the Viterbi derivation (counts 0/1)."""
    scorer = model if beta == 1.0 else PowerModel(model, beta)
    n_sc: Dict = {}
    n_cw: Dict = {}
    theta_counts: Dict[str, Dict[C.Cat, float]] = {}
    ctx_cat: Dict[C.Cat, Dict] = {}
    ctx_key: Dict[Tuple[str, C.Cat], Dict] = {}
    n_stop = n_cont = 0.0
    ll, parsed = 0.0, 0
    for lat in lats:
        if hard:
            path, p = viterbi(lat, model, goal)
            if path is None:
                continue
            Zt, _, _ = forward_backward(lat, model, goal)
            Z = Zt
            edges = [(k, Edge(prev, c, nxt, rule, 1.0), 1.0) for k, (prev, c, nxt, rule) in enumerate(path)]
        else:
            Z, cnt, edges = forward_backward(lat, scorer, goal)
            if Z <= 0:
                continue
            if beta != 1.0:
                Z, _, _ = forward_backward(lat, model, goal)
        if Z <= 0:
            continue
        parsed += 1
        ll += math.log(Z)
        n_stop += 1.0
        for k, e, post in edges:
            w = lat.words[k]
            n_sc.setdefault(e.prev, {})[e.cat] = n_sc.get(e.prev, {}).get(e.cat, 0.0) + post
            n_cw.setdefault(e.cat, {})[w] = n_cw.get(e.cat, {}).get(w, 0.0) + post
            theta_counts.setdefault(w, {})[e.cat] = theta_counts.get(w, {}).get(e.cat, 0.0) + post
            d = ctx_cat.setdefault(e.cat, {}); d[e.prev] = d.get(e.prev, 0.0) + post
            d2 = ctx_key.setdefault((w, e.cat), {}); d2[e.prev] = d2.get(e.prev, 0.0) + post
            if e.prev == goal:
                n_cont += post
    return {'n_sc': n_sc, 'n_cw': n_cw, 'theta_counts': theta_counts, 'n_stop': n_stop, 'n_cont': n_cont,
            'll': ll, 'parsed': parsed, 'ctx_cat': ctx_cat, 'ctx_key': ctx_key}


def em(lats: List[Lattice], model: Model, iters: int = 20, tol: float = 1e-3, goal='S', log=None,
       mode: str = 'soft', anneal_max: float = 2.0):
    """EM in place. Returns (history of log-likelihoods, last E-step statistics).
    mode: 'soft' (standard), 'hard' (Viterbi training), 'anneal' (beta grows 1 -> anneal_max)."""
    history, prev, stats = [], None, None
    for it in range(iters):
        beta = 1.0 if mode != 'anneal' else 1.0 + (anneal_max - 1.0) * it / max(1, iters - 1)
        stats = e_step(lats, model, goal, beta, mode == 'hard')
        history.append(stats['ll'])
        model.set_counts(stats['n_sc'], stats['n_cw'], stats['n_stop'], stats['n_cont'], stats['theta_counts'])
        if log:
            log(f'  EM it {it}: ll={stats["ll"]:.2f} parsed={stats["parsed"]}/{len(lats)}')
        if prev is not None and abs(stats['ll'] - prev) < tol * max(1.0, abs(prev)):
            break
        prev = stats['ll']
    # final statistics under the last parameters (for candidate generation)
    stats = e_step(lats, model, goal)
    return history, stats
