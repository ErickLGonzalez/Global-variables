"""PIR model + canonical-serialization + schema-validation tests (Stage 1).

Positive:
  M1  Round-trip: build the models in the minimal example, serialize
      canonically, and confirm hash-stability (same object -> same bytes ->
      same content ID) and Fraction-as-string handling.
  M2  Schema validation: all six schemas validate the corresponding sub-objects
      of examples/pir/minimal_circuit.json (cross-checked against the real
      jsonschema package when it is installed).
  M5  Orthogonality: a fact may pair any L level with any E level; the schema
      does not derive one from the other.

Negative (three of the six required negative tests live here; the other three
live in test_pir_provenance.py / test_pir_namespaces.py / test_pir_passes.py):
  M3  Non-SPEC verdict string -> reject; a candidate-class label in `verdict`
      -> reject (routed to the right home).
  M4  Missing measurement interface on a DOMAIN-layer fact -> reject.
"""

import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pir import (
    AnalyzerRef, Artifact, Event, Fact, Hypothesis, Intervention, Port,
    PIRValidationError, jsonschema_mini,
)
from pir.canonical import canonical_json, content_id, parse_fraction
from pir.types import EvidenceLevel, Layer, Namespace, PassTag, PirLevel, FactStatus

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCHEMA_DIR = os.path.join(ROOT, "pir", "schema")
EXAMPLE = os.path.join(ROOT, "examples", "pir", "minimal_circuit.json")


def _sound_fact(**over):
    base = dict(
        fact_id="fct_x", pir_level="L2", evidence_level="E1", layer="DOMAIN",
        namespace="domain", status="SUPPORTED",
        analyzer=AnalyzerRef("PositivityAnalyzer", "0.1.0", PassTag.SOUND),
        content={"claim": "psd", "min_schur_pivot": "7/1250"},
        created_at="2026-07-15T12:00:00Z",
        measurement_interface=("cal:readout_chain_v2",),
        source_spans=({"artifact_id": "art_1", "span": "col:counts"},),
    )
    base.update(over)
    return Fact(**base)


def m1_round_trip():
    art = Artifact(
        artifact_id="art_1", kind="DATASET",
        content_hash="9f2c" + "0" * 60, acquired_at="2026-06-30T09:12:00Z",
        format="csv", apparatus_id="apparatus:rig", calibration_route=["cal:v2"],
    )
    # Fraction content must serialize as "p/q", never a float.
    f = _sound_fact(content={"min_schur_pivot": Fraction(7, 1250), "rank": 3})
    blob = canonical_json(f.to_dict())
    assert '"7/1250"' in blob, blob
    assert "0.0056" not in blob  # never floated
    # Hash-stability: re-serialize a rebuilt-identical object -> identical bytes.
    f2 = _sound_fact(content={"min_schur_pivot": Fraction(14, 2500), "rank": 3})
    assert canonical_json(f.to_dict()) == canonical_json(f2.to_dict())  # 14/2500 == 7/1250
    cid = content_id("fct", f.to_dict())
    assert cid == content_id("fct", f2.to_dict())
    assert parse_fraction("7/1250") == Fraction(7, 1250)
    # Event round-trips with typed ports.
    ev = Event("evt_1", "MEASURE", "art_1",
               ports=(Port("escape_rate", "Observable", "1/s"),),
               assumptions=("asm:detector_linearity",))
    assert json.loads(canonical_json(ev.to_dict()))["op"] == "MEASURE"
    print(f"M1 round-trip: PASS  Fraction->'7/1250' exact; hash-stable content "
          f"ID {cid}; typed ports serialize")
    return {"content_id": cid}


def _load_schema(name):
    with open(os.path.join(SCHEMA_DIR, f"{name}.schema.json")) as fh:
        return json.load(fh)


