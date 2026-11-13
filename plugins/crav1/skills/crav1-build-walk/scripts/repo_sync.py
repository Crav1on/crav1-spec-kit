#!/usr/bin/env python3
"""Specs-repo sync for the build walk and the ready check (1.151.0).

fetch is read-only. A copy that is behind origin stops before a walk or a
ready check reads or writes; Run next is `git pull --no-rebase` (merge,
never rebase). No upstream, or a failed fetch, is said once and the command
continues. Ahead continues with a Waiting line to push. Diverged stops.

At the end of a walk, settle lists uncommitted files the walk wrote, and
leaves files it did not write uncommitted. A yes then pushes. If the branch
is behind, origin is merged in first (never rebased). A conflict stops and
names the files. After a successful push the ending says the specs repo is
in step with origin. An unpushed branch is a Waiting line.

Usage: repo_sync.py <fetch|status|settle|merge-upstream|commit|push> [options]
The interpreter is crav1-docs/reference/running-scripts.md. The kit wrapper
is scripts/repo-sync.py. This script does not force-push and never rebases.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

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


def emit(payload: dict, status: int = 0) -> int:
    _utf8_stdout()
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")
    return status


def fail(code: str, line: str, status: int = 2, **extra) -> int:
    payload = {"ok": False, "code": code, "line": line}
    payload.update(extra)
    return emit(payload, status)


def git(repo: Path, *args: str, check: bool = False, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=check,
        timeout=timeout,
    )


def find_repo(start: Path) -> Path | None:
    current = Path(start).resolve()
    if current.is_file():
        current = current.parent
    for folder in (current, *current.parents):
        if (folder / ".git").exists():
            return folder
    return None


def _rel(repo: Path, path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


def porcelain(repo: Path) -> list[dict]:
    proc = git(repo, "status", "--porcelain", "-uall")
    rows = []
    for line in (proc.stdout or "").splitlines():
        if not line:
            continue
        code = line[:2]
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        rows.append({"code": code, "path": path, "untracked": code == "??"})
    return rows


def current_branch(repo: Path) -> str | None:
    proc = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    if proc.returncode != 0:
        return None
    name = (proc.stdout or "").strip()
    if not name or name == "HEAD":
        return None
    return name


def upstream_of(repo: Path) -> str | None:
    proc = git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    if proc.returncode != 0:
        return None
    name = (proc.stdout or "").strip()
    return name or None


def ahead_behind(repo: Path, upstream: str) -> tuple[int, int] | None:
    proc = git(repo, "rev-list", "--left-right", "--count", f"HEAD...{upstream}")
    if proc.returncode != 0:
        return None
    parts = (proc.stdout or "").strip().split()
    if len(parts) != 2:
        return None
    return int(parts[0]), int(parts[1])


def pull_ending(why: str = "the specs repo is behind origin; merge, never rebase") -> str:
    return "Run next:\n\n`git pull --no-rebase`\n" + why


def _status_payload(repo: Path, fetched: bool, fetch_error: str | None) -> dict:
    branch = current_branch(repo)
    upstream = upstream_of(repo)
    payload = {
        "ok": True,
        "repo": str(repo),
        "branch": branch,
        "upstream": upstream,
        "fetched": fetched,
        "fetch_error": fetch_error,
        "continue": True,
        "stop": False,
        "state": "in-step",
        "ahead": 0,
        "behind": 0,
        "ending": None,
        "waiting": None,
        "message": None,
    }
    if fetch_error and not fetched:
        payload["state"] = "offline"
        payload["message"] = (
            "The specs repo could not be fetched (offline). Continuing from the local copy."
        )
        payload["line"] = payload["message"]
        return payload
    if not upstream:
        payload["state"] = "no-upstream"
        payload["message"] = "The specs repo has no upstream. Continuing from the local copy."
        payload["line"] = payload["message"]
        return payload
    counts = ahead_behind(repo, upstream)
    if counts is None:
        payload["state"] = "unknown"
        payload["message"] = "The specs repo could not be compared to origin. Continuing from the local copy."
        payload["line"] = payload["message"]
        return payload
    ahead, behind = counts
    payload["ahead"] = ahead
    payload["behind"] = behind
    if behind and ahead:
        payload["state"] = "diverged"
        payload["continue"] = False
        payload["stop"] = True
        payload["message"] = (
            f"The specs repo has diverged from {upstream} "
            f"({ahead} ahead, {behind} behind). Merge origin in, never rebase."
        )
        payload["ending"] = pull_ending(
            f"the specs repo has diverged from {upstream}; merge, never rebase"
        )
        payload["line"] = payload["message"]
        return payload
    if behind:
        payload["state"] = "behind"
        payload["continue"] = False
        payload["stop"] = True
        payload["message"] = (
            f"The specs repo is {behind} commit"
            f"{'s' if behind != 1 else ''} behind {upstream}. Pull before reading."
        )
        payload["ending"] = pull_ending()
        payload["line"] = payload["message"]
        return payload
    if ahead:
        payload["state"] = "ahead"
        payload["waiting"] = (
            f"Waiting: push the specs repo ({ahead} commit"
            f"{'s' if ahead != 1 else ''} ahead of origin)."
        )
        payload["message"] = payload["waiting"]
        payload["line"] = payload["waiting"]
        return payload
    payload["state"] = "in-step"
    payload["message"] = "The specs repo is in step with origin."
    payload["line"] = payload["message"]
    return payload


def fetch_repo(repo: Path) -> tuple[bool, str | None]:
    proc = git(repo, "fetch", "--quiet")
    if proc.returncode == 0:
        return True, None
    err = (proc.stderr or proc.stdout or "git fetch failed").strip().splitlines()
    short = err[-1] if err else "git fetch failed"
    return False, short


def inspect(start: Path, do_fetch: bool = True) -> dict:
    """Fetch (optional) and report the specs repo's relation to origin."""
    repo = find_repo(start)
    if repo is None:
        return {
            "ok": True,
            "state": "no-repo",
            "continue": True,
            "stop": False,
            "repo": None,
            "ending": None,
            "waiting": None,
            "message": None,
            "line": None,
            "ahead": 0,
            "behind": 0,
        }
    fetched = False
    fetch_error = None
    if do_fetch:
        fetched, fetch_error = fetch_repo(repo)
    return _status_payload(repo, fetched, fetch_error)


