"""Bridge to the C++ extension ``ccg._ccg_native`` (native/, nanobind + MSVC; build with
``scripts/build_native.ps1``).

The extension re-implements the three parsing systems — strict left-branching lattice
(ccg/lattice.py), stack lattice (ccg/stack_lattice.py) and the CKY chart with the Eisner normal
form (ccg/cky.py) — together with forward-backward / inside-outside, Viterbi, the E-step
statistics and the unpruned state-set searches of the proposal steps (ccg/mdl.py).  Categories
and parser states cross the boundary as the project's own Python objects (nested tuples,
``Stack`` tuples); model parameters are copied from the Python ``Model`` / ``CKYModel`` into
native scorer tables, cached per model version (``Model._v``).

The pure-Python modules stay the reference implementation; they dispatch here when the
extension is importable.  ``CCG_NATIVE=0`` in the environment disables the extension.
"""
from __future__ import annotations
import os
from typing import Dict, List, Optional

_N = None
available = False
if os.environ.get('CCG_NATIVE', '1').strip().lower() not in ('0', 'false', 'no', 'off'):
    try:
        from . import _ccg_native as _N   # type: ignore
        available = True
    except ImportError:
        _N = None
        available = False

LEFT, STACK = 0, 1


def module_file() -> Optional[str]:
    return getattr(_N, '__file__', None) if _N is not None else None


def register_stack_class(cls) -> None:
    """Native stack states are instances of ccg.stack_lattice.Stack (registered by that module)."""
    if _N is not None:
        _N.set_stack_class(cls)


def set_rules(sa: bool) -> None:
    if _N is not None:
        _N.set_rules(bool(sa))


def is_native_lattice(x) -> bool:
    return _N is not None and isinstance(x, _N.Lattice)


def is_native_chart(x) -> bool:
    return _N is not None and isinstance(x, _N.Chart)


# ----------------------------------------------------------------------------- scorers
_scorer_cache: Dict = {}   # key -> (base model, alias, scorer); the model reference pins its id()
_trans_cache: Dict = {}    # (id(trans), id(lam), kind) -> (trans, lam, TransTable)
_cky_cache: Dict = {}
_CACHE_MAX = 32


def _unwrap(model):
    """PowerModel / DevModel wrappers -> (base model, beta, alias dict or None)."""
    beta, alias, base = 1.0, None, model
    while True:
        if hasattr(base, 'base') and hasattr(base, 'beta') and not hasattr(base, 'lex'):     # em.PowerModel
            beta *= float(base.beta)
            base = base.base
            continue
        if hasattr(base, 'model') and hasattr(base, 'key_of') and not hasattr(base, 'lex'):   # induce.DevModel
            alias = base.key_of
            base = base.model
            continue
        return base, beta, alias


def _trans_table(trans, lam, kind):
    key = (id(trans), id(lam), kind)
    hit = _trans_cache.get(key)
    if hit is not None and hit[0] is trans and hit[1] is lam:
        return hit[2]
    tt = _N.TransTable(trans, lam, kind)
    if len(_trans_cache) >= _CACHE_MAX:
        _trans_cache.clear()
    _trans_cache[key] = (trans, lam, tt)
    return tt


def scorer_for(model, kind: int):
    """Native scorer for a prefix-state model (Model, UniformModel, PowerModel, DevModel)."""
    v = getattr(model, '_v', None)
    if v is not None:                      # a plain model (the common case): no wrapper to unwrap
        base, beta, alias = model, 1.0, None
    else:
        base, beta, alias = _unwrap(model)
        v = getattr(base, '_v', None)
    key = (id(base), v, beta, id(alias) if alias is not None else None, kind)
    hit = _scorer_cache.get(key)
    if hit is not None and hit[0] is base and (alias is None or hit[1] is alias):
        return hit[2]
    sc = _N.Scorer(kind)
    if getattr(base, 'kind', 'generative') == 'conditional':
        sc.set_conditional(base.theta)
    else:
        sc.set_generative(base.emit, base.bo, _trans_table(base.trans, base.lam, kind), float(base.stop_p), base.goal)
    if alias is not None:
        sc.set_alias(alias)
    sc.beta = beta
    if v is not None:
        if len(_scorer_cache) >= _CACHE_MAX:
            _scorer_cache.clear()
        _scorer_cache[key] = (base, alias, sc)
    return sc


