#!/usr/bin/env python3
"""Approval needed items on a spec (kit 1.141.0).

Reads `## Approval needed` and `## Constraints`. An item names the person,
what they approve, and the tasks it holds (`Person:` and `Holds:`). A
matching `Approved:` line clears that hold. The line is never removed.

`Approved: <person>, <source date>, <source>, "<quote>" (accepted by <recorder> <date>)`

The source date is the quote's date. The accepted date is the day this run
accepted it. An earlier quote does not count until `write --yes`.

Usage:
  approval_needed.py <spec.md-or-spec-folder> [tasks.md]
  approval_needed.py show --root <spec-folder> --person ... --source-date ... --source ... --quote ... --recorder ... --accepted ...
  approval_needed.py write --root <spec-folder> ... --yes
  approval_needed.py add-item --root <spec-folder> --person ... --what ... --holds T4,T5 --yes

A folder argument uses <folder>/spec.md, and a sibling tasks.md when the
second argument is omitted. A missing file is a one-line error and exit 2.
Exit 0 on success. Nonzero only for a real error. Standard library only.
Line endings of a file it edits stay as they were. `show` writes nothing.
`write` and `add-item` write only with `--yes`.
"""
import json
import re
import sys
from pathlib import Path


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


_utf8_stdout()

TASK_LINE = re.compile(r"(?m)^- \[[ xX]\] (T\d+)\b[:.]?\s*(.*)$")
TASK_ID = re.compile(r"\bT\d+\b")
HOLDS_TASKS = re.compile(r"^T\d+(?:,\s*T\d+)*$")
HOLDS_NONE = re.compile(r"^none(?:\s*\([^)]*\))?$", re.I)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WHO_TEXT = re.compile(
    r"^(?:person\s+)?(?P<who>.+?)\s+(?:approves|gives a yes)\b",
    re.I,
)
GIVES = re.compile(
    r"^(?:person\s+)?(?P<who>.+?)\s+gives a yes before\s+(?P<what>.+?)\.?$",
    re.I,
)
APOSTROPHE = re.compile(
    r"^(?P<who>.+?)(?:'s|’s)\s+yes(?:\s+is required)?\s+before\s+(?P<what>.+?)\.?$",
    re.I,
)
ACCEPTED = re.compile(
    r'"\s*\(accepted by (?P<recorder>.+?) (?P<accepted>\d{4}-\d{2}-\d{2})\)\s*$'
)
STOP = {
    "the", "a", "an", "before", "after", "and", "or", "of", "to", "for",
    "its", "their", "this", "that", "with", "from", "into", "than", "then",
    "gives", "yes", "person", "when", "only", "over", "under", "into",
    "runs", "running", "applied", "apply", "script", "scripts", "before",
}


def _emit(payload) -> None:
    text = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False, indent=1) + "\n"
    try:
        sys.stdout.write(text if text.endswith("\n") or not isinstance(payload, str) else text)
        if isinstance(payload, str) and not payload.endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.flush()
    except UnicodeEncodeError:
        safe = text.encode("ascii", "replace").decode("ascii")
        sys.stdout.write(safe)
        sys.stdout.flush()


def _fail(code: str, message: str, status: int = 2) -> int:
    _emit({"ok": False, "code": code, "message": message})
    return status


def newline_of(text: str) -> str:
    """The newline the file already uses. A file with no CR uses LF."""
    return "\r\n" if "\r\n" in (text or "") else "\n"


def _section(text: str, heading: str) -> list[str]:
    lines = (text or "").splitlines()
    start = None
    want = heading.strip().lower()
    for i, line in enumerate(lines):
        if line.strip().lower() == want:
            start = i + 1
            break
    if start is None:
        return []
    out = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        out.append(line)
    return out


def _norm_person(value: str | None) -> str:
    text = re.sub(r"\s+", " ", (value or "").strip().lower())
    return re.sub(r"^person\s+", "", text)


def same_person(left: str | None, right: str | None) -> bool:
    a, b = _norm_person(left), _norm_person(right)
    return bool(a) and a == b


def _words(text: str) -> list[str]:
    found = []
    for word in re.findall(r"[a-z0-9]+", (text or "").lower()):
        if len(word) > 3 and word not in STOP and word not in found:
            found.append(word)
    return found


