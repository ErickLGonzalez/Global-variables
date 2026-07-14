"""S3-EM: the fine-structure-constant consistency layer (EXP-D, zero
hardware). The alpha row's LIVE tension, run through the S3 machinery.

Unlike S3 (alpha_s: four channels, chi2/dof = 0.11, d = 1 FORCED), the
alpha channels currently FAIL mutual consistency at 5.5 sigma. The
pipeline's job is to say so with certificates: quantify the tension,
LOCALIZE it (conversion chain vs h/m measurements), jackknife it, refuse
a single-value FORCED verdict, and emit the honest
NONIDENTIFIABLE(systematics vs new physics) cause.

DATA (all values web-verified 2026-07-15; units: offset of alpha^{-1}
from 137.035999 in 1e-9):
  Rb-2020  Morel/Guellati-Khelifa (LKB), Nature 588, 61:   206 +/- 11
  Cs-2018  Parker/Mueller (Berkeley), Science 360, 191:     46 +/- 27
  ae-2008  Gabrielse group + QED (g-2 route):               84 +/- 51
Provenance notes: CODATA-2022 applied an EXPANSION FACTOR 2.5 to both
recoil uncertainties in response to the tension (an M-layer patch, not a
resolution); Morel et al. identified beam-profile-class systematics as
the likely culprit family; a newer a_e determination (2023) exists and is
flagged VERIFY-BEFORE-USE in the memo, not used as input here.

Conversion chain: alpha^2 = (2 R_inf / c)(A_r(X)/A_r(e))(h/m_X).
Shared-input relative uncertainties: R_inf 1.9e-12, A_r(e) 2.9e-11,
A_r(Rb) 7e-11 -- their quadrature (~7.6e-11) is <= 7% of the observed
relative gap (1.17e-9): the tension CANNOT live in the shared conversion
factors. Localization to the h/m measurements is FORCED.
"""

import numpy as np

CHANNELS = [
    {"name": "Rb_2020_recoil", "x": 206.0, "err": 11.0,
     "method": "h/m photon recoil (Bloch + Ramsey-Borde)"},
    {"name": "Cs_2018_recoil", "x": 46.0, "err": 27.0,
     "method": "h/m photon recoil (Bragg + Bloch)"},
    {"name": "ae_2008_g2", "x": 84.0, "err": 51.0,
     "method": "electron g-2 + QED theory"},
]

SHARED_INPUT_BUDGET_REL = np.sqrt(1.9e-12 ** 2 + 2.9e-11 ** 2 + 7e-11 ** 2)
OBSERVED_GAP_REL = 160e-9 / 137.036            # Rb - Cs in relative units
CODATA_EXPANSION = 2.5


def weighted_mean(chans):
    x = np.array([c["x"] for c in chans])
    e = np.array([c["err"] for c in chans])
    w = 1 / e ** 2
    mean = float(np.sum(w * x) / np.sum(w))
    err = float(1 / np.sqrt(np.sum(w)))
    chi2 = float(np.sum(w * (x - mean) ** 2))
    return mean, err, chi2, len(chans) - 1


def pull(a, b):
    return abs(a["x"] - b["x"]) / np.hypot(a["err"], b["err"])


def consistency_report(chans=CHANNELS):
    mean, err, chi2, dof = weighted_mean(chans)
    pulls = {f"{a['name']}~{b['name']}": float(pull(a, b))
             for i, a in enumerate(chans) for b in chans[i + 1:]}
    consistent = chi2 / dof < 2.0
    verdict = ("CONSISTENT: single-value FORCED (d=1)" if consistent else
               "TENSION: single-value verdict REFUSED; PERMITTED band "
               "spans channels; cause NONIDENTIFIABLE(unmodeled "
               "systematics vs new physics) from these data alone")
    return {"mean": mean, "err": err, "chi2": chi2, "dof": dof,
            "chi2_dof": chi2 / dof, "pulls": pulls, "verdict": verdict,
            "permitted_band": [min(c["x"] - c["err"] for c in chans),
                               max(c["x"] + c["err"] for c in chans)]}


def jackknife(chans=CHANNELS):
    out = {}
    for i, dropped in enumerate(chans):
        rest = [c for j, c in enumerate(chans) if j != i]
        _, _, chi2, dof = weighted_mean(rest)
        p = pull(rest[0], rest[1])
        out["drop_" + dropped["name"]] = {"pull_sigma": float(p),
                                          "consistent": bool(p < 2.0)}
    return out


def localization():
    frac = float(SHARED_INPUT_BUDGET_REL / OBSERVED_GAP_REL)
    return {"shared_input_budget_rel": float(SHARED_INPUT_BUDGET_REL),
            "observed_gap_rel": float(OBSERVED_GAP_REL),
            "max_fraction_explainable_by_shared_inputs": frac,
            "verdict": "LOCALIZATION FORCED: the tension lives in the "
                       "h/m measurement channel; the shared conversion "
                       "chain (R_inf, mass ratios) is >= 13x too precise "
                       "to absorb it"}


def codata_expansion_view():
    inflated = [dict(c) for c in CHANNELS]
    for c in inflated:
        if "recoil" in c["name"]:
            c["err"] *= CODATA_EXPANSION
    rep = consistency_report(inflated)
    rep["note"] = ("CODATA-2022 operational response reproduced: x2.5 "
                   "error expansion drops all pairwise pulls below 3 "
                   "sigma but leaves chi2/dof ~ 3.9 for this channel set "
                   "-- the patch SOFTENS, it does not resolve. M-layer "
                   "mitigation, quantified, not endorsed as physics")
    return rep
