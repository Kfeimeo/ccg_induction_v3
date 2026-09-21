"""Lexicon (support) and the probabilistic model over prefix-state derivations.

Two model kinds (config `learning.model`):

  generative (default; deviation from the task text, see report §偏离):
      P(words, derivation) = Π_k P(c_k | σ_{k-1}) · P(w_k | c_k) · 1/n_app(σ_{k-1}, c_k)  · P(stop | S)
      transitions P(c|σ) are Witten-Bell interpolated with a global category distribution,
      emissions P(w|c) are restricted to the lexicon support.  L(D|M) = −log2 P(words).
  conditional (the literal reading "EM estimates P(c|w)"):
      P(accept | words) = Σ_derivations Π_k P(c_k | w_k) · 1/n_app.
      This objective cannot distinguish a grammar from one that collapses atoms and parses
      everything: it never pays for over-generation (see synthetic experiment).

The lexicon P(c|w) reported for the generative model is the normalised expected count.
L(M) = Σ_entries (|c| + pair_bits) in both cases.
"""
from __future__ import annotations
import math
import random
from typing import Dict, Iterable, List, Optional, Set, Tuple
from . import category as C

STOP = '<STOP>'


class Lexicon:
    def __init__(self, support: Dict[str, Set[C.Cat]], pair_bits: float = 10.0, param_bits: float = 0.0):
        self.support = {k: set(v) for k, v in support.items()}
        self.pair_bits = pair_bits
        self.param_bits = param_bits
        self.index: Dict[C.Cat, Set[str]] = {}
        for k, cs in self.support.items():
            for c in cs:
                self.index.setdefault(c, set()).add(k)

    def copy(self) -> 'Lexicon':
        return Lexicon(self.support, self.pair_bits, self.param_bits)

    def add_entry(self, k, c):
        self.support.setdefault(k, set()).add(c)
        self.index.setdefault(c, set()).add(k)

    def remove_entry(self, k, c):
        cs = self.support.get(k)
        if cs is None or c not in cs:
            return
        cs.discard(c)
        if not cs:
            del self.support[k]
        ws = self.index.get(c)
        if ws is not None:
            ws.discard(k)
            if not ws:
                del self.index[c]

    def support_lists(self) -> Dict[str, List[C.Cat]]:
        return {k: sorted(v, key=lambda c: (C.size(c), C.show(c))) for k, v in self.support.items()}

    def entry_bits(self, c: C.Cat) -> float:
        return C.size(c) + self.pair_bits + self.param_bits

    def model_bits(self) -> float:
        return sum(self.entry_bits(c) for cs in self.support.values() for c in cs)

    def n_entries(self) -> int:
        return sum(len(v) for v in self.support.values())

    def categories(self) -> Set[C.Cat]:
        return set(self.index)

    def words_with(self, c: C.Cat) -> List[str]:
        return list(self.index.get(c, ()))


