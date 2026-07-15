"""A4 / cdl-strong-cp: certified |theta-bar| upper bound from the nEDM limit.

Forward map: theta-bar -> d_n = k * theta-bar (lattice k). Inverted with the
experimental bound |d_n| < 1.8e-26 e cm (90% CL, PSI nEDM, arXiv:2001.11966).

Lattice coefficient (Dragos et al., arXiv:1902.03254):
    d_n = -0.00152(71) * theta-bar  [e fm] = -1.52(71)e-16 * theta-bar [e cm]

Convention: conservative bound uses |k| - N_SIGMA_K * sigma_k in the denominator.
Exact Fraction arithmetic (repo verifier standard); floats only in the report.
SOUND given the stipulated lattice coefficient (stipulation carried explicitly).
"""
from __future__ import annotations
from fractions import Fraction as F
from .common import make_certificate

D_N_LIMIT_E_CM = F(18, 10) * F(1, 10 ** 26)     # 1.8e-26 e cm, 90% CL
K_CENTRAL_E_CM = F(152, 100000) * F(1, 10 ** 13)  # 0.00152 e fm -> e cm
K_SIGMA_E_CM = F(71, 100000) * F(1, 10 ** 13)     # 0.00071 e fm -> e cm
N_SIGMA_K = 1


def run():
    k_conservative = K_CENTRAL_E_CM - N_SIGMA_K * K_SIGMA_E_CM
    assert k_conservative > 0, "coefficient consistent with zero at chosen N_SIGMA_K"
    theta_central = D_N_LIMIT_E_CM / K_CENTRAL_E_CM
    theta_conservative = D_N_LIMIT_E_CM / k_conservative

    return make_certificate(
        pipeline="strong_cp", entry_id="cdl-strong-cp",
        soundness_tag="SOUND",
        stipulations=[
            {"name": "lattice_coefficient_dn_per_theta",
             "assumed": {"central_e_cm": float(K_CENTRAL_E_CM), "sigma_e_cm": float(K_SIGMA_E_CM)},
             "source": "arXiv:1902.03254"},
            {"name": "nEDM_limit", "assumed": {"limit_e_cm": float(D_N_LIMIT_E_CM), "CL": 0.90},
             "source": "arXiv:2001.11966"},
            {"name": "conservative_convention",
             "assumed": f"denominator = |k| - {N_SIGMA_K}*sigma_k", "source": "B13-CDL design §4"},
        ],
        inputs={"d_n_limit_e_cm": float(D_N_LIMIT_E_CM)},
        verdict="CONDITIONAL(lattice-k)-value: |theta_bar| PERMITTED interval [0, upper)",
        verdict_detail={
            "theta_bar_upper_central": float(theta_central),
            "theta_bar_upper_conservative": float(theta_conservative),
            "exact_fractions": {
                "central": f"{theta_central.numerator}/{theta_central.denominator}",
                "conservative": f"{theta_conservative.numerator}/{theta_conservative.denominator}",
            },
        },
        witness={"type": "exact-division",
                 "statement": "upper bounds are exact rationals; any theta_bar above the "
                              "conservative bound implies |d_n| above the 90% CL limit"},
        notes="Bidirectional: f-nedm-next. A nonzero d_n measures theta_bar directly.",
    )
