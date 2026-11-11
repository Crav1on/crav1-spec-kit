#!/usr/bin/env python3
"""Overlay a published CRAV1 kit release onto a consumer project.

The same file is the release asset ``crav1-update-kit.py``. It detects the
installed version, refuses anything that is not a published ``vX.Y.Z`` tag,
three-way merges kit-owned files, and leaves project files alone.

It does not switch branches. It does not commit or write unless ``--yes`` is
passed. It has no way to publish a push.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


_utf8_stdout()

KIT_REPO = "https://github.com/Crav1on/crav1-spec-kit.git"
RELEASE_TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
VERSION_NUM = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
KIT_VERSION_LINE = re.compile(r"^Kit version:\s*v?(\d+\.\d+\.\d+)\s*$", re.M)
CHANGELOG_HEAD = re.compile(r"^##\s+v?(\d+\.\d+\.\d+)\b", re.M)
SHA = re.compile(r"^[0-9a-f]{7,40}$", re.I)
PR_WORD = re.compile(
    r"^(?:pr\s*#?|#|pull\s*request\s+|pull/?request\s*#?)(\d+)$", re.I
)
BRANCH_WORD = re.compile(r"^(?:main|master|develop|trunk|head)$", re.I)
BANNED_GIT = {"push", "rebase", "reset", "checkout", "switch", "clean", "stash"}

CURSOR_DROPIN_MARKER = ".cursor/skills/crav1/crav1-docs/reference/workflow.md"
CLAUDE_DROPIN_MARKER = ".claude/skills/crav1-docs/reference/workflow.md"
CLAUDE_USER_MARKER = ".claude/skills/crav1-docs/reference/workflow.md"
TEMPLATE_ROOTS = ("docs/specs/_template/", "docs/system/_template/")


class Refuse(SystemExit):
    def __init__(self, message: str):
        self.message = message
        super().__init__(2)


def refuse(message: str) -> None:
    print(message, file=sys.stderr)
    raise Refuse(message)


def version_key(value: str) -> tuple[int, int, int]:
    match = VERSION_NUM.fullmatch(value.strip())
    if not match:
        refuse(f"Refused: {value} is not a published release tag.")
    return tuple(int(part) for part in match.groups())


def tagify(value: str) -> str:
    text = value.strip()
    if text.startswith("v"):
        return text
    return "v" + text


def commit_message(old: str, new: str) -> str:
    return f"Update CRAV1 kit {tagify(old)} to {tagify(new)}"


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    if args and args[0] == "push":
        refuse("Refused: this script does not push.")
    if args and args[0] in {"checkout", "switch"}:
        refuse("Refused: this script does not switch branches.")
    if args and args[0] == "rebase":
        refuse("Refused: this script does not rebase.")
    if args and args[0] in BANNED_GIT:
        refuse("Refused: this script does not change branches or history.")
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=check,
        capture_output=True,
        text=True,
    )


def published_tags(text: str) -> list[str]:
    found: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" in line:
            line = line.split("\t", 1)[1].strip()
        if line.startswith("refs/tags/"):
            line = line[len("refs/tags/") :]
        if line.endswith("^{}"):
            line = line[:-3]
        if RELEASE_TAG.fullmatch(line):
            found.append(line)
    return sorted(set(found), key=version_key)


def normalize_request(text: str | None) -> str | None:
    """Return a tag request, or None when the caller wants the latest tag."""
    if text is None:
        return None
    cleaned = text.strip()
    if not cleaned or cleaned.lower() in {"latest", "to latest"}:
        return None
    cleaned = re.sub(r"^to\s+", "", cleaned, flags=re.I).strip()
    if cleaned.lower().startswith("refs/tags/"):
        cleaned = cleaned[len("refs/tags/") :]
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", cleaned)
    if match:
        return f"v{match.group(1)}.{match.group(2)}.{match.group(3)}"
    return cleaned


def refusal_reason(request: str) -> str:
    if BRANCH_WORD.fullmatch(request):
        return f"Refused: {request} is not a published release tag."
    if PR_WORD.fullmatch(request) or re.fullmatch(r"\d+", request):
        return "Refused: an open pull request is not a published release tag."
    if SHA.fullmatch(request):
        return "Refused: a commit is not a published release tag."
    if "/" in request or request.startswith("origin"):
        return f"Refused: {request} is a branch, not a published release tag."
    return f"Refused: {request} is not a published release tag."


def resolve_target(request: str | None, tags: list[str]) -> dict:
    if not tags:
        refuse("Refused: no published vX.Y.Z release tag was found.")
    if request is None:
        tag = tags[-1]
        return {"tag": tag, "latest": True, "version": tag[1:]}
    if not RELEASE_TAG.fullmatch(request):
        refuse(refusal_reason(request))
    if request not in tags:
        refuse(f"Refused: {request} is not a published release tag.")
    return {"tag": request, "latest": request == tags[-1], "version": request[1:]}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return ""


def version_in_workflow(path: Path) -> str | None:
    match = KIT_VERSION_LINE.search(_read_text(path))
    return match.group(1) if match else None


def version_in_changelog(path: Path) -> str | None:
    match = CHANGELOG_HEAD.search(_read_text(path))
    return match.group(1) if match else None


def version_in_plugin(path: Path) -> str | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    version = data.get("version")
    if isinstance(version, str) and VERSION_NUM.fullmatch(version):
        return version[1:] if version.startswith("v") else version
    return None


def _marker_version(workflow: Path) -> tuple[str | None, str | None]:
    version = version_in_workflow(workflow)
    if version:
        return version, "workflow.md"
    changelog = workflow.parents[1] / "CHANGELOG.md"
    # reference/workflow.md -> crav1-docs/CHANGELOG.md (parents: reference, crav1-docs)
    if workflow.parent.name == "reference":
        changelog = workflow.parent.parent / "CHANGELOG.md"
    version = version_in_changelog(changelog)
    if version:
        return version, "CHANGELOG.md"
    return None, None


def _plugin_installs(home: Path) -> list[dict]:
    base = home / ".cursor" / "plugins"
    if not base.is_dir():
        return []
    found = []
    for path in sorted(base.rglob("plugin.json")):
        if path.parent.name != ".cursor-plugin" or path.parent.parent.name != "crav1":
            continue
        version = version_in_plugin(path)
        if not version:
            continue
        found.append(
            {
                "kind": "cursor-plugin",
                "version": version,
                "version_from": "plugin.json",
                "path": str(path),
            }
        )
    return found


def detect(root: Path, home: Path | None = None) -> dict:
    root = root.resolve()
    home = (home or Path.home()).resolve()
    installs: list[dict] = []
    kit_repo = (root / ".cursor/rules/kit-maintainer.mdc").is_file() and (
        root / "plugins/crav1/.cursor-plugin/plugin.json"
    ).is_file()
    if kit_repo:
        plugin = root / "plugins/crav1/.cursor-plugin/plugin.json"
        version = version_in_plugin(plugin)
        installs.append(
            {
                "kind": "kit-repo",
                "version": version,
                "version_from": "plugin.json",
                "path": str(plugin),
            }
        )
    for kind, rel in (
        ("cursor-drop-in", CURSOR_DROPIN_MARKER),
        ("claude-drop-in", CLAUDE_DROPIN_MARKER),
    ):
        marker = root / rel
        if not marker.is_file():
            continue
        version, source = _marker_version(marker)
        installs.append(
            {
                "kind": kind,
                "version": version,
                "version_from": source,
                "path": rel,
            }
        )
    installs.extend(_plugin_installs(home))
    user_marker = home / CLAUDE_USER_MARKER
    if user_marker.is_file():
        version, source = _marker_version(user_marker)
        installs.append(
            {
                "kind": "claude-user",
                "version": version,
                "version_from": source,
                "path": str(user_marker),
            }
        )
    dropins = [item for item in installs if item["kind"] in {"cursor-drop-in", "claude-drop-in"}]
    plugins = [item for item in installs if item["kind"] in {"cursor-plugin", "claude-user"}]
    if kit_repo:
        mode = "kit-repo"
    elif dropins:
        mode = "drop-in"
    elif plugins:
        mode = "plugin"
    else:
        mode = "none"
    primary = None
    if dropins:
        primary = next((item for item in dropins if item["kind"] == "cursor-drop-in"), dropins[0])
    elif plugins:
        primary = plugins[0]
    elif installs:
        primary = installs[0]
    branch = current_branch(root)
    dirty = dirty_paths(root)
    return {
        "mode": mode,
        "installs": installs,
        "version": None if primary is None else primary.get("version"),
        "version_from": None if primary is None else primary.get("version_from"),
        "branch": branch,
        "dirty": dirty,
        "heads_up": heads_up(branch, dirty),
        "writes_kit_files": mode == "drop-in",
    }


def current_branch(root: Path) -> str | None:
    if not (root / ".git").exists():
        return None
    result = git(root, "rev-parse", "--abbrev-ref", "HEAD", check=False)
    if result.returncode != 0:
        return None
    name = result.stdout.strip()
    if not name or name == "HEAD":
        return None
    return name


def dirty_paths(root: Path) -> list[str]:
    if not (root / ".git").exists():
        return []
    result = git(root, "status", "--porcelain", check=False)
    if result.returncode != 0:
        return []
    paths = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        paths.append(path)
    return paths


def is_template(path: str) -> bool:
    return path.startswith(TEMPLATE_ROOTS)


def is_cursor_kit(path: str) -> bool:
    if path.startswith(".cursor/skills/crav1/"):
        return True
    if path.startswith(".cursor/agents/crav1-") and path.endswith(".md") and path.count("/") == 2:
        return True
    if path == ".cursor/agent-assets/README.md" or path.startswith(".cursor/agent-assets/crav1-"):
        return True
    return path == ".cursor/rules/crav1.mdc"


def is_claude_kit(path: str) -> bool:
    if path.startswith(".claude/skills/"):
        top = path[len(".claude/skills/") :].split("/", 1)[0]
        if top == "crav1-docs" or top.startswith("crav1-"):
            return True
    if path.startswith(".claude/agents/crav1-") and path.endswith(".md") and path.count("/") == 2:
        return True
    if path == ".claude/agent-assets/README.md" or path.startswith(".claude/agent-assets/crav1-"):
        return True
    return path == ".claude/CLAUDE.md"


def is_kit_path(path: str) -> bool:
    return is_cursor_kit(path) or is_claude_kit(path)


def is_managed(path: str) -> bool:
    return is_kit_path(path) or is_template(path)


def heads_up(branch: str | None, dirty: list[str]) -> dict:
    kit = [path for path in dirty if is_kit_path(path)]
    project = [path for path in dirty if not is_kit_path(path)]
    shown = branch or "(detached or not a git checkout)"
    return {
        "branch": branch,
        "text": (
            f"You are on {shown}. Only this branch gets the new kit. "
            "Other branches stay on the old kit until you merge this branch into them. "
            "Say merge develop into the branch. Never rebase. "
            "If this branch should not get the new kit, merge first or switch branch, then run the command again."
        ),
        "uncommitted_kit": kit,
        "uncommitted_project": project,
    }


def _safe(root: Path, rel: str) -> Path:
    if rel.startswith("/") or ".." in Path(rel).parts:
        refuse(f"Refused: {rel} is a project file.")
    path = (root / rel).resolve()
    root_resolved = root.resolve()
    if path != root_resolved and root_resolved not in path.parents:
        refuse(f"Refused: {rel} is a project file.")
    return path


def _read_tree(folder: Path, prefix: str, out: dict[str, bytes]) -> None:
    if not folder.is_dir():
        return
    for path in folder.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        rel = f"{prefix}/{path.relative_to(folder).as_posix()}"
        out[rel] = path.read_bytes()


def _read_named(folder: Path, prefix: str, pattern: str, out: dict[str, bytes]) -> None:
    if not folder.is_dir():
        return
    for path in folder.glob(pattern):
        if path.is_file() and not path.is_symlink():
            out[f"{prefix}/{path.name}"] = path.read_bytes()


def _read_assets(folder: Path, prefix: str, out: dict[str, bytes]) -> None:
    if not folder.is_dir():
        return
    readme = folder / "README.md"
    if readme.is_file() and not readme.is_symlink():
        out[f"{prefix}/README.md"] = readme.read_bytes()
    for child in folder.iterdir():
        if child.is_dir() and child.name.startswith("crav1-") and not child.is_symlink():
            _read_tree(child, f"{prefix}/{child.name}", out)


def collect_kit(root: Path, hosts: set[str]) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    if "cursor" in hosts:
        _read_tree(root / ".cursor/skills/crav1", ".cursor/skills/crav1", out)
        _read_named(root / ".cursor/agents", ".cursor/agents", "crav1-*.md", out)
        _read_assets(root / ".cursor/agent-assets", ".cursor/agent-assets", out)
        rule = root / ".cursor/rules/crav1.mdc"
        if rule.is_file() and not rule.is_symlink():
            out[".cursor/rules/crav1.mdc"] = rule.read_bytes()
    if "claude" in hosts:
        skills = root / ".claude/skills"
        if skills.is_dir():
            for child in skills.iterdir():
                if child.is_dir() and (child.name == "crav1-docs" or child.name.startswith("crav1-")):
                    _read_tree(child, f".claude/skills/{child.name}", out)
        _read_named(root / ".claude/agents", ".claude/agents", "crav1-*.md", out)
        _read_assets(root / ".claude/agent-assets", ".claude/agent-assets", out)
        claude = root / ".claude/CLAUDE.md"
        if claude.is_file() and not claude.is_symlink():
            out[".claude/CLAUDE.md"] = claude.read_bytes()
    return out


def collect_templates(root: Path) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    for prefix in TEMPLATE_ROOTS:
        folder = root / prefix
        if folder.is_dir():
            _read_tree(folder, prefix[:-1], out)
    return out


def _preview(data: bytes | None) -> str:
    if data is None:
        return ""
    if b"\0" in data:
        return f"<binary {len(data)} bytes>"
    try:
        return data.decode("utf-8")
    except UnicodeError:
        return f"<binary {len(data)} bytes>"


def _binary(data: bytes | None) -> bool:
    return data is not None and (b"\0" in data or _preview(data).startswith("<binary "))


def _newline_style(data: bytes | None) -> str | None:
    """lf, crlf, mixed, or None when the bytes have no newline. Binary is None."""
    if data is None or _binary(data):
        return None
    crlf = data.count(b"\r\n")
    bare_lf = data.count(b"\n") - crlf
    bare_cr = data.count(b"\r") - crlf
    if crlf and not bare_lf and not bare_cr:
        return "crlf"
    if bare_lf and not crlf and not bare_cr:
        return "lf"
    if crlf or bare_lf or bare_cr:
        return "mixed"
    return None


def _normalize_newlines(data: bytes | None) -> bytes | None:
    """CRLF and LF compare equal. Binary bytes stay as they are."""
    if data is None or _binary(data):
        return data
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _restyle(data: bytes | None, style: str) -> bytes | None:
    """Write text with lf or crlf. Binary bytes stay as they are."""
    if data is None or _binary(data) or style not in {"lf", "crlf"}:
        return data
    text = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    if style == "crlf":
        return text.replace(b"\n", b"\r\n")
    return text


def _attr_match(pattern: str, rel: str) -> bool:
    rel = rel.replace("\\", "/")
    if pattern.startswith("/"):
        pattern = pattern[1:]
    if pattern == "*":
        return True
    if pattern.startswith("*."):
        return rel.endswith(pattern[1:])
    return rel == pattern or rel.endswith("/" + pattern)


def gitattributes_eol(root: Path, rel: str) -> str | None:
    """eol from the repo's .gitattributes, last matching pattern wins."""
    path = root / ".gitattributes"
    if not path.is_file():
        return None
    chosen = None
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeError:
        return None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2 or not _attr_match(parts[0], rel):
            continue
        eol = None
        for attr in parts[1:]:
            if attr in {"eol=lf", "eol=crlf"}:
                eol = attr.split("=", 1)[1]
            if attr in {"binary", "-text"}:
                eol = None
        if eol:
            chosen = eol
    return chosen


