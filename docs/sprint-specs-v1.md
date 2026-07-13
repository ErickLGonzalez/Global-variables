# Sprint Specifications v1 — Computational Work Packages

Deep-research specs so each sprint starts with a full work order: inputs, algorithm, certificate class, falsifier, and definition-of-done. Ordered by (payoff × readiness).

---

## S1 — Ratify the engine's first pass (atlas v0.6) ✅ DONE

**Goal:** convert Atlas Engine propagations into edit records. **Work:** (1) edit-004: Cmp ?→P for λ_H, Yukawa, neutrino, θ_QCD [R-CLUSTER chains]; (2) edit-005: Top ?→P (weak ?₆) for Yukawa/neutrino [R-ANOMALY], explicitly leaving the index form of ?₆ open; (3) edit-006: Λ Pos ?→P (weak ?₇) [R-DS-ENTROPY], rank form open; (4) resolve the two engine findings — annotate the Sym column (internal vs spacetime), and adjudicate gravity's Uni="—" → **P** (semiclassical boundary/horizon unitarity). **Class:** structural-derivation → human ratification. **DoD:** atlas v0.6 with changelog; engine re-run reproduces v0.6 as its own fixpoint (idempotence check). **Status:** applied 2026-07-11 — `docs/constant-atlas-v0.6.md`; T6 idempotence green; standing rule R-OS-UNI added.

## S2 — GNS realization for ?₂ → H (the decisive item) — PARTIAL

**Honest framing:** any PSD 2×2 matrix is trivially a Gram matrix (Cholesky); the deliverable is a *physical* realization: operators A₀, A₁ and state ω in an actual QFT with ω(A_i†A_j) = M_ij = [[c/6, S′],[S′, 2πT − S″]]. **Route (computable):** free-fermion chain (Gaussian states — everything is determinants). (1) Build reduced density matrices ρ_A for intervals from correlation matrices; (2) compute relative entropy S(ρ‖σ) and its first/second null-cut derivatives numerically with interval bounds (quarantined class); (3) test the candidate identification A₀ ~ 1-normalized modular charge, A₁ ~ null-momentum density smeared at the cut, against M's entries across states (vacuum, thermal, coherent); (4) success = one operator pair reproducing M for ALL tested states within certified intervals. **Falsifier:** no state-independent operator pair exists (would demote the Gram interpretation to accidental). **Compute:** O(hours) laptop-scale; chains L ≤ 400. **DoD:** edit-007 draft (?₂→H conditions partially met: GNS item), or a documented obstruction.

**Status (2026-07-13):** PARTIAL — (a) operator probe: continuum vacuum GNS ray exact; geometric (K, cut-T) pair does **not** track M ratios at L≤120; (b) **state layer** (5/5): `s2_gns/gaussian.py` + `qnec_lattice.py` — c blind-fit, vacuum saturation Q→0, thermal identity Q=cπ²/(3β²), modular first law, positivity gate; (c) **S2-b exact-kernel orbit** (6/6): fixed `modular_1p(C_vac)` on boosted coherent orbit — dual-route S_rel <0.5%, local ansatz ≥10× worse, capacity=entropy Gram entry; lattice bulk mismatch attributed to Eisler–Peschel long-range structure (erratum: CH bilocal is multi-interval). Certificates: `s2_gns_certificate.json`, `s2_certificate.json`, `s2b_certificate.json`. Notes: `docs/notes/s2-gns-free-fermion.md`, `docs/notes/s2-gns-status.md`. Draft edit-007 (not applied). Next: multi-interval bilocal modular term or thermal/coherent holdouts for state-independent M tracking.

## S3 — PDG empirical layer for B5

