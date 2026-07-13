"""B12-b tests -- rival grammars, quantum layer.

T1  PROCESS FAMILIES BLIND: G1 -> QUANTUM_CPTP, G2 -> CLASSICAL_EMBEDDABLE,
    G3 -> BEYOND_QUANTUM (Choi negativity = failed ancilla composition;
    the Cmp column deciding), G4 -> NOT_A_PROCESS. Three seeds each.
T2  APPARATUS-LIMITED REFUSAL: with population-only access, G1 and G3
    both return NONIDENTIFIABLE(apparatus) -- CP is undecidable when
    coherence blocks are unobserved; full Pauli access separates the SAME
    channels. The M-layer decides decidability, demonstrated live.
T3  CHSH LADDER: LHV / singlet / PR-box classified against the classical
    and Tsirelson gates with propagated shot-noise error bars.
T4  FALSE-BEYOND-QUANTUM DISCIPLINE: across 12 noisy CPTP runs (G1, G2 x
    6 seeds), ZERO BEYOND_QUANTUM verdicts -- negativity claims require
    a 5-sigma bootstrap-certified Choi eigenvalue (headline metric).
T5  HELD-OUT PREDICTION: the reconstructed G1 channel predicts the output
    of an unseen input state to trace distance < 0.02.
"""

import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from b12_rgrc.quantum_families import (apply_family, tomography_data,
                                       reconstruct_choi, chsh_data, I2)
from b12_rgrc.quantum_engine import (classify_process,
                                     classify_correlations,
                                     _partial_trace_in)
from b1_moment_solver.certificate import save_certificate

TRUTH = {"G1": "QUANTUM_CPTP", "G2": "CLASSICAL_EMBEDDABLE",
         "G3": "BEYOND_QUANTUM", "G4": "NOT_A_PROCESS"}
N_SHOTS = 200_000


def t1_families():
    results, ok = {}, 0
    for fam in TRUTH:
        for seed in (0, 1, 2):
            ex = tomography_data(fam, N_SHOTS, seed=seed)
            v = classify_process(ex, N_SHOTS)["verdict"]
            ok += (v == TRUTH[fam])
            results.setdefault(fam, []).append(v)
    assert ok == 12, results
    print("T1 quantum families: PASS  12/12 blind:")
    for fam, vs in results.items():
        print(f"    {fam} -> {vs[0]} (x3)")
    return {f: v[0] for f, v in results.items()}


def t2_apparatus_refusal():
    outs = {}
    for fam in ("G1", "G3"):
        ex = tomography_data(fam, N_SHOTS, seed=4, access="populations")
        r = classify_process(ex, N_SHOTS)
        assert r["verdict"] == "NONIDENTIFIABLE", (fam, r)
        assert "apparatus" in r["cause"]
        outs[fam + "_populations"] = r["verdict"]
        ex_full = tomography_data(fam, N_SHOTS, seed=4, access="full")
        r2 = classify_process(ex_full, N_SHOTS)
        assert r2["verdict"] == TRUTH[fam], (fam, r2)
        outs[fam + "_full"] = r2["verdict"]
    print("T2 apparatus-limited refusal: PASS  population-only access -> "
          "NONIDENTIFIABLE(apparatus) for both a CPTP and a P-not-CP "
          "channel; full Pauli access separates the same channels -- "
          "decidability lives in the M-layer")
    return outs


def t3_chsh():
    outs = {}
    expect = {"C1": "LHV_COMPATIBLE", "C2": "QUANTUM_COMPATIBLE",
              "C3": "BEYOND_QUANTUM_CORRELATIONS"}
    for fam, want in expect.items():
        r = classify_correlations(chsh_data(fam, seed=0))
        assert r["verdict"].startswith(want), (fam, r)
        outs[fam] = {"S": round(r["S"], 3), "sigma": round(r["sigma"], 4),
                     "verdict": r["verdict"]}
    print(f"T3 CHSH ladder: PASS  S = {outs['C1']['S']} (LHV), "
          f"{outs['C2']['S']} (quantum, > 2), {outs['C3']['S']} "
          f"(> Tsirelson 2.828) -- both gates live with error bars")
    return outs


def t4_false_beyond():
    fp = 0
    for fam in ("G1", "G2"):
        for seed in range(6):
            ex = tomography_data(fam, N_SHOTS, seed=20 + seed)
            if classify_process(ex, N_SHOTS)["verdict"] == "BEYOND_QUANTUM":
                fp += 1
    assert fp == 0, fp
    print("T4 discipline: PASS  0/12 false BEYOND_QUANTUM on noisy CPTP "
          "data (5-sigma bootstrap gate on Choi negativity)")
    return {"false_beyond": fp, "trials": 12}


def t5_heldout():
    ex = tomography_data("G1", N_SHOTS, seed=7)
    C, _ = reconstruct_choi(ex)
    psi = np.array([np.cos(0.4), np.exp(0.9j) * np.sin(0.4)])
    rho = np.outer(psi, psi.conj())
    pred = 2 * _partial_trace_in(C @ np.kron(np.eye(2), rho.T))
    truth = apply_family("G1", rho)
    d = 0.5 * np.abs(np.linalg.eigvalsh(pred - truth)).sum()
    assert d < 0.02, d
    print(f"T5 held-out: PASS  unseen input predicted to trace distance "
          f"{d:.4f}")
    return {"trace_distance": float(d)}


if __name__ == "__main__":
    r1 = t1_families(); r2 = t2_apparatus_refusal(); r3 = t3_chsh()
    r4 = t4_false_beyond(); r5 = t5_heldout()
    cert = {
        "certificate_version": "0.3",
        "certificate_class": "NUMERICAL-DISCOVERY / STATISTICAL "
                             "(BENCHMARK tier, E3; bootstrap-calibrated)",
        "problem": "B12-b: rival grammars, quantum layer (CPTP / classical "
                   "/ P-not-CP / non-process; CHSH ladder)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "m_layer_stipulations": [
            "single-qubit process tomography; shot noise 1/sqrt(n) per "
            "Pauli component; 5-sigma bootstrap gates",
            "population-only access = X/Y components unobserved (the "
            "apparatus-limited regime, by construction)",
            "GPT state-space families beyond correlation tables deferred "
            "to B12-c",
        ],
        "headline": "the Cmp column separates quantum from beyond-quantum: "
                    "P-not-CP channels detected by certified Choi "
                    "negativity (failed ancilla composition), 12/12 blind, "
                    "0/12 false-beyond; CP shown UNDECIDABLE under "
                    "population-only apparatus access (refusal with "
                    "M-layer cause); Tsirelson gate live in the CHSH "
                    "ladder.",
        "results": {"T1": r1, "T2": r2, "T3": r3, "T4": r4, "T5": r5},
    }
    save_certificate(cert, os.path.join(os.path.dirname(__file__), "..",
                                        "certificates",
                                        "b12b_certificate.json"))
    print("\nCertificate written: certificates/b12b_certificate.json")
    print("ALL B12-B TESTS PASS")
