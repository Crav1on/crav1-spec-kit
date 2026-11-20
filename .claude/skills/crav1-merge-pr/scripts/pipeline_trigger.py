#!/usr/bin/env python3
"""Which pipeline files trigger on a merge into a branch (1.199.0). Read-only.

    pipeline_trigger.py check --repo <code checkout> --branch <base> [--path <changed file> ...]

A merge card names a deploy or pipeline side effect only when this finds a
pipeline file whose trigger covers the base branch (and, when the file lists
trigger paths and --path is given, one of the changed paths). It reads
Azure Pipelines YAML (`trigger:` branches and paths, `trigger: none`) and
GitHub workflows (`on: push: branches/paths`). It cannot see whether a
pipeline is turned on in the host, so the card says "has a trigger in
<file>", never that a deploy starts. No file found: say nothing.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
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


SKIP_DIRS = {".git", "node_modules", "bin", "obj", ".venv", "venv"}


def pipeline_files(repo: Path) -> list[Path]:
    out = []
    for path in sorted(repo.rglob("*.y*ml")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        rel = path.relative_to(repo).as_posix()
        if rel.startswith(".github/workflows/"):
            out.append(path)
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if re.search(r"^(trigger|pr|stages|jobs|steps)\s*:", text, re.M) and re.search(r"^trigger\s*:", text, re.M):
            out.append(path)
    return out


def _block(text: str, key: str) -> list[str]:
    """The indented lines under a top-level `key:` (or its inline value as one line)."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(rf"^{re.escape(key)}\s*:\s*(.*)$", line)
        if not m:
            continue
        rest = m.group(1).strip()
        body = [rest] if rest else []
        for nxt in lines[i + 1:]:
            if nxt.strip() and not nxt.startswith((" ", "\t", "-")):
                break
            body.append(nxt)
        return body
    return []


def _list_under(lines: list[str], name: str) -> list[str] | None:
    """Items of `name:` (with an optional `include:`) inside a block; None when absent."""
    found = None
    capture = False
    indent = None
    for line in lines:
        stripped = line.strip()
        if re.match(rf"^{name}\s*:", stripped):
            found = []
            inline = stripped.split(":", 1)[1].strip()
            if inline.startswith("["):
                return [x.strip().strip("'\"") for x in inline.strip("[]").split(",") if x.strip()]
            capture, indent = True, len(line) - len(line.lstrip())
            continue
        if capture:
            if not stripped:
                continue
            cur = len(line) - len(line.lstrip())
            if stripped.startswith("exclude"):
                capture = False
                continue
            if stripped.startswith("include"):
                continue
            if cur <= indent and not stripped.startswith("-"):
                capture = False
                continue
            if stripped.startswith("- "):
                found.append(stripped[2:].strip().strip("'\""))
    return found


def _match(value: str, patterns: list[str]) -> bool:
    value = value.removeprefix("refs/heads/")
    return any(fnmatch.fnmatch(value, p.removeprefix("refs/heads/")) for p in patterns)


def triggers(path: Path, rel: str, branch: str, changed: list[str]) -> dict | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if rel.startswith(".github/workflows/"):
        on = _block(text, "on")
        if not on:
            return None
        flat = " ".join(on)
        if "push" not in flat:
            return None
        branches = _list_under(on, "branches")
        paths = _list_under(on, "paths")
    else:
        block = _block(text, "trigger")
        if not block:
            return {"file": rel, "why": f"no trigger section, so every push to {branch} runs it"}
        if block[0].strip().lower() == "none":
            return None
        if block[0].strip().startswith("-") or block[0].strip().startswith("["):
            inline = block[0].strip()
            branches = ([x.strip().strip("'\"") for x in inline.strip("[]").split(",")] if inline.startswith("[")
                        else [line.strip()[2:].strip() for line in block if line.strip().startswith("- ")])
            paths = None
        else:
            branches = _list_under(block, "branches")
            paths = _list_under(block, "paths")
    if branches is not None and not _match(branch, branches):
        return None
    if paths and changed and not any(_match(c, paths) or any(c.startswith(p.rstrip("*").rstrip("/") + "/") for p in paths) for c in changed):
        return None
    why = f"its trigger covers {branch}" + (" and the changed paths" if paths and changed else "")
    return {"file": rel, "why": why}


def check(repo: Path, branch: str, changed: list[str] | None = None) -> dict:
    changed = changed or []
    found = []
    for path in pipeline_files(repo):
        rel = path.relative_to(repo).as_posix()
        hit = triggers(path, rel, branch, changed)
        if hit:
            found.append(hit)
    if not found:
        return {"ok": True, "triggered": [], "line": None,
                "note": "No pipeline file triggers on this merge; the card names no deploy or pipeline."}
    names = ", ".join(item["file"] for item in found)
    return {"ok": True, "triggered": found,
            "line": f"Merging into {branch} matches the trigger in {names}; whether that pipeline is turned on is not checked here."}


def main(argv: list[str] | None = None) -> int:
    _utf8_stdout()
    parser = argparse.ArgumentParser(description="Pipeline files that trigger on a merge (read-only).")
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--repo", required=True)
    c.add_argument("--branch", required=True)
    c.add_argument("--path", action="append", default=[])
    args = parser.parse_args(argv)
    json.dump(check(Path(args.repo), args.branch, args.path), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
