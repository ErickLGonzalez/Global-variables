"""Run B4 REAL mode on official posterior samples and write certificate."""

import json
import os
import sys
import time

import h5py

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from b4_area_pipeline.loader import FINAL_KEYS_RINGDOWN, load_pesummary
from b4_area_pipeline.pipeline import test_event

EVENTS = {
    "GW250114": {
        "path": os.path.join(ROOT, "data", "GW250114_posterior.h5"),
        "analysis": None,
        "source": "Zenodo 16877102 posterior_samples_NRSur7dq4.h5 (LVK PRL 135, 111403)",
        "data_ref": "data/GW250114_posterior.h5 (zenodo.org/records/16877102 posterior_samples_NRSur7dq4.h5)",
    },
    "GW150914": {
        "path": os.path.join(ROOT, "data", "GW150914_posterior.h5"),
        "analysis": "C01:Mixed",
        "source": "GWTC-2.1 PEDataRelease mixed_cosmo (Zenodo 6513631)",
        "data_ref": (
            "data/GW150914_posterior.h5 "
            "(zenodo.org/records/6513631 "
            "IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_cosmo.h5, "
            "analysis=C01:Mixed)"
        ),
    },
}


def provenance(path, analysis):
    with h5py.File(path, "r") as f:
        groups = [k for k in f.keys() if k not in ("history", "version")]
        g = f[analysis] if analysis else f[groups[0]]
        ps = g["posterior_samples"]
        names = list(ps.dtype.names)
    if all(k in names for k in FINAL_KEYS_RINGDOWN):
        return "ringdown-only final state (circularity-free)"
    return "NR-fit final state (partially circular; see remnant.py note)"


def main():
    results = {}
    data_files = {}
    for name, meta in EVENTS.items():
        samples = load_pesummary(meta["path"], analysis=meta["analysis"])
        prov = provenance(meta["path"], meta["analysis"])
        r = test_event(samples)
        r["source"] = meta["source"]
        r["final_state_provenance"] = prov
        results[name] = r
        data_files[name] = meta["data_ref"]
        print(name, r)

    all_supported = all(
        r["status"] == "SUPPORTED_AT_CREDIBILITY" for r in results.values()
    )
    cert = {
        "certificate_version": "0.3",
        "certificate_class": (
            "STATISTICAL (Monte Carlo + exact Clopper-Pearson bound); "
            "NOT the exact-rational class of B1"
        ),
        "problem": "B4: area theorem as gravity's composition law (conjecture ?3)",
        "mode": "REAL -- official GWOSC/zenodo posterior samples",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "data_files": data_files,
        "conservative_choices": [
            "exact binomial lower bound instead of MC point estimate",
            "component spins from posterior spin_1z/spin_2z (absolute value)",
        ],
        "known_caveats": [
            "These PE releases expose NR-fit final states "
            "(final_mass_source/final_spin), not ringdown-only columns; "
            "provenance labeled accordingly. Ringdown-preferred path remains "
            "available when those keys are present.",
            "Large posterior HDF5s are not committed; download URLs recorded "
            "in data/README.md and this certificate.",
        ],
        "results": results,
        "composition_law_statement": (
            "A_f >= A_1 + A_2 realized as entropy subadditivity under merger; "
            "dimensionless invariant eta_A"
        ),
        "aggregate": "ALL_EVENTS_SUPPORTED" if all_supported else "MIXED",
        "external_anchors": [
            "Isi et al., PRL 127, 011103 (2021): GW150914 area law ~97%",
            "LVK, PRL 135, 111403 (2025): GW250114 area law, highest-precision test",
            "GW230814/GW231226 (GWTC-4): area law at effectively >=5 sigma "
            "(arXiv:2509.03480)",
        ],
    }
    out = os.path.join(ROOT, "certificates", "b4_certificate.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(cert, f, indent=2)
    print("WROTE", out, "aggregate=", cert["aggregate"])


if __name__ == "__main__":
    main()
