# R15 Addendum: Cross-Agent Review (ChatGPT take on Chen et al. 2024)

A second AI analysis of R15 was reviewed on 2026-07-12. Verdict: four adoptions, one correction to our own note, one explicit non-adoption. Items are graded against the repo's discipline, not against the other agent's framing.

## Correction to our R15 note (credit where due)

Our note compressed the evolution law to Ż = −M∇V. The full S-OnsagerNet structure is

    Ż = −[M(Z) + W(Z)] ∇V(Z) + σ(Z) Ḃ

with **W antisymmetric** carrying the conservative (Hamiltonian-like) part alongside the PSD dissipative M — i.e., the architecture encodes Sym, Pos, AND the dissipative/conservative split simultaneously (GENERIC-style). This strengthens the constraint-native-generator case: three atlas columns, one architecture. Noted as an erratum to `onsager-sonsagernet-chen2024.md`.

## Adoption A — Canonicalization of learned dynamics (the strongest idea)

**Problem (correctly identified):** learned latent coordinates are not unique; Y = f(Z) yields an apparently different (M, W, V, σ) describing identical physics. Un-quotiented, equivalent laws would look like distinct discoveries.

**Our resolution (atlas-native):** this is our existing redundancy rule — d_identifiable is counted *after removing gauge, unit, and scheme redundancies* — extended to latent dynamics. Rule adopted: **only reparametrization-invariant data of a learned (M, W, V, σ) count as discovered structure.** Concretely, the invariant content of a landscape is its Morse-type data: number and indices of critical points, barrier heights in noise units, Hessian-spectrum ratios at critical points, entropy-production rate along paths, basin adjacency (landscape topology). Neural weights and coordinate charts are chart-dependent and never enter certificates. This is the program thesis applied reflexively: *learned laws, like constants, are only ever invariants.*

## Adoption B — Distill-before-score rule

**Problem (correctly identified):** dimensional compression ≠ algorithmic compression; neural (M, W, V, σ) can have larger description length than the microscopic law that generated the data.

**Rule adopted:** the L(𝕽) term of the Score is evaluated **only on symbolically distilled objects** (sparse polynomial/rational fits to V, M, W with controlled approximation error), never on raw network weights. Undistilled learned dynamics are step-5 intermediates — usable, but unscoreable and unpromotable. This makes explicit an ordering our Score formula implied but never enforced.

## Adoption C — Grammar identification as a testable output → queue B8

**Idea (correctly identified):** S-OnsagerNet *presupposes* its grammar (gradient-flow + conservative + noise); the deeper question is which structural grammar — Hamiltonian/symplectic, Onsager/gradient-flow, CP quantum evolution, gauge-covariant — best explains given data. Our step-4 type assignment is close, but the addendum sharpens it into a falsifiable benchmark:

**B8 (queued): blind grammar identification.** Generate trajectories from known grammars (a Hamiltonian system, a gradient flow, a mixed GENERIC system, a CPTP quantum process); hide the labels; run competing constraint-native generators; arbitrate by held-out error + distilled description length + constraint-violation certificates. Falsifiers built in: the chain must NOT select the Onsager grammar for pure Hamiltonian data (no dissipation to find), must NOT select Hamiltonian for dissipative data, and must report AMBIGUOUS when data genuinely underdetermine the grammar (short/noisy trajectories) rather than forcing a choice. This directly extends B5/B7's forced-vs-permitted epistemics to *structural class* rather than parameter values.

## Adoption D — Certified closure dimension (our improvement over R15)

The paper selects the closure dimension **partly by trial and error** (authors' own limitation). We already own the fix: B3-style Jacobian/rank certificates. Research item adopted: **replace trial-and-error latent-dimension selection with certified rank estimation** — d_identifiable^dyn discovered, not tuned, with an INCONCLUSIVE output when trajectory sampling cannot support the estimate. If executed, this is a concrete original contribution of our machinery back to the R15 method line, and slots into B8's pipeline.

## Adoption E — M-layer stipulations for any S-OnsagerNet-class usage

Recorded per certificate-format v0.3: near-equilibrium/small-noise assumption; non-chaotic domain of validity; trajectory sampling must cover stable AND transition regions; closure-dimension selection method. Practical pointers recorded for the B7/B8 empirical layer: datasets public, original reproduction code available, and a general JAX implementation exists (`onsagernet` package) — verify package provenance before any use.

## Non-adoption — the "encode physics into one number / minimal program N" endpoint

The reviewed analysis frames the ultimate goal as a pipeline ending in canonicalization → **numerical encoding N** of physical law. We adopt every stage *up to* canonicalization and stop there, for a disciplined reason: our Score's L(𝕽) term already captures minimal-description content in a testable form, while a single-number encoding adds no falsifiable structure — two encodings differing in an arbitrary bijection are empirically identical, so N itself can never be FORCED, only chosen. The atlas's deliverables remain **invariants, d_identifiable reductions, and forced/permitted/rejected certificates**, not encodings. (If a separate encoding track is ever wanted, it must live outside the certified layers and inherits Adoption A as a prerequisite; nothing in the current program depends on it.)

**Filed:** 2026-07-12. Companion to `onsager-sonsagernet-chen2024.md` (R15).
