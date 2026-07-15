"""A1 / cdl-ew-vacuum: electroweak vacuum stability boundary forward map.

Forward map: (m_t_pole, alpha_s(M_Z), M_H) -> verdict {ABSOLUTELY_STABLE-side,
METASTABLE-side} with sigma distance to the stability boundary.

Boundary (linearized around criticality, Buttazzo et al. 2013, arXiv:1307.3536):
    M_H^crit [GeV] = 129.6 + 2.0*(m_t - 173.34) - 0.5*(alpha_s - 0.1184)/0.0007
with theoretical uncertainty ~0.3 GeV (we carry a stipulated sigma_th).

SOUNDNESS: HEURISTIC. This is a linearization valid near central 2013 inputs; the
SOUND upgrade path is a full 2-loop-matching + 3-loop-RGE pipeline (backlogged).
"""
from __future__ import annotations
import math
from .common import make_certificate

BOUNDARY = {"MH0": 129.6, "mt0": 173.34, "as0": 0.1184,
            "c_mt": 2.0, "c_as_per_unit": 0.5 / 0.0007, "sigma_th": 0.3}

DEFAULT_INPUTS = {
    # PDG-era central values with uncertainties (stipulated; update on integration)
    "m_t_pole": (172.57, 0.29),      # GeV
    "alpha_s_MZ": (0.1180, 0.0009),
    "M_H": (125.20, 0.11),           # GeV
}


def critical_mh(m_t, alpha_s):
    b = BOUNDARY
    return b["MH0"] + b["c_mt"] * (m_t - b["mt0"]) - b["c_as_per_unit"] * (alpha_s - b["as0"])


def run(inputs=None):
    inp = inputs or DEFAULT_INPUTS
    (mt, s_mt) = inp["m_t_pole"]
    (a_s, s_as) = inp["alpha_s_MZ"]
    (mh, s_mh) = inp["M_H"]

    mh_crit = critical_mh(mt, a_s)
    # propagate: sigma_crit^2 = (c_mt*s_mt)^2 + (c_as*s_as)^2 + sigma_th^2
    b = BOUNDARY
    s_crit = math.sqrt((b["c_mt"] * s_mt) ** 2 +
                       (b["c_as_per_unit"] * s_as) ** 2 +
                       b["sigma_th"] ** 2)
    delta = mh - mh_crit                       # >0 stable side, <0 metastable side
    sigma_total = math.sqrt(s_crit ** 2 + s_mh ** 2)
    n_sigma = delta / sigma_total

    verdict = "CONDITIONAL(m_t,alpha_s,M_H)-value: " + (
        "ABSOLUTELY_STABLE-side" if delta > 0 else "METASTABLE-side")

    return make_certificate(
        pipeline="ew_vacuum", entry_id="cdl-ew-vacuum",
        soundness_tag="HEURISTIC",
        warning=("ew_vacuum.critical_mh: linearized Buttazzo-2013 boundary; valid near "
                 "2013 central inputs only. SOUND upgrade: 2-loop matching + 3-loop RGE "
                 "pipeline (B13 backlog item 1)."),
        stipulations=[
            {"name": "boundary_coefficients", "assumed": BOUNDARY,
             "source": "arXiv:1307.3536 (linearized)"},
            {"name": "input_values", "assumed": inp, "source": "PDG-era, stipulated"},
        ],
        inputs={"m_t_pole": mt, "alpha_s_MZ": a_s, "M_H": mh},
        verdict=verdict,
        verdict_detail={
            "M_H_critical_GeV": round(mh_crit, 3),
            "sigma_boundary_GeV": round(s_crit, 3),
            "delta_GeV": round(delta, 3),
            "n_sigma_from_boundary": round(n_sigma, 3),
            "interpretation": "negative delta = central values on metastable side; "
                              "|n_sigma| < 2 means verdict is input-limited, not settled",
        },
        notes="Bidirectional: falsifier f-top-mass-ee (e+e- top threshold scan) decides.",
    )
