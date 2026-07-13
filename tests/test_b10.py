"""B10 tests -- CV Gaussian-channel completion (EXP-A software back-end).

T1  CHANNEL ZOO (exact): quantum-limited attenuator and amplifier certify
    CP with FLAT boundary (rank-deficient M_CP); beam splitter (symplectic,
    N = 0) certifies; a sub-uncertainty 'amplifier' is NOT_A_CHANNEL with
    an exact witness -- the uncertainty principle as an executable gate.
T2  CAVES BOUND AS A PERMITTED INTERVAL: hiding the noise entry of an
    amplifier under CP alone yields the certified interval
    N_00 in [(g-1)/2, inf) -- the quantum limit of amplification
    recovered as a B1-style restraint boundary, flat at the endpoint.
T3  UNITARITY STACKING: N = 0 forces the hidden T entry exactly via the
    symplectic condition det T = 1 (PERMITTED -> FORCED upgrade).
T4  COMPOSITION SEMIGROUP (exact): quantum-limited attenuators compose to
    the quantum-limited attenuator with eta = eta1*eta2 -- CP closure and
    the scale-flow structure of the Cmp column, exact to the Fraction.
T5  TOMOGRAPHY LAYER (numeric): (eta, N) recovered from noisy input/output
    covariance pairs; CP gate passes on the estimate; data from a fake
    channel is REJECTED (negative control).
T6  HELD-OUT PREDICTION: channel calibrated on thermal inputs predicts a
    SQUEEZED input's output covariance to <1% -- the 1985 protocol shape.
"""

import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fractions import Fraction as Fr

import numpy as np

from b10_cv_channel.gaussian_channel import (certify_channel, cp_matrix,
                                             permitted_noise_interval,
                                             force_symplectic_entry,
                                             matmul_r, transpose)
from b1_moment_solver.certificate import save_certificate


def diagT(x):
    return [[Fr(x), Fr(0)], [Fr(0), Fr(x)]]


def diagN(y):
    return [[Fr(y), Fr(0)], [Fr(0), Fr(y)]]


def t1_zoo():
    att = certify_channel(diagT(Fr(3, 5)), diagN(Fr(8, 25)))
    amp = certify_channel(diagT(Fr(5, 3)), diagN(Fr(8, 9)))
    assert att["verdict"].startswith("QUANTUM_LIMITED"), att
    assert amp["verdict"].startswith("QUANTUM_LIMITED"), amp
    c, s, z = Fr(3, 5), Fr(4, 5), Fr(0)
    Tbs = [[c, z, s, z], [z, c, z, s], [-s, z, c, z], [z, -s, z, c]]
    Nbs = [[z] * 4 for _ in range(4)]
    bs = certify_channel(Tbs, Nbs)
    assert bs["status"] != "NOT_PSD_CERTIFIED" and bs["rank"] == 0, bs
    cl = certify_channel(diagT(1), diagN(Fr(1, 4)))
    assert cl["verdict"].startswith("CHANNEL_CP_CERTIFIED"), cl
    fake = certify_channel(diagT(Fr(5, 3)), diagN(Fr(1, 3)))
    assert fake["verdict"].startswith("NOT_A_CHANNEL"), fake
    print("T1 zoo: PASS  attenuator/amplifier QUANTUM_LIMITED (flat), "
          "beam splitter symplectic (rank 0), noise channel strict, "
          "sub-uncertainty amplifier NOT_A_CHANNEL (exact witness)")
    return {"attenuator": att, "amplifier": amp, "beam_splitter": bs,
            "fake": fake}


def t2_caves():
    T = diagT(Fr(5, 3))
    N = diagN(Fr(8, 9))          # hole at (0,0) will override
    res = permitted_noise_interval(T, N, (0, 0))
    lo = Fr(res["certified_inner_interval"][0])
    bound = Fr(8, 9)             # (g-1)/2 with g = 25/9
    assert res["status"] == "PERMITTED"
    assert abs(lo - bound) < Fr(1, 10**12), (lo, bound)
    at_bound = certify_channel(T, diagN(bound))
    assert at_bound["verdict"].startswith("QUANTUM_LIMITED")
    below = certify_channel(T, [[bound - Fr(1, 1000), Fr(0)],
                                [Fr(0), Fr(8, 9)]])
    assert below["verdict"].startswith("NOT_A_CHANNEL")
    print(f"T2 Caves bound: PASS  hidden amplifier noise PERMITTED down to "
          f"{lo} = (g-1)/2 exactly; boundary flat; below REJECTED -- the "
          f"quantum limit of amplification as a certified interval")
    return {"certified_lower": str(lo), "exact_bound": str(bound)}


def t3_symplectic():
    T = [[Fr(2), Fr(3)], [Fr(1), None]]
    res = force_symplectic_entry([[Fr(2), Fr(3)], [Fr(1), Fr(0)]], (1, 1))
    assert res["status"] == "FORCED" and res["_frac"] == Fr(2), res
    Tfull = [[Fr(2), Fr(3)], [Fr(1), Fr(2)]]
    cert = certify_channel(Tfull, diagN(0))
    assert cert["rank"] == 0, cert            # exactly symplectic
    print(f"T3 symplectic forcing: PASS  hidden entry FORCED to "
          f"{res['value']} by det T = 1; completed T certifies N = 0")
    return res


