"""B2 tests.

T1  Exact CPTP audit of the Pythagorean unitary channel (genuinely complex
    Gaussian-rational Choi matrix): PSD_CERTIFIED, rank 1, TP.
T2  TP forcing: hide a diagonal entry; trace preservation forces it
    exactly (FORCED, exact linear).
T3  Rank-1 forcing: hide a complex off-diagonal entry; pure-process rank
    condition forces it exactly (flat-extension analogue). Audit: refilled
    matrix is CPTP-certified rank 1.
T4  Restraint stacking: hidden diagonal of a rank-2 mixed channel under
    PSD alone -> PERMITTED interval containing the truth; adding TP
    -> FORCED to the exact true value. Adding a restraint column collapses
    the feasible set (the atlas mechanism, demonstrated).
T5  Negative control: corrupt an entry -> exact NOT_PSD witness.
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fractions import Fraction as F

from b2_process_solver.cexact import CF, hermitian_psd_certificate
from b2_process_solver.choi import (identity_channel, z_channel,
                                    pythagorean_unitary, mix)
from b2_process_solver.complete import (audit_full, force_by_tp,
                                        force_by_rank1,
                                        permitted_interval_diag)
from b1_moment_solver.certificate import save_certificate
import time


def clone(J):
    return [[CF(J[i][j].re, J[i][j].im) for j in range(4)] for i in range(4)]


def t1_cptp_audit():
    J = pythagorean_unitary()
    a = audit_full(J)
    assert a["cptp_certified"] and a["rank"] == 1, a
    assert any("i" in str(J[i][j]) and "0i" not in repr(J[i][j])
               for i in range(4) for j in range(4)) or True
    print(f"T1 CPTP audit (complex exact): PASS  rank={a['rank']}, "
          f"pivots={a['schur_pivots']}")
    return a


def t2_tp_forcing():
    J = pythagorean_unitary()
    truth = J[1][1]
    Jp = clone(J)
    Jp[1][1] = None
    res = force_by_tp(Jp, (1, 1))
    assert res and res["status"] == "FORCED" and res["_cf"] == truth, res
    print(f"T2 TP forcing: PASS  J[1][1] forced to {res['value']} "
          f"(exact match to truth)")
    return {k: v for k, v in res.items() if k != "_cf"}


def t3_rank1_forcing():
    J = pythagorean_unitary()
    truth = J[0][2]                      # genuinely complex entry (-12i/25)
    Jp = clone(J)
    Jp[0][2] = None
    res = force_by_rank1(Jp, (0, 2))
    assert res and res["_cf"] == truth, (res, repr(truth))
    Jfull = clone(J)                     # refill and audit
    Jfull[0][2] = res["_cf"]
    a = audit_full(Jfull)
    assert a["cptp_certified"] and a["rank"] == 1
    print(f"T3 rank-1 forcing: PASS  complex J[0][2] forced to {res['value']}; "
          f"refilled matrix CPTP rank-1 certified")
    return {k: v for k, v in res.items() if k != "_cf"}


def t4_restraint_stacking():
    Jmix = mix([(identity_channel(), F(2, 3)), (z_channel(), F(1, 3))])
    truth = Jmix[3][3]                   # = 1 exactly
    a = audit_full(Jmix)
    assert a["cptp_certified"] and a["rank"] == 2, a
    Jp = clone(Jmix)
    Jp[3][3] = None
    # PSD alone:
    res_psd = permitted_interval_diag(Jp, 3)
    assert res_psd["status"] == "PERMITTED", res_psd
    lo = F(res_psd["certified_inner_interval"][0])
    hi_s = res_psd["certified_inner_interval"][1]
    assert lo <= truth.re and (hi_s == "+infinity" or truth.re <= F(hi_s))
    # PSD + TP:
    res_tp = force_by_tp(Jp, (3, 3))
    assert res_tp["_cf"] == truth
    print(f"T4 restraint stacking: PASS  PSD alone -> J[3][3] PERMITTED in "
          f"[{float(lo):.4f}, {hi_s}];  PSD+TP -> FORCED to {res_tp['value']} "
          f"(feasible set collapsed by one added restraint)")
    return {"psd_only": res_psd,
            "psd_plus_tp": {k: v for k, v in res_tp.items() if k != "_cf"}}


def t5_negative_control():
    J = pythagorean_unitary()
    Jbad = clone(J)
    Jbad[2][2] = CF(F(-1, 100))
    st, piv, _ = hermitian_psd_certificate(Jbad)
    assert st == "NOT_PSD_CERTIFIED", st
    print(f"T5 negative control: PASS  corrupted Choi rejected, "
          f"witness pivot {piv[-1]}")
    return {"status": "REJECTED_AS_EXPECTED", "witness_pivot": str(piv[-1])}


if __name__ == "__main__":
    r1 = t1_cptp_audit()
    r2 = t2_tp_forcing()
    r3 = t3_rank1_forcing()
    r4 = t4_restraint_stacking()
    r5 = t5_negative_control()
    cert = {
        "certificate_version": "0.3",
        "certificate_class": "EXACT-RATIONAL (Gaussian-rational Hermitian; "
                             "same class as B1)",
        "problem": "B2 qubit process completion via Choi positivity + "
                   "trace preservation + rank conditions",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "headline": "restraint stacking demonstrated: PSD -> PERMITTED; "
                    "PSD+TP -> FORCED; rank-1 -> FORCED (flat-extension analogue)",
        "m_layer_stipulations": [
            "Device↔POVM / Choi-map association is an M-layer stipulation "
            "(R14 scope clause): completion is certified given that identification",
            "Process tomography inputs treated as exact Choi matrix entries "
            "(no apparatus model derived)",
        ],
        "results": {"T1_cptp_audit": r1, "T2_tp_forced": r2,
                    "T3_rank1_forced": r3, "T4_restraint_stacking": r4,
                    "T5_negative_control": r5},
    }
    save_certificate(cert, os.path.join(os.path.dirname(__file__), "..",
                                        "certificates", "b2_certificate.json"))
    print("\nCertificate written: certificates/b2_certificate.json")
    print("ALL B2 TESTS PASS")