def settle_lists(repo: Path, written: list[str]) -> dict:
    """Split uncommitted files into walk-written and foreign."""
    wanted = set()
    for item in written:
        text = str(item).strip().replace("\\", "/")
        if not text:
            continue
        path = Path(text)
        if path.is_absolute():
            text = _rel(repo, path)
        wanted.add(text)
    rows = porcelain(repo)
    walk_files = []
    foreign = []
    for row in rows:
        path = row["path"]
        if path in wanted or any(path == item or path.startswith(item.rstrip("/") + "/") for item in wanted):
            walk_files.append(path)
        else:
            foreign.append(path)
    ahead = 0
    upstream = upstream_of(repo)
    if upstream:
        counts = ahead_behind(repo, upstream)
        if counts:
            ahead = counts[0]
    payload = {
        "ok": True,
        "repo": str(repo),
        "branch": current_branch(repo),
        "written": walk_files,
        "foreign": foreign,
        "ahead": ahead,
        "dirty": bool(walk_files or foreign),
        "commit_needed": bool(walk_files),
        "commit_message": "Record the walk in the specs repo",
        "card": {
            "words": ["yes", "stop"],
            "recommended": "yes",
            "action": "commit the walk's files, then push the specs repo",
        },
    }
    if foreign:
        payload["foreign_line"] = "Left uncommitted (not written by this walk): " + ", ".join(foreign)
    if walk_files:
        payload["written_line"] = "Commit: " + ", ".join(walk_files)
    if ahead and not walk_files:
        payload["waiting"] = (
            f"Waiting: push the specs repo ({ahead} commit"
            f"{'s' if ahead != 1 else ''} ahead of origin)."
        )
    return payload


