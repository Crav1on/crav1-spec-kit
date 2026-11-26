"""link-to-spec: read unread SoT notes against one 1.x spec.

The engine checks the gap-finder JSON, builds the cards, and writes events
and crav1-2 item lines. It does not commit. dry-run writes nothing. park and
resume use the session file.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path

from crav1_2.cards import card_problems
from crav1_2.ending import render_settled
from crav1_2.errors import EngineError
from crav1_2.fold import fold_events
from crav1_2.lines import line_has_mark, one_x_lines_unchanged
from crav1_2.lint import lint_events
from crav1_2.notes import render_note
from crav1_2.repo import append_events, read_events, rebuild_views, require_init
from crav1_2.schema import (
    HYPHEN_WORD,
    NOTE_ID,
    RUN_ID,
    SPEC_SLUG,
    WEAK,
    must_on_assumption,
    now_iso,
    parse_at,
    validate_event,
)
from crav1_2.sessions import write_session
from crav1_2.spec_edit import (
    anchor_for,
    answered_block,
    bullet_block,
    insert_sorted,
    insert_under_question,
    insert_waits,
    see_also_line,
    sort_key,
    waits_line,
)
from crav1_2.ulid import ulid
from crav1_2.views import render_decisions

_WORDS = "Words: none, note-<id>, dry-run, resume, park."
_NOTE = re.compile(r"^note-(\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*)$")
_ANSWERS = {
    "skip", "close-all", "pick-some", "accept-all", "change-some",
    "add-pointer", "open-question", "leave-out", "prefer-source",
    "keep-spec", "ask-owner", "use-proposed",
}
_WRITE = {"add-pointer", "prefer-source", "use-proposed"}
_ASK = {"open-question", "ask-owner"}
_LEAVE = {"leave-out", "keep-spec", "skip"}
_GAP_OPTIONS = {
    "silent": (
        ("add-pointer", "Write the proposed line into that section.", "A later run can unlink that item."),
        ("open-question", "Write it as an open question.", "A later run can unlink that item."),
        ("leave-out", "Record the gap and write no line.", "Run link-to-spec on this note again."),
    ),
    "conflicting": (
        ("prefer-source", "Write the proposed line and leave the current line.", "A later run can unlink that item."),
        ("keep-spec", "Leave the current line and write no line.", "Run link-to-spec on this note again."),
        ("ask-owner", "Write an open question and leave the current line.", "A later run can unlink that item."),
    ),
    "vague": (
        ("use-proposed", "Write the proposed line.", "A later run can unlink that item."),
        ("ask-owner", "Write an open question.", "A later run can unlink that item."),
        ("leave-out", "Record the gap and write no line.", "Run link-to-spec on this note again."),
    ),
}
_RECOMMENDED = {"silent": "add-pointer", "conflicting": "prefer-source", "vague": "use-proposed"}
_FINDER_KEYS = {"items"}
_ITEM_KEYS = {
    "status", "note", "passages", "impact", "uncertainty", "holds",
    "file", "section", "text", "who", "question", "attach", "weak",
}
_PAYLOAD_KEYS = {"at", "finder"}


@dataclass
class Invocation:
    slug: str | None = None
    note_id: str | None = None
    dry_run: bool = False
    resume: bool = False
    park: bool = False
    explicit_none: bool = False
    answer: str | None = None
    picks: list[int] = field(default_factory=list)
    run_pick: str | None = None


def parse_invocation(words: list[str]) -> Invocation:
    inv = Invocation()
    for word in words:
        if word == "none":
            inv.explicit_none = True
            continue
        if word == "dry-run":
            inv.dry_run = True
            continue
        if word == "resume":
            inv.resume = True
            continue
        if word == "park":
            inv.park = True
            continue
        match = _NOTE.fullmatch(word)
        if match:
            if inv.note_id:
                raise EngineError("Refused: note-<id> is given twice.")
            inv.note_id = match.group(1)
            continue
        if re.fullmatch(r"\d+", word):
            inv.picks.append(int(word))
            continue
        if isinstance(word, str) and RUN_ID.fullmatch(word):
            if inv.run_pick:
                raise EngineError("Refused: the session id is given twice.")
            inv.run_pick = word
            continue
        if word in _ANSWERS:
            if inv.answer and inv.answer != word:
                raise EngineError("Refused: the card word is given twice and they differ.")
            inv.answer = word
            continue
        if isinstance(word, str) and SPEC_SLUG.fullmatch(word):
            if inv.slug and inv.slug != word:
                raise EngineError("Refused: the spec slug is given twice and they differ.")
            if not inv.slug:
                inv.slug = word
                continue
        raise EngineError(f"Refused: unknown word {word}. {_WORDS}")
    if inv.note_id and inv.explicit_none:
        raise EngineError("Refused: none and note-<id> are different reads.")
    if inv.resume and inv.park:
        raise EngineError("Refused: resume and park are different steps.")
    if inv.dry_run and inv.answer:
        raise EngineError("Refused: dry-run writes nothing and takes no card word.")
    if inv.picks and inv.answer not in {"pick-some", "change-some"}:
        raise EngineError("Refused: a number needs pick-some or change-some.")
    if not inv.slug and not inv.resume and not inv.park and not inv.answer:
        raise EngineError(f"Refused: a spec slug is missing. {_WORDS}")
    return inv


def link_to_spec(repo: Path, words: list[str], payload: dict | None) -> dict:
    inv = parse_invocation(words)
    payload = _payload(payload)
    if inv.resume or (inv.answer and "finder" not in payload) or (inv.park and "finder" not in payload):
        return _continue(repo, inv)
    if not inv.slug:
        raise EngineError(f"Refused: a spec slug is missing. {_WORDS}")
    require_init(repo)
    if "finder" not in payload:
        return _packet(repo, inv)
    plan = _build_plan(repo, inv, payload)
    if inv.dry_run:
        return _preview(plan)
    if not plan["cards"]:
        return _finalize(repo, _shell(repo, plan, parked=False), [])
    session = _save(repo, plan, parked=inv.park, previous=None)
    if inv.answer:
        return _apply(repo, session, inv)
    return _show(session)


def _payload(payload: dict | None) -> dict:
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        raise EngineError("Refused: link-to-spec reads one JSON object.")
    extra = set(payload) - _PAYLOAD_KEYS
    if extra:
        raise EngineError(f"Refused: unknown field {sorted(extra)[0]}.")
    if "at" in payload:
        try:
            parse_at(payload["at"])
        except EngineError as exc:
            raise EngineError("Refused: at must be an ISO time with a numeric offset.") from exc
    return payload


def _continue(repo: Path, inv: Invocation) -> dict:
    require_init(repo)
    if inv.resume:
        session = _load(repo, "parked", inv.run_pick)
        if inv.dry_run:
            return _preview(session["payload"]["plan"])
        if inv.answer:
            return _apply(repo, session, inv)
        return _show(session)
    if inv.park and not inv.answer:
        session = _load(repo, "open", inv.run_pick)
        saved = _save(repo, session["payload"]["plan"], parked=True, previous=session)
        return _show(saved)
    session = _load(repo, "open", inv.run_pick, missing_ok=True)
    if session is None:
        parked = _load(repo, "parked", inv.run_pick, missing_ok=True)
        if parked is not None:
            raise EngineError("Refused: that run is parked. Say resume.")
        raise EngineError("Refused: no open link-to-spec run.")
    return _apply(repo, session, inv)


def _packet(repo: Path, inv: Invocation) -> dict:
    state, _events = _state(repo)
    spec_text = _spec_text(repo, inv.slug)
    notes = _select_notes(state, inv)
    if not notes:
        return _empty(inv.slug, inv.dry_run)
    packet_notes = []
    for note in notes:
        packet_notes.append({"note": note["note"], "markdown": _note_text(repo, note)})
    tasks = repo / "docs" / "specs" / inv.slug / "tasks.md"
    return {
        "wrote": False,
        "dry_run": inv.dry_run,
        "needs_finder": True,
        "spec": inv.slug,
        "ending": None,
        "card_text": "",
        "cards": [],
        "proposed_items": [],
        "parked": None,
        "session": None,
        "events": [],
        "notes": packet_notes,
        "spec_markdown": spec_text,
        "decisions_markdown": render_decisions(state),
        "tasks_markdown": tasks.read_text(encoding="utf-8") if tasks.is_file() else "",
    }


def _empty(slug: str, dry_run: bool = False) -> dict:
    return {
        "wrote": False,
        "dry_run": dry_run,
        "needs_finder": False,
        "spec": slug,
        "ending": render_settled(None),
        "card_text": "",
        "cards": [],
        "proposed_items": [],
        "parked": None,
        "session": None,
        "events": [],
    }


def _build_plan(repo: Path, inv: Invocation, payload: dict) -> dict:
    state, events = _state(repo)
    _spec_text(repo, inv.slug)
    selected = _select_notes(state, inv)
    if inv.note_id and not selected:
        raise EngineError(f"Refused: {inv.note_id} is not a note.")
    allowed = {note["note"] for note in selected}
    if not allowed:
        raise EngineError("Refused: no unread note for that spec.")
    finder = payload.get("finder")
    if not isinstance(finder, dict) or set(finder) - _FINDER_KEYS:
        raise EngineError("Refused: finder must be an object with items.")
    rows = finder.get("items")
    if not isinstance(rows, list):
        raise EngineError("Refused: finder items must be a list.")
    at = payload.get("at") or now_iso()
    at = _after(at, events)
    ids = _Ids(state)
    facts: list[dict] = []

    def cite(note_id: str, passage_id: str, hint: str | None) -> tuple[str, str | None]:
        if note_id not in allowed and note_id not in {note["note"] for note in state["notes"].values()}:
            raise EngineError(f"Refused: {note_id} is not a note.")
        if allowed and note_id not in allowed:
            raise EngineError(f"Refused: {note_id} is not in this read.")
        passage = _passage(state, note_id, passage_id)
        weak = passage.get("weak") if "weak" in passage else hint
        if weak is not None and weak not in WEAK:
            raise EngineError("Refused: weak must be verbal, unmerged, ai-summary, inferred, or null.")
        for row in facts:
            if row["note"] == note_id and row["passage"] == passage_id:
                return row["fact"], row["weak"]
        existing = _existing_fact(state, note_id, passage_id, passage["quote"])
        if existing:
            known = state["facts"][existing]
            facts.append({
                "fact": existing, "note": note_id, "passage": passage_id,
                "quote": passage["quote"], "weak": known.get("weak"), "new": False,
            })
            return existing, known.get("weak")
        ident = ids.take("F")
        facts.append({
            "fact": ident, "note": note_id, "passage": passage_id,
            "quote": passage["quote"], "weak": weak, "new": True,
        })
        return ident, weak

    gaps = []
    for raw in rows:
        gaps.append(_gap_from(raw, cite, ids, inv.slug))
    gaps = [gap for gap in gaps if not gap.get("covered")]
    answers = _answer_rows(state, inv.slug, allowed, cite)
    cards = _cards(gaps, answers, ids)
    return {
        "spec": inv.slug,
        "notes": sorted(allowed),
        "at": at,
        "facts": facts,
        "gaps": gaps,
        "answers": answers,
        "cards": cards,
        "reserved": sorted(ids.taken),
    }


def _gap_from(raw: object, cite, ids: "_Ids", spec: str) -> dict:
    if not isinstance(raw, dict):
        raise EngineError("Refused: a finder item must be an object.")
    extra = set(raw) - _ITEM_KEYS
    if extra:
        raise EngineError(f"Refused: unknown finder field {sorted(extra)[0]}.")
    status = raw.get("status")
    if status not in {"covered", "silent", "conflicting", "vague"}:
        raise EngineError("Refused: status must be covered, silent, conflicting, or vague.")
    note_id = raw.get("note")
    if not isinstance(note_id, str) or not NOTE_ID.fullmatch(note_id):
        raise EngineError("Refused: a finder item needs a note id.")
    passages = raw.get("passages")
    if not isinstance(passages, list) or any(not isinstance(item, str) for item in passages):
        raise EngineError("Refused: passages must be a list of passage ids.")
    hint = raw.get("weak") if "weak" in raw else None
    if status == "covered" and not passages:
        return {"covered": True}
    if status != "covered" and not passages:
        raise EngineError("Refused: a gap cites a passage.")
    cited = [cite(note_id, passage, hint) for passage in passages]
    if status == "covered":
        return {"covered": True}
    impact = raw.get("impact")
    uncertainty = raw.get("uncertainty")
    if impact not in (1, 2, 3) or uncertainty not in (1, 2, 3):
        raise EngineError("Refused: impact and uncertainty must be 1, 2, or 3.")
    holds = raw.get("holds") if "holds" in raw else []
    if not isinstance(holds, list) or any(not isinstance(item, str) or not re.fullmatch(r"T\d+", item) for item in holds):
        raise EngineError("Refused: holds must be a list of task ids like T12.")
    file_name = raw.get("file") or "spec.md"
    if file_name not in {"spec.md", "plan.md"}:
        raise EngineError("Refused: a finder item writes spec.md or plan.md. Phase 1 adds no tasks.")
    section = raw.get("section")
    text = raw.get("text")
    if not isinstance(section, str) or not section.strip() or "\n" in section:
        raise EngineError("Refused: a gap needs a section.")
    if not isinstance(text, str) or not text.strip() or "\n" in text or "\r" in text:
        raise EngineError("Refused: a gap needs proposed text on one line.")
    if line_has_mark(text) or line_has_mark(section):
        raise EngineError("Refused: proposed text would write a 1.x mark.")
    attach = raw.get("attach") or "new"
    if attach not in {"new", "see-also"}:
        raise EngineError("Refused: attach must be new or see-also.")
    question = raw.get("question")
    if attach == "see-also" and (not isinstance(question, str) or not question.strip()):
        raise EngineError("Refused: see-also names the open question.")
    if question is not None and (not isinstance(question, str) or "\n" in question):
        raise EngineError("Refused: question must be a single line.")
    who = raw.get("who") or "the spec owner"
    if not isinstance(who, str) or not who.strip() or "\n" in who:
        raise EngineError("Refused: who must be a single line.")
    fact_ids = [item[0] for item in cited]
    weaks = {item[1] for item in cited}
    weak = next(iter(weaks)) if len(weaks) == 1 else None
    low = impact == 1 and not must_on_assumption("asm", text)
    return {
        "covered": False,
        "gap": ids.take("G"),
        "spec": spec,
        "kind": status,
        "impact": impact,
        "uncertainty": uncertainty,
        "holds": list(holds),
        "facts": fact_ids,
        "file": file_name,
        "section": section.strip(),
        "text": text.strip(),
        "attach": attach,
        "question": question.strip() if isinstance(question, str) else None,
        "who": who.strip(),
        "weak": weak,
        "low": low,
    }


def _answer_rows(state: dict, spec: str, allowed: set[str], cite) -> list[dict]:
    closed = _closed(state)
    rows = []
    seen = set()
    for answer in state["answers"]:
        if answer["spec"] != spec:
            continue
        if answer["note"] not in allowed:
            continue
        key = sort_key(answer["question"])
        if key in closed or key in seen:
            continue
        seen.add(key)
        fact, _weak = cite(answer["note"], answer["passage"], None)
        passage = _passage(state, answer["note"], answer["passage"])
        note = state["notes"][answer["note"]]
        kinds = list(note.get("kinds") or [])
        kind = "session" if "session" in kinds else (kinds[0] if kinds else "note")
        rows.append({
            "note": answer["note"],
            "passage": answer["passage"],
            "question": answer["question"],
            "quote": passage["quote"],
            "who": passage.get("who") or "person A",
            "date": note.get("date") or answer["note"][:10],
            "kind": kind,
            "fact": fact,
        })
    return rows


def _cards(gaps: list[dict], answers: list[dict], ids: "_Ids") -> list[dict]:
    real = [gap for gap in gaps if not gap.get("covered")]
    high = [gap for gap in real if not gap["low"]]
    low = [gap for gap in real if gap["low"]]
    high.sort(key=lambda gap: (-(gap["impact"] * gap["uncertainty"]), -gap["impact"], gap["gap"]))
    low.sort(key=lambda gap: gap["gap"])
    cards = [_gap_card(gap, ids) for gap in high]
    if low:
        cards.append(_assumption_card(low, ids))
    if answers:
        cards.append(_answer_card(answers, ids))
    for card in cards:
        problems = card_problems(card["card"])
        if problems:
            raise EngineError("Refused: " + problems[0])
    return cards


def _gap_card(gap: dict, ids: "_Ids") -> dict:
    options = [_option(*row) for row in _GAP_OPTIONS[gap["kind"]]]
    card = _backed(
        f"What should the spec do with this {gap['kind']} gap?",
        options,
        _RECOMMENDED[gap["kind"]] if gap["facts"] else None,
        gap["facts"],
        gap["who"],
        "No cited passage backs a recommendation for this gap.",
    )
    holds = ", ".join(gap["holds"]) if gap["holds"] else "none"
    preamble = (
        f"Impact {gap['impact']}, uncertainty {gap['uncertainty']}, holds {holds}.\n"
        f"Proposed: {gap['text']}"
    )
    entry = {
        "role": "gap",
        "card_id": ids.take("C"),
        "gap": gap["gap"],
        "gap_ids": [gap["gap"]],
        "card": card,
        "preamble": preamble,
        "proposed": [],
    }
    entry["card_text"] = _render(card, preamble)
    entry["proposed"] = _preview_lines(gap, card.get("recommended"))
    return entry


def _assumption_card(gaps: list[dict], ids: "_Ids") -> dict:
    facts = []
    for gap in gaps:
        for fact in gap["facts"]:
            if fact not in facts:
                facts.append(fact)
    options = [
        _option("accept-all", "Record every assumption and write the lines.", "A later fact can close an assumption."),
        _option("change-some", "Record only the numbered assumptions.", "Run link-to-spec again for one you left out."),
        _option("skip", "Record none of them.", "Resume and choose accept-all."),
    ]
    who = gaps[0]["who"]
    card = _backed(
        "These low-impact gaps can be recorded as assumptions.",
        options,
        "accept-all" if facts else None,
        facts,
        who,
        "No cited passage backs these assumptions.",
    )
    lines = [f"{number}. {gap['text']}" for number, gap in enumerate(gaps, 1)]
    preamble = "Assumptions:\n" + "\n".join(lines)
    entry = {
        "role": "assumptions",
        "card_id": ids.take("C"),
        "gap": gaps[0]["gap"],
        "gap_ids": [gap["gap"] for gap in gaps],
        "card": card,
        "preamble": preamble,
        "proposed": [],
    }
    entry["card_text"] = _render(card, preamble)
    entry["proposed"] = []
    for gap in gaps:
        entry["proposed"].extend(_preview_lines(gap, "accept-all"))
    return entry


def _answer_card(answers: list[dict], ids: "_Ids") -> dict:
    facts = []
    for answer in answers:
        if answer["fact"] not in facts:
            facts.append(answer["fact"])
    count = len(answers)
    options = [
        _option("close-all", "Close every listed question and write Answered.", "The questions stay open if you skip."),
        _option("pick-some", "Close only the numbered questions.", "Run link-to-spec again for one you left open."),
        _option("skip", "Leave the questions open.", "Resume and choose close-all."),
    ]
    who = answers[0]["who"]
    card = _backed(
        f"These {count} open questions have answers in the SoT",
        options,
        "close-all" if facts else None,
        facts,
        who,
        "No cited passage backs these answers.",
    )
    lines = []
    for number, answer in enumerate(answers, 1):
        lines.append(f"{number}. {answer['question']}")
        lines.append(f"   \"{answer['quote']}\"")
    entry = {
        "role": "answers",
        "card_id": ids.take("C"),
        "gap": None,
        "gap_ids": [],
        "answer_gap": ids.take("G"),
        "card": card,
        "preamble": "\n".join(lines),
        "proposed": [_answered_preview(answer) for answer in answers],
    }
    entry["card_text"] = _render(card, entry["preamble"])
    return entry


def _backed(question: str, options: list[dict], recommended: str | None, facts: list[str], who: str, missing: str) -> dict:
    card = {"question": question, "options": options, "recommended": None}
    if recommended and facts:
        card["recommended"] = recommended
        card["facts"] = list(facts)
    else:
        card["recommended"] = None
        card["missing_fact"] = f"{missing} {who} could give it."
    return card


def _option(word: str, impact: str, undo: str) -> dict:
    if not HYPHEN_WORD.fullmatch(word):
        raise EngineError("Refused: an option word is hyphen-only.")
    return {"word": word, "impact": impact, "undo": undo}


def _end(text: str) -> str:
    body = text.rstrip()
    if body.endswith((".", "?", "!")):
        return body
    return body + "."


def _render(card: dict, preamble: str) -> str:
    lines = []
    if preamble.strip():
        lines.append(preamble.rstrip())
        lines.append("")
    lines.append("Card: " + card["question"])
    options = list(card["options"])
    recommended = card.get("recommended")
    if recommended:
        options.sort(key=lambda option: option["word"] != recommended)
    words = {option["word"] for option in card["options"]}
    for option in options:
        label = " ".join(part.capitalize() for part in option["word"].split("-"))
        impact = _end(option["impact"])
        undo = _end(option["undo"])
        if option["word"] == recommended:
            facts = ", ".join(card.get("facts") or [])
            why = f"{facts} is cited in the note" if len(card.get("facts") or []) == 1 else f"{facts} are cited in the note"
            lines.append(
                f"- **{label} (Recommended)** (`{option['word']}`): {impact} Undo: {undo} Why: {why}."
            )
        elif option["word"] in {"pick-some", "change-some"}:
            lines.append(
                f"- **{label}** (`{option['word']}`): {impact} Type the numbers, e.g. 1 3. Undo: {undo}"
            )
        else:
            lines.append(f"- **{label}** (`{option['word']}`): {impact} Undo: {undo}")
    if "skip" not in words:
        lines.append("- **Skip** (`skip`): Leave this for later. Undo: Resume and answer it.")
    if not recommended:
        lines.append("Missing fact: " + card["missing_fact"])
    return "\n".join(lines) + "\n"


def _preview_lines(gap: dict, word: str | None) -> list[dict]:
    if word in _LEAVE or word is None:
        return []
    if word in _ASK or (word == "accept-all"):
        return [_item_preview(gap, word)]
    if word in _WRITE or word == "accept-all":
        return [_item_preview(gap, word)]
    return []


def _item_preview(gap: dict, word: str) -> dict:
    origin = "asm" if word == "accept-all" else "src"
    return {
        "file": f"docs/specs/{gap['spec']}/{gap['file']}" if "spec" in gap else gap["file"],
        "origin": origin,
        "text": gap["text"],
        "section": "Open questions" if word in _ASK else gap["section"],
    }


def _answered_preview(answer: dict) -> dict:
    return {
        "file": "spec.md",
        "origin": "dec",
        "text": answer["question"],
        "section": "Open questions",
    }


def _preview(plan: dict) -> dict:
    texts = [card["card_text"] for card in plan["cards"]]
    proposed = []
    for card in plan["cards"]:
        proposed.extend(card["proposed"])
    return {
        "wrote": False,
        "dry_run": True,
        "needs_finder": False,
        "spec": plan["spec"],
        "ending": None,
        "card_text": texts[0] if texts else "",
        "cards": texts,
        "proposed_items": proposed,
        "parked": None,
        "session": None,
        "events": [],
    }


def _shell(repo: Path, plan: dict, *, parked: bool) -> dict:
    state, events = _state(repo)
    run = _next_run(repo, events)
    body = write_session(
        repo, run, "parked" if parked else "open", step="card" if plan["cards"] else "done",
        at=plan["at"], payload={"flow": "link-to-spec", "spec": plan["spec"], "plan": plan, "cursor": 0, "choices": []},
    )
    return body


def _save(repo: Path, plan: dict, *, parked: bool, previous: dict | None) -> dict:
    if previous is None:
        return _shell(repo, plan, parked=parked)
    payload = dict(previous["payload"])
    payload["plan"] = plan
    body = write_session(
        repo, previous["id"], "parked" if parked else previous["status"],
        step=previous.get("step") or "card", left=previous.get("left") or [],
        at=plan["at"], payload=payload,
    )
    return body


def _show(session: dict) -> dict:
    plan = session["payload"]["plan"]
    cursor = session["payload"]["cursor"]
    card = plan["cards"][cursor]
    parked = session["id"] if session["status"] == "parked" else None
    return {
        "wrote": False,
        "dry_run": False,
        "needs_finder": False,
        "spec": plan["spec"],
        "ending": None,
        "card_text": card["card_text"],
        "cards": [card["card_text"]],
        "proposed_items": card["proposed"],
        "parked": parked,
        "session": session["id"],
        "events": [],
    }


def _apply(repo: Path, session: dict, inv: Invocation) -> dict:
    payload = session["payload"]
    plan = payload["plan"]
    cursor = payload["cursor"]
    if cursor >= len(plan["cards"]):
        return _finalize(repo, session, payload["choices"])
    card = plan["cards"][cursor]
    _check_answer(card, inv)
    payload["choices"].append({"index": cursor, "word": inv.answer, "picks": list(inv.picks)})
    payload["cursor"] = cursor + 1
    status = session["status"]
    saved = write_session(
        repo, session["id"], status, step="card", at=plan["at"], payload=payload,
    )
    if payload["cursor"] >= len(plan["cards"]):
        return _finalize(repo, saved, payload["choices"])
    return _show(saved)


def _check_answer(card: dict, inv: Invocation) -> None:
    if not inv.answer:
        raise EngineError("Refused: the card needs a word.")
    words = [option["word"] for option in card["card"]["options"]]
    allowed = set(words)
    allowed.add("skip")
    if inv.answer not in allowed:
        listed = ", ".join(words + (["skip"] if "skip" not in words else []))
        raise EngineError(f"Refused: {inv.answer} is not an option on this card. Words: {listed}.")
    if inv.answer in {"pick-some", "change-some"} and not inv.picks:
        raise EngineError(f"Refused: {inv.answer} takes numbers, for example 1 3.")
    if inv.picks and inv.answer not in {"pick-some", "change-some"}:
        raise EngineError("Refused: a number needs pick-some or change-some.")


def _finalize(repo: Path, session: dict, choices: list[dict]) -> dict:
    plan = session["payload"]["plan"]
    state, existing = _state(repo)
    ids = _Ids(state, plan.get("reserved") or [])
    built = _effects(repo, plan, choices, ids)
    events = _events(plan, built, session["id"])
    for event in events:
        validate_event(event)
    before = lint_events(existing, repo)
    after = lint_events(existing + [validate_event(event) for event in events], repo)
    fresh = [row for row in after if row not in before]
    if fresh:
        raise EngineError("Refused: " + fresh[0]["message"])
    _commit_files(repo, built["files"])
    if events:
        append_events(repo, events)
    rebuild_views(repo)
    write_session(repo, session["id"], "ended", step="done", left=built["left"], at=plan["at"], payload=session["payload"])
    recorded = _recorded(built, plan["spec"])
    return {
        "wrote": True,
        "dry_run": False,
        "needs_finder": False,
        "spec": plan["spec"],
        "ending": render_settled(recorded),
        "card_text": "",
        "cards": [],
        "proposed_items": built["written"],
        "parked": None,
        "session": session["id"],
        "events": [validate_event(event) for event in events],
    }


def _effects(repo: Path, plan: dict, choices: list[dict], ids: "_Ids") -> dict:
    files: dict[str, str] = {}
    extras: list[tuple[str, dict]] = []
    written = []
    left = []
    gaps = {gap["gap"]: gap for gap in plan["gaps"] if not gap.get("covered")}
    choice_by_index = {choice["index"]: choice for choice in choices}

    def text_of(rel: str) -> str:
        if rel not in files:
            path = repo / rel
            if not path.is_file():
                raise EngineError(f"Refused: {rel} is a 1.x file kit 2.0 does not create.")
            files[rel] = path.read_text(encoding="utf-8")
        return files[rel]

    def put(rel: str, updated: str) -> None:
        files[rel] = updated

    for index, card in enumerate(plan["cards"]):
        choice = choice_by_index.get(index)
        word = choice["word"] if choice else "skip"
        picks = choice["picks"] if choice else []
        if word == "skip":
            left.append(card["card_id"])
            continue
        if card["role"] == "gap":
            _apply_gap(card, gaps[card["gap"]], word, ids, plan, extras, written, text_of, put)
        elif card["role"] == "assumptions":
            chosen = _picked(card, picks, word)
            _apply_assumptions(card, [gaps[gid] for gid in chosen], word, ids, plan, extras, written, text_of, put)
        elif card["role"] == "answers":
            chosen_answers = _picked_answers(plan, card, picks, word)
            _apply_answers(card, chosen_answers, word, ids, plan, extras, written, text_of, put)
    return {"files": files, "extras": extras, "written": written, "left": left}


def _picked(card: dict, picks: list[int], word: str) -> list[str]:
    gap_ids = card["gap_ids"]
    if word == "accept-all":
        return list(gap_ids)
    if len(picks) != len(set(picks)):
        raise EngineError("Refused: a number is repeated.")
    chosen = []
    for number in picks:
        if number < 1 or number > len(gap_ids):
            raise EngineError(f"Refused: {number} is not one of the assumptions.")
        chosen.append(gap_ids[number - 1])
    return chosen


def _picked_answers(plan: dict, card: dict, picks: list[int], word: str) -> list[dict]:
    rows = plan["answers"]
    if word == "close-all":
        return list(rows)
    if len(picks) != len(set(picks)):
        raise EngineError("Refused: a number is repeated.")
    chosen = []
    for number in picks:
        if number < 1 or number > len(rows):
            raise EngineError(f"Refused: {number} is not one of the questions.")
        chosen.append(rows[number - 1])
    return chosen


def _apply_gap(card, gap, word, ids, plan, extras, written, text_of, put) -> None:
    if word in _LEAVE:
        if gap["holds"]:
            _decision(extras, ids, card, word, plan, gap["facts"], gap["holds"], "No line was written.", "The current line stays.")
        return
    item = ids.take("I")
    if word in _ASK:
        _write_question(gap, item, "src", gap["facts"], plan, written, text_of, put)
        affects = [item, *gap["holds"]]
        decision = _decision(extras, ids, card, word, plan, gap["facts"], affects, "The question is in the spec.", "An open question was written.")
        for task in gap["holds"]:
            _write_waits(plan, task, decision, ids, written, text_of, put, extras)
        return
    if gap["attach"] == "see-also" and gap.get("question"):
        _write_see_also(gap, item, plan, written, text_of, put)
    else:
        _write_bullet(gap, item, "src", gap["facts"], gap["section"], gap["file"], None, plan, written, text_of, put)
    affects = [item, *gap["holds"]]
    _decision(extras, ids, card, word, plan, gap["facts"], affects, "The item is in the spec.", "The proposed line is written.")


def _apply_assumptions(card, gaps, word, ids, plan, extras, written, text_of, put) -> None:
    if not gaps:
        raise EngineError("Refused: change-some takes numbers, for example 1 3.")
    items = []
    facts = []
    for gap in gaps:
        if must_on_assumption("asm", gap["text"]):
            raise EngineError("Refused: MUST is not allowed on an asm item.")
        item = ids.take("I")
        assumption = ids.take("A")
        extras.append(("assumption.recorded", {
            "assumption": assumption,
            "gap": gap["gap"],
            "text": gap["text"],
            "owner": gap["who"],
            "confirms_if": "A later source cites the same passage.",
            "breaks_if": "A later source contradicts the passage.",
        }))
        blocks = "none" if gap["section"] == "Open questions" else None
        _write_bullet(gap, item, "asm", [assumption], gap["section"], gap["file"], blocks, plan, written, text_of, put, text=gap["text"])
        items.append(item)
        for fact in gap["facts"]:
            if fact not in facts:
                facts.append(fact)
    _decision(
        extras, ids, card, word, plan, facts, items,
        "The assumptions are recorded.",
        "The assumption lines are in the spec.",
    )


def _apply_answers(card, answers, word, ids, plan, extras, written, text_of, put) -> None:
    if not answers:
        raise EngineError("Refused: pick-some takes numbers, for example 1 3.")
    over = [option["word"] for option in card["card"]["options"] if option["word"] != word]
    for answer in answers:
        item = ids.take("I")
        decision = ids.take("D")
        extras.append(("decision.recorded", {
            "decision": decision,
            "card": card["card_id"],
            "chosen": word,
            "over": over,
            "accepting": answer["question"],
            "facts": [answer["fact"]],
            "affects": [item],
            "check": "The question shows Answered.",
        }))
        sentence = _sentence(answer)
        weak = _fact_weak(plan, answer["fact"])
        lines = answered_block(sentence, "dec", [decision], weak, item, anchor_for(answer["fact"]))
        rel = f"docs/specs/{plan['spec']}/spec.md"
        put(rel, insert_under_question(text_of(rel), answer["question"], lines))
        extras.append(("item.linked", {
            "item": item,
            "spec": plan["spec"],
            "file": "spec.md",
            "section": "Open questions",
            "text": sentence,
            "origin": "dec",
            "refs": [decision],
        }))
        written.append({"file": rel, "item": item, "origin": "dec", "text": sentence, "preview": "\n".join(lines)})


def _write_bullet(gap, item, origin, refs, section, file_name, blocks, plan, written, text_of, put, text=None) -> None:
    prose = text if text is not None else gap["text"]
    weak = gap.get("weak") if origin == "src" else None
    anchor = anchor_for(gap["facts"][0]) if origin == "asm" and gap.get("facts") else anchor_for(refs[0])
    block_lines = bullet_block(prose, origin, refs, weak, item, blocks=blocks, anchor=anchor)
    rel = f"docs/specs/{plan['spec']}/{file_name}"
    put(rel, insert_sorted(text_of(rel), section, block_lines, sort_key(prose)))
    extras_item = {
        "item": item,
        "spec": plan["spec"],
        "file": file_name,
        "section": section,
        "text": prose,
        "origin": origin,
        "refs": list(refs),
    }
    written.append({"file": rel, "item": item, "origin": origin, "text": prose, "preview": "\n".join(block_lines)})
    gap.setdefault("_items", []).append(extras_item)


def _write_question(gap, item, origin, refs, plan, written, text_of, put) -> None:
    holds = ", ".join(gap["holds"]) if gap["holds"] else "none"
    saved_section, saved_file = gap["section"], gap["file"]
    gap["section"], gap["file"] = "Open questions", "spec.md"
    _write_bullet(gap, item, origin, refs, "Open questions", "spec.md", holds, plan, written, text_of, put)
    gap["section"], gap["file"] = saved_section, saved_file


def _write_see_also(gap, item, plan, written, text_of, put) -> None:
    anchor = anchor_for(gap["facts"][0])
    line = see_also_line(anchor, "src", gap["facts"], gap.get("weak"), item)
    rel = f"docs/specs/{plan['spec']}/spec.md"
    put(rel, insert_under_question(text_of(rel), gap["question"], [line]))
    gap.setdefault("_items", []).append({
        "item": item,
        "spec": plan["spec"],
        "file": "spec.md",
        "section": "Open questions",
        "text": f"See also: {anchor}",
        "origin": "src",
        "refs": list(gap["facts"]),
    })
    written.append({"file": rel, "item": item, "origin": "src", "text": gap["text"], "preview": line})


def _write_waits(plan, task, decision, ids, written, text_of, put, extras) -> None:
    item = ids.take("I")
    line = waits_line(decision, item)
    rel = f"docs/specs/{plan['spec']}/tasks.md"
    try:
        current = text_of(rel)
    except EngineError:
        return
    updated = insert_waits(current, task, line)
    if updated is None:
        return
    put(rel, updated)
    extras.append(("item.linked", {
        "item": item,
        "spec": plan["spec"],
        "file": "tasks.md",
        "section": "Tasks",
        "text": f"Waits on: {decision}",
        "origin": "dec",
        "refs": [decision],
    }))
    written.append({"file": rel, "item": item, "origin": "dec", "text": f"Waits on: {decision}", "preview": line})


def _decision(extras, ids, card, word, plan, facts, affects, check, accepting) -> str:
    if not facts or not affects:
        return ""
    decision = ids.take("D")
    over = [option["word"] for option in card["card"]["options"] if option["word"] != word]
    if word == "skip":
        over = [option["word"] for option in card["card"]["options"]]
    extras.append(("decision.recorded", {
        "decision": decision,
        "card": card["card_id"],
        "chosen": word,
        "over": over,
        "accepting": accepting,
        "facts": list(facts),
        "affects": list(affects),
        "check": check,
    }))
    return decision


def _events(plan: dict, built: dict, run: str) -> list[dict]:
    rows: list[tuple[str, dict]] = []
    for fact in plan["facts"]:
        if not fact["new"]:
            continue
        rows.append(("fact.cited", {
            "fact": fact["fact"], "note": fact["note"], "passage": fact["passage"],
            "quote": fact["quote"], "weak": fact["weak"],
        }))
    for gap in plan["gaps"]:
        if gap.get("covered"):
            continue
        rows.append(("gap.found", {
            "gap": gap["gap"], "spec": plan["spec"], "kind": gap["kind"], "facts": list(gap["facts"]),
            "impact": gap["impact"], "uncertainty": gap["uncertainty"], "holds": list(gap["holds"]),
        }))
    for card in plan["cards"]:
        if card["role"] == "answers":
            facts = list(card["card"].get("facts") or [])
            if not facts:
                continue
            rows.append(("gap.found", {
                "gap": card["answer_gap"], "spec": plan["spec"], "kind": "vague", "facts": facts,
                "impact": 2, "uncertainty": 1, "holds": [],
            }))
            card["gap"] = card["answer_gap"]
        rows.append(("card.asked", _card_event(card)))
    for gap in plan["gaps"]:
        for item in gap.get("_items") or []:
            rows.append(("item.linked", item))
    rows.extend(built["extras"])
    for note_id in plan["notes"]:
        rows.append(("note.read", {"note": note_id, "spec": plan["spec"]}))
    rows.append(("run.ended", {"step": "done", "left": list(built["left"])}))
    # Item events were appended before extras, but a decision must exist for a
    # dec item and an assumption must exist for an asm item. Lint uses the
    # whole list, so order does not matter. Fold still wants facts first.
    stamps = _stamps(plan["at"], len(rows))
    base = int(parse_at(plan["at"]).timestamp() * 1000)
    events = []
    for offset, (kind, data) in enumerate(rows):
        events.append({
            "v": 1, "id": ulid(base + offset), "at": stamps[offset], "by": "engine",
            "run": run, "type": kind, "data": data,
        })
    return events


def _card_event(card: dict) -> dict:
    body = {
        "card": card["card_id"],
        "gap": card["gap"],
        "question": card["card"]["question"],
        "options": card["card"]["options"],
        "recommended": card["card"]["recommended"],
    }
    if body["recommended"] is None:
        body["missing_fact"] = card["card"]["missing_fact"]
    else:
        body["facts"] = list(card["card"]["facts"])
    return body


def _commit_files(repo: Path, files: dict[str, str]) -> None:
    from crav1_2.paths import guarded_write

    for rel, text in files.items():
        old = (repo / rel).read_text(encoding="utf-8")
        if not one_x_lines_unchanged(old, text):
            raise EngineError(f"Refused: {rel} would change a 1.x line.")
        for line in text.splitlines():
            if "crav1-2:item" in line and line_has_mark(line):
                raise EngineError(f"Refused: {rel} would write a 1.x mark.")
        guarded_write(repo, rel, text.encode("utf-8"))


def _recorded(built: dict, spec: str) -> str | None:
    items = []
    decisions = []
    assumptions = []
    for kind, data in built["extras"]:
        if kind == "decision.recorded":
            decisions.append(data["decision"])
        elif kind == "assumption.recorded":
            assumptions.append(data["assumption"])
    for row in built["written"]:
        items.append(row["item"])
    parts = []
    if items:
        parts.append("items " + ", ".join(items))
    if decisions:
        parts.append("decisions " + ", ".join(decisions))
    if assumptions:
        parts.append("assumptions " + ", ".join(assumptions))
    if not parts:
        return None
    return "; ".join(parts) + f" on {spec}"


def _sentence(answer: dict) -> str:
    quote = answer["quote"].replace('"', "'")
    source = f"sot/{answer['note']}/note.md#{answer['passage']}"
    return f'Answered: {answer["date"]}, {answer["who"]}, {answer["kind"]}: "{quote}" Source: {source}'


def _fact_weak(plan: dict, fact: str) -> str | None:
    for row in plan["facts"]:
        if row["fact"] == fact:
            return row["weak"]
    return None


def _spec_text(repo: Path, slug: str | None) -> str:
    if not slug:
        raise EngineError(f"Refused: a spec slug is missing. {_WORDS}")
    path = repo / "docs" / "specs" / slug / "spec.md"
    if not path.is_file():
        raise EngineError(f"Refused: docs/specs/{slug}/spec.md does not exist.")
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise EngineError(f"Refused: docs/specs/{slug}/spec.md is not UTF-8 text.") from exc


def _select_notes(state: dict, inv: Invocation) -> list[dict]:
    reads = {(row["note"], row["spec"]) for row in state.get("reads", {}).values()}
    chosen = []
    for note_id in sorted(state["notes"]):
        note = state["notes"][note_id]
        if note.get("missing"):
            continue
        if inv.note_id and note_id != inv.note_id:
            continue
        if inv.note_id is None and (note_id, inv.slug) in reads:
            continue
        chosen.append(note)
    return chosen


def _open_answers(state: dict, spec: str, allowed: list[dict]) -> list[dict]:
    notes = {note["note"] for note in allowed} if allowed else None
    closed = _closed(state)
    found = []
    for answer in state["answers"]:
        if answer["spec"] != spec:
            continue
        if notes is not None and answer["note"] not in notes:
            continue
        if sort_key(answer["question"]) in closed:
            continue
        found.append(answer)
    return found


def _closed(state: dict) -> set[str]:
    closed = set()
    for decision in state["decisions"].values():
        if decision.get("superseded_by") or decision.get("missing"):
            continue
        if decision.get("chosen") in {"close-all", "pick-some"}:
            closed.add(sort_key(decision.get("accepting") or ""))
    return closed


def _passage(state: dict, note_id: str, passage_id: str) -> dict:
    note = state["notes"].get(note_id)
    if note is None or note.get("missing"):
        raise EngineError(f"Refused: {note_id} is not a note.")
    for passage in note.get("passage_list") or []:
        if passage["id"] == passage_id:
            return passage
    raise EngineError(f"Refused: {passage_id} is not in {note_id}.")


def _existing_fact(state: dict, note_id: str, passage_id: str, quote: str) -> str | None:
    for fact in state["facts"].values():
        if fact["note"] == note_id and fact["passage"] == passage_id and fact["quote"] == quote:
            return fact["fact"]
    return None


def _note_text(repo: Path, note: dict) -> str:
    path = repo / "sot" / note["note"] / "note.md"
    if path.is_file():
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            pass
    return render_note(note)


def _state(repo: Path) -> tuple[dict, list[dict]]:
    events = read_events(repo)
    return fold_events(events), events


def _after(at: str, events: list[dict]) -> str:
    stamp = parse_at(at)
    for event in events:
        current = parse_at(event["at"])
        if current >= stamp:
            stamp = current + timedelta(seconds=1)
    return stamp.isoformat()


def _stamps(start: str, count: int) -> list[str]:
    base = parse_at(start)
    return [(base + timedelta(seconds=offset)).isoformat() for offset in range(count)]


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


def _load(repo: Path, status: str, run_pick: str | None, missing_ok: bool = False) -> dict | None:
    folder = repo / ".crav1-2" / "sessions"
    if not folder.is_dir():
        if missing_ok:
            return None
        raise EngineError("Refused: no parked link-to-spec run.")
    rows = []
    for path in sorted(folder.glob("s-*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError):
            continue
        if not isinstance(data, dict) or data.get("status") != status:
            continue
        payload = data.get("payload")
        if not isinstance(payload, dict) or payload.get("flow") != "link-to-spec":
            continue
        if run_pick and data.get("id") != run_pick:
            continue
        rows.append(data)
    if not rows:
        if missing_ok:
            return None
        if status == "parked":
            raise EngineError("Refused: no parked link-to-spec run.")
        raise EngineError("Refused: no open link-to-spec run.")
    if len(rows) > 1:
        ids = ", ".join(str(row.get("id")) for row in rows)
        raise EngineError(f"Refused: more than one {status} link-to-spec run: {ids}.")
    return rows[0]


class _Ids:
    def __init__(self, state: dict, reserved: list[str] | None = None):
        self.taken: set[str] = set(reserved or [])
        pools = (
            state["facts"], state["gaps"], state["cards"], state["decisions"],
            state["assumptions"], state["items"],
        )
        for pool in pools:
            self.taken.update(pool)
        self._n = {prefix: 0 for prefix in "FGCDAI"}
        for ident in self.taken:
            match = re.fullmatch(r"([FGCDAI])-(\d+)", ident)
            if match:
                prefix, number = match.group(1), int(match.group(2))
                if number > self._n[prefix]:
                    self._n[prefix] = number

    def take(self, prefix: str) -> str:
        while True:
            self._n[prefix] += 1
            ident = f"{prefix}-{self._n[prefix]:04d}"
            if ident not in self.taken:
                self.taken.add(ident)
                return ident
