#!/usr/bin/env python3
"""Install kit 2.0 next to 1.x, at user level. Words: install, uninstall, status, dry-run.

--home is an internal test hook. It is not a user-facing option.
The installer never writes a project's sot/ or .crav1-2/events.jsonl.
Codex is skipped: 1.x installs Codex into the project .agents/skills/ tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ENGINE = "2.0.0-alpha.4"
MIN_1X = (1, 205, 0)
CODEX_NOTE = (
    "skipped: 1.x Codex install writes project .agents/skills/ and has no user-level skills path"
)
PROTECTED_EXACT = {
    ".crav1-2/events.jsonl",
    ".crav1-2/.gitattributes",
    ".crav1-2/engine.json",
}


def _utf8() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(encoding="utf-8")
        except (AttributeError, OSError, ValueError):
            pass


def source_root() -> Path:
    here = Path(__file__).resolve().parent
    if (here / "crav1_2" / "version.py").is_file() and (here / "skills" / "crav1-2-help" / "SKILL.md").is_file():
        return here
    raise SystemExit("Refused: run install from the kit v2/ directory.")


def payloads(root: Path) -> list[tuple[str, bytes]]:
    files: list[tuple[str, bytes]] = []
    for path in sorted((root / "crav1_2").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = Path(".crav1-2") / "engine" / path.relative_to(root)
        files.append((rel.as_posix(), path.read_bytes()))
    files.append((".crav1-2/install.py", (root / "install.py").read_bytes()))
    plugin = (root / "cursor-plugin" / "plugin.json").read_bytes()
    files.append((".cursor/plugins/local/crav1-2/.cursor-plugin/plugin.json", plugin))
    skills_root = root / "skills"
    for skill in sorted(path for path in skills_root.iterdir() if path.is_dir() and path.name.startswith("crav1-2-")):
        for path in sorted(item for item in skill.rglob("*") if item.is_file()):
            rel = path.relative_to(skill).as_posix()
            data = path.read_bytes()
            files.append((f".cursor/plugins/local/crav1-2/skills/{skill.name}/{rel}", data))
            files.append((f".claude/skills/{skill.name}/{rel}", data))
    agents = root / "agents"
    if agents.is_dir():
        for path in sorted(agents.glob("crav1-2-*.md")):
            data = path.read_bytes()
            files.append((f".cursor/plugins/local/crav1-2/agents/{path.name}", data))
            files.append((f".claude/agents/{path.name}", data))
    return files


def _parse_version(value: str | None) -> tuple[int, int, int] | None:
    if not value:
        return None
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", value.strip())
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def one_x_installs(home: Path) -> list[dict]:
    """1.x plugin.json and the Claude user kit record. crav1-2 is not 1.x."""
    found = []
    plugins = home / ".cursor" / "plugins"
    if plugins.is_dir():
        for path in sorted(plugins.rglob("plugin.json")):
            if path.parent.name != ".cursor-plugin" or path.parent.parent.name != "crav1":
                continue
            item = {"path": _safe_rel(home, path), "version": None, "parsed": None}
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                item["error"] = "unreadable"
                found.append(item)
                continue
            version = data.get("version") if isinstance(data, dict) else None
            item["version"] = version if isinstance(version, str) else None
            item["parsed"] = _parse_version(item["version"])
            if item["parsed"] is None:
                item["error"] = "unreadable"
            found.append(item)
    workflow = home / ".claude" / "skills" / "crav1-docs" / "reference" / "workflow.md"
    changelog = home / ".claude" / "skills" / "crav1-docs" / "CHANGELOG.md"
    record = workflow if workflow.is_file() else changelog if changelog.is_file() else None
    if record is not None:
        item = {"path": _safe_rel(home, record), "version": None, "parsed": None}
        try:
            text = record.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            item["error"] = "unreadable"
            found.append(item)
        else:
            if record.name == "workflow.md":
                match = re.search(r"^Kit version:\s*v?(\d+\.\d+\.\d+)\s*$", text, re.M)
            else:
                match = re.search(r"^##\s+v?(\d+\.\d+\.\d+)\b", text, re.M)
            if match:
                item["version"] = match.group(1)
                item["parsed"] = _parse_version(match.group(1))
            if item["parsed"] is None:
                item["error"] = "unreadable"
            found.append(item)
    return found


def _safe_rel(home: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(home.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def one_x_block(installs: list[dict]) -> dict:
    if not installs:
        return {
            "found": False,
            "ok": True,
            "note": "No installed 1.x kit was found. Install is allowed.",
            "installs": [],
        }
    problems = []
    for item in installs:
        parsed = item.get("parsed")
        if parsed is None or parsed < MIN_1X:
            label = item.get("version") or "unreadable"
            problems.append(f"{label} at {item['path']}")
    return {
        "found": True,
        "ok": not problems,
        "minimum": "1.205.0",
        "installs": [
            {"path": item["path"], "version": item.get("version"), "ok": item.get("parsed") is not None and item["parsed"] >= MIN_1X}
            for item in installs
        ],
        "note": None if not problems else "installed 1.x is older than 1.205.0: " + ", ".join(problems),
    }


def _refuse_old(block: dict) -> None:
    if block["found"] and not block["ok"]:
        raise SystemExit(
            "Refused: installed 1.x is older than 1.205.0 (" + block["note"].split(": ", 1)[-1] + "). Update 1.x before installing 2.0."
        )


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _record_path(home: Path) -> Path:
    return home / ".crav1-2" / "installed.json"


def _now() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def _protected(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    if rel == "sot" or rel.startswith("sot/"):
        return True
    if rel in PROTECTED_EXACT or rel.startswith(".crav1-2/sessions/"):
        return True
    return False


def _under(home: Path, path: Path) -> bool:
    try:
        resolved = path.resolve()
        root = home.resolve()
    except OSError:
        return False
    return resolved == root or root in resolved.parents


def _load_record(home: Path) -> dict | None:
    path = _record_path(home)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit("Refused: ~/.crav1-2/installed.json is not readable.") from exc
    if not isinstance(data, dict) or not isinstance(data.get("files"), dict):
        raise SystemExit("Refused: ~/.crav1-2/installed.json is not a file list.")
    return data


def _write_record(home: Path, files: dict[str, str]) -> None:
    body = {
        "version": ENGINE,
        "engine": ENGINE,
        "installed_at": _now(),
        "codex": CODEX_NOTE,
        "files": files,
    }
    path = _record_path(home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(body, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def _prune(home: Path, rels: list[str]) -> None:
    """Remove empty directories that held installed files. Never remove home, .cursor, or .claude."""
    stop = {home.resolve()}
    for name in (".cursor", ".claude"):
        candidate = home / name
        if candidate.exists():
            stop.add(candidate.resolve())
    for rel in rels:
        folder = (home / rel).parent
        while True:
            try:
                resolved = folder.resolve()
            except OSError:
                break
            if resolved in stop or folder == home:
                break
            rel_folder = folder.relative_to(home).as_posix()
            if _protected(rel_folder) or not folder.is_dir() or folder.is_symlink() or any(folder.iterdir()):
                break
            parent = folder.parent
            try:
                folder.rmdir()
            except OSError:
                break
            folder = parent
    engine = home / ".crav1-2" / "engine"
    crav = home / ".crav1-2"
    for folder in (engine / "crav1_2", engine, crav):
        if folder.is_dir() and not folder.is_symlink() and not any(folder.iterdir()):
            try:
                folder.rmdir()
            except OSError:
                pass


def install(home: Path, dry_run: bool) -> dict:
    block = one_x_block(one_x_installs(home))
    _refuse_old(block)
    files = payloads(source_root())
    listed = [rel for rel, _data in files]
    if any(_protected(rel) for rel in listed):
        raise SystemExit("Refused: the install list includes project SoT state.")
    result = {
        "action": "install",
        "dry_run": dry_run,
        "version": ENGINE,
        "codex": CODEX_NOTE,
        "one_x": block,
        "files": listed,
    }
    if dry_run:
        return result
    home.mkdir(parents=True, exist_ok=True)
    written = {}
    for rel, data in files:
        path = home / rel
        if not _under(home, path.parent if path.parent.exists() else home):
            raise SystemExit(f"Refused: {rel} is outside the home directory.")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        if not _under(home, path):
            path.unlink(missing_ok=True)
            raise SystemExit(f"Refused: {rel} is outside the home directory.")
        written[rel] = _digest(data)
    _write_record(home, written)
    result["installed"] = True
    return result


def _changed(path: Path, digest: str) -> bool:
    if not path.is_file():
        return False
    return hashlib.sha256(path.read_bytes()).hexdigest() != digest


def status(home: Path) -> dict:
    record = _load_record(home)
    block = one_x_block(one_x_installs(home))
    if record is None:
        return {
            "action": "status",
            "installed": False,
            "version": None,
            "codex": CODEX_NOTE,
            "one_x": block,
            "changed": [],
        }
    changed = []
    for rel, digest in sorted(record["files"].items()):
        path = home / rel
        if path.is_file() and _changed(path, digest):
            changed.append(rel)
    return {
        "action": "status",
        "installed": True,
        "version": record.get("version"),
        "codex": record.get("codex") or CODEX_NOTE,
        "one_x": block,
        "changed": changed,
        "files": len(record["files"]),
    }


def uninstall(home: Path, dry_run: bool) -> dict:
    record = _load_record(home)
    if record is None:
        raise SystemExit("Refused: kit 2.0 is not installed.")
    deleted = []
    kept = []
    for rel, digest in sorted(record["files"].items()):
        if _protected(rel):
            kept.append({"path": rel, "reason": "protected"})
            continue
        path = home / rel
        if not path.is_file():
            continue
        if not _under(home, path):
            kept.append({"path": rel, "reason": "outside home"})
            continue
        if _changed(path, digest):
            kept.append({"path": rel, "reason": "hash differs"})
            continue
        if not dry_run:
            path.unlink()
        deleted.append(rel)
    if not dry_run:
        if kept:
            remaining = {item["path"]: record["files"][item["path"]] for item in kept if item["path"] in record["files"]}
            _write_record(home, remaining)
        else:
            record_path = _record_path(home)
            if record_path.is_file():
                record_path.unlink()
        _prune(home, deleted)
    return {
        "action": "uninstall",
        "dry_run": dry_run,
        "codex": CODEX_NOTE,
        "deleted": deleted,
        "kept": kept,
    }


def _emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    _utf8()
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--home", default=None)
    parser.add_argument("words", nargs="*")
    try:
        args, unknown = parser.parse_known_args(argv)
    except SystemExit:
        print("Refused: words are install, uninstall, status, and dry-run.", file=sys.stderr)
        return 2
    if unknown:
        print("Refused: words are install, uninstall, status, and dry-run.", file=sys.stderr)
        return 2
    words = args.words
    if not words or words[0] not in {"install", "uninstall", "status"}:
        print("Refused: words are install, uninstall, status, and dry-run.", file=sys.stderr)
        return 2
    dry = False
    if len(words) == 2 and words[1] == "dry-run" and words[0] in {"install", "uninstall"}:
        dry = True
    elif len(words) != 1 or words[0] == "dry-run":
        print("Refused: say install, uninstall, status, or install dry-run, or uninstall dry-run.", file=sys.stderr)
        return 2
    home = Path(args.home).expanduser() if args.home else Path.home()
    try:
        if words[0] == "install":
            _emit(install(home, dry))
        elif words[0] == "status":
            _emit(status(home))
        else:
            _emit(uninstall(home, dry))
    except SystemExit as exc:
        message = exc.args[0] if exc.args else "Refused."
        if isinstance(message, int):
            return message
        print(message, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
