#!/usr/bin/env python3
"""Export the full PIR view to a JSON bundle (data layer for P9).

This is the read-only integration step named in `docs/pir-p9-workbench-scope.md`:
it lowers the entire benchmark corpus into PIR facts, runs the analysis products,
and serializes everything the future workbench UI needs into a single bundle
under `build/pir_view/` (gitignored). It writes nothing to the committed tree and
changes no verdict, certificate, or atlas cell.

Bundle sections:
  meta                — version + counts
  facts               — every lowered PIR fact (B9 + B1/B2/B3 + generic rest + BEC)
  coverage            — per-benchmark fact counts
  verdict_matrix      — verdict × evidence-level histogram
  distributions       — verdict and evidence-level totals
  invalidation_demo   — invalidate asm:hard_wall_truncation -> downgraded facts
  cross_domain_diff   — B9 vs BEC (similarity, confidence, correlator, apparatus)
  structural_graph    — the B9 act-trace graph
  candidate_lattice   — GVAR rules -> compatible families, verdict, obligations
  corpus_analysis     — analyzer-runtime run over the whole corpus
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, List

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pir.domains import b9, bec, exact_benchmarks as EB, generic as G
from pir.domains import circuit_semantics as CS
from pir.provenance import FactStore
from pir.runtime import AnalyzerRuntime, detect_conflicts
from pir import analyzers as A
from pir.diff import cross_domain_diff
from pir.intervention_search import AdmissibleIntervention
from pir import candidates as C


# GVAR rule fixture (the P5a documented lattice): three competing grammar
# families over the shared predicate set {Sym, Pos}. Hamiltonian and
# gradient-flow both fire and are observationally equivalent under the null
# intervention set; quantum-CPTP needs Cmp and stays out. Mirrors
# tests/test_pir_candidates.py so the exported lattice matches the certified one.
_GVAR_RULES = [
    {"rule_id": "r_ham", "family": "hamiltonian",
     "requires_predicates": ["Sym", "Pos"],
     "test_obligation": {"intervention": "int_time_reversal",
                         "separates": ["gradient_flow"]}},
    {"rule_id": "r_grad", "family": "gradient_flow",
     "requires_predicates": ["Pos"], "forbids_predicates": ["Uni"],
     "test_obligation": {"intervention": "int_time_reversal",
                         "separates": ["hamiltonian"]}},
    {"rule_id": "r_cptp", "family": "quantum_cptp",
     "requires_predicates": ["Pos", "Cmp"]},
]


def build_candidate_lattice() -> Dict:
    """Evaluate the documented GVAR lattice into a renderable, read-only view."""
    predicates = {"Sym", "Pos"}
    cands = C.apply_rules(_GVAR_RULES, predicates)
    result = C.evaluate(cands, declared_interventions=[])
    hyps = C.to_hypotheses(cands, "eqc_demo")
    fact = C.lattice_fact(result, "eqc_demo")
    return {
        "equivalence_class_id": "eqc_demo",
        "predicates": sorted(predicates),
        "rules": _GVAR_RULES,
        "verdict": result.verdict,
        "compatible_families": result.compatible,
        "obligations": [o for o in result.obligations if o],
        "detail": result.detail,
        "hypotheses": [h.to_dict() for h in hyps],
        "lattice_fact": fact.to_dict(),
    }


def collect_facts() -> Dict[str, List]:
    """Lower the whole corpus. Keys are benchmark ids; values are Fact lists."""
    out: Dict[str, List] = {}
    b9_cert = b9.load_certificate()
    _, b9_events, b9_facts = b9.lower(b9_cert)
    out["b9"] = b9_facts
    for b in ("b1", "b2", "b3"):
        out[b] = EB.lower(b)
    for b, facts in G.lower_all().items():
        out[b] = facts
    out["bec"] = bec.lower()
    return out, b9_events, b9_facts


def build_bundle() -> Dict:
    by_bench, b9_events, b9_facts = collect_facts()
    all_facts = [f for facts in by_bench.values() for f in facts]

    # verdict × evidence matrix + distributions
    matrix: Dict[str, Counter] = defaultdict(Counter)
    verdicts = Counter()
    evidence = Counter()
    for f in all_facts:
        v = f.verdict.value if f.verdict else "(none)"
        matrix[v][f.evidence_level.value] += 1
        verdicts[v] += 1
        evidence[f.evidence_level.value] += 1

    # invalidation demo on a fresh B9 store
    store = FactStore()
    for f in b9_facts:
        store.add_fact(f)
    downgraded = store.invalidate_assumption(
        "asm:hard_wall_truncation", reason="escape-width boundary conditions required")

    # cross-domain diff B9 vs BEC
    b9_feats = {"symmetry_group": "U(1)", "rank_sequence": [1, 2],
                "positivity_cone": "PSD", "spectral_class": "linear_response_positive"}
    interventions = [
        AdmissibleIntervention("int_scale_sweep", "SCALE_SWEEP", cost=3.0,
                               predicted_outcomes={"h_circuit": "a", "h_bec": "b"}),
        AdmissibleIntervention("int_geometry", "GEOMETRY_CHANGE", cost=40.0,
                               predicted_outcomes={"h_circuit": "a", "h_bec": "b"}),
    ]
    diff = cross_domain_diff(b9_feats, bec.canonical_invariants(),
                             {"id": "apparatus:josephson_circuit", "route": "cal:spectroscopy_route"},
                             bec.apparatus(), interventions, ["h_circuit", "h_bec"])

    # structural graph of the B9 act-trace
    graph = CS.structural_graph(b9_events)

    # corpus-level analyzer run (measurement-provenance audit + conflicts)
    corpus = G.suite_store()
    for f in b9_facts + [x for b in ("b1", "b2", "b3") for x in EB.lower(b)]:
        try:
            corpus.add_fact(f)
        except Exception:
            pass
    rt = AnalyzerRuntime()
    rt.register(A.measurement_provenance_pass())
    report = rt.run(corpus)

    return {
        "meta": {"bundle_version": "0.1", "n_benchmarks": len(by_bench),
                 "n_facts": len(all_facts),
                 "note": "read-only PIR view for the P9 workbench; no committed "
                         "data is modified."},
        "facts": [f.to_dict() for f in all_facts],
        "coverage": {b: len(facts) for b, facts in sorted(by_bench.items())},
        "verdict_matrix": {v: dict(cnt) for v, cnt in sorted(matrix.items())},
        "distributions": {"verdicts": dict(verdicts.most_common()),
                          "evidence_levels": dict(sorted(evidence.items()))},
        "invalidation_demo": {"assumption": "asm:hard_wall_truncation",
                              "downgraded_facts": downgraded},
        "cross_domain_diff": diff.to_dict(),
        "structural_graph": graph.to_dict(),
        "candidate_lattice": build_candidate_lattice(),
        "corpus_analysis": {"order": report.order, "quarantined": report.quarantined,
                            "conflicts": detect_conflicts(corpus),
                            "n_corpus_facts": len(corpus)},
    }


def main(argv=None) -> int:
    out_dir = os.path.join(ROOT, "build", "pir_view")
    os.makedirs(out_dir, exist_ok=True)
    bundle = build_bundle()
    path = os.path.join(out_dir, "bundle.json")
    with open(path, "w") as f:
        json.dump(bundle, f, indent=2, sort_keys=True)
    m = bundle["meta"]
    print(f"PIR view exported: {path}")
    print(f"  benchmarks: {m['n_benchmarks']}   facts: {m['n_facts']}")
    print(f"  verdicts: {bundle['distributions']['verdicts']}")
    print(f"  evidence: {bundle['distributions']['evidence_levels']}")
    print(f"  invalidation demo downgraded: {bundle['invalidation_demo']['downgraded_facts']}")
    print(f"  B9~BEC similarity={bundle['cross_domain_diff']['similarity']} "
          f"confidence={bundle['cross_domain_diff']['confidence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
