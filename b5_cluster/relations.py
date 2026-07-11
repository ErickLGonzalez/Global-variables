"""Discover cluster / factorization relations by exact template matching.

Headline identities (?5):
  F1  R_24 = A_22²                         (2→4 residue = product of 2→2)
  F2  R_24_b = A_22_cross²                 (second channel, same structure)
  F3  A_22 = A_22_cross                    (one coupling across sectors)
  F4  alpha_22 = alpha_24 = ...            (channel couplings collapse)
  F5  A_22 = κ · alpha_22                  (definition / scheme link)

Together these force d_identifiable = 1 for the coupling sector (plus κ
if treated as a free scheme factor — we fix κ as known scheme data, so
the physical identifiable count for the coupling is 1).
"""

from fractions import Fraction
from typing import Dict, List

from .exact import fmt

Obs = Dict[str, Fraction]


def discover_factorization(obs: Obs) -> List[Dict]:
    found: List[Dict] = []

    def add(name, formula, inputs, output, mechanism, witness=None):
        found.append({
            "name": name,
            "formula": formula,
            "inputs": list(inputs),
            "output": output,
            "mechanism": mechanism,
            "status": "FORCED",
            "witness": witness or "exact Fraction identity",
        })

    if "R_24" in obs and "A_22" in obs and obs["R_24"] == obs["A_22"] ** 2:
        add("F1", "R_24 = A_22²", ["A_22"], "R_24",
            "exact factorization residue forcing")

    if "R_24_b" in obs and "A_22_cross" in obs and obs["R_24_b"] == obs["A_22_cross"] ** 2:
        add("F2", "R_24_b = A_22_cross²", ["A_22_cross"], "R_24_b",
            "exact factorization residue forcing (channel b)")

    if "A_22" in obs and "A_22_cross" in obs and obs["A_22"] == obs["A_22_cross"]:
        add("F3", "A_22 = A_22_cross", ["A_22"], "A_22_cross",
            "exact cross-sector equality (one coupling)")

    # Channel-coupling collapse
    alphas = [(k, obs[k]) for k in
              ("alpha_22", "alpha_24", "alpha_22_cross", "alpha_24_b")
              if k in obs]
    if len(alphas) >= 2 and all(v == alphas[0][1] for _, v in alphas):
        for name, _ in alphas[1:]:
            add(f"F4_{name}", f"{name} = alpha_22",
                ["alpha_22"], name,
                "exact channel-coupling collapse (cluster / locality)")

    if ("A_22" in obs and "kappa" in obs and "alpha_22" in obs
            and obs["A_22"] == obs["kappa"] * obs["alpha_22"]):
        add("F5", "A_22 = κ · α_22", ["kappa", "alpha_22"], "A_22",
            "exact scheme link")

    if ("R_24" in obs and "kappa" in obs and "alpha_24" in obs
            and obs["R_24"] == (obs["kappa"] * obs["alpha_24"]) ** 2):
        add("F6", "R_24 = (κ · α_24)²", ["kappa", "alpha_24"], "R_24",
            "exact residue–coupling link")

    return found


def factorization_holds(obs: Obs) -> bool:
    return ("A_22" in obs and "R_24" in obs
            and obs["R_24"] == obs["A_22"] ** 2)
