# Note: BEC / Frontier-Interferometry Experimental Program for the Restraint Matrix

Filed 2026-07-14. Papers: **R23** = Howl & Fuentes, "Quantum Frequency Interferometry" (arXiv:2103.02618); **R24** = Zhang, del Aguila, Mazzoni, Poli, Tino, "A trapped atom interferometer with ultracold Sr atoms" (arXiv:1609.06092). Both read directly this session. Companion: cross-agent review of a second AI analysis ([`bec-multimode-decompilation-draft.md`](bec-multimode-decompilation-draft.md), §4).

## 1. What the papers establish (independent reading)

**R23 (theory/architecture).** Frequency interferometry uses field modes sharp in frequency, delocalized in position, trapped in one volume and *in contact at all times*. Consequence stated by the authors: one can estimate not only U(1) phases but **parameters of global multi-mode channels** — mode mixing U_M(ζ), two-mode squeezing U_S(ξ), i.e. the generators of two-mode Gaussian/Bogoliubov transformations — with quantum-Fisher-information precision bounds, in a three-mode (pumped-up SU(1,1)-descended) scheme. Implementations: BEC phonons, superconducting circuits, cavity-QED. Applications: phononic GW detection (orders-of-magnitude sensitivity gains even with modest squeezing and short phonon lifetimes), magnetometry, gravimetry, dark-matter searches.

**R24 (engineering blueprint).** Trapped Ramsey–Bordé Bragg interferometer with ⁸⁸Sr held against gravity in a vertical lattice via Bloch oscillations: interference out to **1 s in-lattice evolution**; decoherence budget characterized (lattice lifetime, beam inhomogeneity); Sr chosen for zero nuclear spin (first-order Zeeman immunity) and low collisional cross-section (Bloch coherence >100 s demonstrated elsewhere). Lesson class: long interrogation *without* free-fall towers; loss-vs-decoherence discrimination; T-scaling as a diagnostic.

## 2. Answer to the device question

**Yes — and more sharply than either paper states.** R23 supplies the *estimation theory* for global multi-mode channels; R24 supplies the *platform discipline* for long trapped interrogation. A trapped multi-mode condensate interferometer driven by calibrated external perturbations x_j(ω) is a **coupling-matrix machine**: it reconstructs, per drive frequency, the 2N×2N symplectic map S(ω_d) + noise block acting on mode quadratures — equivalently the susceptibility matrix M_ij(ω) = ∂O_i/∂x_j — not a single phase.

The decisive point for this repo: **every layer of that reconstruction already has a certification back-end here.**

| Reconstructed object | Repo back-end | Certificate |
|---|---|---|
| Gaussian-channel Choi matrix | **B2** (Choi PSD + TP, restraint stacking, hidden-entry completion) | EXACT class on discretized data |
| Susceptibility matrix M(ω) | **B7** (L ⪰ 0 second law + Onsager reciprocity → FORCED entries) + Kramers–Kronig (Cau) | Onsager completion |
| Drift/covariance at equilibria | **B9** (K = −J_b H_V⁻¹ → M/W split; **FDT audit**; calibration-route field) | Nobel-recipe gates |
| Quantum Fisher information matrix | Pos column at the metrology layer (QFIM ⪰ 0; multiparameter bounds = positivity restraints on joint estimability) | Gram-class |
| Blind channel classification | **B8** (grammar ID with AMBIGUOUS first-class) | invariant-signature |

