# Atlas Edit 005 — Weak ?₆: flavor Top → P (anomaly / integrality); index form stays open

**Status: APPLIED (2026-07-11) — atlas bumped to [`constant-atlas-v0.6.md`](../constant-atlas-v0.6.md).**

## Proposed change

Restraint Matrix, column **Top (topology/quantization)**:

| Row | BEFORE | AFTER |
|---|---|---|
| Yukawa / CKM | **?₆** (N_g as index?) | **P** (anomaly cancellation / charge integrality; weak ?₆) |
| Neutrino sector | **?₆** | **P** (same; weak ?₆) |

The **strong / index form** of ?₆ — generation number N_g = 3 as `ind(D)` for a bridge operator — remains **?** (unchanged conjecture with the same falsifier).

## Derivation chain (Atlas Engine)

Rule **R-ANOMALY**: scope `gauge_qft`; preconditions Sym≥H and Uni≥H; conclusion Top≥P.

Anchor: anomaly cancellation forces topological (integrality) constraints on charge assignments — the 1970s solved blank, now recognized as applying to the flavor rows that still carried `?` in Top. Engine first pass: `certificates/atlas_engine_certificate.json`.

## What this does and does not claim

**Claims:** flavor sectors are not Top-exempt; anomaly / integrality restraints apply at least at P (framework-dependent). Weak direction of ?₆ closes.

**Does not claim:** that N_g is derived as an index; any specific candidate D with ind(D)=3; promotion of ?₆ to H.

## P → H / strong-?₆ requirements (recorded now)

1. Exhibit a candidate operator D in the bridge whose index equals 3 **and** correlates hierarchy patterns with spectral gaps.
2. Falsifier (unchanged): candidate structures reproduce couplings but leave N_g arbitrary.

## Apply checklist

- [x] Engine propagation reproduces Yukawa/neutrino Top upgrades under R-ANOMALY
- [x] Index form of ?₆ explicitly left open in atlas blank-filling table
- [x] Matrix cells updated in `constant-atlas-v0.6.md`

— Drafted and applied 2026-07-11, S1 ratification session.