class Model:
    """Parameters + sufficient statistics.  Everything is re-derived from counts by fit()."""

    def __init__(self, lex: Lexicon, kind: str = 'generative', word_counts: Optional[Dict[str, float]] = None,
                 trans_beta: float = 1.0, emit_gamma: float = 0.01, cond_smooth: float = 0.01, goal: str = 'S'):
        self.lex = lex
        self.kind = kind
        self.goal = goal
        self.trans_beta, self.emit_gamma, self.cond_smooth = trans_beta, emit_gamma, cond_smooth
        self.word_counts = word_counts or {}
        # sufficient statistics
        self.n_sc: Dict[Optional[C.Cat], Dict[C.Cat, float]] = {}   # n(σ, c)
        self.n_cw: Dict[C.Cat, Dict[str, float]] = {}                # n(c, w)
        self.n_stop: float = 0.0                                     # times σ=S ended the sentence
        self.n_cont_S: float = 0.0                                   # times σ=S was continued
        # parameters
        self.trans: Dict[Optional[C.Cat], Dict[C.Cat, float]] = {}
        self.lam: Dict[Optional[C.Cat], float] = {}
        self.bo: Dict[C.Cat, float] = {}
        self.stop_p: float = 0.5
        self.emit: Dict[C.Cat, Dict[str, float]] = {}
        self.theta: Dict[str, Dict[C.Cat, float]] = {}               # P(c|w) (conditional params / derived)

    # ------------------------------------------------------------------ copy
    def copy(self, light: bool = True) -> 'Model':
        """light=True shares the transition statistics/parameters (unchanged by lexicon edits
        except merges, which un-share and re-fit them)."""
        m = Model(self.lex.copy(), self.kind, self.word_counts, self.trans_beta, self.emit_gamma, self.cond_smooth, self.goal)
        m.n_sc = self.n_sc if light else {s: dict(d) for s, d in self.n_sc.items()}
        m.n_cw = {c: dict(d) for c, d in self.n_cw.items()}
        m.n_stop, m.n_cont_S = self.n_stop, self.n_cont_S
        m.theta = {w: dict(d) for w, d in self.theta.items()}
        m.emit = {c: dict(d) for c, d in self.emit.items()}
        m.bo = dict(self.bo)
        m.trans, m.lam, m.stop_p = self.trans, self.lam, self.stop_p
        m._fit_conditional()
        return m

    # ------------------------------------------------------------------ init
    def init_uniform(self, theta0: Optional[Dict[str, Dict[C.Cat, float]]] = None):
        """Initialise counts from an initial P0(c|w) (sampled prior): n(c,w) = count(w)·P0(c|w),
        transitions from the global category distribution only (λ=0)."""
        self.n_sc, self.n_cw = {}, {}
        for w, cs in self.lex.support.items():
            th = theta0.get(w) if theta0 else None
            cw = self.word_counts.get(w, 1.0)
            for c in cs:
                p = th.get(c, 0.0) if th else 1.0 / len(cs)
                self.n_cw.setdefault(c, {})[w] = cw * p + 1e-6
        self.n_stop, self.n_cont_S = 1.0, 1.0
        self.theta = {w: {c: (theta0[w].get(c, 0.0) if theta0 else 1.0 / len(cs)) for c in cs} for w, cs in self.lex.support.items()}
        self.fit()

    # ------------------------------------------------------------------ parameters from counts
    def fit_emissions(self, cats=None):
        lex = self.lex
        if cats is None:
            self.emit = {}
            cats = lex.categories()
        for c in cats:
            ws = lex.words_with(c)
            if not ws:
                self.emit.pop(c, None)
                continue
            d = self.n_cw.get(c, {})
            tot = sum(d.get(w, 0.0) for w in ws) + self.emit_gamma * len(ws)
            self.emit[c] = {w: (d.get(w, 0.0) + self.emit_gamma) / tot for w in ws}

    def fit_backoff(self):
        lex = self.lex
        cats = lex.categories()
        kappa = 1.0
        n_c = {}
        for c in cats:
            d = self.n_cw.get(c, {})
            n_c[c] = sum(d.get(w, 0.0) for w in lex.words_with(c))
        z = sum(n_c[c] + kappa * 2.0 ** (-C.size(c)) for c in cats)
        self.bo = {c: (n_c[c] + kappa * 2.0 ** (-C.size(c))) / z for c in cats}

    def fit_transitions(self):
        cats = self.lex.categories()
        self.trans, self.lam = {}, {}
        for s, d in self.n_sc.items():
            d2 = {c: v for c, v in d.items() if c in cats}
            n = sum(d2.values())
            if n <= 0:
                continue
            self.trans[s] = {c: v / n for c, v in d2.items()}
            self.lam[s] = n / (n + self.trans_beta)
        self.stop_p = (self.n_stop + 0.5) / (self.n_stop + self.n_cont_S + 1.0)

    def fit(self):
        self.fit_emissions()
        self.fit_backoff()
        self.fit_transitions()
        self._fit_conditional()

    def _fit_conditional(self):
        lex = self.lex
        if self.kind == 'conditional':
            for w, cs in lex.support.items():
                th = self.theta.get(w, {})
                tot = sum(th.get(c, 0.0) + self.cond_smooth for c in cs)
                self.theta[w] = {c: (th.get(c, 0.0) + self.cond_smooth) / tot for c in cs}

    def trans_p(self, prev: Optional[C.Cat], c: C.Cat) -> float:
        lam = self.lam.get(prev, 0.0)
        p = (1.0 - lam) * self.bo.get(c, 0.0)
        if lam:
            p += lam * self.trans.get(prev, {}).get(c, 0.0)
        if prev == self.goal:
            p *= (1.0 - self.stop_p)
        return p

    def w(self, prev: Optional[C.Cat], c: C.Cat, word: str) -> float:
        """Edge weight without the 1/n_app factor."""
        if self.kind == 'conditional':
            return self.theta.get(word, {}).get(c, 0.0)
        e = self.emit.get(c, {}).get(word, 0.0)
        if not e:
            return 0.0
        return self.trans_p(prev, c) * e

    def final_weight(self) -> float:
        return 1.0 if self.kind == 'conditional' else self.stop_p

    # ------------------------------------------------------------------ M-step
    def set_counts(self, n_sc, n_cw, n_stop, n_cont_S, theta_counts=None):
        self.n_sc, self.n_cw, self.n_stop, self.n_cont_S = n_sc, n_cw, n_stop, n_cont_S
        if self.kind == 'conditional' and theta_counts is not None:
            self.theta = theta_counts
        elif theta_counts is not None:
            # derived P(c|w): expected counts normalised (reported lexicon distribution)
            self.theta = {}
            for w, d in theta_counts.items():
                z = sum(d.values())
                self.theta[w] = {c: v / z for c, v in d.items()} if z > 0 else {}
        self.fit()

    # ------------------------------------------------------------------ lexicon edits (counts-level)
    def remove_entry(self, w: str, c: C.Cat):
        """Remove (w, c); the entry's expected mass is redistributed to w's remaining categories
        in proportion to their counts (approximates EM re-estimation after the removal)."""
        self.lex.remove_entry(w, c)
        m = self.n_cw.get(c, {}).pop(w, 0.0)
        rest = list(self.lex.support.get(w, ()))
        if rest and m > 0:
            tot = sum(self.n_cw.get(c2, {}).get(w, 0.0) + self.emit_gamma for c2 in rest)
            for c2 in rest:
                self.n_cw.setdefault(c2, {})[w] = self.n_cw.get(c2, {}).get(w, 0.0) + m * (self.n_cw.get(c2, {}).get(w, 0.0) + self.emit_gamma) / tot
        th = self.theta.get(w, {})
        pm = th.pop(c, 0.0)
        if th and pm > 0:
            z = sum(th.values())
            for k in th:
                th[k] = th[k] / z if z > 0 else 1.0 / len(th)
        self.fit_emissions([c] + rest)
        self.fit_backoff()
        if c not in self.lex.index:
            self.fit_transitions()
        self._fit_conditional()

    def add_entry(self, w: str, c: C.Cat, mass: float = 0.2):
        new_cat = c not in self.lex.index
        self.lex.add_entry(w, c)
        cw = self.word_counts.get(w, 1.0)
        self.n_cw.setdefault(c, {})[w] = max(self.emit_gamma, mass * cw)
        th = self.theta.setdefault(w, {})
        for k in th:
            th[k] *= (1 - mass)
        th[c] = mass if th else 1.0
        self.fit_emissions([c])
        self.fit_backoff()
        if new_cat:
            self.fit_transitions()
        self._fit_conditional()

    def merge_cats(self, c1: C.Cat, c2: C.Cat):
        self.n_sc = {s: dict(d) for s, d in self.n_sc.items()}   # un-share before editing
        for w in list(self.lex.words_with(c1)):
            self.lex.remove_entry(w, c1)
            self.lex.add_entry(w, c2)
            th = self.theta.get(w, {})
            th[c2] = th.get(c2, 0.0) + th.pop(c1, 0.0)
        d1 = self.n_cw.pop(c1, {})
        d2 = self.n_cw.setdefault(c2, {})
        for w, v in d1.items():
            d2[w] = d2.get(w, 0.0) + v
        for s, d in self.n_sc.items():
            if c1 in d:
                d[c2] = d.get(c2, 0.0) + d.pop(c1)
        self.fit()

    # ------------------------------------------------------------------ reporting
    def entropy(self, w: str) -> float:
        th = self.theta.get(w, {})
        return -sum(p * math.log2(p) for p in th.values() if p > 0)

    def lexicon_json(self) -> dict:
        return {w: {C.show(c): round(p, 4) for c, p in sorted(d.items(), key=lambda x: -x[1])} for w, d in self.theta.items()}


