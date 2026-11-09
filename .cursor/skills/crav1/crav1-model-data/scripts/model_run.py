#!/usr/bin/env python3
"""State machine for /crav1-model-data and the saved-model review export.

Both flows call this script. It does not score candidates, does not read a
network, and does not edit specs. Confirmed text is append-only. An open auto
run cannot approve. Time limits are checked between passes.

Diagram PDFs are drawn here with the standard library for Mermaid `erDiagram`
and `flowchart` `LR` or `TD`. Any other diagram fails the export. A rendered
picture is not method conformance, a physical constraint, or an empirical result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import zlib
from datetime import datetime, timezone
from pathlib import Path

STAGES = ("business-model", "physical-design")
EVIDENCE = (
    "requirement",
    "recorded-decision",
    "observation",
    "user-answer",
    "inference",
    "background",
)
REQUIREMENTS = ("supported", "contradicted", "conflicting", "unknown", "not-applicable")
FITS = ("meets", "fails", "conflicting", "unknown", "assumed")
OUTCOMES = ("excluded", "viable-unverified", "viable-on-evidence", "held", "tie")
RECS = ("retain", "targeted", "redesign", "held", "tie")
FLOWS = ("manual", "auto")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REV = re.compile(r"^r([1-9][0-9]*|0)$")

# 5x7 glyphs, bit 4 is the leftmost pixel. Missing glyphs draw as a block.
FONT = {
    " ": (0, 0, 0, 0, 0, 0, 0),
    "-": (0, 0, 0, 31, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 0, 12, 8),
    ":": (0, 12, 12, 0, 12, 12, 0),
    "/": (1, 2, 4, 8, 16, 0, 0),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 2, 4, 8, 31),
    "3": (31, 2, 4, 2, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 2, 12),
    "?": (14, 17, 1, 2, 4, 0, 4),
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 14),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 17, 25, 21, 19, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (14, 17, 16, 14, 1, 17, 14),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 21, 10),
    "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
}


class ModelError(Exception):
    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.code = code


def _slug(value: str, label: str) -> str:
    if not SLUG.fullmatch(value or ""):
        raise ModelError(f"{label} must be a lowercase slug.", "slug")
    return value


def _revision(value: str) -> str:
    if not REV.fullmatch(value or ""):
        raise ModelError(f"Revision {value!r} is not rN.", "revision")
    return value


def _bump(revision: str) -> str:
    return f"r{int(revision[1:]) + 1}"


def _now(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    text = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ModelError(f"Time {value!r} is not ISO-8601.", "time") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _stamp(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_lines(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.is_file():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- ") and ": " in line:
            key, _, val = line[2:].partition(": ")
            data[key] = val
    return data


def _index(home: Path) -> dict[str, str]:
    data = _load_lines(home / "index.md")
    if "Revision" not in data:
        raise ModelError(f"No model index at {home}.", "model")
    return data


def _write_index(home: Path, data: dict[str, str]) -> None:
    order = [
        "Model",
        "Flow",
        "Scope",
        "Scope confirmed",
        "Scope proposed",
        "Revision",
        "Home",
    ]
    lines = [f"# {data['Model']}", ""]
    for key in order:
        if key in data:
            lines.append(f"- {key}: {data[key]}")
    lines += [
        "",
        "## Offers",
        "",
        "- Schema and migration code: offered, not generated.",
        "- Detailed migration planning: offered, not written.",
        "- Spec edits: offered through /crav1-add-to-spec, not run.",
        "",
    ]
    (home / "index.md").write_text("\n".join(lines), encoding="utf-8")


def _run_path(home: Path) -> Path:
    return home / "run.md"


def _load_run(home: Path) -> dict[str, str]:
    path = _run_path(home)
    if not path.is_file():
        return {}
    data = _load_lines(path)
    return data


def _fingerprints(text: str) -> list[str]:
    rows = []
    grab = False
    for line in text.splitlines():
        if line.strip() == "## Fingerprints":
            grab = True
            continue
        if grab:
            if line.startswith("## "):
                break
            if line.startswith("- "):
                rows.append(line[2:].strip())
    return rows


def _norms(text: str) -> list[str]:
    rows = []
    grab = False
    for line in text.splitlines():
        if line.strip() == "## Norms":
            grab = True
            continue
        if grab:
            if line.startswith("## "):
                break
            if line.startswith("- "):
                rows.append(line[2:].strip())
    return rows


def _write_run(home: Path, data: dict[str, str], fingerprints: list[str], norms: list[str]) -> None:
    keys = [
        "Minutes",
        "Passes",
        "Started",
        "Passes used",
        "Open",
        "Stop",
        "Last progress",
        "Last unresolved",
    ]
    lines = ["# Auto run", ""]
    for key in keys:
        lines.append(f"- {key}: {data.get(key, '')}")
    lines += ["", "## Fingerprints", ""]
    lines += [f"- {item}" for item in fingerprints]
    lines += ["", "## Norms", ""]
    lines += [f"- {item}" for item in norms]
    lines.append("")
    _run_path(home).write_text("\n".join(lines), encoding="utf-8")


def _confirmed_text(home: Path) -> str:
    return (home / "confirmed.md").read_text(encoding="utf-8")


def _proposed_text(home: Path) -> str:
    return (home / "proposed.md").read_text(encoding="utf-8")


def _decisions_span(text: str) -> tuple[int, int]:
    start = text.find("\n## Decisions\n")
    if start < 0:
        raise ModelError("Proposed model has no Decisions section.", "layout")
    start = start + 1
    rest = text.find("\n## ", start + len("## Decisions"))
    end = len(text) if rest < 0 else rest + 1
    return start, end


def _blocks(section: str) -> list[tuple[str, str]]:
    """Return (id, raw block including heading) for ### blocks."""
    parts = re.split(r"(?m)^(?=### )", section)
    found = []
    for part in parts:
        if not part.startswith("### "):
            continue
        first = part.splitlines()[0]
        did = first[4:].strip()
        found.append((did, part if part.endswith("\n") else part + "\n"))
    return found


def _parse_block(raw: str) -> dict:
    lines = raw.splitlines()
    did = lines[0][4:].strip()
    fields: dict[str, str] = {}
    body_at = 1
    for i, line in enumerate(lines[1:], start=1):
        if line.startswith("- ") and ": " in line:
            key, _, val = line[2:].partition(": ")
            fields[key] = val
            body_at = i + 1
        elif line == "":
            body_at = i + 1
            break
        else:
            break
    body = "\n".join(lines[body_at:]).strip("\n")
    fields["id"] = did
    fields["body"] = body
    return fields


def _serialize_block(fields: dict) -> str:
    order = [
        "Stage",
        "Revision",
        "Status",
        "Evidence",
        "Requirement",
        "Fit",
        "Outcome",
        "Scope",
        "Axis",
        "Sources",
        "Depends",
        "Conditional",
        "Implementable",
        "Grain",
        "Measure",
        "Short source",
        "Drift",
    ]
    lines = [f"### {fields['id']}"]
    for key in order:
        if key in fields and fields[key] != "":
            lines.append(f"- {key}: {fields[key]}")
    body = fields.get("body", "").strip("\n")
    lines.append("")
    if body:
        lines.append(body)
        lines.append("")
    else:
        lines.append("")
    return "\n".join(lines)


def _replace_decisions(text: str, blocks: list[str]) -> str:
    start, end = _decisions_span(text)
    head = text[:start]
    tail = text[end:]
    body = "## Decisions\n\n" + "".join(blocks)
    if not body.endswith("\n"):
        body += "\n"
    return head + body + (tail if tail.startswith("## ") or tail == "" else tail)


def _set_header_revision(text: str, revision: str) -> str:
    return re.sub(r"(?m)^- Revision: .*$", f"- Revision: {revision}", text, count=1)


def _bump_proposed(home: Path, text: str) -> tuple[str, str]:
    index = _index(home)
    revision = _bump(index["Revision"])
    index["Revision"] = revision
    _write_index(home, index)
    text = _set_header_revision(text, revision)
    return revision, text


def _open_questions(home: Path) -> list[dict]:
    text = (home / "questions.md").read_text(encoding="utf-8")
    return [_parse_block(raw) for _did, raw in _blocks(text)]


def _example_gaps(text: str) -> list[str]:
    start = text.find("\n## Worked examples\n")
    end = text.find("\n## Diagrams\n")
    if start < 0:
        return []
    section = text[start: end if end > 0 else None]
    gaps = []
    for did, raw in _blocks(section):
        parsed = _parse_block(raw)
        if parsed.get("Result") == "gap" or parsed.get("Blocks physical") == "yes":
            gaps.append(did)
    return gaps


def _approvals(text: str) -> list[str]:
    return [line[2:].strip() if line.startswith("- ") else line.strip()
            for line in text.splitlines()
            if line.startswith("Approved:") or line.startswith("- Approved:")]


def current_approvals(home: Path) -> dict[str, str]:
    found: dict[str, str] = {}
    for line in _approvals(_confirmed_text(home)):
        match = re.match(r"Approved: (business-model|physical-design) (r\d+), (\d{4}-\d{2}-\d{2})$", line)
        if match:
            found[match.group(1)] = line
    return found


def _auto_open(home: Path) -> bool:
    run = _load_run(home)
    return run.get("Open") == "yes"


