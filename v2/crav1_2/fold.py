"""Fold events into state.

Exact duplicate ids are dropped. Two different bodies that share an id keep
one id and give the others a run suffix. The suffix is chosen by sorting, so
the same set folds to the same state in any merge order. Application order is
(time, id), not file order.
"""

from __future__ import annotations

import copy
import hashlib

from crav1_2.events import canonical
from crav1_2.schema import parse_at
from crav1_2.version import SCHEMA


def empty_state() -> dict:
    return {
        "schema": SCHEMA,
        "notes": {},
        "facts": {},
        "gaps": {},
        "cards": {},
        "decisions": {},
        "assumptions": {},
        "items": {},
        "runs": {},
        "answers": [],
        "dropped_duplicate_ids": [],
        "disambiguated": [],
    }


def fold_events(events: list[dict]) -> dict:
    copied = [copy.deepcopy(event) for event in events]
    unique, dropped, disambiguated = _dedup(copied)
    unique.sort(key=lambda event: (parse_at(event["at"]), event["id"]))
    state = empty_state()
    state["dropped_duplicate_ids"] = dropped
    state["disambiguated"] = disambiguated
    for event in unique:
        _touch_run(state, event)
        _apply(state, event)
    return state


def _dedup(events: list[dict]) -> tuple[list[dict], list[str], list[dict]]:
    groups: dict[str, list[dict]] = {}
    for event in events:
        groups.setdefault(event["id"], []).append(event)
    dropped: list[str] = []
    unique_groups: dict[str, list[dict]] = {}
    for eid, group in groups.items():
        seen = set()
        unique = []
        for event in group:
            key = canonical(event)
            if key in seen:
                dropped.append(eid)
                continue
            seen.add(key)
            unique.append(event)
        unique_groups[eid] = sorted(unique, key=lambda event: (event["run"], canonical(event)))
    used = {eid for eid, group in unique_groups.items()}
    assigned = []
    disambiguated = []
    for eid in sorted(unique_groups):
        group = unique_groups[eid]
        for index, event in enumerate(group):
            body = copy.deepcopy(event)
            if index == 0:
                assigned.append(body)
                continue
            digest = hashlib.sha256(canonical(event).encode("utf-8")).hexdigest()[:6]
            candidate = f"{eid}-{event['run']}"
            if candidate in used:
                candidate = f"{eid}-{event['run']}-{digest}"
            if candidate in used:
                candidate = f"{eid}-{digest}"
            used.add(candidate)
            body["id"] = candidate
            disambiguated.append({"from": eid, "to": candidate, "run": event["run"]})
            assigned.append(body)
    disambiguated.sort(key=lambda item: item["to"])
    return assigned, sorted(set(dropped)), disambiguated


def _touch_run(state: dict, event: dict) -> None:
    state["runs"].setdefault(
        event["run"],
        {"run": event["run"], "status": "open", "step": "", "left": [], "at": event["at"]},
    )


def _apply(state: dict, event: dict) -> None:
    kind = event["type"]
    data = event["data"]
    if kind == "note.added":
        rec = {
            "note": data["note"],
            "kinds": list(data["kinds"]),
            "date": data["date"],
            "files": list(data["files"]),
            "from_sources": data["from_sources"],
            "passages": data["passages"],
            "at": event["at"],
        }
        for key in (
            "title", "added_by", "passage_list", "know",
            "vendor", "captured_from", "session_id", "quotes", "redactions",
        ):
            if key in data:
                rec[key] = copy.deepcopy(data[key])
        state["notes"][data["note"]] = rec
        return
    if kind == "note.extended":
        rec = state["notes"].get(data["note"])
        if rec is None:
            rec = {
                "note": data["note"],
                "kinds": ["session"],
                "date": data["note"][:10],
                "files": [],
                "from_sources": None,
                "passages": 0,
                "passage_list": [],
                "missing": True,
                "at": event["at"],
            }
            state["notes"][data["note"]] = rec
        rec.setdefault("passage_list", [])
        rec["passage_list"].extend(copy.deepcopy(data["passage_list"]))
        rec["passages"] = len(rec["passage_list"])
        for name in data.get("files") or []:
            if name not in rec.setdefault("files", []):
                rec["files"].append(name)
        if data.get("know"):
            rec.setdefault("know", [])
            rec["know"].extend(copy.deepcopy(data["know"]))
        return
    if kind == "answer.matched":
        state["answers"].append({
            "note": data["note"],
            "passage": data["passage"],
            "spec": data["spec"],
            "question": data["question"],
            "at": event["at"],
            "run": event["run"],
        })
        return
    if kind == "fact.cited":
        state["facts"][data["fact"]] = {
            "fact": data["fact"],
            "note": data["note"],
            "passage": data["passage"],
            "quote": data["quote"],
            "weak": data["weak"],
            "at": event["at"],
        }
        return
    if kind == "gap.found":
        state["gaps"][data["gap"]] = {**copy.deepcopy(data), "at": event["at"]}
        return
    if kind == "card.asked":
        state["cards"][data["card"]] = {**copy.deepcopy(data), "at": event["at"]}
        return
    if kind == "decision.recorded":
        state["decisions"][data["decision"]] = {
            **copy.deepcopy(data),
            "at": event["at"],
            "superseded_by": None,
        }
        return
    if kind == "decision.superseded":
        rec = state["decisions"].get(data["decision"])
        if rec is None:
            state["decisions"][data["decision"]] = {
                "decision": data["decision"],
                "superseded_by": data["by"],
                "at": event["at"],
                "missing": True,
            }
        else:
            rec["superseded_by"] = data["by"]
            rec["superseded_at"] = event["at"]
        return
    if kind == "assumption.recorded":
        state["assumptions"][data["assumption"]] = {
            **copy.deepcopy(data),
            "at": event["at"],
            "closed_by": None,
        }
        return
    if kind == "assumption.closed":
        rec = state["assumptions"].get(data["assumption"])
        if rec is None:
            state["assumptions"][data["assumption"]] = {
                "assumption": data["assumption"],
                "closed_by": data["by"],
                "at": event["at"],
                "missing": True,
            }
        else:
            rec["closed_by"] = data["by"]
            rec["closed_at"] = event["at"]
        return
    if kind == "item.linked":
        state["items"][data["item"]] = {**copy.deepcopy(data), "at": event["at"], "unlinked": None}
        return
    if kind == "item.updated":
        rec = state["items"].get(data["item"])
        if rec is None or rec.get("missing"):
            state["items"][data["item"]] = {
                "item": data["item"],
                "text": data["text"],
                "refs": list(data["refs"]),
                "at": event["at"],
                "missing": True,
                "unlinked": None,
            }
        else:
            rec["text"] = data["text"]
            rec["refs"] = list(data["refs"])
            rec["updated_at"] = event["at"]
        return
    if kind == "item.unlinked":
        rec = state["items"].get(data["item"])
        if rec is None:
            state["items"][data["item"]] = {
                "item": data["item"],
                "unlinked": data["reason"],
                "at": event["at"],
                "missing": True,
            }
        else:
            rec["unlinked"] = data["reason"]
            rec["unlinked_at"] = event["at"]
        return
    if kind == "run.parked":
        _set_run(state, event, "parked")
        return
    if kind == "run.ended":
        _set_run(state, event, "ended")


def _set_run(state: dict, event: dict, status: str) -> None:
    state["runs"][event["run"]] = {
        "run": event["run"],
        "status": status,
        "step": event["data"]["step"],
        "left": list(event["data"]["left"]),
        "at": event["at"],
    }
