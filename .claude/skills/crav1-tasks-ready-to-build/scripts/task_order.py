#!/usr/bin/env python3
"""Dependency order for a slice's tasks.md (kit 1.103.0, text split 1.127.0).

Reads `- [ ] T#: ...` / `- [x] T#: ...` lines. A task's dependencies are its `(after: T1, T3)` mark; a task
with no `(after: ...)` waits on the task just before it in the file (the first task waits on nothing).
Dependency order is a topological sort in waves (a task's wave is one more than its latest dependency's),
lowest task number first inside a wave.
Ready: unticked, every dependency ticked, no missing dependency, not in a cycle. Next: the ready task that
unblocks the most unticked tasks (all tasks downstream of it), lowest number on a tie.
A recorded-merged task counts as done (1.136.0), the same rule as walk_progress: `(PR n)` and the word
merged on the task line, or on the Match Branch line for its `(branch:)` or `(map:)` branch. It is not
Ready and not Next. It is listed under Needs tick while the checkbox is still open. A sibling spec.md
is read when this file is given a tasks.md path. An unapproved `## Approval needed`
item moves the tasks it holds out of Ready and into Waiting on approval (1.141.0).
A task that waits on one of those is listed there too. A matching `Approved:` line
clears the hold. The section is omitted when nothing is held.
A sibling claims.md holds a task that a build walk has claimed (1.151.0). Those
tasks leave Ready and are listed under Waiting, in progress, as
`in progress by <user> since <date>`. They are never a Next. A claim is not
cleared here.

Usage: task_order.py <tasks.md-or-spec-folder> [--failed T7,T9] [--json] [--full]
A folder uses <folder>/tasks.md. Default output is short labels (T# plus a
short title). Pass --full for the complete title. Exit 0 on success, 2 when
the file is missing or cannot be read. Standard library only. Prints nothing
secret; reads only the file it is given and a sibling spec.md.
"""
import json
import pathlib
import re
import sys

sys.dont_write_bytecode = True  # before any sibling import; no __pycache__ in the project (1.121.1)


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


_utf8_stdout()

TASK = re.compile(r"^\s*- \[( |x|X)\] T(\d+)\b[:.]?\s*(.*)$")
AFTER = re.compile(r"\(after:\s*([^)]*)\)")
BRANCH_MARK = re.compile(r"\((?:branch|map):\s*([^)]+)\)", re.I)
BRANCH_NAME = re.compile(
    r"\b((?:feature|feat|hotfix|bugfix|fix|spec|chore|bug)/[A-Za-z0-9][A-Za-z0-9._/-]*)"
)


def branch_token(value):
    """The branch in a mark. A repo prefix is the first word; the branch is the last."""
    parts = (value or "").strip().split()
    return parts[-1].strip("`.,;:") if parts else ""


def first_words(rest):
    """First readable words of a task line. Never blank."""
    text = re.sub(r"\s*\((verify|spec|after|branch|step|map):[^)]*\)", " ", rest or "")
    text = re.sub(r"\s*\(PR\s+\d+[^)]*\)", " ", text, flags=re.I)
    text = BRANCH_NAME.sub(" ", text)
    text = re.sub(r"`+", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" ,;.:")
    return text or "work"


def short_title(title, limit=60):
    """A short label for default CLI output. Cut at a word boundary with an ellipsis."""
    text = re.sub(r"\s+", " ", title or "").strip()
    if not text:
        return "work"
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    cut = cut.rstrip(" ,;.") or text[:limit].rstrip()
    return cut + "..." if cut != text else cut


_PR_MERGED = re.compile(r"\(PR\s+\d+\s*(?:,\s*merged|merged|\)\s*merged)\b", re.I)


def pr_merged(text):
    """A pull request recorded on this line is merged. Local text only.

    The word `merged` must sit on the PR mark, as in `(PR 78, merged)` or
    `(PR 78) merged`. A future line such as `(PR 12) to be merged into
    develop` is not a recorded merge.
    """
    return bool(_PR_MERGED.search(text or ""))


