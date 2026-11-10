#!/usr/bin/env python3
"""Build map for one slice (kit 1.128.0).

Groups the open tasks onto branches: one branch per numbered step under
plan.md `## Approach` by default. A task id written in that step, or
`(step: <n>)` on the task, is the link. `(step:)` wins when both are present.
`(map: <branch>)` puts the task on that branch instead. Tasks that name the
same branch share it.

When the plan has no steps, or the steps name no task, each open task gets
its own branch and the file says so.

Waves are branch dependencies. Wave 1 does not wait for another open branch.
A later wave opens after the branches it waits for. A cycle, or an `(after:)`
that names no task, is listed under Blocked. The rendered file has no task ids.

Usage:
  build_map.py <spec-dir> [--chat] [--stdout]
  build_map.py --root <docs/specs> [--scope <words>] [--chat] [--stdout]

The interpreter is python3, then python, then py -3. The Store alias message
`Python was not found` means that command was not found.
Standard library only. Writes build-map.md in the spec folder unless --stdout.
"""
import importlib.util
import pathlib
import re
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


def _load(name):
    path = pathlib.Path(__file__).resolve().parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"crav1_build_map_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


task_order = _load("task_order")
question_blocks = _load("question_blocks")

STEP_LINE = re.compile(r"^(\d+)[.)]\s*(.*)$")
TASK_ID = re.compile(r"\bT(\d+)\b")
STEP_MARK = re.compile(r"\(step:\s*(\d+)\)")
MAP_MARK = re.compile(r"\(map:\s*([^)]*)\)")
SPEC_MARK = re.compile(r"\(spec:\s*([^)]*)\)", re.I)
TICK_PATH = re.compile(r"`([^`\n]+)`")
WORD = re.compile(r"(?<![\w-])build-map(?![\w-])")
PIPELINE = re.compile(r"(?<![\w-])pipeline runs(?![\w-])")
STOP = {
    "a", "an", "the", "and", "or", "of", "to", "for", "on", "in", "with",
    "from", "by", "its", "into",
}
NO_STEPS = "The plan has no steps, so this map uses one branch per task."
UNNAMED = "The plan steps do not name tasks, so this map uses one branch per task."
BY_STEP = "One branch per plan step."
SOME = "Some tasks are not named on a plan step, so each of those has its own branch."
MISSING_STEP = "A task names a plan step that is not in the plan, so that task has its own branch."
UNKNOWN_DEP = "a dependency that names no task"


def parse_invocation(text):
    """The word build-map selects the map. The remaining words are the scope."""
    raw = (text or "").strip()
    raw = re.sub(r"^/crav1-tasks-ready-to-build\b", "", raw).strip()
    mode = "map" if WORD.search(raw) else "report"
    raw = WORD.sub(" ", raw)
    pipeline = bool(PIPELINE.search(raw))
    raw = PIPELINE.sub(" ", raw)
    scope = re.sub(r"\s+", " ", raw).strip()
    if scope.startswith("@"):
        scope = scope[1:].strip()
    return {"mode": mode, "scope": scope, "pipeline_runs": pipeline}


def scope_folder_names(scope):
    """Folder names a scope may mean. `cc 1.0` matches `cc 1.0`, `cc-1.0`, and `cc-1-0`."""
    text = (scope or "").strip()
    if not text:
        return []
    low = text.lower()
    names = [text, low]
    spaced = re.sub(r"\s+", "-", low)
    kebab = re.sub(r"[^a-z0-9]+", "-", low).strip("-")
    for name in (spaced, kebab):
        if name and name not in names:
            names.append(name)
    return names