def preferred_newline(root: Path, rel: str, local: bytes | None) -> str:
    """The file's own endings, else .gitattributes eol, else LF."""
    style = _newline_style(local)
    if style in {"lf", "crlf"}:
        return style
    attr = gitattributes_eol(root, rel)
    if attr in {"lf", "crlf"}:
        return attr
    return "lf"


def _lines(text: str) -> list[str]:
    if text == "":
        return []
    return text.splitlines(keepends=True)


def _regions(base: list[str], other: list[str]) -> list[tuple[int, int, list[str]]]:
    regions = []
    matcher = difflib.SequenceMatcher(a=base, b=other)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        # A same-length replace is one region per changed line, so a clash on
        # one line does not swallow the neighbouring lines.
        if tag == "replace" and (i2 - i1) == (j2 - j1):
            for offset in range(i2 - i1):
                if base[i1 + offset] != other[j1 + offset]:
                    regions.append((i1 + offset, i1 + offset + 1, [other[j1 + offset]]))
            continue
        regions.append((i1, i2, other[j1:j2]))
    return regions


def _overlaps(start: int, end: int, i1: int, i2: int) -> bool:
    if i1 < end and i2 > start:
        return True
    if i1 == i2 and (i1 == start or i1 == end):
        return True
    if start == end and i1 <= start <= i2:
        return True
    return False


