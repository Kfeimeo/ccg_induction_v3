"""Dependency extraction from left-branching derivations, with UD-style head mapping.

Every rule application records one event (functor word f, slot index i on f's *lexical*
spine, argument head a).  Slot ownership is tracked through composition, so the Z slot of
X/Z obtained by B> from X/Y + Y/Z belongs to the word that supplied Y/Z.

Head mapping policy (configurable through HeadMap; this is the "mapping module" of §4).
Slot kinds for slot i of the lexical category of word f:

  cc-left / cc-right : f in the coordination list with shape (X\\X)/X.  The left conjunct is
                       the phrase head, the right conjunct attaches to it (conj), the
                       conjunction attaches to the right conjunct (cc).
  poss               : f is a possessive clitic with shape (NP/N)\\NP: the clitic attaches to the
                       possessor, the possessor attaches to the possessed noun (nmod:poss + case).
  marked             : f is a function word and i is its head-child slot:
                         DET/CASE words: outermost forward slot with an N/NP-targeting argument,
                           unless the category is verb-like (target S with \\NP as innermost slot);
                         AUX/MARK words: outermost forward slot whose argument targets S;
                         COP words: as AUX, else the outermost forward slot.
                       f attaches to the argument's phrase head; other arguments of f attach
                       to that head as well (content-word-head convention: det, case, aux, cop, mark).
  modifier           : argument category == result category at that level (X|X), or the
                       argument and the functor both target S and the functor has no subject
                       slot (e.g. (S/(S\\NP))/NP for a pre-subject adverb / interjection).  The
                       argument's phrase head becomes the head; the functor's phrase attaches to it.
  normal             : the argument's phrase head attaches to f's phrase head.  If an inner
                       slot j < i takes a clausal argument and f is not an object-control verb,
                       an NP in slot i is a raised subject and attaches to that clause's head.

Phrase head PH(f) = PH(modifier child) if any, else PH(marked child) if any, else f.
The root is PH(head word of the final state).
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from . import category as C

DET = set('the a an this that these those my your his her its our their some any no every each all both another such which what'.split())
AUX = set("am is are was were be been being 's 're 'm ’s have has had having 've 'd do does did will would can could shall should may might must 'll ca wo ai to na gon wan".split())
COP = set("am is are was were be been being 's 're 'm ’s".split())
CASE = set("in on at to for of with by from about into over after before under between through during without against among around as like than up out off down near since until across behind toward towards upon via per within along despite except beyond onto inside outside 's ’s".split())
MARK = set('that if because while when although since before after whether so until unless though once as for to whereas who which whom whose where why how'.split())
CC = set('and or but nor yet'.split())
POSS_CLITICS = {"'s", '’s', "'"}
CONTROL = set('want wanted wants try tried tries seem seemed seems start started starts stop stopped keep kept begin began hope hoped like liked love loved need needed have has had got get going gon wan plan planned decide decided used continue continued tend tended appear appeared happen happened manage managed fail failed'.split())
OBJ_CONTROL = set('let make made makes help helps helped see saw sees hear heard want wanted wants need needed needs have has had get got gets watch watched ask asked keep kept find found'.split())
FUNCTION_WORDS = DET | AUX | COP | CASE | MARK


def _targets_S(c: C.Cat) -> bool:
    return C.spine(c)[0].startswith('S')


def _targets_N(c: C.Cat) -> bool:
    t = C.spine(c)[0]
    return t == 'N' or t == 'NP'


class HeadMap:
    """Configurable head-flip policy (all flags on = UD content-word heads)."""

    def __init__(self, flip_function_words=True, flip_modifiers=True, flip_cc=True,
                 raised_subjects=True, det=DET, aux=AUX, cop=COP, case=CASE, mark=MARK, cc=CC,
                 obj_control=OBJ_CONTROL, control=CONTROL):
        self.flip_function_words = flip_function_words
        self.flip_modifiers = flip_modifiers
        self.flip_cc = flip_cc
        self.raised_subjects = raised_subjects
        self.det, self.aux, self.cop, self.case, self.mark, self.cc = det, aux, cop, case, mark, cc
        self.obj_control = obj_control
        self.control = control

    def is_function_word(self, w):
        return w in self.det or w in self.aux or w in self.cop or w in self.case or w in self.mark

    @staticmethod
    def raised_slots(cat: C.Cat) -> Dict[int, int]:
        """{raised NP slot i: clausal slot j}: the first forward N/NP slot outside a slot whose
        argument is a subject-less clause (S\\NP...), e.g. the /NP of (S/(S\\NP))/NP."""
        target, slots = C.spine(cat)
        out = {}
        for j, (sl, a) in enumerate(slots):
            if _targets_S(a) and not C.is_atom(a):
                at, aslots = C.spine(a)
                if aslots and aslots[0][0] == C.BWD and _targets_N(aslots[0][1]):
                    for i in range(j + 1, len(slots)):
                        if slots[i][0] == C.FWD and _targets_N(slots[i][1]) and i not in out:
                            out[i] = j
                            break
        return out

    def marked_slot(self, word: str, cat: C.Cat) -> int:
        target, slots = C.spine(cat)
        if not slots or not self.flip_function_words:
            return -1
        verb_like = target.startswith('S') and slots[0][0] == C.BWD and _targets_N(slots[0][1])
        raised = self.raised_slots(cat) if self.raised_subjects else {}
        if (word in self.det or word in self.case) and not verb_like:
            if word in self.det:
                for i in range(len(slots) - 1, -1, -1):
                    if slots[i][0] == C.FWD and slots[i][1] == 'N':
                        return i
            for i in range(len(slots) - 1, -1, -1):
                if slots[i][0] == C.FWD and _targets_N(slots[i][1]) and i not in raised:
                    return i
        if word in self.aux or word in self.mark or word in self.cop:
            for i in range(len(slots) - 1, -1, -1):
                if slots[i][0] == C.FWD and _targets_S(slots[i][1]):
                    return i
        if word in self.cop:
            for i in range(len(slots) - 1, -1, -1):
                if slots[i][0] == C.FWD:
                    return i
        return -1

    def slot_kind(self, word: str, cat: C.Cat, i: int) -> str:
        target, slots = C.spine(cat)
        sl, a = slots[i]
        if self.flip_cc and word in self.cc and len(slots) == 2 and slots[0][0] == C.BWD and \
                slots[1][0] == C.FWD and slots[0][1] == slots[1][1] == target:
            return 'cc-left' if i == 0 else 'cc-right'
        if self.flip_function_words and word in POSS_CLITICS and len(slots) == 2 and \
                slots[0] == (C.FWD, 'N') and slots[1][0] == C.BWD and target == 'NP':
            return 'poss-head' if i == 0 else 'poss'
        if self.flip_function_words and self.is_function_word(word) and i == self.marked_slot(word, cat):
            return 'marked'
        if self.flip_modifiers:
            verb_like = target.startswith('S') and slots[0][0] == C.BWD and _targets_N(slots[0][1])
            if C.build(target, slots[:i]) == a:
                # X|X: a modifier, except complements of verb-like categories
                # ((S\NP)/(S\NP))/NP: inner X|X slot is a complement; (S\NP)/(S\NP): control verb
                if verb_like and (len(slots) >= 3 or word in self.control):
                    return 'normal'
                return 'modifier'
            if target.startswith('S') and _targets_S(a) and not verb_like:
                return 'modifier'
        return 'normal'


DEFAULT_HEADMAP = HeadMap()


def replay(words: List[str], path, headmap: HeadMap = DEFAULT_HEADMAP) -> Tuple[List[int], List[Tuple[int, int, int]]]:
    """Given a Viterbi path [(prev_state, cat, next_state, rule)], return (heads, events).

    heads: 1-based head per word (0 = root).  events: (f, slot, a) with 0-based word indices.
    """
    from .combine import sa_matches
    n = len(words)
    lexcat = [p[1] for p in path]
    head = None
    owners: Tuple[Tuple[int, int], ...] = ()
    events: List[Tuple[int, int, int]] = []
    for k, (prev, c, nxt, rule) in enumerate(path):
        ar = C.arity(c)
        if rule == 'LEX':
            head, owners = k, tuple((k, i) for i in range(ar))
        elif rule == 'FA':
            f, i = owners[-1]
            events.append((f, i, k))
            owners = owners[:-1]
        elif rule == 'BA':
            events.append((k, ar - 1, head))
            head, owners = k, tuple((k, i) for i in range(ar - 1))
        elif rule == 'B>':
            f, i = owners[-1]
            events.append((f, i, k))
            owners = owners[:-1] + ((k, ar - 1),)
        elif rule == 'B<':
            events.append((k, ar - 1, head))
            head = k
            owners = tuple((k, i) for i in range(ar - 1)) + (owners[-1],)
        elif rule == 'SA':
            _, slots = C.spine(c)
            m = [j for j in sa_matches(prev, c) if j < len(slots) - 1]
            j = m[-1]
            events.append((k, j, head))
            head = k
            owners = tuple((k, i) for i in range(ar) if i != j)
        else:
            raise ValueError(rule)
    heads = resolve_heads(words, lexcat, events, head, headmap)
    return heads, events


def resolve_heads(words, lexcat, events, final_head, headmap: HeadMap) -> List[int]:
    n = len(words)
    kinds: Dict[Tuple[int, int], str] = {}
    marked_child: Dict[int, int] = {}
    modifier_child: Dict[int, int] = {}
    filled: Dict[Tuple[int, int], int] = {}
    for (f, i, a) in events:
        kind = headmap.slot_kind(words[f], lexcat[f], i)
        kinds[(f, i)] = kind
        filled[(f, i)] = a
        if kind in ('marked', 'cc-left', 'poss-head'):
            marked_child[f] = a
        elif kind == 'modifier':
            modifier_child[f] = a

    def PH(x: int) -> int:
        seen = set()
        while x not in seen:
            seen.add(x)
            if x in modifier_child:
                x = modifier_child[x]
            elif x in marked_child:
                x = marked_child[x]
            else:
                break
        return x

    def PHx(x: int) -> int:  # head of x's phrase, excluding x's own modifier child
        return PH(marked_child[x]) if x in marked_child else x

    heads = [0] * n
    for (f, i, a) in events:
        kind = kinds[(f, i)]
        if kind == 'marked':
            heads[f] = PH(a) + 1
        elif kind == 'cc-left':
            pass
        elif kind == 'cc-right':
            left = marked_child.get(f, f)
            heads[PH(a)] = PH(left) + 1
            heads[f] = PH(a) + 1
        elif kind == 'poss-head':
            pass
        elif kind == 'poss':
            heads[f] = PH(a) + 1
            heads[PH(a)] = PHx(f) + 1
        elif kind == 'modifier':
            heads[PHx(f)] = PH(a) + 1
        else:
            target = PHx(f)
            if headmap.raised_subjects and words[f] not in headmap.obj_control:
                raised = headmap.raised_slots(lexcat[f])
                j = raised.get(i)
                if j is not None and (f, j) in filled:
                    target = PH(filled[(f, j)])
            heads[PH(a)] = target + 1
    root = PH(final_head)
    heads[root] = 0
    return heads


def raw_heads(words: List[str], path) -> List[int]:
    """Functor -> argument dependencies without any head mapping (reference)."""
    hm = HeadMap(flip_function_words=False, flip_modifiers=False, flip_cc=False, raised_subjects=False)
    return replay(words, path, hm)[0]
