"""MDL trainer for the CKY (inside-outside) contrast system: same objective and operations,
derivations are unconstrained binary trees."""
from __future__ import annotations
import math
from typing import Dict, List, Optional, Set, Tuple
from . import category as C
from .cky import Chart, CKYModel, inside_outside, combine_pair
from .combine import combine
from .mdl import MDLTrainer
from .lattice import lattice_stats


class CKYTrainer(MDLTrainer):
    @property
    def nf(self) -> bool:
        return bool(self.cfg.get('normal_form', False))

    def build(self, words, supp):
        return Chart(words, supp, self.max_depth, self.goal, self.nf)

    def Z(self, chart, model) -> float:
        return inside_outside(chart, model)[0]

    def run_em(self):
        iters, tol = self.cfg.get('em_iters', 20), self.cfg.get('em_tol', 1e-3)
        hist, prev, stats = [], None, None
        for it in range(iters + 1):
            stats = self.e_step()
            hist.append(stats['ll'])
            if it == iters or (prev is not None and abs(stats['ll'] - prev) < tol * max(1.0, abs(prev))):
                break
            prev = stats['ll']
            self.model.n_pe, self.model.n_lex = stats['n_pe'], stats['n_lex']
            self.model.base.set_counts({}, stats['n_cw'], 1.0, 1.0, stats['theta_counts'])
            self.model.fit()
        return hist, stats

    def e_step(self):
        n_pe: Dict = {}; n_lex: Dict = {}; n_cw: Dict = {}; theta_counts: Dict = {}
        ctx_cat: Dict = {}; ctx_key: Dict = {}
        ll, parsed = 0.0, 0
        for ch in self.active_lats:
            Z, ep, lp = inside_outside(ch, self.model)
            if Z <= 0:
                continue
            parsed += 1; ll += math.log(Z)
            for parent, exp, post in ep:
                n_pe.setdefault(parent, {})[exp] = n_pe.get(parent, {}).get(exp, 0.0) + post
                rule, lc, rc = exp
                d = ctx_cat.setdefault(lc, {}); d[(parent, 'L')] = d.get((parent, 'L'), 0.0) + post
                d = ctx_cat.setdefault(rc, {}); d[(parent, 'R')] = d.get((parent, 'R'), 0.0) + post
            for k, c, post in lp:
                w = ch.words[k]
                n_lex[c] = n_lex.get(c, 0.0) + post
                n_cw.setdefault(c, {})[w] = n_cw.get(c, {}).get(w, 0.0) + post
                theta_counts.setdefault(w, {})[c] = theta_counts.get(w, {}).get(c, 0.0) + post
                d2 = ctx_key.setdefault((w, c), {}); d2[k] = d2.get(k, 0.0) + post
        return {'n_pe': n_pe, 'n_lex': n_lex, 'n_cw': n_cw, 'theta_counts': theta_counts, 'll': ll,
                'parsed': parsed, 'ctx_cat': ctx_cat, 'ctx_key': ctx_key}

    # --- proposals: neighbours instead of prefix states -------------------------------
    def oracle_proposals(self, key: str, occurrences, top: int, state_filter=None):
        supp = self.lex.support_lists()
        have = self.lex.support.get(key, set())
        score: Dict[C.Cat, float] = {}
        small = [c for c in self.pool if C.n_slashes(c) <= 2]
        for (i, k) in occurrences[:6]:
            words = self.sents[i]
            ch = Chart(words, supp, self.max_depth, self.goal, self.nf) if not self.lats[i].accepted else self.lats[i]
            neigh_L = set(); neigh_R = set()
            for (a, b), d in ch.cell.items():
                if b == k:
                    neigh_L.update(nd[0] for nd in d)
                if a == k + 1:
                    neigh_R.update(nd[0] for nd in d)
            cands = set()
            for L in neigh_L:
                for c in self._combinable(L):
                    cands.add(c)
            for R in neigh_R:
                for c in small:
                    if combine_pair(c, R, False, self.max_depth):
                        cands.add(c)
            if k == 0:
                cands.update(c for c in self.pool if C.n_slashes(c) <= 3)
            cands = [c for c in cands if c not in have and c in self.pool_set]
            cands.sort(key=C.size)
            for c in cands[:150]:
                supp2 = dict(supp); supp2[key] = supp.get(key, []) + [c]
                if Chart(words, supp2, self.max_depth, self.goal, self.nf).accepted:
                    score[c] = score.get(c, 0.0) + 1.0
        ranked = sorted(score.items(), key=lambda x: -(x[1] * 2.0 ** (-C.size(x[0]))))
        return [c for c, _ in ranked[:top]]

    def pair_step(self, max_sents: int = 300) -> int:
        return 0   # no failure position in CKY; neighbour-based oracle proposals only

    def failure_step(self) -> int:
        by_key: Dict[str, float] = {}
        for ch in self.active_lats:
            if ch.accepted:
                continue
            for w in set(ch.words):
                by_key[w] = by_key.get(w, 0.0) + 1.0
        cands = sorted(by_key.items(), key=lambda x: -x[1])[: self.cfg.get('max_candidates_per_op', 40)]
        top = self.cfg.get('proposals_per_word', 5)
        return self._try_additions([(key, self.oracle_proposals(key, self.occurrences_of(key, only_failed=True), top))
                                    for key, _ in cands])

    def structure_record(self, rnd, lm, ld, parsed, em_hist) -> dict:
        n = len(self.active_lats)
        cells = [len(d) for ch in self.active_lats for d in ch.cell.values()]
        return {
            'round': rnd, 'L_M': lm, 'L_D': ld, 'total': lm + ld, 'parsed': parsed, 'n_sent': len(self.sents),
            'n_categories': len(self.lex.categories()), 'n_entries': self.lex.n_entries(),
            'avg_cats_per_word': self.lex.n_entries() / max(1, len(self.lex.support)),
            'Q_mean': sum(cells) / len(cells) if cells else 0, 'Q_max': max(cells) if cells else 0,
            'b_mean': sum(ch.n_edges() for ch in self.active_lats) / max(1, sum(len(ch.cell) for ch in self.active_lats)),
            'em_ll': em_hist[-1] if em_hist else None, 'em_iters': len(em_hist),
        }

    def failure_log(self):
        return [{'sentence': ' '.join(ch.words), 'fail_pos': -1, 'word': '<CKY>', 'word_cats': []} for ch in self.active_lats if not ch.accepted]


