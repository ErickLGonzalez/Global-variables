"""The three priority analyzers (Stage 2 / P3).

Each is an :class:`pir.runtime.AnalyzerPass` factory. They read facts already in
the store and emit new, provenance-bearing facts -- never mutating inputs. All
verdicts use the SPEC-locked vocabulary; conditionality rides as assumption-taint
(ADR-0002).

* :func:`measurement_provenance_pass` -- audits that each DOMAIN/MEASUREMENT fact
  rests on a *promotable* calibration route; flags facts resting on a
  non-promotable route (the B9 Gibbs blind spot) as APPARATUS_LIMITED.
* :func:`observational_equivalence_pass` -- partitions competing hypotheses into
  equivalence classes under the declared interventions; a class with >=2 members
  and no distinguishing intervention emits OBSERVATIONALLY_EQUIVALENT, otherwise
  NONIDENTIFIABLE(insufficient intervention).
* :func:`global_variable_candidate_pass` -- proposes GLOBAL_CANDIDATE facts for a
  canonical invariant shared by facts from >=2 distinct namespaces/domains.
"""

from __future__ import annotations

from typing import Dict, List

from .canonical import content_id
from .models import AnalyzerRef, Fact, Warning_
from .provenance import FactStore
from .runtime import AnalyzerPass
from .types import PassTag

try:
    from .domains.circuit_semantics import is_promotable_route, CALIBRATION_ROUTES
except Exception:  # pragma: no cover
    CALIBRATION_ROUTES = {"cal:spectroscopy_route": True, "cal:gibbs_route": False}
    def is_promotable_route(r):  # type: ignore
        return CALIBRATION_ROUTES.get(r, True)


def _mk_fact(analyzer_id, tag, evidence, verdict, content, assumptions=(),
             layer="UNIVERSAL", namespace="analyst", warning=None, mi=()):
    warns = (Warning_(location=analyzer_id, message=warning),) if warning else ()
    analyzer = AnalyzerRef(id=analyzer_id, version="0.1.0", tag=tag)
    fid = content_id("fct", {"a": analyzer_id, "c": content, "v": verdict,
                             "asm": list(assumptions)})
    return Fact(
        fact_id=fid, pir_level="L2", evidence_level=evidence, layer=layer,
        namespace=namespace, status="SUPPORTED", analyzer=analyzer, content=content,
        created_at="1970-01-01T00:00:00Z", assumptions=tuple(assumptions),
        measurement_interface=tuple(mi), warnings=warns, verdict=verdict,
        source_spans=({"artifact_id": analyzer_id, "span": content.get("subject", "analysis")},),
    )


# --------------------------------------------------------------------------- #
# 1. MeasurementProvenanceAnalyzer                                            #
# --------------------------------------------------------------------------- #
def measurement_provenance_pass() -> AnalyzerPass:
    def fn(store: FactStore, ctx: Dict[str, List[Fact]]) -> List[Fact]:
        out: List[Fact] = []
        for f in sorted(store.facts(), key=lambda x: x.fact_id):
            if f.layer.value not in ("DOMAIN", "MEASUREMENT"):
                continue
            routes = list(f.measurement_interface)
            nonpromotable = [r for r in routes
                             if r in CALIBRATION_ROUTES and not is_promotable_route(r)]
            if nonpromotable:
                out.append(_mk_fact(
                    "MeasurementProvenanceAnalyzer", PassTag.SOUND, "E1",
                    "APPARATUS_LIMITED",
                    {"subject": f"provenance:{f.fact_id}", "audited_fact": f.fact_id,
                     "nonpromotable_routes": nonpromotable},
                    warning=None, mi=routes,
                    layer="MEASUREMENT", namespace="analyst"))
        return out
    return AnalyzerPass(id="MeasurementProvenanceAnalyzer", version="0.1.0",
                        tag=PassTag.SOUND, fn=fn,
                        description="flags facts resting on non-promotable routes")


