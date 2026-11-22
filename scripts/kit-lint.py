#!/usr/bin/env python3
"""Kit lint (no model, seconds). Usage: kit-lint.py [kit-dir]
- every relative Markdown link in a skill (SKILL.md and references/) points at a file that exists
- each SKILL.md has front matter with name == its folder and a description that says when to use it
- docs/reference/skills.yaml lists exactly the skill folders, each with a numeric prompt_budget
- the .cursor, .claude and plugin copies of each skill have the same files
- a Python entry point that imports a local helper sets sys.dont_write_bytecode = True
  after import sys and before that import (1.121.1)
- every SKILL.md points at crav1-docs/reference/run-ending.md, unless the skill is in RUN_ENDING_EXEMPT (1.122.0)
- no skill file has a Next: instruction that names more than one step to run now (1.122.0)
- no question card offers an Edits option, a Change some option, an Other name option, or an option that says to type under Other (1.130.0)
- a documented kit-script command includes the script's required arguments and does not hardcode python3 alone (1.144.0)
"""
import ast, glob, os, re, subprocess, sys
sys.dont_write_bytecode = True

# Calls that load a .py file. Bytecode is written when that file is executed.
LOADERS = {"spec_from_file_location", "spec_from_loader", "SourceFileLoader", "SourcelessFileLoader", "exec_module"}
DYNAMIC = {"import_module", "__import__"}


def _call_name(node):
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _local_import_lines(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    tree = ast.parse(text, filename=path)
    folder = os.path.dirname(path)
    siblings = set()
    for name in os.listdir(folder):
        if name == os.path.basename(path):
            continue
        if name.endswith(".py"):
            siblings.add(name[:-3])
        elif os.path.isfile(os.path.join(folder, name, "__init__.py")):
            siblings.add(name)
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in siblings:
                    lines.append(node.lineno)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                lines.append(node.lineno)
            elif node.module and node.module.split(".")[0] in siblings:
                lines.append(node.lineno)
        elif isinstance(node, ast.Call):
            name = _call_name(node)
            if name in LOADERS:
                lines.append(node.lineno)
            elif name in DYNAMIC and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                if node.args[0].value.split(".")[0] in siblings:
                    lines.append(node.lineno)
    return tree, lines


def _sys_import_line(tree):
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "sys" and (alias.asname or "sys") == "sys":
                    lines.append(node.lineno)
    return min(lines) if lines else None


def _flag_line(tree):
    lines = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Attribute) or target.attr != "dont_write_bytecode":
            continue
        if not isinstance(target.value, ast.Name) or target.value.id != "sys":
            continue
        if isinstance(node.value, ast.Constant) and node.value.value is True:
            lines.append(node.lineno)
    return min(lines) if lines else None


def bytecode_problem(path):
    """None when this script does not import a local module, or sets the flag in time."""
    try:
        tree, lines = _local_import_lines(path)
    except SyntaxError as exc:
        return f"cannot parse ({exc})"
    if not lines:
        return None
    first = min(lines)
    flag = _flag_line(tree)
    sys_line = _sys_import_line(tree)
    if flag is None or sys_line is None or not (sys_line < flag < first):
        return (
            f"imports a local module at line {first} without "
            "sys.dont_write_bytecode = True after import sys and before that import"
        )
    return None


def py_entry_points(kit):
    """Skill scripts in every install tree, plus kit scripts/*.py (not tests)."""
    roots = [
        os.path.join(kit, ".cursor", "skills", "crav1"),
        os.path.join(kit, ".claude", "skills"),
        os.path.join(kit, "plugins", "crav1", "skills"),
    ]
    found = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ("crav1-docs", "__pycache__")]
            for name in filenames:
                if name.endswith(".py"):
                    found.append(os.path.join(dirpath, name))
    scripts = os.path.join(kit, "scripts")
    if os.path.isdir(scripts):
        for name in sorted(os.listdir(scripts)):
            if name.endswith(".py"):
                found.append(os.path.join(scripts, name))
    return found


# Skills that do not point at the shared run-ending rule. Empty on purpose.
# Add a folder name here only with the reason in the same comment.
RUN_ENDING_EXEMPT = set()
RUN_ENDING_REF = "run-ending.md"
CMD = re.compile(r"/crav1-[a-z0-9-]+")


def _indent(line):
    return len(line) - len(line.lstrip(" "))


