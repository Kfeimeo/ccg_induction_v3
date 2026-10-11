# ccg_induction_v3 — 严格增量 CCG 的无监督范畴归纳

报告：`REPORT.md`（方法、偏离说明、默认值、全部结果表、结论）。汇总表：`results/tables.md`。
最新实验：§7.5 超标注器种子词典（Hol-CCG 的 NP / N 标注作锚定，栈 2 与 Eisner 正规形式两种解析器）；对比表 `python scripts/compare_anchors.py`。

```
pip install numpy pyyaml pytest
python3 scripts/prepare_data.py                 # 需要 data/raw/en_gum-ud-{train,dev,test}.conllu（UD English-GUM）
python3 -m pytest tests -q
python3 scripts/run_upper_bound.py              # §5 手写词库上界
python3 scripts/run_synthetic.py --seeds 1,2,3,4,5,6,7,8 --init_support 4 --outer 15 \
    --set mdl.curriculum=null --set mdl.patience=100 --set mdl.pair_proposals=false      # §7.3 人造数据门槛实验
python3 scripts/run_induction.py --group A --seeds 1   # 一个配置的一个种子（其它参数见 scripts/jobs*.txt）
python3 scripts/run_induction.py --anchors closed --seeds 1,2,3   # 种子词典：锚定 38 个高频单范畴功能词（ccg/seeds.py；--anchors the|closed|hw1）
python3 scripts/compare_anchors.py   # 锚定 vs 基线：搜索复杂度与结果对比表
E:/anaconda3/envs/ccg/python.exe scripts/supertag_gum.py --splits train,dev,test   # Hol-CCG 超标注（../hol-ccg，conda env ccg）-> data/supertags/
python3 scripts/build_supertag_seeds.py          # 超标注器种子集 stNP / stNPN -> data/supertags/seed_sets.json
python3 scripts/run_induction.py --system stack --max_stack 2 --anchors stNP --seeds 1,2   # 超标注器种子集 x 栈系统 / --system cky_nf（Eisner 正规形式）
python3 scripts/aggregate.py results/induction/left_A_SA_d4_le10
python3 scripts/run_phenomena.py --models 'results/induction/*/seed1_model.pkl'
python3 scripts/run_test.py --model results/induction/left_A_SA_d4_le10/seed1_model.pkl
python3 scripts/make_tables.py
```

目录：`ccg/`（category, combine, lattice, deps, model, em, mdl, cky, phenomena…）、`scripts/`、`tests/`、`configs/default.yaml`、`results/`、`native/`（C++ 扩展）。

## C++ 扩展（left / stack / cky 三个解析系统的原生实现）

`native/` 用 nanobind 重写了三个解析系统的热点：格构造（`build_lattice`、`build_stack_lattice`）、CKY 图（`Chart`，含 Eisner 正规形式）、前向后向 / 内外算法、Viterbi、E 步统计量，以及提议步骤用到的无剪枝状态集搜索（`forward_states`、`suffix_completes`、`oracle_check`）。范畴仍以项目原有的 Python 对象（嵌套元组、`Stack`）跨越边界；模型参数从 Python `Model` / `CKYModel` 复制到原生打分表，按 `Model._v` 版本号缓存。纯 Python 实现保留为参考实现（`*_py` 函数），`ccg/native.py` 是桥接层；扩展可导入时各模块自动转发，`CCG_NATIVE=0` 可关闭。

```
# Windows + MSVC（VS 2022+，含 C++ 工具集与 CMake/Ninja 组件）+ vcpkg（vcpkg install nanobind）+ 运行项目的 Python
powershell -ExecutionPolicy Bypass -File scripts/build_native.ps1 [-Python E:\anaconda3\python.exe] [-Vcpkg E:\vcpkg]
python -m pytest tests/test_native.py -q      # 与 Python 参考实现逐项对比（格结构、Z、后验、Viterbi、E 步）
```

构建产物 `ccg/_ccg_native.cp3XX-win_amd64.pyd` 与解释器版本绑定（已在 .gitignore 中）；换 Python 需重新构建。构建脚本不使用 vcpkg 工具链文件（其 FindPython 包装会强制使用 vcpkg 自带的 Python 头文件），而是把 vcpkg 安装前缀加入 `CMAKE_PREFIX_PATH`。目前仅支持 Windows。
