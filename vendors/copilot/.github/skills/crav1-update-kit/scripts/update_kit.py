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
import fnmatch
import json
import re
import shutil
import subprocess
import sys
import tempfile
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
# Kit 2.0 names its skills and agents crav1-2- and writes .crav1-2/ and sot/.
# This 1.x script never writes, stages, or deletes those paths.
V2_NAME = re.compile(r"^crav1-2-")
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
KIT_JSON = ".crav1/kit.json"
KIT_SCHEMA = 1


class Refuse(SystemExit):
    def __init__(self, message: str):
        self.message = message
        super().__init__(2)


def refuse(message: str) -> None:
    print(message, file=sys.stderr)
    raise Refuse(message)


def _is_v1_version(value: str) -> bool:
    """True for a 1.x release number. 2.0 tags are ignored by this kit."""
    match = VERSION_NUM.fullmatch(value.strip().lstrip("v"))
    return bool(match) and match.group(1) == "1"


def is_v2_path(path: str) -> bool:
    """A kit 2.0 path: a crav1-2- skill or agent name, .crav1-2/, or sot/.

    The crav1-2- name can sit at any skill or agent folder level, such as
    .cursor/agents/crav1-2-review.md or .agents/skills/crav1-2-help/SKILL.md.
    """
    rel = path.replace("\\", "/").strip()
    while rel.startswith("./"):
        rel = rel[2:]
    rel = rel.lstrip("/")
    if rel == "sot" or rel.startswith("sot/"):
        return True
    if rel == ".crav1-2" or rel.startswith(".crav1-2/"):
        return True
    for part in rel.split("/"):
        if part == ".crav1-2" or part.startswith(".crav1-2/"):
            return True
        stem = part[:-3] if part.endswith(".md") else part
        if V2_NAME.match(part) or V2_NAME.match(stem):
            return True
    return False


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
        match = RELEASE_TAG.fullmatch(line)
        # 1.205.0: a 1.x install is never offered a 2.0 tag, including v2.x
        # and a prerelease such as v2.0.0-alpha.N (that one already fails the
        # vX.Y.Z shape). Only v1.Y.Z stays in the list.
        if match and match.group(1) == "1":
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
    if request is not None:
        match = RELEASE_TAG.fullmatch(request)
        if match and match.group(1) != "1":
            refuse(f"Refused: {request} is not a 1.x release.")
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
    for kind, rel in _dropin_markers():
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
    selected, source = read_selection(root)
    return {
        "mode": mode,
        "installs": installs,
        "version": None if primary is None else primary.get("version"),
        "version_from": None if primary is None else primary.get("version_from"),
        "branch": branch,
        "dirty": dirty,
        "heads_up": heads_up(branch, dirty, selection_hosts(root)),
        "writes_kit_files": mode == "drop-in",
        "vendors": present_vendors(root) if source == "inferred" else selected,
        "vendors_from": source,
    }


def _dropin_markers() -> list[tuple[str, str]]:
    """Cursor and Claude drop-in markers. The table's values match the 1.200 constants."""
    cursor = _row("cursor")
    claude = _row("claude")
    cursor_marker = str(cursor["marker"]) if cursor and cursor.get("marker") else CURSOR_DROPIN_MARKER
    claude_marker = str(claude["marker"]) if claude and claude.get("marker") else CLAUDE_DROPIN_MARKER
    return [("cursor-drop-in", cursor_marker), ("claude-drop-in", claude_marker)]


def present_vendors(root: Path) -> list[str]:
    """Vendor names whose marker file is in this tree. Read-only."""
    table = vendor_table()
    rows = table.get("vendors") if isinstance(table, dict) else None
    if not isinstance(rows, dict):
        found = []
        if (root / CURSOR_DROPIN_MARKER).is_file():
            found.append("cursor")
        if (root / CLAUDE_DROPIN_MARKER).is_file():
            found.append("claude")
        return sorted(found)
    found = []
    for name, row in rows.items():
        marker = row.get("marker") if isinstance(row, dict) else None
        if marker and (root / str(marker)).is_file():
            found.append(name)
    return sorted(found)


def _skill_count(root: Path, folder: str) -> int:
    base = root / folder
    if not base.is_dir():
        return 0
    return sum(1 for child in base.iterdir() if child.is_dir() and (child / "SKILL.md").is_file())


def vendor_report(root: Path) -> dict:
    """Each vendor's folder and skill count. Writes nothing."""
    table = vendor_table()
    rows = table.get("vendors") if isinstance(table, dict) else None
    if not isinstance(rows, dict):
        refuse("Refused: the vendor table is not in this install.")
    listed = []
    for name in sorted(rows):
        row = rows[name]
        if not isinstance(row, dict):
            continue
        folder = str(row.get("skills") or "")
        listed.append({"name": name, "folder": folder, "skills": _skill_count(root, folder)})
    return {"vendors": listed}


def command_prefix(vendor: str | None) -> str:
    """`/` unless the vendor's row says otherwise. Empty stays `/`."""
    if not vendor:
        return "/"
    row = _row(vendor)
    if row is not None:
        prefix = row.get("prefix")
        return str(prefix) if prefix else "/"
    if vendor_table() is None and vendor in _FALLBACK_PREFIX:
        return _FALLBACK_PREFIX[vendor]
    refuse(f"Refused: {vendor} is not a vendor.")
    return "/"


def with_vendor(text: str, vendor: str | None) -> str:
    """Rewrite `/crav1-` commands. A `/` prefix returns the same text."""
    prefix = command_prefix(vendor)
    if prefix == "/":
        return text
    return COMMAND_PREFIX.sub(prefix + "crav1-", text)


def _require_vendor(name: str) -> dict:
    rows = _vendor_rows()
    if not rows:
        refuse("Refused: the vendor table is not in this install.")
    row = rows.get(name)
    if not isinstance(row, dict):
        refuse(f"Refused: {name} is not a vendor.")
    return row


