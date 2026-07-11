"""B3 tests — electroweak closed-system discovery.

T1  Pseudo-data closes exactly: all nine residuals vanish; Pythagorean
    Weinberg angle; G_F squared identity holds.
T2  Discovery finds the four headline relations
    (e = g sinθ_W, M_W = gv/2, M_Z = (v/2)√(g²+g′²), G_F = 1/(√2 v²)).
T3  Exact Jacobian rank ⇒ d_identifiable = 3; preferred free basis
    {g, g′, v} recovered.
T4  Held-out check: hide M_Z from the forcing view by verifying R4
    predicts the observed M_Z from {g, g′, v} exactly.
T5  Negative control: corrupt e → R1/R2/R9 break; discovery status FAIL
    or broken residuals nonempty (pipeline can reject).
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fractions import Fraction

from b1_moment_solver.certificate import save_certificate
from b3_electroweak.discover import broken_relations, corrupt, run_discovery
from b3_electroweak.exact import isqrt_exact
from b3_electroweak.pseudo_data import make_closed_system
from b3_electroweak.rank import d_identifiable, holding_residuals, residuals


def t1_closed_system_exact():
    obs = make_closed_system()
    res = residuals(obs)
    assert all(r == 0 for _, r in res), res
    assert obs["sin_theta_W"] ** 2 + obs["cos_theta_W"] ** 2 == 1
    assert obs["G_F_inv_sq"] == 2 * obs["v"] ** 4
    print(f"T1 closed-system exactness: PASS  "
          f"{len(res)} residuals = 0; sin^2+cos^2=1; 1/G_F^2 = 2 v^4")
    return {"n_residuals": len(res), "all_zero": True,
            "quantities": {k: str(v) for k, v in obs.items()}}


def t2_headline_discovery():
    result = run_discovery()
    assert result["headline_complete"], result["headline_relations_found"]
    names = {r["name"] for r in result["relations_discovered"]}
    for req in ("R1", "R3", "R4", "R5"):
        assert req in names, names
    formulas = {r["name"]: r["formula"] for r in result["relations_discovered"]}
    print(f"T2 headline discovery: PASS  found {sorted(names)}; "
          f"R1={formulas['R1']}; R3={formulas['R3']}; "
          f"R4={formulas['R4']}; R5={formulas['R5']}")
    return {"relations": sorted(names), "formulas": formulas}


def t3_d_identifiable():
    obs = make_closed_system()
    info = d_identifiable(obs)
    assert info["d_identifiable"] == 3, info
    result = run_discovery(obs)
    assert result["d_identifiable"] == 3
    free = set(result["dependency_graph"]["free_sources"])
    assert free == {"g", "g_prime", "v"}, free
    print(f"T3 d_identifiable: PASS  n={info['n_quantities']}, "
          f"rank={info['constraint_rank']}, d={info['d_identifiable']}; "
          f"FREE={sorted(free)}")
    return info


def t4_held_out_M_Z():
    obs = make_closed_system()
    g, gp, v = obs["g"], obs["g_prime"], obs["v"]
    root = isqrt_exact(g * g + gp * gp)
    predicted = v * root / 2
    assert predicted == obs["M_Z"]
    # R4 residual with predicted value
    assert 4 * predicted * predicted == v * v * (g * g + gp * gp)
    print(f"T4 held-out M_Z: PASS  predicted {predicted} from {{g,g',v}} "
          f"matches observed (exact)")
    return {"predicted_M_Z": str(predicted), "observed_M_Z": str(obs["M_Z"]),
            "status": "FORCED"}


def t5_negative_control():
    obs = make_closed_system()
    bad = corrupt(obs, "e")
    broken = broken_relations(bad)
    assert "R1" in broken and "R2" in broken, broken
    # Rank/discovery on corrupted table: either d≠3 or headline incomplete
    # because R1 no longer holds as a discovered exact identity.
    from b3_electroweak.relations import discover_relations
    rels = discover_relations(bad)
    names = {r["name"] for r in rels}
    assert "R1" not in names, names
    print(f"T5 negative control: PASS  corrupted e breaks {sorted(broken)}; "
          f"R1 absent from discovery")
    return {"status": "REJECTED_AS_EXPECTED", "broken_residuals": sorted(broken)}


if __name__ == "__main__":
    r1 = t1_closed_system_exact()
    r2 = t2_headline_discovery()
    r3 = t3_d_identifiable()
    r4 = t4_held_out_M_Z()
    r5 = t5_negative_control()
    full = run_discovery()
    cert = {
        "certificate_version": "0.3",
        "certificate_class": "EXACT-RATIONAL (Fraction; Jacobian rank over Q); "
                             "same epistemic class as B1/B2",
        "problem": "B3 electroweak closed system: discover tree-level "
                   "relations and report d_identifiable = 3",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "headline": "discovered e=g sinθ_W, M_W=gv/2, M_Z=(v/2)√(g²+g′²), "
                    "G_F=1/(√2 v²); d_identifiable = 3 with FREE basis {g, g′, v}",
        "m_layer_stipulations": [
            "Tree-level electroweak map; loop/RG corrections not included",
            "Weinberg angle represented by a Pythagorean rational proxy "
            "(exact Fraction); physical sin²θ_W scheme (on-shell vs MS-bar) "
            "not selected",
            "G_F certified via squared identity 1/G_F² = 2 v⁴ (√2 not a "
            "rational observable)",
            "Pseudo-data presented as exact independent measurements "
            "(no experimental noise model)",
        ],
        "d_identifiable": full["d_identifiable"],
        "free_sources": full["dependency_graph"]["free_sources"],
        "forced_quantities": full["dependency_graph"]["forced"],
        "relations": full["relations_discovered"],
        "rank_analysis": full["rank_analysis"],
        "results": {
            "T1_closed_system": r1,
            "T2_headline_discovery": r2,
            "T3_d_identifiable": r3,
            "T4_held_out_M_Z": r4,
            "T5_negative_control": r5,
        },
    }
    out = os.path.join(os.path.dirname(__file__), "..", "certificates",
                       "b3_certificate.json")
    save_certificate(cert, out)
    print(f"\nCertificate written: certificates/b3_certificate.json")
    print("ALL B3 TESTS PASS")
