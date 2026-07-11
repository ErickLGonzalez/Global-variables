# Atlas Edit 002 — Promotion of Conjecture ?₅ (gauge Composition column → H)

**Status: APPLIED (2026-07-11) — atlas bumped to [`constant-atlas-v0.4.md`](../constant-atlas-v0.4.md).**

## Proposed change

Restraint Matrix, column **Cmp (composition)**, rows:

| Row | BEFORE | AFTER |
|---|---|---|
| α (QED) | ?₅ (cluster decomp. → H) | **H** (cluster / factorization) |
| α_s (QCD) | ?₅ | **H** (cluster / factorization) |
| Electroweak block (g, g′, v) | ?₅ | **H** (cluster / factorization) |

This is the least-speculative blank: cluster decomposition and ⊗-associativity are theorems of local QFT; the couplings inherit them. The blank was bookkeeping omission. B5 supplies the program's internal certificate that one coupling governs all factorization channels (d_identifiable collapse to 1) and that channel-dependent couplings are rejected.

## Evidence basis

**External (established QFT):**
1. Weinberg, *The Quantum Theory of Fields*, Vol. 1 — cluster decomposition principle.
2. Haag, *Local Quantum Physics* — locality / factorization structure.

**Internal (this program):**
3. B5 certificate (`certificates/b5_certificate.json`): exact factorization R_24 = A_22² across channels; Jacobian rank ⇒ d_identifiable = 1; channel-dependent counterexample correctly FAIL / REJECTED.
4. B3 electroweak closed system already demonstrated exact relation discovery and d_identifiable accounting; B5 is the multi-channel extension named in the ?₅ test protocol.

## Conditions to apply (both required)

- [x] **B5 benchmark green:** factorization identities discovered; d_identifiable = 1; falsifier (channel-dependent couplings) rejected.
- [x] **Certificate committed:** `certificates/b5_certificate.json` in this repo.

## What promotion does and does not claim

**Claims:** the Composition column for gauge couplings (α, α_s, electroweak) is populated by a hard restraint — cluster decomposition / multi-channel factorization with a single coupling per sector. The atlas's bookkeeping blank is closed.

**Does not claim:** a new derivation of locality from 𝕽; numerical PDG cross-section fits (toy exact-Fraction channels only); that Yukawa / flavor Cmp blanks (?₆ neighborhood) are filled; that gravity Cmp upgrades from P to H.

## Follow-ons

1. Replace toy channels with PDG ratio checks (held-out empirical layer).
2. Extend factorization templates to non-Abelian color flow (α_s-specific).
3. Keep λ_Higgs / Yukawa Cmp cells as open `?` until dedicated benchmarks exist.

— Drafted and applied 2026-07-11, B5 session. Matrix cells → H; changelog hash recorded in atlas v0.4.