def discover(root: Path, scope: str | None) -> dict:
    specs_root = root / "docs" / "specs"
    if not specs_root.is_dir():
        raise ModelError(f"No docs/specs under {root}.", "discover")
    tokens = [tok.lower() for tok in re.findall(r"[A-Za-z0-9]{3,}", scope or "")]
    candidates = []
    for spec in sorted(specs_root.glob("*/spec.md")):
        slug = spec.parent.name
        if slug.startswith("_") or slug == "retired":
            continue
        if "retired" in spec.parts:
            continue
        text = spec.read_text(encoding="utf-8", errors="replace")
        title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), slug)
        hay = f"{slug}\n{text}".lower()
        if not scope:
            included = True
            reason = "No scope was given. This spec is a candidate container. Scope is not confirmed."
            hits: list[str] = []
        else:
            hits = [tok for tok in tokens if tok in hay]
            included = bool(hits)
            reason = (
                f"Included in the area view because these scope words appear: {', '.join(hits)}."
                if included
                else "Excluded from the area view. The scope words were not found in this spec."
            )
        rel = spec.relative_to(root).as_posix()
        candidates.append({
            "path": rel,
            "slug": slug,
            "title": title,
            "included_in_area": included if scope else False,
            "reason": reason,
        })
    context = []
    system = root / "docs" / "system"
    if system.is_dir():
        for path in sorted(system.glob("*.md")):
            context.append({
                "path": path.relative_to(root).as_posix(),
                "included_as_container": False,
                "reason": "System picture. Not a storage-container spec. Read as context.",
            })
    area = [c for c in candidates if c["included_in_area"]] if scope else []
    return {
        "ok": True,
        "scope": scope or "",
        "scope_confirmed": False,
        "default_view": None,
        "area": {
            "available": True,
            "default": False,
            "candidates": area if scope else [],
            "note": (
                "Area view lists specs that match the scope words. It is not the default."
                if scope
                else "No scope was given, so the area view has no selected specs yet. It stays available."
            ),
        },
        "platform": {
            "available": True,
            "default": False,
            "candidates": candidates,
            "note": "Platform view lists every spec candidate. It is not the default. It does not drop an area.",
        },
        "excluded": [c for c in candidates if scope and not c["included_in_area"]],
        "context": context,
    }


def check_recommendation(payload: dict, flow: str | None = None) -> dict:
    rec = payload.get("recommendation")
    if rec not in RECS:
        raise ModelError("Recommendation must be retain, targeted, redesign, held, or tie.", "recommendation")
    if flow == "auto" and payload.get("user_chose"):
        raise ModelError("Auto cannot record a user choice. Leave the tie unresolved.", "auto-choice")
    docs = payload.get("documentation", "unspecified")
    meets = payload.get("existing_meets_need")
    gaps = list(payload.get("decision_changing_gaps") or [])
    if rec == "redesign" and meets is True and docs == "poor" and not gaps:
        raise ModelError(
            "Poor documentation is not a business gap. The existing model meets the need, so retain it.",
            "retain-fit",
        )
    if rec == "retain" and meets is False:
        raise ModelError("The existing model does not meet the stated need. Do not recommend retain.", "not-retain")
    final = bool(payload.get("final"))
    if gaps and final:
        raise ModelError("Decision-changing gaps are open. Hold the final choice.", "hold")
    if gaps and rec not in ("held", "tie") and not payload.get("provisional"):
        raise ModelError(
            "Decision-changing gaps are open. A shortlist may stay provisional. The final choice is held.",
            "hold",
        )
    if payload.get("tie") and payload.get("best_fit") and not payload.get("user_chose"):
        raise ModelError("This is a genuine tie. Do not manufacture a winner. The user chooses.", "tie")
    if rec == "tie" and payload.get("best_fit") and not payload.get("user_chose"):
        raise ModelError("A tie has no best fit until the user chooses.", "tie")
    if payload.get("unknown_feasibility") and payload.get("outcome") == "excluded":
        raise ModelError("Unknown feasibility is not disproof and is not an exclusion.", "unknown")
    if payload.get("binding") and payload.get("overrides_binding"):
        raise ModelError(
            "A confirmed decision stays in force. Flag a revisit. Do not override it.",
            "binding",
        )
    if payload.get("requirement") == "supported" and payload.get("fit") == "unknown" and payload.get("outcome") == "viable-on-evidence":
        raise ModelError(
            "A supported requirement is not candidate fit. Unknown fit cannot be a viable-on-evidence outcome.",
            "separate",
        )
    if payload.get("fit") == "meets" and payload.get("approved") and not payload.get("user_approved"):
        raise ModelError("Candidate fit is not approval.", "separate")
    provisional = bool(payload.get("provisional") or gaps or rec in ("held", "tie"))
    return {
        "ok": True,
        "recommendation": rec,
        "provisional": provisional,
        "final": final and not provisional,
        "assumption": payload.get("assumptions") or "",
    }


def check_example(kind: str, payload: dict) -> dict:
    if kind == "history-window":
        retained = int(payload.get("retained_days", -1))
        needed = int(payload.get("needed_days", -1))
        other = bool(payload.get("other_source"))
        claim = payload.get("claim")
        if claim == "can-reconstruct" and not other and retained < needed:
            raise ModelError(
                f"{retained} retained days cannot reconstruct {needed} days without another source.",
                "history-window",
            )
        if claim not in ("can-reconstruct", "conditional", "met"):
            raise ModelError("History claim must be can-reconstruct, conditional, or met.", "history-window")
        if claim == "met" and not other and retained < needed:
            raise ModelError("The history window does not cover the question.", "history-window")
        missing = None if claim == "met" or (claim == "can-reconstruct" and (other or retained >= needed)) else (
            f"Need {needed} days. Retained window is {retained} days."
            + ("" if other else " No other history source is recorded.")
        )
        return {"ok": True, "kind": kind, "result": "gap" if missing else "ok", "gap": missing, "conditional": bool(missing)}
    if kind == "schema-not-disproof":
        claim = payload.get("claim")
        if claim == "history-impossible":
            raise ModelError(
                "A schema without history columns does not prove history is impossible. Feasibility stays unknown until evidence says otherwise.",
                "unknown",
            )
        if claim != "unknown-feasibility":
            raise ModelError("Schema claim must be history-impossible or unknown-feasibility.", "schema")
        return {
            "ok": True,
            "kind": kind,
            "result": "unknown",
            "requirement": "separate",
            "fit": "unknown",
            "outcome": "held",
            "note": "Unknown feasibility is not a fail and not an exclusion.",
        }
    if kind == "double-count":
        rows = payload.get("rows") or []
        grains = {row.get("grain") for row in rows}
        if payload.get("operation") == "sum" and len(grains) > 1:
            return {
                "ok": True,
                "kind": kind,
                "result": "gap",
                "gap": "Summing different grains double-counts the same amount.",
                "conditional": True,
            }
        if payload.get("operation") != "sum":
            raise ModelError("This worked example checks a sum.", "example")
        total = sum(int(row.get("amount", 0)) for row in rows)
        return {"ok": True, "kind": kind, "result": "ok", "total": total, "gap": None}
    if kind == "correction":
        meaning = payload.get("correction_meaning")
        if not meaning:
            return {
                "ok": True,
                "kind": kind,
                "result": "gap",
                "gap": "The correction meaning is missing, so physical design is not confirmable for this question.",
                "blocks_physical": True,
            }
        return {"ok": True, "kind": kind, "result": "ok", "gap": None, "blocks_physical": False}
    if kind == "views":
        area = list(payload.get("area_obligations") or [])
        platform = list(payload.get("platform_obligations") or [])
        if payload.get("default_view"):
            raise ModelError("Neither the area view nor the platform view is the default.", "views")
        missing = [item for item in area if item not in platform]
        if missing:
            raise ModelError(
                "The platform view dropped a local obligation: " + "; ".join(missing),
                "views",
            )
        if payload.get("promoted_to_platform_rule"):
            raise ModelError(
                "A local obligation stays local. Do not promote it to a platform-wide rule.",
                "views",
            )
        return {
            "ok": True,
            "kind": kind,
            "result": "ok",
            "area_available": True,
            "platform_available": True,
            "default_view": None,
            "local_obligations_preserved": True,
        }
    raise ModelError(f"Unknown example kind {kind}.", "example")


