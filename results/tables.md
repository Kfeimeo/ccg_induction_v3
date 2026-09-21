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
| left_A_SA_d4_le10 | 5 | 140862±998 | 0.985±0.003 | 492.6±20.4 | 2.18±0.02 | 11.7±0.8 | 0.18±0.00 | 0.198±0.010 | 0.520±0.025 | 0.048±0.005 | 0.320±0.031 | 159.4±16.6 | 0.250±0.009 | 0.069±0.008 | 1 |

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

### induction_left_A_SA_d4_le10_seed1

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
