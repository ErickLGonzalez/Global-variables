"""S2 Gaussian machinery: free Dirac fermion chain (c = 1), the solvable
microscopic laboratory for the ?2 GNS program.

Everything reduces to the two-point correlation matrix C_ij = <c_i^dag c_j>:
  - infinite-chain GROUND STATE at half filling (exact kernel):
        C_ij = sin(pi (i-j)/2) / (pi (i-j)),   C_ii = 1/2
  - infinite-chain THERMAL state (dispersion e_k = -cos k, mu = 0):
        C_ij = (1/2pi) int dk cos(k(i-j)) / (1 + exp(-beta cos k))
  - entanglement entropy of a region A from the eigenvalues nu of C_A:
        S = -sum [nu ln nu + (1-nu) ln(1-nu)]
  - modular Hamiltonian (single-particle form, Peschel):
        K_1p = ln((1 - C_A)/C_A),   S = <K> exactly (K = -ln rho).

VALIDITY GATE: a matrix is a fermionic Gaussian state iff 0 <= nu <= 1.
Violations are REJECTED at the gate -- microscopic positivity, same
epistemics as every other benchmark.
"""

import numpy as np
from scipy.integrate import quad

CLIP = 1e-12


def ground_state_C(L):
    idx = np.arange(L)
    d = idx[:, None] - idx[None, :]
    with np.errstate(divide="ignore", invalid="ignore"):
        C = np.sin(np.pi * d / 2.0) / (np.pi * d)
    np.fill_diagonal(C, 0.5)
    return C


def thermal_C(L, beta):
    def kernel(r):
        f = lambda k: np.cos(k * r) / (1.0 + np.exp(-beta * np.cos(k)))
        val, _ = quad(f, -np.pi, np.pi, limit=200)
        return val / (2 * np.pi)
    row = np.array([kernel(r) for r in range(L)])
    idx = np.arange(L)
    return row[np.abs(idx[:, None] - idx[None, :])]


def validity_gate(C_A):
    nu = np.linalg.eigvalsh((C_A + C_A.T) / 2)
    ok = bool(nu.min() > -1e-9 and nu.max() < 1 + 1e-9)
    return ok, nu


def entropy(C_A):
    ok, nu = validity_gate(C_A)
    if not ok:
        raise ValueError(f"NOT_A_GAUSSIAN_STATE: nu range "
                         f"[{nu.min():.3e}, {nu.max():.3e}] outside [0,1] "
                         f"-- microscopic positivity gate REJECTED")
    nu = np.clip(nu, CLIP, 1 - CLIP)
    return float(-np.sum(nu * np.log(nu) + (1 - nu) * np.log(1 - nu)))


def modular_1p(C_A):
    """Single-particle modular Hamiltonian K = ln((1-C)/C) via
    eigendecomposition (numerical layer; quarantined class)."""
    Cs = (C_A + C_A.T) / 2
    nu, U = np.linalg.eigh(Cs)
    nu = np.clip(nu, CLIP, 1 - CLIP)
    eps = np.log((1 - nu) / nu)
    return U @ np.diag(eps) @ U.T
