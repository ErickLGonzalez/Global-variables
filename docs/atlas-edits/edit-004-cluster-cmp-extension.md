# Atlas Edit 004 — Extend Composition P to remaining gauge_qft couplings (R-CLUSTER)

**Status: APPLIED (2026-07-11) — atlas bumped to [`constant-atlas-v0.6.md`](../constant-atlas-v0.6.md).**

## Proposed change

Restraint Matrix, column **Cmp (composition)**, rows still at `?` after edit-002:

| Row | BEFORE | AFTER |
|---|---|---|
| λ_Higgs | ? | **P** (cluster / factorization; structural extension of ?₅) |
| Yukawa / CKM | ? | **P** (same) |
| Neutrino sector | ? | **P** (same) |
| θ_QCD | ? | **P** (same) |

## Derivation chain (Atlas Engine)

Rule **R-CLUSTER**: scope `gauge_qft`; preconditions Uni≥H and Cau≥P; conclusion Cmp≥P.

Anchor: cluster decomposition (Weinberg QTF I; Haag). Locality + Poincaré covariance are carried by the row **TYPE** (`gauge_qft`), not by the internal Sym cell. Internal certificate for the mechanism: B5 / edit-002 (?₅ → H on α, α_s, EW). Engine first pass: `certificates/atlas_engine_certificate.json`.

## What this does and does not claim

**Claims:** the remaining gauge_qft Composition blanks inherit at least framework-dependent P status from the same cluster theorem that forced H on the pure-gauge rows. The matrix bookkeeping gap closes at P.

**Does not claim:** H for these rows (no dedicated multi-channel factorization benchmark yet for Yukawa / θ / λ_H); that flavor Top (?₆ index form) is settled; any change to Λ Cmp (?₈).

## P → H requirements (recorded now)

1. Dedicated factorization / cluster certificates per sector (Yukawa channels; θ-sector correlators; Higgs effective vertices), analogous to B5.
2. Optional: collapse d_identifiable under joint constraints across those channels.

## Apply checklist

- [x] Engine propagation reproduces these four Cmp upgrades under R-CLUSTER
- [x] Human ratification: structural extension of edit-002, not a new empirical claim
- [x] Matrix cells updated in `constant-atlas-v0.6.md`

— Drafted and applied 2026-07-11, S1 ratification session.