# --------------------------------------------------------------------------- #
# 2. ObservationalEquivalenceAnalyzer                                         #
# --------------------------------------------------------------------------- #
def observational_equivalence_pass(hypotheses: List[Dict],
                                   declared_interventions: List[str]) -> AnalyzerPass:
    """``hypotheses`` = [{id, equivalence_class_id, compatibility:{fact_id:relation},
    distinguishing_interventions:[id...]}]. Interventions in
    ``declared_interventions`` are the ones actually in scope."""
    def fn(store: FactStore, ctx: Dict[str, List[Fact]]) -> List[Fact]:
        classes: Dict[str, List[Dict]] = {}
        for h in hypotheses:
            classes.setdefault(h.get("equivalence_class_id", h["id"]), []).append(h)
        out: List[Fact] = []
        for cid, members in sorted(classes.items()):
            if len(members) < 2:
                continue
            # Is there a declared, in-scope intervention that separates them?
            distinguishers = set()
            for h in members:
                distinguishers |= set(h.get("distinguishing_interventions", []))
            in_scope = distinguishers & set(declared_interventions)
            if in_scope:
                verdict = "NONIDENTIFIABLE"  # separable in principle, not yet run
                detail = {"cause": "insufficient intervention (declared but not executed)",
                          "separating_interventions": sorted(in_scope)}
            else:
                verdict = "OBSERVATIONALLY_EQUIVALENT"
                detail = {"class": cid, "members": sorted(h["id"] for h in members)}
            out.append(_mk_fact(
                "ObservationalEquivalenceAnalyzer", PassTag.SOUND, "E1", verdict,
                {"subject": f"equivalence_class:{cid}", **detail,
                 "members": sorted(h["id"] for h in members)}))
        return out
    return AnalyzerPass(id="ObservationalEquivalenceAnalyzer", version="0.1.0",
                        tag=PassTag.SOUND, fn=fn,
                        description="partitions hypotheses into OE classes")


# --------------------------------------------------------------------------- #
# 3. GlobalVariableCandidateAnalyzer                                          #
# --------------------------------------------------------------------------- #
def global_variable_candidate_pass(invariant_key: str = "invariant_hash") -> AnalyzerPass:
    """Propose a GLOBAL_CANDIDATE when the same canonical invariant value appears
    in facts drawn from >=2 distinct namespaces (cross-domain invariance -- the
    program's core signal that a constant may be a global structural datum)."""
    def fn(store: FactStore, ctx: Dict[str, List[Fact]]) -> List[Fact]:
        by_inv: Dict[str, set] = {}
        carriers: Dict[str, List[str]] = {}
        for f in sorted(store.facts(), key=lambda x: x.fact_id):
            inv = f.content.get(invariant_key)
            if inv is None:
                continue
            by_inv.setdefault(inv, set()).add(f.namespace.value)
            carriers.setdefault(inv, []).append(f.fact_id)
        out: List[Fact] = []
        for inv, namespaces in sorted(by_inv.items()):
            if len(namespaces) >= 2:
                out.append(_mk_fact(
                    "GlobalVariableCandidateAnalyzer", PassTag.HEURISTIC, "E3",
                    None,   # candidate_class taxonomy is NOT a verdict (locked)
                    {"subject": f"global_candidate:{inv}", "invariant": inv,
                     "candidate_class": "GLOBAL_CANDIDATE",
                     "shared_across_namespaces": sorted(namespaces),
                     "carrier_facts": sorted(carriers[inv])},
                    namespace="invariant", layer="UNIVERSAL",
                    warning=("HEURISTIC: cross-namespace invariance is a candidate "
                             "signal, not a promotion; test obligation = an "
                             "intervention that could break the shared invariant.")))
        return out
    return AnalyzerPass(id="GlobalVariableCandidateAnalyzer", version="0.1.0",
                        tag=PassTag.HEURISTIC, fn=fn,
                        description="proposes cross-domain GLOBAL_CANDIDATE invariants")
