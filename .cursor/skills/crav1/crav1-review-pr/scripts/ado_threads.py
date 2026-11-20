#!/usr/bin/env python3
"""Read and change Azure DevOps pull requests: threads, votes, pushes, description (1.172.0, 1.193.0).

    ado_threads.py list        --pr N [--project P] [--repo R] [--org URL] [--code-repo <path>]
    ado_threads.py compare     --pr N --draft <file>
    ado_threads.py post        --pr N --file <file> [--yes]
    ado_threads.py pr          --pr N        (title, state, description, created, votes)
    ado_threads.py iterations  --pr N        (pushes: id, date, head commit)
    ado_threads.py changes     --pr N --iteration I [--compare-to J]   (files a push changed)
    ado_threads.py set-status  --pr N --thread T --status fixed [--yes]  (read back after)
    ado_threads.py reply       --pr N --thread T --file <file> [--status fixed] [--yes]  (1.199.0)
    ado_threads.py list        --pr N --brief  (one line per thread, 1.199.0)
    ado_threads.py set-point   --pr N --note <PR note> --thread T --status answered [--text T] [--yes]  (1.199.0)
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
    if not found.get("org") and not getattr(args, "org", None):
        found = {**repos_md_route(Path.cwd(), getattr(args, "repo", None)), **found}
    for key in ("org", "project", "repo"):
        if not getattr(args, key, None) and found.get(key):
            setattr(args, key, found[key])


def repos_md_route(start: Path, repo: str | None = None) -> dict:
    """1.198.0: the Azure DevOps org (and project, repo) from `docs/system/repos.md` when the remote
    names none, for example when run from the specs repo. The row naming `repo` wins, else the only
    Azure DevOps URL. {} when not found or ambiguous."""
    for folder in (start, *start.parents):
        path = folder / "docs" / "system" / "repos.md"
        if not path.is_file():
            continue
        routes = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            for url in re.findall(r"https?://[^\s|)>`]+", line):
                found = remote_route(url)
                if found:
                    routes.append(found)
        if repo:
            named = [r for r in routes if r["repo"].lower() == repo.lower()]
            if named:
                return named[0]
        orgs = {r["org"] for r in routes}
        if len(orgs) == 1:
            return {"org": routes[0]["org"]} if len(routes) > 1 else routes[0]
        return {}
    return {}


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
        context = thread.get("threadContext") or {}
        out.append({
            "thread": thread.get("id"),
            "status": STATUS.get(status, status) if isinstance(status, int) else (status or ""),
            "file": context.get("filePath") or None,
            "line": ((context.get("rightFileStart") or context.get("leftFileStart") or {}).get("line")) or None,
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


def brief_lines(threads: list[dict], limit: int = 200) -> list[str]:
    """`thread 195 | active | src/app.py:12 | person A | <last 200 characters>` (1.199.0).

    The key is always `thread`, so no summary prints `thread None`.
    """
    rows = []
    for thread in threads:
        last = thread["comments"][-1] if thread.get("comments") else {}
        where = thread.get("file") or "(no file)"
        if thread.get("line"):
            where += f":{thread['line']}"
        text = " ".join(str(last.get("content") or "").split())
        if len(text) > limit:
            text = "…" + text[-limit:]
        rows.append(f"thread {thread.get('thread')} | {thread.get('status') or 'unknown'} | {where} | "
                    f"{last.get('author') or 'unknown'} | {text}")
    return rows


def cmd_list(args) -> dict:
    threads = summarize(load_threads(args))
    if getattr(args, "brief", False):
        return {"ok": True, "pr": args.pr, "count": len(threads), "brief": brief_lines(threads),
                "line": f"{len(threads)} threads on PR {args.pr}."}
    return {"ok": True, "pr": args.pr, "count": len(threads), "threads": threads}


def thread_link(args, thread) -> str | None:
    """The thread's web link, `...pullrequest/<n>?discussionId=<t>` (1.199.0)."""
    if not (args.org and args.project and args.repo):
        return None
    return f"{args.org.rstrip('/')}/{args.project}/_git/{args.repo}/pullrequest/{args.pr}?discussionId={thread}"


def reply_body(text: str, parent: int) -> dict:
    return {"parentCommentId": parent, "content": text, "commentType": 1}


