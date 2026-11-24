#!/usr/bin/env python3
"""Print a findings table and the batch card that belongs with it (1.145.0).

The card line is built only by reading the table this command just printed.
No rows, and there is no card.

Usage:
  <interpreter> -X utf8 <skill crav1-tighten-plan>/scripts/batch_offer.py --title "Tighten-plan batch" --items <file>

<file> is JSON: a list of objects with id, issue, options, and recommendation.
On Windows the interpreter is python. Elsewhere it is python3. Then py -3.
Set PYTHONUTF8=1 and pass -X utf8.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

sys.dont_write_bytecode = True


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


_utf8_stdout()

COLUMNS = ("id", "issue", "options", "recommendation")

# Plain labels (1.196.0): no option letters and no internal resolution ids on a card.
LABELS = {
    "tick-from-verify": "tick it from the passing verify row",
    "park-risk": "note it as a risk",
    "add-regression": "add a regression test",
    "add-verify": "add a verify check",
    "add-cases": "add the missing cases",
    "add-integration": "add an integration check",
    "add-missing-path": "add the missing path",
    "cover-security": "cover the security case",
    "drop-scope": "drop it from scope",
    "fix-trace": "add the Trace row",
    "fix-loop": "break the dependency loop",
    "retarget-files": "point the task at the right files",
    "name-linter": "name the linter",
    "send-to-spec": "fix it in the spec",
    "split-task": "split the task",
    "make-testable": "make it a yes/no check",
    "cut-from-v0": "cut it from v0",
    "to-constraint": "make it a constraint",
    "to-adr": "record it as a decision",
    "to-open-question": "leave it as an open question",
    "mark-dropped": "mark the branch dropped",
    "sync-here": "update the diagram or decision to match",
    "keep": "keep as written",
    "suggest": "get a suggestion",
    "ask": "ask the owner",
}
_LETTER = re.compile(r"^[A-H]\s+(?=\S)")
_SEP = re.compile(r"([;,]\s*)")


def _plain_part(part: str) -> str:
    """One option: drop a leading A/B letter; map an id only when it is the whole option
    or the part before its first ':' (1.197.0). Words inside option text never change."""
    lead = part[: len(part) - len(part.lstrip())]
    body = _LETTER.sub("", part.strip())
    head, colon, rest = body.partition(":")
    if body in LABELS:
        body = LABELS[body]
    elif colon and head.strip() in LABELS:
        body = LABELS[head.strip()] + colon + rest
    return lead + body


def plain(text: str) -> str:
    """One option or a list of options in plain words: drop A/B letters, map whole internal ids."""
    text = " ".join(str(text).split())
    pieces = _SEP.split(text)
    return "".join(p if i % 2 else _plain_part(p) for i, p in enumerate(pieces))


HEADER = "| Id | Issue | Options | Recommendation |"
RULE = "| --- | --- | --- | --- |"


class BatchOfferError(Exception):
    """The card cannot be built. Nothing is printed for the card."""


def _cell(value: object, field: str) -> str:
    text = " ".join(str(value).split())
    if not text:
        raise BatchOfferError(f"missing {field}")
    return text.replace("|", "/")


def render_table(items: list) -> str:
    """Markdown findings table. Raises when there is no complete row."""
    if not isinstance(items, list) or not items:
        raise BatchOfferError("card text needs the findings table rows")
    seen: set[str] = set()
    lines = [HEADER, RULE]
    for item in items:
        if not isinstance(item, dict):
            raise BatchOfferError("each row is an object with id, issue, options, and recommendation")
        cells = []
        for key in COLUMNS:
            if key not in item:
                raise BatchOfferError(f"missing {key}")
            value = plain(item[key]) if key in ("options", "recommendation") else item[key]
            cells.append(_cell(value, key))
        if cells[0] in seen:
            raise BatchOfferError(f"duplicate id {cells[0]}")
        seen.add(cells[0])
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _rows_from_table(table: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for raw in (table or "").splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [part.strip() for part in line.strip("|").split("|")]
        if cells == ["Id", "Issue", "Options", "Recommendation"]:
            continue
        if cells and cells[0] and set(cells[0]) <= set("-: "):
            continue
        if len(cells) != 4 or not all(cells):
            raise BatchOfferError("a findings table row needs id, issue, options, and recommendation")
        rows.append(dict(zip(COLUMNS, cells)))
    return rows


def card_text(title: str, table: str) -> str:
    """Card question built from table rows. Empty or header-only tables raise.

    There is no other way to build the card. Callers pass the table markdown.
    """
    name = " ".join(str(title).split())
    if not name:
        raise BatchOfferError("title is required")
    rows = _rows_from_table(table)
    if not rows:
        raise BatchOfferError("card text needs the findings table rows")
    parts = [f"{row['id']} {row['issue']}: {row['recommendation']}" for row in rows]
    n = len(rows)
    what = "the recommendation" if n == 1 else f"all {n} recommendations"
    return f"{name}: apply {what}?\nOn yes: " + "; ".join(parts) + "."


def bullets(items: list) -> str:
    """One background bullet per item, right above the card: what, why, what yes does (1.196.0)."""
    lines = []
    for item in items:
        why = " ".join(str(item.get("why", "")).split())
        yes = plain(item.get("recommendation", ""))
        line = f"- {item['id']} {' '.join(str(item['issue']).split())}."
        if why:
            line += f" Why: {why.rstrip('.')}."
        line += f" Yes: {yes}."
        lines.append(line)
    return "\n".join(lines)


def offer(title: str, items: list) -> str:
    """Table, the bullets, then the short card and its result-on-yes line. No card without rows."""
    table = render_table(items)
    card = card_text(title, table)
    return table + "\n\n" + bullets(items) + "\n\nCard: " + card + "\n"


def _load_items(path: str) -> list:
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        raise BatchOfferError(f"cannot read items file: {exc.strerror or exc}") from exc
    except json.JSONDecodeError as exc:
        raise BatchOfferError(f"items file is not JSON: {exc.msg}") from exc
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return data["items"]
    if isinstance(data, list):
        return data
    raise BatchOfferError("items file must be a JSON list of rows")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print a findings table and its batch card.")
    parser.add_argument("--title", required=True, help="Card title, for example Tighten-plan batch")
    parser.add_argument("--items", required=True, help="JSON file of findings rows")
    args = parser.parse_args(argv)
    try:
        text = offer(args.title, _load_items(args.items))
    except BatchOfferError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