def m2_schema_validation():
    with open(EXAMPLE) as fh:
        ex = json.load(fh)
    checks = [
        ("artifact", ex["artifact"]),
        ("event", ex["events"][0]),
        ("event", ex["events"][2]),
        ("fact", ex["facts"][0]),
        ("hypothesis", ex["hypotheses"][0]),
        ("hypothesis", ex["hypotheses"][1]),
        ("intervention", ex["interventions"][0]),
    ]
    # provenance schema validated on a constructed record (example has none).
    prov_instance = {
        "record_id": "prov_1", "entity": "fct_rank_0001",
        "activity": {"id": "act_1", "type": "ANALYZE"},
        "agent": {"id": "PositivityAnalyzer", "kind": "ANALYZER"},
        "used": [], "generated": ["fct_rank_0001"],
        "created_at": "2026-07-15T12:00:00Z",
    }
    checks.append(("provenance", prov_instance))

    for name, instance in checks:
        schema = _load_schema(name)
        jsonschema_mini.validate(schema, instance)  # raises on failure

    # Cross-check against the real jsonschema package if available.
    try:
        import jsonschema  # type: ignore
        for name, instance in checks:
            jsonschema.validate(instance, _load_schema(name))
        cross = "cross-checked vs jsonschema"
    except ImportError:
        cross = "jsonschema not installed; mini-validator only"

    names = sorted({n for n, _ in checks})
    assert names == ["artifact", "event", "fact", "hypothesis", "intervention", "provenance"]
    print(f"M2 schema validation: PASS  all six schemas validate the example "
          f"({cross})")
    return {"schemas": names}


def m3_verdict_lock():
    # (a) a non-SPEC verdict string is rejected.
    try:
        _sound_fact(verdict="TOTALLY_MADE_UP")
        assert False, "non-SPEC verdict accepted"
    except PIRValidationError as e:
        assert "locked vocabulary" in str(e)
    # (b) a candidate-class label in `verdict` is rejected and routed home.
    try:
        _sound_fact(verdict="GLOBAL_CANDIDATE")
        assert False, "candidate-class label accepted as verdict"
    except PIRValidationError as e:
        assert "candidate_class" in str(e)
    # (c) a real SPEC verdict is accepted.
    ok = _sound_fact(verdict="OBSERVATIONALLY_EQUIVALENT")
    assert ok.verdict.value == "OBSERVATIONALLY_EQUIVALENT"
    print("M3 verdict lock: PASS  non-SPEC string and candidate-class label "
          "both rejected; SPEC verdict accepted")
    return {"rejected": ["TOTALLY_MADE_UP", "GLOBAL_CANDIDATE"]}


def m4_measurement_interface():
    try:
        _sound_fact(measurement_interface=())
        assert False, "DOMAIN fact without measurement interface accepted"
    except PIRValidationError as e:
        assert "measurement interface" in str(e)
    # A UNIVERSAL-layer fact does NOT require one.
    u = _sound_fact(layer="UNIVERSAL", namespace="invariant", measurement_interface=())
    assert u.layer is Layer.UNIVERSAL
    print("M4 measurement interface: PASS  DOMAIN fact without a declared 𝖬 "
          "rejected; UNIVERSAL structural fact exempt")
    return {"ok": True}


def m5_orthogonality():
    # Any L pairs with any E; the model never derives one from the other.
    pairs = [("L0", "E4"), ("L2", "E0"), ("L3", "E2"), ("L1", "E3")]
    seen = []
    for lvl, ev in pairs:
        tag = PassTag.SOUND if ev in ("E0", "E1", "E2") else PassTag.HEURISTIC
        warns = () if tag is PassTag.SOUND else ({"location": "loc", "message": "m"},)
        f = _sound_fact(
            pir_level=lvl, evidence_level=ev, layer="UNIVERSAL",
            namespace="invariant", measurement_interface=(),
            analyzer=AnalyzerRef("A", "0.1.0", tag),
            warnings=tuple(__import__("pir").Warning_(**w) for w in warns),
        )
        seen.append((f.pir_level.value, f.evidence_level.value))
    assert seen == pairs
    print(f"M5 orthogonality: PASS  L and E freely combined {seen} — axes are "
          f"independent (ADJUDICATION #4)")
    return {"pairs": seen}


if __name__ == "__main__":
    r1 = m1_round_trip(); r2 = m2_schema_validation(); r3 = m3_verdict_lock()
    r4 = m4_measurement_interface(); r5 = m5_orthogonality()
    print("\nALL PIR MODEL TESTS PASS (M1-M5)")
