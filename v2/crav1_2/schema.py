"""events.jsonl schema version 1.

Required fields are the phase-1 design. ``note.added`` also accepts optional
``title``, ``added_by``, ``passage_list``, and ``know`` so a note page can be
rebuilt from the log, plus ``vendor``, ``captured_from``, ``session_id``,
``quotes``, and ``redactions`` for this-session. ``note.extended`` appends
passages to a note. ``answer.matched`` records an open-question match and does
not close the question. Unknown fields are refused.
"""

from __future__ import annotations

import re
from datetime import datetime

from crav1_2.errors import SchemaError
from crav1_2.ulid import is_ulid
from crav1_2.version import SCHEMA

KINDS = ("mail", "chat", "meeting", "session", "document", "fact")
LABELS = ("finding", "answer", "decision", "open", "todo")
VENDORS = ("cursor", "claude", "codex")
CAPTURED = ("live-context", "file")
QUOTE_STATE = ("checked", "unchecked")
REDACTION_KINDS = ("access-key", "private-key", "secret", "token")
WEAK = ("verbal", "unmerged", "ai-summary", "inferred")
GAP_KINDS = ("silent", "conflicting", "vague")
ORIGINS = ("src", "dec", "asm")
SPEC_FILES = ("spec.md", "plan.md", "tasks.md")

NOTE_ID = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
FACT_ID = re.compile(r"^F-\d{4,}$")
GAP_ID = re.compile(r"^G-\d{4,}$")
DEC_ID = re.compile(r"^D-\d{4,}$")
ASM_ID = re.compile(r"^A-\d{4,}$")
ITEM_ID = re.compile(r"^I-\d{4,}$")
CARD_ID = re.compile(r"^C-\d{4,}$")
PASSAGE_ID = re.compile(r"^p-\d{3,}$")
RUN_ID = re.compile(r"^s-\d{4,}$")
HYPHEN_WORD = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FILE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")
SPEC_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BY_AGENT = re.compile(r"^crav1-2-[a-z0-9][a-z0-9-]*$")
WHEN = re.compile(r"^\d{2}:\d{2}$")
LINE_SPAN = re.compile(r"^L\d+-L\d+$")

TOP_KEYS = ("v", "id", "at", "by", "run", "type", "data")
NOTE_KEYS = (
    "note", "kinds", "date", "files", "from_sources", "passages",
    "title", "added_by", "passage_list", "know",
    "vendor", "captured_from", "session_id", "quotes", "redactions",
)
PASSAGE_KEYS = ("id", "kind", "who", "when", "quote", "path", "lines", "label", "verified", "weak", "answers")
KNOW_KEYS = ("heading", "body", "cites", "inferred")
OPTION_KEYS = ("word", "impact", "undo")

DATA_KEYS = {
    "note.added": NOTE_KEYS,
    "note.extended": ("note", "passages", "passage_list", "files", "know"),
    "answer.matched": ("note", "passage", "spec", "question"),
    "fact.cited": ("fact", "note", "passage", "quote", "weak"),
    "gap.found": ("gap", "spec", "kind", "facts", "impact", "uncertainty", "holds"),
    "card.asked": ("card", "gap", "question", "options", "recommended", "missing_fact", "facts"),
    "decision.recorded": ("decision", "card", "chosen", "over", "accepting", "facts", "affects", "check"),
    "decision.superseded": ("decision", "by"),
    "assumption.recorded": ("assumption", "gap", "text", "owner", "confirms_if", "breaks_if"),
    "assumption.closed": ("assumption", "by"),
    "item.linked": ("item", "spec", "file", "section", "text", "origin", "refs"),
    "item.updated": ("item", "text", "refs"),
    "item.unlinked": ("item", "reason"),
    "run.parked": ("step", "left"),
    "run.ended": ("step", "left"),
}


def parse_at(value: str) -> datetime:
    """ISO-8601 time with a numeric offset. Z is accepted as +00:00."""
    if not isinstance(value, str):
        raise SchemaError("Refused: at must be an ISO time with a numeric offset.")
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    if not re.search(r"[+-]\d{2}:\d{2}$", text):
        raise SchemaError("Refused: at must be an ISO time with a numeric offset.")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise SchemaError("Refused: at must be an ISO time with a numeric offset.") from exc
    if parsed.tzinfo is None:
        raise SchemaError("Refused: at must be an ISO time with a numeric offset.")
    return parsed


