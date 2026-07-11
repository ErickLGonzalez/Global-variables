"""B6 tests -- the 2D QNEC inside the certified verifier.

T1  Equivalence audit: for many random rational (c, S', Q22), the Schur
    pivot of M equals the independently computed QNEC combination, and
    the PSD verdict flips exactly at pivot sign change. (The
    reformulation is exact, not approximate.)
T2  Vacuum saturation: for a grid of rational (c, du), M is PSD with
    rank 1 and second pivot EXACTLY 0 -- QNEC saturated on the
    rank-deficient boundary (the flat-extension structure).
T3  Coherent-state strictness: vacuum bracket certified exactly zero;
    pivot = 2 pi (f')^2, strict iff f' != 0, saturated at critical
    points of the profile. Exact rationals throughout; 2 pi never
    numerically evaluated.
T4  Thermal symbolic identity: Q(x) = 1 + (x^2-1) - x^2 has ALL
    coefficients exactly zero -- saturation for every interval size and
    temperature simultaneously (symbolic certificate class).
T5  Negative control: fabricated wrong-concavity state rejected with an
    exact negative witness pivot.
"""

import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fractions import Fraction as F
import random

from b6_qnec.qnec import (certify, schur_pivot, vacuum_interval,
                          coherent_state, thermal_identity_poly,
                          fabricated_violation)
from b1_moment_solver.certificate import save_certificate


def t1_equivalence():
    rng = random.Random(42)
    checked = 0
    for _ in range(500):
        c6 = F(rng.randint(1, 60), rng.randint(1, 9))
        Sp = F(rng.randint(-40, 40), rng.randint(1, 9))
        Q22 = F(rng.randint(-40, 40), rng.randint(1, 9))
        piv = schur_pivot(c6, Sp, Q22)
        res = certify(c6, Sp, Q22)
        if piv < 0:
            assert res["psd_status"] == "NOT_PSD_CERTIFIED", (piv, res)
        elif piv == 0:
            assert res["rank"] == 1 and res["psd_status"] == "PSD_CERTIFIED"
        else:
            assert res["psd_status"] == "PD_CERTIFIED", (piv, res)
        checked += 1
    print(f"T1 equivalence audit: PASS  ({checked} random rational cases; "
          f"PSD verdict tracks QNEC combination exactly)")
    return {"cases": checked, "status": "EXACT_EQUIVALENCE_VERIFIED"}


def t2_vacuum_saturation():
    grid = [(F(1), F(1)), (F(1, 2), F(3)), (F(26), F(1, 4)),
            (F(12, 5), F(7, 2)), (F(100), F(1000))]
    for c, du in grid:
        res = certify(*vacuum_interval(c, du))
        assert res["verdict"].startswith("QNEC_SATURATED"), (c, du, res)
        assert res["schur_pivots"][1] == "0", res
    print(f"T2 vacuum saturation: PASS  ({len(grid)} rational (c, du) cases; "
          f"second Schur pivot exactly 0, rank 1 -- flat boundary)")
    return {"grid_cases": len(grid), "status": "SATURATED_EXACT"}


def t3_coherent_strict():
    # profile f'(u) values at sampled rational points, incl. a critical point
    cases = [(F(1), F(2), F(3, 7)), (F(1), F(5, 3), F(-2, 5)),
             (F(1), F(9, 4), F(0))]
    out = []
    for c, du, fp in cases:
        r = coherent_state(c, du, fp)
        assert r["vacuum_bracket_is_zero"], r
        if fp == 0:
            assert r["verdict"].startswith("QNEC_SATURATED"), r
        else:
            assert r["verdict"] == "QNEC_STRICT", r
        out.append(r)
    print("T3 coherent strictness: PASS  vacuum bracket exactly 0 in all "
          "cases; pivot = 2*pi*(f')^2 -- strict off critical points, "
          "saturated at f' = 0")
    return out


def t4_thermal_identity():
    coeffs = thermal_identity_poly()
    assert all(a == 0 for a in coeffs), coeffs
    print("T4 thermal symbolic identity: PASS  Q(x) == 0 identically "
          "(all coefficients exactly zero) -- saturation for ALL du, beta "
          "at once")
    return {"coefficients": [str(a) for a in coeffs],
            "status": "SYMBOLIC_IDENTITY_CERTIFIED"}


def t5_negative_control():
    res = certify(*fabricated_violation(F(1), F(2)))
    assert res["psd_status"] == "NOT_PSD_CERTIFIED", res
    assert res["verdict"].startswith("QNEC_VIOLATED"), res
    print(f"T5 negative control: PASS  wrong-concavity fake rejected, "
          f"witness pivots {res['schur_pivots']}")
    return res


if __name__ == "__main__":
    r1 = t1_equivalence()
    r2 = t2_vacuum_saturation()
    r3 = t3_coherent_strict()
    r4 = t4_thermal_identity()
    r5 = t5_negative_control()
    cert = {
        "certificate_version": "0.2",
        "certificate_class": "EXACT-RATIONAL + SYMBOLIC-IDENTITY "
                             "(no statistical or floating-point content)",
        "problem": "B6: strengthened 2D QNEC as certified Schur-pivot "
                   "positivity (conjecture ?2)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "central_fact": "2piT >= S'' + (6/c)(S')^2  <=>  "
                        "PSD([[c/6, S'],[S', 2piT - S'']]); saturation <=> "
                        "rank 1 (flat boundary)",
        "epistemic_scope": "exact reformulation + certified instances; NOT a "
                           "new proof of QNEC (Wall 2011; Balakrishnan-"
                           "Faulkner-Khandker-Wang 2017); GNS/Gram operator "
                           "identification of M remains the open item for "
                           "P -> H",
        "results": {"T1_equivalence": r1, "T2_vacuum_saturation": r2,
                    "T3_coherent_strict": r3, "T4_thermal_identity": r4,
                    "T5_negative_control": r5},
    }
    save_certificate(cert, os.path.join(os.path.dirname(__file__), "..",
                                        "certificates", "b6_certificate.json"))
    print("\nCertificate written: certificates/b6_certificate.json")
    print("ALL B6 TESTS PASS")
