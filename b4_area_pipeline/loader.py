"""REAL-mode loader for official LVK posterior sample releases.

Download posterior files from GWOSC (https://gwosc.org) / zenodo for the
events of interest, place them under data/, and run:

    from b4_area_pipeline.loader import load_pesummary
    from b4_area_pipeline.pipeline import test_event
    samples = load_pesummary("data/GW250114_posterior.h5")
    print(test_event(samples))

Ringdown preference: if ringdown-only final-state parameter names are
present, they are used for (mf, chif) -- this removes the remnant-fit
circularity and upgrades the certificate provenance.
"""

import numpy as np

INITIAL_KEYS = ["mass_1_source", "mass_2_source", "spin_1z", "spin_2z"]
FINAL_KEYS_FIT = ["final_mass_source", "final_spin"]
FINAL_KEYS_RINGDOWN = ["ringdown_final_mass_source", "ringdown_final_spin"]


def load_pesummary(path, analysis=None):
    import h5py  # imported lazily; pip install h5py
    with h5py.File(path, "r") as f:
        groups = [k for k in f.keys() if k not in ("history", "version")]
        g = f[analysis] if analysis else f[groups[0]]
        ps = g["posterior_samples"]
        names = (list(ps.dtype.names) if hasattr(ps, "dtype") and ps.dtype.names
                 else list(ps.keys()))

        def col(key):
            return np.asarray(ps[key][:] if key in names else None, float)

        m1, m2 = col("mass_1_source"), col("mass_2_source")
        chi1 = col("spin_1z") if "spin_1z" in names else np.zeros_like(m1)
        chi2 = col("spin_2z") if "spin_2z" in names else np.zeros_like(m1)
        if all(k in names for k in FINAL_KEYS_RINGDOWN):
            mf, chif = col(FINAL_KEYS_RINGDOWN[0]), col(FINAL_KEYS_RINGDOWN[1])
            provenance = "ringdown-only final state (circularity-free)"
        else:
            mf, chif = col(FINAL_KEYS_FIT[0]), col(FINAL_KEYS_FIT[1])
            provenance = "NR-fit final state (partially circular; see remnant.py note)"
    print(f"loaded {m1.size} samples; final-state provenance: {provenance}")
    return m1, m2, np.abs(chi1), np.abs(chi2), mf, np.abs(chif)
