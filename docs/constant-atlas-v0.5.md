# Observational Decompilation of Physics — Constant Atlas & Restraint Program v0.5

**Central conjecture (speculative, clearly labeled):**
> Fundamental constants are not primitive numbers. They are invariants — eigenvalue ratios, residues, indices, anomaly coefficients, fixed-point data — of a single positive, compositional, scale-consistent operator structure 𝕽. The composition rule, not any individual law, is the missing object.

**Defensible claim (what we actually assert today):**
> Many constants and laws can be represented as invariants of *compatible* algebraic, spectral, compositional, and RG structures. Whether one structure forces all of them is the research question, not an assumption.

**Changelog:** see §9. v0.3: G Cmp ?₃→P. v0.4: gauge Cmp ?₅→H. v0.5: G Pos ?₂→P (2D CFT QNEC ≡ Schur-pivot positivity; H-track).

---

## 0. Epistemic ground rules

| Symbol | Meaning | Rule |
|---|---|---|
| **H** | Established hard restraint | May be used as an axiom / rejection gate |
| **P** | Partial or framework-dependent | May constrain, never reject alone |
| **?** | **Predicted** restraint (forced by the synthesis, not yet demonstrated) | Treated as a *conjecture with an attached falsifiable test*. Never used as evidence for the synthesis that generated it. |
| **—** | Not applicable | — |

Three non-negotiable disciplines:

1. **No circularity.** A `?` filled in "because the synthesis demands it" is a *prediction*. It earns H status only via an independent derivation or empirical test. Until then a candidate rule that relies on it scores **unknown, not pass**.
2. **Uncertified ≠ pass.** Score(𝕽) = ∞ if any applicable hard constraint is violated *or uncertified*. (Interval certification standard: e.g. G₀₀ > 0 and Schur pivot S₂ = G₂₂ − G₀₂²/G₀₀ > 0 on every adaptive interval, audited normalization and signs. The certified base layer stays trusted; unaudited extensions stay quarantined.)
3. **Dimensionless or it didn't happen.** Only dimensionless invariants are comparison objects. c, ħ, k_B, and (in Planck-unit conventions) G are unit conventions once used to define units; the physical content lives in α, mass ratios, mixing angles, S/k_B, A/4ℓ_P², etc.

---

## 1. Constant Atlas v0.5 — dependency classes

**Class U (unit conventions):** c, ħ, k_B, (G as unit-setter). Physical content: *which structures they mediate*, not their values.

**Class D (dimensionless couplings):** α ≈ 1/137.036, α_s(M_Z), sin²θ_W, λ_Higgs.

**Class S (symmetry-breaking scales, as ratios):** v/M_Pl, Λ_QCD/M_Pl.

**Class F (flavor):** 9 charged-fermion Yukawa ratios, 4 CKM parameters, 4+ PMNS parameters, neutrino mass ratios/ordering.

**Class T (topological/quantized):** θ_QCD (< 10⁻¹⁰), electric charge quantization, generation number N_g = 3, anomaly coefficients (which cancel — a solved "blank").

**Class C (cosmological/state):** Λℓ_P² ≈ 10⁻¹²², Ω_b, Ω_c, Ω_Λ, n_s, A_s, η_B (baryon asymmetry).

**Class R (derived — unit tests, not inputs):** m_p/m_e ≈ 1836.15 (≈ f(α_s, quark Yukawas)), Rydberg, G_F = 1/(√2 v²), M_W = gv/2, M_Z = (v/2)√(g²+g′²), e = g sinθ_W = g′cosθ_W, S_BH/k_B = A/4ℓ_P².

**Dependency-graph rule:** an edge q → q′ exists iff q′ is computable from q within an established framework. The identifiable parameter count d_identifiable is the number of source nodes after removing unit/scheme/gauge redundancy. Current Standard Model + ΛCDM: ~19 + ~7 sources. **The program's success metric is reducing this number.**

---

## 2. Restraint Matrix v0.5