def _validate_decision(fields: dict, flow: str, approvals: dict[str, str]) -> None:
    if fields["id"] and not SLUG.fullmatch(fields["id"]):
        raise ModelError("Decision id must be a lowercase slug.", "slug")
    if fields.get("Stage") not in STAGES:
        raise ModelError("Stage must be business-model or physical-design.", "stage")
    if fields.get("Evidence") not in EVIDENCE:
        raise ModelError("Evidence kind is not one of the recorded kinds.", "evidence")
    if fields.get("Requirement") not in REQUIREMENTS:
        raise ModelError("Requirement status is missing or unknown as a label.", "requirement")
    if fields.get("Fit") not in FITS:
        raise ModelError("Candidate fit is missing or unknown as a label.", "fit")
    if fields.get("Outcome") not in OUTCOMES:
        raise ModelError("Outcome is missing.", "outcome")
    if fields.get("Status") == "confirmed":
        raise ModelError("A proposal cannot mark itself confirmed. Approval is a separate step.", "status")
    if fields.get("Fit") == "unknown" and fields.get("Outcome") == "excluded":
        raise ModelError("Unknown feasibility is not disproof and cannot exclude a candidate.", "unknown")
    if fields.get("Requirement") == "supported" and fields.get("Fit") == "unknown" and fields.get("Outcome") == "viable-on-evidence":
        raise ModelError("Supported requirement evidence is not candidate fit.", "separate")
    conditional = fields.get("Conditional") == "yes"
    implementable = fields.get("Implementable") == "yes"
    if conditional and implementable:
        raise ModelError("A conditional portion is not implementable.", "conditional")
    if fields.get("Evidence") == "inference" and fields.get("Requirement") == "supported" and "documented" in fields.get("body", "").lower():
        raise ModelError("An inference is not a documented requirement.", "inference")
    stage = fields["Stage"]
    if stage == "physical-design":
        business_ok = "business-model" in approvals
        if flow == "manual" and not business_ok:
            raise ModelError(
                "Manual flow confirms the business model before any physical design is recorded.",
                "business-first",
            )
        if flow == "auto" and not business_ok:
            if not conditional or implementable or fields.get("Status") != "conditional":
                raise ModelError(
                    "Auto may draft physical detail only as a conditional proposal that depends on the unconfirmed business model.",
                    "conditional",
                )
            depends = fields.get("Depends", "")
            if "business-model" not in depends:
                raise ModelError("Conditional physical detail must depend on the unconfirmed business model.", "conditional")
        if not business_ok and implementable:
            raise ModelError("Physical detail that depends on an unconfirmed business model is not implementable.", "conditional")


def init_model(home: Path, name: str, flow: str, scope: str | None) -> dict:
    _slug(name, "Model name")
    if flow not in FLOWS:
        raise ModelError("Flow must be manual or auto.", "flow")
    if home.exists() and any(home.iterdir()):
        raise ModelError(f"{home} already exists.", "model")
    home.mkdir(parents=True, exist_ok=True)
    data = {
        "Model": name,
        "Flow": flow,
        "Scope": scope or "",
        "Scope confirmed": "no",
        "Revision": "r0",
        "Home": f"docs/data-model/{name}/",
    }
    if scope:
        data["Scope proposed"] = scope
    _write_index(home, data)
    (home / "confirmed.md").write_text(f"# Confirmed {name}\n\n## Approvals\n", encoding="utf-8")
    (home / "proposed.md").write_text(
        "\n".join([
            f"# Proposed {name}",
            "",
            "- Revision: r0",
            "- Status: proposed",
            "",
            "## Recommendation",
            "",
            "- Choice: held",
            "- Best fit:",
            "- Alternatives:",
            "- Assumptions:",
            "- Gaps:",
            "- Binding:",
            "- Revisit:",
            "- Provisional: yes",
            "- Reason: Not assessed yet.",
            "",
            "## Decisions",
            "",
            "## Worked examples",
            "",
            "## Diagrams",
            "",
            "## Transition",
            "",
            "- Kind: none",
            "- Detailed migration: offered, not written.",
            "",
            "No structural transition is recorded yet.",
            "",
        ]),
        encoding="utf-8",
    )
    (home / "questions.md").write_text(
        f"# Questions for {name}\n\nUnanswered questions stay with the model. They are not written into specs.\n",
        encoding="utf-8",
    )
    (home / "comparisons.md").write_text(
        "\n".join([
            f"# Comparisons for {name}",
            "",
            "Both views stay available. Neither is the default.",
            "",
            "## Area",
            "",
            "- Confirmed: no",
            "- Default: no",
            "- Obligations:",
            "",
            "## Platform",
            "",
            "- Confirmed: no",
            "- Default: no",
            "- Promoted: no",
            "- Obligations:",
            "",
        ]),
        encoding="utf-8",
    )
    (home / "sources.md").write_text(f"# Sources checked for {name}\n\n## Checked\n", encoding="utf-8")
    return {"ok": True, "home": data["Home"], "revision": "r0", "scope_confirmed": False, "flow": flow}


def _save_proposed(home: Path, text: str) -> str:
    revision, text = _bump_proposed(home, text)
    (home / "proposed.md").write_text(text, encoding="utf-8")
    return revision


def recommend(home: Path, payload: dict) -> dict:
    if _auto_open(home) and payload.get("user_chose"):
        raise ModelError("An open auto run cannot record a user choice.", "auto-choice")
    flow = _index(home)["Flow"]
    result = check_recommendation(payload, flow=flow)
    text = _proposed_text(home)
    start = text.find("\n## Recommendation\n")
    end = text.find("\n## Decisions\n")
    if start < 0 or end < 0:
        raise ModelError("Proposed model has no Recommendation section.", "layout")
    gaps = payload.get("decision_changing_gaps") or []
    alternatives = payload.get("alternatives") or []
    block = "\n".join([
        "## Recommendation",
        "",
        f"- Choice: {payload['recommendation']}",
        f"- Best fit: {payload.get('best_fit') or ''}",
        "- Alternatives: " + "; ".join(alternatives),
        f"- Assumptions: {payload.get('assumptions') or ''}",
        "- Gaps: " + "; ".join(gaps),
        f"- Binding: {payload.get('binding') or ''}",
        f"- Revisit: {payload.get('revisit') or ''}",
        f"- Provisional: {'yes' if result['provisional'] else 'no'}",
        f"- Reason: {payload.get('reason') or ''}",
        "",
    ])
    text = text[: start + 1] + block + text[end + 1 :]
    revision = _save_proposed(home, text)
    result["revision"] = revision
    return result


def _normalize_decision(raw: dict) -> dict:
    alias = {
        "stage": "Stage",
        "status": "Status",
        "evidence": "Evidence",
        "requirement": "Requirement",
        "fit": "Fit",
        "outcome": "Outcome",
        "scope": "Scope",
        "axis": "Axis",
        "sources": "Sources",
        "depends": "Depends",
        "conditional": "Conditional",
        "implementable": "Implementable",
        "grain": "Grain",
        "measure": "Measure",
        "short_source": "Short source",
        "body": "body",
        "id": "id",
        "revision": "Revision",
        "drift": "Drift",
    }
    out: dict[str, str] = {}
    for key, val in raw.items():
        name = alias.get(key, key)
        if isinstance(val, bool):
            val = "yes" if val else "no"
        elif isinstance(val, list):
            val = ", ".join(str(item) for item in val)
        elif val is None:
            val = ""
        else:
            val = str(val)
        out[name] = val
    out.setdefault("Status", "proposed")
    out.setdefault("Conditional", "no")
    out.setdefault("Implementable", "no")
    out.setdefault("Depends", "none")
    return out


def add_decision(home: Path, fields: dict) -> dict:
    fields = _normalize_decision(fields)
    index = _index(home)
    approvals = current_approvals(home)
    _validate_decision(fields, index["Flow"], approvals)
    text = _proposed_text(home)
    _start, _end = _decisions_span(text)
    section = text[_start:_end]
    existing = _blocks(section)
    if any(did == fields["id"] for did, _raw in existing):
        raise ModelError(f"Decision {fields['id']} already exists. Record a revision instead of a second copy.", "decision")
    revision, text = _bump_proposed(home, text)
    fields = dict(fields)
    fields["Revision"] = revision
    if "Conditional" not in fields:
        fields["Conditional"] = "no"
    if "Implementable" not in fields:
        fields["Implementable"] = "no"
    if "Depends" not in fields:
        fields["Depends"] = "none"
    block = _serialize_block(fields)
    start, end = _decisions_span(text)
    section = text[start:end]
    blocks = [raw for _did, raw in _blocks(section)]
    blocks.append(block)
    text = _replace_decisions(text, blocks)
    (home / "proposed.md").write_text(text, encoding="utf-8")
    return {"ok": True, "id": fields["id"], "revision": revision, "status": fields.get("Status")}


def add_question(home: Path, fields: dict) -> dict:
    _slug(fields["id"], "Question id")
    path = home / "questions.md"
    text = path.read_text(encoding="utf-8")
    if f"### {fields['id']}\n" in text:
        raise ModelError(f"Question {fields['id']} already exists.", "question")
    block = "\n".join([
        f"### {fields['id']}",
        f"- Affects: {fields.get('affects') or ''}",
        f"- Provider: {fields.get('provider') or 'unknown'}",
        f"- Blocks: {fields.get('blocks') or ''}",
        "- Status: open",
        "",
        (fields.get("body") or "").strip(),
        "",
    ])
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text + block, encoding="utf-8")
    text_p = _proposed_text(home)
    revision = _save_proposed(home, text_p)
    return {"ok": True, "id": fields["id"], "revision": revision, "status": "open"}


def add_example(home: Path, kind: str, payload: dict) -> dict:
    result = check_example(kind, payload)
    text = _proposed_text(home)
    marker = "\n## Diagrams\n"
    at = text.find(marker)
    if at < 0:
        raise ModelError("Proposed model has no Diagrams section.", "layout")
    gap = result.get("gap") or ""
    blocks_physical = "yes" if result.get("result") == "gap" or result.get("blocks_physical") else "no"
    block = "\n".join([
        f"### {kind}",
        f"- Kind: {kind}",
        f"- Result: {result['result']}",
        f"- Gap: {gap}",
        f"- Blocks physical: {blocks_physical}",
        "",
        (payload.get("narrative") or gap or "The example matches the recorded grains.").strip(),
        "",
    ])
    # Insert before Diagrams, after existing examples.
    text = text[:at] + "\n" + block + text[at:]
    revision = _save_proposed(home, text)
    result["revision"] = revision
    return result


