# B13-CDL — certificate identity + PIR bridge (v0.1)

This note documents the three-tier upgrade that reconciles B13-CDL's certificate
machinery with the repository's conventions and the PIR evidence substrate.

## Tier 1 — content-addressed, stable-filename certificates
**Before:** `certificate_id = "b13cdl-<pipeline>-" + uuid4().hex[:12]`, written to
`b13cdl-<pipeline>-<uuid>.json`. Every run minted a *new* random id and a *new*
file, so reruns accumulated files and no result could be diffed against its
prior version.

**Now:** `certificate_id` is a sha256 (first 12 hex) of the canonical certificate
body with the id and `timestamp_utc` excluded (`common._content_hash`). Same
inputs → same id (reproducible); changed inputs → changed id (real
discrimination). Each pipeline writes one **stable** filename
`b13cdl-<pipeline>.json` that reruns overwrite. Only `timestamp_utc` differs
between two runs of unchanged inputs.

Rationale: this is content-addressing done the way `pir/canonical.py` already
does it, but kept stdlib-local so the id is identical with or without `pir`
importable.

## Tier 2 — under the repo CI gate
`ci/run_all_certified.py` now reruns `b13_cdl/tests/test_b13.py` alongside
`tests/test_b*.py`. Each suite is pinned to its own certificate zone
(`certificates/` for B1–B12, `b13_cdl/certificates/` for B13); the runner
snapshots, diffs regenerated vs committed with the shared **degradation
predicate**, and restores each zone byte-for-byte. Because B13 certificates are
now reproducible, the only per-run difference is the timestamp (and
`created_at` inside the PIR facts), both treated as volatile by the predicate.
A genuine change to any verdict/soundness/result field trips the gate.

## Tier 3 — the PIR-fact view
Each certificate is also emitted as a `pir.Fact` (`src/cdl/pir_bridge.py`) into an
append-only `pir.FactStore`; the combined view is written to
`certificates/pir_facts.json`. Mapping:

| pipeline | evidence | PIR verdict | layer | namespace |
|---|---|---|---|---|
| ew_vacuum | E3 (HEURISTIC, warning) | — | MEASUREMENT | domain |
| strong_cp | E0 (exact) | PERMITTED | MEASUREMENT | domain |
| varying_constants | E1 (interval) | REJECTED | MEASUREMENT | domain |
| grh_miller | E0 (exact) | — (mixed rows) | UNIVERSAL | invariant |
| tunnell_bsd | E0 (exact) | — (mixed rows) | UNIVERSAL | invariant |
| muon_g2 | E2 (published σ) | NONIDENTIFIABLE | MEASUREMENT | domain |
| h0_tension | E2 (published σ) | NONIDENTIFIABLE | MEASUREMENT | domain |
| coverage | E0 (exact audit) | — (meta) | UNIVERSAL | analyst |

- **Assumptions = stipulations.** Each certificate stipulation becomes a PIR
  assumption `asm:<name>`, so the verdict's conditionality is carried as
  first-class taint.
- **Measurement interface.** DOMAIN/MEASUREMENT facts derive their declared 𝖬
  from the stipulation `source` fields (the experiments/papers), satisfying
  SPEC §2 in the PIR model.
- **Honesty is enforced by construction.** `pir.Fact.__post_init__` rejects a
  SOUND fact at E3/E4, a HEURISTIC fact at E0, and a HEURISTIC E3/E4 fact with
  no located warning — so building the facts validates the mapping above.

### Why `CONDITIONAL(X)` maps to assumptions, not a verdict
B13's proposed `CONDITIONAL(X)` verdict is a DRAFT SPEC-§6 extension awaiting
sign-off. Rather than pre-empt that decision, the bridge represents the
conditioning unknowns X as PIR **assumptions**. The PIR `verdict` field uses only
the SPEC-locked vocabulary (`PERMITTED`, `REJECTED`, `NONIDENTIFIABLE`, or none
for mixed/meta certificates). The payoff is exact and testable
(`tests/test_b13.py`): invalidating `asm:GRH` downgrades precisely the
GRH-conditional Miller fact while leaving the unconditional physics facts
`SUPPORTED`. This is *offered as evidence for the sign-off discussion* that
conditionality may be better modelled as taint than as a new verdict — but
nothing here is filed to `docs/SPECIFICATION.md`, the atlas, or the claims table.

## Scope
Changes are confined to `b13_cdl/` and `ci/run_all_certified.py`
(`created_at` added to the volatile-key set; a B13 suite added to the runner).
No existing B1–B12 code, verdict, certificate, SPEC clause, or atlas cell is
modified.
