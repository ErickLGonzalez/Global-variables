"""S2 lattice-QNEC layer: the B6 matrix populated by an actual quantum
system.

For a static (equal-time) interval of length l, both chiralities
contribute, so the continuum predictions are the SPATIAL forms of B6:

  vacuum:   S(l) = (c/3) ln l + k0
            => saturation identity   Q(l) := S'' + (3/c)(S')^2  ->  0
  thermal:  S(l) = (c/3) ln[(beta/pi) sinh(pi l / beta)] + k0
            => Q(l) = c pi^2 / (3 beta^2) = 2 pi * e(beta),
            the ENERGY DENSITY -- QNEC saturation with T != 0, verified
            from microscopic correlation data with no CFT input beyond c.

This is B6's exact continuum result (vacuum rank-1 boundary; thermal
coth identity) recovered from a microscopic model: the matrix
M_lat = [[c/3, S'], [S', Q - S'' ...]] structure is populated by data,
not postulated.

Stipulations: finite differences in l (step 2, central), lattice-to-
continuum matching at half filling (v_F = 1), UV constant k0 dropped by
differentiation, weak parity oscillations averaged by the step choice.
"""

import numpy as np

from .gaussian import ground_state_C, thermal_C, entropy


def S_of_l(C_full, lmin, lmax, step=1):
    ls = np.arange(lmin, lmax + 1, step)
    return ls, np.array([entropy(C_full[:l, :l]) for l in ls])


def derivatives(ls, S, h=2):
    """Central differences on the entropy curve at interior points."""
    out = []
    lset = {int(l): i for i, l in enumerate(ls)}
    for l in ls:
        l = int(l)
        if (l - h) in lset and (l + h) in lset:
            Sp = (S[lset[l + h]] - S[lset[l - h]]) / (2 * h)
            Spp = (S[lset[l + h]] - 2 * S[lset[l]] + S[lset[l - h]]) / h ** 2
            out.append((l, Sp, Spp))
    return out


def central_charge_fit(ls, S):
    """Fit S = (c/3) ln l + k0 over the window."""
    A = np.stack([np.log(ls), np.ones_like(ls, float)], axis=1)
    coef, *_ = np.linalg.lstsq(A, S, rcond=None)
    return 3.0 * coef[0]


def vacuum_saturation_report(lmax=64):
    C = ground_state_C(lmax + 4)
    ls, S = S_of_l(C, 8, lmax)
    c_fit = central_charge_fit(ls[8:], S[8:])
    rows = []
    for l, Sp, Spp in derivatives(ls, S):
        Q = Spp + (3.0 / c_fit) * Sp ** 2
        rows.append({"l": l, "Sp": Sp, "Spp": Spp, "Q": Q,
                     "Q_over_Spp": abs(Q) / abs(Spp)})
    return c_fit, rows


def thermal_identity_report(beta=16.0, lmin=10, lmax=30):
    C = thermal_C(lmax + 4, beta)
    ls, S = S_of_l(C, lmin - 2, lmax + 2)
    c = 1.0  # Dirac; independently confirmed by the vacuum fit
    pred = c * np.pi ** 2 / (3.0 * beta ** 2)
    rows = []
    for l, Sp, Spp in derivatives(ls, S):
        Q = Spp + (3.0 / c) * Sp ** 2
        rows.append({"l": l, "Q": Q, "prediction_2pi_e": pred,
                     "rel_dev": abs(Q - pred) / pred})
    return pred, rows
