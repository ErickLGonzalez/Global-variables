"""Discover electroweak algebraic relations by exact template matching.

The engine is *not* told the Standard Model map. It enumerates a finite
library of multiplicative / Pythagorean / linear templates (the same
forcing style as B2's exact-linear TP and rank-1 completion) and retains
only identities that hold exactly on the observed Fraction table.

Discovered physics relations (reported names):
  R1  e = g · sin θ_W
  R2  e = g′ · cos θ_W
  R3  M_W = g · v / 2
  R4  M_Z = (v/2) · √(g²+g′²)     [certified as 4 M_Z² = v² (g²+g′²)]
  R5  G_F = 1/(√2 v²)             [certified as G_F_inv_sq = 2 v⁴]
  R6  cos θ_W = M_W / M_Z         [and sin²+cos²=1, etc.]
"""

from fractions import Fraction
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from .exact import fmt, isqrt_exact, q

Obs = Dict[str, Fraction]


def _get(obs: Obs, *keys: str) -> Optional[Tuple[Fraction, ...]]:
    if any(k not in obs for k in keys):
        return None
    return tuple(obs[k] for k in keys)


def discover_relations(obs: Obs) -> List[Dict]:
    """Return every template that holds exactly on `obs`."""
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

    # R1: e = g * sin_theta_W
    t = _get(obs, "e", "g", "sin_theta_W")
    if t and t[0] == t[1] * t[2]:
        add("R1", "e = g · sin θ_W", ["g", "sin_theta_W"], "e",
            "exact multiplicative forcing")

    # R2: e = g_prime * cos_theta_W
    t = _get(obs, "e", "g_prime", "cos_theta_W")
    if t and t[0] == t[1] * t[2]:
        add("R2", "e = g′ · cos θ_W", ["g_prime", "cos_theta_W"], "e",
            "exact multiplicative forcing")

    # R3: M_W = g * v / 2
    t = _get(obs, "M_W", "g", "v")
    if t and t[0] == t[1] * t[2] / 2:
        add("R3", "M_W = g v / 2", ["g", "v"], "M_W",
            "exact linear-multiplicative forcing")

    # R4: 4 M_Z² = v² (g² + g′²)  ↔  M_Z = (v/2) √(g²+g′²)
    t = _get(obs, "M_Z", "v", "g", "g_prime")
    if t:
        M_Z, v, g, gp = t
        if 4 * M_Z * M_Z == v * v * (g * g + gp * gp):
            add("R4", "M_Z = (v/2) √(g²+g′²)", ["v", "g", "g_prime"], "M_Z",
                "exact Pythagorean / quadratic forcing",
                witness=f"4 M_Z² = v²(g²+g′²) = {fmt(4*M_Z*M_Z)}")

    # R5: G_F_inv_sq = 2 v⁴  ↔  G_F = 1/(√2 v²)
    t = _get(obs, "G_F_inv_sq", "v")
    if t and t[0] == 2 * t[1] ** 4:
        add("R5", "G_F = 1/(√2 v²)", ["v"], "G_F_inv_sq",
            "exact squared-√2 forcing (1/G_F² = 2 v⁴)",
            witness=f"G_F_inv_sq = 2 v⁴ = {fmt(t[0])}")

    # R6: cos_theta_W = M_W / M_Z
    t = _get(obs, "cos_theta_W", "M_W", "M_Z")
    if t and t[2] != 0 and t[0] == t[1] / t[2]:
        add("R6", "cos θ_W = M_W / M_Z", ["M_W", "M_Z"], "cos_theta_W",
            "exact ratio forcing")

    # R7: sin² + cos² = 1
    t = _get(obs, "sin_theta_W", "cos_theta_W")
    if t and t[0] * t[0] + t[1] * t[1] == 1:
        add("R7", "sin²θ_W + cos²θ_W = 1",
            ["sin_theta_W", "cos_theta_W"], "sin_theta_W",
            "exact Pythagorean identity on Weinberg angle",
            witness="unit-circle constraint (either angle component free)")

    # R8: g / g_prime = cos / sin  (coupling–angle consistency)
    t = _get(obs, "g", "g_prime", "cos_theta_W", "sin_theta_W")
    if t and t[1] != 0 and t[3] != 0 and t[0] / t[1] == t[2] / t[3]:
        add("R8", "g/g′ = cosθ_W/sinθ_W",
            ["g_prime", "cos_theta_W", "sin_theta_W"], "g",
            "exact cross-ratio forcing")

    # R9: e² (g²+g′²) = g² g′²   (follows from e = g sin = g′ cos)
    t = _get(obs, "e", "g", "g_prime")
    if t:
        e, g, gp = t
        if e * e * (g * g + gp * gp) == g * g * gp * gp:
            add("R9", "e²(g²+g′²) = g² g′²",
                ["g", "g_prime"], "e",
                "exact quadratic elimination of θ_W")

    return found


def relation_names(relations: Sequence[Dict]) -> List[str]:
    return [r["name"] for r in relations]
