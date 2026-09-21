## 手写上界（dev）

| variant | atoms | len | words | entries | cov(all) | cov(in-lex) | n in-lex | UAS all | UAS covered | UAS in-lex | SA amb/applied | |Q| | b | LB | RB | RB(cov) | rand |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SA | B | ≤10 | 500 | 1790 | 0.208 | 0.652 | 92 | 0.147 | 0.929 | 0.564 | 0/55 | 2.8 | 0.37 | 0.068 | 0.363 | 0.409 | 0.154 |
| SA | B | ≤8 | 500 | 1790 | 0.262 | 0.675 | 83 | 0.204 | 0.930 | 0.596 | 0/50 | 2.9 | 0.38 | 0.069 | 0.380 | 0.426 | 0.172 |
| SA | A | ≤10 | 500 | 1743 | 0.215 | 0.674 | 92 | 0.144 | 0.881 | 0.552 | 0/55 | 2.6 | 0.40 | 0.068 | 0.363 | 0.403 | 0.154 |
| SA | A | ≤8 | 500 | 1743 | 0.271 | 0.699 | 83 | 0.201 | 0.882 | 0.587 | 0/50 | 2.6 | 0.41 | 0.069 | 0.380 | 0.418 | 0.172 |
| TR | B | ≤10 | 500 | 1990 | 0.225 | 0.707 | 92 | 0.160 | 0.928 | 0.611 | 0/12 | 3.2 | 0.37 | 0.068 | 0.363 | 0.404 | 0.154 |
| TR | B | ≤8 | 500 | 1990 | 0.285 | 0.735 | 83 | 0.224 | 0.929 | 0.653 | 0/8 | 3.2 | 0.39 | 0.069 | 0.380 | 0.419 | 0.172 |
| TR | A | ≤10 | 500 | 1943 | 0.232 | 0.728 | 92 | 0.157 | 0.884 | 0.600 | 0/11 | 2.9 | 0.39 | 0.068 | 0.363 | 0.398 | 0.154 |
| TR | A | ≤8 | 500 | 1943 | 0.294 | 0.759 | 83 | 0.221 | 0.886 | 0.644 | 0/7 | 2.9 | 0.41 | 0.069 | 0.380 | 0.412 | 0.172 |

## 人造数据 synthetic.json

| seed | total bits | entries | cats | parsed | majority acc | derivation recovery |
|---|---|---|---|---|---|---|
| 1 | 9813 | 136 | 50 | 500 | 0.15 | n/a |

mean±sd: majority acc 0.150±0.000; derivation recovery n/a±n/a; MDL-selected seed None

## 人造数据 synthetic_anneal.json

| seed | total bits | entries | cats | parsed | majority acc | derivation recovery |
|---|---|---|---|---|---|---|
| 1 | 7525 | 58 | 29 | 500 | 0.25 | n/a |

mean±sd: majority acc 0.250±0.000; derivation recovery n/a±n/a; MDL-selected seed None

## 人造数据 synthetic_hard.json

| seed | total bits | entries | cats | parsed | majority acc | derivation recovery |
|---|---|---|---|---|---|---|
| 1 | 8852 | 93 | 33 | 500 | 0.65 | n/a |

mean±sd: majority acc 0.650±0.000; derivation recovery n/a±n/a; MDL-selected seed None

## 人造数据 synthetic_k2.json

| seed | total bits | entries | cats | parsed | majority acc | derivation recovery |
|---|---|---|---|---|---|---|
| 1 | 26079 | 28 | 11 | 307 | 0.40 | n/a |

mean±sd: majority acc 0.400±0.000; derivation recovery n/a±n/a; MDL-selected seed None

## 人造数据 synthetic_k3.json

| seed | total bits | entries | cats | parsed | majority acc | derivation recovery |
|---|---|---|---|---|---|---|
| 1 | 6285 | 41 | 23 | 500 | 0.60 | n/a |
| 2 | 6206 | 34 | 17 | 500 | 0.15 | n/a |
| 3 | 41602 | 21 | 16 | 80 | 0.10 | n/a |
| 4 | 28671 | 27 | 12 | 282 | 0.15 | n/a |
| 5 | 26703 | 25 | 11 | 301 | 0.20 | n/a |

mean±sd: majority acc 0.240±0.183; derivation recovery n/a±n/a; MDL-selected seed None

## 人造数据 synthetic_k4.json

