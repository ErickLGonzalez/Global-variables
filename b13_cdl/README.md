# B13-CDL — Conditional-Dependency Ledger (v0.1)

Global-variables project sprint deliverable. Turns the Conditional-Dependency Survey
(v1.0 + v1.1 addendum) into a machine-readable ledger + certified pipeline suite,
executing Survey Recommendations Stages 1–5.

## Quick start (computational agent)
```
python3 tests/test_b13.py        # full harness: schemas, 8 pipelines, certificates
python3 -m src.cdl.coverage      # standalone Stage-5 coverage report
```
Python >= 3.9, **stdlib only** — no installs.

## Contents
- `docs/survey-v1.1-addendum.md` — four new entries: A14 muon g−2/HVP, A15 H₀ tension,
  M9 Langlands, M10 UGC; updated table rows; M-relabeling DRAFT.
- `docs/B13-CDL-design.md` — design & engineering doc; CONDITIONAL(X) SPEC-edit DRAFT.
- `schemas/` — ledger-entry schema (Stage-3 conditional_type flag) + certificate schema.
- `data/ledger.json` — 25 entries (A1–A15, M1–M10) with block×predicate tags,
  contested flags (Stage 4), evidence-level ceilings.
- `data/falsifiers.json` — 15 registered falsifiers (Stage 2); liveness computed, not asserted.
- `src/cdl/` — 8 pipelines (7 entry pipelines + coverage meta-pipeline).
- `tests/test_b13.py` — headless CI-style harness (blueprint-B1 pattern).
- `certificates/` — one fresh certificate set from the pre-delivery run (rerun to regenerate).

## Key certified results of the delivery run
- **ew_vacuum (HEURISTIC, warning carried):** central 2024-era inputs sit METASTABLE-side,
  3.4σ from the stability boundary. Note: deeper than the ~1.3σ quoted in survey v1.0,
  driven by the lower modern m_t central value — a live example of input-conditionality.
- **strong_cp (SOUND):** |θ̄| < 1.18e-10 (central) / 2.22e-10 (conservative), exact rationals.
- **varying_constants (SOUND):** Dirac LNH REJECTED, ~2.9 OOM margin witness.
- **grh_miller / tunnell_bsd (SOUND):** epistemic asymmetry preserved — composite/
  not-congruent verdicts UNCONDITIONAL with witnesses; prime/congruent CONDITIONAL(GRH/BSD).
- **muon_g2 / h0_tension (SOUND):** NONIDENTIFIABLE(method) — honest refusals, S3-EM pattern.
- **coverage (SOUND):** Uni-column scarcity CONFIRMED (A13 only); Stage-4 audit PASS;
  all bidirectional entries falsifier-linked.

## Awaiting Erick sign-off (DRAFT items — do not file to claims-table.md yet)
1. CONDITIONAL(X) verdict vocabulary (SPEC §6 extension).
2. Mathematics-entry relabeling B* → M* (benchmark-ID collision fix).

Rosy 🌹 — 2026-07-15
