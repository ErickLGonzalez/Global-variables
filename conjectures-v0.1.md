# Conjectures ?₁–?₁₀ — Expanded Research Briefs (v0.1)

Companion to `constant-atlas-v0.2.md`. Each brief follows the fixed schema:
**Statement · Why the synthesis forces it · Formalization · Test protocol · Falsifier · Status · Anchors.**
A conjecture is *never* evidence for the synthesis that generated it. Promotion path: ? → P (independent derivation or empirical support in a restricted regime) → H (established across regimes).

---

## ?₁ — Causal structure is thermodynamically forced (c ↔ Thm)

**Statement.** The Lorentzian causal structure (finite invariant speed, relativistic velocity composition) is derivable from thermodynamic consistency of local horizons; the c-row's Thermodynamics entry is H, not —.

**Why forced.** In the synthesis, no column may be independent for a unit-setting constant: c mediates the causal *and* the entropic interface (every horizon entropy formula carries c³). Jacobson (1995) derived the Einstein equations as an equation of state from δQ = T dS on local Rindler horizons — dynamics from thermodynamics. The conjecture extends this downward: not just gravitational dynamics, but the causal composition law itself.

**Formalization.** Let 𝕽 carry a state ω, a modular flow (Tomita–Takesaki) on wedge algebras, and entropy S(ω|region). Claim: demanding (i) S finite on bounded diamonds, (ii) generalized second law (GSL) under inclusion, (iii) composition consistency of nested wedges, forces the automorphism group of the causal order to be the Poincaré group (up to conformal factor), and forces the velocity-composition law u⊕v = (u+v)/(1+uv/c²).

**Test protocol.** (a) Toy model: causal sets or a 2D lattice with a thermal state; check whether GSL + composition already excludes Galilean composition. (b) Literature bridge: modular theory yields boost generators on wedges (Bisognano–Wichmann); formalize the step "modular flow = geometric boost" as the mechanism forcing finite c.

**Falsifier.** A mathematically consistent model with (i)–(iii) intact and superluminal signaling or Galilean composition.

**Status.** ? → promising; the Bisognano–Wichmann and Jacobson results are rigorous anchors, the downward extension is open.

**Anchors.** Jacobson 1995; Bisognano–Wichmann theorem; Bousso covariant entropy bound.

---

## ?₂ — Gravitational positivity upgrades to H via QNEC/GSL (G ↔ Pos)

**Statement.** Gravity's Positivity entry is a hard operator-level constraint: the Quantum Null Energy Condition ⟨T_kk⟩ ≥ (ħ/2π) S″ and the GSL are the gravitational instances of Gram positivity.

**Why forced.** In 𝕽, positivity is universal (ω(a†a) ≥ 0). Classical energy conditions fail quantum-mechanically, which looked like gravity escaping the Positivity column. QNEC restores it *as an entropy-corrected Gram inequality* — precisely the pattern the synthesis predicts: apparent positivity violations signal a missing information-theoretic term, not an exemption.

**Formalization.** QNEC as a Schur-complement condition: define the two-entry Gram block G₀₀ = ⟨T_kk⟩, cross terms from relative-entropy variations; QNEC ⇔ a pivot inequality of the same form as S₂ = G₂₂ − G₀₂²/G₀₀ > 0. Making this identification exact (via relative modular operators, where QNEC has been proven from relative entropy monotonicity) is the deliverable.

**Test protocol.** (a) Reproduce the free-field / 2D CFT QNEC proofs inside the interval-certified verifier: express the proof's key inequality as certified pivot positivity. (b) Numerical lattice check in an interacting 2D model.

**Falsifier.** A consistent QFT-coupled-to-gravity regime with certified QNEC violation and intact unitarity/causality.

**Status.** ? → near-P: QNEC is proven in wide QFT classes (Balakrishnan–Faulkner–Khandker–Wang); the *Gram/Schur reformulation* is our open work item.

**Anchors.** Bousso et al. (QNEC); Faulkner et al. proof via modular theory; Wall's GSL proof.

---

## ?₃ — The area theorem is gravity's composition law (G ↔ Cmp) — FIRST PROMOTION CANDIDATE

**Statement.** Horizon-area additivity under merger, A_final ≥ A₁ + A₂, is the Composition-column entry for G: entropy subadditivity realized geometrically.

