"""Byte check for a shared 1.x spec, plan, or tasks file.

Lines kit 2.0 owns carry ``crav1-2:item``. A bullet that carries the comment
also owns the indented Full source, Blocks, See also, and Waits on lines under
it. Every other line must match the previous bytes, apart from CRLF versus LF.
"""

from __future__ import annotations

import re

_MARK = re.compile(r"\*\*New:\*\*|(?:^|[ \t])Trace:|(?:^|[ \t])Synced at\b")
_CONTINUATION = ("Full source:", "Blocks:", "See also:", "Waits on:")


def _normalized(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _lines(text: str) -> tuple[list[str], bool]:
    norm = _normalized(text)
    ended = norm.endswith("\n")
    parts = norm.split("\n")
    if ended:
        parts = parts[:-1]
    return parts, ended


def owned_indexes(lines: list[str]) -> set[int]:
    owned: set[int] = set()
    i = 0
    while i < len(lines):
        line = lines[i]
        if "crav1-2:item" not in line:
            i += 1
            continue
        owned.add(i)
        stripped = line.lstrip(" ")
        is_bullet = stripped.startswith("- ") or stripped.startswith("* ")
        if not is_bullet:
            i += 1
            continue
        base = len(line) - len(stripped)
        j = i + 1
        while j < len(lines):
            nxt = lines[j]
            if nxt.strip() == "":
                break
            body = nxt.lstrip(" ")
            indent = len(nxt) - len(body)
            if indent > base and body.startswith(_CONTINUATION):
                owned.add(j)
                j += 1
                continue
            break
        i = j
    return owned


def strip_owned(text: str) -> str:
    lines, ended = _lines(text)
    kept = [line for i, line in enumerate(lines) if i not in owned_indexes(lines)]
    if not kept:
        return ""
    body = "\n".join(kept)
    if ended:
        body += "\n"
    return body


def one_x_lines_unchanged(before: str, after: str) -> bool:
    """True when every line 2.0 does not own is unchanged."""
    return strip_owned(before) == strip_owned(after)


def line_has_mark(line: str) -> bool:
    """A 1.x bookkeeping mark. 2.0 does not write these."""
    return _MARK.search(line) is not None


def owned_mark_lines(text: str) -> list[str]:
    lines, _ended = _lines(text)
    return [lines[i] for i in sorted(owned_indexes(lines)) if line_has_mark(lines[i])]