def add_diagram(home: Path, diagram_id: str, kind: str, caption: str, mermaid: str) -> dict:
    _slug(diagram_id, "Diagram id")
    if kind not in ("er", "flow"):
        raise ModelError("Diagram kind is er or flow.", "diagram")
    # Parse now so a bad diagram is not stored as if it could be exported.
    if kind == "er":
        parse_er(mermaid)
    else:
        parse_flow(mermaid)
    text = _proposed_text(home)
    fence = mermaid.strip("\n")
    block = "\n".join([
        f"### {diagram_id}",
        f"- Kind: {kind}",
        f"- Caption: {caption}",
        "",
        "```mermaid",
        fence,
        "```",
        "",
    ])
    marker = "\n## Transition\n"
    at = text.find(marker)
    if at < 0:
        raise ModelError("Proposed model has no Transition section.", "layout")
    text = text[:at] + "\n" + block + text[at:]
    revision = _save_proposed(home, text)
    return {"ok": True, "id": diagram_id, "revision": revision}


def set_transition(home: Path, text_body: str, kind: str = "concise") -> dict:
    if kind not in ("none", "concise"):
        raise ModelError("Transition kind is none or concise. Detailed migration planning is offered, not written.", "transition")
    if re.search(r"migration (script|plan written|applied)", text_body, re.I):
        raise ModelError("Detailed migration planning is offered, not written by this command.", "transition")
    proposed = _proposed_text(home)
    start = proposed.find("\n## Transition\n")
    if start < 0:
        raise ModelError("Proposed model has no Transition section.", "layout")
    block = "\n".join([
        "## Transition",
        "",
        f"- Kind: {kind}",
        "- Detailed migration: offered, not written.",
        "",
        text_body.strip(),
        "",
    ])
    proposed = proposed[: start + 1] + block
    revision = _save_proposed(home, proposed)
    return {"ok": True, "revision": revision, "kind": kind}


def set_views(home: Path, payload: dict) -> dict:
    result = check_example("views", payload)
    name = _index(home)["Model"]
    area = payload.get("area_obligations") or []
    platform = payload.get("platform_obligations") or []
    lines = [
        f"# Comparisons for {name}",
        "",
        "Both views stay available. Neither is the default.",
        "",
        "## Area",
        "",
        "- Confirmed: no",
        "- Default: no",
        "- Obligations: " + "; ".join(area),
        "",
        "## Platform",
        "",
        "- Confirmed: no",
        "- Default: no",
        "- Promoted: no",
        "- Obligations: " + "; ".join(platform),
        "",
    ]
    (home / "comparisons.md").write_text("\n".join(lines), encoding="utf-8")
    return result


def confirm_scope(home: Path, yes: bool) -> dict:
    if not yes:
        raise ModelError("Scope stays unconfirmed until an explicit yes.", "scope")
    if _auto_open(home):
        raise ModelError("An open auto run cannot confirm scope. Record a proposed scope.", "scope")
    index = _index(home)
    if not index.get("Scope") and not index.get("Scope proposed"):
        raise ModelError("Name the scope before confirming it.", "scope")
    index["Scope confirmed"] = "yes"
    _write_index(home, index)
    return {"ok": True, "scope_confirmed": True, "scope": index.get("Scope", "")}


def propose_scope(home: Path, scope: str) -> dict:
    if not scope.strip():
        raise ModelError("A proposed scope needs text.", "scope")
    index = _index(home)
    index["Scope proposed"] = scope.strip()
    index["Scope"] = scope.strip()
    index["Scope confirmed"] = "no"
    _write_index(home, index)
    return {"ok": True, "scope_confirmed": False, "scope_proposed": scope.strip()}


def _decision_map(home: Path) -> list[tuple[str, str]]:
    text = _proposed_text(home)
    start, end = _decisions_span(text)
    return _blocks(text[start:end])


def approve(home: Path, stage: str, revision: str, date: str, yes: bool) -> dict:
    if stage not in STAGES:
        raise ModelError("Stage must be business-model or physical-design.", "stage")
    _revision(revision)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date or ""):
        raise ModelError("Approval date must be YYYY-MM-DD.", "date")
    if not yes:
        raise ModelError("Approval needs an explicit yes for this stage and revision.", "approve")
    if _auto_open(home):
        raise ModelError(
            "An open auto run cannot approve. Unconfirmed results stay proposals.",
            "auto-approve",
        )
    index = _index(home)
    if index["Revision"] != revision:
        raise ModelError(
            f"The proposed revision is {index['Revision']}, not {revision}. Approve the exact revision.",
            "revision",
        )
    approvals = current_approvals(home)
    if stage == "physical-design" and "business-model" not in approvals:
        raise ModelError("Business-model approval does not exist yet. It is not implied by a physical approval.", "stage")
    blocking = []
    for question in _open_questions(home):
        if question.get("Status") != "open":
            continue
        blocked = [item.strip() for item in question.get("Blocks", "").split(",") if item.strip()]
        if blocked:
            blocking.append(question["id"])
    # Questions block approval of a stage when they name a decision in that stage.
    stage_ids = set()
    blocks = []
    for did, raw in _decision_map(home):
        parsed = _parse_block(raw)
        if parsed.get("Stage") == stage:
            stage_ids.add(did)
            blocks.append(raw)
            if parsed.get("Status") == "conditional" or parsed.get("Conditional") == "yes":
                raise ModelError(f"{did} is conditional and cannot be approved.", "conditional")
            if parsed.get("Outcome") in ("held", "tie"):
                raise ModelError(f"{did} is {parsed.get('Outcome')} and cannot be approved.", "hold")
            if parsed.get("Fit") == "unknown" or parsed.get("Requirement") == "unknown":
                raise ModelError(f"{did} still has unknown evidence. Hold it.", "hold")
    if not blocks:
        raise ModelError(f"No {stage} decisions are proposed at {revision}.", "approve")
    for question in _open_questions(home):
        if question.get("Status") != "open":
            continue
        named = {item.strip() for item in question.get("Blocks", "").split(",") if item.strip()}
        if named & stage_ids:
            raise ModelError(
                f"Open question {question['id']} still blocks this stage. Leave the choice conditional or answer it.",
                "question",
            )
    if stage == "physical-design":
        proposed_now = _proposed_text(home)
        part = proposed_now[proposed_now.find("\n## Transition\n") :]
        if "- Kind: none" in part:
            raise ModelError("Physical approval needs the concise transition assessment first.", "transition")
        gaps = _example_gaps(proposed_now)
        if gaps:
            raise ModelError(
                "Worked examples still have gaps (" + ", ".join(gaps) + "). Physical design stays unapproved.",
                "example",
            )
    line = f"Approved: {stage} {revision}, {date}"
    prior = _confirmed_text(home)
    snapshot = "".join(blocks)
    addition = f"\n## {stage} {revision}\n\n{line}\n\n{snapshot}"
    if not prior.endswith("\n"):
        prior += "\n"
    (home / "confirmed.md").write_text(prior + addition, encoding="utf-8")
    return {"ok": True, "approved": line, "stage": stage, "revision": revision, "bytes_appended": True}


def pin_source(home: Path, root: Path, rel: str, decisions: list[str]) -> dict:
    path = root / rel
    if not path.is_file():
        raise ModelError(f"Source not found: {rel}", "source")
    digest = _hash(path)
    sources = home / "sources.md"
    text = sources.read_text(encoding="utf-8")
    block = "\n".join([
        f"### {rel}",
        f"- Checked: {digest}",
        "- Decisions: " + ", ".join(decisions),
        "",
    ])
    # Replace an existing pin for this path.
    pattern = re.compile(rf"(?ms)^### {re.escape(rel)}\n.*?(?=^### |\Z)")
    if pattern.search(text):
        text = pattern.sub(block, text)
    else:
        if not text.endswith("\n"):
            text += "\n"
        text += block
    sources.write_text(text, encoding="utf-8")
    return {"ok": True, "path": rel, "checked": digest}


def _pins(home: Path) -> list[dict]:
    text = (home / "sources.md").read_text(encoding="utf-8")
    pins = []
    for did, raw in _blocks(text):
        parsed = _parse_block(raw)
        pins.append({
            "path": did,
            "checked": parsed.get("Checked", ""),
            "decisions": [item.strip() for item in parsed.get("Decisions", "").split(",") if item.strip()],
        })
    return pins


def _internal_issues(home: Path) -> list[str]:
    issues = []
    seen: dict[tuple[str, str], tuple[str, str]] = {}
    approvals = current_approvals(home)
    for did, raw in _decision_map(home):
        parsed = _parse_block(raw)
        key = (parsed.get("Scope", ""), parsed.get("Measure", ""))
        grain = parsed.get("Grain", "")
        if key[1] and grain:
            if key in seen and seen[key][0] != grain:
                issues.append(
                    f"Internal inconsistency: {seen[key][1]} and {did} give different grains for {key[1]} in {key[0] or 'the same scope'}."
                )
            else:
                seen[key] = (grain, did)
        if parsed.get("Status") == "confirmed" and parsed.get("Stage") not in approvals:
            issues.append(f"Internal inconsistency: {did} says confirmed but that stage has no approval.")
        if parsed.get("Implementable") == "yes" and parsed.get("Conditional") == "yes":
            issues.append(f"Internal inconsistency: {did} is conditional and also marked implementable.")
        if parsed.get("Stage") == "physical-design" and parsed.get("Implementable") == "yes" and "business-model" not in approvals:
            issues.append(f"Internal inconsistency: {did} is marked implementable while the business model is not approved.")
    return issues


