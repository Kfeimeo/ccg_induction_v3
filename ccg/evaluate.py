"""Metrics: UAS (excl. punct, which is already removed), coverage, perplexity, bracket F1."""
from __future__ import annotations
import math
from typing import Dict, List, Optional, Sequence, Tuple


def uas(pred_heads: Sequence[int], gold_heads: Sequence[int]) -> Tuple[int, int]:
    assert len(pred_heads) == len(gold_heads)
    return sum(1 for p, g in zip(pred_heads, gold_heads) if p == g), len(gold_heads)


def uas_core(pred_heads, gold_heads, core_idx: Sequence[int]) -> Tuple[int, int]:
    return sum(1 for i in core_idx if pred_heads[i] == gold_heads[i]), len(core_idx)


def yields(heads: Sequence[int]) -> set:
    """Constituent spans (i, j) inclusive, 0-based, of each head's projective yield; |span|>1."""
    n = len(heads)
    children = {i: [] for i in range(n)}
    for i, h in enumerate(heads):
        if h:
            children[h - 1].append(i)

    def span(i):
        lo, hi = i, i
        for c in children[i]:
            a, b = span(c)
            lo, hi = min(lo, a), max(hi, b)
        return lo, hi
    out = set()
    for i in range(n):
        s = span(i)
        if s[1] > s[0] and not (s[0] == 0 and s[1] == n - 1):
            out.add(s)
    return out


def bracket_prf(pred_spans: set, gold_spans: set) -> Tuple[int, int, int]:
    return len(pred_spans & gold_spans), len(pred_spans), len(gold_spans)


def left_comb_spans(n: int) -> set:
    return {(0, j) for j in range(1, n - 1)}


def summarize(results: List[dict]) -> dict:
    """Aggregate per-sentence dicts with keys: covered, uas_correct, uas_total, logprob, n."""
    cov = sum(1 for r in results if r['covered'])
    tot = len(results)
    corr = sum(r['uas_correct'] for r in results)
    toks = sum(r['uas_total'] for r in results)
    corr_c = sum(r['uas_correct'] for r in results if r['covered'])
    toks_c = sum(r['uas_total'] for r in results if r['covered'])
    lp = sum(r['logprob'] for r in results if r['covered'])
    nt = sum(r['n'] for r in results if r['covered'])
    return {
        'n_sent': tot,
        'coverage': cov / tot if tot else 0.0,
        'uas_all': corr / toks if toks else 0.0,           # uncovered sentences count as wrong
        'uas_covered': corr_c / toks_c if toks_c else 0.0,
        'ppl_per_word': math.exp(-lp / nt) if nt else float('inf'),  # over covered sentences
    }


def mean_std(xs: List[float]) -> Tuple[float, float]:
    if not xs:
        return float('nan'), float('nan')
    m = sum(xs) / len(xs)
    v = sum((x - m) ** 2 for x in xs) / len(xs)
    return m, math.sqrt(v)
