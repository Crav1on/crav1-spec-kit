"""Engine command line. Words only; the project is the working directory, or `repo <path>`."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from crav1_2.errors import EngineError
from crav1_2.events import load_jsonl
from crav1_2.lines import one_x_lines_unchanged, owned_mark_lines
from crav1_2.lint import lint_repo
from crav1_2.repo import append_events, init_repo, rebuild_views, record_session, show_state
from crav1_2.schema import validate_event

WORDS = (
    "init",
    "append",
    "show-state",
    "rebuild-views",
    "lint",
    "check-lines",
    "session-open",
    "session-park",
    "session-end",
)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        return _main(argv)
    except EngineError as exc:
        print(exc.message, file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Refused: not a JSON object ({exc.msg}).", file=sys.stderr)
        return 2


def _main(argv: list[str]) -> int:
    if not argv or argv[0] in {"help"}:
        _usage()
        return 0 if argv and argv[0] == "help" else 2
    if any(arg.startswith("-") for arg in argv):
        print("Refused: options are words, not flags. " + _word_list(), file=sys.stderr)
        return 2
    command = argv[0]
    if command not in WORDS:
        print("Refused: unknown command. " + _word_list(), file=sys.stderr)
        return 2
    if command == "check-lines":
        return _check_lines(argv[1:])
    args, repo = _take_repo(argv[1:])
    if command == "init":
        if args:
            raise EngineError("Refused: init takes no other words.")
        _emit(init_repo(repo))
        return 0
    if command == "append":
        if args:
            raise EngineError("Refused: append reads JSON from stdin.")
        _emit(append_events(repo, _stdin_events()))
        return 0
    if command == "show-state":
        if args:
            raise EngineError("Refused: show-state takes no other words.")
        _emit(show_state(repo))
        return 0
    if command == "rebuild-views":
        if args:
            raise EngineError("Refused: rebuild-views takes no other words.")
        _emit(rebuild_views(repo))
        return 0
    if command == "lint":
        if args:
            raise EngineError("Refused: lint takes no other words.")
        findings = lint_repo(repo)
        _emit({"ok": not findings, "findings": findings})
        return 1 if findings else 0
    status = {"session-open": "open", "session-park": "parked", "session-end": "ended"}[command]
    if len(args) != 1:
        raise EngineError(f"Refused: {command} takes a session id.")
    _emit(record_session(repo, args[0], status))
    return 0


def _check_lines(args: list[str]) -> int:
    if len(args) != 2:
        raise EngineError("Refused: check-lines takes the before file and the after file.")
    before = Path(args[0]).read_text(encoding="utf-8")
    after = Path(args[1]).read_text(encoding="utf-8")
    unchanged = one_x_lines_unchanged(before, after)
    marks = owned_mark_lines(after)
    ok = unchanged and not marks
    _emit({"ok": ok, "unchanged": unchanged, "marks": marks})
    return 0 if ok else 1


def _stdin_events() -> list[dict]:
    if sys.stdin.isatty():
        raise EngineError("Refused: append reads JSON from stdin.")
    text = sys.stdin.read()
    stripped = text.strip()
    if not stripped:
        raise EngineError("Refused: append reads JSON from stdin.")
    try:
        raw = json.loads(stripped)
    except json.JSONDecodeError:
        raw = None
    if isinstance(raw, dict):
        return [validate_event(raw)]
    if isinstance(raw, list):
        raise EngineError("Refused: append one JSON object per line, not a JSON array.")
    return load_jsonl(text if text.endswith("\n") else text + "\n")


def _take_repo(args: list[str]) -> tuple[list[str], Path]:
    if len(args) >= 2 and args[-2] == "repo":
        return args[:-2], Path(args[-1])
    if "repo" in args:
        raise EngineError("Refused: repo <path> comes last.")
    return args, Path.cwd()


def _emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _word_list() -> str:
    return "Words: " + ", ".join(WORDS) + "."


def _usage() -> None:
    print(
        "crav1-2 engine (alpha). Words: " + ", ".join(WORDS) + ".\n"
        "The project is the working directory. Add `repo <path>` at the end to point elsewhere.\n"
        "append reads one JSON object, or one object per line, from stdin.",
        file=sys.stderr,
    )
