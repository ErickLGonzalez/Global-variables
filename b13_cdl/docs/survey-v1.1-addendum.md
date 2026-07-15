# Conditional-Dependency Survey — v1.1 Addendum

**Status:** Extends v1.0 ("A Restraint-Matrix Survey of Conditional Results") with four
entries flagged in v1.0 Caveats as omissions: muon g−2 / HVP, the H₀ tension,
Langlands-conditional results, and UGC hardness-of-approximation corollaries.

**Relabeling note (DRAFT, needs Erick sign-off):** v1.0 used B1–B8 for the mathematics
block, colliding with the repository's benchmark IDs (B1–B12). v1.1 proposes relabeling
mathematics entries **M1–M10** (M1=RH/GRH … M8=misc families, M9=Langlands, M10=UGC).
Physics entries remain A1–A15. Filed as a DRAFT edit per erratum culture; do not apply
to claims-table.md until confirmed.

---

## A14. Muon g−2 / hadronic vacuum polarization — blocks: α, α_s (hadronic); predicates: Sym, RG, Cmp

**(1) Statement.** The anomalous magnetic moment of the muon a_μ = (g−2)/2 is both the
most precisely measured and (in principle) most precisely predicted quantity sensitive
to all SM sectors. Whether experiment and the SM agree is currently **conditioned on the
method used to evaluate the leading-order hadronic vacuum polarization (HVP)**.

**(2) Fundamental unknown.** Not a Lagrangian parameter but an *evaluation-path
ambiguity*: the true value of a_μ^HVP,LO. Data-driven (e⁺e⁻ → hadrons dispersive) and
lattice-QCD determinations disagree with each other beyond stated errors; the CMD-3
e⁺e⁻→π⁺π⁻ measurement (2023) conflicts with the earlier e⁺e⁻ catalogue, and no
data-driven average is currently deemed reliable by the Theory Initiative.

**(3) Dependency mechanism.** a_μ^SM = QED + EW + HVP + HLbL. QED/EW are uncontested;
HLbL = 115.5(9.9)×10⁻¹¹ is subdominant. HVP,LO ≈ 7045(61)×10⁻¹¹ dominates the theory
error. Swapping WP20's data-driven HVP for WP25's lattice-only HVP moves the SM
prediction by ~+2.2×10⁻⁹ — larger than the experimental error by an order of magnitude —
flipping the experiment-theory comparison from ~5σ tension to ~0.6σ agreement.

**(4) Key numbers & references.**
- Experiment (final, Fermilab E989 + BNL world average, 2025):
  a_μ^Exp = 116 592 071.5(14.5)×10⁻¹¹ (124 ppb). Muon g−2 Collab., final report
  (arXiv:2506.03069 / final-report arXiv:2606.17323).
- Theory WP25 (lattice HVP): a_μ^SM = 116 592 033(62)×10⁻¹¹ (530 ppb).
  Aliberti et al. (Muon g−2 Theory Initiative), White Paper 2025.
- Theory WP20 (data-driven HVP): a_μ^SM = 116 591 810(43)×10⁻¹¹.
  Aoyama et al., Phys. Rept. 887 (2020) 1.
- BMW lattice HVP: Borsanyi et al., Nature 593 (2021) 51. CMD-3: Ignatov et al. (2023).

**(5) Status of unknown.** Experiment is done (E989 complete). The unknown — which HVP
is right — is live: WP25 declined to average e⁺e⁻ data due to internal scatter at the ρ
resonance. Resolution expected from MUonE (spacelike HVP), new e⁺e⁻ data (BaBar/Belle II,
BESIII), and next-gen lattice.

**Restraint-matrix mapping.** Rows: α (QED series), α_s (hadronic blocks). Columns:
Sym (magnetic-moment operator structure), RG (running couplings into HVP), Cmp
(additive compositionality of sector contributions).

**Compute note.** Maximal. The tension calculator is pure arithmetic on published
central values/errors; the *verdict* is method-conditional. This is a structural twin of
**S3-EM**: an honest pipeline must emit NONIDENTIFIABLE(HVP-method) rather than force a
single experiment-vs-SM sigma. Implemented in `src/cdl/muon_g2.py`.