def merge_upstream(repo: Path) -> dict:
    """Merge @{upstream} into HEAD. Never rebase. A conflict names the files."""
    upstream = upstream_of(repo)
    if not upstream:
        return {"ok": False, "code": "no-upstream", "line": "The specs repo has no upstream."}
    fetched, fetch_error = fetch_repo(repo)
    if not fetched:
        return {
            "ok": False,
            "code": "offline",
            "line": f"The specs repo could not be fetched: {fetch_error}",
        }
    proc = git(repo, "merge", "--no-edit", upstream)
    if proc.returncode == 0:
        return {
            "ok": True,
            "merged": True,
            "conflict": False,
            "files": [],
            "line": f"Merged {upstream} into the specs repo.",
        }
    conflicted = git(repo, "diff", "--name-only", "--diff-filter=U")
    files = [line.strip() for line in (conflicted.stdout or "").splitlines() if line.strip()]
    return {
        "ok": False,
        "code": "conflict",
        "conflict": True,
        "merged": False,
        "files": files,
        "line": "Merge conflict in " + (", ".join(files) if files else "the specs repo") + ". Stopped. Nothing was pushed.",
    }


def commit_paths(repo: Path, paths: list[str], message: str) -> dict:
    if not paths:
        return {"ok": True, "committed": False, "sha": None, "line": "Nothing walk-written to commit."}
    for path in paths:
        proc = git(repo, "add", "--", path)
        if proc.returncode != 0:
            return {
                "ok": False,
                "code": "add",
                "line": (proc.stderr or proc.stdout or f"could not add {path}").strip(),
            }
    proc = git(repo, "commit", "-m", message)
    if proc.returncode != 0:
        text = (proc.stderr or proc.stdout or "commit failed").strip()
        if "nothing to commit" in text.lower():
            return {"ok": True, "committed": False, "sha": None, "line": "Nothing walk-written to commit."}
        return {"ok": False, "code": "commit", "line": text}
    sha = git(repo, "rev-parse", "HEAD").stdout.strip()
    return {"ok": True, "committed": True, "sha": sha, "line": f"Committed {sha[:12]}."}


def push_repo(repo: Path) -> dict:
    proc = git(repo, "push")
    if proc.returncode != 0:
        return {
            "ok": False,
            "code": "push",
            "line": (proc.stderr or proc.stdout or "git push failed").strip(),
            "waiting": "Waiting: the specs repo is not pushed.",
        }
    return {
        "ok": True,
        "pushed": True,
        "line": "The specs repo is in step with origin.",
        "ending_note": "The specs repo is in step with origin.",
    }


def _need_yes(args: argparse.Namespace, words: str = "yes and stop") -> int | None:
    if getattr(args, "headless", False) and not getattr(args, "yes", False):
        return fail("headless", f"a headless run stops. The words are {words}.")
    if getattr(args, "need_yes", False) and not getattr(args, "yes", False):
        return fail("yes", f"the words are {words}.")
    return None


def cmd_fetch(args: argparse.Namespace) -> int:
    payload = inspect(Path(args.repo), do_fetch=True)
    return emit(payload, 0 if payload.get("continue") or payload.get("ok") else 1)


def cmd_status(args: argparse.Namespace) -> int:
    payload = inspect(Path(args.repo), do_fetch=not args.no_fetch)
    status = 1 if payload.get("stop") else 0
    return emit(payload, status)


def _written_from(args: argparse.Namespace) -> list[str]:
    items = list(args.written or [])
    if args.written_file:
        text = Path(args.written_file).read_text(encoding="utf-8")
        items.extend(line.strip() for line in text.splitlines() if line.strip())
    return items


