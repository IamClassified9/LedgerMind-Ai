from __future__ import annotations

import math
from datetime import date
from typing import Any

from fastapi import HTTPException


def validate_record_values(fields: list[dict[str, Any]], values: dict[str, Any]) -> dict[str, Any]:
    """Validate record data against the editable template field definitions."""
    definitions = {field["key"]: field for field in fields}
    unknown = sorted(set(values) - set(definitions))
    if unknown:
        raise HTTPException(
            status_code=422,
            detail={"message": "Record contains fields not defined by its template.", "fields": unknown},
        )

    normalized = dict(values)
    for key, definition in definitions.items():
        value = normalized.get(key)
        required = bool(definition.get("required", False))
        if value is None or (isinstance(value, str) and not value.strip()):
            if required:
                raise HTTPException(
                    status_code=422,
                    detail={"message": "A required field is missing or empty.", "field": key},
                )
            normalized.pop(key, None)
            continue

        field_type = definition.get("type")
        if field_type == "text":
            if not isinstance(value, str):
                _invalid(key, "must be text")
            normalized[key] = value.strip()
        elif field_type == "select":
            if not isinstance(value, str) or value not in definition.get("options", []):
                _invalid(key, "must match one of the template's allowed options")
        elif field_type == "date":
            if not isinstance(value, str):
                _invalid(key, "must be an ISO date (YYYY-MM-DD)")
            try:
                date.fromisoformat(value)
            except ValueError:
                _invalid(key, "must be a valid ISO date (YYYY-MM-DD)")
        elif field_type in ("money", "number"):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                _invalid(key, "must be a number")
            if not math.isfinite(value):
                _invalid(key, "must be a finite number")
        else:
            # Unknown template field types should fail closed rather than silently
            # accepting data that the application cannot validate.
            _invalid(key, f"uses unsupported template field type {field_type!r}")
    return normalized


def _invalid(key: str, reason: str) -> None:
    raise HTTPException(status_code=422, detail={"message": f"Field {reason}.", "field": key})
