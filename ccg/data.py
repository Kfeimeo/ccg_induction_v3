"""CoNLL-U reading and preprocessing.

Training uses word forms only.  Gold heads/deprels are kept alongside for evaluation
(never used in training).  Punctuation is removed and heads re-indexed; a token whose
head is punctuation is re-attached to the punctuation's head.
"""
from __future__ import annotations
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional


@dataclass
class Sentence:
    sid: str
    words: List[str]            # surface forms after preprocessing (lowercased if configured)
    orig: List[str]             # original forms
    upos: List[str]
    heads: List[int]            # 1-based, 0 = root, re-indexed after punct removal
    deprels: List[str]
    s_type: str = ''
    text: str = ''

    @property
    def n(self):
        return len(self.words)

    def to_json(self):
        return json.dumps(asdict(self), ensure_ascii=False)

    @staticmethod
    def from_json(s):
        return Sentence(**json.loads(s))


def read_conllu(path: str) -> List[dict]:
    sents, cur, meta = [], [], {}
    with open(path, encoding='utf8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('#'):
                if '=' in line:
                    k, v = line[1:].split('=', 1)
                    meta[k.strip()] = v.strip()
                continue
            if not line:
                if cur:
                    sents.append({'meta': meta, 'toks': cur})
                cur, meta = [], {}
                continue
            f_ = line.split('\t')
            if '-' in f_[0] or '.' in f_[0]:
                continue  # multiword token ranges / empty nodes
            cur.append(f_)
    if cur:
        sents.append({'meta': meta, 'toks': cur})
    return sents


def _is_punct(tok) -> bool:
    return tok[3] == 'PUNCT' or tok[7] == 'punct'


def preprocess(raw: dict, lowercase: bool = True) -> Optional[Sentence]:
    toks = raw['toks']
    keep = [t for t in toks if not _is_punct(t)]
    if not keep:
        return None
    old2new: Dict[int, int] = {int(t[0]): i + 1 for i, t in enumerate(keep)}
    head_of = {int(t[0]): int(t[6]) for t in toks}
    heads, deprels = [], []
    for t in keep:
        h = int(t[6])
        # re-attach through punctuation heads
        guard = 0
        while h != 0 and h not in old2new and guard < 50:
            h = head_of[h]
            guard += 1
        heads.append(old2new.get(h, 0) if h != 0 else 0)
        deprels.append(t[7].split(':')[0])
    words = [t[1].lower() if lowercase else t[1] for t in keep]
    meta = raw['meta']
    return Sentence(sid=meta.get('sent_id', ''), words=words, orig=[t[1] for t in keep],
                    upos=[t[3] for t in keep], heads=heads, deprels=deprels,
                    s_type=meta.get('s_type', ''), text=meta.get('text', ''))


def load_split(path: str, max_len: int = 10, lowercase: bool = True,
               s_types: Optional[List[str]] = None, min_len: int = 1) -> List[Sentence]:
    out = []
    for raw in read_conllu(path):
        s = preprocess(raw, lowercase)
        if s is None or not (min_len <= s.n <= max_len):
            continue
        if s_types and s.s_type not in s_types:
            continue
        # EWT has no s_type: crude filter for titles/fragments -> require a verb
        if not s.s_type and not any(u in ('VERB', 'AUX') for u in s.upos):
            continue
        out.append(s)
    return out


def save_jsonl(sents: List[Sentence], path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf8') as f:
        for s in sents:
            f.write(s.to_json() + '\n')


def load_jsonl(path: str) -> List[Sentence]:
    with open(path, encoding='utf8') as f:
        return [Sentence.from_json(l) for l in f if l.strip()]


def word_counts(sents: List[Sentence]) -> Dict[str, int]:
    c: Dict[str, int] = {}
    for s in sents:
        for w in s.words:
            c[w] = c.get(w, 0) + 1
    return c
