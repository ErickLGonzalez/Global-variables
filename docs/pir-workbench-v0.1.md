# PIR Workbench v0.1

A single, self-contained, **read-only** web page that renders the lowered PIR
corpus. It is the P9 presentation layer of the PIR program (scope:
[`pir-p9-workbench-scope.md`](pir-p9-workbench-scope.md)); it originates no fact,
verdict, or certificate — the committed JSON stays authoritative and the page
only displays it.

## Regenerate and open

```bash
python3 ci/export_pir_view.py          # 1. (re)build the view bundle -> build/pir_view/bundle.json
python3 pir_workbench/build.py         # 2. inline it -> build/pir_view/workbench.html
```

Open `build/pir_view/workbench.html` in any browser. Both outputs live under the
gitignored `build/` tree; nothing in the committed tree is modified. The build is
stdlib-only (no runtime dependency) and the page makes **no external request**
(all CSS/JS inline, the bundle embedded as a data island) — so it also renders
correctly with the network disabled and satisfies a strict CSP.

To publish it as a claude.ai **Artifact**, emit the body-only fragment:

```bash
python3 pir_workbench/build.py --artifact build/pir_view/workbench.body.html
```

## What it shows (six surfaces)

1. **Fact table** — every `pir.Fact` with L (structural level) and E (evidence
   level) as orthogonal axes, plus verdict, layer, namespace, and a
   SOUND/HEURISTIC badge; filter by verdict / evidence / tag / layer / free text;
   click a warned row to read its located warnings verbatim.
2. **Provenance & invalidation** — pick an assumption (`asm:*`); the page replays
   `FactStore.invalidate_assumption` offline (direct membership + transitive
   closure over `depends_on_facts`) and lists every fact that would be
   DOWNGRADED. It cross-checks against the committed invalidation demo.
3. **Verdict × evidence matrix** — fact counts by SPEC verdict and evidence
   level, colour-tinted by evidence, with row/column totals.
4. **Candidate lattice** — the GVAR-rule evaluation: compatible grammar families,
   the SPEC verdict (here OBSERVATIONALLY_EQUIVALENT), the discriminating test
   obligations, and the L3 hypotheses retained in parallel.
5. **Cross-domain diff** — B9 (Josephson circuit) vs BEC with **separate**
   similarity and confidence, the named correlator, shared invariant motifs,
   divergent features, apparatus differences, and the least-cost discriminator.
6. **Structural graph** — the B9 act-trace (PREPARE → EVOLVE → MEASURE) rendered
   as an SVG with time/coordinate edges.

## Honesty invariants (enforced by `tests/test_pir_workbench.py`)

- **Read-only.** The page and its build never write a fact, verdict, or
  certificate.
- **Self-contained.** No `http(s)://`, `<link>`, external `src=`, or remote
  font; the only `url(...)` references are in-document fragment ids.
- **Evidence honesty preserved.** SOUND vs HEURISTIC, evidence levels E0–E4, and
  located warnings are all rendered and never flattened — the legend states
  explicitly that a HEURISTIC / E3 result is *not* certified.
- **Invalidation fidelity.** The interactive invalidation reproduces
  `FactStore.invalidate_assumption` exactly (checked against both a Python mirror
  of the page algorithm and the real store).

## Files

```
ci/export_pir_view.py        data layer: lowers the corpus, emits build/pir_view/bundle.json
pir_workbench/template.html   the UI shell (HTML/CSS/JS; a data island placeholder)
pir_workbench/build.py        stdlib build: inlines the bundle -> self-contained page
tests/test_pir_workbench.py   self-contained + honesty + read-only + invalidation-fidelity gate
```
