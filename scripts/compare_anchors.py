"""Seed-lexicon (anchors) comparison: search complexity and result quality, base vs anchored.
Reads results/induction/<config>/seed*.json (+ seed*_model_hwmap.json from scripts/analyze_lexicon.py
when present); prints a markdown table (mean±sd over seeds).
Usage: python scripts/compare_anchors.py [config ...]   (default: hand-written seed sets §7.4 + supertagger seed sets §7.5)"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ccg.evaluate import mean_std

DEFAULT = ['left_A_SA_d4_le10', 'left_A_SA_d4_le10_ctr', 'left_A_SA_anch_d4_le10', 'left_A_SA_seedC_d4_le10', 'left_A_SA_seedH_d4_le10',
           'left_A_SA_seedNP_d4_le10', 'left_A_SA_seedNPN_d4_le10',
           'stack2_A_SA_d4_le10', 'stack2_A_SA_seedNP_d4_le10', 'stack2_A_SA_seedNPN_d4_le10',
           'cky_nf_A_SA_d4_le8', 'cky_nf_A_SA_d4_le10', 'cky_nf_A_SA_seedNP_d4_le10', 'cky_nf_A_SA_seedNPN_d4_le10']
configs = sys.argv[1:] or DEFAULT


def f(vals, nd=2):
    vals = [v for v in vals if v is not None]
    if not vals:
        return '–'
    m, sd = mean_std(vals)
    return f'{m:.{nd}f}±{sd:.{nd}f}' if len(vals) > 1 else f'{m:.{nd}f}'


def op_total(r, op):
    return sum(h.get('op_seconds', {}).get(op, 0.0) for h in r['history']) if any('op_seconds' in h for h in r['history']) else None


def load(path):
    return json.load(open(path, encoding='utf-8'))


print('| config | seeds | anchor words | train s | EM s* | prune s | split s | fail s | pair s | merge s | ΔMDL evals | eval·sents | rounds | cats | entries | avg/word | \\|Q\\| | b | train parsed | dev cov | in-lex cov | UAS cov | RB (same subset) | UAS all | hw exact | hw shape | MDL |')
print('|' + '---|' * 27)
for c in configs:
    rows = [load(p) for p in sorted(glob.glob(f'results/induction/{c}/seed*.json')) if '_hwmap' not in p]
    rows = [r for r in rows if 'final' in r]
    if not rows:
        continue
    hw = [load(p) for p in sorted(glob.glob(f'results/induction/{c}/seed*_model_hwmap.json'))]
    ops = {op: [op_total(r, op) for r in rows] for op in ('prune', 'split', 'fail', 'pair', 'merge')}
    em = [r['train_time_s'] - sum(op_total(r, o) or 0 for o in ops) if op_total(r, 'prune') is not None else None for r in rows]
    ev = [max((h.get('n_evals', 0) for h in r['history']), default=None) or None for r in rows]
    evs = [max((h.get('n_eval_sents', 0) for h in r['history']), default=None) or None for r in rows]
    rb = [r['dev'].get('baselines', {}).get('right_branching', {}).get('uas_covered_subset') for r in rows]
    print(f"| {c} | {len(rows)} | {rows[0].get('n_anchor_words', 0)} | {f([r['train_time_s'] for r in rows], 0)} | {f(em, 0)} | "
          + ' | '.join(f(ops[o], 0) for o in ops) + f" | {f(ev, 0)} | {f(evs, 0)} | {f([len(r['history']) for r in rows], 1)} | "
          f"{f([r['final']['n_categories'] for r in rows], 0)} | {f([r['final']['n_entries'] for r in rows], 0)} | {f([r['final']['avg_cats_per_word'] for r in rows])} | "
          f"{f([r['final']['Q_mean'] for r in rows], 1)} | {f([r['final']['b_mean'] for r in rows])} | {f([r['final']['parsed'] / r['final']['n_sent'] for r in rows], 3)} | "
          f"{f([r['dev']['coverage'] for r in rows], 3)} | {f([r['dev']['coverage_in_lex'] for r in rows], 3)} | {f([r['dev']['uas_covered'] for r in rows], 3)} | "
          f"{f(rb, 3)} | {f([r['dev']['uas_all'] for r in rows], 3)} | {f([h['exact'] for h in hw], 3)} | {f([h['shape'] for h in hw], 3)} | "
          f"{f([r['final']['total'] for r in rows], 0)} |")
print('\n*EM s = train time minus the logged proposal/prune/merge seconds (EM + lattice rebuilds + bookkeeping); '
      'op seconds and ΔMDL evaluation counts exist only for runs made with the current code (–: not logged). '
      'hw exact / shape: agreement of the majority category with the hand-written lexicon over shared words '
      '(scripts/analyze_lexicon.py; –: not computed). RB: right-branching UAS on the same covered dev subset.')
