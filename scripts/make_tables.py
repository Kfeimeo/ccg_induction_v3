"""Aggregate results/* into markdown tables for the report."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def f(x, d=3):
    return 'n/a' if x is None else (f'{x:.{d}f}' if isinstance(x, float) else str(x))


def ms(a, d=3):
    return 'n/a' if not a else f"{a['mean']:.{d}f}±{a['sd']:.{d}f}"


out = []
# ---- upper bound
ub = json.load(open('results/upper_bound/summary.json')) if os.path.exists('results/upper_bound/summary.json') else []
if ub:
    out.append('## 手写上界（dev）\n')
    out.append('| variant | atoms | len | words | entries | cov(all) | cov(in-lex) | n in-lex | UAS all | UAS covered | UAS in-lex | SA amb/applied | |Q| | b | LB | RB | RB(cov) | rand |')
    out.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for r in ub:
        b = r['baselines']
        out.append(f"| {r['variant']} | {r['atoms']} | ≤{r['max_len']} | {r['lex_words']} | {r['lex_entries']} | {f(r['coverage'])} | {f(r['coverage_in_lex'])} | {r['n_in_lex']} | {f(r['uas_all'])} | {f(r['uas_covered'])} | {f(r['uas_all_in_lex'])} | {r['sa_ambiguous']}/{r['sa_applied']} | {f(r['lat_Q_unpruned_mean'],1)} | {f(r['lat_b_mean'],2)} | {f(b['left_branching']['uas_all'])} | {f(b['right_branching']['uas_all'])} | {f(b['right_branching']['uas_covered_subset'])} | {f(b['random_tree']['uas_all'])} |")
# ---- synthetic
SYN_LABEL = {'synthetic_nocurr.json': 'S1 无课程（门槛实验）', 'synthetic_final.json': 'S2 真实数据调度', 'synthetic_conditional.json': '条件式目标（S1 调度）'}
for p in sorted(glob.glob('results/synthetic/synthetic*.json')):
    if os.path.basename(p) not in SYN_LABEL:
        continue
    d = json.load(open(p))
    out.append(f'\n## 人造数据 {SYN_LABEL[os.path.basename(p)]} ({os.path.basename(p)})\n')
    out.append('| seed | total bits | entries | cats | parsed | majority acc | derivation recovery |')
    out.append('|---|---|---|---|---|---|---|')
    for r in d['rows']:
        out.append(f"| {r['seed']} | {r['total_bits']:.0f} | {r['n_entries']} | {r['n_categories']} | {r['parsed']} | {f(r['majority_acc'],2)} | {f(r.get('derivation_recovery'))} |")
    out.append(f"\nmean±sd: majority acc {f(d['majority_acc_mean'])}±{f(d['majority_acc_sd'])}; derivation recovery {f(d.get('deriv_rec_mean'))}±{f(d.get('deriv_rec_sd'))}; MDL-selected seed {d.get('mdl_selected_seed')}")
# ---- induction
rows = []
for p in sorted(glob.glob('results/induction/*/summary.json')):
    rows.append(json.load(open(p)))
if rows:
    out.append('\n## 归纳结果（dev，均值±标准差 over seeds）\n')
    out.append('| config | seeds | objective (bits) | train parsed | #cats | cats/word | |Q| | b | dev cov | dev cov in-lex | UAS all | UAS covered | ppl | dev≤8 cov | dev≤8 UAS | MDL-sel seed |')
    out.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        out.append(f"| {r['name']} | {len(r['seeds'])} | {ms(r['objective'],0)} | {ms(r['train_parsed'])} | {ms(r['n_categories'],1)} | {ms(r['avg_cats_per_word'],2)} | {ms(r['Q_mean'],1)} | {ms(r['b_mean'],2)} | {ms(r['dev_coverage'])} | {ms(r['dev_coverage_in_lex'])} | {ms(r['dev_uas_all'])} | {ms(r['dev_uas_covered'])} | {ms(r['dev_ppl'],1)} | {ms(r['dev8_coverage'])} | {ms(r['dev8_uas_all'])} | {r['mdl_selected_seed']} |")
    b = rows[0].get('baselines')
    if b:
        out.append(f"\nBaselines on dev (UAS all sentences): left-branching {f(b['left_branching']['uas_all'])}, right-branching {f(b['right_branching']['uas_all'])}, random {f(b['random_tree']['uas_all'])}±{f(b['random_tree']['uas_all_std'])}")
# ---- phenomena
pp = 'results/phenomena/phenomena_results.json'
if os.path.exists(pp):
    res = json.load(open(pp))
    out.append('\n## 现象测试集\n')
    for name, r in res.items():
        out.append(f'\n### {name}\n')
        out.append('| phenomenon | group | n (dev/train/constructed) | L1 accept | L2 reject neg | L3 pred-arg | L4 no CS | pair acc | in-lex n | L1 in-lex | L3 in-lex |')
        out.append('|---|---|---|---|---|---|---|---|---|---|---|')
        for ph, v in r.items():
            out.append(f"| {ph} | {v['group']} | {v['n']} ({v['n_dev']}/{v['n_train']}/{v['n_constructed']}) | {f(v['L1_accept'],2)} | {f(v['L2_reject_neg'],2)} | {f(v['L3_pred_arg'],2)} | {f(v['L4_no_cs'],2)} | {f(v['pair_acc'],2)} | {v['n_in_lex']} | {f(v['L1_in_lex'],2)} | {f(v['L3_in_lex'],2)} |")
# ---- top categories of the MDL-selected main seed
for p in sorted(glob.glob('results/induction/*/summary.json')):
    r = json.load(open(p))
    sp = os.path.join(os.path.dirname(p), f"seed{r['mdl_selected_seed']}.json")
    if not os.path.exists(sp):
        continue
    d = json.load(open(sp))
    out.append(f"\n## 高频范畴（{r['name']}, MDL-selected seed {r['mdl_selected_seed']}）\n")
    out.append('| # | category | expected count | 20 words |')
    out.append('|---|---|---|---|')
    for i, t in enumerate(d['top_categories'][:50]):
        out.append(f"| {i+1} | `{t['category']}` | {t['count']} | {', '.join(t['words'])} |")
    fc = d['dev_failure_clusters']
    out.append(f"\n失败日志汇总（dev, {d['n_dev_failures']} failures）: by UPOS/deprel of failing word: {fc['by_upos_deprel'][:15]}; by word: {fc['by_word'][:15]}; by position: {fc['by_position']}\n")
open('results/tables.md', 'w').write('\n'.join(out))
print('\n'.join(out)[:3000])
