# Atlas Edit 003 — Promotion of Conjecture ?₂ (QNEC as gravitational Gram positivity)

**Status: APPLIED (2026-07-11) — atlas bumped to [`constant-atlas-v0.5.md`](../constant-atlas-v0.5.md).**

## Proposed change

Restraint Matrix, row **G (gravity)**, column **Pos (positivity)**:

    BEFORE:  P → ?₂ (GSL)
    AFTER:   P (framework: 2D CFT — QNEC ≡ certified Schur-pivot positivity; H-track)

## What B6 established (internal evidence)

The strengthened 2D QNEC, 2π⟨T₊₊⟩ ≥ S″ + (6/c)(S′)², is **exactly equivalent** to positive semidefiniteness of

    M = [[ c/6, S′ ], [ S′, 2πT − S″ ]]

whose Schur pivot *is* the QNEC combination — the verifier standard S₂ = G₂₂ − G₀₂²/G₀₀ ≥ 0, realized gravitationally. Certified instances (all exact-rational or symbolic, zero floating point):
1. **Equivalence audit** — 500 random rational cases; PSD verdict tracks the QNEC combination exactly (T1).
2. **Vacuum saturation** — rank 1, second pivot exactly 0: QNEC saturation is the rank-deficient *flat boundary*, structurally identical to B1's flat-extension forcing locus (T2).
3. **Coherent-state strictness** — entropy unchanged, pivot = 2π(f′)², strict off critical points; the vacuum bracket cancels exactly (T3).
4. **Thermal saturation** — symbolic polynomial identity in x = coth(πΔu/β), all coefficients exactly zero: saturation for *all* interval sizes and temperatures at once (T4).
5. **Negative control** — wrong-concavity fake rejected with exact witness pivot −1/12 (T5).

## External evidence basis

1. Wall (2011) — QNEC proof for free fields; GSL proof lineage.
2. Balakrishnan, Faulkner, Khandker, Wang (2017) — QNEC from modular theory in general QFT.
3. Standard 2D CFT: vacuum-conformal states saturate the strengthened QNEC.

## No-circular-credit clauses

Promotion records that the Positivity blank for gravity is populated *in the 2D CFT framework* by the predicted mechanism (entropy-corrected Gram positivity). It does **not** claim: a new proof of QNEC; that M is (yet) the Gram matrix ω(A_i†A_j) of concrete operators; support for any other `?`; or anything beyond 2D.

## P → H requirements (recorded now)

1. **GNS realization:** exhibit operators {A₀, A₁} and a state ω with ω(A_i†A_j) = M_ij, so QNEC becomes literal Gram positivity (the bridge formula's ω(a†a) ≥ 0 instance). This is the decisive step.
2. **Beyond saturation:** certified strict cases outside the vacuum-conformal orbit (e.g., free-fermion excited states via exact resolvent/kernel methods).
3. **Higher dimensions:** interval-certified numerical instances (quarantined class) of QNEC in d > 2, or the holographic form.
4. **Unification with ?₃:** exhibit the GSL and the area theorem as instances of one certified positivity statement (Wall's proof is the anchor); success would advance both G-row entries toward H simultaneously.

## Apply checklist

- [x] Owner review of the equivalence claim and epistemic scope *(integrated from Claude B6 package; continue-work instruction)*
- [x] `certificates/b6_certificate.json` committed
- [x] Matrix cell updated in a new `constant-atlas-v0.5.md`; this file's hash appended to the changelog

— Drafted 2026-07-11, B6 session. Applied 2026-07-11.