def drift(home: Path, root: Path) -> dict:
    pins = _pins(home)
    checked = []
    material = []
    for pin in pins:
        path = root / pin["path"]
        if not path.is_file():
            checked.append({
                "path": pin["path"],
                "was": pin["checked"],
                "now": "",
                "content_changed": True,
                "missing": True,
            })
            for did in pin["decisions"]:
                material.append({"decision": did, "source": pin["path"], "reason": "source missing"})
            continue
        digest = _hash(path)
        changed = digest != pin["checked"]
        checked.append({
            "path": pin["path"],
            "was": pin["checked"],
            "now": digest,
            "content_changed": changed,
            "missing": False,
        })
        if changed:
            for did in pin["decisions"]:
                material.append({"decision": did, "source": pin["path"], "reason": "source content changed"})
    seeded = {item["decision"] for item in material}
    growing = True
    while growing:
        growing = False
        for did, raw in _decision_map(home):
            if did in seeded:
                continue
            depends = {
                item.strip()
                for item in _parse_block(raw).get("Depends", "").split(",")
                if item.strip() and item.strip() != "none"
            }
            if depends & seeded:
                seeded.add(did)
                material.append({
                    "decision": did,
                    "source": "dependency",
                    "reason": "depends on a decision whose source changed",
                })
                growing = True
    internal = _internal_issues(home)
    affected = sorted({item["decision"] for item in material})
    all_ids = [did for did, _raw in _decision_map(home)]
    unaffected = [did for did in all_ids if did not in affected]
    statement = (
        f"Checked {len(checked)} pinned source(s). "
        f"Content changed in {sum(1 for item in checked if item['content_changed'])}. "
        f"Material for {len(affected)} decision(s). "
        f"Internal inconsistencies: {len(internal)}. "
        "This is not a claim that nothing else drifted."
    )
    return {
        "ok": True,
        "checked": checked,
        "material": material,
        "internal": internal,
        "affected": affected,
        "unaffected": unaffected,
        "statement": statement,
        "pinned": bool(pins),
    }


def note_drift(home: Path, root: Path) -> dict:
    report = drift(home, root)
    if not report["affected"] and not report["internal"]:
        report["proposed_changed"] = False
        report["confirmed_unchanged"] = True
        return report
    before_confirmed = _confirmed_text(home)
    text = _proposed_text(home)
    start, end = _decisions_span(text)
    pairs = _blocks(text[start:end])
    raw_by_id = {did: raw for did, raw in pairs}
    internal_ids = set()
    for issue in report["internal"]:
        for did in raw_by_id:
            if re.search(rf"(?<![A-Za-z0-9-]){re.escape(did)}(?![A-Za-z0-9-])", issue):
                internal_ids.add(did)
    unchanged_ids = [did for did in report["unaffected"] if did not in internal_ids]
    unaffected_before = {did: raw_by_id[did] for did in unchanged_ids}
    report["unaffected"] = unchanged_ids
    report["affected"] = sorted(set(report["affected"]) | internal_ids)
    revision, text = _bump_proposed(home, text)
    start, end = _decisions_span(text)
    pairs = _blocks(text[start:end])
    new_blocks = []
    reasons: dict[str, list[str]] = {}
    for item in report["material"]:
        reasons.setdefault(item["decision"], []).append(f"{item['source']} ({item['reason']})")
    for issue in report["internal"]:
        for did, _raw in pairs:
            if re.search(rf"(?<![A-Za-z0-9-]){re.escape(did)}(?![A-Za-z0-9-])", issue):
                reasons.setdefault(did, []).append(issue)
    for did, raw in pairs:
        if did not in reasons:
            new_blocks.append(raw)
            continue
        parsed = _parse_block(raw)
        parsed["Status"] = "needs-review"
        if parsed.get("Outcome") in ("viable-on-evidence", "excluded"):
            parsed["Outcome"] = "held"
        parsed["Revision"] = revision
        parsed["Drift"] = "; ".join(reasons[did])
        new_blocks.append(_serialize_block(parsed))
    text = _replace_decisions(text, new_blocks)
    (home / "proposed.md").write_text(text, encoding="utf-8")
    after = _proposed_text(home)
    start, end = _decisions_span(after)
    after_pairs = dict(_blocks(after[start:end]))
    for did, raw in unaffected_before.items():
        if after_pairs.get(did) != raw:
            raise ModelError(f"Drift note changed an unaffected decision: {did}", "drift")
    if _confirmed_text(home) != before_confirmed:
        raise ModelError("Drift note changed the confirmed model.", "drift")
    report["revision"] = revision
    report["proposed_changed"] = True
    report["confirmed_unchanged"] = True
    return report


def _checkpoint(home: Path, stop: str, unfinished: bool, unresolved: int) -> None:
    run = _load_run(home)
    lines = [
        "# Checkpoint",
        "",
        f"- Stop: {stop}",
        f"- Passes used: {run.get('Passes used', '')}",
        f"- Passes limit: {run.get('Passes', '')}",
        f"- Minutes: {run.get('Minutes', '')}",
        f"- Unfinished: {'yes' if unfinished else 'no'}",
        "- Confirmed model: unchanged",
        f"- Proposed: {(home / 'proposed.md').as_posix()}",
        "- Note: Time is checked between passes, not during a pass. This is not a live preemption.",
        "",
        "## Unresolved",
        "",
        f"- Open count recorded on the last pass: {unresolved}",
        "",
    ]
    (home / "checkpoint.md").write_text("\n".join(lines), encoding="utf-8")


def normalize_text(text: str) -> str:
    lines = []
    for line in text.lower().splitlines():
        line = re.sub(r"[^a-z0-9 ]+", " ", line)
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            lines.append(line)
    return "\n".join(sorted(lines))


def auto_begin(home: Path, minutes: int, passes: int, now: str) -> dict:
    if minutes < 1 or passes < 1:
        raise ModelError("The budget needs a positive minute limit and a positive pass limit.", "budget")
    moment = _now(now)
    data = {
        "Minutes": str(minutes),
        "Passes": str(passes),
        "Started": moment.isoformat(),
        "Passes used": "0",
        "Open": "yes",
        "Stop": "",
        "Last progress": "",
        "Last unresolved": "",
    }
    _write_run(home, data, [], [])
    if (home / "checkpoint.md").is_file():
        # A new invocation replaces the checkpoint only after the new budget is approved.
        (home / "checkpoint.md").unlink()
    return {
        "ok": True,
        "minutes": minutes,
        "passes": passes,
        "started": data["Started"],
        "note": "Budget applies to this run only. Passes are shared across stages and are not reset. No watcher is started.",
    }


def auto_pass(
    home: Path,
    fingerprint: str,
    unresolved: int,
    progress: str,
    now: str,
    text: str | None = None,
    stage: str | None = None,
) -> dict:
    if progress not in ("yes", "no"):
        raise ModelError("Progress is yes or no.", "progress")
    if stage and stage not in STAGES:
        raise ModelError("Stage must be business-model or physical-design.", "stage")
    path = _run_path(home)
    if not path.is_file():
        raise ModelError("No auto run is open. Start one only after the budget is approved.", "resume")
    raw = path.read_text(encoding="utf-8")
    data = _load_lines(path)
    if data.get("Open") != "yes":
        raise ModelError(
            "This run already stopped. Resume needs a new auto-flow invocation and a new approved budget. Nothing is watching between runs.",
            "resume",
        )
    moment = _now(now)
    started = _now(data["Started"])
    elapsed = (moment - started).total_seconds()
    limit = int(data["Minutes"]) * 60
    if elapsed >= limit:
        data["Open"] = "no"
        data["Stop"] = "time"
        _write_run(home, data, _fingerprints(raw), _norms(raw))
        _checkpoint(home, "time", True, unresolved)
        return {
            "ok": True,
            "applied": False,
            "stop": "time",
            "passes_used": int(data["Passes used"]),
            "unfinished": True,
            "note": "The time limit was reached between passes. The pass did not start. Time is not preempted mid-pass.",
        }
    used = int(data["Passes used"])
    if used >= int(data["Passes"]):
        data["Open"] = "no"
        data["Stop"] = "passes"
        _write_run(home, data, _fingerprints(raw), _norms(raw))
        _checkpoint(home, "passes", True, unresolved)
        return {
            "ok": True,
            "applied": False,
            "stop": "passes",
            "passes_used": used,
            "unfinished": True,
            "note": "The shared correction-pass budget is used up. It was not reset for a new stage.",
        }
    fps = _fingerprints(raw)
    norms = _norms(raw)
    norm = hashlib.sha256(normalize_text(text if text is not None else fingerprint).encode()).hexdigest()
    used += 1
    data["Passes used"] = str(used)
    cycle = False
    if fps and fingerprint in fps and fingerprint != fps[-1]:
        cycle = True
    if norms and norm in norms and norm != norms[-1]:
        cycle = True
    same_state = bool(fps) and fingerprint == fps[-1]
    same_meaning = bool(norms) and norm == norms[-1]
    stalled = False
    stable = False
    if cycle:
        stop = "cycle"
    elif (same_state or same_meaning) and unresolved == 0:
        stop = "stable"
        stable = True
    elif (same_state or same_meaning) and unresolved > 0:
        stop = "stall"
        stalled = True
    elif progress == "no" and data.get("Last progress") == "no":
        stop = "stall"
        stalled = True
    else:
        stop = ""
    data["Last progress"] = progress
    data["Last unresolved"] = str(unresolved)
    fps.append(fingerprint)
    norms.append(norm)
    if stop:
        data["Open"] = "no"
        data["Stop"] = stop
    _write_run(home, data, fps, norms)
    if stop:
        _checkpoint(home, stop, unfinished=not stable, unresolved=unresolved)
    return {
        "ok": True,
        "applied": True,
        "stop": stop,
        "passes_used": used,
        "stage": stage or "",
        "stable": stable,
        "stall": stalled,
        "cycle": cycle,
        "unfinished": bool(stop) and not stable,
        "heuristic": "Normalized text is a cycle heuristic. It is not proof that two wordings mean the same thing.",
    }


