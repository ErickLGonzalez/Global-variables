# Research Paper Ledger

Papers researched for the program, with role classification. Roles:
**ANCHOR** (external evidence cited in an edit/certificate) · **METHOD** (shapes the pipeline/discipline) · **TARGET** (source of data or falsifiers) · **CANDIDATE** (queued, not yet assessed).

| Ref | Paper | Role | Where it acts |
|---|---|---|---|
| R01 | Isi, Farr, Giesler, Scheel, Teukolsky, PRL 127, 011103 (2021) — GW150914 area-law test | ANCHOR | ?₃ / edit-001 / B4 |
| R02 | LVK, "GW250114: Testing Hawking's area law and the Kerr nature of black holes," PRL 135, 111403 (2025) | ANCHOR | ?₃ / edit-001 / B4 REAL |
| R03 | arXiv:2509.03480 — GW230814/GW231226 area law ≳5σ (GWTC-4) | ANCHOR | ?₃ / edit-001 |
| R04 | Curto & Fialkow — flat extensions of positive moment matrices | ANCHOR | B1 forcing mechanism |
| R05 | Choi (1975) — completely positive maps; Stinespring dilation | ANCHOR | B2 gate |
| R06 | Weinberg, *QTF* Vol. 1 — cluster decomposition | ANCHOR | ?₅ / edit-002 / B5 |
| R07 | Haag, *Local Quantum Physics* | ANCHOR | ?₅ / edit-002 |
| R08 | Wall (2011) — GSL proof; QNEC for free fields | ANCHOR | ?₂ / edit-003 / B6 |
| R09 | Balakrishnan, Faulkner, Khandker, Wang (2017) — QNEC from modular theory | ANCHOR | ?₂ / edit-003 / B6 |
| R10 | Jacobson (1995) — Einstein equations as equation of state | ANCHOR | ?₁ |
| R11 | Adams et al. — positivity bounds from causality/analyticity/unitarity | METHOD | feasible set 𝔉; future EFT gate |
| R12 | Schmidt & Lipson; AI Feynman; SINDy | METHOD | decoding-chain step 5 (candidate generators only) |
| R13 | Chamseddine & Connes — spectral action | METHOD (hypothesis) | bridge formula; flagged conjectural |
| R14 | **Maudlin, "Actual Physics, Observation, and Quantum Theory," arXiv:2512.22618 (physics.hist-ph, Dec 2025)** | **METHOD** | **𝓜-layer (decoding-chain step 1); certificate format; arrival-time track** |
| R15 | **Chen, Soh, Ooi, Vissol-Gaudin, Yu, Novoselov, Hippalgaonkar, Li — "Constructing custom thermodynamics using deep learning," Nat. Comput. Sci. 4, 66–85 (2024); arXiv:2308.04119; code: Zenodo 10.5281/zenodo.10212239** | **METHOD** | **decoding-chain step 5 (constraint-native generators); closure-as-d_identifiable; B7 + B8 done; Atlas Engine seeded** |

## R14 annotation (added 2026-07-11)

Philosophy-of-physics essay; produces no theorems or certificates and changes no matrix cell. Adopted contributions (see `docs/notes/measurement-interface-maudlin.md`):
1. **M-layer stipulation ledger** — every certificate must list its un-derived measurement-interface stipulations explicitly (Einstein's clocks-and-rods "incurred obligation," systematized).
2. **Scope clause for process-type certificates (B2 class)** — completions certify consistency *given* a device↔POVM association; the association itself is an M-layer stipulation, not a certified object.
3. **Arrival-time track (candidate held-out domain)** — standard QM supplies no unique arrival-time observable (Pauli's theorem: spectral positivity of H forbids a conjugate self-adjoint T — an atlas-native restraint fact); rival completions differ measurably. Rare domain where candidate rule-objects 𝕽 genuinely disagree → high U_prediction value in the Score function.

## R15 annotation (added 2026-07-11)

Open-access research article (pointer received via its paywalled Research Briefing, doi:10.1038/s43588-023-00590-4). S-OnsagerNet: learns closed macroscopic stochastic dynamics Ż = −M∇V(Z) (+ stochastic extension) from microscopic trajectories, with M ⪰ 0 (dissipation) and generalized-potential structure ENFORCED BY ARCHITECTURE, while simultaneously learning the minimal closure coordinates (polymer stretching: ~900 DOF → 3 coordinates; DNA-experiment validation). Adopted contributions (see `docs/notes/onsager-sonsagernet-chen2024.md`):
1. **Constraint-native candidate generation** — restraint bundles embedded in the generator's hypothesis space (structured) vs applied as post-hoc gates (unstructured, SINDy/R12). Firewall: by-construction constraints characterize the hypothesis class, never the learned object; certification classes and held-out gates unchanged.
2. **Closure coordinates = dynamical d_identifiable** — algorithmic pattern for extending rank discovery (B3/B5) from static relations to evolution laws.
3. **Benchmark B7 implemented: Onsager transport-matrix completion** — `b7_onsager/` + certificate; PSD alone → PERMITTED; +reciprocity → FORCED.

**R15 addendum (2026-07-12):** cross-agent review filed (`docs/notes/r15-addendum-cross-agent-review.md`). Adopted: canonicalization rule, distill-before-score rule for L(𝕽), **B8 implemented** (blind grammar identification), certified closure dimension research item. Rejected: single-number "encoding N" endpoint. Erratum: full S-OnsagerNet law is Ż = −[M(Z)+W(Z)]∇V(Z)+σ(Z)Ḃ with W antisymmetric.
