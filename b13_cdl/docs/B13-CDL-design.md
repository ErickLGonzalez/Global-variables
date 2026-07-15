# B13-CDL — Conditional-Dependency Ledger: Design & Engineering Sprint

**Sprint ID:** B13-CDL v0.1
**Author:** Rosy 🌹 (Claude), for Erick L. González — Global-variables project
**Date:** 2026-07-15
**Inputs (stipulated):** Conditional-Dependency Survey v1.0 + v1.1 addendum;
SPECIFICATION.md v1.0 (𝕽, evidence levels E0–E4, outcome vocabulary); the reverse-
engineering blueprint document (Ghidra/PGSD patterns A4, A5, A7, B1).

---

## 1. Objective

Turn the survey from a document into a **machine-readable ledger + certified pipeline
suite**: every conditional dependency becomes (a) a schema-validated ledger entry filed
to restraint-matrix cells, (b) where compute-friendly, a forward-map pipeline emitting
JSON certificates in the repo standard, and (c) a registered falsifier direction.

This directly executes Survey Recommendations 1–5 and imports three RE-blueprint
patterns: SOUND/HEURISTIC pass tagging (blueprint A5), SAT-witness/UNSAT-style
independently checkable certificates (A7), and headless CI-style reruns (B1).

## 2. New outcome verdict — SPEC edit DRAFT

The survey's core object — a result true *conditional on* unknown X — has no exact home
in the current SPEC §6 vocabulary. **Proposed (DRAFT, requires Erick sign-off before
claims-table filing):**

```
CONDITIONAL(X)            — verdict certified given stipulated truth/value of X;
                            X named; certificate carries the stipulation explicitly.
CONDITIONAL(X)-value      — numerical value depends on X (physics-style).
CONDITIONAL(X)-truth      — theoremhood depends on X (math-style).
```

Key epistemic asymmetries the pipelines must preserve (and do — see §4):
- GRH-Miller: "composite" is UNCONDITIONAL (witness found); "prime" is CONDITIONAL(GRH).
- Tunnell-BSD: "not congruent" is UNCONDITIONAL (count inequality is a Tunnell-theorem
  witness); "congruent" is CONDITIONAL(BSD).
- Muon g−2 / H₀: verdicts are NONIDENTIFIABLE(method) — existing vocabulary suffices;
  no forcing.

## 3. Deliverables map (Stages 1–5 of Survey Recommendations)

| Stage | Survey Rec | Deliverable in this package | Acceptance benchmark |
|---|---|---|---|
| 1 | Seed matrix with bidirectional compute-friendly entries | `data/ledger.json` (25 entries: A1–A15, M1–M10) + 7 pipelines in `src/cdl/` | Each priority entry has coded forward map + falsifier ID; `tests/test_b13.py` green |
| 2 | Falsifier ledger | `data/falsifiers.json` with `live` flag (within ~1 OOM of current capability) | Every bidirectional ledger entry references ≥1 falsifier; liveness computed, not asserted |
| 3 | Conditional-truth vs conditional-value flag | `schemas/cdl_entry.schema.json` field `conditional_type` (enum: value/truth/method) | 100% of entries validate against schema |
| 4 | Contested flags | `contested` + `contested_reason` fields; DESI w₀wₐ, α-dipole, Mochizuki-abc, A14/A15 tagged | Coverage check reports 0 untagged contested entries |
| 5 | Expansion/stopping rule | `src/cdl/coverage.py`: block×predicate coverage matrix; admission rule (new cell OR new compute hook) | Coverage report emitted as certificate; Uni-column scarcity flagged |

## 4. Pipeline suite (`src/cdl/`)

All pipelines emit certificates conforming to `schemas/cdl_certificate.schema.json`,
carrying: `soundness` tag (SOUND | HEURISTIC + located warning, per blueprint A5),
`stipulations` (named unknowns and assumed values — the m-layer analogue),
`verdict`, `witness` where applicable, and full input provenance.

