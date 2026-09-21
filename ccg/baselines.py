"""Left-branching, right-branching and random-tree dependency baselines."""
from __future__ import annotations
import random
from typing import List


def left_branching(n: int) -> List[int]:
    """Each word depends on the word to its left; first word is root (head-initial chain)."""
    return [0] + [i for i in range(1, n)]


def right_branching(n: int) -> List[int]:
    """Each word depends on the word to its right; last word is root."""
    return [i + 2 for i in range(n - 1)] + [0]


def random_tree(n: int, rng: random.Random) -> List[int]:
    order = list(range(n))
    rng.shuffle(order)
    heads = [0] * n
    attached = [order[0]]
    for w in order[1:]:
        heads[w] = rng.choice(attached) + 1
        attached.append(w)
    return heads
