"""B9 circuit-domain lowering: the Nobel decompilation as PIR facts.

Stage 2 / P2: lower the committed B9 certificate into PIR L0/L1/L2 and
**re-derive** B9's verdicts from the stored quantities. This proves the PIR
substrate consumes a real benchmark end-to-end without touching B9's code or
its certificate, and without any atlas change.

Two things make this a genuine reproduction rather than a copy:

1. The FDT gate is re-applied here (``FDT_THRESHOLD`` = 0.15, identical to
   ``b9_circuit/estimate.py``): a relative residual below the threshold is
   EQUILIBRIUM_CONSISTENT, at or above it is EQUILIBRIUM_REJECTED. Feeding B9's
   own residuals back through this gate must reproduce B9's per-test verdicts.

2. B9's ``m_layer_stipulations`` become PIR **assumptions** (asm:*), exactly the
   conditionality=taint model adopted in ADR-0002. The T3 Gibbs-route blind spot
   and the T4 model-order inversion are then first-class: invalidating
   ``asm:hard_wall_truncation`` downgrades the T6 held-out prediction that rests
   on it, via the store's invalidation traversal.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

from ..canonical import content_id
from ..models import AnalyzerRef, Artifact, Event, Fact, Port, Warning_
from ..provenance import FactStore

FDT_THRESHOLD = 0.15  # mirror of b9_circuit/estimate.py

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_B9_CERT = os.path.join(_ROOT, "certificates", "b9_certificate.json")

_ANALYZER = AnalyzerRef(id="pir.domains.b9", version="0.1.0", tag="HEURISTIC")
_ANALYZER_EXACT = AnalyzerRef(id="pir.domains.b9", version="0.1.0", tag="SOUND")

# B9's four stipulations, keyed to the assumption id each becomes and the tests
# that rest on it. Names match certificates/b9_certificate.json phrasing.
_STIPULATION_ASSUMPTIONS = {
    "linearized_well": "asm:linearized_well",
    "gibbs_route": "asm:gibbs_route",
    "1d_reduction": "asm:1d_reduction",
    "hard_wall_truncation": "asm:hard_wall_truncation",
}

_MEASUREMENT = ("cal:spectroscopy_route",)


def fdt_verdict(relative_residual: float) -> str:
    """Reproduce B9's FDT gate verdict from a relative residual."""
    return ("EQUILIBRIUM_CONSISTENT" if relative_residual < FDT_THRESHOLD
            else "EQUILIBRIUM_REJECTED")


def load_certificate(path: str = _B9_CERT) -> dict:
    with open(path) as f:
        return json.load(f)


# --------------------------------------------------------------------------- #
# lowering                                                                     #
# --------------------------------------------------------------------------- #
def _artifact(cert: dict) -> Artifact:
    """The B9 certificate is the L0 evidence this lowering is grounded in."""
    return Artifact(
        artifact_id=content_id("art", cert),
        kind="CERTIFICATE_EXTERNAL",
        content_hash=content_id("sha", cert).split("_")[-1],
        acquired_at=cert.get("timestamp_utc", "1970-01-01T00:00:00Z"),
        format="json",
        apparatus_id="apparatus:josephson_circuit",
        calibration_route=list(_MEASUREMENT),
        source_uri="certificates/b9_certificate.json",
    )


def _events(art_id: str) -> List[Event]:
    """A minimal representative L1 act-trace of the decompilation recipe."""
    return [
        Event("b9_evt_prepare", "PREPARE", art_id,
              ports=(Port("equilibrium_state", "State", "1", "thermal"),),
              timing={"ordering_index": 0}, assumptions=("asm:linearized_well",)),
        Event("b9_evt_evolve", "EVOLVE", art_id,
              ports=(Port("ou_drift", "Process", "1/s", None),),
              timing={"ordering_index": 1}, assumptions=("asm:linearized_well",)),
        Event("b9_evt_measure", "MEASURE", art_id,
              ports=(Port("trajectory", "Observable", "1", None),),
              timing={"ordering_index": 2},
              calibration_route=list(_MEASUREMENT)),
    ]


def _fact(fact_id_seed, verdict, evidence, assumptions, content, art_id,
          warning=None, analyzer=None) -> Fact:
    analyzer = analyzer or (_ANALYZER if warning else _ANALYZER_EXACT)
    warnings = (Warning_(location="b9_certificate", message=warning),) if warning else ()
    fid = content_id("fct", {"seed": fact_id_seed, "content": content,
                             "assumptions": list(assumptions)})
    return Fact(
        fact_id=fid, pir_level="L2", evidence_level=evidence, layer="DOMAIN",
        namespace="domain", status="SUPPORTED", analyzer=analyzer,
        content=content, created_at="1970-01-01T00:00:00Z",
        assumptions=tuple(assumptions), measurement_interface=_MEASUREMENT,
        source_spans=({"artifact_id": art_id, "span": fact_id_seed},),
        warnings=warnings, verdict=verdict,
    )


