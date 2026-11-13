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
            cells.append(_cell(item[key], key))
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
    return f"{name}. Yes applies every recommendation: " + "; ".join(parts) + "."


def offer(title: str, items: list) -> str:
    """Table first, then the card line. The card is not returned without rows."""
    table = render_table(items)
    card = card_text(title, table)
    return table + "\n\nCard: " + card + "\n"


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
