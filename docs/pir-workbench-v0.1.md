# PIR Workbench v0.1 (P9)

A single, self-contained, **read-only** page that renders the PIR evidence
substrate for a human reader. It is a viewer, never a source of truth: it renders
the committed JSON artifacts and writes no fact, verdict, or certificate.

## Regenerate & open
```bash
python3 ci/export_pir_view.py     # build build/pir_view/bundle.json (the data)
python3 ci/build_workbench.py     # inline the bundle -> build/pir_view/workbench.html
```
Open `build/pir_view/workbench.html` in any browser (no server needed — the data
is inlined, there are no external requests), or publish it as an Artifact. Both
`build/` outputs are gitignored; the generators and this doc are the committed
source.

## The six surfaces
1. **Facts** — every lowered fact with its `pir_level` (L, representation) and
   `evidence_level` (E, warrant) shown as *orthogonal* axes, the verdict pill,
   the namespace/layer, and the SOUND/HEURISTIC tag. Rows expand to content,
   assumption-taint, measurement interface, and witness / impossibility
   certificate. Filter by verdict, evidence, soundness, or text.
2. **Verdict × evidence** — a matrix; cell shade encodes count on one sequential
   ramp, with row/column totals.
3. **Provenance** — assumptions ranked by how many facts rest on them; selecting
   one lists those facts, and the invalidation demo shows which fact
   `asm:hard_wall_truncation` would downgrade (appended, never deleted).
4. **Candidate lattice** — the compatible grammar families retained in parallel
   and the interventions (test obligations) that would discriminate them.
5. **Cross-domain diff** — B9 vs BEC with **separate** similarity and confidence
   gauges, the named correlator, shared vs divergent motifs, apparatus
   differences, and the least-cost discriminator (no ontology-identity claim).
6. **Structural graph** — the B9 act-trace (nodes = acts, edges = time ordering
   and shared coordinates).

## Honesty affordances (the point of the page)
- **SOUND vs HEURISTIC** is a chip plus a left severity stripe on every row; an
  E3/E4 result is never styled as a certificate. The rail legend states the rule.
- **Evidence level** E0→E4 is a sequential ramp (exact → proxy); verdicts are
  status pills always shown *with the verdict word*, so identity never rides on
  color alone.
- Similarity and confidence are rendered as two separate gauges, never merged.

## Design & constraints
- Self-contained: all CSS/JS inline, the bundle inlined as a JSON island, zero
  external requests (CSP-safe); the `</script>` inside the data is escaped.
- Theme-aware: light and dark are both designed at the token level
  (`prefers-color-scheme` + a `data-theme` toggle), not a naive invert.
- Monospace-forward (the content is decompiler output); system font stacks avoid
  any webfont-CDN dependency.
- Verified: `tests/test_pir_workbench.py` (build + self-containment + surfaces +
  escaping); rendered in headless Chromium across all six surfaces in both themes
  with no console errors.