def now_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def origin_problem(origin: str, refs: list) -> str | None:
    """None when the item has one origin kind and every ref matches it."""
    if origin not in ORIGINS:
        return "origin must be src, dec, or asm"
    if not isinstance(refs, list) or not refs:
        return "an item needs at least one ref"
    kinds = []
    for ref in refs:
        if not isinstance(ref, str):
            return "a ref must be a string"
        if FACT_ID.fullmatch(ref):
            kinds.append("src")
        elif DEC_ID.fullmatch(ref):
            kinds.append("dec")
        elif ASM_ID.fullmatch(ref):
            kinds.append("asm")
        else:
            return f"ref {ref} is not an origin id"
    if set(kinds) != {origin}:
        return "an item must have exactly one origin kind"
    return None


def must_on_assumption(origin: str, text: str) -> bool:
    return origin == "asm" and re.search(r"\bMUST\b", text or "") is not None


def _order(data: dict, keys: tuple[str, ...]) -> dict:
    return {key: data[key] for key in keys if key in data}


def validate_event(raw: object, line: int | None = None) -> dict:
    prefix = f"line {line}: " if line else ""

    def fail(message: str) -> None:
        raise SchemaError(f"Refused: {prefix}{message}")

    if not isinstance(raw, dict):
        fail("an event must be a JSON object.")
    extra = set(raw) - set(TOP_KEYS)
    missing = [key for key in TOP_KEYS if key not in raw]
    if extra:
        fail(f"unknown field {sorted(extra)[0]}.")
    if missing:
        fail(f"missing field {missing[0]}.")
    if type(raw["v"]) is not int or isinstance(raw["v"], bool):
        fail("v must be an integer.")
    if raw["v"] != SCHEMA:
        fail(f"unknown events schema version {raw['v']}. Update kit 2.0.")
    if not is_ulid(raw["id"]):
        fail("id must be a 26-character ULID.")
    try:
        parse_at(raw["at"])
    except SchemaError as exc:
        fail(exc.message.removeprefix("Refused: "))
    by = raw["by"]
    if by not in {"user", "engine"} and not (isinstance(by, str) and BY_AGENT.fullmatch(by)):
        fail("by must be user, engine, or a crav1-2 agent name.")
    if not isinstance(raw["run"], str) or not RUN_ID.fullmatch(raw["run"]):
        fail("run must be a session id like s-0001.")
    kind = raw["type"]
    if kind not in DATA_KEYS:
        fail(f"unknown event type {kind}.")
    data = raw["data"]
    if not isinstance(data, dict):
        fail("data must be an object.")
    cleaned = _validate_data(kind, data, fail)
    return _order(
        {
            "v": SCHEMA,
            "id": raw["id"],
            "at": raw["at"],
            "by": by,
            "run": raw["run"],
            "type": kind,
            "data": cleaned,
        },
        TOP_KEYS,
    )


def _validate_data(kind: str, data: dict, fail) -> dict:
    allowed = set(DATA_KEYS[kind])
    extra = set(data) - allowed
    if extra:
        fail(f"unknown data field {sorted(extra)[0]}.")
    if kind == "note.added":
        return _note(data, fail)
    if kind == "note.extended":
        return _extended(data, fail)
    if kind == "answer.matched":
        return _answer_matched(data, fail)
    if kind == "fact.cited":
        return _fact(data, fail)
    if kind == "gap.found":
        return _gap(data, fail)
    if kind == "card.asked":
        return _card(data, fail)
    if kind == "decision.recorded":
        return _decision(data, fail)
    if kind == "decision.superseded":
        return _order(
            {"decision": _ident(data, "decision", DEC_ID, fail), "by": _ident(data, "by", DEC_ID, fail)},
            DATA_KEYS[kind],
        )
    if kind == "assumption.recorded":
        return _assumption(data, fail)
    if kind == "assumption.closed":
        return _closed_assumption(data, fail)
    if kind == "item.linked":
        return _item_linked(data, fail)
    if kind == "item.updated":
        return _item_updated(data, fail)
    if kind == "item.unlinked":
        return _order(
            {"item": _ident(data, "item", ITEM_ID, fail), "reason": _text(data, "reason", fail)},
            DATA_KEYS[kind],
        )
    if kind in {"run.parked", "run.ended"}:
        return _run(data, fail)
    fail(f"unknown event type {kind}.")
    return {}


def _require(data: dict, key: str, fail) -> object:
    if key not in data:
        fail(f"missing data field {key}.")
    return data[key]


