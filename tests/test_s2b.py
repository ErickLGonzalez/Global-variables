"""S2-b tests -- exact-kernel GNS probe over the coherent (boosted) orbit.

T1  KERNEL ANATOMY (finding upgraded in-sprint): exact K matches
    -pi*beta(x) NEAR THE EDGES (<= 12%) but PLATEAUS in the bulk
    (NN element ~ 0.45x prediction) while the parabolic weight escapes
    into long-range hoppings (3rd-neighbor ~ +4; long-range Frobenius
    fraction ~ 0.24) -- the Eisler-Peschel structure, quantified: a
    strictly local ansatz is edge-correct and bulk-wrong. (Erratum
    carried: single-interval continuum K is local; CH bilocal belongs
    to multi-interval geometry.)
T2  ORBIT GATE: boosted states have Delta S = 0 to machine precision
    (diagonal-unitary spectrum invariance) -- the coherent orbit is real.
T3  DUAL-ROUTE S_rel: eigen-route and exact-kernel modular route agree
    to < 0.5%; S_rel scales quadratically in q (coherent signature,
    ratio ~ 4 for q doubling).
T4  LOCAL-ANSATZ FAILURE QUANTIFIED: on identical data, the local
    kernel's modular route misses S_rel by >= 10x the exact kernel's
    deviation -- the old probe's mismatch reproduced under controlled
    conditions and attributed.
T5  GRAM-DIAGONAL IDENTITY: capacity of entanglement tracks entropy
    (2D CFT capacity = entropy): d(C_E)/d(ln l) within 10% of dS/d(ln l)
    -- the first verified second-moment (Gram) entry for the fixed
    kernel: omega(K^2) - omega(K)^2 = the entropy slot.
T6  NEGATIVE CONTROL: a scrambled kernel of identical sparsity fails the
    dual-route agreement at O(1) -- the exact kernel's success is not
    generic.
"""

import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from s2_gns.s2b_probe import (kernel_anatomy, orbit_test,
                              capacity_vs_entropy, local_ansatz_kernel,
                              interval, boosted_C, gaussian_relative_entropy,
                              _entropy_c)
from s2_gns.gaussian import ground_state_C, modular_1p
from b1_moment_solver.certificate import save_certificate


def t1_anatomy():
    r = kernel_anatomy(l=48)
    assert r["edge_max_dev"] < 0.10, r
    assert r["bulk_NN_over_prediction"] < 0.6, r
    assert r["long_range_frobenius_fraction"] > 0.05, r
    print(f"T1 kernel anatomy: PASS  edge NN matches -pi*beta(x) to "
          f"{100*r['edge_max_dev']:.1f}%; bulk NN plateaus at "
          f"{r['bulk_NN_over_prediction']:.2f}x prediction; long-range "
          f"fraction {r['long_range_frobenius_fraction']:.3f} "
          f"(Eisler-Peschel structure: local at edges, weight escapes to "
          f"long range in the bulk)")
    return r


def t2_orbit_gate(orbit):
    for row in orbit:
        assert abs(row["dS"]) < 1e-9, row
    print(f"T2 orbit gate: PASS  Delta S = 0 to machine precision on the "
          f"boosted (coherent) orbit (max |dS| = "
          f"{max(abs(r['dS']) for r in orbit):.1e})")
    return {"max_abs_dS": max(abs(r["dS"]) for r in orbit)}


def t3_dual_route(orbit):
    for row in orbit:
        assert row["dev_exact"] < 0.005, row
    ratio = orbit[1]["S_rel"] / orbit[0]["S_rel"]
    assert 3.5 < ratio < 4.5, (ratio, orbit)
    print(f"T3 dual-route S_rel: PASS  exact-kernel route matches "
          f"eigen-route to {100*max(r['dev_exact'] for r in orbit):.2f}%; "
          f"quadratic q-scaling ratio = {ratio:.2f} (coherent signature)")
    return {"max_dev_exact": max(r["dev_exact"] for r in orbit),
            "q_scaling_ratio": ratio}


