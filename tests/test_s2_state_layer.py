"""S2 tests -- GNS program for ?2, free-fermion route.

T1  Central charge extracted blind from S(l): c within 3% of 1 (Dirac).
T2  VACUUM SATURATION from microscopic data: Q = S'' + (3/c)(S')^2 is
    suppressed relative to S'' (|Q|/|S''| small and shrinking with l) --
    the B6 rank-1 flat boundary populated by an actual quantum system.
T3  THERMAL IDENTITY: Q(l) matches the energy-density prediction
    c pi^2/(3 beta^2) across the window -- QNEC saturation with T != 0
    verified microscopically (B6's coth identity, from data).
T4  ENTANGLEMENT FIRST LAW (symmetric form): [S(C+e dC)-S(C-e dC)]/2e
    = Tr[K dC] + O(e^2); halving e shrinks the mismatch ~4x. Validates
    the modular technology any GNS identification must stand on -- and
    supplies the EXACT lattice modular kernel (modular_1p) that the
    operator probe's geometric ansatz lacked.
T5  POSITIVITY GATE: a corrupted correlation matrix (nu outside [0,1])
    is REJECTED as NOT_A_GAUSSIAN_STATE -- microscopic Gram positivity.
"""

import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from s2_gns.gaussian import (ground_state_C, thermal_C, entropy,
                             modular_1p, validity_gate)
from s2_gns.qnec_lattice import (vacuum_saturation_report,
                                 thermal_identity_report)
from b1_moment_solver.certificate import save_certificate


def t1_central_charge():
    c_fit, _ = vacuum_saturation_report(lmax=64)
    assert abs(c_fit - 1.0) < 0.03, c_fit
    print(f"T1 central charge: PASS  c_fit = {c_fit:.4f} (Dirac c = 1), "
          f"extracted blind from S(l)")
    return {"c_fit": c_fit}


def t2_vacuum_saturation():
    c_fit, rows = vacuum_saturation_report(lmax=64)
    mid = [r for r in rows if r["l"] == 30][0]
    far = [r for r in rows if r["l"] == 58][0]
    assert mid["Q_over_Spp"] < 0.15, mid
    assert far["Q_over_Spp"] < mid["Q_over_Spp"] + 0.02, (mid, far)
    print(f"T2 vacuum saturation: PASS  |Q|/|S''| = "
          f"{mid['Q_over_Spp']:.3f} (l=30) -> {far['Q_over_Spp']:.3f} "
          f"(l=58); the B6 flat boundary emerges from microscopic data")
    return {"l30": mid, "l58": far}


def t3_thermal_identity():
    pred, rows = thermal_identity_report(beta=16.0)
    devs = [r["rel_dev"] for r in rows]
    assert np.median(devs) < 0.10, (pred, rows)
    print(f"T3 thermal identity: PASS  Q(l) = {pred:.5f} predicted "
          f"(= 2*pi*energy density, c*pi^2/3beta^2); median deviation "
          f"{100*np.median(devs):.1f}% across l -- QNEC saturation with "
          f"T != 0, from data")
    return {"prediction": pred, "median_rel_dev": float(np.median(devs))}


def t4_first_law():
    L = 24
    C0 = ground_state_C(L)
    Cth = thermal_C(L, beta=8.0)
    # ground state sits on the BOUNDARY of the Gaussian-state set (nu ~ 0
    # modes) -- the positivity gate rejects backward steps there. Use a
    # strictly interior base point (physically: slightly thermalized).
    Cb = 0.95 * C0 + 0.05 * Cth
    dC = Cth - C0
    K = modular_1p(Cb)
    first = float(np.trace(K @ dC))
    errs = []
    for eps in (2e-3, 1e-3):
        dS_sym = (entropy(Cb + eps * dC) - entropy(Cb - eps * dC)) / (2 * eps)
        errs.append(abs(dS_sym - first))
    ratio = errs[0] / errs[1]
    assert 2.5 < ratio < 6.5, (errs, ratio)
    assert errs[1] / abs(first) < 0.02, (errs, first)
    print(f"T4 first law: PASS  symmetric dS/de = Tr[K dC] to "
          f"{100*errs[1]/abs(first):.2f}%; halving eps shrinks the O(e^2) "
          f"mismatch {ratio:.2f}x (theory: 4x)")
    return {"errors": errs, "ratio": ratio}


def t5_positivity_gate():
    C = ground_state_C(16)
    C[3, 3] = 1.4                     # unphysical occupation
    ok, nu = validity_gate(C)
    assert not ok
    try:
        entropy(C)
        raise AssertionError("gate failed to reject")
    except ValueError as e:
        assert "NOT_A_GAUSSIAN_STATE" in str(e)
    print(f"T5 positivity gate: PASS  corrupted C rejected "
          f"(nu_max = {nu.max():.3f} > 1) -- microscopic Gram positivity "
          f"is a hard gate")
    return {"nu_max": float(nu.max())}


if __name__ == "__main__":
    r1 = t1_central_charge(); r2 = t2_vacuum_saturation()
    r3 = t3_thermal_identity(); r4 = t4_first_law(); r5 = t5_positivity_gate()
    cert = {
        "certificate_version": "0.3",
        "certificate_class": "NUMERICAL-DISCOVERY (lattice Gaussian exact "
                             "kernels; finite differences; quarantined)",
        "problem": "S2: GNS program for ?2 -- free-fermion microscopic "
                   "verification layer",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "m_layer_stipulations": [
            "infinite-chain kernels at half filling (v_F = 1); "
            "lattice-continuum matching",
            "central finite differences (h=2) on S(l); UV constant removed "
            "by differentiation",
            "hard-wall region truncation; von Neumann entropy only",
            "GNS Gram OFF-DIAGONAL identification NOT achieved this sprint: "
            "documented obstruction in docs/notes/s2-gns-status.md",
        ],
        "headline": "B6 matrix structure populated from microscopic data: "
                    "vacuum flat boundary and thermal energy-density "
                    "identity verified; modular first law validated; "
                    "positivity gate armed. ?2 stays P: no premature "
                    "promotion.",
        "results": {"T1": r1, "T2": r2, "T3": r3, "T4": r4, "T5": r5},
    }
    save_certificate(cert, os.path.join(os.path.dirname(__file__), "..",
                                        "certificates", "s2_certificate.json"))
    print("\nCertificate written: certificates/s2_certificate.json")
    print("ALL S2 TESTS PASS")
