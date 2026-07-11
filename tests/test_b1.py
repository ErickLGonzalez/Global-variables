"""B1 benchmark tests.

T1  FORCED:    hide the tail moments of a known 3-atom measure; the flat
               extension must recover them exactly and certify positivity.
T2  PERMITTED: hide the top moment at non-flat order; positivity must
               yield a certified interval (not a point).
T3  REJECTED:  corrupt one moment; the exact PSD gate must reject with a
               negative-pivot witness (gate #6 of the decoding chain).
T4  ATOMS:     extracted support/weights must reproduce all moments to
               < 1e-30 (audited numerical layer).
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fractions import Fraction as F

from b1_moment_solver.exact import hankel, psd_certificate
from b1_moment_solver.recover import recover_hidden_tail, permitted_interval, extract_atoms
from b1_moment_solver.certificate import make_certificate, save_certificate

# Ground-truth measure: atoms x = -1/2, 1/4, 2 with weights 1/3, 1/6, 1/2.
ATOMS = [(F(-1, 2), F(1, 3)), (F(1, 4), F(1, 6)), (F(2), F(1, 2))]


def moments(n):
    return [sum(w * x ** k for x, w in ATOMS) for k in range(n + 1)]


def t1_forced():
    known = moments(6)                      # m_0..m_6 known (M_3 is flat, rank 3)
    truth = moments(12)
    res = recover_hidden_tail(known, upto=12)
    assert res["status"] == "FORCED", res
    for i in range(7, 13):
        assert F(res["recovered"][str(i)]) == truth[i], f"m_{i} mismatch"
    print("T1 FORCED tail recovery: PASS  (m_7..m_12 recovered exactly, rank",
          res["rank"], ")")
    return res


def t2_permitted():
    ms = moments(4)                          # m_0..m_4 -> M_2, rank 3 = full: not flat
    ms = ms + [None]                         # hide m_5? need pairs; hide top of M_2 pattern
    # Hide m_4 itself: M_2 depends on m_0..m_4 with m_4 unknown.
    hole = 4
    data = moments(4)
    data[hole] = None
    res = permitted_interval(data, hole=hole, t=2)
    assert res["status"] == "PERMITTED", res
    lo = F(res["certified_inner_interval"][0])
    hi_s = res["certified_inner_interval"][1]
    true_m4 = moments(4)[4]
    assert lo <= true_m4 and (hi_s == "+infinity" or true_m4 <= F(hi_s))
    print(f"T2 PERMITTED interval: PASS  m_4 in [{float(lo):.6f}, {hi_s}] "
          f"(true {float(true_m4):.6f}) -- lower bound certified, top moment unbounded above (correct)")
    return res


def t3_rejected():
    bad = moments(6)
    bad[4] -= F(2)                           # corrupt m_4 downward -> indefinite
    st, piv, rk = psd_certificate(hankel(bad, 3))
    assert st == "NOT_PSD_CERTIFIED", st
    print("T3 REJECTED negative control: PASS  (witness pivot",
          str(piv[-1]), ", exact)")
    return {"status": "REJECTED_AS_EXPECTED", "witness_pivot": str(piv[-1])}


def t4_atoms(forced_result):
    res = extract_atoms(forced_result["full_moments"], forced_result["rank"])
    resid = float(res["max_moment_residual"])
    assert resid < 1e-30, res
    print(f"T4 ATOM extraction: PASS  residual {resid:.1e}; atoms:")
    for a in res["atoms"]:
        print(f"     x = {a['x'][:12]:>12}   w = {a['weight'][:12]}")
    return res


if __name__ == "__main__":
    r1 = t1_forced()
    r2 = t2_permitted()
    r3 = t3_rejected()
    r4 = t4_atoms(r1)
    r1.pop("full_moments")
    cert = make_certificate(
        "B1 truncated Hankel moment problem (3-atom ground truth)",
        {"known_moments": "m_0..m_6", "hidden": "m_7..m_12 (T1), m_4 (T2)"},
        {"T1_forced_tail": r1, "T2_permitted_hole": r2,
         "T3_negative_control": r3, "T4_atom_audit": r4},
        m_layer_stipulations=[
            "Reported m_0..m_k are moments of a positive Borel measure "
            "(calibration/normalization audit not re-derived here)",
            "Exact-arithmetic claims cover positivity/rank/forcing; atom "
            "extraction numerics are quarantined with audited residual",
        ],
    )
    save_certificate(cert, os.path.join(os.path.dirname(__file__), "..",
                                        "certificates", "b1_certificate.json"))
    print("\nCertificate written: certificates/b1_certificate.json")
    print("ALL B1 TESTS PASS")
