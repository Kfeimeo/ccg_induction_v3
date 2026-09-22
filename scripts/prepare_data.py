"""Preprocess UD corpora into data/processed/*.jsonl (word forms + gold deps for eval)."""
import argparse, os, sys, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ccg.data import load_split, save_jsonl

ap = argparse.ArgumentParser()
ap.add_argument('--config', default='configs/default.yaml')
args = ap.parse_args()
cfg = yaml.safe_load(open(args.config))
d = cfg['data']
for corpus in ('gum', 'ewt'):
    for split in ('train', 'dev', 'test'):
        path = os.path.join(d['raw_dir'], f'en_{corpus}-ud-{split}.conllu')
        if not os.path.exists(path):
            continue
        sents = load_split(path, max_len=d['max_len'], lowercase=d['lowercase'],
                           s_types=d['s_types'] if corpus == 'gum' else None)
        out = os.path.join(d['processed_dir'], f'{corpus}_{split}_le{d["max_len"]}.jsonl')
        save_jsonl(sents, out)
        n8 = sum(1 for s in sents if s.n <= 8)
        print(f'{corpus} {split}: {len(sents)} sentences (<=8: {n8}) -> {out}')