def merged_branch_names(spec_text):
    """Match Branch lines whose pull request is recorded merged."""
    names = set()
    for line in (spec_text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            stripped = stripped[2:].strip()
        if not stripped.lower().startswith("branch:"):
            continue
        if not pr_merged(stripped):
            continue
        body = stripped.split(":", 1)[1]
        cleaned = re.sub(r"\([^)]*\)", " ", body)
        cleaned = re.sub(r"\bmerged\b", " ", cleaned, flags=re.I)
        token = branch_token(cleaned)
        if token:
            names.add(token)
    return names


def merged_ids(tasks_text, spec_text=""):
    """Task ids that are recorded merged and still count as done (1.136.0)."""
    branches = merged_branch_names(spec_text)
    found = set()
    for line in (tasks_text or "").splitlines():
        match = TASK.match(line)
        if not match:
            continue
        number, rest = int(match.group(2)), match.group(3)
        if pr_merged(rest):
            found.add(number)
            continue
        for mark in BRANCH_MARK.finditer(rest or ""):
            token = branch_token(mark.group(1))
            if token and token in branches:
                found.add(number)
                break
    return found


def parse(text):
    tasks, prev = [], None
    for line in text.splitlines():
        m = TASK.match(line)
        if not m:
            continue
        num, rest = int(m.group(2)), m.group(3)
        a = AFTER.search(rest)
        if a:
            deps = [int(x) for x in re.findall(r"T(\d+)", a.group(1))]
            recorded = True
        else:
            deps = [prev] if prev is not None else []
            recorded = False
        title = re.sub(r"\s*\((verify|spec|after|branch|step|map):[^)]*\)", "", rest)
        title = re.sub(r"\s*\(PR\s+\d+[^)]*\)", "", title, flags=re.I)
        title = BRANCH_NAME.sub(" ", title)
        title = re.sub(r"`+", " ", title)
        title = re.sub(r"\s+", " ", title).strip(" ,;.:")
        if not title:
            title = first_words(rest)
        tasks.append({"id": num, "done": m.group(1) != " ", "title": title, "deps": deps, "recorded": recorded})
        prev = num
    return tasks


def _cycles(ids, deps):
    """Tasks that sit on a dependency cycle, with one cycle path for each."""
    on_cycle, color, stack = {}, {}, []

    def visit(n):
        color[n] = 1
        stack.append(n)
        for d in deps.get(n, []):
            if d not in ids:
                continue
            if color.get(d) == 1:
                path = stack[stack.index(d):] + [d]
                for p in path[:-1]:
                    on_cycle.setdefault(p, path)
            elif not color.get(d):
                visit(d)
        stack.pop()
        color[n] = 2

    for n in sorted(ids):
        if not color.get(n):
            visit(n)
    return on_cycle


def analyse(tasks, failed=(), merged=()):
    merged = set(merged or ())
    needs_tick = []
    for task in tasks:
        if task["id"] in merged and not task["done"]:
            needs_tick.append({"id": task["id"], "title": task["title"]})
            task["done"] = True
    ids = {t["id"] for t in tasks}
    by = {t["id"]: t for t in tasks}
    deps = {t["id"]: t["deps"] for t in tasks}
    users = {i: [] for i in ids}
    for t in tasks:
        for d in t["deps"]:
            if d in ids:
                users[d].append(t["id"])
    cyc = _cycles(ids, deps)

    # Kahn in waves: a task's wave is one more than its latest dependency's wave. Order is wave by wave,
    # lowest number first inside a wave (tasks in one wave can run in parallel). Cycle members go last.
    indeg = {i: sum(1 for d in deps[i] if d in ids) for i in ids}
    wave = {i: 0 for i in ids if indeg[i] == 0}
    frontier = sorted(wave)
    while frontier:
        nxt_frontier = []
        for n in frontier:
            for u in users[n]:
                indeg[u] -= 1
                wave[u] = max(wave.get(u, 0), wave[n] + 1)
                if indeg[u] == 0:
                    nxt_frontier.append(u)
        frontier = sorted(nxt_frontier)
    placed = [i for i in ids if indeg[i] == 0]
    order = sorted(placed, key=lambda i: (wave[i], i)) + sorted(ids - set(placed))

    def downstream(n):
        seen, todo = set(), list(users[n])
        while todo:
            u = todo.pop()
            if u not in seen:
                seen.add(u)
                todo.extend(users[u])
        return seen

    failed = set(failed)
    rows = []
    for n in order:
        t = by[n]
        if t["done"]:
            continue
        missing = [d for d in t["deps"] if d not in ids]
        open_deps = [d for d in t["deps"] if d in ids and not by[d]["done"]]
        tag = "recorded" if t["recorded"] else "inferred"
        if n in cyc:
            reason = "cycle " + " → ".join(f"T{x}" for x in cyc[n]) + " (recorded)"
        elif missing:
            reason = "after: " + ", ".join(f"T{x}" for x in missing) + " names no task (recorded)"
        elif open_deps:
            reason = "waits on " + ", ".join(f"T{x}" for x in open_deps) + f" ({tag})"
        else:
            reason = None
        rows.append({"id": n, "title": t["title"], "ready": reason is None, "reason": reason,
                     "unblocks": len([u for u in downstream(n) if not by[u]["done"]])})
    ready = [r for r in rows if r["ready"]]
    nxt = min(ready, key=lambda r: (-r["unblocks"], r["id"]))["id"] if ready else None
    failed_deps = {}
    for f in sorted(failed):
        if f in ids:
            for u in downstream(f):
                failed_deps.setdefault(u, f)
    return {"order": [n for n in order if not by[n]["done"]], "ready": [r["id"] for r in ready],
            "blocked": [r for r in rows if not r["ready"]], "next": nxt,
            "needs_tick": needs_tick,
            "depends_on_failed": {f"T{k}": f"depends on T{v} (failed)" for k, v in sorted(failed_deps.items())},
            "rows": rows}


def _order_wait(reason):
    """A wait on a real earlier task. A cycle, or an after: that names no task, is a blocker."""
    text = (reason or "").lower()
    if "cycle" in text or "names no task" in text:
        return False
    return "waits on t" in text


def _split_blocked(blocked):
    waits = [item for item in blocked if _order_wait(item.get("reason"))]
    blockers = [item for item in blocked if not _order_wait(item.get("reason"))]
    return waits, blockers


def _wait_line(row, full=False):
    title = (row.get("title") or "").strip()
    if title and not full:
        title = short_title(title)
    if title:
        return f"- T{row['id']} {title}: {row['reason']}"
    return f"- T{row['id']}: {row['reason']}"


def _approval_mod():
    import importlib.util

    path = pathlib.Path(__file__).resolve().parents[2] / "crav1-record-approval" / "scripts" / "approval_needed.py"
    spec = importlib.util.spec_from_file_location("approval_needed", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def apply_approval_holds(res, tasks, spec_text):
    """Move tasks an unapproved Approval needed item holds out of Ready.

    A task that only waits on one of those moves too. A cycle, or an after
    that names no task, stays blocked. analyse() is unchanged when this is
    not called.
    """
    waiting = []
    if not spec_text:
        res["waiting_on_approval"] = waiting
        return res
    ids = [f"T{task['id']}" for task in tasks]
    held = dict(_approval_mod().holds(spec_text, ids))
    for task in tasks:
        if task["done"]:
            held.pop(f"T{task['id']}", None)
    if not held:
        res["waiting_on_approval"] = waiting
        return res
    changed = True
    while changed:
        changed = False
        for task in tasks:
            if task["done"]:
                continue
            tid = f"T{task['id']}"
            if tid in held:
                continue
            for dep in task["deps"]:
                via = f"T{dep}"
                if via not in held:
                    continue
                held[tid] = {**held[via], "via": via}
                changed = True
                break

    def take(row):
        tid = f"T{row['id']}"
        info = held.get(tid)
        if not info:
            return False
        reason = row.get("reason") or ""
        if "cycle" in reason.lower() or "names no task" in reason.lower():
            return False
        who = info.get("who") or "not named yet"
        if info.get("via"):
            shown = f"held, waits on {info['via']}"
        else:
            shown = f"waiting for {who}"
        waiting.append({"id": row["id"], "title": row.get("title") or "", "reason": shown, "who": who})
        return True

    ready_left = []
    by_row = {row["id"]: row for row in res["rows"]}
    for number in res["ready"]:
        row = by_row.get(number) or {"id": number, "title": "", "reason": None}
        if take(row):
            row["ready"] = False
            row["reason"] = waiting[-1]["reason"]
        else:
            ready_left.append(number)
    blocked_left = []
    for row in res["blocked"]:
        if take(row):
            row["reason"] = waiting[-1]["reason"]
        else:
            blocked_left.append(row)
    res["ready"] = ready_left
    res["blocked"] = blocked_left
    res["waiting_on_approval"] = waiting
    ready_rows = [row for row in res["rows"] if row["id"] in set(ready_left)]
    res["next"] = min(ready_rows, key=lambda row: (-row["unblocks"], row["id"]))["id"] if ready_rows else None
    return res


def _claims_mod():
    import importlib.util

    path = pathlib.Path(__file__).resolve().parents[2] / "crav1-build-walk" / "scripts" / "claims.py"
    spec = importlib.util.spec_from_file_location("claims", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def apply_claim_holds(res, tasks, claims_text, now=None):
    """Move claimed tasks out of Ready into Waiting, in progress (1.151.0)."""
    waiting = []
    res["waiting_in_progress"] = waiting
    if not claims_text:
        return res
    parsed = _claims_mod().parse_claims(claims_text, now=now)
    claims = parsed.get("claims") or []
    if not claims:
        return res
    by_task = {}
    for claim in claims:
        for task in claim["tasks"]:
            by_task[task] = claim
    held = {}
    for task in tasks:
        if task["done"]:
            continue
        tid = f"T{task['id']}"
        if tid in by_task:
            held[tid] = by_task[tid]
    changed = True
    while changed:
        changed = False
        for task in tasks:
            if task["done"]:
                continue
            tid = f"T{task['id']}"
            if tid in held:
                continue
            for dep in task["deps"]:
                via = f"T{dep}"
                if via not in held:
                    continue
                held[tid] = {**held[via], "via": via}
                changed = True
                break

    def take(row):
        tid = f"T{row['id']}"
        info = held.get(tid)
        if not info:
            return False
        reason = row.get("reason") or ""
        if "cycle" in reason.lower() or "names no task" in reason.lower():
            return False
        if info.get("via"):
            shown = f"held, waits on {info['via']}"
        else:
            shown = info.get("phrase") or f"in progress by {info.get('user') or 'someone'} since {info.get('since_date') or 'unknown'}"
        waiting.append({"id": row["id"], "title": row.get("title") or "", "reason": shown, "who": info.get("user")})
        return True

    ready_left = []
    by_row = {row["id"]: row for row in res["rows"]}
    for number in res["ready"]:
        row = by_row.get(number) or {"id": number, "title": "", "reason": None}
        if take(row):
            row["ready"] = False
            row["reason"] = waiting[-1]["reason"]
        else:
            ready_left.append(number)
    blocked_left = []
    for row in res["blocked"]:
        if take(row):
            row["reason"] = waiting[-1]["reason"]
        else:
            blocked_left.append(row)
    res["ready"] = ready_left
    res["blocked"] = blocked_left
    res["waiting_in_progress"] = waiting
    ready_rows = [row for row in res["rows"] if row["id"] in set(ready_left)]
    res["next"] = min(ready_rows, key=lambda row: (-row["unblocks"], row["id"]))["id"] if ready_rows else None
    return res


def render(res, full=False):
    waits, blockers = _split_blocked(res["blocked"])

    def shown(title):
        text = (title or "").strip() or "work"
        return text if full else short_title(text)

    out = ["Ready (dependency order)"]
    out += [f"- T{r['id']}: {shown(r['title'])}" for r in res["rows"] if r["ready"]] or ["- none"]
    out.append("Waits in order (dependency order)")
    out += [_wait_line(r, full=full) for r in waits] or ["- none"]
    approvals = res.get("waiting_on_approval") or []
    if approvals:
        out.append("Waiting on approval")
        for row in approvals:
            title = shown(row.get("title"))
            label = f"T{row['id']} {title}".strip()
            out.append(f"- {label}: {row['reason']}")
    in_progress = res.get("waiting_in_progress") or []
    if in_progress:
        out.append("Waiting, in progress")
        for row in in_progress:
            title = shown(row.get("title"))
            label = f"T{row['id']} {title}".strip()
            out.append(f"- {label}: {row['reason']}")
    out.append("Blocked (dependency order)")
    out += [f"- T{r['id']}: {r['reason']}" for r in blockers] or ["- none"]
    needs = res.get("needs_tick") or []
    if needs:
        out.append("Needs tick")
        out += [f"- T{r['id']}: {shown(r['title'])}" for r in needs]
    out.append("Order: " + " → ".join(f"T{n}" for n in res["order"]))
    out.append(f"Next: T{res['next']}" if res["next"] else "Next: none ready")
    for k, v in res["depends_on_failed"].items():
        out.append(f"{k}: {v}")
    return "\n".join(out)


def _tid(n):
    if n is None:
        return None
    return f"T{n}"


def public(res):
    """JSON shape. Task ids are T1 style. analyse() itself still uses ints."""
    def row(item):
        return {**item, "id": _tid(item["id"])}

    waits, blockers = _split_blocked(res["blocked"])
    return {
        "order": [_tid(n) for n in res["order"]],
        "ready": [_tid(n) for n in res["ready"]],
        "waits_in_order": [row(item) for item in waits],
        "blocked": [row(item) for item in blockers],
        "next": _tid(res["next"]),
        "needs_tick": [row(item) for item in res.get("needs_tick") or []],
        "waiting_on_approval": [row(item) for item in res.get("waiting_on_approval") or []],
        "waiting_in_progress": [row(item) for item in res.get("waiting_in_progress") or []],
        "depends_on_failed": res["depends_on_failed"],
        "rows": [row(item) for item in res["rows"]],
    }


def emit_text(text):
    _utf8_stdout()
    try:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.flush()
    except UnicodeEncodeError:
        safe = text.replace("\u2192", "->").replace("\u2014", "-")
        sys.stdout.write(safe)
        if not safe.endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.flush()


def _as_file(path, name):
    """A folder uses <folder>/<name>. A missing file is a one-line error."""
    target = pathlib.Path(path)
    if target.is_dir():
        target = target / name
    if not target.is_file():
        return None, f"{name} not found: {target}"
    try:
        return target, None
    except OSError as exc:
        return None, f"cannot read {target}: {exc}"


def main(argv):
    _utf8_stdout()
    if not argv or argv[0] in ("-h", "--help"):
        emit_text(__doc__ or "")
        return 0
    failed = []
    flags = set()
    positional = []
    i = 0
    while i < len(argv):
        if argv[i] == "--failed" and i + 1 < len(argv):
            failed = [int(x) for x in re.findall(r"\d+", argv[i + 1])]
            i += 2
            continue
        if argv[i] in ("--json", "--full"):
            flags.add(argv[i])
            i += 1
            continue
        positional.append(argv[i])
        i += 1
    if not positional:
        emit_text("tasks.md not found: (no path given)")
        return 2
    tasks_path, err = _as_file(positional[0], "tasks.md")
    if err:
        emit_text(err)
        return 2
    try:
        text = tasks_path.read_text(encoding="utf-8")
    except OSError:
        emit_text(f"cannot read {tasks_path}")
        return 2
    spec_path = tasks_path.parent / "spec.md"
    try:
        spec_text = spec_path.read_text(encoding="utf-8") if spec_path.is_file() else ""
    except OSError:
        spec_text = ""
    parsed = parse(text)
    res = analyse(parsed, failed, merged_ids(text, spec_text))
    apply_approval_holds(res, parsed, spec_text)
    claims_path = tasks_path.parent / "claims.md"
    try:
        claims_text = claims_path.read_text(encoding="utf-8") if claims_path.is_file() else ""
    except OSError:
        claims_text = ""
    apply_claim_holds(res, parsed, claims_text)
    if "--json" in flags:
        emit_text(json.dumps(public(res), ensure_ascii=False, indent=1))
    else:
        emit_text(render(res, full="--full" in flags))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
