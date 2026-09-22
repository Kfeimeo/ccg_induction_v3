"""Final one-time evaluation on the GUM test split (§2: test is used exactly once)."""
import argparse, json, os, pickle, sys, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ccg.data import load_jsonl, word_counts
from ccg.handwritten import build, CONSTRUCTION_SPECIFIC
from ccg.experiment import evaluate_lexicon
from ccg.induce import DevModel, dev_support
from ccg.deps import HeadMap

ap = argparse.ArgumentParser()
ap.add_argument('--config', default='configs/default.yaml')
ap.add_argument('--model', required=True, help='seedN_model.pkl of the MDL-selected main model')
ap.add_argument('--out', default='results/test')
args = ap.parse_args()
cfg = yaml.safe_load(open(args.config))
d = cfg['data']
tr = load_jsonl(os.path.join(d['processed_dir'], f'{d["corpus"]}_train_le{d["max_len"]}.jsonl'))
dv = load_jsonl(os.path.join(d['processed_dir'], f'{d["corpus"]}_dev_le{d["max_len"]}.jsonl'))
te = load_jsonl(os.path.join(d['processed_dir'], f'{d["corpus"]}_test_le{d["max_len"]}.jsonl'))
md = cfg['formal_system']['max_depth']
hm = HeadMap(**cfg['eval']['headmap'])
os.makedirs(args.out, exist_ok=True)
rows = {}
lex = build('SA', word_counts(tr + dv), 500)
r = evaluate_lexicon(te, lex, None, md, hm, CONSTRUCTION_SPECIFIC)
rows['handwritten_SA_B'] = r['summary']
obj = pickle.load(open(args.model, 'rb'))
supp = dev_support(obj['model'].lex, obj['key_of'], te)
r2 = evaluate_lexicon(te, supp, DevModel(obj['model'], obj['key_of']), obj['max_depth'], hm)
rows['induced_' + os.path.basename(os.path.dirname(args.model)) + '_' + os.path.basename(args.model)] = r2['summary']
json.dump(rows, open(os.path.join(args.out, 'test_results.json'), 'w'), indent=1)
for k, s in rows.items():
    b = s['baselines']
    print(f"{k}: n={s['n_sent']} cov={s['coverage']:.3f} cov_inlex={s['coverage_in_lex']:.3f} (n_inlex={s['n_in_lex']}) UAS_all={s['uas_all']:.3f} "
          f"UAS_cov={s['uas_covered']:.3f} UAS_inlex={s['uas_all_in_lex']:.3f} | LB={b['left_branching']['uas_all']:.3f} RB={b['right_branching']['uas_all']:.3f} "
          f"RB_cov={b['right_branching']['uas_covered_subset']:.3f} rand={b['random_tree']['uas_all']:.3f}")
