"""Run endings. Run next comes first. At most one Also recorded line. No Next: line."""

from __future__ import annotations

from crav1_2.errors import EngineError


def render_ending(specs: list[str], note_id: str | None) -> str:
    if specs:
        slug = specs[0]
        extra = ""
        if len(specs) > 1:
            extra = " Matches on " + ", ".join(specs[1:]) + " stay recorded."
        lines = [
            "Run next:",
            f"The note holds an answer on {slug}.{extra}",
            "",
            "Link the answer into the spec:",
            f"`/crav1-2-link-to-spec {slug}`",
        ]
    else:
        lines = ["Run next: nothing needed now."]
    if note_id:
        lines.extend(["", f"Also recorded: note {note_id}."])
    text = "\n".join(lines) + "\n"
    _check(text)
    return text


def render_settled(recorded: str | None) -> str:
    """The link-to-spec ending. Run next first. At most one Also recorded line."""
    lines = ["Run next: nothing needed now."]
    if recorded:
        lines.extend(["", f"Also recorded: {recorded}."])
    text = "\n".join(lines) + "\n"
    _check(text)
    return text


def _check(text: str) -> None:
    if not text.startswith("Run next:"):
        raise EngineError("Refused: the ending must start with Run next.")
    also = 0
    for line in text.splitlines():
        if line.startswith("Next:"):
            raise EngineError("Refused: the ending must not use a Next line.")
        if line.startswith("Also recorded:"):
            also += 1
    if also > 1:
        raise EngineError("Refused: the ending has more than one Also recorded line.")
