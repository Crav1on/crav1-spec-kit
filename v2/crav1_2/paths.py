"""Writes stay inside the phase-1 path list.

Allowed: the event log, its merge rule, engine.json, session files, the four
generated sot/ pages, originals under sot/<YYYY-MM-DD-slug>/, and a 2.0 item
edit of an existing docs/specs/<slug>/{spec,plan,tasks}.md.

Refused: .crav1/, .cursor/, .claude/, docs/notes/, docs/sources/, docs/system/,
the repo-root .gitattributes, any other path, a path that escapes the project,
a 1.x mark, and a change to a 1.x line.
"""

from __future__ import annotations

import os
import re

from crav1_2.errors import PathGuardError
from crav1_2.lines import line_has_mark, one_x_lines_unchanged, owned_mark_lines

GITATTRIBUTES = b"events.jsonl merge=union\n"
EXACT = {
    ".crav1-2/events.jsonl",
    ".crav1-2/.gitattributes",
    ".crav1-2/engine.json",
    "sot/index.md",
    "sot/facts.md",
    "sot/decisions.md",
    "sot/assumptions.md",
}
NOTE_SLUG = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
SPEC_FILE = re.compile(r"^docs/specs/([a-z0-9]+(?:-[a-z0-9]+)*)/(spec|plan|tasks)\.md$")
SESSION_FILE = re.compile(r"^\.crav1-2/sessions/(s-\d{4,})\.json$")


def normalize_rel(rel: str) -> str:
    if not isinstance(rel, str) or rel.strip() == "":
        raise PathGuardError("Refused: empty path.")
    text = rel.replace("\\", "/").strip()
    if text.startswith("/") or (len(text) >= 2 and text[1] == ":"):
        raise PathGuardError(f"Refused: {rel} is outside the project.")
    parts = []
    for part in text.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            raise PathGuardError(f"Refused: {rel} is outside the project.")
        parts.append(part)
    if not parts:
        raise PathGuardError("Refused: empty path.")
    return "/".join(parts)


def _forbidden(rel: str) -> bool:
    if rel in {".gitattributes", ".crav1", ".cursor", ".claude", "docs/notes", "docs/sources", "docs/system"}:
        return True
    prefixes = (".crav1/", ".cursor/", ".claude/", "docs/notes/", "docs/sources/", "docs/system/")
    return rel.startswith(prefixes)


def classify(rel: str) -> str:
    rel = normalize_rel(rel)
    if rel in EXACT:
        return rel
    if SESSION_FILE.fullmatch(rel):
        return "session"
    if rel.startswith(".crav1-2/"):
        raise PathGuardError(f"Refused: {rel} is not a kit 2.0 path.")
    if _forbidden(rel):
        raise PathGuardError(f"Refused: {rel} is not a kit 2.0 path.")
    if rel.startswith("sot/"):
        rest = rel[len("sot/") :]
        slug, sep, tail = rest.partition("/")
        if sep and NOTE_SLUG.fullmatch(slug) and tail and not tail.endswith("/"):
            return "note"
        raise PathGuardError(f"Refused: {rel} is outside the paths kit 2.0 writes.")
    if SPEC_FILE.fullmatch(rel):
        return "spec"
    raise PathGuardError(f"Refused: {rel} is outside the paths kit 2.0 writes.")


def locate(repo, rel: str):
    """Return (normalized relative path, absolute path inside repo)."""
    if not repo.is_dir():
        raise PathGuardError("Refused: the project directory does not exist.")
    rel = normalize_rel(rel)
    classify(rel)
    root = repo.resolve()
    current = root
    for part in rel.split("/"):
        current = current / part
        if current.is_symlink():
            resolved = current.resolve()
            if resolved != root and root not in resolved.parents:
                raise PathGuardError(f"Refused: {rel} is outside the project.")
    destination = (root / rel).resolve()
    if destination != root and root not in destination.parents:
        raise PathGuardError(f"Refused: {rel} is outside the project.")
    return rel, destination


def _marks(text: str, rel: str) -> None:
    for line in text.splitlines():
        if line_has_mark(line):
            raise PathGuardError(f"Refused: {rel} would write a 1.x mark.")


def atomic_write(path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_bytes(data)
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


def guarded_write(repo, rel: str, data: bytes) -> None:
    rel, path = locate(repo, rel)
    if rel == ".crav1-2/events.jsonl":
        raise PathGuardError("Refused: events.jsonl is append-only.")
    kind = classify(rel)
    # Originals under a note folder are copied unchanged, including screenshots.
    original = kind == "note" and not rel.endswith("/note.md")
    text = ""
    if not original:
        if b"\x00" in data:
            raise PathGuardError(f"Refused: {rel} is not UTF-8 text.")
        try:
            text = data.decode("utf-8")
        except UnicodeError as exc:
            raise PathGuardError(f"Refused: {rel} is not UTF-8 text.") from exc
    if rel == ".crav1-2/.gitattributes":
        if data != GITATTRIBUTES:
            raise PathGuardError("Refused: .crav1-2/.gitattributes must be the events.jsonl merge rule.")
        if path.exists() and path.read_bytes() != data:
            raise PathGuardError("Refused: .crav1-2/.gitattributes already differs.")
    elif kind == "spec":
        if not path.is_file():
            raise PathGuardError(f"Refused: {rel} is a 1.x file kit 2.0 does not create.")
        old = path.read_text(encoding="utf-8")
        if not one_x_lines_unchanged(old, text):
            raise PathGuardError(f"Refused: {rel} would change a 1.x line.")
        if owned_mark_lines(text):
            raise PathGuardError(f"Refused: {rel} would write a 1.x mark.")
    elif not original:
        _marks(text, rel)
    atomic_write(path, data)


def guarded_append(repo, rel: str, tail: bytes) -> None:
    rel = normalize_rel(rel)
    if rel != ".crav1-2/events.jsonl":
        raise PathGuardError("Refused: only events.jsonl is appended.")
    if not tail or not tail.endswith(b"\n") or b"\x00" in tail:
        raise PathGuardError("Refused: an event line must be UTF-8 and end in a newline.")
    try:
        tail.decode("utf-8")
    except UnicodeError as exc:
        raise PathGuardError("Refused: an event line must be UTF-8.") from exc
    _rel, path = locate(repo, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab") as handle:
        handle.write(tail)
