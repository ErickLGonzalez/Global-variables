"""Cut derivatives, QNEC matrix assembly, and GNS operator probe.

EPISTEMIC SCOPE
---------------
- Lattice equal-time endpoint motion proxies null-cut derivatives for
  static states via Sp_null ~= Sp_et/2 (c/3 vs c/6). QUARANTINED.
- Operators A0, A1 are *state-independent* kernels fixed by interval
  geometry (GNS requirement). The state enters only through omega.
- A0 := geometric modular Hamiltonian kernel  sum_i beta(i) T_bond(i)
  A1 := cut-bond stress kernel T_bond(b-1)
  with beta(x) = x (ell-x)/ell  (Casini-Huerta / Bisognano-Wichmann shape).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np

from .chain import energy_density_bonds, restrict
from .modular import entanglement_entropy, quadratic_connected


def _entropy_interval(C: np.ndarray, a: int, b: int) -> float:
    return entanglement_entropy(restrict(C, a, b))


def cut_derivatives(C: np.ndarray, a: int, b: int) -> Tuple[float, float, float]:
    L = C.shape[0]
    assert 2 <= a < b <= L - 2
    S0 = _entropy_interval(C, a, b)
    Sp1 = _entropy_interval(C, a, b + 1)
    Sm1 = _entropy_interval(C, a, b - 1)
    Sp = 0.5 * (Sp1 - Sm1)
    Spp = Sp1 - 2.0 * S0 + Sm1
    return S0, Sp, Spp


def bond_kernel(n: int, bond: int) -> np.ndarray:
    """Single-particle kernel for T_bond ~ -(c^dagger_i c_{i+1}+h.c.)/2."""
    h = np.zeros((n, n))
    if 0 <= bond < n - 1:
        h[bond, bond + 1] = h[bond + 1, bond] = -0.5
    return h


def geometric_modular_kernel(n: int) -> np.ndarray:
    """K_geom = sum_i beta_i T_i with beta_i = x(1-x), x=(i+0.5)/n.

    State-independent continuum-interval modular weight (2pi absorbed into
    calibration). Bond-noise vs IR-correlated stress changes the G01/G00
    scaling; the certificate records the measured fingerprint.
    """
    h = np.zeros((n, n))
    for i in range(n - 1):
        x = (i + 0.5) / n
        beta = x * (1.0 - x)
        h += beta * bond_kernel(n, i)
    return h


def operator_kernels(n: int) -> Tuple[np.ndarray, np.ndarray]:
    """State-independent (A0, A1) kernels on an interval of n sites."""
    h0 = geometric_modular_kernel(n)
    h1 = bond_kernel(n, n - 2) if n >= 2 else np.zeros((n, n))
    return h0, h1


def connected_gram_region(C: np.ndarray, a: int, b: int) -> np.ndarray:
    C_A = restrict(C, a, b)
    n = C_A.shape[0]
    h0, h1 = operator_kernels(n)
    g00 = quadratic_connected(C_A, h0, h0)
    g01 = quadratic_connected(C_A, h0, h1)
    g11 = quadratic_connected(C_A, h1, h1)
    return np.array([[g00, g01], [g01, g11]], dtype=float)


def qnec_matrix_vacuum_proxy(c6: float, Sp_et: float, ell: float) -> np.ndarray:
    """Vacuum/static proxy: T=0, Sp_null=Sp_et/2, Q22 = Sp_null / ell.

    Uses the continuum vacuum relation Q22 = Sp/du (= Sp/ell) rather than
    noisy lattice S'' (second finite differences are unreliable at small L).
    Stipulation recorded in the certificate.
    """
    Sp = 0.5 * Sp_et
    Q22 = Sp / ell if ell != 0 else 0.0
    return np.array([[c6, Sp], [Sp, Q22]], dtype=float)


def qnec_matrix_with_T(c6: float, Sp_et: float, ell: float, T: float) -> np.ndarray:
    """As vacuum proxy, but Q22 = 2*pi*T + Sp/ell (T excess over vacuum)."""
    Sp = 0.5 * Sp_et
    Q22 = 2.0 * np.pi * T + (Sp / ell if ell != 0 else 0.0)
    return np.array([[c6, Sp], [Sp, Q22]], dtype=float)


def psd_eigvals(M: np.ndarray) -> np.ndarray:
    return np.linalg.eigvalsh(M)


def fit_c_over_3(C: np.ndarray, a: int, lengths: np.ndarray) -> float:
    Ss = []
    for ell in lengths:
        b = a + int(ell)
        Ss.append(_entropy_interval(C, a, b))
    slope, _ = np.polyfit(np.log(lengths.astype(float)), np.array(Ss), 1)
    return float(3.0 * slope)


@dataclass
class Calibration:
    scale: float
    c6: float


def calibrate_vacuum(C: np.ndarray, a: int, b: int, c6: float) -> Calibration:
    G = connected_gram_region(C, a, b)
    if abs(G[0, 0]) < 1e-18:
        raise RuntimeError("vanishing G00 — geometric A0 is null on this state")
    return Calibration(scale=c6 / G[0, 0], c6=c6)


def probe_matrix(C: np.ndarray, a: int, b: int, cal: Calibration,
                 T_excess: float = 0.0,
                 mode: str = "vacuum_proxy") -> Dict:
    S, Sp, Spp = cut_derivatives(C, a, b)
    ell = float(b - a)
    if mode == "vacuum_proxy":
        M = qnec_matrix_vacuum_proxy(cal.c6, Sp, ell)
    else:
        M = qnec_matrix_with_T(cal.c6, Sp, ell, T_excess)
    G = connected_gram_region(C, a, b)
    G_scaled = cal.scale * G
    evals_M = psd_eigvals(M)
    evals_G = psd_eigvals(G_scaled)
    # Structure ratios (scale-invariant GNS fingerprint)
    def ratios(X):
        if abs(X[0, 0]) < 1e-18:
            return {"r01": np.nan, "r11": np.nan}
        return {"r01": float(X[0, 1] / X[0, 0]),
                "r11": float(X[1, 1] / X[0, 0])}

    rM, rG = ratios(M), ratios(G)
    rel = float(np.linalg.norm(G_scaled - M) / max(np.linalg.norm(M), 1e-12))
    return {
        "S": S,
        "Sp_equal_time": Sp,
        "Spp_equal_time": Spp,
        "ell": ell,
        "T_excess": T_excess,
        "M": M,
        "G_scaled": G_scaled,
        "rel_frobenius": rel,
        "ratio_M": rM,
        "ratio_G": rG,
        "ratio_target_r01": 1.0 / ell,
        "M_evals": evals_M,
        "G_evals": evals_G,
        "M_psd": bool(evals_M[0] >= -1e-8),
        "G_psd": bool(evals_G[0] >= -1e-8),
        "near_sat": bool(abs(evals_M[0]) / max(abs(evals_M[1]), 1e-12) < 0.05),
    }


def continuum_vacuum_M(c: float, du: float) -> np.ndarray:
    c6 = c / 6.0
    Sp = c / (6.0 * du)
    Q22 = c / (6.0 * du ** 2)
    return np.array([[c6, Sp], [Sp, Q22]])


def cut_stress_excess(C: np.ndarray, C_ref: np.ndarray, b: int) -> float:
    """Cut-bond kinetic energy minus the same bond in a reference state."""
    e = energy_density_bonds(C)
    e0 = energy_density_bonds(C_ref)
    return float(e[b - 1] - e0[b - 1])
