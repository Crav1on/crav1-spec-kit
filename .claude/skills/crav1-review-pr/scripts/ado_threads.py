#!/usr/bin/env python3
"""Read and change Azure DevOps pull requests: threads, votes, pushes, description (1.172.0, 1.193.0).

    ado_threads.py list        --pr N [--project P] [--repo R] [--org URL] [--code-repo <path>]
    ado_threads.py compare     --pr N --draft <file>
    ado_threads.py post        --pr N --file <file> [--yes]
    ado_threads.py pr          --pr N        (title, state, description, created, votes)
    ado_threads.py iterations  --pr N        (pushes: id, date, head commit)
    ado_threads.py changes     --pr N --iteration I [--compare-to J]   (files a push changed)
    ado_threads.py set-status  --pr N --thread T --status fixed [--yes]  (read back after)
    ado_threads.py since-last  --pr N --note <PR note> --who <name>      (against the recorded state)

This is the one way the kit reads and changes Azure DevOps pull requests:
no `az rest`, no hand-made token or curl calls. Thread and comment dates
(`published`, `updated`) come with `list`.

Organization, project and repository come from the code repo's git remote
(`--code-repo`, default the current folder), the same read the host lookup
uses (1.182.0), so a post does not 404 for want of them. `--org`,
`--project` and `--repo` still override each one.

It reads `az ... -o json` from stdout as bytes, never through a shell
redirect, and decodes UTF-8 first, then UTF-8 with a BOM, then cp1252, so a
Windows console code page does not break the JSON. `--from-file` reads saved
az output instead of calling az. A post is always a new top-level thread
(`parentCommentId` 0), as a re-review needs (1.171.0). Nothing is posted
without `--yes`. Output is one JSON object; errors have `ok: false`.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass


def decode(data: bytes) -> str:
    """UTF-8, then UTF-8 with BOM, then cp1252. Never raises."""
    if isinstance(data, str):
        return data
    for codec in ("utf-8", "utf-8-sig"):
        try:
            return data.decode(codec).lstrip("\ufeff")
        except UnicodeDecodeError:
            continue
    try:
        return data.decode("cp1252")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


def az_command() -> str:
    for name in ("az", "az.cmd"):
        found = shutil.which(name)
        if found:
            return found
    return "az"


def run_az(args: list[str]) -> bytes:
    """Run az and return stdout bytes. Tests replace this function."""
    done = subprocess.run([az_command(), *args], capture_output=True)
    if done.returncode != 0:
        raise RuntimeError(decode(done.stderr or b"").strip() or f"az exited {done.returncode}")
    return done.stdout


import re

AZURE_REMOTE = re.compile(
    r"(?:dev\.azure\.com[:/](?:v3/)?(?P<org>[^/]+)|(?P<org2>[^./@]+)\.visualstudio\.com(?::v3)?)"
    r"/(?P<project>[^/]+)/(?:_git/)?(?P<repo>[^/]+?)(?:\.git)?/?$",
    re.I,
)


def remote_url(code_repo: str | None) -> str | None:
    """The code repo's git remote: origin, else its only remote. Tests replace this."""
    where = code_repo or "."

    def git(*args: str) -> str | None:
        try:
            done = subprocess.run(["git", "-C", where, *args], capture_output=True, timeout=15)
        except (OSError, subprocess.SubprocessError):
            return None
        return decode(done.stdout).strip() if done.returncode == 0 else None

    url = git("remote", "get-url", "origin")
    if url:
        return url
    names = (git("remote") or "").split()
    return git("remote", "get-url", names[0]) if len(names) == 1 else None


def remote_route(url: str | None) -> dict:
    """{"org": URL, "project", "repo"} from an Azure DevOps remote, else {} (1.182.0)."""
    match = AZURE_REMOTE.search((url or "").strip())
    if not match:
        return {}
    org = match.group("org") or match.group("org2")
    return {"org": f"https://dev.azure.com/{org}", "project": match.group("project"), "repo": match.group("repo")}


def fill_route(args) -> None:
    """Fill a missing --org, --project or --repo from the git remote; flags win (1.182.0)."""
    if getattr(args, "from_file", None) or (args.org and args.project and args.repo):
        return
    found = remote_route(remote_url(getattr(args, "code_repo", None)))
    for key in ("org", "project", "repo"):
        if not getattr(args, key, None) and found.get(key):
            setattr(args, key, found[key])