| seed | total bits | entries | cats | parsed | majority acc | derivation recovery |
|---|---|---|---|---|---|---|
| 1 | 8015 | 35 | 10 | 500 | 0.10 | 0.232 |
| 2 | 16163 | 38 | 15 | 393 | 0.35 | 0.541 |
| 3 | 10799 | 31 | 10 | 458 | 0.10 | 0.531 |
| 4 | 7508 | 33 | 9 | 497 | 0.10 | 0.439 |
| 5 | 7889 | 48 | 14 | 500 | 0.55 | 0.563 |
| 6 | 6670 | 26 | 10 | 500 | 0.55 | 0.861 |
| 7 | 6091 | 20 | 9 | 500 | 0.60 | 0.972 |
| 8 | 7509 | 31 | 9 | 500 | 0.45 | 0.934 |

mean±sd: majority acc 0.350±0.206; derivation recovery 0.634±0.245; MDL-selected seed 7

## 人造数据 synthetic_k40.json

| seed | total bits | entries | cats | parsed | majority acc | derivation recovery |
|---|---|---|---|---|---|---|
| 1 | 8117 | 108 | 52 | 500 | 0.20 | n/a |

mean±sd: majority acc 0.200±0.000; derivation recovery n/a±n/a; MDL-selected seed None

## 人造数据 synthetic_k5.json

| seed | total bits | entries | cats | parsed | majority acc | derivation recovery |
|---|---|---|---|---|---|---|
| 1 | 7306 | 20 | 6 | 500 | 0.35 | 0.972 |
| 2 | 6963 | 47 | 19 | 500 | 0.20 | 0.319 |
| 3 | 6367 | 38 | 17 | 500 | 0.55 | 0.898 |
| 4 | 7446 | 37 | 13 | 500 | 0.10 | 0.427 |
| 5 | 8100 | 32 | 11 | 500 | 0.35 | 0.531 |
| 6 | 8677 | 28 | 13 | 481 | 0.70 | 0.462 |
| 7 | 7124 | 33 | 13 | 493 | 0.60 | 0.960 |
| 8 | 9461 | 38 | 9 | 500 | 0.10 | 0.239 |

mean±sd: majority acc 0.369±0.215; derivation recovery 0.601±0.278; MDL-selected seed 3

## 人造数据 synthetic_k6.json

| seed | total bits | entries | cats | parsed | majority acc | derivation recovery |
|---|---|---|---|---|---|---|
| 1 | 8287 | 77 | 27 | 500 | 0.45 | 0.301 |
| 2 | 8090 | 38 | 14 | 486 | 0.20 | 0.522 |
| 3 | 7017 | 49 | 18 | 500 | 0.10 | 0.479 |
| 4 | 6384 | 38 | 15 | 500 | 0.80 | 0.972 |
| 5 | 8163 | 42 | 14 | 500 | 0.15 | 0.343 |
| 6 | 7934 | 57 | 26 | 500 | 0.35 | 0.667 |
| 7 | 6523 | 50 | 21 | 500 | 0.10 | 0.335 |
| 8 | 7561 | 55 | 18 | 500 | 0.35 | 0.584 |

mean±sd: majority acc 0.312±0.220; derivation recovery 0.525±0.208; MDL-selected seed 4

## 人造数据 synthetic_oracle.json

| seed | total bits | entries | cats | parsed | majority acc | derivation recovery |
|---|---|---|---|---|---|---|
| 1 | 8408 | 100 | 34 | 500 | 0.35 | n/a |

mean±sd: majority acc 0.350±0.000; derivation recovery n/a±n/a; MDL-selected seed None

## 人造数据 synthetic_small21.json

| seed | total bits | entries | cats | parsed | majority acc | derivation recovery |
|---|---|---|---|---|---|---|
| 1 | 7038 | 51 | 14 | 500 | 0.75 | n/a |

mean±sd: majority acc 0.750±0.000; derivation recovery n/a±n/a; MDL-selected seed None

## 归纳结果（dev，均值±标准差 over seeds）

| config | seeds | objective (bits) | train parsed | #cats | cats/word | |Q| | b | dev cov | dev cov in-lex | UAS all | UAS covered | ppl | dev≤8 cov | dev≤8 UAS | MDL-sel seed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| left_A_SA_d4_le10_smoke | 1 | 49473±0 | 0.133±0.000 | 183.0±0.0 | 3.79±0.00 | 2.6±0.0 | 0.27±0.00 | 0.003±0.000 | 0.032±0.000 | 0.001±0.000 | 0.500±0.000 | 4.3±0.0 | 0.005±0.000 | 0.002±0.000 | 1 |

