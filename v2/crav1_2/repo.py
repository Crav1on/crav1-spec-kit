"""Project commands: init, append, show-state, rebuild-views."""

from __future__ import annotations

import json
from pathlib import Path

from crav1_2.errors import EngineError, SchemaError
from crav1_2.events import dump_event, load_jsonl
from crav1_2.fold import fold_events
from crav1_2.paths import GITATTRIBUTES, guarded_append, guarded_write, locate
from crav1_2.schema import validate_event
from crav1_2.sessions import write_session
from crav1_2.version import ENGINE, SCHEMA
from crav1_2.views import view_files

EVENTS = ".crav1-2/events.jsonl"
ATTR = ".crav1-2/.gitattributes"
ENGINE_JSON = ".crav1-2/engine.json"


def engine_payload() -> bytes:
    body = {"engine": ENGINE, "schema": SCHEMA}
    return (json.dumps(body, indent=2) + "\n").encode("utf-8")


def require_init(repo: Path) -> None:
    if not (repo / ".crav1-2" / "engine.json").is_file():
        raise EngineError("Refused: run init first.")


def init_repo(repo: Path) -> dict:
    locate(repo, EVENTS)
    locate(repo, ATTR)
    locate(repo, ENGINE_JSON)
    events = repo / ".crav1-2" / "events.jsonl"
    events.parent.mkdir(parents=True, exist_ok=True)
    if not events.exists():
        events.write_bytes(b"")
    (repo / ".crav1-2" / "sessions").mkdir(parents=True, exist_ok=True)
    guarded_write(repo, ATTR, GITATTRIBUTES)
    guarded_write(repo, ENGINE_JSON, engine_payload())
    return {"initialized": True, "engine": ENGINE, "schema": SCHEMA}


def read_events(repo: Path) -> list[dict]:
    path = repo / ".crav1-2" / "events.jsonl"
    if not path.exists():
        return []
    locate(repo, EVENTS)
    return load_jsonl(path.read_text(encoding="utf-8"))


def append_events(repo: Path, raw_events: list[dict]) -> dict:
    require_init(repo)
    if not raw_events:
        raise SchemaError("Refused: append needs at least one event.")
    normalized = [validate_event(event) for event in raw_events]
    seen = {event["id"] for event in read_events(repo)}
    for event in normalized:
        if event["id"] in seen:
            raise SchemaError(f"Refused: duplicate id {event['id']}.")
        seen.add(event["id"])
    blob = "".join(dump_event(event) + "\n" for event in normalized).encode("utf-8")
    guarded_append(repo, EVENTS, blob)
    guarded_write(repo, ENGINE_JSON, engine_payload())
    return {"appended": len(normalized)}


def show_state(repo: Path) -> dict:
    require_init(repo)
    return fold_events(read_events(repo))


def record_session(repo: Path, session_id: str, status: str) -> dict:
    require_init(repo)
    body = write_session(repo, session_id, status)
    guarded_write(repo, ENGINE_JSON, engine_payload())
    return body


def rebuild_views(repo: Path) -> dict:
    require_init(repo)
    files = view_files(show_state(repo))
    for rel, text in files.items():
        guarded_write(repo, rel, text.encode("utf-8"))
    guarded_write(repo, ENGINE_JSON, engine_payload())
    return {"wrote": list(files)}