def _next_spans(text):
    """Each Next: instruction, plus lines indented under it.

    A deeper bullet is part of that instruction (a Next: heading with several
    steps). A sibling line is the next instruction or ordinary text.
    """
    lines = text.splitlines()
    spans = []
    i = 0
    while i < len(lines):
        if "Next:" in lines[i]:
            base = _indent(lines[i])
            start = lines[i].index("Next:")
            block = [lines[i][start:]]
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                stripped = nxt.strip()
                if stripped == "" or stripped.startswith("#"):
                    break
                if stripped.startswith(("Waiting:", "Uncommitted:", "Source:", "Ready:")):
                    break
                if _indent(nxt) <= base:
                    break
                block.append(nxt)
                j += 1
            spans.append((i + 1, "\n".join(block)))
            i = j
        else:
            i += 1
    return spans


def next_step_problems(path, text):
    """A Next: instruction that names more than one distinct kit command.

    Since 1.143.0 a ready Next line may also name /crav1-build-tasks in the
    sentence "builds one task without the walk". That names the alternative,
    not a second step. See docs/reference/run-ending.md.
    """
    out = []
    for lineno, block in _next_spans(text):
        cmds = list(dict.fromkeys(CMD.findall(block)))
        if "builds one task without the walk" in block and "/crav1-build-walk" in cmds:
            cmds = [cmd for cmd in cmds if cmd != "/crav1-build-tasks"]
        if len(cmds) > 1:
            out.append(
                f"{path}:{lineno}: Next: names {len(cmds)} steps ({', '.join(cmds)}); "
                "one Next line names one step"
            )
    return out


def run_ending_problems(kit):
    """Every SKILL.md cites the shared rule, and no skill file lists two steps as Next."""
    root = os.path.join(kit, ".cursor", "skills", "crav1")
    out = []
    if not os.path.isdir(root):
        return [f"{root}: missing"]
    for name in sorted(os.listdir(root)):
        skill = os.path.join(root, name)
        skill_md = os.path.join(skill, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue
        if name in RUN_ENDING_EXEMPT:
            continue
        with open(skill_md, encoding="utf-8") as fh:
            text = fh.read()
        if RUN_ENDING_REF not in text:
            out.append(f"{name}: SKILL.md does not reference {RUN_ENDING_REF} (or add it to RUN_ENDING_EXEMPT with a reason)")
        for dirpath, dirnames, filenames in os.walk(skill):
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            for fn in filenames:
                if not fn.endswith(".md"):
                    continue
                path = os.path.join(dirpath, fn)
                with open(path, encoding="utf-8") as fh:
                    body = fh.read()
                rel = os.path.relpath(path, kit)
                out.extend(next_step_problems(rel, body))
    return out


# A question-card option that only tells the user to type somewhere else (1.130.0).
# "There is no Edits option" and "Do not add an Edits option" are the rule, not an offer.
DEAD_REPLY = re.compile(r"(?i)reply with (?:your )?edits")
DEAD_CHOOSE = re.compile(r"(?i)choose this, then type")
DEAD_UNDER = re.compile(r"(?i)type(?: your [\w' -]{0,48}| [\w' -]{1,24})? under other")
DEAD_EDITS = re.compile(
    r"(?i)(?:^|\s)(?:[-*]|\d+\.)\s+(?:\*\*)?`?Edits`?\b|\*\*Edits\*\*|offer(?:s|ed)?\s+(?:an\s+)?`?Edits`?\b"
)
DEAD_EDITS_OK = re.compile(r"(?i)(?:there is )?no `?Edits`?|do not add an? `?Edits`?")
DEAD_CHANGE_SOME = re.compile(r"(?m)^\s*\d+\.\s+\*\*Change some")
DEAD_OTHER_NAME = re.compile(r"\*\*Other name\*\*")
# A choice word the card tells the user to type (none, skip, all) instead of offering it (1.130.0).
DEAD_TYPED = re.compile(r"(?i)\btype\s+(?:none|skip|all)\b")
DEAD_TYPED_OK = re.compile(r"(?i)\b(?:do not|never|not)\b")


def dead_card_hits(text):
    """Lines that tell an agent to offer a dead Edits / type-under-Other option."""
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if DEAD_REPLY.search(line):
            hits.append((i, "reply with edits"))
        if DEAD_CHOOSE.search(line):
            hits.append((i, "choose this, then type"))
        if DEAD_UNDER.search(line):
            hits.append((i, "type under Other"))
        if DEAD_EDITS.search(line) and not DEAD_EDITS_OK.search(line):
            hits.append((i, "Edits option"))
        if DEAD_CHANGE_SOME.search(line):
            hits.append((i, "Change some option"))
        if DEAD_OTHER_NAME.search(line):
            hits.append((i, "Other name option"))
        if DEAD_TYPED.search(line) and not DEAD_TYPED_OK.search(line):
            hits.append((i, "typed choice"))
    return hits


def _card_sources(kit):
    roots = [
        os.path.join(kit, ".cursor", "skills", "crav1"),
        os.path.join(kit, ".cursor", "rules"),
        os.path.join(kit, "docs"),
    ]
    found = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ("crav1-docs", "__pycache__")]
            for name in filenames:
                if not name.endswith(".md"):
                    continue
                if name == "CHANGELOG.md":
                    continue
                found.append(os.path.join(dirpath, name))
    rule = os.path.join(kit, ".cursor", "rules", "crav1.mdc")
    if os.path.isfile(rule):
        found.append(rule)
    return found


