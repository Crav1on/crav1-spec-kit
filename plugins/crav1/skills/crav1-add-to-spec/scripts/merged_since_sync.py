#!/usr/bin/env python3
"""Merged since sync (1.194.0): has a branch in the spec's Synced at lines merged since the recorded commit?

One shared check for the tighten-and-plan walk start, /crav1-pr-status, the
specs sweep and the kit merge paths (/crav1-build-walk, /crav1-merge-pr).

    merged_since_sync.py check --spec <spec.md> --code-repo <checkout> [--base <ref>] [--pr N] [--headless]
    merged_since_sync.py stamp --spec <spec.md> --repo <repo> --branch <branch> --base <name> --merge <sha> --date <YYYY-MM-DD> [--yes]

`check` reads refs on disk only (no fetch) and writes nothing. The base is
`--base`, else the default branch: origin/HEAD, then origin/main, then
origin/master (the same order as design_run.py's default_branch). For each
work-branch `Synced at:` line whose branch tip is merged into the base, it
finds the merge commit and the commits after the recorded one. When the
spec has not recorded them it returns ONE yes card. A headless run only
reports (`offer` is null). `stamp` moves Synced at to the merge, only with
--yes, after the add-to-spec PR or branch step took the commits in.
"""
from __future__ import annotations

import argparse
import json
import re
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

SYNCED = re.compile(r"^Synced at:\s*(?:(?P<repo>\S+)\s+)?(?P<branch>\S+)@(?P<sha>[0-9a-f]{7,40})(?P<rest>.*)$", re.M)
PR_SUBJECT = re.compile(r"(?:Merge pull request #(\d+)|Merged PR (\d+):|\(#(\d+)\)\s*$)")
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def emit(payload: dict, code: int = 0) -> int:
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return code


