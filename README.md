# Global-variables

**Observational decompilation of physics.** Treat physical law as an unknown rule system; recover its grammar — types, invariants, operators, composition rules — one certified constraint at a time. Constants are conjectured to be invariants of a positive, compositional operator structure 𝕽, not primitive numbers.

Core documents:
- [`docs/constant-atlas-v0.5.md`](docs/constant-atlas-v0.5.md) — constant atlas, restraint matrix, bridge formula, discipline formula, decoding chain (the base algorithm). *(Prior: [v0.4](docs/constant-atlas-v0.4.md), [v0.3](docs/constant-atlas-v0.3.md), [v0.2](docs/constant-atlas-v0.2.md).)*
- [`docs/conjectures-v0.1.md`](docs/conjectures-v0.1.md) — the ten blank-filling conjectures ?₁–?₁₀, each with formalization, test protocol, and falsifier.

## B1 — Truncated moment solver (implemented ✅)

Benchmark B1 of the decoding chain: hidden moments of a finite measure are recovered through positivity + Curto–Fialkow flat extension, with **exact rational certificates**.

Epistemic outcomes (Discipline Formula v0.2):

| Outcome | Meaning | Mechanism |
|---|---|---|
| `FORCED` | uniquely determined | flat extension → exact recurrence, exact recovery |
| `PERMITTED` | constrained to a certified interval | exact-PSD bisection; inner interval certified feasible, outer bracket certified infeasible; unbounded directions reported honestly |
| `REJECTED` | hard constraint violated | exact negative Schur pivot as witness |

Design guarantees:
- All positivity/rank/forcing claims use **exact `Fraction` arithmetic** (the Schur pivots generalize the `G00 > 0`, `S2 = G22 − G02²/G00 > 0` verifier standard).
- Numerics are **quarantined** to atom extraction only, with an audited residual against the exact moments reported in the certificate.
- `Score = ∞` on any violated **or uncertified** hard constraint — uncertified ≠ pass.

Run:
```bash
python3 tests/test_b1.py
```
Output: 4/4 tests pass; JSON certificate written to `certificates/b1_certificate.json`.

```
b1_moment_solver/
  exact.py        exact Hankel matrices, PSD certificates, rank, flat-extension recurrence
  recover.py      forced-tail recovery, permitted intervals, audited atom extraction
  certificate.py  forced/permitted/free/rejected JSON certificate format
tests/test_b1.py  T1 forced · T2 permitted · T3 rejected (negative control) · T4 atom audit
```

## B4 — Area theorem as gravity's composition law (implemented ✅, REAL mode)

Benchmark B4 tests conjecture **?₃**: A_f ≥ A₁ + A₂ under merger, via the dimensionless invariant η_A = (A_f − A₁ − A₂)/A_f. Certificate class: **STATISTICAL** (Monte Carlo + exact Clopper–Pearson binomial lower bound) — deliberately distinct from B1's exact-rational class.

```bash
python3 tests/test_b4.py          # DEMO regression
python3 scripts/run_b4_real.py    # REAL mode (see data/README.md)
```

**REAL results** (official posteriors; certificate `certificates/b4_certificate.json`, mode REAL):
GW250114 → SUPPORTED (P_lower 0.99977, η_A ≈ 0.366) · GW150914 → SUPPORTED (P_lower 0.99862, η_A ≈ 0.363). Final-state provenance in these PE releases is NR-fit (ringdown columns absent); loader still auto-prefers ringdown keys when present. Edit-001 apply conditions are checked; atlas bump to v0.3 remains for the promotion pass.

Demo regression (reconstructed summary-statistic posteriors): GW150914 / GW250114 SUPPORTED; GW190521 / GW190814 INCONCLUSIVE **by design**; falsifier injection → VIOLATION_CANDIDATE.

