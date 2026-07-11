"""B8 identifier. Decoding-chain roles: step 5 (candidate structure) with
step 6 gates and the R15-addendum canonicalization rule enforced -- only
similarity-invariant data (spectra) drive classification; no chart-
dependent quantity is consulted.

Epistemics: AMBIGUOUS is a first-class output. Data that cannot separate
weakly-damped from conservative dynamics at the achieved noise floor MUST
NOT be assigned a grammar. Certificate classes: NUMERICAL-DISCOVERY for
the dynamical part (least-squares generator estimate + spectral test),
EXACT-RATIONAL for the quantum part (Choi rank / TP via B2).
"""

import numpy as np


def estimate_generator(trajs, dt):
    """Estimate A via one-step propagator + matrix logarithm:
    z_{k+1} = P z_k (least squares), A = log(P)/dt. Exact for linear flows,
    unlike forward differencing, which injects artificial damping
    ~ dt*omega^2/2 into oscillatory data (an M-layer estimator artifact
    that masquerades as physical dissipation -- recorded in stipulations)."""
    from scipy.linalg import logm
    X, Y = [], []
    for Z in trajs:
        X.append(Z[:-1])
        Y.append(Z[1:])
    X, Y = np.vstack(X), np.vstack(Y)
    P, *_ = np.linalg.lstsq(X, Y, rcond=None)
    P = P.T
    resid = float(np.sqrt(np.mean((X @ P.T - Y) ** 2)))
    A = logm(P).real / dt
    return A, resid


def classify_dynamics(trajs, dt, noise_floor):
    """Return {grammar, spectrum, margins}. Thresholds are set by the
    estimated noise floor on Re(lambda); AMBIGUOUS when the decisive
    quantity sits inside the floor."""
    A, resid = estimate_generator(trajs, dt)
    ev = np.linalg.eigvals(A)
    re, im = ev.real, ev.imag
    tol = noise_floor
    out = {"spectrum": [f"{e:.6f}" for e in ev],
           "fit_residual": resid, "re_tolerance": tol}
    if np.all(np.abs(im) <= tol):                      # purely real spectrum
        if np.all(re < -tol):
            out["grammar"] = "GRADIENT_FLOW"
        else:
            out["grammar"] = "AMBIGUOUS"
            out["reason"] = "real spectrum but sign not resolved above noise"
        return out
    # oscillatory spectrum: decide by damping vs noise floor
    max_abs_re = float(np.max(np.abs(re)))
    if max_abs_re <= tol:
        out["grammar"] = "AMBIGUOUS"
        out["reason"] = ("|Re lambda| <= noise floor: conservative "
                         "(HAMILTONIAN) vs weakly damped (GENERIC) not "
                         "separable from these data")
        out["candidates"] = ["HAMILTONIAN", "GENERIC_MIXED"]
    elif np.all(re < 0):
        out["grammar"] = "GENERIC_MIXED"
        out["damping_margin"] = max_abs_re / tol
    else:
        out["grammar"] = "REJECTED"
        out["reason"] = "positive real part: outside all stable candidate grammars"
    return out


def classify_dynamics_conservative_check(trajs, dt, noise_floor):
    """Second, independent invariant test: candidate conserved quadratic
    Q(z) = z^T S z (SVD direction of minimal variation), then a SLOPE test
    with uncertainty on Q(t) across trajectories.

    Honest verdict structure: exactly-zero damping is never certifiable
    from finite data. Outcomes:
      - relative slope significant (>3 sigma) and negative
            -> GENERIC_MIXED (damping DETECTED below the spectral floor)
      - slope consistent with zero
            -> HAMILTONIAN_WITHIN_BOUND, with certified bound
               |Re lambda| <= (|s| + 3 sigma_s)/2
    The bound is the claim; a true weak damping inside the bound does not
    falsify it."""
    base = classify_dynamics(trajs, dt, noise_floor)
    if base.get("grammar") != "AMBIGUOUS" or \
       "HAMILTONIAN" not in base.get("candidates", []):
        return base
    # conserved-form candidate direction from global SVD
    C = []
    for Z in trajs:
        f = np.stack([Z[:, 0] ** 2, Z[:, 1] ** 2, 2 * Z[:, 0] * Z[:, 1]],
                     axis=1)
        C.append(f - f.mean(axis=0))
    _, _, Vt = np.linalg.svd(np.vstack(C), full_matrices=False)
    v = Vt[-1]
    # canonicalize sign: orient the quadratic form to positive mean value
    # (SVD sign is arbitrary; drift direction is only physical after this)
    allf = np.vstack([np.stack([Z[:, 0] ** 2, Z[:, 1] ** 2,
                                2 * Z[:, 0] * Z[:, 1]], axis=1)
                      for Z in trajs])
    if float(np.mean(allf @ v)) < 0:
        v = -v
    slopes = []
    for Z in trajs:
        f = np.stack([Z[:, 0] ** 2, Z[:, 1] ** 2, 2 * Z[:, 0] * Z[:, 1]],
                     axis=1)
        Q = f @ v
        Qm = np.mean(np.abs(Q))
        if Qm < 1e-12:
            continue
        t = np.arange(len(Q)) * dt
        s_i = np.polyfit(t, Q, 1)[0] / Qm      # relative drift rate
        slopes.append(s_i)
    slopes = np.array(slopes)
    s_mean = float(np.mean(slopes))
    s_err = float(np.std(slopes, ddof=1) / np.sqrt(len(slopes)))
    out = dict(base)
    out["conserved_form_coeffs"] = [f"{c:.4f}" for c in v]
    out["relative_slope"] = s_mean
    out["slope_stderr"] = s_err
    if abs(s_mean) > 3 * s_err and s_mean < 0:
        out["grammar"] = "GENERIC_MIXED"
        out["note"] = ("damping DETECTED by drift test below the spectral "
                       "noise floor (second invariant resolves what the "
                       "spectrum could not)")
        out["implied_Re_lambda"] = s_mean / 2.0
    elif abs(s_mean) > 3 * s_err and s_mean > 0:
        out["grammar"] = "REJECTED"
        out["note"] = "significant growth: outside stable candidate grammars"
    else:
        bound = (abs(s_mean) + 3 * s_err) / 2.0
        out["grammar"] = "HAMILTONIAN_WITHIN_BOUND"
        out["certified_damping_bound"] = bound
        out["note"] = ("conservation certified as a BOUND: |Re lambda| <= "
                       f"{bound:.2e}; exactly-zero damping is never "
                       "certifiable from finite data")
    return out


def classify_quantum(J):
    """EXACT grammar identification for processes (reuses B2)."""
    from b2_process_solver.complete import audit_full
    a = audit_full(J)
    if not a["cptp_certified"]:
        return {"grammar": "NOT_A_CHANNEL", "audit": a}
    if a["rank"] == 1:
        return {"grammar": "UNITARY_GRAMMAR", "audit": a}
    return {"grammar": "DISSIPATIVE_CPTP", "audit": a}
