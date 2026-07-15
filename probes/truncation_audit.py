"""Truncation-audit probe -- the GfE critique as an executable gate.

CONTEXT (docs/notes/gfe-bianconi-review.md, ledger R34-R35): the
Gravity-from-Entropy papers derive modified Einstein equations and an
emergent cosmological term inside a CHOSEN field content (Dirac-Kahler
forms truncated at 2-forms; auxiliary G-field). The critique (Erick,
2026-07-16): absent a consistency proof, an 'emergent constant' derived
in a truncated sector may be an artifact of the truncation rather than a
property of the full framework.

THE LOGIC, MADE EXACT: for Gaussian (quadratic) theories, integrating
out sectors is EXACTLY a Schur complement. Take a ladder of modes
0-1-2-3-4 with stiffnesses k_i and nearest couplings g_{i,i+1}. The
'emergent constant' of mode 0 is its effective stiffness:

  lambda_trunc = k0 - g01^2/(k1 - g12^2/k2)          <- DROPS modes 3,4
  lambda_full  = k0 - g01^2/(k1 - g12^2/(k2 - g23^2/(k3 - g34^2/k4)))

Both continued fractions are exact rationals. Verdicts:

  TRUNCATION_ROBUST     lambda_trunc == lambda_full exactly; holds IFF
                        the boundary coupling vanishes (g23 = 0) -- a
                        protection statement, certified in Fractions.
  TRUNCATION_ARTIFACT   shift = lambda_full - lambda_trunc != 0,
                        quantified exactly; the 'emergent constant'
                        depends on what was dropped.
  TRUNCATION_UNAUDITED  only the truncated model supplied, no decoupling
                        certificate and no shift bound: the claim's
                        honest status (GfE's, in our classification,
                        pending a consistency proof).

Perturbative law: shift ~ g23^2 x (downstream response): quadratic in
the neglected coupling -- 'weak coupling to dropped sectors' is a
QUANTITATIVE license, never a qualitative one.

SCOPE STIPULATION: this Gaussian toy certifies the LOGIC of the required
audit. It is NOT a verdict on GfE itself, whose setting is nonlinear; it
defines what a GfE consistency proof must establish, in our vocabulary.
"""

from fractions import Fraction
from typing import Dict, List, Optional


def effective_stiffness(ks: List, gs: List) -> Fraction:
    """Exact continued-fraction Schur elimination of modes 1..n-1 from a
    nearest-neighbor ladder."""
    ks = [Fraction(k) for k in ks]
    gs = [Fraction(g) for g in gs]
    acc = ks[-1]
    for i in range(len(ks) - 2, -1, -1):
        acc = ks[i] - gs[i] ** 2 / acc
    return acc


def truncation_audit(ks: List, gs: List, keep: int) -> Dict:
    """Emergent constant from the first `keep` modes (dropping the rest)
    vs the full exact elimination."""
    lam_full = effective_stiffness(ks, gs)
    lam_trunc = effective_stiffness(ks[:keep], gs[:keep - 1])
    shift = lam_full - lam_trunc
    boundary = Fraction(gs[keep - 1]) if keep - 1 < len(gs) else Fraction(0)
    verdict = ("TRUNCATION_ROBUST (exact): kept sector decouples "
               f"(boundary coupling g = {boundary})" if shift == 0 else
               "TRUNCATION_ARTIFACT (exact shift quantified): the "
               "'emergent constant' depends on the dropped sector")
    return {"lambda_full": lam_full, "lambda_trunc": lam_trunc,
            "shift": shift, "boundary_coupling": boundary,
            "verdict": verdict}


def gate(truncated_only: bool, decoupling_certificate: bool,
         shift_bound: Optional[Fraction] = None) -> str:
    """Claims gate: what may be asserted about an emergent constant
    derived in a truncated sector (SPEC sections 2 and 4)."""
    if decoupling_certificate:
        return ("CLAIM_PERMITTED: property of the framework "
                "(decoupling certified)")
    if shift_bound is not None:
        return (f"CLAIM_PERMITTED_WITH_INTERVAL: property up to certified "
                f"shift bound {shift_bound}")
    if truncated_only:
        return ("TRUNCATION_UNAUDITED: no decoupling certificate and no "
                "shift bound -- 'emergent' may be artifact; claim not "
                "promotable")
    return "AUDIT_INCOMPLETE"