def parse_approved(line: str) -> dict | None:
    """One Approved line, or None when the line is not that mark."""
    body = (line or "").strip()
    if body.startswith("- "):
        body = body[2:].strip()
    if not body.startswith("Approved:"):
        return None
    head = re.match(r"^Approved:\s*(.*?),\s*(\d{4}-\d{2}-\d{2}),\s*(.*)$", body)
    if not head:
        return None
    tail = ACCEPTED.search(head.group(3))
    if not tail:
        return None
    before = head.group(3)[: tail.start()]
    split = before.rfind(', "')
    if split < 0:
        return None
    source = before[:split].strip().rstrip(",")
    quote = before[split + 3 :]
    if not source or '"' in quote:
        return None
    return {
        "who": head.group(1).strip(),
        "source_date": head.group(2),
        "source": source,
        "quote": quote,
        "recorder": tail.group("recorder").strip(),
        "accepted": tail.group("accepted"),
        "line": body,
    }


def format_approved(person, source_date, source, quote, recorder, accepted) -> str:
    """The lasting Approved line. The quote has no double quote."""
    if '"' in (quote or ""):
        raise ValueError("quote")
    return (
        f'Approved: {person}, {source_date}, {source}, "{quote}" '
        f"(accepted by {recorder} {accepted})"
    )


def _who_from_text(text: str) -> str | None:
    found = WHO_TEXT.match((text or "").strip())
    if not found:
        return None
    who = found.group("who").strip()
    return who or None


def _task_ids(tasks_text: str | None) -> list[str] | None:
    if tasks_text is None:
        return None
    found = []
    for match in TASK_LINE.finditer(tasks_text):
        tid = match.group(1)
        if tid not in found:
            found.append(tid)
    return found


def _text_tasks(text: str, known: list[str] | None) -> list[str]:
    if known is None:
        return []
    allowed = set(known)
    found = []
    for match in TASK_ID.finditer(text or ""):
        tid = match.group(0)
        if tid in allowed and tid not in found:
            found.append(tid)
    return found


def items(spec_text: str, task_ids: list[str] | None = None) -> list[dict]:
    """Approval needed items, in document order.

    `holding` is true when the item has no matching Approved line and names
    tasks. An approved item keeps its task list so a later write can say
    what it unblocks. A Holds line that is not tasks or none is unparsed
    and holds nothing.
    """
    rows = []
    current = None
    for line in _section(spec_text, "## Approval needed"):
        if line.startswith("- ") and not line.startswith("  "):
            body = line[2:].strip()
            current = {"text": body, "marks": []} if body else None
            if current:
                rows.append(current)
            continue
        if current is not None and line.startswith("  - "):
            current["marks"].append(line[4:].strip())
    out = []
    for row in rows:
        person = None
        holds_lines = []
        approved = []
        asked = False
        pending = False
        for mark in row["marks"]:
            low = mark.lower()
            if low.startswith("person:"):
                person = mark.split(":", 1)[1].strip()
            elif low.startswith("holds:"):
                holds_lines.append(mark.split(":", 1)[1].strip())
            elif mark.startswith("Approved:"):
                parsed = parse_approved(mark)
                if parsed:
                    approved.append(parsed)
            elif mark.startswith("Asked:"):
                asked = True
            elif mark.startswith("Pending:"):
                pending = True
        who = person or _who_from_text(row["text"])
        hold = holds_lines[-1] if holds_lines else None
        if hold is None:
            named = _text_tasks(row["text"], task_ids)
            mark, tasks = ("inferred", named) if named else ("missing", [])
        elif HOLDS_NONE.fullmatch(hold):
            mark, tasks = "none", []
        elif HOLDS_TASKS.fullmatch(hold):
            mark = "tasks"
            tasks = [part.strip() for part in hold.split(",")]
        else:
            mark, tasks = "unparsed", []
        match = next((line for line in approved if who and same_person(line["who"], who)), None)
        if match is None and not who and len(approved) == 1:
            match = approved[0]
            who = match["who"]
        out.append({
            "text": row["text"],
            "who": who,
            "mark": mark,
            "tasks": tasks,
            "approved": match is not None,
            "approved_who": match["who"] if match else None,
            "approved_line": match["line"] if match else None,
            "asked": asked,
            "pending": pending,
            "holding": match is None and bool(tasks),
        })
    return out


def holds(spec_text: str, task_ids: list[str] | None = None) -> dict:
    """T# -> the first unapproved item that holds it."""
    found = {}
    for item in items(spec_text, task_ids):
        if not item["holding"]:
            continue
        for tid in item["tasks"]:
            found.setdefault(tid, item)
    return found