def dead_card_problems(kit):
    out = []
    for path in sorted(set(_card_sources(kit))):
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for lineno, why in dead_card_hits(text):
            out.append(f"{os.path.relpath(path, kit)}:{lineno}: question card offers a dead option ({why})")
    return out


# A ready-check ending has one Run next block at the top and no Next: line of
# its own (1.153.0). A skill file must not tell the agent to write a Next line
# after the Waiting or Held lines, or give a `Next: /crav1-build-walk` example
# for that ending (1.154.0).
STRAY_NEXT_AFTER = re.compile(
    r"(?i)\bNext:?\s+lines?\b[^.\n]{0,80}?\b(?:stays?|follows?|comes?|goes|is printed|are printed)\b"
    r"[^.\n]{0,40}?\bafter\b[^.\n]{0,40}?\b(?:Waiting|Held)\b"
)
STRAY_NEXT_WALK = re.compile(r"Next:\s*/crav1-build-walk\b")
STRAY_NEXT_OK = re.compile(r"(?i)\b(?:never|do not|don't|no)\b[^.\n]{0,40}Next")


# The ready-check skills, whose ending is the readiness script's Run next block.
READY_CHECK_SKILLS = ("crav1-tighten-and-plan-ready-to-build", "crav1-tasks-ready-to-build")


def stray_next_hits(text, ready_check=True):
    """Lines that tell the agent to write a Next line after Waiting (1.154.0)."""
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if STRAY_NEXT_AFTER.search(line) and not STRAY_NEXT_OK.search(line):
            hits.append((i, "a Next line after the Waiting lines"))
        elif ready_check and STRAY_NEXT_WALK.search(line):
            hits.append((i, "a `Next: /crav1-build-walk` example"))
    return hits


def stray_next_problems(kit):
    root = os.path.join(kit, ".cursor", "skills", "crav1")
    out = []
    if not os.path.isdir(root):
        return out
    for name in sorted(os.listdir(root)):
        if name == "crav1-docs":
            continue
        skill = os.path.join(root, name)
        paths = [os.path.join(skill, "SKILL.md")]
        paths += glob.glob(os.path.join(skill, "references", "**", "*.md"), recursive=True)
        for path in paths:
            if not os.path.isfile(path):
                continue
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            # Since 1.157.0 no skill shows a `Next: /crav1-build-walk` example:
            # every walk ending, and a resume of one, is a Run next entry.
            for lineno, why in stray_next_hits(text, True):
                out.append(
                    f"{os.path.relpath(path, kit)}:{lineno}: tells the agent to write {why}; "
                    "the ending has one Run next block and no Next: line (1.153.0)"
                )
    return out


# Skills whose every ending is Run next or nothing (1.173.0). No line in
# their SKILL.md, references, or branches starts with `Next:` or shows a
# `Next: ...` example in a code span.
RUN_NEXT_ONLY_SKILLS = (
    "crav1-finalize-commit",
    # 1.176.0: the plan steps end with Run next too.
    "crav1-plan-from-spec",
    "crav1-tighten-plan",
    "crav1-review-plan",
    # 1.177.0: the four PR skills end with Run next too.
    "crav1-open-pr",
    "crav1-pr-status",
    "crav1-review-pr",
    "crav1-merge-pr",
    # 1.193.0: add-to-spec and the sweep end with Run next too.
    "crav1-add-to-spec",
    "crav1-update-specs-from-changes-and-prs",
)
NEXT_EXAMPLE = re.compile(r"`Next:\s*[^`]")


def run_next_only_hits(text):
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("Next:") or NEXT_EXAMPLE.search(line):
            hits.append(i)
    return hits


def run_next_only_problems(kit):
    root = os.path.join(kit, ".cursor", "skills", "crav1")
    out = []
    for name in RUN_NEXT_ONLY_SKILLS:
        skill = os.path.join(root, name)
        if not os.path.isdir(skill):
            continue
        for path in sorted(glob.glob(os.path.join(skill, "**", "*.md"), recursive=True)):
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            for lineno in run_next_only_hits(text):
                out.append(
                    f"{os.path.relpath(path, kit)}:{lineno}: a `Next:` line in a skill that ends with "
                    "Run next or nothing (1.173.0)"
                )
    return out


