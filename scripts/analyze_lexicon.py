"""Post-hoc best atom mapping (§6): compare an induced lexicon's majority categories with the
hand-written lexicon over shared words, maximising agreement over permutations of the
non-S atoms; also reports agreement on category *shape* (atoms ignored)."""
import argparse, itertools, json, os, pickle, sys, collections, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ccg import category as C
from ccg.handwritten import build
from ccg.data import load_jsonl, word_counts

ap = argparse.ArgumentParser()
ap.add_argument('--model', required=True)
ap.add_argument('--config', default='configs/default.yaml')
args = ap.parse_args()
cfg = yaml.safe_load(open(args.config)); d = cfg['data']
tr = load_jsonl(os.path.join(d['processed_dir'], f'{d["corpus"]}_train_le{d["max_len"]}.jsonl'))
dv = load_jsonl(os.path.join(d['processed_dir'], f'{d["corpus"]}_dev_le{d["max_len"]}.jsonl'))
hw = build('SA', word_counts(tr + dv), 500)
hwA = {w: {C.rename_atoms(c, {'PP': 'NP'}) for c in cs} for w, cs in hw.items()}
obj = pickle.load(open(args.model, 'rb'))
model, key_of = obj['model'], obj['key_of']
maj = {}
for w, k in key_of.items():
    th = model.theta.get(k)
    if th and k == w:
        maj[w] = max(th, key=th.get)
shared = [w for w in maj if w in hwA]
atoms = sorted({a for cs in hwA.values() for c in cs for a in C.atoms_of(c)} - {'S'})
ind_atoms = sorted({a for c in maj.values() for a in C.atoms_of(c)} - {'S'})


def shape(c):
    return C.rename_atoms(c, {a: 'X' for a in C.atoms_of(c) if a != 'S'})


best = (-1, None)
for perm in itertools.permutations(atoms, len(ind_atoms)) if len(ind_atoms) <= len(atoms) else [tuple(atoms)]:
    mp = dict(zip(ind_atoms, perm))
    ok = sum(1 for w in shared if C.rename_atoms(maj[w], mp) in hwA[w])
    if ok > best[0]:
        best = (ok, mp)
ok, mp = best
shape_ok = sum(1 for w in shared if shape(maj[w]) in {shape(c) for c in hwA[w]})
arity_ok = sum(1 for w in shared if C.arity(maj[w]) in {C.arity(c) for c in hwA[w]})
print(f'shared words {len(shared)}; best mapping {mp}: exact agreement {ok}/{len(shared)} = {ok/len(shared):.3f}; '
      f'shape agreement {shape_ok/len(shared):.3f}; arity agreement {arity_ok/len(shared):.3f}')
# per hand-written class: what did the learner do?
by_hw = collections.defaultdict(collections.Counter)
for w in shared:
    for c in hwA[w]:
        if C.arity(c) <= 2:
            by_hw[C.show(c)][C.show(C.rename_atoms(maj[w], mp))] += 1
for hc, cnt in sorted(by_hw.items(), key=lambda x: -sum(x[1].values()))[:12]:
    print(f'  hand-written {hc:14s} -> induced (mapped): {cnt.most_common(5)}')
json.dump({'shared': len(shared), 'mapping': mp, 'exact': ok / len(shared), 'shape': shape_ok / len(shared), 'arity': arity_ok / len(shared)},
          open(os.path.splitext(args.model)[0] + '_hwmap.json', 'w'))