def _checkout_root() -> Path | None:
    """The kit checkout that holds this script, when it also has the Codex tree."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if not (parent / "vendors" / "codex").is_dir():
            continue
        if (parent / "plugins/crav1/.cursor-plugin/plugin.json").is_file():
            return parent
        if (parent / ".cursor/skills/crav1/crav1-update-kit/vendors.json").is_file():
            return parent
    return None


def _resolve_tree(explicit: str | None) -> Path:
    """A release checkout. `--new` or `--old` wins. Otherwise the checkout that holds this script."""
    if explicit:
        path = Path(explicit)
        if not path.is_dir():
            refuse(f"Refused: {explicit} is not a release tree.")
        return path.resolve()
    found = _checkout_root()
    if found is None:
        refuse("Refused: add needs the release tree (--new).")
    return found


def _tree_version(tree: Path) -> str:
    plugin = tree / "plugins/crav1/.cursor-plugin/plugin.json"
    version = version_in_plugin(plugin) if plugin.is_file() else None
    if version:
        return version
    for rel in (
        ".cursor/skills/crav1/crav1-docs/reference/workflow.md",
        "vendors/codex/.agents/skills/crav1-docs/reference/workflow.md",
    ):
        path = tree / rel
        if path.is_file():
            found = version_in_workflow(path)
            if found:
                return found
    return ""


def _source_has_vendor(tree: Path, row: dict) -> bool:
    marker = str(row.get("marker") or "")
    if not marker:
        return False
    return (_release_base(tree, row) / marker).is_file()


def _vendor_view(name: str, row: dict, actions: dict, note: str | None = None) -> dict:
    """Counts first, then the paths. Clash rows match the normal plan (`path` and `hunks`)."""
    files = actions["files"]
    samples: list[str] = []
    for key in ("add", "update", "merge", "delete"):
        for path in files[key]:
            if len(samples) < 10:
                samples.append(path)
    for item in files["clash"]:
        if len(samples) >= 10:
            break
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            samples.append(item["path"])
    view = {
        "vendor": name,
        "folder": row.get("skills"),
        "install": bool(row.get("install")),
        "added": files["add"],
        "merged": files["merge"],
        "updated": files["update"],
        "delete": files["delete"],
        "clash": files["clash"],
        "unchanged": len(files["unchanged"]),
        "left_extra": files["left_extra"],
        "extras": list(row.get("extras") or []),
        "samples": samples,
        "counts": {
            "add": len(files["add"]),
            "update": len(files["update"]),
            "merge": len(files["merge"]),
            "delete": len(files["delete"]),
            "clash": len(files["clash"]),
            "unchanged": len(files["unchanged"]),
        },
        "project_untouched": True,
    }
    if note:
        view["note"] = note
    return view


def _not_installed_view(name: str, row: dict) -> dict:
    return {
        "vendor": name,
        "folder": row.get("skills"),
        "install": False,
        "added": [],
        "merged": [],
        "updated": [],
        "delete": [],
        "clash": [],
        "unchanged": 0,
        "left_extra": [],
        "extras": list(row.get("extras") or []),
        "samples": [],
        "counts": {"add": 0, "update": 0, "merge": 0, "delete": 0, "clash": 0, "unchanged": 0},
        "project_untouched": True,
        "note": f"{name} is in the vendor table and is not installed by this release.",
    }


def _vendor_actions(root: Path, name: str, row: dict, *, adding: bool, tree: Path, selected: list[str]) -> dict:
    if not _source_has_vendor(tree, row):
        refuse(f"Refused: the {name} tree is not in this release.")
    empty = Path(tempfile.mkdtemp(prefix="crv"))
    try:
        if adding:
            return build_actions(root, empty, tree, {name}, with_templates=False, with_style=False)
        if name not in selected and not (root / str(row.get("marker") or "\0")).is_file():
            refuse(f"Refused: {name} is not installed here.")
        return build_actions(root, tree, empty, {name}, with_templates=False, with_style=False)
    finally:
        shutil.rmtree(empty, ignore_errors=True)


def vendor_change(root: Path, names: list[str], *, adding: bool, tree: Path) -> dict:
    """Plan for add or remove. The old side of an add is empty. Remove's new side is empty."""
    if not names:
        refuse("Refused: name the vendor to add or remove.")
    selected, _source = read_selection(root)
    listed = []
    changed: list[str] = []
    for name in names:
        row = _require_vendor(name)
        if not row.get("install"):
            listed.append(_not_installed_view(name, row))
            continue
        actions = _vendor_actions(root, name, row, adding=adding, tree=tree, selected=selected)
        listed.append(_vendor_view(name, row, actions))
        changed.append(name)
    if changed and adding:
        after = sorted(set(selected) | set(changed))
    elif changed:
        after = sorted(set(selected) - set(changed))
    else:
        after = list(selected)
    kit_op = "unchanged"
    if changed:
        desired = kit_json_bytes(after)
        current_path = root / KIT_JSON
        current = current_path.read_bytes() if current_path.is_file() else None
        if current is None:
            kit_op = "add"
        elif _normalize_newlines(current) != _normalize_newlines(desired):
            kit_op = "update"
    writes = kit_op != "unchanged" or any(
        item.get("added") or item.get("updated") or item.get("merged") or item.get("delete") or item.get("clash")
        for item in listed
    )
    return {
        "vendors": listed,
        "project_untouched": True,
        "writes_kit_files": writes,
        "kit_json": KIT_JSON,
        "kit_json_op": kit_op,
        "vendors_after": after,
        "version": _tree_version(tree),
    }


