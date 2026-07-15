"""A15 / cdl-h0-tension: pairwise H0 tension matrix, early vs late universe.

Inputs (km/s/Mpc): Planck 2018, DESI-era BAO+CMB, SH0ES 2022, JWST-era ladder
compilation, CCHP TRGB/JAGB. Verdict: NONIDENTIFIABLE(model-vs-systematic) —
the tension is a clash of *conditional* forward maps (CMB conditional on LCDM,
ladder conditional on calibration), and the late branch has internal spread.
SOUND: pure arithmetic on published values.
"""
from __future__ import annotations
import math
from itertools import combinations
from .common import make_certificate

VALUES = {
    "planck2018_cmb": (67.4, 0.5, "Planck 2018, A&A 641 A6 (conditional on LCDM)"),
    "desi_bao_cmb": (67.97, 0.38, "DESI BAO + CMB, 2024-25 (conditional on LCDM)"),
    "sh0es_2022": (73.04, 1.04, "Riess et al. ApJL 934 L7 (Cepheid ladder)"),
    "ladder_jwst_2025": (73.17, 0.86, "JWST-era distance-ladder compilation (2025)"),
    "cchp_trgb_jagb": (69.8, 1.7, "Freedman et al. CCHP TRGB/JAGB (JWST)"),
}


def run():
    matrix = {}
    for a, b in combinations(VALUES, 2):
        (va, sa, _), (vb, sb, _) = VALUES[a], VALUES[b]
        matrix[f"{a}__vs__{b}"] = round(abs(va - vb) / math.sqrt(sa**2 + sb**2), 2)

    headline = matrix["planck2018_cmb__vs__ladder_jwst_2025"]

    return make_certificate(
        pipeline="h0_tension", entry_id="cdl-h0-tension",
        soundness_tag="SOUND",
        stipulations=[
            {"name": k, "assumed": {"H0": v, "sigma": s}, "source": src}
            for k, (v, s, src) in VALUES.items()
        ],
        inputs={"units": "km/s/Mpc"},
        verdict="NONIDENTIFIABLE(model-vs-systematic): early- and late-branch H0 are "
                "each conditional forward maps; identification requires a branch-"
                "independent probe",
        verdict_detail={
            "tension_matrix_sigma": matrix,
            "headline_early_vs_late_sigma": headline,
            "intra_late_branch_spread_sigma": matrix["ladder_jwst_2025__vs__cchp_trgb_jagb"],
            "reading": "early-branch pair internally consistent; late branch has "
                       "method spread (SH0ES vs CCHP); headline tension ~5 sigma and "
                       "hardening — JWST crowding checks removed the leading systematic "
                       "candidate on the ladder side",
        },
        witness={"type": "branch-consistency-pattern",
                 "statement": "if a single H0 existed and both branches' conditionals "
                              "held, all pairwise sigmas would be O(1); they are not"},
        notes="Falsifier f-standard-sirens (GW sirens at +/-1 km/s/Mpc) is branch-"
              "independent. Couples to cdl-dark-energy-eos (A3): evolving w reshapes "
              "the early-branch conditional. contested: intra-branch spread.",
    )
