"""Continuum free-field square: vacuum M as an exact Gram matrix.

For the 2D CFT / free-field vacuum on a null interval of width du, B6 gives

    M = (c/6) * [[1, 1/du], [1/du, 1/du^2]] = |v><v|,
    v = sqrt(c/6) * (1, 1/du).

This is a *physical* GNS realization in a 1-dimensional cyclic subspace:
a single (unbounded) operator family whose vacuum matrix elements reproduce
M, with A1 = A0 / du on that subspace (rank-1 saturation).

Wall (2011) / free-field QNEC proofs write the Schur pivot as an L2 norm
||Psi||^2 of an explicit field functional — the continuum completion of
this square. Here we record the exact vacuum Gram and the pivot identity
used as the analytic half of S2; lattice holdouts test whether a single
operator *pair* continues to track M off the vacuum orbit.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict

from b6_qnec.qnec import schur_pivot, vacuum_interval


def vacuum_gram_rank1(c: Fraction, du: Fraction) -> Dict:
    c6, Sp, Q22 = vacuum_interval(c, du)
    # v = sqrt(c/6) * (1, 1/du)  =>  M_ij = v_i v_j
    # Avoid floats: M_ij = (c/6) * u_i u_j with u = (1, 1/du)
    M00 = c6
    M01 = c6 / du
    M11 = c6 / (du * du)
    assert Sp == M01
    assert Q22 == M11
    piv = schur_pivot(c6, Sp, Q22)
    return {
        "c6": str(c6),
        "du": str(du),
        "M": [[str(M00), str(M01)], [str(M01), str(M11)]],
        "vector_u": ["1", str(1 / du)],
        "rank": 1,
        "schur_pivot": str(piv),
        "saturation": piv == 0,
        "operator_relation": "A1 = A0 / du  on the vacuum GNS ray",
    }


def coherent_pivot_split(c: Fraction, du: Fraction, fprime: Fraction) -> Dict:
    """B6 coherent: vacuum rank-1 block + diagonal 2*pi*(f')^2 on the T slot.

    GNS reading: A0 stays on the vacuum ray; A1 acquires an orthogonal
    piece proportional to the classical null-momentum displacement.
    Same operator *definitions* (modular charge vs cut stress) must realize
    that split — tested numerically on the lattice current-carrying proxy.
    """
    vac = vacuum_gram_rank1(c, du)
    return {
        "vacuum_block": vac,
        "extra_A1_norm_squared": f"2*pi*({fprime})^2",
        "interpretation": (
            "coherent excitation enlarges ||A1 Omega|| without changing "
            "||A0 Omega|| or <A0 Omega|A1 Omega> (entropy unchanged)"
        ),
    }
