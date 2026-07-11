"""B2 completion engine: recover hidden Choi-matrix entries under stacked
restraints, with the same FORCED / PERMITTED / REJECTED epistemics as B1.

Restraint stacking is the point of this benchmark:
  PSD alone            -> hidden entries typically PERMITTED (interval/disk)
  PSD + TP             -> some entries collapse to FORCED (exact linear)
  PSD + rank condition -> off-diagonals collapse to FORCED (flat-extension
                          analogue: rank-1 Choi <=> pure process)
Adding a restraint column shrinks the feasible set -- the atlas mechanism
demonstrated on a finite-dimensional quantum process.
"""

from fractions import Fraction
from typing import Dict, Optional, Tuple

from .cexact import CF, CMat, hermitian_psd_certificate
from .choi import block_traces


def force_by_tp(J_partial: CMat, hidden: Tuple[int, int]) -> Optional[Dict]:
    """If the hidden entry sits on a block diagonal used by a TP condition
    and is the only unknown there, it is FORCED by exact linear algebra."""
    r, c = hidden
    i, a = divmod(r, 2)
    j, b = divmod(c, 2)
    if a != b:
        return None  # entry does not appear in any block trace
    partner = (2 * i + (1 - a), 2 * j + (1 - a))
    target = CF(1) if i == j else CF(0)
    known = J_partial[partner[0]][partner[1]]
    if known is None:
        return None
    forced = target - known
    return {"status": "FORCED", "mechanism": "trace-preservation (exact linear)",
            "value": repr(forced), "_cf": forced}


def force_by_rank1(J_partial: CMat, hidden: Tuple[int, int]) -> Optional[Dict]:
    """Rank-1 (pure-process) forcing: J[r][c] = J[r][k] J[k][c] / J[k][k]
    for any reference k with J[k][k] > 0 and required entries known.
    The finite-dimensional analogue of B1's flat-extension recurrence."""
    r, c = hidden
    for k in range(4):
        if k in (r, c):
            continue
        d, x, y = J_partial[k][k], J_partial[r][k], J_partial[k][c]
        if d is None or x is None or y is None:
            continue
        if d.im != 0 or d.re <= 0:
            continue
        forced = x * y / d
        return {"status": "FORCED",
                "mechanism": f"rank-1 completion via pivot k={k} "
                             "(flat-extension analogue)",
                "value": repr(forced), "_cf": forced}
    return None


def permitted_interval_diag(J_partial: CMat, hidden_diag: int,
                            refine_bits: int = 48) -> Dict:
    """Hidden REAL diagonal entry under PSD alone: certified interval by
    exact bisection (inner points certified feasible, outer certified
    infeasible)."""
    def feasible(v: Fraction) -> bool:
        M = [[J_partial[i][j] if (i, j) != (hidden_diag, hidden_diag)
              else CF(v) for j in range(4)] for i in range(4)]
        st, _, _ = hermitian_psd_certificate(M)
        return st in ("PSD_CERTIFIED", "PD_CERTIFIED")

    center = next((Fraction(g) for g in
                   [0, 1, Fraction(1, 2), 2, Fraction(1, 4), 4, 8]
                   if feasible(Fraction(g))), None)
    if center is None:
        return {"status": "REJECTED", "detail": "no feasible value found"}

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
    width = None if hi_out is None or lo_out is None else hi_in - lo_in
    return {"status": "PERMITTED" if (width is None or width > 0) else "FORCED",
            "certified_inner_interval": [str(lo_in),
                                         str(hi_in) if hi_out is not None else "+infinity"],
            "inner_width": str(width) if width is not None else "infinite",
            "witness_value": str(center)}


def audit_full(J: CMat) -> Dict:
    st, piv, rank = hermitian_psd_certificate(J)
    T = block_traces(J)
    tp = (T[0][0] == CF(1) and T[1][1] == CF(1)
          and T[0][1].is_zero() and T[1][0].is_zero())
    return {"psd_status": st, "schur_pivots": [str(p) for p in piv],
            "rank": rank, "trace_preserving": tp,
            "cptp_certified": st in ("PSD_CERTIFIED", "PD_CERTIFIED") and tp}