DRAFT_HEAD = re.compile(r"^## Replies as drafted, (?P<date>[^(]+?) \((?P<state>[^)]*)\)\s*$")


def mark_draft_posted(note: str, thread, when: str) -> tuple[str, bool]:
    """Mark the newest `## Replies as drafted` section that names this thread as posted (1.199.0).

    `(not posted)` becomes `(thread 195 posted 2026-11-20)`; a section that
    holds other threads too keeps `not posted` for them:
    `(not posted; thread 195 posted 2026-11-20)`. Only the heading changes;
    the drafted words stay as they were.
    """
    lines = note.split("\n")
    heads = [i for i, line in enumerate(lines) if DRAFT_HEAD.match(line)]
    for index in reversed(heads):
        end = next((j for j in range(index + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
        body = "\n".join(lines[index + 1:end])
        if not re.search(rf"\bthread {re.escape(str(thread))}\b", body, re.I):
            continue
        match = DRAFT_HEAD.match(lines[index])
        state = match.group("state")
        mark = f"thread {thread} posted {when}"
        if mark in state:
            return note, False
        others = len(set(re.findall(r"\bthread (\d+)\b", body, re.I)) - {str(thread)}) > 0
        if state == "not posted":
            state = f"not posted; {mark}" if others else mark
        else:
            state = f"{state}; {mark}"
        lines[index] = f"## Replies as drafted, {match.group('date')} ({state})"
        return "\n".join(lines), True
    return note, False


POINT_RE = re.compile(r"^- Point: (?P<anchor>[^|]*?) \| (?P<status>[^|]*?) \| (?P<owner>[^|]*?) \| (?P<tags>[^|]*?) \| (?P<text>.*)$")


def parse_point(line: str) -> dict | None:
    """The same Point fields pr_common.py reads (crav1-open-pr), 1.199.0."""
    m = POINT_RE.match(line.rstrip("\n"))
    if not m:
        return None
    d = m.groupdict()
    d["tags"] = [] if d["tags"].strip() == "-" else [t.strip() for t in d["tags"].split(";") if t.strip()]
    return d


def point_line(p: dict) -> str:
    tags = "; ".join(p["tags"]) if p["tags"] else "-"
    return f"- Point: {p['anchor']} | {p['status']} | {p['owner']} | {tags} | {p['text']}"


POINT_STATUSES = ("done", "agreed", "declined", "answered", "open", "waiting on", "needs", "follow-up", "migrated")


def status_words(status: str) -> str:
    """A Point status in plain words for a reply (1.199.0): never `done host` jargon."""
    text = (status or "").strip()
    if text == "answered":
        return "answered; no code change"
    if text == "done host":
        return "done: the host setting reads back live"
    if text.startswith("done "):
        return f"done in {text[5:]}"
    return text


def set_point(note: str, thread, status: str, text: str | None, when: str) -> tuple[str, str | None]:
    """Replace the status (and text) of the Point tagged `thread <id>`, in place (1.199.0).

    `answered` also adds `answered <date>`. Returns the new note and the new
    line, or the note unchanged and None when no Point names that thread.
    The script writes the record, so a non-ASCII Point line never needs a
    hand edit.
    """
    lines = note.split("\n")
    for i, line in enumerate(lines):
        p = parse_point(line)
        if not p or f"thread {thread}" not in p["tags"]:
            continue
        p["status"] = status
        if status == "answered":
            p["tags"] = [t for t in p["tags"] if not t.startswith("answered ")] + [f"answered {when}"]
        if text:
            p["text"] = " ".join(text.split())
        lines[i] = point_line(p)
        return "\n".join(lines), lines[i]
    return note, None


def cmd_set_point(args) -> dict:
    import datetime
    if not any(args.status == s or args.status.startswith(s + " ") for s in POINT_STATUSES):
        return {"ok": False, "error": "status", "line": "The status is one of: " + ", ".join(POINT_STATUSES) + "."}
    path = Path(args.note)
    note = path.read_text(encoding="utf-8")
    new, line = set_point(note, args.thread, args.status, args.text, datetime.date.today().isoformat())
    if line is None:
        return {"ok": False, "error": "no-point", "line": f"No Point in the record names thread {args.thread}."}
    if args.yes:
        path.write_text(new, encoding="utf-8")
    return {"ok": True, "written": bool(args.yes), "point": line,
            "line": f"Thread {args.thread}: {status_words(args.status)}." + ("" if args.yes else " Preview only; add --yes to write.")}


def cmd_reply(args) -> dict:
    """Reply inside an existing thread, then optionally set its status (1.199.0)."""
    text = decode(Path(args.file).read_bytes())
    if args.status and args.status not in STATUS_CODES:
        return {"ok": False, "error": "status", "line": "The status is one of " + ", ".join(sorted(STATUS_CODES)) + "."}
    route = _route(args, "pullRequestThreads", [f"threadId={args.thread}"])
    thread = _json(Path(args.from_file).read_bytes()) if args.from_file else _json(run_az(route))
    comments = [c for c in thread.get("comments") or [] if not c.get("isDeleted") and c.get("commentType") != "system"]
    parent = comments[-1].get("id") if comments else 1
    body = reply_body(text, parent or 1)
    link = thread_link(args, args.thread)
    then = f" and set it to {args.status}" if args.status else ""
    if not args.yes:
        return {"ok": True, "posted": False, "thread": args.thread, "body": body, "status": args.status, "link": link,
                "line": f"Preview only. Add --yes after the user's yes to post the reply in thread {args.thread}{then}."}
    fd, tmp = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(body, handle, ensure_ascii=False)
        posted = _json(run_az(_route(args, "pullRequestThreadComments", [f"threadId={args.thread}"])
                              + ["--http-method", "POST", "--in-file", tmp]))
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    out = {"ok": True, "posted": True, "thread": args.thread, "comment": posted.get("id"), "link": link,
           "line": f"Posted your reply in thread {args.thread} on PR {args.pr}."}
    if args.status:
        args.yes = True
        status = cmd_set_status(args)
        out["status"] = status.get("status")
        out["ok"] = bool(status.get("ok"))
        out["line"] = f"Posted your reply in thread {args.thread} and it now shows {status.get('status')} on the host."
    if getattr(args, "note", None):
        import datetime
        note_path = Path(args.note)
        text = note_path.read_text(encoding="utf-8")
        new, changed = mark_draft_posted(text, args.thread, datetime.date.today().isoformat())
        if changed:
            note_path.write_text(new, encoding="utf-8")
        out["note_marked"] = changed
    return out


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
    spt = sub.add_parser("set-point", help="set one PR-record Point's status by its thread (1.199.0)")
    spt.add_argument("--note", required=True)
    spt.add_argument("--thread", required=True)
    spt.add_argument("--status", required=True)
    spt.add_argument("--text")
    spt.add_argument("--yes", action="store_true")
    spt.add_argument("--pr", type=int, help="the pull request; accepted for symmetry, the note names it")
    rpl = sub.add_parser("reply")
    rpl.add_argument("--thread", required=True, type=int)
    rpl.add_argument("--file", required=True)
    rpl.add_argument("--status", help="also set the thread status after the reply, for example fixed")
    rpl.add_argument("--yes", action="store_true")
    rpl.add_argument("--note", help="the PR note whose drafted reply is marked posted after the post")
    lst.add_argument("--brief", action="store_true", help="one line per thread")
    snc = sub.add_parser("since-last")
    snc.add_argument("--note", required=True, help="the PR note; its Read line and saved description are the recorded state")
    snc.add_argument("--who", required=True, help="the name on your Read line")
    snc.add_argument("--from-dir", help="saved threads.json, iterations.json and pr.json instead of az")
    for p in (lst, cmp_, pst, prv, its, chg, sts, snc, rpl):
        _common(p)
    args = parser.parse_args(argv)
    if args.cmd == "set-point":
        result = cmd_set_point(args)
        json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0 if result.get("ok") else 2
    fill_route(args)
    try:
        result = {"list": cmd_list, "compare": cmd_compare, "post": cmd_post, "pr": cmd_pr,
                  "iterations": cmd_iterations, "changes": cmd_changes, "set-status": cmd_set_status, "reply": cmd_reply,
                  "since-last": cmd_since_last}[args.cmd](args)
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        result = {"ok": False, "error": args.cmd, "line": str(exc)}
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    sys.exit(main())