def cmd_settle(args: argparse.Namespace) -> int:
    repo = find_repo(Path(args.repo))
    if repo is None:
        return fail("repo", "not a git repository")
    written = _written_from(args)
    payload = settle_lists(repo, written)
    return emit(payload)


def cmd_merge(args: argparse.Namespace) -> int:
    blocked = _need_yes(args)
    if blocked is not None:
        return blocked
    repo = find_repo(Path(args.repo))
    if repo is None:
        return fail("repo", "not a git repository")
    result = merge_upstream(repo)
    return emit(result, 0 if result.get("ok") else 2)


def cmd_commit(args: argparse.Namespace) -> int:
    blocked = _need_yes(args)
    if blocked is not None:
        return blocked
    repo = find_repo(Path(args.repo))
    if repo is None:
        return fail("repo", "not a git repository")
    if not args.yes:
        listed = settle_lists(repo, _written_from(args))
        listed["card"] = {
            "words": ["yes", "stop"],
            "recommended": "yes",
            "action": "commit the walk's files",
        }
        return emit(listed)
    result = commit_paths(repo, _written_from(args), args.message or "Record the walk in the specs repo")
    if result.get("ok"):
        status = inspect(repo, do_fetch=False)
        result["ahead"] = status.get("ahead") or 0
        if result["ahead"]:
            result["waiting"] = (
                f"Waiting: push the specs repo ({result['ahead']} commit"
                f"{'s' if result['ahead'] != 1 else ''} ahead of origin)."
            )
            result["card"] = {
                "words": ["yes", "stop"],
                "recommended": "yes",
                "action": f"push the specs repo ({result['ahead']} commits ahead)"
                if result["ahead"] != 1
                else "push the specs repo (1 commit ahead)",
            }
    return emit(result, 0 if result.get("ok") else 2)


def cmd_push(args: argparse.Namespace) -> int:
    blocked = _need_yes(args)
    if blocked is not None:
        return blocked
    repo = find_repo(Path(args.repo))
    if repo is None:
        return fail("repo", "not a git repository")
    if not args.yes:
        status = inspect(repo, do_fetch=False)
        status["card"] = {
            "words": ["yes", "stop"],
            "recommended": "yes",
            "action": "push the specs repo",
        }
        return emit(status)
    # Behind or diverged: merge first, never rebase.
    status = inspect(repo, do_fetch=True)
    if status.get("state") in ("behind", "diverged"):
        merged = merge_upstream(repo)
        if not merged.get("ok"):
            return emit(merged, 2)
    result = push_repo(repo)
    return emit(result, 0 if result.get("ok") else 2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    for name, func, extra in (
        ("fetch", cmd_fetch, False),
        ("status", cmd_status, True),
    ):
        p = sub.add_parser(name)
        p.add_argument("--repo", required=True)
        if extra:
            p.add_argument("--no-fetch", action="store_true")
        p.set_defaults(func=func)

    s = sub.add_parser("settle")
    s.add_argument("--repo", required=True)
    s.add_argument("--written", nargs="*", default=None)
    s.add_argument("--written-file", default=None)
    s.set_defaults(func=cmd_settle)

    m = sub.add_parser("merge-upstream")
    m.add_argument("--repo", required=True)
    m.add_argument("--yes", action="store_true")
    m.add_argument("--headless", action="store_true")
    m.set_defaults(func=cmd_merge)

    c = sub.add_parser("commit")
    c.add_argument("--repo", required=True)
    c.add_argument("--written", nargs="*", default=None)
    c.add_argument("--written-file", default=None)
    c.add_argument("--message", default=None)
    c.add_argument("--yes", action="store_true")
    c.add_argument("--headless", action="store_true")
    c.set_defaults(func=cmd_commit)

    p = sub.add_parser("push")
    p.add_argument("--repo", required=True)
    p.add_argument("--yes", action="store_true")
    p.add_argument("--headless", action="store_true")
    p.set_defaults(func=cmd_push)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