def git(repo: str, *args: str) -> str | None:
    try:
        done = subprocess.run(["git", "-C", repo, *args], capture_output=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.decode("utf-8", "replace").strip() if done.returncode == 0 else None


def ref_ok(repo: str, ref: str) -> bool:
    return git(repo, "rev-parse", "--verify", "--quiet", ref + "^{commit}") is not None


def default_branch(repo: str) -> tuple[str, str]:
    """origin/HEAD, else origin/main, then origin/master; ("", reason) when none."""
    head = git(repo, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if head and head.startswith("refs/remotes/") and ref_ok(repo, head[len("refs/remotes/"):]):
        return head[len("refs/remotes/"):], ""
    for ref in ("origin/main", "origin/master"):
        if ref_ok(repo, ref):
            return ref, ""
    return "", "no default branch found (origin/HEAD is not set and there is no origin/main or origin/master)"


def is_ancestor(repo: str, older: str, newer: str) -> bool:
    try:
        done = subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", older, newer], capture_output=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return False
    return done.returncode == 0


def short(name: str) -> str:
    return name.split("/", 1)[1] if name.startswith("origin/") else name


def branch_ref(repo: str, branch: str) -> str | None:
    for cand in (f"origin/{branch}", branch):
        if ref_ok(repo, cand):
            return cand
    return None


def check(spec_text: str, repo: str, base: str | None = None, pr: str | None = None, headless: bool = False) -> dict:
    if base:
        base_ref = base if ref_ok(repo, base) else (f"origin/{base}" if ref_ok(repo, f"origin/{base}") else "")
        reason = "" if base_ref else f"base {base} not found in {repo}"
    else:
        base_ref, reason = default_branch(repo)
    if not base_ref:
        return {"ok": True, "status": "skipped", "reason": reason, "offer": None, "wrote": None}
    base_name = short(base_ref)
    rows = [m.groupdict() for m in SYNCED.finditer(spec_text)]
    found = []
    for row in rows:
        if row["branch"] == base_name or "(dropped)" in (row["rest"] or ""):
            continue
        tip = branch_ref(repo, row["branch"])
        if not tip or not is_ancestor(repo, tip, base_ref):
            found.append({"branch": row["branch"], "status": "not-merged"})
            continue
        merges = (git(repo, "rev-list", "--merges", "--ancestry-path", "--reverse", f"{tip}..{base_ref}") or "").split()
        merge = merges[0] if merges else (git(repo, "rev-parse", tip) or "")
        merge_short = merge[:7]
        synced_after = any(is_ancestor(repo, merge, r["sha"]) for r in rows)
        commits = (git(repo, "rev-list", f"{row['sha']}..{tip}") or "").split()
        subject = git(repo, "log", "-1", "--format=%s", merge) or ""
        m = PR_SUBJECT.search(subject)
        number = pr or (next(g for g in m.groups() if g) if m else None)
        status = "already-synced" if synced_after or not commits else "merged"
        found.append({"branch": row["branch"], "repo": row["repo"], "status": status, "merge": merge_short,
                      "commits": len(commits), "pr": number, "synced": row["sha"]})
    todo = [f for f in found if f["status"] == "merged"]
    out = {"ok": True, "base": base_name, "branches": found, "wrote": None, "offer": None}
    if not todo:
        out["status"] = "already-synced" if any(f["status"] == "already-synced" for f in found) else "not-merged"
        return out
    first = todo[0]
    who = f"PR {first['pr']}" if first["pr"] else first["branch"]
    noun = "commit" if first["commits"] == 1 else "commits"
    question = f"{who} merged at {first['merge']} with {first['commits']} {noun} the spec hasn't recorded. Take them in now?"
    command = f"/crav1-add-to-spec pr{first['pr']}" if first["pr"] else f"/crav1-add-to-spec {first['branch']}"
    out.update({"status": "merged", "merged": first, "question": question, "command": command})
    if headless:
        out["report"] = question.replace(" Take them in now?", "") + f" Run {command} to take them in."
        return out
    out["offer"] = "take-in"
    out["options"] = [
        {"id": "yes", "label": "yes, take them in now (Recommended)", "recommended": True,
         "text": f"Run the add-to-spec PR or branch step for {who} here, move Synced at to the merge {first['merge']}, then go on with this command."},
        {"id": "no", "label": "not now, go on", "recommended": False,
         "text": "Leave the spec as it is and go on; nothing is written."},
    ]
    out["after_yes"] = (f"merged_since_sync.py stamp --spec <spec.md> --repo {first['repo'] or '<repo>'} --branch {first['branch']} "
                        f"--base {base_name} --merge {first['merge']} --date <YYYY-MM-DD> --yes")
    return out


def stamp_text(text: str, repo: str, branch: str, base: str, merge: str, date: str) -> str:
    lines = text.splitlines(keepends=True)
    entry = f"Synced at: {repo} {base}@{merge[:7]}, {date}\n"
    done_base = False
    for i, line in enumerate(lines):
        m = SYNCED.match(line.rstrip("\n"))
        if not m:
            continue
        if m.group("branch") == base and (m.group("repo") or repo) == repo:
            lines[i] = entry
            done_base = True
        elif m.group("branch") == branch and "(merged" not in line:
            lines[i] = line.rstrip("\n") + f" (merged {merge[:7]})\n"
    if not done_base:
        last = max((i for i, l in enumerate(lines) if l.startswith("Synced at:")), default=None)
        at = (last + 1) if last is not None else next((i + 1 for i, l in enumerate(lines) if l.startswith("# ")), 0)
        lines.insert(at, entry)
    return "".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--spec", required=True)
    c.add_argument("--code-repo", required=True)
    c.add_argument("--base")
    c.add_argument("--pr")
    c.add_argument("--headless", action="store_true", help="report only, no card")
    s = sub.add_parser("stamp")
    s.add_argument("--spec", required=True)
    s.add_argument("--repo", required=True)
    s.add_argument("--branch", required=True)
    s.add_argument("--base", required=True)
    s.add_argument("--merge", required=True)
    s.add_argument("--date", required=True)
    s.add_argument("--yes", action="store_true")
    a = ap.parse_args(argv)
    spec = Path(a.spec)
    if not spec.is_file():
        return emit({"ok": False, "error": "spec", "line": f"no spec file at {spec}"}, 1)
    text = spec.read_text(encoding="utf-8")
    if a.cmd == "check":
        return emit(check(text, a.code_repo, a.base, a.pr, a.headless))
    if not SHA_RE.fullmatch(a.merge) or not DATE_RE.fullmatch(a.date):
        return emit({"ok": False, "error": "args", "line": "merge is a hex sha and date is YYYY-MM-DD"}, 1)
    new = stamp_text(text, a.repo, a.branch, a.base, a.merge, a.date)
    if not a.yes:
        return emit({"ok": True, "written": False, "line": f"Synced at: {a.repo} {a.base}@{a.merge[:7]}, {a.date}",
                     "message": "Planned only. Run again with --yes after the card's yes and the add-to-spec step."})
    if new != text:
        spec.write_text(new, encoding="utf-8")
    return emit({"ok": True, "written": new != text, "line": f"Synced at: {a.repo} {a.base}@{a.merge[:7]}, {a.date}"})


if __name__ == "__main__":
    sys.exit(main())
