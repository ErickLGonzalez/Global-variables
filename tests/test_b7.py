"""B7 tests — Onsager transport-matrix completion (R15 / Chen et al. seed).

T1  Ground-truth thermoelectric L is PD-certified and symmetric
    (Onsager-ready).
T2  PSD alone on a hidden off-diagonal → PERMITTED interval containing
    the truth (restraint stacking baseline).
T3  Add reciprocity → off-diagonal FORCED exactly to the partner entry.
T4  Negative control A: L with negative diagonal → NOT_PSD / σ < 0 witness.
T5  Negative control B: asymmetric L (no B field) → reciprocity REJECTED.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fractions import Fraction as F

from b1_moment_solver.certificate import save_certificate
from b7_onsager.complete import (
    audit_full,
    entropy_production,
    force_by_reciprocity,
    permitted_offdiag,
    psd_certify,
)
from b7_onsager.exact import fmt, q
from b7_onsager.pseudo_data import (
    clone,
    corrupt_asymmetry,
    corrupt_negative,
    hide,
    thermoelectric_L,
)


def t1_ground_truth():
    L = thermoelectric_L()
    a = audit_full(L)
    assert a["onsager_certified"] and a["psd_status"] == "PD_CERTIFIED", a
    assert a["symmetric"]
    print(f"T1 ground-truth Onsager L: PASS  PD pivots={a['schur_pivots']}; "
          f"symmetric; Onsager-certified")
    return a


def t2_psd_permitted():
    L = thermoelectric_L()
    truth = L[0][1]
    M = hide(L, [(0, 1)])
    # partner L[1][0] still known; under PSD alone we still search x with
    # partner fixed? For a true PERMITTED demo hide both off-diagonals.
    M[1][0] = None
    res = permitted_offdiag(M, (0, 1))
    assert res["status"] == "PERMITTED", res
    lo = F(res["certified_inner_interval"][0])
    hi_s = res["certified_inner_interval"][1]
    assert lo <= truth
    assert hi_s == "+infinity" or truth <= F(hi_s)
    print(f"T2 PSD alone: PASS  L[0][1] PERMITTED in "
          f"[{float(lo):.4f}, {hi_s}]; truth={truth} inside")
    return res


def t3_reciprocity_force():
    L = thermoelectric_L()
    truth = L[0][1]
    M = hide(L, [(0, 1)])   # partner L[1][0] known
    res = force_by_reciprocity(M, (0, 1))
    assert res and res["status"] == "FORCED" and res["_frac"] == truth, res
    # refill and audit
    L2 = clone(L)
    L2[0][1] = res["_frac"]
    a = audit_full(L2)
    assert a["onsager_certified"]
    print(f"T3 reciprocity forcing: PASS  L[0][1] FORCED to {res['value']} "
          f"(exact); refilled matrix Onsager-certified")
    return {k: v for k, v in res.items() if k != "_frac"}


def t4_negative_psd():
    bad = corrupt_negative(thermoelectric_L())
    st = psd_certify(bad)
    assert st["psd_status"] == "NOT_PSD_CERTIFIED", st
    X = [F(1), F(0)]
    sig = entropy_production(bad, X)
    assert sig < 0, sig
    print(f"T4 second-law violation: PASS  NOT_PSD; σ(X)={sig} < 0 "
          f"(witness pivots {st['schur_pivots']})")
    return {"status": "REJECTED_AS_EXPECTED", "sigma": str(sig),
            "witness_pivots": st["schur_pivots"]}


def t5_negative_reciprocity():
    bad = corrupt_asymmetry(thermoelectric_L())
    a = audit_full(bad)
    assert not a["symmetric"]
    assert not a["onsager_certified"]
    # Asymmetry alone is enough to reject reciprocity; PSD of the
    # symmetrized part is irrelevant — the gate is L = Lᵀ.
    print(f"T5 reciprocity violation: PASS  L01≠L10 rejected "
          f"(symmetric=False; onsager_certified=False; "
          f"psd_status={a['psd_status']})")
    return {"status": "REJECTED_AS_EXPECTED",
            "symmetric": False,
            "onsager_certified": False,
            "psd_status": a["psd_status"]}


if __name__ == "__main__":
    r1 = t1_ground_truth()
    r2 = t2_psd_permitted()
    r3 = t3_reciprocity_force()
    r4 = t4_negative_psd()
    r5 = t5_negative_reciprocity()
    cert = {
        "certificate_version": "0.3",
        "certificate_class": "EXACT-RATIONAL (same class as B1/B2); "
                             "effective-coefficient / transport type",
        "problem": "B7: Onsager transport-matrix completion — "
                   "L ⪰ 0 (second law) + L = Lᵀ (reciprocity)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "headline": "restraint stacking on effective coefficients: "
                    "PSD alone → PERMITTED; +reciprocity → FORCED; "
                    "second-law and reciprocity falsifiers rejected",
        "seed_paper": "R15 Chen et al., Nat. Comput. Sci. 4, 66-85 (2024)",
        "m_layer_stipulations": [
            "Near-equilibrium linear-response regime "
            "(Onsager domain of validity)",
            "No magnetic field / time-reversal odd fluxes "
            "(reciprocity is L_ij = L_ji, not L_ij(B)=L_ji(-B))",
            "Toy rational thermoelectric L (not empirical Seebeck/Peltier data)",
        ],
        "results": {
            "T1_ground_truth": r1,
            "T2_psd_permitted": r2,
            "T3_reciprocity_forced": r3,
            "T4_second_law_violation": r4,
            "T5_reciprocity_violation": r5,
        },
    }
    out = os.path.join(os.path.dirname(__file__), "..", "certificates",
                       "b7_certificate.json")
    save_certificate(cert, out)
    print("\nCertificate written: certificates/b7_certificate.json")
    print("ALL B7 TESTS PASS")
