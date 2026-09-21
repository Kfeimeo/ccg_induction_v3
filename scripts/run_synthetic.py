"""§7.3 synthetic validation: 20-word grammar, 500 sentences, EM+MDL must recover the lexicon."""
import argparse, json, os, sys, yaml, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ccg.synthetic import generate, gold_lexicon, best_atom_mapping, GOLD, derivation_recovery
from ccg.induce import induce, majority_categories
from ccg import category as C
from ccg.evaluate import mean_std

ap = argparse.ArgumentParser()
ap.add_argument('--config', default='configs/default.yaml')
ap.add_argument('--seeds', default='1,2,3,4,5')
ap.add_argument('--out', default='results/synthetic')
ap.add_argument('--n', type=int, default=500)
ap.add_argument('--init_support', type=int, default=0)
ap.add_argument('--model', default='')
ap.add_argument('--tag', default='')
ap.add_argument('--em_mode', default='')
ap.add_argument('--outer', type=int, default=0)
ap.add_argument('--init_max_slashes', type=int, default=0)
args = ap.parse_args()
cfg = yaml.safe_load(open(args.config))
cfg['learning']['min_freq'] = 1          # 20-word vocabulary: every word is its own key
cfg['learning']['n_clusters'] = 6
if args.init_support: cfg['learning']['init_support'] = args.init_support
if args.model: cfg['learning']['model'] = args.model
if args.em_mode: cfg['learning']['em_mode'] = args.em_mode
if args.outer: cfg['mdl']['max_outer_iters'] = args.outer
if args.init_max_slashes: cfg['learning']['init_max_slashes'] = args.init_max_slashes
os.makedirs(args.out, exist_ok=True)
sents = generate(args.n, 0)
gold = gold_lexicon()
rows = []
for seed in [int(x) for x in args.seeds.split(',')]:
    t0 = time.time()
    trainer, key_of, _ = induce(sents, cfg['atoms']['A'], cfg, seed, log=print, max_depth=cfg['formal_system']['max_depth'])
    pred = majority_categories(trainer)
    acc, mp = best_atom_mapping(pred, gold)
    # full-lexicon recovery: set equality of the pruned support (after renaming) with gold
    ren = {k: {C.rename_atoms(c, mp) for c in cs} for k, cs in trainer.lex.support.items()}
    exact = sum(1 for w in GOLD if ren.get(w) == set(gold[w]))
    extra = sum(len(cs - set(gold.get(w, []))) for w, cs in ren.items())
    h = trainer.history[-1]
    drec = derivation_recovery(sents, trainer.lex.support_lists(), trainer.model, gold, cfg['formal_system']['max_depth'])
    row = {'seed': seed, 'majority_acc': acc, 'derivation_recovery': drec, 'exact_words': exact, 'extra_entries': extra, 'mapping': mp,
           'parsed': h['parsed'], 'n_categories': h['n_categories'], 'n_entries': h['n_entries'],
           'total_bits': h['total'], 'time_s': time.time() - t0,
           'lexicon': {k: [C.show(c) for c in sorted(cs, key=C.size)] for k, cs in trainer.lex.support.items()},
           'pred_majority': {k: C.show(c) for k, c in pred.items()}}
    rows.append(row)
    print(f'seed {seed}: majority acc={acc:.2f} deriv_rec={drec:.3f} bits={h["total"]:.0f} exact words={exact}/20 extra entries={extra} parsed={h["parsed"]}/{len(sents)} '
          f'cats={h["n_categories"]} entries={h["n_entries"]} map={mp} ({row["time_s"]:.0f}s)')
    print('   ', {k: v for k, v in row['pred_majority'].items()})
m, sd = mean_std([r['majority_acc'] for r in rows])
dm, dsd = mean_std([r['derivation_recovery'] for r in rows])
best = min(rows, key=lambda r: r['total_bits'])
print(f'majority accuracy mean={m:.3f} sd={sd:.3f}; derivation recovery mean={dm:.3f} sd={dsd:.3f}; '
      f'MDL-selected seed {best["seed"]}: acc={best["majority_acc"]:.2f} deriv_rec={best["derivation_recovery"]:.3f} bits={best["total_bits"]:.0f}')
json.dump({'rows': rows, 'gold': GOLD, 'majority_acc_mean': m, 'majority_acc_sd': sd, 'deriv_rec_mean': dm, 'deriv_rec_sd': dsd,
           'mdl_selected_seed': best['seed'],
           'history': [t for t in []]}, open(os.path.join(args.out, f'synthetic{args.tag}.json'), 'w'), indent=1)