def lower(cert: dict) -> Tuple[Artifact, List[Event], List[Fact]]:
    """Lower the B9 certificate into (L0 artifact, L1 events, L2 facts).

    Each fact re-derives its verdict from the residuals/quantities stored in the
    certificate; nothing is copied blindly from B9's headline."""
    r = cert["results"]
    art = _artifact(cert)
    events = _events(art.artifact_id)
    facts: List[Fact] = []
    sim_warn = ("OU estimation is simulation-conditioned (E3): the verdict "
                "depends on the numerical generator and step DT; not an exact "
                "certificate.")

    # T1 RECOVERY -> PERMITTED (recovered within a few %), FDT-consistent.
    t1 = r["T1"]
    v1 = "PERMITTED" if fdt_verdict(t1["fdt_residual"]) == "EQUILIBRIUM_CONSISTENT" else "REJECTED"
    facts.append(_fact("b9_T1_recovery", v1, "E3", ("asm:linearized_well",),
                       {"errM": t1["errM"], "errW": t1["errW"],
                        "fdt_residual": t1["fdt_residual"],
                        "fdt_verdict": fdt_verdict(t1["fdt_residual"]),
                        "psd_certified": True}, art.artifact_id, warning=sim_warn))

    # T2 HIDDEN BATH -> REJECTED via the FDT gate.
    t2 = r["T2"]
    v2 = "REJECTED" if fdt_verdict(t2["fdt_residual"]) == "EQUILIBRIUM_REJECTED" else "PERMITTED"
    facts.append(_fact("b9_T2_hidden_bath", v2, "E3", ("asm:linearized_well",),
                       {"fdt_residual": t2["fdt_residual"],
                        "fdt_verdict": fdt_verdict(t2["fdt_residual"])},
                       art.artifact_id, warning=sim_warn))

    # T3 GIBBS CIRCULARITY -> spec route REJECTED; the Gibbs route falsely passes
    # and is non-promotable (assumption-tainted, warned).
    t3 = r["T3"]
    v3 = "REJECTED" if fdt_verdict(t3["spec_residual"]) == "EQUILIBRIUM_REJECTED" else "PERMITTED"
    facts.append(_fact("b9_T3_gibbs_circularity", v3, "E3",
                       ("asm:linearized_well", "asm:gibbs_route"),
                       {"spec_residual": t3["spec_residual"],
                        "gibbs_residual": t3["gibbs_residual"],
                        "gibbs_would_pass": fdt_verdict(t3["gibbs_residual"]) == "EQUILIBRIUM_CONSISTENT"},
                       art.artifact_id,
                       warning=("Gibbs-route FDT consistency "
                                f"(residual {t3['gibbs_residual']:.3f} < {FDT_THRESHOLD}) is a "
                                "circular artifact of inferring H_V from the same "
                                "trajectories; NOT promotable (m-layer stipulation).")))

    # T4 MODEL ORDER -> REPRESENTATION_DEPENDENT (coordinate choice inverts M).
    t4 = r["T4"]
    inverted = abs(t4["mobility_1d"] - t4["G_2d"]) / t4["G_2d"] > 0.9
    v4 = "REPRESENTATION_DEPENDENT" if inverted else "PERMITTED"
    facts.append(_fact("b9_T4_model_order", v4, "E3", ("asm:1d_reduction",),
                       {"mobility_1d": t4["mobility_1d"], "G_2d": t4["G_2d"],
                        "inverts_dissipative_coefficient": inverted},
                       art.artifact_id,
                       warning=("1D overdamped reduction returns mobility 1/G where "
                                "the 2D representation's M entry is G; the dissipative "
                                "number is chart-dependent.")))

    # T5 EFFECTIVE-TEMPERATURE PROHIBITION -> REJECTED via the FDT gate.
    t5 = r["T5"]
    v5 = "REJECTED" if fdt_verdict(t5["fdt_residual"]) == "EQUILIBRIUM_REJECTED" else "PERMITTED"
    facts.append(_fact("b9_T5_effective_temperature", v5, "E3", ("asm:linearized_well",),
                       {"fdt_residual": t5["fdt_residual"],
                        "fdt_verdict": fdt_verdict(t5["fdt_residual"])},
                       art.artifact_id, warning=sim_warn))

    # T6 QUANTUM HELD-OUT -> PERMITTED (held-out match), exact charge-basis (E1),
    # resting on the hard-wall truncation assumption.
    t6 = r["T6"]
    matched = (t6["E01_rel_dev_from_asymptotic"] < 0.02
               and t6["truncation_convergence"] < 1e-6)
    v6 = "PERMITTED" if matched else "REJECTED"
    facts.append(_fact("b9_T6_quantum_heldout", v6, "E1", ("asm:hard_wall_truncation",),
                       {"E01": t6["E01"],
                        "E01_asymptotic_prediction": t6["E01_asymptotic_prediction"],
                        "E01_rel_dev_from_asymptotic": t6["E01_rel_dev_from_asymptotic"],
                        "truncation_convergence": t6["truncation_convergence"],
                        "heldout_match": matched}, art.artifact_id,
                       analyzer=_ANALYZER_EXACT))
    return art, events, facts


def to_store(cert: dict) -> Tuple[FactStore, List[Fact]]:
    store = FactStore()
    _, _, facts = lower(cert)
    for f in facts:
        store.add_fact(f)
    return store, facts


def reproduced_verdicts(cert: dict) -> Dict[str, str]:
    """Map B9 test id -> the PIR-derived verdict (for cross-check vs B9)."""
    _, _, facts = lower(cert)
    out = {}
    for f in facts:
        test = f.source_spans[0]["span"].split("_")[1]  # "b9_T2_..." -> "T2"
        out[test] = f.verdict.value if f.verdict else None
    return out
