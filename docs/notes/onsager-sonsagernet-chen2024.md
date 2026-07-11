# Note: Constraint-Native Discovery & the Onsager Restraints — Chen et al. 2024 (R15)

**Paper:** Chen, Soh, Ooi, Vissol-Gaudin, Yu, Novoselov, Hippalgaonkar, Li, "Constructing custom thermodynamics using deep learning," *Nat. Comput. Sci.* 4, 66–85 (2024). Open access; arXiv:2308.04119; code Zenodo 10.5281/zenodo.10212239. Pointer arrived via its paywalled Research Briefing (doi:10.1038/s43588-023-00590-4). Ledger entry **R15, METHOD**.

## The method, compressed

S-OnsagerNet learns, from microscopic trajectories of a stochastic dissipative system, (i) a set of low-dimensional **closure coordinates** Z = (Z*, Ẑ) sufficient to close the dynamics of chosen macroscopic variables Z*, and (ii) an evolution law on them of generalized-Onsager form — deterministic core Ż = −M∇V(Z) with **M symmetric PSD** (dissipation) and V a learned generalized potential, extended with stochastic fluctuations. The physical structure is enforced **by network architecture**, not by regularization. Demonstration: polymer chains with ~900 DOF compressed to **3** thermodynamic coordinates; energy landscape with stable/transition states; validation on single-molecule DNA stretching experiments including predicted fluctuation correlations.

## Why this is our kind of paper

It is an operating instance of the program's core mechanism — *restraints shrink hypothesis space until structure is forced* — realized in the candidate-generation layer rather than the gating layer. Their structured/unstructured distinction maps exactly onto our architecture:

| Their term | Our term | Where constraints act |
|---|---|---|
| unstructured (SINDy, kernels, PINN-regularized) | R12-class generators | post-hoc gates (decoding-chain step 6) |
| structured (S-OnsagerNet, Hamiltonian/symplectic/Poisson nets) | constraint-native generators | hypothesis space itself (step 5) |

## What we adopt

**A. Constraint-native generators as a step-5 option.** When a sector's restraint bundle contains architecture-expressible entries (PSD dissipative parts, antisymmetric conservative parts, symplectic structure, potential/Lyapunov form), prefer generators that enforce them by construction: the search never leaves 𝔉 along those axes, so gate rejections concentrate on the *informative* constraints. **Firewall (mandatory):** by-construction constraints are claims about the hypothesis class, not certificates about the learned object. Learned M, V, closure maps remain NUMERICAL-DISCOVERY class; held-out verification, adversarial attack (step 8), and the M-layer stipulation ledger (R14) apply unchanged. "PSD by architecture" never substitutes for "PSD certified on the fitted object."

**B. Closure = dynamical d_identifiable.** Their closure problem — given macroscopic variables of interest, learn the minimal supplementary coordinates that close the dynamics — is the evolution-law analogue of our static rank discovery (B3 Jacobian rank, B5 coupling collapse). Adopt the pattern: d_identifiable^dyn(sector) := minimal closure dimension, discovered not assumed, with the closure claim tested on held-out trajectories.

**C. Benchmark B7 (implemented): Onsager transport-matrix completion.** Near-equilibrium transport is governed by J_i = Σ_j L_ij X_j with two stacked restraints on the coefficient matrix L: second law ⇒ **L ⪰ 0** (entropy production σ = XᵀLX ≥ 0, Pos/Thm columns) and microscopic reversibility ⇒ **L = Lᵀ** (Onsager reciprocity, Sym column). Delivered as `b7_onsager/` + `tests/test_b7.py` + `certificates/b7_certificate.json`: PSD alone → PERMITTED; +reciprocity → FORCED; second-law and reciprocity falsifiers rejected. Empirical thermoelectric layer (Seebeck/Peltier / Kelvin) remains optional later.

## What we do not adopt

- No deep-learning dependency enters the certified layers; if S-OnsagerNet-style generators are used, they live strictly in step 5 with outputs quarantined until gated.
- No claim that the Onsager principle is fundamental; it is a near-equilibrium effective restraint (its own domain-of-validity is an M-layer stipulation).

**Filed:** 2026-07-11.
