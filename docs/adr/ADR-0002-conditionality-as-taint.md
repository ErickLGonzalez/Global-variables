# ADR-0002 — Conditional results are modelled as assumption-taint, not a new verdict

- **Status:** PROVISIONAL (adopted 2026-07-16 — "adapt conditionality = taint for now").
  Revisit and either RATIFY or REPLACE; see "Revisit trigger" below.
- **Deciders:** Erick (sign-off), Rosy/agent (proposal).
- **Supersedes DRAFT item:** B13-CDL README "Awaiting sign-off #1 — CONDITIONAL(X)
  verdict vocabulary (SPEC §6 extension)".
- **Related:** `docs/adr/ADR-PIR-0001.md`, `docs/SPECIFICATION.md` §4/§6,
  `b13_cdl/docs/pir-bridge-v0.1.md`, `pir/` substrate.

## Context
B13-CDL surfaces results that hold only *conditional on* a stipulated unknown —
`CONDITIONAL(GRH)` primality, `CONDITIONAL(BSD)` congruent numbers,
`CONDITIONAL(lattice-k)` bounds, input-conditional vacuum stability. The sprint
proposed adding a first-class `CONDITIONAL(X)` verdict to the SPEC §6 vocabulary.

The PIR substrate (ADR-PIR-0001) already models exactly this shape: every fact
carries **assumption-taint** and the store supports **invalidation traversal** —
invalidate an assumption and every transitively dependent fact is downgraded,
deleting nothing. The B13→PIR bridge demonstrated that conditioning unknowns map
cleanly onto assumptions (`asm:GRH`, `asm:weak_BSD_for_E_n`, …), and that
invalidating `asm:GRH` downgrades exactly the GRH-conditional facts.

## Decision
**Conditionality is represented as assumption-taint, not as a new verdict.**
- The `verdict`/`outcome` field stays locked to the existing SPEC §4/§6
  vocabulary (`FORCED, PERMITTED, REJECTED, NONIDENTIFIABLE,
  OBSERVATIONALLY_EQUIVALENT, APPARATUS_LIMITED, REPRESENTATION_DEPENDENT,
  AMBIGUOUS`). **No `CONDITIONAL(X)` verdict is added.**
- A result that holds only under stipulated unknown(s) X carries those X as
  assumptions (`asm:X`); its base verdict is whatever it is modulo X. If an X is
  later withdrawn, invalidation traversal downgrades the dependent results.
- B13's certificate `verdict` *string* may still read "CONDITIONAL(X): …" for
  human readability; that is a display string, not a member of the locked
  vocabulary. The machine-checkable verdict lives on the PIR fact.

## Consequences
- No SPEC verdict-list change; the locked vocabulary is unchanged.
- Conditional epistemics become *operational*: withdrawing an assumption
  automatically propagates via the PIR store instead of requiring a bespoke
  verdict semantics.
- The epistemic asymmetry B13 cares about (unconditional COMPOSITE /
  NOT_CONGRUENT vs conditional PRIME / CONGRUENT) is preserved as "has the
  relevant `asm:` or not".

## Rejected alternative
Adding `CONDITIONAL(X)` as a SPEC §6 verdict — rejected (for now) as redundant
with assumption-taint and as introducing a parametric verdict the engine would
have to special-case, when the substrate already carries X losslessly.

## Revisit trigger (reminder)
This decision is PROVISIONAL. Come back to it if it has not been RATIFIED (or
REPLACED) in later work. Concretely, revisit when any of these happens:
- a later sprint needs conditional semantics the taint model cannot express, or
- the atlas/claims-table needs to *display* conditionality as a verdict, or
- two release cycles pass with the decision still PROVISIONAL.
To ratify: change **Status** above to `RATIFIED` (with a date) and, if desired,
add a one-line pointer in `docs/SPECIFICATION.md` §4. A scheduled reminder is
configured to check this file's status and ping if it is still PROVISIONAL.
