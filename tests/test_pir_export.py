"""PIR view exporter (data layer for P9).

X1  The bundle has all required sections and covers the whole corpus (>=23
    benchmarks); every fact validates against fact.schema.json.
X2  The verdict×evidence matrix is consistent with the flat fact list, and every
    non-null verdict is SPEC-locked.
X3  The analysis products are present and coherent: the invalidation demo
    downgrades >=1 fact; the cross-domain diff reports SEPARATE similarity and
    confidence with a named correlator; the structural graph has nodes+edges;
    the corpus analyzer run did not quarantine or raise spurious conflicts.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pir
from ci.export_pir_view import build_bundle
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


BUNDLE = build_bundle()


def x1_structure():
    errs = []
    required = {"meta", "facts", "coverage", "verdict_matrix", "distributions",
                "invalidation_demo", "cross_domain_diff", "structural_graph",
                "corpus_analysis"}
    missing = required - set(BUNDLE)
    if missing:
        errs.append(f"missing bundle sections: {sorted(missing)}")
    if BUNDLE["meta"]["n_benchmarks"] < 23:
        errs.append(f"only {BUNDLE['meta']['n_benchmarks']} benchmarks covered")
    schema = _schema()
    bad = 0
    for fd in BUNDLE["facts"]:
        if pir.jsonschema_mini.iter_errors(schema, fd):
            bad += 1
    if bad:
        errs.append(f"{bad} facts fail fact.schema.json")
    check(f"X1 bundle structure + {BUNDLE['meta']['n_facts']} schema-valid facts "
          f"over {BUNDLE['meta']['n_benchmarks']} benchmarks", errs)


def x2_matrix():
    errs = []
    # matrix totals == flat verdict distribution
    from collections import Counter
    flat = Counter()
    for fd in BUNDLE["facts"]:
        flat[fd["verdict"] or "(none)"] += 1
    mtotal = Counter()
    for v, row in BUNDLE["verdict_matrix"].items():
        mtotal[v] += sum(row.values())
    if flat != mtotal:
        errs.append(f"verdict matrix {dict(mtotal)} != flat {dict(flat)}")
    for v in BUNDLE["verdict_matrix"]:
        if v != "(none)" and v not in VERDICTS:
            errs.append(f"non-SPEC verdict in matrix: {v}")
    check("X2 verdict×evidence matrix consistent; verdicts SPEC-locked", errs)


def x3_analysis():
    errs = []
    if not BUNDLE["invalidation_demo"]["downgraded_facts"]:
        errs.append("invalidation demo downgraded nothing")
    d = BUNDLE["cross_domain_diff"]
    if d["similarity"] == d["confidence"]:
        errs.append("similarity/confidence collapsed")
    if not d["correlator"]:
        errs.append("diff correlator unnamed")
    g = BUNDLE["structural_graph"]
    if not g["nodes"] or not g["edges"]:
        errs.append("structural graph empty")
    ca = BUNDLE["corpus_analysis"]
    if ca["quarantined"]:
        errs.append(f"corpus analyzer quarantined: {ca['quarantined']}")
    if ca["conflicts"]:
        errs.append(f"spurious corpus conflicts: {ca['conflicts']}")
    check("X3 invalidation/diff/graph/corpus-analysis coherent", errs)


if __name__ == "__main__":
    print("== PIR view exporter ==")
    x1_structure(); x2_matrix(); x3_analysis()
    print("\n== SUMMARY ==")
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} check(s) failed."); sys.exit(1)
    print("PASS: full-corpus PIR view bundle exports coherently (P9 data layer ready).")
    sys.exit(0)
