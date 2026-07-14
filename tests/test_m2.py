"""M2 acceptance tests -- 'infer' as executable code.

The R15 rule + M1 canonicalization + M2 typed grammar together = a
decompiler that PROPOSES candidate laws from raw tables. The certified
verifiers (B1/B2/B3/B6/B10) then dispose. This suite is the PROPOSAL
side's acceptance test.

T1  B3 REDISCOVERY: from a raw (e, M_W, s_W, G_F) table with no template
    hints, the top-ranked monomial law is exactly G_F ~ e^2 / (M_W^2
    s_W^2) up to a numerical constant (tree-level Fermi relation). The
    engine returns the correct exponent multiset {-2, -2, 2} as the
    MDL-minimum class.
T2  B5 REDISCOVERY: from a raw (A_22, R_24) table, the engine
    rediscovers R_24 = c * A_22^2 -- exponent {2}, constant recovered.
T3  CANONICAL DEDUPLICATION: 3^n raw candidates collapse to k canonical
    classes; equivalent laws under exponent-multiset symmetry are grouped
    (proof-of-work for M1 as the search-engine's index).
T4  FALSE-LAW REJECTION (scrambled control): on shuffled y-values, no
    candidate reaches the residual bar that B3 hits on real data --
    the engine is a proposer, not a fitter of noise.
T5  VERIFIER HANDOFF (contract check): top candidates carry the exponent
    tuple + constant + canonical signature in the shape the verifiers
    expect (interface freeze for M2 -> B1/B2/... plumbing).
"""

import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from generator.engine import search, enumerate_monomials
from b1_moment_solver.certificate import save_certificate

RNG = np.random.default_rng(0)


def _b3_table(n=80):
    """Sample tree-level: G_F = e^2 / (4 sqrt(2) M_W^2 s_W^2) with random
    physical-range inputs. The engine sees only the table -- no formula,
    no exponent hints."""
    e = RNG.uniform(0.28, 0.34, size=n)             # electric coupling
    MW = RNG.uniform(78.0, 85.0, size=n)            # GeV
    sW = RNG.uniform(0.45, 0.50, size=n)            # sin theta_W
    GF = e ** 2 / (4 * np.sqrt(2) * MW ** 2 * sW ** 2)
    return np.stack([e, MW, sW], axis=1), GF


def _b5_table(n=60):
    A22 = RNG.uniform(0.3, 1.8, size=n)
    R24 = 1.7 * A22 ** 2
    return A22[:, None], R24


def t1_b3():
    X, y = _b3_table()
    ranked, meta = search(X, y, ["e", "MW", "sW"])
    top = ranked[0]
    assert tuple(top["exponents"]) == (2, -2, -2), top["exponents"]
    ms = top["canonical"]["exponent_multiset"]
    assert ms == (-2.0, -2.0, 2.0), ms
    c_true = 1.0 / (4 * np.sqrt(2))
    assert abs(top["fit"]["c"] - c_true) / c_true < 0.01, top["fit"]["c"]
    assert top["fit"]["rel_log_residual"] < 1e-10
    print(f"T1 B3 rediscovery: PASS  law G_F ~ e^2 M_W^-2 s_W^-2 "
          f"recovered from raw table (c_hat = {top['fit']['c']:.5f}, true "
          f"= {c_true:.5f}); {meta['n_classes']} canonical classes "
          f"searched, correct one MDL-minimum")
    return {"exponents": list(top["exponents"]), "c": top["fit"]["c"],
            "n_classes": meta["n_classes"]}


def t2_b5():
    X, y = _b5_table()
    ranked, _ = search(X, y, ["A22"], max_nonzero=1)
    top = ranked[0]
    assert tuple(top["exponents"]) == (2,), top["exponents"]
    assert abs(top["fit"]["c"] - 1.7) / 1.7 < 0.001
    print(f"T2 B5 rediscovery: PASS  R_24 = {top['fit']['c']:.4f} * "
          f"A_22^2 (true 1.7000)")
    return {"exponent": 2, "c": top["fit"]["c"]}


