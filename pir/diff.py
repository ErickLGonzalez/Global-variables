"""Cross-domain PIR-Diff (Stage 2 / S3 / P8).

Compare two lowered structures at the level of **canonical invariants** and
report shared *motifs* with the BinDiff discipline the substrate mandates:
**similarity and confidence are separate numbers with a named correlator**
(SPEC §5 feature-level equality — never an ontology-identity claim). Apparatus
differences are listed explicitly, and the least-cost discriminating
intervention is proposed.

* **similarity** — fraction of comparable invariant keys whose values match;
* **confidence** — coverage: fraction of the union of keys that were actually
  comparable (few shared keys => low confidence even at similarity 1.0);
* **correlator** — the named matching algorithm ("canonical-invariant-match/0.1").
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .intervention_search import AdmissibleIntervention, least_cost_discriminator

CORRELATOR = "canonical-invariant-match/0.1"
_INVARIANT_KEYS = ("symmetry_group", "rank_sequence", "positivity_cone",
                   "spectral_class")


@dataclass
class DiffResult:
    similarity: float
    confidence: float
    correlator: str
    shared_motifs: List[str]
    divergent: List[str]
    apparatus_differences: List[Dict]
    least_cost_discriminator: Optional[str]
    ontology_claim: str = ("feature-level canonical-invariant equality only; "
                           "no ontology-identity claim (SPEC §5)")

    def to_dict(self):
        return {"similarity": self.similarity, "confidence": self.confidence,
                "correlator": self.correlator, "shared_motifs": self.shared_motifs,
                "divergent": self.divergent,
                "apparatus_differences": self.apparatus_differences,
                "least_cost_discriminator": self.least_cost_discriminator,
                "ontology_claim": self.ontology_claim}


def _apparatus_differences(a: Dict, b: Dict) -> List[Dict]:
    keys = sorted(set(a) | set(b))
    return [{"key": k, "a": a.get(k), "b": b.get(k)}
            for k in keys if a.get(k) != b.get(k)]


def cross_domain_diff(features_a: Dict, features_b: Dict,
                      apparatus_a: Dict, apparatus_b: Dict,
                      interventions: Optional[List[AdmissibleIntervention]] = None,
                      hyp_ids: Optional[List[str]] = None) -> DiffResult:
    comparable = [k for k in _INVARIANT_KEYS if k in features_a and k in features_b]
    union = [k for k in _INVARIANT_KEYS if k in features_a or k in features_b]
    shared = [k for k in comparable if features_a[k] == features_b[k]]
    divergent = [k for k in comparable if features_a[k] != features_b[k]]

    similarity = (len(shared) / len(comparable)) if comparable else 0.0
    confidence = (len(comparable) / len(union)) if union else 0.0

    disc = None
    if interventions and hyp_ids:
        disc = least_cost_discriminator(interventions, hyp_ids)

    return DiffResult(
        similarity=round(similarity, 6), confidence=round(confidence, 6),
        correlator=CORRELATOR, shared_motifs=shared, divergent=divergent,
        apparatus_differences=_apparatus_differences(apparatus_a, apparatus_b),
        least_cost_discriminator=disc)
