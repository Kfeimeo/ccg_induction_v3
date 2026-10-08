"""Seed-lexicon (anchors) comparison: search complexity and result quality, base vs anchored.
Reads results/induction/<config>/seed*.json; prints a markdown table (mean±sd over seeds)."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ccg.evaluate import mean_std

configs = sys.argv[1:] or ['left_A_SA_d4_le10', 'left_A_SA_d4_le10_ctr', 'left_A_SA_anch_d4_le10',
                           'left_A_SA_seedC_d4_le10', 'left_A_SA_seedH_d4_le10']


def f(vals, nd=2):
    vals = [v for v in vals if v is not None]
    if not vals:
        return '–'
    m, sd = mean_std(vals)
    return f'{m:.{nd}f}±{sd:.{nd}f}' if len(vals) > 1 else f'{m:.{nd}f}'


def op_total(r, op):
    return sum(h.get('op_seconds', {}).get(op, 0.0) for h in r['history']) if any('op_seconds' in h for h in r['history']) else None


print('| config | seeds | anchor words | train s | EM s* | prune s | split s | fail s | pair s | merge s | ΔMDL evals | eval·sents | rounds | cats | entries | avg/word | \\|Q\\| | b | train parsed | dev cov | in-lex cov | UAS cov | UAS all | MDL |')
print('|' + '---|' * 24)
for c in configs:
    rows = [json.load(open(p)) for p in sorted(glob.glob(f'results/induction/{c}/seed*.json'))]
    rows = [r for r in rows if 'final' in r]
    if not rows:
        continue
    ops = {op: [op_total(r, op) for r in rows] for op in ('prune', 'split', 'fail', 'pair', 'merge')}
    em = [r['train_time_s'] - sum(op_total(r, o) or 0 for o in ops) if op_total(r, 'prune') is not None else None for r in rows]
    ev = [max((h.get('n_evals', 0) for h in r['history']), default=None) or None for r in rows]
    evs = [max((h.get('n_eval_sents', 0) for h in r['history']), default=None) or None for r in rows]
    print(f"| {c} | {len(rows)} | {rows[0].get('n_anchor_words', 0)} | {f([r['train_time_s'] for r in rows], 0)} | {f(em, 0)} | "
          + ' | '.join(f(ops[o], 0) for o in ops) + f" | {f(ev, 0)} | {f(evs, 0)} | {f([len(r['history']) for r in rows], 1)} | "
          f"{f([r['final']['n_categories'] for r in rows], 0)} | {f([r['final']['n_entries'] for r in rows], 0)} | {f([r['final']['avg_cats_per_word'] for r in rows])} | "
          f"{f([r['final']['Q_mean'] for r in rows], 1)} | {f([r['final']['b_mean'] for r in rows])} | {f([r['final']['parsed'] / r['final']['n_sent'] for r in rows], 3)} | "
          f"{f([r['dev']['coverage'] for r in rows], 3)} | {f([r['dev']['coverage_in_lex'] for r in rows], 3)} | {f([r['dev']['uas_covered'] for r in rows], 3)} | "
          f"{f([r['dev']['uas_all'] for r in rows], 3)} | {f([r['final']['total'] for r in rows], 0)} |")
print('\n*EM s = train time minus the logged proposal/prune/merge seconds (EM + lattice rebuilds + bookkeeping); '
      'op seconds and ΔMDL evaluation counts exist only for runs made with the current code (–: not logged).')
