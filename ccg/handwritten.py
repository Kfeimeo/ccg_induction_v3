"""Hand-written lexicon (§5 upper bound), atoms {S, N, NP, PP}.

Written for the strictly left-branching system: everything to the right of a subject must
be consumed by FA/B> from a functor state, embedded subjects are taken as NP arguments of
the preceding word (there is no online type-raising), and post-verbal modifiers attach
to S (S\\S) because the VP has already been reduced to S when they arrive.

Entries flagged construction-specific (for the L4 criterion) are listed in CONSTRUCTION_SPECIFIC.
The TR variant adds S/(S\\NP) to subject pronouns / determiners (lexicalised type raising).
"""
from __future__ import annotations
from typing import Dict, List
from .category import parse, Cat

P = parse

# ------------------------------------------------------------------ word classes
PRON_SUBJ = "i you we they he she it this that there these those who everything something nothing everyone someone anything everybody somebody one what".split()
PRON_OBJ = "me him her us them it you myself yourself himself herself itself ourselves themselves this that these those something anything nothing everything someone everyone one".split()
DET = "the a an this that these those every each some any no another such all both what which half many most several few much more less".split()
POSS = "my your his her its our their".split()
NOUNS = """movie letter dinner keys pen card story room bed paper cake tea coffee juice chess magazines rice bread joke jokes night people time idea kind set end reasons lot thing things mom dad phone number lack moderation exercise title accident guys trouble lie lies hold trust while bookstore cuffs bed hair volleyball church care blades mice garbage bags pin ass butt mother headaches jeans practice mess morning work computers pattern opposite case nature government bugs pocket school editor voices house day days week weeks year years way man woman men women child children boy girl friend friends family home money water food car house room door hand hands eyes eye head face place world life story book books word words name game games team teams song music movie movies picture pictures class student students teacher job problem problems question questions answer point part parts side fact minute minutes hour hours thing stuff guy girl kids kid dog cat cats dogs baby city country state states war art paper letter reason love power law history science study studies research data information system group groups company business market party government area areas level number numbers cards card motion strike touch fun secret past nights weekend title protector exercise moderation lack cuffs trouble mexico""".split()
PROPN = "tom ann norton melanie coron kim mary penn state north america athens bangladesh rezwan bogard susan marlena mexico saturdays wednesdays wednesday john god london paris english france germany china europe".split()
ADJ = """taller bigger faster better little good stupid fun particular similar secret interesting incredible crucial totalitarian dark tired hungry done physical last other long complete excellent dead global first only right big small new old great bad best better worse happy sad sure nice hard easy true real free full high low young important different same whole own next late early strange funny hot cold cool warm huge tiny beautiful ugly rich poor wrong ready able possible black white red green blue awake sick alive dead busy careful""".split()
NUM = "two three six thirty thirteen four five seven eight nine ten twenty hundred thousand one zero".split()
ADV_S = "so now then also just still even really actually maybe probably here there again too always never often sometimes usually already yet later back home anywhere ago officially first well right ever only away out around today tonight yesterday tomorrow though anyway indeed practically".split()
ADV_VP = "just still even really actually always never often sometimes usually already also probably officially only ever".split()
ADV_DEG = "very really so too pretty quite rather extremely kind sort".split()
NEG = "not n't n’t never".split()
AUX = "will would can could should may might must shall do does did have has had am is are was were be been being 'll 've 'd 're 'm 's ’s wo ca ai to gon wan".split()
COP = "am is are was were be been being 's ’s 'm 're".split()
PREP = "in on at to for of with by from about into over after before under between through during without against among around as like than up out off down near since until across behind toward towards upon inside outside per via".split()
PARTICLE = "up out off down away back over on in around through".split()
V_INTR = """know go come happened happen happened goes going came leaving looks staying dying working sleeping talking sit sat stand stood wait waited laugh laughed cry cried live lived die died work worked run ran walk walked fall fell rise rose start started stop stopped end ended change changed matter matters mean means help helps help agree agreed care cares thinking eat ate drink drank read sing sang dance danced play played win won lose lost stay stayed leave left move moved sleep slept swim swam smile smiled""".split()
V_TRANS = """hates hate bought sold wrote cooked drink drinks reads filed cutting read eats eat eating ate play plays know knew have has had got get gets put puts see saw said say says think thought want wanted like liked love loved need needed make made makes take took takes give gave gives call called spend spent lose lost touch touched affects affect wished wish wanted let mean meant remember packed wiped suck whip fortify tell told ask asked find found keep kept hold held bring brought buy bought sell sold send sent show showed hear heard feel felt leave left meet met read write wrote eat ate drink drank play played watch watched use used try tried help helped stop stopped start started move moved open opened close closed hit hit pay paid win won lose lost forget forgot understand understood believe believed hate hated enjoy enjoyed learn learned teach taught catch caught cut cut break broke build built draw drew hang hung hurt hurt kill killed lead led pick picked pull pulled push pushed reach reached run ran turn turned wear wore doing done making getting giving having taking seeing thinking""".split()
V_DITRANS = "showed gave give gave gives told tell give sent send show showed brought bring bought buy made make call called ask asked teach taught pay paid".split()
V_PP = "put puts go goes went come came look looked talk talked think thought wait waited live lived stay stayed get got sit sat work worked care cared agree agreed belong belonged happen happened".split()
V_PPNP = "put puts took take give gave send sent bring brought get got".split()
V_CLAUSE = "know knew think thought say said says mean meant guess hope hoped believe believed see saw hear heard wish wished want wanted told tell remember feel felt suppose bet figured figure".split()   # zero-complementizer: NP then VP
V_CONTROL = "want wanted need needed try tried like liked love loved hope hoped start started stop stopped keep kept begin began seem seemed have has had got get gon wan going".split()   # (S\NP)/(S\NP): "want to go"
V_OBJCONTROL = "want wanted let make made help see saw hear heard told tell ask asked need needed".split()   # ((S\NP)/(S\NP))/NP : "let it go"
GERUND = "thinking going doing making getting giving leaving staying dying happening working talking sleeping".split()
INTJ = "yeah uh um oh well okay ok yes no hey wow ah anyways like right so alright please thanks hmm mm huh".split()
CONJ = "and or but nor".split()
SUBORD = "when if because while after before since although though unless until so whether as once".split()
WH_ADV = "when where why how".split()


