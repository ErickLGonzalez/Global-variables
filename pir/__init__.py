"""PIR (Physics Intermediate Representation) v0.1 -- evidence substrate.

Stage 1 of the adjudicated Physics Reverse-Engineering Architecture. PIR is an
*evidence substrate*, not a proof engine: it records what was measured (L0),
what was done (L1), what was certified (L2), and which grammars remain in play
(L3), each fact carrying orthogonal representation (L) and warrant (E)
coordinates, full provenance, and assumption taint. The atlas engine never
reads raw datasets directly -- it reads certified PIR facts.

Public surface:

* vocabularies -- :mod:`pir.types`
* models       -- :mod:`pir.models`
* namespaces   -- :mod:`pir.namespaces`
* canonical    -- :mod:`pir.canonical`
* store/prov   -- :mod:`pir.provenance`
* pass layer   -- :mod:`pir.passes`
* validation   -- :mod:`pir.jsonschema_mini`
"""

from __future__ import annotations

__version__ = "0.1.0"

from . import canonical, jsonschema_mini, models, namespaces, passes, provenance, types
# Stage 2/3 subsystems (import-safe; each is additive over the substrate).
from . import analyzers, candidates, diff, domains, fingerprints, forward
from . import intervention_search, runtime, symbolic
from .models import (
    AnalyzerRef,
    Artifact,
    Event,
    Fact,
    Hypothesis,
    Intervention,
    PIRValidationError,
    Port,
    ProvenanceRecord,
    Warning_,
)
from .provenance import (
    AppendOnlyViolation,
    DowngradeRecord,
    FactStore,
    ProvenanceCycle,
)
from .passes import PassHonestyViolation, PassRegistry, PassSpec
from .namespaces import IllegalNamespacePromotion, NamespaceTransform
from .types import (
    CandidateClass,
    EvidenceLevel,
    FactStatus,
    HypothesisStatus,
    Layer,
    Namespace,
    PassTag,
    PirLevel,
    Verdict,
)

__all__ = [
    "__version__",
    "canonical", "jsonschema_mini", "models", "namespaces", "passes",
    "provenance", "types",
    "AnalyzerRef", "Artifact", "Event", "Fact", "Hypothesis", "Intervention",
    "PIRValidationError", "Port", "ProvenanceRecord", "Warning_",
    "AppendOnlyViolation", "DowngradeRecord", "FactStore", "ProvenanceCycle",
    "PassHonestyViolation", "PassRegistry", "PassSpec",
    "IllegalNamespacePromotion", "NamespaceTransform",
    "CandidateClass", "EvidenceLevel", "FactStatus", "HypothesisStatus",
    "Layer", "Namespace", "PassTag", "PirLevel", "Verdict",
]
