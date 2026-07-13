"""S4: ?7 toy -- rank saturation of static-patch dS2 Gram matrices.

PHYSICS OF THE TOY (free-field tier; the entropy here is the FIELD's, not
gravitational -- recorded stipulation):
  - dS2 static patch, massless/conformal matter: Bunch-Davies restricted
    to the patch = THERMAL state at the Gibbons-Hawking temperature
    T = 1/(2 pi l) in the tortoise coordinate (conformal map). Lattice
    realization: the free Dirac chain thermal state at beta = 2 pi l
    (machinery from s2_gns, accelerated here).
  - The horizon enters as the observer's REDSHIFT weight on observables:
    Omega(x) = 1/cosh((x - x0)/l)  (= sqrt(g_00) in tortoise coords).
    Accessible observables A_x = Omega(x) c_x; their Gram matrix is
        G = D C D,   D = diag(Omega),   C = thermal correlations.

?7-TOY PREDICTIONS:
  weak:   r_eps(W) = #{eigenvalues of G > eps * max} SATURATES as the
          window W grows -- the horizon caps the accessible rank.
          Control/falsifier: WITHOUT the redshift weight, rank grows
          unboundedly with W (saturation is a horizon effect).
  2D signature: the saturated rank is (approximately) l-INDEPENDENT --
          nontrivial and correct: a dS2 horizon is a point, its entropy
          does not scale with l. [Accessible window ~ 2 l ln(1/eps);
          distinguishable-mode density ~ T = 1/(2 pi l); product: l drops.]
  strong: r_eps tracks the entanglement entropy of the eps-accessible
          window (rank ~ entropy, the flat-extension reading of ?7).
"""

import numpy as np


def thermal_kernel_fast(L, beta, Mk=16384):
    """C(r) = (1/2pi) int dk cos(kr) / (1 + e^{-beta cos k}), vectorized."""
    k = np.linspace(-np.pi, np.pi, Mk, endpoint=False)
    f = 1.0 / (1.0 + np.exp(-beta * np.cos(k)))
    r = np.arange(L)
    cosmat = np.cos(np.outer(r, k))
    Cr = cosmat @ f * (2 * np.pi / Mk) / (2 * np.pi)
    idx = np.arange(L)
    return Cr[np.abs(idx[:, None] - idx[None, :])]


def redshift_profile(W, ell):
    x = np.arange(W) - (W - 1) / 2.0
    return 1.0 / np.cosh(x / ell)


def weighted_gram(C_W, ell, weighted=True):
    W = C_W.shape[0]
    if not weighted:
        return C_W
    D = redshift_profile(W, ell)
    return (D[:, None] * C_W) * D[None, :]


def effective_rank(G, eps):
    lam = np.linalg.eigvalsh(G)
    lam = lam[lam > 0]
    return int(np.sum(lam > eps * lam.max()))


def saturation_curve(beta, ell, Ws, eps, weighted=True, Mk=16384):
    out = []
    C = thermal_kernel_fast(max(Ws), beta, Mk)
    for W in Ws:
        G = weighted_gram(C[:W, :W], ell, weighted)
        out.append(effective_rank(G, eps))
    return out


def compression_certificate(G, r):
    """B1-tie-in: compress G to its top-r eigenspace; report the maximum
    entrywise error -- 'all further Gram entries are FORCED by the rank-r
    description to this tolerance' (the flat-extension reading)."""
    lam, U = np.linalg.eigh(G)
    order = np.argsort(lam)[::-1]
    lam, U = lam[order], U[:, order]
    Gr = (U[:, :r] * lam[:r]) @ U[:, :r].T
    return float(np.max(np.abs(G - Gr)) / np.max(np.abs(G)))


def precision_audit(beta, ell, W, eps, Mk=16384):
    """Quarantine audit: k-grid doubling must leave r_eps unchanged."""
    r1 = effective_rank(weighted_gram(
        thermal_kernel_fast(W, beta, Mk)[:W, :W], ell), eps)
    r2 = effective_rank(weighted_gram(
        thermal_kernel_fast(W, beta, 2 * Mk)[:W, :W], ell), eps)
    return r1, r2