**Data:** R-ratio σ(e⁺e⁻→hadrons)/σ(→μ⁺μ⁻) vs √s (PDG tables); τ hadronic branching; Z hadronic width. **Algorithm:** the B5 factorization identities predict ONE α_s governs all three after RG evolution; run the B3-style pipeline: dimensionless invariants → single-coupling hypothesis vs channel-dependent alternative → Score comparison with holdout by *observable class*, not data point. Expected: single-coupling wins with the residuals attributable to known higher-order terms (report as the RG column, B3-PDG pattern). **Stipulations:** scheme (MS-bar), quark-mass thresholds, QED corrections. **Falsifier:** certified need for channel-dependent α_s after scheme/threshold effects. **DoD:** b5 REAL certificate + edit note strengthening ?₅'s empirical basis.

**Status (2026-07-14):** DONE (5/5) — `s3_pdg/running.py` + `tests/test_s3.py`: four independent measurement classes (τ, EW fit, lattice, tt̄) spanning 51× in scale evolve to one α_s(M_Z) = 0.1186 ± 0.0009 (χ²/dof = 0.11); no-running null rejected at ~13σ; Score A (d=1) beats B (d=4). Certificate: `s3_certificate.json`. Memo: `docs/atlas-edits/edit-008-s3-empirical-note.md` (no cell change).

## S4 — ?₇ toy-dS rank saturation (B1 engine, the wild one)

**Setup:** static-patch dS₂ ≅ thermal state at T_dS = 1/2πℓ for a conformal field — thermal 2-point functions are exact (hyperbolic kernels, cf. B6's coth variable). **Algorithm:** (1) observables = smeared field modes {φ(f_k)} on the patch, k = 1..N; (2) Gram G_ij from exact thermal correlators (high-precision + interval audit); (3) effective rank r(ε) = # singular values > ε vs N and vs ℓ; (4) TEST: does r saturate, and does log r at saturation scale with the horizon entropy proxy? Repeat across ℓ to get the scaling exponent. **Truth conditions:** ?₇-weak predicts saturation; ?₇-strong predicts entropy scaling. Free-field caveat recorded (entropy here is the field's, not gravitational — this is the toy tier only). **Falsifier:** unbounded rank growth at fixed ℓ. **Compute:** dense Gram spectra with k-grid doubling audit. **DoD:** signed scaling report; ?₇ status memo.

**Status (2026-07-14):** DONE (5/5) — `s4_ds/kernel.py` + `tests/test_s4.py`: ?₇-weak confirmed (horizon-weighted rank saturates; unweighted control grows); naive ?₇-strong fails (kinematic rank ~ ℓ); **refinement discovered**: information Gram `D C(1−C) D` has ℓ-independent saturated rank tracking entropy; B1 compression certificate + k-grid audit pass. Certificate: `s4_certificate.json`. BEC bridge: `docs/notes/experimental-program-bec.md` (EXP-C uses G_info signature).

## S5 — B7 empirical layer: Kelvin relation

**Data:** tabulated Seebeck (S) and Peltier (Π) coefficients for 3–5 materials at matched T. **Test:** Π = T·S is Onsager reciprocity in disguise; run the B7 completion with Π hidden → reciprocity must FORCE Π = TS within measurement intervals; report per-material certificates. **Falsifier:** certified violation beyond error bars (would contradict microreversibility — escalate, audit data first). **DoD:** b7 REAL certificate; the program's second real-data composition/symmetry law after B4.

**Next-phase roadmap:** after S1–S4 and B10, see [`docs/roadmap-v2.md`](roadmap-v2.md) and [`docs/SPECIFICATION.md`](SPECIFICATION.md).

## Queued behind: B8-nonlinear (certified closure dimension from R15-addendum Adoption D — replace trial-and-error latent dimension with B3-rank certificates on delay-embedded data); arrival-time catalogue (R14 Adoption C).

## Engine growth path (per-sprint standing task)

Each sprint adds ≥1 theorem-anchored rule to the Atlas Engine (candidates: OS-reconstruction Pos→Uni for Euclidean-type rows; Nernst/third-law rules for the thermal row; strong-subadditivity rules for Thm→Cmp on quantum rows) and re-runs propagation. The matrix is now a living derivation object; its fixpoint should tighten monotonically with the benchmark record.