def cky_scorer_for(model):
    v = getattr(model, '_v', None)
    key = (id(model), v)
    hit = _cky_cache.get(key)
    if hit is not None and hit[0] is model:
        return hit[1]
    sc = _N.CKYScorer(model.pe, model.lam, model.plex, model.base.emit)
    if v is not None:
        if len(_cky_cache) >= _CACHE_MAX:
            _cky_cache.clear()
        _cky_cache[key] = (model, sc)
    return sc


def clear_caches() -> None:
    _scorer_cache.clear(); _trans_cache.clear(); _cky_cache.clear()


# ----------------------------------------------------------------------------- prefix-state lattices
def build_lattice(words, support, max_depth=4, goal='S', beam=0):
    if beam:
        raise NotImplementedError('the diversity beam is not implemented in the native backend')
    return _N.build_lattice(words, support, max_depth, goal, LEFT, 1, True)


def build_stack_lattice(words, support, max_depth=4, goal='S', max_stack=3, cascade=True, beam=0):
    if beam:
        raise NotImplementedError('the diversity beam is not implemented in the native backend')
    return _N.build_lattice(words, support, max_depth, goal, STACK, max_stack, cascade)


def Z(lat, model, goal) -> float:
    return _N.Z(lat, scorer_for(model, lat.kind), goal)


def forward_backward(lat, model, goal):
    """(Z, {(k, cat): posterior}, [(k, (prev, cat, nxt, rule, w), posterior)])."""
    return _N.forward_backward(lat, scorer_for(model, lat.kind), goal)


def viterbi(lat, model, goal):
    return _N.viterbi(lat, scorer_for(model, lat.kind), goal)


def e_step(lats: List, model, goal, beta: float = 1.0, hard: bool = False) -> dict:
    """em.e_step over native lattices (all of one kind)."""
    kind = lats[0].kind if lats else LEFT
    plain = scorer_for(model, kind)
    if beta != 1.0 and not hard:
        from .em import PowerModel
        return _N.e_step(lats, scorer_for(PowerModel(model, beta), kind), plain, goal, False)
    return _N.e_step(lats, plain, None, goal, hard)


# ----------------------------------------------------------------------------- search helpers (mdl.py)
def successors(state, c, kind, max_depth, max_stack=1, cascade=True):
    return _N.successors(state, c, kind, max_depth, max_stack, cascade)


def forward_states(words, upto, support, kind, max_depth, max_stack=1, cascade=True):
    return _N.forward_states(words, upto, support, kind, max_depth, max_stack, cascade)


def suffix_completes(words, states, k, support, goal, kind, max_depth, max_stack=1, cascade=True):
    return _N.suffix_completes(words, states, k, support, goal, kind, max_depth, max_stack, cascade)


def oracle_check(words, F, c, k, support, goal, kind, max_depth, max_stack=1, cascade=True):
    """starts = successors of every state in F on c; does the suffix from position k reach the goal?"""
    return _N.oracle_check(words, F, c, k, support, goal, kind, max_depth, max_stack, cascade)


def oracle_filter(words, F, cands, k, support, goal, kind, max_depth, max_stack=1, cascade=True, first_only=False):
    """The candidates of `cands` (in order) that pass oracle_check; first_only -> at most one."""
    idx = _N.oracle_filter(words, F, cands, k, support, goal, kind, max_depth, max_stack, cascade, first_only)
    return [cands[i] for i in idx]


# ----------------------------------------------------------------------------- CKY
def Chart(words, support, max_depth=4, goal='S', nf=False):
    return _N.Chart(words, support, max_depth, goal, nf)


def cky_Z(chart, model) -> float:
    return _N.cky_Z(chart, cky_scorer_for(model))


def inside_outside(chart, model):
    return _N.inside_outside(chart, cky_scorer_for(model))


def viterbi_tree(chart, model):
    return _N.viterbi_tree(chart, cky_scorer_for(model))


def count_derivations(chart) -> int:
    return _N.count_derivations(chart)


def cky_e_step(charts, model) -> dict:
    return _N.cky_e_step(charts, cky_scorer_for(model))
