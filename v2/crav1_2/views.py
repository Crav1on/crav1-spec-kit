"""Generated sot/ pages. A pure function of the fold: no clocks, no edit-in-place."""

from __future__ import annotations

import re

from crav1_2.notes import render_note

BANNER = "Generated from the event log. Do not edit."
DECISION_BANNER = "Generated from the event log. Do not edit. Entries are never edited, only superseded."


def _num(value: str) -> tuple[int, str]:
    match = re.search(r"(\d+)$", value or "")
    return (int(match.group(1)) if match else 0, value or "")


def _finish(lines: list[str]) -> str:
    text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    return text


def render_index(state: dict) -> str:
    notes = list(state["notes"].values())
    notes.sort(key=lambda note: note["note"])
    notes.sort(key=lambda note: note["date"], reverse=True)
    lines = ["# SoT index", "", BANNER, ""]
    if not notes:
        lines.append("(none)")
        return _finish(lines)
    for note in notes:
        kinds = ", ".join(note.get("kinds") or [])
        lines.append(
            f"- {note['date']} · [{note['note']}]({note['note']}/note.md) · {kinds} · {note['passages']} passages"
        )
    return _finish(lines)


def render_facts(state: dict) -> str:
    facts = sorted(state["facts"].values(), key=lambda fact: _num(fact["fact"]))
    lines = ["# Facts", "", BANNER, ""]
    if not facts:
        lines.append("(none)")
        return _finish(lines)
    blocks = []
    for fact in facts:
        fid = fact["fact"]
        target = f"sot/{fact['note']}/note.md#{fact['passage']}"
        relative = f"{fact['note']}/note.md#{fact['passage']}"
        weak = f" · {fact['weak']}" if fact.get("weak") else ""
        blocks.append(
            f'<a id="{fid}"></a>\n**{fid}** → [{target}]({relative}) "{fact["quote"]}"{weak}'
        )
    lines.append("\n\n".join(blocks))
    return _finish(lines)


def render_decisions(state: dict) -> str:
    decisions = sorted(state["decisions"].values(), key=lambda item: _num(item["decision"]))
    lines = ["# Decisions", "", DECISION_BANNER, ""]
    if not decisions:
        lines.append("(none)")
        return _finish(lines)
    blocks = []
    for decision in decisions:
        did = decision["decision"]
        if decision.get("missing"):
            blocks.append(f'<a id="{did}"></a>\n**{did}** · superseded by {decision.get("superseded_by")}')
            continue
        over = ", ".join(decision.get("over") or [])
        body = [
            f'<a id="{did}"></a>',
            f"**{did}** · {decision.get('at', '')} · chosen {decision.get('chosen', '')} · over {over}",
            f"Accepting: {decision.get('accepting', '')}",
            "Facts: " + ", ".join(decision.get("facts") or []),
            "Affects: " + ", ".join(decision.get("affects") or []),
            f"Check: {decision.get('check', '')}",
            f"Card: {decision.get('card', '')}",
        ]
        if decision.get("superseded_by"):
            body.append(f"Superseded by {decision['superseded_by']}")
        blocks.append("\n".join(body))
    lines.append("\n\n".join(blocks))
    return _finish(lines)


def render_assumptions(state: dict) -> str:
    rows = sorted(state["assumptions"].values(), key=lambda item: _num(item["assumption"]))
    open_rows = [row for row in rows if not row.get("closed_by")]
    closed_rows = [row for row in rows if row.get("closed_by")]
    lines = ["# Assumptions", "", BANNER, "", "## Open", ""]
    lines.append(_assumption_block(open_rows, closed=False))
    lines.extend(["", "## Closed", ""])
    lines.append(_assumption_block(closed_rows, closed=True))
    return _finish(lines)


def _assumption_block(rows: list[dict], *, closed: bool) -> str:
    if not rows:
        return "(none)"
    blocks = []
    for row in rows:
        aid = row["assumption"]
        if row.get("missing"):
            extra = f" · closed by {row.get('closed_by')}" if closed else ""
            blocks.append(f'<a id="{aid}"></a>\n**{aid}**{extra}')
            continue
        head = f'<a id="{aid}"></a>\n**{aid}** · gap {row.get("gap", "")}'
        if closed:
            head += f" · closed by {row.get('closed_by')}"
        body = [
            head,
            row.get("text", ""),
            f"Owner: {row.get('owner', '')}",
            f"Confirms if: {row.get('confirms_if', '')}",
            f"Breaks if: {row.get('breaks_if', '')}",
        ]
        blocks.append("\n".join(body))
    return "\n\n".join(blocks)


def view_files(state: dict) -> dict[str, str]:
    """Repo-relative path to UTF-8 text, each ending in one LF."""
    files = {
        "sot/index.md": render_index(state),
        "sot/facts.md": render_facts(state),
        "sot/decisions.md": render_decisions(state),
        "sot/assumptions.md": render_assumptions(state),
    }
    for note_id in sorted(state["notes"]):
        files[f"sot/{note_id}/note.md"] = render_note(state["notes"][note_id])
    return files
