"""Phenomenon test sets (§4): positives are real corpus sentences selected by UD annotation
patterns, negatives are constructed minimal pairs.  Criteria per item:
  L1 positive accepted;  L2 negative rejected;  L3 the construction's core UD arcs recovered;
  L4 no construction-specific category used (hand-written: explicit list; induced: the key
  function word's category in this derivation is its majority category over the whole dev set).
"""
from __future__ import annotations
import random
from typing import Callable, Dict, List, Optional, Tuple
from .data import Sentence

EAT = {'eat', 'eats', 'ate', 'eating', 'eaten'}


def _children(s: Sentence, i: int) -> List[int]:
    return [j for j, h in enumerate(s.heads) if h == i + 1]


def _rel(s, i):
    return s.deprels[i]


# ------------------------------------------------------------------ detectors: return core arc indices or None
def det_argument_structure(s: Sentence):
    for i in range(s.n):
        if s.upos[i] == 'VERB' and s.heads[i] == 0:
            ch = _children(s, i)
            subj = [c for c in ch if _rel(s, c) == 'nsubj']
            obj = [c for c in ch if _rel(s, c) == 'obj']
            if subj and obj:
                return subj + obj
    return None


def det_modifiers(s: Sentence):
    core = [i for i in range(s.n) if _rel(s, i) in ('amod', 'advmod')]
    return core or None


def det_determiners(s: Sentence):
    core = [i for i in range(s.n) if _rel(s, i) == 'det']
    return core or None


def det_aux_sequence(s: Sentence):
    core = [i for i in range(s.n) if _rel(s, i) in ('aux', 'cop')]
    return core if len(core) >= 1 and any(s.upos[h - 1] in ('VERB', 'ADJ', 'NOUN') for h in [s.heads[i] for i in core] if h) else None


def det_vp_coordination(s: Sentence):
    for i in range(s.n):
        if _rel(s, i) == 'conj' and s.upos[i] == 'VERB':
            h = s.heads[i] - 1
            if s.upos[h] == 'VERB' and not any(_rel(s, c) == 'nsubj' for c in _children(s, i)):
                cc = [c for c in _children(s, i) if _rel(s, c) == 'cc']
                subj = [c for c in _children(s, h) if _rel(s, c) == 'nsubj']
                return [i] + cc + subj
    return None


def det_subject_relative(s: Sentence):
    for i in range(s.n):
        if _rel(s, i) == 'acl' and s.upos[i] == 'VERB':
            subj = [c for c in _children(s, i) if _rel(s, c) == 'nsubj' and s.words[c] in ('who', 'that', 'which')]
            if subj:
                return [i] + subj
    return None


def det_object_relative(s: Sentence):
    for i in range(s.n):
        if _rel(s, i) == 'acl' and s.upos[i] == 'VERB':
            ch = _children(s, i)
            rel = [c for c in ch if s.words[c] in ('who', 'that', 'which', 'whom') and _rel(s, c) == 'obj']
            subj = [c for c in ch if _rel(s, c) == 'nsubj']
            if subj and (rel or not any(_rel(s, c) == 'obj' for c in ch)) and s.heads[i] - 1 < i and subj[0] > s.heads[i] - 1:
                return [i] + subj + rel
    return None


def det_valency_eat(s: Sentence):
    for i in range(s.n):
        if s.words[i] in EAT and s.upos[i] == 'VERB':
            return [i] + [c for c in _children(s, i) if _rel(s, c) in ('obj', 'nsubj')]
    return None


def det_that(s: Sentence):
    core = [i for i in range(s.n) if s.words[i] == 'that']
    return core or None


def det_nested_clause(s: Sentence):
    for i in range(s.n):
        if _rel(s, i) in ('ccomp', 'xcomp', 'advcl') and s.upos[i] == 'VERB':
            subj = [c for c in _children(s, i) if _rel(s, c) == 'nsubj']
            return [i] + subj
    return None


def det_comparative(s: Sentence):
    core = [i for i in range(s.n) if s.words[i] == 'than']
    return core or None


PHENOMENA: Dict[str, Tuple[str, Callable, str]] = {
    # name: (group, detector, key-word role for L4)
    'argument_structure': ('gate', det_argument_structure, ''),
    'modifiers': ('gate', det_modifiers, ''),
    'determiners': ('gate', det_determiners, ''),
    'aux_sequence': ('gate', det_aux_sequence, ''),
    'vp_coordination': ('discriminating', det_vp_coordination, 'cc'),
    'right_node_raising': ('discriminating', None, 'cc'),
    'nonconstituent_coordination': ('discriminating', None, 'cc'),
    'subject_relative': ('discriminating', det_subject_relative, 'rel'),
    'object_relative': ('discriminating', det_object_relative, 'rel'),
    'valency_eat': ('discriminating', det_valency_eat, ''),
    'multifunction_that': ('discriminating', det_that, 'that'),
    'nested_clause': ('discriminating', det_nested_clause, 'comp'),
    'parasitic_gap': ('stretch', None, ''),
    'gapping': ('stretch', None, 'cc'),
    'comparative': ('stretch', det_comparative, 'than'),
}

