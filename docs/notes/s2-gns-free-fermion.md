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
