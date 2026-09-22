"""Shared evaluation driver: parse sentences with a lexicon, read dependencies, score."""
from __future__ import annotations
import collections
import random
from typing import Dict, List, Optional
from . import category as C
from .combine import STATS, reset_stats, sa_matches
from .lattice import build_lattice, viterbi, failure_record, lattice_stats, forward_backward
from .deps import replay, HeadMap, DEFAULT_HEADMAP
from .evaluate import uas, summarize, yields, bracket_prf, left_comb_spans
from .baselines import left_branching, right_branching, random_tree
from .data import Sentence


class UniformModel:
    """Conditional model with P(c|w) uniform over the support (hand-written lexicon evaluation)."""
    kind = 'conditional'

    def __init__(self, support):
        self.theta = {w: {c: 1.0 / len(cs) for c in cs} for w, cs in support.items()}

    def w(self, prev, c, word):
        return self.theta.get(word, {}).get(c, 0.0)

    def final_weight(self):
        return 1.0


def evaluate_lexicon(sents: List[Sentence], support: Dict[str, List[C.Cat]],
                     model=None, max_depth: int = 4, headmap: HeadMap = DEFAULT_HEADMAP,
                     construction_specific: Optional[set] = None, goal='S') -> dict:
    model = model or UniformModel(support)
    per_sent, failures, oov_sents = [], [], 0
    sa_applied = sa_ambig = 0
    stats_acc = collections.defaultdict(float)
    n_lat = 0
    derivations = {}
    for s in sents:
        rec = {'sid': s.sid, 'n': s.n, 'covered': False, 'uas_correct': 0, 'uas_total': s.n,
               'logprob': 0.0, 'oov': False, 'in_lex': all(w in support for w in s.words)}
        if not rec['in_lex']:
            rec['oov'] = True
            oov_sents += 1
            per_sent.append(rec)
            continue
        lat = build_lattice(s.words, support, max_depth, goal)
        st = lattice_stats(lat)
        for k, v in st.items():
            stats_acc[k] += v
        n_lat += 1
        if not lat.accepted:
            fr = failure_record(lat, support)
            k = fr['fail_pos']
            if k <= s.n:
                fr['upos'] = s.upos[k - 1]
                fr['deprel'] = s.deprels[k - 1]
                fr['head_word'] = s.words[s.heads[k - 1] - 1] if s.heads[k - 1] else '<root>'
            else:
                fr['upos'] = 'END'
                fr['deprel'] = 'END'
            failures.append(fr)
            per_sent.append(rec)
            continue
        Z, _, _ = forward_backward(lat, model, goal)
        path, p = viterbi(lat, model, goal)
        import math
        rec['covered'] = True
        rec['logprob'] = math.log(Z) if Z > 0 else 0.0
        heads, events = replay(s.words, path, headmap)
        c_, t_ = uas(heads, s.heads)
        rec['uas_correct'], rec['uas_total'] = c_, t_
        rec['pred_heads'] = heads
        rec['cats'] = [C.show(e[1]) for e in path]
        rec['rules'] = [e[3] for e in path]
        for prev, c, nxt, rule in path:
            if rule == 'SA':
                sa_applied += 1
                if len(sa_matches(prev, c)) > 1:
                    sa_ambig += 1
        if construction_specific is not None:
            rec['uses_cs'] = any(e[1] in construction_specific for e in path)
        # bracket F1 (appendix): left comb vs gold yields
        g = yields(s.heads)
        m, np_, ng = bracket_prf(left_comb_spans(s.n), g)
        rec['br'] = (m, np_, ng)
        derivations[s.sid] = path
        per_sent.append(rec)
    summ = summarize(per_sent)
    inlex = [r for r in per_sent if r['in_lex']]
    summ_inlex = summarize(inlex) if inlex else {}
    summ['n_oov_sent'] = oov_sents
    summ['coverage_in_lex'] = summ_inlex.get('coverage', 0.0)
    summ['uas_all_in_lex'] = summ_inlex.get('uas_all', 0.0)
    summ['n_in_lex'] = len(inlex)
    summ['sa_applied'] = sa_applied
    summ['sa_ambiguous'] = sa_ambig
    summ['sa_ambiguous_rate'] = sa_ambig / sa_applied if sa_applied else 0.0
    for k in list(stats_acc):
        summ['lat_' + k] = stats_acc[k] / n_lat if n_lat else 0.0
    br = [r['br'] for r in per_sent if r.get('br')]
    if br:
        m = sum(b[0] for b in br); npred = sum(b[1] for b in br); ngold = sum(b[2] for b in br)
        pr = m / npred if npred else 0.0; rc = m / ngold if ngold else 0.0
        summ['bracket_f1'] = 2 * pr * rc / (pr + rc) if pr + rc else 0.0
    # baselines on the same sentences (all sentences; also restricted to covered)
    summ['baselines'] = baselines(sents, [r['covered'] for r in per_sent])
    return {'summary': summ, 'per_sent': per_sent, 'failures': failures, 'derivations': derivations}


def baselines(sents: List[Sentence], covered_mask: List[bool], seeds=(1, 2, 3, 4, 5)) -> dict:
    out = {}
    for name, fn in (('left_branching', left_branching), ('right_branching', right_branching)):
        c = t = cc = tc = 0
        for s, cov in zip(sents, covered_mask):
            a, b = uas(fn(s.n), s.heads)
            c += a; t += b
            if cov:
                cc += a; tc += b
        out[name] = {'uas_all': c / t if t else 0, 'uas_covered_subset': cc / tc if tc else 0}
    vals, valsc = [], []
    for seed in seeds:
        rng = random.Random(seed)
        c = t = cc = tc = 0
        for s, cov in zip(sents, covered_mask):
            a, b = uas(random_tree(s.n, rng), s.heads)
            c += a; t += b
            if cov:
                cc += a; tc += b
        vals.append(c / t if t else 0); valsc.append(cc / tc if tc else 0)
    from .evaluate import mean_std
    m, sd = mean_std(vals); mc, sdc = mean_std(valsc)
    out['random_tree'] = {'uas_all': m, 'uas_all_std': sd, 'uas_covered_subset': mc, 'uas_covered_subset_std': sdc}
    return out


def failure_clusters(failures: List[dict]) -> dict:
    by_word = collections.Counter(f['word'] for f in failures)
    by_upos_rel = collections.Counter((f.get('upos', '?'), f.get('deprel', '?')) for f in failures)
    by_pos = collections.Counter(f['fail_pos'] for f in failures)
    return {'by_word': by_word.most_common(40),
            'by_upos_deprel': [(f'{u}/{r}', c) for (u, r), c in by_upos_rel.most_common(40)],
            'by_position': sorted(by_pos.items())}
