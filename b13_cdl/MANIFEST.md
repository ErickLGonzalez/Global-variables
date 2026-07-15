# B13-CDL v0.1 — Manifest
docs/survey-v1.1-addendum.md · docs/B13-CDL-design.md · docs/pir-bridge-v0.1.md
schemas/cdl_entry.schema.json · schemas/cdl_certificate.schema.json
data/ledger.json (25 entries) · data/falsifiers.json (15 falsifiers)
src/cdl/{common,ew_vacuum,strong_cp,varying_constants,grh_miller,tunnell_bsd,muon_g2,h0_tension,coverage,pir_bridge}.py
tests/test_b13.py · certificates/ (8 stable-named pipeline certs + pir_facts.json)
Identity: certificate_id = content hash; stable filenames; reruns reproducible.
Under repo CI: ci/run_all_certified.py reruns test_b13.py and diffs certificates.
Verification: `python3 tests/test_b13.py` → PASS expected, exit 0.
