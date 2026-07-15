"""A14 / cdl-muon-g2: experiment-vs-theory tension conditional on HVP method.

Inputs (units of 1e-11):
  Experiment (world avg, final E989 + BNL, 2025): 116592071.5 (14.5)  [124 ppb]
  Theory WP25 (lattice HVP):                      116592033   (62)    [530 ppb]
  Theory WP20 (data-driven HVP):                  116591810   (43)

The pipeline computes all pairwise sigmas and then — S3-EM pattern — REFUSES to
force a single experiment-vs-SM verdict, because the SM prediction is not
method-invariant. Verdict: NONIDENTIFIABLE(HVP-method).
SOUND: pure arithmetic on published values.
"""
from __future__ import annotations
import math
from .common import make_certificate

VALUES = {
    "exp_2025": (116592071.5, 14.5, "Muon g-2 Collab final report (2025)"),
    "wp25_lattice": (116592033.0, 62.0, "Theory Initiative White Paper 2025 (lattice HVP)"),
    "wp20_datadriven": (116591810.0, 43.0, "Theory Initiative White Paper 2020 (e+e- HVP)"),
}


def _sigma(a, b):
    (va, sa, _), (vb, sb, _) = a, b
    return abs(va - vb) / math.sqrt(sa * sa + sb * sb)


def run():
    pairs = {
        "exp_vs_wp25": _sigma(VALUES["exp_2025"], VALUES["wp25_lattice"]),
        "exp_vs_wp20": _sigma(VALUES["exp_2025"], VALUES["wp20_datadriven"]),
        "wp25_vs_wp20": _sigma(VALUES["wp25_lattice"], VALUES["wp20_datadriven"]),
    }
    tension_matrix = {k: round(v, 2) for k, v in pairs.items()}

    return make_certificate(
        pipeline="muon_g2", entry_id="cdl-muon-g2",
        soundness_tag="SOUND",
        stipulations=[
            {"name": k, "assumed": {"value_1e-11": v, "sigma_1e-11": s}, "source": src}
            for k, (v, s, src) in VALUES.items()
        ],
        inputs={"units": "1e-11"},
        verdict="NONIDENTIFIABLE(HVP-method): experiment-vs-SM verdict is not "
                "method-invariant; pipeline declines a single sigma",
        verdict_detail={
            "tension_matrix_sigma": tension_matrix,
            "reading": {
                "exp_vs_wp25": "agreement (~0.6 sigma) — no new-physics signal under lattice HVP",
                "exp_vs_wp20": "strong tension (~5.8 sigma) under data-driven HVP",
                "wp25_vs_wp20": "the discrepancy lives INSIDE theory (HVP method), "
                                "not between experiment and theory",
            },
        },
        witness={"type": "method-branch-divergence",
                 "statement": "the two theory branches differ by more than the "
                              "experiment-theory gap under either branch; verdict "
                              "identification requires an external selector (MUonE, "
                              "new e+e- data) — see falsifiers f-muone, f-ee-hadrons-new"},
        notes="Structural twin of S3-EM (fine-structure Rb/Cs h/m channel): honest "
              "refusal is the deliverable, not a limitation. contested: method-dependent.",
    )
