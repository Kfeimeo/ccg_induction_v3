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

    def _combinable(self, sigma) -> List[C.Cat]:
        """Candidates for a stack state: categories combining with the top, plus (if a push is
        possible) the small categories (<= 2 slashes), since any of them can be pushed."""
        key = ('stack', sigma)
        if key in self._comb_cache:
            return self._comb_cache[key]
        top = sigma[-1] if sigma else None
        cands: Set[C.Cat] = set(MDLTrainer._combinable(self, top))
        if sigma is None or len(sigma) < self.max_stack:
            cands.update(c for c in self.pool if C.n_slashes(c) <= 2)
        res = [c for c in cands if self.successors(sigma, c)]
        self._comb_cache[key] = res
        return res
