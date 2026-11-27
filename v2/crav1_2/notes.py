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
    added = note.get("added") or date
    files = list(note.get("files") or [])
    source = note.get("from_sources") or None
    lines = [
        f"# {title} ({_and(kinds)}, {date})",
        "",
        f"Kinds: {', '.join(kinds)} · Date: {date} · Added: {added} by {added_by}",
        "Originals: " + (", ".join(files) if files else "none"),
        "From sources: " + (source if source else "none"),
    ]
    if note.get("captured_from") == "live-context":
        lines.append("Captured from: live context")
    elif note.get("captured_from"):
        lines.append(f"Captured from: {note['captured_from']}")
    if note.get("vendor"):
        lines.append(f"Vendor: {note['vendor']}")
    if note.get("session_id"):
        lines.append(f"Session: {note['session_id']}")
    if note.get("quotes") == "unchecked":
        lines.append("Quotes: not checked against a file.")
    elif note.get("quotes") == "checked":
        lines.append("Quotes: checked against the session file.")
    if note.get("redactions"):
        lines.append("Redactions: " + ", ".join(note["redactions"]))
    lines.extend(["", "## Passages"])
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
            cites = block.get("cites") or []
            if cites:
                lines.append("Cites: " + ", ".join(f"[{cite}]" for cite in cites))
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
    bits = [head]
    if passage.get("path"):
        loc = f"`{passage['path']}`"
        if passage.get("lines"):
            loc += f" {passage['lines']}"
        bits.append(loc)
    else:
        who = passage.get("who") or ""
        when = passage.get("when")
        bits.append(passage.get("kind", ""))
        bits.append(f"{who}, {when}" if when else who)
    if passage.get("label"):
        bits.append(passage["label"])
    if passage.get("verified") is True:
        bits.append("verified")
    elif passage.get("verified") is False:
        bits.append("unverified")
    if passage.get("weak"):
        bits.append(passage["weak"])
    if passage.get("answers"):
        bits.append(f"answers: {passage['answers']}")
    return " · ".join(bits) + f' · "{quote}"'
