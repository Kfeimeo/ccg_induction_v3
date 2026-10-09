r"""Build the supertagger-derived seed sets from data/supertags/gum_train_le10_stags.jsonl
(scripts/supertag_gum.py, Hol-CCG) and write data/supertags/seed_sets.json (read by ccg/seeds.py).

Reading of a Hol-CCG word category (CCGbank conventions, features stripped):
  - a unary chain containing NP (`N-->NP` bare noun phrase, `NP-->S/(S\NP)` type-raised NP,
    `NP[nb]`, `NP[thr]` ...) counts as NP: in this project's formal system (no unary rules, no
    type raising) such a word must carry NP itself;
  - plain `N` (noun under a determiner / in a compound) counts as N;
  - anything else is the lexical category (first element of the chain).
A word is seeded iff it has its own key (train count >= min_count) and its top-1 supertag reads
as the seed category in >= tau of its training occurrences.  Sets: stNP (NP only), stNPN (NP + N).
"""
import argparse, collections, json, os, re, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from ccg.handwritten import build
from ccg import category as C

ap = argparse.ArgumentParser()
ap.add_argument('--stags', default='data/supertags/gum_train_le10_stags.jsonl')
ap.add_argument('--tau', type=float, default=0.9)
ap.add_argument('--min_count', type=int, default=2, help='= learning.min_freq: rarer words share a cluster key and cannot be anchored')
ap.add_argument('--out', default='data/supertags/seed_sets.json')
args = ap.parse_args()


def read(cat: str) -> str:
    chain = [re.sub(r'\[[a-z]+\]', '', x) for x in cat.split('-->')]
    if 'NP' in chain:
        return 'NP'
    if chain == ['N']:
        return 'N'
    return chain[0]


recs = [json.loads(l) for l in open(args.stags, encoding='utf-8')]
cnt = collections.Counter(); dist = collections.defaultdict(collections.Counter); n_tok = 0
for r in recs:
    for w, t in zip(r['words'], r['topk']):
        cnt[w] += 1; n_tok += 1; dist[w][read(t[0][0])] += 1
hw = build('SA', cnt, 500)
hwA = {w: {C.show(C.rename_atoms(c, {'PP': 'NP'})) for c in cs} for w, cs in hw.items()}
out = {'tau': args.tau, 'min_count': args.min_count, 'n_train_tokens': n_tok, 'sets': {}, 'stats': {}, 'words': {}}
for name, cats in (('stNP', ['NP']), ('stNPN', ['NP', 'N'])):
    seed = {}
    for cat in cats:
        for w in cnt:
            if cnt[w] >= args.min_count and dist[w][cat] / cnt[w] >= args.tau:
                seed[w] = [cat]
    shared = [w for w in seed if w in hwA]
    agree = sum(seed[w][0] in hwA[w] for w in shared)
    out['sets'][name] = dict(sorted(seed.items(), key=lambda x: -cnt[x[0]]))
    out['stats'][name] = {'n_words': len(seed), 'token_frac': sum(cnt[w] for w in seed) / n_tok,
                          'by_cat': {c: sum(1 for w in seed if seed[w] == [c]) for c in cats},
                          'hw_shared': len(shared), 'hw_agree': agree,
                          'hw_disagree': [(w, sorted(hwA[w])) for w in shared if seed[w][0] not in hwA[w]]}
    print(f'{name}: {len(seed)} words, {out["stats"][name]["token_frac"]:.3f} of train tokens, by_cat={out["stats"][name]["by_cat"]}, '
          f'hand-written agreement {agree}/{len(shared)}; disagreements {out["stats"][name]["hw_disagree"]}')
out['words'] = {w: {'count': cnt[w], 'tags': dict(dist[w].most_common())} for w in cnt if cnt[w] >= args.min_count}
os.makedirs(os.path.dirname(args.out), exist_ok=True)
json.dump(out, open(args.out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
