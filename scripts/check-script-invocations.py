#!/usr/bin/env python3
"""Documented kit-script commands include required arguments and do not hardcode python3 alone (1.144.0).

Scans skill instructions and current docs. A command that names a skill script
must include that script's required flags. A command that starts with python3
and a .py file is python3 alone unless the nearby lines also run that same
script with python (Windows) or the command uses <interpreter>.
A documented `scripts/<name>.py` path must exist in that skill's installed
folder (1.152.0), unless the same paragraph names another skill that has
the script.

Generated reference pages, the changelog, and crav1-docs copies are not scanned.
Those pages are generated, and the changelog records what an older release said.

Usage: check-script-invocations.py [kit-dir]
Exit 1 when a problem is found. Prints one line per problem.
"""
from __future__ import annotations

import ast
import os
import re
import sys

SKIP_DIR_NAMES = {"crav1-docs", "assets", "__pycache__"}
SKIP_REL = {
    "docs/reference/skills.md",
    "docs/guild-routing.md",
    "docs/reference/workflow.md",
    "CHANGELOG.md",
}
PY3_CMD = re.compile(r"(?<![\w.-])python3\s+(?:-X\s+utf8\s+)?(?P<path>\S+?\.py)\b")
INTERPRETER = re.compile(r"(?<![\w.-])python\s+(?:-X\s+utf8\s+)?\S*")
SCRIPT_NEAR = re.compile(r"`[^`]*?([A-Za-z0-9_-]+\.py)")


def _kit(argv):
    return os.path.abspath(argv[1] if len(argv) > 1 else os.environ.get("KIT_DIR", "."))


def _scripts(kit):
    root = os.path.join(kit, ".cursor", "skills", "crav1")
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in filenames:
            if name.endswith(".py"):
                found.append(os.path.join(dirpath, name))
    return found


def _required_from_ast(path):
    """Map subcommand name (or '*') to required --flags. Hand parsers return {}."""
    try:
        with open(path, encoding="utf-8") as fh:
            source = fh.read()
        tree = ast.parse(source, filename=path)
    except SyntaxError:
        return {}
    var_sub = {}
    subs = {}
    top = []

    class Visitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            if isinstance(node.value, ast.Call) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                name = _parser_name(node.value)
                if name:
                    var_sub[node.targets[0].id] = name
                    subs.setdefault(name, [])
            self.generic_visit(node)

        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "add_argument":
                flag = _flag(node)
                if flag and _required(node):
                    owner = None
                    if isinstance(node.func.value, ast.Name):
                        owner = var_sub.get(node.func.value.id)
                    if owner:
                        subs.setdefault(owner, []).append(flag)
                    else:
                        top.append(flag)
            self.generic_visit(node)

    Visitor().visit(tree)
    if top:
        subs["*"] = top
    return subs


def _parser_name(call):
    func = call.func
    if not isinstance(func, ast.Attribute) or func.attr != "add_parser":
        return None
    if not call.args or not isinstance(call.args[0], ast.Constant):
        return None
    if isinstance(call.args[0].value, str):
        return call.args[0].value
    return None


def _flag(call):
    if not call.args or not isinstance(call.args[0], ast.Constant):
        return None
    value = call.args[0].value
    if isinstance(value, str) and value.startswith("--"):
        return value
    return None


def _required(call):
    for kw in call.keywords:
        if kw.arg == "required" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
            return True
    return False


# Flags a documented command must show even when the script also has a default.
# resolve_spec defaults --root to docs/specs (1.144.0) and the command still names it.
HAND = {
    "resolve_spec.py": {"*": ["--root"]},
    "tick_only.py": {"*": ["--root"]},
    "approval_needed.py": {
        "show": ["--root", "--person", "--source-date", "--source", "--quote", "--recorder", "--accepted"],
        "write": ["--root", "--person", "--source-date", "--source", "--quote", "--recorder", "--accepted"],
        "add-item": ["--root", "--person", "--what", "--holds"],
    },
    "question_blocks.py": {"*": []},
    "task_order.py": {"*": []},
    "sh_eol.py": {"*": []},
    "ask_order.py": {"*": []},
    "notes_index.py": {"*": []},
    "merge_safe_migrate.py": {"*": []},
    "update_kit.py": {"*": []},
    "crav1-update-kit.py": {"*": []},
    "build_map.py": {"*": []},
}

# Required flags argparse does not mark, because another mode can omit them.
EXTRA = {
    "walk_progress.py": {"readiness": ["--root"]},
}
SUBS = {}

# A --recommend command must name the spec folder. The flag's value is the task id.
SPEC_FOLDER = re.compile(r"docs/specs/|<spec-folder>|<spec-dir>|<slug>")


def catalog(kit):
    out = {}
    for path in _scripts(kit):
        name = os.path.basename(path)
        parsed = _required_from_ast(path)
        if name in HAND:
            parsed = {key: list(value) for key, value in HAND[name].items()}
        elif not parsed:
            parsed = {"*": []}
        for sub, flags in EXTRA.get(name, {}).items():
            parsed.setdefault(sub, [])
            for flag in flags:
                if flag not in parsed[sub]:
                    parsed[sub].append(flag)
        out[name] = parsed
    out["crav1-update-kit.py"] = HAND["crav1-update-kit.py"]
    return out


