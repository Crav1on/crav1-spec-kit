#!/usr/bin/env python3
"""Computed plan checks for /crav1-plan-from-spec and /crav1-tighten-plan (kit 1.159.0).

The ordering, counts, finding queue, batch card and ending that both skills
used to work out in prose are computed here. The skill prints the stdout
as-is. It never adds, drops or rewrites a line, and never writes a second
Next line.

Commands:
  order   --root <spec-folder>
      Waves from the (after: ...) graph, the same sort the ready check uses
      (skill crav1-tasks-ready-to-build, scripts/task_order.py). Lists a
      loop, an after: that names no task, and a task line with no verify
      kind or no (spec: ...) mark.
  recap   --root <spec-folder> --branch <name> [--facts <file>] [--uncommitted <n>]
      The plan-from-spec "After writing" output, in its fixed order, ending
      with its one Next line. <file> is JSON with what only the agent can
      know: built_pieces (list of {piece, choice}), branch_read,
      security_unmapped (list), stale_checked (true once the research
      section was read).
  queue   --items <file> [--root <spec-folder>] [--went-on-without-linter] [--uncommitted <n>]
      The tighten-plan index (remaining P# titles, current marked, plan or
      spec), the finding counts, and, when no plan P# is open, the one
      empty-queue Next line.
  batch   --items <file> [--title <text>]
      The findings table and its Card: line for every open plan P#, built
      by batch_offer.py in this same reply. No open plan P#, no card.
  reviewed --root <spec-folder> --open <n> [--write]
      Lowers P# open on the Reviewed line, keeping the date. No line, none added.

<file> for queue and batch is JSON: a list of objects with id, issue,
tag (plan or spec), status (open, patched, dropped, skipped, kept), and, for
spec findings, kind (defect or question). Batch rows also need options and
recommendation. One row may have "current": true.

Usage: <interpreter> -X utf8 scripts/plan_check.py <command> ...
On Windows the interpreter is python. Elsewhere python3, then py -3.
Standard library only. Exit 0 on success, 2 on a missing file or bad input.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

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


class PlanCheckError(Exception):
    """Input that cannot be checked. One line on stderr, exit 2."""


def _sibling(skill: str, name: str) -> Path:
    here = Path(__file__).resolve().parent
    # <skills>/<this-skill>/scripts -> <skills>/<skill>/scripts/<name>
    for base in (here.parent.parent, here.parent.parent.parent):
        candidate = base / skill / "scripts" / name
        if candidate.is_file():
            return candidate
    raise PlanCheckError(f"{name} was not found in {skill}/scripts")


def _load(skill: str, name: str, alias: str):
    path = _sibling(skill, name)
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _task_order():
    return _load("crav1-tasks-ready-to-build", "task_order.py", "plan_check_task_order")


def _batch_offer():
    return _load("crav1-tighten-plan", "batch_offer.py", "plan_check_batch_offer")


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except OSError as exc:
        raise PlanCheckError(f"cannot read {path}: {exc.strerror or exc}") from exc


def _root(value: str) -> Path:
    root = Path(value)
    if not root.is_dir():
        raise PlanCheckError(f"spec folder not found: {root}")
    return root


def section(text: str, heading: str) -> str:
    """Body of `## <heading>` (case-insensitive prefix match), up to the next `## `."""
    out: list[str] = []
    inside = False
    for line in text.splitlines():
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].strip().lower().startswith(heading.lower())
            continue
        if inside:
            out.append(line)
    return "\n".join(out).strip()


def has_section(text: str, heading: str) -> bool:
    return any(line.startswith("## ") and line[3:].strip().lower().startswith(heading.lower())
               for line in text.splitlines())


# ---------- order ----------

KINDS = ("unit", "system", "browser", "integration", "contract", "load", "speed",
         "accessibility", "golden", "property", "manual")
TASK_LINE = re.compile(r"^\s*-\s*\[( |x|X)\]\s*T(\d+)\s*:\s*(.*)$")
VERIFY = re.compile(r"\(verify:\s*([^)]*)\)", re.I)


def waves(tasks: list[dict]) -> tuple[list[list[int]], set[int]]:
    """Waves over every task, done or not. Wave 1 waits on nothing. Loop members are left out."""
    ids = {t["id"] for t in tasks}
    deps = {t["id"]: [d for d in t["deps"] if d in ids] for t in tasks}
    wave: dict[int, int] = {}
    remaining = set(ids)
    level = 0
    while remaining:
        layer = sorted(i for i in remaining if all(d in wave for d in deps[i]))
        if not layer:
            break
        for i in layer:
            wave[i] = level
        remaining -= set(layer)
        level += 1
    out: list[list[int]] = []
    for i, w in sorted(wave.items(), key=lambda kv: (kv[1], kv[0])):
        while len(out) <= w:
            out.append([])
        out[w].append(i)
    return out, remaining


def line_problems(text: str) -> list[str]:
    problems: list[str] = []
    for line in text.splitlines():
        m = TASK_LINE.match(line)
        if not m:
            continue
        tid, rest = f"T{m.group(2)}", m.group(3)
        setup = "(host setup)" in rest.lower() or "manual" in rest.lower()
        verify = VERIFY.search(rest)
        if not verify:
            if not setup:
                problems.append(f"{tid} has no verify note")
        else:
            head = re.split(r"\s+[—–-]\s+|:", verify.group(1).strip(), maxsplit=1)[0].strip().lower()
            words = re.findall(r"[a-z]+", head)
            if not setup and not any(w in KINDS for w in words):
                problems.append(f"{tid} verify note names no kind")
        if not re.search(r"\(spec:\s*[^)]+\)", rest, re.I):
            problems.append(f"{tid} has no (spec: ...) mark")
    return problems


def order_lines(root: Path) -> list[str]:
    text = _read(root / "tasks.md")
    if not text.strip():
        raise PlanCheckError(f"tasks.md not found: {root / 'tasks.md'}")
    to = _task_order()
    tasks = to.parse(text)
    ids = {t["id"] for t in tasks}
    layers, looped = waves(tasks)
    lines = ["Order (dependency waves; a task in one wave can start together with the others in it):"]
    for n, layer in enumerate(layers, start=1):
        lines.append(f"- Wave {n}: " + ", ".join(f"T{i}" for i in layer))
    cycles = to._cycles(ids, {t["id"]: t["deps"] for t in tasks}) if tasks else {}
    seen: set[tuple[int, ...]] = set()
    for tid in sorted(cycles):
        path = tuple(cycles[tid])
        key = tuple(sorted(set(path)))
        if key in seen:
            continue
        seen.add(key)
        lines.append("- Loop: " + " → ".join(f"T{x}" for x in path) + ". Fix one (after: ...) mark.")
    leftover = sorted(looped - set(cycles))
    if leftover:
        lines.append("- Waits on a loop: " + ", ".join(f"T{i}" for i in leftover))
    for t in tasks:
        missing = [d for d in t["deps"] if d not in ids]
        if missing and t["recorded"]:
            lines.append(f"- T{t['id']}: after: " + ", ".join(f"T{x}" for x in missing) + " names no task")
    inferred = [t["id"] for t in tasks if not t["recorded"] and t["deps"]]
    if inferred:
        lines.append("- Inferred from file order (no after: mark): " + ", ".join(f"T{i}" for i in inferred))
    return lines


# ---------- recap (plan-from-spec After writing) ----------

def _norm(text: str) -> str:
    text = re.sub(r"[`*_]", "", text.lower())
    text = re.sub(r"^\s*-\s*(\[[ xX]\]\s*)?", "", text)
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def acceptance_lines(spec: str) -> list[str]:
    out = []
    for line in section(spec, "Acceptance").splitlines():
        if re.match(r"^\s*-\s", line):
            body = re.sub(r"^\s*-\s*(\[[ xX]\]\s*)?", "", line).strip()
            if body:
                out.append(body)
    return out


def trace_rows(plan: str) -> list[tuple[str, str]]:
    body = section(plan, "Trace") or section(plan, "Requirements trace")
    rows = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2 or set(cells[0]) <= set("-: ") or cells[0].lower().startswith("acceptance"):
            continue
        rows.append((cells[0], cells[1]))
    return rows


def _ids(text: str) -> set[str]:
    return set(re.findall(r"\b(?:REQ|AC|A)-?\d+\b", text, re.I))


# The match is by wording only, so a reworded line can be listed when a task
# does cover it. The note tells the agent to compare by meaning first.
ACCEPTANCE_HEAD = "Check these acceptance lines, no task matched their wording: "
ACCEPTANCE_NOTE = (" (compare each by meaning with the trace table and tasks first. A line a task covers needs"
                   " only its trace row or (spec: ...) mark. A line nothing covers is missing: the plan is not done"
                   " until it has a task, already there, or left as committed)")


def untraced(spec: str, plan: str, tasks_text: str) -> list[str]:
    rows = trace_rows(plan)
    marks = [m.group(1) for m in re.finditer(r"\(spec:\s*([^)]+)\)", tasks_text, re.I)]
    covered: list[str] = []
    for key, tasks in rows:
        cell = tasks.lower()
        if re.search(r"\bT\d+\b", tasks, re.I) or "already there" in cell or "left as committed" in cell or "covered by" in cell:
            covered.append(key)
    covered += marks
    keys = [_norm(k) for k in covered if _norm(k)]
    idsets = [_ids(k) for k in covered]
    missing = []
    for line in acceptance_lines(spec):
        n = _norm(line)
        if not n:
            continue
        if any(k in n or n in k for k in keys):
            continue
        if any(_ids(line) & ids for ids in idsets if ids):
            continue
        head = " ".join(n.split()[:4])
        if any(head and head in k for k in keys):
            continue
        missing.append(line)
    return missing


def trace_problems(plan: str, tasks_text: str) -> list[str]:
    known = {f"T{m.group(2)}" for m in map(TASK_LINE.match, tasks_text.splitlines()) if m}
    out = []
    for key, tasks in trace_rows(plan):
        for tid in re.findall(r"\bT\d+\b", tasks):
            if tid not in known:
                out.append(f"Trace row {key!r} names {tid}, which is not in tasks.md")
    return out


def open_questions(spec: str) -> list[str]:
    """Each kept-open question with its Blocks line, one line each."""
    out: list[str] = []
    current = None
    blocks = None
    for line in section(spec, "Open questions").splitlines():
        top = re.match(r"^-\s+(.*\S)", line)
        sub = re.match(r"^\s+-\s+Blocks:\s*(.*\S)", line)
        if top:
            if current:
                out.append(current + (f" Blocks: {blocks}" if blocks else " No Blocks line."))
            current, blocks = top.group(1), None
        elif sub and current:
            blocks = sub.group(1)
    if current:
        out.append(current + (f" Blocks: {blocks}" if blocks else " No Blocks line."))
    return [q for q in out if not q.lower().startswith(("none", "resolved"))]


def approval_items(spec: str) -> list[str]:
    out: list[str] = []
    item = None
    extra: list[str] = []
    for line in section(spec, "Approval needed").splitlines():
        top = re.match(r"^-\s+(.*\S)", line)
        sub = re.match(r"^\s+-\s+(Person|Holds|Approved):\s*(.*\S)", line)
        if top:
            if item:
                out.append(item + (" (" + "; ".join(extra) + ")" if extra else ""))
            item, extra = top.group(1), []
        elif sub and item:
            extra.append(f"{sub.group(1)}: {sub.group(2)}")
    if item:
        out.append(item + (" (" + "; ".join(extra) + ")" if extra else ""))
    return out


def stale_lines(spec: str) -> list[str]:
    return [l.strip("- ").strip() for l in section(spec, "Research findings").splitlines() if "stale since" in l.lower()]


NO_LINTER = re.compile(r"\b(no|none|not have|has no|lacks|without)\b[^.]*\b(linter|checker|lint)\b|^\W*none\W*$", re.I)


def linter_line(plan: str) -> tuple[str, bool]:
    """(text, named). named is False when the section is missing, empty, or says there is none."""
    body = section(plan, "Linter")
    text = " ".join(l.strip("- ").strip() for l in body.splitlines() if l.strip("- ").strip())
    if not text:
        return ("", False)
    return (text, not NO_LINTER.search(text))


def recap(root: Path, branch: str, facts: dict, uncommitted: int | None) -> str:
    spec, plan, tasks_text = (_read(root / n) for n in ("spec.md", "plan.md", "tasks.md"))
    if not plan.strip() or not tasks_text.strip():
        raise PlanCheckError("plan.md and tasks.md must be written before the recap")
    slug = root.name
    rel = f"docs/specs/{slug}"
    written = [f"{rel}/plan.md", f"{rel}/tasks.md"]
    for name in ("design.md", "tasks.md"):
        if (root / "export/openspec" / name).is_file():
            written.append(f"{rel}/export/openspec/{name}")
    task_ids = [m.group(2) for m in map(TASK_LINE.match, tasks_text.splitlines()) if m]
    out = ["Written: " + ", ".join(written)]
    missing = untraced(spec, plan, tasks_text)
    out.append(f"Tasks: {len(task_ids)}. {ACCEPTANCE_HEAD}" + ("none" if not missing else "; ".join(missing) + ACCEPTANCE_NOTE))
    out += order_lines(root)
    for piece in facts.get("built_pieces") or []:
        out.append(f"Built piece: {piece.get('piece')}: {piece.get('choice')}")
    if facts.get("branch_read"):
        out.append(f"Branch read: {facts['branch_read']}")
    problems = line_problems(tasks_text) + trace_problems(plan, tasks_text)
    out.append("Verify notes with no kind, and other task-line gaps: " + ("none" if not problems else "; ".join(problems)))
    security = facts.get("security_unmapped") or []
    out.append("Kept security checks with no task: " + ("none" if not security else "; ".join(security)))
    questions = open_questions(spec)
    out.append("Kept-open questions parked as risks:" + (" none" if not questions else ""))
    out += [f"- {q}" for q in questions]
    items = approval_items(spec)
    if items:
        out.append("Approval needed:")
        out += [f"- {i}" for i in items]
    stale = stale_lines(spec)
    out.append("Stale research under Risks: " + ("none was marked stale" if not stale else "; ".join(stale)))
    out.append("These notes name the checks. /crav1-verify-build-against-spec is the gate that says they passed.")
    text, named = linter_line(plan)
    out.append("Linter: " + (text if text else "not stated yet"))
    out.append("")
    if branch.strip() == f"spec/{slug}":
        out.append("Next: /crav1-open-pr, because this specify-only branch is not on the default branch yet.")
    else:
        out.append("Next: /crav1-review-plan, because the plan is written and not reviewed.")
        if not named:
            out.append("Build is not named until you add a linter or choose to go on without one.")
    if uncommitted:
        out.append(f"Uncommitted: {uncommitted} files; commit with /crav1-finalize-commit when ready.")
    return "\n".join(out) + "\n"


# ---------- queue (tighten-plan) ----------

DONE = {"patched", "dropped", "kept", "skipped", "done", "sent"}


def _items(path: str) -> list[dict]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise PlanCheckError(f"cannot read items file: {exc.strerror or exc}") from exc
    except json.JSONDecodeError as exc:
        raise PlanCheckError(f"items file is not JSON: {exc.msg}") from exc
    if isinstance(data, dict):
        data = data.get("items")
    if not isinstance(data, list):
        raise PlanCheckError("items file must be a JSON list of findings")
    seen = set()
    for item in data:
        if not isinstance(item, dict) or not item.get("id") or not item.get("issue"):
            raise PlanCheckError("each finding needs id and issue")
        if item["id"] in seen:
            raise PlanCheckError(f"duplicate id {item['id']}")
        seen.add(item["id"])
        tag = str(item.get("tag", "plan")).lower()
        if tag not in ("plan", "spec"):
            raise PlanCheckError(f"{item['id']}: tag is plan or spec")
        item["tag"] = tag
        item["status"] = str(item.get("status", "open")).lower()
    return sorted(data, key=lambda i: (int(re.sub(r"\D", "", str(i["id"])) or 0), str(i["id"])))


def empty_queue_next(items: list[dict], linter_named: bool, went_on: bool) -> str:
    spec = [i for i in items if i["tag"] == "spec"]
    if any(str(i.get("kind", "defect")).lower() != "question" for i in spec):
        return "Next: /crav1-tighten-spec, because that finding is a spec defect."
    if spec:
        return "Next: /crav1-resolve-open-questions, because that finding is an open question."
    if linter_named or went_on:
        return ("Next: /crav1-build-tasks, because the plan issues are done. "
                "A new chat, with plan.md, tasks.md, and spec.md attached.")
    return "Next: nothing needed now."


def queue(items: list[dict], root: Path | None, went_on: bool, uncommitted: int | None) -> str:
    open_plan = [i for i in items if i["tag"] == "plan" and i["status"] not in DONE]
    open_spec = [i for i in items if i["tag"] == "spec" and i["status"] not in DONE]
    current = next((i["id"] for i in open_plan if i.get("current")), open_plan[0]["id"] if open_plan else None)
    out: list[str] = []
    plan_n = sum(1 for i in items if i["tag"] == "plan")
    counts = {s: sum(1 for i in items if i["status"] == s) for s in ("patched", "dropped", "kept", "skipped")}
    tail = ", ".join(f"{n} {s}" for s, n in counts.items() if n)
    out.append(f"Findings: {len(items)} ({plan_n} plan, {len(items) - plan_n} spec). "
               f"Open: {len(open_plan)} plan, {len(open_spec)} spec" + (f". Done: {tail}." if tail else "."))
    remaining = open_plan + open_spec
    if remaining:
        out.append("Remaining:")
        for i in remaining:
            mark = " ← current" if i["id"] == current else ""
            if i["tag"] == "plan":
                note = "plan"
            elif str(i.get("kind", "defect")).lower() == "question":
                note = "spec, skipped for plan: /crav1-resolve-open-questions"
            else:
                note = "spec, skipped for plan: /crav1-tighten-spec"
            out.append(f"- {i['id']} {' '.join(str(i['issue']).split())} ({note}){mark}")
    if not open_plan:
        named = False
        if root is not None:
            named = linter_line(_read(root / "plan.md"))[1]
        if not remaining:
            out.append("No plan issues remain.")
        out.append("")
        out.append(empty_queue_next(items, named, went_on))
        if uncommitted:
            out.append(f"Uncommitted: {uncommitted} files; commit with /crav1-finalize-commit when ready.")
    return "\n".join(out) + "\n"


def batch(items: list[dict], title: str) -> str:
    rows = [{k: i.get(k, "") for k in ("id", "issue", "options", "recommendation")}
            for i in items if i["tag"] == "plan" and i["status"] not in DONE]
    if not rows:
        raise PlanCheckError("no open plan P#, so there is no batch card")
    bo = _batch_offer()
    try:
        return bo.offer(title, rows)
    except bo.BatchOfferError as exc:
        raise PlanCheckError(str(exc)) from exc


REVIEWED = re.compile(r"^(Reviewed:\s*[^,\n]+,\s*P#\s*open:\s*)(\d+)\s*$", re.M)


def reviewed(root: Path, open_n: int, write: bool) -> str:
    path = root / "plan.md"
    text = _read(path)
    m = REVIEWED.search(text)
    if not m:
        return "Reviewed line: none in plan.md, none added.\n"
    old = int(m.group(2))
    if open_n < 0:
        raise PlanCheckError("--open is 0 or more")
    new_text = text[: m.start(2)] + str(open_n) + text[m.end(2):]
    if write and new_text != text:
        path.write_text(new_text, encoding="utf-8")
    verb = "now" if write else "would be"
    return f"Reviewed line: P# open {old} {verb} {open_n}, date kept.\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Computed plan checks (1.159.0).")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("order")
    p.add_argument("--root", required=True)
    p = sub.add_parser("recap")
    p.add_argument("--root", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--facts")
    p.add_argument("--uncommitted", type=int)
    p = sub.add_parser("queue")
    p.add_argument("--items", required=True)
    p.add_argument("--root")
    p.add_argument("--went-on-without-linter", action="store_true")
    p.add_argument("--uncommitted", type=int)
    p = sub.add_parser("batch")
    p.add_argument("--items", required=True)
    p.add_argument("--title", default="Tighten-plan batch")
    p = sub.add_parser("reviewed")
    p.add_argument("--root", required=True)
    p.add_argument("--open", required=True, type=int)
    p.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "order":
            text = "\n".join(order_lines(_root(args.root))) + "\n"
        elif args.command == "recap":
            facts = {}
            if args.facts:
                try:
                    facts = json.loads(Path(args.facts).read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    raise PlanCheckError(f"facts file: {exc}") from exc
            text = recap(_root(args.root), args.branch, facts, args.uncommitted)
        elif args.command == "queue":
            text = queue(_items(args.items), _root(args.root) if args.root else None,
                         args.went_on_without_linter, args.uncommitted)
        elif args.command == "batch":
            text = batch(_items(args.items), args.title)
        else:
            text = reviewed(_root(args.root), args.open, args.write)
    except PlanCheckError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
