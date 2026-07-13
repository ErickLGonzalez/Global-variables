"""B12-RGRC engine: blind classification of WHY two systems look related.

The engine sees only (Y1, Y2) and, when provided, intervention metadata
(window locations and the actuated handle -- never the family label).

Feature stack:
  r(tau)      normalized cross-correlation over lags (baseline segment)
  peakiness   |r(0)| vs |r(tau>0)| decay -- delta-like => sensor common
              mode; colored => dynamical cross-structure
  env_corr    correlation of local variance envelopes -- multiplicative
              calibration signature when linear r ~ 0
  spec_match  per-system generator timescales (lag-1 regression) --
              identical spectra with zero cross-corr => shared math only
  clamp test  do(clamp x1): compare system 2's baseline vs clamped
              statistics -- unchanged => latent-driven (F1); changed =>
              direct coupling (F6). Without interventions this pair is
              returned NONIDENTIFIABLE(passive) BY DESIGN.

Verdicts: GENUINE_SHARED_LATENT | DIRECT_COUPLING |
SHARED_SENSOR_COMMON_MODE | SHARED_CALIBRATION_ARTIFACT |
SHARED_MATHEMATICS_ONLY | INDEPENDENT |
NONIDENTIFIABLE(passive: latent vs direct coupling)
Each verdict carries the features and a margin-based confidence.
"""

import numpy as np


def _norm_xcorr(a, b, max_lag):
    a = (a - a.mean()) / a.std()
    b = (b - b.mean()) / b.std()
    n = len(a)
    out = {}
    for L in range(-max_lag, max_lag + 1):
        if L >= 0:
            out[L] = float(np.dot(a[L:], b[:n - L]) / (n - L))
        else:
            out[L] = float(np.dot(a[:n + L], b[-L:]) / (n + L))
    return out


def _envelope(x, w=200):
    x = x - x.mean()
    v = x ** 2
    k = np.ones(w) / w
    return np.convolve(v, k, mode="valid")


def _timescale(x):
    x = x - x.mean()
    r1 = float(np.dot(x[1:], x[:-1]) / np.dot(x, x))
    return r1


def analyze(Y1, Y2, meta, thr_r=0.08, thr_env=0.25):
    iv = meta.get("interventions")
    n = len(Y1)
    base_end = int(0.55 * n)
    b1, b2 = Y1[:base_end], Y2[:base_end]
    xc = _norm_xcorr(b1, b2, max_lag=40)
    r0 = abs(xc[0])
    r_far = max(abs(xc[L]) for L in range(8, 41))
    # empirical null floor: the SAME max-statistic on a time-shifted
    # surrogate pair (decoupled by construction) calibrates the threshold
    # from the data itself -- no fixed magic number decides "related".
    floor = 0.0
    for k in (2, 3, 4, 5, 7):
        surr = _norm_xcorr(b1, np.roll(b2, base_end // k), max_lag=40)
        floor = max(floor, max(abs(v) for v in surr.values()))
    thr_r = max(thr_r, 1.5 * floor)
    e1, e2 = _envelope(b1), _envelope(b2)
    env_corr = float(np.corrcoef(e1, e2)[0, 1])
    ts = (_timescale(b1), _timescale(b2))
    feats = {"r0": r0, "r_far": r_far, "null_floor": floor,
             "threshold_used": thr_r, "env_corr": env_corr,
             "lag1_timescales": ts}

    # multiplicative-artifact signature: envelopes co-vary far more than
    # the linear signals do (genuine latents move BOTH together)
    if env_corr > 0.4 and r0 < 0.5 * env_corr:
        return {"verdict": "SHARED_CALIBRATION_ARTIFACT", "features": feats,
                "confidence": float(min(1.0, env_corr))}

    if r0 < thr_r and r_far < thr_r:
        if env_corr > thr_env:
            v = "SHARED_CALIBRATION_ARTIFACT"
        elif abs(ts[0] - ts[1]) < 0.01:
            v = "SHARED_MATHEMATICS_ONLY"
        else:
            v = "INDEPENDENT"
        return {"verdict": v, "features": feats,
                "confidence": float(min(1.0, 3 * abs(env_corr - thr_env)
                                        + 0.5))}

    # nonzero cross-structure
    if r0 > 3 * r_far and r_far < thr_r:
        return {"verdict": "SHARED_SENSOR_COMMON_MODE", "features": feats,
                "confidence": float(min(1.0, r0 / (r_far + 1e-9) / 10))}

    # colored cross-structure: latent vs direct coupling
    if not iv:
        return {"verdict": "NONIDENTIFIABLE",
                "cause": "passive observation cannot separate a shared "
                         "dynamical latent from direct coupling "
                         "(no-go: intervention required)",
                "features": feats, "confidence": 1.0}
    w0, w1 = iv["clamp_system1"]["window"]
    pre = Y2[:base_end]
    clamped = Y2[w0 + 200:w1]
    # discriminator: system 2's lag-1 timescale. Clamping x1 removes a
    # DIRECT drive (timescale drops measurably) but leaves a LATENT drive
    # untouched. Timescale estimates are far more precise than variance
    # ratios at this window length (se ~ 0.003 vs ~16%).
    dts = float(_timescale(pre) - _timescale(clamped))
    feats["clamp_var_ratio_sys2"] = float(clamped.var() / pre.var())
    feats["clamp_timescale_drop_sys2"] = dts
    if dts < 0.007:
        v, conf = "GENUINE_SHARED_LATENT", min(1.0, (0.007 - dts) / 0.007
                                               + 0.5)
    else:
        v, conf = "DIRECT_COUPLING", min(1.0, dts / 0.014)
    return {"verdict": v, "features": feats, "confidence": float(conf)}


def heldout_intervention_prediction(Y1, Y2, meta, delta_new):
    """From the TRAINING latent-shift segment, estimate per-system gains
    (stationary response / delta0) and predict means under an unseen
    shift delta_new."""
    iv = meta["interventions"]["latent_proxy_shift"]
    (w0, w1), d0 = iv["window"], iv["delta"]
    n = len(Y1)
    base = slice(0, int(0.55 * n))
    seg = slice(w0 + 400, w1)
    g1 = (Y1[seg].mean() - Y1[base].mean()) / d0
    g2 = (Y2[seg].mean() - Y2[base].mean()) / d0
    return {"predicted_mean_shift": (float(g1 * delta_new),
                                     float(g2 * delta_new)),
            "gains": (float(g1), float(g2))}