The B9 mapping is exact down to the history: **trap-frequency spectroscopy is the resonant-activation analogue** (independent calibration channel; R17), Feshbach tuning is the **controlled-dissipation/coupling dial** (R20's shunted junction), and the Gibbs-circularity guard (B9-T3) applies verbatim — mode temperatures must come from independent thermometry, never from the same trajectories.

## 3. Proposed experiments (realistic today) and their matrix cells (v0.6)

**Tier labels adopted (from the cross-agent review, §4): BENCHMARK (synthetic) / ANALOGUE-REAL (real data testing structure, not the constant) / FUNDAMENTAL-REAL (constrains a fundamental row; only this tier can change a cell).**

- **EXP-A — Two-phonon Gaussian-channel tomography + B2 completion** (endorsed from cross-agent E1/B10). Reconstruct S(ω_d) under one calibrated perturbation at a time; hide entries; complete via Choi positivity + TP; hold out resonances for prediction. **Cells: ħ row Pos/Uni/Cmp (+Cau via Kramers–Kronig on M(ω)); tier ANALOGUE-REAL.** Feasible now: mode-resolved Bogoliubov readout is demonstrated technology.
- **EXP-B — FDT/B9 audit in a driven-dissipative condensate** *(our addition — absent from the cross-agent doc)*. Measure linewidths (→ dissipative M), noise spectra (→ σσᵀ), independent thermometry; gate σσᵀ = 2k_BT·M; structured residuals escalate to M(ω) per B9's sanctioned path. **Cells: k_B row Thm/Pos; effective-coefficient type; tier ANALOGUE-REAL** with the calibration-route field mandatory.
- **EXP-C — Information-Gram rank saturation across an analogue horizon** *(our addition, enabled by S4 today)*. In a sonic-horizon or engineered cosh-redshift condensate, measure the ε-rank of **G_info = D C(1−C) D** vs the kinematic Gram: S4 predicts kinematic rank ∝ ℓ (mode counting) while information rank is ℓ-independent and ∝ ln(1/ε) (entropy tracking) — a sharp, falsifiable laboratory signature of the ?₇ refinement discovered this sprint. **Cells: Λ Pos (?₇) + Initial/state Pos, tier ANALOGUE-REAL (methodology only — the entropy is the field's).**
- **EXP-D — α-consistency layer, "S3-EM"** *(our addition; zero new hardware)*. Published atom-interferometric α extractions (Cs recoil, Rb recoil) + electron g−2 currently exhibit a known **>5σ Rb–Cs tension** — a live PERMITTED-interval case in the atlas's most precise row. Run the S3 pipeline: channel consistency, no-common-value null, Score(d=1) vs per-channel. R24's platform class is exactly what feeds future h/m inputs. **Cells: α row Pos/Uni/RG memo; tier FUNDAMENTAL-REAL-adjacent (analysis of real fundamental data; any cell action only via edit record).**
- **EXP-E — Blind composition classifier** (endorsed from cross-agent E2/B11, with corrections §4). Product channel vs classically-correlated vs common drive vs coherent joint channel vs AMBIGUOUS — B8 in the laboratory. **Cells: ħ Cmp primary; ?₈ methodology secondary. NOT G/Λ cells (see §4 rejection).**

## 4. Cross-agent review (second AI analysis, [`bec-multimode-decompilation-draft.md`](bec-multimode-decompilation-draft.md))

**Overall: a strong document — the best of the cross-agent series.** Its promotion policy (BENCHMARK/ANALOGUE-REAL/FUNDAMENTAL-REAL, "only the third can change a cell") is adopted verbatim as program policy; its falsifiability pentad (repeatable + parameterized + cross-validated + control-resistant + predictive) and the Phase A/B/C demonstrator (Phase B = adversarial blind classification, literally B8-in-the-lab) are adopted; its experiment-record JSON schema is adopted **with two added mandatory fields**: `calibration_route` (B9-T3 lesson — absent from their schema) and `m_layer_stipulations` (certificate v0.3 requirement).

**Accepted:** E1 → B10 CV-channel completion (= our EXP-A); E2 → B11 composition classifier (= EXP-E, cells corrected); E3 resonance spectroscopy (folded into B10 as its held-out-prediction layer — the ω₁±ω₂ table mapping resonances to J/K matrix elements is genuinely useful); E4 Feshbach interaction-null scan (accepted, and sharpened: it is the **coupling-dial analogue of R20's shunted-junction test** — dissipation/coupling as a causal dial); E7 nonlinearity/cross-coupling tensor (accepted; folds into B9-nonlinear exactly as they themselves suggest); the ⁸⁸Sr engineering-lessons reading of R24 (matches mine).

**Accepted with restrictions:** E5 distributed-BEC latent-variable network — excellent safeguards list (no shared laser references/timing/grounds/code during blinds), but multi-lab and expensive: **Tier-3/long-horizon**, and its "global latent variable" language must stay under the ?₈ retyping discipline (a shared driver is a hypothesis to be *typed*, not a discovery to be named). E6 geometry/topology scan — good design (linked vs unlinked synthetic flux with matched local forces is elegant); **ANALOGUE, ?₆-methodology only**. B13 "experimental scale-flow semigroup" — kept, but as METHOD with an explicit non-promotion clause: BEC effective-coupling flow validates RG *machinery*, not ?₄/?₉ physics.

**Rejected / corrected:**
1. **B11's primary-cell claim "G Cmp, Λ Cmp":** a condensate composition classifier cannot list gravity or cosmological rows as *primary cells* at any tier — that is exactly the tier confusion their own promotion policy forbids. Corrected: primary = ħ Cmp; ?₈/?₃ appear only as methodology-relevance notes.
2. **B12 finite-rank reconstruction misses the decisive object:** without the **information-Gram vs kinematic-Gram distinction (S4, this sprint)**, their experiment measures accessible-mode count (∝ system size) and would wrongly "refute" rank–entropy. Reconsolidated into EXP-C with G_info = D C(1−C) D as the measured object and the ℓ-independence signature as the pass/fail criterion.
3. **No FDT / calibration-route discipline anywhere:** their Phase A injects heating and laser noise but never certifies fluctuation–dissipation consistency or records where H_V came from — the Voss–Webb lesson (B9-T2/T3) unapplied. Fixed by EXP-B and the two added schema fields.
4. Minor: the decoding-chain section renders 𝕽 as ℝ (notational only); "matrix item" is used for both restraint-matrix cells and susceptibility entries — we disambiguate: **restraint-matrix cells** change only by edit record; **susceptibility/coupling-matrix entries** are experimental data feeding certificates.

**Best interpretation (decision):** adopt their experimental skeleton (E1–E3, E7, policy, schema, phased demonstrator), correct the two tier violations, inject the three missing disciplines (FDT gate, calibration route, information-Gram refinement), and add the zero-hardware EXP-D that connects the program to a *live* fundamental-constant tension today.

## 5. Repository increments proposed

Queue: **B10** (CV Gaussian-channel completion — mostly assembled from B2 + new symplectic layer), **B11** (composition classifier — B8 extension), **EXP-D/S3-EM** (analysis sprint, real α data). Ledger: R23, R24 filed with contribution traces. Schema: `schemas/bec_experiment_record.schema.json` with the corrected fields, drawn when B10 lands.
