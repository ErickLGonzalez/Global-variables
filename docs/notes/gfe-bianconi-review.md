# Note: Gravity-from-Entropy (Bianconi) — Review, Truncation Audit, Matrix Mapping, Mathematics Imported

Filed 2026-07-16. Papers read directly: **R34** = Bianconi, "Gravity from entropy," arXiv:2408.14391 (v7); **R35** = Bianconi, "The Thermodynamics of the Gravity from Entropy Theory," arXiv:2510.22545 (v4). Companion code: `probes/truncation_audit.py`, `tests/test_truncation.py` (5/5), M1 `metric_pair` kind.

## 1. What the papers claim
R34: gravity from an entropic action = quantum relative entropy (GQRE, Araki-adjacent) between the spacetime metric and the metric induced by matter fields; metric treated as a quantum-operator/density-matrix-like object; matter in Dirac–Kähler-like topological form (0⊕1⊕2-forms, bosonic sector; fermions/non-Abelian deferred); auxiliary **G-field** (Lagrange multipliers, "extending the f(R) Legendre move") reduces the action to a dressed Einstein–Hilbert form with an **emergent small positive Λ depending only on the G-field**; equations second order; Einstein + Λ=0 recovered at low coupling. R35: FRW thermodynamics — k-temperatures/k-pressures with a GfE first law; Λ_G as dynamical effective dark energy; total entropy non-decreasing while GQRE/volume does not increase; Friedmann recovered in the low-energy small-curvature limit with a stated validity criterion; companion result: Schwarzschild area law from GfE first principles.

## 2. Verdict on the truncation critique (Erick, 2026-07-16)
Split verdict, now with code behind it:
- **Field-content truncation (0⊕1⊕2-forms): the strong point.** In d=4 the full Dirac–Kähler complex is 0⊕1⊕2⊕3⊕4; the papers *choose* the sub-complex and defer the rest. No consistency proof (truncated solutions lifting to full-theory solutions) is offered. In program vocabulary the emergent-Λ result carries an undeclared `m_layer_stipulation: field-content truncation`, status **TRUNCATION_UNAUDITED** — exactly the third verdict of the new gate (T3).
- **Auxiliary G-field: the softer point.** Lagrange-multiplier/Legendre reformulations are usually exact (f(R)↔scalar–tensor is rigorous where f″≠0). The legitimate demand is narrower: state the invertibility/branch conditions under which elimination is global. Suspicion warranted at that level only.
- **The probe (exact):** on a Gaussian ladder, integrating out IS a Schur complement; the truncated "emergent constant" differs from the full one by an exact rational shift (−6/3311 in the demo) unless the boundary coupling vanishes — in which case robustness is *certified*, not assumed. The shift scales quadratically in the neglected coupling (4.002× under halving): "weakly coupled dropped sectors" is a quantitative license with a computable constant. **Scope: the probe certifies the logic of the audit GfE owes, not a verdict on GfE's nonlinear setting.**

## 3. Matrix mapping (v0.6 rows × columns; all rival/methodology tier — no cell changes)
| Cell | GfE relevance | Action |
|---|---|---|
| **Λ × Pos** | Λ_G emergent, positive, dynamical — a rival TYPING of Λ vs ?₇ (rank) and ?₈ (global state datum); closest to ?₈ (Λ as derived data, not input) | add GfE to the ?₇/?₈ rival list in the conjecture ledger |
| **G × RG (?₄)** | GfE = a rival grammar to asymptotic-safety-biased ?₄ (exactly the model-comparison the related-programs review demanded) | GfE joins the ?₄ rival families |
| **G × Thm (?₃-adjacent)** | Schwarzschild area law derived from GfE first principles — theory-side corroboration that area laws follow from entropy-first axioms | ledger note on the ?₃ row |
| **k_B × Thm** | k-temperatures + GfE first law: R-KMS-adjacent structure; FRW-toy testable | future S-sprint candidate |
| **Cau** | equations remain second order — a well-posedness restraint GfE satisfies by construction | recorded |
| **B12-c** | "relative-entropy grammar" = a live *published* rival family for the RGRC quantum/gravity layer | B12-c generator family spec |

## 4. Mathematics imported (done this sprint)
1. **Metric-pair invariants → M1** (`canonicalize(kind="metric_pair")`): GfE's Lorentz/GL-invariant eigenvalue definition for rank-2 tensor pairs — the spectrum of g⁻¹G, invariant under simultaneous congruence — is precisely an M1 canonical feature; tested (3 random congruences → identical hash; discrimination preserved).
2. **Burg/Stein divergence** D(g‖G) = Σ(λ − ln λ − 1) ≥ 0 — the eigenvalue-log core of the GQRE, now computable in canon; = 0 iff G = g, congruence-invariant. Bridge to S2's Gaussian relative entropy machinery for future GfE-toy work.
3. **Truncation-audit gate** (`probes/`): general-purpose; applies to ANY emergent-constant claim in the repo going forward (SPEC §§2,4 wired via T3).
Deferred: Lorentzian-signature pairs (positive-definite demo only); the full GQRE functional; a GfE-FRW toy for the R35 first law.

## 5. Bottom line
Not previously in the repo; now ledgered (R34–R35) as a serious, testable rival grammar with genuinely importable mathematics — and the critique that motivated this sprint is no longer an intuition: it is a gate with three exact verdicts, one of which currently names GfE's own status.
