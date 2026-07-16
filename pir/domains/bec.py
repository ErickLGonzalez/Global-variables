"""BEC Domain Semantics Module + loader (Stage 2 / S3 / P8).

The Bose-Einstein-condensate domain, in the same four-contract form as the
circuit domain (:mod:`pir.domains.circuit_semantics`). It exists so a
cross-domain PIR-Diff (:mod:`pir.diff`) can compare B9 (circuit) and BEC
structures at the level of canonical invariants — shared *motifs* — while
keeping apparatus differences explicit and making no ontology-identity claim.
"""

from __future__ import annotations

from typing import Dict, List

from ..models import AnalyzerRef, Artifact, Event, Fact, Port, Warning_
from ..canonical import content_id

# C1 TYPES
BEC_PORT_UNITS: Dict[str, tuple] = {
    "density":            ("Observable", "1/m^3"),
    "phase":              ("GaugeCoordinate", "rad"),
    "condensate_fraction": ("Observable", "1"),
    "healing_length":     ("Invariant", "m"),
    "trap_frequency":     ("ApparatusParameter", "Hz"),
    "scattering_length":  ("Coupling", "m"),
    "initial_state":      ("State", "1"),
    "collective_mode":    ("Observable", "Hz"),
}

# C2 ACT-OPS
BEC_ACT_OPS = {
    "PREPARE": "evaporatively cool to a condensate ground state",
    "INTERVENE": "change a trap / scattering parameter (Feshbach)",
    "EVOLVE": "Gross-Pitaevskii mean-field evolution",
    "MEASURE": "time-of-flight or in-situ imaging",
    "RECORD": "record a calibrated absorption image",
}

# C3 MEASUREMENT routes
BEC_CALIBRATION_ROUTES = {
    "cal:tof_imaging": True,
    "cal:in_situ_imaging": True,
    "cal:self_calibrated_density": False,   # density inferred from same shot: circular
}

_MEASUREMENT = ("cal:tof_imaging",)


def canonical_invariants() -> Dict:
    """The BEC structure's representation-invariant feature set (for PIR-Diff).
    A dilute condensate shares U(1) phase symmetry and a positive-definite
    Bogoliubov (collective-mode) spectrum with many quadratic systems."""
    return {
        "symmetry_group": "U(1)",
        "rank_sequence": [1, 2],
        "positivity_cone": "PSD",
        "spectral_class": "bogoliubov_positive",
    }


def apparatus() -> Dict:
    return {"id": "apparatus:bec_trap", "cooling": "evaporative",
            "imaging": "time_of_flight", "route": "cal:tof_imaging"}


def lower() -> List[Fact]:
    """A minimal BEC lowered fact carrying the canonical invariants."""
    art_id = content_id("art", {"domain": "bec"})
    inv = canonical_invariants()
    analyzer = AnalyzerRef(id="pir.domains.bec", version="0.1.0", tag="HEURISTIC")
    fid = content_id("fct", {"domain": "bec", "inv": inv})
    f = Fact(
        fact_id=fid, pir_level="L2", evidence_level="E3", layer="DOMAIN",
        namespace="domain", status="SUPPORTED", analyzer=analyzer,
        content={"claim": "bec_collective_mode_structure",
                 "invariant_hash": content_id("inv", inv), **inv},
        created_at="1970-01-01T00:00:00Z",
        assumptions=("asm:dilute_gas", "asm:mean_field"),
        measurement_interface=_MEASUREMENT,
        warnings=(Warning_(location="bec", message=(
            "mean-field (E3): Bogoliubov spectrum is a numerical model, not "
            "an exact certificate.")),),
        source_spans=({"artifact_id": art_id, "span": "bec_collective_mode"},))
    return [f]
