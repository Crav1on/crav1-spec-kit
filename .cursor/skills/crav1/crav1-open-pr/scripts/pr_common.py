#!/usr/bin/env python3
"""Shared pull-request steps for open-pr, merge-pr, pr-status and review-pr (1.158.0).

Read-only. It never pushes, posts, merges, completes, votes, logs in, or
prints a token. It never writes claims.md. The rules it follows are
crav1-docs/reference/pr-common.md.

Subcommands, each printing one JSON object:

  parse   --ref <n-or-url> [--remote-url <url>]
          Which host and number a pull request reference names. A branch
          name is not a pull request.
  host    --remote-url <url>
          github, azure, or other, with the org/project/repo parts.
  find    --branch <head> [--base <base>] [--repo <dir>] [--from-json <file>]
          Open pull requests for one head branch. Never picks the newest:
          more than one is `pick: null` with every match listed.
  checks  --ref <n-or-url> [--repo <dir>] [--from-json <file>]
          State, draft, and the checks summed up as passing, failing,
          pending; `blocked` names what stops a merge.
  claim   --root <spec-folder> --branch <branch>
          The In progress: lines in claims.md for that branch. Read-only.
  behind  --head <ref> --base <ref> [--repo <dir>]
          Commits the head is behind and ahead of the base, and the
          catch-up advice: merge the base in, never rebase.

The interpreter is crav1-docs/reference/running-scripts.md. The canonical
copy lives in skill crav1-open-pr; the other three skills ship a thin copy
that runs it.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
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

GITHUB_PR = re.compile(r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<n>\d+)/?(?:[?#].*)?$", re.I)
AZURE_PR = re.compile(
    r"^https?://(?:dev\.azure\.com/(?P<org>[^/]+)|(?P<org2>[^./]+)\.visualstudio\.com)"
    r"/(?P<project>[^/]+)/_git/(?P<repo>[^/]+)/pullrequest/(?P<n>\d+)/?(?:[?#].*)?$",
    re.I,
)
NUMBER = re.compile(r"^#?(?P<n>\d+)$")
GITHUB_REMOTE = re.compile(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$", re.I)
AZURE_REMOTE = re.compile(
    r"(?:dev\.azure\.com[:/](?:v3/)?(?P<org>[^/]+)|(?P<org2>[^./@]+)\.visualstudio\.com(?::v3)?)"
    r"/(?P<project>[^/]+)/(?:_git/)?(?P<repo>[^/]+?)(?:\.git)?/?$",
    re.I,
)
CLAIM_LINE = re.compile(
    r"^In progress:\s*(?P<branch>\S+),\s*(?P<tasks>T?\d+(?:\s*,\s*T?\d+)*),\s*"
    r"(?P<user>.+),\s*since\s+(?P<since>\S.*?)\s*$",
    re.I,
)
REBASE_FREE = "Merge {base} into {head} (git merge {base}), resolve any conflicts, then push. Never rebase."

PASS = {"SUCCESS", "NEUTRAL", "SKIPPED", "PASS", "APPROVED", "SUCCEEDED"}
FAIL = {"FAILURE", "ERROR", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE", "FAIL", "REJECTED", "BROKEN"}


def emit(payload: dict, status: int = 0) -> int:
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return status


def host_of(url: str | None) -> dict:
    """github, azure, or other for a remote or pull-request URL."""
    text = (url or "").strip()
    m = GITHUB_PR.match(text) or GITHUB_REMOTE.search(text)
    if m:
        return {"host": "github", "owner": m.group("owner"), "repo": m.group("repo")}
    m = AZURE_PR.match(text) or AZURE_REMOTE.search(text)
    if m:
        org = m.group("org") or m.group("org2")
        return {"host": "azure", "org": org, "project": m.group("project"), "repo": m.group("repo")}
    return {"host": "other" if text else "unknown"}


def same_repo(a: dict, b: dict) -> bool:
    """dev.azure.com/<org> and <org>.visualstudio.com are the same; case and .git are ignored."""
    if a.get("host") != b.get("host") or a.get("host") not in ("github", "azure"):
        return False
    keys = ("owner", "repo") if a["host"] == "github" else ("org", "project", "repo")
    return all((a.get(k) or "").lower().removesuffix(".git") == (b.get(k) or "").lower().removesuffix(".git") for k in keys)


def parse_ref(ref: str, remote_url: str | None = None) -> dict:
    text = (ref or "").strip()
    m = GITHUB_PR.match(text)
    if m:
        out = {"host": "github", "owner": m.group("owner"), "repo": m.group("repo"), "number": int(m.group("n")), "url": text}
    else:
        m = AZURE_PR.match(text)
        if m:
            out = {"host": "azure", "org": m.group("org") or m.group("org2"), "project": m.group("project"),
                   "repo": m.group("repo"), "number": int(m.group("n")), "url": text}
        else:
            m = NUMBER.match(text)
            if not m:
                return {"status": "not-a-pr", "line": f"{text!r} is not a pull request number or URL. A branch name is not a pull request."}
            remote = host_of(remote_url)
            if remote["host"] in ("other", "unknown"):
                return {"status": "needs-remote", "number": int(m.group("n")),
                        "line": "A bare number needs the single git remote, or a gh repo that matches it."}
            out = dict(remote, number=int(m.group("n")))
            out["status"] = "ok"
            return out
    out["status"] = "ok"
    if remote_url:
        remote = host_of(remote_url)
        if remote["host"] in ("github", "azure") and not same_repo(out, remote):
            out["status"] = "mismatch"
            out["line"] = f"PR repository {text} is not this remote ({remote_url}). Name both; do not act across that mismatch."
    return out


def _run(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    exe = shutil.which(cmd[0]) or shutil.which(cmd[0] + ".cmd")
    if not exe:
        return 127, "", f"{cmd[0]} not found"
    proc = subprocess.run([exe] + cmd[1:], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, proc.stdout, proc.stderr


def _remote_url(repo: str | None) -> str:
    code, out, _ = _run(["git", "remote"], cwd=repo)
    remotes = out.split() if code == 0 else []
    if len(remotes) != 1:
        return ""
    code, out, _ = _run(["git", "remote", "get-url", remotes[0]], cwd=repo)
    return out.strip() if code == 0 else ""


def summarize_find(items: list[dict], branch: str, base: str | None) -> dict:
    rows = []
    for it in items:
        head = it.get("headRefName") or (it.get("sourceRefName") or "").removeprefix("refs/heads/") or branch
        target = it.get("baseRefName") or (it.get("targetRefName") or "").removeprefix("refs/heads/")
        if base and target and target != base:
            continue
        rows.append({"number": it.get("number") or it.get("pullRequestId"), "url": it.get("url") or "",
                     "head": head, "base": target, "draft": bool(it.get("isDraft"))})
    pick = rows[0]["number"] if len(rows) == 1 else None
    if not rows:
        line = f"No open pull request for {branch}" + (f" -> {base}" if base else "") + "."
    elif pick is None:
        line = f"{len(rows)} open pull requests for {branch}; ask which one. Do not pick the newest."
    else:
        line = f"PR {pick} is the one open pull request for {branch}."
    return {"status": "ok", "branch": branch, "base": base, "matches": rows, "pick": pick, "line": line}


def cmd_find(args) -> int:
    if args.from_json:
        items = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
        items = items.get("value", items) if isinstance(items, dict) else items
        return emit(summarize_find(items, args.branch, args.base))
    host = host_of(_remote_url(args.repo))["host"]
    if host == "github":
        cmd = ["gh", "pr", "list", "--head", args.branch, "--state", "open", "--json", "number,url,headRefName,baseRefName,isDraft"]
        if args.base:
            cmd += ["--base", args.base]
        code, out, err = _run(cmd, cwd=args.repo)
    elif host == "azure":
        cmd = ["az", "repos", "pr", "list", "--source-branch", f"refs/heads/{args.branch}", "--status", "active", "--output", "json"]
        if args.base:
            cmd += ["--target-branch", f"refs/heads/{args.base}"]
        code, out, err = _run(cmd, cwd=args.repo)
    else:
        return emit({"status": "no-host", "branch": args.branch, "line": "The remote is neither GitHub nor Azure DevOps; find the pull request by hand."}, 1)
    if code != 0:
        return emit({"status": "cli-failed", "host": host, "line": (err or out).strip()[:300]}, 1)
    return emit(summarize_find(json.loads(out or "[]"), args.branch, args.base))


def _state_of(raw: str | None) -> str:
    s = (raw or "").upper()
    return {"ACTIVE": "OPEN", "COMPLETED": "MERGED", "ABANDONED": "CLOSED"}.get(s, s)


def summarize_checks(view: dict) -> dict:
    """Sum up a gh pr view JSON (statusCheckRollup) or an Azure policy list."""
    passing, failing, pending = [], [], []
    for c in view.get("statusCheckRollup") or []:
        name = c.get("name") or c.get("context") or "check"
        verdict = (c.get("conclusion") or c.get("state") or "").upper()
        status = (c.get("status") or "").upper()
        if verdict in PASS:
            passing.append(name)
        elif verdict in FAIL:
            failing.append(name)
        elif status in ("COMPLETED",) and not verdict:
            passing.append(name)
        else:
            pending.append(name)
    for p in view.get("policies") or []:
        name = ((p.get("configuration") or {}).get("type") or {}).get("displayName") or p.get("name") or "policy"
        verdict = (p.get("status") or "").upper()
        if verdict in ("APPROVED", "NOTAPPLICABLE"):
            passing.append(name)
        elif verdict in ("REJECTED", "BROKEN"):
            failing.append(name)
        else:
            pending.append(name)
    state = _state_of(view.get("state") or view.get("status"))
    draft = bool(view.get("isDraft"))
    blocked = []
    if state != "OPEN":
        blocked.append(f"state is {state or 'unknown'}")
    if failing:
        blocked.append("failing: " + ", ".join(failing))
    if pending:
        blocked.append("pending: " + ", ".join(pending))
    review = (view.get("reviewDecision") or "").upper()
    if review in ("CHANGES_REQUESTED", "REVIEW_REQUIRED"):
        blocked.append("review: " + review.lower())
    merge_state = (view.get("mergeStateStatus") or "").upper()
    if merge_state == "BEHIND":
        blocked.append("behind the base: " + REBASE_FREE.format(base=view.get("baseRefName") or "<base>", head=view.get("headRefName") or "<head>"))
    if (view.get("mergeable") or "").upper() == "CONFLICTING":
        blocked.append("conflicts: " + REBASE_FREE.format(base=view.get("baseRefName") or "<base>", head=view.get("headRefName") or "<head>"))
    return {"status": "ok", "state": state, "draft": draft, "passing": passing, "failing": failing,
            "pending": pending, "review": review.lower() or None, "blocked": blocked,
            "line": f"{len(passing)} passing, {len(failing)} failing, {len(pending)} pending" + ("" if state == "OPEN" else f"; {state}")}


def cmd_checks(args) -> int:
    if args.from_json:
        return emit(summarize_checks(json.loads(Path(args.from_json).read_text(encoding="utf-8"))))
    ref = parse_ref(args.ref, _remote_url(args.repo))
    if ref.get("status") not in ("ok",):
        return emit(ref, 1)
    if ref["host"] == "github":
        code, out, err = _run(["gh", "pr", "view", args.ref, "--json",
                               "number,url,state,isDraft,baseRefName,headRefName,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup"], cwd=args.repo)
        if code != 0:
            return emit({"status": "cli-failed", "host": "github", "line": (err or out).strip()[:300]}, 1)
        return emit(summarize_checks(json.loads(out)))
    code, out, err = _run(["az", "repos", "pr", "show", "--id", str(ref["number"]), "--detect", "false", "--output", "json"], cwd=args.repo)
    if code != 0:
        return emit({"status": "cli-failed", "host": "azure", "line": (err or out).strip()[:300]}, 1)
    view = json.loads(out)
    code, pol, _ = _run(["az", "repos", "pr", "policy", "list", "--id", str(ref["number"]), "--detect", "false", "--output", "json"], cwd=args.repo)
    view["policies"] = json.loads(pol) if code == 0 and pol.strip() else []
    return emit(summarize_checks(view))


def claims_for(text: str, branch: str) -> list[dict]:
    rows = []
    for raw in text.splitlines():
        m = CLAIM_LINE.match(raw.strip())
        if m and m.group("branch") == branch:
            tasks = ["T" + t.strip().lstrip("Tt") for t in m.group("tasks").split(",")]
            rows.append({"branch": branch, "tasks": tasks, "user": m.group("user").strip(), "since": m.group("since")})
    return rows


def cmd_claim(args) -> int:
    path = Path(args.root) / "claims.md"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    rows = claims_for(text, args.branch)
    line = (f"{args.branch} is claimed: " + "; ".join(f"{', '.join(r['tasks'])} by {r['user']} since {r['since']}" for r in rows)) if rows else f"No claim for {args.branch}."
    return emit({"status": "ok", "branch": args.branch, "claims": rows, "line": line,
                 "note": "Read-only. /crav1-build-walk writes and clears claims.md; the PR skills never do."})


def cmd_behind(args) -> int:
    code, out, err = _run(["git", "rev-list", "--left-right", "--count", f"{args.base}...{args.head}"], cwd=args.repo)
    if code != 0:
        return emit({"status": "git-failed", "line": (err or out).strip()[:300]}, 1)
    behind, ahead = (int(x) for x in out.split())
    advice = REBASE_FREE.format(base=args.base, head=args.head) if behind else ""
    return emit({"status": "ok", "head": args.head, "base": args.base, "behind": behind, "ahead": ahead, "advice": advice,
                 "line": f"{args.head} is {behind} behind and {ahead} ahead of {args.base}." + (" " + advice if advice else "")})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pr_common.py", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("parse")
    p.add_argument("--ref", required=True)
    p.add_argument("--remote-url")
    h = sub.add_parser("host")
    h.add_argument("--remote-url", required=True)
    f = sub.add_parser("find")
    f.add_argument("--branch", required=True)
    f.add_argument("--base")
    f.add_argument("--repo")
    f.add_argument("--from-json")
    c = sub.add_parser("checks")
    c.add_argument("--ref", required=True)
    c.add_argument("--repo")
    c.add_argument("--from-json")
    cl = sub.add_parser("claim")
    cl.add_argument("--root", required=True)
    cl.add_argument("--branch", required=True)
    b = sub.add_parser("behind")
    b.add_argument("--head", required=True)
    b.add_argument("--base", required=True)
    b.add_argument("--repo")
    args = parser.parse_args(argv)
    if args.cmd == "parse":
        out = parse_ref(args.ref, args.remote_url)
        return emit(out, 0 if out.get("status") == "ok" else 1)
    if args.cmd == "host":
        return emit(host_of(args.remote_url))
    return {"find": cmd_find, "checks": cmd_checks, "claim": cmd_claim, "behind": cmd_behind}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
