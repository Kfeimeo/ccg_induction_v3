"""Re-evaluate saved models on dev with the current head-mapping module (left-branching models only);
prints old vs new UAS on covered sentences so a mapping change can be checked for its effect."""
import glob, json, os, pickle, sys, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ccg.data import load_jsonl
from ccg.experiment import evaluate_lexicon
from ccg.induce import DevModel, dev_support
from ccg.deps import HeadMap

cfg = yaml.safe_load(open('configs/default.yaml')); d = cfg['data']
dv = load_jsonl(os.path.join(d['processed_dir'], f'{d["corpus"]}_dev_le{d["max_len"]}.jsonl'))
hm = HeadMap(**cfg['eval']['headmap'])
for sp in sorted(glob.glob('results/induction/left_*/summary.json')):
    dd = os.path.dirname(sp); s = json.load(open(sp))['mdl_selected_seed']
    obj = pickle.load(open(os.path.join(dd, f'seed{s}_model.pkl'), 'rb'))
    old = json.load(open(os.path.join(dd, f'seed{s}.json')))['dev']
    supp = dev_support(obj['model'].lex, obj['key_of'], dv)
    r = evaluate_lexicon(dv, supp, DevModel(obj['model'], obj['key_of']), obj['max_depth'], hm, goal=getattr(obj['model'], 'goal', 'S'))['summary']
    print(f"{os.path.basename(dd):28s} seed{s}: UAS_cov old={old['uas_covered']:.3f} new={r['uas_covered']:.3f}  UAS_all old={old['uas_all']:.3f} new={r['uas_all']:.3f}")
