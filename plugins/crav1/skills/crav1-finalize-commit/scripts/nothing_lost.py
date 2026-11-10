#!/usr/bin/env python3
"""Nothing-lost check for /crav1-finalize-commit (kit 1.123.0).

For a merge, every line either parent added to a kit file must still be in
the merge, in HEAD, or in the working tree. Say nothing was lost only when
this script prints "nothing_lost": true.

Kit files: docs/specs/**/spec.md, docs/architecture/spec.md, docs/system/*.md,
and docs/notes/**.

Not lost: a note index line when notes_index.py --check passes, a Synced at
line replaced by a newer one for the same repo and branch, and an old
"; "-joined Synced at or Branch line whose entries are all kept.

Usage (JSON on stdout):
  nothing_lost.py --root <repo>                 merge in progress (MERGE_HEAD)
  nothing_lost.py --root <repo> --merge <sha>   a merge commit

Exit 0 when nothing was lost, 1 when a line was lost, 2 when this is not a merge.
Standard library only.
"""

from __future__ import annotations

import argparse
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

sys.dont_write_bytecode = True

SLICE_SYNCED = re.compile(
    r"^Synced at:\s+(\S+)\s+(\S+)@([0-9a-fA-F]+),\s*(\d{4}-\d{2}-\d{2})"
)
REPO_SYNCED = re.compile(
    r"^-\s+(\S+)\s+(\S+)@([0-9a-fA-F]+),\s*(\d{4}-\d{2}-\d{2})"
)


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def fail(code: str, message: str, status: int = 2) -> None:
    json.dump({"ok": False, "nothing_lost": False, "code": code, "message": message}, sys.stdout)
    sys.stdout.write("\n")
    raise SystemExit(status)


def emit(payload: dict, status: int) -> None:
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")
    raise SystemExit(status)


def is_kit(path: str) -> bool:
    if path == "docs/architecture/spec.md":
        return True
    if path.startswith("docs/specs/") and path.endswith("/spec.md"):
        return True
    if path.startswith("docs/system/") and "/" not in path[len("docs/system/"):] and path.endswith(".md"):
        return True
    if path.startswith("docs/notes/"):
        return True
    return False


def is_index(path: str) -> bool:
    return path == "docs/notes/index.md" or (
        path.startswith("docs/notes/") and path.endswith("/index.md")
    )


def notes_index_script() -> Path | None:
    sibling = Path(__file__).resolve().parents[2] / "crav1-add-to-spec" / "scripts" / "notes_index.py"
    return sibling if sibling.is_file() else None