def _apply_regions(base: list[str], regions: list[tuple[int, int, list[str]]], start: int, end: int) -> list[str]:
    out: list[str] = []
    cursor = start
    for i1, i2, repl in sorted(regions, key=lambda item: (item[0], item[1])):
        if i2 < start or i1 > end:
            continue
        take_from = max(i1, start)
        if take_from > cursor:
            out.extend(base[cursor:take_from])
        out.extend(repl)
        cursor = max(cursor, i2)
    if cursor < end:
        out.extend(base[cursor:end])
    return out


def merge_text(old: str, local: str, new: str) -> dict:
    """Three-way line merge. Non-overlapping edits combine. A clash reports both sides."""
    if local == new:
        return {"status": "unchanged", "text": local}
    if local == old:
        return {"status": "take-new", "text": new}
    if new == old:
        return {"status": "keep-local", "text": local}
    base = _lines(old)
    left = _regions(base, _lines(local))
    right = _regions(base, _lines(new))
    items = [("L", i1, i2, repl) for i1, i2, repl in left] + [
        ("N", i1, i2, repl) for i1, i2, repl in right
    ]
    items.sort(key=lambda item: (item[1], item[2], item[0]))
    groups: list[dict] = []
    for side, i1, i2, repl in items:
        if groups and _overlaps(groups[-1]["start"], groups[-1]["end"], i1, i2):
            group = groups[-1]
            group["start"] = min(group["start"], i1)
            group["end"] = max(group["end"], i2)
            group["regs"].append((side, i1, i2, repl))
        else:
            groups.append({"start": i1, "end": i2, "regs": [(side, i1, i2, repl)]})
    keep_lines: list[str] = []
    take_lines: list[str] = []
    clashes = []
    cursor = 0
    for group in groups:
        prefix = base[cursor : group["start"]]
        keep_lines.extend(prefix)
        take_lines.extend(prefix)
        left_regs = [(i1, i2, repl) for side, i1, i2, repl in group["regs"] if side == "L"]
        right_regs = [(i1, i2, repl) for side, i1, i2, repl in group["regs"] if side == "N"]
        if left_regs and right_regs:
            local_lines = _apply_regions(base, left_regs, group["start"], group["end"])
            kit_lines = _apply_regions(base, right_regs, group["start"], group["end"])
            if local_lines == kit_lines:
                keep_lines.extend(local_lines)
                take_lines.extend(local_lines)
            else:
                clashes.append({"local": "".join(local_lines), "kit": "".join(kit_lines)})
                keep_lines.extend(local_lines)
                take_lines.extend(kit_lines)
        elif left_regs:
            applied = _apply_regions(base, left_regs, group["start"], group["end"])
            keep_lines.extend(applied)
            take_lines.extend(applied)
        else:
            applied = _apply_regions(base, right_regs, group["start"], group["end"])
            keep_lines.extend(applied)
            take_lines.extend(applied)
        cursor = group["end"]
    tail = base[cursor:]
    keep_lines.extend(tail)
    take_lines.extend(tail)
    if clashes:
        return {
            "status": "clash",
            "hunks": clashes,
            "keep_text": "".join(keep_lines),
            "take_text": "".join(take_lines),
        }
    return {"status": "merged", "text": "".join(keep_lines)}


