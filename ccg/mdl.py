"""Outer MDL loop: prune / split / merge, each applied iff ΔMDL < 0.

Objective:  L(M) + L(D|M)
  L(M)   = Σ_entries (|c| + pair_bits)             (category code length + word-category pairing)
  L(D|M) = Σ_sentences −log2 P(accept | words), unparsed sentences cost n·escape_bits
Candidate thresholds (min count, entropy, JS) only narrow the search; every change is
accepted only if it lowers the objective.
"""
from __future__ import annotations
import math
import time
from typing import Dict, List, Optional, Set, Tuple
from . import category as C
from .combine import combine
from .lattice import Lattice, build_lattice, forward_backward, failure_record
from .model import Lexicon, Model
from .em import data_bits, em


def js_divergence(p: Dict, q: Dict) -> float:
    zp, zq = sum(p.values()), sum(q.values())
    if zp <= 0 or zq <= 0:
        return 1.0
    keys = set(p) | set(q)
    js = 0.0
    for k in keys:
        a, b = p.get(k, 0.0) / zp, q.get(k, 0.0) / zq
        m = 0.5 * (a + b)
        if a > 0:
            js += 0.5 * a * math.log2(a / m)
        if b > 0:
            js += 0.5 * b * math.log2(b / m)
    return js


