"""M5 / cdl-bsd-tunnell: congruent-number decision via Tunnell's theorem.

For squarefree n:
  odd n:  A = #{(x,y,z) in Z^3 : 2x^2 + y^2 + 8z^2  = n}
          B = #{(x,y,z) in Z^3 : 2x^2 + y^2 + 32z^2 = n}
  even n: A = #{(x,y,z) in Z^3 : 4x^2 + y^2 + 8z^2  = n/2}
          B = #{(x,y,z) in Z^3 : 4x^2 + y^2 + 32z^2 = n/2}

Tunnell (1983), unconditional direction: n congruent  =>  A = 2B.
Converse (A = 2B => n congruent) requires weak BSD for E_n: y^2 = x^3 - n^2 x.

EPISTEMIC ASYMMETRY:
  - A != 2B  =>  NOT_CONGRUENT, UNCONDITIONAL; (A, B) counts are the witness.
  - A == 2B  =>  CONGRUENT, CONDITIONAL(BSD).

Exhaustive exact integer counting (SOUND).
"""
from __future__ import annotations
import math
from .common import make_certificate


def _squarefree(n: int) -> bool:
    i = 2
    while i * i <= n:
        if n % (i * i) == 0:
            return False
        i += 1
    return True


def _count(cx: int, cy: int, cz: int, target: int) -> int:
    """#{(x,y,z) in Z^3 : cx*x^2 + cy*y^2 + cz*z^2 = target}, exhaustive and exact."""
    count = 0
    xmax = math.isqrt(target // cx)
    for x in range(-xmax, xmax + 1):
        rx = target - cx * x * x
        if rx < 0:
            continue
        zmax = math.isqrt(rx // cz)
        for z in range(-zmax, zmax + 1):
            ry = rx - cz * z * z
            if ry < 0:
                continue
            y = math.isqrt(ry)
            if y * y == ry:
                count += 2 if y > 0 else 1   # +y and -y
    return count


def classify(n: int):
    if n <= 0 or not _squarefree(n):
        return {"n": n, "verdict": "OUT_OF_SCOPE (need positive squarefree n)"}
    if n % 2 == 1:
        A = _count(2, 1, 8, n)
        B = _count(2, 1, 32, n)
    else:
        A = _count(4, 1, 8, n // 2)
        B = _count(4, 1, 32, n // 2)
    if A != 2 * B:
        return {"n": n, "A": A, "B": B,
                "verdict": "NOT_CONGRUENT (UNCONDITIONAL, Tunnell forward direction)",
                "witness": {"A": A, "B": B, "relation": "A != 2B"}}
    return {"n": n, "A": A, "B": B,
            "verdict": "CONGRUENT CONDITIONAL(BSD)",
            "witness": None}


def run(test_numbers=None):
    tests = test_numbers or [1, 2, 3, 5, 6, 7, 10, 13, 14, 15, 21, 22, 23, 30, 31, 34, 41, 157]
    results = [classify(n) for n in tests]
    known_congruent = {5, 6, 7, 13, 14, 15, 21, 22, 23, 30, 31, 34, 41, 157}
    consistency = all(
        (r["n"] in known_congruent) == r["verdict"].startswith("CONGRUENT")
        for r in results if "A" in r)

    return make_certificate(
        pipeline="tunnell_bsd", entry_id="cdl-bsd-tunnell",
        soundness_tag="SOUND",
        stipulations=[
            {"name": "weak_BSD_for_E_n", "assumed": True,
             "source": "Stipulated only for CONGRUENT verdicts; NOT_CONGRUENT rows are "
                       "unconditional (Tunnell 1983 forward direction)"},
        ],
        inputs={"test_set": tests},
        verdict="Mixed per-n verdicts; see verdict_detail (asymmetry preserved)",
        verdict_detail={"results": results,
                        "cross_check_vs_known_table": "PASS" if consistency else "FAIL"},
        witness={"type": "ternary-form-counts",
                 "statement": "each NOT_CONGRUENT row carries exact (A,B) counts, "
                              "re-verifiable by exhaustive enumeration"},
        notes="Negative-control: cross-checked against the classical congruent-number "
              "table (5,6,7 congruent; 1,2,3 not; 157 the famous Zagier example).",
    )
