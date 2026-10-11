// Probability models read by the algorithms.  The parameters live in the Python Model objects
// (ccg/model.py, ccg/cky.py::CKYModel); the Python bridge copies them into these tables.
#pragma once
#include <cmath>
#include <memory>
#include "core.h"

namespace ccg {

// Witten-Bell transitions P(c | state) shared between light copies of a Model (model.copy()
// shares `trans`/`lam`), hence a separate, shareable table.
struct TransTable {
    std::unordered_map<uint64_t, double, U64Hash> trans;   // (state, cat) -> P
    std::unordered_map<Id, double> lam;                    // state -> lambda
    double lam_of(Id state) const {
        auto it = lam.find(state);
        return it == lam.end() ? 0.0 : it->second;
    }
    double trans_of(Id state, Id c) const {
        auto it = trans.find(pack2(state, c));
        return it == trans.end() ? 0.0 : it->second;
    }
};

// model.w(prev, c, word) and model.final_weight() for the prefix-state systems.
struct Scorer {
    Kind kind = K_LEFT;
    bool conditional = false;
    double beta = 1.0;                      // PowerModel exponent
    double stop_p = 0.5;
    bool has_goal = false;                  // the stop factor applies iff prev == model.goal (a category)
    Id model_goal = NONE;
    std::unordered_map<uint64_t, double, U64Hash> emit;    // (cat, word) -> P(w|c)
    std::unordered_map<uint64_t, double, U64Hash> theta;   // (word, cat) -> P(c|w)  (conditional)
    std::unordered_map<Id, double> bo;                     // cat -> backoff P(c)
    std::shared_ptr<TransTable> tt;
    std::unordered_map<Id, Id> alias;                      // DevModel: word -> training key

    Id map_word(Id w) const {
        if (alias.empty()) return w;
        auto it = alias.find(w);
        return it == alias.end() ? w : it->second;
    }
    double raw_w(Id prev, Id c, Id word) const {
        word = map_word(word);
        if (conditional) {
            auto it = theta.find(pack2(word, c));
            return it == theta.end() ? 0.0 : it->second;
        }
        auto e = emit.find(pack2(c, word));
        if (e == emit.end() || e->second == 0.0) return 0.0;
        double lam = tt ? tt->lam_of(prev) : 0.0;
        auto b = bo.find(c);
        double p = (1.0 - lam) * (b == bo.end() ? 0.0 : b->second);
        if (lam != 0.0) p += lam * tt->trans_of(prev, c);
        if (has_goal && prev == model_goal) p *= (1.0 - stop_p);
        return p * e->second;
    }
    double w(Id prev, Id c, Id word) const {
        double x = raw_w(prev, c, word);
        if (beta != 1.0) return x > 0.0 ? std::pow(x, beta) : 0.0;
        return x;
    }
    double final_weight() const {
        double fw = conditional ? 1.0 : stop_p;
        return beta != 1.0 ? std::pow(fw, beta) : fw;
    }
};

// CKYModel: P(expansion | parent) with Witten-Bell smoothing, P(w | c) from the base model.
struct CKYScorer {
    std::unordered_map<Id, double> lam, plex;
    std::unordered_map<Key128, double, Key128Hash> pe;      // (parent, rule), (lcat, rcat) -> P
    std::unordered_map<uint64_t, double, U64Hash> emit;     // (cat, word) -> P

    double lam_of(Id parent) const { auto it = lam.find(parent); return it == lam.end() ? 0.0 : it->second; }
    double exp_p(Id parent, uint8_t rule, Id l, Id r) const {
        double la = lam_of(parent);
        auto it = pe.find(Key128{pack2(parent, rule), pack2(l, r)});
        double p = it == pe.end() ? 0.0 : it->second;
        return la * p + (1.0 - la) * 0.01;      // backoff: uniform over a nominal 100 expansions
    }
    double lex_p(Id parent, Id word) const {
        double la = lam_of(parent);
        auto pl = plex.find(parent);
        double p = la * (pl == plex.end() ? 0.0 : pl->second) + (1.0 - la) * 0.5;
        auto e = emit.find(pack2(parent, word));
        return p * (e == emit.end() ? 0.0 : e->second);
    }
};

}  // namespace ccg
