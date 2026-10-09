"""Anchored (seed) entries are invariant under MDL training."""
import os, sys, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ccg import category as C
from ccg.synthetic import generate
from ccg.induce import induce
from ccg import seeds


def _cfg():
    cfg = yaml.safe_load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'configs', 'default.yaml')))
    cfg['mdl']['max_outer_iters'] = 3
    cfg['mdl']['curriculum'] = None
    cfg['learning']['em_iters'] = 3
    cfg['mdl']['max_candidates_per_op'] = 30
    return cfg


def test_seed_sets_parse():
    for name in ('the', 'closed'):
        for w, cats in seeds.get(name).items():
            for x in cats:
                assert C.show(C.parse(x)) == x
    hw = seeds.get('hw1', {'i': 100, 'the': 100, 'look': 10})
    assert hw['i'] == ['NP'] and 'the' not in hw   # "the" has two hand-written categories


def test_anchors_fixed_through_training():
    sents = generate(60, seed=0, max_len=6)
    words = [s.words if hasattr(s, 'words') else s for s in sents]
    counts = {}
    for s in words:
        for w in s:
            counts[w] = counts.get(w, 0) + 1
    common = sorted(counts, key=lambda w: -counts[w])[:3]
    cfg = _cfg()
    cfg['anchors'] = {common[0]: ['NP'], common[1]: ['NP/N'], common[2]: ['(S\\NP)/NP']}
    cfg['mdl']['rename_moves'] = True
    trainer, key_of, _ = induce(words, ['S', 'N', 'NP'], cfg, seed=1, log=lambda *a, **k: None, max_depth=4)
    assert trainer.history[-1]['round'] >= 1
    for w, cats in cfg['anchors'].items():
        assert trainer.lex.support[w] == {C.parse(x) for x in cats}, (w, trainer.lex.support[w])
        th = trainer.model.theta[w]
        assert abs(sum(th.values()) - 1.0) < 1e-6 and set(th) == set(trainer.lex.support[w])
    assert trainer.history[-1]['n_evals'] > 0


def test_anchors_fixed_cky_nf_and_stack():
    """The Eisner-normal-form CKY trainer and the stack trainer honour anchors too."""
    from ccg.cky_trainer import induce_cky
    from ccg.stack_trainer import StackTrainer
    sents = generate(40, seed=0, max_len=5)
    words = [s.words if hasattr(s, 'words') else s for s in sents]
    counts = {}
    for s in words:
        for w in s:
            counts[w] = counts.get(w, 0) + 1
    common = sorted(counts, key=lambda w: -counts[w])[:2]
    cfg = _cfg()
    cfg['mdl']['max_outer_iters'] = 2
    cfg['anchors'] = {common[0]: ['NP'], common[1]: ['N']}
    cfg['rules'] = {'SA': True, 'forbid_TR': True, 'standard_slots': True}
    quiet = lambda *a, **k: None
    cky = induce_cky(words, ['S', 'N', 'NP'], cfg, 1, log=quiet, max_depth=4, normal_form=True)[0]
    cfg_stack = dict(cfg, mdl=dict(cfg['mdl'], max_stack=2))
    stack = induce(words, ['S', 'N', 'NP'], cfg_stack, 1, log=quiet, max_depth=4, trainer_cls=StackTrainer)[0]
    for trainer in (cky, stack):
        for w, cats in cfg['anchors'].items():
            assert trainer.lex.support[w] == {C.parse(x) for x in cats}, (w, trainer.lex.support[w])


def test_supertag_seed_sets():
    for name in ('stNP', 'stNPN'):
        s = seeds.get(name)
        assert s['i'] == ['NP'] and s['it'] == ['NP']
        for w, cats in s.items():
            assert len(cats) == 1 and cats[0] in ('NP', 'N')
    assert seeds.get('stNPN')['day'] == ['N'] and 'day' not in seeds.get('stNP')