Columns: Sym = symmetry · Pos = positivity (Gram/moment/Choi/energy conditions) · Uni = unitarity · Cau = causality/analyticity · Cmp = composition (tensor/cluster/associativity) · RG = scale-flow consistency · Top = topology/quantization · Thm = thermodynamics/information.

| Constant block | Sym | Pos | Uni | Cau | Cmp | RG | Top | Thm |
|---|---|---|---|---|---|---|---|---|
| c (causal structure) | **H** (Lorentz) | — | — | **H** | P (velocity comp.) | — | — | **?₁** |
| ħ (quantum scale) | P | **H** (Gram/uncert.) | **H** | P | **H** (⊗, established) | — | P (quantized action) | P (Landauer, bounds) |
| G (gravity) | **H** (diffeo) | **P** (2D CFT: QNEC ≡ Schur-pivot positivity; H-track) | — | **H** | **P** (H-track; area theorem = composition law) | **?₄** (asympt. safety?) | P (Euler/GHY terms) | **H** (S=A/4ℓ_P²) |
| k_B | P | **H** (entropy ≥ 0) | — | — | **H** (extensivity/subadd.) | — | — | **H** |
| α (QED) | **H** (U(1)) | P (spectral fn ≥ 0) | **H** | **H** (Kramers–Kronig) | **H** (cluster / factorization) | **H** (running) | P (Dirac quantization) | P |
| α_s (QCD) | **H** (SU(3)) | P | **H** | **H** | **H** (cluster / factorization) | **H** (asympt. freedom) | **H** (instantons, θ-sectors) | P (confinement/deconf.) |
| Electroweak block (g, g′, v) | **H** | P | **H** | **H** | **H** (cluster / factorization) | **H** | P (sphalerons) | P |
| λ_Higgs | P (custodial) | **H** (vacuum stability!) | **H** | **H** | ? | **H** (near-criticality) | — | P (metastability) |
| Yukawa / CKM | **H** (flavor basis inv.) | P | **H** (unitarity triangles!) | P | ? | **H** | **?₆** (N_g as index?) | P |
| Neutrino sector | **H** | P | **H** (PMNS unitarity — test!) | P | ? | P | **?₆** | P |
| θ_QCD | **H** (CP) | P | **H** | P | ? | **H** (θ doesn't run pert.) | **H** (integer winding) | P |
| Λ, cosmological | P (de Sitter?) | **?₇** (dS entropy bounds) | — | **H** | **?₈** | **?₉** (Λ as IR fixed pt?) | **?₁₀** | **H** (S_dS = A/4ℓ_P²) |
| Initial/state params (n_s, A_s, η_B) | P | **H** (spectra ≥ 0, ρ ⪰ 0) | P | P (horizon problem) | ? | P | — | P (2nd law arrow) |

**Already-solved blanks (proof the method works):** anomaly cancellation (Top column of the fermion sector was a `?` in 1970; hypercharge assignments are now *forced*, H). CKM unitarity (Pos/Uni was a prediction; unitarity-triangle closure is now a precision test). Vacuum stability bound on λ_Higgs (Pos was unintuitive; m_H = 125 GeV sits eerily on the boundary).

---

## 3. The blank-filling table — every `?` is a conjecture + test

| # | Predicted restraint | Why the synthesis forces it | Concrete test / falsifier |
|---|---|---|---|
| ?₁ | c ↔ Thermodynamics | Jacobson (1995): Einstein equations derivable as an equation of state from δQ = T dS on local horizons. Causal structure and entropy flow are not independent columns. | Derive the velocity-composition law from entropy monotonicity alone in a toy causal-set/thermal model. Falsifier: a consistent thermal model with superluminal signaling and intact GSL. |
| ?₂ → **P** | G positivity → H | Generalized Second Law + quantum focusing (QNEC) supply operator-level positivity (⟨T_kk⟩ bounded by entropy derivatives). | **PROMOTED (edit-003, 2026-07-11):** B6 certificate — 2D QNEC ≡ PSD([[c/6,S'],[S',2πT−S'']]); vacuum/coherent/thermal instances + negative control. Status **P (H-track)** — H requires GNS realization of M as ω(A_i†A_j). |
| ?₃ → **P** | G composition rule | If S = A/4ℓ_P² is fundamental, merging subsystems must satisfy entropy subadditivity ↔ horizon-area theorems. Composition column of gravity = area theorem. | **PROMOTED (edit-001, 2026-07-11):** B4 REAL certificate on GW250114 (P_lower=0.99977) and GW150914 (P_lower=0.99862); external anchors Isi et al. PRL 2021, LVK PRL 135, 111403 (2025), GWTC-4 ≳5σ. Status **P (H-track)** — H requires population ringdown tests / structural unification with ?₂. |
| ?₄ | G RG flow | A rule-object with universal 𝓡_μ cannot exempt gravity. Predicts G(μ) with a fixed point (asymptotic safety) or embedding scale. | Lattice/functional-RG fixed-point searches; falsifier: proof of no UV completion within the same 𝓡_μ that governs matter couplings. |
| ?₅ → **H** | Composition column of all gauge couplings → H | Cluster decomposition + associativity of ⊗ are theorems in axiomatic QFT; the couplings inherit them. This is the *least* speculative blank: mostly bookkeeping. | **PROMOTED (edit-002, 2026-07-11):** B5 certificate — factorization R_24 = A_22²; d_identifiable = 1; channel-dependent couplings rejected. External anchors: Weinberg QFT Vol. 1; Haag LQP. |
| ?₆ | Flavor ↔ Topology | If constants are invariants, the *integer* N_g = 3 is the most index-like object in the table. Predicts generation number = index of some operator D (à la index theorems / family index). | Search: does any candidate D in the bridge produce ind(D) = 3 *and* correlate hierarchy patterns with spectral gaps? Falsifier: candidate structures reproduce couplings but leave N_g arbitrary. |
| ?₇ | Λ ↔ Positivity | dS entropy finite ⇒ dimension of accessible Hilbert space bounded ⇒ Gram matrices of cosmological correlators have *finite rank*. Flat-extension theorems then become physical: Λ as a rank condition. | Look for finite-rank / flat-extension signatures in cosmological correlation data (CMB moment matrices). This is the wildest and most original prediction of the program. |
| ?₈ | Λ composition | Vacuum energy must compose consistently under subsystem union (extensivity violation is exactly its weirdness). Predicts Λ is *not* a local coupling but a global state invariant — type "cosmological state," not "coupling." | If Λ reclassifies as state data, it should drop out of the local dependency graph; check that no local RG-invariant reproduces 10⁻¹²². |
| ?₉ | Λ RG | If ?₈ holds: Λℓ_P² is an IR fixed-point datum of 𝓡_μ, not a bare input. | Functional RG toy models: does any positive, compositional flow generically produce hierarchically small IR invariants? |
| ?₁₀ | Λ topology | dS entropy A/4ℓ_P² being (near-)integer-quantized in fundamental units would be the smoking gun. | Almost untestable directly; keep as marker. |

**Reading of the matrix as data:** the Composition column was systematically empty across established physics. That is the program's core empirical observation — *we possess dynamical rules in every sector but a composition rule in almost none outside quantum mechanics proper.* The blank column IS the conjectured missing grammar. **v0.3** filled gravity Cmp (?₃ → P, H-track). **v0.4** fills gauge Cmp (?₅ → H). **v0.5** fills gravity Pos (?₂ → P, H-track) via QNEC ≡ Schur-pivot positivity in 2D CFT.

---

## 4. Physical Bridge Formula (formal)

Candidate rule-object:

    𝕽 = (𝒜, †, 1, ω, ⊗, Φ, D, 𝓡_μ, 𝒞)

𝒜: observable *-algebra · ω: state (ω(1)=1, ω(a†a) ≥ 0) · ⊗: subsystem composition · Φ: allowed processes (CP, trace-preserving) · D: self-adjoint spectral/dynamical operator · 𝓡_μ: scale flow · 𝒞: causal/symmetry/domain constraints.

Bridge:

    𝕽 → (K, G, spec D) → Γ_eff → { p_dimensionless }

with K(a,b) = ω(a†b), G_ij = K(A_i, A_j) ⪰ 0 (GNS), and the spectral-action *hypothesis* (model, not axiom):

    Γ_𝕽[Φ; μ] ~ Tr F(D²/μ²) + Γ_matter,   Γ_𝕽 = Σ_i g_i(μ) 𝒪_i[Φ] + …

Constants extracted only as invariants:

    p_𝕽 = Inv( {g_i(μ)}, spec D, ω, 𝓡_μ ),   with Σ_i β_i ∂I/∂g_i = 0 (RG-invariance requirement).

**Promotion rule:** no certified mathematical result is promoted into physics without an explicit map ending in a dimensionless observable and a falsifiable prediction. Until then: methodological, not physical.

---

## 5. Discipline Formula (v0.2, frozen)

Type assignment: type(q) ∈ {state, moment, process, correlator, amplitude, RG coupling, topological, cosmological-state}.

Restraint bundle: 𝒞_required(q) = 𝒞_universal ∪ 𝒞_type(q) ∪ 𝒞_domain(q).

Feasible set 𝔉(𝒟): G ⪰ 0 (GNS) · M ⪰ 0 and M_{g_r} ⪰ 0 (moment/localizing) · J(Φ) ⪰ 0, Tr_out J = I (Choi) · D = D† · reflection positivity where applicable · causality/analyticity dispersion bounds where applicable · 𝓡_{μ₁}∘𝓡_{μ₂} ≃ 𝓡_{μ₁μ₂} · composition & symmetry relations.

    Score(𝕽) = ∞  if any applicable hard constraint is violated OR uncertified;
    Score(𝕽) = χ²_holdout + λ·L(𝕽) + η·d_identifiable(𝕽) + ζ·U_prediction  otherwise.

Promotion requires ALL of: (1) all hard constraints certified, (2) ≥ 2 domains reproduced from the same 𝕽, (3) d_identifiable strictly reduced, (4) survives held-out *domains* (not points), (5) ≥ 1 novel prediction survives a blind test.

---

## 6. Decoding Chain — the base algorithm

    𝒟_obs → 𝓘_invariant → K → G → D → 𝕽 → Γ_eff → p_dimensionless → held-out prediction

1. **Ingest** measurements with calibration, uncertainty, scale μ, and scheme metadata (CODATA, PDG).
2. **Invariantize:** convert to dimensionless RG-invariant combinations; discard unit conventions.
3. **Graph:** build the dependency graph; identify source nodes; compute d_identifiable.
4. **Type & bundle:** assign type(q) and 𝒞_required(q); populate the restraint matrix; every blank becomes a numbered conjecture with a falsifier (§3).
5. **Generate candidates:** symbolic regression / SINDy / spectral inference / bootstrap — *candidate generators only, never proof*.
6. **Gate:** reject on any certified hard-constraint violation; quarantine on "uncertified."
7. **Fit** only residual parameters the structure does not determine.
8. **Attack:** forward-simulate; generate adversarial counterexamples; attempt to break positivity certificates.
9. **Blind test** on withheld domains.
10. **Promote or demote** per §5; log the certificate: *forced / permitted / free* for every quantity.

---

## 7. Benchmark suite v0 (build order)

| # | Benchmark | Validates | Deliverable |
|---|---|---|---|
| B1 | Truncated moment problem: hide moments of a known finite measure; recover via M ⪰ 0 + flat extension (Curto–Fialkow) | Spectral-completion module; interval-certified positivity gates | Solver + certificate format |
| B2 | Qubit process tomography with hidden entries; recover via Choi J(Φ) ⪰ 0 + trace condition | Process/composition constraints | CP-map completion module |
| B3 | Electroweak closed system: pseudo-data for (e, g, g′, θ_W, M_W, M_Z, v, G_F); algorithm must *discover* the relations and report d_identifiable = 3 | Full chain end-to-end on real structure | **DONE** — `certificates/b3_certificate.json`; d_identifiable = 3, FREE `{g, g′, v}` |
| B4 | BH thermodynamics: LIGO merger catalog → verify area theorem as composition law (?₃) | First cross-domain blank-fill promoted from ? to P | **DONE** — `certificates/b4_certificate.json` (REAL); ?₃ → P (H-track) |
| B5 | Multi-channel factorization / cluster decomposition (?₅) | Gauge Cmp column → H; one coupling across channels | **DONE** — `certificates/b5_certificate.json`; d_identifiable = 1; ?₅ → H |
| B6 | 2D QNEC as certified Schur-pivot positivity (?₂) | G Pos column → P (H-track); verifier-standard reformulation | **DONE** — `certificates/b6_certificate.json`; ?₂ → P (H-track) |
| B7 | Onsager transport-matrix completion (L ⪰ 0 + L = Lᵀ) | Restraint stacking on effective-coefficient type; Thm/Sym columns | **DONE** — `certificates/b7_certificate.json` (R15 seed) |

Then: GNS realization of the QNEC matrix M (P→H for ?₂); unification of GSL/?₃; ?₇ toy-dS rank saturation; PDG layer for B5; flavor/topology search (?₆).

---

## 8. Status ledger

- Certified base layer: interval-certified G₀₀ > 0 and S₂ Schur pivot — **trusted**.
- Unaudited normalizations/signs — **quarantined**.
- Spectral action — **model hypothesis**.
- One-structure-for-everything — **conjecture**; the narrower compatibility claim is the working assertion.
- Composition column — **G Cmp = P (H-track)**; **gauge Cmp = H** (α, α_s, EW); remaining Cmp blanks (Yukawa/Λ/…) still open.
- Positivity column — **G Pos = P (H-track)** via 2D QNEC ≡ Schur pivot (B6); GNS identification of M remains open for H.
- B1–B7 — **implemented** with certificates; next: ?₇ / GNS for ?₂ / PDG for B5.

---

## 9. Changelog

| Version | Date | Edit | Summary |
|---|---|---|---|
| v0.2 | — | — | Initial restraint matrix and blank-filling table (?₁–?₁₀). |
| v0.3 | 2026-07-11 | [edit-001](atlas-edits/edit-001-conjecture3-promotion.md) `1ff977d4bcf2ae2b3525a7b6ea29e0b84fffb192` | Promote G Cmp ?₃ → **P (H-track)** (area theorem = composition law). Evidence: B4 REAL certificate + external LVK/Isi anchors. |
| v0.4 | 2026-07-11 | [edit-002](atlas-edits/edit-002-conjecture5-promotion.md) `73376f9ca3453efc1a4d88206634f09135ff6b64` | Promote gauge Cmp ?₅ → **H** for α, α_s, electroweak. Evidence: B5 factorization certificate (d_identifiable = 1) + Weinberg/Haag anchors. |
| v0.5 | 2026-07-11 | [edit-003](atlas-edits/edit-003-conjecture2-qnec.md) `43a9a8b1e1158a2e4519726c2d95a32e58879ecf` | Promote G Pos ?₂ → **P (H-track)** (2D QNEC ≡ certified Schur-pivot positivity). Evidence: B6 certificate + Wall/BFKW anchors. H requires GNS realization of M. |
| v0.5+R14 | 2026-07-11 | — (infra; no matrix cell) | Adopt Maudlin arXiv:2512.22618 as METHOD R14: mandatory `m_layer_stipulations` in certificate format v0.3; B2 device↔POVM scope clause; queued arrival-time track. See `docs/references.md`, `docs/notes/measurement-interface-maudlin.md`. |
| v0.5+R15 | 2026-07-11 | — (infra + B7; no matrix cell) | Adopt Chen et al. Nat. Comput. Sci. 2024 as METHOD R15: constraint-native generators (firewall), closure-as-dynamical-d_identifiable; implement B7 Onsager transport-matrix completion. See `docs/notes/onsager-sonsagernet-chen2024.md`. |