def _text(data: dict, key: str, fail, *, empty: bool = False) -> str:
    value = _require(data, key, fail)
    if not isinstance(value, str) or "\n" in value or "\r" in value or "\x00" in value:
        fail(f"{key} must be a single-line string.")
    if not empty and value.strip() == "":
        fail(f"{key} is empty.")
    if len(value) > 8000:
        fail(f"{key} is too long.")
    return value


def _ident(data: dict, key: str, pattern: re.Pattern[str], fail) -> str:
    value = _text(data, key, fail)
    if not pattern.fullmatch(value):
        fail(f"{key} has the wrong id shape.")
    return value


def _id_list(data: dict, key: str, pattern: re.Pattern[str], fail, *, empty: bool = False) -> list[str]:
    value = _require(data, key, fail)
    if not isinstance(value, list):
        fail(f"{key} must be a list.")
    if not value and not empty:
        fail(f"{key} is empty.")
    out = []
    for item in value:
        if not isinstance(item, str) or not pattern.fullmatch(item):
            fail(f"{key} has an id with the wrong shape.")
        out.append(item)
    return out


def _score(data: dict, key: str, fail) -> int:
    value = _require(data, key, fail)
    if type(value) is not int or value not in (1, 2, 3):
        fail(f"{key} must be 1, 2, or 3.")
    return value


def _rel_path(value: object, key: str, fail) -> str:
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/"):
        fail(f"{key} must be a relative path.")
    body = value[:-1] if value.endswith("/") else value
    parts = body.split("/")
    if not body or any(part in ("", ".", "..") for part in parts):
        fail(f"{key} must be a relative path.")
    return value


def _date(value: str, fail) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        fail("date must be YYYY-MM-DD.")
    try:
        datetime.fromisoformat(value)
    except ValueError:
        fail("date must be YYYY-MM-DD.")
    return value


def _note(data: dict, fail) -> dict:
    note = _text(data, "note", fail)
    if not NOTE_ID.fullmatch(note):
        fail("note must be a YYYY-MM-DD-slug id.")
    date = _date(_text(data, "date", fail), fail)
    if not note.startswith(date + "-"):
        fail("note id must start with its date.")
    kinds = _require(data, "kinds", fail)
    if not isinstance(kinds, list) or not kinds:
        fail("kinds must be a non-empty list.")
    if any(not isinstance(kind, str) or kind not in KINDS for kind in kinds) or len(set(kinds)) != len(kinds):
        fail("kinds must be mail, chat, meeting, session, document, or fact.")
    files = _require(data, "files", fail)
    if not isinstance(files, list) or any(not isinstance(name, str) or not FILE_NAME.fullmatch(name) for name in files):
        fail("files must be a list of file names.")
    if "from_sources" not in data:
        fail("missing data field from_sources.")
    source = data["from_sources"]
    if source is not None:
        source = _rel_path(source, "from_sources", fail)
    passages = _require(data, "passages", fail)
    if type(passages) is not int or passages < 0:
        fail("passages must be a count.")
    cleaned = {
        "note": note,
        "kinds": list(kinds),
        "date": date,
        "files": list(files),
        "from_sources": source,
        "passages": passages,
    }
    if "title" in data:
        cleaned["title"] = _text(data, "title", fail)
    if "added_by" in data:
        cleaned["added_by"] = _text(data, "added_by", fail)
    if "passage_list" in data:
        cleaned["passage_list"] = _passages(data["passage_list"], fail)
        if passages != len(cleaned["passage_list"]):
            fail("passages count does not match passage_list.")
    if "know" in data:
        cleaned["know"] = _know(data["know"], cleaned.get("passage_list"), fail)
    if "vendor" in data:
        vendor = _text(data, "vendor", fail)
        if vendor not in VENDORS:
            fail("vendor must be cursor, claude, or codex.")
        cleaned["vendor"] = vendor
    if "captured_from" in data:
        captured = _text(data, "captured_from", fail)
        if captured not in CAPTURED:
            fail("captured_from must be live-context or file.")
        cleaned["captured_from"] = captured
    if "session_id" in data:
        cleaned["session_id"] = _text(data, "session_id", fail)
    if "quotes" in data:
        quotes = _text(data, "quotes", fail)
        if quotes not in QUOTE_STATE:
            fail("quotes must be checked or unchecked.")
        cleaned["quotes"] = quotes
    if "redactions" in data:
        redactions = data["redactions"]
        if (
            not isinstance(redactions, list)
            or any(item not in REDACTION_KINDS for item in redactions)
            or len(set(redactions)) != len(redactions)
        ):
            fail("redactions must be access-key, private-key, secret, or token.")
        cleaned["redactions"] = list(redactions)
    return _order(cleaned, NOTE_KEYS)


