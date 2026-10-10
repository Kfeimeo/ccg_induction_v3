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


def make_parse_fn(support, model, key_of=None, goal='S', builder=None, replay_fn=None, goal_state=None):
    builder = builder or build_lattice
    replay_fn = replay_fn or replay
    gs = goal_state if goal_state is not None else goal

    def parse(words):
        parse.last_in_lex = all(w in support for w in words)
        if not parse.last_in_lex:
            return False, None, None
        lat = builder(words, support, md, goal)
        if not lat.accepted:
            return False, None, None
        path, p = viterbi(lat, model, gs)
        if path is None or p <= 0:
            return False, None, None
        heads, _ = replay_fn(words, path, hm)
        return True, heads, [e[1] for e in path]
    return parse


def evaluate_cky(obj, sets, dv, md, hm):
    """CKY / Eisner-normal-form models: Viterbi tree over the chart of the training keys;
    heads via cky.tree_heads, lexical categories from the tree leaves."""
    from ccg.cky import Chart, viterbi_tree, tree_heads
    from ccg.data import Sentence
    model, key_of, nf = obj['model'], obj['key_of'], obj['system'] == 'cky_nf'
    goal = getattr(model, 'goal', 'S')
    allw = sorted({w for st in sets.values() for it in st['items'] for w in it['pos'] + it['neg']})
    supp = dev_support(model.lex, key_of, [Sentence('', allw, allw, [], [], [])])
    supp_keys = model.lex.support_lists()

    def leaf_cats(t, out):
        if len(t) == 3:
            out.append(t[0])
        else:
            leaf_cats(t[4], out); leaf_cats(t[5], out)
        return out

    def best_tree(words):
        ch = Chart([key_of.get(w, w) for w in words], supp_keys, md, goal, nf)
        if not ch.accepted:
            return None
        p, t = viterbi_tree(ch, model)
        return t if t is not None and p > 0 else None

    def parse(words):
        parse.last_in_lex = all(w in supp for w in words)
        if not parse.last_in_lex:
            return False, None, None
        t = best_tree(words)
        if t is None:
            return False, None, None
        return True, tree_heads(t, words, hm), leaf_cats(t, [])
    maj = {}
    cnt = collections.defaultdict(collections.Counter)
    for s in dv:
        if all(w in supp for w in s.words):
            t = best_tree(s.words)
            if t is not None:
                for w, c in zip(s.words, leaf_cats(t, [])):
                    cnt[w][c] += 1
    for w, c in cnt.items():
        maj[w] = c.most_common(1)[0][0]
    return evaluate_sets(sets, parse, maj, None)


vc = word_counts(tr + dv)
for variant in ('SA', 'TR'):
    lex = build(variant, vc, 500)
    # the phenomenon sentences may contain words outside the 500-word cap: use the full hand-written lexicon
    lex_full = build(variant)
    res = evaluate_sets(sets, make_parse_fn(lex_full, UniformModel(lex_full)), None, CONSTRUCTION_SPECIFIC)
    results[f'handwritten_{variant}'] = res
for path in sorted(glob.glob(args.models)) if args.models else []:
    obj = pickle.load(open(path, 'rb'))
    if obj.get('system') not in ('left', 'stack', 'cky', 'cky_nf'):
        continue
    name = os.path.relpath(path, 'results').replace('/', '_').replace('\\', '_').replace('_model.pkl', '')
    if obj.get('system') in ('cky', 'cky_nf'):
        results[name] = evaluate_cky(obj, sets, dv, md, hm)
        continue
    pk = {}
    if obj.get('system') == 'stack':
        from ccg.stack_lattice import make_builder, goal_state as gs_fn
        from ccg.deps import replay_stack
        pk = {'builder': make_builder(obj.get('max_stack', 3)), 'replay_fn': replay_stack}
    model, key_of = obj['model'], obj['key_of']
    allw = sorted({w for st in sets.values() for it in st['items'] for w in it['pos'] + it['neg']})
    from ccg.data import Sentence
    supp = dev_support(model.lex, key_of, [Sentence('', allw, allw, [], [], [])])
    dm = DevModel(model, key_of)
    goal = getattr(model, 'goal', 'S')
    if pk:
        pk['goal_state'] = gs_fn(goal)
    # majority category per word over dev (for L4)
    maj = {}
    cnt = collections.defaultdict(collections.Counter)
    for s in dv:
        if all(w in supp for w in s.words):
            lat = pk['builder'](s.words, supp, obj['max_depth'], goal) if pk else build_lattice(s.words, supp, obj['max_depth'], goal)
            if lat.accepted:
                p, _ = viterbi(lat, dm, pk['goal_state'] if pk else goal)
                if p:
                    for w, e in zip(s.words, p):
                        cnt[w][e[1]] += 1
    for w, c in cnt.items():
        maj[w] = c.most_common(1)[0][0]
    results[name] = evaluate_sets(sets, make_parse_fn(supp, dm, goal=goal, **pk), maj, None)
json.dump(results, open(os.path.join(args.out, 'phenomena_results.json'), 'w'), indent=1)
for name, res in results.items():
    print(f'--- {name}')
    for ph, r in res.items():
        print(f"  {ph:28s} n={r['n']:3d} L1={r['L1_accept']:.2f} L2={r['L2_reject_neg']:.2f} L3={r['L3_pred_arg']:.2f} L4={r['L4_no_cs']:.2f} pair={r['pair_acc']:.2f} | in-lex n={r['n_in_lex']:3d} L1={r['L1_in_lex'] if r['L1_in_lex'] is not None else float('nan'):.2f} L3={r['L3_in_lex'] if r['L3_in_lex'] is not None else float('nan'):.2f}")
