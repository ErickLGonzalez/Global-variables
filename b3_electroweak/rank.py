"""Independent-constraint rank → d_identifiable.

Each discovered relation is a polynomial residual r(obs) = 0. The
identifiable-parameter count is

    d_identifiable = n_quantities − rank(J)

where J is the Jacobian of the residual vector at the observed point,
computed with exact Fraction arithmetic (Gaussian elimination over Q).

This automatically accounts for redundant templates (R6/R8/R9 etc.):
they do not inflate the rank, so the electroweak closed system yields
d_identifiable = 3 regardless of how many equivalent forms are found.
"""

from fractions import Fraction
from typing import Callable, Dict, List, Sequence, Tuple

from .exact import q

Obs = Dict[str, Fraction]

# Ordered quantity keys used as Jacobian columns.
KEYS = [
    "g", "g_prime", "v", "sin_theta_W", "cos_theta_W",
    "e", "M_W", "M_Z", "G_F_inv_sq",
]


def residuals(obs: Obs) -> List[Tuple[str, Fraction]]:
    """Named residuals for every template that is well-defined on `obs`.

    A residual of exactly 0 means the relation holds. Non-zero means it
    fails (used by the negative-control test).
    """
    out: List[Tuple[str, Fraction]] = []
    g = obs.get("g"); gp = obs.get("g_prime"); v = obs.get("v")
    s = obs.get("sin_theta_W"); c = obs.get("cos_theta_W")
    e = obs.get("e"); mw = obs.get("M_W"); mz = obs.get("M_Z")
    gf = obs.get("G_F_inv_sq")

    if e is not None and g is not None and s is not None:
        out.append(("R1", e - g * s))
    if e is not None and gp is not None and c is not None:
        out.append(("R2", e - gp * c))
    if mw is not None and g is not None and v is not None:
        out.append(("R3", mw - g * v / 2))
    if mz is not None and v is not None and g is not None and gp is not None:
        out.append(("R4", 4 * mz * mz - v * v * (g * g + gp * gp)))
    if gf is not None and v is not None:
        out.append(("R5", gf - 2 * v ** 4))
    if c is not None and mw is not None and mz is not None and mz != 0:
        out.append(("R6", c - mw / mz))
    if s is not None and c is not None:
        out.append(("R7", s * s + c * c - 1))
    if g is not None and gp is not None and c is not None and s is not None and gp != 0 and s != 0:
        out.append(("R8", g / gp - c / s))
    if e is not None and g is not None and gp is not None:
        out.append(("R9", e * e * (g * g + gp * gp) - g * g * gp * gp))
    return out


def holding_residuals(obs: Obs) -> List[Tuple[str, Fraction]]:
    return [(n, r) for n, r in residuals(obs) if r == 0]


def _jacobian(obs: Obs, names: Sequence[str], eps: Fraction = Fraction(1, 10**9)) -> List[List[Fraction]]:
    """Exact forward-difference Jacobian is awkward over Q; instead use
    analytic derivatives of each residual (hand-coded, matching residuals).
    """
    rows: List[List[Fraction]] = []
    # Map name -> gradient dict
    g = obs["g"]; gp = obs["g_prime"]; v = obs["v"]
    s = obs["sin_theta_W"]; c = obs["cos_theta_W"]
    e = obs["e"]; mw = obs["M_W"]; mz = obs["M_Z"]
    gf = obs["G_F_inv_sq"]

    grads = {
        # residual → partials w.r.t. KEYS order
        "R1": {"e": 1, "g": -s, "sin_theta_W": -g},
        "R2": {"e": 1, "g_prime": -c, "cos_theta_W": -gp},
        "R3": {"M_W": 1, "g": -v / 2, "v": -g / 2},
        "R4": {
            "M_Z": 8 * mz,
            "v": -2 * v * (g * g + gp * gp),
            "g": -v * v * 2 * g,
            "g_prime": -v * v * 2 * gp,
        },
        "R5": {"G_F_inv_sq": 1, "v": -8 * v ** 3},
        "R6": {"cos_theta_W": 1, "M_W": -1 / mz, "M_Z": mw / (mz * mz)},
        "R7": {"sin_theta_W": 2 * s, "cos_theta_W": 2 * c},
        "R8": {
            "g": 1 / gp,
            "g_prime": -g / (gp * gp),
            "cos_theta_W": -1 / s,
            "sin_theta_W": c / (s * s),
        },
        "R9": {
            "e": 2 * e * (g * g + gp * gp),
            "g": e * e * 2 * g - 2 * g * gp * gp,
            "g_prime": e * e * 2 * gp - 2 * gp * g * g,
        },
    }

    for name in names:
        grad = grads[name]
        rows.append([q(grad.get(k, 0)) for k in KEYS])
    return rows


def matrix_rank(A: List[List[Fraction]]) -> int:
    """Exact Gaussian elimination rank over Q."""
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
    d = n - r
    return {
        "n_quantities": n,
        "holding_constraints": names,
        "n_holding": len(names),
        "constraint_rank": r,
        "d_identifiable": d,
        "formula": "d = n_quantities - rank(Jacobian of holding residuals)",
    }
