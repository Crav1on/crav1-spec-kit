"""Read-only view of sot/. Writes nothing."""

from __future__ import annotations

from pathlib import Path

from crav1_2.errors import EngineError
from crav1_2.fold import fold_events
from crav1_2.repo import read_events, require_init
from crav1_2.schema import HYPHEN_WORD
from crav1_2.views import view_files

_WORDS = "Words: none, facts, decisions, assumptions, about-<topic>."


def show_sot(repo: Path, words: list[str]) -> dict:
    mode, topic = _words(words)
    require_init(repo)
    state = fold_events(read_events(repo))
    files = view_files(state)
    if mode == "index":
        text = files["sot/index.md"]
    elif mode == "facts":
        text = files["sot/facts.md"]
    elif mode == "decisions":
        text = files["sot/decisions.md"]
    elif mode == "assumptions":
        text = files["sot/assumptions.md"]
    else:
        text = _about(state, topic or "")
    broken = _broken(repo, state)
    if broken:
        text = text.rstrip("\n") + "\n\n## Broken pointers\n" + "\n".join(broken) + "\n"
    return {"wrote": False, "word": "none" if mode == "index" else words[0], "text": text}


def _words(words: list[str]) -> tuple[str, str | None]:
    if not words or words == ["none"]:
        return "index", None
    if len(words) != 1:
        raise EngineError("Refused: show-sot takes one word. " + _WORDS)
    word = words[0]
    if word in {"facts", "decisions", "assumptions"}:
        return word, None
    if word.startswith("about-") and word != "about" and HYPHEN_WORD.fullmatch(word):
        return "about", word[len("about-") :]
    raise EngineError("Refused: unknown word. " + _WORDS)


def _mentions(text: str, topic: str) -> bool:
    hay = text.lower()
    needle = topic.lower()
    spaced = needle.replace("-", " ")
    return needle in hay or (spaced != needle and spaced in hay)


def _about(state: dict, topic: str) -> str:
    hits = []
    for note in sorted(state["notes"].values(), key=lambda item: item["note"]):
        if _mentions(note.get("title") or "", topic):
            hits.append(f"- {note['note']} · {note.get('title') or note['note']}")
        for passage in note.get("passage_list") or []:
            blob = passage.get("quote", "") + " " + (passage.get("answers") or "")
            if _mentions(blob, topic):
                hits.append(f"- {note['note']} {passage['id']} · \"{passage['quote']}\"")
        for block in note.get("know") or []:
            blob = (block.get("heading") or "") + " " + (block.get("body") or "")
            if _mentions(blob, topic):
                hits.append(f"- {note['note']} know · {block.get('heading', '')}")
    for decision in sorted(state["decisions"].values(), key=lambda item: item["decision"]):
        blob = " ".join(str(decision.get(key) or "") for key in ("chosen", "accepting", "check"))
        if _mentions(blob, topic):
            mark = f" · superseded by {decision['superseded_by']}" if decision.get("superseded_by") else ""
            hits.append(f"- {decision['decision']}{mark}")
    for row in sorted(state["assumptions"].values(), key=lambda item: item["assumption"]):
        if _mentions(row.get("text") or "", topic):
            hits.append(f"- {row['assumption']}")
    body = "\n".join(hits) if hits else "(none)"
    return f"# About {topic}\n\n{body}\n"


def _broken(repo: Path, state: dict) -> list[str]:
    lines = []
    for note in sorted(state["notes"].values(), key=lambda item: item["note"]):
        for passage in note.get("passage_list") or []:
            path = passage.get("path")
            if not path:
                continue
            file_path = repo / path
            quote = passage.get("quote") or ""
            if not file_path.is_file():
                problem = "file is missing"
            else:
                try:
                    body = file_path.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    problem = "file is not UTF-8 text"
                else:
                    problem = "" if quote in body else "quote is gone"
            if problem:
                lines.append(f"- {note['note']} {passage['id']}: {problem}")
    return lines
