## 手写上界（dev）

| variant | atoms | len | words | entries | cov(all) | cov(in-lex) | n in-lex | UAS all | UAS covered | UAS in-lex | SA amb/applied | |Q| | b | LB | RB | RB(cov) | rand |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SA | B | ≤10 | 500 | 1796 | 0.204 | 0.656 | 90 | 0.146 | 0.928 | 0.567 | 0/54 | 2.9 | 0.37 | 0.068 | 0.363 | 0.407 | 0.154 |
| SA | B | ≤8 | 500 | 1796 | 0.257 | 0.679 | 81 | 0.202 | 0.929 | 0.600 | 0/49 | 2.9 | 0.38 | 0.069 | 0.380 | 0.423 | 0.172 |
| SA | A | ≤10 | 500 | 1749 | 0.211 | 0.678 | 90 | 0.146 | 0.890 | 0.567 | 0/54 | 2.7 | 0.39 | 0.068 | 0.363 | 0.403 | 0.154 |
| SA | A | ≤8 | 500 | 1749 | 0.266 | 0.704 | 81 | 0.204 | 0.893 | 0.605 | 0/49 | 2.7 | 0.40 | 0.069 | 0.380 | 0.418 | 0.172 |
| TR | B | ≤10 | 500 | 1998 | 0.221 | 0.711 | 90 | 0.158 | 0.927 | 0.615 | 0/12 | 3.2 | 0.37 | 0.068 | 0.363 | 0.402 | 0.154 |
| TR | B | ≤8 | 500 | 1998 | 0.280 | 0.741 | 81 | 0.221 | 0.928 | 0.659 | 0/8 | 3.2 | 0.38 | 0.069 | 0.380 | 0.416 | 0.172 |
| TR | A | ≤10 | 500 | 1951 | 0.228 | 0.733 | 90 | 0.158 | 0.892 | 0.615 | 0/12 | 3.0 | 0.39 | 0.068 | 0.363 | 0.398 | 0.154 |
| TR | A | ≤8 | 500 | 1951 | 0.290 | 0.765 | 81 | 0.223 | 0.895 | 0.663 | 0/8 | 3.0 | 0.40 | 0.069 | 0.380 | 0.412 | 0.172 |

## 人造数据 条件式目标（S1 调度） (synthetic_conditional.json)

| seed | total bits | entries | cats | parsed | majority acc | derivation recovery |
|---|---|---|---|---|---|---|
| 1 | 2521 | 39 | 16 | 500 | 0.10 | 0.329 |
| 2 | 1739 | 43 | 21 | 500 | 0.05 | 0.450 |
| 3 | 156 | 20 | 7 | 500 | 0.10 | 0.241 |
| 4 | 1103 | 28 | 11 | 500 | 0.40 | 0.341 |
| 5 | 2318 | 54 | 23 | 500 | 0.10 | 0.448 |
| 6 | 334 | 23 | 11 | 500 | 0.35 | 0.541 |
| 7 | 1713 | 38 | 18 | 500 | 0.10 | 0.284 |
| 8 | 983 | 28 | 12 | 500 | 0.60 | 0.547 |

mean±sd: majority acc 0.225±0.187; derivation recovery 0.398±0.108; MDL-selected seed 3

## 人造数据 S2 真实数据调度 (synthetic_final.json)

| seed | total bits | entries | cats | parsed | majority acc | derivation recovery |
|---|---|---|---|---|---|---|
| 1 | 7042 | 29 | 11 | 500 | 0.10 | 0.138 |
| 2 | 6444 | 34 | 17 | 500 | 0.60 | 0.765 |
| 3 | 6429 | 37 | 17 | 500 | 0.20 | 0.374 |
| 4 | 7090 | 39 | 17 | 500 | 0.10 | 0.746 |
| 5 | 6836 | 29 | 13 | 500 | 0.35 | 0.541 |
| 6 | 6219 | 33 | 14 | 500 | 0.25 | 0.641 |
| 7 | 6481 | 33 | 13 | 500 | 0.40 | 0.247 |
| 8 | 6241 | 37 | 17 | 500 | 0.50 | 0.931 |

mean±sd: majority acc 0.312±0.171; derivation recovery 0.548±0.258; MDL-selected seed 6

## 人造数据 S1 无课程（门槛实验） (synthetic_nocurr.json)

| seed | total bits | entries | cats | parsed | majority acc | derivation recovery |
|---|---|---|---|---|---|---|
| 1 | 6168 | 30 | 13 | 500 | 0.45 | 0.725 |
| 2 | 6517 | 42 | 18 | 500 | 0.15 | 0.638 |
| 3 | 6894 | 40 | 15 | 500 | 0.10 | 0.602 |
| 4 | 7662 | 49 | 19 | 500 | 0.30 | 0.509 |
| 5 | 6523 | 35 | 14 | 500 | 0.35 | 0.500 |
| 6 | 6091 | 20 | 9 | 500 | 0.60 | 0.972 |
| 7 | 6282 | 33 | 15 | 500 | 0.10 | 0.549 |
| 8 | 6132 | 24 | 11 | 500 | 0.60 | 0.972 |

mean±sd: majority acc 0.331±0.194; derivation recovery 0.683±0.180; MDL-selected seed 6

## 归纳结果（dev，均值±标准差 over seeds）

| config | seeds | objective (bits) | train parsed | #cats | cats/word | |Q| | b | dev cov | dev cov in-lex | UAS all | UAS covered | ppl | dev≤8 cov | dev≤8 UAS | MDL-sel seed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cky_A_SA_d4_le8 | 2 | 83750±924 | 0.973±0.009 | 210.5±21.5 | 1.86±0.03 | 2.3±0.1 | 4.86±0.01 | 0.182±0.005 | 0.610±0.017 | 0.039±0.012 | 0.284±0.086 | 165.9±6.3 | n/a | n/a | 2 |
| left_A_SA_anch_d4_le10 | 2 | 142527±854 | 0.986±0.000 | 520.5±0.5 | 2.22±0.06 | 13.4±0.3 | 0.18±0.00 | 0.202±0.002 | 0.532±0.005 | 0.047±0.011 | 0.296±0.075 | 179.7±0.2 | 0.252±0.005 | 0.066±0.012 | 1 |
| left_A_SA_d3_le10 | 2 | 141628±1101 | 0.987±0.003 | 537.0±26.0 | 2.26±0.00 | 11.8±0.4 | 0.18±0.00 | 0.196±0.016 | 0.514±0.041 | 0.032±0.004 | 0.224±0.004 | 155.1±13.3 | 0.252±0.014 | 0.048±0.004 | 1 |
| left_A_SA_d4_le10 | 5 | 140862±998 | 0.985±0.003 | 492.6±20.4 | 2.18±0.02 | 11.7±0.8 | 0.18±0.00 | 0.198±0.010 | 0.520±0.025 | 0.048±0.005 | 0.320±0.031 | 159.4±16.6 | 0.250±0.009 | 0.069±0.008 | 1 |
| left_A_SA_d4_le8 | 2 | 80437±23 | 0.997±0.000 | 308.5±0.5 | 2.17±0.02 | 9.2±0.4 | 0.21±0.00 | 0.157±0.002 | 0.529±0.006 | 0.034±0.003 | 0.296±0.022 | 131.8±0.3 | 0.210±0.005 | 0.053±0.004 | 2 |
| left_A_SA_d5_le10 | 2 | 139576±1614 | 0.986±0.003 | 430.0±59.0 | 2.10±0.09 | 11.7±1.1 | 0.19±0.01 | 0.227±0.022 | 0.595±0.059 | 0.067±0.004 | 0.377±0.015 | 177.7±23.2 | 0.278±0.026 | 0.095±0.004 | 2 |
| left_A_SA_rigid_d4_le10 | 2 | 315198±1832 | 0.151±0.012 | 181.0±5.0 | 1.00±0.00 | 0.6±0.0 | 0.64±0.01 | 0.028±0.000 | 0.073±0.000 | 0.009±0.001 | 0.692±0.100 | 15.4±6.4 | 0.037±0.000 | 0.014±0.001 | 2 |
| left_A_TR_d4_le10 | 2 | 168581±27087 | 0.857±0.115 | 362.5±11.5 | 1.97±0.17 | 10.3±2.6 | 0.20±0.01 | 0.168±0.040 | 0.441±0.105 | 0.033±0.011 | 0.264±0.019 | 128.7±13.6 | 0.215±0.047 | 0.048±0.013 | 1 |
| left_A_reorder_d4_le10 | 2 | 142604±57 | 0.984±0.003 | 546.0±58.0 | 2.24±0.04 | 11.3±0.1 | 0.18±0.00 | 0.190±0.021 | 0.500±0.055 | 0.044±0.004 | 0.300±0.026 | 169.7±46.6 | 0.241±0.021 | 0.065±0.007 | 2 |
| left_B_SA_d4_le10 | 2 | 145455±740 | 0.975±0.000 | 807.5±16.5 | 2.38±0.03 | 12.9±1.7 | 0.16±0.00 | 0.152±0.017 | 0.400±0.045 | 0.030±0.009 | 0.277±0.042 | 132.4±4.1 | 0.199±0.021 | 0.044±0.011 | 1 |
| left_C_SA_d4_le10 | 2 | 279796±1257 | 0.467±0.006 | 698.0±32.0 | 1.30±0.01 | 3.0±0.2 | 0.34±0.02 | 0.093±0.028 | 0.245±0.073 | 0.012±0.008 | 0.206±0.069 | 60.5±17.1 | 0.126±0.037 | 0.020±0.012 | 2 |
| left_D_SA_d4_le10 | 2 | 135280±798 | 0.987±0.005 | 484.5±55.5 | 2.06±0.05 | 14.8±0.6 | 0.19±0.00 | 0.209±0.019 | 0.550±0.050 | 0.025±0.004 | 0.159±0.039 | 147.3±19.6 | 0.262±0.028 | 0.035±0.003 | 1 |

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

### phenomena_selected_left_A_SA_anch_d4_le10_seed1

| phenomenon | group | n (dev/train/constructed) | L1 accept | L2 reject neg | L3 pred-arg | L4 no CS | pair acc | in-lex n | L1 in-lex | L3 in-lex |
|---|---|---|---|---|---|---|---|---|---|---|
| argument_structure | gate | 95 (95/0/0) | 0.12 | 0.92 | 0.03 | 0.12 | 0.04 | 25 | 0.44 | 0.12 |
| modifiers | gate | 142 (142/0/0) | 0.17 | 0.84 | 0.04 | 0.17 | 0.01 | 50 | 0.48 | 0.10 |
| determiners | gate | 115 (115/0/0) | 0.10 | 0.90 | 0.04 | 0.10 | 0.00 | 32 | 0.34 | 0.16 |
| aux_sequence | gate | 155 (155/0/0) | 0.23 | 0.76 | 0.04 | 0.23 | 0.03 | 62 | 0.58 | 0.10 |
| vp_coordination | discriminating | 20 (4/16/0) | 0.80 | 0.45 | 0.05 | 0.05 | 0.25 | 17 | 0.94 | 0.06 |
| right_node_raising | discriminating | 5 (0/0/5) | 0.20 | 0.80 | 0.00 | 0.00 | 0.00 | 2 | 0.50 | 0.00 |
| nonconstituent_coordination | discriminating | 5 (0/0/5) | 0.20 | 0.60 | 0.00 | 0.00 | 0.00 | 3 | 0.33 | 0.00 |
| subject_relative | discriminating | 18 (1/17/0) | 0.94 | 0.28 | 0.17 | 0.50 | 0.22 | 17 | 1.00 | 0.18 |
| object_relative | discriminating | 20 (7/13/0) | 0.80 | 0.45 | 0.05 | 0.50 | 0.25 | 16 | 1.00 | 0.06 |
| valency_eat | discriminating | 3 (0/3/0) | 1.00 | 0.00 | 0.00 | 1.00 | 0.00 | 3 | 1.00 | 0.00 |
| multifunction_that | discriminating | 34 (34/0/0) | 0.38 | 0.65 | 0.06 | 0.12 | 0.03 | 19 | 0.68 | 0.11 |
| nested_clause | discriminating | 32 (32/0/0) | 0.12 | 0.88 | 0.06 | 0.12 | 0.06 | 15 | 0.27 | 0.13 |
| parasitic_gap | stretch | 3 (0/0/3) | 0.33 | 0.67 | 0.00 | 0.33 | 0.00 | 1 | 1.00 | 0.00 |
| gapping | stretch | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0 | n/a | n/a |
| comparative | stretch | 18 (1/12/5) | 0.61 | 0.44 | 0.22 | 0.61 | 0.06 | 13 | 0.85 | 0.31 |

### phenomena_selected_left_A_SA_d3_le10_seed1

| phenomenon | group | n (dev/train/constructed) | L1 accept | L2 reject neg | L3 pred-arg | L4 no CS | pair acc | in-lex n | L1 in-lex | L3 in-lex |
|---|---|---|---|---|---|---|---|---|---|---|
| argument_structure | gate | 95 (95/0/0) | 0.09 | 0.91 | 0.01 | 0.09 | 0.04 | 25 | 0.36 | 0.04 |
| modifiers | gate | 142 (142/0/0) | 0.18 | 0.85 | 0.01 | 0.18 | 0.04 | 50 | 0.52 | 0.04 |
| determiners | gate | 115 (115/0/0) | 0.16 | 0.87 | 0.08 | 0.16 | 0.03 | 32 | 0.56 | 0.28 |
| aux_sequence | gate | 155 (155/0/0) | 0.21 | 0.86 | 0.03 | 0.21 | 0.10 | 62 | 0.53 | 0.06 |
| vp_coordination | discriminating | 20 (4/16/0) | 0.80 | 0.45 | 0.00 | 0.05 | 0.25 | 17 | 0.94 | 0.00 |
| right_node_raising | discriminating | 5 (0/0/5) | 0.20 | 0.80 | 0.00 | 0.00 | 0.00 | 2 | 0.50 | 0.00 |
| nonconstituent_coordination | discriminating | 5 (0/0/5) | 0.20 | 1.00 | 0.00 | 0.00 | 0.20 | 3 | 0.33 | 0.00 |
| subject_relative | discriminating | 18 (1/17/0) | 0.94 | 0.39 | 0.06 | 0.56 | 0.33 | 17 | 1.00 | 0.06 |
| object_relative | discriminating | 20 (7/13/0) | 0.70 | 0.55 | 0.00 | 0.50 | 0.25 | 16 | 0.88 | 0.00 |
| valency_eat | discriminating | 3 (0/3/0) | 1.00 | 0.00 | 0.00 | 1.00 | 0.00 | 3 | 1.00 | 0.00 |
| multifunction_that | discriminating | 34 (34/0/0) | 0.41 | 0.68 | 0.06 | 0.29 | 0.09 | 19 | 0.74 | 0.11 |
| nested_clause | discriminating | 32 (32/0/0) | 0.09 | 0.94 | 0.03 | 0.09 | 0.03 | 15 | 0.20 | 0.07 |
| parasitic_gap | stretch | 3 (0/0/3) | 0.33 | 0.67 | 0.00 | 0.33 | 0.00 | 1 | 1.00 | 0.00 |
| gapping | stretch | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0 | n/a | n/a |
| comparative | stretch | 18 (1/12/5) | 0.72 | 0.39 | 0.11 | 0.72 | 0.11 | 13 | 1.00 | 0.15 |

### phenomena_selected_left_A_SA_d4_le10_seed1

