# Global-variables

**Observational decompilation of physics.** Treat physical law as an unknown rule system; recover its grammar — types, invariants, operators, composition rules — one certified constraint at a time. Constants are conjectured to be invariants of a positive, compositional operator structure 𝕽, not primitive numbers.

Core documents:
- [`docs/constant-atlas-v0.2.md`](docs/constant-atlas-v0.2.md) — constant atlas, restraint matrix, bridge formula, discipline formula, decoding chain (the base algorithm).
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

## Roadmap (proposed next steps)

**Immediate (next session):**
1. **B4 / promote ?₃** — the area-theorem-as-composition-law pipeline on public LIGO–Virgo (GWTC) posterior samples: compute η_A = (A_f − A₁ − A₂)/A_f per event, certify positivity at stated credibility, emit the program's *first cross-domain composition-law certificate*. Highest testability-to-effort ratio in the whole atlas.
2. **B2** — qubit process completion via Choi positivity J(Φ) ⪰ 0 (extends `exact.py` to complex Hermitian matrices — the one structural upgrade B1 needs anyway).

**Near-term:**
3. **B3** — electroweak closed-system test: the chain must *discover* e = g sinθ_W, M_W = gv/2, M_Z = (v/2)√(g²+g′²), G_F = 1/(√2v²) from pseudo-data and report d_identifiable = 3.
4. **?₅ formalization** — cluster-decomposition entries promoted to H; B3 extension with multi-channel factorization.
5. **?₂** — reformulate the 2D-CFT QNEC proof as certified Schur-pivot positivity inside the verifier.

**Research tracks:** ?₇ toy-dS rank-saturation study (B1 is the engine); ?₁ causal-thermal toy model; ?₄/?₈/?₉ functional-RG modeling; ?₆ index-theoretic flavor search (long horizon).

## Discipline

Every `?` is a **prediction with a falsifier**, never evidence for the synthesis that produced it. Promotion requires: all hard constraints certified · ≥2 domains from one 𝕽 · d_identifiable strictly reduced · survival on held-out **domains** · ≥1 novel blind-tested prediction.