def sample_initial_support(keys: Iterable[str], cluster_of: Dict[str, int], pool: List[C.Cat],
                           n_support: int, seed: int, noise_scale: float = 1.0,
                           atom_boost: Optional[Dict[int, Dict[str, float]]] = None,
                           always: Optional[List[C.Cat]] = None) -> Tuple[Dict[str, Set[C.Cat]], Dict[str, Dict[C.Cat, float]]]:
    """Initial support and P0(c|key):  P0(c|key) ∝ 2^-|c| · exp(noise_scale·(ε_cluster(c) + 0.5 ε_key(c))),
    ε ~ N(0,1); words in a cluster share ε_cluster (distributional-clustering prior + noise).
    n_support categories per key are drawn without replacement from P0 (Gumbel top-k).
    atom_boost (group D): {cluster: {atom: bonus}} added to the log-weight of categories on that atom."""
    log_prior = [-C.size(c) * math.log(2) for c in pool]
    cl_noise: Dict[int, List[float]] = {}
    support, theta = {}, {}
    for key in keys:
        cl = cluster_of.get(key, -1)
        if cl not in cl_noise:
            r = random.Random(seed * 1000 + cl + 7)
            cl_noise[cl] = [r.gauss(0, 1) for _ in pool]
        kr = random.Random((seed * 7919 + hash(key)) & 0x7fffffff)
        w = []
        for i, c in enumerate(pool):
            lw = log_prior[i] + noise_scale * (cl_noise[cl][i] + 0.5 * kr.gauss(0, 1))
            if atom_boost and cl in atom_boost:
                lw += sum(atom_boost[cl].get(a, 0.0) for a in C.atoms_of(c))
            w.append(lw)
        g = [w[i] - math.log(-math.log(kr.random())) for i in range(len(pool))]
        idx = sorted(range(len(pool)), key=lambda i: -g[i])[:n_support]
        cats = [pool[i] for i in idx]
        if always:
            for a in always:
                if a not in cats and a in pool:
                    cats.append(a); idx.append(pool.index(a))
        m = max(w[i] for i in idx)
        ps = [math.exp(w[i] - m) for i in idx]
        z = sum(ps)
        support[key] = set(cats)
        theta[key] = {c: p / z for c, p in zip(cats, ps)}
    return support, theta
