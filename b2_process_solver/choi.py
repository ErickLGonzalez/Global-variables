"""Exact Choi matrices for qubit channels.

Convention: J(Phi) = sum_{ij} E_ij (x) Phi(E_ij), a 4x4 Hermitian matrix in
blocks -- block (i,j) is the 2x2 matrix Phi(E_ij). Row index = 2*i + a,
column index = 2*j + b, for input indices i,j and output indices a,b.

Choi's theorem:      Phi completely positive  <=>  J(Phi) >= 0.
Trace preservation:  Tr Phi(E_ij) = delta_ij  <=>  Tr_out J = I_in
(block traces: Tr block(i,j) = delta_ij).
"""

from fractions import Fraction
from typing import List

from .cexact import CF, CMat, matmul, dagger


def choi_of_unitary(U: CMat) -> CMat:
    """J for Phi(rho) = U rho U^dagger. Rank-1 (pure Choi state)."""
    J = [[CF(0) for _ in range(4)] for _ in range(4)]
    cols = [[U[a][i] for a in range(2)] for i in range(2)]  # cols[i][a]
    for i in range(2):
        for j in range(2):
            # Phi(E_ij) = (U e_i)(U e_j)^dagger
            for a in range(2):
                for b in range(2):
                    J[2 * i + a][2 * j + b] = cols[i][a] * cols[j][b].conj()
    return J


def mix(channels_weights) -> CMat:
    """Convex mixture of Choi matrices: J = sum_k p_k J_k (exact)."""
    J = [[CF(0) for _ in range(4)] for _ in range(4)]
    for Jk, p in channels_weights:
        p = Fraction(p)
        for r in range(4):
            for c in range(4):
                J[r][c] = J[r][c] + Jk[r][c] * CF(p)
    return J


def block_traces(J: CMat):
    """(Tr_out J)_{ij} = Tr block(i,j); TP <=> equals identity."""
    return [[J[2 * i + 0][2 * j + 0] + J[2 * i + 1][2 * j + 1]
             for j in range(2)] for i in range(2)]


def is_trace_preserving(J: CMat) -> bool:
    T = block_traces(J)
    return (T[0][0] == CF(1) and T[1][1] == CF(1)
            and T[0][1].is_zero() and T[1][0].is_zero())


# --- standard exact channels ---------------------------------------------

def identity_channel() -> CMat:
    I = [[CF(1), CF(0)], [CF(0), CF(1)]]
    return choi_of_unitary(I)


def z_channel() -> CMat:
    Z = [[CF(1), CF(0)], [CF(0), CF(-1)]]
    return choi_of_unitary(Z)


def pythagorean_unitary() -> CMat:
    """U = [[3/5, 4i/5], [4i/5, 3/5]] -- exactly unitary over Gaussian
    rationals (3-4-5 triple), with genuinely complex Choi entries."""
    U = [[CF(Fraction(3, 5)), CF(0, Fraction(4, 5))],
         [CF(0, Fraction(4, 5)), CF(Fraction(3, 5))]]
    UdU = matmul(dagger(U), U)
    assert UdU[0][0] == CF(1) and UdU[1][1] == CF(1) \
        and UdU[0][1].is_zero() and UdU[1][0].is_zero()
    return choi_of_unitary(U)
