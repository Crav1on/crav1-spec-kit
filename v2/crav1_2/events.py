"""Read and write events.jsonl lines. Append-only; one JSON object per line."""

from __future__ import annotations

import json

from crav1_2.errors import SchemaError
from crav1_2.schema import DATA_KEYS, validate_event


def dump_event(event: dict) -> str:
    """One canonical line, UTF-8, keys in schema order, no ASCII escaping."""
    cleaned = validate_event(event)
    return json.dumps(cleaned, ensure_ascii=False, separators=(",", ":"))


def load_jsonl(text: str) -> list[dict]:
    if text.startswith("\ufeff"):
        raise SchemaError("Refused: events.jsonl must be UTF-8 without a BOM.")
    events = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SchemaError(f"Refused: line {lineno}: not a JSON object ({exc.msg}).") from exc
        events.append(validate_event(raw, line=lineno))
    return events


def canonical(event: dict) -> str:
    """Order-independent identity of one event, used to drop exact duplicates."""
    return json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def event_types() -> tuple[str, ...]:
    return tuple(DATA_KEYS)