def auto_finish(home: Path, root: Path) -> dict:
    report = drift(home, root)
    path = _run_path(home)
    if not path.is_file():
        raise ModelError("No auto run to finish.", "resume")
    raw = path.read_text(encoding="utf-8")
    data = _load_lines(path)
    material = bool(report["material"] or report["internal"] or not report["pinned"])
    if material and data.get("Stop") in ("", "stable") and int(data.get("Passes used") or 0) < int(data["Passes"]):
        data["Stop"] = ""
        data["Open"] = "yes"
        _write_run(home, data, _fingerprints(raw), _norms(raw))
        report["result"] = "needs-correction"
        report["ok"] = True
        report["note"] = "Drift or an incomplete source check blocks a stable result. The pass budget was not reset."
        return report
    if data.get("Stop") == "stable" and not material:
        report["result"] = "stable"
        report["note"] = report["statement"]
        return report
    report["result"] = data.get("Stop") or "open"
    report["unfinished"] = data.get("Stop") not in ("stable", "")
    report["note"] = report["statement"]
    return report


def feedback(home: Path, review: Path, comment: str, decision: str) -> dict:
    report = review / "report.md"
    if not report.is_file():
        raise ModelError("Review report.md was not found. Comments attach to an exported review.", "review")
    before_report = report.read_bytes()
    pdf = review / "report.pdf"
    before_pdf = pdf.read_bytes() if pdf.is_file() else None
    before_confirmed = _confirmed_text(home)
    version = ""
    for line in report.read_text(encoding="utf-8").splitlines():
        if line.startswith("Review-Version:"):
            version = line.split(":", 1)[1].strip()
            break
    if not version:
        raise ModelError("The review has no Review-Version line.", "review")
    text = _proposed_text(home)
    note = "\n".join([
        f"### review-{version.lower()}",
        "- Stage: business-model",
        "- Status: proposed",
        "- Evidence: user-answer",
        "- Requirement: unknown",
        "- Fit: unknown",
        "- Outcome: held",
        "- Scope: review",
        "- Axis: review",
        f"- Sources: {report.as_posix()}",
        f"- Depends: {decision}",
        "- Conditional: yes",
        "- Implementable: no",
        f"- Short source: review {version}",
        "",
        f"Review comment on {version}, not an approval. Target: {decision}.",
        "",
        comment.strip(),
        "",
    ])
    # The review note is a proposal. It uses the decision serializer's rules loosely:
    # write it as a revision block under Decisions via add path but skip auto physical gate
    # by storing it with stage business-model, conditional, held.
    if f"### review-{version.lower()}\n" in text:
        raise ModelError("This review version was already brought back.", "review")
    revision, text = _bump_proposed(home, text)
    note = note.replace("- Status: proposed", "- Status: proposed", 1)
    # Stamp the revision on the note.
    note = note.replace(
        "- Stage: business-model\n",
        f"- Stage: business-model\n- Revision: {revision}\n",
        1,
    )
    start, end = _decisions_span(text)
    blocks = [raw for _did, raw in _blocks(text[start:end])]
    blocks.append(note if note.endswith("\n") else note + "\n")
    text = _replace_decisions(text, blocks)
    (home / "proposed.md").write_text(text, encoding="utf-8")
    if report.read_bytes() != before_report or (before_pdf is not None and pdf.read_bytes() != before_pdf):
        raise ModelError("Bringing comments back changed the exported review.", "review")
    if _confirmed_text(home) != before_confirmed:
        raise ModelError("Bringing comments back changed the confirmed model.", "review")
    approvals = current_approvals(home)
    return {
        "ok": True,
        "revision": revision,
        "review_version": version,
        "approved": False,
        "approvals_unchanged": approvals,
        "confirmed_unchanged": True,
        "review_unchanged": True,
    }


def parse_er(source: str) -> dict:
    entities: dict[str, list[str]] = {}
    rels = []
    current = None
    for raw in source.splitlines():
        line = raw.strip()
        if not line or line.startswith("%%") or line == "erDiagram":
            continue
        if current and line == "}":
            current = None
            continue
        if current:
            attr = re.sub(r"\s+", " ", line)
            entities[current].append(attr)
            continue
        block = re.match(r"^([A-Za-z][A-Za-z0-9_]*)\s*\{$", line)
        if block:
            current = block.group(1)
            entities.setdefault(current, [])
            continue
        rel = re.match(r"^([A-Za-z][A-Za-z0-9_]*)\s+(\S+)\s+([A-Za-z][A-Za-z0-9_]*)\s*:\s*(.+)$", line)
        if not rel:
            raise ModelError(f"Cannot draw this ER line as a relationship or entity: {line}", "diagram")
        mid = rel.group(2)
        card = re.fullmatch(
            r"(\|o|o\||\|\||\}o|o\{|\|\{|\}\|)([.|-]{2})(\|o|o\||\|\||\}o|o\{|\|\{|\}\|)",
            mid,
        )
        if not card:
            raise ModelError(f"Cardinality {mid} is outside the ER subset this exporter draws.", "diagram")
        entities.setdefault(rel.group(1), [])
        entities.setdefault(rel.group(3), [])
        rels.append({
            "left": rel.group(1),
            "right": rel.group(3),
            "left_card": card.group(1),
            "right_card": card.group(3),
            "label": rel.group(4).strip(),
        })
    if not entities:
        raise ModelError("ER diagram has no entities to draw.", "diagram")
    return {"entities": entities, "rels": rels}


def parse_flow(source: str) -> dict:
    direction = "LR"
    nodes: dict[str, str] = {}
    edges = []
    edge_re = re.compile(
        r"^([A-Za-z][A-Za-z0-9_]*)(?:\[([^\]]*)\])?\s+-+>(?:\|([^|]*)\|)?\s+([A-Za-z][A-Za-z0-9_]*)(?:\[([^\]]*)\])?$"
    )
    node_re = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)\[([^\]]*)\]$")
    for raw in source.splitlines():
        line = raw.strip()
        if not line or line.startswith("%%"):
            continue
        head = re.match(r"^flowchart\s+(LR|TD|TB|RL)$", line)
        if head:
            direction = "TD" if head.group(1) in ("TD", "TB") else "LR"
            continue
        if line.startswith("flowchart"):
            raise ModelError("Flowchart direction must be LR or TD.", "diagram")
        edge = edge_re.match(line)
        if edge:
            nodes.setdefault(edge.group(1), edge.group(2) or edge.group(1))
            if edge.group(2):
                nodes[edge.group(1)] = edge.group(2)
            nodes.setdefault(edge.group(4), edge.group(5) or edge.group(4))
            if edge.group(5):
                nodes[edge.group(4)] = edge.group(5)
            edges.append({"src": edge.group(1), "dst": edge.group(4), "label": (edge.group(3) or "").strip()})
            continue
        node = node_re.match(line)
        if node:
            nodes[node.group(1)] = node.group(2)
            continue
        raise ModelError(f"Cannot draw this flowchart line: {line}", "diagram")
    if not nodes:
        raise ModelError("Flowchart has no nodes to draw.", "diagram")
    return {"direction": direction, "nodes": nodes, "edges": edges}


class Canvas:
    def __init__(self, width: int, height: int):
        self.w = width
        self.h = height
        self.px = bytearray([255, 255, 255] * width * height)

    def set(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i : i + 3] = bytes(color)

    def rect(self, x: int, y: int, w: int, h: int, color: tuple[int, int, int], fill: bool = False) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                border = xx in (x, x + w - 1) or yy in (y, y + h - 1)
                if fill or border:
                    self.set(xx, yy, color)

    def line(self, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx - dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def text(self, x: int, y: int, text: str, color: tuple[int, int, int] = (20, 20, 20), scale: int = 2) -> None:
        cursor = x
        for ch in text:
            rows = FONT.get(ch.upper(), FONT["?"]) if ch != " " else FONT[" "]
            if ch == " ":
                rows = FONT[" "]
            for ry, bits in enumerate(rows):
                for rx in range(5):
                    if bits & (1 << (4 - rx)):
                        for sy in range(scale):
                            for sx in range(scale):
                                self.set(cursor + rx * scale + sx, y + ry * scale + sy, color)
            cursor += 6 * scale

    def dark_pixels(self) -> int:
        count = 0
        for i in range(0, len(self.px), 3):
            if self.px[i] < 250 or self.px[i + 1] < 250 or self.px[i + 2] < 250:
                count += 1
        return count


def _label(text: str, limit: int = 28) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9 :./,-]+", " ", text).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned[:limit]


