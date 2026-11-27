#!/usr/bin/env python3
"""Early-access flags for one repo (1.206.0).

The file is ``.crav1/flags.local.json``. ``.crav1/.gitignore`` lists
``flags.local.json``. The project's ``.gitignore`` is not changed.

Known flags are ``REGISTRY``. Each entry has a one-line description and a
status of ``experimental`` or ``beta``. ``kit2`` is the first entry.

Words, on ``update_kit.py``: ``flags-list``, ``flags-on <flag> [<flag> ...]``,
``flags-off <flag> [<flag> ...]``. An unknown name is refused in one line
that names the known flags. Known names in that command are still applied.
A flag already stored that this registry does not know is kept and reported.
A file that cannot be read is one plain line, and an update continues with
no flags.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

FLAG_REL = ".crav1/flags.local.json"
IGNORE_REL = ".crav1/.gitignore"
IGNORE_LINE = "flags.local.json"
RECORD_REL = ".crav1-2/installed.json"
MALFORMED = "Flags file .crav1/flags.local.json is not readable; continuing with no flags."
OFFER = "Kit 2.0: uninstall offered; uninstall-kit2 removes only the listed files, keep-kit2 leaves them."
STATUSES = ("experimental", "beta")

# Documented registry. kit2 is the first entry.
REGISTRY: dict[str, dict[str, str]] = {
    "kit2": {
        "description": "Install kit 2.0 at user level from the same release when this repo is updated.",
        "status": "experimental",
    },
}


def _utf8() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


_utf8()


class FlagState:
    def __init__(self, present: bool, malformed: bool, message: str | None, values: dict[str, bool]):
        self.present = present
        self.malformed = malformed
        self.message = message
        self.values = values


def read_flags(root: Path) -> FlagState:
    """Read the flag file. A missing file is not an error and not malformed."""
    path = Path(root) / FLAG_REL
    if not path.exists():
        return FlagState(False, False, None, {})
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return FlagState(True, True, MALFORMED, {})
    if not isinstance(data, dict) or any(not isinstance(key, str) or not isinstance(value, bool) for key, value in data.items()):
        return FlagState(True, True, MALFORMED, {})
    return FlagState(True, False, None, dict(data))


def known_names(registry: dict | None = None) -> list[str]:
    return sorted(registry if registry is not None else REGISTRY)


def unknown_names(values: dict[str, bool], registry: dict | None = None) -> list[str]:
    known = registry if registry is not None else REGISTRY
    return sorted(name for name in values if name not in known)


def refusal_line(names: list[str], registry: dict | None = None) -> str:
    if len(names) == 1:
        shown, verb = names[0], "is not a known flag"
    else:
        shown, verb = ", ".join(names[:-1]) + " and " + names[-1], "are not known flags"
    known = ", ".join(known_names(registry))
    return f"Refused: {shown} {verb}. Known flags: {known}."


def banner(root: Path) -> str | None:
    """``Flags:`` line, the malformed line, or None when the file is absent."""
    state = read_flags(root)
    if not state.present:
        return None
    if state.malformed:
        return state.message
    names = sorted(name for name, on in state.values.items() if on)
    return "Flags: " + (", ".join(names) if names else "none")


def seed_worktree(repo: Path, worktree: Path) -> None:
    """Copy the flag file into a temp worktree. A missing file copies nothing."""
    src = Path(repo) / FLAG_REL
    if not src.is_file():
        return
    dest = Path(worktree) / FLAG_REL
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())


def _newline(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def ensure_ignore(root: Path) -> bool:
    """List ``flags.local.json`` in ``.crav1/.gitignore``. Return True when the file changes.

    An existing ``*`` line is kept. The project's ``.gitignore`` is not opened.
    """
    path = Path(root) / IGNORE_REL
    if path.is_file():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            text = ""
        rows = [row.strip() for row in text.splitlines()]
        if IGNORE_LINE in rows:
            return False
        nl = _newline(text)
        body = text
        if body and not body.endswith(("\n", "\r")):
            body += nl
        path.write_text(body + IGNORE_LINE + nl, encoding="utf-8")
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(IGNORE_LINE + "\n", encoding="utf-8")
    return True


def _dump(values: dict[str, bool]) -> str:
    return json.dumps(values, indent=2, sort_keys=True) + "\n"


def _write_flags(root: Path, values: dict[str, bool]) -> bool:
    path = Path(root) / FLAG_REL
    text = _dump(values)
    path.parent.mkdir(parents=True, exist_ok=True)
    current = path.read_text(encoding="utf-8") if path.is_file() else None
    if current == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def _on_word(value: bool) -> str:
    return "on" if value else "off"


def _sentence(line: str) -> str:
    return line if line.endswith(".") else line + "."


def _change_line(before: dict[str, bool], after: dict[str, bool], names: list[str]) -> str:
    parts = []
    for name in names:
        parts.append(f"{name}: {_on_word(bool(before.get(name)))} -> {_on_word(bool(after.get(name)))}")
    return ", ".join(parts)


def _print(payload: dict) -> None:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def set_flags(root: Path, names: list[str], on: bool, registry: dict | None = None, home: Path | None = None) -> dict:
    """Set known names. Unknown names are listed and not stored. Stored unknown keys stay."""
    table = registry if registry is not None else REGISTRY
    state = read_flags(root)
    before = {} if state.malformed else dict(state.values)
    refused = [name for name in names if name not in table]
    accepted: list[str] = []
    seen: set[str] = set()
    for name in names:
        if name in table and name not in seen:
            accepted.append(name)
            seen.add(name)
    accepted.sort()
    after = dict(before)
    for name in accepted:
        after[name] = on
    wrote: list[str] = []
    if accepted:
        if ensure_ignore(root):
            wrote.append(IGNORE_REL)
        if _write_flags(root, after):
            wrote.append(FLAG_REL)
        elif not (Path(root) / FLAG_REL).is_file():
            _write_flags(root, after)
            wrote.append(FLAG_REL)
    unknown = unknown_names(after, table)
    line = _change_line(before, after, accepted) if accepted else "No known flag was applied."
    if unknown:
        line = f"{_sentence(line)} Unknown flag kept: {', '.join(unknown)}."
    payload: dict = {
        "flags": after,
        "line": line,
        "malformed": state.malformed,
        "refused": refused,
        "unknown_kept": unknown,
        "wrote": wrote,
    }
    if "kit2" in accepted and on is False and _record_exists(home):
        payload["kit2_line"] = OFFER
        payload["line"] = f"{_sentence(line)} {OFFER}"
    return payload


def _record_exists(home: Path | None) -> bool:
    base = Path.home() if home is None else Path(home)
    return (base / RECORD_REL).is_file()


def list_flags(root: Path, registry: dict | None = None) -> dict:
    table = registry if registry is not None else REGISTRY
    state = read_flags(root)
    values = {} if state.malformed or not state.present else state.values
    unknown = [] if state.malformed else unknown_names(values, table)
    rows = []
    for name in known_names(table):
        row = table[name]
        rows.append({
            "description": row.get("description", ""),
            "name": name,
            "on": bool(values.get(name)),
            "status": row.get("status", ""),
        })
    if not state.present or state.malformed:
        line = "No early-access flags are set."
    else:
        parts = [f"{row['name']}: {_on_word(row['on'])} ({row['status']})" for row in rows]
        line = ", ".join(parts) if parts else "No early-access flags are set."
        if unknown:
            line = f"{_sentence(line)} Unknown flag kept: {', '.join(unknown)}."
    return {
        "file": FLAG_REL,
        "flags": values,
        "line": line,
        "malformed": state.malformed,
        "present": state.present and not state.malformed,
        "registry": rows,
        "unknown_kept": unknown,
    }


def _install_script(new_root: Path | None, home: Path) -> Path | None:
    if new_root is not None:
        candidate = Path(new_root) / "v2" / "install.py"
        if candidate.is_file():
            return candidate
    installed = Path(home) / ".crav1-2" / "install.py"
    if installed.is_file():
        return installed
    return None


def _run_install(script: Path, home: Path, words: list[str]) -> tuple[int, str, str]:
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    try:
        proc = subprocess.run(
            [sys.executable, "-X", "utf8", str(script), "--home", str(home), *words],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return 1, "", f"{type(exc).__name__}: {exc}"
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def _one_line(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return fallback


def _kit2_result(new_root: Path, home: Path, dry: bool) -> str:
    script = Path(new_root) / "v2" / "install.py"
    if not script.is_file():
        return "Kit 2.0: v2/install.py was not in this release."
    updating = _record_exists(home)
    words = ["install", "dry-run"] if dry else ["install"]
    code, out, err = _run_install(script, home, words)
    if code != 0:
        return "Kit 2.0: " + _one_line(err or out, "install failed.")
    try:
        payload = json.loads(out)
    except json.JSONDecodeError:
        return "Kit 2.0: install returned no record."
    version = payload.get("version") or "2.0"
    count = len(payload.get("files") or [])
    if dry:
        return f"Kit 2.0: dry-run {version}, {count} files."
    verb = "updated" if updating else "installed"
    return f"Kit 2.0: {verb} {version} at user level, {count} files."


def early_access(root: Path, new_root: Path, home: Path, dry: bool) -> tuple[str | None, dict]:
    """Extra JSON for plan or apply. Empty when the output must match a run with no flag file.

    The first item is the one plain line for a file that cannot be read, else None.
    """
    state = read_flags(root)
    if not state.present:
        return None, {}
    if state.malformed:
        return state.message, {}
    extra: dict = {}
    unknown = unknown_names(state.values)
    if unknown:
        extra["unknown_flags"] = unknown
    if state.values.get("kit2") is True:
        extra["kit2_line"] = _kit2_result(new_root, home, dry)
    elif state.values.get("kit2") is False and _record_exists(home):
        extra["kit2_line"] = OFFER
    return None, extra


def uninstall_kit2(new_root: Path | None, home: Path, yes: bool) -> dict:
    """Offer, or with yes remove only the files the install record lists."""
    if not _record_exists(home):
        return {"kit2_line": "Kit 2.0: nothing to uninstall.", "removed": []}
    if not yes:
        return {"kit2_line": OFFER, "removed": []}
    script = _install_script(new_root, home)
    if script is None:
        return {"kit2_line": "Kit 2.0: v2/install.py was not in this release.", "removed": []}
    code, out, err = _run_install(script, home, ["uninstall"])
    if code != 0:
        return {"kit2_line": "Kit 2.0: " + _one_line(err or out, "uninstall failed."), "removed": []}
    try:
        payload = json.loads(out)
    except json.JSONDecodeError:
        return {"kit2_line": "Kit 2.0: uninstall returned no record.", "removed": []}
    removed = payload.get("deleted") if isinstance(payload.get("deleted"), list) else []
    return {"kit2_line": f"Kit 2.0: uninstalled {len(removed)} listed files.", "removed": removed}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description="Set or list early-access flags for this repo.")
    parser.add_argument("command", choices=["flags-list", "flags-on", "flags-off", "uninstall-kit2"])
    parser.add_argument("names", nargs="*")
    parser.add_argument("--root", default=".")
    parser.add_argument("--home", default=None)
    parser.add_argument("--new", default=None)
    parser.add_argument("--yes", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code in (0, None):
            return 0
        print("Refused: words are flags-list, flags-on <flag>, flags-off <flag>, and uninstall-kit2.", file=sys.stderr)
        return 2
    root = Path(args.root).resolve()
    home = Path(args.home).expanduser().resolve() if args.home else None
    new_root = Path(args.new).expanduser().resolve() if args.new else None
    if args.command == "flags-list":
        if args.names:
            print("Refused: flags-list takes no flag names.", file=sys.stderr)
            return 2
        state = read_flags(root)
        if state.malformed and state.message:
            print(state.message, file=sys.stderr)
        _print(list_flags(root))
        return 0
    if args.command == "uninstall-kit2":
        if args.names:
            print("Refused: uninstall-kit2 takes no flag names.", file=sys.stderr)
            return 2
        _print(uninstall_kit2(new_root, home if home is not None else Path.home(), args.yes))
        return 0
    if not args.names:
        print(f"Refused: name at least one flag. Known flags: {', '.join(known_names())}.", file=sys.stderr)
        return 2
    state = read_flags(root)
    if state.malformed and state.message:
        print(state.message, file=sys.stderr)
    on = args.command == "flags-on"
    payload = set_flags(root, args.names, on, home=home if home is not None else Path.home())
    _print(payload)
    if payload["refused"]:
        print(refusal_line(payload["refused"]), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