# Prose that tells a skill to print a Next: line (1.177.0). Script output is
# checked by the ending layout below; this catches reference prose such as
# "ends with one `Next:` line" or "print a Next: line" in a skill that ends
# with Run next, in the shared PR steps, and in the PR skills' scripts.
PROSE_NEXT = re.compile(
    r"(?i)\b(?:one|a|print|prints|printing|write|writes|ends?\s+with|then)\s+`?Next:?`?\s+lines?\b"
)
PROSE_NEXT_OK = re.compile(r"(?i)\b(?:never|no|not|nor|without)\b[^.\n]{0,40}$")
SCRIPT_NEXT = re.compile(r"""["'](?:[^"'\n]*\n)?Next:""")
PR_SKILLS = ("crav1-open-pr", "crav1-pr-status", "crav1-review-pr", "crav1-merge-pr")


def prose_next_hits(text):
    """Line numbers where prose tells the agent to print a Next: line."""
    hits = []
    for i, line in enumerate(str(text or "").splitlines(), 1):
        for m in PROSE_NEXT.finditer(line):
            if not PROSE_NEXT_OK.search(line[: m.start()]):
                hits.append(i)
                break
    return hits


def prose_next_problems(kit):
    root = os.path.join(kit, ".cursor", "skills", "crav1")
    out = []
    paths = [os.path.join(kit, "docs", "reference", "pr-common.md")]
    for name in RUN_NEXT_ONLY_SKILLS:
        paths += sorted(glob.glob(os.path.join(root, name, "**", "*.md"), recursive=True))
    for path in paths:
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for lineno in prose_next_hits(text):
            out.append(f"{os.path.relpath(path, kit)}:{lineno}: tells the skill to print a `Next:` line; "
                       "this skill ends with Run next, the label above the command (1.177.0)")
    for name in PR_SKILLS:
        for path in sorted(glob.glob(os.path.join(root, name, "scripts", "*.py"))):
            with open(path, encoding="utf-8") as fh:
                for lineno, line in enumerate(fh, 1):
                    if SCRIPT_NEXT.search(line):
                        out.append(f"{os.path.relpath(path, kit)}:{lineno}: prints a `Next:` line; "
                                   "the PR skills end with Run next (1.177.0)")
    return out


# No `Next:` anywhere (1.193.0). Every skill file and every skill script is
# checked: a line that starts with `Next:`, a `Next: ...` example in a code
# span, or a script string that prints `Next:`. Files not moved to Run next
# yet are listed in scripts/next-line-baseline.tsv with their count; a file
# not listed, or a count above its baseline, fails. A count below the
# baseline fails too, so the baseline only shrinks.
NEXT_BASELINE = os.path.join("scripts", "next-line-baseline.tsv")
# A script line that only detects or strips a `Next:` line prints nothing.
NEXT_CHECK_OK = re.compile(r"""startswith\(\s*["']Next:|len\(\s*["']Next:|re\.(?:search|match)\(""")


def next_line_counts(kit):
    root = os.path.join(kit, ".cursor", "skills", "crav1")
    counts = {}
    if not os.path.isdir(root):
        return counts
    for name in sorted(os.listdir(root)):
        if name == "crav1-docs":
            continue
        skill = os.path.join(root, name)
        for path in sorted(glob.glob(os.path.join(skill, "**", "*"), recursive=True)):
            if not os.path.isfile(path) or "__pycache__" in path:
                continue
            rel = os.path.relpath(path, kit).replace(os.sep, "/")
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            if path.endswith(".md"):
                n = len(run_next_only_hits(text))
            elif path.endswith(".py"):
                n = sum(1 for line in text.splitlines() if SCRIPT_NEXT.search(line) and not NEXT_CHECK_OK.search(line))
            else:
                continue
            if n:
                counts[rel] = n
    return counts


def read_next_baseline(kit):
    path = os.path.join(kit, NEXT_BASELINE)
    base = {}
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if not line.strip() or line.startswith("#"):
                    continue
                rel, _, n = line.rstrip("\n").partition("\t")
                base[rel] = int(n)
    return base


def next_anywhere_problems(kit):
    counts = next_line_counts(kit)
    base = read_next_baseline(kit)
    out = []
    for rel, n in sorted(counts.items()):
        allowed = base.get(rel, 0)
        if n > allowed:
            out.append(f"{rel}: {n} `Next:` line(s), baseline {allowed}; end with Run next, the label above the command alone in its code span (1.193.0)")
    for rel, allowed in sorted(base.items()):
        n = counts.get(rel, 0)
        if n < allowed:
            out.append(f"{NEXT_BASELINE}: {rel} has {n} `Next:` line(s) now, below its baseline {allowed}; lower the baseline (1.193.0)")
    return out