def apply_vendor_change(
    root: Path,
    names: list[str],
    *,
    adding: bool,
    tree: Path,
    yes: bool,
    keep: set[str],
    take: set[str],
) -> dict:
    if not yes:
        refuse("Refused: writing kit files needs a yes in this run.")
    if keep & take:
        refuse("Refused: a clash cannot be both kept and taken.")
    selected, _source = read_selection(root)
    clash_paths: set[str] = set()
    payloads: dict[str, bytes | None | dict] = {}
    skip: set[str] = set()
    changed: list[str] = []
    for name in names:
        row = _require_vendor(name)
        if not row.get("install"):
            continue
        actions = _vendor_actions(root, name, row, adding=adding, tree=tree, selected=selected)
        changed.append(name)
        clash_paths |= {item["path"] for item in actions["files"]["clash"]}
        payloads.update(actions["payloads"])
        skip.update(actions["files"]["unchanged"])
        skip.update(actions["files"]["left_extra"])
    missing = clash_paths - keep - take
    if missing:
        listed = ", ".join(sorted(missing))
        refuse(f"Refused: a clash needs keep or take before writing: {listed}")
    unknown = (keep | take) - clash_paths
    if unknown:
        listed = ", ".join(sorted(unknown))
        refuse(f"Refused: {listed} is not a clash.")
    touched: list[str] = []
    for path, data in payloads.items():
        if path in clash_paths or path in skip or isinstance(data, dict):
            continue
        _write(root, path, data)
        touched.append(path)
    for path in sorted(keep | take):
        choice = payloads[path]
        if not isinstance(choice, dict):
            refuse(f"Refused: {path} is not a clash.")
        picked = choice["keep"] if path in keep else choice["take"]
        _write(root, path, picked)
        touched.append(path)
    after = sorted(set(selected) | set(changed)) if adding else sorted(set(selected) - set(changed))
    if changed:
        desired = kit_json_bytes(after)
        current_path = root / KIT_JSON
        current = current_path.read_bytes() if current_path.is_file() else None
        if current is None or _normalize_newlines(current) != _normalize_newlines(desired):
            _write(root, KIT_JSON, desired)
            touched.append(KIT_JSON)
    return {
        "vendors": changed,
        "touched": sorted(set(touched)),
        "kept": sorted(keep & clash_paths),
        "project_untouched": True,
        "vendors_after": after if changed else list(selected),
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


def _status_paths(text: str, prefix: str | None = None) -> list[str]:
    paths = []
    for line in text.splitlines():
        if len(line) < 4:
            continue
        if prefix is not None and not line.startswith(prefix):
            continue
        path = line[3:].strip().strip('"')
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip().strip('"')
        paths.append(path)
    return paths


def dirty_paths(root: Path) -> list[str]:
    if not (root / ".git").exists():
        return []
    # -uall lists files inside a new folder. A plain status collapses `.crav1/` to one line.
    result = git(root, "status", "--porcelain", "-uall", check=False)
    if result.returncode != 0:
        return []
    return _status_paths(result.stdout)


def _ignored_owned(root: Path, hosts: set[str] | None) -> list[str]:
    """Kit files a gitignore hides. `.crav1/.gitignore` of `*` hides kit.json."""
    specs = [".crav1", ".cursor", ".claude", ".agents", ".github"]
    result = git(root, "status", "--porcelain", "-uall", "--ignored", "--", *specs, check=False)
    if result.returncode != 0:
        return []
    found = []
    for path in _status_paths(result.stdout, "!!"):
        if is_managed(path, hosts) or style_rule_kit_owned(root, path):
            found.append(path)
    return found


def is_template(path: str) -> bool:
    return path.startswith(TEMPLATE_ROOTS)


COMMAND_PREFIX = re.compile(r"(?<![A-Za-z0-9_./-])/crav1-")
_VENDOR_CACHE: dict | None = None
_VENDOR_LOADED = False
_HOST_ORDER = ("cursor", "claude", "codex", "copilot")
_FALLBACK_PREFIX = {"cursor": "/", "claude": "/", "codex": "$", "copilot": "/"}


def _vendors_file() -> Path | None:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent / "vendors.json", here / "vendors.json"):
        if candidate.is_file():
            return candidate
    return None


def vendor_table() -> dict | None:
    """The vendor table next to this skill, or None for the single-file release asset."""
    global _VENDOR_CACHE, _VENDOR_LOADED
    if not _VENDOR_LOADED:
        path = _vendors_file()
        if path is None:
            _VENDOR_CACHE = None
        else:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                data = None
            _VENDOR_CACHE = data if isinstance(data, dict) else None
        _VENDOR_LOADED = True
    return _VENDOR_CACHE


def _legacy_is_cursor_kit(path: str) -> bool:
    if path.startswith(".cursor/skills/crav1/"):
        return True
    if path.startswith(".cursor/agents/crav1-") and path.endswith(".md") and path.count("/") == 2:
        return True
    if path == ".cursor/agent-assets/README.md" or path.startswith(".cursor/agent-assets/crav1-"):
        return True
    return path == ".cursor/rules/crav1.mdc"


def _legacy_is_claude_kit(path: str) -> bool:
    if path.startswith(".claude/skills/"):
        top = path[len(".claude/skills/") :].split("/", 1)[0]
        if top == "crav1-docs" or top.startswith("crav1-"):
            return True
    if path.startswith(".claude/agents/crav1-") and path.endswith(".md") and path.count("/") == 2:
        return True
    if path == ".claude/agent-assets/README.md" or path.startswith(".claude/agent-assets/crav1-"):
        return True
    return path == ".claude/CLAUDE.md"


def _match_owns(path: str, owns: list) -> bool:
    """One allow-list row. The shapes match the 1.200 Cursor and Claude checks."""
    for rule in owns:
        if not isinstance(rule, dict):
            continue
        if "tree" in rule:
            root = str(rule["tree"]).rstrip("/")
            if path.startswith(root + "/"):
                return True
        elif "glob" in rule:
            pattern = str(rule["glob"])
            if "/" not in pattern:
                continue
            directory, name = pattern.rsplit("/", 1)
            prefix = directory + "/"
            if not path.startswith(prefix):
                continue
            rest = path[len(prefix) :]
            if "/" in rest:
                continue
            if fnmatch.fnmatch(rest, name):
                return True
        elif "assets" in rule:
            base = str(rule["assets"]).rstrip("/")
            readme = str(rule.get("readme") or "README.md")
            token = str(rule.get("prefix") or "crav1-")
            if path == f"{base}/{readme}" or path.startswith(f"{base}/{token}"):
                return True
        elif "skills" in rule:
            base = str(rule["skills"]).rstrip("/")
            if not path.startswith(base + "/"):
                continue
            token = str(rule.get("names") or "crav1")
            top = path[len(base) + 1 :].split("/", 1)[0]
            if top == f"{token}-docs" or top.startswith(f"{token}-"):
                return True
        elif "file" in rule and path == rule["file"]:
            return True
    return False