def on_record(spec_text: str, person: str | None, task_id: str | None, task_ids: list[str] | None = None) -> bool:
    """True when a matching Approved line covers this person and task.

    A line for a different person, or an item that does not hold this task,
    does not count. Chat text and Answered lines are not read here.
    """
    for item in items(spec_text, task_ids):
        if not item["approved"]:
            continue
        if task_id and item["tasks"] and task_id not in item["tasks"]:
            continue
        if task_id and not item["tasks"]:
            continue
        if person and not same_person(person, item.get("approved_who") or item.get("who")):
            continue
        return True
    return False


def constraints(spec_text: str) -> list[dict]:
    """Constraint lines that name a person's yes before something."""
    found = []
    for line in _section(spec_text, "## Constraints"):
        body = line.strip()
        if body.startswith("- "):
            body = body[2:].strip()
        if not body:
            continue
        match = GIVES.match(body) or APOSTROPHE.match(body)
        if not match:
            continue
        found.append({
            "who": match.group("who").strip(),
            "what": match.group("what").strip().rstrip("."),
            "line": body,
        })
    return found


def suggest_holds(what: str, tasks_text: str) -> list[str]:
    """Unticked tasks whose title shares a word with what.

    When nothing shares a word and the what says apply, unticked
    `(host setup)` tasks are the suggestion. Otherwise none.
    """
    words = set(_words(what))
    hits = []
    host = []
    for match in TASK_LINE.finditer(tasks_text or ""):
        tid, rest = match.group(1), match.group(2) or ""
        if tid in hits or tid in host:
            continue
        title_words = set(_words(rest))
        if words and title_words & words:
            hits.append(tid)
        if "(host setup)" in rest.lower():
            host.append(tid)
    if hits:
        return hits
    if host and re.search(r"\bapply\b", what or "", re.I):
        return host
    return []


def gates(spec_text: str, tasks_text: str = "") -> list[dict]:
    """Constraint gates, with a suggested Holds list and whether an item exists."""
    existing = items(spec_text, _task_ids(tasks_text) if tasks_text else None)
    out = []
    for gate in constraints(spec_text):
        already = next((item for item in existing if same_person(item.get("who"), gate["who"])), None)
        out.append({
            **gate,
            "holds": [] if already else suggest_holds(gate["what"], tasks_text),
            "already": already is not None,
            "item": already["text"] if already else None,
        })
    return out


def analyse(spec_text: str, tasks_text: str = "") -> dict:
    ids = _task_ids(tasks_text) if tasks_text else None
    return {"items": items(spec_text, ids), "gates": gates(spec_text, tasks_text)}


def _find_item(spec_text: str, person: str | None, item_prefix: str | None, task_ids: list[str] | None):
    rows = items(spec_text, task_ids)
    if item_prefix:
        prefix = item_prefix.strip().lower()
        hits = [row for row in rows if row["text"].lower().startswith(prefix)]
    elif person:
        hits = [row for row in rows if same_person(row.get("who"), person)]
    else:
        hits = []
    return hits


def _as_file(path: Path | str, name: str):
    """A folder uses <folder>/<name>. A missing file is a one-line error."""
    target = Path(path)
    if target.is_dir():
        target = target / name
    if not target.is_file():
        return None, f"{name} not found: {target}"
    return target, None


def _spec_path(root: Path) -> Path:
    if root.is_file():
        return root
    return root / "spec.md"


def _load_spec(root: Path):
    path = _spec_path(root)
    if not path.is_file():
        return None, None
    # decode keeps CR LF. Text mode would turn them into LF and hide the file's endings.
    return path, path.read_bytes().decode("utf-8")


def _matching_constraints(spec_text: str, person: str | None) -> list[str]:
    return [gate["line"] for gate in constraints(spec_text) if not person or same_person(gate["who"], person)]


def _validate_dates(source_date: str, accepted: str) -> str | None:
    if not DATE.fullmatch(source_date or ""):
        return "source-date"
    if not DATE.fullmatch(accepted or ""):
        return "accepted"
    return None