def _route(args, resource: str = "pullRequestThreads", extra: list[str] | None = None) -> list[str]:
    route = [f"pullRequestId={args.pr}", *(extra or [])]
    if args.project:
        route.append(f"project={args.project}")
    if args.repo:
        route.append(f"repositoryId={args.repo}")
    out = ["devops", "invoke", "--area", "git", "--resource", resource,
           "--route-parameters", *route, "--api-version", "7.1", "-o", "json"]
    if args.org:
        out += ["--org", args.org]
    return out


def load_threads(args) -> list[dict]:
    raw = Path(args.from_file).read_bytes() if args.from_file else run_az(_route(args))
    data = json.loads(decode(raw) or "{}")
    if isinstance(data, dict):
        data = data.get("value") or []
    return [t for t in data if isinstance(t, dict)]


def normalize(text: str) -> str:
    rows = (text or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(row.rstrip() for row in rows).strip()


STATUS = {0: "unknown", 1: "active", 2: "fixed", 3: "wontFix", 4: "closed", 5: "byDesign", 6: "pending"}


def summarize(threads: list[dict]) -> list[dict]:
    out = []
    for thread in threads:
        comments = []
        for comment in thread.get("comments") or []:
            if comment.get("isDeleted") or comment.get("commentType") == "system":
                continue
            author = (comment.get("author") or {}).get("displayName") or ""
            comments.append({
                "id": comment.get("id"),
                "parent": comment.get("parentCommentId") or 0,
                "author": author,
                "content": comment.get("content") or "",
                "published": comment.get("publishedDate"),
                "updated": comment.get("lastContentUpdatedDate") or comment.get("lastUpdatedDate"),
            })
        if not comments:
            continue
        status = thread.get("status")
        out.append({
            "thread": thread.get("id"),
            "status": STATUS.get(status, status) if isinstance(status, int) else (status or ""),
            "file": ((thread.get("threadContext") or {}).get("filePath")) or None,
            "published": thread.get("publishedDate"),
            "updated": thread.get("lastUpdatedDate"),
            "comments": comments,
        })
    return out


def compare(threads: list[dict], draft: str) -> dict:
    want = normalize(draft)
    for thread in summarize(threads):
        for comment in thread["comments"]:
            if normalize(comment["content"]) == want:
                return {"same": True, "thread": thread["thread"], "comment": comment["id"],
                        "line": f"The posted comment in thread {thread['thread']} matches the draft."}
    return {"same": False, "thread": None, "comment": None,
            "line": "No posted comment matches the draft."}


def post_body(text: str) -> dict:
    return {"comments": [{"parentCommentId": 0, "content": text, "commentType": 1}], "status": 1}


def cmd_list(args) -> dict:
    threads = summarize(load_threads(args))
    return {"ok": True, "pr": args.pr, "count": len(threads), "threads": threads}


def cmd_compare(args) -> dict:
    draft = decode(Path(args.draft).read_bytes())
    found = compare(load_threads(args), draft)
    found["ok"] = True
    return found


def cmd_post(args) -> dict:
    text = decode(Path(args.file).read_bytes())
    body = post_body(text)
    if not args.yes:
        return {"ok": True, "posted": False, "body": body,
                "line": "Preview only. Add --yes after the user's yes to post a new thread."}
    fd, tmp = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(body, handle, ensure_ascii=False)
        cmd = _route(args) + ["--http-method", "POST", "--in-file", tmp]
        data = json.loads(decode(run_az(cmd)) or "{}")
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    return {"ok": True, "posted": True, "thread": data.get("id"),
            "line": f"Posted a new thread{(' ' + str(data.get('id'))) if data.get('id') else ''} on PR {args.pr}."}


STATUS_CODES = {name: code for code, name in STATUS.items() if code}
VOTES = {10: "approved", 5: "approved with suggestions", 0: "no vote", -5: "waiting for author", -10: "rejected"}


def _json(raw: bytes):
    return json.loads(decode(raw) or "{}")


def _load(args, cmd: list[str]):
    """Saved az output (--from-file) or a live az call, decoded as UTF-8 first."""
    return _json(Path(args.from_file).read_bytes() if args.from_file else run_az(cmd))


def pr_view(data: dict) -> dict:
    reviewers = []
    for r in data.get("reviewers") or []:
        vote = r.get("vote") or 0
        reviewers.append({"name": r.get("displayName") or "", "vote": vote, "vote_text": VOTES.get(vote, str(vote)),
                          "required": bool(r.get("isRequired"))})
    return {
        "pr": data.get("pullRequestId"),
        "title": data.get("title") or "",
        "state": data.get("status") or "",
        "created": data.get("creationDate"),
        "created_by": (data.get("createdBy") or {}).get("displayName") or "",
        "description": normalize(data.get("description") or ""),
        "source": data.get("sourceRefName"),
        "target": data.get("targetRefName"),
        "head": ((data.get("lastMergeSourceCommit") or {}).get("commitId")),
        "votes": reviewers,
    }


def _pr_cmd(args) -> list[str]:
    cmd = ["repos", "pr", "show", "--id", str(args.pr), "--detect", "false", "-o", "json"]
    if args.org:
        cmd += ["--org", args.org]
    return cmd


def cmd_pr(args) -> dict:
    return dict(ok=True, **pr_view(_load(args, _pr_cmd(args))))


def iterations_view(data) -> list[dict]:
    rows = data.get("value") if isinstance(data, dict) else data
    out = []
    for it in rows or []:
        out.append({"id": it.get("id"), "created": it.get("createdDate"),
                    "head": (it.get("sourceRefCommit") or {}).get("commitId"),
                    "description": it.get("description") or ""})
    return sorted(out, key=lambda r: r["id"] or 0)


def cmd_iterations(args) -> dict:
    rows = iterations_view(_load(args, _route(args, "pullRequestIterations")))
    return {"ok": True, "pr": args.pr, "count": len(rows), "iterations": rows,
            "head": rows[-1]["head"] if rows else None, "push": rows[-1]["id"] if rows else 0}


def cmd_changes(args) -> dict:
    cmd = _route(args, "pullRequestIterationChanges", [f"iterationId={args.iteration}"])
    if args.compare_to:
        cmd += ["--query-parameters", f"$compareTo={args.compare_to}"]
    data = _load(args, cmd)
    files = sorted({(e.get("item") or {}).get("path") for e in (data.get("changeEntries") or []) if (e.get("item") or {}).get("path")})
    return {"ok": True, "pr": args.pr, "iteration": args.iteration, "files": files}


def cmd_set_status(args) -> dict:
    if args.status not in STATUS_CODES:
        return {"ok": False, "error": "status", "line": "The status is one of " + ", ".join(sorted(STATUS_CODES)) + "."}
    body = {"status": STATUS_CODES[args.status]}
    if not args.yes:
        return {"ok": True, "changed": False, "thread": args.thread, "body": body,
                "line": f"Preview only. Add --yes after the user's yes to set thread {args.thread} to {args.status}."}
    route = _route(args, "pullRequestThreads", [f"threadId={args.thread}"])
    fd, tmp = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(body, handle)
        run_az(route + ["--http-method", "PATCH", "--in-file", tmp])
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    back = _json(run_az(route))
    shown = back.get("status")
    shown = STATUS.get(shown, shown) if isinstance(shown, int) else shown
    return {"ok": shown == args.status, "changed": True, "thread": args.thread, "status": shown,
            "line": f"Thread {args.thread} now shows {shown} on the host."}


READ_RE = re.compile(r"^- Read: (?P<who>[^|]+?) \| (?P<head>[0-9a-f]{7,40}), push (?P<push>\d+), newest comment (?P<newest>\S+) \| (?P<date>\S+)\s*$")
DESC_RE = re.compile(r"^## Description as of (?P<date>.+?)\s*$")
HISTORY_RE = re.compile(r"^## (?:Description as of|PR updates as of|Comment as drafted|Comment as posted|Replies as drafted|Review follow-ups)")


def recorded_state(note: str, who: str) -> dict:
    """The state the PR note recorded: your Read line and the newest saved description."""
    read, desc, desc_date, cur = None, None, None, None
    for line in note.splitlines():
        m = READ_RE.match(line)
        if m and m.group("who").strip().lower() == who.strip().lower():
            read = m.groupdict()
        if HISTORY_RE.match(line):
            if cur is not None:
                desc = "\n".join(cur)
            cur = None
            d = DESC_RE.match(line)
            if d:
                cur, desc_date = [], d.group("date")
            continue
        if cur is not None:
            cur.append(line)
    if cur is not None:
        desc = "\n".join(cur)
    return {"read": read, "description": normalize(desc) if desc is not None else None, "description_date": desc_date}


def newest_comment(threads: list[dict]) -> str | None:
    stamps = [c.get("updated") or c.get("published") for t in threads for c in t["comments"]]
    stamps = [x for x in stamps if x]
    return max(stamps) if stamps else None


def since_last(note: str, who: str, threads: list[dict], iterations: list[dict], pr: dict) -> dict:
    rec = recorded_state(note, who)
    read = rec["read"]
    push = iterations[-1]["id"] if iterations else 0
    head = iterations[-1]["head"] if iterations else None
    if not read:
        return {"ok": True, "earlier": False, "line": "No earlier run of yours; showing everything."}
    since = read["newest"]
    newer = []
    for t in threads:
        for c in t["comments"]:
            when = c.get("updated") or c.get("published")
            if when and (since == "none" or when[:16] > since.rstrip("Z")[:16]):
                newer.append({"thread": t["thread"], "comment": c["id"], "author": c["author"], "when": when})
    desc_changed = None if rec["description"] is None else rec["description"] != pr.get("description", "")
    return {
        "ok": True, "earlier": True,
        "recorded": {"head": read["head"], "push": int(read["push"]), "newest_comment": since, "date": read["date"],
                     "description_date": rec["description_date"]},
        "new_push": push > int(read["push"]), "push": push, "head": head,
        "new_comments": newer,
        "newest_comment": newest_comment(threads),
        "description_changed": desc_changed,
        "nothing_new": push <= int(read["push"]) and not newer and not desc_changed,
    }


def cmd_since_last(args) -> dict:
    note = decode(Path(args.note).read_bytes())
    if args.from_dir:
        base = Path(args.from_dir)
        threads = summarize(_json_list((base / "threads.json").read_bytes()))
        its = iterations_view(_json((base / "iterations.json").read_bytes()))
        pr = pr_view(_json((base / "pr.json").read_bytes()))
    else:
        threads = summarize(load_threads(args))
        its = iterations_view(_json(run_az(_route(args, "pullRequestIterations"))))
        pr = pr_view(_json(run_az(_pr_cmd(args))))
    return dict(pr=args.pr, **since_last(note, args.who, threads, its, pr))


def _json_list(raw: bytes) -> list[dict]:
    data = _json(raw)
    if isinstance(data, dict):
        data = data.get("value") or []
    return [t for t in data if isinstance(t, dict)]


def _common(p) -> None:
    p.add_argument("--pr", required=True, type=int)
    p.add_argument("--project")
    p.add_argument("--repo")
    p.add_argument("--org")
    p.add_argument("--code-repo", default=".", help="the code repo whose git remote names org, project and repo")
    p.add_argument("--from-file")


def main(argv: list[str] | None = None) -> int:
    _utf8_stdout()
    parser = argparse.ArgumentParser(description="Azure DevOps pull-request threads")
    sub = parser.add_subparsers(dest="cmd", required=True)
    lst = sub.add_parser("list")
    cmp_ = sub.add_parser("compare")
    cmp_.add_argument("--draft", required=True)
    pst = sub.add_parser("post")
    pst.add_argument("--file", required=True)
    pst.add_argument("--yes", action="store_true")
    prv = sub.add_parser("pr")
    its = sub.add_parser("iterations")
    chg = sub.add_parser("changes")
    chg.add_argument("--iteration", required=True, type=int)
    chg.add_argument("--compare-to", type=int)
    sts = sub.add_parser("set-status")
    sts.add_argument("--thread", required=True, type=int)
    sts.add_argument("--status", required=True)
    sts.add_argument("--yes", action="store_true")
    snc = sub.add_parser("since-last")
    snc.add_argument("--note", required=True, help="the PR note; its Read line and saved description are the recorded state")
    snc.add_argument("--who", required=True, help="the name on your Read line")
    snc.add_argument("--from-dir", help="saved threads.json, iterations.json and pr.json instead of az")
    for p in (lst, cmp_, pst, prv, its, chg, sts, snc):
        _common(p)
    args = parser.parse_args(argv)
    fill_route(args)
    try:
        result = {"list": cmd_list, "compare": cmd_compare, "post": cmd_post, "pr": cmd_pr,
                  "iterations": cmd_iterations, "changes": cmd_changes, "set-status": cmd_set_status,
                  "since-last": cmd_since_last}[args.cmd](args)
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        result = {"ok": False, "error": args.cmd, "line": str(exc)}
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    sys.exit(main())