def classify_file(old: bytes | None, local: bytes | None, new: bytes | None, style: str = "lf") -> dict:
    """Three-way classify. CRLF and LF are the same text (1.132.0).

    A local file that matches the old release apart from line endings is a
    plain update. Written text uses `style`, which is the file's own endings.
    """
    old_n = _normalize_newlines(old)
    local_n = _normalize_newlines(local)
    new_n = _normalize_newlines(new)

    def styled(data: bytes | None) -> bytes | None:
        return _restyle(data, style)

    if local_n == old_n == new_n:
        return {"op": "unchanged"}
    if local_n == old_n:
        if new is None:
            return {"op": "delete"} if old is not None else {"op": "unchanged"}
        if old is None:
            return {"op": "add", "data": styled(new_n)}
        return {"op": "write", "data": styled(new_n), "why": "matches-old"}
    if new_n == old_n or local_n == new_n:
        return {"op": "unchanged"} if local_n == new_n else {"op": "leave", "why": "no-upstream-change"}
    if new is None:
        return {
            "op": "clash",
            "hunks": [{"local": _preview(local_n), "kit": ""}],
            "keep_data": styled(local_n),
            "take_data": None,
        }
    if local is None:
        return {
            "op": "clash",
            "hunks": [{"local": "", "kit": _preview(new_n)}],
            "keep_data": None,
            "take_data": styled(new_n),
        }
    if _binary(old) or _binary(local) or _binary(new):
        return {
            "op": "clash",
            "hunks": [{"local": _preview(local), "kit": _preview(new)}],
            "keep_data": local,
            "take_data": new,
        }
    merged = merge_text(old_n.decode("utf-8"), local_n.decode("utf-8"), new_n.decode("utf-8"))
    if merged["status"] == "clash":
        return {
            "op": "clash",
            "hunks": merged["hunks"],
            "keep_data": styled(merged["keep_text"].encode("utf-8")),
            "take_data": styled(merged["take_text"].encode("utf-8")),
        }
    return {"op": "write", "data": styled(merged["text"].encode("utf-8")), "why": merged["status"]}


