"""Exact rational-arithmetic core for the B1 truncated moment problem.

Everything in this module is EXACT (Python Fractions). The PSD certificate
produced here is a genuine mathematical certificate, not a numerical claim:
symmetric Gaussian elimination without pivoting is valid for PSD detection
because a PSD matrix with a zero diagonal entry must have the entire
corresponding row and column equal to zero.

The successive pivots ARE the successive Schur complements — pivot d_k is
the Schur complement of the leading k-block, generalizing the verifier
standard  G00 > 0,  S2 = G22 - G02^2/G00 > 0.
"""

from fractions import Fraction
from typing import List, Optional, Tuple

Mat = List[List[Fraction]]


def hankel(moments: List[Fraction], t: int) -> Mat:
    """Moment matrix M_t with (M_t)_{ij} = m_{i+j}, size (t+1)x(t+1).

    Requires moments m_0 .. m_{2t}.
    """
    if len(moments) < 2 * t + 1:
        raise ValueError(f"need {2*t+1} moments for M_{t}, got {len(moments)}")
    return [[Fraction(moments[i + j]) for j in range(t + 1)] for i in range(t + 1)]


def psd_certificate(M: Mat) -> Tuple[str, List[Fraction], int]:
    """Exact PSD test via symmetric elimination.

    Returns (status, pivots, rank) where status is one of:
      'PSD_CERTIFIED'      all pivots >= 0, zero pivots have zero rows
      'PD_CERTIFIED'       all pivots strictly > 0 (full rank)
      'NOT_PSD_CERTIFIED'  a negative pivot or a zero diagonal with a
                           nonzero off-diagonal entry was found (exact
                           witness of indefiniteness)
    pivots: the successive Schur-complement pivots (exact rationals).
    rank:   number of strictly positive pivots (= rank when PSD).
    """
    n = len(M)
    A = [[Fraction(M[i][j]) for j in range(n)] for i in range(n)]
    pivots: List[Fraction] = []
    rank = 0
    for k in range(n):
        d = A[k][k]
        if d < 0:
            pivots.append(d)
            return "NOT_PSD_CERTIFIED", pivots, rank
        if d == 0:
            # PSD requires the whole remaining row to vanish.
            if any(A[k][j] != 0 for j in range(k + 1, n)):
                pivots.append(d)
                return "NOT_PSD_CERTIFIED", pivots, rank
            pivots.append(Fraction(0))
            continue
        pivots.append(d)
        rank += 1
        for i in range(k + 1, n):
            if A[i][k] == 0:
                continue
            f = A[i][k] / d
            for j in range(k, n):
                A[i][j] -= f * A[k][j]
    status = "PD_CERTIFIED" if rank == n else "PSD_CERTIFIED"
    return status, pivots, rank


def hankel_rank(moments: List[Fraction], t: int) -> int:
    """Exact rank of M_t (valid when M_t is PSD)."""
    _, _, r = psd_certificate(hankel(moments, t))
    return r


def is_flat(moments: List[Fraction], t: int) -> bool:
    """Curto-Fialkow flatness: rank M_t == rank M_{t-1}."""
    if t < 1:
        return False
    return hankel_rank(moments, t) == hankel_rank(moments, t - 1)


def kernel_recurrence(moments: List[Fraction], r: int) -> List[Fraction]:
    """Monic degree-r polynomial p(x) = x^r + c_{r-1}x^{r-1} + ... + c_0
    annihilating the moment sequence:

        m_{n+r} + c_{r-1} m_{n+r-1} + ... + c_0 m_n = 0   for all valid n.

    Solved exactly from the first r recurrence rows. Requires
    rank M_s = r (flat) with enough known moments (>= 2r).
    Returns [c_0, ..., c_{r-1}, 1].
    """
    if len(moments) < 2 * r:
        raise ValueError("need at least 2r moments to identify the recurrence")
    # Solve  sum_{k=0}^{r-1} c_k m_{n+k} = -m_{n+r},  n = 0..r-1  (exact).
    A = [[Fraction(moments[n + k]) for k in range(r)] for n in range(r)]
    b = [-Fraction(moments[n + r]) for n in range(r)]
    c = _solve_exact(A, b)
    if c is None:
        raise ValueError("recurrence system singular: rank assumption violated")
    # Consistency check against ALL remaining known moments (exact).
    for n in range(len(moments) - r):
        s = Fraction(moments[n + r]) + sum(c[k] * moments[n + k] for k in range(r))
        if s != 0:
            raise ValueError(f"recurrence inconsistent at n={n}: data not rank-{r} Hankel")
    return c + [Fraction(1)]


def extend_by_recurrence(moments: List[Fraction], poly: List[Fraction], upto: int) -> List[Fraction]:
    """Extend the moment list to index `upto` (inclusive) using the exact
    recurrence. Every extended moment is FORCED by flatness (unique flat
    extension, Curto-Fialkow)."""
    r = len(poly) - 1
    out = [Fraction(m) for m in moments]
    while len(out) <= upto:
        n = len(out) - r
        nxt = -sum(poly[k] * out[n + k] for k in range(r))
        out.append(nxt)
    return out


def _solve_exact(A: Mat, b: List[Fraction]) -> Optional[List[Fraction]]:
    """Exact Gaussian elimination with partial (nonzero) pivoting."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for k in range(n):
        piv = next((i for i in range(k, n) if M[i][k] != 0), None)
        if piv is None:
            return None
        M[k], M[piv] = M[piv], M[k]
        for i in range(k + 1, n):
            if M[i][k] == 0:
                continue
            f = M[i][k] / M[k][k]
            for j in range(k, n + 1):
                M[i][j] -= f * M[k][j]
    x = [Fraction(0)] * n
    for k in range(n - 1, -1, -1):
        s = M[k][n] - sum(M[k][j] * x[j] for j in range(k + 1, n))
        x[k] = s / M[k][k]
    return x
