"""B10: continuous-variable Gaussian-channel completion (exact class).

A Gaussian channel acts on covariance matrices as  V -> T V T^t + N.
Convention: vacuum covariance = I/2, symplectic form Omega = [[0,1],[-1,0]]
per mode (direct sum for N modes). Complete positivity (the CV Choi
condition, Caruso-Eisert-Giovannetti-Holevo lineage):

    M_CP := N + (i/2) (Omega - T Omega T^t)  >= 0   (Hermitian PSD)

With rational (T, N), M_CP is a GAUSSIAN-RATIONAL Hermitian matrix, so
B2's exact certificate applies verbatim -- the CV layer inherits the
exact-rational class for free.

Physics delivered as matrix items (huge-payoff freebies of the formalism):
  - quantum-limited attenuator/amplifier noise saturates M_CP >= 0 with
    RANK DEFICIENCY: quantum-limited channels live on the flat boundary
    (same structure as B1 flat extension, B6 QNEC saturation, S2 vacuum).
  - the Caves amplifier bound N >= (g^2-1)/2 is a FORCED matrix item:
    positivity + symplectic structure alone force amplifier noise.

Restraint stacking (the benchmark pattern):
  CP alone                  -> hidden noise entries PERMITTED (intervals)
  CP + unitary hypothesis   -> N = 0 and T symplectic: hidden T entries
                               FORCED by T Omega T^t = Omega (exact linear
                               /quadratic relations)
"""

from fractions import Fraction
from typing import Dict, List, Optional, Tuple

from b2_process_solver.cexact import CF, hermitian_psd_certificate

Rat = Fraction


def omega(n_modes: int) -> List[List[Fraction]]:
    N = 2 * n_modes
    O = [[Fraction(0)] * N for _ in range(N)]
    for m in range(n_modes):
        O[2 * m][2 * m + 1] = Fraction(1)
        O[2 * m + 1][2 * m] = Fraction(-1)
    return O


def matmul_r(A, B):
    n, k, m = len(A), len(B), len(B[0])
    return [[sum(A[i][t] * B[t][j] for t in range(k)) for j in range(m)]
            for i in range(n)]


def transpose(A):
    return [list(row) for row in zip(*A)]


def cp_matrix(T, N) -> List[List[CF]]:
    """M_CP = N + (i/2)(Omega - T Omega T^t), exact Gaussian-rational."""
    n = len(N)
    O = omega(n // 2)
    TOTt = matmul_r(matmul_r(T, O), transpose(T))
    return [[CF(N[i][j], Fraction(O[i][j] - TOTt[i][j], 1) / 2)
             for j in range(n)] for i in range(n)]


def certify_channel(T, N) -> Dict:
    st, piv, rank = hermitian_psd_certificate(cp_matrix(T, N))
    if st == "NOT_PSD_CERTIFIED":
        verdict = "NOT_A_CHANNEL (CP violated; exact witness)"
    elif rank < len(N):
        verdict = "QUANTUM_LIMITED (CP saturated: flat boundary)"
    else:
        verdict = "CHANNEL_CP_CERTIFIED (strictly inside)"
    return {"status": st, "pivots": [str(p) for p in piv],
            "rank": rank, "verdict": verdict}


def permitted_noise_interval(T, N_partial, hole: Tuple[int, int],
                             refine_bits: int = 48) -> Dict:
    """Hidden real diagonal noise entry under CP alone: certified interval
    by exact bisection (B1/B2 pattern)."""
    i, j = hole
    assert i == j, "demo covers diagonal holes"
    N = [row[:] for row in N_partial]

    def feasible(v: Fraction) -> bool:
        N[i][i] = v
        st, _, _ = hermitian_psd_certificate(cp_matrix(T, N))
        return st != "NOT_PSD_CERTIFIED"

    center = next((Fraction(g) for g in
                   [1, 2, Fraction(1, 2), 4, 8, 16] if feasible(Fraction(g))),
                  None)
    if center is None:
        return {"status": "REJECTED"}

    def bisect(direction):
        step, inside, outside = Fraction(1), center, None
        for _ in range(80):
            cand = center + direction * step
            if feasible(cand):
                inside, step = cand, 2 * step
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
    return {"status": "PERMITTED",
            "certified_inner_interval": [str(lo_in),
                                         str(hi_in) if hi_out is not None
                                         else "+infinity"],
            "witness": str(center)}


def force_symplectic_entry(T_partial, hole: Tuple[int, int]) -> Optional[Dict]:
    """Unitary (N = 0) hypothesis: T must satisfy T Omega T^t = Omega.
    For a single-mode T = [[a,b],[c,d]] this is det T = ad - bc = 1;
    one hidden entry is FORCED exactly by the others."""
    a, b = T_partial[0]
    c, d = T_partial[1]
    known = {(0, 0): a, (0, 1): b, (1, 0): c, (1, 1): d}
    known.pop(hole)
    vals = {k: Fraction(v) for k, v in known.items()}
    try:
        if hole == (0, 0):
            forced = (1 + vals[(0, 1)] * vals[(1, 0)]) / vals[(1, 1)]
        elif hole == (0, 1):
            forced = (vals[(0, 0)] * vals[(1, 1)] - 1) / vals[(1, 0)]
        elif hole == (1, 0):
            forced = (vals[(0, 0)] * vals[(1, 1)] - 1) / vals[(0, 1)]
        else:
            forced = (1 + vals[(0, 1)] * vals[(1, 0)]) / vals[(0, 0)]
    except ZeroDivisionError:
        return None
    return {"status": "FORCED",
            "mechanism": "symplectic condition det T = 1 (exact)",
            "value": str(forced), "_frac": forced}