INK = (25, 40, 60)
ACCENT = (30, 70, 110)
MUTED = (70, 80, 90)


def draw_er(parsed: dict) -> Canvas:
    names = list(parsed["entities"])
    box_w, box_h = 220, 36 + 16 * max(1, max(len(v) for v in parsed["entities"].values()))
    gap = 70
    width = 40 + len(names) * (box_w + gap)
    height = 80 + box_h + 80
    canvas = Canvas(width, height)
    canvas.text(16, 12, "ER structure. Legend: lines are relationships, not movement.", INK, 1)
    centers = {}
    for i, name in enumerate(names):
        x = 20 + i * (box_w + gap)
        y = 40
        canvas.rect(x, y, box_w, box_h, ACCENT, fill=False)
        canvas.rect(x, y, box_w, 22, ACCENT, fill=True)
        canvas.text(x + 6, y + 4, _label(name, 18), (255, 255, 255), 1)
        for j, attr in enumerate(parsed["entities"][name][:8]):
            canvas.text(x + 6, y + 28 + j * 14, _label(attr, 24), INK, 1)
        centers[name] = (x + box_w, y + box_h // 2, x, y + box_h // 2)
    for rel in parsed["rels"]:
        x1 = centers[rel["left"]][0]
        y1 = centers[rel["left"]][1]
        x2 = centers[rel["right"]][2]
        y2 = centers[rel["right"]][3]
        if x2 < x1:
            x1, x2 = centers[rel["left"]][2], centers[rel["right"]][0]
        canvas.line(x1, y1, x2, y2, ACCENT)
        canvas.text((x1 + x2) // 2 - 20, y1 - 18, _label(rel["label"], 16), MUTED, 1)
        canvas.text(x1 + 2, y1 + 4, rel["left_card"], MUTED, 1)
        canvas.text(x2 - 24, y2 + 4, rel["right_card"], MUTED, 1)
    canvas.text(16, height - 28, "Cardinality marks follow Mermaid crow-foot spelling. Not a formal UML claim.", MUTED, 1)
    return canvas


def draw_flow(parsed: dict) -> Canvas:
    names = list(parsed["nodes"])
    box_w, box_h = 160, 48
    if parsed["direction"] == "TD":
        width, height = 360, 40 + len(names) * 100
    else:
        width, height = 40 + len(names) * 220, 220
    canvas = Canvas(max(width, 320), max(height, 180))
    canvas.text(12, 10, "Flow. Arrow means movement, a layer, or ownership, as labelled.", INK, 1)
    pos = {}
    for i, name in enumerate(names):
        if parsed["direction"] == "TD":
            x, y = 80, 40 + i * 90
        else:
            x, y = 20 + i * 210, 70
        pos[name] = (x, y)
        canvas.rect(x, y, box_w, box_h, ACCENT, fill=False)
        canvas.text(x + 8, y + 16, _label(parsed["nodes"][name], 16), INK, 1)
    for edge in parsed["edges"]:
        x1, y1 = pos[edge["src"]]
        x2, y2 = pos[edge["dst"]]
        if parsed["direction"] == "TD":
            canvas.line(x1 + box_w // 2, y1 + box_h, x2 + box_w // 2, y2, ACCENT)
            canvas.text(x1 + box_w // 2 + 6, (y1 + y2) // 2, _label(edge["label"], 18), MUTED, 1)
        else:
            canvas.line(x1 + box_w, y1 + box_h // 2, x2, y2 + box_h // 2, ACCENT)
            canvas.text(x1 + box_w + 4, y1 + 4, _label(edge["label"], 16), MUTED, 1)
    canvas.text(12, canvas.h - 24, "Legend is local communication, not an official method notation.", MUTED, 1)
    return canvas


def render_mermaid(source: str) -> Canvas:
    first = next((ln.strip() for ln in source.splitlines() if ln.strip()), "")
    if first.startswith("erDiagram"):
        return draw_er(parse_er(source))
    if first.startswith("flowchart"):
        return draw_flow(parse_flow(source))
    raise ModelError(
        f"This exporter draws erDiagram and flowchart only. It will not hide an unsupported diagram ({first or 'empty'}).",
        "diagram",
    )


def _png(canvas: Canvas) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return len(data).to_bytes(4, "big") + tag + data + zlib.crc32(tag + data).to_bytes(4, "big")

    raw = bytearray()
    row = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * row : (y + 1) * row]
    ihdr = canvas.w.to_bytes(4, "big") + canvas.h.to_bytes(4, "big") + bytes([8, 2, 0, 0, 0])
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrap(text: str, width: int = 90) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) > width:
            if cur:
                lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines or [""]


def build_pdf(title: str, sections: list[tuple[str, list[str]]], images: list[tuple[str, Canvas]]) -> bytes:
    """One PDF. Images are Flate-compressed RGB XObjects, not Mermaid source."""
    page_w, page_h = 612, 792
    margin = 48
    pages: list[tuple[str, list[int]]] = []
    image_objs = []
    # Build content streams referencing image indexes.
    content_parts: list[list[str]] = [[]]
    image_use: list[list[tuple[int, int]]] = [[]]  # (image index, y) per page — y tracked in stream directly

    def new_page():
        content_parts.append([])
        return len(content_parts) - 1

    y = page_h - margin

    def ensure(height: int):
        nonlocal y
        if y - height < margin:
            new_page()
            y = page_h - margin

    def add_text(size: int, text: str):
        nonlocal y
        for line in _wrap(text, 95 if size <= 11 else 80):
            ensure(size + 4)
            content_parts[-1].append(f"BT /F1 {size} Tf {margin} {y - size} Td ({_pdf_escape(line)}) Tj ET")
            y -= size + 4

    add_text(16, title)
    y -= 6
    for heading, paras in sections:
        add_text(13, heading)
        for para in paras:
            add_text(10, para)
        y -= 6
    for index, (caption, canvas) in enumerate(images):
        add_text(11, caption)
        scale = min(1.0, (page_w - 2 * margin) / canvas.w, 360 / canvas.h)
        dw, dh = canvas.w * scale, canvas.h * scale
        ensure(int(dh) + 12)
        y -= int(dh)
        content_parts[-1].append(
            f"q {dw:.2f} 0 0 {dh:.2f} {margin} {y} cm /Im{index + 1} Do Q"
        )
        y -= 16
        image_objs.append(canvas)
    # Assemble objects.
    streams = []
    for part in content_parts:
        data = ("\n".join(part) + "\n").encode("latin-1", errors="replace")
        streams.append(data)
    objects: list[bytes] = []

    def add_obj(body: bytes) -> int:
        objects.append(body)
        return len(objects)

    catalog_id = add_obj(b"<< /Type /Catalog /Pages 2 0 R >>")
    # pages object filled later
    pages_id = add_obj(b"")  # placeholder index 2
    page_ids = []
    content_ids = []
    for data in streams:
        content_ids.append(add_obj(b"<< /Length %d >>\nstream\n" % len(data) + data + b"endstream"))
    image_ids = []
    for canvas in image_objs:
        raw = zlib.compress(bytes(canvas.px), 9)
        header = (
            f"<< /Type /XObject /Subtype /Image /Width {canvas.w} /Height {canvas.h} "
            f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {len(raw)} >>\nstream\n"
        ).encode()
        image_ids.append(add_obj(header + raw + b"\nendstream"))
    font_id = add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for i, cid in enumerate(content_ids):
        xobj = " ".join(f"/Im{n + 1} {image_ids[n]} 0 R" for n in range(len(image_ids)))
        body = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_w} {page_h}] "
            f"/Contents {cid} 0 R /Resources << /Font << /F1 {font_id} 0 R >> "
            f"/XObject << {xobj} >> >> >>"
        ).encode()
        page_ids.append(add_obj(body))
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects[pages_id - 1] = f"<< /Type /Pages /Count {len(page_ids)} /Kids [{kids}] >>".encode()
    # Write file with xref.
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        f"trailer << /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    ).encode()
    return bytes(out)


def _fences(text: str) -> list[str]:
    return re.findall(r"```mermaid\n(.*?)```", text, flags=re.S)


def _short_sources(home: Path) -> list[str]:
    rows = []
    for did, raw in _decision_map(home):
        parsed = _parse_block(raw)
        short = parsed.get("Short source") or parsed.get("Sources") or "no source recorded"
        rows.append(f"{did} ({parsed.get('Status')}): {short}")
    return rows