**Why forced.** The synthesis says every sector must possess a composition rule. If S = A/4ℓ_P² is fundamental, composing two gravitating subsystems must respect quantum entropy inequalities; Hawking's area theorem is exactly that statement projected onto horizons.

**Formalization.** ⊗-composition of horizon states ω₁, ω₂ → ω₁₂ with S(ω₁₂) ≥ S(ω₁) + S(ω₂) (entropy production under merger) ⇔ A₁₂ ≥ A₁ + A₂. Dimensionless invariant per event: η_A = (A_f − A₁ − A₂)/A_f ∈ [0, 1).

**Test protocol.** This is benchmark **B4** and is *already empirically supported*: LIGO–Virgo tested the area theorem on GW150914 (Isi et al. 2021, ~97% confidence; later catalogs strengthen it). Pipeline: pull public GWTC posterior samples → compute η_A per event with propagated uncertainty → certify A_f − A₁ − A₂ > 0 at stated credibility → emit a composition-law certificate.

**Falsifier.** A merger with certified area decrease (would also violate the GSL — catastrophic for the whole program, which is what makes it a *good* test).

**Status.** **PROMOTED to P (H-track)** — atlas edit-001, `constant-atlas-v0.3.md` (2026-07-11). B4 REAL certificate: GW250114 P_lower=0.99977, GW150914 P_lower=0.99862. H requires population ringdown tests and structural unification with ?₂.

**Anchors.** Hawking area theorem; Isi–Farr–Giesler–Scheel–Teukolsky 2021; LVK PRL 135, 111403 (2025); GWTC-4 ≳5σ analyses; `certificates/b4_certificate.json`.

---

## ?₄ — G participates in universal scale flow (G ↔ RG)

**Statement.** Newton's constant is a running coupling of the same 𝓡_μ that governs matter: G(μ) with a nontrivial UV fixed point (asymptotic safety) or an explicit embedding scale; "G does not run" is excluded in 𝕽.

**Why forced.** 𝓡_μ is a *universal* structure map of 𝕽; exempting one coupling breaks composition of the flow (𝓡_{μ₁}∘𝓡_{μ₂} ≃ 𝓡_{μ₁μ₂}) on the gravity–matter product sector.

**Formalization.** Dimensionless g(μ) = G(μ)μ². Conjecture: β_g has a fixed point g* > 0 with finite-dimensional critical surface, and matter content shifts g* in a way correlated with the matter columns of the atlas (a *cross-column* prediction).

**Test protocol.** Functional RG computations of g* as a function of (N_scalar, N_fermion, N_vector); check whether the Standard Model matter content lies inside the safe region — a nontrivial consistency test linking the gravity row to the flavor row.

**Falsifier.** Proof that no UV completion exists within the same flow category that renormalizes the matter sector (e.g., only string-type completions with structurally different 𝓡).

**Status.** ?; substantial but unsettled literature.

**Anchors.** Weinberg's asymptotic safety; Reuter fixed point; functional RG reviews (Percacci; Eichhorn).

---

## ?₅ — Composition column of gauge couplings is H (least speculative)

**Statement.** α, α_s, and the electroweak couplings inherit hard composition restraints — cluster decomposition, ⊗-associativity, factorization of amplitudes on multi-sector states — as theorems, not conjectures.

**Why forced.** Cluster decomposition and tensorial subsystem composition are axioms/theorems of local QFT (Wightman/Haag frameworks); couplings are coefficients inside a structure that already composes. The column is blank by bookkeeping omission, not physics.

**Formalization.** For spacelike-separated preparations, ⟨𝒪_A 𝒪_B⟩ → ⟨𝒪_A⟩⟨𝒪_B⟩; amplitudes factorize on multi-particle poles with residues fixed by the *same* coupling appearing in single-sector processes. The composition entry for a coupling g = the statement "one g governs all factorization channels."

**Test protocol.** Benchmark extension of B3: generate pseudo-data for 2→2 and 2→4 processes; the decoding chain must *discover* that one parameter controls both (d_identifiable collapse), then verify on real PDG cross-section ratios.

**Falsifier.** Any certified need for channel-dependent couplings after scheme/RG effects are removed — this would falsify locality itself.

**Status.** **PROMOTED to H** — atlas edit-002, `constant-atlas-v0.4.md` (2026-07-11). B5 certificate: factorization R_24 = A_22²; d_identifiable = 1; channel-dependent couplings rejected.

