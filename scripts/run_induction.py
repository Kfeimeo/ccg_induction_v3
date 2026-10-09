"""Real-data induction (§7.4-5): train on GUM train (word forms only), evaluate on dev.
One configuration = atom group x rule set x lexicon type x MAX_DEPTH x system, several seeds."""
import argparse, collections, json, math, os, pickle, sys, time, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ccg.data import load_jsonl, word_counts
from ccg.induce import induce, DevModel, dev_support, majority_categories
from ccg.experiment import evaluate_lexicon, failure_clusters
from ccg.deps import HeadMap
from ccg.evaluate import mean_std
from ccg import category as C
from ccg.clustering import cluster_words

ap = argparse.ArgumentParser()
ap.add_argument('--config', default='configs/default.yaml')
ap.add_argument('--group', default='A')
ap.add_argument('--rules', default='SA', choices=['SA', 'TR', 'reorder'])
ap.add_argument('--rigid', action='store_true')
ap.add_argument('--anchored', action='store_true', help='same as --anchors the')
ap.add_argument('--anchors', default='none', choices=['none', 'the', 'closed', 'hw1', 'stNP', 'stNPN'], help='seed lexicon (ccg/seeds.py)')
ap.add_argument('--max_depth', type=int, default=0)
ap.add_argument('--system', default='left', choices=['left', 'cky', 'cky_nf', 'stack'])
ap.add_argument('--max_stack', type=int, default=3)
ap.add_argument('--seeds', default='1,2,3,4,5')
ap.add_argument('--train_max_len', type=int, default=10)
ap.add_argument('--train_limit', type=int, default=0)
ap.add_argument('--init_support', type=int, default=0)
ap.add_argument('--outer', type=int, default=0)
ap.add_argument('--tag', default='')
ap.add_argument('--set', action='append', default=[], help='override config: section.key=value')
ap.add_argument('--out', default='results/induction')
args = ap.parse_args()
cfg = yaml.safe_load(open(args.config))
for kv in args.set:
    k, v = kv.split('=', 1)
    sec, key = k.split('.')
    cfg[sec][key] = yaml.safe_load(v)
d = cfg['data']
tr = load_jsonl(os.path.join(d['processed_dir'], f'{d["corpus"]}_train_le{d["max_len"]}.jsonl'))
dv = load_jsonl(os.path.join(d['processed_dir'], f'{d["corpus"]}_dev_le{d["max_len"]}.jsonl'))
tr = [s for s in tr if s.n <= args.train_max_len]
if args.train_limit:
    tr = tr[:args.train_limit]
if args.max_depth:
    cfg['formal_system']['max_depth'] = args.max_depth
if args.init_support:
    cfg['learning']['init_support'] = args.init_support
if args.outer:
    cfg['mdl']['max_outer_iters'] = args.outer
cfg['learning']['rigid'] = args.rigid
cfg['rules'] = {'SA': args.rules == 'SA', 'forbid_TR': args.rules != 'TR', 'standard_slots': args.rules != 'reorder'}
if args.anchored:
    args.anchors = 'the'
if args.anchors != 'none':
    from ccg import seeds
    cfg['anchors'] = seeds.get(args.anchors, word_counts(tr))
    print(f'anchors ({args.anchors}): {len(cfg["anchors"])} words, '
          f'{sum(word_counts(tr).get(w, 0) for w in cfg["anchors"]) / sum(s.n for s in tr):.3f} of train tokens')
ANCH_TAG = {'none': '', 'the': '_anch', 'closed': '_seedC', 'hw1': '_seedH', 'stNP': '_seedNP', 'stNPN': '_seedNPN'}[args.anchors]
atoms = cfg['atoms'][args.group]
if args.group == 'C':
    cfg['category_space']['max_slashes'] = 3     # 7 atoms: bound the pool (documented)
md = cfg['formal_system']['max_depth']
goal = 'S' if 'S' in atoms else next(a for a in atoms if a.startswith('S'))   # group C: S[dcl]
cfg['formal_system']['goal'] = goal
name = f'{args.system}{args.max_stack if args.system == "stack" else ""}_{args.group}_{args.rules}{"_rigid" if args.rigid else ""}{ANCH_TAG}_d{md}_le{args.train_max_len}{args.tag}'
out = os.path.join(args.out, name)
os.makedirs(out, exist_ok=True)
hm = HeadMap(**cfg['eval']['headmap'])
train_words = [s.words for s in tr]
atom_boost = None
if args.group == 'D':
    k_atoms = len([a for a in atoms if a != 'S'])
    coarse, _ = cluster_words(train_words, k_atoms, 0)
    atom_boost = {c: {f'C{c}': 2.0} for c in range(k_atoms)}
    # cluster ids of group-D atoms are given by the coarse clustering (see induce: cluster_of)
    cfg['learning']['n_clusters'] = k_atoms
rows = []
log_f = open(os.path.join(out, f'log_seeds{args.seeds.replace(",", "-")}.txt'), 'w')


def log(msg):
    print(msg); log_f.write(msg + '\n'); log_f.flush()


