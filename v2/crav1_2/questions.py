"""Match an answer to a spec's open questions by the question's words.

The match is recorded. The question stays open. link-to-spec closes it later.
"""

from __future__ import annotations

import re
from pathlib import Path

from crav1_2.schema import SPEC_SLUG

_STOP = {
    "a", "an", "the", "and", "or", "of", "to", "for", "in", "on", "is", "are",
    "was", "were", "be", "who", "how", "what", "when", "where", "which", "does",
    "do", "did", "will", "with", "from", "that", "this", "into", "not", "can",
    "before", "after", "about", "than", "then", "them", "they", "their",
}


def open_questions(repo: Path) -> list[dict]:
    root = repo / "docs" / "specs"
    if not root.is_dir():
        return []
    found = []
    for path in sorted(root.glob("*/spec.md")):
        slug = path.parent.name
        if not SPEC_SLUG.fullmatch(slug) or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for question in _section(text):
            found.append({"spec": slug, "question": question})
    return found


def match_answer(text: str, questions: list[dict]) -> list[dict]:
    """The best word-overlap matches. An empty list is no match, not a guess."""
    scored = []
    for item in questions:
        ratio, shared = _score(text, item["question"])
        if ratio <= 0 or shared < 2 and _significant(item["question"]) and len(_significant(item["question"])) > 2:
            continue
        words = _significant(item["question"])
        if not words:
            continue
        if len(words) <= 2 and shared != len(words):
            continue
        if len(words) > 2 and (shared < 2 or shared / len(words) < 0.5):
            continue
        scored.append((shared / len(words), shared, item))
    if not scored:
        return []
    best = max(item[0] for item in scored)
    return [item[2] for item in scored if item[0] == best]


def _section(text: str) -> list[str]:
    found = []
    inside = False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.strip() == "## Open questions"
            continue
        if inside and line.startswith("- "):
            question = line[2:].strip()
            if question:
                found.append(question)
    return found


def _significant(text: str) -> list[str]:
    return [word for word in re.findall(r"[a-z0-9]+", text.lower()) if len(word) >= 4 and word not in _STOP]


def _score(answer: str, question: str) -> tuple[float, int]:
    words = _significant(question)
    if not words:
        return 0.0, 0
    shared = [word for word in words if word in set(_significant(answer))]
    return len(shared) / len(words), len(shared)
