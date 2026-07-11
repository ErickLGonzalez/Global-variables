"""Demo event set: summary statistics (median, ~1-sigma) reconstructed from
published LVK results.

PROVENANCE FLAG -- READ BEFORE TRUSTING:
These are approximate values transcribed from published papers/catalogs for
DEMO MODE only. The sandbox cannot reach gwosc.org / zenodo, so official
posterior samples must be downloaded by the user and run through
loader.load_pesummary() for a REAL-mode result. Demo posteriors are
independent truncated Gaussians -- real posteriors are correlated, so demo
credibilities are indicative, not citable. Verify every number against
GWOSC / the cited papers before promotion decisions.

Component spins are set to chi = 0, which MAXIMIZES the initial Kerr area
(A is largest at chi=0 for fixed mass). This makes the area-increase test
strictly HARDER to pass -- a conservative choice in the correct direction.
"""

EVENTS = {
    "GW150914": {
        "m1": (35.6, 3.5), "m2": (30.6, 3.0),
        "mf": (63.1, 3.3), "chif": (0.69, 0.05),
        "source": "GWTC-1 (approx.); first area-law test: Isi et al., PRL 127, 011103 (2021)",
    },
    "GW190521": {
        "m1": (85.0, 17.0), "m2": (66.0, 17.0),
        "mf": (142.0, 16.0), "chif": (0.72, 0.09),
        "source": "LVK PRL 125, 101102 (2020) (approx.)",
    },
    "GW190814": {
        "m1": (23.2, 1.1), "m2": (2.59, 0.08),
        "mf": (25.6, 1.0), "chif": (0.28, 0.02),
        "source": "LVK ApJL 896, L44 (2020) (approx.)",
    },
    "GW250114": {
        "m1": (34.0, 1.5), "m2": (32.0, 1.5),
        "mf": (63.0, 1.5), "chif": (0.68, 0.02),
        "source": "LVK PRL 135, 111403 (2025) (approx. -- VERIFY; ringdown-based "
                  "final state available in official data release)",
    },
}
