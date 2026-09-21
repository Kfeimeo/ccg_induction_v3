"""Induction driver: keys (rare-word tying), clustering, initial lexicon, MDL training, evaluation."""
from __future__ import annotations
import collections
import math
import time
from typing import Dict, List, Optional, Tuple
from . import category as C
from .clustering import cluster_words
from .model import Lexicon, Model, sample_initial_support
from .mdl import MDLTrainer
from .data import Sentence


def make_keys(train: List[List[str]], min_freq: int, cluster_of: Dict[str, int]) -> Tuple[Dict[str, str], List[List[str]]]:
    """Words with count < min_freq share the parameters of their distributional cluster
    (key '<C{k}>'); everything else is its own key.  Returns key_of_word and key sequences."""
    counts = collections.Counter(w for s in train for w in s)
    key_of = {}
    for w, c in counts.items():
        key_of[w] = w if c >= min_freq else f'<C{cluster_of.get(w, 0)}>'
    return key_of, [[key_of[w] for w in s] for s in train]


def induce(train_words: List[List[str]], atoms: List[str], cfg: dict, seed: int, log=print,
           max_depth: int = 4, goal: str = 'S', pool: Optional[List[C.Cat]] = None,
           atom_boost=None) -> Tuple[MDLTrainer, Dict[str, str], Dict[str, int]]:
    lc, mc, cs = cfg['learning'], cfg['mdl'], cfg['category_space']
    t0 = time.time()
    cluster_of, counts = cluster_words(train_words, lc['n_clusters'], seed)
    key_of, keyseqs = make_keys(train_words, lc['min_freq'], cluster_of)
    keys = sorted(set(k for s in keyseqs for k in s))
    from .combine import set_rules
    rules = cfg.get('rules', {})
    set_rules(sa=rules.get('SA', True))
    if pool is None:
        pool = C.enumerate_categories(atoms, cs['max_arity'], cs['max_depth'], cs['max_slashes'], cs['max_complex_args'])
        pool = C.filter_pool(pool, rules.get('forbid_TR', True), rules.get('standard_slots', True))
    init_pool = [c for c in pool if C.n_slashes(c) <= lc.get('init_max_slashes', 2)]
    anchors = {w: [C.parse(x) for x in xs] for w, xs in (cfg.get('anchors') or {}).items()}
    V = len(keys)
    pair_bits = math.log2(V) if mc.get('word_pair_bits', 'log2V') == 'log2V' else float(mc['word_pair_bits'])
    cluster_key = {k: (cluster_of.get(k, -1) if not k.startswith('<C') else int(k[2:-1])) for k in keys}
    always = [C.parse(c) for c in lc.get('always_include', [])] or None
    support, theta0 = sample_initial_support(keys, cluster_key, init_pool, lc['init_support'], seed, lc['noise_scale'],
                                             atom_boost, always)
    for w, xs in anchors.items():
        if w in support:
            support[w] = set(xs)
            theta0[w] = {x: 1.0 / len(xs) for x in xs}
    if lc.get('rigid', False):
        for k in support:
            best = max(theta0[k], key=theta0[k].get)
            support[k] = {best}; theta0[k] = {best: 1.0}
    lex = Lexicon(support, pair_bits)
    key_counts = collections.Counter(k for s in keyseqs for k in s)
    model = Model(lex, lc.get('model', 'generative'), dict(key_counts), lc.get('trans_beta', 1.0),
                  lc.get('emit_gamma', 0.01), lc.get('dirichlet_smooth', 0.01), goal)
    model.init_uniform(theta0)
    log(f'seed {seed}: {len(train_words)} sentences, {V} keys ({sum(1 for k in keys if k.startswith("<C"))} cluster keys), '
        f'pool={len(pool)} init_pool={len(init_pool)} init entries={lex.n_entries()} model={model.kind} ({time.time()-t0:.1f}s)')
    tcfg = dict(mc)
    tcfg.update({'em_iters': lc['em_iters'], 'em_tol': lc['em_tol'], 'em_mode': lc.get('em_mode', 'soft'),
                 'anneal_max': lc.get('anneal_max', 2.0)})
    tcfg['escape_bits_per_word'] = math.log2(len(pool)) + (math.log2(V) if model.kind == 'generative' else 0.0) + 1
    tcfg['rigid'] = lc.get('rigid', False)
    tcfg['anchors'] = {w: [C.show(x) for x in xs] for w, xs in anchors.items()}
    tcfg['rename_moves'] = mc.get('rename_moves', True)
    trainer = MDLTrainer(keyseqs, model, pool, tcfg, max_depth, goal, log)
    trainer.train(mc['max_outer_iters'], mc.get('failure_proposals', True))
    return trainer, key_of, cluster_of


class DevModel:
    """Wraps a trained model so that dev words are looked up through their training key."""

    def __init__(self, model: Model, key_of: Dict[str, str]):
        self.model, self.key_of = model, key_of
        self.kind = model.kind

    def w(self, prev, c, word):
        return self.model.w(prev, c, self.key_of.get(word, word))

    def final_weight(self):
        return self.model.final_weight()


def dev_support(lex: Lexicon, key_of: Dict[str, str], dev: List[Sentence]):
    """Map dev words to their training key's support; unseen words get no entry (OOV)."""
    supp = {}
    for s in dev:
        for w in s.words:
            if w in supp:
                continue
            k = key_of.get(w)
            if k is not None and k in lex.support:
                supp[w] = sorted(lex.support[k], key=lambda c: (C.size(c), C.show(c)))
    return supp


def majority_categories(trainer: MDLTrainer) -> Dict[str, C.Cat]:
    """Most probable category per key under Viterbi over the training data (falls back to argmax θ)."""
    from .lattice import viterbi
    cnt: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for lat in trainer.lats:
        path, p = viterbi(lat, trainer.model, trainer.goal)
        if path is None:
            continue
        for k, (_, c, _, _) in enumerate(path):
            cnt[lat.words[k]][c] += 1
    out = {}
    for key, cs in trainer.lex.support.items():
        th = trainer.model.theta.get(key, {})
        if cnt[key]:
            out[key] = cnt[key].most_common(1)[0][0]
        elif th:
            out[key] = max(th, key=th.get)
        else:
            out[key] = min(cs, key=C.size)
    return out