def export_report(home: Path, now: str, kit_version: str) -> dict:
    moment = _now(now)
    index = _index(home)
    proposed = _proposed_text(home)
    confirmed = _confirmed_text(home)
    before_proposed = proposed
    before_confirmed = confirmed
    approvals = current_approvals(home)
    fences = _fences(proposed) + _fences(confirmed)
    if not fences:
        raise ModelError("The saved model has no diagram to render. The PDF is not written.", "diagram")
    images = []
    for i, fence in enumerate(fences, start=1):
        try:
            images.append((f"Diagram {i}", render_mermaid(fence)))
        except ModelError:
            raise
        if images[-1][1].dark_pixels() < 50:
            raise ModelError("A diagram rendered as a blank image. The PDF is not written.", "diagram")
    revision = index["Revision"]
    approval_lines = list(approvals.values()) or ["No stage is approved."]
    questions = (home / "questions.md").read_text(encoding="utf-8")
    comparisons = (home / "comparisons.md").read_text(encoding="utf-8")
    sources = (home / "sources.md").read_text(encoding="utf-8")
    version = f"{revision}-{_stamp(moment)}"
    summary = [
        f"Model {index['Model']} at revision {revision}. Flow recorded: {index['Flow']}.",
        "Approval applies only to the stage and revision named below. A business-model approval is not a physical-design approval.",
        "Proposed text that is not in the confirmed file is a proposal. Conditional text is not implementable.",
        "This review reads the saved files. It does not model again.",
    ]
    status = [
        f"Revision: {revision}",
        f"Scope confirmed: {index.get('Scope confirmed', 'no')}",
        *[f"Current {line}" for line in approval_lines],
    ]
    sections_md = [
        ("## Summary", summary),
        ("## Status", status),
        ("## Recommendation and decisions", [proposed.strip()]),
        ("## Confirmed snapshot", [confirmed.strip()]),
        ("## Comparisons", [comparisons.strip()]),
        ("## Worked examples and questions", [questions.strip()]),
        ("## Why, with short sources", _short_sources(home) or ["No decisions recorded."]),
        ("## Diagrams", [
            "The Markdown keeps the Mermaid source. The PDF draws that same revision as pictures.",
            "A picture is not proof of a modeling method, an enforced key, or an empirical result.",
            proposed[proposed.find("## Diagrams") :] if "## Diagrams" in proposed else "",
        ]),
        ("## Sources", [sources.strip()]),
    ]
    md_lines = [
        f"# Data model review: {index['Model']}",
        "",
        f"Report: report-data-model-full · {_stamp(moment)[:8]} · kit {kit_version}",
        f"Review-Version: {version}",
        f"Model: {index['Home']}",
        f"Revision: {revision}",
        "Approval:",
        *[f"- {line}" for line in approval_lines],
        "",
        "Confirmed, proposed, conditional, and implementable are different. This file is an immutable snapshot of the saved model at this revision.",
        "",
    ]
    for heading, paras in sections_md:
        md_lines.append(heading)
        md_lines.append("")
        for para in paras:
            md_lines.append(para)
            md_lines.append("")
    md_lines.append("Comments on this review are brought back as proposed revisions. They are not approval.")
    md_lines.append("")
    pdf_sections = [(h, [p for p in paras if not p.startswith("```")]) for h, paras in sections_md]
    # Drop huge raw dumps from PDF body; keep summary, status, short sources, captions.
    pdf_sections = [
        ("Summary", summary),
        ("Status", status),
        ("Short sources beside decisions", _short_sources(home) or ["No decisions recorded."]),
        ("Review questions", [ln[4:].strip() for ln in questions.splitlines() if ln.startswith("### ")] or ["No open questions stored."]),
        ("Full source list", [pin["path"] + " @ " + pin["checked"][:12] for pin in _pins(home)] or ["No sources pinned."]),
        ("Picture limit", ["Rendered diagrams illustrate the saved Mermaid. They do not certify a method or a physical constraint."]),
    ]
    pdf = build_pdf(f"{index['Model']} {version}", pdf_sections, images)
    if b"/Subtype /Image" not in pdf:
        raise ModelError("The PDF has no rendered image.", "diagram")
    # Text showing operators sit before the first image stream. Mermaid source must not be there.
    head = pdf.split(b"/Subtype /Image", 1)[0]
    if b"erDiagram" in head or b"flowchart" in head:
        raise ModelError("The PDF text contained Mermaid source instead of a drawing.", "diagram")
    out_dir = home / "reviews" / version
    if out_dir.exists():
        raise ModelError(f"Review {version} already exists and is immutable.", "review")
    tmp = home / "reviews" / f".tmp-{version}"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    try:
        (tmp / "report.md").write_text("\n".join(md_lines), encoding="utf-8")
        (tmp / "report.pdf").write_bytes(pdf)
        tmp.rename(out_dir)
    except Exception:
        if tmp.exists():
            shutil.rmtree(tmp)
        raise
    if _proposed_text(home) != before_proposed or _confirmed_text(home) != before_confirmed:
        raise ModelError("The review export changed the saved model.", "review")
    return {
        "ok": True,
        "review": out_dir.as_posix(),
        "version": version,
        "revision": revision,
        "approvals": approval_lines,
        "diagrams": len(images),
        "model_unchanged": True,
    }


def link_line(name: str) -> str:
    _slug(name, "Model name")
    return f"Data model: docs/data-model/{name}/"


def _print(payload: dict, code: int = 0) -> int:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return code


def _read_json(path: str | None) -> dict:
    if not path:
        raise ModelError("A JSON payload is required.", "json")
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Data model state for crav1-model-data")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("discover")
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--scope", default="")

    p = sub.add_parser("init")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--flow", required=True)
    p.add_argument("--scope", default="")

    p = sub.add_parser("recommend")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--json", dest="payload", required=True)

    p = sub.add_parser("example")
    p.add_argument("--home", type=Path)
    p.add_argument("--kind", required=True)
    p.add_argument("--json", dest="payload", required=True)

    p = sub.add_parser("decide")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--json", dest="payload", required=True)

    p = sub.add_parser("question")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--json", dest="payload", required=True)

    p = sub.add_parser("diagram")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--kind", required=True)
    p.add_argument("--caption", required=True)
    p.add_argument("--mermaid", type=Path, required=True)

    p = sub.add_parser("transition")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--kind", default="concise")
    p.add_argument("--text", required=True)

    p = sub.add_parser("views")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--json", dest="payload", required=True)

    p = sub.add_parser("confirm-scope")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--yes", action="store_true")

    p = sub.add_parser("propose-scope")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--scope", required=True)

    p = sub.add_parser("pin")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--decisions", required=True)

    p = sub.add_parser("drift")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--root", type=Path, required=True)

    p = sub.add_parser("note-drift")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--root", type=Path, required=True)

    p = sub.add_parser("approve")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--stage", required=True)
    p.add_argument("--revision", required=True)
    p.add_argument("--date", required=True)
    p.add_argument("--yes", action="store_true")

    p = sub.add_parser("auto-begin")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--minutes", type=int, required=True)
    p.add_argument("--passes", type=int, required=True)
    p.add_argument("--now", required=True)

    p = sub.add_parser("auto-pass")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--fingerprint", required=True)
    p.add_argument("--unresolved", type=int, required=True)
    p.add_argument("--progress", required=True)
    p.add_argument("--now", required=True)
    p.add_argument("--text", default=None)
    p.add_argument("--stage", default=None)

    p = sub.add_parser("auto-finish")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--root", type=Path, required=True)

    p = sub.add_parser("feedback")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--review", type=Path, required=True)
    p.add_argument("--comment", required=True)
    p.add_argument("--decision", required=True)

    p = sub.add_parser("report")
    p.add_argument("--home", type=Path, required=True)
    p.add_argument("--now", required=True)
    p.add_argument("--kit", default="1.118.0")

    p = sub.add_parser("link-line")
    p.add_argument("--name", required=True)

    args = parser.parse_args(argv)
    try:
        if args.cmd == "discover":
            payload = discover(args.root, args.scope or None)
        elif args.cmd == "init":
            payload = init_model(args.home, args.name, args.flow, args.scope or None)
        elif args.cmd == "recommend":
            payload = recommend(args.home, _read_json(args.payload))
        elif args.cmd == "example":
            body = _read_json(args.payload)
            payload = add_example(args.home, args.kind, body) if args.home else check_example(args.kind, body)
        elif args.cmd == "decide":
            payload = add_decision(args.home, _read_json(args.payload))
        elif args.cmd == "question":
            payload = add_question(args.home, _read_json(args.payload))
        elif args.cmd == "diagram":
            payload = add_diagram(args.home, args.id, args.kind, args.caption, args.mermaid.read_text(encoding="utf-8"))
        elif args.cmd == "transition":
            payload = set_transition(args.home, args.text, args.kind)
        elif args.cmd == "views":
            payload = set_views(args.home, _read_json(args.payload))
        elif args.cmd == "confirm-scope":
            payload = confirm_scope(args.home, args.yes)
        elif args.cmd == "propose-scope":
            payload = propose_scope(args.home, args.scope)
        elif args.cmd == "pin":
            payload = pin_source(args.home, args.root, args.source, [d for d in args.decisions.split(",") if d])
        elif args.cmd == "drift":
            payload = drift(args.home, args.root)
        elif args.cmd == "note-drift":
            payload = note_drift(args.home, args.root)
        elif args.cmd == "approve":
            payload = approve(args.home, args.stage, args.revision, args.date, args.yes)
        elif args.cmd == "auto-begin":
            payload = auto_begin(args.home, args.minutes, args.passes, args.now)
        elif args.cmd == "auto-pass":
            payload = auto_pass(args.home, args.fingerprint, args.unresolved, args.progress, args.now, args.text, args.stage)
        elif args.cmd == "auto-finish":
            payload = auto_finish(args.home, args.root)
        elif args.cmd == "feedback":
            payload = feedback(args.home, args.review, args.comment, args.decision)
        elif args.cmd == "report":
            payload = export_report(args.home, args.now, args.kit)
        elif args.cmd == "link-line":
            payload = {"ok": True, "line": link_line(args.name)}
        else:
            raise ModelError("Unknown command.", "cli")
        return _print(payload, 0)
    except ModelError as exc:
        return _print({"ok": False, "error": str(exc), "code": exc.code}, 2)


if __name__ == "__main__":
    sys.exit(main())