def t3_dedup():
    X, y = _b3_table(60)
    ranked, meta = search(X, y, ["e", "MW", "sW"])
    assert meta["n_raw"] > 4 * meta["n_classes"], meta
    # spot-check: multiset key is invariant under permuting exponents
    # among physically-similar variables -- verify no two entries in the
    # dedupe output share a multiset
    keys = [r["canonical"]["exponent_multiset"] for r in ranked]
    assert len(keys) == len(set(keys)), "dedup produced duplicate keys"
    print(f"T3 canonical dedup: PASS  {meta['n_raw']} raw candidates -> "
          f"{meta['n_classes']} canonical classes ({meta['n_raw']/meta['n_classes']:.1f}x "
          f"compression); M1-style multiset key indexes the search space")
    return {"n_raw": meta["n_raw"], "n_classes": meta["n_classes"]}


def t4_scrambled():
    X, y = _b3_table(80)
    y_scrambled = RNG.permutation(y)
    ranked, _ = search(X, y_scrambled, ["e", "MW", "sW"])
    best_resid = ranked[0]["fit"]["rel_log_residual"]
    real_bar = 1e-8
    assert best_resid > 100 * real_bar, best_resid
    print(f"T4 scrambled control: PASS  best residual on shuffled data = "
          f"{best_resid:.3f} (>> {real_bar:.0e} on real data) -- the "
          f"engine proposes, it does not manufacture")
    return {"best_scrambled_residual": best_resid}


def t5_contract():
    X, y = _b3_table(40)
    ranked, meta = search(X, y, ["e", "MW", "sW"])
    top = ranked[0]
    required = {"exponents", "fit", "k_nonzero", "mdl", "canonical"}
    assert required <= set(top.keys()), (required, top.keys())
    fit_required = {"c", "lnc", "rel_log_residual", "n", "rss_log"}
    assert fit_required <= set(top["fit"].keys())
    canon_required = {"exponent_multiset", "lnc_quantized"}
    assert canon_required <= set(top["canonical"].keys())
    assert "verifier_hook" in meta
    print("T5 contract: PASS  M2 output shape frozen "
          "(exponents/fit/canonical/mdl) -- verifier interface stable")
    return {"schema": "frozen"}


if __name__ == "__main__":
    r1 = t1_b3(); r2 = t2_b5(); r3 = t3_dedup(); r4 = t4_scrambled()
    r5 = t5_contract()
    cert = {
        "certificate_version": "0.3",
        "certificate_class": "NUMERICAL-DISCOVERY (typed grammar; MDL; "
                             "canonical dedup; BENCHMARK tier, E3)",
        "problem": "M2: generator engine (roadmap 'infer' machine, "
                   "acceptance = B3/B5 rediscovery from raw tables)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "m_layer_stipulations": [
            "monomial grammar only this sprint (integer/half exponents); "
            "sufficient for B3/B5; wider grammars deferred to M2-b",
            "log-linear regression assumes positive inputs and outputs",
            "canonical key = sorted exponent multiset (R15/M1 flavor); "
            "the multiplicative constant is a fit parameter, not part of "
            "the equivalence class",
            "the engine only PROPOSES; certified verifiers dispose",
        ],
        "headline": "raw-table proposer that rediscovers G_F ~ e^2 M_W^-2 "
                    "s_W^-2 (B3) and R_24 ~ A_22^2 (B5) with no template "
                    "hints; canonical dedup compresses the search space; "
                    "scrambled controls reject the noise-fitting failure "
                    "mode. The 'infer' word of roadmap-v2, executable.",
        "results": {"T1": r1, "T2": r2, "T3": r3, "T4": r4, "T5": r5},
    }
    save_certificate(cert, os.path.join(os.path.dirname(__file__), "..",
                                        "certificates",
                                        "m2_certificate.json"))
    print("\nCertificate written: certificates/m2_certificate.json")
    print("ALL M2 TESTS PASS")