Baselines on dev (UAS all sentences): left-branching 0.068, right-branching 0.363, random 0.154±0.012

## 现象测试集


### handwritten_SA

| phenomenon | group | n (dev/train/constructed) | L1 accept | L2 reject neg | L3 pred-arg | L4 no CS | pair acc | in-lex n | L1 in-lex | L3 in-lex |
|---|---|---|---|---|---|---|---|---|---|---|
| argument_structure | gate | 95 (95/0/0) | 0.24 | 0.99 | 0.22 | 0.21 | 0.24 | 35 | 0.66 | 0.60 |
| modifiers | gate | 142 (142/0/0) | 0.25 | 0.83 | 0.21 | 0.21 | 0.08 | 56 | 0.64 | 0.54 |
| determiners | gate | 115 (115/0/0) | 0.23 | 0.96 | 0.23 | 0.22 | 0.18 | 39 | 0.67 | 0.67 |
| aux_sequence | gate | 155 (155/0/0) | 0.35 | 0.97 | 0.34 | 0.30 | 0.33 | 73 | 0.74 | 0.71 |
| vp_coordination | discriminating | 20 (4/16/0) | 0.10 | 1.00 | 0.00 | 0.00 | 0.10 | 4 | 0.50 | 0.00 |
| right_node_raising | discriminating | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 4 | 0.00 | 0.00 |
| nonconstituent_coordination | discriminating | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 5 | 0.00 | 0.00 |
| subject_relative | discriminating | 18 (1/17/0) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1 | 0.00 | 0.00 |
| object_relative | discriminating | 20 (7/13/0) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 5 | 0.00 | 0.00 |
| valency_eat | discriminating | 3 (0/3/0) | 0.33 | 1.00 | 0.00 | 0.00 | 0.33 | 1 | 1.00 | 0.00 |
| multifunction_that | discriminating | 34 (34/0/0) | 0.38 | 0.68 | 0.35 | 0.38 | 0.06 | 19 | 0.68 | 0.63 |
| nested_clause | discriminating | 32 (32/0/0) | 0.31 | 0.94 | 0.25 | 0.12 | 0.25 | 18 | 0.56 | 0.44 |
| parasitic_gap | stretch | 3 (0/0/3) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1 | 0.00 | 0.00 |
| gapping | stretch | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 4 | 0.00 | 0.00 |
| comparative | stretch | 18 (1/12/5) | 0.22 | 1.00 | 0.17 | 0.22 | 0.22 | 4 | 1.00 | 0.75 |

### handwritten_TR

| phenomenon | group | n (dev/train/constructed) | L1 accept | L2 reject neg | L3 pred-arg | L4 no CS | pair acc | in-lex n | L1 in-lex | L3 in-lex |
|---|---|---|---|---|---|---|---|---|---|---|
| argument_structure | gate | 95 (95/0/0) | 0.25 | 0.99 | 0.24 | 0.22 | 0.25 | 35 | 0.69 | 0.66 |
| modifiers | gate | 142 (142/0/0) | 0.26 | 0.82 | 0.22 | 0.23 | 0.08 | 56 | 0.66 | 0.55 |
| determiners | gate | 115 (115/0/0) | 0.23 | 0.96 | 0.23 | 0.23 | 0.19 | 39 | 0.69 | 0.69 |
| aux_sequence | gate | 155 (155/0/0) | 0.36 | 0.96 | 0.35 | 0.34 | 0.33 | 73 | 0.77 | 0.74 |
| vp_coordination | discriminating | 20 (4/16/0) | 0.10 | 1.00 | 0.00 | 0.00 | 0.10 | 4 | 0.50 | 0.00 |
| right_node_raising | discriminating | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 4 | 0.00 | 0.00 |
| nonconstituent_coordination | discriminating | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 5 | 0.00 | 0.00 |
| subject_relative | discriminating | 18 (1/17/0) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1 | 0.00 | 0.00 |
| object_relative | discriminating | 20 (7/13/0) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 5 | 0.00 | 0.00 |
| valency_eat | discriminating | 3 (0/3/0) | 0.33 | 1.00 | 0.00 | 0.00 | 0.33 | 1 | 1.00 | 0.00 |
| multifunction_that | discriminating | 34 (34/0/0) | 0.38 | 0.68 | 0.35 | 0.38 | 0.06 | 19 | 0.68 | 0.63 |
| nested_clause | discriminating | 32 (32/0/0) | 0.31 | 0.94 | 0.25 | 0.22 | 0.25 | 18 | 0.56 | 0.44 |
| parasitic_gap | stretch | 3 (0/0/3) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1 | 0.00 | 0.00 |
| gapping | stretch | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 4 | 0.00 | 0.00 |
| comparative | stretch | 18 (1/12/5) | 0.22 | 1.00 | 0.17 | 0.22 | 0.22 | 4 | 1.00 | 0.75 |