def _extended(data: dict, fail) -> dict:
    note = _text(data, "note", fail)
    if not NOTE_ID.fullmatch(note):
        fail("note must be a YYYY-MM-DD-slug id.")
    passages = _passages(data.get("passage_list"), fail) if "passage_list" in data else None
    if passages is None:
        fail("missing data field passage_list.")
    count = _require(data, "passages", fail)
    if type(count) is not int or count != len(passages):
        fail("passages count does not match passage_list.")
    cleaned: dict = {"note": note, "passages": count, "passage_list": passages}
    if "files" in data:
        files = data["files"]
        if not isinstance(files, list) or any(not isinstance(name, str) or not FILE_NAME.fullmatch(name) for name in files):
            fail("files must be a list of file names.")
        cleaned["files"] = list(files)
    if "know" in data:
        cleaned["know"] = _know(data["know"], None, fail)
    return _order(cleaned, DATA_KEYS["note.extended"])


def _answer_matched(data: dict, fail) -> dict:
    return _order(
        {
            "note": _ident(data, "note", NOTE_ID, fail),
            "passage": _ident(data, "passage", PASSAGE_ID, fail),
            "spec": _ident(data, "spec", SPEC_SLUG, fail),
            "question": _text(data, "question", fail),
        },
        DATA_KEYS["answer.matched"],
    )


def _passages(value: object, fail) -> list[dict]:
    if not isinstance(value, list):
        fail("passage_list must be a list.")
    seen = set()
    out = []
    for item in value:
        if not isinstance(item, dict):
            fail("a passage must be an object.")
        extra = set(item) - set(PASSAGE_KEYS)
        if extra or "id" not in item or "quote" not in item:
            fail("a passage needs an id and a quote.")
        pid = item["id"]
        if not isinstance(pid, str) or not PASSAGE_ID.fullmatch(pid):
            fail("a passage id must look like p-001.")
        if pid in seen:
            fail(f"passage {pid} is repeated.")
        seen.add(pid)
        quote = item["quote"]
        if not isinstance(quote, str) or quote.strip() == "" or "\n" in quote or "\r" in quote:
            fail("a passage quote must be a single line.")
        cleaned = {"id": pid, "quote": quote}
        if "path" in item:
            cleaned["path"] = _rel_path(item["path"], "path", fail)
            if "lines" in item:
                if not isinstance(item["lines"], str) or not LINE_SPAN.fullmatch(item["lines"]):
                    fail("passage lines must look like L40-L42.")
                cleaned["lines"] = item["lines"]
        else:
            if "lines" in item:
                fail("passage lines need a path.")
            if "kind" not in item or "who" not in item:
                fail("a passage needs a path, or a kind and a speaker.")
            if item["kind"] not in KINDS:
                fail("a passage kind is not a source kind.")
            who = item["who"]
            if not isinstance(who, str) or who.strip() == "" or "\n" in who:
                fail("a passage speaker must be a single line.")
            cleaned["kind"] = item["kind"]
            cleaned["who"] = who
        if "when" in item:
            if not isinstance(item["when"], str) or not WHEN.fullmatch(item["when"]):
                fail("a passage time must be HH:MM.")
            cleaned["when"] = item["when"]
        if "label" in item:
            if item["label"] not in LABELS:
                fail("a passage label must be finding, answer, decision, open, or todo.")
            cleaned["label"] = item["label"]
        if "verified" in item:
            if type(item["verified"]) is not bool:
                fail("verified must be true or false.")
            cleaned["verified"] = item["verified"]
        if "weak" in item:
            if item["weak"] is not None and item["weak"] not in WEAK:
                fail("weak must be verbal, unmerged, ai-summary, inferred, or null.")
            cleaned["weak"] = item["weak"]
        if "answers" in item:
            answers = item["answers"]
            if not isinstance(answers, str) or answers.strip() == "" or "\n" in answers or "\r" in answers:
                fail("answers must be a single line.")
            cleaned["answers"] = answers
        out.append(_order(cleaned, PASSAGE_KEYS))
    return out