def induce_cky(train_words, atoms, cfg: dict, seed: int, log=print, max_depth: int = 4, goal: str = 'S',
               atom_boost=None, normal_form: bool = False):
    """CKY / Eisner-normal-form counterpart of induce.induce(): same keys, clustering, initial
    support, anchors and MDL configuration; CKYModel + CKYTrainer instead of the prefix model."""
    import collections, math
    from .cky import CKYModel
    from .model import Lexicon, sample_initial_support
    from .induce import make_keys
    from .clustering import cluster_words
    lc, mc, cs = cfg['learning'], cfg['mdl'], cfg['category_space']
    rules = cfg.get('rules', {})
    cluster_of, counts = cluster_words(train_words, lc['n_clusters'], seed)
    key_of, keyseqs = make_keys(train_words, lc['min_freq'], cluster_of)
    keys = sorted(set(k for s in keyseqs for k in s))
    pool = C.filter_pool(C.enumerate_categories(atoms, cs['max_arity'], cs['max_depth'], cs['max_slashes'], cs['max_complex_args']),
                         rules.get('forbid_TR', True), rules.get('standard_slots', True))
    init_pool = [c for c in pool if C.n_slashes(c) <= lc.get('init_max_slashes', 2)]
    cluster_key = {k: (cluster_of.get(k, -1) if not k.startswith('<C') else int(k[2:-1])) for k in keys}
    support, theta0 = sample_initial_support(keys, cluster_key, init_pool, lc['init_support'], seed, lc['noise_scale'], atom_boost)
    anchors = {w: [C.parse(x) for x in xs] for w, xs in (cfg.get('anchors') or {}).items()}
    for w, xs in anchors.items():
        if w in support:
            support[w] = set(xs)
            theta0[w] = {x: 1.0 / len(xs) for x in xs}
    rigid = lc.get('rigid', False)
    if rigid:
        for k in support:
            best = max(theta0[k], key=theta0[k].get)
            support[k] = {best}; theta0[k] = {best: 1.0}
    lex = Lexicon(support, math.log2(len(keys)))
    key_counts = collections.Counter(k for s in keyseqs for k in s)
    model = CKYModel(lex, dict(key_counts), lc.get('trans_beta', 1.0), lc.get('emit_gamma', 0.01), goal)
    model.init_uniform(theta0)
    log(f'seed {seed}: {len(train_words)} sentences, {len(keys)} keys, pool={len(pool)} init_pool={len(init_pool)} '
        f'init entries={lex.n_entries()} anchors={len(anchors)} normal_form={normal_form}')
    tcfg = dict(mc)
    tcfg.update({'em_iters': lc['em_iters'], 'em_tol': lc['em_tol'], 'rigid': rigid,
                 'anchors': {w: [C.show(x) for x in xs] for w, xs in anchors.items()},
                 'escape_bits_per_word': math.log2(len(pool)) + math.log2(len(keys)) + 1, 'rename_moves': False,
                 'normal_form': normal_form})
    trainer = CKYTrainer(keyseqs, model, pool, tcfg, max_depth, goal, log)
    trainer.train(mc['max_outer_iters'], True)
    return trainer, key_of, cluster_of
