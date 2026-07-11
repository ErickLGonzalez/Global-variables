# Posterior sample data (REAL mode)

HDF5 posterior files are **not committed** (size). Download locally into this directory:

| Event | Local name | Source |
|---|---|---|
| GW250114 | `GW250114_posterior.h5` | [Zenodo 16877102](https://zenodo.org/records/16877102) — `posterior_samples_NRSur7dq4.h5` |
| GW150914 | `GW150914_posterior.h5` | [Zenodo 6513631](https://zenodo.org/records/6513631) — `IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_cosmo.h5` |

Then:

```bash
python scripts/run_b4_real.py
```
