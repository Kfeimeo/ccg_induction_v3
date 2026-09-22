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
ap.add_argument('--anchored', action='store_true')
ap.add_argument('--max_depth', type=int, default=0)
ap.add_argument('--system', default='left', choices=['left', 'cky'])
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
    cfg['anchors'] = {'the': ['NP/N']}
atoms = cfg['atoms'][args.group]
if args.group == 'C':
    cfg['category_space']['max_slashes'] = 3     # 7 atoms: bound the pool (documented)
md = cfg['formal_system']['max_depth']
goal = 'S' if 'S' in atoms else next(a for a in atoms if a.startswith('S'))   # group C: S[dcl]
cfg['formal_system']['goal'] = goal
name = f'{args.system}_{args.group}_{args.rules}{"_rigid" if args.rigid else ""}{"_anch" if args.anchored else ""}_d{md}_le{args.train_max_len}{args.tag}'
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
    if args.system == 'cky':
        from ccg.cky_trainer import CKYTrainer
        import ccg.induce as I
        trainer, key_of, cluster_of = induce_cky = None, None, None
        # reuse induce() machinery with the CKY trainer/model
        from ccg.cky import CKYModel
        from ccg.model import Lexicon, sample_initial_support
        from ccg.induce import make_keys
        lc, mc, cs = cfg['learning'], cfg['mdl'], cfg['category_space']
        cluster_of, counts = cluster_words(train_words, lc['n_clusters'], seed)
        key_of, keyseqs = make_keys(train_words, lc['min_freq'], cluster_of)
        keys = sorted(set(k for s in keyseqs for k in s))
        pool = C.filter_pool(C.enumerate_categories(atoms, cs['max_arity'], cs['max_depth'], cs['max_slashes'], cs['max_complex_args']),
                             cfg['rules']['forbid_TR'], cfg['rules']['standard_slots'])
        init_pool = [c for c in pool if C.n_slashes(c) <= lc.get('init_max_slashes', 2)]
        cluster_key = {k: (cluster_of.get(k, -1) if not k.startswith('<C') else int(k[2:-1])) for k in keys}
        support, theta0 = sample_initial_support(keys, cluster_key, init_pool, lc['init_support'], seed, lc['noise_scale'], atom_boost)
        lex = Lexicon(support, math.log2(len(keys)))
        key_counts = collections.Counter(k for s in keyseqs for k in s)
        model = CKYModel(lex, dict(key_counts), lc.get('trans_beta', 1.0), lc.get('emit_gamma', 0.01), goal)
        model.init_uniform(theta0)
        tcfg = dict(mc); tcfg.update({'em_iters': lc['em_iters'], 'em_tol': lc['em_tol'], 'rigid': args.rigid, 'anchors': {},
                                      'escape_bits_per_word': math.log2(len(pool)) + math.log2(len(keys)) + 1, 'rename_moves': False})
        trainer = CKYTrainer(keyseqs, model, pool, tcfg, md, goal, log)
        trainer.train(mc['max_outer_iters'], True)
    else:
        trainer, key_of, cluster_of = induce(train_words, atoms, cfg, seed, log=log, max_depth=md, goal=goal, atom_boost=atom_boost)
    train_time = time.time() - t0
    # ---- dev evaluation
    supp = dev_support(trainer.lex, key_of, dv)
    res = {}
    if args.system == 'cky':
        from ccg.cky import Chart, viterbi_tree, tree_heads, inside_outside
        from ccg.evaluate import uas, summarize
        per = []
        for s in dv:
            rec = {'sid': s.sid, 'n': s.n, 'covered': False, 'uas_correct': 0, 'uas_total': s.n, 'logprob': 0.0,
                   'in_lex': all(w in supp for w in s.words)}
            if rec['in_lex']:
                ch = Chart([key_of.get(w, w) for w in s.words], trainer.lex.support_lists(), md, goal)
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
        res = evaluate_lexicon(dv, supp, DevModel(trainer.model, key_of), md, hm, goal=goal)
    res8 = None
    dv8 = [s for s in dv if s.n <= 8]
    if args.system == 'left':
        res8 = evaluate_lexicon(dv8, supp, DevModel(trainer.model, key_of), md, hm, goal=goal)
    h = trainer.history[-1]
    # ---- top categories table
    n_cw = trainer.model.n_cw if args.system == 'left' else trainer.model.base.n_cw
    cat_tot = sorted(((sum(d.values()), c) for c, d in n_cw.items() if c in trainer.lex.categories()), key=lambda x: -x[0])
    top_cats = [{'category': C.show(c), 'count': round(t, 1),
                 'words': [w for w, _ in sorted(n_cw[c].items(), key=lambda x: -x[1])[:20]]} for t, c in cat_tot[:50]]
    row = {'seed': seed, 'train_time_s': train_time, 'final': h, 'history': trainer.history,
           'dev': res['summary'], 'dev_le8': res8['summary'] if res8 else None,
           'dev_failure_clusters': failure_clusters(res['failures']), 'n_dev_failures': len(res['failures']),
           'train_failures': trainer.failure_log()[:200], 'top_categories': top_cats,
           'lexicon_size': {'keys': len(trainer.lex.support), 'entries': trainer.lex.n_entries(), 'categories': len(trainer.lex.categories())}}
    rows.append(row)
    with open(os.path.join(out, f'seed{seed}.json'), 'w') as f:
        json.dump({**row, 'dev_per_sent': res['per_sent'], 'dev_failures': res['failures']}, f, indent=1, ensure_ascii=False)
    with open(os.path.join(out, f'seed{seed}_model.pkl'), 'wb') as f:
        pickle.dump({'model': trainer.model, 'key_of': key_of, 'system': args.system, 'max_depth': md}, f)
    s_ = res['summary']
    log(f'== seed {seed}: total={h["total"]:.0f} parsed={h["parsed"]}/{h["n_sent"]} cats={h["n_categories"]} entries={h["n_entries"]} '
        f'| dev cov={s_["coverage"]:.3f} cov_inlex={s_["coverage_in_lex"]:.3f} UAS_all={s_["uas_all"]:.3f} UAS_cov={s_["uas_covered"]:.3f} '
        f'ppl={s_["ppl_per_word"]:.1f} ({train_time:.0f}s)')


import subprocess
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aggregate.py'), out])
