"""B1 recovery engine.

Three epistemic outcomes, matching the Discipline Formula:

  FORCED     the hidden quantity is uniquely determined by flatness
             (rank M_t = rank M_{t-1}) -> exact rational value, exact proof.
  PERMITTED  positivity constrains the hidden quantity to an interval;
             bounds are certified from inside (every reported point passes
             the exact PSD certificate) and bracketed from outside.
  REJECTED   the data violate an exact hard constraint (NOT_PSD witness).

Atom extraction (support points and weights of the representing measure)
is numerical-with-audit: roots are found in high precision, then weights
are solved and ALL moments are recomputed and compared against the exact
rationals. The residual bound is reported in the certificate; the
positivity and forcing claims never depend on this numerical step.
"""

from fractions import Fraction
from typing import Dict, List, Optional

import mpmath as mp

from .exact import (
    extend_by_recurrence,
    hankel,
    hankel_rank,
    is_flat,
    kernel_recurrence,
    psd_certificate,
)

mp.mp.dps = 50  # 50-digit working precision for the numerical layer only


def recover_hidden_tail(known: List[Fraction], upto: int) -> Dict:
    """Given a complete prefix m_0..m_{2s} that is PSD and flat, recover all
    moments up to index `upto` as FORCED values, with certificates."""
    known = [Fraction(m) for m in known]
    s = (len(known) - 1) // 2
    M = hankel(known, s)
    status, pivots, rank = psd_certificate(M)
    if status == "NOT_PSD_CERTIFIED":
        return {"status": "REJECTED", "witness_pivots": [str(p) for p in pivots]}
    if not is_flat(known, s):
        return {"status": "NOT_FLAT",
                "detail": f"rank M_{s} != rank M_{s-1}; tail not forced by these data"}
    poly = kernel_recurrence(known, rank)
    full = extend_by_recurrence(known, poly, upto)
    # Audit: extended sequence must remain PSD at every accessible order.
    t_max = len(full) // 2
    aud_status, aud_pivots, aud_rank = psd_certificate(hankel(full, t_max))
    return {
        "status": "FORCED" if aud_status != "NOT_PSD_CERTIFIED" else "REJECTED",
        "rank": rank,
        "recurrence_monic": [str(c) for c in poly],
        "recovered": {str(i): str(full[i]) for i in range(len(known), upto + 1)},
        "schur_pivots_prefix": [str(p) for p in pivots],
        "schur_pivots_extended": [str(p) for p in aud_pivots],
        "extended_rank": aud_rank,
        "full_moments": full,
    }


def permitted_interval(moments_with_hole: List[Optional[Fraction]], hole: int,
                       t: int, refine_bits: int = 48) -> Dict:
    """One hidden moment m_hole inside m_0..m_{2t}. Compute the interval of
    values keeping M_t PSD.

    Method: locate a feasible rational point, then bisect each boundary.
    Guarantee: lo_in and hi_in are certified feasible (exact PSD test);
    lo_out and hi_out are certified infeasible; true boundary lies between.
    """
    ms = list(moments_with_hole)

    def feasible(v: Fraction) -> bool:
        ms[hole] = v
        st, _, _ = psd_certificate(hankel([Fraction(x) for x in ms], t))
        return st != "NOT_PSD_CERTIFIED"

    center = _find_feasible(feasible, ms, hole)
    if center is None:
        return {"status": "REJECTED", "detail": "no feasible value found in scan range"}

    lo_in, lo_out = _bisect_boundary(feasible, center, direction=-1, bits=refine_bits)
    hi_in, hi_out = _bisect_boundary(feasible, center, direction=+1, bits=refine_bits)

    lo_unbounded, hi_unbounded = lo_out is None, hi_out is None
    width = None if (lo_unbounded or hi_unbounded) else hi_in - lo_in
    forced = width == 0
    return {
        "status": "FORCED" if forced else "PERMITTED",
        "certified_inner_interval": [str(lo_in) if not lo_unbounded else "-infinity",
                                     str(hi_in) if not hi_unbounded else "+infinity"],
        "outer_bracket": [str(lo_out) if lo_out is not None else "unbounded",
                          str(hi_out) if hi_out is not None else "unbounded"],
        "inner_width": str(width) if width is not None else "infinite",
        "witness_value": str(center),
        "note": ("top-degree moments are only bounded below by positivity; "
                 "an infinite permitted direction is correct, not an error")
                if (lo_unbounded or hi_unbounded) else "",
    }


def extract_atoms(full_moments: List[Fraction], rank: int) -> Dict:
    """Numerical atom extraction with exact residual audit."""
    poly = kernel_recurrence(full_moments, rank)
    coeffs = [mp.mpf(int(c.numerator)) / mp.mpf(int(c.denominator)) for c in poly]
    roots = mp.polyroots(list(reversed(coeffs)), maxsteps=200, extraprec=100)
    xs = [mp.mpf(r.real) for r in roots]
    # Weights from Vandermonde system  sum_j w_j x_j^i = m_i, i=0..rank-1.
    V = mp.matrix(rank, rank)
    b = mp.matrix(rank, 1)
    for i in range(rank):
        b[i] = mp.mpf(int(full_moments[i].numerator)) / mp.mpf(int(full_moments[i].denominator))
        for j in range(rank):
            V[i, j] = xs[j] ** i
    w = mp.lu_solve(V, b)
    # Exact-vs-numerical residual over ALL known moments.
    resid = mp.mpf(0)
    for i, m in enumerate(full_moments):
        approx = sum(w[j] * xs[j] ** i for j in range(rank))
        exact = mp.mpf(int(m.numerator)) / mp.mpf(int(m.denominator))
        resid = max(resid, abs(approx - exact))
    return {
        "atoms": [{"x": mp.nstr(xs[j], 30), "weight": mp.nstr(w[j], 30)} for j in range(rank)],
        "max_moment_residual": mp.nstr(resid, 5),
        "note": "atoms are numerical-with-audit; positivity/forcing claims are exact and independent of this step",
    }


def _find_feasible(feasible, ms, hole) -> Optional[Fraction]:
    # Scan a coarse dyadic grid around a Hankel-neutral guess.
    guesses = [Fraction(0)]
    for scale_exp in range(0, 24, 2):
        s = Fraction(1, 2 ** scale_exp) if scale_exp else Fraction(1)
        guesses += [s, -s, 3 * s, -3 * s, 10 * s, -10 * s]
    for g in guesses:
        if feasible(g):
            return g
    return None


def _bisect_boundary(feasible, center: Fraction, direction: int, bits: int):
    """Return (last_feasible, first_infeasible) in the given direction."""
    step = Fraction(1)
    inside, outside = center, None
    for _ in range(80):  # expand until infeasible
        cand = center + direction * step
        if feasible(cand):
            inside = cand
            step *= 2
        else:
            outside = cand
            break
    if outside is None:
        return inside, None  # unbounded direction (possible for some holes)
    for _ in range(bits):
        mid = (inside + outside) / 2
        if feasible(mid):
            inside = mid
        else:
            outside = mid
    return inside, outside
