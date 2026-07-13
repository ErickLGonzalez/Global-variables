# S2 GNS program — status ledger

**Last updated:** 2026-07-13  
**?₂ matrix cell:** P (H-track) — **not** promoted to H.

## Three layers

| Layer | Code | Certificate | Status |
|---|---|---|---|
| Operator probe | `s2_gns/probe.py`, `tests/test_s2_gns.py` | `certificates/s2_gns_certificate.json` | PARTIAL — continuum vacuum ray exact; geometric (K, cut-T) ansatz fails ratio tracking |
| State / modular | `s2_gns/gaussian.py`, `s2_gns/qnec_lattice.py`, `tests/test_s2_state_layer.py` | `certificates/s2_certificate.json` | PASS (5/5) — c blind-fit, vacuum saturation, thermal identity, first law, positivity gate |
| Exact-kernel orbit (S2-b) | `s2_gns/s2b_probe.py`, `tests/test_s2b.py` | `certificates/s2b_certificate.json` | PASS (6/6) — fixed `modular_1p` kernel on coherent orbit; dual-route S_rel <0.5%; capacity=entropy Gram entry |

## Headline

B6 matrix structure is **populated from microscopic data** on the state side. The geometric (K, cut-T) operator mismatch is **attributed**: single-interval continuum modular Hamiltonian is local (Bisognano–Wichmann); lattice bulk deviation is Eisler–Peschel long-range structure (T1 quantifies). The **exact vacuum kernel** passes the coherent-orbit GNS first-moment test to <0.5% with quadratic q-scaling; local ansatz fails ≥10× worse on identical data.

## Next

1. Extend to multi-interval geometry (Casini–Huerta bilocal terms).
2. State-independent operator pair tracking M on thermal/coherent holdouts (edit-007 checklist).

## Edit record

[`edit-007-gns-partial-draft.md`](../atlas-edits/edit-007-gns-partial-draft.md) — draft only; no atlas bump.

Full analysis: [`s2-gns-free-fermion.md`](s2-gns-free-fermion.md).
