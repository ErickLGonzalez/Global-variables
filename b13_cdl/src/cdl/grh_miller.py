"""M1 / cdl-rh-grh: deterministic Miller primality test under GRH.

Bases tested: all a in [2, min(n-2, floor(2*ln(n)^2))]  (Bach's GRH bound).

EPISTEMIC ASYMMETRY (the whole point of this pipeline):
  - COMPOSITE verdict: UNCONDITIONAL. The witness base is an independently
    checkable certificate (SAT-witness analogue).
  - PRIME verdict: CONDITIONAL(GRH). No witness exists in the GRH window; the
    verdict is certified only under the stipulated truth of GRH.

Exact integer arithmetic throughout (SOUND).
"""
from __future__ import annotations
import math
from .common import make_certificate


def _miller_witness(a: int, n: int) -> bool:
    """True iff a is a Miller witness for compositeness of n (n odd, >2)."""
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return False
    for _ in range(r - 1):
        x = x * x % n
        if x == n - 1:
            return False
    return True


def classify(n: int):
    """Return (verdict, witness_or_None, bases_tested)."""
    if n < 2:
        return ("NOT_PRIME (trivial)", None, 0)
    if n in (2, 3):
        return ("PRIME (UNCONDITIONAL, trivial)", None, 0)
    if n % 2 == 0:
        return ("COMPOSITE (UNCONDITIONAL)", 2, 0)
    bound = min(n - 2, int(2 * math.log(n) ** 2))
    for a in range(2, bound + 1):
        if _miller_witness(a, n):
            return ("COMPOSITE (UNCONDITIONAL)", a, bound)
    return ("PRIME CONDITIONAL(GRH)", None, bound)


def run(test_numbers=None):
    tests = test_numbers or [
        97, 561, 2047, 1373653, 25326001,          # Carmichael / strong-pseudoprime stress
        67280421310721,                            # Fermat factor, prime
        3215031751,                                # smallest strong pseudoprime to bases 2,3,5,7
        2 ** 61 - 1,                               # Mersenne prime
    ]
    results = []
    for n in tests:
        verdict, witness, bound = classify(n)
        results.append({"n": str(n), "verdict": verdict,
                        "witness_base": witness, "grh_base_bound": bound})

    return make_certificate(
        pipeline="grh_miller", entry_id="cdl-rh-grh",
        soundness_tag="SOUND",
        stipulations=[
            {"name": "GRH", "assumed": True,
             "source": "Stipulated only for PRIME verdicts; COMPOSITE verdicts are unconditional"},
            {"name": "witness_bound", "assumed": "a <= 2*ln(n)^2",
             "source": "Miller (1976); Bach (1990)"},
        ],
        inputs={"test_set_size": len(tests)},
        verdict="Mixed per-n verdicts; see verdict_detail (asymmetry preserved)",
        verdict_detail={"results": results},
        witness={"type": "miller-witness-bases",
                 "statement": "each COMPOSITE row carries a base a that any third party "
                              "can re-verify with one modular exponentiation chain"},
        notes="AKS (2002) provides the unconditional-polynomial-time upgrade path; this "
              "pipeline exists to encode the CONDITIONAL(GRH) verdict shape, not for speed.",
    )
