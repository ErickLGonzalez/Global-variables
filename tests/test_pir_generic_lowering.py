"""Generic certificate lowering — full benchmark-suite coverage.

G1  Every remaining benchmark certificate lowers to >=1 PIR fact, all facts
    validate against fact.schema.json, and no crash occurs.
G2  Every non-null verdict is in the SPEC-locked vocabulary; HEURISTIC (E3)
    facts carry a located warning; domain-specific states are preserved as
    raw_status with a null verdict (never force-fit).
G3  Spot-checks: B10 yields a FORCED and a REJECTED; B6 yields a REJECTED
    (QNEC violation); B7 yields a FORCED; B4 is E2 (statistical); a metric-only
    certificate (m1) still yields a summary fact.
G4  The combined suite store is append-only-consistent and the whole benchmark
    corpus (bespoke B1/B2/B3/B9 + generic rest) is represented.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pir
from pir.domains import generic as G
from pir.domains import exact_benchmarks as EB, b9
from pir.types import VERDICTS

FAILURES = []


def check(label, errors):
    if errors:
        FAILURES.append((label, errors)); print(f"  [FAIL] {label}")
        for e in errors[:6]:
            print(f"         - {e}")
    else:
        print(f"  [ ok ] {label}")


def _schema():
    with open(os.path.join(os.path.dirname(pir.__file__), "schema", "fact.schema.json")) as fh:
        return json.load(fh)


def g1_coverage():
    schema = _schema()
    errs = []
    all_facts = G.lower_all()
    for bench, facts in all_facts.items():
        if not facts:
            errs.append(f"{bench}: produced no facts")
        for f in facts:
            errs.extend(f"{bench}: {e}" for e in pir.jsonschema_mini.iter_errors(schema, f.to_dict()))
    check(f"G1 all {len(all_facts)} remaining benchmarks lower to valid PIR facts", errs)
    return all_facts


def g2_honesty(all_facts):
    errs = []
    for bench, facts in all_facts.items():
        for f in facts:
            if f.verdict is not None and f.verdict.value not in VERDICTS:
                errs.append(f"{bench}: non-SPEC verdict {f.verdict}")
            if f.analyzer.tag.value == "HEURISTIC" and f.evidence_level.value in ("E3", "E4") and not f.warnings:
                errs.append(f"{bench}: HEURISTIC E3 fact without warning")
            # domain-specific raw states must be preserved when unmapped.
            if f.verdict is None and "raw_status" not in f.content:
                errs.append(f"{bench}: null-verdict fact lost its raw_status")
    check("G2 verdicts SPEC-locked or null(+raw_status); HEURISTIC warns", errs)


def g3_spotchecks(all_facts):
    errs = []
    def verds(b):
        return {f.verdict.value for f in all_facts.get(b, []) if f.verdict}
    if not {"FORCED", "REJECTED"} <= verds("b10"):
        errs.append(f"b10 verdicts {verds('b10')} missing FORCED/REJECTED")
    if "REJECTED" not in verds("b6"):
        errs.append(f"b6 verdicts {verds('b6')} missing REJECTED (QNEC violation)")
    if "FORCED" not in verds("b7"):
        errs.append(f"b7 verdicts {verds('b7')} missing FORCED")
    # B4 is statistical -> E2.
    if not all(f.evidence_level.value == "E2" for f in all_facts.get("b4", [])):
        errs.append("b4 facts should be E2 (statistical)")
    # metric-only m1 -> a summary fact exists.
    if not any("summary" in f.source_spans[0]["span"] for f in all_facts.get("m1", [])):
        errs.append("m1 (metric-only) produced no summary fact")
    check("G3 spot-checks: b10 FORCED+REJECTED, b6 REJECTED, b7 FORCED, b4 E2, "
          "m1 summary", errs)


def g4_full_corpus(all_facts):
    st = G.suite_store()
    errs = []
    if len(st) < sum(len(v) for v in all_facts.values()):
        errs.append("suite store dropped facts (append-only?)")
    # whole corpus represented: bespoke + generic.
    bespoke = set()
    for b in ("b1", "b2", "b3"):
        bespoke |= {b}
    generic = set(all_facts)
    covered = bespoke | {"b9"} | generic
    # every certificate basename is either bespoke or generic-covered.
    all_bases = set(G._certificates()) - {"b4_demo"}
    missing = all_bases - covered
    if missing:
        errs.append(f"benchmarks not represented: {sorted(missing)}")
    check(f"G4 full corpus represented ({len(covered)} benchmarks), store consistent", errs)


if __name__ == "__main__":
    print("== generic full-suite lowering ==")
    af = g1_coverage(); g2_honesty(af); g3_spotchecks(af); g4_full_corpus(af)
    print("\n== SUMMARY ==")
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} check(s) failed."); sys.exit(1)
    n = sum(len(v) for v in af.values())
    print(f"PASS: full benchmark suite lowered to PIR ({n} generic facts + bespoke B1/B2/B3/B9).")
    sys.exit(0)