def t4_composition():
    T1, N1 = diagT(Fr(3, 5)), diagN(Fr(8, 25))
    T2, N2 = diagT(Fr(4, 5)), diagN(Fr(9, 50))
    T = matmul_r(T2, T1)
    N2T = matmul_r(matmul_r(T2, N1), transpose(T2))
    N = [[N2T[i][j] + N2[i][j] for j in range(2)] for i in range(2)]
    assert T[0][0] == Fr(12, 25) and N[0][0] == Fr(481, 1250), (T, N)
    assert N[0][0] == (1 - Fr(12, 25) ** 2) / 2   # quantum-limited again
    cert = certify_channel(T, N)
    assert cert["verdict"].startswith("QUANTUM_LIMITED"), cert
    print("T4 composition: PASS  eta1*eta2 semigroup exact "
          "(12/25 = 3/5 * 4/5, N = 481/1250 = quantum limit); CP closed "
          "on the flat boundary")
    return {"eta_composite": "144/625", "N_composite": str(N[0][0])}


def _simulate(eta, Nf, inputs, noise, rng):
    return [eta * s + Nf + noise * rng.standard_normal((2, 2))
            for s in inputs]


def _reconstruct(inputs, outputs):
    A, b = [], []
    for s, o in zip(inputs, outputs):
        for i in range(2):
            for j in range(2):
                A.append([s[i, j]] + [1.0 if (i, j) == (p, q) else 0.0
                                      for p in range(2) for q in range(2)])
                b.append(o[i, j])
    coef, *_ = np.linalg.lstsq(np.array(A), np.array(b), rcond=None)
    Nhat = coef[1:].reshape(2, 2)
    return coef[0], (Nhat + Nhat.T) / 2


def _cp_numeric(eta, Nhat, tol=2e-2):
    Om = np.array([[0., 1.], [-1., 0.]])
    M = Nhat + 0.5j * (Om - eta * Om)
    return float(np.linalg.eigvalsh((M + M.conj().T) / 2).min()) > -tol


def t5_tomography():
    rng = np.random.default_rng(0)
    eta, Nf = 0.36, 0.32 * np.eye(2) + 0.05 * np.array([[1, .5], [.5, 1]])
    inputs = [0.5 * np.eye(2) * t for t in (1.0, 1.6, 2.4, 3.5, 5.0)]
    outs = _simulate(eta, Nf, inputs, 3e-3, rng)
    eta_hat, N_hat = _reconstruct(inputs, outs)
    assert abs(eta_hat - eta) < 0.01 and np.abs(N_hat - Nf).max() < 0.02
    assert _cp_numeric(eta_hat, N_hat)
    fake_outs = _simulate(25 / 9, 0.15 * np.eye(2), inputs, 3e-3, rng)
    e2, N2 = _reconstruct(inputs, fake_outs)
    assert not _cp_numeric(e2, N2)
    print(f"T5 tomography: PASS  (eta, N) recovered "
          f"(eta_hat = {eta_hat:.4f}); CP gate passes; fake-channel data "
          f"REJECTED (negative control)")
    return {"eta_hat": float(eta_hat)}


def t6_heldout():
    rng = np.random.default_rng(1)
    eta, Nf = 0.36, 0.32 * np.eye(2)
    inputs = [0.5 * np.eye(2) * t for t in (1.0, 1.8, 2.8, 4.0)]
    outs = _simulate(eta, Nf, inputs, 2e-3, rng)
    eta_hat, N_hat = _reconstruct(inputs, outs)
    r = 0.6
    sq = 0.5 * np.diag([np.exp(-2 * r), np.exp(2 * r)])
    truth = eta * sq + Nf
    pred = eta_hat * sq + N_hat
    err = float(np.abs(pred - truth).max() / np.abs(truth).max())
    assert err < 0.01, err
    print(f"T6 held-out: PASS  squeezed-input output predicted to "
          f"{100*err:.2f}% from thermal-only calibration")
    return {"rel_err": err}


if __name__ == "__main__":
    r1 = t1_zoo(); r2 = t2_caves(); r3 = t3_symplectic()
    r3.pop("_frac", None)
    r4 = t4_composition(); r5 = t5_tomography(); r6 = t6_heldout()
    cert = {
        "certificate_version": "0.3",
        "certificate_class": "EXACT-RATIONAL (CP gate, intervals, forcing, "
                             "composition) + NUMERICAL-DISCOVERY (tomography)",
        "problem": "B10: CV Gaussian-channel completion (EXP-A back-end)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "calibration_route": "synthetic ground truth (BENCHMARK tier); "
                             "real-data runs must record instrument route",
        "m_layer_stipulations": [
            "vacuum covariance = I/2 convention; Omega block-diagonal",
            "noise holes: diagonal entries (demo); off-diagonal holes via "
            "the same bisection pattern",
            "tomography assumes T = sqrt(eta) I isotropy (single mode)",
        ],
        "headline": "uncertainty principle as an exact CP gate; Caves "
                    "amplifier bound recovered as a certified PERMITTED "
                    "boundary (flat); symplectic forcing; quantum-limited "
                    "semigroup exact; tomography + held-out squeezed "
                    "prediction pass. hbar row Pos/Uni/Cmp exercised at "
                    "BENCHMARK tier.",
        "results": {"T1": r1, "T2": r2, "T3": r3, "T4": r4, "T5": r5,
                    "T6": r6},
    }
    save_certificate(cert, os.path.join(os.path.dirname(__file__), "..",
                                        "certificates",
                                        "b10_certificate.json"))
    print("\nCertificate written: certificates/b10_certificate.json")
    print("ALL B10 TESTS PASS")
