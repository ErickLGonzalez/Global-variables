"""A tiny, dependency-free JSON-Schema validator.

Supports exactly the Draft 2020-12 constructs the six PIR schemas use:
``type`` (incl. a list of types), ``enum``, ``const``, ``required``,
``properties``, ``additionalProperties`` (bool), ``items``, ``minimum`` /
``maximum``. Unknown keywords (``$schema``, ``$id``, ``title``,
``description``, ``format``) are ignored, matching lenient validator behavior.

Rationale (ADR-PIR-0001): the substrate and its CI must run on a clean
checkout with **stdlib only**. When the real ``jsonschema`` package is
installed the test suite cross-checks against it, but correctness never
depends on it. Keeping this small and auditable is the point.
"""

from __future__ import annotations

from typing import Any, List

_TYPE_CHECKS = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


class SchemaError(Exception):
    """Raised with the JSON-path of the first constraint that fails."""


def _err(path: str, msg: str) -> None:
    raise SchemaError(f"{path or '<root>'}: {msg}")


def _check_type(schema_type, value, path):
    types = schema_type if isinstance(schema_type, list) else [schema_type]
    if not any(_TYPE_CHECKS.get(t, lambda v: True)(value) for t in types):
        _err(path, f"expected type {schema_type}, got {type(value).__name__}")


def _validate(schema: Any, value: Any, path: str) -> None:
    if not isinstance(schema, dict):
        return

    if "const" in schema and value != schema["const"]:
        _err(path, f"expected const {schema['const']!r}, got {value!r}")

    if "enum" in schema and value not in schema["enum"]:
        _err(path, f"{value!r} not in enum {schema['enum']}")

    if "type" in schema:
        _check_type(schema["type"], value, path)

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            _err(path, f"{value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            _err(path, f"{value} > maximum {schema['maximum']}")

    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                _err(path, f"missing required property {req!r}")
        props = schema.get("properties", {})
        add = schema.get("additionalProperties", True)
        for key, sub in value.items():
            if key in props:
                _validate(props[key], sub, f"{path}.{key}" if path else key)
            elif add is False:
                _err(path, f"additional property {key!r} not allowed")

    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            _validate(schema["items"], item, f"{path}[{i}]")


def validate(schema: dict, instance: Any) -> None:
    """Raise :class:`SchemaError` on the first violation; return None if valid."""
    _validate(schema, instance, "")


def iter_errors(schema: dict, instance: Any) -> List[str]:
    """Convenience: return a list with the first error message, or empty."""
    try:
        validate(schema, instance)
        return []
    except SchemaError as exc:
        return [str(exc)]
