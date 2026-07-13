# S2 — GNS realization probe for ?₂ (free-fermion route)

**Date:** 2026-07-11  
**Certificate:** `certificates/s2_gns_certificate.json`  
**Code:** `s2_gns/`

## Claim under test

Not Cholesky: exhibit **state-independent** operators \(A_0,A_1\) in a real QFT such that

\[
\omega(A_i^\dagger A_j)=M_{ij}=\begin{pmatrix}c/6&S'\\S'&2\pi T-S''\end{pmatrix}
\]

for vacuum, thermal, and coherent-class states. Success ⇒ GNS item on the ?₂→H checklist (edit-003).

## What passed (exact)

**Continuum vacuum:** \(M=(c/6)\,uu^\top\) with \(u=(1,1/\mathrm{d}u)\). Rank-1 saturation; on the vacuum GNS ray \(A_1=A_0/\mathrm{d}u\). Coherent reading: \(A_1\) gains an orthogonal piece \(\propto f'\) while \(A_0\) stays put (B6 pivot split). This is a physical Gram realization for the vacuum orbit — not a generic PSD completion.

## Lattice probe (quarantined)

Free Dirac chain (open, half-filled). Candidate pair (region-only kernels):

- \(A_0=\sum_i \beta_i T_i\), \(\beta(x)=x(1-x)\) (geometric modular weight)
- \(A_1=T_{\mathrm{cut}}\) (last bond)

Stipulations: \(\mathrm{Sp_{null}}\simeq\mathrm{Sp_{et}}/2\); vacuum \(Q_{22}:=\mathrm{Sp_{null}}/\ell\) (no noisy \(S''\)); Peierls current as coherent-stress proxy.

### Result

| Check | Outcome |
|---|---|
| \(c_{\mathrm{eff}}\) from \(S\simeq(c/3)\ln\ell\) | ~0.90 at \(L=96\) (band OK) |
| Vacuum proxy \(M\) PSD + near-sat | Pass (by construction of \(Q_{22}\)) |
| Scale-invariant \(G_{01}/G_{00}\) vs \(1/\ell\) | **Fail** — measured \(r_{01}\sim O(\ell)\), wrong continuum scaling |
| Thermal / current holdouts | Degrade further; verdict `PARTIAL_CONTINUUM_EXACT_LATTICE_OPERATOR_MISMATCH` |

**Interpretation:** the geometric-(K, cut-T) pair is the right *candidate class* (Casini–Huerta / B-W shape) but at \(L\le 120\) is dominated by short-range bond noise, not the IR stress correlator that would give \(r_{01}\to 1/\ell\). Random weights can beat modular β on the ratio test at this size — a red flag, not a success.

## Verdict for edit-007

**PARTIAL GNS.** Continuum vacuum ray certified. Lattice operator-pair tracking **not** certified. Full ?₂→H remains blocked on: (i) continuum-limit / larger-\(L\) or null-cut formulation of the same kernels; (ii) or an explicit Wall free-field integrand whose two smearings reproduce \(M\) off vacuum; (iii) interacting checks stay with BFKW as external existence proof, not an in-repo operator certificate.

Cholesky remains rejected as evidence.

---

## Addendum: State-layer verification + obstruction diagnosis (2026-07-13)

A complementary **state layer** (`s2_gns/gaussian.py`, `s2_gns/qnec_lattice.py`, `tests/test_s2_state_layer.py`, 5/5) now verifies the OTHER half of the GNS claim — that the state/modular technology is sound:

1. Central charge extracted blind from S(l): c_fit = 1.0001 (Dirac c = 1).
2. **Vacuum saturation from microscopic data:** |Q|/|S''| = 0.001 at l = 30, shrinking with l — the B6 rank-1 flat boundary emerges from correlation data, not postulates.
3. **Thermal identity from data:** Q(l) = c·π²/(3β²) = 2π × energy density, median deviation 1.9% across the window — B6's coth identity with T ≠ 0, verified microscopically.
4. Entanglement first law (symmetric form): dS/dε = Tr[K dC] to 0.00%, error scaling exactly 4.00× under ε-halving. (Instructive finding en route: the ground state sits on the **boundary** of the Gaussian-state set, and the positivity gate correctly rejected backward perturbations — interior base point required.)
5. Positivity gate armed: corrupted C rejected as NOT_A_GAUSSIAN_STATE.

**Diagnostic conclusion (the point of running both layers):** the state side passes everything; the probe's mismatch is therefore **localized to the operator ansatz**. And the literature says why: the probe's A₀ used only the *local* geometric kernel β(x) = x(ℓ−x)/ℓ, but the exact modular Hamiltonian of a single interval for free fermions is NOT purely local — Casini–Huerta's continuum solution contains an additional **bilocal term** coupling x ↔ conjugate points, and Eisler–Peschel showed the lattice modular Hamiltonian likewise carries long-range hopping beyond the β-weighted energy density. The 10²–10³ relative errors are the *expected signature of the missing bilocal/long-range piece*, not a failure of the GNS idea.

**Concrete next construction (S2-b spec):** rerun the probe with A₀ = the **exact vacuum lattice kernel** K_vac = ln((1−C_vac)/C_vac) (now available as `modular_1p`) held FIXED as the state-independent operator, and ω varied over the coherent/current family (legitimate GNS test on the vacuum orbit: fixed operator, varying state); thermal states then map where the orbit ends. Secondary route: implement the Casini–Huerta bilocal term explicitly and test the corrected geometric ansatz. Falsifier unchanged: if the exact-kernel operator pair still fails across the coherent family, the vacuum-orbit Gram identification is refuted, and edit-007 records the refutation instead.

**?₂ status: remains P.** Continuum vacuum ray exact + state layer verified + operator obstruction diagnosed with a named repair path. No premature promotion.

See also: [`s2-gns-status.md`](s2-gns-status.md). Certificate: `certificates/s2_certificate.json`.
