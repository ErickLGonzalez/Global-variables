"""A12 / cdl-varying-constants: Dirac Large Numbers Hypothesis vs LLR Gdot/G bound.

LNH prediction: G proportional to 1/t  =>  |Gdot/G| ~ H_0 ~ 7e-11 / yr.
LLR bound (Hofmann & Muller 2018): Gdot/G = (7.1 +/- 7.6)e-14 / yr.

Verdict: REJECTED with numeric margin witness (pure interval arithmetic — SOUND).
This is the ledger's exemplar of an already-decided falsifier (f-llr-g).
"""
from __future__ import annotations
from .common import make_certificate

H0_PER_YR = 7.0e-11          # LNH-predicted |Gdot/G| scale
LLR_CENTRAL = 7.1e-14        # /yr
LLR_SIGMA = 7.6e-14          # /yr
N_SIGMA = 5                  # generous exclusion band


def run():
    bound_5sigma = abs(LLR_CENTRAL) + N_SIGMA * LLR_SIGMA
    margin_orders = 0.0
    import math
    margin_orders = math.log10(H0_PER_YR / bound_5sigma)

    return make_certificate(
        pipeline="varying_constants", entry_id="cdl-varying-constants",
        soundness_tag="SOUND",
        stipulations=[
            {"name": "LNH_prediction", "assumed": {"|Gdot/G|_per_yr": H0_PER_YR},
             "source": "Dirac (1937); |Gdot/G| ~ H_0"},
            {"name": "LLR_measurement",
             "assumed": {"central_per_yr": LLR_CENTRAL, "sigma_per_yr": LLR_SIGMA},
             "source": "Class. Quantum Grav. 35, 035015 (2018)"},
        ],
        inputs={"n_sigma_exclusion": N_SIGMA},
        verdict="REJECTED: Dirac-LNH varying-G prediction excluded",
        verdict_detail={
            "llr_bound_5sigma_per_yr": bound_5sigma,
            "lnh_prediction_per_yr": H0_PER_YR,
            "exclusion_margin_orders_of_magnitude": round(margin_orders, 2),
        },
        witness={"type": "interval-separation",
                 "statement": f"LNH prediction exceeds the {N_SIGMA}-sigma LLR band by "
                              f"~{margin_orders:.1f} orders of magnitude"},
        notes="Filed as REJECTED per erratum culture, not silently dropped. General "
              "varying-constants searches (f-clock-drift) remain live falsifiers for "
              "the alpha and mu rows.",
    )
