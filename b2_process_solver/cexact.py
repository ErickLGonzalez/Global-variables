"""Exact complex (Gaussian-rational) arithmetic and Hermitian PSD
certification -- the structural upgrade B1's exact.py needed.

CF = complex numbers with Fraction real and imaginary parts. All claims in
this module are exact; the certificate class is the same exact-rational
class as B1. Pivots of a Hermitian matrix are real, so the Schur-pivot
standard (G00 > 0, S2 > 0, ...) carries over unchanged.
"""

from fractions import Fraction
from typing import List, Tuple

class CF:
    """Gaussian rational: re + i*im with exact Fraction parts."""
    __slots__ = ("re", "im")

    def __init__(self, re=0, im=0):
        self.re, self.im = Fraction(re), Fraction(im)

    def __add__(a, b): b = _cf(b); return CF(a.re + b.re, a.im + b.im)
    def __sub__(a, b): b = _cf(b); return CF(a.re - b.re, a.im - b.im)
    def __mul__(a, b):
        b = _cf(b)
        return CF(a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re)
    def __truediv__(a, b):
        b = _cf(b)
        d = b.re * b.re + b.im * b.im
        if d == 0:
            raise ZeroDivisionError
        return CF((a.re * b.re + a.im * b.im) / d, (a.im * b.re - a.re * b.im) / d)
    def __neg__(a): return CF(-a.re, -a.im)
    def __eq__(a, b): b = _cf(b); return a.re == b.re and a.im == b.im
    def conj(a): return CF(a.re, -a.im)
    def is_zero(a): return a.re == 0 and a.im == 0
    def __repr__(a): return f"({a.re}{'+' if a.im >= 0 else ''}{a.im}i)"


def _cf(x):
    return x if isinstance(x, CF) else CF(x)


CMat = List[List[CF]]


def dagger(M: CMat) -> CMat:
    n, m = len(M), len(M[0])
    return [[M[j][i].conj() for j in range(n)] for i in range(m)]


def matmul(A: CMat, B: CMat) -> CMat:
    n, k, m = len(A), len(B), len(B[0])
    out = [[CF(0) for _ in range(m)] for _ in range(n)]
    for i in range(n):
        for j in range(m):
            s = CF(0)
            for t in range(k):
                s = s + A[i][t] * B[t][j]
            out[i][j] = s
    return out


def is_hermitian(M: CMat) -> bool:
    n = len(M)
    return all(M[i][j] == M[j][i].conj() for i in range(n) for j in range(n))


def hermitian_psd_certificate(M: CMat) -> Tuple[str, List[Fraction], int]:
    """Exact Hermitian PSD test via complex symmetric (Schur) elimination.

    Valid for Hermitian input: pivots are exact real Fractions; a zero
    diagonal pivot in a PSD matrix forces the entire row/column to vanish,
    so encountering a zero pivot with a nonzero row is an exact witness of
    indefiniteness, as is a negative or non-real diagonal.
    Returns (status, real_pivots, rank).
    """
    n = len(M)
    if not is_hermitian(M):
        return "NOT_HERMITIAN", [], 0
    A = [[CF(M[i][j].re, M[i][j].im) for j in range(n)] for i in range(n)]
    pivots: List[Fraction] = []
    rank = 0
    for k in range(n):
        d = A[k][k]
        if d.im != 0:  # cannot happen for Hermitian input; defensive
            return "NOT_HERMITIAN", pivots, rank
        if d.re < 0:
            pivots.append(d.re)
            return "NOT_PSD_CERTIFIED", pivots, rank
        if d.re == 0:
            if any(not A[k][j].is_zero() for j in range(k + 1, n)):
                pivots.append(Fraction(0))
                return "NOT_PSD_CERTIFIED", pivots, rank
            pivots.append(Fraction(0))
            continue
        pivots.append(d.re)
        rank += 1
        for i in range(k + 1, n):
            if A[i][k].is_zero():
                continue
            f = A[i][k] / d
            for j in range(k, n):
                A[i][j] = A[i][j] - f * A[k][j]
    status = "PD_CERTIFIED" if rank == n else "PSD_CERTIFIED"
    return status, pivots, rank
