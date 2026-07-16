"""B9 -> PIR lowering tests (Stage 2 / P2).

Proves the PIR substrate consumes a real benchmark: the committed B9 certificate
is lowered to L0/L1/L2 and its verdicts are RE-DERIVED (not copied) and shown to
match B9's own gate outcomes. No B9 code or certificate is modified.

L1  REPRODUCTION: feeding B9's stored residuals back through the FDT gate
    reproduces B9's per-test verdicts (T2/T5 rejected, T1 consistent, ...).
L2  SCHEMA + HONESTY: every lowered fact validates against fact.schema.json and
    satisfies PIR's construction invariants (HEURISTIC E3 carry warnings; the
    exact T6 fact is SOUND E1).
L3  TAINT: B9's m_layer_stipulations are present as assumptions; invalidating
    asm:hard_wall_truncation downgrades exactly the T6 held-out fact that rests
    on it, leaving the FDT-gate facts SUPPORTED (ADR-0002 conditionality=taint).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pir
from pir.domains import b9
from pir.domains import circuit_semantics as cs

FAILURES = []


def check(label, errors):
    if errors:
        FAILURES.append((label, errors))
        print(f"  [FAIL] {label}")
        for e in errors[:6]:
            print(f"         - {e}")
    else:
        print(f"  [ ok ] {label}")


def l1_reproduction():
    cert = b9.load_certificate()
    got = b9.reproduced_verdicts(cert)
    # Expected verdicts re-derived from B9's gate logic / stipulations.
    expected = {
        "T1": "PERMITTED",                 # fdt 0.021 < 0.15 -> consistent -> recovered
        "T2": "REJECTED",                  # fdt 0.497 -> hidden bath rejected
        "T3": "REJECTED",                  # spec 0.489 rejected (Gibbs blind spot warned)
        "T4": "REPRESENTATION_DEPENDENT",  # mobility inverts the 2D M entry
        "T5": "REJECTED",                  # fdt 0.885 -> effective-temperature rejected
        "T6": "PERMITTED",                 # held-out E01 within 2%, truncation converged
    }
    errs = [f"{t}: got {got.get(t)!r}, expected {v!r}" for t, v in expected.items()
            if got.get(t) != v]
    # And the gate itself reproduces B9's residual->verdict mapping.
    if b9.fdt_verdict(0.02) != "EQUILIBRIUM_CONSISTENT":
        errs.append("gate mislabels a sub-threshold residual")
    if b9.fdt_verdict(0.5) != "EQUILIBRIUM_REJECTED":
        errs.append("gate mislabels a super-threshold residual")
    check("B9 verdicts re-derived from PIR facts match B9's gate", errs)
    return got


def l2_schema_and_honesty():
    cert = b9.load_certificate()
    _, events, facts = b9.lower(cert)
    fact_schema = pir.jsonschema_mini  # module handle
    import json
    schema_path = os.path.join(os.path.dirname(pir.__file__), "schema", "fact.schema.json")
    with open(schema_path) as fh:
        schema = json.load(fh)
    errs = []
    for f in facts:
        errs.extend(fact_schema.iter_errors(schema, f.to_dict()))
    # The exact quantum fact must be SOUND at E1; the FDT-gate facts HEURISTIC E3.
    t6 = next(f for f in facts if "T6" in f.source_spans[0]["span"])
    if not (t6.analyzer.tag.value == "SOUND" and t6.evidence_level.value == "E1"):
        errs.append(f"T6 should be SOUND/E1, is {t6.analyzer.tag.value}/{t6.evidence_level.value}")
    t2 = next(f for f in facts if "T2" in f.source_spans[0]["span"])
    if not (t2.analyzer.tag.value == "HEURISTIC" and t2.warnings):
        errs.append("T2 (simulation-conditioned) should be HEURISTIC with a warning")
    if len(events) != 3:
        errs.append(f"expected 3 L1 events, got {len(events)}")
    check("lowered facts validate against fact.schema.json and honesty rules", errs)
    return {"n_facts": len(facts)}


def l3_taint_invalidation():
    cert = b9.load_certificate()
    store, facts = b9.to_store(cert)
    errs = []
    # m_layer_stipulations present as assumptions somewhere in the fact set.
    all_asm = set().union(*(set(f.assumptions) for f in facts))
    for needed in ("asm:linearized_well", "asm:gibbs_route", "asm:1d_reduction",
                   "asm:hard_wall_truncation"):
        if needed not in all_asm:
            errs.append(f"missing stipulation->assumption {needed}")
    # Invalidate the hard-wall truncation: only T6 rests on it.
    t6 = next(f for f in facts if "T6" in f.source_spans[0]["span"])
    t2 = next(f for f in facts if "T2" in f.source_spans[0]["span"])
    affected = store.invalidate_assumption("asm:hard_wall_truncation",
                                           reason="escape-width boundary conditions required")
    if t6.fact_id not in affected:
        errs.append("invalidation did not reach the T6 held-out fact")
    if store.get(t6.fact_id).status.value != "DOWNGRADED":
        errs.append("T6 fact not DOWNGRADED after truncation withdrawn")
    if store.get(t2.fact_id).status.value != "SUPPORTED":
        errs.append("T2 FDT-gate fact wrongly affected by truncation withdrawal")
    check("m_layer stipulations are taint; invalidating truncation downgrades only T6", errs)
    return {"affected": sorted(affected)}


def l4_domain_contracts():
    cert = b9.load_certificate()
    _, events, _ = b9.lower(cert)
    errs = []
    # C1-C3: the lowered act-trace obeys the four circuit-domain contracts.
    errs.extend(cs.validate(events))
    # C3: promotability rule — spectroscopy promotable, Gibbs not.
    if cs.is_promotable_route("cal:spectroscopy_route") is not True:
        errs.append("spectroscopy route should be promotable")
    if cs.is_promotable_route("cal:gibbs_route") is not False:
        errs.append("gibbs route must be non-promotable")
    # C4: structural graph exports nodes + a coherent edge set.
    g = cs.structural_graph(events)
    if len(g.nodes) != len(events):
        errs.append("graph node count != event count")
    time_edges = [e for e in g.edges if e["kind"] == "time"]
    if len(time_edges) != len(events) - 1:
        errs.append(f"expected {len(events)-1} time edges, got {len(time_edges)}")
    check("circuit domain semantics: 4 contracts hold + structural graph exported", errs)
    return {"nodes": len(g.nodes), "edges": len(g.edges)}


if __name__ == "__main__":
    print("== B9 -> PIR lowering ==")
    r1 = l1_reproduction()
    r2 = l2_schema_and_honesty()
    r3 = l3_taint_invalidation()
    r4 = l4_domain_contracts()
    print("\n== SUMMARY ==")
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} check(s) failed.")
        sys.exit(1)
    print(f"PASS: B9 verdicts reproduced from PIR facts {r1}")
    sys.exit(0)