**Anchors.** Weinberg QFT Vol. 1 (cluster decomposition); Haag, Local Quantum Physics; `certificates/b5_certificate.json`.

---

## ?₆ — Generation number is an index (Flavor ↔ Top)

**Statement.** N_g = 3 is a topological invariant — the index of an operator in 𝕽 (family index / zero-mode count) — and flavor hierarchies correlate with spectral data of the same operator.

**Why forced.** In the synthesis, exact integers are index-like, never fitted. N_g is the sharpest unexplained integer in physics. Anomaly cancellation (the historical solved blank) already ties integer charge assignments to topology; N_g should be its sibling.

**Formalization.** Find D and a compact auxiliary structure X with ind(D_X) = dim ker D₊ − dim ker D₋ = 3, such that the Yukawa matrices arise as overlap integrals of the three zero-modes — predicting *correlations* between mass hierarchy and mixing angles rather than independent parameters.

**Test protocol.** (a) Survey: string compactifications (Euler-characteristic counting χ/2 = N_g), noncommutative-geometry Standard Model (where N_g is currently *inserted by hand* — a known deficiency to attack), domain-wall zero modes. (b) Concrete search: within spectral-triple models, scan for minimal geometries where 3 is forced and check the induced Yukawa textures against CKM/PMNS data via the decoding chain.

**Falsifier.** Demonstration that candidate structures reproducing the coupling sectors leave N_g strictly arbitrary (a modulus with no index interpretation) across the whole feasible set 𝔉.

**Status.** ? — the deepest and hardest; high payoff.

**Anchors.** Atiyah–Singer index theorem; Candelas–Horowitz–Strominger–Witten (χ/2 counting); Chamseddine–Connes spectral Standard Model.

---

## ?₇ — Λ is a rank condition (Λ ↔ Pos) — MOST ORIGINAL

**Statement.** A positive cosmological constant bounds the accessible Hilbert space (finite de Sitter entropy S_dS = A/4ℓ_P² ⇒ dim ℋ_eff ≲ e^{S_dS}); therefore cosmological correlator Gram/moment matrices have *effectively finite rank*, and Λ is recoverable as a flat-extension rank datum — exactly the object B1 certifies.

**Why forced.** In 𝕽, every constant is an invariant of (K, G, spec D). Finite entropy is a rank statement about G. Λ is then not a coupling but the rank scale of the global state — mechanizing its reclassification (see ?₈).

**Formalization.** For a family of cosmological observables {A_i}, G_ij = ω_dS(A_i†A_j). Claim: rank growth of G_t saturates at t* with log rank(G_{t*}) ~ S_dS, and the flat-extension measure extracted at saturation encodes Λℓ_P².

**Test protocol.** (a) Toy: exact dS₂/dS₃ QFT correlators → build moment matrices → verify rank saturation scaling with the horizon entropy (fully computable). (b) Data: CMB multipole covariance as a proxy Gram matrix; search for certified effective-rank plateaus beyond noise/resolution artifacts (hard; treat with maximal skepticism about instrumental rank limits — this is the "measurement interface" trap).

**Falsifier.** Toy-model result showing rank grows without bound in dS at fixed entropy, or scaling with the wrong entropy power.

**Status.** ? — wildest conjecture in the program; also the one B1 was built to serve.

**Anchors.** Gibbons–Hawking dS entropy; Banks/Fischler finite-N dS proposals; Curto–Fialkow flat extension.

---

## ?₈ — Λ composes as state data, not as a local coupling (Λ ↔ Cmp)

**Statement.** Λ violates extensivity because it is global state data (type: cosmological-state) rather than a local coupling; under subsystem composition it behaves like a boundary/rank invariant, not an additive charge.

**Why forced.** The composition column cannot be blank; but vacuum energy composed additively gives the 10¹²² catastrophe. The synthesis resolves blanks by *retyping*, and the only type whose composition law is non-extensive is state/rank data (consistent with ?₇).

**Formalization.** In the dependency graph, move Λ from Class D (couplings) to Class C-state (source node of ω, not of 𝒜). Prediction: no RG-invariant built purely from local couplings reproduces Λℓ_P² ~ 10⁻¹²²; any successful formula must reference global state functionals (entropy, rank, horizon data).