| phenomenon | group | n (dev/train/constructed) | L1 accept | L2 reject neg | L3 pred-arg | L4 no CS | pair acc | in-lex n | L1 in-lex | L3 in-lex |
|---|---|---|---|---|---|---|---|---|---|---|
| argument_structure | gate | 95 (95/0/0) | 0.11 | 0.92 | 0.01 | 0.11 | 0.03 | 25 | 0.40 | 0.04 |
| modifiers | gate | 142 (142/0/0) | 0.17 | 0.85 | 0.04 | 0.17 | 0.02 | 50 | 0.48 | 0.10 |
| determiners | gate | 115 (115/0/0) | 0.14 | 0.90 | 0.08 | 0.14 | 0.04 | 32 | 0.50 | 0.28 |
| aux_sequence | gate | 155 (155/0/0) | 0.23 | 0.83 | 0.05 | 0.23 | 0.06 | 62 | 0.56 | 0.13 |
| vp_coordination | discriminating | 20 (4/16/0) | 0.80 | 0.45 | 0.05 | 0.10 | 0.25 | 17 | 0.94 | 0.06 |
| right_node_raising | discriminating | 5 (0/0/5) | 0.20 | 0.80 | 0.00 | 0.00 | 0.00 | 2 | 0.50 | 0.00 |
| nonconstituent_coordination | discriminating | 5 (0/0/5) | 0.20 | 0.80 | 0.00 | 0.00 | 0.00 | 3 | 0.33 | 0.00 |
| subject_relative | discriminating | 18 (1/17/0) | 0.94 | 0.56 | 0.00 | 0.56 | 0.50 | 17 | 1.00 | 0.00 |
| object_relative | discriminating | 20 (7/13/0) | 0.80 | 0.40 | 0.00 | 0.50 | 0.20 | 16 | 1.00 | 0.00 |
| valency_eat | discriminating | 3 (0/3/0) | 1.00 | 0.33 | 0.00 | 1.00 | 0.33 | 3 | 1.00 | 0.00 |
| multifunction_that | discriminating | 34 (34/0/0) | 0.47 | 0.56 | 0.12 | 0.12 | 0.03 | 19 | 0.84 | 0.21 |
| nested_clause | discriminating | 32 (32/0/0) | 0.16 | 0.94 | 0.00 | 0.16 | 0.09 | 15 | 0.33 | 0.00 |
| parasitic_gap | stretch | 3 (0/0/3) | 0.33 | 1.00 | 0.00 | 0.33 | 0.33 | 1 | 1.00 | 0.00 |
| gapping | stretch | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0 | n/a | n/a |
| comparative | stretch | 18 (1/12/5) | 0.56 | 0.50 | 0.17 | 0.56 | 0.06 | 13 | 0.77 | 0.23 |

### phenomena_selected_left_A_SA_d4_le8_seed2

| phenomenon | group | n (dev/train/constructed) | L1 accept | L2 reject neg | L3 pred-arg | L4 no CS | pair acc | in-lex n | L1 in-lex | L3 in-lex |
|---|---|---|---|---|---|---|---|---|---|---|
| argument_structure | gate | 95 (95/0/0) | 0.07 | 0.95 | 0.01 | 0.07 | 0.03 | 20 | 0.35 | 0.05 |
| modifiers | gate | 142 (142/0/0) | 0.08 | 0.92 | 0.05 | 0.08 | 0.01 | 37 | 0.32 | 0.19 |
| determiners | gate | 115 (115/0/0) | 0.08 | 0.94 | 0.05 | 0.08 | 0.02 | 19 | 0.47 | 0.32 |
| aux_sequence | gate | 155 (155/0/0) | 0.17 | 0.86 | 0.03 | 0.17 | 0.05 | 49 | 0.53 | 0.10 |
| vp_coordination | discriminating | 20 (4/16/0) | 0.20 | 0.90 | 0.00 | 0.00 | 0.10 | 7 | 0.57 | 0.00 |
| right_node_raising | discriminating | 5 (0/0/5) | 0.20 | 0.80 | 0.00 | 0.00 | 0.00 | 1 | 1.00 | 0.00 |
| nonconstituent_coordination | discriminating | 5 (0/0/5) | 0.20 | 0.80 | 0.00 | 0.20 | 0.00 | 2 | 0.50 | 0.00 |
| subject_relative | discriminating | 18 (1/17/0) | 0.28 | 0.78 | 0.00 | 0.17 | 0.06 | 5 | 1.00 | 0.00 |
| object_relative | discriminating | 20 (7/13/0) | 0.60 | 0.60 | 0.00 | 0.45 | 0.20 | 13 | 0.92 | 0.00 |
| valency_eat | discriminating | 3 (0/3/0) | 0.33 | 1.00 | 0.00 | 0.33 | 0.33 | 1 | 1.00 | 0.00 |
| multifunction_that | discriminating | 34 (34/0/0) | 0.41 | 0.65 | 0.12 | 0.15 | 0.06 | 19 | 0.74 | 0.21 |
| nested_clause | discriminating | 32 (32/0/0) | 0.12 | 0.91 | 0.03 | 0.12 | 0.03 | 11 | 0.36 | 0.09 |
| parasitic_gap | stretch | 3 (0/0/3) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0 | n/a | n/a |
| gapping | stretch | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0 | n/a | n/a |
| comparative | stretch | 18 (1/12/5) | 0.22 | 0.78 | 0.06 | 0.22 | 0.00 | 6 | 0.67 | 0.17 |

### phenomena_selected_left_A_SA_d5_le10_seed2

| phenomenon | group | n (dev/train/constructed) | L1 accept | L2 reject neg | L3 pred-arg | L4 no CS | pair acc | in-lex n | L1 in-lex | L3 in-lex |
|---|---|---|---|---|---|---|---|---|---|---|
| argument_structure | gate | 95 (95/0/0) | 0.11 | 0.92 | 0.02 | 0.11 | 0.03 | 25 | 0.40 | 0.08 |
| modifiers | gate | 142 (142/0/0) | 0.23 | 0.80 | 0.04 | 0.23 | 0.03 | 50 | 0.64 | 0.10 |
| determiners | gate | 115 (115/0/0) | 0.17 | 0.84 | 0.04 | 0.17 | 0.01 | 32 | 0.59 | 0.16 |
| aux_sequence | gate | 155 (155/0/0) | 0.27 | 0.74 | 0.12 | 0.27 | 0.05 | 62 | 0.68 | 0.31 |
| vp_coordination | discriminating | 20 (4/16/0) | 0.80 | 0.55 | 0.10 | 0.20 | 0.35 | 17 | 0.94 | 0.12 |
| right_node_raising | discriminating | 5 (0/0/5) | 0.20 | 0.80 | 0.00 | 0.20 | 0.00 | 2 | 0.50 | 0.00 |
| nonconstituent_coordination | discriminating | 5 (0/0/5) | 0.40 | 0.60 | 0.00 | 0.00 | 0.00 | 3 | 0.67 | 0.00 |
| subject_relative | discriminating | 18 (1/17/0) | 0.94 | 0.28 | 0.11 | 0.44 | 0.22 | 17 | 1.00 | 0.12 |
| object_relative | discriminating | 20 (7/13/0) | 0.75 | 0.50 | 0.00 | 0.55 | 0.25 | 16 | 0.94 | 0.00 |
| valency_eat | discriminating | 3 (0/3/0) | 1.00 | 0.00 | 0.33 | 1.00 | 0.00 | 3 | 1.00 | 0.33 |
| multifunction_that | discriminating | 34 (34/0/0) | 0.41 | 0.68 | 0.24 | 0.24 | 0.09 | 19 | 0.74 | 0.42 |
| nested_clause | discriminating | 32 (32/0/0) | 0.31 | 0.75 | 0.03 | 0.31 | 0.06 | 15 | 0.67 | 0.07 |
| parasitic_gap | stretch | 3 (0/0/3) | 0.33 | 0.67 | 0.00 | 0.33 | 0.00 | 1 | 1.00 | 0.00 |
| gapping | stretch | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0 | n/a | n/a |
| comparative | stretch | 18 (1/12/5) | 0.72 | 0.33 | 0.00 | 0.72 | 0.06 | 13 | 1.00 | 0.00 |

### phenomena_selected_left_A_SA_rigid_d4_le10_seed2

| phenomenon | group | n (dev/train/constructed) | L1 accept | L2 reject neg | L3 pred-arg | L4 no CS | pair acc | in-lex n | L1 in-lex | L3 in-lex |
|---|---|---|---|---|---|---|---|---|---|---|
| argument_structure | gate | 95 (95/0/0) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 25 | 0.00 | 0.00 |
| modifiers | gate | 142 (142/0/0) | 0.01 | 1.00 | 0.00 | 0.01 | 0.01 | 50 | 0.02 | 0.00 |
| determiners | gate | 115 (115/0/0) | 0.02 | 1.00 | 0.02 | 0.02 | 0.02 | 32 | 0.06 | 0.06 |
| aux_sequence | gate | 155 (155/0/0) | 0.05 | 1.00 | 0.03 | 0.05 | 0.05 | 62 | 0.13 | 0.06 |
| vp_coordination | discriminating | 20 (4/16/0) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 17 | 0.00 | 0.00 |
| right_node_raising | discriminating | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 2 | 0.00 | 0.00 |
| nonconstituent_coordination | discriminating | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 3 | 0.00 | 0.00 |
| subject_relative | discriminating | 18 (1/17/0) | 0.06 | 1.00 | 0.00 | 0.06 | 0.06 | 17 | 0.06 | 0.00 |
| object_relative | discriminating | 20 (7/13/0) | 0.05 | 1.00 | 0.00 | 0.05 | 0.05 | 16 | 0.06 | 0.00 |
| valency_eat | discriminating | 3 (0/3/0) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 3 | 0.00 | 0.00 |
| multifunction_that | discriminating | 34 (34/0/0) | 0.12 | 1.00 | 0.06 | 0.12 | 0.12 | 19 | 0.21 | 0.11 |
| nested_clause | discriminating | 32 (32/0/0) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 15 | 0.00 | 0.00 |
| parasitic_gap | stretch | 3 (0/0/3) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1 | 0.00 | 0.00 |
| gapping | stretch | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0 | n/a | n/a |
| comparative | stretch | 18 (1/12/5) | 0.06 | 1.00 | 0.06 | 0.06 | 0.06 | 13 | 0.08 | 0.08 |

### phenomena_selected_left_A_TR_d4_le10_seed1

| phenomenon | group | n (dev/train/constructed) | L1 accept | L2 reject neg | L3 pred-arg | L4 no CS | pair acc | in-lex n | L1 in-lex | L3 in-lex |
|---|---|---|---|---|---|---|---|---|---|---|
| argument_structure | gate | 95 (95/0/0) | 0.11 | 0.86 | 0.01 | 0.11 | 0.01 | 25 | 0.40 | 0.04 |
| modifiers | gate | 142 (142/0/0) | 0.16 | 0.85 | 0.02 | 0.16 | 0.01 | 50 | 0.46 | 0.06 |
| determiners | gate | 115 (115/0/0) | 0.13 | 0.92 | 0.06 | 0.13 | 0.07 | 32 | 0.47 | 0.22 |
| aux_sequence | gate | 155 (155/0/0) | 0.23 | 0.77 | 0.09 | 0.23 | 0.06 | 62 | 0.58 | 0.23 |
| vp_coordination | discriminating | 20 (4/16/0) | 0.75 | 0.60 | 0.00 | 0.10 | 0.35 | 17 | 0.88 | 0.00 |
| right_node_raising | discriminating | 5 (0/0/5) | 0.20 | 0.60 | 0.00 | 0.00 | 0.00 | 2 | 0.50 | 0.00 |
| nonconstituent_coordination | discriminating | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 3 | 0.00 | 0.00 |
| subject_relative | discriminating | 18 (1/17/0) | 0.94 | 0.39 | 0.06 | 0.44 | 0.33 | 17 | 1.00 | 0.06 |
| object_relative | discriminating | 20 (7/13/0) | 0.80 | 0.60 | 0.00 | 0.65 | 0.40 | 16 | 1.00 | 0.00 |
| valency_eat | discriminating | 3 (0/3/0) | 1.00 | 0.33 | 0.00 | 1.00 | 0.33 | 3 | 1.00 | 0.00 |
| multifunction_that | discriminating | 34 (34/0/0) | 0.41 | 0.62 | 0.21 | 0.18 | 0.03 | 19 | 0.74 | 0.37 |
| nested_clause | discriminating | 32 (32/0/0) | 0.09 | 0.88 | 0.06 | 0.09 | 0.00 | 15 | 0.20 | 0.13 |
| parasitic_gap | stretch | 3 (0/0/3) | 0.33 | 0.67 | 0.00 | 0.33 | 0.00 | 1 | 1.00 | 0.00 |
| gapping | stretch | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0 | n/a | n/a |
| comparative | stretch | 18 (1/12/5) | 0.67 | 0.50 | 0.22 | 0.67 | 0.17 | 13 | 0.92 | 0.31 |

### phenomena_selected_left_A_reorder_d4_le10_seed2

| phenomenon | group | n (dev/train/constructed) | L1 accept | L2 reject neg | L3 pred-arg | L4 no CS | pair acc | in-lex n | L1 in-lex | L3 in-lex |
|---|---|---|---|---|---|---|---|---|---|---|
| argument_structure | gate | 95 (95/0/0) | 0.11 | 0.92 | 0.01 | 0.11 | 0.03 | 25 | 0.40 | 0.04 |
| modifiers | gate | 142 (142/0/0) | 0.18 | 0.85 | 0.03 | 0.18 | 0.04 | 50 | 0.52 | 0.08 |
| determiners | gate | 115 (115/0/0) | 0.12 | 0.90 | 0.04 | 0.12 | 0.04 | 32 | 0.44 | 0.16 |
| aux_sequence | gate | 155 (155/0/0) | 0.22 | 0.77 | 0.06 | 0.22 | 0.02 | 62 | 0.55 | 0.16 |
| vp_coordination | discriminating | 20 (4/16/0) | 0.85 | 0.50 | 0.05 | 0.10 | 0.35 | 17 | 1.00 | 0.06 |
| right_node_raising | discriminating | 5 (0/0/5) | 0.20 | 0.60 | 0.00 | 0.00 | 0.00 | 2 | 0.50 | 0.00 |
| nonconstituent_coordination | discriminating | 5 (0/0/5) | 0.40 | 0.80 | 0.00 | 0.00 | 0.20 | 3 | 0.67 | 0.00 |
| subject_relative | discriminating | 18 (1/17/0) | 0.94 | 0.39 | 0.06 | 0.67 | 0.33 | 17 | 1.00 | 0.06 |
| object_relative | discriminating | 20 (7/13/0) | 0.80 | 0.30 | 0.00 | 0.60 | 0.10 | 16 | 1.00 | 0.00 |
| valency_eat | discriminating | 3 (0/3/0) | 1.00 | 0.00 | 0.00 | 1.00 | 0.00 | 3 | 1.00 | 0.00 |
| multifunction_that | discriminating | 34 (34/0/0) | 0.29 | 0.71 | 0.03 | 0.09 | 0.00 | 19 | 0.53 | 0.05 |
| nested_clause | discriminating | 32 (32/0/0) | 0.25 | 0.75 | 0.00 | 0.25 | 0.00 | 15 | 0.53 | 0.00 |
| parasitic_gap | stretch | 3 (0/0/3) | 0.33 | 0.67 | 0.00 | 0.33 | 0.00 | 1 | 1.00 | 0.00 |
| gapping | stretch | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0 | n/a | n/a |
| comparative | stretch | 18 (1/12/5) | 0.67 | 0.39 | 0.22 | 0.67 | 0.06 | 13 | 0.92 | 0.31 |

### phenomena_selected_left_B_SA_d4_le10_seed1

| phenomenon | group | n (dev/train/constructed) | L1 accept | L2 reject neg | L3 pred-arg | L4 no CS | pair acc | in-lex n | L1 in-lex | L3 in-lex |
|---|---|---|---|---|---|---|---|---|---|---|
| argument_structure | gate | 95 (95/0/0) | 0.09 | 0.91 | 0.01 | 0.09 | 0.02 | 25 | 0.36 | 0.04 |
| modifiers | gate | 142 (142/0/0) | 0.14 | 0.85 | 0.06 | 0.14 | 0.00 | 50 | 0.40 | 0.16 |
| determiners | gate | 115 (115/0/0) | 0.06 | 0.91 | 0.02 | 0.06 | 0.00 | 32 | 0.22 | 0.06 |
| aux_sequence | gate | 155 (155/0/0) | 0.17 | 0.88 | 0.05 | 0.17 | 0.09 | 62 | 0.44 | 0.13 |
| vp_coordination | discriminating | 20 (4/16/0) | 0.80 | 0.50 | 0.00 | 0.05 | 0.30 | 17 | 0.94 | 0.00 |
| right_node_raising | discriminating | 5 (0/0/5) | 0.20 | 0.80 | 0.00 | 0.00 | 0.00 | 2 | 0.50 | 0.00 |
| nonconstituent_coordination | discriminating | 5 (0/0/5) | 0.00 | 0.80 | 0.00 | 0.00 | 0.00 | 3 | 0.00 | 0.00 |
| subject_relative | discriminating | 18 (1/17/0) | 0.94 | 0.56 | 0.11 | 0.44 | 0.50 | 17 | 1.00 | 0.12 |
| object_relative | discriminating | 20 (7/13/0) | 0.75 | 0.55 | 0.00 | 0.55 | 0.30 | 16 | 0.94 | 0.00 |
| valency_eat | discriminating | 3 (0/3/0) | 1.00 | 0.00 | 0.33 | 1.00 | 0.00 | 3 | 1.00 | 0.33 |
| multifunction_that | discriminating | 34 (34/0/0) | 0.29 | 0.71 | 0.09 | 0.18 | 0.00 | 19 | 0.53 | 0.16 |
| nested_clause | discriminating | 32 (32/0/0) | 0.16 | 0.84 | 0.00 | 0.16 | 0.00 | 15 | 0.33 | 0.00 |
| parasitic_gap | stretch | 3 (0/0/3) | 0.33 | 1.00 | 0.00 | 0.33 | 0.33 | 1 | 1.00 | 0.00 |
| gapping | stretch | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0 | n/a | n/a |
| comparative | stretch | 18 (1/12/5) | 0.61 | 0.56 | 0.17 | 0.61 | 0.17 | 13 | 0.85 | 0.23 |

