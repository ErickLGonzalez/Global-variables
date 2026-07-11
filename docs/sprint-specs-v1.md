# Sprint Specifications v1 — Computational Work Packages

Deep-research specs so each sprint starts with a full work order: inputs, algorithm, certificate class, falsifier, and definition-of-done. Ordered by (payoff × readiness).

---

## S1 — Ratify the engine's first pass (atlas v0.6)

**Goal:** convert Atlas Engine propagations into edit records. **Work:** (1) edit-004: Cmp ?→P for λ_H, Yukawa, neutrino, θ_QCD [R-CLUSTER chains]; (2) edit-005: Top ?→P (weak ?₆) for Yukawa/neutrino [R-ANOMALY], explicitly leaving the index form of ?₆ open; (3) edit-006: Λ Pos ?→P (weak ?₇) [R-DS-ENTROPY], rank form open; (4) resolve the two engine findings — split or annotate the Sym column (internal vs spacetime), and adjudicate gravity's Uni="—" under the R-SCHUR-QNEC tension (proposal: Uni→P with anchor "unitarity of boundary/horizon evolution in the semiclassical regime," or a documented reaffirmation of NA). **Class:** structural-derivation → human ratification. **DoD:** atlas v0.6 with changelog; engine re-run reproduces v0.6 as its own fixpoint (idempotence check).

## S2 — GNS realization for ?₂ → H (the decisive item)

**Honest framing:** any PSD 2×2 matrix is trivially a Gram matrix (Cholesky); the deliverable is a *physical* realization: operators A₀, A₁ and state ω in an actual QFT with ω(A_i†A_j) = M_ij = [[c/6, S′],[S′, 2πT − S″]]. **Route (computable):** free-fermion chain (Gaussian states — everything is determinants). (1) Build reduced density matrices ρ_A for intervals from correlation matrices; (2) compute relative entropy S(ρ‖σ) and its first/second null-cut derivatives numerically with interval bounds (quarantined class); (3) test the candidate identification A₀ ~ 1-normalized modular charge, A₁ ~ null-momentum density smeared at the cut, against M's entries across states (vacuum, thermal, coherent); (4) success = one operator pair reproducing M for ALL tested states within certified intervals. **Falsifier:** no state-independent operator pair exists (would demote the Gram interpretation to accidental). **Compute:** O(hours) laptop-scale; chains L ≤ 400. **DoD:** edit-007 draft (?₂→H conditions partially met: GNS item), or a documented obstruction.

## S3 — PDG empirical layer for B5

**Data:** R-ratio σ(e⁺e⁻→hadrons)/σ(→μ⁺μ⁻) vs √s (PDG tables); τ hadronic branching; Z hadronic width. **Algorithm:** the B5 factorization identities predict ONE α_s governs all three after RG evolution; run the B3-style pipeline: dimensionless invariants → single-coupling hypothesis vs channel-dependent alternative → Score comparison with holdout by *observable class*, not data point. Expected: single-coupling wins with the residuals attributable to known higher-order terms (report as the RG column, B3-PDG pattern). **Stipulations:** scheme (MS-bar), quark-mass thresholds, QED corrections. **Falsifier:** certified need for channel-dependent α_s after scheme/threshold effects. **DoD:** b5 REAL certificate + edit note strengthening ?₅'s empirical basis.

## S4 — ?₇ toy-dS rank saturation (B1 engine, the wild one)

**Setup:** static-patch dS₂ ≅ thermal state at T_dS = 1/2πℓ for a conformal field — thermal 2-point functions are exact (hyperbolic kernels, cf. B6's coth variable). **Algorithm:** (1) observables = smeared field modes {φ(f_k)} on the patch, k = 1..N; (2) Gram G_ij from exact thermal correlators (high-precision + interval audit); (3) effective rank r(ε) = # singular values > ε vs N and vs ℓ; (4) TEST: does r saturate, and does log r at saturation scale with the horizon entropy proxy? Repeat across ℓ to get the scaling exponent. **Truth conditions:** ?₇-weak predicts saturation; ?₇-strong predicts entropy scaling. Free-field caveat recorded (entropy here is the field's, not gravitational — this is the toy tier only). **Falsifier:** unbounded rank growth at fixed ℓ. **Compute:** the heaviest spec here — dense Gram SVDs to N ~ 4000, mpmath precision sweeps; give the agent a full sprint. **DoD:** signed scaling report; ?₇ status memo.

## S5 — B7 empirical layer: Kelvin relation

**Data:** tabulated Seebeck (S) and Peltier (Π) coefficients for 3–5 materials at matched T. **Test:** Π = T·S is Onsager reciprocity in disguise; run the B7 completion with Π hidden → reciprocity must FORCE Π = TS within measurement intervals; report per-material certificates. **Falsifier:** certified violation beyond error bars (would contradict microreversibility — escalate, audit data first). **DoD:** b7 REAL certificate; the program's second real-data composition/symmetry law after B4.

## Queued behind: B8-nonlinear (certified closure dimension from R15-addendum Adoption D — replace trial-and-error latent dimension with B3-rank certificates on delay-embedded data); arrival-time catalogue (R14 Adoption C).

## Engine growth path (per-sprint standing task)

Each sprint adds ≥1 theorem-anchored rule to the Atlas Engine (candidates: OS-reconstruction Pos→Uni for Euclidean-type rows; Nernst/third-law rules for the thermal row; strong-subadditivity rules for Thm→Cmp on quantum rows) and re-runs propagation. The matrix is now a living derivation object; its fixpoint should tighten monotonically with the benchmark record.