def t4_local_failure(orbit):
    for row in orbit:
        assert row["dev_local"] >= 10 * row["dev_exact"], row
    print(f"T4 local-ansatz failure: PASS  on identical data the local "
          f"kernel misses S_rel by {100*orbit[0]['dev_local']:.1f}% vs "
          f"{100*orbit[0]['dev_exact']:.2f}% for the exact kernel "
          f"(>= 10x) -- the old probe's mismatch, attributed")
    return {"dev_local": orbit[0]["dev_local"],
            "dev_exact": orbit[0]["dev_exact"]}


def t5_capacity_identity():
    rows, sCE, sS = capacity_vs_entropy()
    rel = abs(sCE - sS) / sS
    assert rel < 0.10, (sCE, sS, rows)
    print(f"T5 capacity = entropy: PASS  d(C_E)/dln(l) = {sCE:.4f} vs "
          f"dS/dln(l) = {sS:.4f} ({100*rel:.1f}%): first verified "
          f"second-moment Gram entry (omega(K^2)-omega(K)^2 = entropy slot)")
    return {"slope_capacity": sCE, "slope_entropy": sS, "rel_dev": rel}


def t6_negative():
    l, q = 32, 0.10
    Cfull = ground_state_C(l + 4)
    C_A = interval(Cfull, l).astype(complex)
    Cq_A = interval(boosted_C(Cfull, q), l)
    srel = gaussian_relative_entropy(Cq_A, C_A)
    K = modular_1p(np.real(C_A))
    rng = np.random.default_rng(0)
    P = rng.permutation(l)
    K_scr = K[np.ix_(P, P)]                 # same spectrum, wrong kernel
    dK = float(np.real(np.trace(K_scr @ (Cq_A - C_A))))
    dS = _entropy_c(Cq_A) - _entropy_c(C_A)
    dev = abs(dK - dS - srel) / srel
    assert dev > 0.5, dev
    print(f"T6 negative control: PASS  scrambled kernel (identical "
          f"spectrum!) fails dual-route agreement by {100*dev:.0f}% -- "
          f"the exact kernel's success is structural, not spectral")
    return {"dev_scrambled": dev}


if __name__ == "__main__":
    r1 = t1_anatomy()
    orbit = orbit_test()
    r2 = t2_orbit_gate(orbit); r3 = t3_dual_route(orbit)
    r4 = t4_local_failure(orbit); r5 = t5_capacity_identity()
    r6 = t6_negative()
    cert = {
        "certificate_version": "0.3",
        "certificate_class": "NUMERICAL-DISCOVERY (exact Gaussian kernels; "
                             "quarantined)",
        "problem": "S2-b: exact-kernel GNS probe on the coherent orbit "
                   "(?2 -> H program)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "erratum": "single-interval continuum modular Hamiltonian is LOCAL "
                   "(conformal Bisognano-Wichmann); Casini-Huerta bilocal "
                   "terms belong to multi-interval geometry; lattice "
                   "mismatch attributed to Eisler-Peschel long-range "
                   "corrections (T1 quantifies them)",
        "m_layer_stipulations": [
            "single interval, half filling, open-boundary restriction of "
            "infinite-chain kernels",
            "boosted orbit as the lattice coherent family (bosonization)",
            "fixed operator = exact VACUUM kernel; state-independence "
            "tested on the vacuum orbit only; thermal states out of scope "
            "this sprint",
        ],
        "headline": "fixed exact kernel passes the coherent-orbit GNS "
                    "first-moment test to <0.5% with quadratic scaling; "
                    "local ansatz fails >=10x worse on identical data "
                    "(mismatch attributed); capacity=entropy verified as "
                    "the first second-moment Gram entry. ?2 stays P; "
                    "edit-007 GNS checklist advances one box.",
        "results": {"T1": r1, "T2": r2, "T3": r3, "T4": r4, "T5": r5,
                    "T6": r6},
    }
    save_certificate(cert, os.path.join(os.path.dirname(__file__), "..",
                                        "certificates",
                                        "s2b_certificate.json"))
    print("\nCertificate written: certificates/s2b_certificate.json")
    print("ALL S2-B TESTS PASS")