### phenomena_selected_left_C_SA_d4_le10_seed2

| phenomenon | group | n (dev/train/constructed) | L1 accept | L2 reject neg | L3 pred-arg | L4 no CS | pair acc | in-lex n | L1 in-lex | L3 in-lex |
|---|---|---|---|---|---|---|---|---|---|---|
| argument_structure | gate | 95 (95/0/0) | 0.03 | 0.98 | 0.01 | 0.03 | 0.01 | 25 | 0.12 | 0.04 |
| modifiers | gate | 142 (142/0/0) | 0.06 | 0.94 | 0.01 | 0.06 | 0.01 | 50 | 0.16 | 0.02 |
| determiners | gate | 115 (115/0/0) | 0.03 | 1.00 | 0.00 | 0.03 | 0.03 | 32 | 0.12 | 0.00 |
| aux_sequence | gate | 155 (155/0/0) | 0.12 | 0.95 | 0.00 | 0.12 | 0.08 | 62 | 0.31 | 0.00 |
| vp_coordination | discriminating | 20 (4/16/0) | 0.20 | 0.90 | 0.00 | 0.10 | 0.10 | 17 | 0.24 | 0.00 |
| right_node_raising | discriminating | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 2 | 0.00 | 0.00 |
| nonconstituent_coordination | discriminating | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 3 | 0.00 | 0.00 |
| subject_relative | discriminating | 18 (1/17/0) | 0.28 | 0.94 | 0.00 | 0.17 | 0.22 | 17 | 0.29 | 0.00 |
| object_relative | discriminating | 20 (7/13/0) | 0.40 | 0.80 | 0.00 | 0.30 | 0.20 | 16 | 0.50 | 0.00 |
| valency_eat | discriminating | 3 (0/3/0) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 3 | 0.00 | 0.00 |
| multifunction_that | discriminating | 34 (34/0/0) | 0.29 | 0.71 | 0.06 | 0.15 | 0.03 | 19 | 0.53 | 0.11 |
| nested_clause | discriminating | 32 (32/0/0) | 0.06 | 0.97 | 0.03 | 0.06 | 0.03 | 15 | 0.13 | 0.07 |
| parasitic_gap | stretch | 3 (0/0/3) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1 | 0.00 | 0.00 |
| gapping | stretch | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0 | n/a | n/a |
| comparative | stretch | 18 (1/12/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 13 | 0.00 | 0.00 |

### phenomena_selected_left_D_SA_d4_le10_seed1

| phenomenon | group | n (dev/train/constructed) | L1 accept | L2 reject neg | L3 pred-arg | L4 no CS | pair acc | in-lex n | L1 in-lex | L3 in-lex |
|---|---|---|---|---|---|---|---|---|---|---|
| argument_structure | gate | 95 (95/0/0) | 0.13 | 0.91 | 0.01 | 0.13 | 0.03 | 25 | 0.48 | 0.04 |
| modifiers | gate | 142 (142/0/0) | 0.20 | 0.80 | 0.03 | 0.20 | 0.01 | 50 | 0.56 | 0.08 |
| determiners | gate | 115 (115/0/0) | 0.16 | 0.82 | 0.01 | 0.16 | 0.00 | 32 | 0.56 | 0.03 |
| aux_sequence | gate | 155 (155/0/0) | 0.26 | 0.74 | 0.05 | 0.26 | 0.03 | 62 | 0.66 | 0.13 |
| vp_coordination | discriminating | 20 (4/16/0) | 0.80 | 0.40 | 0.05 | 0.25 | 0.20 | 17 | 0.94 | 0.06 |
| right_node_raising | discriminating | 5 (0/0/5) | 0.40 | 0.60 | 0.00 | 0.00 | 0.00 | 2 | 1.00 | 0.00 |
| nonconstituent_coordination | discriminating | 5 (0/0/5) | 0.60 | 0.40 | 0.00 | 0.00 | 0.00 | 3 | 1.00 | 0.00 |
| subject_relative | discriminating | 18 (1/17/0) | 0.94 | 0.39 | 0.00 | 0.67 | 0.33 | 17 | 1.00 | 0.00 |
| object_relative | discriminating | 20 (7/13/0) | 0.75 | 0.40 | 0.10 | 0.55 | 0.15 | 16 | 0.94 | 0.12 |
| valency_eat | discriminating | 3 (0/3/0) | 1.00 | 0.00 | 0.00 | 1.00 | 0.00 | 3 | 1.00 | 0.00 |
| multifunction_that | discriminating | 34 (34/0/0) | 0.38 | 0.68 | 0.03 | 0.24 | 0.06 | 19 | 0.68 | 0.05 |
| nested_clause | discriminating | 32 (32/0/0) | 0.16 | 0.88 | 0.00 | 0.16 | 0.03 | 15 | 0.33 | 0.00 |
| parasitic_gap | stretch | 3 (0/0/3) | 0.33 | 0.67 | 0.00 | 0.33 | 0.00 | 1 | 1.00 | 0.00 |
| gapping | stretch | 5 (0/0/5) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0 | n/a | n/a |
| comparative | stretch | 18 (1/12/5) | 0.67 | 0.44 | 0.22 | 0.67 | 0.11 | 13 | 0.92 | 0.31 |

## 高频范畴（cky_A_SA_d4_le8, MDL-selected seed 2）

| # | category | expected count | 20 words |
|---|---|---|---|
| 1 | `N` | 1743.6 | the, it, <C1>, that, this, you, a, <C5>, i, she, are, we, <C23>, my, to, not, 'll, like, were, 're |
| 2 | `NP` | 562.5 | 's, <C1>, was, is, got, and, 'm, <C5>, does, ’s, 're, want, will, 've, about, are, <C7>, looks, two, just |
| 3 | `N/N` | 479.1 | do, what, a, have, was, like, <C1>, n't, i, my, just, in, they, you, <C10>, did, okay, <C4>, know, are |
| 4 | `S\S` | 476.0 | <C5>, <C14>, <C1>, <C2>, one, now, it, i, a, of, said, in, am, good, too, even, will, though, sense, that |
| 5 | `S` | 386.8 | i, a, <C3>, <C5>, <C1>, three, are, is, can, have, pretty, not, yeah, the, how, those, both, and, even, no |
| 6 | `S/S` | 318.0 | i, and, so, yeah, but, we, <C1>, yes, she, now, the, that, he, it, here, or, where, some, are, uh |
| 7 | `S/NP` | 306.8 | they, i, that, it, and, he, no, she, this, well, we, then, yeah, so, there, her, na, 'm, had, after |
| 8 | `NP/N` | 242.2 | i, <C1>, oh, you, she, he, can, 's, ’s, we, be, was, just, <C16>, a, uh, gave, sleep, one, yeah |
| 9 | `S\N` | 215.9 | <C1>, know, is, <C19>, <C5>, right, time, have, of, a, us, probably, bear, great, first, says, new, try, 's, was |
| 10 | `(S\S)\N` | 215.4 | <C1>, me, <C14>, there, here, <C19>, work, say, <C5>, are, bit, back, lipstick, answer, face, <C11>, but, robert, keep, fine |
| 11 | `(S\NP)\N` | 212.2 | <C1>, <C5>, <C9>, it, right, great, beautiful, true, correct, trying, nice, game, interesting, down, four, floor, important, who, dreams, fire |
| 12 | `S/N` | 183.4 | i, you, we, just, he, 'm, the, she, was, of, put, well, also, my, died, 's, makes, going, impossible, a |
| 13 | `N\S` | 176.3 | the, to, <C5>, in, it, been, <C1>, he, is, <C2>, are, a, really, <C12>, i, us, <C21>, middle, that, she |
| 14 | `(S\N)/N` | 148.2 | <C1>, is, <C19>, like, ’s, did, pete, a, mother, his, fully, zero |
| 15 | `NP\N` | 140.8 | <C20>, <C5>, <C1>, <C19>, the, doing, need, was, <C14>, is, city, whatsoever, end, plants, all, mother, hole, anything, mandatory, wear |
| 16 | `N\NP` | 112.5 | an, the, n't, to, ’re, my, a, of, it, that, this, not, on, <C5>, best, looks, a.m., 17, words, part |
| 17 | `S\NP` | 110.8 | of, <C5>, a, <C1>, it, trump, once, easily, by, scared, wrong, too |
| 18 | `(S\N)\N` | 103.0 | <C19>, good, same, go, do, ’s, says, bad, her, more, know, huge, student, tell, 1, future, thought, another, means, wanted |
| 19 | `NP\S` | 100.5 | <C1>, him, <C5>, to, last, that, internet, did, 4, knew, easy, <C13>, heard, writes, wine, <C3>, right, successful, worn, teacher |
| 20 | `S/(S/N)` | 92.0 | that, it, he, you, mean, only, possesses, all, medical, wails, eating, lived |
| 21 | `N\N` | 86.9 | the, <C19>, a, <C1>, for, least, remember, everyone, these, n't, yellow, trouble, culture, goes, ’ve |
| 22 | `(S\S)/N` | 83.8 | for, get, to, of, his, few, so, he, understand, one, show, head |
| 23 | `(S/N)/N` | 77.4 | 's, thought, have, low, go, driving |
| 24 | `(S/N)/NP` | 74.7 | <C5>, there, the, his, free, one, <C0>, third |
| 25 | `N/S` | 72.3 | i, <C5>, first, it, in, so, many, um, this, have, does, was, one, getting, off, here, that, her, different |
| 26 | `NP\NP` | 71.2 | <C1>, very, so, not, at, <C8>, of, all, about, above, together, two, it |
| 27 | `(S/NP)/N` | 70.4 | oh, we, it, for, then, people, beat, results, mrs., <C16> |
| 28 | `(S\N)/S` | 64.2 | is, 's, seems, turn, does, take |
| 29 | `N/NP` | 60.8 | i, it, that, you, <C5>, n't, was, the, already, day, 2 |
| 30 | `(S/S)/NP` | 57.2 | it, they |
| 31 | `NP/S` | 53.2 | <C0>, 's, am, is, does, in, <C19>, n’t, 6, anyway |
| 32 | `(S\S)\NP` | 52.3 | <C17>, out, of, different, points, tea, go, went, smiled |
| 33 | `(S/S)/S` | 51.2 | and, yeah, he, like, you, winking, already, girls, love, fourth |
| 34 | `S\(S\S)` | 42.9 | <C1>, here, month, showed, sentence, bringing, see |
| 35 | `(N/N)/N` | 40.3 | <C1>, we, spot, wait |
| 36 | `(S\S)/S` | 38.7 | to, has, you, of, more |
| 37 | `(N/NP)/N` | 37.7 | if, look, quartiles, around, percentiles, horse, years, means, wanted, certainly, iqr, gomez, both, definitely, cara, wikihow, problem |
| 38 | `(N/N)/NP` | 36.7 | in, invisible, us, 21 |
| 39 | `(N\N)\N` | 35.5 | the, real, circuit, minutes, word, events |
| 40 | `S\(NP/N)` | 35.4 | said, think, see, hurt |
| 41 | `S\(S\N)` | 30.5 | <C1>, as, happen, holding, country, results |
| 42 | `(S/N)/S` | 29.9 | <C1>, took |
| 43 | `NP/(S\N)` | 25.9 | this, <C6>, art, head, met, kill |
| 44 | `(S\S)\((N/N)/NP)` | 23.9 | <C7> |
| 45 | `N\(NP/N)` | 22.5 | n't, i |
| 46 | `(S\NP)\S` | 21.4 | them, again, <C15>, small, beer |
| 47 | `(NP/N)/N` | 20.9 | no, still, then, father |
| 48 | `(NP\N)\NP` | 19.1 | of, service, america, year, enjambment, beautiful, floor, september, before, anyway |
| 49 | `(N\N)\S` | 18.8 | at, in, open, hours, afraid |
| 50 | `NP/NP` | 17.8 | my, it, 're, built |

失败日志汇总（dev, 0 failures）: by UPOS/deprel of failing word: []; by word: []; by position: []


## 高频范畴（left_A_SA_anch_d4_le10, MDL-selected seed 1）

| # | category | expected count | 20 words |
|---|---|---|---|
| 1 | `S` | 2424.6 | <C3>, <C1>, know, <C4>, is, do, it, have, 'm, the, this, are, think, 're, that, said, a, 'll, <C2>, <C8> |
| 2 | `S/S` | 1348.1 | i, you, <C3>, the, they, this, <C1>, she, he, it, we, just, really, can, to, <C13>, are, oh, of, yes |
| 3 | `S\S` | 1004.3 | <C1>, <C3>, it, of, with, there, a, them, to, out, now, what, one, from, right, day, that, her, as, up |
| 4 | `N` | 607.3 | 's, <C3>, ’s, n't, i, is, was, the, a, out, beautiful, an, she, does, <C19>, probably, now, oh, looks, not |
| 5 | `NP` | 493.4 | <C3>, <C1>, and, is, were, <C12>, the, we, you, too, for, as, to, that, back, it, will, <C5>, one, n't |
| 6 | `N/S` | 482.7 | the, i, 's, we, <C3>, n't, a, there, and, my, to, it, is, was, many, today, you, then, like, not |
| 7 | `S/NP` | 341.0 | <C3>, <C9>, do, <C10>, like, <C12>, be, <C13>, us, i, <C2>, a, am, for, it, bad, felt, could, your, say |
| 8 | `(S\S)/S` | 315.6 | in, <C3>, a, you, n't, like, very, that, 's, says, he, from, <C9>, both, i, any, be, good, doing, than |
| 9 | `S/N` | 294.6 | did, <C3>, do, there, the, in, that, has, is, from, what, other, so, three, have, thought, he, but, long, course |
| 10 | `NP\S` | 279.5 | a, she, at, his, to, in, and, was, he, <C3>, never, an, is, our, your, even, of, it, were, way |
| 11 | `S\N` | 268.5 | <C3>, <C1>, of, for, the, today, <C2>, me, would, years, percentiles, it, in, take, are, like, science, happen, girls, interest |
| 12 | `S\NP` | 247.5 | <C3>, <C7>, me, here, said, are, fun, then, asked, hand, lot, all, okay, <C10>, better, name, he, offer, mouth, badly |
| 13 | `N\S` | 217.0 | <C3>, the, my, two, for, some, also, not, and, are, up, n’t, <C11>, just, small, held, <C16>, university, telling, structures |
| 14 | `(S/S)/N` | 207.1 | it, that, and, she, well, yeah, no, you |
| 15 | `(S/S)/S` | 206.3 | i, this, we, but, so, he, a, <C1>, these, ferries, man |
| 16 | `N/N` | 199.7 | that, it, <C16>, and, sorry, the, into, one, like, 's, all, mayor, not, 4, stand, time, but, answer, learned, children |
| 17 | `((S\S)/S)/S` | 161.8 | the, i, makes, goes, example, <C22> |
| 18 | `(S\N)/N` | 134.0 | it, that, he, there, data, <C21>, october, exciting, chalmers, symmetry |
| 19 | `S\(S\N)` | 129.6 | <C14>, good, at, not, him, right, for, just, me, are, interesting, it, impossible, wrong, allowed, forever, peace, honey, different, smiled |
| 20 | `NP/S` | 123.2 | <C1>, n't, okay, and, is, all, i, first, look, to, a, <C3>, santa, are, into, q, stories, lost, ginny, eventually |
| 21 | `N/NP` | 122.9 | <C1>, down, the, <C9>, you, ’s, uh, we, trying, seems, <C12>, no, <C20>, on, also, my, till, surgery, close, take |
| 22 | `NP/N` | 87.5 | the, was, to, important, is, happy, fourth, needs, ginny, modernity, size, ready, show, lack, fish, must, holt |
| 23 | `((S/S)/N)/S` | 78.3 | i, you, today |
| 24 | `S/(S/S)` | 73.0 | so, yeah, <C3>, in, the, least, em, stories, a, greek |
| 25 | `S\((S/S)/S)` | 72.3 | <C2>, told, judy, moment, group |
| 26 | `(S\NP)/S` | 71.5 | of, i, <C7>, we, he, it, open, god, best, oh, pizza, happy |
| 27 | `S\(NP\S)` | 67.2 | <C3>, game, point, yesterday, mandatory, spot, delicious, now, touch, english |
| 28 | `S\(S\NP)` | 61.3 | <C18>, great, 1, <C10>, like, as, history, than, back, september, problems, sometime, most, uh, thursday, likes |
| 29 | `NP\N` | 60.7 | my, and, so, of, with, this, were, to, short, <C23>, roll, going, questions, bit, later, sure, arrested |
| 30 | `(S\S)/N` | 57.9 | of, <C3>, one, <C15>, came, dillard, up, boys |
| 31 | `(S\N)/S` | 56.6 | the, two, no, we, not, strange, saturday, say, word, movies, demonstrate, eleven, left, practical, met |
| 32 | `S\(S\S)` | 52.5 | <C16>, does, us, <C20>, points, you, quidditch, up, alright, states, rental, tell, biological, of, more, said, wonderful, hands, black |
| 33 | `(S\N)\S` | 51.5 | 's, is, like, to, not, only, bar, 'd, translated, driving, places, ask |
| 34 | `NP/(S/S)` | 51.2 | to, is, but, gets, regular |
| 35 | `NP\NP` | 50.1 | on, a, with, <C3>, mathematics, you, its, older, 's, roberts, 25, football, cultural, details, necessity, home |
| 36 | `(NP\N)/S` | 48.6 | <C3>, alone, to, buy, love, forgot, coupons, survive, another, x, 5, problems |
| 37 | `NP/NP` | 47.7 | the, <C1>, <C3>, we, fine, fair, lemon, triumph, parents, ie6, north, president, climate, outliers, seem |
| 38 | `(N\S)/S` | 47.2 | <C1>, you, interviews, show, scientology, opening, today, bringing, consultation, article, business, teacher, next |
| 39 | `(NP\S)/S` | 46.0 | and, has, for, never, it, yet |
| 40 | `(S\S)/(S/NP)` | 44.5 | to, she, might, <C20>, 2, 2:25 |
| 41 | `(S\S)\S` | 41.4 | it, sending, car, itself, dreams, pinotage, guests, family, away, living, united |
| 42 | `(S\(S\NP))/S` | 40.8 | a, <C5>, getting, more, <C18>, further, look |
| 43 | `(S/N)/S` | 39.5 | in, alright, through, thank, totally |
| 44 | `N\NP` | 39.4 | na, and, pretty, doing, a, mexico, infected, work, instead, are, get, anything, chalmers, shock |
| 45 | `((S\N)/S)/S` | 39.0 | by, they, find, do, public, hire, even, internet, high, tired, list, medicating, words, event, result |
| 46 | `S\((S/S)/N)` | 37.1 | 's, eight, live |
| 47 | `S/(NP\S)` | 35.6 | have, 've, not, this, just, uhhh, shit, twelve |
| 48 | `S/(S/NP)` | 35.6 | of, little, few, that, looks, next, noon |
| 49 | `(S\NP)/NP` | 35.5 | <C3>, they, have, an |
| 50 | `(S\(S\S))/S` | 33.1 | of, <C3>, up, are, what, black, encabalgamiento, do, lay, letter, longer, test |

失败日志汇总（dev, 52 failures）: by UPOS/deprel of failing word: [['END/END', 18], ['ADV/advmod', 6], ['NOUN/obl', 6], ['PRON/nsubj', 3], ['VERB/ccomp', 2], ['VERB/root', 2], ['ADJ/amod', 2], ['NOUN/obj', 1], ['PROPN/compound', 1], ['ADV/reparandum', 1], ['NUM/nummod', 1], ['NOUN/nsubj', 1], ['PRON/nmod', 1], ['AUX/cop', 1], ['PRON/obj', 1]]; by word: [['<END>', 18], ['again', 3], ['morning', 2], ['stop', 2], ['interesting', 2], ['home', 1], ['weekend', 1], ['hold', 1], ['though', 1], ['they', 1], ['this', 1], ['north', 1], ['too', 1], ['we', 1], ['15', 1]]; by position: [[2, 3], [3, 7], [4, 4], [5, 12], [6, 10], [7, 11], [8, 1], [9, 1], [10, 2], [11, 1]]


## 高频范畴（left_A_SA_d3_le10, MDL-selected seed 1）

| # | category | expected count | 20 words |
|---|---|---|---|
| 1 | `S\S` | 1421.7 | <C1>, <C3>, not, <C16>, it, one, to, like, said, of, with, from, a, <C10>, me, good, so, now, great, right |
| 2 | `S` | 936.0 | <C2>, <C1>, is, 's, <C3>, was, the, out, that, down, i, ’s, and, day, mother, we, has, of, it, these |
| 3 | `N` | 735.5 | <C3>, i, he, the, there, <C1>, that, it, you, we, his, this, she, they, for, a, and, before, ’s, here |
| 4 | `S\N` | 710.3 | of, <C3>, this, <C1>, the, <C13>, was, is, do, she, got, have, go, say, it, are, also, same, 's, for |
| 5 | `NP\N` | 612.7 | <C7>, <C3>, like, a, <C10>, about, <C1>, little, into, their, good, not, after, what, way, the, <C0>, na, things, lot |
| 6 | `NP` | 607.6 | have, 're, <C4>, are, can, want, 've, will, am, know, see, do, 'm, said, 'll, back, need, look, <C3>, just |
| 7 | `S/S` | 513.8 | it, that, the, <C1>, i, and, there, <C9>, <C3>, my, oh, 's, yeah, but, he, all, ca, first, so, thing |
| 8 | `N\S` | 494.2 | to, the, <C14>, n't, <C3>, a, all, i, not, and, no, 's, okay, he, never, more, just, an, god, as |
| 9 | `N/S` | 391.6 | it, that, this, there, he, she, the, now, <C9>, because, about, also, well, 'd, and, more, said, wikihow, hopefully, budweiser |
| 10 | `S/NP` | 350.8 | i, you, they, we, he, <C1>, my, it, that, 's, she, her, does, are, then, the, minute, gets, and, low |
| 11 | `S/N` | 317.9 | <C3>, n't, <C13>, and, <C18>, so, <C1>, no, are, if, these, like, man, sorry, when, is, maybe, for, i, both |
| 12 | `N/NP` | 303.1 | i, you, we, <C3>, she, they, he, over, and, but, of, this, middle, alright, out, even, like, use, new, allowed |
| 13 | `N/N` | 285.4 | and, yeah, but, well, <C1>, then, <C3>, no, like, has, a, he, uh, what, this, by, tulsa, we, as, be |
| 14 | `N\N` | 272.2 | <C3>, i, the, you, we, and, a, like, <C1>, my, it, had, do, more, no, he, gon, is, square, coming |
| 15 | `(S\S)/S` | 270.3 | the, <C3>, it, what, on, that, <C11>, <C1>, really, get, <C7>, his, many, those, funny, he, nice, called, <C10>, got |
| 16 | `S\(N/S)` | 200.0 | 's, is, ’s, does, trouble, 2015, <C10>, minute, 2006 |
| 17 | `(S\S)/(NP\N)` | 196.5 | a, of, for, <C3>, and, my, your, at, as, got, <C16>, n’t, gon, other, these, fully, football, thursday, taking, lot |
| 18 | `NP\S` | 186.9 | <C10>, in, on, a, was, be, <C3>, is, ’re, would, the, called, both, been, it, us, hole, bad, hear, my |
| 19 | `NP/N` | 184.4 | <C3>, know, oh, so, to, like, and, <C11>, yes, interest, just, but, down, is, <C12>, okay, the, was, march, eating |
| 20 | `S\NP` | 179.6 | <C3>, here, <C1>, from, said, be, a, process, <C21>, at, joke, getting, now, all, more, ’s, point, everything, known, experience |
| 21 | `NP/S` | 145.8 | <C3>, think, her, the, mean, thought, <C19>, just, love, today, here, they, follow, <C4>, in, hope, did, never, earth, for |
| 22 | `S\(S\N)` | 125.9 | <C3>, is, it, know, are, yet, her, a, remembered, idiot, brains, enough, mukalla, help, movies, prolific, among |
| 23 | `N\NP` | 110.3 | on, work, <C3>, a, all, n't, for, we, september, n’t, in, baucus, president, tiny, bowl, studying, stated, greek, active, least |
| 24 | `S/(NP\N)` | 99.4 | 's, was, is, the, but, this, ’m, some, ended, years, word, around, good |
| 25 | `(S\N)/S` | 83.7 | the, <C3>, a, one, work, is, study, another, boys, lay, um, ’m, ever, explorer |
| 26 | `(S\S)/N` | 75.5 | the, had, over, <C7>, with, she, another, us, use, very, up, somewhere, <C22>, her, ever |
| 27 | `NP/NP` | 75.0 | 'll, <C3>, people, was, we, in, go, he, come, my, <C4>, telling, schools, 'm, um, eventually |
| 28 | `(S\NP)/S` | 74.2 | the, in, a, how, <C6>, its, up, following, us, san, addiction, white, room, explorer |
| 29 | `NP\NP` | 70.5 | in, any, asked, done, depends, unprecedented, yours |
| 30 | `NP/(S/N)` | 69.3 | do, 'm, could, kill, top |
| 31 | `(S/N)/S` | 68.7 | <C2>, end, luther, toss, write, 20, worn, competition |
| 32 | `S\(N/NP)` | 65.5 | know, think, 'm, <C3>, 2012, failed, so |
| 33 | `S/(N\S)` | 64.8 | 's, by, that, looks, yield |
| 34 | `(N\S)/N` | 64.3 | at, was, as, <C16>, only, super, if, wait, pretty, give, <C15>, fourth, hold |
| 35 | `(S\N)\S` | 62.8 | very, an, my, were, our, <C3>, culture, a, of, spot, usually, tried, myself |
| 36 | `NP/(N\S)` | 60.1 | have, did, be, were, <C1>, remember, key, even, usually, sometimes |
| 37 | `S\(NP\N)` | 55.5 | <C3>, <C8>, months, doing, ever, not, extensive, self |
| 38 | `(S\S)/(S/S)` | 53.2 | in, to, offer, below, different, is, <C7>, equals, exciting |
| 39 | `(S/N)/NP` | 49.1 | n't, get, values |
| 40 | `(S/S)/N` | 47.4 | so, well, yes, <C3>, um, see, plan, another, to, school, flight |
| 41 | `(NP\N)/NP` | 45.3 | most, first, wikinews, the, robert, our, between, further, began, expired, starts, hands, jenna, problem, dad, yes, across |
| 42 | `(S\N)\N` | 42.2 | <C4>, get, ways, loved, church, roberts, rate, knew, worse, groups |
| 43 | `(S\S)/(N\N)` | 42.1 | and, to, it, have, show, at, match, shows, gram |
| 44 | `S/(S/N)` | 42.0 | the, will, feel, 's, 're, southeast |
| 45 | `(S\S)/(S\N)` | 40.0 | <C5>, per, her, alone, must, ever |
| 46 | `S\(S\S)` | 39.0 | you, us, headset, move, american, erasmus, injection, effect, took, recorder, chalmers, roll, ie6, tired, sentence |
| 47 | `S\(N\S)` | 38.1 | once, to, year, services, love, judy, looked, delicious, ahead, thought, problem, remarks, 22, thursday |
| 48 | `(S/S)/S` | 37.5 | <C8>, this, your, been, alright, goldsmith, downtown, big |
| 49 | `((S\S)/NP)/S` | 37.0 | <C12>, wanted, going, on, studies |
| 50 | `(NP\N)/((S/N)/S)` | 35.3 | the, little |

失败日志汇总（dev, 49 failures）: by UPOS/deprel of failing word: [['END/END', 11], ['ADV/advmod', 7], ['NOUN/root', 4], ['VERB/xcomp', 4], ['ADP/case', 4], ['NOUN/obj', 3], ['VERB/root', 3], ['ADJ/root', 2], ['VERB/advcl', 1], ['PRON/obj', 1], ['DET/det', 1], ['NUM/compound', 1], ['PRON/nsubj', 1], ['PROPN/compound', 1], ['PRON/nmod', 1]]; by word: [['<END>', 11], ['thinking', 3], ['home', 2], ['there', 2], ['of', 2], ['trouble', 1], ['works', 1], ['number', 1], ['people', 1], ['it', 1], ['a', 1], ['thirty', 1], ['they', 1], ['touch', 1], ['north', 1]]; by position: [[2, 2], [3, 4], [4, 8], [5, 10], [6, 8], [7, 7], [8, 5], [9, 4], [10, 1]]


## 高频范畴（left_A_SA_d4_le10, MDL-selected seed 1）

| # | category | expected count | 20 words |
|---|---|---|---|
| 1 | `S\N` | 1191.8 | <C3>, <C14>, to, <C1>, <C4>, was, know, it, are, is, that, 's, even, me, <C10>, now, does, this, ’s, one |
| 2 | `N\N` | 1046.8 | of, do, that, 's, i, did, n't, had, ’s, to, was, <C11>, <C3>, all, the, a, is, we, really, have |
| 3 | `S` | 991.3 | <C1>, <C16>, just, <C3>, no, here, 'm, says, in, have, very, <C12>, an, will, up, over, about, really, it, get |
| 4 | `S\S` | 988.5 | <C1>, <C3>, <C10>, it, them, say, i, be, and, now, from, my, to, there, for, more, that, too, good, people |
| 5 | `N` | 948.2 | i, that, it, this, she, <C3>, there, he, we, oh, so, they, the, then, and, on, here, if, you, at |
| 6 | `N\S` | 793.9 | <C3>, it, you, they, that, and, he, the, she, to, <C12>, so, <C9>, we, as, is, into, with, i, of |
| 7 | `NP` | 588.9 | <C2>, <C3>, <C13>, you, <C1>, only, this, <C5>, the, <C10>, man, help, most, for, ’re, make, also, voice, about, and |
| 8 | `N/S` | 360.2 | i, it, the, you, <C3>, this, we, they, all, oh, she, <C1>, want, these, back, a, ’re, like, 'll, those |
| 9 | `NP\N` | 319.9 | 's, is, was, are, it, have, you, the, we, very, <C3>, part, were, least, may, his, n't, mother, pag, hard |
| 10 | `S\NP` | 318.5 | <C1>, <C3>, me, right, some, of, it, go, all, you, is, a, one, sense, like, yeah, her, said, been, each |
| 11 | `S/N` | 273.2 | know, <C8>, <C4>, have, <C1>, we, no, and, seen, are, the, for, like, did, 'm, see, 'll, <C0>, an, my |
| 12 | `N/N` | 254.1 | and, yeah, but, well, <C3>, the, na, yes, <C1>, um, my, they, his, after, thus, garden, was, bowl, generation, fled |
| 13 | `N\NP` | 239.2 | the, <C18>, one, down, not, a, your, of, <C12>, to, made, big, like, 're, i, <C3>, leave, thursday, her, internet |
| 14 | `S/NP` | 216.3 | the, a, we, they, i, like, can, not, is, in, her, it, those, one, love, oh, 'm, very, whole, american |
| 15 | `(S\N)/S` | 203.2 | 's, is, was, still, have, get, n't, you, really, my, came, we, one, four, future, it, twelve |
| 16 | `NP\S` | 196.5 | in, to, at, of, with, like, have, by, this, a, out, it, and, example, you, <C3>, are, big, years, mrs. |
| 17 | `(S\S)/NP` | 193.2 | the, to, of, a, and, like, this, 're, than, people |
| 18 | `NP/S` | 160.9 | <C3>, bit, my, <C7>, <C13>, alone, <C2>, only, take, new, <C1>, <C10>, has, easily, are, your, scared, also, all, course |
| 19 | `N/NP` | 119.6 | the, <C3>, you, this, he, our, my, at, a, try, today, girls, holt, ways, unprecedented, conventions, quartiles, other, all, percentiles |
| 20 | `S/S` | 113.7 | <C1>, 'm, 's, 've, the, got, two, and, his, is, not, so, ’m, out, currently, article, covered, first, study, could |
| 21 | `(N\N)/S` | 105.4 | you, n't, is, no, to, quite, need, and, actually, always, good, with, care, find, from, older, lipstick, mean, again, lot |
| 22 | `N\(N\S)` | 104.8 | 're, 's, 'll, <C3>, <C19>, ’s, i, will, to, he, must, kill |
| 23 | `NP/NP` | 100.6 | the, <C2>, are, little, and, <C13>, real, long, good, will, consultation, any, budweiser, meal, often, at, power, necessity |
| 24 | `NP/N` | 96.8 | i, <C2>, the, he, <C13>, few, 4, data, course, all, she, second, academic, freedom, experience, injection, much, camera, website, harry |
| 25 | `(S\N)/NP` | 90.9 | to, the, 's, a, sending, minute, bring, tiny, an |
| 26 | `S/(S/N)` | 90.4 | i, you, in, questions, ever |
| 27 | `S\(N\S)` | 79.1 | <C3>, started, pretty, already, to, are, i, is, watch, fair, starving, happened, winning, quarters, became, movies, minute |
| 28 | `S\(NP\NP)` | 77.0 | <C7>, problem, bear, throat, breath, badly, year, buildings, since, week, san, sold |
| 29 | `(S\S)/N` | 76.9 | in, and, get, my, public, because, wan, high |
| 30 | `S\(S\S)` | 74.8 | <C1>, will, from, think, there, science, better, 'll, erasmus, hire, yoga, wine, sports, red, area, but, them, nathan |
| 31 | `N/(S\N)` | 72.4 | that, the, <C9>, <C19>, but, he, feel, around |
| 32 | `NP\NP` | 69.3 | <C7>, also, <C5>, 're, been, are, somehow, members, with, little, refused, everywhere, measures, or, five, $, len, mystery, award, they |
| 33 | `(S\N)/N` | 62.9 | is, that, been, n't, then, there, love, n’t, come, meant, could |
| 34 | `S/(N\N)` | 60.2 | <C5>, do, what, she, parents |
| 35 | `S\(S\NP)` | 60.1 | long, two, of, pizza, eyes, might, animal, part, roll, greek, whatever, stand, along, days, values, service, south, stated, both, because |
| 36 | `(S\NP)/S` | 59.2 | is, a, gets, <C10>, starts, almost |
| 37 | `N/(NP\N)` | 57.1 | it, my, people, grizzly, made, personal |
| 38 | `S\(S\N)` | 57.1 | great, work, correct, good, i, interesting, right, three, impossible, mandatory, low |
| 39 | `(S\S)/S` | 56.0 | for, i, comes, three, won, than, world, <C23>, head, land, goes, us |
| 40 | `N\(S\S)` | 54.3 | <C3>, i, we, that, there, at, called, my |
| 41 | `(S\S)\S` | 54.0 | what, with, i, would, september, white, follows, behind, precise, data, pete, score, cinnamon, children, higher |
| 42 | `(NP\S)/S` | 51.7 | in, i, we, under, wikihow, arrested, global, holding |
| 43 | `(S\N)/(N\N)` | 49.2 | <C3>, <C15>, sure, not, through, long, burning, ’m, our, higher, better, gone |
| 44 | `(N\N)\S` | 47.8 | it, i, 's, went, does, go, moreau, behind, air |
| 45 | `(NP\N)\NP` | 47.4 | a, the, so, enter |
| 46 | `S\(N\N)` | 45.6 | said, choice, cool, n’t, happy, wrong, 's, guessed, hand, tired, nine, fled, strong |
| 47 | `(N\S)/S` | 44.6 | the, i, when, contains, but, brains |
| 48 | `(S\S)/(S/N)` | 44.5 | in, the, my, an, have |
| 49 | `(S\N)/(N\NP)` | 41.7 | was, <C6>, never |
| 50 | `(S/N)/S` | 36.0 | i, have, also, eventually, translated, 2011 |

失败日志汇总（dev, 48 failures）: by UPOS/deprel of failing word: [['END/END', 24], ['VERB/root', 3], ['NOUN/obj', 2], ['ADV/advmod', 2], ['ADJ/root', 2], ['NUM/flat', 2], ['VERB/advcl', 1], ['AUX/aux', 1], ['NOUN/obl', 1], ['PRON/obj', 1], ['PRON/nmod', 1], ['VERB/ccomp', 1], ['NUM/nummod', 1], ['NOUN/nsubj', 1], ['INTJ/discourse', 1]]; by word: [['<END>', 24], ['lot', 2], ['interesting', 2], ['two', 2], ['thinking', 1], ['would', 1], ['number', 1], ['mess', 1], ['touch', 1], ['anything', 1], ['about', 1], ['his', 1], ['turn', 1], ['well', 1], ['twelve', 1]]; by position: [[2, 2], [3, 7], [4, 7], [5, 9], [6, 8], [7, 6], [8, 2], [9, 3], [10, 3], [11, 1]]


## 高频范畴（left_A_SA_d4_le8, MDL-selected seed 2）

| # | category | expected count | 20 words |
|---|---|---|---|
| 1 | `S\S` | 1313.3 | <C1>, <C5>, it, <C9>, me, <C3>, in, <C2>, on, here, that, of, to, right, one, not, at, good, now, them |
| 2 | `S/S` | 669.3 | and, <C1>, so, yeah, oh, the, my, like, but, no, that, you, well, i, he, <C5>, then, she, also, a |
| 3 | `NP` | 618.3 | <C1>, said, do, have, was, did, be, of, know, think, are, just, in, out, the, does, 'm, am, say, 's |
| 4 | `S` | 614.5 | <C5>, <C1>, a, this, her, was, to, that, been, there, you, our, two, today, first, n't, will, him, ’s, has |
| 5 | `S/NP` | 534.1 | i, <C14>, we, he, there, it, she, this, <C5>, you, they, the, <C1>, are, 's, one, or, to, my, his |
| 6 | `N` | 454.1 | i, the, you, they, it, she, <C1>, that, he, go, <C5>, we, want, and, little, this, game, need, <C0>, once |
| 7 | `S\N` | 372.0 | <C19>, is, was, will, <C5>, <C4>, see, mean, get, have, work, look, are, same, want, 'll, and, trump, started, way |
| 8 | `(S\S)\N` | 265.6 | 's, do, ’s, is, 'm, hope, can, felt, <C11>, earth, try, like, santa, ways, who, together, most, luther, follow, collapse |
| 9 | `NP/S` | 238.2 | <C1>, 's, <C5>, we, i, they, doing, is, of, know, think, thought, not, now, that, 'll, you, have, for, to |
| 10 | `NP/N` | 200.1 | you, <C1>, we, i, says, they, a, sorry, zero, 's, up, <C19>, died, floor, talking, definitely, those, my, with, 'll |
| 11 | `NP/NP` | 197.1 | it, <C1>, yes, i, the, 'll, ’s, <C10>, was, 's, <C5>, too, are, for, just, 'd, point, to, he, so |
| 12 | `N\S` | 179.2 | the, n't, more, can, your, his, is, <C6>, in, at, culture, not, 21, ta, head, kidding, anything, door, thought, popularity |
| 13 | `S/((S\S)\N)` | 167.5 | that, it, there, here, goes, mrs. |
| 14 | `(S\S)/NP` | 150.2 | <C0>, <C1>, it, to, all, he, a, she, n't, their, nice, want, ’s, in, both, pete, q, hear, would, remember |
| 15 | `(S\S)/S` | 138.0 | what, <C1>, like, so, never, how, at, you, make, up, really, guys, for, going, an, right, guy, getting, down, another |
| 16 | `N/NP` | 105.8 | i, and, she, they, his, but, so, first, one, wait, least, what, same, shirts, course, ninety-nine, trouble, <C1>, heard, country |
| 17 | `S\(S\S)` | 87.6 | <C1>, not, like, you, <C5>, to, so, that, three, trying, find, nice, sports, carry, lipstick, comes, thought, renata, collapse, friend |
| 18 | `N/N` | 86.7 | <C7>, we, in, the, oh, had, yes, makes, face, only, he, goes, 2012, almost, because |
| 19 | `S/((N\N)\N)` | 83.5 | this, <C6>, it |
| 20 | `(S\S)/(S/NP)` | 79.0 | a, the, over, mexico |
| 21 | `S\(NP/N)` | 63.5 | know, are, 're, 4, small, sister, nephew |
| 22 | `(N\N)\N` | 62.2 | is, looks, vlog, starts, rained |
| 23 | `N\(S/S)` | 56.6 | i, it, they, he |
| 24 | `(S\S)/N` | 55.2 | a, to, my, is, has, big, beautiful, ended, color, yours, show, changed, study, nonna |
| 25 | `S\NP` | 52.6 | into, you, old, uh, <C21>, while, blue, month, study, 22, letter, millions, hotel, cultural, are, service, ’re, could, he, seems |
| 26 | `S/N` | 47.0 | <C1>, the, was, of, a, to, <C5>, you, real, whatsoever |
| 27 | `S\(NP/NP)` | 40.6 | of, <C1>, he, long |
| 28 | `(NP\S)/NP` | 38.4 | <C20>, kind, as, okay, him, part |
| 29 | `(S/S)/S` | 35.4 | it, source, bird, simply |
| 30 | `S/(NP/N)` | 31.8 | he, mother, not, god, the, power, below, what, players |
| 31 | `((S\S)/S)/S` | 30.2 | <C1>, is, two, wo |
| 32 | `(S\S)/(N/N)` | 30.1 | in |
| 33 | `NP/((N\NP)/S)` | 28.0 | and |
| 34 | `(N\NP)/S` | 27.7 | <C17>, words |
| 35 | `N/S` | 27.0 | <C19>, have, many, pretty, my, a, spot, grizzly, different |
| 36 | `(S\N)/NP` | 26.0 | <C19>, always, is, stood, might, key, have, still |
| 37 | `N\NP` | 21.4 | <C12>, low, process, n’t, said, headset, time, white, called |
| 38 | `(S\(NP/N))/NP` | 21.2 | <C1>, 're, i |
| 39 | `(S\N)/(NP/N)` | 20.2 | 'm, mom, chalmers |
| 40 | `(S\N)/(NP/S)` | 20.1 | 're, mother |
| 41 | `(NP\(S\S))/N` | 19.7 | n't, gram |
| 42 | `S\(N/NP)` | 18.2 | <C1>, reasons |
| 43 | `(S\S)/(NP/N)` | 17.8 | was, <C16>, to, us, from |
| 44 | `((N\N)\N)/S` | 17.6 | is |
| 45 | `S\(S\N)` | 16.9 | writes, lot, not, okay, fine, did, know, ’s, asked |
| 46 | `(S/NP)/N` | 16.7 | no, football, plan |
| 47 | `(NP\S)/N` | 15.0 | sense, his, 2014, remarks, too, interest, dillard |
| 48 | `(NP/N)/S` | 14.6 | <C5> |
| 49 | `S\(NP/S)` | 14.4 | got, fair, visited, before |
| 50 | `(N\N)/S` | 14.1 | for, own, was, but, hate, blue |

失败日志汇总（dev, 40 failures）: by UPOS/deprel of failing word: [['END/END', 11], ['ADV/advmod', 7], ['VERB/root', 3], ['NOUN/root', 3], ['PART/advmod', 2], ['NOUN/compound', 1], ['ADV/root', 1], ['DET/det', 1], ['PRON/obl', 1], ['NOUN/obl', 1], ['PRON/obj', 1], ['ADJ/parataxis', 1], ['ADV/reparandum', 1], ['ADJ/root', 1], ['PRON/nmod', 1]]; by word: [['<END>', 11], ['again', 3], ['home', 2], ["n't", 2], ['get', 1], ['phone', 1], ['ago', 1], ['any', 1], ['something', 1], ['while', 1], ['thing', 1], ['anything', 1], ['little', 1], ['right', 1], ['tired', 1]]; by position: [[2, 1], [3, 5], [4, 3], [5, 15], [6, 6], [7, 7], [8, 2], [9, 1]]


## 高频范畴（left_A_SA_d5_le10, MDL-selected seed 2）

| # | category | expected count | 20 words |
|---|---|---|---|
| 1 | `S` | 2057.8 | <C10>, it, know, <C11>, the, <C2>, <C21>, are, <C6>, <C13>, a, said, 're, this, <C7>, <C9>, <C1>, like, right, say |
| 2 | `S/S` | 1274.8 | i, and, so, they, well, yeah, but, no, like, you, <C10>, my, really, we, oh, in, this, just, what, <C1> |
| 3 | `N` | 1046.4 | <C10>, the, <C2>, <C4>, got, one, <C16>, i, good, he, that, a, just, go, mother, and, our, could, for, always |
| 4 | `S\S` | 937.8 | <C2>, <C10>, it, <C1>, that, now, out, for, the, them, down, you, more, him, here, be, said, again, way, with |
| 5 | `S/N` | 702.6 | the, a, <C10>, 's, i, is, was, are, all, <C20>, can, <C2>, it, very, we, not, she, to, called, other |
| 6 | `(S\S)/S` | 578.8 | of, and, in, is, was, <C10>, that, on, from, with, to, into, a, you, 's, my, we, like, are, would |
| 7 | `NP\S` | 540.2 | to, <C10>, <C2>, <C17>, you, <C18>, n’t, not, be, all, by, from, your, some, on, n't, an, the, pretty, percentiles |
| 8 | `S/(S/N)` | 476.0 | it, that, he, this, there, she, i, down, never, <C21>, from |
| 9 | `N/N` | 368.6 | the, <C2>, on, <C16>, <C3>, he, with, we, another, it, of, <C10>, i, this, there, my, are, for, today, but |
| 10 | `N/S` | 331.7 | and, in, <C10>, his, it, about, not, only, <C3>, i, my, the, a, so, like, she, did, <C16>, first, very |
| 11 | `S\NP` | 326.6 | <C10>, <C1>, <C2>, of, you, to, are, will, wikinews, there, from, years, asked, help, <C14>, have, at, 's, tell, wine |
| 12 | `(S/N)/S` | 313.3 | 's, is, was, ’s, 'll, by, most, like, also, my |
| 13 | `(S\N)/S` | 208.5 | n't, is, <C19>, <C2>, to, i, was, ’s, answer, went, two, he, they, till, we, big, mr., enjoyed, nature |
| 14 | `S\N` | 196.6 | the, <C2>, n't, says, is, we, on, she, time, 's, was, has, least, he, back, best, those, wikihow, 4, morning |
| 15 | `NP` | 171.0 | think, 'm, <C2>, these, the, get, love, said, 've, have, up, i, they, ten, knew, we, for, do, wrote, loved |
| 16 | `S\(S\N)` | 136.6 | <C16>, same, are, me, 9, deal, phone, rained, concerts, finished |
| 17 | `N\S` | 134.0 | it, he, did, <C4>, mom, <C1>, <C15>, long, <C2>, yesterday, <C5>, 's, <C16>, black, writing, goes, were, ’s, process, place |
| 18 | `(S/S)/S` | 128.4 | you, we, oh, <C10>, yeah, it, people, my, jenna, unambiguous, magic, sentence, funny, their, younger, roberts, herself, totally, lipstick |
| 19 | `S/NP` | 121.8 | i, we, <C2>, they, says, grew, spot, injection, woke, sports, 's, least, 10 |
| 20 | `(S\S)/N` | 108.1 | the, <C3>, a, we, that, by, her, she, you, thought, doing, 20, supports, whole, andrew, happy, focused, it |
| 21 | `S/(NP\S)` | 93.9 | <C18>, do, 're, is, not, in, hope, more, <C21>, come, changing, taking, hurried, beginning, 20, as, bit, higher |
| 22 | `NP/S` | 91.0 | have, 'm, <C10>, to, on, because, actually, headset, known, remarks, pete, removed, received, economically, hour, islands, q |
| 23 | `(S\N)\(S/S)` | 88.3 | the, still |
| 24 | `S\(S\S)` | 85.7 | <C10>, <C2>, started, that, received, longer, funny, power, wrong, 5, myself, delicious, idiot, schools, <C3>, what, gave, really, her, sector |
| 25 | `(NP\S)/S` | 85.3 | a, have, $, ball, over, us, old, different, super, state, between, size, nephew, needs, stories, south, iqr, wanted, but, quinoa |
| 26 | `((S/S)/S)/N` | 82.9 | i, the, you, this, and, they |
| 27 | `(S\NP)/S` | 81.4 | to, <C10>, <C1>, and, three, than, on, best, at, following, write, their, ginny, towards, movies |
| 28 | `N\NP` | 77.0 | <C3>, game, also, number, match, shock, effect, <C16>, bathtub, water, biological, mom, kid, extensive |
| 29 | `(S/N)/N` | 66.3 | 's, wiped, events |
| 30 | `(S/S)/NP` | 61.7 | i, her |
| 31 | `(S\S)/(NP\S)` | 61.6 | the, 's, with, most, around, writes, scba, kid, three, no, face, 21, days, gomez |
| 32 | `(S\N)/N` | 55.8 | <C10>, is, felt, ago, blue, zero, n't, a, love, published, 2012, animals |
| 33 | `((S\S)/S)/S` | 53.7 | i, as, ’s, how, share, located, said, problem, gets, saw |
| 34 | `(S\S)\N` | 52.7 | the, and, public, a, forgot, reason, not, your |
| 35 | `S/(NP\NP)` | 48.5 | we, i, you |
| 36 | `NP\N` | 47.8 | me, hear, once, all, flights, horse, still, connection, god, eight, either, men, tell, could, tells, tuesday, deal |
| 37 | `(NP\NP)/S` | 46.2 | have, ’re, made, for, very, match, animals |
| 38 | `NP/(S\N)` | 45.8 | do |
| 39 | `(NP\N)/S` | 45.7 | <C10>, of, this, has, had, won, considered, country, 5 |
| 40 | `S/(N\NP)` | 45.4 | a, each |
| 41 | `N\N` | 44.6 | <C2>, <C4>, somehow, x, needed, measures, checks, owner, along, median, means, potential, the, or, times, hole, patrons |
| 42 | `(N\S)/N` | 43.7 | my, of, name, i, to, she, given, then, got, sleep, eight, exciting |
| 43 | `(S\(S\S))/S` | 38.4 | <C10>, service, over, betty, arrested, honey |
| 44 | `(S/(NP\S))/S` | 34.4 | they, you, this |
| 45 | `S/(S/S)` | 32.3 | of, 're, 've, kinda, explorer, something, his, downtown, extensive, meal |
| 46 | `S/((S\N)/S)` | 29.2 | i |
| 47 | `(NP\NP)/(NP\S)` | 26.7 | want, need, this |
| 48 | `(S\S)/(N\S)` | 26.4 | of, good, in, fully, long, well |
| 49 | `(NP\S)/N` | 26.3 | <C12>, i, big, wear, absolutely |
| 50 | `NP\(S/S)` | 25.3 | an, <C18>, two, strong |

失败日志汇总（dev, 38 failures）: by UPOS/deprel of failing word: [['END/END', 9], ['PRON/obj', 3], ['ADJ/amod', 2], ['DET/det', 2], ['ADV/advmod', 2], ['NUM/nummod', 2], ['NOUN/obj', 2], ['AUX/aux', 1], ['VERB/advcl', 1], ['NOUN/compound', 1], ['NOUN/obl', 1], ['NUM/compound', 1], ['PROPN/obj', 1], ['NOUN/nmod', 1], ['VERB/ccomp', 1]]; by word: [['<END>', 9], ['it', 3], ['there', 2], ['lot', 2], ['last', 1], ['would', 1], ['works', 1], ['phone', 1], ['any', 1], ['morning', 1], ['thirty', 1], ['anything', 1], ['america', 1], ['15', 1], ['throat', 1]]; by position: [[2, 1], [3, 5], [4, 9], [5, 10], [6, 6], [7, 1], [8, 2], [9, 4]]


## 高频范畴（left_A_SA_rigid_d4_le10, MDL-selected seed 2）

| # | category | expected count | 20 words |
|---|---|---|---|
| 1 | `NP` | 397.0 | it, <C10>, that, he, n't, she, not, there, great, right, of, here, them, <C13>, beautiful, good, correct, just, down, gon |
| 2 | `S/N` | 119.0 | we, they, 'm, <C19>, you, do, <C4>, say, ’m, felt, understand, culture, knew, hurried, am, grown, hope, loved, wo |
| 3 | `(S\NP)/NP` | 108.0 | 's, ’s, does, did, both, looks, always, america, super |
| 4 | `NP/NP` | 66.0 | in, so, <C1>, all, well, yes, really, on, <C14>, jenna, after, then, as, him, try, alright, literally, biological, if |
| 5 | `N` | 63.0 | is, are, put, face, gave, tuesday, explorer, sister, those, nephew, another, question, could, forever, long, kill, vlog, guys, 've |
| 6 | `(S/NP)/(S/N)` | 61.0 | i |
| 7 | `S\S` | 58.0 | know, now, <C16>, na, um, <C7>, 20, around, up, even, kidding, happen, us, rider, best, two, square, land, <C15>, real |
| 8 | `N/N` | 42.0 | <C2>, me, <C6>, tape, 4, opposite, backed, everything, these, though, place |
| 9 | `S` | 41.0 | the, <C9>, event, fit, asked, god, free, game, brains, dreams, source, nothing, cultural, central, worn |
| 10 | `S\NP` | 38.0 | was, will, looked, unimportant, wikinews, fair, only, happened |
| 11 | `N\S` | 28.0 | a, interviewed, make, below |
| 12 | `(S\S)/NP` | 25.0 | very, her, be, horse, get, but, look, over, above, come, writes, already, go, never, much, hire |
| 13 | `S\N` | 25.0 | <C3>, <C21>, joke, moment, painting, dream, sense, teacher, mistake, limited, zero, survive, day |
| 14 | `N/NP` | 24.0 | were, with, can, ’re, ca, made, wrote, church, 6, went, love, hand |
| 15 | `(S/NP)/N` | 20.0 | this, mine |
| 16 | `NP/S` | 18.0 | my, <C8>, vision, judy, luther, something, website, problem, open, door |
| 17 | `N/((N\N)\S)` | 14.0 | 're |
| 18 | `N/S` | 14.0 | have, year, mean, matter, usually, particular |
| 19 | `(S/N)/NP` | 12.0 | and, 'd, hate, drank, started |
| 20 | `S/NP` | 9.0 | said, shit, wails, hard, crazy |
| 21 | `(S/NP)/(S/NP)` | 9.0 | oh, cause, mom |
| 22 | `NP\N` | 9.0 | trump, by, dillard, dinner, months |
| 23 | `(N\N)\S` | 8.0 | <C17>, allowed |
| 24 | `NP\NP` | 7.0 | name, seems, thing, march, most, than, also |
| 25 | `N/(NP\N)` | 7.0 | want, need |
| 26 | `NP/N` | 6.0 | his, competition, infected, taking |
| 27 | `NP\(S/NP)` | 6.0 | like, coming, experience |
| 28 | `((S\NP)/(N/N))/NP` | 6.0 | <C20>, died, away |
| 29 | `NP/(NP/S)` | 5.0 | to, three |
| 30 | `(S\NP)/S` | 5.0 | anymore, may, comes, lipstick, observed |
| 31 | `(S\S)/(N/N)` | 5.0 | exist, six, definitely, own, become |
| 32 | `NP\S` | 5.0 | wine, who, 2012, today |
| 33 | `(N\S)/S` | 4.0 | for, watching, results |
| 34 | `NP/(S/NP)` | 4.0 | okay, betty, voice |
| 35 | `S/(S/NP)` | 4.0 | <C0>, cara |
| 36 | `NP/(N/N)` | 4.0 | pag, easily, mrs. |
| 37 | `((S\S)/(N/N))/NP` | 4.0 | looking, about, born |
| 38 | `((N\N)\S)/(N/N)` | 3.0 | bringing, still |
| 39 | `((S\NP)/NP)/S` | 3.0 | from, has |
| 40 | `(NP\S)/NP` | 3.0 | wonderful, second, think |
| 41 | `(NP\S)/S` | 3.0 | possesses, different |
| 42 | `((S\S)/NP)/NP` | 3.0 | root, start, again |
| 43 | `(S/(S/NP))/NP` | 3.0 | no |
| 44 | `(S\S)/N` | 3.0 | your, questions |
| 45 | `(NP\(S/NP))/NP` | 3.0 | what |
| 46 | `(N\S)/NP` | 2.0 | years |
| 47 | `S\(N/NP)` | 2.0 | old |
| 48 | `(S\NP)/(S/NP)` | 2.0 | moreau, yet |
| 49 | `NP/(NP/NP)` | 2.0 | an |
| 50 | `(N\S)/N` | 2.0 | median, alone |

失败日志汇总（dev, 102 failures）: by UPOS/deprel of failing word: [['VERB/root', 25], ['PRON/nsubj', 20], ['AUX/cop', 9], ['DET/det', 7], ['ADV/advmod', 6], ['AUX/aux', 6], ['NOUN/nsubj', 3], ['PRON/root', 3], ['ADJ/root', 3], ['PART/advmod', 2], ['ADP/case', 2], ['PRON/nmod', 1], ['ADJ/amod', 1], ['CCONJ/cc', 1], ['PRON/obj', 1]]; by word: [['i', 8], ['know', 6], ['you', 5], ['was', 4], ['did', 3], ['they', 3], ['a', 3], ['the', 3], ['her', 2], ['do', 2], ["'s", 2], ['not', 2], ['it', 2], ['me', 2], ['we', 2]]; by position: [[2, 57], [3, 30], [4, 11], [5, 4]]


## 高频范畴（left_A_TR_d4_le10, MDL-selected seed 1）

| # | category | expected count | 20 words |
|---|---|---|---|
| 1 | `S/S` | 1769.0 | <C3>, i, the, you, we, <C1>, to, a, oh, all, of, no, what, my, well, be, in, this, with, it |
| 2 | `S` | 1257.7 | <C3>, it, <C1>, good, <C14>, <C8>, that, you, <C10>, here, the, do, them, right, there, know, down, three, great, been |
| 3 | `S\S` | 769.4 | <C1>, <C3>, it, of, is, <C10>, out, to, with, now, <C16>, time, said, say, this, today, us, some, back, more |
| 4 | `S/N` | 766.8 | that, the, it, <C9>, this, he, she, i, like, <C3>, there, <C1>, on, <C10>, and, for, are, just, only, other |
| 5 | `S/NP` | 563.2 | do, the, <C3>, a, are, have, did, was, got, to, just, ca, really, been, and, <C1>, <C7>, <C16>, wo, of |
| 6 | `NP/S` | 539.3 | a, n't, not, are, <C3>, <C1>, in, an, the, n’t, so, to, on, say, by, like, going, need, is, from |
| 7 | `N/S` | 524.0 | is, <C3>, 's, and, her, a, i, from, you, for, we, thought, one, of, has, was, like, in, <C12>, probably |
| 8 | `N` | 455.4 | <C3>, is, said, ’s, 's, the, <C1>, i, too, could, both, also, one, had, was, felt, love, alone, you, <C12> |
| 9 | `N/NP` | 385.2 | <C2>, 's, is, <C3>, ’s, did, it, does, in, has, place, and, i, me, the, as, for, ’m, beautiful, second |
| 10 | `NP` | 359.8 | n't, <C1>, want, the, about, very, <C3>, not, trying, world, i, nice, it, their, much, a, <C8>, door, blue, hard |
| 11 | `(S/S)/S` | 341.3 | i, and, they, so, but, yeah, there, if, no, because, people, uh, get, service, kind, where, looking, carroll, downtown, spot |
| 12 | `(S/S)/N` | 251.4 | it, he, that, there, we, she, and, <C3>, my, everything, first, sorry, essential, your |
| 13 | `NP/N` | 228.0 | know, <C4>, see, think, have, will, said, <C3>, ’re, feel, get, 'm, most, my, not, are, loved, nature, knew, hire |
| 14 | `N/N` | 212.0 | <C3>, i, 's, super, says, one, do, another, got, <C10>, he, received, the, was, said, hear, me, now, she, name |
| 15 | `S\N` | 202.6 | <C3>, <C1>, all, says, home, the, said, water, thursday, people, different, will, here, pretty, match, small, ago, breath, next, possession |
| 16 | `N\N` | 190.2 | <C7>, 're, <C3>, the, she, bit, one, you, long, what, always, better, were, another, excited, <C1>, free, joke, for, mandatory |
| 17 | `S/(N\NP)` | 160.1 | it, that, new, went, minute |
| 18 | `S/(S/S)` | 145.2 | and, yeah, <C3>, that, so, those, <C1>, have, of, <C13>, where, around, there, two, runs |
| 19 | `S/(NP/N)` | 138.8 | i, can, 'll, that, moreau, were, yesterday, knows |
| 20 | `(N\NP)/S` | 126.7 | 's, ’s, <C20>, home |
| 21 | `NP/NP` | 126.0 | we, in, <C3>, n't, the, 're, you, not, talking, face, well, she, he, try, traveler, scientology, five, turning, magic, absolutely |
| 22 | `S\NP` | 109.8 | work, again, trump, was, that, to, i, for, interesting, vlog, over, zero, mouth, morning, like, <C5>, 18, party, betty, remarks |
| 23 | `S/(S/NP)` | 84.5 | they, i, you, <C3>, we, 're, went, love, movies, lights |
| 24 | `(S/S)/NP` | 82.6 | <C1>, the, i, are, mother, quite, my, so, <C13>, yellow, ramon, ended, eleven, lack, instead |
| 25 | `S/(N/NP)` | 81.0 | the, their, more, on, that, same, experience, fit, people, 21, rained |
| 26 | `N/(NP/S)` | 80.4 | 's, is, was, does, up, or, follow |
| 27 | `N\NP` | 78.9 | and, was, a, 's, on, further, he, <C20>, walk, interviewed, does, where, mistakes, zealand, example, known |
| 28 | `(NP/N)/S` | 76.4 | have, <C4>, think, get, really, he, this, was, carry |
| 29 | `N\S` | 76.2 | of, in, with, to, by, at, 30, many, <C3>, than, original, its, worth, more, then, making, greek, comes, people, personal |
| 30 | `NP\S` | 75.6 | <C3>, to, at, us, his, way, like, what, below, last, first, is, a, school, children, more, yesterday, 7, built, name |
| 31 | `(NP\N)\S` | 68.0 | to, <C3>, at, was, six, less, 22 |
| 32 | `S\(NP\N)` | 63.4 | me, <C13>, <C1>, <C18>, opposite, help, go, eight, 2015, collapse, renata, tell, months |
| 33 | `S\(N\N)` | 56.3 | <C3>, asked, know, by, ahead, islands, example, judy, land, sector, end, magicians, guess, county |
| 34 | `((S/NP)/S)/S` | 52.8 | the, you, andrew |
| 35 | `NP/(NP/N)` | 47.6 | n't, a, it |
| 36 | `S/(S\NP)` | 47.5 | <C19>, he, it, has, waiting, scared, considered, water |
| 37 | `NP/(N\N)` | 46.2 | a, <C1>, match, even, are, potential |
| 38 | `(S/NP)/S` | 43.8 | 're, are, many, those, up, em, here, higher, better, basil, divided |
| 39 | `(S/S)/(NP/N)` | 42.3 | you, we, erasmus |
| 40 | `(N\S)/S` | 42.1 | of, <C1>, end, almost |
| 41 | `(S/S)/((NP/N)/N)` | 39.3 | i |
| 42 | `S\(S\N)` | 38.9 | that, later, war, percentiles, recorder, equipment, kidding, chair, feet, point, motion, apart, nine, unambiguous, industry, fourth, roll, ie6, definitely |
| 43 | `S/(S/N)` | 38.7 | <C4>, over, is, really, an, believe, lemon, okay, baucus, hour |
| 44 | `N/(S/S)` | 38.2 | to, like, down, is, looks, you, than, meant |
| 45 | `N/(N\N)` | 38.0 | 's, is, a, i, girls, everything |
| 46 | `(S\NP)/S` | 37.6 | to, was, observed, changed, we, and, blood |
| 47 | `NP\N` | 35.0 | <C3>, <C1>, how, him, for, united, n't, my, mathematician, meal, needs, airlines, any, 10 |
| 48 | `(NP/N)/N` | 34.4 | am, have, sorry, <C3>, starving, cara, smiled, watch, build |
| 49 | `NP\NP` | 34.0 | <C16>, day, covenant, yours, dad, 17, days, unimportant, generation |
| 50 | `S/((S\NP)\N)` | 33.2 | to, many, her |

失败日志汇总（dev, 50 failures）: by UPOS/deprel of failing word: [['END/END', 13], ['ADV/advmod', 6], ['NOUN/obl', 3], ['NOUN/obj', 2], ['VERB/ccomp', 2], ['NUM/nummod', 2], ['PRON/nmod', 2], ['ADJ/amod', 2], ['VERB/xcomp', 2], ['ADP/case', 2], ['NUM/flat', 2], ['AUX/aux', 1], ['ADV/root', 1], ['PRON/obj', 1], ['PROPN/compound', 1]]; by word: [['<END>', 13], ['again', 3], ['mess', 2], ['there', 2], ['stop', 2], ['interesting', 2], ['on', 2], ['two', 2], ['night', 1], ['would', 1], ['number', 1], ['ago', 1], ['though', 1], ['it', 1], ['morning', 1]]; by position: [[2, 1], [3, 6], [4, 12], [5, 10], [6, 9], [7, 2], [8, 4], [9, 3], [10, 2], [11, 1]]


## 高频范畴（left_A_reorder_d4_le10, MDL-selected seed 2）

| # | category | expected count | 20 words |
|---|---|---|---|
| 1 | `S\S` | 2095.9 | <C2>, <C10>, the, i, that, it, to, she, you, <C1>, of, now, there, said, like, and, at, they, me, them |
| 2 | `S` | 1060.4 | <C10>, it, <C2>, to, he, and, <C12>, the, i, that, a, we, there, <C1>, never, has, sorry, so, really, these |
| 3 | `S\NP` | 945.4 | <C10>, <C6>, <C21>, ’s, is, right, was, me, this, the, great, a, said, <C1>, it, you, 's, does, good, first |
| 4 | `NP\S` | 842.8 | <C16>, of, is, at, it, for, and, be, not, to, like, <C10>, your, about, he, on, these, little, that, <C14> |
| 5 | `S/S` | 577.0 | i, we, <C19>, <C10>, have, yeah, so, just, <C18>, think, <C2>, to, they, 'm, like, mean, do, oh, know, was |
| 6 | `N` | 540.5 | n't, it, not, <C10>, <C2>, an, you, of, a, n’t, can, <C14>, one, on, the, is, been, had, after, 's |
| 7 | `NP` | 524.5 | it, <C10>, he, the, 're, and, <C2>, i, that, <C11>, were, they, <C12>, for, she, mother, as, in, mom, is |
| 8 | `NP/S` | 380.9 | i, was, we, <C2>, 's, and, but, the, with, those, <C10>, just, is, how, actually, 30, better, months, local, voice |
| 9 | `S/N` | 325.6 | <C13>, this, 're, have, do, are, was, 'm, to, they, he, the, also, i, every, out, only, two, know, that |
| 10 | `S\(S\S)` | 260.0 | <C10>, 'll, <C20>, say, <C2>, go, was, will, do, to, have, see, can, like, <C16>, that, <C15>, is, the, hire |
| 11 | `NP/NP` | 256.8 | <C3>, you, they, so, we, her, no, and, my, <C8>, a, <C1>, bit, lot, few, yeah, now, <C2>, eyes, this |
| 12 | `NP\NP` | 255.3 | the, is, 's, in, this, <C1>, are, had, doing, so, oh, it, <C4>, been, big, all, super, no, earth, put |
| 13 | `S/(S/S)` | 236.9 | i, you, there, it, he, lived, zero |
| 14 | `(S/S)\S` | 197.1 | to, of, in, over, i, really, going, any, because, her, we, have, 's, internet, that, <C7>, know, somewhere, invisible, service |
| 15 | `S\N` | 167.8 | <C10>, n't, their, the, na, always, <C5>, <C2>, it, future, behind, looks, broad, friend, 4, break, easily, throat, wrong, spot |
| 16 | `N/S` | 150.9 | n't, all, <C2>, she, it, that, is, like, really, his, over, made, tea, opposite, hard, against, black, follow, <C1>, wonderful |
| 17 | `N/NP` | 142.6 | says, <C1>, a, the, not, we, brother, received, <C2>, okay, be, bird, love, words, work, changed, strong, mouth, remarks, cool |
| 18 | `(S\N)\NP` | 136.8 | that, this, <C4>, often, observed, baucus, game, laura, pants |
| 19 | `S/NP` | 121.0 | <C10>, and, what, the, she, love, i, a, he, something, like, there, for, website, <C2>, is, no, up, till, san |
| 20 | `(S/N)\S` | 115.4 | <C10>, it, are, did, that, have, our, do, you, very, writing, data, six, crazy, done, tired, huge, change |
| 21 | `(S\S)\S` | 110.1 | i, the, we, what, she, for, wrote, give, went, where, ways, grab, this, on, work, explorer, might |
| 22 | `(S/(NP\S))\S` | 102.7 | the, a, is, all, <C10>, in, looking, this, <C16>, little, word, white, really, one, know, other, ta, 22 |
| 23 | `S\(NP/S)` | 102.7 | <C7>, are, know, have, on, then, made, ago, <C2>, today, still, minutes, home, asks, precise |
| 24 | `N\NP` | 100.3 | the, city, <C2>, sense, does, hole, wan, small, rental, general, example, go, south, 9, apart, rider, fire, sky, peoples, sometime |
| 25 | `(S/S)\NP` | 98.1 | 's, the, what, i, should, following, its, <C1>, came, no, things, something, seem, try, parents, once, past, enough |
| 26 | `(S\S)/S` | 90.4 | i, you, this |
| 27 | `NP\((S\N)\NP)` | 87.6 | 's, is |
| 28 | `S/(NP/S)` | 84.9 | it, basil |
| 29 | `NP/(S\S)` | 82.4 | yeah, well, and, oh, <C0>, yes, call, pinotage, drank |
| 30 | `N/N` | 76.2 | <C10>, i, <C1>, 's, 've, has, n't, on, no, making, oh, plant, guessed |
| 31 | `(S/(NP/NP))\S` | 73.6 | a, not, <C10>, little, <C16>, by, keep, can |
| 32 | `N\S` | 68.4 | the, gon, <C2>, of, <C22>, called, good, 21, beat, airlines, thank, interviews, made, <C14>, at, no, anything, divided, video, asking |
| 33 | `(S/(NP\S))\NP` | 62.8 | the, take, only, big, <C2>, front, equipment, ho, 7 |
| 34 | `(NP/S)/N` | 60.5 | 's, extensive, ca |
| 35 | `NP\N` | 55.3 | <C10>, trump, another, on, happy, na, by, the, may, those, them, excited, all, something, became, wanted, times, chalmers, showed |
| 36 | `(S/S)/N` | 53.1 | do, hope, joke, alone, equals |
| 37 | `(NP/S)\S` | 47.0 | <C10>, was, wait, n't, we, did, few, mom, judge |
| 38 | `S/(NP\S)` | 46.2 | the, talking, woke |
| 39 | `(S/NP)\S` | 45.7 | and, that, say, so, demonstrate, began, contact, people |
| 40 | `(N/N)\S` | 44.7 | you, an, the, <C2>, i, are, president, seems, practical, pay, she |
| 41 | `(S/S)/S` | 44.5 | 'm, am, are, 'd, spencer |
| 42 | `(S/(NP/S))\S` | 43.8 | <C3>, with, <C16>, bit, carolyn, further, divide, six, little, today, some, right, enjambment, jenna, earth, age |
| 43 | `(S/N)\N` | 37.8 | way, us, science, turn, with, mayor, down, contains, show, 2011, vision, gone, brain, bears |
| 44 | `(S/(S/N))\S` | 37.3 | in, it, nice, my, <C16>, eleven, here |
| 45 | `S\((S\N)\NP)` | 36.1 | is, 's, displaced, could |
| 46 | `(S/N)\(S\S)` | 34.6 | did, we, copy, roberts, plants |
| 47 | `S\(N\S)` | 33.6 | <C2>, 2012, erasmus, square, shows, worse, thanks, wet |
| 48 | `S\(NP/N)` | 33.4 | trying, nice, mathematics, also, says, considered, idea, starving, gross, nervous, greek, measures, hurt, week, bears, result |
| 49 | `S/(S/N)` | 31.4 | you, they, some, changing |
| 50 | `(S/S)\(S\S)` | 30.3 | i, have, were, ’re |

失败日志汇总（dev, 49 failures）: by UPOS/deprel of failing word: [['END/END', 15], ['ADV/advmod', 5], ['NOUN/root', 4], ['VERB/root', 4], ['NOUN/obj', 3], ['ADP/case', 2], ['ADJ/amod', 2], ['NUM/flat', 2], ['AUX/aux', 1], ['ADV/root', 1], ['DET/det', 1], ['NUM/compound', 1], ['PROPN/compound', 1], ['VERB/ccomp', 1], ['NOUN/nsubj', 1]]; by word: [['<END>', 15], ['joke', 4], ['there', 2], ['interesting', 2], ['two', 2], ['in', 1], ['would', 1], ['number', 1], ['ago', 1], ['this', 1], ['thirty', 1], ['north', 1], ['idea', 1], ['stop', 1], ['matter', 1]]; by position: [[2, 1], [3, 8], [4, 8], [5, 12], [6, 10], [7, 6], [8, 2], [10, 2]]


## 高频范畴（left_B_SA_d4_le10, MDL-selected seed 1）

| # | category | expected count | 20 words |
|---|---|---|---|
| 1 | `S` | 1450.9 | it, <C3>, <C1>, n't, a, that, the, said, like, was, we, and, say, want, <C13>, he, am, as, know, she |
| 2 | `S\S` | 940.9 | <C1>, <C3>, it, that, <C7>, out, there, for, a, up, now, good, here, them, beautiful, today, my, i, long, she |
| 3 | `S/S` | 723.1 | i, n't, and, that, you, so, he, the, no, oh, is, did, there, know, my, we, yeah, then, <C4>, n’t |
| 4 | `PP` | 685.4 | 're, <C16>, is, <C3>, one, her, <C14>, not, about, <C7>, a, <C2>, all, the, are, have, you, good, can, by |
| 5 | `NP\S` | 523.8 | i, is, was, and, to, we, you, on, are, it, <C3>, does, three, way, <C20>, looks, me, <C1>, get, like |
| 6 | `N` | 472.3 | the, <C1>, i, at, <C3>, from, this, of, he, his, then, there, these, for, we, it, so, take, into, they |
| 7 | `S\NP` | 463.5 | <C3>, a, it, <C18>, with, right, <C1>, down, work, as, very, be, have, my, sorry, more, doing, once, trying, something |
| 8 | `NP/S` | 331.3 | i, and, so, she, the, he, yeah, well, had, oh, they, you, <C11>, our, use, your, alright, see, sports, feet |
| 9 | `S/PP` | 320.2 | the, this, we, i, a, <C9>, they, my, 's, 'll, no, all, was, <C2>, <C3>, n't, you, <C5>, there, provides |
| 10 | `S/N` | 246.0 | <C3>, and, a, in, wait, name, world, died, this, seen, history, new, 's, 30, pretty, another, you, enjambment, university, looked |
| 11 | `PP/PP` | 242.7 | the, a, is, <C1>, <C3>, all, have, <C5>, one, very, <C10>, said, got, other, never, they, some, earth, good, really |
| 12 | `PP/S` | 214.6 | but, what, were, just, <C1>, <C7>, and, <C3>, one, do, will, <C19>, is, have, though, god, he, <C4>, renata, not |
| 13 | `(S\S)/S` | 205.9 | of, <C3>, i, my, to, <C7>, that, you, be, long, big, ’m, have, local, oh, 've, car, funny, writing, pizza |
| 14 | `S/((PP\NP)\S)` | 197.7 | that, it, he |
| 15 | `NP` | 180.0 | i, she, we, this, it, <C2>, there, the, another, leave, then, is, will, they, future, you, here, aged, recorder, live |
| 16 | `N/N` | 132.4 | <C1>, and, hand, from, yeah, thursday, quartiles, older, cheaper, strong, meant, march, event, as, cinnamon, limited, 15, academic, delicious, wednesday |
| 17 | `NP/PP` | 125.8 | you, they, i, joke, pretty, from, knows, achieved, friend |
| 18 | `N/S` | 123.8 | for, are, it, not, to, and, already, find, mrs., erasmus, each, yoga, funny, a, 25, five, walk, data, mermaid, accept |
| 19 | `N/PP` | 116.7 | is, <C3>, a, in, and, has, on, to, from, have, <C9>, 's, talked, thousands, my, change, least |
| 20 | `((PP\NP)\S)/PP` | 114.9 | 's, is, <C3>, two |
| 21 | `NP\N` | 111.5 | <C3>, on, is, like, <C10>, <C8>, course, your, people, are, writes, happy, door, black, but, texas, page, dinner, remembered, either |
| 22 | `(PP\NP)\S` | 101.1 | 's, ’s, ’ve |
| 23 | `PP\S` | 95.9 | 'm, never, 's, was, also, one, <C3>, has, nothing, they, a, betty, ask, blue, jobs, supports, to, itself, mistake, structures |
| 24 | `NP\NP` | 89.3 | just, got, like, can, all, also, 's, my, 6, super, 've, but, liked, fish, runs, meant, sending |
| 25 | `(NP\S)/S` | 88.8 | to, <C3>, did, does, first, clear, gon, invisible, family, perfect, united |
| 26 | `N\S` | 88.4 | the, <C0>, <C3>, actually, more, make, now, under, small, new, low, was, all, three, every, ’m, week, roberts |
| 27 | `S/(NP\S)` | 88.1 | it, this, that, he, how, focused, death, can, study, n’t, shit |
| 28 | `S\(NP\S)` | 86.0 | <C4>, know, think, will, see, 'll, mean, south, stood |
| 29 | `S\N` | 84.0 | day, <C19>, percentiles, is, some, people, further, <C3>, other, moment, paper, hire, morning, on, <C1>, wine, men, ’re, i, attended |
| 30 | `(S\NP)/S` | 83.2 | to, not, really, gon, no, an, how, bringing, nine, three, can, name, age, brain, less, noon |
| 31 | `S\(N/NP)` | 79.8 | <C2>, says, animal |
| 32 | `(S\S)/PP` | 77.7 | you, <C3>, was, 's, with, they, gram, enjoyed |
| 33 | `S\PP` | 74.8 | ’s, <C1>, <C3>, us, was, going, different, opposite, idiot, pack, services, took, gone, hour, nature, likes, start |
| 34 | `((S\S)/PP)/S` | 65.2 | a, to, we, your |
| 35 | `S\(NP/S)` | 63.8 | know, me, <C13>, sleep, that, broad, nathan, brown, great, at |
| 36 | `(N\S)/NP` | 63.0 | the, driving, known, collecting, syria, each, result |
| 37 | `PP/NP` | 62.1 | the, <C3>, she, about, montana, or, 'll, only, made, fourth, achievements, you, make, guy, they, easily, achieved, greek, because, issues |
| 38 | `S/NP` | 59.8 | <C3>, but, a, help, 'm, know, 2011, lipstick, see, right, this, 's, study, also |
| 39 | `PP/N` | 56.2 | is, <C3>, up, will, also, face, him, grown, recording, source, better, 've, demonstrate |
| 40 | `NP\PP` | 53.6 | in, were, same, happen, or, largest, roll, ferries |
| 41 | `S\(PP\NP)` | 52.2 | it, <C14>, that, okay, starving, nervous, 19, shit, received |
| 42 | `(S\NP)/N` | 51.4 | <C3>, to, from, stay, case, rules, example |
| 43 | `(S/S)/N` | 48.3 | and, <C3>, yes, well, sorry, middle, cara, them |
| 44 | `NP\(S\S)` | 47.7 | 's, ’s, comes, knew, shrunk |
| 45 | `(NP\N)/S` | 45.9 | <C10>, <C2>, two, name, looking, behind |
| 46 | `((PP\NP)\S)/S` | 44.5 | 's, hands |
| 47 | `(NP\S)\PP` | 43.7 | in, work, ’re |
| 48 | `S\(PP/PP)` | 42.9 | of, not, go, wrong, before, nephew, so, words, eleven, sister, fled, hey, islands |
| 49 | `(S\(NP\S))/S` | 40.8 | do, mean, <C3>, now, betty, wo |
| 50 | `NP/N` | 40.7 | <C3>, year, floor, here, afraid, medical, mayor, dream, move, my, mistake, each, things, mystery, reach, exam, studies, england |

失败日志汇总（dev, 61 failures）: by UPOS/deprel of failing word: [['END/END', 22], ['ADV/advmod', 4], ['NOUN/obl', 4], ['VERB/xcomp', 4], ['ADP/case', 3], ['ADJ/amod', 2], ['NOUN/compound', 2], ['DET/det', 2], ['NOUN/obj', 2], ['NOUN/root', 2], ['NOUN/nsubj', 1], ['PRON/obj', 1], ['NUM/root', 1], ['PROPN/compound', 1], ['NUM/nummod', 1]]; by word: [['<END>', 22], ['thinking', 3], ['of', 2], ['always', 1], ['last', 1], ['mom', 1], ['phone', 1], ['any', 1], ['it', 1], ['morning', 1], ['six', 1], ['north', 1], ['right', 1], ['yet', 1], ['15', 1]]; by position: [[3, 6], [4, 13], [5, 13], [6, 10], [7, 6], [8, 6], [9, 4], [10, 2], [11, 1]]


## 高频范畴（left_C_SA_d4_le10, MDL-selected seed 2）

| # | category | expected count | 20 words |
|---|---|---|---|
| 1 | `S[dcl]\S[dcl]` | 1196.2 | <C10>, <C2>, it, n't, not, on, and, so, are, <C21>, good, now, that, really, all, is, like, there, down, <C7> |
| 2 | `S[dcl]` | 638.4 | 's, is, was, and, ’s, they, <C2>, i, the, of, then, <C1>, my, did, one, no, it, looks, yeah, had |
| 3 | `S[dcl]/S[dcl]` | 545.7 | it, that, so, oh, this, yeah, well, she, no, we, there, was, i, he, for, like, <C0>, yes, <C4>, sorry |
| 4 | `S[b]/NP` | 301.1 | know, do, <C19>, 'm, have, think, did, am, <C10>, get, see, like, 'll, will, guess, hope, just, can, go, 'd |
| 5 | `(S[dcl]\S[dcl])/S[dcl]` | 170.9 | it, that, what, a, have, we, okay, as, how, there, three, at, <C7>, says, into, drank, still, exist, put, santa |
| 6 | `S[dcl]/(S[b]/NP)` | 169.6 | i, you, senate |
| 7 | `S[dcl]\S[b]` | 148.2 | to, <C1>, it, great, we, just, our, super, these, uh, impossible, back, displaced, yoga, american, thank, real, questions, here, following |
| 8 | `S[dcl]\(S[dcl]\S[dcl])` | 103.3 | was, does, 's, also, are, us, two, funny, do, erasmus, obeys, <C17>, first, mother, like, laura, worse, roberts, guessed, sense |
| 9 | `(S[dcl]\S[dcl])/(S[b]/NP)` | 96.1 | n't, i, to, you |
| 10 | `S[b]\S[dcl]` | 86.4 | like, of, want, not, <C19>, an, her, hard, just, feel, remember, close, need, what, maybe, came |
| 11 | `S[b]\S[pss]` | 79.7 | <C16>, and, same, way, study, old, horse, event, find, open, deal, problem, removed, water, data, following, animal, island |
| 12 | `(S[dcl]\S[dcl])/(S[b]\S[pss])` | 62.8 | the, years |
| 13 | `((S[dcl]\S[dcl])/S[dcl])/S[dcl]` | 62.4 | a, i, have, this, is, <C23>, here, science, which |
| 14 | `(S[dcl]/S[dcl])/S[dcl]` | 57.9 | this, that, yeah, he, she, <C4>, for, surprised, right |
| 15 | `(S[dcl]\S[pss])\S[b]` | 49.0 | <C3>, lot, problem, just, moment, matter, connection, painting, feature, few |
| 16 | `S[dcl]/((S[dcl]\S[pss])\S[b])` | 47.0 | a |
| 17 | `S[dcl]/((S[to]\S[to])\NP)` | 45.2 | the |
| 18 | `NP/S[dcl]` | 44.6 | said, mean, say, love, 're, thought, have |
| 19 | `S[dcl]\((S[dcl]/S[dcl])/S[dcl])` | 41.4 | is, little, letter, joke, bear, dream, teacher, game, mistake, past, jobs, many, few |
| 20 | `S[dcl]/(NP/S[dcl])` | 35.5 | i, she |
| 21 | `N/S[b]` | 35.5 | what, going, about, anything, interesting, some, fair, exciting, on, sore, under, happen, central, d- |
| 22 | `S[dcl]/NP` | 33.0 | you, they, pete |
| 23 | `(S[dcl]/S[dcl])/(S[b]/NP)` | 32.4 | i |
| 24 | `S[b]\(S[dcl]/S[dcl])` | 32.0 | 's, <C18>, is, doing |
| 25 | `(S[to]\S[to])\NP` | 30.5 | <C16>, questions |
| 26 | `(S[dcl]\(S[dcl]\S[dcl]))/S[dcl]` | 26.8 | he, of, some |
| 27 | `(S[to]\S[pss])/S[b]` | 23.0 | they, my, you |
| 28 | `NP/N` | 22.9 | me, one, definitely, six |
| 29 | `S[dcl]/(N/S[b])` | 22.5 | 's, was, really, studied, seems |
| 30 | `S[dcl]\((S[to]\S[pss])/S[b])` | 22.0 | <C9>, name, sister, shirts, camera |
| 31 | `S[dcl]\((S[to]\S[pss])/S[ng])` | 20.7 | <C17>, right, allowed, bringing, both, enough |
| 32 | `(S[dcl]\S[dcl])\S[dcl]` | 18.9 | he, make, her, not, gross, earth, members, active, kill, grew, guy |
| 33 | `S[pss]\S[dcl]` | 18.0 | <C3>, cultural, rights |
| 34 | `S[b]/S[dcl]` | 18.0 | and, again |
| 35 | `(S[dcl]\S[dcl])/(S[dcl]/S[dcl])` | 17.0 | but, love, look, rained |
| 36 | `S[b]/S[ng]` | 17.0 | 're, deal |
| 37 | `(S[ng]\S[ng])\S[dcl]` | 16.6 | in |
| 38 | `((S[to]\S[dcl])\S[pss])/S[b]` | 15.0 | my |
| 39 | `((S[to]\S[to])\NP)/S[dcl]` | 14.7 | <C16>, median, answer |
| 40 | `S[dcl]/((S[dcl]\S[dcl])/S[dcl])` | 14.6 | 's |
| 41 | `S[dcl]\(S[b]\S[dcl])` | 14.0 | <C11>, talking, sports |
| 42 | `S[dcl]\(S[ng]\S[ng])` | 14.0 | <C13>, here |
| 43 | `(S[dcl]\NP)\S[pss]` | 13.8 | are, made, go |
| 44 | `S[dcl]/(NP/N)` | 13.0 | 's, was, makes |
| 45 | `S[dcl]/((S[dcl]\NP)\S[pss])` | 12.8 | we, you |
| 46 | `NP` | 11.0 | 're, got |
| 47 | `(S[dcl]/S[dcl])/(S[dcl]\S[dcl])` | 10.0 | we, customers, those |
| 48 | `(S[dcl]\S[dcl])/(NP/N)` | 10.0 | at, with, for |
| 49 | `(S[b]/NP)/(S[dcl]/S[dcl])` | 9.8 | 'm |
| 50 | `S[dcl]/((S[dcl]\S[to])\S[b])` | 9.0 | to |

失败日志汇总（dev, 75 failures）: by UPOS/deprel of failing word: [['VERB/root', 13], ['ADV/advmod', 8], ['END/END', 7], ['NOUN/root', 6], ['NOUN/nsubj', 5], ['PRON/nsubj', 5], ['ADJ/amod', 4], ['AUX/aux', 4], ['DET/det', 3], ['VERB/xcomp', 3], ['AUX/cop', 2], ['VERB/advcl', 2], ['VERB/acl', 2], ['PART/mark', 1], ['ADV/root', 1]]; by word: [['<END>', 7], ['thinking', 4], ['a', 3], ['are', 2], ['touch', 2], ['only', 2], ['would', 2], ['home', 1], ['mom', 1], ['other', 1], ['get', 1], ['works', 1], ['to', 1], ['ago', 1], ['any', 1]]; by position: [[2, 17], [3, 17], [4, 17], [5, 10], [6, 7], [7, 2], [8, 4], [9, 1]]


## 高频范畴（left_D_SA_d4_le10, MDL-selected seed 1）

| # | category | expected count | 20 words |
|---|---|---|---|
| 1 | `C0` | 1819.9 | <C0>, 's, is, was, are, ’s, me, said, here, had, the, we, and, <C1>, in, says, all, a, this, i |
| 2 | `C0/C0` | 1782.6 | <C0>, it, was, is, the, 's, have, like, to, a, my, that, n't, know, 'm, just, all, i, are, can |
| 3 | `S/C0` | 1387.5 | <C0>, it, that, i, you, there, <C2>, he, this, she, the, we, <C1>, my, of, are, then, a, over, same |
| 4 | `S\S` | 1281.4 | <C0>, <C1>, it, of, good, with, one, in, on, great, now, said, you, them, that, and, beautiful, for, not, right |
| 5 | `S/S` | 565.1 | and, the, <C1>, so, yeah, well, but, no, <C0>, oh, yes, if, because, okay, then, here, um, this, i, usually |
| 6 | `S` | 561.9 | <C1>, <C0>, i, it, yeah, first, at, to, the, my, this, world, something, on, and, down, that, of, he, no |
| 7 | `(S\S)/C0` | 407.5 | a, to, i, in, was, that, from, like, and, the, is, not, about, ’m, up, are, betty, at, 's, looks |
| 8 | `C0/S` | 398.5 | <C0>, is, it, 's, this, a, like, and, the, <C1>, ’s, then, to, of, my, how, n't, on, getting, hair |
| 9 | `(C0/C0)/C0` | 353.5 | 'm, a, do, know, ’re, ca, our, want, really, never, it, even, been, called, go, years, many, looking, vlog, are |
| 10 | `C0/(C0/C0)` | 284.1 | 's, did, do, n't, i, to, just, they, <C1>, really, in, he, not, even, the, have, her, of, you, make |
| 11 | `(S\S)/S` | 223.7 | <C0>, the, of, that, at, is, to, not, any, writing, and, gram, bringing, exist, wonderful, mrs., six, really, have, bad |
| 12 | `S/(C0/C0)` | 216.7 | i, we, they, my, could, ten, word, age, judge, square, dad, ’s |
| 13 | `(S/C0)/C0` | 146.1 | she, that, <C1>, you, he, we, do, some, in, those, process, are, answer, dad, gone, median, usually, yeah, bos |
| 14 | `(S/C0)/S` | 144.9 | <C2>, own, real |
| 15 | `S\C0` | 134.5 | <C0>, <C1>, there, from, a, 're, never, free, up, hard, it, ways, city, down, know, okay, follows, whatever, nations, q |
| 16 | `(S\S)/(S/C0)` | 120.8 | the, your, on, his, gon, i, than, are, its, sending, toph, likes |
| 17 | `C2` | 93.0 | <C1>, or, their, so, for, of, our, <C0>, uh, you, called, ’m, i, this, pete, care, equals, third, ie6, potential |
| 18 | `C0/((S/C0)/S)` | 85.5 | the |
| 19 | `C1/C0` | 85.4 | and, they, we, the, so, yoga, today, nonna, winking, therefore, blinking, major, england, wikihow, new |
| 20 | `S\(C0/C0)` | 82.9 | <C0>, time, of, are, <C1>, whatsoever, hurt, fair, connection, judy, starving, finding, strong, wails, source, na, possible, mistakes, past, sentence |
| 21 | `C0/(S/C0)` | 82.6 | a, 's, one, the, to, of, other, me, big, 've, magic, end, most, long, they, she |
| 22 | `C1\C0` | 80.0 | <C0>, to, quite, original, climate, can, she, not, video, thus, warm, second, backed, knows, ’ve, peace, dreams, responsibility, bit, wrapped |
| 23 | `(S\S)/(C0/C0)` | 69.4 | to, you, was, at, very, done, this, more, years, point, mistakes |
| 24 | `((C1/C0)/C2)/(C0/C0)` | 63.1 | do, get, <C0>, understand, loved, knew |
| 25 | `(S/S)/C0` | 62.3 | it, he, oh, his, while, mexico |
| 26 | `S/(S/C0)` | 62.2 | the, <C1>, i, this, you, equipment, pete, my, either, gone |
| 27 | `(C0/C0)/C2` | 61.7 | know, 're, mean, points, badly, tea, roll, times, herself, exam |
| 28 | `S/((C1/C0)/C2)` | 60.0 | i, for |
| 29 | `C0/((C0/C0)/C0)` | 58.1 | <C0>, you, we, <C1>, are, was, the, fully, white, just, still, 30, older, mom, 22, every, six, therefore |
| 30 | `C0\S` | 55.5 | <C1>, 's, before, their, is, wrong, lemon, over, mexico, clear, stood, letter, become, bears, lipstick, on, trail, strong, everything, once |
| 31 | `C1` | 52.6 | and, to, in, his, <C1>, anymore, much, via, shoes, thousands, ask |
| 32 | `(C0/C0)/(C0/C0)` | 50.7 | n't, best |
| 33 | `(S/(S/C0))/C0` | 50.2 | i, this |
| 34 | `S/C1` | 47.5 | not, right, correct, more, okay, watch, culture, is, appeared, ask, afraid, worth, year |
| 35 | `S/((C0/C0)/C2)` | 45.2 | you, i |
| 36 | `(S\C0)/C0` | 43.9 | in, an, need, three, work, way, pag |
| 37 | `C0\C0` | 43.1 | is, we, to, have, you, really, an, became, school, appeared, through |
| 38 | `C1\C2` | 39.1 | this, stuff, arrogance, example, would, dinner |
| 39 | `S\(S\C0)` | 36.8 | <C1>, quidditch, under, 2015, learned, gel |
| 40 | `(C0/C0)/(S/C0)` | 36.3 | the, have, at, age |
| 41 | `C0/(S/C1)` | 36.1 | 's, is, pinotage |
| 42 | `S\(C1\C2)` | 35.5 | is, somehow, history |
| 43 | `(C0/C0)/S` | 33.9 | what, 'll, oh, she, it, does, forgot, anything |
| 44 | `(S\C2)\C0` | 33.3 | 're, were, <C0>, started, 'm, worth |
| 45 | `(C0\S)/C0` | 33.2 | a, 's, heard, purpose, more, okay, covered, balance |
| 46 | `((S\S)/S)/C0` | 32.9 | for, into, very, people, really, kinda |
| 47 | `(C0\S)/(C0/C0)` | 32.8 | i, will |
| 48 | `S\(C0\C0)` | 30.8 | like, not, some, so, opposite, runs, asked |
| 49 | `S/((S\C2)\C0)` | 30.4 | they |
| 50 | `C0/C1` | 29.4 | <C0>, get, 2, key, word, large, enter |

失败日志汇总（dev, 44 failures）: by UPOS/deprel of failing word: [['END/END', 16], ['ADV/advmod', 4], ['VERB/advcl', 2], ['NOUN/obl', 2], ['NUM/nummod', 2], ['VERB/root', 2], ['ADJ/amod', 1], ['DET/det', 1], ['PRON/obl', 1], ['PART/root', 1], ['PRON/obj', 1], ['PRON/expl', 1], ['NOUN/obj', 1], ['VERB/ccomp', 1], ['AUX/cop', 1]]; by word: [['<END>', 16], ['there', 4], ['last', 1], ['works', 1], ['any', 1], ['something', 1], ['morning', 1], ['not', 1], ['anything', 1], ['move', 1], ['15', 1], ['throat', 1], ['turn', 1], ['school', 1], ["'re", 1]]; by position: [[2, 2], [3, 5], [4, 5], [5, 12], [6, 5], [7, 4], [8, 5], [9, 3], [10, 2], [11, 1]]