# constructed items for phenomena that are (nearly) absent from short corpus sentences
CONSTRUCTED: Dict[str, List[Tuple[str, str, List[int]]]] = {
    # (positive, negative, gold heads of positive (1-based, 0=root))
    'right_node_raising': [
        ('john likes and mary hates the movie', 'john likes and mary the movie hates', [2, 0, 2, 5, 2, 7, 5]),
        ('we bought and they sold the house', 'we bought and they the house sold', [2, 0, 2, 5, 2, 7, 5]),
        ('i wrote and she read the letter', 'i wrote and she the letter read', [2, 0, 2, 5, 2, 7, 5]),
        ('he cooked and we ate the dinner', 'he cooked and we the dinner ate', [2, 0, 2, 5, 2, 7, 5]),
        ('you found and i lost the keys', 'you found and i the keys lost', [2, 0, 2, 5, 2, 7, 5]),
    ],
    'nonconstituent_coordination': [
        ('i gave john a book and mary a pen', 'i gave john a book and a pen mary', [2, 0, 2, 5, 2, 8, 8, 5, 8]),
        ('she sent tom a letter and ann a card', 'she sent tom a letter and a card ann', [2, 0, 2, 5, 2, 8, 8, 5, 8]),
        ('we told him a story and her a joke', 'we told him a story and a joke her', [2, 0, 2, 5, 2, 8, 8, 5, 8]),
        ('he showed me a house and you a car', 'he showed me a house and a car you', [2, 0, 2, 5, 2, 8, 8, 5, 8]),
        ('they gave us a room and them a bed', 'they gave us a room and a bed them', [2, 0, 2, 5, 2, 8, 8, 5, 8]),
    ],
    'parasitic_gap': [
        ('the book i read without buying was good', 'the book i read without buying good was', [2, 7, 4, 2, 6, 4, 0, 7]),
        ('the paper she filed without reading was long', 'the paper she filed without reading long was', [2, 7, 4, 2, 6, 4, 0, 7]),
        ('the cake he ate without cutting was small', 'the cake he ate without cutting small was', [2, 7, 4, 2, 6, 4, 0, 7]),
    ],
    'gapping': [
        ('john likes tea and mary coffee', 'john likes tea and coffee mary', [2, 0, 2, 5, 2, 5]),
        ('i drink water and she juice', 'i drink water and juice she', [2, 0, 2, 5, 2, 5]),
        ('we play chess and they cards', 'we play chess and cards they', [2, 0, 2, 5, 2, 5]),
        ('he reads books and she magazines', 'he reads books and magazines she', [2, 0, 2, 5, 2, 5]),
        ('you eat rice and i bread', 'you eat rice and bread i', [2, 0, 2, 5, 2, 5]),
    ],
    'comparative': [
        ('john is taller than mary', 'john is than taller mary', [3, 3, 0, 5, 3]),
        ('this book is better than that one', 'this book is than better that one', [2, 4, 4, 0, 7, 7, 4]),
        ('she runs faster than he does', 'she runs than faster he does', [2, 0, 2, 6, 6, 3]),
        ('the cat is bigger than the dog', 'the cat is than bigger the dog', [2, 4, 4, 0, 7, 7, 4]),
        ('i have more books than you', 'i have books more than you', [2, 0, 4, 2, 6, 4]),
    ],
}


# ------------------------------------------------------------------ negative construction
def make_negative(s: Sentence, name: str, rng: random.Random) -> Optional[List[str]]:
    """Minimal-pair negative: the construction-relevant transformation, else a generic one."""
    w = list(s.words)
    n = s.n
    if name == 'determiners' or (name in ('argument_structure', 'modifiers') and 'det' in s.deprels):
        i = s.deprels.index('det')
        h = s.heads[i] - 1
        if h == i + 1:                      # "the dog" -> "dog the"
            w[i], w[h] = w[h], w[i]
            return w
    if name == 'aux_sequence':
        i = [k for k in range(n) if s.deprels[k] in ('aux', 'cop')][0]
        h = s.heads[i] - 1
        if h > i:                           # move aux after its head: "is running" -> "running is"
            w.insert(h + 1, w.pop(i))
            return w
    if name in ('argument_structure', 'valency_eat', 'nested_clause', 'vp_coordination', 'subject_relative', 'object_relative', 'multifunction_that'):
        # verb-final scramble of the innermost verb with an object: "loves mary" -> "mary loves"
        for i in range(n):
            if s.upos[i] == 'VERB':
                objs = [c for c in _children(s, i) if s.deprels[c] == 'obj' and c == i + 1]
                if objs:
                    w[i], w[i + 1] = w[i + 1], w[i]
                    return w
        for i in range(n):
            if s.deprels[i] == 'nsubj' and s.heads[i] - 1 == i + 1 and i + 2 < n:
                w.insert(i + 2, w.pop(i))   # "john loves mary" -> "loves john mary" (subject after verb)
                return w
    if name == 'modifiers':
        for i in range(n):
            if s.deprels[i] == 'amod' and s.heads[i] - 1 == i + 1:
                w[i], w[i + 1] = w[i + 1], w[i]   # "big dog" -> "dog big"
                return w
    # generic: duplicate the first function word
    for i in range(n):
        if s.upos[i] in ('DET', 'ADP', 'AUX'):
            return w[:i + 1] + [w[i]] + w[i + 1:]
    return None


