"""S2 free-fermion chain: Gaussian correlation matrices (Peschel).

Dirac fermions on a 1D ring/open chain. All states are Gaussian, so the
reduced state on an interval is fixed by the restricted correlation
matrix C_ij = <c_i^dagger c_j>. Quarantined floating-point class.
"""

from __future__ import annotations

import numpy as np
from numpy.linalg import eigh


def hopping_hamiltonian(L: int, t: float = 1.0, mu: float = 0.0) -> np.ndarray:
    """Single-particle hopping matrix (open chain, half-filling at mu=0)."""
    H = np.zeros((L, L), dtype=float)
    for i in range(L - 1):
        H[i, i + 1] = H[i + 1, i] = -t
    np.fill_diagonal(H, -mu)
    return H


def correlation_from_spectrum(evals: np.ndarray, evecs: np.ndarray,
                              occupancies: np.ndarray) -> np.ndarray:
    """C = V diag(n) V^T with n_k in [0, 1]."""
    return (evecs * occupancies) @ evecs.T


def vacuum_correlation(L: int, t: float = 1.0, mu: float = 0.0) -> np.ndarray:
    H = hopping_hamiltonian(L, t=t, mu=mu)
    evals, evecs = eigh(H)
    n = (evals < 0.0).astype(float)
    # half-fill tie-break at exactly zero
    n[np.isclose(evals, 0.0)] = 0.5
    return correlation_from_spectrum(evals, evecs, n)


def thermal_correlation(L: int, beta: float, t: float = 1.0,
                        mu: float = 0.0) -> np.ndarray:
    H = hopping_hamiltonian(L, t=t, mu=mu)
    evals, evecs = eigh(H)
    # Fermi-Dirac; stable for large beta*|e|
    x = np.clip(beta * (evals - mu), -60.0, 60.0)
    n = 1.0 / (1.0 + np.exp(x))
    return correlation_from_spectrum(evals, evecs, n)


def current_carrying_correlation(L: int, phi: float, t: float = 1.0,
                                 mu: float = 0.0) -> np.ndarray:
    """Ground state of a Peierls-phased chain (uniform vector potential).

    Nonzero bond current / kinetic imbalance is the lattice proxy for a
    chiral 'coherent' excitation: local energy density shifts while the
    entanglement structure stays close to vacuum for small phi.
    """
    H = np.zeros((L, L), dtype=complex)
    z = t * np.exp(1j * phi)
    for i in range(L - 1):
        H[i, i + 1] = -z
        H[i + 1, i] = -np.conj(z)
    np.fill_diagonal(H, -mu)
    evals, evecs = eigh(H)  # Hermitian
    n = (evals < 0.0).astype(float)
    n[np.isclose(evals, 0.0)] = 0.5
    C = (evecs * n) @ evecs.conj().T
    # correlators for density/entropy use Hermitian C; take real part
    # (Im parts cancel in Tr f(C) for our observables)
    return np.real(C)


def energy_density_bonds(C: np.ndarray, t: float = 1.0) -> np.ndarray:
    """Bond kinetic energy density e_i = -t <c_i^dagger c_{i+1} + h.c.>.

    Length L-1. Positive when the bond is more 'excited' than the filled
    bonding orbital (sign convention: vacuum bonds are negative).
    """
    L = C.shape[0]
    e = np.zeros(L - 1)
    for i in range(L - 1):
        hop = C[i, i + 1] + C[i + 1, i]
        e[i] = -t * hop
    return e


def restrict(C: np.ndarray, a: int, b: int) -> np.ndarray:
    """C on sites [a, b)."""
    return np.array(C[a:b, a:b], dtype=float, copy=True)
