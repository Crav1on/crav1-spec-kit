"""Shared fixtures for the kit 2.0 engine tests."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

V2 = Path(__file__).resolve().parents[1]
REPO = V2.parent
if str(V2) not in sys.path:
    sys.path.insert(0, str(V2))

from crav1_2.ulid import encode  # noqa: E402


def ulid_n(n: int) -> str:
    return encode(1_700_000_000_000 + n, n + 1)


def temp_dir() -> Path:
    return Path(tempfile.mkdtemp())


def remove(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)


def note_event(n: int = 1, **data_over) -> dict:
    passage = {
        "id": "p-001",
        "kind": "chat",
        "who": "person A",
        "when": "09:12",
        "quote": "Agreed long term, likely before go-live, not in this slice.",
    }
    data = {
        "note": "2026-11-25-outbound-channel",
        "kinds": ["session", "chat"],
        "date": "2026-11-25",
        "files": ["note.md"],
        "from_sources": None,
        "passages": 1,
        "title": "Outbound messaging channel",
        "added_by": "person A",
        "passage_list": [passage],
    }
    data.update(data_over)
    if "passage_list" in data and data["passage_list"] is not None:
        data["passages"] = len(data["passage_list"])
    return {
        "v": 1,
        "id": ulid_n(n),
        "at": "2026-11-25T11:41:00+01:00",
        "by": "engine",
        "run": "s-0007",
        "type": "note.added",
        "data": data,
    }


def fact_event(n: int = 2, **data_over) -> dict:
    data = {
        "fact": "F-0031",
        "note": "2026-11-25-outbound-channel",
        "passage": "p-001",
        "quote": "Agreed long term, likely before go-live, not in this slice.",
        "weak": "verbal",
    }
    data.update(data_over)
    return {
        "v": 1,
        "id": ulid_n(n),
        "at": "2026-11-25T12:02:10+01:00",
        "by": "crav1-2-gap-finder-agent",
        "run": "s-0008",
        "type": "fact.cited",
        "data": data,
    }