**Bidirectional?** Yes — MUonE or a settled e⁺e⁻ catalogue selects the HVP branch, which
retro-decides whether new physics is required. Registered falsifier: any future
data-driven average agreeing with pre-CMD-3 values at <2σ while lattice holds ⇒ tension
returns at ≳4σ.

---

## A15. The H₀ (Hubble) tension — blocks: Λ, initial parameters, G; predicates: Cau, RG, Pos

**(1) Statement.** Early-universe (CMB+BAO under ΛCDM) and late-universe
(distance-ladder) determinations of the Hubble constant disagree: H₀ = 67.4 ± 0.5
(Planck 2018) / ≈68 (DESI BAO+CMB, 2024–25) vs 73.0–73.2 ± ~0.9 km s⁻¹ Mpc⁻¹
(SH0ES, JWST-reinforced) — a ~5σ discrepancy that has *grown* with precision.

**(2) Fundamental unknown.** Whether ΛCDM's extrapolation from z≈1100 to z=0 is missing
physics (early dark energy, extra relativistic species, evolving w — couples to A3), or
whether an unrecognized systematic afflicts one ladder. Formally: the true value of H₀
and the model that connects the two anchors.

**(3) Dependency mechanism.** The CMB does not measure H₀ directly; it measures the
sound horizon r_s and angular scales, and H₀ is *derived conditionally on ΛCDM*. The
ladder measures H₀ quasi-directly but conditionally on Cepheid/TRGB calibration. The
tension is therefore a conditional-on-model clash of two forward maps — restraint-matrix
gold.

**(4) Key numbers & references.**
- Planck 2018: 67.4 ± 0.5 (A&A 641, A6, 2020).
- DESI DR1/DR2 BAO + CMB: ≈ 68 (67.97 ± 0.38-class constraints; DESI 2024–2025).
- SH0ES: 73.04 ± 1.04 (Riess et al., ApJL 934, L7, 2022); JWST-era distance ladder
  ≈ 73.17 ± 0.86 (2025 compilations); JWST Cepheid crowding checks *confirmed* HST
  photometry (Riess et al. 2023–2025).
- Freedman et al. TRGB/JAGB (CCHP, JWST): ≈ 69–70, intermediate — method-dependence
  inside the late-universe branch itself.
- Sound-horizon-free ensemble analyses report ~3.9σ ladder-vs-SHF discrepancy
  (arXiv:2601.00650, 2026).

**(5) Status.** Open and hardening; leading "new physics" candidates (axion-EDE) reduce
the tension to ~1σ at the cost of extra parameters (e.g., arXiv:2606.19090, 2026).

**Restraint-matrix mapping.** Rows: Λ (expansion history), initial parameters (r_s,
early-universe content), G (ladder anchors assume standard local gravity). Columns:
Cau (light-cone/expansion causal structure), RG (the tension is literally a
scale-consistency failure between z≈1100 and z=0 — the sharpest RG-column entry in the
physics catalogue), Pos (energy conditions of proposed resolutions).

**Compute note.** High. Pairwise tension matrix over published (value, σ) pairs;
verdict NONIDENTIFIABLE(model-vs-systematic) with the DESI w₀wₐ coupling (A3) noted.
Implemented in `src/cdl/h0_tension.py`.

**Bidirectional?** Yes — gravitational-wave standard sirens and lensing time delays are
ladder-independent falsifiers; a siren catalogue at ±1 km s⁻¹ Mpc⁻¹ picks a side.

---

## M9. Langlands-program-conditional results — block: Langlands/functoriality; predicates: Thm, Sym, Cmp

**(1) Statement.** Langlands functoriality — the conjectured transfer of automorphic
representations along L-group homomorphisms — conditions a large family of analytic and
arithmetic theorems.

