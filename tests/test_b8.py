"""B8 tests -- blind grammar identification.

T1  GRADIENT_FLOW data identified (real negative spectrum).
T2  GENERIC_MIXED data identified (complex spectrum, damping above floor).
T3  HAMILTONIAN data: spectral test alone must yield AMBIGUOUS (honest);
    the drift test then certifies HAMILTONIAN_WITHIN_BOUND -- conservation
    is only ever a certified BOUND on |Re lambda|, never exact zero.
T4  WEAK_DAMPING split: (a) eps = 3e-4 -- drift test DETECTS damping the
    spectral test could not resolve -> GENERIC_MIXED (second invariant
    resolves in the positive direction too); (b) eps = 1e-5 -- below drift
    detectability -> HAMILTONIAN_WITHIN_BOUND whose certified bound
    CONTAINS the true damping (a bound-claim is not falsified by damping
    inside it; no over-claim occurs).
T5  Quantum: UNITARY vs DISSIPATIVE identified EXACTLY via Choi rank
    (B2 machinery); fabricated non-PSD 'channel' -> NOT_A_CHANNEL.
T6  Cross-falsifiers: no grammar is ever assigned to data from a
    different grammar (misclassification audit over all cases).
"""

import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from b8_grammar.generators import trajectories, quantum_instance
from b8_grammar.identify import (classify_dynamics,
                                 classify_dynamics_conservative_check,
                                 classify_quantum)
from b1_moment_solver.certificate import save_certificate

DT = 0.01
FLOOR = 5e-3   # noise floor on Re(lambda) for obs_noise=1e-3 at this design


def t1_gradient():
    trajs, _ = trajectories("GRADIENT_FLOW", seed=1)
    r = classify_dynamics(trajs, DT, FLOOR)
    assert r["grammar"] == "GRADIENT_FLOW", r
    print(f"T1 gradient flow: PASS  spectrum {r['spectrum']}")
    return r


def t2_generic():
    trajs, _ = trajectories("GENERIC_MIXED", seed=2)
    r = classify_dynamics(trajs, DT, FLOOR)
    assert r["grammar"] == "GENERIC_MIXED", r
    print(f"T2 GENERIC mixed: PASS  spectrum {r['spectrum']} "
          f"(damping margin {r['damping_margin']:.1f}x floor)")
    return r


def t3_hamiltonian_two_invariant():
    trajs, _ = trajectories("HAMILTONIAN", seed=3)
    r1 = classify_dynamics(trajs, DT, FLOOR)
    assert r1["grammar"] == "AMBIGUOUS", r1   # spectral test alone: honest
    r2 = classify_dynamics_conservative_check(trajs, DT, FLOOR)
    assert r2["grammar"] == "HAMILTONIAN_WITHIN_BOUND", r2
    print(f"T3 Hamiltonian: PASS  spectral -> AMBIGUOUS (honest); drift test "
          f"-> HAMILTONIAN_WITHIN_BOUND, |Re lambda| <= "
          f"{r2['certified_damping_bound']:.2e}")
    return r2


def t4_weak_damping_stays_ambiguous():
    trajs, _ = trajectories("WEAK_DAMPING", seed=4, damping=3e-4)
    ra = classify_dynamics_conservative_check(trajs, DT, FLOOR)
    assert ra["grammar"] == "GENERIC_MIXED", ra
    trajs, _ = trajectories("WEAK_DAMPING", seed=5, damping=1e-5)
    rb = classify_dynamics_conservative_check(trajs, DT, FLOOR)
    assert rb["grammar"] == "HAMILTONIAN_WITHIN_BOUND", rb
    assert rb["certified_damping_bound"] >= 1e-5 * 1.0, rb  # true damping inside bound
    print(f"T4 weak damping: PASS  eps=3e-4 DETECTED by drift test -> "
          f"GENERIC_MIXED (Re lambda ~ {ra['implied_Re_lambda']:.1e}); "
          f"eps=1e-5 -> HAMILTONIAN_WITHIN_BOUND with bound "
          f"{rb['certified_damping_bound']:.1e} containing the truth")
    return {"detected": ra["grammar"], "bounded": rb["grammar"],
            "bound": rb["certified_damping_bound"]}


def t5_quantum_exact():
    ru = classify_quantum(quantum_instance("UNITARY"))
    rd = classify_quantum(quantum_instance("DISSIPATIVE"))
    rf = classify_quantum(quantum_instance("FAKE"))
    assert ru["grammar"] == "UNITARY_GRAMMAR", ru
    assert rd["grammar"] == "DISSIPATIVE_CPTP", rd
    assert rf["grammar"] == "NOT_A_CHANNEL", rf
    print("T5 quantum grammars: PASS  unitary (Choi rank 1) vs dissipative "
          "(rank 2) identified EXACTLY; fake rejected")
    return {"unitary": ru["grammar"], "dissipative": rd["grammar"],
            "fake": rf["grammar"]}


def t6_cross_falsifiers():
    cases = {"GRADIENT_FLOW": "GRADIENT_FLOW",
             "GENERIC_MIXED": "GENERIC_MIXED",
             "HAMILTONIAN": "HAMILTONIAN"}
    for true_g in cases:
        trajs, _ = trajectories(true_g, seed=11)
        r = classify_dynamics_conservative_check(trajs, DT, FLOOR)
        got = r["grammar"]
        ok = {"GRADIENT_FLOW": {"GRADIENT_FLOW", "AMBIGUOUS"},
              "GENERIC_MIXED": {"GENERIC_MIXED", "AMBIGUOUS"},
              "HAMILTONIAN": {"HAMILTONIAN_WITHIN_BOUND", "AMBIGUOUS"}}
        assert got in ok[true_g], (true_g, r)
    print("T6 cross-falsifiers: PASS  no grammar ever assigned to data "
          "from a different grammar")
    return {"misclassifications": 0}


if __name__ == "__main__":
    r1 = t1_gradient(); r2 = t2_generic(); r3 = t3_hamiltonian_two_invariant()
    r4 = t4_weak_damping_stays_ambiguous(); r5 = t5_quantum_exact()
    r6 = t6_cross_falsifiers()
    cert = {
        "certificate_version": "0.3",
        "certificate_class": "NUMERICAL-DISCOVERY (dynamical grammars) + "
                             "EXACT-RATIONAL (quantum grammars via B2)",
        "problem": "B8 blind grammar identification",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "m_layer_stipulations": [
            "linear dynamics with quadratic potentials (grammar signatures exact only there)",
            "observation noise 1e-3; generator estimated via one-step propagator + matrix log (forward-difference estimation REJECTED: injects artificial damping ~dt*omega^2/2, a discretization artifact masquerading as dissipation)",
            "noise floor on Re(lambda) set to 5e-3 for this design",
            "classification uses only similarity-invariant data (spectra, conserved forms) per R15 canonicalization rule",
        ],
        "headline": "grammars identified blind via invariants only; AMBIGUOUS "
                    "enforced where data cannot separate candidates; quantum "
                    "grammar split is exact (Choi rank)",
        "results": {"T1": r1, "T2": r2, "T3": r3, "T4": r4, "T5": r5, "T6": r6},
    }
    save_certificate(cert, os.path.join(os.path.dirname(__file__), "..",
                                        "certificates", "b8_certificate.json"))
    print("\nCertificate written: certificates/b8_certificate.json")
    print("ALL B8 TESTS PASS")
