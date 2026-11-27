#!/usr/bin/env python3
"""List leftover open-state notes and old values after a decision (1.207.0).

After an Answer or a Settle write, run:

  <interpreter> -X utf8 stale_state_lines.py --spec <spec.md> \\
      --changed <section id> --old "<old words>" --new "<new words>" \\
      --decision "<decision>" --date <YYYY-MM-DD>

It writes nothing until --yes. A verbatim quote line is listed under
excluded and is never changed. On yes, each open-state sub-note gains
`Superseded <date> by <decision>` and each derived line is reworded.

Section ids: a heading slug (`constraints`, `open-questions`), `C#` for a
top-level bullet under Constraints, or `Q#` for a top-level bullet under
Open questions. `--changed` may be repeated. `--old` and `--new` pair in
order; one `--new` replaces every `--old`.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True

OPEN_STATE = re.compile(
    r"(?i)(possible answer|waiting for|stands until|not a settlement|\*\*Conflict:\*\*)"
)
HEADING = re.compile(r"^##\s+(.+?)\s*$")
ANSWERED = re.compile(r"^\s*(?:-\s*)?Answered:", re.I)
ITEM_ID = re.compile(r"^([CQ])(\d+)$", re.I)
SUPERSEDED = re.compile(r"Superseded \d{4}-\d{2}-\d{2} by ")


def _utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (AttributeError, OSError, ValueError):
                pass


_utf8_stdout()


def fail(message: str, status: int = 2) -> None:
    json.dump({"ok": False, "message": message}, sys.stdout)
    sys.stdout.write("\n")
    raise SystemExit(status)


def slug(title: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", (title or "").strip().lower()).strip("-")
    return text or "section"


def named_item(name: str, code: str) -> str:
    """Plain name first, code in parentheses. Never a bare code when a name exists."""
    name = re.sub(r"\s+", " ", str(name or "").strip())
    code = str(code or "").strip()
    if not name:
        name = "Note"
    if f"({code})" in name:
        return name
    lead = re.match(rf"^{re.escape(code)}\s+(.+)$", name) if code else None
    if lead:
        name = lead.group(1).strip()
    return f"{name} ({code})" if code else name


def display_name(raw: str, limit: int = 48) -> str:
    text = re.sub(r"\s+", " ", (raw or "").strip())
    text = re.sub(r"^[-*]\s+", "", text)
    text = text.strip("`").rstrip(".")
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0].rstrip(".,;:")
    if text and text[0].isalpha() and text[0].islower():
        text = text[0].upper() + text[1:]
    return text or "Note"


def quote_line(line: str, olds: list[str]) -> bool:
    """A verbatim quote is a blockquote, an Answered line, or an old value that sits only inside quotes."""
    stripped = line.strip()
    if stripped.startswith(">"):
        return True
    if ANSWERED.match(line):
        return True
    if not olds:
        return False
    bare = re.sub(r'"[^"]*"', "", line)
    bare = re.sub(r"“[^”]*”", "", bare)
    has_old = any(old.lower() in line.lower() for old in olds)
    outside = any(old.lower() in bare.lower() for old in olds)
    return has_old and not outside


def _pairs(olds: list[str], news: list[str]) -> list[tuple[str, str]]:
    if not olds:
        return []
    if not news:
        return [(old, "") for old in olds]
    if len(news) == 1:
        return [(old, news[0]) for old in olds]
    if len(news) != len(olds):
        fail("--new must be one value, or one value per --old")
    return list(zip(olds, news))


def parse_items(text: str) -> list[dict]:
    """Top-level bullets under each heading, with the lines that belong to them."""
    lines = text.splitlines()
    sections: list[dict] = []
    current: dict | None = None
    for index, line in enumerate(lines, start=1):
        heading = HEADING.match(line)
        if heading:
            current = {"slug": slug(heading.group(1)), "title": heading.group(1).strip(), "start": index, "items": []}
            sections.append(current)
            continue
        if current is None:
            continue
        if re.match(r"^- ", line):
            current["items"].append({"line": index, "text": line, "rows": [index]})
            continue
        if current["items"] and (line.startswith(" ") or line.startswith("\t") or line.strip() == ""):
            current["items"][-1]["rows"].append(index)
            continue
        if current["items"] and line.strip():
            # A following paragraph in the same section stays with the section, not the bullet.
            current.setdefault("loose", []).append(index)
    return sections


def selected_rows(sections: list[dict], changed: list[str]) -> tuple[set[int], dict[int, dict]]:
    """Line numbers in the changed sections or items, and a label for each item line."""
    wanted = {item.strip() for item in changed if item.strip()}
    rows: set[int] = set()
    labels: dict[int, dict] = {}
    for section in sections:
        codes = {"C": "C", "Q": "Q"}
        prefix = "Q" if section["slug"] == "open-questions" else "C" if section["slug"] in ("constraints", "constraint") else ""
        whole = section["slug"] in wanted or section["title"].lower() in {w.lower() for w in wanted}
        for number, item in enumerate(section["items"], start=1):
            code = f"{prefix}{number}" if prefix else ""
            name = display_name(item["text"])
            hit = whole or (code and code in wanted) or (code and code.lower() in {w.lower() for w in wanted})
            if not hit:
                continue
            for row in item["rows"]:
                rows.add(row)
                labels[row] = {"section": section["slug"], "id": code or section["slug"], "name": name}
        if whole:
            for row in section.get("loose") or []:
                rows.add(row)
                labels.setdefault(row, {"section": section["slug"], "id": section["slug"], "name": section["title"]})
    return rows, labels


def section_at(sections: list[dict], lineno: int) -> str:
    found = "preamble"
    for section in sections:
        if section["start"] <= lineno:
            found = section["slug"]
        else:
            break
    return found


def replace_old(line: str, pairs: list[tuple[str, str]]) -> str:
    out = line
    for old, new in pairs:
        if not old or not new or old.lower() == new.lower():
            continue
        out = re.sub(re.escape(old), new, out, flags=re.I)
    return out


def append_superseded(line: str, when: str, decision: str) -> str:
    mark = f"Superseded {when} by {decision}."
    if SUPERSEDED.search(line):
        return line
    body = line.rstrip()
    if body.endswith("."):
        body = body[:-1].rstrip()
    return body + ". " + mark


def apply_edits(text: str, notes: list[dict], derived: list[dict], pairs: list[tuple[str, str]], when: str, decision: str) -> str:
    note_rows = {item["line"] for item in notes}
    line_rows = {item["line"] for item in derived}
    out = []
    for index, line in enumerate(text.splitlines(), start=1):
        if index in note_rows:
            line = append_superseded(line, when, decision)
        elif index in line_rows:
            line = replace_old(line, pairs)
        out.append(line)
    body = "\n".join(out)
    if text.endswith("\n") or not text:
        body += "\n"
    return body


def card_question(notes: int, lines: int) -> str:
    note_word = "note" if notes == 1 else "notes"
    line_word = "line" if lines == 1 else "lines"
    if notes and lines:
        return f"Mark {notes} {note_word} superseded and update {lines} {line_word}?"
    if notes:
        return f"Mark {notes} {note_word} superseded?"
    return f"Update {lines} {line_word}?"


def analyse(text: str, changed: list[str], pairs: list[tuple[str, str]], decision: str, when: str) -> dict:
    sections = parse_items(text)
    scope, labels = selected_rows(sections, changed)
    if changed and not scope:
        fail("no section matched --changed: " + ", ".join(changed))
    olds = [old for old, _new in pairs if old]
    notes: list[dict] = []
    derived: list[dict] = []
    excluded: list[dict] = []
    logical = text.splitlines()
    for index, line in enumerate(logical, start=1):
        if not line.strip():
            continue
        label = labels.get(index) or {"section": section_at(sections, index), "id": "", "name": display_name(line)}
        if quote_line(line, olds):
            if (index in scope and OPEN_STATE.search(line)) or any(old.lower() in line.lower() for old in olds):
                excluded.append({"line": index, "text": line.strip(), "why": "verbatim quote", **label})
            continue
        in_scope = index in scope
        open_state = bool(OPEN_STATE.search(line)) and in_scope
        carries_old = any(old.lower() in line.lower() for old in olds)
        if open_state and not SUPERSEDED.search(line):
            notes.append({"line": index, "text": line.strip(), "kind": "note", **label})
        elif carries_old:
            derived.append({"line": index, "text": line.strip(), "kind": "line", "old": next(old for old, _n in pairs if old.lower() in line.lower()), **label})
    new_text = apply_edits(text, notes, derived, pairs, when, decision)
    diff = "".join(difflib.unified_diff(
        text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile="spec.md",
        tofile="spec.md",
    ))
    touched_sections = {item["section"] for item in notes + derived}
    touched: list[str] = []
    if touched_sections & {"constraints", "constraint"} or any(item["kind"] == "note" for item in notes):
        if any(item["section"] in ("constraints", "constraint") or item["kind"] == "note" for item in notes):
            touched.append("notes")
    if "open-questions" in touched_sections:
        touched.append("questions")
    body = touched_sections - {"constraints", "constraint", "open-questions"}
    if body:
        touched.append("body")
    if not touched and (notes or derived):
        touched.append("notes")
    header_source = notes[0] if notes else derived[0] if derived else None
    header = named_item(header_source["name"], header_source["id"]) if header_source else "Stale notes"
    question = card_question(len(notes), len(derived))
    return {
        "notes": notes,
        "lines": derived,
        "excluded": excluded,
        "diff": diff,
        "new_text": new_text,
        "touched": touched,
        "notes_only": bool(notes or derived) and "body" not in touched,
        "header": header,
        "question": question,
        "n_notes": len(notes),
        "n_lines": len(derived),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="List stale open-state notes and old values in a spec.")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--changed", action="append", default=[], help="Section slug, C#, or Q#. Repeat for several.")
    parser.add_argument("--old", action="append", default=[], help="Old words still in the spec. Repeat for several.")
    parser.add_argument("--new", action="append", default=[], help="Words that replace --old. One value covers every --old.")
    parser.add_argument("--decision", default="", help="Words after 'Superseded <date> by'.")
    parser.add_argument("--date", default="", help="YYYY-MM-DD. Default is today.")
    parser.add_argument("--yes", action="store_true", help="Write the spec. Without this, nothing is written.")
    args = parser.parse_args(argv)
    path = Path(args.spec)
    if not path.is_file():
        fail(f"no spec: {path}")
    when = args.date.strip() or date.today().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", when):
        fail("--date must be YYYY-MM-DD")
    pairs = _pairs(args.old, args.new)
    decision = " ".join(args.decision.split()) or (args.new[0] if args.new else "the decision")
    text = path.read_text(encoding="utf-8")
    found = analyse(text, args.changed, pairs, decision, when)
    needs_new = [row for row in found["lines"] if not any(new for _old, new in pairs)]
    payload = {
        "ok": True,
        "wrote": None,
        "notes": found["notes"],
        "lines": found["lines"],
        "excluded": found["excluded"],
        "diff": found["diff"],
        "touched": found["touched"],
        "notes_only": found["notes_only"],
        "n_notes": found["n_notes"],
        "n_lines": found["n_lines"],
        "header": found["header"],
        "question": found["question"] if (found["notes"] or found["lines"]) else None,
        "card": None,
    }
    if found["notes"] or found["lines"]:
        payload["card"] = {
            "header": found["header"],
            "question": found["question"],
            "background": f"{found['header']} still has the wording from before the decision.",
            "options": [
                {
                    "id": "yes",
                    "label": "Yes, mark and update (Recommended)",
                    "recommended": True,
                    "text": "Append Superseded to each open-state note and reword each derived line, as the diff shows. Why: the decision is already settled.",
                },
                {
                    "id": "leave",
                    "label": "Leave the old notes",
                    "recommended": False,
                    "text": "Change nothing. The notes stay as they are.",
                },
            ],
        }
    if args.yes and (found["notes"] or found["lines"]):
        if needs_new:
            fail("derived lines need --new before they can be reworded")
        path.write_text(found["new_text"], encoding="utf-8")
        payload["wrote"] = str(path)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