**Conditional results (selection).**
- **Ramanujan–Petersson conjecture** for GL(2) (and generalized to GL(n)): follows from
  functoriality (automorphy of all symmetric powers sym^k). Best unconditional bound
  toward it: Kim–Sarnak 7/64 (2003).
- **Selberg's eigenvalue conjecture** (λ₁ ≥ 1/4 for congruence surfaces): the archimedean
  twin of Ramanujan; same functoriality conditioning, same 7/64 partial result.
- **Artin's conjecture** (holomorphy of Artin L-functions): follows from strong Artin
  conjecture / Langlands reciprocity; known for nilpotent (Arthur–Clozel) and many
  solvable cases (Langlands–Tunnell — the very input to Wiles's FLT proof).
- **Sato–Tate** (equidistribution of a_p angles): *was* Langlands-conditional; proven via
  potential automorphy of sym^k (Barnet-Lamb–Geraghty–Harris–Taylor 2011) — a showcase
  of a conditional result being unconditionally captured by proving *enough*
  functoriality. Promotion-path exemplar for the ledger.
- Beyond endoscopy, symmetric-power L-function analytic continuations, and many
  effective equidistribution statements remain functoriality-conditional.

**(2) Fundamental unknown.** Functoriality itself (open for general L-homomorphisms);
Langlands reciprocity (Galois ↔ automorphic). The **geometric** Langlands conjecture was
proven in 2024 (Gaitsgory–Raskin et al., ~5 papers, ~900 pp) — a different (function
field / categorical) column of the same matrix, demonstrating block-wise resolvability.

**(3) Dependency mechanism.** Automorphy of sym^k π controls the analytic behavior of
L(s, sym^k π); bounds on Satake/Hecke parameters (Ramanujan) follow from holomorphy and
non-vanishing of these L-functions. The unknown enters as *existence of a functorial
lift*, exactly parallel to how a physics unknown enters as *existence of a UV fixed
point* (A10).

**(4) References.** Langlands (1967, 1970); Kim (JAMS 2003, sym⁴); Kim–Sarnak appendix;
Clozel–Harris–Taylor; BLGHT (2011); Gaitsgory–Raskin (2024); Arthur, *The Endoscopic
Classification* (2013).

**(5) Status.** Arithmetic functoriality open; geometric case proven (2024); Sato–Tate
promoted to theorem; Ramanujan/Selberg open with 7/64 partial.

**Restraint-matrix mapping.** Thm (conditional theorem family), Sym (the entire block is
symmetry-transfer: L-group homomorphisms are the "Sym" morphisms of the number-theory
world), Cmp (functoriality is compositional: lifts compose along group homomorphisms —
the closest mathematical analogue of the ⊗-compositionality axiom of 𝕽).

**Compute note.** Medium. Satake-parameter bounds are numerically checkable per-form
(LMFDB pipelines); "distance below 1/4" for eigenvalues is a computable invariant. A
benchmark could verify Kim–Sarnak bounds against LMFDB Maass-form data.

**Bidirectional?** Yes — a single Maass form with λ₁ < 1/4 or a Hecke eigenvalue
violating Ramanujan bounds refutes functoriality in that range.

---

## M10. Unique Games Conjecture — hardness-of-approximation corollaries — block: complexity (UGC sub-block); predicates: Thm, Cmp, Pos

**(1) Statement.** UGC (Khot 2002): for every ε,δ > 0 it is NP-hard to distinguish
Unique-Games instances with value ≥ 1−ε from value ≤ δ (large enough alphabet).
Conditional corollaries fix the *exact* approximation threshold of many problems:

- **MAX-CUT:** the Goemans–Williamson SDP ratio α_GW ≈ 0.87856 is optimal — no
  poly-time algorithm does better unless P=NP (Khot–Kindler–Mossel–O'Donnell 2007 +
  Mossel–O'Donnell–Oleszkiewicz "Majority is Stablest" 2010).
- **Vertex Cover:** 2−ε inapproximable (Khot–Regev 2008).
- **Every CSP:** the basic SDP relaxation achieves the optimal approximation ratio;
  integrality gap = hardness threshold (Raghavendra 2008) — a *universal* conditional
  theorem.
- Sparsest cut, Max-Acyclic-Subgraph, kernel clustering, and scheduling thresholds.

**(2) Fundamental unknown.** Truth of UGC. Notable partial: the **2-to-2 Games Theorem**
(Khot–Minzer–Safra 2018, with Dinur–Khot–Kindler–Minzer–Safra) is *proven*, delivering
unconditionally: NP-hardness of √2−ε vertex-cover approximation and "half" of UGC
(imperfect-completeness regime) — evidence that shifted expert opinion toward UGC-true.

**(3) Dependency mechanism.** UGC-hardness reductions convert a Unique-Games instance
into problem-specific gap instances whose soundness analysis rests on noise-stability
theorems over Gaussian space. The unknown enters as the *seed hardness*; everything
downstream is unconditional reduction machinery.

**(4) References.** Khot (STOC 2002); KKMO (SICOMP 2007); MOO (Ann. Math. 2010);
Khot–Regev (JCSS 2008); Raghavendra (STOC 2008); KMS (FOCS 2018).

**(5) Status.** Open; 2-to-2 proven (2018); expert credence materially higher post-2018.

**Restraint-matrix mapping.** Thm, Cmp (reductions compose; Raghavendra's theorem is a
compositionality statement: one SDP schema governs all CSPs), and — notably — **Pos**:
the entire conditional structure runs through *positive-semidefinite relaxations*. The
optimal algorithms are PSD-cone projections; UGC says the PSD cone is the exact boundary
of tractability. This is the single strongest mathematical entry for the Pos column and
connects directly to the project's exact-Fraction Schur-pivot PSD verifier: a
GW-SDP certificate is checkable by the existing B1-standard machinery.

**Compute note.** Maximal. GW rounding, α_GW to arbitrary precision
(α_GW = min_{θ} (2/π)·θ/(1−cos θ)), integrality-gap instances, and PSD certificates are
all implementable today with repo-standard exact verification.

**Bidirectional?** Yes — a poly-time algorithm beating α_GW on MAX-CUT refutes UGC
outright (modulo P≠NP); conversely a proof of UGC freezes an entire column of
approximation thresholds to their SDP values.

---

## Updated summary-table rows (append to v1.0 table)

| Entry | Block | Sym | Pos | Uni | Cau | Cmp | RG | Top | Thm | Compute | Bidirectional |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A14 Muon g−2 / HVP | α, α_s | ✓ | | | | ✓ | ✓ | | | Maximal (arith.) | Yes |
| A15 H₀ tension | Λ, init, G | | ✓ | | ✓ | | ✓ | | | High (σ-matrix) | Yes |
| M9 Langlands functoriality | Langlands | ✓ | | | | ✓ | | | ✓ | Medium (LMFDB) | Yes |
| M10 UGC hardness | complexity/UGC | | ✓ | | | ✓ | | | ✓ | Maximal (SDP) | Yes |

**Coverage impact (Stage 5 check).** A15 adds the strongest RG-column physics entry
(explicit z≈1100 → z=0 scale-consistency failure). M10 adds the first mathematical Pos
entry with a direct hook into the repo's existing PSD verifier. M9 adds Sym+Cmp to the
mathematics side, previously Thm/Cmp-dominated. A14 adds a second live
method-nonidentifiability exemplar (twin of S3-EM). All four pass the v1.0 Rec-5
admission rule: each adds a distinct predicate touch or a new compute hook.

## Contested/soft flags (Stage 4)
- A14: the *dissolution* of the tension is method-conditional; CMD-3 vs prior e⁺e⁻ data
  unresolved. Tag: `contested: method-dependent`.
- A15: magnitude is analysis-dependent (SH0ES vs CCHP within the late branch). Tag:
  `contested: intra-branch spread`.
- M9: geometric case proven; arithmetic case open — do not conflate. Tag: `partial`.
- M10: 2-to-2 proven; UGC itself open. Tag: `partial, credence-shifted`.
