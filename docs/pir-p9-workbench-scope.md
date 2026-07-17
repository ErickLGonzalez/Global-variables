# P9 — PIR Workbench UI: scope (BUILT)

**Status:** BUILT (v0.1). Implemented as a self-contained, read-only page —
`ci/build_workbench.py` (generator), `tests/test_pir_workbench.py`,
`docs/pir-workbench-v0.1.md`. All six surfaces below render in both themes with
no console errors. This document is retained as the design record and the
constraints it was built against.

## Why P9 is its own session
P9 is the first **non-substrate, presentation-layer** direction in the PIR
program. Everything through P8 is additive library code with headless tests;
a UI is a different kind of artifact with different risks (it must not become a
second source of truth, and it must stay self-contained). Keeping it separate
preserves the clean, test-driven substrate history.

## What P9 is (and is NOT)
- **Is:** a read-only viewer over the JSON artifacts the substrate already
  emits — PIR facts, provenance/invalidation, verdict×evidence coordinates,
  the candidate lattice, and the cross-domain diff.
- **Is NOT:** a fact editor, a solver, or a place any verdict originates. The
  committed JSON (`certificates/`, `b13_cdl/certificates/pir_facts.json`,
  benchmark certificates) remains authoritative; the UI only renders it.

## Hard constraints (carry from the whole program)
1. **Read-only.** The workbench never writes a fact, verdict, or certificate.
2. **Self-contained.** If built as a claude.ai **Artifact**, obey the strict CSP:
   inline all CSS/JS, embed data, no external hosts. If built as a repo asset,
   stdlib-only generation (no new runtime dependency), single static HTML file.
3. **No atlas / SPEC / verdict changes.** Presentation only.
4. **Evidence honesty preserved.** SOUND vs HEURISTIC, evidence level E0–E4, and
   located warnings must be visible, not flattened — the UI must not let a
   HEURISTIC/E3 result read as a certified one.

## Concrete scope (suggested surfaces)
1. **Fact table** — every `pir.Fact` with its L (pir_level) and E (evidence_level)
   as *orthogonal* axes, verdict, namespace, layer, analyzer tag (SOUND/HEURISTIC
   badge), and warnings.
2. **Provenance / invalidation view** — the dependency graph; select an
   assumption (`asm:*`) and highlight the transitive facts an invalidation would
   DOWNGRADE (drive `FactStore.invalidate_assumption` offline and render the
   result; do not mutate committed data).
3. **Verdict × evidence matrix** — a grid of facts by verdict and evidence level,
   so scarcity/robustness is visible at a glance.
4. **Candidate lattice** — equivalence classes, OE/NONIDENTIFIABLE status, and the
   test obligations (discriminating interventions) per class.
5. **Cross-domain diff** — B9 vs BEC shared motifs with the SEPARATE
   similarity/confidence numbers, the named correlator, explicit apparatus
   differences, and the least-cost discriminator.
6. **Structural graph** — render `circuit_semantics.structural_graph(...)` for the
   B9 act-trace (nodes = acts, edges = time/coordinate).

## Data sources (already produced by the substrate)
- `b13_cdl/certificates/pir_facts.json` — PIR-fact view of B13.
- `pir.domains.b9.lower(...)`, `pir.domains.exact_benchmarks.lower(...)`,
  `pir.domains.bec.lower()` — benchmark facts (generate to JSON in a build step).
- `pir.diff.cross_domain_diff(...)`, `pir.candidates.*`, `pir.runtime.*` — the
  analysis products to render.
- **Build step: DONE.** `ci/export_pir_view.py` already serializes the whole
  corpus view (facts, coverage, verdict×evidence matrix, invalidation demo,
  cross-domain diff, structural graph, corpus analysis) to
  `build/pir_view/bundle.json` (gitignored). Run `python3 ci/export_pir_view.py`
  to regenerate; `tests/test_pir_export.py` locks the bundle shape. **The P9
  session can start directly at the UI page and read this bundle.**

## Acceptance criteria for the P9 session
- A single self-contained page (Artifact or static HTML) renders the six surfaces
  above from the exported JSON, in light and dark themes, with no external
  requests.
- SOUND/HEURISTIC and evidence level are visually unmistakable; no HEURISTIC
  result is presented as certified.
- The invalidation view reproduces `invalidate_assumption` results exactly
  (cross-checked against the Python) without mutating any committed file.
- A short `docs/pir-workbench-v0.1.md` documents how to regenerate the export and
  open the page.

## Kickoff prompt for the future session
> Implement PIR P9 (workbench UI) per `docs/pir-p9-workbench-scope.md`: a
> read-only, self-contained viewer over the exported PIR view bundle. The data
> layer is already done — run `python3 ci/export_pir_view.py` to (re)generate
> `build/pir_view/bundle.json`, then build the page against it. Read-only; no
> atlas/SPEC/verdict changes; preserve SOUND/HEURISTIC and evidence-level
> honesty (no HEURISTIC/E3 result may read as certified).