def _row(name: str) -> dict | None:
    table = vendor_table()
    if not table:
        return None
    rows = table.get("vendors")
    if not isinstance(rows, dict):
        return None
    row = rows.get(name)
    return row if isinstance(row, dict) else None


def is_cursor_kit(path: str) -> bool:
    row = _row("cursor")
    if row is None:
        return _legacy_is_cursor_kit(path)
    return _match_owns(path, row.get("owns") or [])


def is_claude_kit(path: str) -> bool:
    row = _row("claude")
    if row is None:
        return _legacy_is_claude_kit(path)
    return _match_owns(path, row.get("owns") or [])


def is_kit_path(path: str, hosts: set[str] | None = None) -> bool:
    """True when path is owned by one of hosts.

    A kit 2.0 path is never owned here, even when a crav1- name pattern would match it.

    With no hosts, only Cursor and Claude match. That keeps a hand-made Codex
    tree a project file until Codex is selected. Pass the hosts for this run
    when Codex is part of it.
    """
    if is_v2_path(path):
        return False
    table = vendor_table()
    if not table or not isinstance(table.get("vendors"), dict):
        return _legacy_is_cursor_kit(path) or _legacy_is_claude_kit(path)
    rows = table["vendors"]
    names = ("cursor", "claude") if hosts is None else tuple(hosts)
    for name in names:
        row = rows.get(name)
        if isinstance(row, dict) and row.get("install") and _match_owns(path, row.get("owns") or []):
            return True
    return False


def owned_by_install(path: str) -> bool:
    """Any vendor this release installs. Copilot stays out until its row is live."""
    if is_v2_path(path):
        return False
    table = vendor_table()
    if not table or not isinstance(table.get("vendors"), dict):
        return _legacy_is_cursor_kit(path) or _legacy_is_claude_kit(path)
    for row in table["vendors"].values():
        if isinstance(row, dict) and row.get("install") and _match_owns(path, row.get("owns") or []):
            return True
    return False


def is_managed(path: str, hosts: set[str] | None = None) -> bool:
    return path == KIT_JSON or is_kit_path(path, hosts) or is_template(path)


def heads_up(branch: str | None, dirty: list[str], hosts: set[str] | None = None) -> dict:
    def kit_file(path: str) -> bool:
        return path == KIT_JSON or is_kit_path(path, hosts)

    kit = [path for path in dirty if kit_file(path)]
    project = [path for path in dirty if not kit_file(path)]
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
        if is_v2_path(rel):
            continue
        out[rel] = path.read_bytes()


def _read_named(folder: Path, prefix: str, pattern: str, out: dict[str, bytes]) -> None:
    if not folder.is_dir():
        return
    for path in folder.glob(pattern):
        if path.is_file() and not path.is_symlink():
            rel = f"{prefix}/{path.name}"
            if is_v2_path(rel):
                continue
            out[rel] = path.read_bytes()


def _read_assets(folder: Path, prefix: str, out: dict[str, bytes]) -> None:
    if not folder.is_dir():
        return
    readme = folder / "README.md"
    if readme.is_file() and not readme.is_symlink():
        out[f"{prefix}/README.md"] = readme.read_bytes()
    for child in folder.iterdir():
        if child.is_dir() and child.name.startswith("crav1-") and not child.name.startswith("crav1-2-") and not child.is_symlink():
            _read_tree(child, f"{prefix}/{child.name}", out)


def _legacy_collect_kit(root: Path, hosts: set[str]) -> dict[str, bytes]:
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
                if child.is_dir() and not child.name.startswith("crav1-2-") and (
                    child.name == "crav1-docs" or child.name.startswith("crav1-")
                ):
                    _read_tree(child, f".claude/skills/{child.name}", out)
        _read_named(root / ".claude/agents", ".claude/agents", "crav1-*.md", out)
        _read_assets(root / ".claude/agent-assets", ".claude/agent-assets", out)
        claude = root / ".claude/CLAUDE.md"
        if claude.is_file() and not claude.is_symlink():
            out[".claude/CLAUDE.md"] = claude.read_bytes()
    return out


def _collect_owns(root: Path, owns: list, out: dict[str, bytes]) -> None:
    for rule in owns:
        if not isinstance(rule, dict):
            continue
        if "tree" in rule:
            rel = str(rule["tree"]).rstrip("/")
            _read_tree(root / rel, rel, out)
        elif "glob" in rule:
            pattern = str(rule["glob"])
            if "/" not in pattern:
                continue
            directory, name = pattern.rsplit("/", 1)
            _read_named(root / directory, directory, name, out)
        elif "assets" in rule:
            base = str(rule["assets"]).rstrip("/")
            readme_name = str(rule.get("readme") or "README.md")
            token = str(rule.get("prefix") or "crav1-")
            folder = root / base
            if not folder.is_dir():
                continue
            readme = folder / readme_name
            if readme.is_file() and not readme.is_symlink():
                out[f"{base}/{readme_name}"] = readme.read_bytes()
            for child in folder.iterdir():
                if (
                    child.is_dir()
                    and child.name.startswith(token)
                    and not child.name.startswith("crav1-2-")
                    and not child.is_symlink()
                ):
                    _read_tree(child, f"{base}/{child.name}", out)
        elif "skills" in rule:
            base = str(rule["skills"]).rstrip("/")
            token = str(rule.get("names") or "crav1")
            folder = root / base
            if not folder.is_dir():
                continue
            for child in folder.iterdir():
                if child.is_dir() and not child.is_symlink() and not child.name.startswith("crav1-2-") and (
                    child.name == f"{token}-docs" or child.name.startswith(f"{token}-")
                ):
                    _read_tree(child, f"{base}/{child.name}", out)
        elif "file" in rule:
            rel = str(rule["file"])
            path = root / rel
            if path.is_file() and not path.is_symlink():
                out[rel] = path.read_bytes()


