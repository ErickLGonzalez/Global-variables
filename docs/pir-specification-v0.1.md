# PIR Specification v0.1 — the evidence substrate

**Status:** Stage 1 (Substrate). Normative for the `pir/` package.
**Companion:** `docs/adr/ADR-PIR-0001.md` (decisions), `docs/verifier-ops-v0.1.md`
(frozen verifier ops), `pir/schema/*.schema.json` (machine-checkable schemas),
`examples/pir/minimal_circuit.json` (worked example).

PIR (Physics Intermediate Representation) is an **evidence substrate, not a
proof engine**. It records what was measured, what was done, what was certified,
and which grammars remain in play — each fact carrying orthogonal representation
(L) and warrant (E) coordinates, full provenance, and assumption taint. The
atlas engine never reads raw datasets directly; it reads certified PIR facts.
The mathematics that *decides* verdicts lives in the B1–B12 benchmarks and the
verifier ops; PIR is where their inputs, outputs, and dependencies are stored
honestly.

## 1. The two orthogonal axes

Every fact carries both, and neither derives the other (ADJUDICATION #4):

| Axis | Field | Values | Meaning |
|---|---|---|---|
| Representation | `pir_level` | L0, L1, L2, L3 | raw records → operational acts → structural facts → candidate grammars |
| Warrant | `evidence_level` | E0–E4 | exact (E0) → interval (E1) → statistical (E2) → simulation (E3) → proxy (E4); SPEC §3 |

A fact also declares a **layer** (`UNIVERSAL` / `DOMAIN` / `MEASUREMENT`; SPEC §2)
and a **namespace** (below).

## 2. Object model (`pir/models.py`)

- **Artifact** (L0) — immutable, content-addressed evidence in namespace `raw`.
  No theoretical labels, no inferred universal claims (loader-enforced).
- **Event** (L1) — one act-op (`PREPARE … MEASURE … COMPOSE`) grounded in an
  artifact, with typed, unit-bearing ports and explicit uncertainty.
- **Fact** (L2) — an append-only derived claim. Carries the full provenance
  quintet (analyzer id+version, dependency fact IDs, assumption taint, source
  spans, evidence level, pir level, layer, namespace, status) plus an optional
  SPEC-locked `verdict`. Reserves `witness` and `impossibility_certificate` for
  the Stage-2 symbolic bridge.
- **Hypothesis** (L3) — a competing explanatory family, retained in parallel
  (never silently pruned), with `candidate_class` *taxonomy* tags and two-hash
  fingerprint slots.
- **Intervention** — a declared experiment; observational equivalence is defined
  *relative to a declared intervention set* (SPEC §5, ADJUDICATION #6).
- **ProvenanceRecord** — PROV-O core (Entity/Activity/Agent), append-only.

## 3. Locked vocabularies (`pir/types.py`)

- **Verdict** (SPEC §4/§6, LAW): `FORCED, PERMITTED, REJECTED, NONIDENTIFIABLE,
  OBSERVATIONALLY_EQUIVALENT, APPARATUS_LIMITED, REPRESENTATION_DEPENDENT,
  AMBIGUOUS`. These are the ONLY strings a `verdict` accepts.
- **CandidateClass** (taxonomy, never a verdict): `GLOBAL_CANDIDATE,
  TOPOLOGICAL_CANDIDATE, HIDDEN_COMMON_CAUSE_CANDIDATE, REPRESENTATION_ARTIFACT,
  NOT_DETECTED`. Lives only on `hypothesis.candidate_class`.
- **Namespaces**: `raw, apparatus, operational, domain, latent, gauge,
  invariant, global, effective, analyst`.
- **Op families**: 16 act-ops and 6 verifier-ops (see verifier-ops doc).

## 4. Invariants the substrate enforces

1. **Append-only** — no pass mutates or deletes another pass's fact; conflicts
   are stored (`AppendOnlyViolation`).
2. **Dual coordinates** — `pir_level` ⟂ `evidence_level`, both mandatory.
3. **Verdict lock** — a candidate-class label in `verdict` raises.
4. **SOUND/HEURISTIC honesty** — SOUND ⇒ E0–E2; HEURISTIC ⇏ E0; HEURISTIC at
   E3/E4 ⇒ non-empty located `warnings[]`.
5. **Provenance quintet** — every derived fact carries analyzer id+version,
   dependency IDs, assumption taint, source spans, and the four coordinate
   fields.
6. **Namespace transforms** — cross-namespace dependencies require a typed
   transform; implicit promotion raises (`IllegalNamespacePromotion`).
7. **L0 purity** — raw artifacts carry no inferred universal claims.
8. **Invalidation traversal** — invalidating an assumption downgrades every
   transitively dependent fact via appended records, deleting nothing.
9. **Hash-stable canonical JSON** — sorted keys, `Fraction` as `"p/q"` strings,
   non-finite floats rejected.
10. **B1–B12 untouched** — no atlas edits, no verdict changes.
11. **CI fails on degradation** — see the CI section and ADR D8.
12. **Measurement interface** — DOMAIN/MEASUREMENT facts must name their 𝖬.
13. **Similarity ⟂ confidence** — reported as separate numbers with a named
    correlator (BinDiff discipline).

## 5. Provenance and invalidation (`pir/provenance.py`)

The `FactStore` is append-only and content-addressed. It refuses cyclic
dependencies (`ProvenanceCycle`), guards cross-namespace promotions, and
implements `invalidate_assumption(assumption_id, reason)`:

> find every fact that names the assumption OR transitively depends on one that
> does; append a `DowngradeRecord` (preserving prior status) and swap each to a
> `DOWNGRADED` copy. Nothing is deleted.

## 6. Pass registry (`pir/passes.py`)

A pass declares `(id, version, SOUND|HEURISTIC, fn)`. `PassRegistry.run` executes
the pass and validates every emitted fact against the honesty contract before it
reaches a caller or the store. Stage 2's dependency-resolved analyzer runtime
(P3) builds on this contract.

## 7. Schemas and validation

Six Draft-2020-12 schemas under `pir/schema/` encode the constraints. Because
the substrate and CI must run on a clean checkout, validation uses a vendored,
auditable subset validator (`pir/jsonschema_mini.py`); the real `jsonschema`
package, when installed, is used as a cross-check. All six schemas validate
`examples/pir/minimal_circuit.json`.

## 8. CI (`ci/run_all_certified.py`)

Reruns `tests/test_b*.py`, captures regenerated certificates to `build/ci/`,
restores the committed certificates, and diffs with the degradation predicate
(ADR D8). Emits a self-hash–signed manifest (pinned seed, library versions,
per-file content hashes) and exits nonzero on any failure or degradation.
`tests/test_ci_guard.py` proves it goes green on the current repo and red on a
synthetically corrupted certificate.

## 9. Scope and progress

Stage 1 (substrate) in scope: schemas, models, provenance, pass registry,
verifier-op reference, CI.

Stage 2 progress:
- **P2 — B9 circuit lowering (started):** `pir/domains/b9.py` lowers the committed
  B9 certificate into L0/L1/L2 and **re-derives** B9's per-test verdicts from the
  stored residuals (the FDT gate at 0.15 is reproduced, not copied). B9's
  `m_layer_stipulations` become assumptions (ADR-0002 conditionality=taint), so
  invalidating `asm:hard_wall_truncation` downgrades exactly the T6 held-out
  fact. Test: `tests/test_pir_b9_lowering.py`. No B9 code, verdict, certificate,
  or atlas cell is changed. Still to do in P2: the full Circuit Domain Semantics
  Module (4 contracts) and structural-graph export.

Out of scope (later): analyzer runtime (P3), symbolic constraint bridge (P4),
candidate lattice & fingerprints (P5), forward recompilation (S3/P6),
intervention search (P7), BEC cross-domain diff (P8), workbench UI (deferred).
