"""S3: PDG empirical layer for B5 -- one alpha_s across channels & scales.

B5 certified (pseudo-data) that factorization forces ONE coupling across
channels. S3 confronts that with reality: independent alpha_s extractions
at scales spanning m_tau = 1.777 GeV to M_Z = 91.19 GeV (a 51x span) must
be mutually consistent under 2-loop RG evolution with flavor-threshold
matching -- d_identifiable = 1 across four measurement classes -- while
the no-running null is REJECTED (asymptotic freedom certified from data).

DATA (verified 2026-07-14 vs PDG-lineage sources; re-verify before any
promotion decision):
  tau hadronic decays:  alpha_s(m_tau = 1.777) = 0.312 +/- 0.015
  EW fit (Z pole):      alpha_s(M_Z) = 0.1194 +/- 0.0029
  lattice QCD:          alpha_s(M_Z) = 0.1188 +/- 0.0011
  ttbar cross-sections: alpha_s(M_Z) = 0.1177 +/- 0.0035
  world average (reference only, NOT an input): 0.1180 +/- 0.0009

RG: mu^2 d(alpha)/d(mu^2) = -alpha^2 (b0 + b1 alpha),
    b0 = (33 - 2 nf)/(12 pi),  b1 = (153 - 19 nf)/(24 pi^2),
thresholds at m_b = 4.18 (nf 4->5); m_tau sits above m_c, so nf = 4 there.
Stipulations: 2-loop truncation (evolution error << data errors at this
precision -- checked in T1), MS-bar scheme throughout, matching by
continuity at mu = m_b.
"""

import numpy as np

MB = 4.18
MTAU = 1.777
MZ = 91.1876

DATA = [
    {"name": "tau_decays", "mu": MTAU, "alpha": 0.312, "err": 0.015},
    {"name": "EW_fit_Z", "mu": MZ, "alpha": 0.1194, "err": 0.0029},
    {"name": "lattice", "mu": MZ, "alpha": 0.1188, "err": 0.0011},
    {"name": "ttbar", "mu": MZ, "alpha": 0.1177, "err": 0.0035},
]
WORLD_AVG = (0.1180, 0.0009)


def beta_coeffs(nf):
    b0 = (33 - 2 * nf) / (12 * np.pi)
    b1 = (153 - 19 * nf) / (24 * np.pi ** 2)
    return b0, b1


def _rk4_segment(alpha, t0, t1, nf, n=400):
    """Integrate d(alpha)/dt = -alpha^2 (b0 + b1 alpha), t = ln mu^2."""
    b0, b1 = beta_coeffs(nf)
    h = (t1 - t0) / n
    a = alpha
    f = lambda a: -a * a * (b0 + b1 * a)
    for _ in range(n):
        k1 = f(a); k2 = f(a + h * k1 / 2)
        k3 = f(a + h * k2 / 2); k4 = f(a + h * k3)
        a += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return a


def evolve(alpha, mu_from, mu_to, match_threshold=True):
    """Evolve alpha_s between scales, crossing m_b with nf 4<->5 matching
    by continuity. match_threshold=False deliberately IGNORES the flavor
    change (the T5 stipulation probe)."""
    t = lambda mu: np.log(mu ** 2)
    up = mu_to > mu_from
    segs = []
    if match_threshold and (mu_from < MB < mu_to or mu_to < MB < mu_from):
        segs = [(mu_from, MB, 4 if up else 5), (MB, mu_to, 5 if up else 4)]
    else:
        nf = 4 if max(mu_from, mu_to) <= MB else (5 if min(mu_from, mu_to) >= MB
                                                  else (4 if not match_threshold else 5))
        segs = [(mu_from, mu_to, nf)]
    a = alpha
    for m0, m1, nf in segs:
        a = _rk4_segment(a, t(m0), t(m1), nf)
    return a


def evolved_to_MZ(entry, match_threshold=True):
    """Central value and propagated error (evolve the +/-1 sigma ends)."""
    c = evolve(entry["alpha"], entry["mu"], MZ, match_threshold)
    hi = evolve(entry["alpha"] + entry["err"], entry["mu"], MZ, match_threshold)
    lo = evolve(entry["alpha"] - entry["err"], entry["mu"], MZ, match_threshold)
    return c, (hi - lo) / 2


def combine(values):
    """Inverse-variance weighted mean + chi^2/dof against the mean."""
    v = np.array([x[0] for x in values])
    e = np.array([x[1] for x in values])
    w = 1 / e ** 2
    mean = float(np.sum(w * v) / np.sum(w))
    err = float(1 / np.sqrt(np.sum(w)))
    chi2 = float(np.sum(w * (v - mean) ** 2))
    return mean, err, chi2, len(v) - 1
