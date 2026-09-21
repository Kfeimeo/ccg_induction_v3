"""Objective diagnostic: on the training sentences whose words are all in the hand-written
lexicon, compare L(M)+L(D|M) of (a) the induced model, (b) the hand-written lexicon with
EM-fitted parameters (same generative model, same L(M) formula, same escape cost)."""
import argparse, collections, json, math, os, pickle, sys, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ccg import category as C
from ccg.data import load_jsonl, word_counts
from ccg.handwritten import build, to_group_A
from ccg.model import Lexicon, Model
from ccg.lattice import build_lattice
from ccg.em import em, data_bits

ap = argparse.ArgumentParser()
ap.add_argument('--model', required=True)
ap.add_argument('--config', default='configs/default.yaml')
args = ap.parse_args()
cfg = yaml.safe_load(open(args.config)); d = cfg['data']
tr = load_jsonl(os.path.join(d['processed_dir'], f'{d["corpus"]}_train_le{d["max_len"]}.jsonl'))
dv = load_jsonl(os.path.join(d['processed_dir'], f'{d["corpus"]}_dev_le{d["max_len"]}.jsonl'))
hw = to_group_A(build('SA', word_counts(tr + dv), 500))
obj = pickle.load(open(args.model, 'rb'))
ind, key_of, md = obj['model'], obj['key_of'], obj['max_depth']
sents = [s.words for s in tr if all(w in hw for w in s.words)]
vocab = sorted({w for s in sents for w in s})
V = len(key_of)
pair = math.log2(V)
pool_bits = math.log2(7914)
esc = pool_bits + math.log2(V) + 1
counts = collections.Counter(w for s in sents for w in s)
# (a) induced model on these sentences (key-mapped)
class KM:
    kind = ind.kind
    def w(self, p, c, w): return ind.w(p, c, key_of.get(w, w))
    def final_weight(self): return ind.final_weight()
supp_ind = {w: sorted(ind.lex.support[key_of[w]], key=C.size) for w in vocab if key_of.get(w) in ind.lex.support}
lats_ind = [build_lattice(s, supp_ind, md) for s in sents]
ld_ind, parsed_ind, _ = data_bits(lats_ind, KM(), esc)
lm_ind = sum(C.size(c) + pair for w in vocab if w in supp_ind for c in supp_ind[w])
# (b) hand-written lexicon restricted to this vocabulary, EM-fitted
lex = Lexicon({w: set(hw[w]) for w in vocab}, pair)
m = Model(lex, 'generative', dict(counts)); m.init_uniform()
lats_hw = [build_lattice(s, lex.support_lists(), md) for s in sents]
hist, _ = em(lats_hw, m, 30, 1e-4)
ld_hw, parsed_hw, _ = data_bits(lats_hw, m, esc)
lm_hw = lex.model_bits()
res = {'n_sent': len(sents), 'vocab': len(vocab),
       'induced': {'L_M': lm_ind, 'L_D': ld_ind, 'total': lm_ind + ld_ind, 'parsed': parsed_ind, 'entries': sum(len(v) for v in supp_ind.values())},
       'handwritten': {'L_M': lm_hw, 'L_D': ld_hw, 'total': lm_hw + ld_hw, 'parsed': parsed_hw, 'entries': lex.n_entries()}}
# (c) hand-written on its own parsed subset only, vs induced on the same subset
sub = [i for i, l in enumerate(lats_hw) if l.accepted]
ld_hw_sub = data_bits([lats_hw[i] for i in sub], m, esc)[0]
ld_ind_sub = data_bits([lats_ind[i] for i in sub], KM(), esc)[0]
res['subset_parsed_by_handwritten'] = {'n': len(sub), 'induced_L_D': ld_ind_sub, 'handwritten_L_D': ld_hw_sub,
                                       'induced_parsed': sum(1 for i in sub if lats_ind[i].accepted)}
print(json.dumps(res, indent=1))
json.dump(res, open(os.path.splitext(args.model)[0] + '_objcmp.json', 'w'), indent=1)