# Ending layout (1.176.0). The ending scripts are run on sample states and
# every printed ending is checked: no line starts with `Next:`, and no
# lowercase line sits right under a command that is alone in its code span
# (the label goes above the command).
LONE_COMMAND = re.compile(r"^`[^`]+`$")


def layout_hits(text):
    """(line number, why) for a Next: line or a lowercase line under a command."""
    hits = []
    lines = str(text or "").splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("Next:"):
            hits.append((i, "a Next: line"))
        if LONE_COMMAND.match(stripped) and i < len(lines):
            below = lines[i].strip()
            if below and below[0].islower():
                hits.append((i + 1, "a lowercase line under a command"))
    return hits


def _load_script(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def ending_samples(kit):
    """(where, text) for the endings the walk scripts print on sample states."""
    sk = os.path.join(kit, ".cursor", "skills", "crav1")
    out = []
    we = _load_script(os.path.join(sk, "crav1-tasks-ready-to-build", "scripts", "walk_ending.py"), "kit_lint_walk_ending")
    out.append(("walk_ending.run_entry", we.run_entry(["T3 Record the decision"], "feat/orders-api", slug="orders-api")))
    out.append(("walk_ending.branch_entry", we.branch_entry(["T3 Record the decision", "T5 Store the card"], "feat/orders-api", slug="orders-api")))
    for counts, first in (({}, False), ({"needs_verify": 1}, False), ({"blocked": 2}, True)):
        out.append(("walk_ending.not_ready_next", we.not_ready_next("orders-api", counts, first) or ""))
    out.append(("walk_ending.catch_up_block", we.catch_up_block("orders-api", ["T4"], [], 2, uncommitted=["plan.md"])))
    bw = _load_script(os.path.join(sk, "crav1-build-walk", "scripts", "build_walk.py"), "kit_lint_build_walk")
    task = [{"id": 3, "title": "Record the decision"}]
    for phase in ("build", "verify", "commit", "open-pr", "next-task", "done-all"):
        state = {"slug": "orders-api", "phase": phase, "branch": "feat/orders-api", "tasks": task, "spec_count": 2,
                 "ready_branches": [], "next_tasks": task, "next_branch": "feat/orders-api"}
        out.append((f"build_walk.next_for {phase}", bw.next_for(state)["ending"]))
    br = _load_script(os.path.join(sk, "crav1-build-walk", "scripts", "branch_run.py"), "kit_lint_branch_run")
    for stop, pr in (("merge", None), ("merge", 82), ({"kind": "question", "line": "T10 waits on an answer"}, 82)):
        state = {"slug": "orders-api", "branch": "feat/orders-cicd", "pr": pr, "stop": stop, "base": "develop"}
        out.append(("branch_run.ending", br.ending(state)["ending"]))
    pc = _load_script(os.path.join(sk, "crav1-plan-from-spec", "scripts", "plan_check.py"), "kit_lint_plan_check")
    for items, named in (([{"id": "P1", "issue": "x", "tag": "spec", "status": "open"}], True), ([], True), ([], False)):
        out.append(("plan_check.empty_queue_next", pc.empty_queue_next(items, named, False, "orders-api")))
    da = _load_script(os.path.join(sk, "crav1-design-architecture", "scripts", "design_run.py"), "kit_lint_design_run")
    for state in ({"phase": "design", "parked": True, "uncommitted": 4}, {"phase": "go-ahead", "uncommitted": 7},
                  {"phase": "merged", "slices": ["orders-api"]}, {"phase": "merged", "no_slice": True}):
        out.append((f"design_run.ending {state['phase']}", da.ending(dict(state, topic="orders-payment-retry"))))
    et = _load_script(os.path.join(sk, "crav1-explain-tech", "scripts", "explain_tech.py"), "kit_lint_explain_tech")
    for kw in ({}, {"deeper": True, "spec": "orders-api"}, {"not_in_spec": True}, {"saved": "docs/specs/orders-api/notes.md"}):
        out.append((f"explain_tech.ending {sorted(kw)}", et.ending("Service Bus", **kw)))
    return out


def ending_layout_problems(kit):
    out = []
    try:
        samples = ending_samples(kit)
    except Exception as exc:  # noqa: BLE001 - report, do not crash the lint
        return [f"ending layout: could not run the ending scripts ({exc})"]
    for where, text in samples:
        for lineno, why in layout_hits(text):
            out.append(f"{where}: line {lineno} is {why}; put the label above the command (1.176.0)")
    return out


# Card wording (1.164.0). A card in a skill file is written as a block:
#   Card: <short plain question>
#   - **<label> (Recommended)** (`word`): <what happens>. Why: <reason>
#   - **<label>** (`word`): <what happens>
# Only `Card:` lines and the option lines right under them are read, so prose
# is never checked. Since 1.200.0 the check runs on every skill. The rule is
# docs/reference/question-cards.md.
def _card_lint_skills():
    root = os.path.join(os.path.dirname(__file__), "..", ".cursor", "skills", "crav1")
    if not os.path.isdir(root):
        return ()
    return tuple(sorted(
        name for name in os.listdir(root)
        if name.startswith("crav1-") and name != "crav1-docs" and os.path.isdir(os.path.join(root, name))
    ))


CARD_LINT_SKILLS = _card_lint_skills()
# Kit terms that never belong in a card's question or options.
CARD_JARGON = (
    "needs_yes",
    "needs-yes",
    "other-owner mode",
    "step name",
    "map mark",
    "progress file",
    "Owner: other",
    "Owner: self",
    "headless",
)
CARD_LINE = re.compile(r"^\s*(?:[-*]\s+)?Card:\s*(.*)$")
CARD_OPTION = re.compile(r"^\s*(?:\d+\.|[-*])\s+(.*)$")
CARD_BRACKETS = re.compile(r"[()\[\]{}<>]")
CARD_WORD = re.compile(r"^\s*\(`[^`\n]+`\)")
# An option list written inline in prose instead of a Card block.
# An option that corrects itself mid-sentence (1.190.0): "... no: on ...", "... I mean ...".
SELF_CORRECTION = re.compile(r"(?i)(?:\bno:\s|\bI mean\b|\bactually\b|\bor rather\b|\bwait,)")
INLINE_CARD = re.compile(
    r"(?i)(?:\bcard is|\boptions?:?|\boffer)\s+`[^`\n]+`\s*\(Recommended\)\s*(?:,|\bor\b|/)"
    r"|\*\*[^*\n]+\(Recommended\)\*\*\s*/\s*\*\*"
)


def _jargon(text):
    low = text.lower()
    return [word for word in CARD_JARGON if word.lower() in low]


def card_option_parts(line):
    """(label, description) of one option line, or None when it is not one."""
    match = CARD_OPTION.match(line)
    if not match:
        return None
    rest = match.group(1).strip()
    bold = re.match(r"^\*\*(.+?)\*\*(.*)$", rest)
    if bold:
        label, tail = bold.group(1), bold.group(2)
        tail = CARD_WORD.sub("", tail)
        return label.strip().rstrip(".:"), tail.strip().lstrip(":.—-").strip()
    plain = re.sub(r"`[^`\n]*`", lambda m: "x" * len(m.group(0)), rest)
    cut = plain.find(": ")
    if cut < 0:
        return rest, ""
    return rest[:cut].strip(), rest[cut + 2:].strip()


def card_hits(question, options):
    """Problems with one card: its question and its (label, description) options."""
    hits = []
    if CARD_BRACKETS.search(question):
        hits.append("the question has brackets")
    for word in _jargon(question):
        hits.append(f"the question uses the kit term `{word}`")
    if question.count("?") > 1:
        hits.append("two questions on one card; ask one question per card (1.190.0)")
    if not options:
        hits.append("the card has no options")
    for index, (label, text) in enumerate(options):
        if len(re.findall(r"[A-Za-z0-9]+", text)) < 3:
            hits.append(f"option `{label}` does not say what happens")
        for word in _jargon(label + " " + text):
            hits.append(f"option `{label}` uses the kit term `{word}`")
        if SELF_CORRECTION.search(label + " " + text):
            hits.append(f"option `{label}` corrects itself mid-sentence; write the option once, as meant (1.190.0)")
        if index and "(Recommended)" in label:
            hits.append(f"option `{label}` is Recommended but not first")
    return hits


def card_blocks(text):
    """(line number, question, options) for each Card block outside code fences."""
    blocks, fence, lines = [], False, text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("```"):
            fence = not fence
        match = None if fence else CARD_LINE.match(line)
        if match:
            options, j = [], i + 1
            indent = _indent(lines[j]) if j < len(lines) else 0
            while j < len(lines) and card_option_parts(lines[j]) is not None and _indent(lines[j]) == indent:
                options.append(card_option_parts(lines[j]))
                j += 1
            blocks.append((i + 1, match.group(1).strip(), options))
            i = j
            continue
        i += 1
    return blocks


def card_text_hits(text):
    """Card problems in one skill file: every Card block, plus inline option lists."""
    hits = []
    for lineno, question, options in card_blocks(text):
        hits.extend((lineno, why) for why in card_hits(question, options))
    for i, line in enumerate(text.splitlines(), 1):
        if INLINE_CARD.search(line):
            hits.append((i, "options listed inline; write a Card block"))
    return hits


def card_wording_problems(kit, skills=CARD_LINT_SKILLS):
    root = os.path.join(kit, ".cursor", "skills", "crav1")
    out = []
    for name in skills:
        skill = os.path.join(root, name)
        paths = [os.path.join(skill, "SKILL.md")]
        paths += glob.glob(os.path.join(skill, "references", "**", "*.md"), recursive=True)
        paths += glob.glob(os.path.join(skill, "branches", "**", "*.md"), recursive=True)
        for path in sorted(paths):
            if not os.path.isfile(path):
                continue
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            for lineno, why in card_text_hits(text):
                out.append(f"{os.path.relpath(path, kit)}:{lineno}: card wording: {why} (docs/reference/question-cards.md)")
    return out


DESIGN_CARD_SKILL = "crav1-design-architecture"
TYPE_ONLY = re.compile(r"(?i)^(keep talking|add my idea|change it|type\b.*|other\b.*|something else)$")


def design_card_hits(text):
    """1.189.0: a design card has at most 4 options, one question, and no option that only says to type."""
    hits = []
    for lineno, question, options in card_blocks(text):
        if len(options) > 4:
            hits.append((lineno, f"{len(options)} options; a card holds at most 4, typed input goes through Other"))
        if question.count("?") > 1:
            hits.append((lineno, "more than one question on one card"))
        for label, desc in options:
            if TYPE_ONLY.match(label.replace(" (Recommended)", "").strip()) or re.match(r"(?i)^type\b", desc):
                hits.append((lineno, f"option `{label}` only says to type; typed input goes through the Other field"))
    return hits


def explain_tech_problems(kit):
    """1.192.0: the /crav1-explain-tech sample answers keep the fixed shape and word counts."""
    skill = os.path.join(kit, ".cursor", "skills", "crav1", "crav1-explain-tech")
    et = _load_script(os.path.join(skill, "scripts", "explain_tech.py"), "kit_lint_explain_tech_check")
    out = []
    for name, deeper in (("sample-short.md", False), ("sample-not-in-spec.md", False), ("sample-deeper.md", True)):
        path = os.path.join(skill, "assets", name)
        if not os.path.isfile(path):
            out.append(f"{os.path.relpath(path, kit)}: missing sample answer")
            continue
        with open(path, encoding="utf-8") as fh:
            res = et.check(fh.read(), deeper)
        out += [f"{os.path.relpath(path, kit)}: explain-tech answer: {p}" for p in res["problems"]]
    return out


def design_card_problems(kit):
    skill = os.path.join(kit, ".cursor", "skills", "crav1", DESIGN_CARD_SKILL)
    paths = [os.path.join(skill, "SKILL.md")]
    for sub in ("references", "assets"):
        paths += glob.glob(os.path.join(skill, sub, "**", "*.md"), recursive=True)
    out = []
    for path in sorted(paths):
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for lineno, why in design_card_hits(text):
            out.append(f"{os.path.relpath(path, kit)}:{lineno}: design card: {why} (docs/reference/question-cards.md)")
    return out


def bytecode_problems(kit):
    out = []
    for path in sorted(py_entry_points(kit)):
        problem = bytecode_problem(path)
        if problem:
            out.append(f"{os.path.relpath(path, kit)}: {problem}")
    return out


def invocation_problems(kit):
    """Documented script commands (1.144.0). See scripts/check-script-invocations.py."""
    path = os.path.join(kit, "scripts", "check-script-invocations.py")
    proc = subprocess.run([sys.executable, path, kit], capture_output=True, text=True)
    lines = [line[6:] for line in (proc.stdout or "").splitlines() if line.startswith("FAIL  ")]
    if proc.returncode and not lines:
        detail = (proc.stderr or proc.stdout or "script invocation check failed").strip()
        lines.append(detail)
    return lines


def maintainer_tool_problems(kit):
    """1.199.0: the maintainer-only kit_dry_run tester is never named where users or skills read it.

    Skills, their copies, plugin files, docs/ (skills.yaml included) and the
    README stay silent about it; CONTRIBUTING.md and the repo's top-level
    scripts/ are the only places it lives. The CHANGELOG is bundled into
    crav1-docs, so it describes the tester without its file name.
    """
    out = []
    word = "kit_dry_run"
    roots = [os.path.join(kit, part) for part in (".cursor", ".claude", "plugins", "docs")]
    singles = [os.path.join(kit, name) for name in ("README.md", "CHANGELOG.md", "SUPPORT.md")]
    paths = list(singles)
    for root in roots:
        for folder, _dirs, names in os.walk(root):
            if "__pycache__" in folder:
                continue
            paths += [os.path.join(folder, name) for name in names]
    for path in paths:
        if not os.path.isfile(path) or path.endswith((".pyc", ".png", ".jpg", ".gif", ".pptx")):
            continue
        try:
            text = open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
        if word in text:
            out.append(f"{os.path.relpath(path, kit)}: names the maintainer-only kit_dry_run tester; keep it to CONTRIBUTING.md and scripts/")
    return out


def main(argv):
    kit = os.path.abspath(argv[1] if len(argv) > 1 else os.environ.get("KIT_DIR", "."))
    errs = []
    SK = os.path.join(kit, ".cursor", "skills", "crav1")
    skills = sorted(d for d in os.listdir(SK) if os.path.exists(os.path.join(SK, d, "SKILL.md")))
    for s in skills:
        root = os.path.join(SK, s)
        text = open(os.path.join(root, "SKILL.md"), encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m: errs.append(f"{s}: SKILL.md has no front matter"); continue
        fm = m.group(1)
        name = re.search(r"^name:\s*(\S+)", fm, re.M)
        if not name or name.group(1).strip("'\"") != s: errs.append(f"{s}: front matter name is {name.group(1) if name else 'missing'}, not the folder name")
        desc = re.search(r"^description:[ \t]*(.*(?:\n[ \t]+.*)*)", fm, re.M)
        if not desc or len(desc.group(1).strip()) < 40: errs.append(f"{s}: description missing or under 40 characters")
        elif not re.search(r"\b(use|when|after|before)\b", desc.group(1), re.I): print(f"WARN  {s}: description does not say when to use it")
        for md in [os.path.join(root, "SKILL.md")] + glob.glob(os.path.join(root, "references", "**", "*.md"), recursive=True):
            body = re.sub(r"```.*?```", "", open(md, encoding="utf-8").read(), flags=re.S)
            body = re.sub(r"`[^`\n]*`", "", body)
            for tgt in re.findall(r"\]\(([^)\s]+)\)", body):
                if re.match(r"^(https?:|mailto:|#|<|\{)", tgt) or "<" in tgt: continue
                p = os.path.normpath(os.path.join(os.path.dirname(md), tgt.split("#")[0]))
                if not os.path.exists(p) and not os.path.exists(os.path.join(root, tgt.split("#")[0])): errs.append(f"{os.path.relpath(md, kit)}: broken link {tgt}")
    y = os.path.join(kit, "docs", "reference", "skills.yaml")
    if os.path.exists(y):
        names, cur, budgets = [], None, {}
        for line in open(y, encoding="utf-8"):
            m = re.match(r"^- name: (\S+)", line)
            if m: cur = m.group(1); names.append(cur); continue
            m = re.match(r"^  prompt_budget: (\S+)", line)
            if m and cur: budgets[cur] = m.group(1)
        for n in sorted(set(skills) - set(names)): errs.append(f"skills.yaml: no entry for skill {n}")
        agents = {os.path.basename(a)[:-3] for a in glob.glob(os.path.join(kit, ".cursor", "agents", "**", "*.md"), recursive=True)}
        for n in sorted(set(names) - set(skills) - agents): errs.append(f"skills.yaml: entry {n} has no skill folder")
        for n in names:
            if n in budgets and not budgets[n].isdigit(): errs.append(f"skills.yaml: {n} prompt_budget is not a number ({budgets[n]})")
    else: errs.append("docs/reference/skills.yaml missing")
    def files(r): return sorted(os.path.relpath(os.path.join(a, f), r) for a, _, fs in os.walk(r) for f in fs if "__pycache__" not in a)
    for other in (os.path.join(kit, ".claude", "skills", "crav1"), os.path.join(kit, "plugins", "crav1", "skills")):
        if not os.path.isdir(other): continue
        for s in skills:
            if not os.path.isdir(os.path.join(other, s)): errs.append(f"{os.path.relpath(other, kit)}: no copy of {s}"); continue
            a, b = set(files(os.path.join(SK, s))), set(files(os.path.join(other, s)))
            if a != b: errs.append(f"{os.path.relpath(other, kit)}/{s}: files differ ({', '.join(sorted(a ^ b)[:3])})")
    errs.extend(bytecode_problems(kit))
    errs.extend(run_ending_problems(kit))
    errs.extend(dead_card_problems(kit))
    errs.extend(stray_next_problems(kit))
    errs.extend(run_next_only_problems(kit))
    errs.extend(prose_next_problems(kit))
    errs.extend(next_anywhere_problems(kit))
    errs.extend(ending_layout_problems(kit))
    errs.extend(card_wording_problems(kit))
    errs.extend(design_card_problems(kit))
    errs.extend(explain_tech_problems(kit))
    errs.extend(invocation_problems(kit))
    errs.extend(maintainer_tool_problems(kit))
    for e in errs: print("FAIL  " + e)
    print(f"kit lint: {len(skills)} skills, {len(errs)} problem(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