def index_check(root: Path, script: Path | None) -> str:
    if script is None:
        return "not-run"
    proc = subprocess.run(
        [sys.executable, str(script), "--check", "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    return "pass" if proc.returncode == 0 else "fail"


def merge_parents(root: Path, merge: str | None) -> tuple[str, str, str | None]:
    """Return ours, theirs, and the merge sha when the merge is already committed.

    During a merge, the merge sha is None and the working tree is the merge.
    """
    if merge:
        proc = git(root, "rev-parse", f"{merge}^1", f"{merge}^2")
        if proc.returncode != 0:
            fail("not-a-merge", f"{merge} is not a merge commit")
        parents = proc.stdout.split()
        if len(parents) != 2:
            fail("not-a-merge", f"{merge} is not a merge commit")
        shown = git(root, "rev-parse", merge)
        if shown.returncode != 0:
            fail("not-a-merge", f"cannot resolve {merge}")
        return parents[0], parents[1], shown.stdout.strip()
    head = git(root, "rev-parse", "--git-path", "MERGE_HEAD")
    if head.returncode != 0:
        fail("not-a-merge", "no merge in progress and no --merge commit")
    path = Path(head.stdout.strip())
    if not path.is_absolute():
        path = root / head.stdout.strip()
    if not path.is_file():
        fail("not-a-merge", "no merge in progress and no --merge commit")
    ours = git(root, "rev-parse", "HEAD")
    theirs = git(root, "rev-parse", "MERGE_HEAD")
    if ours.returncode != 0 or theirs.returncode != 0:
        fail("not-a-merge", "cannot read the merge parents")
    return ours.stdout.strip(), theirs.stdout.strip(), None


def added_lines(root: Path, base: str, parent: str, path: str) -> list[str]:
    proc = git(root, "diff", "-U0", "--ignore-cr-at-eol", base, parent, "--", path)
    if proc.returncode != 0:
        return []
    lines = []
    for line in proc.stdout.splitlines():
        if line.startswith(("+++ ", "--- ", "@@", "diff ", "index ")):
            continue
        if line.startswith("+"):
            lines.append(line[1:].rstrip("\r"))
    return lines


def changed_files(root: Path, base: str, parent: str) -> list[str]:
    proc = git(root, "diff", "--name-only", "--ignore-cr-at-eol", base, parent)
    if proc.returncode != 0:
        return []
    return [line for line in proc.stdout.splitlines() if line and is_kit(line)]


def show_file(root: Path, rev: str, path: str) -> str | None:
    proc = git(root, "show", f"{rev}:{path}")
    if proc.returncode != 0:
        return None
    return proc.stdout


def kept_lines(root: Path, path: str, head: str, merge: str | None) -> list[str]:
    texts = []
    disk = root / path
    if disk.is_file():
        texts.append(disk.read_text(encoding="utf-8", errors="replace"))
    for rev in (head, merge):
        if not rev:
            continue
        shown = show_file(root, rev, path)
        if shown is not None:
            texts.append(shown)
    lines = []
    for text in texts:
        lines.extend(line.rstrip("\r") for line in text.splitlines())
    return lines


def synced_of(line: str) -> tuple[str, str, str] | None:
    text = line.strip()
    match = SLICE_SYNCED.match(text)
    if match:
        return match.group(1), match.group(2), match.group(4)
    if text.startswith("- ") and not text.startswith("- Branch:") and not text.startswith("- Synced"):
        match = REPO_SYNCED.match(text)
        if match:
            return match.group(1), match.group(2), match.group(4)
    return None


def superseded(line: str, kept: list[str]) -> bool:
    parsed = synced_of(line)
    if parsed is None:
        return False
    repo, branch, date = parsed
    for other in kept:
        got = synced_of(other)
        if got and got[0] == repo and got[1] == branch and got[2] > date:
            return True
    return False


def joined_kept(line: str, kept: list[str]) -> bool:
    if "; " not in line:
        return False
    if "Synced at:" not in line and "Branch:" not in line:
        return False
    parts = [part.strip() for part in line.split("; ") if part.strip()]
    return bool(parts) and all(any(part in got for got in kept) for part in parts)


def short(root: Path, rev: str) -> str:
    proc = git(root, "rev-parse", "--short=12", rev)
    return proc.stdout.strip() if proc.returncode == 0 else rev[:12]


def check(root: Path, merge: str | None) -> dict:
    ours, theirs, merge_sha = merge_parents(root, merge)
    base_proc = git(root, "merge-base", ours, theirs)
    if base_proc.returncode != 0 or not base_proc.stdout.strip():
        fail("not-a-merge", "the parents have no merge base")
    base = base_proc.stdout.strip()
    head = git(root, "rev-parse", "HEAD").stdout.strip()
    files = sorted(set(changed_files(root, base, ours) + changed_files(root, base, theirs)))
    indexes = index_check(root, notes_index_script())
    lost = []
    for path in files:
        if is_index(path) and indexes == "pass":
            continue
        ours_lines = added_lines(root, base, ours, path)
        theirs_lines = added_lines(root, base, theirs, path)
        kept = kept_lines(root, path, head, merge_sha)
        seen = set(kept)
        by_side: dict[str, str] = {}
        for line in ours_lines:
            by_side.setdefault(line, "ours")
        for line in theirs_lines:
            if line in by_side:
                by_side[line] = "both"
            else:
                by_side[line] = "theirs"
        ours_sha = short(root, ours)
        theirs_sha = short(root, theirs)
        for line, side in by_side.items():
            if line in seen or superseded(line, kept) or joined_kept(line, kept):
                continue
            sha = {"ours": ours_sha, "theirs": theirs_sha, "both": f"{ours_sha} {theirs_sha}"}[side]
            lost.append({"file": path, "side": side, "sha": sha, "line": line})
    ok = not lost
    return {
        "ok": ok,
        "nothing_lost": ok,
        "lost": lost,
        "checked_files": files,
        "index_check": indexes,
        "ours": ours,
        "theirs": theirs,
        "merge": merge_sha,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Nothing-lost check for a merge")
    parser.add_argument("--root", default=".")
    parser.add_argument("--merge", help="Merge commit to check. Omit during a merge.")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if not (root / ".git").exists():
        fail("not-a-git-repo", f"not a git repo: {root}")
    payload = check(root, args.merge)
    emit(payload, 0 if payload["ok"] else 1)


if __name__ == "__main__":
    main()
