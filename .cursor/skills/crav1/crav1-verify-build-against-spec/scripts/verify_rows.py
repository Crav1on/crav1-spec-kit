#!/usr/bin/env python3
"""Scoped verify and row updates for verify.md (1.172.0).

    verify_rows.py scope --file verify.md --repo <code repo> [--stamp <hash>]
    verify_rows.py set   --file verify.md --task T6 --status "Implemented, verified"
                         --evidence "..." [--branch <b> --tip <sha>] [--yes]

`scope` says which rows to verify again: a row whose branch or tip moved
since the last verify, a row with no recorded tip, or every row when the
spec stamp (a hash of spec.md, plan.md and tasks.md, checkboxes ignored) changed. The
rest are kept, and `kept_line` says which. `set` writes one overview row,
recounts the TL;DR table, and records the row's branch and tip under
`## Row tips`, so rows are not edited by hand. Nothing is written without
`--yes`. Output is one JSON object; errors have `ok: false`.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

STATUSES = (
    "Implemented, verified",
    "Implemented, verified, tick pending",
    "Implemented, verify failed",
    "Not implemented",
    "Claimed done, unverified",
)
ROW = re.compile(r"^\|\s*(T\d+)\s*\|(.*)$")
TIP = re.compile(r"^- (T\d+): (\S+) ([0-9a-f]{7,40})$")
TIPS_HEAD = "## Row tips"


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass


def overview_rows(text: str) -> dict:
    """T# -> [title, status, verify] from the overview table."""
    out = {}
    for line in text.splitlines():
        match = ROW.match(line)
        if not match:
            continue
        cells = [c.strip() for c in match.group(2).rstrip().rstrip("|").split("|")]
        if len(cells) >= 3 and cells[1] in STATUSES:
            out.setdefault(match.group(1), cells[:3])
    return out


def read_tips(text: str) -> dict:
    tips = {"stamp": None, "rows": {}}
    if TIPS_HEAD not in text:
        return tips
    section = text.split(TIPS_HEAD, 1)[1].split("\n## ", 1)[0]
    for line in section.splitlines():
        line = line.strip()
        if line.startswith("Spec stamp:"):
            tips["stamp"] = line.split(":", 1)[1].strip() or None
        match = TIP.match(line)
        if match:
            tips["rows"][match.group(1)] = {"branch": match.group(2), "tip": match.group(3)}
    return tips


def write_tips(text: str, tips: dict) -> str:
    lines = [TIPS_HEAD, "", "Written by `scripts/verify_rows.py`. A row whose branch and tip did not move is kept on the next verify."]
    if tips.get("stamp"):
        lines += ["", f"Spec stamp: {tips['stamp']}"]
    lines.append("")
    for task in sorted(tips["rows"], key=lambda t: int(t[1:])):
        row = tips["rows"][task]
        lines.append(f"- {task}: {row['branch']} {row['tip']}")
    block = "\n".join(lines).rstrip() + "\n"
    if TIPS_HEAD in text:
        before, rest = text.split(TIPS_HEAD, 1)
        after = rest.split("\n## ", 1)
        tail = ("\n## " + after[1]) if len(after) > 1 else ""
        return before + block + tail
    return text.rstrip() + "\n\n" + block


def recount(text: str) -> str:
    rows = overview_rows(text)
    out = []
    for line in text.splitlines():
        match = re.match(r"^\|\s*([^|]+?)\s*\|\s*\d+\s*\|[^|]*\|\s*$", line)
        if match and match.group(1) in STATUSES:
            label = match.group(1)
            ids = [t for t, cells in rows.items() if cells[1] == label]
            ids.sort(key=lambda t: int(t[1:]))
            line = f"| {label} | {len(ids)} | {', '.join(ids)} |"
        out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def set_row(text: str, task: str, status: str, evidence: str) -> str:
    out = []
    found = False
    for line in text.splitlines():
        match = ROW.match(line)
        if match and match.group(1) == task and not found:
            cells = [c.strip() for c in match.group(2).rstrip().rstrip("|").split("|")]
            if len(cells) >= 3 and cells[1] in STATUSES:
                cells[1] = status
                cells[2] = evidence.replace("|", "\\|").replace("\n", " ")
                line = f"| {task} | " + " | ".join(cells) + " |"
                found = True
        out.append(line)
    if not found:
        raise KeyError(task)
    return recount("\n".join(out) + ("\n" if text.endswith("\n") else ""))


