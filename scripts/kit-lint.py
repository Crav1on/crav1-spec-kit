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
"""
import ast, os, re, sys, glob

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
    """A Next: instruction that names more than one distinct kit command."""
    out = []
    for lineno, block in _next_spans(text):
        cmds = list(dict.fromkeys(CMD.findall(block)))
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
DEAD_UNDER = re.compile(r"(?i)type(?: your [\w' -]{0,48})? under other")
DEAD_EDITS = re.compile(
    r"(?i)(?:^|\s)(?:[-*]|\d+\.)\s+(?:\*\*)?`?Edits`?\b|\*\*Edits\*\*|offer(?:s|ed)?\s+(?:an\s+)?`?Edits`?\b"
)
DEAD_EDITS_OK = re.compile(r"(?i)(?:there is )?no `?Edits`?|do not add an? `?Edits`?")
DEAD_CHANGE_SOME = re.compile(r"(?m)^\s*\d+\.\s+\*\*Change some")
DEAD_OTHER_NAME = re.compile(r"\*\*Other name\*\*")


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


def bytecode_problems(kit):
    out = []
    for path in sorted(py_entry_points(kit)):
        problem = bytecode_problem(path)
        if problem:
            out.append(f"{os.path.relpath(path, kit)}: {problem}")
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
    for e in errs: print("FAIL  " + e)
    print(f"kit lint: {len(skills)} skills, {len(errs)} problem(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
