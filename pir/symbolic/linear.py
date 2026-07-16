"""Exact-rational linear feasibility core (Stage 2 / P4).

Stdlib only, exact ``Fraction`` arithmetic — the same discipline as
``b1_moment_solver`` (SymPy/Z3 are not repo dependencies; a numeric solver's
output would have to be quarantined to a lower evidence class, which the bridge
enforces). This module answers three questions about a linear system A x = b
over ℚ, each with an exact certificate:

* **UNIQUE** — one solution; it is the SAT witness. (Forcing: the unknown is
  determined, cf. B1 flat extension.)
* **UNDERDETERMINED** — a nontrivial null space; each basis vector is a witness
  of non-identifiability (cf. B3 rank-deficient Jacobian).
* **INCONSISTENT** — no solution; a Farkas vector y with yᵀA = 0 and yᵀb ≠ 0 is
  the UNSAT / impossibility certificate.

Everything is exact; ``verify_*`` functions re-check each certificate.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Optional, Tuple

Vec = List[Fraction]
Mat = List[List[Fraction]]


def _F(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def _augment(A: Mat, b: Vec) -> Mat:
    return [row[:] + [b[i]] for i, row in enumerate(A)]


def solve(A, b) -> Dict:
    """Solve A x = b exactly. Returns a dict with:
      status ∈ {UNIQUE, UNDERDETERMINED, INCONSISTENT}
      solution         (particular solution) when not INCONSISTENT
      null_space       (list of basis vectors) when UNDERDETERMINED
      farkas           (y) when INCONSISTENT: yᵀA = 0, yᵀb ≠ 0
      rank, n_vars
    We track the row operations as a transform T so that, on inconsistency, the
    offending combined row gives the exact Farkas certificate."""
    A = [[_F(x) for x in row] for row in A]
    b = [_F(x) for x in b]
    m = len(A)
    n = len(A[0]) if A else 0
    # Track T (m x m) with M = T · A_orig so reduced rows are exact combinations.
    T = [[Fraction(1) if i == j else Fraction(0) for j in range(m)] for i in range(m)]
    M = [row[:] for row in A]
    rhs = b[:]

    pivots: List[int] = []
    r = 0
    for c in range(n):
        piv = next((i for i in range(r, m) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        rhs[r], rhs[piv] = rhs[piv], rhs[r]
        T[r], T[piv] = T[piv], T[r]
        inv = M[r][c]
        M[r] = [x / inv for x in M[r]]
        rhs[r] = rhs[r] / inv
        T[r] = [x / inv for x in T[r]]
        for i in range(m):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][j] - f * M[r][j] for j in range(n)]
                rhs[i] = rhs[i] - f * rhs[r]
                T[i] = [T[i][j] - f * T[r][j] for j in range(m)]
        pivots.append(c)
        r += 1
        if r == m:
            break

    rank = len(pivots)
    # Inconsistency: a zero row of M with nonzero rhs. Its T-row is the Farkas y.
    for i in range(m):
        if all(M[i][j] == 0 for j in range(n)) and rhs[i] != 0:
            return {"status": "INCONSISTENT", "farkas": T[i][:], "rank": rank,
                    "n_vars": n}

    # Particular solution: free vars = 0, pivot vars = reduced rhs.
    sol = [Fraction(0)] * n
    for row_i, c in enumerate(pivots):
        sol[c] = rhs[row_i]

    free = [c for c in range(n) if c not in pivots]
    if not free:
        return {"status": "UNIQUE", "solution": sol, "rank": rank, "n_vars": n}

    # Null space basis: one vector per free column.
    null: List[Vec] = []
    for fc in free:
        v = [Fraction(0)] * n
        v[fc] = Fraction(1)
        for row_i, c in enumerate(pivots):
            v[c] = -M[row_i][fc]
        null.append(v)
    return {"status": "UNDERDETERMINED", "solution": sol, "null_space": null,
            "rank": rank, "n_vars": n, "free_vars": free}


# ---- verification (each certificate is independently checkable) ----------- #
def _matvec(A: Mat, x: Vec) -> Vec:
    return [sum(_F(A[i][j]) * x[j] for j in range(len(x))) for i in range(len(A))]


def verify_solution(A, b, x) -> bool:
    A = [[_F(v) for v in row] for row in A]
    b = [_F(v) for v in b]
    x = [_F(v) for v in x]
    return _matvec(A, x) == b


def verify_null(A, v) -> bool:
    A = [[_F(x) for x in row] for row in A]
    v = [_F(x) for x in v]
    return all(s == 0 for s in _matvec(A, v)) and any(x != 0 for x in v)


def verify_farkas(A, b, y) -> bool:
    """yᵀA = 0 and yᵀb ≠ 0 certifies A x = b has no solution."""
    A = [[_F(x) for x in row] for row in A]
    b = [_F(x) for x in b]
    y = [_F(x) for x in y]
    n = len(A[0]) if A else 0
    yA = [sum(y[i] * A[i][j] for i in range(len(A))) for j in range(n)]
    yb = sum(y[i] * b[i] for i in range(len(A)))
    return all(v == 0 for v in yA) and yb != 0