def build_sets(dev: List[Sentence], train: List[Sentence], min_pos: int = 20, seed: int = 0) -> Dict[str, dict]:
    rng = random.Random(seed)
    sets = {}
    for name, (group, det, role) in PHENOMENA.items():
        items = []
        if det is not None:
            for src, sents in (('dev', dev), ('train', train)):
                for s in sents:
                    if len(items) >= min_pos and src == 'train':
                        break
                    core = det(s)
                    if core is None:
                        continue
                    neg = make_negative(s, name, rng)
                    if neg is None or neg == s.words:
                        continue
                    items.append({'pos': s.words, 'neg': neg, 'gold_heads': s.heads, 'core': core, 'source': src, 'sid': s.sid})
                if len(items) >= min_pos:
                    break
        for pos, neg, heads in CONSTRUCTED.get(name, []):
            pw = pos.split()
            items.append({'pos': pw, 'neg': neg.split(), 'gold_heads': heads, 'core': list(range(len(pw))), 'source': 'constructed', 'sid': ''})
        sets[name] = {'group': group, 'role': role, 'items': items,
                      'n_dev': sum(1 for it in items if it['source'] == 'dev'),
                      'n_train': sum(1 for it in items if it['source'] == 'train'),
                      'n_constructed': sum(1 for it in items if it['source'] == 'constructed')}
    return sets


KEY_WORDS = {'cc': {'and', 'or', 'but'}, 'rel': {'who', 'that', 'which', 'whom'}, 'that': {'that'},
             'comp': set(), 'than': {'than'}}


def evaluate_sets(sets: Dict[str, dict], parse_fn, majority_cat: Optional[Dict[str, object]] = None,
                  construction_specific: Optional[set] = None) -> Dict[str, dict]:
    """parse_fn(words) -> (accepted: bool, heads: list or None, cats: list or None).
    Returns per-phenomenon L1..L4 rates and pairwise accuracy."""
    out = {}
    for name, d in sets.items():
        n = len(d['items'])
        l1 = l2 = l3 = l4 = pair = 0
        n_in = l1_in = l3_in = pair_in = 0
        for it in d['items']:
            acc_p, heads, cats = parse_fn(it['pos'])
            acc_n, _, _ = parse_fn(it['neg'])
            in_lex = heads is not None or (acc_p is False and getattr(parse_fn, 'last_in_lex', True))
            ok1 = bool(acc_p); ok2 = not acc_n
            ok3 = ok1 and heads is not None and all(heads[i] == it['gold_heads'][i] for i in it['core'])
            ok4 = True
            if ok1 and cats is not None:
                if construction_specific is not None:
                    ok4 = not any(c in construction_specific for c in cats)
                elif majority_cat is not None and d['role']:
                    keys = KEY_WORDS.get(d['role'], set())
                    for w, c in zip(it['pos'], cats):
                        if w in keys and w in majority_cat and majority_cat[w] != c:
                            ok4 = False
            l1 += ok1; l2 += ok2; l3 += ok3; l4 += (ok1 and ok4); pair += (ok1 and ok2)
            if in_lex:
                n_in += 1; l1_in += ok1; l3_in += ok3; pair_in += (ok1 and ok2)
        out[name] = {'group': d['group'], 'n': n, 'n_dev': d['n_dev'], 'n_train': d['n_train'], 'n_constructed': d['n_constructed'],
                     'L1_accept': l1 / n if n else None, 'L2_reject_neg': l2 / n if n else None,
                     'L3_pred_arg': l3 / n if n else None, 'L4_no_cs': l4 / n if n else None,
                     'pair_acc': pair / n if n else None,
                     'n_in_lex': n_in, 'L1_in_lex': l1_in / n_in if n_in else None, 'L3_in_lex': l3_in / n_in if n_in else None,
                     'pair_acc_in_lex': pair_in / n_in if n_in else None}
    return out