def _doc_files(kit):
    files = []
    skill_root = os.path.join(kit, ".cursor", "skills", "crav1")
    for dirpath, dirnames, filenames in os.walk(skill_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in filenames:
            if name.endswith(".md"):
                files.append(os.path.join(dirpath, name))
    docs = os.path.join(kit, "docs")
    for dirpath, dirnames, filenames in os.walk(docs):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in filenames:
            if name.endswith(".md"):
                files.append(os.path.join(dirpath, name))
    rule = os.path.join(kit, ".cursor", "rules", "crav1.mdc")
    if os.path.isfile(rule):
        files.append(rule)
    kept = []
    for path in files:
        rel = os.path.relpath(path, kit).replace(os.sep, "/")
        if rel in SKIP_REL or rel.startswith("docs/reference/skills/"):
            continue
        kept.append(path)
    return kept


def _paragraphs(text):
    """Yield (start_line, paragraph_text). A following bullet list stays in the paragraph."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        start = i + 1
        buf = []
        while i < len(lines) and lines[i].strip():
            buf.append(lines[i])
            i += 1
        j = i
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines) and lines[j].lstrip().startswith(("- ", "* ")):
            while j < len(lines):
                if lines[j].startswith("#"):
                    break
                if not lines[j].strip():
                    nxt = j + 1
                    while nxt < len(lines) and not lines[nxt].strip():
                        nxt += 1
                    if nxt < len(lines) and lines[nxt].lstrip().startswith(("- ", "* ")):
                        j = nxt
                        continue
                    break
                if lines[j].lstrip().startswith(("- ", "* ", "  ")):
                    buf.append(lines[j])
                    j += 1
                    continue
                break
            i = j
        yield start, "\n".join(buf)


def _is_invocation(paragraph, base):
    if base not in paragraph:
        return False
    if base == "resolve_spec.py" and (
        "scripts/resolve_spec.py" in paragraph
        or re.search(r"\b(prints|[Rr]un|Find the spec)\b", paragraph)
    ):
        return True
    if re.search(r"(?<![\w.-])(?:python3|python|py -3|<interpreter>)\s+\S*" + re.escape(base), paragraph):
        return True
    if re.search(re.escape(base) + r"\s+(?:--|[\w-])", paragraph):
        return True
    if re.search(r"\b[Rr]un\b", paragraph) and base in paragraph:
        return True
    for span in re.findall(r"`([^`]+)`", paragraph):
        tokens = span.split()
        if tokens and tokens[0] in subs_for(base) and "--" in span:
            return True
    return False


def subs_for(base):
    """Subcommand names, filled once catalog has run. Tests set KNOWN."""
    return SUBS.get(base, ())


def _subcommand(paragraph, base, subs):
    """The subcommand this paragraph actually runs, not a word that shares a name."""
    match = re.search(re.escape(base) + r"\s+([A-Za-z][\w-]*)", paragraph)
    if match and match.group(1) in subs:
        return match.group(1)
    for span in re.findall(r"`([^`]+)`", paragraph):
        tokens = span.split()
        if tokens and tokens[0] in subs and "--" in span:
            return tokens[0]
    for name in subs:
        if name == "*":
            continue
        if re.search(r"\b[Rr]un\s+`" + re.escape(name) + r"`", paragraph):
            return name
    if "*" in subs:
        return "*"
    return None


def _names_interpreter(paragraph):
    if "<interpreter>" in paragraph or "running-scripts.md" in paragraph:
        return True
    cmd = r"(?:-X\s+utf8\s+)?\S*resolve_spec\.py"
    has_python3 = re.search(r"(?<![\w.-])python3\s+" + cmd, paragraph)
    has_python = re.search(r"(?<![\w.-])python\s+" + cmd, paragraph)
    return bool(has_python3 and has_python)


def _flag_has_value(paragraph, flag):
    match = re.search(re.escape(flag) + r"(?:\s+|`)(<[^`\s>]+>|\"[^\"]+\"|'[^']+'|\S+)", paragraph)
    if not match:
        return False
    value = match.group(1).strip("`")
    return not value.startswith("--")


def _problems_in_paragraph(rel, line, paragraph, known):
    out = []
    for base, subs in known.items():
        if not _is_invocation(paragraph, base):
            continue
        sub = _subcommand(paragraph, base, subs)
        if sub is None:
            continue
        flags = list(subs.get(sub, []))
        if sub != "*" and "*" in subs:
            flags.extend(subs["*"])
        for flag in flags:
            if not _flag_has_value(paragraph, flag):
                out.append(
                    f"{rel}:{line}: {base} command is missing {flag}"
                    + (f" for {sub}" if sub != "*" else "")
                )
        if base == "build_map.py":
            for span in re.findall(r"`([^`]*)`", paragraph):
                if "build_map.py" in span and "--recommend" in span and not SPEC_FOLDER.search(span):
                    out.append(
                        f"{rel}:{line}: build_map.py --recommend is missing the spec folder (docs/specs/<slug>)"
                    )
                    break
        if base == "resolve_spec.py" and not _names_interpreter(paragraph):
            out.append(f"{rel}:{line}: resolve_spec.py command does not name <interpreter> or running-scripts.md")
    return out


def _python3_alone(rel, text):
    out = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        for match in PY3_CMD.finditer(line):
            base = os.path.basename(match.group("path").rstrip("`.),"))
            window = "\n".join(lines[max(0, i - 25): i + 26])
            alt = re.search(
                r"(?<![\w.-])python\s+(?:-X\s+utf8\s+)?\S*" + re.escape(base),
                window,
            )
            if alt:
                continue
            if "<interpreter>" in window and base in window:
                # A nearby <interpreter> command for this script covers Windows.
                if re.search(r"<interpreter>\S*.{0,80}" + re.escape(base), window) or re.search(
                    re.escape(base) + r".{0,40}<interpreter>", window
                ):
                    continue
                if f"<interpreter>" in line:
                    continue
            out.append(f"{rel}:{i + 1}: command hardcodes python3 for {base} with no Windows python command")
    return out


DOC_SCRIPT = re.compile(r"(?<!/)scripts/([A-Za-z0-9_-]+\.py)\b")
OTHER_SKILL = re.compile(r"(?:skill\s+`?|/|<skill\s+)?(crav1-[A-Za-z0-9-]+)")
EXPLICIT_SKILL_SCRIPT = re.compile(
    r"<skill\s+(crav1-[A-Za-z0-9-]+)>/scripts/([A-Za-z0-9_-]+\.py)"
)


def _skill_docs(kit):
    """SKILL.md and references in each installed skill, not generated docs."""
    skill_root = os.path.join(kit, ".cursor", "skills", "crav1")
    if not os.path.isdir(skill_root):
        return []
    found = []
    for name in sorted(os.listdir(skill_root)):
        if name in SKIP_DIR_NAMES or name == "crav1-docs":
            continue
        skill_dir = os.path.join(skill_root, name)
        if not os.path.isdir(skill_dir):
            continue
        skill_md = os.path.join(skill_dir, "SKILL.md")
        files = []
        if os.path.isfile(skill_md):
            files.append(skill_md)
        ref = os.path.join(skill_dir, "references")
        if os.path.isdir(ref):
            for dirpath, dirnames, filenames in os.walk(ref):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
                for fname in filenames:
                    if fname.endswith(".md"):
                        files.append(os.path.join(dirpath, fname))
        found.append((name, skill_dir, files))
    return found


def _named_skills(paragraph):
    names = []
    for match in OTHER_SKILL.finditer(paragraph):
        token = match.group(1) or match.group(2)
        if token and token not in names:
            names.append(token)
    return names


def _missing_script_paths(kit):
    """Documented scripts/<name>.py must exist in that skill's folder."""
    skill_root = os.path.join(kit, ".cursor", "skills", "crav1")
    out = []
    for skill, skill_dir, files in _skill_docs(kit):
        for path in files:
            rel = os.path.relpath(path, kit).replace(os.sep, "/")
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            for line, paragraph in _paragraphs(text):
                if "Generated by" in paragraph:
                    continue
                explicit = {name for _skill, name in EXPLICIT_SKILL_SCRIPT.findall(paragraph)}
                others = _named_skills(paragraph)
                for name in dict.fromkeys(DOC_SCRIPT.findall(paragraph)):
                    if name in explicit:
                        continue
                    local = os.path.join(skill_dir, "scripts", name)
                    if os.path.isfile(local):
                        continue
                    # Kit-repo wrappers such as scripts/build-walk.py live at the repo root.
                    if "-" in name and os.path.isfile(os.path.join(kit, "scripts", name)):
                        continue
                    elsewhere = False
                    for other in others:
                        other_path = os.path.join(skill_root, other, "scripts", name)
                        if os.path.isfile(other_path):
                            elsewhere = True
                            break
                    if elsewhere:
                        continue
                    out.append(
                        f"{rel}:{line}: documented scripts/{name} is missing from {skill}/scripts"
                    )
    return out


def problems(kit):
    known = catalog(kit)
    SUBS.clear()
    for base, subs in known.items():
        SUBS[base] = tuple(name for name in subs if name != "*")
    out = []
    for path in _doc_files(kit):
        rel = os.path.relpath(path, kit).replace(os.sep, "/")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        out.extend(_python3_alone(rel, text))
        for line, paragraph in _paragraphs(text):
            if "Generated by" in paragraph:
                continue
            out.extend(_problems_in_paragraph(rel, line, paragraph, known))
    out.extend(_missing_script_paths(kit))
    return out


def main(argv):
    kit = _kit(argv)
    found = problems(kit)
    for item in found:
        print("FAIL  " + item)
    print(f"script invocations: {len(found)} problem(s)")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
