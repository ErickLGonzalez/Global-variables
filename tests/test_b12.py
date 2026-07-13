"""B12-RGRC tests -- can the engine prove 'genuinely shared'?

T1  BLIND CLASSIFICATION: all six families, three seeds each, verdicts
    correct with interventions available (18/18 confusion-matrix diagonal).
T2  HEADLINE FALSE-POSITIVE RATE: across families F2-F5 (everything that
    merely LOOKS related), the engine NEVER outputs GENUINE_SHARED_LATENT
    -- shared calibration, shared sensors, shared mathematics, and
    independence are all correctly refused (roadmap M4's success metric).
T3  THE NO-GO, LIVE: without intervention metadata, an F1 (shared latent)
    and an F6 (direct coupling) dataset both return
    NONIDENTIFIABLE(passive) -- the engine refuses to guess where passive
    observation provably cannot decide; with interventions the same data
    separate correctly. 'No unique causal structure from passive
    observations alone' as an executed gate, not a caveat.
T4  HELD-OUT INTERVENTION PREDICTION: gains estimated from the training
    latent-shift predict the response to an unseen shift (delta x 2.5) on
    fresh simulation within tolerance -- Layer-4 shape (predict an
    intervention the estimator never saw).
"""

import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from b12_rgrc.generators import simulate
from b12_rgrc.engine import analyze, heldout_intervention_prediction
from b1_moment_solver.certificate import save_certificate

TRUTH = {"F1": "GENUINE_SHARED_LATENT", "F2": "SHARED_CALIBRATION_ARTIFACT",
         "F3": "INDEPENDENT", "F4": "SHARED_MATHEMATICS_ONLY",
         "F5": "SHARED_SENSOR_COMMON_MODE", "F6": "DIRECT_COUPLING"}


def t1_confusion():
    results, correct = {}, 0
    for fam in TRUTH:
        for seed in (0, 1, 2):
            params = {"a2": 1.4} if fam != "F4" else {"a2": 1.0, "a1": 1.0}
            Y1, Y2, meta = simulate(fam, seed=seed, params=params)
            r = analyze(Y1, Y2, meta)
            ok = r["verdict"] == TRUTH[fam]
            correct += ok
            results.setdefault(fam, []).append(r["verdict"])
    assert correct == 18, results
    print("T1 blind classification: PASS  18/18 across six families x "
          "three seeds:")
    for fam, vs in results.items():
        print(f"    {fam} -> {vs[0]} (x3)")
    return {f: v[0] for f, v in results.items()}


def t2_false_positive():
    fp = 0
    for fam in ("F2", "F3", "F4", "F5"):
        for seed in range(6):
            params = {"a2": 1.0, "a1": 1.0} if fam == "F4" else None
            Y1, Y2, meta = simulate(fam, seed=10 + seed, params=params)
            if analyze(Y1, Y2, meta)["verdict"] == "GENUINE_SHARED_LATENT":
                fp += 1
    assert fp == 0, fp
    print("T2 headline metric: PASS  0/24 false GENUINE_SHARED_LATENT on "
          "look-alike families (calibration, sensors, shared math, "
          "independence)")
    return {"false_shared": fp, "trials": 24}


def t3_no_go():
    outs = {}
    for fam in ("F1", "F6"):
        Y1, Y2, meta = simulate(fam, seed=5, interventions=False)
        r = analyze(Y1, Y2, meta)
        assert r["verdict"] == "NONIDENTIFIABLE", (fam, r)
        assert "passive" in r["cause"]
        outs[fam + "_passive"] = r["verdict"]
        Y1, Y2, meta = simulate(fam, seed=5, interventions=True)
        r2 = analyze(Y1, Y2, meta)
        assert r2["verdict"] == TRUTH[fam], (fam, r2)
        outs[fam + "_interventional"] = r2["verdict"]
    print("T3 no-go live: PASS  F1 and F6 both NONIDENTIFIABLE(passive); "
          "the SAME data separate correctly once the clamp intervention "
          "exists -- causal discrimination demonstrated, not assumed")
    return outs


def t4_heldout():
    Y1, Y2, meta = simulate("F1", seed=7)
    delta_new = 3.0
    pred = heldout_intervention_prediction(Y1, Y2, meta, delta_new)
    # fresh simulation with the unseen shift as the persistent drive
    from b12_rgrc.generators import DT, N_STEPS, _ou_step
    rng = np.random.default_rng(99)
    x1 = x2 = z = 0.0
    m1 = m2 = 0.0
    n = 40_000
    for i in range(n):
        z = _ou_step(z, 0.5, 0.5 * delta_new, 0.6, DT, rng)
        x1 = _ou_step(x1, 1.0, 1.0 * z, 0.35, DT, rng)
        x2 = _ou_step(x2, 1.4, 0.8 * z, 0.35, DT, rng)
        if i > n // 2:
            m1 += x1; m2 += x2
    m1, m2 = m1 / (n - n // 2), m2 / (n - n // 2)
    p1, p2 = pred["predicted_mean_shift"]
    e1, e2 = abs(p1 - m1) / abs(m1), abs(p2 - m2) / abs(m2)
    assert e1 < 0.12 and e2 < 0.12, (pred, m1, m2)
    print(f"T4 held-out intervention: PASS  unseen delta=3.0 predicted to "
          f"({p1:.3f}, {p2:.3f}) vs fresh-sim ({m1:.3f}, {m2:.3f}) -- "
          f"{100*max(e1,e2):.1f}% max error")
    return {"pred": (p1, p2), "sim": (float(m1), float(m2))}


if __name__ == "__main__":
    r1 = t1_confusion(); r2 = t2_false_positive(); r3 = t3_no_go()
    r4 = t4_heldout()
    cert = {
        "certificate_version": "0.3",
        "certificate_class": "NUMERICAL-DISCOVERY / STATISTICAL "
                             "(BENCHMARK tier, E3)",
        "problem": "B12-RGRC: rival-grammar recovery challenge (core: "
                   "shared-latent discrimination)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "m_layer_stipulations": [
            "OU-class generators; thresholds registered in engine.py "
            "before T1/T2 were run",
            "clamp intervention = do(x1 = 0); latent proxy = mean shift",
            "GPT-beyond-quantum and CPTP families deferred to B12-b "
            "(roadmap M4 full scope)",
        ],
        "headline": "engine separates GENUINE shared latents from shared "
                    "calibration, shared sensors, shared mathematics, "
                    "direct coupling and independence: 18/18 blind, 0/24 "
                    "false-shared; refuses (NONIDENTIFIABLE) exactly where "
                    "passive data provably cannot decide; predicts an "
                    "unseen intervention to <12%. The words 'genuinely "
                    "shared' now have an executable test.",
        "results": {"T1": r1, "T2": r2, "T3": r3, "T4": r4},
    }
    save_certificate(cert, os.path.join(os.path.dirname(__file__), "..",
                                        "certificates",
                                        "b12_certificate.json"))
    print("\nCertificate written: certificates/b12_certificate.json")
    print("ALL B12 TESTS PASS")
