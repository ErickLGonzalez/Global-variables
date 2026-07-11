"""B9 tests -- the Nobel decompilation recipe as executable gates.

T1  RECOVERY: from equilibrium trajectories + spectroscopy-route H_V, the
    pipeline recovers M (conductance block) and canonical W to few %;
    M certified PSD; FDT consistent.
T2  HIDDEN BATH: extra noise injected on the flux channel (violating FDT
    at the nominal T) -> EQUILIBRIUM_REJECTED. The Voss-Webb-era
    ambiguity, caught by the gate.
T3  GIBBS CIRCULARITY: the same corrupted data pass the FDT audit when
    H_V is inferred from the trajectories themselves (Gibbs route) -- the
    audit is provably blind there. Pass condition: the circularity IS
    detected as a route property, and Gibbs-route consistency is flagged
    non-promotable. This is the identifiability lesson of the whole
    Nobel sequence, in one test.
T4  MODEL ORDER: the overdamped 1D reduction returns mobility 1/G where
    the 2D representation's M entry is G -- coordinate/model-order choice
    inverts the dissipative number. Demonstrated and stipulated.
T5  EFFECTIVE-TEMPERATURE PROHIBITION: sigma inflated x3 (mimicking
    'more escape') with unchanged claimed T -> spectroscopy-route FDT
    audit REJECTS (residual ~ 8/9). The historically fatal shortcut is a
    certified gate failure, not a modeling option.
T6  QUANTUM HELD-OUT: exact rational charge-basis H; predicted E01 agrees
    with the independent transmon asymptotic to <2%, anharmonicity ~ -EC,
    truncation converged -- the 1985 parameter-free protocol miniature.
"""

import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from b9_circuit.model import ground_truth, simulate, simulate_overdamped_1d
from b9_circuit.estimate import decompile
from b9_circuit.quantum import heldout_spectroscopy
from b1_moment_solver.certificate import save_certificate

DT = 0.02


def t1_recovery():
    gt = ground_truth()
    Z = simulate(gt, seed=0)
    r = decompile(Z, DT, gt["T"], H_V=gt["H_V"])
    errM = np.linalg.norm(r["M_hat"] - gt["M"]) / np.linalg.norm(gt["M"])
    errW = np.linalg.norm(r["W_hat"] - gt["W"]) / np.linalg.norm(gt["W"])
    assert errM < 0.05 and errW < 0.05, (errM, errW)
    assert r["M_psd_ok"] and r["fdt_verdict"].startswith("EQUILIBRIUM_CONSISTENT")
    print(f"T1 recovery: PASS  |dM|={errM:.3f}, |dW|={errW:.3f}; "
          f"G_hat={r['M_hat'][1,1]:.3f} (truth 0.5); W canonical; "
          f"FDT residual {r['fdt_relative_residual']:.3f}")
    return {"errM": errM, "errW": errW,
            "fdt_residual": r["fdt_relative_residual"]}


def t2_hidden_bath():
    gt = ground_truth()
    extra = np.diag([0.4, 0.0])          # hidden bath on the flux channel
    Z = simulate(gt, seed=2, extra_D=extra)
    r = decompile(Z, DT, gt["T"], H_V=gt["H_V"])
    assert r["fdt_verdict"].startswith("EQUILIBRIUM_REJECTED"), r["fdt_verdict"]
    print(f"T2 hidden bath: PASS  FDT residual "
          f"{r['fdt_relative_residual']:.2f} -> {r['fdt_verdict'][:22]}...")
    return {"fdt_residual": r["fdt_relative_residual"]}


def t3_gibbs_circularity():
    gt = ground_truth()
    Z = simulate(gt, seed=3, extra_D=np.diag([0.4, 0.0]))
    r_spec = decompile(Z, DT, gt["T"], H_V=gt["H_V"])
    r_gibbs = decompile(Z, DT, gt["T"], H_V=None)
    assert r_spec["fdt_verdict"].startswith("EQUILIBRIUM_REJECTED")
    # the KNOWN blind spot: Gibbs route is more forgiving on the same data
    assert (r_gibbs["fdt_relative_residual"]
            < 0.6 * r_spec["fdt_relative_residual"]), \
        (r_gibbs["fdt_relative_residual"], r_spec["fdt_relative_residual"])
    assert "NOT promotable" in r_gibbs["calibration_route"]
    print(f"T3 Gibbs circularity: PASS  same corrupted data -- spectroscopy "
          f"residual {r_spec['fdt_relative_residual']:.2f} vs Gibbs "
          f"{r_gibbs['fdt_relative_residual']:.2f}; Gibbs route flagged "
          f"non-promotable (independent calibration is what breaks the "
          f"degeneracy)")
    return {"spec_residual": r_spec["fdt_relative_residual"],
            "gibbs_residual": r_gibbs["fdt_relative_residual"]}


