# Note: Closest Existing Research Programs — Review, Imports, and Cross-Agent Comparison

Filed 2026-07-14. Independent web-verified sweep + review of a second-agent
assessment (`docs/notes/assessment-2026-07.md` if archived). Companion to
`docs/SPECIFICATION.md` and `docs/roadmap-v2.md`.

## 1. The map (my research), with import actions

| Program | Core overlap with us | Verified anchors | Import action |
|---|---|---|---|
| **S-matrix / EFT positivity bootstrap** | Consistency conditions (unitarity, crossing, analyticity, symmetry) carve allowed theory space; FORCED ↔ extremal points; REJECTED ↔ exclusion certificates. **Key find: Wan–Zhou, "Matrix moment approach to positivity bounds and UV reconstruction from IR," JHEP 02 (2025) 168 (arXiv:2411.11964) — our B1 mathematics (moment matrices, positivity cones, reconstruction) operating inside EFT bounds.** Also: EFT-hedron (Arkani-Hamed–Huang–Huang, JHEP 05 (2021) 259); dual convex certificates (He–Kruczenski, JHEP 08 (2021) 125); SDPB (Simmons-Duffin); and bootstrap-meets-REAL-data: Guerrieri–Häring–Su, "From data to the analytic S-matrix: a bootstrap fit of the pion amplitude" (arXiv:2410.23333) — their B4/S3 analogue. | search-verified this session | **Import:** dual/exclusion certificates as first-class outputs (our Schur pivots already are primal certificates; add the dual functional that *excludes*); extremal-ray language for FORCED boundaries (B10's quantum-limited flatness is an extremal ray); ledger R25–R27. |
| **Operational / GPT reconstructions of QM** (Hardy arXiv:1104.2066 lineage; local tomography, composition, purification axioms) | Deriving quantum structure from operational restraints = our program restricted to the ħ row. | known literature, spot-consistent | **Import:** a neutral operational substrate for 𝖢 so Pos isn't secretly Hilbert-space-shaped (now in SPECIFICATION §1); GPT state spaces as a rival family in B12-RGRC. |
| **Categorical/compositional QM** (Abramsky–Coecke lineage) | Typed processes, monoidal composition, diagram equivalence = the Cmp column's proper mathematics. | known literature | **Import:** the 𝒞/⊗/† skeleton of SPECIFICATION §1; process-equivalence as the "same" relation's syntactic layer. |
| **Equation discovery: SINDy, symmetry-invariant discovery (arXiv:2505.18798), AI Poincaré 2.0 (arXiv:2203.12610)** | Automated candidate generation, sparsity, train/test discipline; conserved-quantity discovery with independence tests. | cited in R12 lineage + assessment | **Import:** the generator engine (roadmap M2) — typed grammar + dimensional analysis + MDL, feeding OUR certified verifiers (their gap: no certificates; our gap: no generator). |
| **Causal discovery** (equations+causality reviews, arXiv:2305.13341 lineage) | Observational equivalence classes; interventions required for unique recovery — the "genuinely shared" problem is a causal-inference problem. | known literature | **Import:** NONIDENTIFIABLE(cause) vocabulary (done, SPEC §4); intervention metadata in B12-RGRC; the ?₈ typing discipline. |
| **System ID / Koopman / GENERIC identification** | B8/B9 territory; coordinate-invariant operator representations. | in-repo (R15, B8, B9) | Already core; unify under 𝖱 (coarse-graining engine, roadmap M5). |
| **Moment problems / SOS / NPA hierarchies** | B1/B2/B6/S4 mathematics; flat extension = our rank certificates. | in-repo (R03 lineage) + Wan–Zhou | **Elevate from "one benchmark" to the central verifier layer** (assessment agrees; Wan–Zhou proves the physics community independently converged). |

**Meta-finding:** the program's mathematical core (positivity cones +
moment/flat-extension certificates + composition restraints) now has
*independent convergent instances in frontier physics* (EFT-hedron,
Wan–Zhou, dual bootstrap certificates). Our differentiators, confirmed
against the field: (a) cross-domain scope with one certificate discipline;
(b) exact-rational certificates rather than floating SDP output; (c) the
measurement-interface layer with calibration-route provenance; (d)
REAL-data verdicts under the same gates (B4, S3). Our deficits, confirmed:
no generator, no rival-grammar comparison, no preregistered prospective
prediction, prose-level 𝕽 (now fixed by SPECIFICATION.md).

## 2. Cross-agent comparison (second-agent assessment)

**Verdict: their strongest strategic document; adopt the skeleton, with
corrections.** It is right that the repo has "many compelling local
demonstrations and no decisive global identification test," and right
about the five missing machines (formal 𝕽, equivalence/identifiability,
prospective prediction, rival grammars, measurement layer).

**Adopted (implemented this sprint):** SPECIFICATION.md (their Priority 1);
evidence levels E0–E4 (§8 of theirs → SPEC §3); extended outcome
vocabulary incl. NONIDENTIFIABLE/OBSERVATIONALLY_EQUIVALENT/
APPARATUS_LIMITED/REPRESENTATION_DEPENDENT (their §12 → SPEC §4);
observational-equivalence definition (their §4 → SPEC §5); claims table
(their Priority 0 → SPEC §6); layered architecture L0–L4 and the
directories (`ontology/`, `baselines/`, `blind_tests/`,
`preregistrations/`, `provenance/`) → roadmap M-items; their §17 BEC
protocol (known-hidden-variable recovery BEFORE any residual search) →
EXP-F, endorsed as written.

**Corrected:**
1. **Namespace collision:** their proposed "B10 Rival-Grammar Recovery
   Challenge" collides with our B10 (CV channels, now landed 6/6). Their
   benchmark is renamed **B12-RGRC** and adopted as specified (8 generator
   families; success = separating genuine shared latents from shared
   mathematics/apparatus/units/calibration).
2. **Under-credited existing machinery:** S3 already performs model
   comparison with a rejected alternative (no-running, 13σ) and a
   d-penalized score on REAL data — single-domain, but the template
   exists. B9-T3 already implements a measurement-interface theorem
   (calibration-route circularity). The assessment's "missing" list is a
   scaling-up claim, not a from-zero claim; roadmap phrases it that way.
3. **?₅ critique partially misses our records:** edit-002's H is filed for
   the QFT-theorem status of factorization, not as synthesis evidence —
   the no-circularity rule already forbids the reading they warn against.
   Their three-way distinction (theorem / atlas-prediction / synthesis
   support) is nonetheless adopted verbatim into the claims table.
4. **?₇ critique is pre-empted by data:** their demand to discriminate
   exact rank / effective rank / operational capacity / algebraic entropy
   is exactly what S4 delivered (kinematic vs information Gram;
   capacity=entropy at S2-b). The rank-type pentad becomes ?₇'s required
   typing, with two of five types already measured.
5. **Their per-conjecture countermodel demands** (?₁ Galilean/Lifshitz/
   Carrollian enumeration; ?₆ prior-free forcing; ?₈ search-scope theorem)
   are accepted and filed as falsifier-strengthening items on the
   conjecture ledger — they make our falsifiers sharper, which is the
   program working as designed.
