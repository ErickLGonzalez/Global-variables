# Atlas Edit 007 (DRAFT) — GNS item for ?₂: partial (continuum vacuum ray)

**Status: DRAFT (2026-07-11) — does NOT bump atlas version; does NOT promote ?₂ → H.**

## Proposed change

None to matrix cells. This edit records progress on the **P→H requirements** listed in [edit-003](edit-003-conjecture2-qnec.md):

> 1. **GNS realization:** exhibit operators {A₀, A₁} and a state ω with ω(A_i†A_j) = M_ij …

## What S2 established

**Internal certificate:** `certificates/s2_gns_certificate.json` + [`docs/notes/s2-gns-free-fermion.md`](../notes/s2-gns-free-fermion.md).

| Item | Status |
|---|---|
| Continuum vacuum: M = (c/6) u uᵀ, u=(1,1/du); A₁=A₀/du on the GNS ray | **DONE (exact)** |
| Coherent pivot split as orthogonal A₁ piece (B6 reading) | **Recorded** |
| State-independent lattice (A₀,A₁)=(geometric modular K, cut stress) tracks M across vacuum/thermal/current | **NOT MET** (quarantined; wrong ratio scaling at L≤120) |
| Cholesky-as-GNS | **Rejected** (sprint discipline) |

## What this does and does not claim

**Claims:** the vacuum sector of M admits a physical rank-1 GNS realization; the free-fermion lattice probe is implemented with state-independent kernels and an honest holdout verdict.

**Does not claim:** ?₂ → H; a state-independent operator pair that reproduces M for thermal/coherent; a new proof of QNEC.

## Remaining P→H checklist (unchanged from edit-003, annotated)

1. **GNS realization** — **PARTIAL** (vacuum ray only). Need continuum-limit tracking or Wall-integrand smearings off vacuum.
2. Beyond saturation (strict free-fermion excited states) — still open.
3. Higher-d QNEC instances — still open.
4. Unification with ?₃ — still open.

## Apply checklist (when promoting beyond draft)

- [ ] Lattice or continuum operator pair tracks M on ≥2 non-vacuum holdouts within certified bands
- [ ] Owner review of stipulations (equal-time proxy; Q₂₂:=Sp/ℓ)
- [ ] Atlas bump only if H criteria are actually met (not expected from this draft alone)

— Drafted 2026-07-11, S2 session. **Not applied.**
