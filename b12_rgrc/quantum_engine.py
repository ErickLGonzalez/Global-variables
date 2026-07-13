"""B12-b quantum engine.

Process verdicts from tomography data alone:
  NOT_A_PROCESS            output-state positivity fails on observed
                           single-system data (min output eigenvalue
                           certifiably negative)
  BEYOND_QUANTUM (P-not-CP) all single-system outputs valid, but the Choi
                           has a bootstrap-certified negative eigenvalue:
                           the process fails COMPOSITION with an ancilla
                           -- the Cmp column as the discriminator
  CLASSICAL_EMBEDDABLE     CPTP and coherence-annihilating (off-diagonal
                           Choi blocks at noise floor): a stochastic
                           matrix in quantum clothes
  QUANTUM_CPTP             CPTP with certified coherence transport
  NONIDENTIFIABLE(apparatus) coherence blocks unobserved (population-only
                           preparation/measurement access): CP is
                           UNDECIDABLE from the data -- refusal, with the
                           M-layer cause stated

All thresholds are bootstrap-calibrated from the stated shot noise, not
fixed magic numbers (B12 discipline).
"""

import numpy as np

from .quantum_families import PAULIS, reconstruct_choi


def _bootstrap_min_eig(ex, n_shots, n_boot=120, seed=1):
    rng = np.random.default_rng(seed)
    C0, _ = reconstruct_choi(ex)
    base = float(np.linalg.eigvalsh((C0 + C0.conj().T) / 2).min())
    sig = 1.0 / np.sqrt(n_shots)
    vals = []
    for _ in range(n_boot):
        ex_b = {k: (None if v is None else v + rng.standard_normal() * sig)
                for k, v in ex.items()}
        Cb, _ = reconstruct_choi(ex_b)
        vals.append(float(np.linalg.eigvalsh((Cb + Cb.conj().T) / 2).min()))
    return base, float(np.std(vals))


def _coherence_norm(C):
    """Frobenius norm of the coherence-transport block: components of the
    Choi on (X or Y) x (X or Y) Paulis."""
    tot = 0.0
    for a in (1, 2):
        for b in (1, 2):
            tot += float(np.real(np.trace(C @ np.kron(PAULIS[a],
                                                      PAULIS[b])))) ** 2
    return np.sqrt(tot) / 4


def classify_process(ex, n_shots):
    n_known = sum(v is not None for v in ex.values())
    if n_known < 16:
        return {"verdict": "NONIDENTIFIABLE",
                "cause": "apparatus access limited to populations: "
                         "coherence blocks unobserved, so complete "
                         "positivity is UNDECIDABLE from these data "
                         "(M-layer, not physics)",
                "observed_components": n_known, "confidence": 1.0}
    C, _ = reconstruct_choi(ex)
    min_eig, sig = _bootstrap_min_eig(ex, n_shots)
    # single-system output positivity: reduced action on Bloch-ball
    # extreme points ~ encoded in Choi partial structure; use the map's
    # action reconstructed from the Choi
    worst_out = _worst_output_eig(C)
    feats = {"choi_min_eig": min_eig, "boot_sigma": sig,
             "worst_output_eig": worst_out,
             "coherence_norm": _coherence_norm(C)}
    if worst_out < -5 * sig:
        return {"verdict": "NOT_A_PROCESS", "features": feats,
                "confidence": 1.0}
    if min_eig < -5 * sig:
        return {"verdict": "BEYOND_QUANTUM",
                "cause": "positive on single systems but Choi eigenvalue "
                         f"{min_eig:.3f} < -5 sigma ({sig:.4f}): fails "
                         "composition with an ancilla (P-not-CP)",
                "features": feats, "confidence": 1.0}
    if feats["coherence_norm"] < 5 * sig:
        return {"verdict": "CLASSICAL_EMBEDDABLE", "features": feats,
                "confidence": 0.9}
    return {"verdict": "QUANTUM_CPTP", "features": feats, "confidence": 0.9}


def _worst_output_eig(C, n_dirs=60):
    """Minimum output eigenvalue over pure input states (map action from
    the Choi: Lambda(rho) = 2 Tr_in[C (I x rho^T)])."""
    worst = 1.0
    for k in range(n_dirs):
        th, ph = np.pi * (k % 12) / 12, 2 * np.pi * k / n_dirs
        psi = np.array([np.cos(th / 2),
                        np.exp(1j * ph) * np.sin(th / 2)])
        rho = np.outer(psi, psi.conj())
        M = 2 * _partial_trace_in(C @ np.kron(np.eye(2), rho.T))
        worst = min(worst, float(np.linalg.eigvalsh((M + M.conj().T) / 2)
                                 .min()))
    return worst


def _partial_trace_in(X):
    X = X.reshape(2, 2, 2, 2)
    return np.trace(X, axis1=1, axis2=3)


def classify_correlations(data):
    S, var = 0.0, 0.0
    signs = {(0, 0): 1, (0, 1): 1, (1, 0): 1, (1, 1): -1}
    for k, (e, n) in data.items():
        S += signs[k] * e
        var += (1 - e ** 2) / n
    sig = np.sqrt(var)
    tsirelson = 2 * np.sqrt(2)
    if S <= 2 + 3 * sig:
        v = "LHV_COMPATIBLE"
    elif S <= tsirelson + 3 * sig:
        v = "QUANTUM_COMPATIBLE (violates classical bound)"
    else:
        v = "BEYOND_QUANTUM_CORRELATIONS (violates Tsirelson)"
    return {"verdict": v, "S": float(S), "sigma": float(sig),
            "gates": {"classical": 2.0, "tsirelson": float(tsirelson),
                      "algebraic": 4.0}}
