"""Ground-truth Onsager transport matrices and hide/corrupt helpers.

Near-equilibrium linear response: J = L X with
  L ⪰ 0          (second law / entropy production σ = Xᵀ L X ≥ 0)
  L = Lᵀ         (Onsager reciprocity from microscopic reversibility)

Ground truth uses exact rational entries so all FORCED claims stay in
the B1/B2 exact-rational certificate class.
"""

from fractions import Fraction
from typing import Dict, List, Optional, Tuple

from .exact import Mat, q


def thermoelectric_L() -> List[List[Fraction]]:
    """2×2 heat/charge coupling style matrix, SPD and symmetric.

    L = [[4, 1],
         [1, 3]]
    det = 11 > 0, so SPD; L = Lᵀ.
    """
    return [[q(4), q(1)],
            [q(1), q(3)]]


def clone(L: List[List[Fraction]]) -> Mat:
    return [[q(L[i][j]) for j in range(len(L))] for i in range(len(L))]


def hide(L: List[List[Fraction]], positions: List[Tuple[int, int]]) -> Mat:
    M = clone(L)
    for i, j in positions:
        M[i][j] = None
        if i != j:
            # keep partner visible unless also hidden — reciprocity forcing
            # needs the known partner when only one off-diagonal is hidden.
            pass
    return M


def hide_pair(L: List[List[Fraction]], i: int, j: int) -> Mat:
    """Hide both L[i][j] and L[j][i] (unknown off-diagonal pair)."""
    M = clone(L)
    M[i][j] = None
    M[j][i] = None
    return M


def corrupt_asymmetry(L: List[List[Fraction]]) -> List[List[Fraction]]:
    """Reciprocity-violating matrix (no B field): L01 ≠ L10."""
    M = clone(L)
    M[0][1] = q(L[0][1]) + 1
    return M


def corrupt_negative(L: List[List[Fraction]]) -> List[List[Fraction]]:
    """Second-law violating: flip a diagonal to make σ < 0 possible."""
    M = clone(L)
    M[0][0] = q(-1)
    return M
