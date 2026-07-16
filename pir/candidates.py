"""Candidate lattice + GVAR rules (Stage 2 / P5a).

A grammar **compatibility matrix** over competing candidate families, driven by
declarative **GVAR rules**. Rules emit *candidate facts and test obligations
only* — never a verdict on their own. The lattice then reads the compatible set
and the declared interventions and returns a SPEC-locked verdict:

* >=2 compatible families, no in-scope discriminating intervention
  -> OBSERVATIONALLY_EQUIVALENT;
* >=2 compatible but the discriminator is declared-not-executed
  -> NONIDENTIFIABLE(insufficient intervention);
* exactly one compatible family -> that family is identified (PERMITTED);
* none compatible -> REJECTED.

The rule format is JSON (the repo is stdlib-only; the "YAML rule schema" of the
backlog is realized as JSON, validated by :mod:`pir.jsonschema_mini`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from .canonical import content_id
from .jsonschema_mini import validate as _validate_schema
from .models import AnalyzerRef, Fact, Hypothesis
from .types import PassTag

# JSON schema for a single GVAR rule.
GVAR_RULE_SCHEMA = {
    "type": "object",
    "required": ["rule_id", "family", "requires_predicates"],
    "additionalProperties": False,
    "properties": {
        "rule_id": {"type": "string"},
        "family": {"type": "string"},
        "requires_predicates": {"type": "array", "items": {"type": "string"}},
        "forbids_predicates": {"type": "array", "items": {"type": "string"}},
        "test_obligation": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "intervention": {"type": "string"},
                "separates": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
}


def validate_rule(rule: Dict) -> None:
    _validate_schema(GVAR_RULE_SCHEMA, rule)


@dataclass
class Candidate:
    family: str
    rule_id: str
    test_obligation: Optional[Dict] = None


def apply_rules(rules: List[Dict], predicates: Set[str]) -> List[Candidate]:
    """A rule fires when all ``requires_predicates`` hold and no
    ``forbids_predicates`` do. Firing emits one candidate + its test obligation
    (an intervention that would discriminate it from named rivals)."""
    out: List[Candidate] = []
    for rule in rules:
        validate_rule(rule)
        req = set(rule["requires_predicates"])
        forb = set(rule.get("forbids_predicates", []))
        if req <= predicates and not (forb & predicates):
            out.append(Candidate(family=rule["family"], rule_id=rule["rule_id"],
                                 test_obligation=rule.get("test_obligation")))
    return out


@dataclass
class LatticeResult:
    verdict: str
    compatible: List[str]
    obligations: List[Dict] = field(default_factory=list)
    detail: Dict = field(default_factory=dict)


def evaluate(candidates: List[Candidate], declared_interventions: List[str]) -> LatticeResult:
    families = sorted({c.family for c in candidates})
    obligations = [c.test_obligation for c in candidates if c.test_obligation]
    if not families:
        return LatticeResult("REJECTED", [], obligations,
                             {"reason": "no candidate grammar compatible with the facts"})
    if len(families) == 1:
        return LatticeResult("PERMITTED", families, obligations,
                             {"identified_family": families[0]})
    # >=2 compatible families: is there a declared, in-scope discriminator?
    separators = {o["intervention"] for o in obligations if o and "intervention" in o}
    in_scope = separators & set(declared_interventions)
    if in_scope:
        return LatticeResult("NONIDENTIFIABLE", families, obligations,
                             {"cause": "insufficient intervention "
                              "(discriminator declared, not executed)",
                              "separating_interventions": sorted(in_scope)})
    return LatticeResult("OBSERVATIONALLY_EQUIVALENT", families, obligations,
                         {"class_members": families,
                          "required_interventions": sorted(separators)})


def to_hypotheses(candidates: List[Candidate], eqc_id: str,
                  derived_from_facts=()) -> List[Hypothesis]:
    """Emit L3 candidate hypotheses (retained in parallel, never pruned)."""
    hyps = []
    for c in sorted(candidates, key=lambda x: x.family):
        hyps.append(Hypothesis(
            hypothesis_id=f"hyp_{eqc_id}_{c.family}",
            family=c.family, status="OBSERVATIONALLY_EQUIVALENT_MEMBER",
            equivalence_class_id=eqc_id, derived_from_facts=tuple(derived_from_facts),
            distinguishing_interventions=(
                ({"intervention_id": c.test_obligation["intervention"],
                  "predicted_separation": ",".join(c.test_obligation.get("separates", []))},)
                if c.test_obligation and "intervention" in c.test_obligation else ()),
        ))
    return hyps


def lattice_fact(result: LatticeResult, eqc_id: str) -> Fact:
    """Lower a lattice evaluation into a SPEC-locked PIR verdict fact."""
    analyzer = AnalyzerRef(id="pir.candidates", version="0.1.0", tag=PassTag.SOUND)
    content = {"subject": f"equivalence_class:{eqc_id}",
               "compatible_families": result.compatible, **result.detail}
    fid = content_id("fct", {"eqc": eqc_id, "verdict": result.verdict,
                             "compat": result.compatible})
    return Fact(
        fact_id=fid, pir_level="L3", evidence_level="E1", layer="UNIVERSAL",
        namespace="invariant", status="SUPPORTED", analyzer=analyzer,
        content=content, created_at="1970-01-01T00:00:00Z",
        verdict=result.verdict,
        source_spans=({"artifact_id": "pir.candidates", "span": eqc_id},),
    )
