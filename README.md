# ccg_induction_v3 — 严格增量 CCG 的无监督范畴归纳

报告：`REPORT.md`（方法、偏离说明、默认值、全部结果表、结论）。汇总表：`results/tables.md`。

```
pip install numpy pyyaml pytest
python3 scripts/prepare_data.py                 # 需要 data/raw/en_gum-ud-{train,dev,test}.conllu（UD English-GUM）
python3 -m pytest tests -q
python3 scripts/run_upper_bound.py              # §5 手写词库上界
python3 scripts/run_synthetic.py --seeds 1,2,3,4,5,6,7,8 --init_support 4 --outer 15 \
    --set mdl.curriculum=null --set mdl.patience=100 --set mdl.pair_proposals=false      # §7.3 人造数据门槛实验
python3 scripts/run_induction.py --group A --seeds 1   # 一个配置的一个种子（其它参数见 scripts/jobs*.txt）
python3 scripts/aggregate.py results/induction/left_A_SA_d4_le10
python3 scripts/run_phenomena.py --models 'results/induction/*/seed1_model.pkl'
python3 scripts/run_test.py --model results/induction/left_A_SA_d4_le10/seed1_model.pkl
python3 scripts/make_tables.py
```

目录：`ccg/`（category, combine, lattice, deps, model, em, mdl, cky, phenomena…）、`scripts/`、`tests/`、`configs/default.yaml`、`results/`。