log(f'config {name}: {len(tr)} train sentences, {len(dv)} dev sentences, atoms={atoms}, rules={cfg["rules"]}')
for seed in [int(x) for x in args.seeds.split(',')]:
    t0 = time.time()
    if args.system in ('cky', 'cky_nf'):
        from ccg.cky_trainer import induce_cky
        trainer, key_of, cluster_of = induce_cky(train_words, atoms, cfg, seed, log=log, max_depth=md, goal=goal,
                                                 atom_boost=atom_boost, normal_form=args.system == 'cky_nf')
    elif args.system == 'stack':
        from ccg.stack_trainer import StackTrainer
        cfg['mdl']['max_stack'] = args.max_stack
        trainer, key_of, cluster_of = induce(train_words, atoms, cfg, seed, log=log, max_depth=md, goal=goal, atom_boost=atom_boost,
                                             trainer_cls=StackTrainer)
    else:
        trainer, key_of, cluster_of = induce(train_words, atoms, cfg, seed, log=log, max_depth=md, goal=goal, atom_boost=atom_boost)
    train_time = time.time() - t0
    # ---- dev evaluation
    supp = dev_support(trainer.lex, key_of, dv)
    res = {}
    if args.system in ('cky', 'cky_nf'):
        from ccg.cky import Chart, viterbi_tree, tree_heads, inside_outside
        from ccg.evaluate import uas, summarize
        per = []
        for s in dv:
            rec = {'sid': s.sid, 'n': s.n, 'covered': False, 'uas_correct': 0, 'uas_total': s.n, 'logprob': 0.0,
                   'in_lex': all(w in supp for w in s.words)}
            if rec['in_lex']:
                ch = Chart([key_of.get(w, w) for w in s.words], trainer.lex.support_lists(), md, goal, args.system == 'cky_nf')
                if ch.accepted:
                    Z, _, _ = inside_outside(ch, trainer.model)
                    p, t = viterbi_tree(ch, trainer.model)
                    if t is not None and Z > 0:
                        rec['covered'] = True; rec['logprob'] = math.log(Z)
                        heads = tree_heads(t, s.words, hm)
                        rec['uas_correct'], _ = uas(heads, s.heads)
            per.append(rec)
        summ = summarize(per); inlex = [r for r in per if r['in_lex']]
        summ['coverage_in_lex'] = summarize(inlex)['coverage'] if inlex else 0
        summ['uas_all_in_lex'] = summarize(inlex)['uas_all'] if inlex else 0
        summ['n_in_lex'] = len(inlex)
        res = {'summary': summ, 'failures': [], 'per_sent': per}
    else:
        pk = {}
        if args.system == 'stack':
            from ccg.stack_lattice import make_builder, goal_state as gs
            from ccg.deps import replay_stack
            pk = {'builder': make_builder(args.max_stack), 'replay_fn': replay_stack, 'goal_state': gs(goal)}
        res = evaluate_lexicon(dv, supp, DevModel(trainer.model, key_of), md, hm, goal=goal, **pk)
    res8 = None
    dv8 = [s for s in dv if s.n <= 8]
    if args.system in ('left', 'stack'):
        res8 = evaluate_lexicon(dv8, supp, DevModel(trainer.model, key_of), md, hm, goal=goal, **pk)
    h = trainer.history[-1]
    # ---- top categories table
    n_cw = trainer.model.n_cw if args.system in ('left', 'stack') else trainer.model.base.n_cw
    cat_tot = sorted(((sum(d.values()), c) for c, d in n_cw.items() if c in trainer.lex.categories()), key=lambda x: -x[0])
    top_cats = [{'category': C.show(c), 'count': round(t, 1),
                 'words': [w for w, _ in sorted(n_cw[c].items(), key=lambda x: -x[1])[:20]]} for t, c in cat_tot[:50]]
    row = {'seed': seed, 'train_time_s': train_time, 'final': h, 'history': trainer.history,
           'anchors': args.anchors, 'n_anchor_words': len(cfg.get('anchors', {})),
           'dev': res['summary'], 'dev_le8': res8['summary'] if res8 else None,
           'dev_failure_clusters': failure_clusters(res['failures']), 'n_dev_failures': len(res['failures']),
           'train_failures': trainer.failure_log()[:200], 'top_categories': top_cats,
           'lexicon_size': {'keys': len(trainer.lex.support), 'entries': trainer.lex.n_entries(), 'categories': len(trainer.lex.categories())}}
    rows.append(row)
    with open(os.path.join(out, f'seed{seed}.json'), 'w') as f:
        json.dump({**row, 'dev_per_sent': res['per_sent'], 'dev_failures': res['failures']}, f, indent=1, ensure_ascii=False)
    with open(os.path.join(out, f'seed{seed}_model.pkl'), 'wb') as f:
        pickle.dump({'model': trainer.model, 'key_of': key_of, 'system': args.system, 'max_depth': md, 'max_stack': args.max_stack}, f)
    s_ = res['summary']
    log(f'== seed {seed}: total={h["total"]:.0f} parsed={h["parsed"]}/{h["n_sent"]} cats={h["n_categories"]} entries={h["n_entries"]} '
        f'| dev cov={s_["coverage"]:.3f} cov_inlex={s_["coverage_in_lex"]:.3f} UAS_all={s_["uas_all"]:.3f} UAS_cov={s_["uas_covered"]:.3f} '
        f'ppl={s_["ppl_per_word"]:.1f} ({train_time:.0f}s)')


import subprocess
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aggregate.py'), out])