def t4_model_order():
    k_phi, G = 3.0, 8.0
    X, a_true = simulate_overdamped_1d(k_phi=k_phi, G=G)
    # scalar drift fit
    x, y = X[:-1], X[1:]
    P = float(np.dot(x, y) / np.dot(x, x))
    a_hat = -np.log(P) / DT
    mobility = a_hat / k_phi              # = 1/G in the 1D representation
    assert abs(a_hat - a_true) / a_true < 0.05
    assert abs(mobility - 1.0 / G) / (1.0 / G) < 0.06
    assert abs(mobility - G) / G > 0.9    # NOT the 2D M entry
    print(f"T4 model order: PASS  1D mobility {mobility:.4f} = 1/G "
          f"(2D M entry is G = {G}); representation choice inverts the "
          f"dissipative number -- stipulation mandatory")
    return {"mobility_1d": mobility, "G_2d": G}


def t5_effective_temperature_prohibition():
    gt = ground_truth()
    Z = simulate(gt, seed=5, extra_D=8.0 * gt["D"])   # sigma^2 x9 total
    r = decompile(Z, DT, gt["T"], H_V=gt["H_V"])
    assert r["fdt_verdict"].startswith("EQUILIBRIUM_REJECTED"), r
    assert r["fdt_relative_residual"] > 0.5
    print(f"T5 effective-T prohibition: PASS  inflated noise at claimed T "
          f"rejected (residual {r['fdt_relative_residual']:.2f}); the "
          f"pre-1984 shortcut is a gate failure, not a fit option")
    return {"fdt_residual": r["fdt_relative_residual"]}


def t6_quantum_heldout():
    r = heldout_spectroscopy()
    assert r["E01_rel_dev_from_asymptotic"] < 0.02, r
    assert abs(r["anharmonicity"] - r["anharmonicity_prediction"]) \
        / abs(r["anharmonicity_prediction"]) < 0.35, r
    assert r["truncation_convergence"] < 1e-6, r
    print(f"T6 quantum held-out: PASS  E01={r['E01']:.4f} vs asymptotic "
          f"{r['E01_asymptotic_prediction']:.4f} "
          f"({100*r['E01_rel_dev_from_asymptotic']:.2f}%); anharmonicity "
          f"{r['anharmonicity']:.3f} ~ -EC={r['anharmonicity_prediction']}; "
          f"truncation {r['truncation_convergence']:.1e}")
    return r


if __name__ == "__main__":
    r1 = t1_recovery(); r2 = t2_hidden_bath(); r3 = t3_gibbs_circularity()
    r4 = t4_model_order(); r5 = t5_effective_temperature_prohibition()
    r6 = t6_quantum_heldout()
    cert = {
        "certificate_version": "0.3",
        "certificate_class": "NUMERICAL-DISCOVERY (OU estimation + FDT "
                             "audit) + EXACT-RATIONAL (charge-basis H)",
        "problem": "B9 circuit decompilation (2025 Nobel methodology as gates)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "m_layer_stipulations": [
            "linearized well (equilibrium-point estimator: K = -J_b H_V^{-1})",
            "calibration ROUTE recorded per run; Gibbs-route FDT consistency "
            "is never promotable evidence (T3 demonstrates its blind spot)",
            "state representation fixed to canonical flux-charge; 1D "
            "reductions invert the dissipative coefficient (T4)",
            "hard-wall truncation: quantum level positions only, no escape "
            "widths",
        ],
        "headline": "M, W, sigma recovered from trajectories with certified "
                    "PSD and FDT gates; hidden bath and effective-temperature "
                    "shortcuts REJECTED; independent calibration shown to be "
                    "the degeneracy-breaking ingredient (the Nobel lesson, "
                    "executable)",
        "results": {"T1": r1, "T2": r2, "T3": r3, "T4": r4, "T5": r5,
                    "T6": r6},
    }
    save_certificate(cert, os.path.join(os.path.dirname(__file__), "..",
                                        "certificates", "b9_certificate.json"))
    print("\nCertificate written: certificates/b9_certificate.json")
    print("ALL B9 TESTS PASS")
