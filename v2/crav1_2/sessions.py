"""Session files under .crav1-2/sessions/. Status is open, parked, or ended."""

from __future__ import annotations

import json

from crav1_2.errors import EngineError
from crav1_2.paths import guarded_write
from crav1_2.schema import RUN_ID, now_iso, parse_at


def write_session(repo, session_id: str, status: str, step: str = "", left: list | None = None, at: str | None = None, payload: dict | None = None) -> dict:
    if status not in {"open", "parked", "ended"}:
        raise EngineError("Refused: a session is open, parked, or ended.")
    if not isinstance(session_id, str) or not RUN_ID.fullmatch(session_id):
        raise EngineError("Refused: a session id looks like s-0001.")
    if not isinstance(step, str) or "\n" in step:
        raise EngineError("Refused: step must be a single line.")
    cards = list(left or [])
    stamp = at or now_iso()
    parse_at(stamp)
    body = {"id": session_id, "status": status, "step": step, "left": cards, "at": stamp}
    if payload is not None:
        if not isinstance(payload, dict):
            raise EngineError("Refused: a session payload must be an object.")
        body["payload"] = payload
    encoded = (json.dumps(body, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    guarded_write(repo, f".crav1-2/sessions/{session_id}.json", encoded)
    return body
