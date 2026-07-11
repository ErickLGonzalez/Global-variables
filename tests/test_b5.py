"""B5 tests — cluster decomposition / multi-channel factorization (?5).

T1  Factorization identity holds exactly on local pseudo-data:
    R_24 = A_22² and cross-sector A_22 = A_22_cross.
T2  Discovery finds headline relations (F1, F3, F4_*, F5).
T3  Exact Jacobian rank ⇒ d_identifiable = 1 (single coupling).
T4  Held-out: R_24 predicted from A_22 alone matches observation.
T5  Falsifier: channel-dependent couplings break F1; discovery FAIL.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from b1_moment_solver.certificate import save_certificate
from b5_cluster.discover import broken_residuals, run_discovery
from b5_cluster.pseudo_data import (
    channel_dependent_counterexample,
    make_factorization_data,
)
from b5_cluster.rank import d_identifiable
from b5_cluster.relations import discover_factorization, factorization_holds


def t1_factorization_exact():
    obs = make_factorization_data()
    assert factorization_holds(obs)
    assert obs["A_22"] == obs["A_22_cross"]
    assert obs["R_24_b"] == obs["A_22_cross"] ** 2
    print("T1 factorization exactness: PASS  R_24 = A_22^2; "
          "A_22 = A_22_cross; R_24_b = A_22_cross^2")
    return {"factorization": True, "cross_sector_equal": True}


def t2_headline_discovery():
    result = run_discovery()
    assert result["headline_complete"], result
    names = {r["name"] for r in result["relations_discovered"]}
    assert "F1" in names and "F3" in names and "F5" in names
    assert any(n.startswith("F4_") for n in names)
    print(f"T2 headline discovery: PASS  found {sorted(names)}")
    return {"relations": sorted(names)}


def t3_d_identifiable():
    obs = make_factorization_data()
    info = d_identifiable(obs)
    assert info["d_identifiable"] == 1, info
    result = run_discovery(obs)
    assert result["d_identifiable"] == 1
    print(f"T3 d_identifiable: PASS  n={info['n_quantities']}, "
          f"rank={info['constraint_rank']}, d={info['d_identifiable']} "
          f"(single coupling)")
    return info


def t4_held_out_residue():
    obs = make_factorization_data()
    predicted = obs["A_22"] ** 2
    assert predicted == obs["R_24"]
    print(f"T4 held-out R_24: PASS  predicted {predicted} from A_22 "
          f"matches observed")
    return {"predicted_R_24": str(predicted), "status": "FORCED"}


def t5_channel_dependent_falsifier():
    bad = channel_dependent_counterexample()
    assert not factorization_holds(bad)
    broken = broken_residuals(bad)
    assert "F1" in broken, broken
    rels = discover_factorization(bad)
    names = {r["name"] for r in rels}
    assert "F1" not in names
    result = run_discovery(bad)
    assert result["status"] == "FAIL"
    print(f"T5 falsifier: PASS  channel-dependent couplings break {sorted(broken)}; "
          f"discovery status FAIL")
    return {"status": "REJECTED_AS_EXPECTED", "broken": sorted(broken)}


if __name__ == "__main__":
    r1 = t1_factorization_exact()
    r2 = t2_headline_discovery()
    r3 = t3_d_identifiable()
    r4 = t4_held_out_residue()
    r5 = t5_channel_dependent_falsifier()
    full = run_discovery()
    cert = {
        "certificate_version": "0.4",
        "certificate_class": "EXACT-RATIONAL (Fraction; Jacobian rank over Q); "
                             "same epistemic class as B1/B2/B3",
        "problem": "B5 / ?5: cluster decomposition as gauge Cmp column — "
                   "one coupling governs all factorization channels",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "headline": "R_24 = A_22^2 across channels; d_identifiable = 1; "
                    "channel-dependent couplings falsified",
        "m_layer_stipulations": [
            "Toy 2→2 / 2→4 channels with exact-Fraction amplitudes "
            "(not PDG cross sections)",
            "Factorization residue identified with product of 2→2 strengths "
            "(locality / cluster template)",
            "Scheme factor κ treated as known (not a physical source)",
        ],
        "d_identifiable": full["d_identifiable"],
        "free_sources": full["free_sources"],
        "forced_quantities": full["forced_quantities"],
        "relations": full["relations_discovered"],
        "rank_analysis": full["rank_analysis"],
        "composition_claim": full["composition_claim"],
        "results": {
            "T1_factorization": r1,
            "T2_headline_discovery": r2,
            "T3_d_identifiable": r3,
            "T4_held_out_residue": r4,
            "T5_falsifier": r5,
        },
    }
    out = os.path.join(os.path.dirname(__file__), "..", "certificates",
                       "b5_certificate.json")
    save_certificate(cert, out)
    print("\nCertificate written: certificates/b5_certificate.json")
    print("ALL B5 TESTS PASS")
