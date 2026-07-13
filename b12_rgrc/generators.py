"""B12-RGRC generators -- six rival explanations for 'two systems look
related', each a data-generating family with ground truth known to the
test harness and hidden from the engine.

F1  GENUINE_SHARED_LATENT: one latent OU process z(t) drives BOTH systems'
    dynamics (dx_i = -a_i x_i dt + b_i z dt + s_i dW_i). Cross-structure
    is dynamical (colored, filtered through both responses).
F2  SHARED_CALIBRATION_ARTIFACT: independent systems; both READOUTS are
    multiplied by a common slow drift (1 + g c(t)). Linear cross-corr ~ 0
    but envelopes co-vary -- apparatus, not physics.
F3  INDEPENDENT: nothing shared.
F4  SHARED_MATHEMATICS_ONLY: independent noise, IDENTICAL dynamics
    parameters -- same grammar/spectrum, zero cross-covariance. The trap
    the central thesis must not fall into: same math != shared latent.
F5  SHARED_SENSOR_COMMON_MODE: independent dynamics; a common WHITE noise
    added to both readouts -- delta-like cross-corr at lag 0, no
    dynamical filtering.
F6  DIRECT_COUPLING: no latent; the systems couple directly and
    symmetrically (dx1 gets +k x2, dx2 gets +k x1). Passively this can
    mimic F1 (colored cross-corr); interventions separate them.

Intervention metadata (when provided): a training segment where a known
handle is actuated -- for F1 a latent-mean shift delta0 (both systems
respond); for F6/others a CLAMP of system 1 (x1 held at 0). Under
do(clamp x1): F1 leaves system 2's statistics unchanged (z still drives
it); F6 changes them (the x1 drive is removed). That asymmetry is the
causal discriminator passive data cannot supply.
"""

import numpy as np

DT = 0.05
N_STEPS = 60_000


def _ou_step(x, a, drive, s, dt, rng):
    return x + (-a * x + drive) * dt + s * np.sqrt(dt) * rng.standard_normal()


def simulate(family, seed=0, interventions=True, params=None):
    rng = np.random.default_rng(seed)
    p = {"a1": 1.0, "a2": 1.4, "b1": 1.0, "b2": 0.8, "s": 0.35,
         "az": 0.5, "sz": 0.6, "gcal": 0.9, "scm": 0.5, "k": 0.55}
    if params:
        p.update(params)
    n = N_STEPS
    x1 = x2 = z = c = 0.0
    Y1, Y2 = np.empty(n), np.empty(n)
    # intervention windows: [i0, i1) latent-shift (F1) or clamp-x1 (all)
    shift_win = (int(0.60 * n), int(0.70 * n))
    clamp_win = (int(0.80 * n), int(0.90 * n))
    delta0 = 1.2
    meta = {"family_hidden": family,
            "interventions": ({"latent_proxy_shift":
                               {"window": shift_win, "delta": delta0},
                               "clamp_system1": {"window": clamp_win}}
                              if interventions else None)}
    for i in range(n):
        in_shift = interventions and shift_win[0] <= i < shift_win[1]
        in_clamp = interventions and clamp_win[0] <= i < clamp_win[1]
        z = _ou_step(z, p["az"], p["az"] * delta0 if in_shift else 0.0,
                     p["sz"], DT, rng)
        c = _ou_step(c, 0.05, 0.0, 0.15, DT, rng)
        if family == "F1":
            d1, d2 = p["b1"] * z, p["b2"] * z
        elif family == "F6":
            d1, d2 = p["k"] * x2, p["k"] * x1
        else:
            d1 = d2 = 0.0
        x1 = 0.0 if in_clamp else _ou_step(x1, p["a1"], d1, p["s"], DT, rng)
        x2 = _ou_step(x2, p["a2"], d2, p["s"], DT, rng)
        y1, y2 = x1, x2
        if family == "F2":
            y1, y2 = (1 + p["gcal"] * c) * x1, (1 + p["gcal"] * c) * x2
        if family == "F5":
            w = p["scm"] * rng.standard_normal()
            y1, y2 = x1 + w, x2 + w
        Y1[i], Y2[i] = y1, y2
    return Y1, Y2, meta
