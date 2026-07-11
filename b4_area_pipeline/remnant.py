"""NR-calibrated remnant fits (nonspinning), used ONLY as a cross-check
layer, never as the source of the test statistic.

Epistemic note (circularity guard): catalog final mass/spin values are
themselves produced by NR remnant fits applied to inspiral parameters, so
an area test built on them is partially an internal-consistency check of
general relativity's waveform pipeline. The rigorous test (Isi et al. 2021;
LVK GW250114, PRL 135, 111403) measures the FINAL state from the ringdown
alone and the INITIAL state from the inspiral alone. This pipeline
therefore accepts ringdown-only final-state posteriors when available
(see loader.py) and labels the provenance in every certificate.

Fits implemented (nonspinning, symmetric mass ratio nu = m1 m2 / M^2):
  M_f / M = 1 + (sqrt(8/9) - 1) nu - 0.4333 nu^2 - 0.4392 nu^3
            (Tichy & Marronetti 2008 lineage)
  chi_f   = sqrt(12) nu - 3.871 nu^2 + 4.028 nu^3
            (Berti et al. / Buonanno et al. lineage)
Both are validated in tests against the equal-mass NR benchmarks
M_f/M ~ 0.9516, chi_f ~ 0.6865.
"""

import numpy as np

SQRT89 = np.sqrt(8.0 / 9.0)
SQRT12 = np.sqrt(12.0)


def sym_mass_ratio(m1, m2):
    m1, m2 = np.asarray(m1, float), np.asarray(m2, float)
    return (m1 * m2) / (m1 + m2) ** 2


def final_mass_nonspinning(m1, m2):
    nu = sym_mass_ratio(m1, m2)
    M = np.asarray(m1, float) + np.asarray(m2, float)
    return M * (1.0 + (SQRT89 - 1.0) * nu - 0.4333 * nu ** 2 - 0.4392 * nu ** 3)


def final_spin_nonspinning(m1, m2):
    nu = sym_mass_ratio(m1, m2)
    return SQRT12 * nu - 3.871 * nu ** 2 + 4.028 * nu ** 3
