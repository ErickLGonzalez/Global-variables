"""Stage 3: forward recompilation (P6), intervention search (P7), cross-domain
diff (P8).

P6-1 The B9 T6 realization is reproduced exactly (E01 = 4.75, anharmonicity
     -0.25 from EC=1/4, EJ=25/2).
P6-2 Altering one latent (EC) changes the held-out spectroscopy prediction;
     the held-out point is not reused; residual provenance is complete.
P7-1 On a synthetic benchmark the known discriminator (temperature sweep) is
     recovered as the top proposal; every proposal is HEURISTIC + states
     assumptions.
P7-2 Negative control: when no intervention separates the candidates ->
     NONIDENTIFIABLE.
P8-1 BEC vs B9 cross-domain diff reports shared motifs with SEPARATE similarity
     and confidence and a named correlator; apparatus differences explicit; no
     ontology-identity claim; least-cost discriminator proposed.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pir import forward
from pir.intervention_search import AdmissibleIntervention, search
from pir.diff import cross_domain_diff
from pir.domains import bec

FAILURES = []


def check(label, errors):
    if errors:
        FAILURES.append((label, errors)); print(f"  [FAIL] {label}")
        for e in errors[:6]:
            print(f"         - {e}")
    else:
        print(f"  [ ok ] {label}")


def p6_forward():
    base = forward.b9_baseline()
    pred = forward.predict_spectroscopy(base)
    errs = []
    if abs(pred["E01"] - 4.75) > 1e-9:
        errs.append(f"baseline E01 {pred['E01']} != 4.75")
    if abs(pred["anharmonicity"] + 0.25) > 1e-9:
        errs.append(f"anharmonicity {pred['anharmonicity']} != -0.25")
    # Patch a latent -> changed held-out prediction.
    patched = base.patch("EC", 0.5)
    pred2 = forward.predict_spectroscopy(patched)
    if abs(pred2["E01"] - pred["E01"]) < 1e-6:
        errs.append("altering EC did not change the held-out E01 prediction")
    # held-out residual with complete provenance, no reuse.
    res = forward.held_out_residual(patched, pred2, held_out_value=4.735,
                                    held_out_id="b9_T6_E01_measured")
    prov = res.provenance
    if prov["held_out_reused_in_fit"] is not False:
        errs.append("held-out point marked reused")
    for k in ("realized_from_latents", "apparatus", "held_out_id", "predictor"):
        if k not in prov:
            errs.append(f"residual provenance missing {k}")
    check("P6 forward recompilation: latent patch changes held-out prediction, "
          "provenance complete, no reuse", errs)


def p7_intervention():
    hyps = ["hyp_qtunnel", "hyp_thermal"]
    interventions = [
        AdmissibleIntervention("int_temp_sweep", "TEMPERATURE_CHANGE", cost=8.0,
                               predicted_outcomes={"hyp_qtunnel": "plateau",
                                                   "hyp_thermal": "arrhenius"},
                               assumptions=("asm:thermometry_calibrated",)),
        AdmissibleIntervention("int_flux_sweep", "BOUNDARY_CHANGE", cost=2.0,
                               predicted_outcomes={"hyp_qtunnel": "same",
                                                   "hyp_thermal": "same"},
                               assumptions=("asm:flux_linear",)),
    ]
    out = search(interventions, hyps)
    errs = []
    if out["verdict"] != "DISCRIMINATOR_FOUND":
        errs.append(f"expected a discriminator, got {out['verdict']}")
    elif out["best"]["intervention_id"] != "int_temp_sweep":
        errs.append(f"wrong discriminator: {out['best']['intervention_id']}")
    if out.get("best") and out["best"]["tag"] != "HEURISTIC":
        errs.append("proposal not HEURISTIC-tagged")
    if out.get("best") and not out["best"]["assumptions"]:
        errs.append("proposal states no assumptions")
    # negative control: neither intervention separates.
    flat = [AdmissibleIntervention("a", "X", 1.0, {"hyp_qtunnel": "s", "hyp_thermal": "s"}),
            AdmissibleIntervention("b", "Y", 1.0, {"hyp_qtunnel": "t", "hyp_thermal": "t"})]
    neg = search(flat, hyps)
    if neg["verdict"] != "NONIDENTIFIABLE":
        errs.append(f"negative control not NONIDENTIFIABLE: {neg['verdict']}")
    check("P7 intervention search: known discriminator recovered; negative "
          "control -> NONIDENTIFIABLE; proposals HEURISTIC + assumptions", errs)


def p8_cross_domain():
    # B9 circuit invariants (feature-level) vs BEC.
    b9_feats = {"symmetry_group": "U(1)", "rank_sequence": [1, 2],
                "positivity_cone": "PSD", "spectral_class": "linear_response_positive"}
    bec_feats = bec.canonical_invariants()
    b9_app = {"id": "apparatus:josephson_circuit", "imaging": "readout_chain",
              "route": "cal:spectroscopy_route"}
    interventions = [
        AdmissibleIntervention("int_scale_sweep", "SCALE_SWEEP", cost=3.0,
                               predicted_outcomes={"h_circuit": "a", "h_bec": "b"}),
        AdmissibleIntervention("int_expensive", "GEOMETRY_CHANGE", cost=50.0,
                               predicted_outcomes={"h_circuit": "a", "h_bec": "b"}),
    ]
    d = cross_domain_diff(b9_feats, bec_feats, b9_app, bec.apparatus(),
                          interventions, ["h_circuit", "h_bec"])
    errs = []
    # shared motifs: symmetry_group, rank_sequence, positivity_cone match;
    # spectral_class diverges (linear_response vs bogoliubov).
    if set(d.shared_motifs) != {"symmetry_group", "rank_sequence", "positivity_cone"}:
        errs.append(f"unexpected shared motifs {d.shared_motifs}")
    if "spectral_class" not in d.divergent:
        errs.append("spectral_class should diverge")
    # similarity and confidence are SEPARATE numbers + named correlator.
    if d.similarity == d.confidence:
        errs.append("similarity and confidence collapsed to one number")
    if d.correlator != "canonical-invariant-match/0.1":
        errs.append("correlator not named")
    # apparatus differences explicit.
    if not d.apparatus_differences:
        errs.append("apparatus differences not surfaced")
    if "ontology-identity" not in d.ontology_claim and "no ontology" not in d.ontology_claim:
        errs.append("ontology overclaim not guarded")
    # least-cost discriminator proposed (the cheaper of the two).
    if d.least_cost_discriminator != "int_scale_sweep":
        errs.append(f"least-cost discriminator {d.least_cost_discriminator} != int_scale_sweep")
    check("P8 cross-domain diff: shared motifs, separate similarity/confidence + "
          "correlator, explicit apparatus diff, least-cost discriminator", errs)


if __name__ == "__main__":
    print("== Stage 3: forward / intervention / cross-domain ==")
    p6_forward(); p7_intervention(); p8_cross_domain()
    print("\n== SUMMARY ==")
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} check(s) failed."); sys.exit(1)
    print("PASS: forward recompilation, intervention search, cross-domain diff live.")
    sys.exit(0)
