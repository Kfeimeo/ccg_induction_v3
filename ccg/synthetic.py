"""Synthetic validation (§7.3): a 20-word grammar, 500 generated sentences."""
from __future__ import annotations
import random
from typing import Dict, List, Tuple
from .category import parse as P, Cat

GOLD: Dict[str, List[str]] = {
    'john': ['NP'], 'mary': ['NP'], 'dogs': ['NP'], 'cats': ['NP'],
    'the': ['NP/N'], 'a': ['NP/N'],
    'dog': ['N'], 'cat': ['N'], 'man': ['N'],
    'sleeps': ['S\\NP'], 'runs': ['S\\NP'],
    'sees': ['(S\\NP)/NP'], 'likes': ['(S\\NP)/NP'],
    'big': ['N/N'], 'old': ['N/N'],
    'quickly': ['S\\S'], 'today': ['S\\S'],
    'with': ['(S\\S)/NP', '(NP\\NP)/NP'],
    'in': ['(S\\S)/NP'],
    'and': ['((S\\S)/(S\\NP))/NP'],   # clause coordination must take the second subject (no TR)
}
assert len(GOLD) == 20


def gold_lexicon() -> Dict[str, List[Cat]]:
    return {w: [P(c) for c in cs] for w, cs in GOLD.items()}


def _np(rng):
    r = rng.random()
    if r < 0.4:
        return [rng.choice(['john', 'mary', 'dogs', 'cats'])]
    out = [rng.choice(['the', 'a'])]
    while rng.random() < 0.3:
        out.append(rng.choice(['big', 'old']))
    out.append(rng.choice(['dog', 'cat', 'man']))
    return out


def _clause(rng, depth=0):
    s = _np(rng)
    if rng.random() < 0.5:
        s.append(rng.choice(['sleeps', 'runs']))
    else:
        s.append(rng.choice(['sees', 'likes']))
        s += _np(rng)
    r = rng.random()
    if r < 0.2:
        s.append(rng.choice(['quickly', 'today']))
    elif r < 0.4:
        s.append(rng.choice(['with', 'in']))
        s += _np(rng)
    return s


def generate(n: int = 500, seed: int = 0, max_len: int = 10) -> List[List[str]]:
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        s = _clause(rng)
        if rng.random() < 0.15:
            s = s + ['and'] + _clause(rng)
        if len(s) <= max_len:
            out.append(s)
    return out


def best_atom_mapping(pred: Dict[str, Cat], gold: Dict[str, List[Cat]], atoms=('N', 'NP')) -> Tuple[float, dict]:
    """Fraction of words whose predicted (majority) category equals a gold category, maximised
    over permutations of the non-S atoms."""
    import itertools
    from .category import rename_atoms
    best, bestmap = -1.0, None
    for perm in itertools.permutations(atoms):
        mp = dict(zip(atoms, perm))
        ok = 0
        for w, c in pred.items():
            if rename_atoms(c, mp) in gold.get(w, []):
                ok += 1
        acc = ok / len(gold)
        if acc > best:
            best, bestmap = acc, mp
    return best, bestmap


def derivation_recovery(sents: List[List[str]], learned_support, learned_model, gold_support, max_depth: int = 4) -> float:
    """Fraction of (raw functor->argument) dependencies of the learned Viterbi derivations that
    agree with the gold-lexicon derivations (unmapped heads), over sentences parsed by both."""
    from .lattice import build_lattice, viterbi
    from .deps import raw_heads
    from .experiment import UniformModel
    gm = UniformModel(gold_support)
    agree = total = 0
    for s in sents:
        lg = build_lattice(s, gold_support, max_depth)
        ll = build_lattice(s, learned_support, max_depth)
        if not (lg.accepted and ll.accepted):
            continue
        pg, _ = viterbi(lg, gm)
        pl, _ = viterbi(ll, learned_model)
        hg, hl = raw_heads(s, pg), raw_heads(s, pl)
        agree += sum(1 for a, b in zip(hg, hl) if a == b)
        total += len(s)
    return agree / total if total else 0.0
