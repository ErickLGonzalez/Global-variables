"""Jacobian rank → d_identifiable for the coupling / factorization sector.

Quantities in the observation table. Scheme factor κ is treated as known
(not a physical source). Physical identifiable count targets 1: a single
coupling α controlling all channels.
"""

from fractions import Fraction
from typing import Dict, List, Sequence, Tuple

from .exact import q

Obs = Dict[str, Fraction]

# Physical + derived observables (κ excluded from identifiable count).
KEYS = [
    "A_22", "R_24", "A_22_cross", "R_24_b",
    "alpha_22", "alpha_24", "alpha_22_cross", "alpha_24_b",
]


def residuals(obs: Obs) -> List[Tuple[str, Fraction]]:
    out: List[Tuple[str, Fraction]] = []
    A = obs.get("A_22"); R = obs.get("R_24")
    Ac = obs.get("A_22_cross"); Rb = obs.get("R_24_b")
    a22 = obs.get("alpha_22"); a24 = obs.get("alpha_24")
    a22c = obs.get("alpha_22_cross"); a24b = obs.get("alpha_24_b")
    k = obs.get("kappa")

    if A is not None and R is not None:
        out.append(("F1", R - A * A))
    if Ac is not None and Rb is not None:
        out.append(("F2", Rb - Ac * Ac))
    if A is not None and Ac is not None:
        out.append(("F3", A - Ac))
    if a22 is not None and a24 is not None:
        out.append(("F4a", a24 - a22))
    if a22 is not None and a22c is not None:
        out.append(("F4b", a22c - a22))
    if a22 is not None and a24b is not None:
        out.append(("F4c", a24b - a22))
    if A is not None and k is not None and a22 is not None:
        out.append(("F5", A - k * a22))
    if R is not None and k is not None and a24 is not None:
        out.append(("F6", R - (k * a24) ** 2))
    return out


def holding_residuals(obs: Obs) -> List[Tuple[str, Fraction]]:
    return [(n, r) for n, r in residuals(obs) if r == 0]


def _jacobian(obs: Obs, names: Sequence[str]) -> List[List[Fraction]]:
    A = obs.get("A_22", 0); R = obs.get("R_24", 0)
    Ac = obs.get("A_22_cross", 0); Rb = obs.get("R_24_b", 0)
    a22 = obs.get("alpha_22", 0); a24 = obs.get("alpha_24", 0)
    a22c = obs.get("alpha_22_cross", 0); a24b = obs.get("alpha_24_b", 0)
    k = obs.get("kappa", 1)

    grads = {
        "F1": {"R_24": 1, "A_22": -2 * A},
        "F2": {"R_24_b": 1, "A_22_cross": -2 * Ac},
        "F3": {"A_22": 1, "A_22_cross": -1},
        "F4a": {"alpha_24": 1, "alpha_22": -1},
        "F4b": {"alpha_22_cross": 1, "alpha_22": -1},
        "F4c": {"alpha_24_b": 1, "alpha_22": -1},
        "F5": {"A_22": 1, "alpha_22": -k},
        "F6": {"R_24": 1, "alpha_24": -2 * k * k * a24},
    }
    rows = []
    for name in names:
        g = grads[name]
        rows.append([q(g.get(col, 0)) for col in KEYS])
    return rows


def matrix_rank(A: List[List[Fraction]]) -> int:
    if not A:
        return 0
    M = [row[:] for row in A]
    rows, cols = len(M), len(M[0])
    rank = 0
    row = 0
    for col in range(cols):
        pivot = None
        for i in range(row, rows):
            if M[i][col] != 0:
                pivot = i
                break
        if pivot is None:
            continue
        M[row], M[pivot] = M[pivot], M[row]
        piv = M[row][col]
        M[row] = [x / piv for x in M[row]]
        for i in range(rows):
            if i == row:
                continue
            f = M[i][col]
            if f != 0:
                M[i] = [a - f * b for a, b in zip(M[i], M[row])]
        rank += 1
        row += 1
        if row == rows:
            break
    return rank


def d_identifiable(obs: Obs) -> Dict:
    held = holding_residuals(obs)
    names = [n for n, _ in held]
    J = _jacobian(obs, names)
    r = matrix_rank(J)
    n = len(KEYS)
    return {
        "n_quantities": n,
        "holding_constraints": names,
        "n_holding": len(names),
        "constraint_rank": r,
        "d_identifiable": n - r,
        "formula": "d = n_quantities - rank(Jacobian); κ treated as known scheme",
        "target": 1,
    }
