#!/usr/bin/env python3
"""List, compare and post Azure DevOps pull-request threads (1.172.0).

    ado_threads.py list    --pr N [--project P] [--repo R] [--org URL]
    ado_threads.py compare --pr N --draft <file>
    ado_threads.py post    --pr N --file <file> [--yes]

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


def _route(args) -> list[str]:
    route = [f"pullRequestId={args.pr}"]
    if args.project:
        route.append(f"project={args.project}")
    if args.repo:
        route.append(f"repositoryId={args.repo}")
    out = ["devops", "invoke", "--area", "git", "--resource", "pullRequestThreads",
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
            })
        if not comments:
            continue
        status = thread.get("status")
        out.append({
            "thread": thread.get("id"),
            "status": STATUS.get(status, status) if isinstance(status, int) else (status or ""),
            "file": ((thread.get("threadContext") or {}).get("filePath")) or None,
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


def _common(p) -> None:
    p.add_argument("--pr", required=True, type=int)
    p.add_argument("--project")
    p.add_argument("--repo")
    p.add_argument("--org")
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
    for p in (lst, cmp_, pst):
        _common(p)
    args = parser.parse_args(argv)
    try:
        result = {"list": cmd_list, "compare": cmd_compare, "post": cmd_post}[args.cmd](args)
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        result = {"ok": False, "error": args.cmd, "line": str(exc)}
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    sys.exit(main())