def show_line(spec_text, tasks_text, person, source_date, source, quote, recorder, accepted, item_prefix=None):
    bad = _validate_dates(source_date, accepted)
    if bad:
        return None, bad
    try:
        line = format_approved(person, source_date, source, quote, recorder, accepted)
    except ValueError:
        return None, "quote"
    ids = _task_ids(tasks_text)
    hits = _find_item(spec_text, person, item_prefix, ids)
    if len(hits) != 1:
        return {
            "ok": False,
            "code": "item" if not hits else "ambiguous",
            "line": line,
            "constraints": _matching_constraints(spec_text, person),
            "items": [row["text"] for row in hits],
        }, "item" if not hits else "ambiguous"
    item = hits[0]
    return {
        "ok": True,
        "line": line,
        "item": item["text"],
        "who": item.get("who"),
        "unblocks": item["tasks"],
        "constraints": _matching_constraints(spec_text, person or item.get("who")),
        "already": item["approved"],
        "asks": (
            "Show the quote, its source date, and the constraint. "
            "An earlier quote does not count until accept in this run. "
            "Keep both dates when it is accepted."
        ),
    }, None


def _insert_block(text: str, block: str) -> str:
    """Append a block inside ## Approval needed, creating the section after Open questions."""
    nl = newline_of(text)
    if text and not text.endswith(("\n", "\r\n")):
        text += nl
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.strip().lower() == "## approval needed"), None)
    if start is None:
        insert_at = len(lines)
        for i, line in enumerate(lines):
            if line.strip().lower() != "## open questions":
                continue
            insert_at = len(lines)
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("## "):
                    insert_at = j
                    break
            break
        lines.insert(insert_at, f"## Approval needed{nl}{nl}")
        start = insert_at
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    addition = block if block.endswith(("\n", "\r\n")) else block + nl
    if any(lines[k].strip() for k in range(start + 1, end)) and lines[end - 1].strip():
        addition = nl + addition
    lines.insert(end, addition)
    return "".join(lines)


def add_item(text: str, person: str, what: str, holds_ids: list[str]) -> tuple[str, str]:
    """Return (new text, status). status is wrote or already."""
    existing = items(text, None)
    for item in existing:
        if same_person(item.get("who"), person) and what.lower() in item["text"].lower():
            return text, "already"
    nl = newline_of(text)
    holds_s = ", ".join(holds_ids)
    block = nl.join([
        f"- {person} approves {what}.",
        f"  - Person: {person}",
        f"  - Holds: {holds_s}",
        "",
    ])
    return _insert_block(text, block), "wrote"


def _append_approved(text: str, person: str | None, item_prefix: str | None, line: str) -> tuple[str, str]:
    ids = None
    hits = _find_item(text, person, item_prefix, ids)
    if not hits:
        return text, "item"
    if len(hits) != 1:
        return text, "ambiguous"
    target = hits[0]["text"]
    if any(mark.strip() == line for mark in _marks_of(text, target)):
        return text, "already"
    nl = newline_of(text)
    lines = text.splitlines(keepends=True)
    # Find the bullet and the last mark under it.
    bullet = None
    for i, raw in enumerate(lines):
        stripped = raw.strip()
        if stripped == f"- {target}" or stripped.startswith("- ") and stripped[2:].strip() == target:
            bullet = i
            break
    if bullet is None:
        return text, "item"
    last = bullet
    for j in range(bullet + 1, len(lines)):
        if lines[j].startswith("## ") or (lines[j].startswith("- ") and not lines[j].startswith("  ")):
            break
        if lines[j].strip():
            last = j
    indent = f"  - {line}{nl}"
    if not lines[last].endswith(("\n", "\r\n")):
        lines[last] = lines[last] + nl
    lines.insert(last + 1, indent)
    return "".join(lines), "wrote"


def _marks_of(text: str, target: str) -> list[str]:
    current = None
    marks = []
    for line in _section(text, "## Approval needed"):
        if line.startswith("- ") and not line.startswith("  "):
            if current == target:
                return marks
            body = line[2:].strip()
            current = body
            marks = []
            continue
        if current == target and line.startswith("  - "):
            marks.append(line[4:].strip())
    return marks if current == target else []


def _args(argv: list[str]) -> dict:
    out = {"yes": False, "holds": []}
    i = 0
    while i < len(argv):
        token = argv[i]
        if token == "--yes":
            out["yes"] = True
            i += 1
            continue
        if token.startswith("--") and i + 1 < len(argv):
            key = token[2:].replace("-", "_")
            out[key] = argv[i + 1]
            i += 2
            continue
        i += 1
    if "holds" in out and isinstance(out["holds"], str):
        out["holds"] = [part.strip() for part in out["holds"].split(",") if part.strip()]
    return out


def _need(args: dict, *keys: str) -> str | None:
    for key in keys:
        if not str(args.get(key) or "").strip():
            return key
    return None


