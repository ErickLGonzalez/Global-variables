# Preregistration 001 — Area-theorem population prediction for the next LVK catalog

**Status: DRAFT-FOR-FREEZE.** Becomes ACTIVE when Erick pushes the freeze
tag; the git commit timestamp is the registration timestamp. Rules may not
change between ACTIVE and evaluation (SPEC §6).

## Frozen machinery
- Pipeline: `b4_area_pipeline/` exactly as at freeze tag `v0.7-frozen`
  (hash recorded by the tag itself; certificate
  `certificates/b4_certificate.json` at that commit).
- Quality cuts (as implemented at freeze): inspiral segment SNR ≥ 8 AND
  ringdown segment SNR ≥ 8 with the pipeline's existing mass/spin
  posterior inputs; Clopper–Pearson interval construction unchanged.

## Registered predictions (evaluated on the first full LVK catalog
released after the freeze date, all qualifying BBH events, no exclusions
beyond the frozen cuts)
1. **P1 (population, primary):** ≥ 90% of qualifying events will yield
   area-nondecrease evidence P_lower(η_A > 0) ≥ 0.5, and the catalog-level
   combined statement (independent-event product as implemented at freeze)
   will certify area nondecrease at ≥ 0.999.
2. **P2 (strong-event rate):** ≥ 25% of qualifying events will
   individually reach P_lower ≥ 0.9 (GW250114-class evidence will not be
   unique).
3. **P3 (falsifier direction, registered):** ZERO qualifying events will
   show a certified area DECREASE at the 90% level. A single such event,
   surviving the pipeline's INCONCLUSIVE guards, is filed as a
   FUNDAMENTAL-REAL anomaly and freezes ?₃'s status pending review.

## Evaluation protocol
Run the frozen pipeline verbatim; publish per-event table + combined
certificate in `preregistrations/prereg-001-evaluation.md`; grade each of
P1–P3 PASS/FAIL against the registered thresholds; file the outcome in
the claims table as the program's first **novel prospective prediction**
result (PASS or FAIL — both are results; FAIL at P1/P2 triggers the
SPEC §6 program-level review, FAIL at P3 is an anomaly filing).

## Secondary registration (S3 pipeline, same freeze)
**P4:** the next published independent α_s(M_Z) extraction class average
(any new class, 2026+) will lie within 2σ_combined of the frozen S3
combination 0.1186 ± 0.0009 (σ_combined = quadrature of both errors).

## Honesty notes
These predictions are *conservative by design* — GR and QCD are expected
to pass them. The registered content is the program's discipline: frozen
rules, stated thresholds, timestamped commitment, symmetric treatment of
PASS and FAIL, and a registered falsifier direction (P3) with named
consequences. Registering a bold beyond-standard-model prediction without
a certified basis would violate our own claims-table rules.
