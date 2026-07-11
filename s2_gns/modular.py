"""Peschel modular data from a correlation matrix block."""

from __future__ import annotations

import numpy as np
from numpy.linalg import eigh


def _clip_spectrum(nu: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    return np.clip(nu, eps, 1.0 - eps)


def entanglement_entropy(C_A: np.ndarray) -> float:
    """S = -Tr[C ln C + (1-C) ln(1-C)]."""
    nu = _clip_spectrum(eigh(C_A, UPLO="U")[0])
    return float(-np.sum(nu * np.log(nu) + (1.0 - nu) * np.log(1.0 - nu)))


def modular_sp_matrix(C_A: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Single-particle modular Hamiltonian h = ln((1-C)/C).

    Full modular operator on Fock space is Q[h] = sum h_ij c_i^dagger c_j
    (up to an additive constant).
    """
    nu, U = eigh(C_A, UPLO="U")
    nu = _clip_spectrum(nu, eps=eps)
    lam = np.log((1.0 - nu) / nu)
    return (U * lam) @ U.T


def quadratic_connected(C: np.ndarray, h1: np.ndarray, h2: np.ndarray) -> float:
    """Connected correlator <Q[h1]; Q[h2]> for free fermions.

    <Q[h]> = Tr(h C)
    <Q[h1] Q[h2]>_c = Tr(h1 C h2 (1-C))   (standard Wick for number-type
    bilinears when h Hermitian; see Peschel / free-fermion notes).
    """
    return float(np.trace(h1 @ C @ h2 @ (np.eye(C.shape[0]) - C)))


def quadratic_mean(C: np.ndarray, h: np.ndarray) -> float:
    return float(np.trace(h @ C))