def spec_stamp(folder: Path) -> str:
    """Hash of spec.md, plan.md and tasks.md, line endings and checkboxes ignored."""
    import hashlib

    parts = []
    for name in ("spec.md", "plan.md", "tasks.md"):
        path = Path(folder) / name
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        text = text.replace("\r\n", "\n")
        text = re.sub(r"^(\s*- )\[[ xX]\]", r"\1[ ]", text, flags=re.M)
        parts.append(text.strip())
    return hashlib.sha256("\n\0".join(parts).encode("utf-8")).hexdigest()[:12]


def git_tip(repo: str, branch: str) -> str | None:
    for ref in (f"origin/{branch}", branch):
        try:
            done = subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref], cwd=repo, capture_output=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            return None
        if done.returncode == 0:
            return done.stdout.decode("utf-8", errors="replace").strip()
    return None


def scope(text: str, current: dict, stamp: str | None = None) -> dict:
    """current: T# -> tip sha now (None when unknown)."""
    rows = overview_rows(text)
    tips = read_tips(text)
    stamp_moved = bool(stamp and tips.get("stamp") and stamp != tips["stamp"])
    rerun, kept = [], []
    for task in sorted(rows, key=lambda t: int(t[1:])):
        old = tips["rows"].get(task)
        now = current.get(task)
        if stamp_moved or not old or not now or not now.startswith(old["tip"]) and not old["tip"].startswith(now):
            rerun.append(task)
        else:
            kept.append(task)
    if stamp_moved:
        why = "The spec, plan or tasks changed since the last verify, so every row is verified again."
    elif kept:
        why = f"Kept from the last verify: {', '.join(kept)} (branch and tip unchanged)."
    else:
        why = "Every row is verified again."
    return {"rerun": rerun, "kept": kept, "stamp_moved": stamp_moved, "kept_line": why}


def main(argv: list[str] | None = None) -> int:
    _utf8_stdout()
    parser = argparse.ArgumentParser(description="Scoped verify rows")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("scope")
    sc.add_argument("--file", required=True)
    sc.add_argument("--repo", default=".")
    sc.add_argument("--stamp", help="defaults to the spec stamp of the verify.md folder")
    sc.add_argument("--tips-json", help="T# -> sha, instead of reading git")
    st = sub.add_parser("set")
    st.add_argument("--file", required=True)
    st.add_argument("--task", required=True)
    st.add_argument("--status", required=True, choices=STATUSES)
    st.add_argument("--evidence", required=True)
    st.add_argument("--branch")
    st.add_argument("--tip")
    st.add_argument("--yes", action="store_true")
    args = parser.parse_args(argv)
    path = Path(args.file)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return _out({"ok": False, "error": "file", "line": str(exc)})
    task = "T" + str(int(re.sub(r"^[Tt]", "", args.task))) if args.cmd == "set" else None
    if args.cmd == "scope":
        if args.tips_json:
            current = json.loads(Path(args.tips_json).read_text(encoding="utf-8"))
        else:
            current = {t: git_tip(args.repo, row["branch"]) for t, row in read_tips(text)["rows"].items()}
        result = scope(text, current, args.stamp or spec_stamp(path.parent))
        result["ok"] = True
        return _out(result)
    try:
        new = set_row(text, task, args.status, args.evidence)
    except KeyError:
        return _out({"ok": False, "error": "task", "line": f"{task} has no row in the overview table."})
    if args.branch and args.tip:
        tips = read_tips(new)
        tips["rows"][task] = {"branch": args.branch, "tip": args.tip[:12]}
        tips["stamp"] = spec_stamp(path.parent)
        new = write_tips(new, tips)
    wrote = False
    if args.yes:
        path.write_text(new, encoding="utf-8", newline="\n")
        wrote = True
    return _out({"ok": True, "wrote": wrote, "task": task, "status": args.status,
                 "line": f"Wrote the {task} row." if wrote else "Preview only. Add --yes to write the row."})


def _out(payload: dict) -> int:
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if payload.get("ok") else 2


if __name__ == "__main__":
    sys.exit(main())
