"""S3 tests -- one alpha_s across channels and a 51x scale span (REAL data).

T1  RG ENGINE VALIDATION: world-average 0.1180 at M_Z evolved DOWN to
    m_tau lands in the tau-extraction band 0.312 +/- 0.015 -- 2-loop
    running + threshold matching reproduce the known 51x-span connection.
T2  SINGLE COUPLING FORCED: all four independent extractions, evolved to
    M_Z, are mutually consistent (chi^2/dof < 2); combined value within
    1.5 sigma of the (non-input) world average. d_identifiable = 1 across
    four measurement classes -- B5's factorization verdict on real data.
T3  NO-RUNNING NULL REJECTED: a scale-independent coupling is excluded
    at > 10 sigma by the same data -- asymptotic freedom (the alpha_s
    row's RG = H entry) certified from data by our own pipeline.
T4  SCORE COMPARISON: model A (one running coupling, d = 1) beats model
    B (channel-dependent couplings, d = 4) under chi^2 + 2*d -- the
    Discipline Formula's d_identifiable penalty deciding on real data.
T5  THRESHOLD STIPULATION PROBE: deliberately skipping the m_b flavor
    matching shifts the evolved tau point by >> its error -- scheme/
    threshold metadata (decoding-chain step 1) demonstrably matters.
"""

import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from s3_pdg.running import (DATA, WORLD_AVG, MTAU, MZ, evolve,
                            evolved_to_MZ, combine)
from b1_moment_solver.certificate import save_certificate


def t1_engine():
    down = evolve(WORLD_AVG[0], MZ, MTAU)
    tau = DATA[0]
    pull = abs(down - tau["alpha"]) / tau["err"]
    assert pull < 1.5, (down, pull)
    print(f"T1 RG engine: PASS  0.1180 @ M_Z -> {down:.4f} @ m_tau "
          f"(tau band 0.312 +/- 0.015; pull {pull:.2f} sigma) -- the 51x "
          f"span closes")
    return {"alpha_at_mtau": down, "pull_sigma": pull}


def t2_forced():
    vals = [evolved_to_MZ(e) for e in DATA]
    mean, err, chi2, dof = combine(vals)
    assert chi2 / dof < 2.0, (chi2, dof)
    pull_wa = abs(mean - WORLD_AVG[0]) / np.hypot(err, WORLD_AVG[1])
    assert pull_wa < 1.5, (mean, err, pull_wa)
    print(f"T2 single coupling FORCED: PASS  4 channels -> alpha_s(M_Z) = "
          f"{mean:.4f} +/- {err:.4f}, chi2/dof = {chi2/dof:.2f}; vs world "
          f"avg pull {pull_wa:.2f} sigma. d_identifiable = 1 on real data")
    return {"alpha_MZ": mean, "err": err, "chi2_dof": chi2 / dof,
            "per_channel": {d["name"]: {"central": v[0], "err": v[1]}
                            for d, v in zip(DATA, vals)}}


def t3_null_rejected():
    # constant-coupling hypothesis: fit one number to raw values at
    # native scales
    v = np.array([d["alpha"] for d in DATA])
    e = np.array([d["err"] for d in DATA])
    w = 1 / e ** 2
    mean = np.sum(w * v) / np.sum(w)
    chi2 = float(np.sum(w * (v - mean) ** 2))
    sig = np.sqrt(chi2)  # gross significance of the rejection
    assert sig > 10, (chi2, sig)
    print(f"T3 no-running null: REJECTED at ~{sig:.0f} sigma "
          f"(chi2 = {chi2:.0f} for 3 dof) -- asymptotic freedom certified "
          f"from data by this pipeline")
    return {"chi2": chi2, "significance_sigma": sig}


def t4_score():
    vals = [evolved_to_MZ(e) for e in DATA]
    _, _, chi2_A, _ = combine(vals)
    score_A = chi2_A + 2 * 1          # one running coupling
    score_B = 0.0 + 2 * 4             # channel-dependent (fits exactly)
    assert score_A < score_B, (score_A, score_B)
    print(f"T4 Score comparison: PASS  A (d=1): {score_A:.2f} < "
          f"B (d=4): {score_B:.2f} -- the d_identifiable penalty decides "
          f"on real data (B5's verdict, empirically)")
    return {"score_single": score_A, "score_channel_dependent": score_B}


def t5_threshold_probe():
    tau = DATA[0]
    with_m, err_m = evolved_to_MZ(tau, match_threshold=True)
    without, _ = evolved_to_MZ(tau, match_threshold=False)
    shift = abs(with_m - without)
    assert shift > 2 * err_m, (shift, err_m)
    print(f"T5 threshold probe: PASS  skipping m_b matching shifts the "
          f"evolved tau point by {shift:.4f} (= {shift/err_m:.1f}x its "
          f"error) -- threshold/scheme metadata demonstrably matters")
    return {"shift": shift, "shift_over_error": shift / err_m}


if __name__ == "__main__":
    r1 = t1_engine(); r2 = t2_forced(); r3 = t3_null_rejected()
    r4 = t4_score(); r5 = t5_threshold_probe()
    cert = {
        "certificate_version": "0.3",
        "certificate_class": "EMPIRICAL-STATISTICAL (real PDG-lineage "
                             "extractions + 2-loop RG; REAL-mode analogue "
                             "of B4 for the coupling sector)",
        "problem": "S3: one alpha_s across channels and scales (B5 "
                   "empirical layer)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "calibration_route": "independent measurement classes (tau, EW fit, "
                             "lattice, ttbar); world average used only as a "
                             "non-input cross-check (no Gibbs-style "
                             "circularity)",
        "m_layer_stipulations": [
            "input values verified 2026-07-14 against PDG-lineage sources; "
            "re-verify before promotion decisions",
            "2-loop MS-bar running; m_b = 4.18 threshold by continuity; "
            "truncation error << data errors (T1 closes the span)",
            "error propagation by evolving the +/-1 sigma ends",
        ],
        "headline": "d_identifiable = 1 across four real measurement "
                    "classes spanning 51x in scale; no-running null "
                    "rejected at >10 sigma; B5's factorization verdict and "
                    "the alpha_s RG=H entry both certified on real data",
        "results": {"T1": r1, "T2": r2, "T3": r3, "T4": r4, "T5": r5},
    }
    save_certificate(cert, os.path.join(os.path.dirname(__file__), "..",
                                        "certificates", "s3_certificate.json"))
    print("\nCertificate written: certificates/s3_certificate.json")
    print("ALL S3 TESTS PASS")
