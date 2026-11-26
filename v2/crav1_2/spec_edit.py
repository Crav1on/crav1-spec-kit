"""Insert crav1-2 item lines into a shared 1.x spec, plan, or tasks file.

A new line carries ``crav1-2:item``. Full source under that bullet is owned
with it. Every other line is copied unchanged, including its bytes.
"""

from __future__ import annotations

import re

from crav1_2.errors import EngineError

_COMMENT = re.compile(r"<!--.*?-->")
_TAG = re.compile(r"\[(src|dec|asm):[^\]]*\]")
_TASK = re.compile(r"^- \[[ xX]\] (T\d+)\b")


def origin_tag(origin: str, refs: list[str], weak: str | None) -> str:
    body = ", ".join(refs)
    if weak and origin == "src":
        body = f"{body} {weak}"
    return f"[{origin}: {body}]"


def item_comment(item: str) -> str:
    return f"<!-- crav1-2:item {item} -->"


def sort_key(text: str) -> str:
    cleaned = _TAG.sub("", _COMMENT.sub("", text or ""))
    return re.sub(r"\s+", " ", cleaned).strip().casefold()


def bullet_block(text: str, origin: str, refs: list[str], weak: str | None, item: str, *, blocks: str | None, anchor: str) -> list[str]:
    """A new top-level bullet, its Full source line, and an optional Blocks mark."""
    lines = [f"- {text} {origin_tag(origin, refs, weak)} {item_comment(item)}"]
    lines.append(f"  Full source: {anchor}")
    if blocks is not None:
        lines.append(f"  - Blocks: {blocks} {item_comment(item)}")
    return lines


def answered_block(sentence: str, origin: str, refs: list[str], weak: str | None, item: str, anchor: str) -> list[str]:
    return [
        f"  - {sentence} {origin_tag(origin, refs, weak)} {item_comment(item)}",
        f"    Full source: {anchor}",
    ]


def see_also_line(anchor: str, origin: str, refs: list[str], weak: str | None, item: str) -> str:
    return f"  See also: {anchor} {origin_tag(origin, refs, weak)} {item_comment(item)}"


def waits_line(decision: str, item: str) -> str:
    return f"  Waits on: {decision} {item_comment(item)}"


def anchor_for(ref: str) -> str:
    if ref.startswith("D-"):
        return f"sot/decisions.md#{ref}"
    if ref.startswith("A-"):
        return f"sot/assumptions.md#{ref}"
    return f"sot/facts.md#{ref}"


def insert_sorted(text: str, section: str, block: list[str], key: str) -> str:
    lines, ended = _split(text)
    span = _section_span(lines, section)
    if span is None:
        raise EngineError(f"Refused: the spec has no section {section}.")
    start, end = span
    place = end
    for begin, _stop, existing in _bullets(lines, start, end):
        if existing > key:
            place = begin
            break
    lines[place:place] = block
    return _join(lines, ended)


def insert_under_question(text: str, question: str, extra: list[str]) -> str:
    lines, ended = _split(text)
    span = _section_span(lines, "Open questions")
    if span is None:
        raise EngineError("Refused: the spec has no section Open questions.")
    start, end = span
    wanted = sort_key(question)
    for begin, stop, existing in _bullets(lines, start, end):
        if existing == wanted:
            lines[stop:stop] = extra
            return _join(lines, ended)
    raise EngineError("Refused: that open question is not in the spec.")


def insert_waits(text: str, task: str, line: str) -> str | None:
    """Put a Waits on line under an existing task. None when the task is absent."""
    lines, ended = _split(text)
    for index, row in enumerate(lines):
        match = _TASK.match(row)
        if not match or match.group(1) != task:
            continue
        stop = index + 1
        while stop < len(lines) and not _TASK.match(lines[stop]) and not lines[stop].startswith("## "):
            if lines[stop].startswith("- ") and not lines[stop].startswith("  "):
                break
            stop += 1
        lines[stop:stop] = [line]
        return _join(lines, ended)
    return None


def _split(text: str) -> tuple[list[str], bool]:
    norm = text.replace("\r\n", "\n").replace("\r", "\n")
    ended = norm.endswith("\n") or norm == ""
    parts = norm.split("\n")
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return parts, ended


def _join(lines: list[str], ended: bool) -> str:
    body = "\n".join(lines)
    if ended:
        body += "\n"
    return body


def _section_span(lines: list[str], section: str) -> tuple[int, int] | None:
    want = f"## {section}".strip()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == want:
            start = index
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return start, end


def _bullets(lines: list[str], start: int, end: int) -> list[tuple[int, int, str]]:
    found = []
    index = start + 1
    while index < end:
        line = lines[index]
        if line.startswith("- ") and not line.startswith("  "):
            begin = index
            key = sort_key(line[2:])
            index += 1
            while index < end and not (lines[index].startswith("- ") and not lines[index].startswith("  ")):
                if lines[index].startswith("## "):
                    break
                index += 1
            found.append((begin, index, key))
            continue
        index += 1
    return found
