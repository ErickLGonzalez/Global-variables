"""Multi-channel pseudo-data for conjecture ?5.

Toy local QFT with a single coupling α (standing in for α, α_s, or an
electroweak gauge coupling). Two process classes:

  2→2 :  strength A_22 = κ · α
  2→4 :  factorizes on an intermediate pole with residue
         R_24 = (κ · α) · (κ · α) = κ² · α² = A_22²

Cluster decomposition / locality says the *same* α governs every
factorization channel. Channel-dependent couplings (α_22 ≠ α_24) would
falsify the composition column entry.

We also emit a second sector (e.g. a crossed or multi-leg channel) with
the same α, so the discovery engine must collapse putative per-channel
parameters to one identifiable source.
"""

from fractions import Fraction
from typing import Dict

from .exact import q


def make_factorization_data(
    alpha: Fraction = Fraction(1, 137),
    kappa: Fraction = Fraction(2, 1),
) -> Dict[str, Fraction]:
    """Return an unlabeled exact-Fraction observation table.

    Presented as if each entry were independently measured; the engine
    is not told that a single α generated them.
    """
    alpha, kappa = q(alpha), q(kappa)
    A_22 = kappa * alpha
    R_24 = A_22 * A_22                    # factorization residue
    # Crossed / multi-leg channel with same α (different kinematic prefactor)
    A_22_cross = kappa * alpha            # same coupling, same κ toy
    R_24_b = (kappa * alpha) ** 2         # second factorization channel
    return {
        "A_22": A_22,
        "R_24": R_24,
        "A_22_cross": A_22_cross,
        "R_24_b": R_24_b,
        # Putative per-channel couplings as if fitted independently
        # (truth: all equal to alpha). Discovery must force equality.
        "alpha_22": alpha,
        "alpha_24": alpha,
        "alpha_22_cross": alpha,
        "alpha_24_b": alpha,
        "kappa": kappa,
    }


def channel_dependent_counterexample(
    alpha_22: Fraction = Fraction(1, 137),
    alpha_24: Fraction = Fraction(1, 100),
    kappa: Fraction = Fraction(2, 1),
) -> Dict[str, Fraction]:
    """Falsifier data: different couplings per channel — factorization
    identity R_24 = A_22² fails when A_22 = κ α_22 but residue uses α_24.
    """
    alpha_22, alpha_24, kappa = q(alpha_22), q(alpha_24), q(kappa)
    A_22 = kappa * alpha_22
    R_24 = (kappa * alpha_24) ** 2        # wrong channel coupling
    return {
        "A_22": A_22,
        "R_24": R_24,
        "A_22_cross": A_22,
        "R_24_b": R_24,
        "alpha_22": alpha_22,
        "alpha_24": alpha_24,
        "alpha_22_cross": alpha_22,
        "alpha_24_b": alpha_24,
        "kappa": kappa,
    }
