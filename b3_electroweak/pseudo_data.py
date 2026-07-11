"""Generate electroweak closed-system pseudo-data from three free sources.

Canonical free basis (d_identifiable = 3): (g, g′, v).
All other quantities are derived by the Standard Model tree-level map:

    sin θ_W = g′ / √(g²+g′²),   cos θ_W = g / √(g²+g′²)
    e       = g sin θ_W = g′ cos θ_W
    M_W     = g v / 2
    M_Z     = (v/2) √(g²+g′²)
    G_F     = 1 / (√2 v²)     (certified via 1/(G_F² v⁴) = 2)

For exact Fraction arithmetic we choose (g, g′, v) so that g²+g′² is a
perfect square in Q (Pythagorean coupling pair), and we store G_F via the
rational proxy G_F_sq2 := G_F·√2 = 1/v² together with the exact-rational
witness 1/(G_F_proxy²) wait — we store:
    G_F_inv_sq = 2 v⁴     (= 1/G_F²)
so G_F itself is represented by the rational 1/G_F² and the relation
templates know to look for that squared form.
"""

from fractions import Fraction
from typing import Dict

from .exact import isqrt_exact, q


def make_closed_system(
    g: Fraction = Fraction(3, 5),
    gp: Fraction = Fraction(4, 5),
    v: Fraction = Fraction(2, 1),
) -> Dict[str, Fraction]:
    """Return the full observed table as exact rationals.

    G_F is not itself rational when √2 is present; we expose:
      G_F_inv_sq = 1/G_F² = 2 v⁴   (exact rational)
    and keep the symbolic label 'G_F' out of the numeric table, using
    'G_F_inv_sq' as the observable that the discovery engine sees.
    The discovered relation is reported as G_F = 1/(√2 v²).
    """
    g, gp, v = q(g), q(gp), q(v)
    s = g * g + gp * gp
    root = isqrt_exact(s)          # √(g²+g′²)
    sin_w = gp / root
    cos_w = g / root
    e = g * sin_w                  # = gp * cos_w
    # cross-check identity
    assert e == gp * cos_w
    assert sin_w * sin_w + cos_w * cos_w == 1
    M_W = g * v / 2
    M_Z = v * root / 2
    G_F_inv_sq = 2 * v ** 4        # 1/G_F²
    return {
        "g": g,
        "g_prime": gp,
        "v": v,
        "sin_theta_W": sin_w,
        "cos_theta_W": cos_w,
        "e": e,
        "M_W": M_W,
        "M_Z": M_Z,
        "G_F_inv_sq": G_F_inv_sq,
    }


def observed_as_independent(data: Dict[str, Fraction]) -> Dict[str, Fraction]:
    """Present the table as if every entry were an independent measurement
    (the discovery engine must find the relations; it is not told which
    three were free)."""
    return dict(data)