def classify_template(old: bytes | None, local: bytes | None, new: bytes | None, style: str = "lf") -> dict:
    if local is None:
        return {"op": "absent"}
    old_n = _normalize_newlines(old)
    local_n = _normalize_newlines(local)
    new_n = _normalize_newlines(new)
    if old is not None and local_n == old_n:
        if new is None:
            return {"op": "delete"}
        if new_n == local_n:
            return {"op": "unchanged"}
        return {"op": "write", "data": _restyle(new_n, style)}
    reason = "edited" if old is not None else "not-in-old-kit"
    return {"op": "leave", "reason": reason}


def hosts_from_detect(info: dict) -> set[str]:
    hosts = set()
    for item in info.get("installs") or []:
        if item["kind"] == "cursor-drop-in":
            hosts.add("cursor")
        elif item["kind"] == "claude-drop-in":
            hosts.add("claude")
    return hosts


def plugin_advice(info: dict, target: str | None) -> str:
    installed = info.get("version") or "unknown"
    kinds = ", ".join(item["kind"] for item in info["installs"] if item["kind"] in {"cursor-plugin", "claude-user"})
    if target and info.get("version"):
        if version_key(target) > version_key(info["version"]):
            lead = f"Installed {kinds} is v{installed}. Latest published release is v{target}."
        elif version_key(target) == version_key(info["version"]):
            lead = f"Installed {kinds} is already v{installed}, the latest published release."
        else:
            lead = f"Installed {kinds} is v{installed}, which is newer than v{target}."
    else:
        lead = f"Installed {kinds} is v{installed}."
    lines = [
        lead,
        "A plugin install is not updated by a commit in this repo.",
        "Team marketplace: use Auto Refresh or Dashboard Refresh, then update or reinstall the plugin if Cursor asks. Reload the window. A running Cloud Agent keeps the plugin it started with; start a new agent.",
        "Local plugin: copy plugins/crav1 from that release into ~/.cursor/plugins/local/crav1 and reload. This command does not copy it.",
    ]
    if any(item["kind"] == "claude-user" for item in info["installs"]):
        lines.append(
            "User-scope Claude Code: copy the release .claude tree into ~/.claude. This command does not copy it and does not commit."
        )
    return " ".join(lines)