```
b4_area_pipeline/
  kerr.py       Kerr horizon area, η_A invariant
  remnant.py    validated nonspinning NR fits (cross-check layer only)
  demo_data.py  published summary stats, provenance-flagged
  pipeline.py   MC test, exact binomial bounds, statistical certificate
  loader.py     GWOSC/PESummary HDF5 loader (REAL mode, ringdown-preferred)
```

## B2 — Qubit process completion via Choi positivity (implemented ✅)

Extends the exact-rational certificate class to **Gaussian-rational Hermitian matrices** (`cexact.py`) and demonstrates **restraint stacking** — the atlas mechanism — on a finite quantum process:

| Restraints active | Hidden Choi entry | Outcome |
|---|---|---|
| PSD alone | diagonal of rank-2 mixed channel | PERMITTED — certified interval [1/9, ∞) |
| PSD + trace preservation | same entry | **FORCED** to exact truth (1) |
| PSD + rank-1 (pure process) | complex off-diagonal | **FORCED** to −12i/25 exactly (flat-extension analogue) |

Plus exact CPTP audit (Choi's theorem as the gate) and a negative control (corrupted Choi rejected with exact witness pivot). Run: `python3 tests/test_b2.py` — 5/5 pass, certificate in `certificates/b2_certificate.json`.

## B3 — Electroweak closed system (implemented ✅)

Benchmark B3 runs the decoding chain on tree-level electroweak structure. Pseudo-data for `(e, g, g′, θ_W, M_W, M_Z, v, G_F)` is presented as an unlabeled exact-Fraction table; the engine must *discover* the relations by template forcing (same epistemic class as B1/B2) and report **d_identifiable = 3**.

```bash
python3 tests/test_b3.py
```

Results (5/5):
- Headline relations found: `e = g sinθ_W`, `M_W = gv/2`, `M_Z = (v/2)√(g²+g′²)`, `G_F = 1/(√2 v²)` (√2 certified via `1/G_F² = 2 v⁴`)
- Exact Jacobian rank over ℚ: n=9, rank=6 → **d_identifiable = 3**
- FREE basis recovered: `{g, g′, v}`; forced: `{e, sinθ_W, cosθ_W, M_W, M_Z, G_F_inv_sq}`
- Held-out `M_Z` predicted exactly from the free basis; corrupted `e` breaks R1/R2/R9 (negative control)

```
b3_electroweak/
  exact.py        Fraction helpers, Pythagorean Weinberg angle
  pseudo_data.py  closed-system generator from free basis (g, g′, v)
  relations.py    exact template discovery (R1–R9)
  rank.py         Jacobian rank → d_identifiable
  graph.py        FREE/FORCED dependency labels
  discover.py     end-to-end pipeline
```

## B5 — Cluster / multi-channel factorization (?₅ → H) (implemented ✅)

Benchmark B5 is the B3 extension named in conjecture ?₅: 2→2 and 2→4 toy channels with exact-Fraction amplitudes. The engine must discover that **one coupling** controls all factorization residues (`R_24 = A_22²`) and reject channel-dependent couplings.

```bash
python3 tests/test_b5.py
```

Results (5/5): factorization identities hold; **d_identifiable = 1**; falsifier FAIL as required. Atlas edit-002 promotes gauge Cmp (?₅) → **H** for α, α_s, and the electroweak block.

```
b5_cluster/
  exact.py        Fraction helpers
  pseudo_data.py  local vs channel-dependent counterexample tables
  relations.py    factorization template discovery (F1–F6)
  rank.py         Jacobian rank → d_identifiable
  discover.py     end-to-end pipeline
```

## B6 — 2D QNEC as Schur-pivot positivity (?₂ → P) (implemented ✅)

Benchmark B6 places the strengthened 2D QNEC inside the certified verifier: `2π⟨T⟩ ≥ S'' + (6/c)(S')²` **⇔** PSD of `M = [[c/6, S'], [S', 2πT − S'']]`. Saturation ⇔ rank-1 flat boundary (same structure B1 uses for forcing).

```bash
python3 tests/test_b6.py
```

Results (5/5): 500-case equivalence audit; vacuum saturation (pivot exactly 0); coherent-state strictness; thermal symbolic identity; negative control (witness pivot −1/12). Atlas edit-003 promotes G Pos (?₂) → **P (H-track)**. Epistemic scope: exact reformulation + certified instances — not a new QNEC proof; GNS realization of M remains open for H.

```
b6_qnec/
  qnec.py   matrix, Schur pivot, vacuum / coherent / thermal / falsifier instances
```

## B7 — Onsager transport-matrix completion (implemented ✅)

Benchmark B7 (seeded by R15) exercises restraint stacking on **effective coefficients**: near-equilibrium transport `J = L X` with `L ⪰ 0` (second law) and `L = Lᵀ` (Onsager reciprocity).

```bash
python3 tests/test_b7.py
```

Results (5/5): ground-truth PD+symmetric; PSD alone → PERMITTED; +reciprocity → FORCED; second-law and reciprocity falsifiers rejected. Certificate: `certificates/b7_certificate.json`.

```
b7_onsager/
  exact.py         Fraction helpers
  pseudo_data.py   thermoelectric L, hide/corrupt
  complete.py      PSD audit, reciprocity forcing, permitted intervals
```

## B8 — Blind grammar identification (implemented ✅) & Atlas Engine v0.1 (implemented ✅)

**B8** (6/6): identifies Hamiltonian / gradient-flow / GENERIC / quantum grammars from unlabeled data using similarity-invariant signatures only (R15 canonicalization). Exactly-zero damping is never claimed — conservative verdict is **HAMILTONIAN_WITHIN_BOUND** with a certified damping bound; drift test detects weak damping below the spectral floor. Quantum split is exact via Choi rank (B2).

```bash
python3 tests/test_b8.py
python3 tests/test_atlas_engine.py
```

**Atlas Engine v0.1** (5/5): restraint matrix as a constraint-satisfaction object. Eight theorem-anchored implication rules propagate to fixpoint → **7 candidate upgrades** (Cmp/Top/Λ-Pos), each with derivation chains; engine cannot mint H. Certificates: `certificates/b8_certificate.json`, `certificates/atlas_engine_certificate.json`.

**Sprint work orders:** [`docs/sprint-specs-v1.md`](docs/sprint-specs-v1.md) — S1 ratify engine → atlas v0.6; S2 GNS for ?₂→H; S3 PDG/B5; S4 ?₇ dS rank; S5 B7 Kelvin data.

## Atlas edits

- [edit-001](docs/atlas-edits/edit-001-conjecture3-promotion.md) — **?₃ → P (H-track)** (atlas v0.3)
- [edit-002](docs/atlas-edits/edit-002-conjecture5-promotion.md) — **?₅ → H** (atlas v0.4)
- [edit-003](docs/atlas-edits/edit-003-conjecture2-qnec.md) — **?₂ → P (H-track)** (atlas v0.5)

## Research library

[`docs/references.md`](docs/references.md) — research-paper ledger. **R15** + [addendum](docs/notes/r15-addendum-cross-agent-review.md): **B7 done**, **B8 done**, engine v0.1. **R14** Maudlin: M-layer + arrival-time track.

## Roadmap (proposed next steps)

**Immediate (next session):**
1. **S1** — ratify Atlas Engine pass → atlas v0.6 (edit-004/005/006).
2. **S2 / ?₂ → H** — GNS realization (free-fermion route).
3. **S3** — PDG empirical layer for B5.

**Near-term:**
4. **S4** — ?₇ toy-dS rank saturation (heavy compute).
5. **S5** — B7 Kelvin-relation real data.
6. Arrival-time track (R14); ?₁ / ?₄/?₈/?₉ / ?₆.

## Discipline

Every `?` is a **prediction with a falsifier**, never evidence for the synthesis that produced it. Promotion requires: all hard constraints certified · ≥2 domains from one 𝕽 · d_identifiable strictly reduced · survival on held-out **domains** · ≥1 novel blind-tested prediction.