class MDLTrainer:
    def __init__(self, sents: List[List[str]], model: Model, pool: List[C.Cat], cfg: dict,
                 max_depth: int = 4, goal: str = 'S', log=print, pool_set: Optional[Set[C.Cat]] = None):
        self.sents = sents
        self.model = model
        self.pool = pool
        self.pool_set = pool_set or set(pool)
        self.cfg = cfg
        self.max_depth = max_depth
        self.goal = goal
        self.log = log
        self.escape = cfg.get('escape_bits_per_word', math.log2(len(pool)) + 1)
        self.lats: List[Lattice] = []
        self.history: List[dict] = []
        self.full_index: Dict[str, List[int]] = {}
        for i, s in enumerate(sents):
            for w in set(s):
                self.full_index.setdefault(w, []).append(i)
        self.active: List[int] = list(range(len(sents)))
        self.index = self.full_index

    def set_active(self, max_len: Optional[int]):
        """Curriculum: restrict the training objective to sentences of length <= max_len."""
        self.active = [i for i, s in enumerate(self.sents) if max_len is None or len(s) <= max_len]
        act = set(self.active)
        self.index = {w: [i for i in idxs if i in act] for w, idxs in self.full_index.items()}
        supp = self.lex.support_lists()
        if not self.lats:
            self.lats = [None] * len(self.sents)
        for i in self.active:
            if self.lats[i] is None:
                self.lats[i] = self.build(self.sents[i], supp)

    # ----------------------------------------------------------------- helpers
    @property
    def lex(self) -> Lexicon:
        return self.model.lex

    def build(self, words, supp):
        return build_lattice(words, supp, self.max_depth, self.goal)

    def Z(self, lat, model) -> float:
        return forward_backward(lat, model, self.goal)[0]

    def rebuild(self, idxs=None):
        supp = self.lex.support_lists()
        if idxs is None:
            if not self.lats:
                self.lats = [None] * len(self.sents)
            for i in self.active:
                self.lats[i] = self.build(self.sents[i], supp)
        else:
            for i in idxs:
                self.lats[i] = self.build(self.sents[i], supp)

    @property
    def active_lats(self):
        return [self.lats[i] for i in self.active]

    def objective(self) -> Tuple[float, float, int]:
        lm = self.lex.model_bits()
        ld, parsed = 0.0, 0
        for lat in self.active_lats:
            Z = self.Z(lat, self.model)
            if Z > 0:
                ld -= math.log2(Z); parsed += 1
            else:
                ld += lat.n * self.escape
        return lm, ld, parsed

    def sentence_bits(self, i: int, model: Model, lat=None) -> float:
        lat = lat or self.lats[i]
        Z = self.Z(lat, model)
        return -math.log2(Z) if Z > 0 else lat.n * self.escape

    def delta_data_bits(self, idxs: List[int], new_model: Model, rebuild: bool) -> Tuple[float, Dict[int, Lattice]]:
        """ΔL(D|M) over sentences idxs when switching to new_model; returns new lattices if rebuilt."""
        supp = new_model.lex.support_lists() if rebuild else None
        delta, new_lats = 0.0, {}
        for i in idxs:
            old = self.sentence_bits(i, self.model)
            if rebuild:
                lat = self.build(self.sents[i], supp)
                new_lats[i] = lat
            else:
                lat = self.lats[i]
            delta += self.sentence_bits(i, new_model, lat) - old
        return delta, new_lats

    # ----------------------------------------------------------------- EM
    def run_em(self):
        hist, stats = em(self.active_lats, self.model, self.cfg.get('em_iters', 20), self.cfg.get('em_tol', 1e-3),
                         self.goal, log=None, mode=self.cfg.get('em_mode', 'soft'), anneal_max=self.cfg.get('anneal_max', 2.0))
        return hist, stats

    # ----------------------------------------------------------------- operations
    def prune_step(self, counts) -> int:
        cands = [(v, key, c) for (key, c), v in counts.items()]
        for key, cs in self.lex.support.items():
            for c in cs:
                if (key, c) not in counts:
                    cands.append((0.0, key, c))
        thr = self.cfg.get('prune_min_count', 0.05)
        frac = self.cfg.get('prune_rel_frac', 0.5)
        wc = self.model.word_counts
        cands = sorted([x for x in cands if x[0] < thr or x[0] < frac * wc.get(x[1], 1.0)], key=lambda x: x[0])
        cands = cands[: 5 * self.cfg.get('max_candidates_per_op', 40)]
        accepted = 0
        anchors = self.cfg.get('anchors', {})
        for v, key, c in cands:
            if key not in self.lex.support or c not in self.lex.support[key] or len(self.lex.support[key]) <= 1:
                continue
            if key in anchors and C.show(c) in anchors[key]:
                continue
            new = self.model.copy()
            new.remove_entry(key, c)
            d_model = -self.lex.entry_bits(c)
            d_data, _ = self.delta_data_bits(self.index.get(key, []), new, rebuild=False)
            if d_model + d_data < 0:
                self.model = new
                accepted += 1
                # a removed entry has zero weight: the cached lattice stays valid
        return accepted

    def propose_for_states(self, states: Dict[C.Cat, float], key: str, top: int) -> List[C.Cat]:
        """Categories in the pool that combine with the given prefix states, ranked by
        prior × weighted number of states they combine with."""
        scores: Dict[C.Cat, float] = {}
        have = self.lex.support.get(key, set())
        for sigma, w in states.items():
            for c in self._combinable(sigma):
                if c in have:
                    continue
                scores[c] = scores.get(c, 0.0) + w
        ranked = sorted(scores.items(), key=lambda x: -(x[1] * 2.0 ** (-C.size(x[0]))))
        return [c for c, _ in ranked[:top]]

    _comb_cache: Dict = {}

    def _combinable(self, sigma) -> List[C.Cat]:
        """Pool categories c such that combine(sigma, c) is non-empty (constructed, then filtered)."""
        if sigma in self._comb_cache:
            return self._comb_cache[sigma]
        out: Set[C.Cat] = set()
        atoms = sorted({a for c in self.pool for a in C.atoms_of(c)})
        small = [c for c in self.pool if C.n_slashes(c) <= 2]
        if sigma is None:
            out = set(c for c in self.pool if C.n_slashes(c) <= 3)
        else:
            # FA: c = arg(sigma); BA: X\sigma; B>: arg(sigma)/Z; B<: X\res(sigma); SA: inner \sigma
            if not C.is_atom(sigma) and sigma[1] == C.FWD:
                out.add(sigma[2])
                for z in small:
                    out.add((sigma[2], C.FWD, z))
            for x in small:
                out.add((x, C.BWD, sigma))
            if not C.is_atom(sigma) and sigma[1] == C.BWD:
                for x in small:
                    out.add((x, C.BWD, sigma[0]))
            one = [c for c in self.pool if C.n_slashes(c) <= 1]
            for x in small:
                # SA: (X\sigma)|Y
                for y in one:
                    out.add(((x, C.BWD, sigma), C.FWD, y))
                    out.add(((x, C.BWD, sigma), C.BWD, y))
            for x in atoms:
                # SA: ((X\sigma)|Y)|Z  (e.g. ((S\NP)/PP)/NP, ((S\S)/(S\NP))/NP)
                for y in one:
                    for z in atoms:
                        for s1 in (C.FWD, C.BWD):
                            for s2 in (C.FWD, C.BWD):
                                out.add((((x, C.BWD, sigma), s1, y), s2, z))
        res = [c for c in out if c in self.pool_set and combine(sigma, c, self.max_depth)]
        self._comb_cache[sigma] = res
        return res

    def forward_states(self, words: List[str], upto: int, supp) -> Set[Optional[C.Cat]]:
        """Unpruned prefix states after words[:upto] under support supp."""
        states: Set[Optional[C.Cat]] = {None}
        for k in range(upto):
            nxt = set()
            for st in states:
                for c in supp.get(words[k], ()):
                    for r, _ in combine(st, c, self.max_depth):
                        nxt.add(r)
            states = nxt
            if not states:
                break
        return states

    def suffix_completes(self, words: List[str], start_states: Set[C.Cat], k: int, supp) -> bool:
        states = set(start_states)
        for j in range(k, len(words)):
            nxt = set()
            for st in states:
                for c in supp.get(words[j], ()):
                    for r, _ in combine(st, c, self.max_depth):
                        nxt.add(r)
            states = nxt
            if not states:
                return False
        return self.goal in states

    def oracle_proposals(self, key: str, occurrences: List[Tuple[int, int]], top: int,
                         state_filter: Optional[Set[C.Cat]] = None) -> List[C.Cat]:
        """Categories c' (not yet in support) such that giving `key` the category c' at an
        occurrence (sentence i, position k) makes the sentence parseable, everything else
        fixed.  Ranked by (#occurrences fixed) · 2^-|c'|.  state_filter restricts the prefix
        states considered (split step: the minority group)."""
        supp = self.lex.support_lists()
        have = self.lex.support.get(key, set())
        score: Dict[C.Cat, float] = {}
        for (i, k) in occurrences:
            words = self.sents[i]
            F = self.forward_states(words, k, supp)
            if state_filter is not None:
                F = {s for s in F if s in state_filter}
            if not F:
                continue
            tried: Set[C.Cat] = set()
            for sigma in F:
                for c in self._combinable(sigma):
                    if c in have or c in tried:
                        continue
                    tried.add(c)
                    starts = set()
                    for s2 in F:
                        for r, _ in combine(s2, c, self.max_depth):
                            starts.add(r)
                    if self.suffix_completes(words, starts, k + 1, supp):
                        score[c] = score.get(c, 0.0) + 1.0
        ranked = sorted(score.items(), key=lambda x: -(x[1] * 2.0 ** (-C.size(x[0]))))
        return [c for c, _ in ranked[:top]]

    def occurrences_of(self, key: str, only_failed: bool = False, max_occ: int = 16) -> List[Tuple[int, int]]:
        occ = []
        for i in self.index.get(key, []):
            if only_failed and self.lats[i].accepted:
                continue
            for k, w in enumerate(self.sents[i]):
                if w == key:
                    occ.append((i, k))
        if len(occ) > max_occ:
            step = len(occ) / max_occ
            occ = [occ[int(j * step)] for j in range(max_occ)]
        return occ

    def split_step(self, ctx_key, counts) -> int:
        """§3.3 split: words with high H(c|w) whose occurrences separate into two groups by
        prefix state; a new entry for the minority group is proposed and kept iff ΔMDL < 0."""
        ent_min = self.cfg.get('split_entropy_min', 0.5)
        cands = []
        for key in self.lex.support:
            h = self.model.entropy(key)
            if h < ent_min:
                continue
            # occurrences by prefix state (posterior weighted), pooled over the word's categories
            states: Dict[C.Cat, float] = {}
            for (k2, c), d in ctx_key.items():
                if k2 != key:
                    continue
                for sigma, v in d.items():
                    states[sigma] = states.get(sigma, 0.0) + v
            if len(states) < 2:
                continue
            top_state = max(states, key=states.get)
            minority = {s: v for s, v in states.items() if s != top_state}
            tot = sum(states.values())
            if sum(minority.values()) < 0.2 * tot:
                continue
            cands.append((h, key, minority))
        cands.sort(key=lambda x: -x[0])
        cands = cands[: self.cfg.get('max_candidates_per_op', 40)]
        top = self.cfg.get('proposals_per_word', 5)
        return self._try_additions([(key, self.oracle_proposals(key, self.occurrences_of(key), top, set(minority)))
                                    for _, key, minority in cands])

    def failure_step(self) -> int:
        """Failure-driven proposals (addition to §3.3, documented): for unparsed sentences,
        propose categories for the failing word that combine with σ_{k-1}; accept iff ΔMDL < 0."""
        by_key: Dict[str, Dict[C.Cat, float]] = {}
        back = self.cfg.get('failure_lookback', 3)
        for lat in self.active_lats:
            if lat.accepted:
                continue
            k = min(lat.fail_pos, lat.n)
            # the failing word and the words before it (the missing category is often on an
            # earlier word, e.g. a pre-subject adverb that must take the subject)
            for j in range(max(1, k - back), k + 1):
                key = lat.words[j - 1]
                d = by_key.setdefault(key, {})
                d['_'] = d.get('_', 0.0) + (1.0 if j == k else 0.5)
        cands = sorted(by_key.items(), key=lambda x: -sum(x[1].values()))[: self.cfg.get('max_candidates_per_op', 40)]
        top = self.cfg.get('proposals_per_word', 5)
        return self._try_additions([(key, self.oracle_proposals(key, self.occurrences_of(key, only_failed=True), top))
                                    for key, states in cands])

    def pair_step(self, max_sents: int = 300) -> int:
        """Two-word proposals for sentences that no single addition can parse: tentatively give a
        word before the failure point one of its top single candidates, then run the oracle for the
        remaining failure; the pair is added jointly iff ΔMDL < 0."""
        supp0 = self.lex.support_lists()
        failed = [i for i in self.active if not self.lats[i].accepted]
        if len(failed) > max_sents:
            step = len(failed) / max_sents
            failed = [failed[int(j * step)] for j in range(max_sents)]
        accepted = 0
        tried_pairs: Set[Tuple[str, C.Cat, str, C.Cat]] = set()
        for i in failed:
            lat = self.lats[i]
            if lat.accepted:
                continue
            words = self.sents[i]
            k = min(lat.fail_pos, lat.n)
            done = False
            for j in range(max(1, k - 2), k + 1):
                if done:
                    break
                key1 = words[j - 1]
                F = self.forward_states(words, j - 1, supp0)
                cands1: Dict[C.Cat, float] = {}
                for sigma in F:
                    for c in self._combinable(sigma):
                        if c not in self.lex.support.get(key1, set()):
                            cands1[c] = cands1.get(c, 0.0) + 1.0
                cands1 = sorted(cands1, key=lambda c: C.size(c))[:12]
                for c1 in cands1:
                    supp1 = dict(supp0); supp1[key1] = supp0.get(key1, []) + [c1]
                    lat1 = self.build(words, supp1)
                    if lat1.accepted:
                        continue  # single fix: handled by failure_step
                    k2 = min(lat1.fail_pos, lat1.n)
                    if k2 <= j:
                        continue
                    for j2 in range(max(j + 1, k2 - 1), k2 + 1):
                        key2 = words[j2 - 1]
                        F2 = self.forward_states(words, j2 - 1, supp1)
                        found = None
                        for sigma in F2:
                            for c2 in self._combinable(sigma):
                                if c2 in self.lex.support.get(key2, set()) and key2 != key1:
                                    continue
                                if (key1, c1, key2, c2) in tried_pairs:
                                    continue
                                starts = set()
                                for s2 in F2:
                                    for r, _ in combine(s2, c2, self.max_depth):
                                        starts.add(r)
                                if self.suffix_completes(words, starts, j2, supp1):
                                    found = c2
                                    break
                            if found:
                                break
                        if not found:
                            continue
                        tried_pairs.add((key1, c1, key2, found))
                        new = self.model.copy()
                        if self.cfg.get('rigid', False):
                            for kk, cc in ((key1, c1), (key2, found)):
                                old = list(new.lex.support.get(kk, ()))
                                new.add_entry(kk, cc, mass=1.0)
                                for o in old:
                                    if o != cc:
                                        new.remove_entry(kk, o)
                        else:
                            new.add_entry(key1, c1, mass=self.cfg.get('new_entry_mass', 0.2))
                            new.add_entry(key2, found, mass=self.cfg.get('new_entry_mass', 0.2))
                        idxs = sorted(set(self.index.get(key1, [])) | set(self.index.get(key2, [])))
                        d_model = new.lex.model_bits() - self.lex.model_bits()
                        d_data, new_lats = self.delta_data_bits(idxs, new, rebuild=True)
                        if d_model + d_data < 0:
                            self.model = new
                            for ii, l in new_lats.items():
                                self.lats[ii] = l
                            supp0 = self.lex.support_lists()
                            accepted += 1
                            done = True
                        break
                    if done:
                        break
        return accepted

    def _try_additions(self, proposals: List[Tuple[str, List[C.Cat]]]) -> int:
        accepted = 0
        rigid = self.cfg.get('rigid', False)
        anchors = self.cfg.get('anchors', {})
        for key, cats in proposals:
            n_new = 0
            for c in cats:
                if key not in self.lex.support or c in self.lex.support[key] or key in anchors:
                    continue
                new = self.model.copy()
                if rigid:
                    for old in list(new.lex.support[key]):
                        new.remove_entry(key, old) if len(new.lex.support.get(key, ())) > 1 else None
                    # a rigid word swaps its single category
                    old = next(iter(new.lex.support[key]))
                    new.add_entry(key, c, mass=1.0)
                    new.remove_entry(key, old)
                else:
                    new.add_entry(key, c, mass=self.cfg.get('new_entry_mass', 0.2))
                idxs = self.index.get(key, [])
                d_model = new.lex.model_bits() - self.lex.model_bits()
                d_data, new_lats = self.delta_data_bits(idxs, new, rebuild=True)
                if d_model + d_data < 0:
                    self.model = new
                    for i, lat in new_lats.items():
                        self.lats[i] = lat
                    accepted += 1
                    n_new += 1
                    if n_new >= self.cfg.get('max_new_per_word', 3):
                        break
        return accepted

    def rename_step(self) -> int:
        """Merge move, global variant: a complex category X that occurs (also as a sub-part of other
        categories) is renamed to an atom that no lexical category currently uses.  This is a
        bijective relabelling, so derivations are preserved and L(M) drops; accepted iff ΔMDL < 0."""
        used_atoms = {a for c in self.lex.categories() for a in C.atoms_of(c)}
        atoms = sorted({a for c in self.pool for a in C.atoms_of(c)})
        free = [a for a in atoms if a not in used_atoms and a != self.goal]
        if not free:
            return 0
        # complex sub-categories by frequency of occurrence inside lexical categories
        sub: Dict[C.Cat, int] = {}

        def walk(c):
            if C.is_atom(c):
                return
            sub[c] = sub.get(c, 0) + 1
            walk(c[0]); walk(c[2])
        for key, cs in self.lex.support.items():
            for c in cs:
                walk(c)
        cands = sorted(sub.items(), key=lambda x: -x[1] * C.size(x[0]))[:10]
        accepted = 0
        for x, _ in cands:
            if not free:
                break
            a = free[0]
            new = self.model.copy()
            # substitute x -> a everywhere
            mapping = {}
            for key in list(new.lex.support):
                for c in list(new.lex.support[key]):
                    c2 = C.substitute(c, x, a)
                    if c2 != c:
                        mapping[c] = c2
            if not mapping or any(c2 not in self.pool_set for c2 in mapping.values()):
                continue
            for c, c2 in mapping.items():
                new.merge_cats(c, c2)
            d_model = new.lex.model_bits() - self.lex.model_bits()
            idxs = sorted({i for key, cs in self.lex.support.items() if any(c in mapping for c in cs) for i in self.index.get(key, [])})
            d_data, new_lats = self.delta_data_bits(idxs, new, rebuild=True)
            if d_model + d_data < 0:
                self.model = new
                for i, lat in new_lats.items():
                    self.lats[i] = lat
                free.pop(0)
                accepted += 1
                self.log(f'   rename {C.show(x)} -> {a} (Δ={d_model + d_data:.1f})')
        return accepted

    def merge_step(self, ctx_cat, counts) -> int:
        cats = [c for c in self.lex.categories() if c in ctx_cat]
        thr = self.cfg.get('merge_js_max', 0.3)
        pairs = []
        for i in range(len(cats)):
            for j in range(len(cats)):
                if i == j:
                    continue
                c1, c2 = cats[i], cats[j]
                if C.size(c1) < C.size(c2):
                    continue  # merge the larger/rarer into the smaller
                js = js_divergence(ctx_cat[c1], ctx_cat[c2])
                if js <= thr:
                    pairs.append((js, c1, c2))
        pairs.sort(key=lambda x: x[0])
        pairs = pairs[: self.cfg.get('max_candidates_per_op', 40)]
        accepted = 0
        merged: Set[C.Cat] = set()
        for js, c1, c2 in pairs:
            if c1 in merged or c2 in merged or c1 not in self.lex.categories():
                continue
            new = self.model.copy()
            keys = [k for k, cs in new.lex.support.items() if c1 in cs]
            d_model = sum((-self.lex.entry_bits(c1)) + (0.0 if c2 in self.lex.support[k] else self.lex.entry_bits(c2)) for k in keys)
            new.merge_cats(c1, c2)
            idxs = sorted({i for k in keys for i in self.index.get(k, [])})
            d_data, new_lats = self.delta_data_bits(idxs, new, rebuild=True)
            if d_model + d_data < 0:
                self.model = new
                for i, lat in new_lats.items():
                    self.lats[i] = lat
                merged.add(c1)
                accepted += 1
        return accepted

    # ----------------------------------------------------------------- main loop
    def train(self, max_outer: int = 8, use_failure_proposals: bool = True) -> List[dict]:
        """Outer loop.  cfg['curriculum'] = [L1, L2, ...]: stages restricted to sentences of
        length <= L (the last stage must cover all sentences); each stage runs until the lexicon
        stops changing or cfg['rounds_per_stage'] rounds."""
        t0 = time.time()
        stages = self.cfg.get('curriculum') or [None]
        rps = self.cfg.get('rounds_per_stage', max_outer)
        rnd = 0
        for si, L in enumerate(stages):
            self.set_active(L)
            self.log(f'-- stage {si}: max_len={L} active={len(self.active)}/{len(self.sents)}')
            last = (si == len(stages) - 1)
            budget = max_outer - rnd if last else min(rps, max_outer - rnd)
            best, stale = float('inf'), 0
            for r in range(budget + 1):
                stop = self._round(rnd, t0, final=(r == budget) or (last and rnd == max_outer), use_failure_proposals=use_failure_proposals)
                tot = self.history[-1]['total']
                if tot < best - 1.0:
                    best, stale = tot, 0
                else:
                    stale += 1
                if r < budget:
                    rnd += 1
                if stop or stale >= self.cfg.get('patience', 2):
                    if not stop:
                        self.log('   no objective improvement: stage done')
                    break
        return self.history

    def _round(self, rnd, t0, final, use_failure_proposals=True) -> bool:
        if True:
            em_hist, stats = self.run_em()
            lm, ld, parsed = self.objective()
            counts = {(w, c): v for w, d in stats['theta_counts'].items() for c, v in d.items()}
            ctx_cat, ctx_key = stats['ctx_cat'], stats['ctx_key']
            rec = self.structure_record(rnd, lm, ld, parsed, em_hist)
            self.history.append(rec)
            self.log(f'round {rnd}: L(M)={lm:.0f} L(D|M)={ld:.0f} total={lm+ld:.0f} parsed={parsed}/{len(self.active)} '
                     f'cats={rec["n_categories"]} entries={rec["n_entries"]} avg/word={rec["avg_cats_per_word"]:.2f} '
                     f'|Q|={rec["Q_mean"]:.1f} b={rec["b_mean"]:.2f} t={time.time()-t0:.0f}s')
            if final:
                return True
            n_prune = self.prune_step(counts) if not self.cfg.get('rigid', False) else 0
            n_split = self.split_step(ctx_key, counts)
            n_fail = self.failure_step() if use_failure_proposals else 0
            n_pair = self.pair_step() if (use_failure_proposals and self.cfg.get('pair_proposals', True) and n_fail < 5) else 0
            n_fail += n_pair
            n_merge = self.merge_step(ctx_cat, counts)
            n_ren = self.rename_step() if self.cfg.get('rename_moves', True) else 0
            rec.update({'n_prune': n_prune, 'n_split': n_split, 'n_fail_add': n_fail, 'n_merge': n_merge, 'n_rename': n_ren})
            self.log(f'   ops: prune={n_prune} split={n_split} fail_add={n_fail} merge={n_merge} rename={n_ren}')
            if n_prune + n_split + n_fail + n_merge + n_ren == 0:
                self.log('   lexicon unchanged: stage done')
                return True
            return False

    def structure_record(self, rnd, lm, ld, parsed, em_hist) -> dict:
        from .lattice import lattice_stats
        sts = [lattice_stats(l) for l in self.active_lats]
        n = len(sts)
        return {
            'round': rnd, 'L_M': lm, 'L_D': ld, 'total': lm + ld, 'parsed': parsed, 'n_sent': len(self.active),
            'n_categories': len(self.lex.categories()), 'n_entries': self.lex.n_entries(),
            'avg_cats_per_word': self.lex.n_entries() / max(1, len(self.lex.support)),
            'Q_mean': sum(s['Q_unpruned_mean'] for s in sts) / n if n else 0,
            'Q_max': max(s['Q_unpruned_max'] for s in sts) if n else 0,
            'b_mean': sum(s['b_mean'] for s in sts) / n if n else 0,
            'em_ll': em_hist[-1] if em_hist else None, 'em_iters': len(em_hist),
        }

    def failure_log(self) -> List[dict]:
        supp = self.lex.support_lists()
        out = []
        for lat in self.active_lats:
            fr = failure_record(lat, supp)
            if fr:
                out.append(fr)
        return out
