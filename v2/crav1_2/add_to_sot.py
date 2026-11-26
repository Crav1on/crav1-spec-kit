"""add-to-sot: one source becomes one note, one event, and regenerated views.

The engine assigns passage ids. It does not commit. dry-run writes nothing.
this-session asks one card before it writes, and a parked run resumes from
its session file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from crav1_2.cards import build_keep_card, format_card
from crav1_2.ending import render_ending
from crav1_2.errors import EngineError
from crav1_2.fold import empty_state, fold_events
from crav1_2.lint import lint_events
from crav1_2.notes import render_note
from crav1_2.questions import match_answer, open_questions
from crav1_2.quotes import annotate_quotes
from crav1_2.redact import redact_bytes, redact_text
from crav1_2.repo import append_events, read_events, rebuild_views, require_init
from crav1_2.schema import (
    FILE_NAME,
    KINDS,
    LABELS,
    NOTE_ID,
    RUN_ID,
    VENDORS,
    now_iso,
    parse_at,
    validate_event,
)
from crav1_2.sessions import write_session
from crav1_2.ulid import ulid

_WORDS = "Words: mail, chat, meeting, session, document, fact, from-sources, this-session, dry-run."
_SOURCE = {"mail", "chat", "meeting", "session", "document", "fact", "from-sources", "this-session"}
_CARD = {"keep-all", "pick-some", "stop"}
_PAYLOAD_KEYS = {
    "title", "date", "added_by", "at", "slug", "vendor", "session_id",
    "captured_from", "extractor", "originals", "from_sources", "card",
    "picks", "compacted", "session_file", "home",
}
_FROM = re.compile(r"^docs/sources/([A-Za-z0-9][A-Za-z0-9._-]*)/?$")


@dataclass
class Invocation:
    kinds: list[str] = field(default_factory=list)
    from_sources: bool = False
    this_session: bool = False
    dry_run: bool = False
    card: str | None = None
    picks: list[int] = field(default_factory=list)
    run_pick: str | None = None

    def has_source(self) -> bool:
        return bool(self.kinds) or self.from_sources or self.this_session


def parse_invocation(words: list[str]) -> Invocation:
    inv = Invocation()
    for word in words:
        if word in _SOURCE:
            if word == "from-sources":
                inv.from_sources = True
            elif word == "this-session":
                inv.this_session = True
                if "session" not in inv.kinds:
                    inv.kinds.append("session")
            elif word not in inv.kinds:
                inv.kinds.append(word)
            continue
        if word == "dry-run":
            inv.dry_run = True
            continue
        if word in _CARD:
            if inv.card and inv.card != word:
                raise EngineError("Refused: the card word is given twice and they differ.")
            inv.card = word
            continue
        if re.fullmatch(r"\d+", word):
            inv.picks.append(int(word))
            continue
        if isinstance(word, str) and RUN_ID.fullmatch(word):
            inv.run_pick = word
            continue
        raise EngineError(f"Refused: unknown word {word}. {_WORDS}")
    if inv.picks and inv.card != "pick-some":
        raise EngineError("Refused: a number needs pick-some.")
    if not inv.has_source() and not inv.card:
        raise EngineError(f"Refused: a source word is missing. {_WORDS}")
    if inv.from_sources and inv.this_session:
        raise EngineError("Refused: from-sources and this-session are different sources.")
    if inv.card and inv.has_source() and not inv.this_session:
        raise EngineError("Refused: keep-all, pick-some, and stop belong to this-session.")
    if not inv.kinds and inv.from_sources:
        inv.kinds = ["document"]
    return inv


def add_to_sot(repo: Path, words: list[str], payload: dict | None) -> dict:
    inv = parse_invocation(words)
    payload = _payload(payload)
    _apply_payload_card(inv, payload)
    if not inv.has_source():
        return _resume(repo, inv, payload)
    if inv.this_session and "extractor" not in payload:
        parked = _load_parked(repo, inv.run_pick)
        if parked is not None:
            if inv.card:
                return _finish_parked(repo, parked, inv, payload)
            return _show_parked(parked)
        raise EngineError("Refused: this-session needs the extractor JSON.")
    prepared = _prepare(repo, inv, payload)
    if inv.dry_run:
        return _preview(repo, prepared, inv)
    if not (repo / ".crav1-2" / "engine.json").is_file():
        raise EngineError("Refused: run init first.")
    if inv.this_session and inv.card is None:
        return _park(repo, prepared)
    if inv.card == "stop":
        _end_parked(repo, inv.run_pick)
        return _stopped()
    if inv.card == "pick-some" and not inv.picks:
        raise EngineError("Refused: pick-some takes numbers, for example 1 3.")
    _end_parked(repo, None)
    return _write(repo, prepared, inv)


def _payload(payload: dict | None) -> dict:
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        raise EngineError("Refused: add-to-sot reads one JSON object.")
    extra = set(payload) - _PAYLOAD_KEYS
    if extra:
        raise EngineError(f"Refused: unknown field {sorted(extra)[0]}.")
    if "compacted" in payload and type(payload["compacted"]) is not bool:
        raise EngineError("Refused: compacted must be true or false.")
    if "picks" in payload:
        picks = payload["picks"]
        if not isinstance(picks, list) or any(type(item) is not int or item < 1 for item in picks):
            raise EngineError("Refused: picks must be a list of line numbers.")
    return payload


def _apply_payload_card(inv: Invocation, payload: dict) -> None:
    card = payload.get("card")
    if card is not None and card not in _CARD:
        raise EngineError("Refused: the card word must be keep-all, pick-some, or stop.")
    if card and inv.card and card != inv.card:
        raise EngineError("Refused: the card word is given twice and they differ.")
    if card and not inv.card:
        inv.card = card
        if inv.card and inv.has_source() and not inv.this_session:
            raise EngineError("Refused: keep-all, pick-some, and stop belong to this-session.")
    picks = list(payload.get("picks") or [])
    if picks and inv.picks and picks != inv.picks:
        raise EngineError("Refused: the line numbers are given twice and they differ.")
    if picks and not inv.picks:
        inv.picks = picks
    if inv.picks and inv.card != "pick-some":
        raise EngineError("Refused: a number needs pick-some.")


def _prepare(repo: Path, inv: Invocation, payload: dict) -> dict:
    state, _events = _state(repo)
    folder = None
    if inv.from_sources:
        if payload.get("originals"):
            raise EngineError("Refused: from-sources copies nothing.")
        raw_folder = payload.get("from_sources")
        if not isinstance(raw_folder, str) or not _FROM.fullmatch(raw_folder):
            raise EngineError("Refused: from-sources points at docs/sources/<folder>/.")
        folder = raw_folder if raw_folder.endswith("/") else raw_folder + "/"
        if not (repo / folder.rstrip("/")).is_dir():
            raise EngineError("Refused: that docs/sources folder does not exist.")
    elif payload.get("from_sources"):
        raise EngineError("Refused: from_sources was set without the from-sources word.")
    extractor = payload.get("extractor")
    raw_title = payload.get("title")
    if raw_title is None and isinstance(extractor, dict):
        raw_title = extractor.get("title")
    title = _line(raw_title, "title") if raw_title is not None else None
    if not title:
        title = "Session" if inv.this_session else "Source"
    title, title_kinds = redact_text(title)
    date = payload.get("date") or datetime.now().astimezone().date().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(date)):
        raise EngineError("Refused: date must be YYYY-MM-DD.")
    try:
        datetime.fromisoformat(str(date))
    except ValueError as exc:
        raise EngineError("Refused: date must be YYYY-MM-DD.") from exc
    added_by = _line(payload.get("added_by") or "user", "added_by") or "user"
    at = payload.get("at") or now_iso()
    try:
        parse_at(at)
    except EngineError as exc:
        raise EngineError("Refused: at must be an ISO time with a numeric offset.") from exc
    passages, know = _extractor(extractor, inv)
    redactions = list(title_kinds)
    if inv.from_sources:
        passages = _bind_sources(passages, folder or "", repo)
        for passage in passages:
            _text, found = redact_text(passage["quote"])
            if found:
                raise EngineError(
                    "Refused: a secret is in the source quote. from-sources does not copy or edit docs/sources."
                )
    else:
        passages, more = _redact_passages(passages)
        redactions.extend(more)
    know, more = _redact_know(know)
    redactions.extend(more)
    originals, more = _originals(payload.get("originals") or [])
    redactions.extend(more)
    vendor = None
    captured = None
    session_id = None
    quotes = None
    if inv.this_session:
        vendor = payload.get("vendor")
        if vendor not in VENDORS:
            raise EngineError("Refused: this-session needs a vendor. Words: cursor, claude, codex.")
        captured = "live-context"
        if payload.get("session_id") is not None:
            session_id = _line(payload.get("session_id"), "session_id")
        home = Path(payload["home"]).expanduser() if payload.get("home") else Path.home()
        quotes, passages = annotate_quotes(
            passages,
            vendor=vendor,
            repo=repo,
            home=home,
            session_file=payload.get("session_file"),
        )
    existing = _live_note(state, session_id) if inv.this_session else None
    if existing:
        passages, know = _drop_existing(existing, passages, know)
    if inv.this_session and not passages:
        return {"empty": True, "note_id": existing["note"] if existing else None}
    questions = open_questions(repo) if inv.this_session else []
    matches = _matches(passages, questions) if inv.this_session else []
    slug = payload.get("slug") or _slugify(title)
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise EngineError("Refused: the slug must be hyphen-only.")
    note_id = existing["note"] if existing else _fresh_id(repo, state, str(date), slug)
    verified = [index for index, passage in enumerate(passages) if passage.get("verified") is True]
    fact_ids = _next_facts(state, len(verified))
    card = build_keep_card(fact_ids) if inv.this_session else None
    why = _why(fact_ids)
    preamble = _preamble(passages, payload.get("compacted") is True) if inv.this_session else ""
    redaction_list = sorted(set(redactions))
    return {
        "empty": False,
        "extend": existing is not None,
        "note_id": note_id,
        "title": title,
        "date": str(date),
        "added_by": added_by,
        "at": at,
        "not_before": (existing or {}).get("at"),
        "kinds": list(inv.kinds),
        "files": [name for name, _data in originals],
        "from_sources": folder if inv.from_sources else None,
        "vendor": vendor,
        "captured_from": captured,
        "session_id": session_id,
        "quotes": quotes,
        "redactions": redaction_list,
        "passages": passages,
        "know": know,
        "matches": matches,
        "verified_indexes": verified,
        "fact_ids": fact_ids,
        "card": card,
        "why": why,
        "preamble": preamble,
        "_originals": originals,
    }


def _extractor(raw: object, inv: Invocation) -> tuple[list[dict], list[dict]]:
    if not isinstance(raw, dict):
        raise EngineError("Refused: the extractor JSON must be an object.")
    extra = set(raw) - {"title", "passages", "know"}
    if extra:
        raise EngineError(f"Refused: unknown extractor field {sorted(extra)[0]}.")
    rows = raw.get("passages")
    if not isinstance(rows, list) or not rows:
        raise EngineError("Refused: the extractor needs at least one passage.")
    if len(rows) > 500:
        raise EngineError("Refused: a note keeps at most 500 passages.")
    passages = []
    for row in rows:
        passages.append(_one_passage(row, inv))
    know = []
    for block in raw.get("know") or []:
        if not isinstance(block, dict):
            raise EngineError("Refused: a know-about block must be an object.")
        heading = _line(block.get("heading"), "heading")
        body = block.get("body")
        if not isinstance(body, str) or "\n" in body or "\r" in body:
            raise EngineError("Refused: a know-about body must be a single line.")
        cites = block.get("cites") if "cites" in block else []
        if not isinstance(cites, list) or any(type(cite) is not int or cite < 0 or cite >= len(passages) for cite in cites):
            raise EngineError("Refused: know-about cites are indexes into the passages.")
        if not heading:
            raise EngineError("Refused: a know-about heading must be a single line.")
        know.append({"heading": heading, "body": body, "cites": list(cites)})
    return passages, know


def _one_passage(row: object, inv: Invocation) -> dict:
    if not isinstance(row, dict):
        raise EngineError("Refused: a passage must be an object.")
    allowed = {"kind", "who", "when", "quote", "label", "answers", "path", "lines"}
    extra = set(row) - allowed
    if extra:
        raise EngineError(f"Refused: unknown passage field {sorted(extra)[0]}.")
    quote = row.get("quote")
    if not isinstance(quote, str) or quote.strip() == "" or "\n" in quote or "\r" in quote:
        raise EngineError("Refused: a passage quote must be a single line.")
    if inv.from_sources:
        path = row.get("path")
        if not isinstance(path, str) or not path.startswith("docs/sources/") or ".." in path.split("/"):
            raise EngineError("Refused: a from-sources passage points at a file under that folder.")
        passage = {"quote": quote, "path": path}
        if "lines" in row:
            passage["lines"] = row.get("lines")
        return passage
    kind = row.get("kind")
    if kind is None and len(inv.kinds) == 1:
        kind = inv.kinds[0]
    if kind not in KINDS or kind not in inv.kinds:
        raise EngineError("Refused: a passage kind must be one of the words in the invocation.")
    who = _line(row.get("who"), "who")
    if not who:
        raise EngineError("Refused: a passage needs a speaker.")
    passage = {"kind": kind, "who": who, "quote": quote}
    if "when" in row:
        if not isinstance(row["when"], str) or not re.fullmatch(r"\d{2}:\d{2}", row["when"]):
            raise EngineError("Refused: a passage time must be HH:MM.")
        passage["when"] = row["when"]
    if "label" in row:
        if row["label"] not in LABELS:
            raise EngineError("Refused: a passage label must be finding, answer, decision, open, or todo.")
        passage["label"] = row["label"]
    if "answers" in row:
        answers = _line(row.get("answers"), "answers")
        if not answers:
            raise EngineError("Refused: answers must be a single line.")
        passage["answers"] = answers
    return passage


def _bind_sources(passages: list[dict], folder: str, repo: Path) -> list[dict]:
    prefix = folder.rstrip("/") + "/"
    bound = []
    for passage in passages:
        path = passage["path"]
        if not path.startswith(prefix):
            raise EngineError("Refused: a from-sources passage stays inside that folder.")
        file_path = repo / path
        if not file_path.is_file():
            raise EngineError(f"Refused: {path} is not a file.")
        try:
            body = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise EngineError(f"Refused: {path} is not UTF-8 text.") from exc
        lines = passage.get("lines")
        if lines is None:
            lines = _find_lines(body, passage["quote"])
        elif not re.fullmatch(r"L\d+-L\d+", str(lines)) or passage["quote"] not in _span(body, str(lines)):
            raise EngineError("Refused: the quote is not in the named lines.")
        if passage["quote"] not in body:
            raise EngineError(f"Refused: the quote is not in {path}.")
        bound.append({"quote": passage["quote"], "path": path, "lines": lines})
    return bound


def _find_lines(body: str, quote: str) -> str:
    for number, line in enumerate(body.splitlines(), 1):
        if quote in line:
            return f"L{number}-L{number}"
    raise EngineError("Refused: the quote is not in the source file.")


def _span(body: str, lines: str) -> str:
    start_s, end_s = lines[1:].split("-L")
    start, end = int(start_s), int(end_s)
    rows = body.splitlines()
    if start < 1 or end < start or end > len(rows):
        return ""
    return "\n".join(rows[start - 1 : end])


def _redact_passages(passages: list[dict]) -> tuple[list[dict], list[str]]:
    kinds: list[str] = []
    cleaned = []
    for passage in passages:
        passage = dict(passage)
        for key in ("quote", "answers"):
            if isinstance(passage.get(key), str):
                text, found = redact_text(passage[key])
                if key == "quote" and text.strip() == "":
                    raise EngineError("Refused: a passage quote is empty after redaction.")
                passage[key] = text
                kinds.extend(found)
        cleaned.append(passage)
    return cleaned, kinds


def _redact_know(know: list[dict]) -> tuple[list[dict], list[str]]:
    kinds: list[str] = []
    cleaned = []
    for block in know:
        heading, found_h = redact_text(block["heading"])
        body, found_b = redact_text(block["body"])
        kinds.extend(found_h)
        kinds.extend(found_b)
        cleaned.append({"heading": heading, "body": body, "cites": list(block["cites"])})
    return cleaned, kinds


def _originals(items: object) -> tuple[list[tuple[str, bytes]], list[str]]:
    if not isinstance(items, list):
        raise EngineError("Refused: originals must be a list.")
    loaded = []
    kinds: list[str] = []
    seen = set()
    for item in items:
        if not isinstance(item, dict) or "name" not in item:
            raise EngineError("Refused: an original needs a name and from or text.")
        extra = set(item) - {"name", "from", "text"}
        if extra:
            raise EngineError(f"Refused: unknown original field {sorted(extra)[0]}.")
        name = item["name"]
        if not isinstance(name, str) or not FILE_NAME.fullmatch(name) or name == "note.md":
            raise EngineError(f"Refused: {name} is not a file name kit 2.0 can copy.")
        if name in seen:
            raise EngineError(f"Refused: {name} is repeated.")
        seen.add(name)
        if "from" in item and "text" in item:
            raise EngineError("Refused: an original is a file or text, not both.")
        if "text" in item:
            if not isinstance(item["text"], str):
                raise EngineError("Refused: original text must be a string.")
            data = item["text"].encode("utf-8")
        elif "from" in item:
            path = Path(str(item["from"]))
            if not path.is_file():
                raise EngineError(f"Refused: {name} is not a file.")
            data = path.read_bytes()
        else:
            raise EngineError("Refused: an original needs from or text.")
        if len(data) > 50_000_000:
            raise EngineError(f"Refused: {name} is too large.")
        data, found = redact_bytes(data)
        kinds.extend(found)
        loaded.append((name, data))
    return loaded, kinds


def _matches(passages: list[dict], questions: list[dict]) -> list[dict]:
    found = []
    for index, passage in enumerate(passages):
        if passage.get("label") != "answer" and "answers" not in passage:
            continue
        text = passage.get("answers") or passage.get("quote") or ""
        for hit in match_answer(text, questions):
            found.append({"index": index, "spec": hit["spec"], "question": hit["question"]})
    return found


def _live_note(state: dict, session_id: str | None) -> dict | None:
    if not session_id:
        return None
    rows = [
        note for note in state["notes"].values()
        if note.get("session_id") == session_id and not note.get("missing")
    ]
    if not rows:
        return None
    rows.sort(key=lambda note: note.get("at") or "")
    return rows[-1]


def _drop_existing(existing: dict, passages: list[dict], know: list[dict]) -> tuple[list[dict], list[dict]]:
    have = {item.get("quote") for item in existing.get("passage_list") or []}
    mapping = {}
    shown = []
    for index, passage in enumerate(passages):
        if passage.get("quote") in have:
            continue
        mapping[index] = len(shown)
        shown.append(passage)
    remapped = []
    for block in know:
        cites = [mapping[cite] for cite in block["cites"] if cite in mapping]
        remapped.append({"heading": block["heading"], "body": block["body"], "cites": cites})
    return shown, remapped


def _fresh_id(repo: Path, state: dict, date: str, slug: str) -> str:
    base = f"{date}-{slug}"
    candidate = base
    number = 2
    used = set(state["notes"])
    while candidate in used or (repo / "sot" / candidate).exists():
        candidate = f"{base}-{number}"
        number += 1
        if number > 50:
            raise EngineError("Refused: too many notes already use that slug.")
    if not NOTE_ID.fullmatch(candidate):
        raise EngineError("Refused: the note id is not a YYYY-MM-DD-slug.")
    return candidate


def _slugify(title: str) -> str:
    parts = re.findall(r"[a-z0-9]+", title.lower())
    slug = "-".join(parts)
    if len(slug) > 48:
        slug = slug[:48].rstrip("-")
    return slug or "note"


def _next_facts(state: dict, count: int) -> list[str]:
    nums = []
    for key in state["facts"]:
        match = re.search(r"(\d+)$", key)
        if match:
            nums.append(int(match.group(1)))
    start = max(nums, default=0) + 1
    return [f"F-{number:04d}" for number in range(start, start + count)]


def _why(fact_ids: list[str]) -> str:
    if not fact_ids:
        return ""
    if len(fact_ids) == 1:
        return f"{fact_ids[0]} is a quote checked against the session file"
    return ", ".join(fact_ids) + " are quotes checked against the session file"


def _preamble(passages: list[dict], compacted: bool) -> str:
    lines = [f"{len(passages)} lines from this session."]
    if compacted:
        lines.append("Early turns may be missing from this chat. The session word reads a session file.")
    for number, passage in enumerate(passages, 1):
        mark = ""
        if passage.get("verified") is True:
            mark = " · verified"
        elif passage.get("verified") is False:
            mark = " · unverified"
        label = passage.get("label") or passage.get("kind") or "line"
        who = passage.get("who") or ""
        lines.append(f"{number}. {label} · {who}{mark} · \"{passage['quote']}\"")
    return "\n".join(lines)


def _preview(repo: Path, prepared: dict, inv: Invocation) -> dict:
    if prepared.get("empty"):
        return {
            "wrote": False,
            "dry_run": True,
            "note_id": prepared.get("note_id"),
            "note_markdown": "",
            "events": [],
            "ending": render_ending([], None),
            "card": None,
            "card_text": "",
            "proposal": "",
            "parked": None,
        }
    state, _events = _state(repo)
    events, markdown, specs = _events_for(prepared, _selection(inv, prepared), "s-0000", state)
    return {
        "wrote": False,
        "dry_run": True,
        "note_id": prepared["note_id"],
        "note_markdown": markdown,
        "events": events,
        "ending": render_ending(specs, None),
        "card": prepared.get("card"),
        "card_text": _card_text(prepared),
        "proposal": prepared.get("preamble") or "",
        "parked": None,
    }


def _park(repo: Path, prepared: dict) -> dict:
    if prepared.get("empty"):
        return _empty(prepared)
    require_init(repo)
    _end_parked(repo, None)
    state, events = _state(repo)
    run = _next_run(repo, events)
    body = write_session(
        repo,
        run,
        "parked",
        step="card",
        at=prepared["at"],
        payload=_public(prepared),
    )
    return {
        "wrote": False,
        "dry_run": False,
        "note_id": prepared["note_id"],
        "note_markdown": "",
        "events": [],
        "ending": None,
        "card": prepared.get("card"),
        "card_text": _card_text(prepared),
        "proposal": prepared.get("preamble") or "",
        "parked": body["id"],
    }


def _show_parked(parked: dict) -> dict:
    prepared = dict(parked["payload"])
    prepared["empty"] = False
    return {
        "wrote": False,
        "dry_run": False,
        "note_id": prepared.get("note_id"),
        "note_markdown": "",
        "events": [],
        "ending": None,
        "card": prepared.get("card"),
        "card_text": _card_text(prepared),
        "proposal": prepared.get("preamble") or "",
        "parked": parked["id"],
    }


def _finish_parked(repo: Path, parked: dict, inv: Invocation, payload: dict) -> dict:
    if inv.dry_run:
        prepared = dict(parked["payload"])
        prepared.setdefault("empty", False)
        return _preview(repo, prepared, inv)
    if inv.card == "stop":
        _end_one(repo, parked)
        return _stopped()
    if inv.card == "pick-some" and not inv.picks:
        raise EngineError("Refused: pick-some takes numbers, for example 1 3.")
    prepared = dict(parked["payload"])
    prepared["empty"] = False
    prepared["_originals"] = []
    prepared["_run"] = parked["id"]
    result = _write(repo, prepared, inv)
    _end_one(repo, parked)
    return result


def _write(repo: Path, prepared: dict, inv: Invocation) -> dict:
    if prepared.get("empty"):
        return _empty(prepared)
    require_init(repo)
    state, existing = _state(repo)
    run = prepared.get("_run") or _next_run(repo, existing)
    events, markdown, specs = _events_for(prepared, _selection(inv, prepared), run, state)
    before = lint_events(existing, repo)
    after = lint_events(existing + events, repo)
    if len(after) > len(before):
        raise EngineError("Refused: " + after[0]["message"])
    append_events(repo, events)
    written = []
    for name, data in prepared.get("_originals") or []:
        rel = f"sot/{prepared['note_id']}/{name}"
        from crav1_2.paths import guarded_write

        guarded_write(repo, rel, data)
        written.append(rel)
    rebuild_views(repo)
    if inv.this_session and not prepared.get("_run"):
        write_session(repo, run, "ended", step="done", at=prepared["at"])
    return {
        "wrote": True,
        "dry_run": False,
        "note_id": prepared["note_id"],
        "note_markdown": markdown,
        "events": events,
        "ending": render_ending(specs, prepared["note_id"]),
        "card": prepared.get("card"),
        "card_text": "",
        "proposal": "",
        "parked": None,
        "paths": written,
    }


def _events_for(prepared: dict, selected: list[tuple[int, dict]], run: str, state: dict) -> tuple[list[dict], str, list[str]]:
    start = 1
    if prepared.get("extend"):
        current = state["notes"].get(prepared["note_id"]) or {}
        numbers = []
        for passage in current.get("passage_list") or []:
            match = re.search(r"(\d+)$", passage.get("id") or "")
            if match:
                numbers.append(int(match.group(1)))
        start = max(numbers, default=0) + 1
    assigned, mapping = _assign(selected, start)
    know = []
    for block in prepared.get("know") or []:
        cites = [mapping[index] for index in block.get("cites") or [] if index in mapping]
        know.append({
            "heading": block["heading"],
            "body": block["body"],
            "cites": cites,
            "inferred": not bool(cites),
        })
    note_body = {
        "note": prepared["note_id"],
        "kinds": list(prepared["kinds"]),
        "date": prepared["date"],
        "files": list(prepared.get("files") or []),
        "from_sources": _folder(prepared.get("from_sources")),
        "passages": len(assigned),
        "title": prepared["title"],
        "added_by": prepared["added_by"],
        "passage_list": assigned,
    }
    if know:
        note_body["know"] = know
    for key in ("vendor", "captured_from", "session_id", "quotes"):
        if prepared.get(key):
            note_body[key] = prepared[key]
    if prepared.get("redactions"):
        note_body["redactions"] = list(prepared["redactions"])
    if prepared.get("extend"):
        event_data = {
            "note": prepared["note_id"],
            "passages": len(assigned),
            "passage_list": assigned,
        }
        if prepared.get("files"):
            event_data["files"] = list(prepared["files"])
        if know:
            event_data["know"] = know
        event_type = "note.extended"
    else:
        event_data = note_body
        event_type = "note.added"
    # The rendered page is the full note. An extension folds onto the previous passages.
    render_source = dict(note_body)
    if prepared.get("extend"):
        previous = list((state["notes"].get(prepared["note_id"]) or {}).get("passage_list") or [])
        render_source["passage_list"] = previous + assigned
        render_source["passages"] = len(render_source["passage_list"])
        old_know = list((state["notes"].get(prepared["note_id"]) or {}).get("know") or [])
        if old_know or know:
            render_source["know"] = old_know + know
        current = state["notes"].get(prepared["note_id"]) or {}
        for key in ("vendor", "captured_from", "session_id", "quotes", "redactions", "title", "added_by", "kinds", "files", "from_sources"):
            if key in current and key not in render_source:
                render_source[key] = current[key]
        if current.get("files") and not prepared.get("files"):
            render_source["files"] = list(current["files"])
    verified = [passage for passage in assigned if passage.get("verified") is True]
    fact_ids = _next_facts(state, len(verified))
    matches = []
    for match in prepared.get("matches") or []:
        if match["index"] in mapping:
            matches.append({**match, "passage": mapping[match["index"]]})
    specs = []
    for match in matches:
        if match["spec"] not in specs:
            specs.append(match["spec"])
    count = 1 + len(verified) + len(matches)
    stamps = _stamps(prepared["at"], count, prepared.get("not_before"))
    base_ms = int(datetime.now().timestamp() * 1000)
    events = [_event(base_ms, stamps[0], run, event_type, event_data)]
    cursor = 1
    for fact_id, passage in zip(fact_ids, verified):
        events.append(_event(base_ms + cursor, stamps[cursor], run, "fact.cited", {
            "fact": fact_id,
            "note": prepared["note_id"],
            "passage": passage["id"],
            "quote": passage["quote"],
            "weak": passage.get("weak"),
        }))
        cursor += 1
    for match in matches:
        events.append(_event(base_ms + cursor, stamps[cursor], run, "answer.matched", {
            "note": prepared["note_id"],
            "passage": match["passage"],
            "spec": match["spec"],
            "question": match["question"],
        }))
        cursor += 1
    cleaned = [validate_event(event) for event in events]
    return cleaned, render_note(render_source), specs


def _event(millis: int, at: str, run: str, kind: str, data: dict) -> dict:
    return {"v": 1, "id": ulid(millis), "at": at, "by": "engine", "run": run, "type": kind, "data": data}


def _assign(selected: list[tuple[int, dict]], start: int) -> tuple[list[dict], dict[int, str]]:
    assigned = []
    mapping = {}
    number = start
    for old_index, passage in selected:
        pid = f"p-{number:03d}"
        number += 1
        body = {"id": pid, "quote": passage["quote"]}
        for key in ("kind", "who", "when", "path", "lines", "label", "verified", "weak", "answers"):
            if key in passage and passage[key] is not None:
                body[key] = passage[key]
        if "verified" in passage:
            body["verified"] = passage["verified"]
        assigned.append(body)
        mapping[old_index] = pid
    return assigned, mapping


def _selection(inv: Invocation, prepared: dict) -> list[tuple[int, dict]]:
    passages = prepared.get("passages") or []
    if inv.card == "pick-some":
        if len(inv.picks) != len(set(inv.picks)):
            raise EngineError("Refused: a line number is repeated.")
        chosen = []
        for number in inv.picks:
            if number < 1 or number > len(passages):
                raise EngineError(f"Refused: {number} is not one of the proposed lines.")
            chosen.append((number - 1, passages[number - 1]))
        if not chosen:
            raise EngineError("Refused: pick-some takes numbers, for example 1 3.")
        return chosen
    return list(enumerate(passages))


def _stamps(start: str, count: int, not_before: str | None) -> list[str]:
    base = parse_at(start)
    if not_before:
        earlier = parse_at(not_before)
        if base <= earlier:
            base = earlier + timedelta(seconds=1)
    return [(base + timedelta(seconds=offset)).isoformat() for offset in range(count)]


def _folder(value: str | None) -> str | None:
    if not value:
        return None
    return value if str(value).endswith("/") else str(value) + "/"


def _card_text(prepared: dict) -> str:
    card = prepared.get("card")
    if not card:
        return ""
    return format_card(card, why=prepared.get("why") or "", preamble=prepared.get("preamble") or "")


def _public(prepared: dict) -> dict:
    return {key: value for key, value in prepared.items() if not key.startswith("_") and key != "empty"}


def _resume(repo: Path, inv: Invocation, payload: dict) -> dict:
    parked = _load_parked(repo, inv.run_pick)
    if parked is None:
        raise EngineError(f"Refused: no parked run. {_WORDS}")
    return _finish_parked(repo, parked, inv, payload)


def _load_parked(repo: Path, run_pick: str | None) -> dict | None:
    folder = repo / ".crav1-2" / "sessions"
    if not folder.is_dir():
        if run_pick:
            raise EngineError(f"Refused: {run_pick} is not a parked run.")
        return None
    rows = []
    for path in sorted(folder.glob("s-*.json")):
        try:
            import json

            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError):
            continue
        if not isinstance(data, dict) or data.get("status") != "parked" or not isinstance(data.get("payload"), dict):
            continue
        if data["payload"].get("flow") == "link-to-spec":
            continue
        if run_pick and data.get("id") != run_pick:
            continue
        rows.append(data)
    if run_pick and not rows:
        raise EngineError(f"Refused: {run_pick} is not a parked run.")
    if len(rows) > 1:
        ids = ", ".join(str(row.get("id")) for row in rows)
        raise EngineError(f"Refused: more than one parked run: {ids}.")
    return rows[0] if rows else None


def _end_parked(repo: Path, run_pick: str | None) -> None:
    parked = _load_parked(repo, run_pick) if (repo / ".crav1-2" / "sessions").is_dir() else None
    if parked is None and run_pick is None:
        return
    if parked is None:
        return
    _end_one(repo, parked)


def _end_one(repo: Path, parked: dict) -> None:
    write_session(repo, parked["id"], "ended", step=parked.get("step") or "done", at=parked.get("at"))


def _stopped() -> dict:
    return {
        "wrote": False,
        "dry_run": False,
        "note_id": None,
        "note_markdown": "",
        "events": [],
        "ending": render_ending([], None),
        "card": None,
        "card_text": "",
        "proposal": "",
        "parked": None,
    }


def _empty(prepared: dict) -> dict:
    return {
        "wrote": False,
        "dry_run": False,
        "note_id": prepared.get("note_id"),
        "note_markdown": "",
        "events": [],
        "ending": render_ending([], None),
        "card": None,
        "card_text": "",
        "proposal": "Nothing new in this session.",
        "parked": None,
    }


def _state(repo: Path) -> tuple[dict, list[dict]]:
    if not (repo / ".crav1-2" / "engine.json").is_file():
        return empty_state(), []
    events = read_events(repo)
    return fold_events(events), events


def _next_run(repo: Path, events: list[dict]) -> str:
    nums = []
    for event in events:
        match = re.fullmatch(r"s-(\d+)", str(event.get("run") or ""))
        if match:
            nums.append(int(match.group(1)))
    folder = repo / ".crav1-2" / "sessions"
    if folder.is_dir():
        for path in folder.glob("s-*.json"):
            match = re.fullmatch(r"s-(\d+)", path.stem)
            if match:
                nums.append(int(match.group(1)))
    return f"s-{max(nums, default=0) + 1:04d}"


def _line(value: object, key: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or "\n" in value or "\r" in value or value.strip() == "":
        raise EngineError(f"Refused: {key} must be a single line.")
    return value
