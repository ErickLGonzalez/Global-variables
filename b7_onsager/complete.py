"""B7 completion engine: Onsager transport matrix under stacked restraints.

Restraint stacking (atlas mechanism on effective-coefficient type):
  L ⪰ 0 alone              → hidden entries typically PERMITTED (interval)
  L ⪰ 0 + L = Lᵀ           → off-diagonals FORCED (exact reciprocity)
  σ = Xᵀ L X < 0 witness   → REJECTED (second-law violation)
  L ≠ Lᵀ (no B field)      → REJECTED (reciprocity violation)
"""

from fractions import Fraction
from typing import Dict, List, Optional, Tuple

from b2_process_solver.cexact import CF, hermitian_psd_certificate

from .exact import Mat, fmt, q


def as_cf(M: Mat) -> List[List[CF]]:
    n = len(M)
    out = [[CF(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if M[i][j] is None:
                raise ValueError("incomplete matrix")
            out[i][j] = CF(q(M[i][j]))
    return out


def psd_certify(L: List[List[Fraction]]) -> Dict:
    status, pivots, rank = hermitian_psd_certificate(as_cf(L))
    return {
        "psd_status": status,
        "schur_pivots": [str(p) for p in pivots],
        "rank": rank,
        "psd_certified": status in ("PSD_CERTIFIED", "PD_CERTIFIED"),
    }


def is_symmetric(L: List[List[Fraction]]) -> bool:
    n = len(L)
    return all(L[i][j] == L[j][i] for i in range(n) for j in range(n))


def force_by_reciprocity(M: Mat, hidden: Tuple[int, int]) -> Optional[Dict]:
    """If the partner entry is known, reciprocity FORCES the hidden one."""
    i, j = hidden
    if i == j:
        return None
    partner = M[j][i]
    if partner is None:
        return None
    return {
        "status": "FORCED",
        "mechanism": "Onsager reciprocity L_ij = L_ji (microscopic reversibility)",
        "value": fmt(partner),
        "_frac": q(partner),
    }


def permitted_offdiag(M: Mat, hidden: Tuple[int, int],
                      refine_bits: int = 48) -> Dict:
    """Hidden off-diagonal under PSD alone (no reciprocity yet).

    For a 2×2 [[a, x],[x, b]] with a,b known and SPD-feasible, the PSD
    condition is x² ≤ a b, so x ∈ [-√(ab), +√(ab)] when ab is a perfect
    square in Q; otherwise we certify an exact rational inner interval
    by bisection and report outer witnesses.
    """
    i, j = hidden
    n = len(M)

    def with_value(v: Fraction) -> Mat:
        N = [[M[r][c] for c in range(n)] for r in range(n)]
        N[i][j] = v
        # under PSD alone without reciprocity, the partner may also be free;
        # for the thermoelectric 2×2 we set the partner equal when testing
        # a candidate (symmetric trial) OR leave known partner.
        if N[j][i] is None:
            N[j][i] = v
        return N

    def feasible(v: Fraction) -> bool:
        try:
            st = psd_certify([[q(x) for x in row] for row in with_value(v)])
        except Exception:
            return False
        return st["psd_certified"]

    # find a feasible center
    center = None
    for g in [0, 1, Fraction(1, 2), -1, Fraction(-1, 2), 2, -2]:
        if feasible(q(g)):
            center = q(g)
            break
    if center is None:
        return {"status": "REJECTED", "detail": "no feasible value under PSD"}

    def bisect(direction):
        step, inside, outside = Fraction(1), center, None
        for _ in range(80):
            cand = center + direction * step
            if feasible(cand):
                inside, step = cand, step * 2
            else:
                outside = cand
                break
        if outside is None:
            return inside, None
        for _ in range(refine_bits):
            mid = (inside + outside) / 2
            if feasible(mid):
                inside = mid
            else:
                outside = mid
        return inside, outside

    lo_in, lo_out = bisect(-1)
    hi_in, hi_out = bisect(+1)
    return {
        "status": "PERMITTED",
        "certified_inner_interval": [
            fmt(lo_in),
            fmt(hi_in) if hi_out is not None else "+infinity",
        ],
        "mechanism": "PSD alone (L ⪰ 0 / second law); reciprocity not yet applied",
        "witness_value": fmt(center),
    }


def entropy_production(L: List[List[Fraction]], X: List[Fraction]) -> Fraction:
    """σ = Xᵀ L X."""
    n = len(L)
    LX = [sum(L[i][j] * X[j] for j in range(n)) for i in range(n)]
    return sum(X[i] * LX[i] for i in range(n))


def audit_full(L: List[List[Fraction]]) -> Dict:
    psd = psd_certify(L)
    return {
        **psd,
        "symmetric": is_symmetric(L),
        "onsager_certified": psd["psd_certified"] and is_symmetric(L),
    }