def _know(value: object, passages: list[dict] | None, fail) -> list[dict]:
    if not isinstance(value, list):
        fail("know must be a list.")
    known = {item["id"] for item in passages} if passages is not None else None
    out = []
    for block in value:
        if not isinstance(block, dict):
            fail("a know-about block must be an object.")
        extra = set(block) - set(KNOW_KEYS)
        if extra or any(key not in block for key in ("heading", "body", "cites")):
            fail("a know-about block needs a heading, a body, and cites.")
        heading = block["heading"]
        body = block["body"]
        cites = block["cites"]
        if not isinstance(heading, str) or heading.strip() == "" or "\n" in heading:
            fail("a know-about heading must be a single line.")
        if not isinstance(body, str) or "\n" in body or "\r" in body:
            fail("a know-about body must be a single line.")
        if not isinstance(cites, list) or any(not isinstance(cite, str) or not PASSAGE_ID.fullmatch(cite) for cite in cites):
            fail("know-about cites must be passage ids.")
        if known is not None and any(cite not in known for cite in cites):
            fail("a know-about cite is not in the passage list.")
        inferred = block.get("inferred")
        if inferred is None:
            inferred = not cites
        if type(inferred) is not bool:
            fail("inferred must be true or false.")
        if not cites and not inferred:
            fail("a know-about answer with no cite is inferred.")
        if cites and inferred:
            fail("a know-about answer with cites is not inferred.")
        out.append(_order({"heading": heading, "body": body, "cites": list(cites), "inferred": inferred}, KNOW_KEYS))
    return out


def _fact(data: dict, fail) -> dict:
    weak = data.get("weak", None)
    if "weak" not in data:
        fail("missing data field weak.")
    if weak is not None and weak not in WEAK:
        fail("weak must be verbal, unmerged, ai-summary, inferred, or null.")
    return _order(
        {
            "fact": _ident(data, "fact", FACT_ID, fail),
            "note": _ident(data, "note", NOTE_ID, fail),
            "passage": _ident(data, "passage", PASSAGE_ID, fail),
            "quote": _text(data, "quote", fail),
            "weak": weak,
        },
        DATA_KEYS["fact.cited"],
    )


def _gap(data: dict, fail) -> dict:
    kind = _text(data, "kind", fail)
    if kind not in GAP_KINDS:
        fail("gap kind must be silent, conflicting, or vague.")
    holds = _require(data, "holds", fail)
    if not isinstance(holds, list) or any(not isinstance(item, str) or not re.fullmatch(r"T\d+", item) for item in holds):
        fail("holds must be a list of task ids like T12.")
    return _order(
        {
            "gap": _ident(data, "gap", GAP_ID, fail),
            "spec": _ident(data, "spec", SPEC_SLUG, fail),
            "kind": kind,
            "facts": _id_list(data, "facts", FACT_ID, fail),
            "impact": _score(data, "impact", fail),
            "uncertainty": _score(data, "uncertainty", fail),
            "holds": list(holds),
        },
        DATA_KEYS["gap.found"],
    )


def _options(value: object, fail) -> tuple[list[dict], list[str]]:
    if not isinstance(value, list) or not 2 <= len(value) <= 4:
        fail("a card needs 2 to 4 options.")
    words = []
    out = []
    for item in value:
        if not isinstance(item, dict) or set(item) != set(OPTION_KEYS):
            fail("an option needs a word, an impact, and an undo.")
        word = item["word"]
        if not isinstance(word, str) or not HYPHEN_WORD.fullmatch(word):
            fail("an option word is hyphen-only.")
        impact = item["impact"]
        undo = item["undo"]
        if not isinstance(impact, str) or impact.strip() == "" or "\n" in impact:
            fail("an option impact must be a single line.")
        if not isinstance(undo, str) or undo.strip() == "" or "\n" in undo:
            fail("an option undo must be a single line.")
        words.append(word)
        out.append(_order({"word": word, "impact": impact, "undo": undo}, OPTION_KEYS))
    if len(set(words)) != len(words):
        fail("option words must be distinct.")
    return out, words


def _card(data: dict, fail) -> dict:
    for key in ("card", "gap", "question", "options", "recommended"):
        if key not in data:
            fail(f"missing data field {key}.")
    options, words = _options(data["options"], fail)
    recommended = data["recommended"]
    cleaned = {
        "card": _ident(data, "card", CARD_ID, fail),
        "gap": _ident(data, "gap", GAP_ID, fail),
        "question": _text(data, "question", fail),
        "options": options,
        "recommended": None,
    }
    if recommended is None:
        if "missing_fact" not in data:
            fail("a card with no recommendation names the missing fact.")
        cleaned["missing_fact"] = _text(data, "missing_fact", fail)
        if "facts" in data:
            fail("a card with no recommendation has no backing facts.")
    else:
        if not isinstance(recommended, str) or recommended not in words:
            fail("recommended must be one of the option words.")
        if "missing_fact" in data:
            fail("a recommendation does not also name a missing fact.")
        cleaned["recommended"] = recommended
        cleaned["facts"] = _id_list(data, "facts", FACT_ID, fail)
    return _order(cleaned, DATA_KEYS["card.asked"])