def _release_base(root: Path, row: dict) -> Path:
    """Where a release checkout keeps this vendor.

    Cursor and Claude live at the checkout root. Codex lives under ``vendors/codex``.
    """
    tree = str(row.get("tree") or "").strip("/")
    if not tree:
        return root
    for rule in row.get("owns") or []:
        if not isinstance(rule, dict):
            continue
        for key in ("tree", "skills", "file", "assets", "glob"):
            value = rule.get(key)
            if isinstance(value, str) and (value == tree or value.startswith(tree + "/")):
                return root
    nested = root / tree
    if nested.is_dir():
        return nested
    return root


def _vendor_rows() -> dict:
    table = vendor_table()
    rows = table.get("vendors") if isinstance(table, dict) else None
    return rows if isinstance(rows, dict) else {}


def kit_json_bytes(names: list[str]) -> bytes:
    body = {"schema": KIT_SCHEMA, "vendors": sorted(set(names))}
    return (json.dumps(body, indent=2) + "\n").encode("utf-8")


def parse_kit_json(data: bytes) -> list[str]:
    try:
        body = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        refuse("Refused: .crav1/kit.json is not JSON.")
    if not isinstance(body, dict) or body.get("schema") != KIT_SCHEMA:
        refuse("Refused: .crav1/kit.json schema is not 1.")
    names = body.get("vendors")
    if not isinstance(names, list) or any(not isinstance(name, str) for name in names):
        refuse("Refused: .crav1/kit.json vendors must be a list of names.")
    rows = _vendor_rows()
    if not rows:
        refuse("Refused: the vendor table is not in this install.")
    for name in names:
        if name not in rows:
            refuse(f"Refused: {name} is not a vendor.")
    return sorted(set(names))


def inferred_vendors(root: Path) -> list[str]:
    """Installable vendors whose marker file is present. Copilot is not inferred."""
    found = []
    for name, row in _vendor_rows().items():
        if not isinstance(row, dict) or not row.get("install"):
            continue
        marker = row.get("marker")
        if marker and (root / str(marker)).is_file():
            found.append(name)
    return sorted(found)


def read_selection(root: Path) -> tuple[list[str], str]:
    path = root / KIT_JSON
    if path.is_file():
        return parse_kit_json(path.read_bytes()), "kit.json"
    if not _vendor_rows():
        return present_vendors(root), "inferred"
    return inferred_vendors(root), "inferred"


def selection_hosts(root: Path) -> set[str] | None:
    """Installable vendors for this project. None means the legacy allow-list."""
    if not _vendor_rows():
        return None
    names, _source = read_selection(root)
    rows = _vendor_rows()
    return {name for name in names if isinstance(rows.get(name), dict) and rows[name].get("install")}


def ensure_kit_json(root: Path, actions: dict, names: list[str]) -> None:
    """Offer ``.crav1/kit.json`` in this plan. A missing file is an add."""
    if not _vendor_rows():
        return
    desired = kit_json_bytes(names)
    path = root / KIT_JSON
    current = path.read_bytes() if path.is_file() else None
    if current is not None and _normalize_newlines(current) == _normalize_newlines(desired):
        return
    bucket = "add" if current is None else "update"
    actions["files"][bucket].append(KIT_JSON)
    actions["payloads"][KIT_JSON] = desired


def hosts_for_update(root: Path, info: dict) -> set[str]:
    """Vendors a normal update writes. The file wins when it exists."""
    if not _vendor_rows():
        return hosts_from_detect(info)
    selected, source = read_selection(root)
    rows = _vendor_rows()
    installable = {name for name in selected if isinstance(rows.get(name), dict) and rows[name].get("install")}
    if source == "kit.json":
        return installable
    return hosts_from_detect(info) | installable


