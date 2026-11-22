#!/usr/bin/env python3
"""Reply inside a GitHub pull-request review comment (kit 1.200.0).

Preview without --yes. With --yes, post the reply and, when --resolve is
set, resolve the thread. The draft's words are what was shown on the card.
Nothing is posted until that yes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (AttributeError, OSError, ValueError):
                pass


def reply_line(thread: str, resolve: bool, posted: bool) -> str:
    then = " and set it to resolved" if resolve else ""
    if not posted:
        return f"Preview only. Add --yes after the user's yes to post the reply in thread {thread}{then}."
    if resolve:
        return f"Posted your reply in thread {thread} and it now shows resolved on the host."
    return f"Posted your reply in thread {thread}."


def card(thread: str, resolve: bool) -> dict:
    """One card. The recommended option matches the draft that will be posted."""
    if resolve:
        return {
            "question": f"Post your reply in thread {thread} and set it to resolved?",
            "options": [
                {"word": "post-and-resolve", "label": "Post and set resolved (Recommended)"},
                {"word": "leave-it", "label": "Leave it"},
            ],
        }
    return {
        "question": f"Post your reply in thread {thread}?",
        "options": [
            {"word": "post", "label": "Post the reply (Recommended)"},
            {"word": "leave-it", "label": "Leave it"},
        ],
    }


def cmd_reply(args, run=None) -> dict:
    text = Path(args.file).read_text(encoding="utf-8")
    resolve = bool(getattr(args, "resolve", False))
    out = {"ok": True, "posted": False, "thread": str(args.thread), "body": text,
           "card": card(str(args.thread), resolve), "line": reply_line(args.thread, resolve, False)}
    if not args.yes:
        return out
    owner, repo, number = args.repo.split("/", 1)[0], args.repo.split("/", 1)[1], args.pr
    route = ["api", f"repos/{owner}/{repo}/pulls/{number}/comments/{args.thread}/replies", "-f", f"body={text}"]
    if run is None:
        import subprocess
        proc = subprocess.run(["gh", *route], capture_output=True, text=True, encoding="utf-8", check=False)
        if proc.returncode != 0:
            return {"ok": False, "posted": False, "error": (proc.stderr or proc.stdout or "").strip(),
                    "line": "The reply was not posted."}
        posted = proc.stdout
    else:
        posted = run(route)
    out.update(posted=True, line=reply_line(args.thread, resolve, True), response=posted)
    if resolve:
        done = ["api", "--method", "PATCH", f"repos/{owner}/{repo}/pulls/{number}/comments/{args.thread}",
                "-f", "resolved=true"]
        if run is None:
            import subprocess
            proc = subprocess.run(["gh", *done], capture_output=True, text=True, encoding="utf-8", check=False)
            out["resolved"] = proc.returncode == 0
        else:
            run(done)
            out["resolved"] = True
    if getattr(args, "note", None):
        import datetime
        note = Path(args.note)
        body = note.read_text(encoding="utf-8")
        stamp = datetime.date.today().isoformat()
        marker = f"thread {args.thread} posted {stamp}"
        if marker not in body:
            note.write_text(body.rstrip() + f"\n\n{marker}\n", encoding="utf-8")
            out["note_marked"] = True
    return out


def main(argv=None) -> int:
    _utf8()
    parser = argparse.ArgumentParser(description="Reply to a GitHub review comment")
    sub = parser.add_subparsers(dest="cmd", required=True)
    reply = sub.add_parser("reply")
    reply.add_argument("--repo", required=True, help="owner/name")
    reply.add_argument("--pr", required=True)
    reply.add_argument("--thread", required=True)
    reply.add_argument("--file", required=True)
    reply.add_argument("--resolve", action="store_true")
    reply.add_argument("--yes", action="store_true")
    reply.add_argument("--note")
    args = parser.parse_args(argv)
    result = cmd_reply(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    sys.exit(main())
