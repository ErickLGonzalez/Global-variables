"""B13-CDL common machinery: certificate emission + minimal internal schema validation.

Stdlib only by design (blueprint B1 headless-CI pattern: no environment drift).
"""
from __future__ import annotations
import json
import os
import time
import uuid

PKG_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT_DIR = os.path.join(PKG_ROOT, "certificates")
DATA_DIR = os.path.join(PKG_ROOT, "data")
SCHEMA_DIR = os.path.join(PKG_ROOT, "schemas")


def _now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def make_certificate(pipeline, entry_id, soundness_tag, stipulations, inputs,
                     verdict, verdict_detail=None, witness=None, warning=None, notes=""):
    cert = {
        "certificate_id": f"b13cdl-{pipeline}-{uuid.uuid4().hex[:12]}",
        "pipeline": pipeline,
        "entry_id": entry_id,
        "timestamp_utc": _now_utc(),
        "soundness": {"tag": soundness_tag},
        "stipulations": stipulations,
        "inputs": inputs,
        "verdict": verdict,
        "verdict_detail": verdict_detail or {},
        "notes": notes,
    }
    if soundness_tag == "HEURISTIC":
        if not warning:
            raise ValueError("HEURISTIC certificates require a located warning (blueprint A5).")
        cert["soundness"]["warning"] = warning
    if witness is not None:
        cert["witness"] = witness
    return cert


def write_certificate(cert):
    os.makedirs(CERT_DIR, exist_ok=True)
    path = os.path.join(CERT_DIR, f"{cert['certificate_id']}.json")
    with open(path, "w") as f:
        json.dump(cert, f, indent=2)
    return path


# ---- minimal schema validation (subset of JSON Schema, enough for our schemas) ----

def _type_ok(value, t):
    m = {"object": dict, "array": list, "string": str, "boolean": bool,
         "number": (int, float), "integer": int, "null": type(None)}
    if isinstance(t, list):
        return any(_type_ok(value, ti) for ti in t)
    py = m.get(t)
    if py is None:
        return True
    if t == "number" and isinstance(value, bool):
        return False
    return isinstance(value, py)


def validate(instance, schema, path="$"):
    """Return list of error strings (empty = valid). Supports type, required,
    properties, enum, items, minItems, pattern, additionalProperties."""
    errors = []
    t = schema.get("type")
    if t and not _type_ok(instance, t):
        return [f"{path}: expected type {t}, got {type(instance).__name__}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in enum {schema['enum']}")
    if "pattern" in schema and isinstance(instance, str):
        import re
        if not re.match(schema["pattern"], instance):
            errors.append(f"{path}: {instance!r} fails pattern {schema['pattern']}")
    if isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required field '{req}'")
        props = schema.get("properties", {})
        for key, val in instance.items():
            if key in props:
                errors.extend(validate(val, props[key], f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected field '{key}'")
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: fewer than {schema['minItems']} items")
        if "items" in schema:
            for i, item in enumerate(instance):
                errors.extend(validate(item, schema["items"], f"{path}[{i}]"))
    return errors


def load_json(*parts):
    with open(os.path.join(*parts)) as f:
        return json.load(f)
