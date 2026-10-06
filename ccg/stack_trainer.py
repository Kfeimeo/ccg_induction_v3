"""MDL trainer for the stack (Lambek-product) incremental system."""
from __future__ import annotations
from typing import List, Set
from . import category as C
from .mdl import MDLTrainer
from .stack_lattice import build_stack_lattice, step, Stack, goal_state


class StackTrainer(MDLTrainer):
    @property
    def max_stack(self) -> int:
        return int(self.cfg.get('max_stack', 3))

    @property
    def cascade(self) -> bool:
        return bool(self.cfg.get('cascade', True))

    def build(self, words, supp):
        return build_stack_lattice(words, supp, self.max_depth, self.goal, self.max_stack, self.cascade)

    def successors(self, state, c):
        return [st for st, _ in step(state, c, self.max_depth, self.max_stack, self.cascade)]

    def goal_state(self):
        return goal_state(self.goal)

    def oracle_proposals(self, key: str, occurrences, top: int, state_filter=None):
        """Stack version: candidates are computed once per occurrence from the distinct stack
        tops (plus a capped set of small pushable categories), not per stack state; occurrences
        and candidates are capped to keep the suffix checks affordable."""
        supp = self.lex.support_lists()
        have = self.lex.support.get(key, set())
        score = {}
        max_occ = int(self.cfg.get('stack_oracle_occurrences', 6))
        max_cands = int(self.cfg.get('stack_oracle_candidates', 60))
        push_pool = [c for c in self.pool if C.n_slashes(c) <= 1]
        for (i, k) in occurrences[:max_occ]:
            words = self.sents[i]
            F = self.forward_states(words, k, supp)
            if state_filter is not None:
                F = {s for s in F if s in state_filter}
            if not F:
                continue
            tops = {s[-1] for s in F if s}
            can_push = any((s is None or len(s) < self.max_stack) for s in F)
            cands = set()
            for t in tops:
                cands.update(MDLTrainer._combinable(self, t, use_state=False))
            if can_push:
                cands.update(push_pool)
            cands = [c for c in cands if c not in have]
            cands.sort(key=lambda c: (C.size(c), C.show(c)))
            for c in cands[:max_cands]:
                starts = set()
                for s2 in F:
                    starts.update(self.successors(s2, c))
                if starts and self.suffix_completes(words, starts, k + 1, supp):
                    score[c] = score.get(c, 0.0) + 1.0
        ranked = sorted(score.items(), key=lambda x: -(x[1] * 2.0 ** (-C.size(x[0]))))
        return [c for c, _ in ranked[:top]]

    def _combinable(self, sigma) -> List[C.Cat]:
        """Candidates for a stack state: categories combining with the top, plus (if a push is
        possible) the small categories (<= 2 slashes), since any of them can be pushed."""
        key = ('stack', sigma)
        if key in self._comb_cache:
            return self._comb_cache[key]
        top = sigma[-1] if sigma else None
        cands: Set[C.Cat] = set(MDLTrainer._combinable(self, top, use_state=False))
        if sigma is None or len(sigma) < self.max_stack:
            cands.update(c for c in self.pool if C.n_slashes(c) <= 2)
        res = [c for c in cands if self.successors(sigma, c)]
        self._comb_cache[key] = res
        return res
