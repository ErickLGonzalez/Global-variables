"""Exact-certificate benchmark lowerings: B1, B2, B3 -> PIR facts.

Companion to :mod:`pir.domains.b9`. Where B9 is simulation-conditioned (E3),
B1/B2/B3 carry exact-rational certificates, so their lowered facts are E0 / SOUND
and fill the reserved ``witness`` / ``impossibility_certificate`` fields with the
benchmark's own exact witnesses (Schur pivots, kernel recurrences, negative
pivots). Each verdict is RE-DERIVED from the stored quantities:

* B1 T1 FORCED  iff rank == extended_rank (flat extension);
* B1 T3 / B2 T5 REJECTED iff a Schur pivot is negative (exact indefiniteness);
* B2 T1 CPTP certified iff all pivots >= 0 and trace-preserving;
* B3 T3 NONIDENTIFIABLE iff d_identifiable = n_quantities - constraint_rank > 0.

m_layer_stipulations become assumption-taint (ADR-0002). No benchmark code,
verdict, certificate, or atlas cell is touched; the lowerings only read the
committed certificates.
"""

from __future__ import annotations

import json
import os
from fractions import Fraction
from typing import Dict, List

from ..canonical import content_id
from ..models import AnalyzerRef, Fact
from ..provenance import FactStore

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ANALYZER = AnalyzerRef(id="pir.domains.exact_benchmarks", version="0.1.0", tag="SOUND")


def load_certificate(name: str) -> dict:
    with open(os.path.join(_ROOT, "certificates", f"{name}_certificate.json")) as f:
        return json.load(f)


def _assumptions(cert: dict, bench: str) -> tuple:
    return tuple(f"asm:{bench}_mlayer_{i}"
                 for i, _ in enumerate(cert.get("m_layer_stipulations", [])))


def _fact(bench: str, test: str, verdict: str, content: Dict, assumptions,
          witness=None, impossibility=None, namespace="invariant") -> Fact:
    fid = content_id("fct", {"b": bench, "t": test, "v": verdict, "c": content})
    return Fact(
        fact_id=fid, pir_level="L2", evidence_level="E0", layer="DOMAIN",
        namespace=namespace, status="SUPPORTED", analyzer=_ANALYZER,
        content={"subject": f"{bench}:{test}", **content},
        created_at="1970-01-01T00:00:00Z", assumptions=tuple(assumptions),
        measurement_interface=(f"cal:{bench}_exact_inputs",),
        source_spans=({"artifact_id": f"{bench}_certificate", "span": test},),
        verdict=verdict, witness=witness, impossibility_certificate=impossibility)


def _neg_pivot(pivots: List[str]) -> bool:
    return any(Fraction(p) < 0 for p in pivots)


# --------------------------------------------------------------------------- #
def lower_b1(cert: dict) -> List[Fact]:
    r = cert["results"]; asm = _assumptions(cert, "b1"); out = []
    t1 = r["T1_forced_tail"]
    forced = t1["rank"] == t1["extended_rank"]
    out.append(_fact("b1", "T1_forced_tail", "FORCED" if forced else "PERMITTED",
                     {"rank": t1["rank"], "extended_rank": t1["extended_rank"],
                      "flat_extension": forced}, asm,
                     witness={"kind": "kernel_recurrence", "monic": t1["recurrence_monic"],
                              "schur_pivots": t1["schur_pivots_extended"]}))
    t2 = r["T2_permitted_hole"]
    out.append(_fact("b1", "T2_permitted_hole", "PERMITTED",
                     {"certified_inner_interval": t2["certified_inner_interval"],
                      "witness_value": t2["witness_value"]}, asm,
                     witness={"kind": "certified_interval",
                              "inner": t2["certified_inner_interval"]}))
    t3 = r["T3_negative_control"]
    piv = t3["witness_pivot"]
    out.append(_fact("b1", "T3_negative_control",
                     "REJECTED" if Fraction(piv) < 0 else "PERMITTED",
                     {"witness_pivot": piv}, asm,
                     impossibility={"kind": "negative_schur_pivot", "pivot": piv,
                                    "statement": "exact negative pivot witnesses "
                                    "non-positivity (moment matrix not PSD)"}))
    return out


def lower_b2(cert: dict) -> List[Fact]:
    r = cert["results"]; asm = _assumptions(cert, "b2"); out = []
    t1 = r["T1_cptp_audit"]
    cptp = (not _neg_pivot(t1["schur_pivots"])) and t1["trace_preserving"]
    out.append(_fact("b2", "T1_cptp_audit", "PERMITTED" if cptp else "REJECTED",
                     {"psd_status": t1["psd_status"], "rank": t1["rank"],
                      "trace_preserving": t1["trace_preserving"],
                      "cptp_certified": cptp}, asm,
                     witness={"kind": "cptp_pivots", "schur_pivots": t1["schur_pivots"]},
                     namespace="domain"))
    for key in ("T2_tp_forced", "T3_rank1_forced"):
        t = r[key]
        out.append(_fact("b2", key, "FORCED",
                         {"mechanism": t["mechanism"], "value": t["value"]}, asm,
                         witness={"kind": "exact_completion", "value": t["value"]},
                         namespace="domain"))
    t5 = r["T5_negative_control"]
    piv = t5["witness_pivot"]
    out.append(_fact("b2", "T5_negative_control",
                     "REJECTED" if Fraction(piv) < 0 else "PERMITTED",
                     {"witness_pivot": piv}, asm,
                     impossibility={"kind": "negative_schur_pivot", "pivot": piv,
                                    "statement": "corrupted Choi rejected: exact "
                                    "negative pivot (not completely positive)"},
                     namespace="domain"))
    return out


def lower_b3(cert: dict) -> List[Fact]:
    r = cert["results"]; asm = _assumptions(cert, "b3"); out = []
    t3 = r["T3_d_identifiable"]
    d = t3["n_quantities"] - t3["constraint_rank"]
    out.append(_fact("b3", "T3_d_identifiable",
                     "NONIDENTIFIABLE" if d > 0 else "FORCED",
                     {"n_quantities": t3["n_quantities"],
                      "constraint_rank": t3["constraint_rank"],
                      "d_identifiable": d,
                      "cause": "free directions in the constraint Jacobian" if d > 0 else "uniquely identified"},
                     asm, witness={"kind": "rank_deficit", "d_identifiable": d}))
    t5 = r["T5_negative_control"]
    out.append(_fact("b3", "T5_negative_control", "REJECTED",
                     {"broken_residuals": t5["broken_residuals"]}, asm,
                     impossibility={"kind": "broken_relations",
                                    "residuals": t5["broken_residuals"],
                                    "statement": "perturbed inputs break exact "
                                    "electroweak relations (nonzero residuals)"}))
    return out


_LOWER = {"b1": lower_b1, "b2": lower_b2, "b3": lower_b3}


def lower(bench: str) -> List[Fact]:
    return _LOWER[bench](load_certificate(bench))


def reproduced_verdicts(bench: str) -> Dict[str, str]:
    return {f.source_spans[0]["span"]: (f.verdict.value if f.verdict else None)
            for f in lower(bench)}


def suite_store(benches=("b1", "b2", "b3")) -> FactStore:
    st = FactStore()
    for b in benches:
        for f in lower(b):
            st.add_fact(f)
    return st
