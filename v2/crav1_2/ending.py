"""Run endings. Run next comes first. At most one Also recorded line. No Next: line."""

from __future__ import annotations

import re
from pathlib import Path

from crav1_2.errors import EngineError
from crav1_2.schema import SPEC_SLUG

# 1.x has no session or document word. session is a chat; a document is a dump.
_ONE_X = {
    "mail": "mail",
    "chat": "chat",
    "meeting": "meeting",
    "fact": "fact",
    "document": "dump",
    "session": "chat",
}
_LIST_CAP = 6


def render_ending(specs: list[str], note_id: str | None, follow: list[str] | None = None) -> str:
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
    elif follow:
        lines = ["Run next:", *follow]
    else:
        lines = ["Run next: nothing needed now."]
    if note_id:
        lines.extend(["", f"Also recorded: note {note_id}."])
    text = "\n".join(lines) + "\n"
    _check(text)
    return text


def capture_follow(
    repo: Path,
    *,
    kinds: list[str],
    title: str,
    source: str | None,
    passages: list[dict],
) -> list[str]:
    """The matching 1.x command for this source. Suggest only. The caller does not run it.

    One spec in the project is clear. Otherwise a spec slug that the title, the
    file, or a quote names is clear. Anything else stays ``<spec-slug>`` and a
    short question asks the user to pick.
    """
    word = _one_x_word(kinds)
    slugs = project_specs(repo)
    picked = clear_spec(slugs, title=title, source=source, passages=passages)
    lines = [_command(word, picked, source)]
    if picked is None:
        lines.extend(["", _question(word, slugs)])
    return lines


def project_specs(repo: Path) -> list[str]:
    root = repo / "docs" / "specs"
    if not root.is_dir():
        return []
    found = []
    for path in sorted(root.glob("*/spec.md")):
        slug = path.parent.name
        if SPEC_SLUG.fullmatch(slug) and path.is_file():
            found.append(slug)
    return found


def clear_spec(slugs: list[str], *, title: str, source: str | None, passages: list[dict]) -> str | None:
    if len(slugs) == 1:
        return slugs[0]
    if not slugs:
        return None
    quotes = " ".join(str(item.get("quote") or "") for item in passages)
    blob = " ".join(part for part in (title, source or "", quotes) if part)
    hits = [
        slug
        for slug in slugs
        if re.search(rf"(?<![A-Za-z0-9-]){re.escape(slug)}(?![A-Za-z0-9-])", blob)
    ]
    if len(hits) == 1:
        return hits[0]
    return None


def _one_x_word(kinds: list[str]) -> str:
    for kind in kinds:
        mapped = _ONE_X.get(kind)
        if mapped:
            return mapped
    return "dump"


def _command(word: str, slug: str | None, source: str | None) -> str:
    shown = slug or "<spec-slug>"
    if source:
        safe = source.replace('"', "'")
        return f'`/crav1-add-to-spec {shown} {word} "{safe}"`'
    return f"`/crav1-add-to-spec {shown} {word}`"


def _question(word: str, slugs: list[str]) -> str:
    if slugs and len(slugs) <= _LIST_CAP:
        return f"Which spec should this {word} go into? Pick one: {', '.join(slugs)}."
    return "Which spec should this go into? Name the spec slug in place of <spec-slug>."


def render_settled(recorded: str | None) -> str:
    """The link-to-spec ending. Run next first. At most one Also recorded line."""
    lines = ["Run next: nothing needed now."]
    if recorded:
        lines.extend(["", f"Also recorded: {recorded}."])
    text = "\n".join(lines) + "\n"
    _check(text)
    return text


def render_covered() -> str:
    """Every finder item is covered and there is no card. Same sentence in dry-run."""
    text = "Run next: nothing needed; the spec already covers this note.\n"
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