def build_actions(root: Path, old_root: Path, new_root: Path, hosts: set[str]) -> dict:
    old_files = collect_kit(old_root, hosts)
    new_files = collect_kit(new_root, hosts)
    local_files = collect_kit(root, hosts)
    paths = sorted(set(old_files) | set(new_files) | set(local_files))
    files = {
        "update": [],
        "add": [],
        "merge": [],
        "delete": [],
        "clash": [],
        "unchanged": [],
        "left_extra": [],
    }
    payloads: dict[str, bytes | None] = {}
    for path in paths:
        if not is_kit_path(path):
            continue
        style = preferred_newline(root, path, local_files.get(path))
        action = classify_file(old_files.get(path), local_files.get(path), new_files.get(path), style)
        op = action["op"]
        if op == "write":
            bucket = "merge" if action.get("why") == "merged" else "update"
            files[bucket].append(path)
            payloads[path] = action["data"]
        elif op == "add":
            files["add"].append(path)
            payloads[path] = action["data"]
        elif op == "delete":
            files["delete"].append(path)
            payloads[path] = None
        elif op == "clash":
            files["clash"].append({"path": path, "hunks": action["hunks"]})
            payloads[path] = {"keep": action.get("keep_data"), "take": action.get("take_data")}
        elif op == "leave" and path not in old_files and path not in new_files:
            files["left_extra"].append(path)
        elif op == "leave":
            files["unchanged"].append(path)
        else:
            files["unchanged"].append(path)
    old_templates = collect_templates(old_root)
    new_templates = collect_templates(new_root)
    local_templates = collect_templates(root)
    templates = {"update": [], "delete": [], "left": []}
    template_payloads: dict[str, bytes | None] = {}
    for path in sorted(set(local_templates) | set(old_templates) | set(new_templates)):
        style = preferred_newline(root, path, local_templates.get(path))
        action = classify_template(old_templates.get(path), local_templates.get(path), new_templates.get(path), style)
        if action["op"] == "write":
            templates["update"].append(path)
            template_payloads[path] = action["data"]
        elif action["op"] == "delete":
            templates["delete"].append(path)
            template_payloads[path] = None
        elif action["op"] == "leave":
            templates["left"].append({"path": path, "reason": action["reason"]})
    return {
        "files": files,
        "templates": templates,
        "payloads": payloads,
        "template_payloads": template_payloads,
    }


def plan_view(info: dict, actions: dict, target: str | None) -> dict:
    files = actions["files"]
    return {
        "mode": info["mode"],
        "installed": info.get("version"),
        "version_from": info.get("version_from"),
        "target": None if target is None else target.lstrip("v"),
        "branch": info.get("branch"),
        "heads_up": info.get("heads_up"),
        "writes_kit_files": info.get("writes_kit_files", False),
        "files": files,
        "templates": actions["templates"],
        "project_untouched": True,
        "advice": None,
    }


