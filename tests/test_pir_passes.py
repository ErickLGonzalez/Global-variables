"""PIR pass-registry / honesty-layer tests (Stage 1, P1c).

Positive:
  Q1  A SOUND pass emitting an E0 exact fact and a HEURISTIC pass emitting an
      E3 fact WITH located warnings both pass the registry's emission check.
Negative (required):
  Q2  A HEURISTIC pass asserting evidence_level E0 -> reject.
  Q3  A SOUND pass asserting E3 (simulation) -> reject; a HEURISTIC E3 fact with
      empty warnings -> reject.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pir import (
    AnalyzerRef, Fact, PassHonestyViolation, PassRegistry, PassSpec,
    PIRValidationError, Warning_,
)
from pir.types import PassTag


def _fact(tag, evidence, warnings=(), fid="f"):
    return Fact(
        fact_id=fid, pir_level="L2", evidence_level=evidence, layer="UNIVERSAL",
        namespace="invariant", status="SUPPORTED",
        analyzer=AnalyzerRef("A", "0.1.0", tag),
        content={"n": 1}, created_at="2026-07-15T12:00:00Z",
        warnings=tuple(warnings),
        source_spans=({"artifact_id": "art", "span": "s"},),
    )


def q1_valid_emissions():
    reg = PassRegistry()
    sound = reg.register(PassSpec("SchurPivot", "0.1.0", PassTag.SOUND,
                                  fn=lambda: [_fact(PassTag.SOUND, "E0")]))
    heur = reg.register(PassSpec("SpectralGuess", "0.1.0", PassTag.HEURISTIC,
                                 fn=lambda: [_fact(PassTag.HEURISTIC, "E3",
                                                   warnings=[Warning_("rank@1e-6", "near-degenerate")])]))
    out_sound = reg.run(sound)
    out_heur = reg.run(heur)
    assert out_sound[0].evidence_level.value == "E0"
    assert out_heur[0].warnings[0].location == "rank@1e-6"
    assert reg.ids() == ["SchurPivot", "SpectralGuess"]
    print("Q1 valid emissions: PASS  SOUND→E0 and HEURISTIC→E3(+warnings) both "
          "accepted by the registry")
    return {"passes": reg.ids()}


def q2_heuristic_e0_rejected():
    # The model layer already forbids it at construction time.
    try:
        _fact(PassTag.HEURISTIC, "E0")
        assert False, "HEURISTIC E0 fact constructed"
    except PIRValidationError as e:
        assert "cannot assert an E0" in str(e)
    print("Q2 heuristic-E0: PASS  a HEURISTIC pass cannot assert an E0 exact "
          "fact (rejected at construction)")
    return {"ok": True}


def q3_registry_honesty():
    reg = PassRegistry()
    # SOUND pass that tries to emit an E3 fact — the fact itself is illegal at
    # construction, so emulate a mis-tagged emission the registry must catch:
    # build a legal HEURISTIC E3 fact but run it through a SOUND-tagged pass.
    heur_fact = _fact(PassTag.HEURISTIC, "E3",
                      warnings=[Warning_("loc", "msg")])
    bad_sound = PassSpec("MislabeledSound", "0.1.0", PassTag.SOUND,
                         fn=lambda: [heur_fact])
    try:
        reg.check_emission(bad_sound, heur_fact)
        assert False, "tag mismatch not caught"
    except PassHonestyViolation as e:
        assert "tagged SOUND but emitted" in str(e)

    # HEURISTIC E3 fact with EMPTY warnings -> rejected at construction.
    try:
        _fact(PassTag.HEURISTIC, "E3", warnings=())
        assert False, "empty-warning heuristic E3 accepted"
    except PIRValidationError as e:
        assert "warnings" in str(e)

    # SOUND asserting E4 proxy -> rejected at construction.
    try:
        _fact(PassTag.SOUND, "E4")
        assert False, "SOUND E4 accepted"
    except PIRValidationError as e:
        assert "cannot certify" in str(e)
    print("Q3 registry honesty: PASS  SOUND-tagged pass emitting a HEURISTIC "
          "fact caught; empty-warning HEURISTIC E3 and SOUND E4 both rejected")
    return {"ok": True}


if __name__ == "__main__":
    r1 = q1_valid_emissions(); r2 = q2_heuristic_e0_rejected(); r3 = q3_registry_honesty()
    print("\nALL PIR PASS TESTS PASS (Q1-Q3)")
