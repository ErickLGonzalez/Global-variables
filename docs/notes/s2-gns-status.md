# S2 GNS program — status ledger

**Last updated:** 2026-07-13  
**?₂ matrix cell:** P (H-track) — **not** promoted to H.

## Two layers

| Layer | Code | Certificate | Status |
|---|---|---|---|
| Operator probe | `s2_gns/probe.py`, `tests/test_s2_gns.py` | `certificates/s2_gns_certificate.json` | PARTIAL — continuum vacuum ray exact; geometric (K, cut-T) ansatz fails ratio tracking |
| State / modular | `s2_gns/gaussian.py`, `s2_gns/qnec_lattice.py`, `tests/test_s2_state_layer.py` | `certificates/s2_certificate.json` | PASS (5/5) — c blind-fit, vacuum saturation, thermal identity, first law, positivity gate |

## Headline

B6 matrix structure is **populated from microscopic data** on the state side. The operator mismatch is **localized**: missing Casini–Huerta bilocal / Eisler–Peschel long-range modular terms in the geometric ansatz.

## Next (S2-b)

1. Fixed operator A₀ = `modular_1p(C_vac)` on the vacuum orbit; vary ω (coherent/current family).
2. Or: implement bilocal modular term explicitly and retest geometric ansatz.

## Edit record

[`edit-007-gns-partial-draft.md`](../atlas-edits/edit-007-gns-partial-draft.md) — draft only; no atlas bump.

Full analysis: [`s2-gns-free-fermion.md`](s2-gns-free-fermion.md).
