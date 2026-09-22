"""Phenomenon test sets and minimal pairs: hand-written lexicon (SA / TR) and induced models."""
import argparse, glob, json, os, pickle, sys, yaml, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ccg.data import load_jsonl, word_counts
from ccg.phenomena import build_sets, evaluate_sets
from ccg.handwritten import build, CONSTRUCTION_SPECIFIC
from ccg.lattice import build_lattice, viterbi
from ccg.experiment import UniformModel
from ccg.deps import replay, HeadMap
from ccg.induce import DevModel, dev_support
from ccg import category as C

ap = argparse.ArgumentParser()
ap.add_argument('--config', default='configs/default.yaml')
ap.add_argument('--models', default='', help='glob of *_model.pkl files of induced models to evaluate')
ap.add_argument('--out', default='results/phenomena')
args = ap.parse_args()
cfg = yaml.safe_load(open(args.config))
d = cfg['data']
tr = load_jsonl(os.path.join(d['processed_dir'], f'{d["corpus"]}_train_le{d["max_len"]}.jsonl'))
dv = load_jsonl(os.path.join(d['processed_dir'], f'{d["corpus"]}_dev_le{d["max_len"]}.jsonl'))
md = cfg['formal_system']['max_depth']
hm = HeadMap(**cfg['eval']['headmap'])
sets = build_sets(dv, tr, 20)
os.makedirs(args.out, exist_ok=True)
json.dump(sets, open(os.path.join(args.out, 'test_sets.json'), 'w'), indent=1, ensure_ascii=False)
print({k: (v['n_dev'], v['n_train'], v['n_constructed']) for k, v in sets.items()})
results = {}


def make_parse_fn(support, model, key_of=None, goal='S'):
    def parse(words):
        parse.last_in_lex = all(w in support for w in words)
        if not parse.last_in_lex:
            return False, None, None
        lat = build_lattice(words, support, md, goal)
        if not lat.accepted:
            return False, None, None
        path, p = viterbi(lat, model, goal)
        if path is None or p <= 0:
            return False, None, None
        heads, _ = replay(words, path, hm)
        return True, heads, [e[1] for e in path]
    return parse


vc = word_counts(tr + dv)
for variant in ('SA', 'TR'):
    lex = build(variant, vc, 500)
    # the phenomenon sentences may contain words outside the 500-word cap: use the full hand-written lexicon
    lex_full = build(variant)
    res = evaluate_sets(sets, make_parse_fn(lex_full, UniformModel(lex_full)), None, CONSTRUCTION_SPECIFIC)
    results[f'handwritten_{variant}'] = res
for path in sorted(glob.glob(args.models)) if args.models else []:
    obj = pickle.load(open(path, 'rb'))
    if obj.get('system') != 'left':
        continue
    model, key_of = obj['model'], obj['key_of']
    allw = sorted({w for st in sets.values() for it in st['items'] for w in it['pos'] + it['neg']})
    from ccg.data import Sentence
    supp = dev_support(model.lex, key_of, [Sentence('', allw, allw, [], [], [])])
    dm = DevModel(model, key_of)
    goal = getattr(model, 'goal', 'S')
    # majority category per word over dev (for L4)
    maj = {}
    cnt = collections.defaultdict(collections.Counter)
    for s in dv:
        if all(w in supp for w in s.words):
            lat = build_lattice(s.words, supp, obj['max_depth'], goal)
            if lat.accepted:
                p, _ = viterbi(lat, dm, goal)
                if p:
                    for w, e in zip(s.words, p):
                        cnt[w][e[1]] += 1
    for w, c in cnt.items():
        maj[w] = c.most_common(1)[0][0]
    name = os.path.relpath(path, args.out if False else 'results').replace('/', '_').replace('_model.pkl', '')
    results[name] = evaluate_sets(sets, make_parse_fn(supp, dm, goal=goal), maj, None)
json.dump(results, open(os.path.join(args.out, 'phenomena_results.json'), 'w'), indent=1)
for name, res in results.items():
    print(f'--- {name}')
    for ph, r in res.items():
        print(f"  {ph:28s} n={r['n']:3d} L1={r['L1_accept']:.2f} L2={r['L2_reject_neg']:.2f} L3={r['L3_pred_arg']:.2f} L4={r['L4_no_cs']:.2f} pair={r['pair_acc']:.2f} | in-lex n={r['n_in_lex']:3d} L1={r['L1_in_lex'] if r['L1_in_lex'] is not None else float('nan'):.2f} L3={r['L3_in_lex'] if r['L3_in_lex'] is not None else float('nan'):.2f}")
