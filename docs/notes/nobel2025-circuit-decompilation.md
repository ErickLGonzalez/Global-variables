# Note: The 2025 Nobel as a Decompilation Recipe — Deep Research + Cross-Agent Review

**Scope:** 2025 Nobel Prize in Physics (Clarke, Devoret, Martinis — macroscopic quantum tunnelling and energy quantisation in an electric circuit), its causal paper chain (ledger R16–R22), its conversion into benchmark **B9**, and a comparison with a second AI agent's analysis of the same material. Filed 2026-07-13.

## 1. My independent reading of what the Nobel work IS, for this program

The physics headline (a macroscopic variable — the Josephson phase — tunnels and has discrete levels) matters to the atlas's ħ row. But the *methodological* headline matters to the whole program: **the Berkeley sequence is the cleanest historical execution of our discipline formula that we have found.**

The three-paper structure maps onto the decoding chain one-to-one: (1) *Resonant activation* (R17, 1984) = in-situ system identification — ω_p(I), Q, hence C and R measured independently on the working device; restraints calibrated one channel at a time. (2) *Energy-level quantization* (R18, 1985) = structure frozen, then the quantum spectrum predicted from classically-measured parameters with **no refitting** — literally promotion criterion 5 (novel prediction on a held-out **domain**, not held-out points). (3) *MQT* (R19, 1985) = a second held-out-domain confirmation with no adjustable junction parameters, closing the precursor era's ambiguity (R22: Voss–Webb-type saturation that *looked* quantum but had an uncertified environment).

Answer to the first research question — **does the recipe help build constraints for matrix item tests? Yes, in three distinct ways**, all now implemented in B9 (6/6 green):

- **The FDT gate.** σσᵀ = 2k_BT·M is an exact cross-link between the noise and dissipation objects — a Thm-column relation with teeth. Residual D − 2k_BT·M ≠ 0 certifiably signals a hidden bath, non-equilibrium environment, wrong temperature claim, or missing state variables (B9-T2). It is the quantitative instance of the engine's R-KMS rule, and the correct home for FDT in our architecture: a *benchmark gate between quantities*, not a new column-implication rule.
- **The independent-calibration theorem-in-practice.** B9-T3 is the sprint's most important result: on the *same corrupted data*, the FDT audit rejects at residual 0.49 when H_V comes from an independent spectroscopy channel, but passes at 0.02 when H_V is inferred from the trajectories themselves (Gibbs route) — the self-consistency loophole is *provably blind*. This is the Voss–Webb ambiguity and its Berkeley resolution reproduced computationally. Standing rule adopted: every certificate records its **calibration route**, and same-data self-consistent calibrations are never promotable evidence.
- **The prohibition as a gate.** "Do not explain low-temperature saturation by inflating σ or fitting an effective temperature" is now B9-T5: the shortcut produces a certified FDT failure (residual 0.89), not a fit option.

Answer to the second question — **do we have enough data to decode any current matrix items?** Two senses, two answers. (a) *Latent-dynamics matrices (M, W, σ, H_mn):* yes, decodable now — B9-T1 recovers M and canonical W to ≤2% from trajectories via the equilibrium identity K = −J_b·H_V⁻¹, with PSD and FDT certificates; B9-T6 builds the exact rational charge-basis Hamiltonian and passes the 1985-style held-out spectroscopy test (E01 within 0.31% of the independent asymptotic). (b) *Restraint-matrix (atlas) items:* the Nobel block strengthens the **ħ row** empirically (macroscopic energy quantization → Pos/Top entries) and supplies the R-KMS/FDT quantitative instance, but it does not by itself upgrade any cell from P to H — the honest statement is that it hardens the *machinery* that future upgrades must pass through. Real decoding of atlas cells continues to run through S1–S5.

## 2. Cross-agent comparison (second AI analysis, received 2026-07-13)

**Convergences (independent agreement — raises confidence):** the (M+W)∇H canonical mapping of RCSJ; W fixed by circuit topology before any learning; the coordinate/gauge warning (its §9 matches our R15-addendum canonicalization rule, derived independently — M, W entries transform as A(·)Aᵀ, so only invariants are chart-free); the identifiability fact that frequencies alone give eigenvalues of C⁻¹K, never the matrices (our B8 spectral-invariant lesson from the measurement side); and the effective-temperature prohibition.

**Adopted from the other agent (genuinely useful, previously unexplored by us):**
1. **The equilibrium estimator K = −J_b·H_V⁻¹ with sym/antisym split.** Its cleanest single contribution — it upgrades B8 from grammar *classification* to quantitative *decompilation*. Now the core of B9's estimate.py, with the PSD-cone check on the symmetric part.
2. **The hazard-function identity Γ(I) = İ·p(I)/S(I)** — converts switching histograms into physically meaningful escape rates instead of free-form fit targets. Recorded in R19's ledger trace for the future rare-event layer.
3. **The frequency-dependent bath escalation path** — M → M(ω) or auxiliary Markovian environment states when white-noise FDT fails structurally (quantum noise coth form). Recorded as the sanctioned escalation when B9-class FDT residuals are *structured* rather than flat.
4. **The minimum-norm skew solution W_min = (rgᵀ − grᵀ)/|g|² with the orthogonality test gᵀr = 0** — a clean away-from-equilibrium consistency check; queued for B9-nonlinear.
5. **The model-order inversion warning** (1D overdamped mobility = 1/G vs 2D M entry = G) — now B9-T4, demonstrated computationally and made a mandatory stipulation.

**Corrections / where my analysis goes further:**
1. **The other analysis has no promotion epistemics.** It maps physics → matrices excellently but never asks *what certifies what*: no FORCED/PERMITTED/REJECTED structure, no falsifiers, no certificate classes, no held-out discipline. Everything above was converted into gates before adoption — most importantly, its own recipe contains a latent circularity (Gibbs-route H_V) that it never flags; B9-T3 had to be *discovered by us* to make its pipeline honest.
2. **It misses the deepest connection:** that the three-paper sequence *is* the discipline formula's promotion rule executed historically. That reframing — the Nobel as a validation of the program's epistemics, not merely a source of formulas — is this note's central claim.
3. **Numerical prudence:** its quoted sample values (I_c = 9.489 μA, Q = 30±15, escape temperature 37.4±4.0 vs 36.0±1.4 mK, the 1984 R ≈ 48 Ω reconstruction) are plausible against my knowledge and its cited PDFs, but are **not independently re-verified digit-by-digit here**; per provenance discipline they are marked VERIFY-BEFORE-USE in any future empirical layer, exactly as GWTC demo values were.
4. **Scope guard:** its recommended hybrid continuous-plus-jump architecture (SDE in the well + escape point process + optional Lindblad layer) is sound and recorded, but belongs to the *future* B9-nonlinear/rare-event sprint; adopting it now would outrun our certified base.

**Best interpretation (decision):** treat the Nobel block as a **methodological anchor of the highest grade** — the program's discipline formula demonstrated on nature, converted into executable gates (B9) — while its quantitative formulas enter as estimator machinery under our certificate classes, and its historical sample values remain provenance-flagged. The other agent's mapping is adopted as the *computational skeleton*; our epistemics are the *load-bearing structure*; the T3 circularity finding is the proof that both were needed.

## 3. Forward hooks

B9-nonlinear (full washboard, escape hazard layer, W_min test) → sprint queue after S1–S5; quantum-noise FDT (coth form) as the M(ω) escalation; ħ-row edit memo candidate once B9's empirical layer runs on published junction data (R17–R19 tables, VERIFY-first).