def cmd_show(argv: list[str]) -> int:
    args = _args(argv)
    missing = _need(args, "root", "person", "source_date", "source", "quote", "recorder", "accepted")
    if missing:
        return _fail("missing", f"show needs --{missing.replace('_', '-')}")
    root = Path(args["root"])
    path, text = _load_spec(root)
    if text is None:
        return _fail("spec", f"no spec.md in {root}")
    tasks_path = root / "tasks.md"
    tasks = tasks_path.read_text(encoding="utf-8") if tasks_path.is_file() else ""
    payload, code = show_line(
        text, tasks, args["person"], args["source_date"], args["source"],
        args["quote"], args["recorder"], args["accepted"], args.get("item"),
    )
    if code and code in ("source-date", "accepted", "quote"):
        return _fail(code, "the Approved line needs a date, and the quote has no double quote")
    _emit(payload)
    return 0 if payload and payload.get("ok") else 2


def cmd_write(argv: list[str]) -> int:
    args = _args(argv)
    missing = _need(args, "root", "person", "source_date", "source", "quote", "recorder", "accepted")
    if missing:
        return _fail("missing", f"write needs --{missing.replace('_', '-')}")
    if not args["yes"]:
        return _fail("needs-yes", "write changes spec.md only with --yes")
    root = Path(args["root"])
    path, text = _load_spec(root)
    if text is None:
        return _fail("spec", f"no spec.md in {root}")
    tasks_path = root / "tasks.md"
    tasks = tasks_path.read_text(encoding="utf-8") if tasks_path.is_file() else ""
    payload, code = show_line(
        text, tasks, args["person"], args["source_date"], args["source"],
        args["quote"], args["recorder"], args["accepted"], args.get("item"),
    )
    if code in ("source-date", "accepted", "quote"):
        return _fail(code, "the Approved line needs a date, and the quote has no double quote")
    if not payload or not payload.get("ok"):
        _emit(payload)
        return 2
    updated, status = _append_approved(text, args["person"], args.get("item"), payload["line"])
    if status == "wrote":
        path.write_bytes(updated.encode("utf-8"))
    _emit({
        "ok": status in ("wrote", "already"),
        "status": status,
        "line": payload["line"],
        "unblocks": payload["unblocks"],
        "constraints": payload["constraints"],
    })
    return 0 if status in ("wrote", "already") else 2


def cmd_add(argv: list[str]) -> int:
    args = _args(argv)
    missing = _need(args, "root", "person", "what")
    if missing:
        return _fail("missing", f"add-item needs --{missing.replace('_', '-')}")
    holds_ids = args.get("holds") or []
    if not holds_ids:
        return _fail("holds", "add-item needs --holds T#")
    if not args["yes"]:
        return _fail("needs-yes", "add-item changes spec.md only with --yes")
    root = Path(args["root"])
    path, text = _load_spec(root)
    if text is None:
        return _fail("spec", f"no spec.md in {root}")
    updated, status = add_item(text, args["person"].strip(), args["what"].strip().rstrip("."), holds_ids)
    if status == "wrote":
        path.write_bytes(updated.encode("utf-8"))
    _emit({"ok": True, "status": status, "holds": holds_ids, "who": args["person"].strip()})
    return 0


def main(argv: list[str]) -> int:
    _utf8_stdout()
    if not argv or argv[0] in ("-h", "--help"):
        _emit(__doc__ or "")
        return 0
    if argv[0] == "show":
        return cmd_show(argv[1:])
    if argv[0] == "write":
        return cmd_write(argv[1:])
    if argv[0] == "add-item":
        return cmd_add(argv[1:])
    spec_path, err = _as_file(argv[0], "spec.md")
    if err:
        return _fail("spec", err)
    try:
        spec = spec_path.read_text(encoding="utf-8")
    except OSError:
        return _fail("spec", f"cannot read {spec_path}")
    tasks = ""
    if len(argv) > 1:
        tasks_path, err = _as_file(argv[1], "tasks.md")
        if err:
            return _fail("tasks", err)
        try:
            tasks = tasks_path.read_text(encoding="utf-8")
        except OSError:
            return _fail("tasks", f"cannot read {tasks_path}")
    else:
        sibling = spec_path.parent / "tasks.md"
        if sibling.is_file():
            try:
                tasks = sibling.read_text(encoding="utf-8")
            except OSError:
                tasks = ""
    _emit(analyse(spec, tasks))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
