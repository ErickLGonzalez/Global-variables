#!/usr/bin/env python3
"""Build the self-contained PIR Workbench page (P9 presentation layer).

Read-only, stdlib-only. Reads the exported view bundle
(``build/pir_view/bundle.json``, produced by ``ci/export_pir_view.py``) and
inlines it into ``pir_workbench/template.html``, writing a single self-contained
HTML file with no external requests. Writes nothing to the committed tree except
the file you point ``--out`` at (default is the gitignored build dir).

    python3 ci/export_pir_view.py          # (re)generate the bundle
    python3 pir_workbench/build.py          # -> build/pir_view/workbench.html

The workbench never writes a fact, verdict, or certificate; it only renders the
JSON the substrate already emitted.
"""

from __future__ import annotations

import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "pir_workbench", "template.html")
DEFAULT_BUNDLE = os.path.join(ROOT, "build", "pir_view", "bundle.json")
DEFAULT_OUT = os.path.join(ROOT, "build", "pir_view", "workbench.html")

PLACEHOLDER = "/*__PIR_BUNDLE__*/"


def inline_bundle(template: str, bundle_text: str) -> str:
    """Inject the bundle JSON into the template's data island.

    The JSON is embedded inside a ``<script type="application/json">`` element;
    the only breakout risk is a literal ``</script`` (or ``</`` generally), which
    JSON never emits, but we neutralize it defensively so the page can never be
    broken by future data."""
    if PLACEHOLDER not in template:
        raise ValueError("template is missing the %s placeholder" % PLACEHOLDER)
    safe = bundle_text.replace("</", "<\\/")
    return template.replace(PLACEHOLDER, safe)


def extract_body(html: str) -> str:
    """Return the inner content of <body>…</body> (an Artifact-ready fragment).

    The claude.ai Artifact wrapper supplies its own doctype/head/body, so a page
    published as an Artifact must be body content only — style and script tags
    live inside the body in the template precisely so this fragment is valid."""
    lo = html.find("<body>")
    hi = html.rfind("</body>")
    if lo < 0 or hi < 0:
        raise ValueError("template has no <body>…</body>")
    return html[lo + len("<body>"):hi].strip() + "\n"


def build(bundle_path: str = DEFAULT_BUNDLE, template_path: str = TEMPLATE) -> str:
    with open(template_path, "r", encoding="utf-8") as fh:
        template = fh.read()
    with open(bundle_path, "r", encoding="utf-8") as fh:
        bundle_text = fh.read()
    json.loads(bundle_text)  # fail loudly on a malformed bundle
    return inline_bundle(template, bundle_text)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build the PIR Workbench page.")
    ap.add_argument("--bundle", default=DEFAULT_BUNDLE, help="path to bundle.json")
    ap.add_argument("--out", default=DEFAULT_OUT, help="output HTML path")
    ap.add_argument("--artifact", metavar="PATH",
                    help="also write a body-only fragment for publishing as an Artifact")
    args = ap.parse_args(argv)

    if not os.path.exists(args.bundle):
        print("bundle not found: %s\n  run: python3 ci/export_pir_view.py" % args.bundle)
        return 2

    html = build(args.bundle)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("PIR Workbench written: %s (%d bytes)" % (args.out, len(html)))

    if args.artifact:
        frag = extract_body(html)
        os.makedirs(os.path.dirname(os.path.abspath(args.artifact)), exist_ok=True)
        with open(args.artifact, "w", encoding="utf-8") as fh:
            fh.write(frag)
        print("Artifact fragment written: %s (%d bytes)" % (args.artifact, len(frag)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