def _add(lex: Dict[str, set], words, cats):
    for w in words:
        for c in cats:
            lex.setdefault(w, set()).add(P(c))


def build(variant: str = 'SA', vocab_counts: Dict[str, int] = None, max_words: int = 500) -> Dict[str, List[Cat]]:
    """variant: 'SA' (default, no type raising) or 'TR' (adds lexical type raising for subjects).

    If vocab_counts is given, the lexicon is restricted to the `max_words` most frequent
    hand-written words (task §5: 300-500 words).
    """
    lex: Dict[str, set] = {}
    _add(lex, PRON_SUBJ, ['NP'])
    _add(lex, PRON_OBJ, ['NP'])
    _add(lex, DET, ['NP/N'])
    _add(lex, ['all', 'both', 'half', 'such'], ['NP/NP'])
    _add(lex, POSS, ['NP/N'])
    _add(lex, ["'s", '’s'], ['(NP/N)\\NP'])
    _add(lex, NOUNS, ['N', 'NP', 'N/N'])
    _add(lex, PROPN, ['NP', 'N/N', 'N'])
    _add(lex, ADJ, ['N/N'])
    _add(lex, NUM, ['N/N', 'NP', 'N'])
    _add(lex, ADV_S, ['S/S', 'S\\S'])
    _add(lex, ['here', 'there', 'home', 'away', 'back', 'out', 'around', 'inside', 'outside', 'upstairs', 'downstairs'], ['PP'])
    _add(lex, ADV_VP, ['(S\\NP)/(S\\NP)'])
    _add(lex, ADV_DEG, ['(N/N)/(N/N)'])
    _add(lex, ['very', 'really', 'so', 'too', 'pretty', 'quite'], ['(S\\S)/(S\\S)', '(S/S)/(S/S)'])
    _add(lex, ['than'], ['PP/NP', '(S\\S)/NP', '(N\\N)/NP', '(NP\\NP)/NP', '((N/N)\\(N/N))/NP', '(S\\S)/S'])
    _add(lex, ['more'], ['N/N', 'NP/N', '(N/N)/(N/N)'])
    _add(lex, ['does', 'do', 'did'], ['S\\NP'])
    _add(lex, NEG, ['(S\\NP)/(S\\NP)', '(N/N)/(N/N)', 'NP/NP', 'PP/PP', 'S/S'])
    _add(lex, AUX, ['(S\\NP)/(S\\NP)'])
    _add(lex, COP, ['(S\\NP)/NP', '(S\\NP)/(N/N)', '(S\\NP)/PP'])
    _add(lex, PREP, ['PP/NP', '(S\\S)/NP', '(NP\\NP)/NP', '(N\\N)/NP'])
    _add(lex, ['of'], ['(N\\N)/NP', '(NP\\NP)/NP'])
    _add(lex, PARTICLE, ['PP', 'S\\S'])
    _add(lex, ['to'], ['(S\\NP)/(S\\NP)', '(S\\S)/(S\\NP)'])        # infinitival / purpose
    _add(lex, ['like'], ['(S\\NP)/NP', 'PP/NP', 'S/S', '(S\\S)/NP'])
    _add(lex, V_INTR, ['S\\NP'])
    _add(lex, V_TRANS, ['(S\\NP)/NP'])
    _add(lex, V_DITRANS, ['((S\\NP)/NP)/NP'])
    _add(lex, V_PP, ['(S\\NP)/PP'])
    _add(lex, V_PPNP, ['((S\\NP)/PP)/NP'])
    _add(lex, V_CLAUSE, ['((S\\NP)/(S\\NP))/NP', '(S\\NP)/S'])
    _add(lex, V_CONTROL, ['(S\\NP)/(S\\NP)'])
    _add(lex, V_OBJCONTROL, ['((S\\NP)/(S\\NP))/NP'])
    _add(lex, GERUND, ['S\\NP', 'N', '(S\\NP)/NP'])
    _add(lex, INTJ, ['S/S', 'S\\S'])
    # --- pre-subject material must consume the subject (no type raising): (S/(S\\NP))/NP
    _add(lex, INTJ + ADV_S + CONJ + ['so', 'then', 'now', 'well', 'anyways', 'like'], ['(S/(S\\NP))/NP'])
    _add(lex, PREP, ['((S/(S\\NP))/NP)/NP'])                           # sentence-initial PP
    _add(lex, ['this', 'that', 'every', 'last', 'next', 'some', 'each', 'one', 'all', 'the', 'a'], ['(S\\S)/N'])   # temporal NP adverbials
    _add(lex, NOUNS + PROPN, ['N/PP', 'NP/PP'])                          # relational nouns: a lot of, kind of, protector of
    _add(lex, NUM + ['lot', 'kind', 'sort', 'some', 'all', 'none', 'most', 'one'], ['NP/PP'])
    _add(lex, ['back', 'right', 'just', 'only', 'even', 'way', 'all', 'still', 'also'], ['PP/PP', '(S\\S)/(S\\S)'])
    _add(lex, ADV_VP, ['(N/N)/(N/N)'])
    _add(lex, PROPN, ['NP/NP'])
    _add(lex, ['you'], ['NP/N'])
    _add(lex, ['though', 'anyway', 'either', 'too', 'then'], ['S\\S'])
    _add(lex, ['mess', 'waive', 'add', 'confirm', 'modify', 'lift', 'repair', 'attack', 'observed', 'restricted'], ['(S\\NP)/NP'])
    _add(lex, ['have', 'had', 'has', 'get', 'got', 'watch', 'watched', 'keep', 'kept', 'find', 'found'], ['((S\\NP)/(S\\NP))/NP'])
    _add(lex, ['done', 'gone', 'over', 'here', 'there', 'back', 'home', 'ready', 'sure', 'right', 'okay', 'fine', 'alone', 'asleep', 'awake'], ['S\\NP'])  # predicative after aux
    _add(lex, ADJ, ['S\\NP'])                                            # "i 'm officially done" (aux + adjectival predicate)
    _add(lex, CONJ, ['(S\\S)/S', '(NP\\NP)/NP', '(N\\N)/N', '((N/N)\\(N/N))/(N/N)', '(S\\S)/(S\\NP)', '(PP\\PP)/PP', 'S/S'])
    _add(lex, SUBORD, ['((S/S)/(S\\NP))/NP', '((S\\S)/(S\\NP))/NP'])
    _add(lex, ['so', 'because', 'but'], ['(S\\S)/S'])
    _add(lex, ['that'], ['(NP\\NP)/(S\\NP)', '(N\\N)/(S\\NP)', '((NP\\NP)/((S\\NP)/NP))/NP', 'S/S', 'NP', 'NP/N'])
    _add(lex, ['who', 'which'], ['(NP\\NP)/(S\\NP)', '(N\\N)/(S\\NP)', '((NP\\NP)/((S\\NP)/NP))/NP'])
    _add(lex, WH_ADV, ['S/S', '((S/S)/(S\\NP))/NP', '((S\\S)/(S\\NP))/NP'])
    _add(lex, ['there'], ['NP'])                                   # existential
    _add(lex, ['kind', 'sort'], ['(S\\S)/PP', 'N'])                 # "kind of"
    _add(lex, ['na'], ['(S\\NP)/(S\\NP)'])                         # gon na / wan na
    _add(lex, ['gon', 'wan'], ['(S\\NP)/(S\\NP)'])
    if variant == 'TR':
        _add(lex, PRON_SUBJ, ['S/(S\\NP)'])
        _add(lex, DET, ['(S/(S\\NP))/N'])
        _add(lex, POSS, ['(S/(S\\NP))/N'])
        _add(lex, PROPN + NOUNS, ['S/(S\\NP)'])
    if vocab_counts is not None:
        keep = sorted(lex, key=lambda w: -vocab_counts.get(w, 0))[:max_words]
        lex = {w: lex[w] for w in keep if vocab_counts.get(w, 0) > 0}
    return {w: sorted(cs, key=lambda c: str(c)) for w, cs in lex.items()}


# entries that are construction specific (L4): the coordination / clause-taking shapes that
# exist only because the left-branching system cannot delay reduction
CONSTRUCTION_SPECIFIC = {P('(S\\S)/(S\\NP)'), P('((NP\\NP)/((S\\NP)/NP))/NP'), P('((S\\NP)/(S\\NP))/NP'),
                         P('((S/S)/(S\\NP))/NP'), P('((S\\S)/(S\\NP))/NP')}


def to_group_A(lex: Dict[str, List[Cat]]) -> Dict[str, List[Cat]]:
    """Rename PP -> NP for the {S,N,NP} atom group."""
    from .category import rename_atoms
    return {w: sorted({rename_atoms(c, {'PP': 'NP'}) for c in cs}, key=str) for w, cs in lex.items()}
