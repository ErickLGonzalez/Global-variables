"""S3-EM tests -- the alpha row's live tension, certified.

T1  TENSION REPRODUCED: Rb~Cs pull = 5.5 sigma; three-channel chi2/dof
    ~ 17 -- mutual consistency FAILS on the atlas's most precise row.
T2  VERDICT HONESTY: the same machinery that FORCED d=1 for alpha_s
    (S3: chi2/dof = 0.11) REFUSES a single-value verdict here, emits the
    PERMITTED band, and names the cause NONIDENTIFIABLE(systematics vs
    new physics). Two datasets, two verdicts, one pipeline.
T3  JACKKNIFE ASYMMETRY: dropping Rb restores consistency (0.66 sigma);
    dropping Cs leaves 2.3 sigma; dropping g-2 leaves the full 5.5 --
    the recoil channel carries the tension, and the data mildly
    single out Rb-vs-rest as the sharpest split (recorded, NOT promoted
    to a systematics verdict).
T4  LOCALIZATION FORCED: the shared conversion inputs (R_inf, mass
    ratios) can explain <= 7% of the gap -- the tension provably lives
    in the h/m measurements, not the chain.
T5  CODATA EXPANSION CROSS-CHECK (finding upgraded in-sprint): x2.5
    recoil-error inflation drops every pairwise pull below 3 sigma
    (max 2.20) and cuts chi2/dof from 16.9 to 3.9 -- the patch SOFTENS
    the tension but does NOT restore consistency for this channel set.
    Recorded as M-layer mitigation, quantified, not endorsed.
"""

import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from s3em_alpha.analysis import (consistency_report, jackknife,
                                 localization, codata_expansion_view)
from b1_moment_solver.certificate import save_certificate


def t1_tension():
    r = consistency_report()
    p = r["pulls"]["Rb_2020_recoil~Cs_2018_recoil"]
    assert 5.2 < p < 5.8, p
    assert r["chi2_dof"] > 10, r
    print(f"T1 tension: PASS  Rb~Cs pull = {p:.2f} sigma; chi2/dof = "
          f"{r['chi2_dof']:.1f} (3 channels) -- consistency FAILS")
    return {"pull_RbCs": p, "chi2_dof": r["chi2_dof"]}


def t2_verdict():
    r = consistency_report()
    assert r["verdict"].startswith("TENSION"), r
    assert "NONIDENTIFIABLE" in r["verdict"]
    lo, hi = r["permitted_band"]
    assert lo < 46 and hi > 206
    print(f"T2 verdict honesty: PASS  single-value FORCED refused; "
          f"PERMITTED band [{lo:.0f}, {hi:.0f}] (x1e-9 offsets); cause "
          f"NONIDENTIFIABLE(systematics vs new physics). Same pipeline "
          f"FORCED d=1 for alpha_s at chi2/dof = 0.11 (S3)")
    return {"permitted_band": r["permitted_band"]}


def t3_jackknife():
    j = jackknife()
    assert j["drop_Rb_2020_recoil"]["consistent"] is True
    assert j["drop_Rb_2020_recoil"]["pull_sigma"] < 1.0
    assert j["drop_ae_2008_g2"]["pull_sigma"] > 5.0
    assert 2.0 < j["drop_Cs_2018_recoil"]["pull_sigma"] < 2.6
    print(f"T3 jackknife: PASS  drop-Rb -> "
          f"{j['drop_Rb_2020_recoil']['pull_sigma']:.2f} sigma "
          f"(consistent); drop-Cs -> "
          f"{j['drop_Cs_2018_recoil']['pull_sigma']:.2f}; drop-g2 -> "
          f"{j['drop_ae_2008_g2']['pull_sigma']:.2f} -- asymmetry "
          f"recorded, NOT promoted to a systematics verdict")
    return j


def t4_localization():
    r = localization()
    assert r["max_fraction_explainable_by_shared_inputs"] < 0.10, r
    print(f"T4 localization: PASS  shared conversion inputs explain <= "
          f"{100*r['max_fraction_explainable_by_shared_inputs']:.1f}% of "
          f"the gap -- tension FORCED into the h/m channel")
    return r


def t5_codata():
    r0 = consistency_report()
    r = codata_expansion_view()
    max_pull = max(r["pulls"].values())
    assert max_pull < 3.0, r["pulls"]
    assert r["chi2_dof"] < 0.3 * r0["chi2_dof"], (r["chi2_dof"],
                                                  r0["chi2_dof"])
    assert r["chi2_dof"] > 2.0        # honesty: NOT fully restored
    print(f"T5 CODATA expansion: PASS  x2.5 inflation: max pull "
          f"{max_pull:.2f} sigma (< 3), chi2/dof {r0['chi2_dof']:.1f} -> "
          f"{r['chi2_dof']:.2f} -- tension softened, NOT resolved; "
          f"M-layer patch quantified")
    return {"chi2_dof_inflated": r["chi2_dof"], "max_pull": max_pull}


if __name__ == "__main__":
    r1 = t1_tension(); r2 = t2_verdict(); r3 = t3_jackknife()
    r4 = t4_localization(); r5 = t5_codata()
    cert = {
        "certificate_version": "0.3",
        "certificate_class": "EMPIRICAL-STATISTICAL (FUNDAMENTAL-REAL "
                             "tier, E2)",
        "problem": "S3-EM: alpha-channel consistency (EXP-D, puzzle-chain "
                   "step 1)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "calibration_route": "three independent measurement classes; no "
                             "world-average input (values web-verified "
                             "2026-07-15; provenance in module docstring)",
        "m_layer_stipulations": [
            "input values as published; CODATA x2.5 expansion analyzed "
            "separately (T5), never silently applied",
            "2023 a_e determination flagged VERIFY-BEFORE-USE, not input",
            "registered decision rule (memo edit-009): the next "
            "independent h/m measurement adjudicates the jackknife "
            "asymmetry; no systematics verdict before then",
        ],
        "headline": "the alpha row's 5.5-sigma tension certified, "
                    "LOCALIZED to the h/m channel (shared chain <= 7%), "
                    "jackknifed (drop-Rb restores consistency at 0.66 "
                    "sigma), and the pipeline honestly REFUSES the "
                    "single-value verdict it FORCED for alpha_s -- "
                    "verdicts follow data, not hope.",
        "results": {"T1": r1, "T2": r2, "T3": r3, "T4": r4, "T5": r5},
    }
    save_certificate(cert, os.path.join(os.path.dirname(__file__), "..",
                                        "certificates",
                                        "s3em_certificate.json"))
    print("\nCertificate written: certificates/s3em_certificate.json")
    print("ALL S3-EM TESTS PASS")
