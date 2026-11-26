"""Render sot/<date-slug>/note.md from a folded note."""

from __future__ import annotations

import re


def _num(value: str) -> int:
    match = re.search(r"(\d+)$", value)
    return int(match.group(1)) if match else 0


def render_note(note: dict) -> str:
    title = note.get("title") or note["note"]
    kinds = list(note.get("kinds") or [])
    date = note["date"]
    added_by = note.get("added_by") or "engine"
    files = list(note.get("files") or [])
    source = note.get("from_sources") or None
    lines = [
        f"# {title} ({_and(kinds)}, {date})",
        "",
        f"Kinds: {', '.join(kinds)} · Date: {date} · Added: {date} by {added_by}",
        "Originals: " + (", ".join(files) if files else "none"),
        "From sources: " + (source if source else "none"),
        "",
        "## Passages",
    ]
    passages = sorted(note.get("passage_list") or [], key=lambda item: _num(item["id"]))
    for passage in passages:
        lines.append(_passage(passage))
    know = list(note.get("know") or [])
    if know:
        lines.append("")
        lines.append("## Know about this")
        for block in know:
            inferred = block.get("inferred")
            if inferred is None:
                inferred = not block.get("cites")
            suffix = " · inferred" if inferred else ""
            lines.append(f"### {block['heading']}{suffix}")
            lines.append(block["body"])
    lines.append("")
    return "\n".join(lines)


def _and(kinds: list[str]) -> str:
    if not kinds:
        return "note"
    if len(kinds) == 1:
        return kinds[0]
    return " and ".join(kinds)


def _passage(passage: dict) -> str:
    quote = passage["quote"].replace("\n", " ")
    pid = passage["id"]
    head = f'<a id="{pid}"></a>**{pid}**'
    if passage.get("path"):
        loc = f"`{passage['path']}`"
        if passage.get("lines"):
            loc += f" {passage['lines']}"
        return f'{head} · {loc} · "{quote}"'
    who = passage.get("who") or ""
    when = passage.get("when")
    who_when = f"{who}, {when}" if when else who
    return f'{head} · {passage.get("kind", "")} · {who_when} · "{quote}"'
