"""§5 hand-written lexicon upper bound on dev (and the <=8 subset)."""
import argparse, json, os, sys, yaml, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ccg.data import load_jsonl, word_counts
from ccg.handwritten import build, CONSTRUCTION_SPECIFIC, to_group_A
from ccg.experiment import evaluate_lexicon, failure_clusters
from ccg.deps import HeadMap
from ccg import category as C

ap = argparse.ArgumentParser()
ap.add_argument('--config', default='configs/default.yaml')
ap.add_argument('--split', default='dev')
ap.add_argument('--out', default='results/upper_bound')
args = ap.parse_args()
cfg = yaml.safe_load(open(args.config))
d = cfg['data']
tr = load_jsonl(os.path.join(d['processed_dir'], f'{d["corpus"]}_train_le{d["max_len"]}.jsonl'))
dv = load_jsonl(os.path.join(d['processed_dir'], f'{d["corpus"]}_{args.split}_le{d["max_len"]}.jsonl'))
vc = word_counts(tr + dv)
os.makedirs(args.out, exist_ok=True)
md = cfg['formal_system']['max_depth']
hm = HeadMap(**cfg['eval']['headmap'])
rows = []
for variant in ('SA', 'TR'):
    for atoms in ('B', 'A'):
        lex = build(variant, vc, 500)
        if atoms == 'A':
            lex = to_group_A(lex)
        for maxlen in (10, 8):
            sents = [s for s in dv if s.n <= maxlen]
            res = evaluate_lexicon(sents, lex, None, md, hm, CONSTRUCTION_SPECIFIC)
            summ = res['summary']
            summ.update({'variant': variant, 'atoms': atoms, 'max_len': maxlen,
                         'lex_words': len(lex), 'lex_entries': sum(len(v) for v in lex.values())})
            rows.append(summ)
            tag = f'{variant}_{atoms}_le{maxlen}'
            with open(os.path.join(args.out, f'{tag}.json'), 'w') as f:
                json.dump({'summary': summ, 'failures': res['failures'],
                           'failure_clusters': failure_clusters(res['failures']),
                           'per_sent': res['per_sent']}, f, indent=1, ensure_ascii=False)
            print(f"{tag}: cov={summ['coverage']:.3f} cov_inlex={summ['coverage_in_lex']:.3f} (n_inlex={summ['n_in_lex']}) "
                  f"UAS_all={summ['uas_all']:.3f} UAS_cov={summ['uas_covered']:.3f} UAS_inlex={summ['uas_all_in_lex']:.3f} "
                  f"SAamb={summ['sa_ambiguous']}/{summ['sa_applied']} |Q|={summ['lat_Q_unpruned_mean']:.1f} b={summ['lat_b_mean']:.2f} "
                  f"LB={summ['baselines']['left_branching']['uas_all']:.3f} RB={summ['baselines']['right_branching']['uas_all']:.3f} "
                  f"RB_cov={summ['baselines']['right_branching']['uas_covered_subset']:.3f} rand={summ['baselines']['random_tree']['uas_all']:.3f}")
with open(os.path.join(args.out, 'summary.json'), 'w') as f:
    json.dump(rows, f, indent=1)