def _decision(data: dict, fail) -> dict:
    chosen = _text(data, "chosen", fail)
    if not HYPHEN_WORD.fullmatch(chosen):
        fail("chosen must be a hyphen-only word.")
    over = _require(data, "over", fail)
    if not isinstance(over, list) or any(not isinstance(word, str) or not HYPHEN_WORD.fullmatch(word) for word in over):
        fail("over must be a list of hyphen-only words.")
    affects = _require(data, "affects", fail)
    if not isinstance(affects, list) or not affects:
        fail("affects must be a non-empty list.")
    for item in affects:
        if not isinstance(item, str) or not (ITEM_ID.fullmatch(item) or re.fullmatch(r"T\d+", item)):
            fail("affects entries must be item ids or task ids.")
    return _order(
        {
            "decision": _ident(data, "decision", DEC_ID, fail),
            "card": _ident(data, "card", CARD_ID, fail),
            "chosen": chosen,
            "over": list(over),
            "accepting": _text(data, "accepting", fail),
            "facts": _id_list(data, "facts", FACT_ID, fail),
            "affects": list(affects),
            "check": _text(data, "check", fail),
        },
        DATA_KEYS["decision.recorded"],
    )


def _assumption(data: dict, fail) -> dict:
    return _order(
        {
            "assumption": _ident(data, "assumption", ASM_ID, fail),
            "gap": _ident(data, "gap", GAP_ID, fail),
            "text": _text(data, "text", fail),
            "owner": _text(data, "owner", fail),
            "confirms_if": _text(data, "confirms_if", fail),
            "breaks_if": _text(data, "breaks_if", fail),
        },
        DATA_KEYS["assumption.recorded"],
    )


def _closed_assumption(data: dict, fail) -> dict:
    by = _text(data, "by", fail)
    if not (FACT_ID.fullmatch(by) or DEC_ID.fullmatch(by)):
        fail("assumption.closed by must be a fact or decision id.")
    return _order(
        {"assumption": _ident(data, "assumption", ASM_ID, fail), "by": by},
        DATA_KEYS["assumption.closed"],
    )


def _item_linked(data: dict, fail) -> dict:
    origin = _text(data, "origin", fail)
    refs = _require(data, "refs", fail)
    problem = origin_problem(origin, refs)
    if problem:
        fail(problem + ".")
    file_name = _text(data, "file", fail)
    if file_name not in SPEC_FILES:
        fail("file must be spec.md, plan.md, or tasks.md.")
    return _order(
        {
            "item": _ident(data, "item", ITEM_ID, fail),
            "spec": _ident(data, "spec", SPEC_SLUG, fail),
            "file": file_name,
            "section": _text(data, "section", fail),
            "text": _text(data, "text", fail),
            "origin": origin,
            "refs": list(refs),
        },
        DATA_KEYS["item.linked"],
    )


def _one_kind(refs: list, fail) -> None:
    kinds = []
    for ref in refs:
        if not isinstance(ref, str):
            fail("a ref must be a string.")
        if FACT_ID.fullmatch(ref):
            kinds.append("src")
        elif DEC_ID.fullmatch(ref):
            kinds.append("dec")
        elif ASM_ID.fullmatch(ref):
            kinds.append("asm")
        else:
            fail(f"ref {ref} is not an origin id.")
    if len(set(kinds)) != 1:
        fail("an item must have exactly one origin kind.")


def _item_updated(data: dict, fail) -> dict:
    refs = _require(data, "refs", fail)
    if not isinstance(refs, list) or not refs:
        fail("an item needs at least one ref.")
    _one_kind(refs, fail)
    return _order(
        {
            "item": _ident(data, "item", ITEM_ID, fail),
            "text": _text(data, "text", fail),
            "refs": list(refs),
        },
        DATA_KEYS["item.updated"],
    )


def _run(data: dict, fail) -> dict:
    left = _require(data, "left", fail)
    if not isinstance(left, list) or any(not isinstance(item, str) or not CARD_ID.fullmatch(item) for item in left):
        fail("left must be a list of card ids.")
    return _order({"step": _text(data, "step", fail), "left": list(left)}, ("step", "left"))