def clean_prose(text):
    text = re.sub(r"\((?:verify|spec|after|branch|step|map|question):[^)]*\)", "", text or "", flags=re.I)
    text = re.sub(r"\(\s*(?:T\d+\s*,?\s*)+\)", "", text)
    text = re.sub(r"\bT\d+\b", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    text = re.sub(r"\(\s*\)", "", text)
    return text.strip(" ,;")


def kebab(text, limit=4):
    words = re.findall(r"[a-z0-9]+", clean_prose(text).lower())
    words = [w for w in words if w not in STOP]
    if not words:
        words = ["work"]
    return "-".join(words[:limit])


def _section(text, heading):
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


def parse_steps(plan_text):
    steps = []
    current = None
    for line in _section(plan_text, "## Approach"):
        match = STEP_LINE.match(line.strip())
        if match and match.group(2).strip():
            if current:
                steps.append(current)
            current = {"n": int(match.group(1)), "parts": [match.group(2).strip()]}
        elif match and not match.group(2).strip():
            if current:
                steps.append(current)
            current = None
        elif current is not None:
            part = line.strip()
            if part:
                current["parts"].append(part)
    if current:
        steps.append(current)
    for step in steps:
        step["body"] = " ".join(step["parts"])
        step["ids"] = [int(n) for n in TASK_ID.findall(step["body"])]
    return steps


def task_areas(rest):
    """Shared work a branch can collide on. A note only; it does not change readiness.

    A requirement is the text of `(spec: …)`, case folded. A path is a backtick
    span that contains `/` or a file extension, compared exactly as written.
    """
    areas = set()
    for match in SPEC_MARK.finditer(rest or ""):
        token = clean_prose(match.group(1)).lower()
        if token:
            areas.add(("requirement", token))
    for match in TICK_PATH.finditer(rest or ""):
        path = match.group(1).strip()
        if " " in path:
            continue
        if "/" in path or re.search(r"\.[A-Za-z0-9]+$", path):
            areas.add(("path", path))
    return areas


def parse_tasks(text):
    parsed = task_order.parse(text or "")
    extras = []
    for line in (text or "").splitlines():
        match = task_order.TASK.match(line)
        if not match:
            continue
        rest = match.group(3)
        step = STEP_MARK.search(rest)
        mapped = MAP_MARK.search(rest)
        name = mapped.group(1).strip() if mapped else ""
        extras.append({
            "step": int(step.group(1)) if step else None,
            "map": name or None,
            "areas": task_areas(rest),
        })
    for task, extra in zip(parsed, extras):
        task.update(extra)
    return parsed


def _first_sentence(text):
    return question_blocks._first_sentence(text or "")


def _questions_for(task_id, questions):
    token = f"T{task_id}"
    holding = []
    for question in questions:
        if question["mark"] == "none":
            continue
        if question["mark"] == "tasks":
            if token in question["tasks"]:
                holding.append(question)
        elif question["blocks_slice"]:
            holding.append(question)
    return holding


def _suggest(slug, label, used):
    base = f"feat/{kebab(slug, 6)}-{kebab(label)}"
    name = base
    n = 2
    while name in used:
        name = f"{base}-{n}"
        n += 1
    used.add(name)
    return name


def _branch_cycles(names, waits):
    on_cycle, color, stack = {}, {}, []

    def visit(node):
        color[node] = 1
        stack.append(node)
        for dep in waits.get(node, ()):
            if dep not in names:
                continue
            if color.get(dep) == 1:
                path = stack[stack.index(dep):] + [dep]
                for item in path[:-1]:
                    on_cycle.setdefault(item, path)
            elif not color.get(dep):
                visit(dep)
        stack.pop()
        color[node] = 2

    for node in names:
        if not color.get(node):
            visit(node)
    return on_cycle


def build(slug, spec_text, plan_text, tasks_text):
    """Return markdown, a short chat summary, and the one-line pointer."""
    tasks = parse_tasks(tasks_text)
    steps = parse_steps(plan_text if plan_text is not None else "")
    has_plan = plan_text is not None
    questions = question_blocks.kept_open(spec_text or "")
    risks = question_blocks.risks(plan_text or "", questions) if has_plan else []
    risk_blocks = any(row["blocks_slice"] for row in risks)
    analysed = task_order.analyse(tasks)
    rows = {row["id"]: row for row in analysed["rows"]}
    by_id = {task["id"]: task for task in tasks}
    step_by_n = {step["n"]: step for step in steps}
    mentioned = {}
    for step in steps:
        for task_id in step["ids"]:
            mentioned.setdefault(task_id, step["n"])

    open_tasks = [task for task in tasks if not task["done"]]
    linked = []
    missing_step = False
    for task in open_tasks:
        owner = task["step"] if task["step"] is not None else mentioned.get(task["id"])
        task["owner"] = owner
        if owner is None:
            continue
        if owner not in step_by_n:
            missing_step = True
            task["owner"] = None
            continue
        linked.append(task)

    if not steps:
        grouping = NO_STEPS
        mode = "fallback"
    elif not linked:
        grouping = UNNAMED
        mode = "fallback"
    else:
        grouping = BY_STEP
        notes = []
        loose = [
            task for task in open_tasks
            if not task["map"] and task.get("owner") not in step_by_n
        ]
        if any(task["step"] is None for task in loose):
            notes.append(SOME)
        if missing_step:
            notes.append(MISSING_STEP)
        if notes:
            grouping = grouping + " " + " ".join(notes)
        mode = "steps"

    used_names = set()
    groups = {}
    for task in open_tasks:
        if task["map"]:
            key = ("map", task["map"])
        elif mode == "steps" and task.get("owner") in step_by_n:
            key = ("step", task["owner"])
        else:
            key = ("task", task["id"])
        groups.setdefault(key, []).append(task)

    def sort_key(item):
        key, members = item
        return (min(task["id"] for task in members), key[0], str(key[1]))

    branches = []
    for key, members in sorted(groups.items(), key=sort_key):
        members = sorted(members, key=lambda task: task["id"])
        if key[0] == "map":
            name = key[1]
            if name in used_names:
                name = _suggest(slug, name, used_names)
            else:
                used_names.add(name)
            deliver = "; ".join(clean_prose(task["title"]) or "work" for task in members)
        elif key[0] == "step":
            step = step_by_n[key[1]]
            step_tasks = [task for task in open_tasks if task.get("owner") == key[1] and not task["map"]]
            name = _suggest(slug, step["body"], used_names)
            if len(step_tasks) == len(members) and all(task in members for task in step_tasks):
                deliver = clean_prose(step["body"]) or "; ".join(clean_prose(task["title"]) for task in members)
            else:
                deliver = "; ".join(clean_prose(task["title"]) or "work" for task in members)
        else:
            name = _suggest(slug, members[0]["title"], used_names)
            deliver = clean_prose(members[0]["title"]) or "work"
        areas = set()
        for task in members:
            areas.update(task.get("areas") or ())
        branches.append({
            "key": key,
            "name": name,
            "deliver": deliver or "work",
            "tasks": members,
            "task_ids": [task["id"] for task in members],
            "areas": areas,
        })

    id_branch = {}
    for branch in branches:
        for task_id in branch["task_ids"]:
            id_branch[task_id] = branch

    names = [branch["name"] for branch in branches]
    waits = {branch["name"]: [] for branch in branches}
    unknown = {branch["name"]: False for branch in branches}
    holding = {branch["name"]: [] for branch in branches}
    task_blocked = {branch["name"]: False for branch in branches}
    for branch in branches:
        seen_q = set()
        for task in branch["tasks"]:
            questions_here = _questions_for(task["id"], questions) if has_plan or spec_text else _questions_for(task["id"], questions)
            if not has_plan:
                task_blocked[branch["name"]] = True
            elif questions_here:
                for question in questions_here:
                    marker = question["text"]
                    if marker not in seen_q:
                        seen_q.add(marker)
                        holding[branch["name"]].append(question)
            elif risk_blocks:
                task_blocked[branch["name"]] = True
            else:
                reason = (rows.get(task["id"]) or {}).get("reason") or ""
                low = reason.lower()
                if "cycle" in low or "names no task" in low:
                    task_blocked[branch["name"]] = True
                if "names no task" in low:
                    unknown[branch["name"]] = True
            for dep in task["deps"]:
                if dep not in by_id:
                    unknown[branch["name"]] = True
                    task_blocked[branch["name"]] = True
                    continue
                if by_id[dep]["done"]:
                    continue
                other = id_branch.get(dep)
                if other is None or other["name"] == branch["name"]:
                    continue
                if other["name"] not in waits[branch["name"]]:
                    waits[branch["name"]].append(other["name"])

    cycles = _branch_cycles(set(names), waits)
    for branch in branches:
        name = branch["name"]
        if not has_plan or task_blocked[name] or name in cycles:
            status = "blocked"
        elif holding[name]:
            status = "waiting on a question"
        elif waits[name]:
            status = "waits in order"
        else:
            status = "ready"
        branch["status"] = status
        branch["waits"] = waits[name]
        branch["unknown"] = unknown[name]
        branch["questions"] = holding[name]
        branch["cycle"] = name in cycles

    wave = {}
    indeg = {branch["name"]: len(branch["waits"]) for branch in branches}
    frontier = sorted(name for name, degree in indeg.items() if degree == 0)
    for name in frontier:
        wave[name] = 1
    while frontier:
        nxt = []
        for name in frontier:
            for branch in branches:
                if name in branch["waits"]:
                    indeg[branch["name"]] -= 1
                    wave[branch["name"]] = max(wave.get(branch["name"], 1), wave[name] + 1)
                    if indeg[branch["name"]] == 0:
                        nxt.append(branch["name"])
        frontier = sorted(nxt)
    for branch in branches:
        if branch["name"] in cycles or branch["name"] not in wave:
            branch["section"] = "blocked"
            branch["wave"] = None
        elif branch["status"] == "blocked":
            branch["section"] = "blocked"
            branch["wave"] = wave[branch["name"]]
        else:
            branch["section"] = "wave"
            branch["wave"] = wave[branch["name"]]

    by_name = {branch["name"]: branch for branch in branches}
    markdown = _render(slug, grouping, branches, by_name, risks, has_plan, risk_blocks)
    pointer = f"Build map: docs/specs/{slug}/build-map.md"
    summary = _summary(slug, pointer, branches)
    return {"markdown": markdown, "summary": summary, "pointer": pointer, "branches": branches, "grouping": grouping}


def _question_line(questions):
    if not questions:
        return "none"
    parts = []
    for question in questions:
        short = clean_prose(_first_sentence(question["text"])) or "open question"
        who = question.get("who") or "not named yet"
        parts.append(f"{short} — {who}")
    return "; ".join(parts)


def _waits_line(branch, by_name):
    ordered = sorted(branch["waits"], key=lambda name: (by_name[name]["tasks"][0]["id"], name))
    parts = list(ordered)
    if branch["unknown"]:
        parts.append(UNKNOWN_DEP)
    return "; ".join(parts) if parts else "none"


def parallel_phrase(members):
    """How many branches in a wave can run together. A question hold is not a start."""
    count = len(members)
    held = sum(1 for branch in members if branch["status"] == "waiting on a question")
    if held == 0 and count == 1:
        return "1 branch"
    if held == 0:
        return f"{count} branches, can run in parallel"
    noun = "branch" if count == 1 else "branches"
    return f"{count} {noun}, {count - held} can start now"


def overlap_lines(members):
    """Pairs in one wave that share a requirement or a path. A note only."""
    ordered = sorted(members, key=lambda branch: (branch["tasks"][0]["id"], branch["name"]))
    lines = []
    for index, left in enumerate(ordered):
        for right in ordered[index + 1:]:
            shared = sorted(set(left.get("areas") or ()) & set(right.get("areas") or ()))
            if not shared:
                continue
            requirements = [token for kind, token in shared if kind == "requirement"]
            paths = [token for kind, token in shared if kind == "path"]
            bits = []
            if requirements:
                bits.append("both cover " + " and ".join(requirements))
            if paths:
                bits.append("both name " + " and ".join(f"`{path}`" for path in paths))
            lines.append(f"Overlap: {left['name']} and {right['name']} " + "; ".join(bits) + ".")
    return lines


def _render(slug, grouping, branches, by_name, risks, has_plan, risk_blocks):
    lines = ["# Build map", "", grouping, ""]
    diagram = _mermaid(branches, by_name)
    lines.extend(["```mermaid", diagram, "```", ""])
    if branches:
        lines.append("An arrow means the later branch waits for the earlier one.")
        lines.append("")
    else:
        lines.append("Nothing left to build.")
        lines.append("")
    if not has_plan:
        lines.append("Held: no plan.md.")
        lines.append("")
    elif risk_blocks:
        texts = []
        for risk in risks:
            if not risk["blocks_slice"]:
                continue
            short = clean_prose(risk["text"])
            if short and short not in texts:
                texts.append(short)
        detail = "; ".join(texts) if texts else "do not implement until resolved"
        lines.append(f"Held: a plan risk blocks the whole slice ({detail}).")
        lines.append("")
    waves = {}
    blocked = []
    for branch in branches:
        if branch["section"] == "blocked":
            blocked.append(branch)
        else:
            waves.setdefault(branch["wave"], []).append(branch)
    for number in sorted(waves):
        members = sorted(waves[number], key=lambda item: item["tasks"][0]["id"])
        lines.append(f"## Wave {number}: {parallel_phrase(members)}")
        lines.append("")
        for note in overlap_lines(members):
            lines.append(note)
            lines.append("")
        for branch in members:
            lines.extend(_branch_block(branch, by_name))
    if blocked:
        lines.append("## Blocked")
        lines.append("")
        for branch in sorted(blocked, key=lambda item: item["tasks"][0]["id"]):
            lines.extend(_branch_block(branch, by_name))
    text = "\n".join(lines).rstrip() + "\n"
    return text


def _branch_block(branch, by_name):
    titles = "; ".join(clean_prose(task["title"]) or "work" for task in branch["tasks"])
    return [
        f"### {branch['name']}",
        "",
        f"- Delivers: {branch['deliver']}",
        f"- Tasks: {titles}",
        f"- Waits for: {_waits_line(branch, by_name)}",
        f"- Question: {_question_line(branch['questions'])}",
        f"- Ready now: {branch['status']}",
        "",
    ]


def _mermaid_label(name):
    return name.replace('"', "'").replace("[", "(").replace("]", ")")


def _mermaid(branches, by_name):
    if not branches:
        return "flowchart LR\n  none[\"Nothing left to build\"]"
    waves = {}
    blocked = []
    for branch in branches:
        if branch["section"] == "blocked":
            blocked.append(branch)
        else:
            waves.setdefault(branch["wave"], []).append(branch)
    lines = ["flowchart LR"]
    ids = {}
    number = 1

    def add_group(group_id, title, members):
        nonlocal number
        lines.append(f'  subgraph {group_id}["{_mermaid_label(title)}"]')
        lines.append("    direction TB")
        for branch in sorted(members, key=lambda item: item["tasks"][0]["id"]):
            node = f"b{number}"
            number += 1
            ids[branch["name"]] = node
            lines.append(f'    {node}["{_mermaid_label(branch["name"])}"]')
        lines.append("  end")

    for wave_number in sorted(waves):
        add_group(f"w{wave_number}", f"Wave {wave_number}", waves[wave_number])
    if blocked:
        add_group("blocked", "Blocked", blocked)
    seen = set()
    for branch in branches:
        for dep in branch["waits"]:
            edge = (ids.get(dep), ids.get(branch["name"]))
            if edge in seen or None in edge:
                continue
            seen.add(edge)
            lines.append(f"  {edge[0]} --> {edge[1]}")
    return "\n".join(lines)


def _short_list(items, limit=6):
    if len(items) <= limit:
        return ", ".join(items)
    extra = len(items) - limit
    return ", ".join(items[:limit]) + f", and {extra} more"


def _summary(slug, pointer, branches):
    lines = [f"Build map — {slug}", pointer]
    if not branches:
        lines.append("Nothing left to build.")
        return "\n".join(lines)
    waves = {}
    blocked = []
    for branch in branches:
        label = f"{branch['name']} ({branch['status']})"
        if branch["section"] == "blocked":
            blocked.append((branch["tasks"][0]["id"], label))
        else:
            waves.setdefault(branch["wave"], []).append((branch["tasks"][0]["id"], branch, label))
    numbers = sorted(waves)
    if blocked and 1 not in waves:
        lines.append("Wave 1: none")
    for number in numbers:
        ordered = sorted(waves[number], key=lambda item: item[0])
        members = [branch for _, branch, _ in ordered]
        labels = [label for _, _, label in ordered]
        lines.append(f"Wave {number}: {parallel_phrase(members)} — {_short_list(labels)}")
        lines.extend(overlap_lines(members))
    if blocked:
        labels = [label for _, label in sorted(blocked)]
        lines.append("Blocked: " + _short_list(labels))
    return "\n".join(lines)


def _read(path):
    file = pathlib.Path(path)
    if not file.is_file():
        return None
    return file.read_text(encoding="utf-8")


def slice_dirs(root, scope=""):
    root = pathlib.Path(root)
    if scope:
        scope_path = pathlib.Path(scope)
        if scope_path.is_dir():
            return [scope_path]
        if not scope_path.is_absolute():
            candidate = root / scope
            if candidate.is_dir():
                return [candidate]
            docs = pathlib.Path("docs/specs") / scope
            if docs.is_dir():
                return [docs]
        names = set(scope_folder_names(scope))
        found = []
        if root.is_dir():
            for child in sorted(root.iterdir()):
                if child.is_dir() and child.name in names:
                    found.append(child)
        return found
    if not root.is_dir():
        return []
    out = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name in ("_template", "retired"):
            continue
        out.append(child)
    return out


def run_dir(directory, chat=False, stdout=False):
    directory = pathlib.Path(directory)
    slug = directory.name
    tasks = _read(directory / "tasks.md")
    if tasks is None:
        return f"no tasks yet (run /crav1-plan-from-spec): {slug}", 0
    result = build(slug, _read(directory / "spec.md") or "", _read(directory / "plan.md"), tasks)
    if not stdout:
        (directory / "build-map.md").write_text(result["markdown"], encoding="utf-8")
    if stdout and not chat:
        return result["markdown"], 0
    if chat:
        return result["summary"], 0
    return result["pointer"], 0


def main(argv):
    _utf8_stdout()
    if not argv or argv[0] in ("-h", "--help"):
        sys.stdout.write(__doc__ or "")
        if not (__doc__ or "").endswith("\n"):
            sys.stdout.write("\n")
        return 0
    chat = "--chat" in argv
    stdout = "--stdout" in argv
    args = [arg for arg in argv if arg not in ("--chat", "--stdout")]
    scope = ""
    root = None
    positional = []
    i = 0
    while i < len(args):
        if args[i] == "--scope" and i + 1 < len(args):
            scope = args[i + 1]
            i += 2
            continue
        if args[i] == "--root" and i + 1 < len(args):
            root = args[i + 1]
            i += 2
            continue
        positional.append(args[i])
        i += 1
    if root is not None:
        dirs = slice_dirs(root, scope)
        if scope and not dirs:
            sys.stdout.write(f"No slice named {scope}.\n")
            return 0
    elif len(positional) == 1:
        dirs = [pathlib.Path(positional[0])]
    else:
        sys.stdout.write(__doc__ or "")
        return 2
    pieces = []
    for directory in dirs:
        text, code = run_dir(directory, chat=chat, stdout=stdout)
        if code:
            return code
        pieces.append(text.rstrip("\n"))
    sys.stdout.write("\n".join(pieces) + ("\n" if pieces else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
