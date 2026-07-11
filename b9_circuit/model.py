"""B9 ground-truth model: the linearized RCSJ (resistively and capacitively
shunted Josephson junction) circuit as an Ornstein-Uhlenbeck process in
canonical flux-charge coordinates Z = (Phi, Q).

This is the circuit class of the 2025 Nobel Prize (Clarke, Devoret,
Martinis). Canonical rewriting of RCSJ dynamics (ledger R16-R20):

    dZ = -[M + W] grad_H dt + sigma dB,
    H = Q^2/(2C) + (k_Phi/2) Phi^2      (linearized well),
    W = [[0, -1], [1, 0]]                (circuit topology: canonical),
    M = [[0, 0], [0, G]]                 (dissipation: conductance G = 1/R),
    sigma sigma^T = 2 k_B T M            (Johnson noise: FDT).

so the drift generator is A = -(M + W) H_V with H_V = diag(k_Phi, 1/C).

Ground truth is EXACTLY known here; B9 tests whether the estimator
pipeline (R16-R20 methodology) recovers it, detects violations, and
refuses the historically fatal shortcuts.
"""

import numpy as np
from scipy.linalg import expm, solve_lyapunov

KB = 1.0  # units: k_B = 1


def ground_truth(k_phi=3.0, C=2.0, G=0.5, T=0.7):
    H_V = np.diag([k_phi, 1.0 / C])
    W = np.array([[0.0, -1.0], [1.0, 0.0]])
    M = np.array([[0.0, 0.0], [0.0, G]])
    A = -(M + W) @ H_V
    D = 2.0 * KB * T * M                     # FDT: sigma sigma^T
    return {"H_V": H_V, "W": W, "M": M, "A": A, "D": D, "T": T}


def simulate(gt, n_steps=200_000, dt=0.02, seed=0, extra_D=None):
    """Exact discrete OU simulation: z_{k+1} = P z_k + xi_k with
    P = expm(A dt) and Cov(xi) = integral_0^dt e^{As} D e^{A^T s} ds
    (computed via the Lyapunov route). extra_D injects a HIDDEN BATH
    (violating FDT against the nominal temperature)."""
    A, D = gt["A"], gt["D"].copy()
    if extra_D is not None:
        D = D + extra_D
    P = expm(A * dt)
    # Sigma_dt solves: Sigma_dt = Sigma_inf - P Sigma_inf P^T where
    # A Sigma_inf + Sigma_inf A^T + D = 0
    Sig_inf = solve_lyapunov(A, -D)
    Sig_dt = Sig_inf - P @ Sig_inf @ P.T
    Lc = np.linalg.cholesky(Sig_dt + 1e-14 * np.eye(2))
    rng = np.random.default_rng(seed)
    z = np.zeros(2)
    out = np.empty((n_steps + 1, 2))
    out[0] = z
    for k in range(n_steps):
        z = P @ z + Lc @ rng.standard_normal(2)
        out[k + 1] = z
    return out


def simulate_overdamped_1d(k_phi=3.0, G=8.0, T=0.7, n_steps=200_000,
                           dt=0.02, seed=1):
    """Overdamped single-coordinate reduction: G dPhi/dt = -k_phi Phi + xi.
    Effective drift coefficient is k_phi/G (mobility 1/G): the dissipative
    number INVERTS relative to the 2D representation's M entry G.
    Used to demonstrate the model-order warning (R16 sec. 9 analogue)."""
    a = k_phi / G
    Dp = 2.0 * KB * T / G
    P = np.exp(-a * dt)
    s = np.sqrt(Dp / (2 * a) * (1 - P ** 2))
    rng = np.random.default_rng(seed)
    x = 0.0
    out = np.empty(n_steps + 1)
    out[0] = x
    for k in range(n_steps):
        x = P * x + s * rng.standard_normal()
        out[k + 1] = x
    return out, a
