"""Kerr horizon geometry for the B4 composition-law pipeline.

Units: areas are expressed in units of (G * M_sun / c^2)^2, so only
dimensionless mass ratios and spins matter -- consistent with the atlas
rule that only dimensionless invariants are comparison objects.

Kerr horizon area:  A = 8 pi M^2 (1 + sqrt(1 - chi^2))   [geometric units]
"""

import numpy as np


def kerr_area(m, chi):
    """Horizon area in (G M_sun / c^2)^2 units. m in solar masses, |chi|<1."""
    m = np.asarray(m, dtype=float)
    chi = np.clip(np.asarray(chi, dtype=float), -0.9999, 0.9999)
    return 8.0 * np.pi * m ** 2 * (1.0 + np.sqrt(1.0 - chi ** 2))


def eta_A(a1, a2, af):
    """Composition-law invariant: eta_A = (A_f - A_1 - A_2) / A_f.

    Positive iff the merger obeys area increase (entropy subadditivity
    realized geometrically -- conjecture ?3's dimensionless observable)."""
    return (af - a1 - a2) / af
