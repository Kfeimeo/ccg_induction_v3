"""Aggregate seed*.json of one induction config directory into summary.json (mean±sd)."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ccg.evaluate import mean_std

out = sys.argv[1]
rows = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(out, 'seed*.json')))]
rows = [r for r in rows if 'final' in r]
if not rows:
    sys.exit(0)


def agg(key_fn):
    vals = [key_fn(r) for r in rows]
    m, sd = mean_std(vals)
    return {'mean': m, 'sd': sd, 'values': vals}


summary = {
    'name': os.path.basename(out), 'seeds': [r['seed'] for r in rows],
    'objective': agg(lambda r: r['final']['total']),
    'train_parsed': agg(lambda r: r['final']['parsed'] / r['final']['n_sent']),
    'n_categories': agg(lambda r: r['final']['n_categories']),
    'avg_cats_per_word': agg(lambda r: r['final']['avg_cats_per_word']),
    'Q_mean': agg(lambda r: r['final']['Q_mean']), 'b_mean': agg(lambda r: r['final']['b_mean']),
    'dev_coverage': agg(lambda r: r['dev']['coverage']),
    'dev_coverage_in_lex': agg(lambda r: r['dev']['coverage_in_lex']),
    'dev_uas_all': agg(lambda r: r['dev']['uas_all']),
    'dev_uas_covered': agg(lambda r: r['dev']['uas_covered']),
    'dev_ppl': agg(lambda r: r['dev']['ppl_per_word']),
    'dev8_coverage': agg(lambda r: r['dev_le8']['coverage']) if rows[0].get('dev_le8') else None,
    'dev8_uas_all': agg(lambda r: r['dev_le8']['uas_all']) if rows[0].get('dev_le8') else None,
    'train_time_s': agg(lambda r: r['train_time_s']),
    'mdl_selected_seed': min(rows, key=lambda r: r['final']['total'])['seed'],
    'baselines': rows[0]['dev'].get('baselines'),
}
json.dump(summary, open(os.path.join(out, 'summary.json'), 'w'), indent=1)
print(os.path.basename(out), 'seeds', summary['seeds'], 'obj', round(summary['objective']['mean']), 'dev cov', round(summary['dev_coverage']['mean'], 3),
      'UAS all', round(summary['dev_uas_all']['mean'], 3), 'UAS cov', round(summary['dev_uas_covered']['mean'], 3))
