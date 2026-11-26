"""Cross-event checks. A schema problem is raised by the reader before this runs.

Ids, pointers, origin kind, and MUST-on-assumption are decided from the whole
log, so line order does not change the findings. The 1.x line byte check lives
in crav1_2.lines and the check-lines command.
"""

from __future__ import annotations

from pathlib import Path

from crav1_2.fold import fold_events
from crav1_2.schema import DEC_ID, FACT_ID, ITEM_ID, must_on_assumption, origin_problem


def lint_events(events: list[dict], repo: Path | None = None) -> list[dict]:
    notes: dict[str, dict] = {}
    facts: set[str] = set()
    gaps: set[str] = set()
    cards: set[str] = set()
    decisions: set[str] = set()
    assumptions: set[str] = set()
    linked: set[str] = set()
    findings: list[dict] = []

    def add(code: str, message: str, ident: str | None = None) -> None:
        row = {"code": code, "message": message}
        if ident:
            row["id"] = ident
        findings.append(row)

    for event in events:
        data = event["data"]
        kind = event["type"]
        if kind == "note.added":
            notes[data["note"]] = data
        elif kind == "fact.cited":
            facts.add(data["fact"])
        elif kind == "gap.found":
            gaps.add(data["gap"])
        elif kind == "card.asked":
            cards.add(data["card"])
        elif kind == "decision.recorded":
            decisions.add(data["decision"])
        elif kind == "assumption.recorded":
            assumptions.add(data["assumption"])
        elif kind == "item.linked":
            linked.add(data["item"])

    state = fold_events(events)
    for event in events:
        data = event["data"]
        kind = event["type"]
        if kind == "fact.cited":
            _pointer(add, notes, data, repo)
        elif kind == "gap.found":
            for fact in data["facts"]:
                if fact not in facts:
                    add("unresolved-id", f"{fact} is not a cited fact.", data["gap"])
        elif kind == "card.asked":
            if data["gap"] not in gaps:
                add("unresolved-id", f"{data['gap']} is not a gap.", data["card"])
            for fact in data.get("facts") or []:
                if fact not in facts:
                    add("unresolved-id", f"{fact} is not a cited fact.", data["card"])
        elif kind == "decision.recorded":
            if data["card"] not in cards:
                add("unresolved-id", f"{data['card']} is not a card.", data["decision"])
            for fact in data["facts"]:
                if fact not in facts:
                    add("unresolved-id", f"{fact} is not a cited fact.", data["decision"])
            for ref in data["affects"]:
                if ITEM_ID.fullmatch(ref) and ref not in linked:
                    add("unresolved-id", f"{ref} is not a linked item.", data["decision"])
        elif kind == "decision.superseded":
            if data["decision"] not in decisions:
                add("unresolved-id", f"{data['decision']} is not a decision.", data["decision"])
            if data["by"] not in decisions:
                add("unresolved-id", f"{data['by']} is not a decision.", data["decision"])
        elif kind == "assumption.recorded":
            if data["gap"] not in gaps:
                add("unresolved-id", f"{data['gap']} is not a gap.", data["assumption"])
        elif kind == "assumption.closed":
            if data["assumption"] not in assumptions:
                add("unresolved-id", f"{data['assumption']} is not an assumption.", data["assumption"])
            if FACT_ID.fullmatch(data["by"]) and data["by"] not in facts:
                add("unresolved-id", f"{data['by']} is not a cited fact.", data["assumption"])
            if DEC_ID.fullmatch(data["by"]) and data["by"] not in decisions:
                add("unresolved-id", f"{data['by']} is not a decision.", data["assumption"])
        elif kind == "item.linked":
            problem = origin_problem(data["origin"], data["refs"])
            if problem:
                add("origin-kind", problem + ".", data["item"])
            _refs_exist(add, data["origin"], data["refs"], data["item"], facts, decisions, assumptions)
            if must_on_assumption(data["origin"], data["text"]):
                add("must-on-assumption", "MUST is not allowed on an asm item.", data["item"])
        elif kind == "item.updated":
            current = state["items"].get(data["item"]) or {}
            if data["item"] not in linked or "origin" not in current:
                add("unresolved-id", f"{data['item']} is not a linked item.", data["item"])
            else:
                origin = current["origin"]
                problem = origin_problem(origin, data["refs"])
                if problem:
                    add("origin-kind", problem + ".", data["item"])
                else:
                    _refs_exist(add, origin, data["refs"], data["item"], facts, decisions, assumptions)
                if must_on_assumption(origin, data["text"]):
                    add("must-on-assumption", "MUST is not allowed on an asm item.", data["item"])
        elif kind == "item.unlinked":
            if data["item"] not in linked:
                add("unresolved-id", f"{data['item']} is not a linked item.", data["item"])
        elif kind in {"run.parked", "run.ended"}:
            for card in data["left"]:
                if card not in cards:
                    add("unresolved-id", f"{card} is not a card.", event["run"])
    return findings


def _refs_exist(add, origin: str, refs: list[str], ident: str, facts, decisions, assumptions) -> None:
    for ref in refs:
        if origin == "src" and ref not in facts:
            add("unresolved-id", f"{ref} is not a cited fact.", ident)
        elif origin == "dec" and ref not in decisions:
            add("unresolved-id", f"{ref} is not a decision.", ident)
        elif origin == "asm" and ref not in assumptions:
            add("unresolved-id", f"{ref} is not an assumption.", ident)


def _pointer(add, notes: dict, data: dict, repo: Path | None) -> None:
    note = notes.get(data["note"])
    if note is None:
        add("broken-pointer", f"{data['fact']} cites a missing note {data['note']}.", data["fact"])
        return
    passages = note.get("passage_list")
    if passages is None:
        source = note.get("from_sources")
        if source and repo is not None and not (repo / source).exists():
            add("broken-pointer", f"{data['fact']} points at a missing source.", data["fact"])
        else:
            add("broken-pointer", f"{data['fact']} has no passage text to resolve {data['passage']}.", data["fact"])
        return
    match = next((item for item in passages if item["id"] == data["passage"]), None)
    if match is None:
        add("broken-pointer", f"{data['fact']} passage {data['passage']} is not in the note.", data["fact"])
        return
    path = match.get("path")
    if not path or repo is None:
        return
    file_path = _inside(repo, path)
    if file_path is None or not file_path.is_file():
        add("broken-pointer", f"{data['fact']} passage file is missing.", data["fact"])
        return
    try:
        body = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        add("broken-pointer", f"{data['fact']} passage file is not UTF-8 text.", data["fact"])
        return
    if data["quote"] not in body:
        add("broken-pointer", f"{data['fact']} quote is not in the source.", data["fact"])


def _inside(repo: Path, rel: str) -> Path | None:
    if not isinstance(rel, str) or rel.startswith("/") or "\\" in rel or ".." in rel.split("/"):
        return None
    root = repo.resolve()
    path = (root / rel).resolve()
    if path != root and root not in path.parents:
        return None
    return path


def lint_repo(repo: Path) -> list[dict]:
    from crav1_2.repo import read_events, require_init

    require_init(repo)
    return lint_events(read_events(repo), repo)