| Module | Survey entry | Verdict logic | Soundness |
|---|---|---|---|
| `ew_vacuum.py` | A1 | (m_t, α_s, M_H) → stability-boundary distance in σ → STABLE / METASTABLE-side | HEURISTIC (linearized Buttazzo-2013 boundary; warning names the 3-loop-RGE SOUND upgrade path) |
| `strong_cp.py` | A4 | nEDM limit + lattice d_n(θ̄) coefficient → certified |θ̄| upper bound (exact Fraction arithmetic) | SOUND given stipulated lattice coefficient (stipulation carried) |
| `varying_constants.py` | A12 | Dirac-LNH prediction |Ġ/G| ≈ H₀ vs LLR bound → REJECTED with numeric margin witness | SOUND (pure interval arithmetic on published bounds) |
| `grh_miller.py` | M1 | Deterministic Miller, bases ≤ 2(ln n)²: composite ⇒ UNCONDITIONAL + witness base; prime ⇒ CONDITIONAL(GRH) | SOUND integer arithmetic; conditionality explicit |
| `tunnell_bsd.py` | M5 | Exact ternary-form counts: A≠2B ⇒ NOT_CONGRUENT (UNCONDITIONAL, counts as witness); A=2B ⇒ CONGRUENT CONDITIONAL(BSD) | SOUND exhaustive integer count |
| `muon_g2.py` | A14 | σ(exp, WP25), σ(exp, WP20), σ(WP25, WP20) → NONIDENTIFIABLE(HVP-method); refuses single verdict | SOUND arithmetic; honest refusal (S3-EM pattern) |
| `h0_tension.py` | A15 | Pairwise tension matrix (Planck, DESI+CMB, SH0ES, CCHP-JWST) → NONIDENTIFIABLE(model-vs-systematic) | SOUND arithmetic |
| `coverage.py` | Stage 5 | Ledger → block×predicate matrix, saturation + gap report, admission-rule evaluation | SOUND (combinatorial) |

Not yet implemented (Stage-1 backlog, next sprint candidates): B4/Schanuel decidability
stub, M10/UGC GW-SDP certificate via the repo Schur-pivot verifier (flagged as the
highest-value bridge to existing B1-standard machinery), M9/LMFDB Ramanujan-bound check.

## 5. Falsifier ledger schema (Stage 2)

Each falsifier: `{id, entry_id, description, required_capability, current_capability,
liveness}` where `liveness = live` iff required is within one order of magnitude of
current (Survey Rec-2 rule), computed by `coverage.py`, never hand-asserted.

## 6. Certificate & CI discipline

- `python3 tests/test_b13.py` runs every pipeline + schema validation + coverage,
  writing certificates to `certificates/`. Exit nonzero on any schema failure,
  any missing falsifier link, or any pipeline exception — the blueprint-B1 headless
  pattern. Designed to slot into the future single-CI entrypoint.
- Certificates are append-only by convention; a rerun writes a new timestamped file.

## 7. Execution instructions for the computational agent

```
cd b13-cdl
python3 tests/test_b13.py          # runs all pipelines, validates, emits certificates
python3 -m src.cdl.coverage        # standalone coverage report
```
Python ≥3.9, stdlib only (no pip installs required; jsonschema validation is
implemented internally to avoid dependencies).

## 8. Risks / thresholds that change the plan

- If the linearized EW-vacuum boundary disagrees with a future 3-loop pipeline by >1σ
  in verdict-relevant regions, demote A1 output to E4 and prioritize the SOUND upgrade.
- If Erick rejects the CONDITIONAL(X) SPEC edit, pipelines fall back to filing under
  OBSERVATIONALLY_EQUIVALENT with stipulations — lossy but vocabulary-legal.
- If the M/B relabeling (survey addendum) is rejected, ledger IDs `M*` are re-aliased;
  the ledger keys on stable `entry_id` strings, not labels, so this is a rename-only op.

## 9. Definition of done (this sprint)

☐ Ledger validates (25/25 entries) ☐ 7 pipelines certify ☐ Falsifier liveness computed
☐ Coverage certificate flags Uni-column scarcity ☐ Zip < 25 MB ☐ Erick integration +
commit hash confirmation.
