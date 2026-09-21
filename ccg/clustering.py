"""Distributional word clustering (k-means on left/right neighbour PPMI vectors).

Used only to (a) tie parameters of rare words and (b) structure the random initialisation
(words in one cluster share cluster-level noise on their category prior).  No labels.
"""
from __future__ import annotations
import math
from typing import Dict, List, Tuple
import numpy as np


def context_vectors(sents: List[List[str]], n_context: int = 200):
    counts: Dict[str, int] = {}
    for s in sents:
        for w in s:
            counts[w] = counts.get(w, 0) + 1
    ctx_words = [w for w, _ in sorted(counts.items(), key=lambda x: -x[1])[:n_context]]
    ctx_idx = {w: i for i, w in enumerate(ctx_words)}
    D = 2 * (len(ctx_words) + 1)  # left ctx (+BOS), right ctx (+EOS)
    vocab = sorted(counts)
    vidx = {w: i for i, w in enumerate(vocab)}
    M = np.zeros((len(vocab), D))
    for s in sents:
        for i, w in enumerate(s):
            l = s[i - 1] if i > 0 else None
            r = s[i + 1] if i + 1 < len(s) else None
            li = ctx_idx.get(l, len(ctx_words)) if l is not None else len(ctx_words)
            ri = ctx_idx.get(r, len(ctx_words)) if r is not None else len(ctx_words)
            M[vidx[w], li] += 1
            M[vidx[w], len(ctx_words) + 1 + ri] += 1
    # PPMI
    tot = M.sum()
    rs = M.sum(1, keepdims=True); cs = M.sum(0, keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        pmi = np.log((M * tot) / (rs * cs))
    pmi[~np.isfinite(pmi)] = 0.0
    pmi = np.maximum(pmi, 0.0)
    norms = np.linalg.norm(pmi, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vocab, pmi / norms, counts


def kmeans(X: np.ndarray, k: int, seed: int, iters: int = 30, weights=None) -> np.ndarray:
    rng = np.random.RandomState(seed)
    n = X.shape[0]
    k = min(k, n)
    # k-means++ init
    centers = [X[rng.randint(n)]]
    for _ in range(1, k):
        d = np.min([((X - c) ** 2).sum(1) for c in centers], axis=0)
        p = d / d.sum() if d.sum() > 0 else np.ones(n) / n
        centers.append(X[rng.choice(n, p=p)])
    Cm = np.array(centers)
    lab = np.zeros(n, dtype=int)
    for _ in range(iters):
        d = ((X[:, None, :] - Cm[None, :, :]) ** 2).sum(2)
        new = d.argmin(1)
        if np.array_equal(new, lab) and _ > 0:
            break
        lab = new
        for j in range(k):
            m = lab == j
            if m.any():
                Cm[j] = X[m].mean(0)
    return lab


def cluster_words(sents: List[List[str]], k: int = 24, seed: int = 0, n_context: int = 200) -> Tuple[Dict[str, int], Dict[str, int]]:
    vocab, X, counts = context_vectors(sents, n_context)
    lab = kmeans(X, k, seed)
    return {w: int(lab[i]) for i, w in enumerate(vocab)}, counts
