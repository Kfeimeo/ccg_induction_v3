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
    def build(self, words, supp):
        return Chart(words, supp, self.max_depth, self.goal)

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
            ch = Chart(words, supp, self.max_depth, self.goal) if not self.lats[i].accepted else self.lats[i]
            neigh_L = set(); neigh_R = set()
            for (a, b), d in ch.cell.items():
                if b == k:
                    neigh_L.update(d.keys())
                if a == k + 1:
                    neigh_R.update(d.keys())
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
                if Chart(words, supp2, self.max_depth, self.goal).accepted:
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
