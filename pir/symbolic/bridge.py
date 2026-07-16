"""Constraint → PIR-fact bridge (Stage 2 / P4).

Turns an exact linear feasibility result (:mod:`pir.symbolic.linear`) into a PIR
fact, filling the substrate's reserved ``witness`` (SAT model) and
``impossibility_certificate`` (Farkas / UNSAT core) fields, and **quarantining
solver output by evidence class**:

* exact rational arithmetic  -> E0, SOUND (the certificate is checkable);
* numeric / floating solver   -> E3, HEURISTIC + located warning (never promotable
  as an exact certificate, even if the same shape).

Verdict mapping (SPEC-locked): UNIQUE -> FORCED, UNDERDETERMINED ->
NONIDENTIFIABLE, INCONSISTENT -> REJECTED.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Optional

from ..canonical import content_id
from ..models import AnalyzerRef, Fact, Warning_
from ..types import PassTag


def _frac_str(x) -> str:
    x = x if isinstance(x, Fraction) else Fraction(x)
    return f"{x.numerator}/{x.denominator}"


def _vec_strs(v: List) -> List[str]:
    return [_frac_str(x) for x in v]


_VERDICT = {"UNIQUE": "FORCED", "UNDERDETERMINED": "NONIDENTIFIABLE",
            "INCONSISTENT": "REJECTED"}


def constraint_fact(result: Dict, subject: str, assumptions=(),
                    arithmetic: str = "exact", cause: str = "") -> Fact:
    """Build a PIR fact from a :func:`pir.symbolic.linear.solve` result."""
    status = result["status"]
    verdict = _VERDICT[status]
    exact = arithmetic == "exact"
    evidence = "E0" if exact else "E3"
    tag = PassTag.SOUND if exact else PassTag.HEURISTIC
    warning = None if exact else (
        f"numeric solver output quarantined: evidence capped at E3, not an "
        f"exact certificate (arithmetic={arithmetic}).")

    content: Dict = {"subject": subject, "status": status,
                     "rank": result.get("rank"), "n_vars": result.get("n_vars"),
                     "arithmetic": arithmetic}
    witness = None
    impossibility = None

    if status == "UNIQUE":
        witness = {"kind": "sat_model_unique", "solution": _vec_strs(result["solution"])}
        content["forced_solution"] = witness["solution"]
    elif status == "UNDERDETERMINED":
        witness = {"kind": "null_space_directions",
                   "free_directions": [_vec_strs(v) for v in result["null_space"]]}
        content["cause"] = cause or "rank-deficient system (free directions exist)"
        content["d_identifiable"] = result["n_vars"] - result["rank"]
    else:  # INCONSISTENT
        impossibility = {"kind": "farkas_certificate",
                         "y": _vec_strs(result["farkas"]),
                         "statement": "yᵀA = 0 and yᵀb ≠ 0 ⇒ no solution exists"}

    analyzer = AnalyzerRef(id="pir.symbolic.bridge", version="0.1.0", tag=tag)
    fid = content_id("fct", {"subject": subject, "status": status,
                             "witness": witness, "impossibility": impossibility,
                             "arithmetic": arithmetic})
    warns = (Warning_(location="pir.symbolic.bridge", message=warning),) if warning else ()
    return Fact(
        fact_id=fid, pir_level="L2", evidence_level=evidence, layer="UNIVERSAL",
        namespace="invariant", status="SUPPORTED", analyzer=analyzer,
        content=content, created_at="1970-01-01T00:00:00Z",
        assumptions=tuple(assumptions), warnings=warns, verdict=verdict,
        witness=witness, impossibility_certificate=impossibility,
        source_spans=({"artifact_id": "pir.symbolic", "span": subject},),
    )
