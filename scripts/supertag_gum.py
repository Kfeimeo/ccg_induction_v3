"""Supertag the GUM sentences with the Hol-CCG parser (Yamaki et al. 2023; ../hol-ccg).

For every token: the supertagger's top-k lexical categories with probabilities (softmax of the
word-category classifier over the RoBERTa-large word vectors) and, as a sanity check, the leaf
category of the full Hol-CCG parse (CKY over the supertags) when the parse succeeds.
Runs under the conda env `ccg` (torch + transformers):
  E:/anaconda3/envs/ccg/python.exe scripts/supertag_gum.py --splits train,dev
Output: data/supertags/gum_<split>_le10_stags.jsonl  (one record per sentence, tokens in the
original casing `orig`, aligned 1:1 with `words`)."""
import argparse, json, os, re, sys, time
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
HOL = os.path.join(os.path.dirname(HERE), 'hol-ccg')
sys.path.insert(0, os.path.join(HOL, 'src'))
from ccg.data import load_jsonl

ap = argparse.ArgumentParser()
ap.add_argument('--splits', default='train,dev')
ap.add_argument('--model_dir', default=os.path.join(HOL, 'models'))
ap.add_argument('--device', default='cuda')
ap.add_argument('--topk', type=int, default=5)
ap.add_argument('--batch', type=int, default=32)
ap.add_argument('--no_parse', action='store_true', help='skip the full CKY parse (supertags only)')
ap.add_argument('--out', default='data/supertags')
args = ap.parse_args()

import torch
from holccg.parsing.inference import HolCCGParser, InferenceOptions
from holccg.utils.ccg_normalize import normalize_ptb_tokens

parser = HolCCGParser.from_pretrained(args.model_dir, device=args.device, options=InferenceOptions())
model = parser.model
index2cat = model.word_index2category
unk = model.word_category2index.get('<unk>', 0)
LEAF = re.compile(r'\(<L (\S+) \S+ \S+ (\S+) (\S+)>\)')


def leaves(auto: str):
    """(category, word) of the leaves of a .auto string, left to right."""
    return [(m.group(1), m.group(2)) for m in LEAF.finditer(auto)]


@torch.no_grad()
def supertag(batch_words):
    vecs = model._encode_words_batch([normalize_ptb_tokens(w) for w in batch_words])
    out = []
    for v in vecs:
        probs = torch.softmax(model.word_category_classifier(v), dim=-1)
        probs[:, unk] = 0.0
        p, idx = torch.topk(probs, args.topk, dim=-1)
        out.append([[(index2cat[int(i)], float(pp)) for pp, i in zip(prow, irow)] for prow, irow in zip(p.tolist(), idx.tolist())])
    return out


os.makedirs(args.out, exist_ok=True)
for split in args.splits.split(','):
    sents = load_jsonl(os.path.join(HERE, 'data', 'processed', f'gum_{split}_le10.jsonl'))
    t0 = time.time()
    n_ok = n_partial = 0
    with open(os.path.join(args.out, f'gum_{split}_le10_stags.jsonl'), 'w', encoding='utf-8') as f:
        for b in range(0, len(sents), args.batch):
            chunk = sents[b:b + args.batch]
            toks = [s.orig for s in chunk]
            tags = supertag(toks)
            parses = None
            if not args.no_parse:
                parses = parser.parse_tokens_batch(toks, indices=list(range(b, b + len(chunk))), sentence_ids=[s.sid for s in chunk])
            for j, s in enumerate(chunk):
                rec = {'sid': s.sid, 'words': s.words, 'orig': s.orig, 'upos': s.upos,
                       'topk': tags[j], 'parse_status': None, 'parse_leaf': None}
                if parses is not None:
                    pr = parses[j]
                    rec['parse_status'] = pr.status.value
                    auto = pr.auto if pr.auto else None
                    if auto:
                        lv = leaves(auto)
                        if len(lv) == s.n:
                            rec['parse_leaf'] = [c for c, _ in lv]
                        rec['auto'] = auto
                    n_ok += pr.status.value == 'success'
                    n_partial += pr.status.value == 'partial'
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            print(f'{split}: {b + len(chunk)}/{len(sents)} ({time.time() - t0:.0f}s)', flush=True)
    print(f'{split}: {len(sents)} sentences, parse success={n_ok} partial={n_partial} ({time.time() - t0:.0f}s)')