def load_migrations(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("migrations") or []
    if not isinstance(items, list):
        refuse("Refused: the migration registry is not a list.")
    return items


def migration_registry(root: Path, explicit: Path | None) -> Path | None:
    if explicit:
        return explicit
    here = Path(__file__).resolve().parent
    for candidate in (here / "migrations.json", here.parent / "migrations.json"):
        if candidate.is_file():
            return candidate
    for rel in (
        ".cursor/skills/crav1/crav1-update-kit/migrations.json",
        ".claude/skills/crav1-update-kit/migrations.json",
    ):
        candidate = root / rel
        if candidate.is_file():
            return candidate
    return None


def select_migrations(items: list[dict], installed: str | None, target: str | None) -> list[dict]:
    if not installed or not target:
        return []
    old_key = version_key(installed)
    new_key = version_key(target)
    chosen = []
    for item in items:
        if old_key < version_key(str(item["below"])) and new_key >= version_key(str(item["at_least"])):
            chosen.append(item)
    return chosen


def find_migration_script(root: Path, rel: str) -> Path | None:
    for base in (root / ".cursor/skills/crav1", root / ".claude/skills"):
        candidate = base / rel
        if candidate.is_file():
            return candidate
    return None


def run_migrations(root: Path, installed: str | None, target: str | None, registry: Path | None, apply: bool, yes: bool) -> dict:
    if apply and not yes:
        refuse("Refused: applying a migration needs a yes in this run.")
    if registry is None or not registry.is_file():
        return {"migrations": [], "note": "No migration registry in this install."}
    chosen = select_migrations(load_migrations(registry), installed, target)
    results = []
    for item in chosen:
        script = find_migration_script(root, item["script"])
        entry = {
            "id": item["id"],
            "summary": item.get("summary", ""),
            "script": item["script"],
            "found": script is not None,
            "blocked": False,
            "applied": False,
            "output": "",
        }
        if script is None:
            entry["output"] = "The migration script is not in this tree yet. Replace kit files first."
            entry["blocked"] = True
            results.append(entry)
            continue
        dry = subprocess.run(
            [sys.executable, str(script), "--root", str(root), "--dry-run"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        output = (dry.stdout or "") + (dry.stderr or "")
        entry["output"] = output
        if "walk-progress.md" in output:
            entry["blocked"] = True
            entry["output"] += "\nRefused: a migration that mentions walk-progress.md is not applied."
        if dry.returncode != 0:
            entry["blocked"] = True
        if apply and not entry["blocked"]:
            written = subprocess.run(
                [sys.executable, str(script), "--root", str(root)],
                cwd=root,
                capture_output=True,
                text=True,
            )
            entry["output"] += written.stdout or ""
            entry["applied"] = written.returncode == 0
            if written.returncode != 0:
                entry["output"] += written.stderr or ""
                entry["blocked"] = True
        results.append(entry)
    return {"migrations": results, "installed": installed, "target": target}


def _write(root: Path, rel: str, data: bytes | None) -> None:
    if not is_managed(rel):
        refuse(f"Refused: {rel} is a project file.")
    path = _safe(root, rel)
    if data is None:
        if path.is_file():
            path.unlink()
        parent = path.parent
        root_resolved = root.resolve()
        while parent != root_resolved and parent.is_dir() and not any(parent.iterdir()):
            parent.rmdir()
            parent = parent.parent
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def apply_overlay(root: Path, old_root: Path, new_root: Path, hosts: set[str], yes: bool, keep: set[str], take: set[str]) -> dict:
    if not yes:
        refuse("Refused: writing kit files needs a yes in this run.")
    if keep & take:
        refuse("Refused: a clash cannot be both kept and taken.")
    actions = build_actions(root, old_root, new_root, hosts)
    clash_paths = {item["path"] for item in actions["files"]["clash"]}
    missing = clash_paths - keep - take
    if missing:
        listed = ", ".join(sorted(missing))
        refuse(f"Refused: a clash needs keep or take before writing: {listed}")
    unknown = (keep | take) - clash_paths
    if unknown:
        listed = ", ".join(sorted(unknown))
        refuse(f"Refused: {listed} is not a clash.")
    touched = []
    for path, data in list(actions["payloads"].items()):
        if path in clash_paths:
            continue
        if path in actions["files"]["unchanged"] or path in actions["files"]["left_extra"]:
            continue
        _write(root, path, data)
        touched.append(path)
    for path in sorted(keep | take):
        choice = actions["payloads"][path]
        picked = choice["keep"] if path in keep else choice["take"]
        _write(root, path, picked)
        touched.append(path)
    for path, data in actions["template_payloads"].items():
        _write(root, path, data)
        touched.append(path)
    return {"touched": sorted(touched), "kept": sorted(keep & clash_paths), "project_untouched": True}


def _cached_paths(root: Path) -> list[str]:
    result = git(root, "diff", "--cached", "--name-only", "-z", check=False)
    if result.returncode != 0:
        refuse("Refused: a commit needs a git checkout.")
    return [part for part in result.stdout.split("\0") if part]


def commit_kit(root: Path, old: str, new: str, yes: bool) -> dict:
    if not yes:
        refuse("Refused: a commit needs a yes in this run.")
    if not (root / ".git").exists():
        refuse("Refused: a commit needs a git checkout.")
    dirty = dirty_paths(root)
    stage = [path for path in dirty if is_managed(path)]
    left = [path for path in dirty if path not in stage]
    if not stage:
        refuse("Refused: nothing kit-owned to commit.")
    git(root, "add", "--", *stage)
    cached = _cached_paths(root)
    unsafe = [path for path in cached if not is_managed(path)]
    if unsafe:
        subprocess.run(["git", "restore", "--staged", "--", *unsafe], cwd=root, check=False)
        refuse("Refused: the commit would include a project file: " + ", ".join(unsafe))
    message = commit_message(old, new)
    git(root, "commit", "-m", message)
    return {"message": message, "committed": cached, "left_uncommitted": left}


def fetch_release(tag: str, dest: Path, url: str) -> None:
    normalized = normalize_request(tag)
    if normalized is None or not RELEASE_TAG.fullmatch(normalized):
        refuse(refusal_reason(tag.strip()))
    if dest.exists():
        refuse(f"Refused: {dest} already exists.")
    subprocess.run(
        ["git", "-c", "core.autocrlf=false", "clone", "--depth", "1", "--branch", normalized, url, str(dest)],
        check=True,
    )


def _print(payload: dict) -> None:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def _releases_text(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    result = subprocess.run(
        ["git", "ls-remote", "--tags", "--refs", KIT_REPO],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        refuse("Refused: no published vX.Y.Z release tag was found.")
    return result.stdout


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in {"push", "--push"}:
        refuse("Refused: this script does not push.")
    parser = argparse.ArgumentParser(description="Update a consumer project's CRAV1 kit from a published release.")
    parser.add_argument("command", choices=["detect", "resolve-target", "plan", "apply", "migrations", "commit", "fetch"])
    parser.add_argument("--root", default=".")
    parser.add_argument("--home")
    parser.add_argument("--to")
    parser.add_argument("--releases-file")
    parser.add_argument("--old")
    parser.add_argument("--new")
    parser.add_argument("--from-version", dest="from_version")
    parser.add_argument("--to-version")
    parser.add_argument("--migrations")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--keep", action="append", default=[])
    parser.add_argument("--take", action="append", default=[])
    parser.add_argument("--dest")
    parser.add_argument("--tag")
    parser.add_argument("--url", default=KIT_REPO)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    home = Path(args.home).resolve() if args.home else None
    try:
        if args.command == "detect":
            _print(detect(root, home))
            return 0
        if args.command == "resolve-target":
            tags = published_tags(_releases_text(args.releases_file))
            _print(resolve_target(normalize_request(args.to), tags))
            return 0
        if args.command == "fetch":
            if not args.tag or not args.dest:
                refuse("Refused: fetch needs a published release tag and a destination.")
            fetch_release(args.tag, Path(args.dest), args.url)
            _print({"fetched": normalize_request(args.tag), "dest": args.dest})
            return 0
        info = detect(root, home)
        if args.command == "plan":
            if info["mode"] == "kit-repo":
                refuse("Refused: this checkout is the kit source. Run the update in a consumer project.")
            if info["mode"] == "none":
                refuse("Refused: no CRAV1 kit install was found.")
            target = args.to_version or (None if args.to is None else normalize_request(args.to))
            if info["mode"] == "plugin":
                view = {
                    "mode": "plugin",
                    "installed": info.get("version"),
                    "version_from": info.get("version_from"),
                    "target": None if target is None else str(target).lstrip("v"),
                    "branch": info.get("branch"),
                    "heads_up": info.get("heads_up"),
                    "writes_kit_files": False,
                    "files": {"update": [], "add": [], "merge": [], "delete": [], "clash": [], "unchanged": [], "left_extra": []},
                    "templates": {"update": [], "delete": [], "left": []},
                    "project_untouched": True,
                    "advice": plugin_advice(info, None if target is None else str(target)),
                }
                _print(view)
                return 0
            if not args.old or not args.new:
                refuse("Refused: a drop-in plan needs the old release tree and the new release tree.")
            hosts = hosts_from_detect(info)
            actions = build_actions(root, Path(args.old), Path(args.new), hosts)
            view = plan_view(info, actions, None if target is None else str(target))
            registry = migration_registry(Path(args.new), Path(args.migrations) if args.migrations else None)
            if registry and registry.is_file() and info.get("version") and target:
                view["migration_ids"] = [
                    item["id"]
                    for item in select_migrations(load_migrations(registry), info["version"], str(target).lstrip("v"))
                ]
            else:
                view["migration_ids"] = []
            _print(view)
            return 0
        if args.command == "apply":
            if info["mode"] != "drop-in":
                refuse("Refused: a plugin install is not updated by a kit commit.")
            if not args.old or not args.new:
                refuse("Refused: apply needs the old release tree and the new release tree.")
            hosts = hosts_from_detect(info)
            _print(
                apply_overlay(
                    root,
                    Path(args.old),
                    Path(args.new),
                    hosts,
                    args.yes,
                    set(args.keep),
                    set(args.take),
                )
            )
            return 0
        if args.command == "migrations":
            registry = migration_registry(root, Path(args.migrations) if args.migrations else None)
            installed = args.from_version or info.get("version")
            target = args.to_version
            _print(run_migrations(root, installed, target, registry, args.apply, args.yes))
            return 0
        if args.command == "commit":
            if not args.from_version or not args.to_version:
                refuse("Refused: a commit needs the installed version and the target version.")
            _print(commit_kit(root, args.from_version, args.to_version, args.yes))
            return 0
    except Refuse:
        return 2
    refuse("Refused: unknown command.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
