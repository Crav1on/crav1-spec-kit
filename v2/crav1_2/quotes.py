"""Check this-session quotes against a vendor session file, when one exists.

Cursor keeps chats in its own store, so a Cursor run is never checked.
Claude Code files live under ~/.claude/projects/<encoded-repo>/*.jsonl.
Codex files live under ~/.codex/sessions and ~/.codex/archived_sessions.
"""

from __future__ import annotations

import re
from pathlib import Path

_MAX_BYTES = 20_000_000


def annotate_quotes(
    passages: list[dict],
    *,
    vendor: str,
    repo: Path,
    home: Path,
    session_file: str | None,
) -> tuple[str, list[dict]]:
    """Return ``checked`` or ``unchecked``, and passages with ``verified`` set when checked."""
    copied = [dict(passage) for passage in passages]
    if vendor == "cursor":
        return "unchecked", [_weak(passage) for passage in copied]
    files = _files(vendor, repo, home, session_file)
    if not files:
        return "unchecked", [_weak(passage) for passage in copied]
    text = _collapse("\n".join(_read(path) for path in files))
    checked = []
    for passage in copied:
        quote = passage.get("quote") or ""
        passage["verified"] = bool(quote) and _collapse(quote) in text
        checked.append(_weak(passage))
    return "checked", checked


def _weak(passage: dict) -> dict:
    who = str(passage.get("who") or "").strip().lower()
    if who == "assistant" and passage.get("verified") is not True:
        passage["weak"] = "ai-summary"
    return passage


def _files(vendor: str, repo: Path, home: Path, session_file: str | None) -> list[Path]:
    if session_file:
        path = Path(session_file)
        if not path.is_file():
            from crav1_2.errors import EngineError

            raise EngineError("Refused: the session file does not exist.")
        return [path]
    if vendor == "claude":
        return _claude(home, repo)
    if vendor == "codex":
        return _codex(home, repo)
    return []


def _claude(home: Path, repo: Path) -> list[Path]:
    root = home / ".claude" / "projects"
    if not root.is_dir():
        return []
    encoded = repo.resolve().as_posix().replace("/", "-")
    return [path for path in sorted(root.glob("*/*.jsonl")) if path.parent.name == encoded and _small(path)]


def _codex(home: Path, repo: Path) -> list[Path]:
    needle = repo.resolve().as_posix()
    found = []
    for folder in (home / ".codex" / "sessions", home / ".codex" / "archived_sessions"):
        if not folder.is_dir():
            continue
        for path in sorted(folder.rglob("*.jsonl")):
            if _small(path) and needle in _read(path):
                found.append(path)
    return found


def _small(path: Path) -> bool:
    try:
        return path.is_file() and path.stat().st_size <= _MAX_BYTES
    except OSError:
        return False


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text)
