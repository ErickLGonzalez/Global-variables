"""B9 estimator pipeline -- the Nobel decompilation recipe as code.

Estimator chain (ledger R16-R20; equilibrium-point identity):

    J_b = -(M + W) H_V   at an equilibrium (grad V = 0)
    =>  K := M + W = -J_b H_V^{-1}
    =>  M = (K + K^T)/2   (PSD-checked),   W = (K - K^T)/2.

TWO calibration routes for H_V, with different epistemic power:
  SPECTROSCOPY route: H_V supplied by an independent measurement channel
      (resonance curvature -- the Berkeley method). Breaks the
      noise/potential degeneracy: effective-temperature fraud is
      DETECTABLE by the FDT audit.
  GIBBS route: H_V = k_B T Sigma^{-1} from the stationary covariance of
      the SAME trajectories. Self-consistent by construction -- an
      inflated sigma silently rescales the inferred potential and FDT
      appears satisfied. The Voss-Webb ambiguity, reproduced exactly.
The pipeline therefore records which route produced H_V in every
certificate; Gibbs-route FDT consistency is NEVER promotable evidence.

FDT audit: D_hat (increment covariance / dt) vs 2 k_B T M_hat;
relative residual > threshold => EQUILIBRIUM_REJECTED (hidden bath,
non-equilibrium environment, wrong temperature claim, or missing state
variables -- the historical precursor ambiguity, now a gate).
"""

import numpy as np
from scipy.linalg import logm


def estimate_generator(Z, dt):
    X, Y = Z[:-1], Z[1:]
    P, *_ = np.linalg.lstsq(X, Y, rcond=None)
    P = P.T
    return logm(P).real / dt


def increment_covariance(Z, dt, A_hat):
    from scipy.linalg import expm
    P = expm(A_hat * dt)
    resid = Z[1:] - Z[:-1] @ P.T
    return (resid.T @ resid) / (len(resid) * dt)


def decompile(Z, dt, T, H_V=None):
    """Full pipeline. H_V=None -> Gibbs route (flagged); else spectroscopy
    route with the supplied independent curvature."""
    A_hat = estimate_generator(Z, dt)
    if H_V is None:
        Sig = np.cov(Z.T)
        H_V_used = T * np.linalg.inv(Sig)
        route = "GIBBS (self-consistent; NOT promotable evidence)"
    else:
        H_V_used = np.asarray(H_V, float)
        route = "SPECTROSCOPY (independent calibration channel)"
    K = -A_hat @ np.linalg.inv(H_V_used)
    M_hat = (K + K.T) / 2
    W_hat = (K - K.T) / 2
    ev = np.linalg.eigvalsh(M_hat)
    psd_ok = bool(ev.min() > -1e-3 * max(1.0, ev.max()))
    D_hat = increment_covariance(Z, dt, A_hat)
    target = 2.0 * T * M_hat
    scale = max(np.linalg.norm(target), np.linalg.norm(D_hat), 1e-12)
    fdt_resid = float(np.linalg.norm(D_hat - target) / scale)
    return {"A_hat": A_hat, "M_hat": M_hat, "W_hat": W_hat,
            "M_psd_ok": psd_ok, "D_hat": D_hat,
            "fdt_relative_residual": fdt_resid,
            "calibration_route": route,
            "fdt_verdict": ("EQUILIBRIUM_CONSISTENT" if fdt_resid < 0.15
                            else "EQUILIBRIUM_REJECTED (hidden bath / "
                                 "non-equilibrium / wrong T / missing "
                                 "state variables)")}
