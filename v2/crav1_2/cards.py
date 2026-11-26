"""Card shape for kit 2.0.

A card has 2 to 4 hyphen-only options. Each option has an impact and an undo.
A recommendation needs a backing fact. With no backing fact, the card names
the missing fact and does not recommend an option.
"""

from __future__ import annotations

from crav1_2.errors import EngineError
from crav1_2.schema import FACT_ID, HYPHEN_WORD

_LABELS = {"keep-all": "Keep all", "pick-some": "Pick some", "stop": "Stop"}


def card_problems(card: dict) -> list[str]:
    problems = []
    options = card.get("options")
    if not isinstance(options, list) or not 2 <= len(options) <= 4:
        problems.append("a card needs 2 to 4 options.")
        options = options if isinstance(options, list) else []
    words = []
    for option in options:
        if not isinstance(option, dict) or set(option) != {"word", "impact", "undo"}:
            problems.append("an option needs a word, an impact, and an undo.")
            continue
        word = option["word"]
        if not isinstance(word, str) or not HYPHEN_WORD.fullmatch(word):
            problems.append("an option word is hyphen-only.")
        else:
            words.append(word)
        for key in ("impact", "undo"):
            value = option[key]
            if not isinstance(value, str) or value.strip() == "" or "\n" in value:
                problems.append(f"an option {key} must be a single line.")
    if len(words) != len(set(words)):
        problems.append("option words must be distinct.")
    recommended = card.get("recommended", None)
    facts = card.get("facts")
    if recommended is None:
        missing = card.get("missing_fact")
        if not isinstance(missing, str) or missing.strip() == "":
            problems.append("a card with no recommendation names the missing fact.")
        if facts:
            problems.append("a card with no recommendation has no backing facts.")
    else:
        if recommended not in words:
            problems.append("recommended must be one of the option words.")
        if not isinstance(facts, list) or not facts or any(not FACT_ID.fullmatch(item) for item in facts if isinstance(item, str)) or any(not isinstance(item, str) for item in facts):
            problems.append("a recommendation needs a backing fact.")
        if card.get("missing_fact"):
            problems.append("a recommendation does not also name a missing fact.")
    return problems


def build_keep_card(fact_ids: list[str]) -> dict:
    card = {
        "question": "Which lines from this session should the note keep?",
        "options": [
            {
                "word": "keep-all",
                "impact": "Store every proposed line in one note.",
                "undo": "Run this-session again. This run does not edit the note.",
            },
            {
                "word": "pick-some",
                "impact": "Store only the numbered lines.",
                "undo": "Run this-session again for a line that was left out.",
            },
            {
                "word": "stop",
                "impact": "Write nothing.",
                "undo": "Run this-session again.",
            },
        ],
    }
    if fact_ids:
        card["recommended"] = "keep-all"
        card["facts"] = list(fact_ids)
    else:
        card["recommended"] = None
        card["missing_fact"] = (
            "No quote was checked against a session file. The user can say which lines to keep."
        )
    problems = card_problems(card)
    if problems:
        raise EngineError("Refused: " + problems[0])
    return card


def format_card(card: dict, *, why: str, preamble: str) -> str:
    lines = []
    if preamble.strip():
        lines.append(preamble.rstrip())
        lines.append("")
    lines.append("Card: " + card["question"])
    options = list(card["options"])
    recommended = card.get("recommended")
    if recommended:
        options.sort(key=lambda option: option["word"] != recommended)
    for option in options:
        shown = _LABELS.get(option["word"], option["word"])
        undo = f" Undo: {option['undo']}."
        if recommended == option["word"]:
            lines.append(f"- **{shown} (Recommended)** (`{option['word']}`): {option['impact']}{undo} Why: {why}.")
        elif option["word"] == "pick-some":
            lines.append(
                f"- **{shown}** (`{option['word']}`): {option['impact']} Type the numbers, e.g. 1 3.{undo}"
            )
        else:
            lines.append(f"- **{shown}** (`{option['word']}`): {option['impact']}{undo}")
    if not recommended:
        lines.append("Missing fact: " + card["missing_fact"])
    return "\n".join(lines) + "\n"
