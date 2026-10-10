"""Stack (Lambek-product) variant of the incremental parser.

State = stack of categories (a Lambek product A•B•…, bottom first).  Reading word category c:
  * if the stack top combines with c under the fixed rules (FA/BA/B>/B</SA), the rule MUST apply
    (no push/reduce choice); the result replaces the top and, with cascade=True, is then reduced
    with the item below it for as long as a rule applies (top-of-stack first).  In cascaded
    reductions the right item is a derived constituent, so SA (lexical functor only) is not
    available there;
  * otherwise c is pushed (product formation), subject to the stack bound max_stack.
Acceptance: the final stack is exactly [goal].  Edge.rule is a tuple of steps: ('PUSH',) or
(rule, cascade_rule, ...).  The strict left-branching system is the special case max_stack = 1.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from . import category as C
from .combine import combine, _combine_cached, RULES_ON
from .lattice import Lattice, Edge, GOAL


class Stack(tuple):
    """Tuple subclass so that stack states are distinguishable from category tuples."""
    __slots__ = ()

    def __repr__(self):
        return '[' + ' '.join(C.show(c) for c in self) + ']'


def step(stack: Optional[Stack], c: C.Cat, max_depth: int = 4, max_stack: int = 3,
         cascade: bool = True) -> List[Tuple[Stack, tuple]]:
    """All successor stacks of `stack` on word category c, with the rule-step tuple."""
    if stack is None or len(stack) == 0:
        return [(Stack((c,)), ('PUSH',))]
    top = stack[-1]
    res = combine(top, c, max_depth)
    if not res:
        if len(stack) >= max_stack:
            return []
        return [(Stack(stack + (c,)), ('PUSH',))]
    out: List[Tuple[Stack, tuple]] = []
    for r, rule in res:
        base = Stack(stack[:-1] + (r,))
        if cascade:
            out.extend(_cascade(base, (rule,), max_depth))
        else:
            out.append((base, (rule,)))
    # deduplicate by resulting stack
    seen, dedup = set(), []
    for st, rules in out:
        if st not in seen:
            seen.add(st)
            dedup.append((st, rules))
    return dedup


def _cascade(stack: Stack, rules: tuple, max_depth: int) -> List[Tuple[Stack, tuple]]:
    if len(stack) < 2:
        return [(stack, rules)]
    below, top = stack[-2], stack[-1]
    res = _combine_cached(below, top, max_depth, False)   # SA off: the right item is derived
    if not res:
        return [(stack, rules)]
    out = []
    for r, rule in res:
        out.extend(_cascade(Stack(stack[:-2] + (r,)), rules + (rule,), max_depth))
    return out


def build_stack_lattice(words: List[str], support: Dict[str, List[C.Cat]], max_depth: int = 4,
                        goal: C.Cat = GOAL, max_stack: int = 3, cascade: bool = True, beam: int = 0) -> Lattice:
    n = len(words)
    layers: List[Dict[Stack, List[Edge]]] = []
    prev_states: List[Optional[Stack]] = [None]
    unpruned, branch = [], []
    fail_pos = -1
    for k, w in enumerate(words):
        layer: Dict[Stack, List[Edge]] = {}
        cands = support.get(w, [])
        for s in prev_states:
            for c in cands:
                succ = step(s, c, max_depth, max_stack, cascade)
                branch.append(len(succ))
                if not succ:
                    continue
                wt = 1.0 / len(succ)
                for st, rules in succ:
                    layer.setdefault(st, []).append(Edge(s, c, st, rules, wt))
        unpruned.append(len(layer))
        layers.append(layer)
        if not layer:
            fail_pos = k + 1
            break
        prev_states = list(layer.keys())
    lat = Lattice(words, layers, accepted=False, unpruned_sizes=unpruned, branch_counts=branch)
    goal_state = Stack((goal,))
    if fail_pos != -1:
        lat.fail_pos = fail_pos
        lat.fail_states = tuple(layers[fail_pos - 2].keys()) if fail_pos >= 2 else ()
        return lat
    if goal_state not in layers[-1]:
        lat.fail_pos = n + 1
        lat.fail_states = tuple(layers[-1].keys())
        return lat
    alive = {goal_state}
    for k in range(n - 1, -1, -1):
        layer = layers[k]
        new_layer: Dict[Stack, List[Edge]] = {}
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


def make_builder(max_stack: int = 3, cascade: bool = True):
    def build(words, support, max_depth=4, goal=GOAL, beam=0):
        return build_stack_lattice(words, support, max_depth, goal, max_stack, cascade, beam)
    return build


def goal_state(goal: C.Cat = GOAL) -> Stack:
    return Stack((goal,))
