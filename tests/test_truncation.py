"""Truncation-audit + GfE-mathematics tests (companion to
docs/notes/gfe-bianconi-review.md; ledger R34-R35).

T1  ARTIFACT (exact): generic ladder couplings -> the truncated
    'emergent constant' differs from the full elimination by an exact
    nonzero rational shift. TRUNCATION_ARTIFACT with the shift as the
    certificate.
T2  PROTECTED (exact): boundary coupling g23 = 0 -> lambda_trunc ==
    lambda_full to the Fraction. TRUNCATION_ROBUST -- decoupling is a
    certifiable symmetry statement, not an assumption.
T3  CLAIMS GATE: truncated-only claims are TRUNCATION_UNAUDITED (the
    GfE status in our classification); a decoupling certificate or a
    shift bound upgrades the claim, per SPEC sections 2/4.
T4  QUADRATIC LICENSE: shift(g23) scales as g23^2 (ratio 4 under
    halving) -- 'weakly coupled dropped sectors' is a quantitative
    statement with a computable constant, never a qualitative wave.
T5  GfE MATHEMATICS IMPORTED (M1 kind 'metric_pair'): the generalized
    eigenvalue spectrum of a metric pair (g, G) is invariant under
    simultaneous congruence (three random GL transforms -> identical
    hash); the Burg/Stein divergence (the eigenvalue-log core of the
    GQRE) is >= 0 and = 0 iff G = g; a genuinely different G changes
    the hash.
"""

import os, sys, time
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from probes.truncation_audit import (effective_stiffness, truncation_audit,
                                     gate)
from canon.engine import canonicalize
from b1_moment_solver.certificate import save_certificate

KS = [Fr(2), Fr(3), Fr(4), Fr(5), Fr(6)]


def t1_artifact():
    r = truncation_audit(KS, [Fr(1), Fr(1), Fr(1), Fr(1)], keep=3)
    assert r["shift"] != 0
    assert r["verdict"].startswith("TRUNCATION_ARTIFACT")
    print(f"T1 artifact: PASS  lambda_trunc = {r['lambda_trunc']} vs "
          f"lambda_full = {r['lambda_full']}; exact shift = {r['shift']} "
          f"-- the 'emergent constant' depends on the dropped sector")
    return {"shift": str(r["shift"])}


def t2_protected():
    r = truncation_audit(KS, [Fr(1), Fr(1), Fr(0), Fr(1)], keep=3)
    assert r["shift"] == 0
    assert r["verdict"].startswith("TRUNCATION_ROBUST")
    print(f"T2 protected: PASS  g23 = 0 -> lambda_trunc == lambda_full "
          f"= {r['lambda_full']} EXACTLY -- decoupling certified, not "
          f"assumed")
    return {"lambda": str(r["lambda_full"])}


def t3_gate():
    g0 = gate(truncated_only=True, decoupling_certificate=False)
    g1 = gate(truncated_only=False, decoupling_certificate=True)
    g2 = gate(truncated_only=True, decoupling_certificate=False,
              shift_bound=Fr(1, 100))
    assert g0.startswith("TRUNCATION_UNAUDITED")
    assert g1.startswith("CLAIM_PERMITTED:")
    assert g2.startswith("CLAIM_PERMITTED_WITH_INTERVAL")
    print("T3 claims gate: PASS  unaudited truncation -> not promotable; "
          "decoupling certificate or shift bound upgrades the claim "
          "(SPEC sections 2/4 wired)")
    return {"unaudited": g0.split(":")[0], "certified": g1.split(":")[0]}


def t4_quadratic():
    shifts = []
    for g in (Fr(1, 10), Fr(1, 20)):
        r = truncation_audit(KS, [Fr(1), Fr(1), g, Fr(1)], keep=3)
        shifts.append(r["shift"])
    ratio = float(shifts[0] / shifts[1])
    assert 3.9 < ratio < 4.1, ratio
    print(f"T4 quadratic license: PASS  halving g23 shrinks the exact "
          f"shift {ratio:.3f}x (theory: 4) -- weak coupling is a "
          f"quantitative license with a computable constant")
    return {"ratio": ratio}


def t5_metric_pair():
    rng = np.random.default_rng(3)
    n = 4
    Xg = rng.standard_normal((n, n)); g = Xg @ Xg.T + n * np.eye(n)
    XG = rng.standard_normal((n, n)); G = XG @ XG.T + n * np.eye(n)
    f1, h1 = canonicalize("metric_pair", g=g, G=G)
    assert f1["burg_divergence"] > 0
    for seed in (11, 12, 13):
        A = rng.standard_normal((n, n)) + n * np.eye(n)
        f2, h2 = canonicalize("metric_pair", g=A @ g @ A.T, G=A @ G @ A.T)
        assert h2 == h1, (seed, f1, f2)
    fs, hs = canonicalize("metric_pair", g=g, G=g)
    assert abs(fs["burg_divergence"]) < 1e-8
    _, hdiff = canonicalize("metric_pair", g=g, G=G + np.eye(n))
    assert hdiff != h1
    print(f"T5 GfE import: PASS  metric-pair spectrum hash {h1} invariant "
          f"under 3 simultaneous congruences; Burg divergence "
          f"{f1['burg_divergence']:.4f} > 0, = 0 at G = g; different G "
          f"discriminated -- the GQRE's eigenvalue-log core now lives in "
          f"M1")
    return {"hash": h1, "burg": f1["burg_divergence"]}


if __name__ == "__main__":
    r1 = t1_artifact(); r2 = t2_protected(); r3 = t3_gate()
    r4 = t4_quadratic(); r5 = t5_metric_pair()
    cert = {
        "certificate_version": "0.3",
        "certificate_class": "EXACT-RATIONAL (Schur continued fractions, "
                             "T1-T4) + NUMERICAL (metric-pair invariants, "
                             "T5)",
        "problem": "Truncation-audit probe + GfE mathematics import "
                   "(R34-R35 review deliverable)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "m_layer_stipulations": [
            "Gaussian-ladder toy certifies the LOGIC of the audit, not a "
            "verdict on GfE's nonlinear setting",
            "metric_pair invariants: simultaneous-congruence group action; "
            "Lorentzian-signature pairs deferred (positive-definite demo)",
        ],
        "headline": "the truncation critique of Gravity-from-Entropy as an "
                    "executable gate: artifact vs protected vs unaudited, "
                    "all exact; the quadratic-coupling license quantified; "
                    "and the GQRE's invariant core (metric-pair spectrum + "
                    "Burg divergence) imported into the canonicalization "
                    "engine.",
        "results": {"T1": r1, "T2": r2, "T3": r3, "T4": r4, "T5": r5},
    }
    save_certificate(cert, os.path.join(os.path.dirname(__file__), "..",
                                        "certificates",
                                        "truncation_certificate.json"))
    print("\nCertificate written: certificates/truncation_certificate.json")
    print("ALL TRUNCATION/GFE TESTS PASS")