## 高频范畴（left_A_SA_d4_le10_smoke, MDL-selected seed 1）

| # | category | expected count | 20 words |
|---|---|---|---|
| 1 | `NP/NP` | 23.9 | that, he, it, this, she, own, no, equipment, my |
| 2 | `N` | 17.1 | i, dad, yeah, american, all, judy, good, wait, see, throat, does, not |
| 3 | `S/NP` | 14.1 | oh, and, so, this, that, it, later |
| 4 | `NP` | 14.0 | 's |
| 5 | `NP/N` | 10.0 | is, i, the, was, at |
| 6 | `NP/S` | 7.0 | <C0>, one, you, do |
| 7 | `S` | 7.0 | i, have, erasmus, yeah, n't, 's |
| 8 | `S\NP` | 6.0 | <C7> |
| 9 | `S\N` | 5.0 | this, now, 'll, will, enough |
| 10 | `S\(N\NP)` | 4.0 | know |
| 11 | `N\S` | 4.0 | n't |
| 12 | `(S\NP)/N` | 3.0 | to, an |
| 13 | `N\N` | 3.0 | four, <C21>, <C9> |
| 14 | `(S\N)/NP` | 3.0 | have, to |
| 15 | `(S\N)\NP` | 3.0 | do, the |
| 16 | `N\NP` | 3.0 | <C7>, just |
| 17 | `(NP/NP)/S` | 3.0 | great |
| 18 | `NP/((NP/NP)/S)` | 3.0 | is |
| 19 | `(S\NP)\(S/N)` | 2.0 | do |
| 20 | `S/S` | 2.0 | <C6> |
| 21 | `S/(S/S)` | 2.0 | the |
| 22 | `(N\NP)\NP` | 1.0 | they |
| 23 | `NP\NP` | 1.0 | on |
| 24 | `(S\S)/S` | 1.0 | is |
| 25 | `N/(NP/S)` | 1.0 | was |
| 26 | `S/N` | 1.0 | she |
| 27 | `S\(NP\NP)` | 1.0 | uh |
| 28 | `NP\(N\NP)` | 1.0 | were |
| 29 | `(NP\N)/N` | 1.0 | know |
| 30 | `N/((NP\N)/N)` | 1.0 | you |
| 31 | `(NP\N)/NP` | 1.0 | mean |
| 32 | `S\(S\N)` | 1.0 | way |
| 33 | `S/(NP/N)` | 1.0 | this |
| 34 | `NP/(S/NP)` | 1.0 | till |
| 35 | `((S\S)/NP)/N` | 1.0 | 'll |
| 36 | `N\(NP\NP)` | 1.0 | the |
| 37 | `(NP\NP)\S` | 1.0 | put |
| 38 | `(S\NP)/(NP/S)` | 1.0 | all |
| 39 | `S\S` | 1.0 | <C20> |
| 40 | `(S\S)/N` | 1.0 | she |
| 41 | `(S\N)/S` | 1.0 | of |
| 42 | `NP/(N\N)` | 1.0 | 's |
| 43 | `N/NP` | 1.0 | i |
| 44 | `S\(NP/N)` | 0.9 | dad |

失败日志汇总（dev, 30 failures）: by UPOS/deprel of failing word: [['END/END', 7], ['ADV/advmod', 4], ['AUX/aux', 3], ['PRON/nsubj', 3], ['VERB/root', 2], ['AUX/cop', 2], ['ADJ/root', 2], ['AUX/root', 1], ['AUX/ccomp', 1], ['NOUN/root', 1], ['DET/obj', 1], ['ADJ/parataxis', 1], ['DET/det', 1], ['VERB/xcomp', 1]]; by word: [['<END>', 7], ['right', 3], ["'re", 2], ['a', 2], ['’s', 2], ["'ll", 1], ['are', 1], ['care', 1], ["'s", 1], ['i', 1], ['thing', 1], ['then', 1], ['little', 1], ['up', 1], ['think', 1]]; by position: [[2, 7], [3, 8], [4, 9], [5, 3], [6, 1], [7, 1], [8, 1]]