def collect_kit(root: Path, hosts: set[str], *, release: bool = False) -> dict[str, bytes]:
    table = vendor_table()
    rows = table.get("vendors") if isinstance(table, dict) else None
    if not isinstance(rows, dict):
        return _legacy_collect_kit(root, hosts)
    out: dict[str, bytes] = {}
    for name in _HOST_ORDER:
        if name not in hosts:
            continue
        row = rows.get(name)
        if not isinstance(row, dict) or not row.get("install"):
            continue
        base = _release_base(root, row) if release else root
        _collect_owns(base, row.get("owns") or [], out)
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
    # No old release to merge against: a different local file is a clash, same shape as any other.
    if old is None and local is not None and local_n != new_n:
        return {
            "op": "clash",
            "hunks": [{"local": _preview(local_n), "kit": _preview(new_n)}],
            "keep_data": styled(local_n),
            "take_data": styled(new_n),
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


# Persisted commit-style rules (1.176.0). The kit wrote them once from the
# message-only assets; an old copy can point at a skill that no longer exists.
STYLE_RULES = {
    ".cursor/rules/draft-commit-style.mdc": "draft-commit-style.mdc",
    ".cursor/rules/draft-commit-gitlog.mdc": "draft-commit-gitlog.mdc",
    ".claude/rules/draft-commit-style.md": "draft-commit-style.mdc",
    ".claude/rules/draft-commit-gitlog.md": "draft-commit-gitlog.mdc",
}
STYLE_ASSET_DIRS = (
    ".cursor/skills/crav1/crav1-finalize-commit/branches/message-only/assets",
    ".claude/skills/crav1-finalize-commit/branches/message-only/assets",
    "plugins/crav1/skills/crav1-finalize-commit/branches/message-only/assets",
    ".cursor/skills/crav1/crav1-draft-commit-message/assets",
)
STALE_STYLE_PATHS = ("crav1-draft-commit-message/",)


def _style_asset(tree: Path, name: str) -> bytes | None:
    for folder in STYLE_ASSET_DIRS:
        path = tree / folder / name
        if path.is_file():
            return path.read_bytes()
    return None


def style_rule_actions(root: Path, old_root: Path, new_root: Path) -> dict:
    """Rewrite a persisted style rule from the current asset when it is stale.

    Stale means it is the old release's copy unchanged, or it names a path
    that no longer exists. A rule edited by hand is left and listed. A stale
    rule with no asset in the new release is removed (1.178.0): it is listed
    under `delete` and the kit removes it in the same yes.
    """
    out = {"update": [], "left": [], "payloads": {}, "remove": []}
    for rel, name in STYLE_RULES.items():
        path = root / rel
        if not path.is_file():
            continue
        local = path.read_bytes()
        new = _style_asset(new_root, name)
        if new is None:
            text = local.decode("utf-8", errors="replace")
            old = _style_asset(old_root, name)
            same_as_old = old is not None and _normalize_newlines(local) == _normalize_newlines(old)
            if same_as_old or any(stale in text for stale in STALE_STYLE_PATHS):
                out["remove"].append(rel)
                out["payloads"][rel] = None
            continue
        if _normalize_newlines(local) == _normalize_newlines(new):
            continue
        old = _style_asset(old_root, name)
        text = local.decode("utf-8", errors="replace")
        same_as_old = old is not None and _normalize_newlines(local) == _normalize_newlines(old)
        if same_as_old or any(stale in text for stale in STALE_STYLE_PATHS):
            out["update"].append(rel)
            out["payloads"][rel] = _restyle(new, preferred_newline(root, rel, local))
        else:
            out["left"].append({"path": rel, "reason": "edited by hand, so it is left as it is"})
    return out


def build_actions(
    root: Path,
    old_root: Path,
    new_root: Path,
    hosts: set[str],
    *,
    with_templates: bool = True,
    with_style: bool = True,
) -> dict:
    old_files = collect_kit(old_root, hosts, release=True)
    new_files = collect_kit(new_root, hosts, release=True)
    local_files = collect_kit(root, hosts, release=False)
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
        if is_v2_path(path) or not is_kit_path(path, hosts):
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
    templates = {"update": [], "delete": [], "left": []}
    template_payloads: dict[str, bytes | None] = {}
    if with_templates:
        old_templates = collect_templates(old_root)
        new_templates = collect_templates(new_root)
        local_templates = collect_templates(root)
        for path in sorted(set(local_templates) | set(old_templates) | set(new_templates)):
            if is_v2_path(path):
                continue
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
    style_rules = style_rule_actions(root, old_root, new_root) if with_style else {"update": [], "left": [], "payloads": {}, "remove": []}
    for rel in style_rules["update"]:
        files["update"].append(rel)
        payloads[rel] = style_rules["payloads"][rel]
    for rel in style_rules.get("remove", []):
        files["delete"].append(rel)
        payloads[rel] = None
    return {
        "files": files,
        "templates": templates,
        "payloads": payloads,
        "template_payloads": template_payloads,
        "style_rules_left": style_rules["left"],
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
        "style_rules_left": actions.get("style_rules_left", []),
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


def is_style_rule(path: str) -> bool:
    """A persisted commit-style rule the kit wrote (STYLE_RULES, 1.178.0)."""
    return path in STYLE_RULES


def style_rule_kit_owned(root: Path, rel: str) -> bool:
    """True when a style rule may go in the kit commit (1.178.0).

    It is removed, or it matches a current message-only asset installed on
    this branch, so it is the kit's own rewrite and not a hand edit.
    """
    if not is_style_rule(rel):
        return False
    path = root / rel
    if not path.is_file():
        return True
    local = _normalize_newlines(path.read_bytes())
    asset = _style_asset(root, STYLE_RULES[rel])
    return asset is not None and local == _normalize_newlines(asset)


def _write(root: Path, rel: str, data: bytes | None) -> None:
    if is_v2_path(rel):
        refuse(f"Refused: {rel} belongs to kit 2.0.")
    if not (rel == KIT_JSON or is_template(rel) or is_style_rule(rel) or owned_by_install(rel)):
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


def apply_overlay(
    root: Path,
    old_root: Path,
    new_root: Path,
    hosts: set[str],
    yes: bool,
    keep: set[str],
    take: set[str],
    kit_names: list[str] | None = None,
) -> dict:
    if not yes:
        refuse("Refused: writing kit files needs a yes in this run.")
    if keep & take:
        refuse("Refused: a clash cannot be both kept and taken.")
    actions = build_actions(root, old_root, new_root, hosts)
    if kit_names is not None:
        ensure_kit_json(root, actions, kit_names)
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


def _ignored(root: Path, paths: list[str]) -> set[str]:
    if not paths:
        return set()
    result = git(root, "check-ignore", "--", *paths, check=False)
    return {line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()}


def release_file_list(trees: list[Path], hosts: set[str] | None) -> set[str]:
    """Paths the release trees actually ship, plus kit.json.

    The commit stages this list. A name pattern is not the list: a crav1-2-
    file matches crav1-* and must not be staged. Templates and a commit-style
    rule are included when that release still contains them.
    """
    listed: set[str] = {KIT_JSON}
    host_set = set(hosts) if hosts else {"cursor", "claude"}
    for tree in trees:
        listed.update(collect_kit(tree, host_set, release=True))
        listed.update(collect_templates(tree))
        for rel, name in STYLE_RULES.items():
            if _style_asset(tree, name) is not None:
                listed.add(rel)
    return {path for path in listed if not is_v2_path(path)}


def _stageable(root: Path, path: str, listed: set[str]) -> bool:
    """True when path is on the release list. Kit 2.0 paths are never stageable."""
    if is_v2_path(path):
        return False
    if path in listed:
        return True
    return style_rule_kit_owned(root, path)


def commit_kit(
    root: Path,
    old: str,
    new: str,
    yes: bool,
    *,
    vendors: list[str] | None = None,
    removing: bool = False,
    old_root: Path | None = None,
    new_root: Path | None = None,
) -> dict:
    if not yes:
        refuse("Refused: a commit needs a yes in this run.")
    if not (root / ".git").exists():
        refuse("Refused: a commit needs a git checkout.")
    trees = [tree for tree in (old_root, new_root) if tree is not None]
    if not trees:
        refuse("Refused: a commit needs the release tree.")
    dirty = dirty_paths(root)
    base = selection_hosts(root)
    hosts = set(base or ()) | set(vendors) if vendors else base
    for path in _ignored_owned(root, hosts):
        if is_v2_path(path):
            continue
        if path not in dirty:
            dirty.append(path)
    listed = release_file_list(trees, hosts)
    already = [path for path in _cached_paths(root) if is_v2_path(path)]
    if already:
        refuse("Refused: " + ", ".join(already) + " belongs to kit 2.0.")
    stage = [path for path in dirty if _stageable(root, path, listed)]
    left = [path for path in dirty if path not in stage]
    if not stage:
        refuse("Refused: nothing kit-owned to commit.")
    ignored = _ignored(root, stage)
    normal = [path for path in stage if path not in ignored]
    forced = [path for path in stage if path in ignored]
    if normal:
        git(root, "add", "--", *normal)
    if forced:
        git(root, "add", "-f", "--", *forced)
    cached = _cached_paths(root)
    v2_cached = [path for path in cached if is_v2_path(path)]
    if v2_cached:
        refuse("Refused: " + ", ".join(v2_cached) + " belongs to kit 2.0.")
    safe = [path for path in cached if _stageable(root, path, listed)]
    unsafe = [path for path in cached if path not in safe]
    if unsafe:
        subprocess.run(["git", "restore", "--staged", "--", *unsafe], cwd=root, check=False)
        refuse("Refused: the commit would include a project file: " + ", ".join(unsafe))
    if vendors:
        verb = "Remove" if removing else "Add"
        shown = " and ".join(vendors)
        message = f"{verb} CRAV1 kit vendor {shown} {tagify(new)}"
    else:
        message = commit_message(old, new)
    git(root, "commit", "-m", message)
    return {"message": message, "committed": cached, "left_uncommitted": left}


def default_dest(tag: str) -> Path:
    """A short folder in the system temp folder (1.190.0): long clone paths fail on Windows."""
    import tempfile

    base = Path(tempfile.gettempdir()) / ("ck" + re.sub(r"[^0-9]", "", tag))
    dest, n = base, 1
    while dest.exists():
        n += 1
        dest = base.with_name(f"{base.name}-{n}")
    return dest


def fetch_release(tag: str, dest: Path | None, url: str) -> Path:
    normalized = normalize_request(tag)
    if normalized is None or not RELEASE_TAG.fullmatch(normalized):
        refuse(refusal_reason(tag.strip()))
    if not normalized.startswith("v1."):
        refuse(f"Refused: {normalized} is not a 1.x release.")
    dest = dest or default_dest(normalized)
    if dest.exists():
        refuse(f"Refused: {dest} already exists.")
    cmd = ["git", "-c", "core.longpaths=true", "-c", "core.autocrlf=false", "clone", "--depth", "1",
           "--config", "core.longpaths=true", "--config", "core.autocrlf=false", "--branch", normalized, url, str(dest)]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip().splitlines()
        refuse(f"Refused: the clone of {normalized} failed: {detail[-1] if detail else 'no output'}. "
               "Try a shorter --dest, such as a folder right under the system temp folder.")
    verify_checkout(dest)
    return dest


def verify_checkout(dest: Path) -> None:
    """The clone must be complete before a plan reads it (1.190.0): git status in it is clean."""
    status = subprocess.run(["git", "-C", str(dest), "status", "--porcelain"], check=False, capture_output=True, text=True)
    lines = [line for line in status.stdout.splitlines() if line.strip()]
    if status.returncode != 0 or lines:
        sample = ", ".join(line[3:] for line in lines[:3])
        refuse(f"Refused: the checkout in {dest} is incomplete ({len(lines)} files differ{': ' + sample if sample else ''}), "
               "often a Windows path-length limit. Delete it and fetch again with a shorter --dest; no plan was made.")


def open_design_topics(root: Path) -> list[str]:
    """Design topics that are not done: Status in goal.md is not go-ahead or dropped."""
    out = []
    for goal in sorted((root / "docs" / "architecture" / "designs").glob("*/goal.md")):
        text = goal.read_text(encoding="utf-8")
        match = re.search(r"^Status: (.+)$", text, re.M)
        state = (match.group(1).strip().lower() if match else "open")
        if not state.startswith(("go-ahead", "dropped", "done")):
            out.append(goal.parent.name)
    return out


def ending_text(root: Path, uncommitted: int = 0, updated: bool = True) -> str:
    """1.190.0: after an update, reload the window; name the resume command for open design topics."""
    lines = ["Run next:"]
    topics = open_design_topics(root)
    if updated:
        lines += ["The kit files changed; reload the window so the new skills load.", "",
                  "Reload the window from the command palette:", "`Developer: Reload Window`"]
    for topic in topics:
        lines += ["", f"Go on with the {topic.replace('-', ' ')} design topic:", f"`/crav1-design-architecture {topic}`"]
    if len(lines) == 1:
        lines = ["Run next: nothing needed now."]
    if uncommitted:
        lines += ["", f"Uncommitted: {uncommitted} file{'s' if uncommitted != 1 else ''}; commit with `/crav1-finalize-commit` when ready."]
    return "\n".join(lines) + "\n"


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


LATEST_CACHE_HOURS = 12


def _latest_release(timeout: int = 5) -> str | None:
    """The newest published release version, read-only (1.198.0). None when offline or slow.

    CRAV1_KIT_LATEST overrides it (tests, offline use). One `git ls-remote` per
    12 hours, cached in the system temp folder.
    """
    import os
    import tempfile
    import time

    forced = os.environ.get("CRAV1_KIT_LATEST", "").strip()
    if forced:
        if forced.lower() in ("none", "off"):
            return None
        version = forced.lstrip("v")
        return version if _is_v1_version(version) else None
    cache = Path(tempfile.gettempdir()) / "crav1-kit-latest.json"
    try:
        data = json.loads(cache.read_text(encoding="utf-8"))
        cached = str(data.get("latest") or "")
        if time.time() - float(data.get("at", 0)) < LATEST_CACHE_HOURS * 3600 and _is_v1_version(cached):
            return cached
    except (OSError, ValueError, TypeError):
        pass
    try:
        result = subprocess.run(["git", "ls-remote", "--tags", "--refs", KIT_REPO], check=False, capture_output=True,
                                text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    tags = published_tags(result.stdout)
    if not tags:
        return None
    latest = tags[-1].lstrip("v")
    try:
        cache.write_text(json.dumps({"at": time.time(), "latest": latest}), encoding="utf-8")
    except OSError:
        pass
    return latest


def update_available(root: Path, home: Path | None = None, timeout: int = 5) -> dict | None:
    """One `Kit update available` line when a newer release is out (1.198.0). Read-only; None when
    the installed version is unknown, this is the kit repo, offline, or already the latest."""
    try:
        info = detect(Path(root), home)
    except Exception:  # noqa: BLE001 - never stop a walk for this check
        return None
    installed = info.get("version")
    if not installed or info.get("mode") in ("none", "kit-repo"):
        return None
    latest = _latest_release(timeout)
    if not latest or not _is_v1_version(latest) or not _is_v1_version(str(installed)):
        return None
    if version_key(latest) <= version_key(str(installed).lstrip("v")):
        return None
    return {"installed": str(installed).lstrip("v"), "latest": latest,
            "line": f"Kit update available: {str(installed).lstrip('v')} -> {latest}",
            "run": f"Update the kit first ({latest} is out):\n`/crav1-update-kit`"}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in {"push", "--push"}:
        refuse("Refused: this script does not push.")
    parser = argparse.ArgumentParser(description="Update a consumer project's CRAV1 kit from a published release.")
    parser.add_argument(
        "command",
        choices=["detect", "resolve-target", "plan", "apply", "migrations", "commit", "fetch", "ending", "available", "vendors"],
    )
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
    parser.add_argument("--uncommitted", type=int, default=0)
    parser.add_argument("--not-updated", action="store_true")
    parser.add_argument("--vendor", default=None, help="cursor, claude, codex, or copilot. The default prefix stays /.")
    parser.add_argument("--add", action="append", default=[], help="vendor to install, such as codex. Uses the release tree and does not upgrade other vendors.")
    parser.add_argument("--remove", action="append", default=[], help="vendor to remove. Deletes only kit-owned files that match the release.")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    home = Path(args.home).resolve() if args.home else None
    try:
        if args.command == "detect":
            _print(detect(root, home))
            return 0
        if args.command == "available":
            found = update_available(root, home)
            if found:
                found = dict(found)
                found["run"] = with_vendor(found["run"], args.vendor)
            _print({"ok": True, "update": found, "line": found["line"] if found else None})
            return 0
        if args.command == "resolve-target":
            tags = published_tags(_releases_text(args.releases_file))
            _print(resolve_target(normalize_request(args.to), tags))
            return 0
        if args.command == "fetch":
            if not args.tag:
                refuse("Refused: fetch needs a published release tag.")
            dest = fetch_release(args.tag, Path(args.dest) if args.dest else None, args.url)
            _print({"fetched": normalize_request(args.tag), "dest": str(dest), "complete": True})
            return 0
        if args.command == "vendors":
            _print(vendor_report(root))
            return 0
        if args.command in {"plan", "apply"} and (args.add or args.remove):
            if args.add and args.remove:
                refuse("Refused: add and remove are separate runs.")
            if (root / ".cursor/rules/kit-maintainer.mdc").is_file() and (
                root / "plugins/crav1/.cursor-plugin/plugin.json"
            ).is_file():
                refuse("Refused: this checkout is the kit source. Run the update in a consumer project.")
            adding = bool(args.add)
            tree = _resolve_tree((args.new or args.old) if adding else (args.old or args.new))
            names = args.add if adding else args.remove
            if args.command == "apply":
                _print(
                    apply_vendor_change(
                        root, names, adding=adding, tree=tree, yes=args.yes, keep=set(args.keep), take=set(args.take)
                    )
                )
            else:
                _print(vendor_change(root, names, adding=adding, tree=tree))
            return 0
        if args.command == "ending":
            sys.stdout.write(with_vendor(ending_text(root, args.uncommitted, not args.not_updated), args.vendor))
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
            hosts = hosts_for_update(root, info)
            actions = build_actions(root, Path(args.old), Path(args.new), hosts)
            names, source = read_selection(root)
            ensure_kit_json(root, actions, sorted(hosts) if source == "inferred" else names)
            view = plan_view(info, actions, None if target is None else str(target))
            view["vendors_from"] = source
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
            hosts = hosts_for_update(root, info)
            names, source = read_selection(root)
            _print(
                apply_overlay(
                    root,
                    Path(args.old),
                    Path(args.new),
                    hosts,
                    args.yes,
                    set(args.keep),
                    set(args.take),
                    sorted(hosts) if source == "inferred" else names,
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
            vendor_names = args.add or args.remove
            if args.add and args.remove:
                refuse("Refused: add and remove are separate runs.")
            if not args.to_version or (not args.from_version and not vendor_names):
                refuse("Refused: a commit needs the installed version and the target version.")
            _print(
                commit_kit(
                    root,
                    args.from_version or args.to_version,
                    args.to_version,
                    args.yes,
                    vendors=vendor_names or None,
                    removing=bool(args.remove),
                    old_root=Path(args.old) if args.old else None,
                    new_root=Path(args.new) if args.new else None,
                )
            )
            return 0
    except Refuse:
        return 2
    refuse("Refused: unknown command.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