**Test protocol.** Adversarial search (decoding-chain step 8): symbolic regression over local RG invariants with the Score function; certified failure to reach 10⁻¹²² without state functionals supports retyping. Include known partial results (Weinberg's no-go for adjusting mechanisms) as structural priors.

**Falsifier.** A certified local-coupling RG invariant that naturally lands at 10⁻¹²² with reduced d_identifiable.

**Status.** ?; conceptually strong, operationally subtle.

**Anchors.** Weinberg 1989 (CC no-go); Bousso bound; unimodular-gravity literature (Λ as integration constant — an existing retyping precedent).

---

## ?₉ — Λℓ_P² is IR fixed-point data of 𝓡_μ (Λ ↔ RG)

**Statement.** If ?₈ holds, the measured smallness of Λℓ_P² is an infrared fixed-point invariant of the universal flow — hierarchically small numbers are generic outputs of long flows, not fine-tuned inputs.

**Why forced.** State data in 𝕽 still transform under 𝓡_μ; a scale-consistent global state must sit at (or flow to) a fixed point of the induced flow on state space. Smallness then has the same origin as Λ_QCD/M_Pl: dimensional transmutation, exp(−#/g²)-type suppression.

**Formalization.** Induced flow ω_μ = 𝓡_μ*(ω); conjecture: the invariant I_Λ = Λℓ_P² satisfies I_Λ ~ e^{−c/g*} or a power thereof for generic positive compositional flows, with c computable from the matter content (linking to ?₄'s cross-column prediction).

**Test protocol.** Functional-RG toy models with coupled matter + state sector: measure the distribution of IR invariants over the feasible set 𝔉; test whether hierarchies ≲ 10⁻¹⁰⁰ occur with non-negligible measure *without* tuning (contrast with a null model of random couplings).

**Falsifier.** Demonstration that positive compositional flows generically produce O(1) IR state invariants, leaving 10⁻¹²² as irreducible tuning.

**Status.** ?; depends on ?₈.

**Anchors.** Wilsonian RG; dimensional transmutation (Coleman–Weinberg); asymptotic-safety cosmology literature.

---

## ?₁₀ — de Sitter entropy quantization (Λ ↔ Top)

**Statement.** S_dS/k_B = A_dS/4ℓ_P² is quantized (integer or rational with fixed denominator) in the exact theory; Λ inherits a topological restraint through horizon-entropy quantization.

**Why forced.** In 𝕽 the Topology column is populated wherever a quantity is secretly a counting invariant; ?₇ makes S_dS a log-dimension, and dimensions are integers.

**Formalization.** dim ℋ_dS = N ∈ ℕ ⇒ Λ = 3/(ℓ_P² · f(ln N)) takes discrete values; the spectrum of allowed Λ is exponentially dense at small Λ (observationally continuous — which is *why* this is nearly untestable directly).

**Test protocol.** Indirect only: consistency of the discrete spectrum with ?₇'s rank plateaus in toy dS models; any exact finite-N dS construction (e.g., matrix-model dS proposals) should exhibit both.

**Falsifier.** A consistent exact dS quantum theory with continuously tunable entropy at fixed ℓ_P.

**Status.** ? — marker conjecture; keep, don't fund.

**Anchors.** Banks finite-N conjecture; horizon-entropy quantization proposals (Bekenstein–Mukhanov lineage).

---

## Cross-conjecture structure (the payoff map)

Dependencies: ?₇ ⇒ ?₈ ⇒ ?₉; ?₇ + ?₉ ⇒ ?₁₀. ?₂ + ?₃ share the GSL. ?₄ ⇔ ?₉ share 𝓡_μ universality. ?₆ stands alone (highest risk, highest payoff).

Priority ordering by (testability × payoff):
1. **?₃** — **done (P, H-track)** via B4 REAL + edit-001 / atlas v0.3.
2. **?₅** — **done (H)** via B5 factorization + edit-002 / atlas v0.4.
3. **?₂** — Gram/Schur reformulation of QNEC; directly reuses the certified verifier.
4. **?₇** — toy dS rank-saturation study; B1 is the engine.
5. **?₁** — toy causal-thermal model.
6. **?₄, ?₈, ?₉** — modeling programs; **?₆** — long-horizon; **?₁₀** — marker.
