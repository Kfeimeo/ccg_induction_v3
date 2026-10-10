"""Seed (anchored) lexicon entries: common words whose category is hand-fixed before induction.

An anchored word keeps exactly the listed categories throughout MDL training: it is never
pruned, never receives proposals, and merge/rename moves that would rewrite its categories
are skipped.  Everything else (its emission probability, the transition model) is still
learned.  Used by scripts/run_induction.py --anchors {none,the,closed,hw1}.

Sets
  the     the single word "the" -> NP/N (the original --anchored ablation)
  closed  closed-class words with one category in the hand-written lexicon:
          personal pronouns -> NP, articles/determiners/possessives -> NP/N,
          modals and clitic auxiliaries -> (S\\NP)/(S\\NP)
  hw1     every hand-written word (group-A atoms) with exactly one category and
          train count >= 5 (adds a few single-category verbs to `closed`)
  stNP    supertagger-derived (Hol-CCG, scripts/supertag_gum.py + build_supertag_seeds.py):
          words whose top-1 supertag reads as NP in >= 90% of their train occurrences -> NP
  stNPN   stNP plus the words whose top-1 supertag reads as N -> N
"""
from __future__ import annotations
import json, os
from typing import Dict, List

PRONOUNS = "i it we he they she me them us him you".split()
DETERMINERS = "the a an every each another my his your our their its".split()
MODALS = "can will 'll could would may wo ca should might must 'd 've na gon".split()

CLOSED: Dict[str, List[str]] = {}
CLOSED.update({w: ['NP'] for w in PRONOUNS})
CLOSED.update({w: ['NP/N'] for w in DETERMINERS})
CLOSED.update({w: ['(S\\NP)/(S\\NP)'] for w in MODALS})

SETS = {'none': {}, 'the': {'the': ['NP/N']}, 'closed': CLOSED}


def hw_single(word_counts: Dict[str, int], min_count: int = 5, max_words: int = 500) -> Dict[str, List[str]]:
    """Hand-written words (atoms renamed PP->NP) with exactly one category and count >= min_count."""
    from . import category as C
    from .handwritten import build
    hw = build('SA', word_counts, max_words)
    out = {}
    for w, cs in hw.items():
        cats = sorted({C.show(C.rename_atoms(c, {'PP': 'NP'})) for c in cs})
        if len(cats) == 1 and word_counts.get(w, 0) >= min_count:
            out[w] = cats
    return out


SUPERTAG_SEEDS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'supertags', 'seed_sets.json')


def supertag_set(name: str, path: str = SUPERTAG_SEEDS) -> Dict[str, List[str]]:
    """stNP / stNPN from data/supertags/seed_sets.json (scripts/build_supertag_seeds.py)."""
    return dict(json.load(open(path, encoding='utf-8'))['sets'][name])


def get(name: str, word_counts: Dict[str, int] = None) -> Dict[str, List[str]]:
    if name == 'hw1':
        return hw_single(word_counts or {})
    if name in ('stNP', 'stNPN'):
        return supertag_set(name)
    return dict(SETS[name])
