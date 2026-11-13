#!/usr/bin/env python3
"""Build-walk claims: a pushed in-progress line other sessions can see (1.151.0).

The file is docs/specs/<slug>/claims.md. It is a dedicated file so a ready
check can rewrite build-map.md without dropping the claim, and so a claim
can be committed and pushed on its own after yes. walk-progress.md and
build-progress/ record walk position, not a shared lock.

A line is:

    In progress: feat/orders-api-host-setup, T27, person A, since 2026-11-13T15:50:00+01:00

Several T#s on one branch may share a line: T3, T27. Claims older than the
max age (default 3 days, or Claim max age: N days in the file, or
--age-days) get a warning. They are never cleared on their own.

Normalized content stamps ignore In progress: and Claim max age: lines.
Tighten-and-plan, plan-from-spec, and tighten-plan run preserve so a claimed
task line is not renumbered, reordered, rewritten, or removed.

Usage: claims.py <add|clear|list|preserve|stamp-strip> [options]
The interpreter is crav1-docs/reference/running-scripts.md. The kit wrapper
is scripts/claims.py. This script does not push.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_AGE_DAYS = 3
CLAIMS_NAME = "claims.md"
CLAIM_LINE = re.compile(
    r"^In progress:\s*(?P<branch>\S+),\s*(?P<tasks>T?\d+(?:\s*,\s*T?\d+)*),\s*"
    r"(?P<user>.+),\s*since\s+(?P<since>\S.*?)\s*$",
    re.I,
)
AGE_LINE = re.compile(r"^Claim max age:\s*(\d+)\s*days?\s*$", re.I)
IN_PROGRESS_LINE = re.compile(r"^\s*In progress:\s+", re.I)
AGE_OR_TITLE = re.compile(r"^\s*(?:#\s*Claims\s*|Claim max age:\s*)", re.I)
TASK_LINE = re.compile(r"^(\s*- \[(?: |x|X)\] T)(\d+)(\b[:.]?\s*.*)$", re.I)
TASK_ID = re.compile(r"T?(\d+)$", re.I)


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


def fail(code: str, line: str, status: int = 2) -> int:
    return emit({"ok": False, "code": code, "line": line}, status)


def task_token(value) -> str:
    if value is None:
        raise ValueError("missing task id")
    text = str(value).strip()
    match = re.match(r"^T?(\d+)$", text, re.I)
    if not match:
        raise ValueError(f"not a task id: {value}")
    return f"T{int(match.group(1))}"


def task_tokens(values) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        parts = [part.strip() for part in values.replace(";", ",").split(",")]
        values = [part for part in parts if part]
    out: list[str] = []
    for item in values:
        token = task_token(item)
        if token not in out:
            out.append(token)
    return out


def parse_when(value: str) -> datetime:
    text = (value or "").strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    when = datetime.fromisoformat(text)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when


def format_when(when: datetime) -> str:
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when.isoformat()


def date_of(when: datetime) -> str:
    return when.date().isoformat()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def strip_claim_lines(text: str) -> str:
    """Drop In progress: and Claim max age: lines. Used by content stamps."""
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    kept = [
        line
        for line in text.split("\n")
        if not IN_PROGRESS_LINE.match(line) and not AGE_LINE.match(line.strip())
    ]
    return "\n".join(kept)


def claims_path(root: Path) -> Path:
    return Path(root) / CLAIMS_NAME


def _blank_document(age_days: int | None = None) -> str:
    lines = ["# Claims", ""]
    if age_days is not None and age_days != DEFAULT_AGE_DAYS:
        lines.append(f"Claim max age: {age_days} days")
        lines.append("")
    return "\n".join(lines)


def parse_claims(text: str, now: datetime | None = None, age_days: int | None = None) -> dict:
    """Parse a claims.md body. Unknown lines are kept as notes."""
    now = now or now_utc()
    file_age = None
    claims: list[dict] = []
    notes: list[str] = []
    for raw in (text or "").splitlines():
        stripped = raw.strip()
        if not stripped or stripped == "# Claims":
            continue
        age_match = AGE_LINE.match(stripped)
        if age_match:
            file_age = int(age_match.group(1))
            continue
        match = CLAIM_LINE.match(stripped)
        if not match:
            notes.append(raw)
            continue
        try:
            tasks = task_tokens(match.group("tasks"))
            when = parse_when(match.group("since"))
        except ValueError:
            notes.append(raw)
            continue
        claims.append({
            "branch": match.group("branch").strip(),
            "tasks": tasks,
            "user": match.group("user").strip(),
            "since": format_when(when),
            "when": when,
        })
    max_age = age_days if age_days is not None else (file_age if file_age is not None else DEFAULT_AGE_DAYS)
    for claim in claims:
        age = now - claim["when"]
        days = age.total_seconds() / 86400
        claim["age_days"] = days
        claim["stale"] = days > max_age
        claim["since_date"] = date_of(claim["when"])
        claim["phrase"] = (
            f"in progress by {claim['user']} since {claim['since_date']}"
        )
    public = [{k: v for k, v in claim.items() if k != "when"} for claim in claims]
    return {
        "claims": public,
        "raw": claims,
        "notes": notes,
        "max_age_days": max_age,
        "file_age_days": file_age,
    }


def render_claims(claims: list[dict], age_days: int | None = None, notes: list[str] | None = None) -> str:
    lines = ["# Claims", ""]
    if age_days is not None and age_days != DEFAULT_AGE_DAYS:
        lines.append(f"Claim max age: {age_days} days")
        lines.append("")
    for claim in claims:
        tasks = ", ".join(claim["tasks"])
        since = claim.get("since") or format_when(claim["when"])
        lines.append(
            f"In progress: {claim['branch']}, {tasks}, {claim['user']}, since {since}"
        )
    if notes:
        if lines[-1] != "":
            lines.append("")
        lines.extend(notes)
    if lines[-1] != "":
        lines.append("")
    return "\n".join(lines)


def load_claims(root: Path, now: datetime | None = None, age_days: int | None = None) -> dict:
    path = claims_path(root)
    if not path.is_file():
        max_age = age_days if age_days is not None else DEFAULT_AGE_DAYS
        return {
            "claims": [],
            "raw": [],
            "notes": [],
            "max_age_days": max_age,
            "file_age_days": None,
            "path": str(path),
            "exists": False,
        }
    parsed = parse_claims(path.read_text(encoding="utf-8"), now=now, age_days=age_days)
    parsed["path"] = str(path)
    parsed["exists"] = True
    return parsed


def write_claims(root: Path, claims: list[dict], age_days: int | None = None, notes: list[str] | None = None) -> Path:
    path = claims_path(root)
    if not claims and not (age_days is not None and age_days != DEFAULT_AGE_DAYS) and not notes:
        if path.is_file():
            path.unlink()
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_claims(claims, age_days=age_days, notes=notes), encoding="utf-8")
    return path


def claim_for(claims: list[dict], task: str) -> dict | None:
    token = task_token(task)
    for claim in claims:
        if token in claim["tasks"]:
            return claim
    return None


def claimed_ids(claims: list[dict]) -> list[str]:
    out: list[str] = []
    for claim in claims:
        for task in claim["tasks"]:
            if task not in out:
                out.append(task)
    return out


def age_warnings(claims: list[dict], max_age: int = DEFAULT_AGE_DAYS) -> list[str]:
    warnings = []
    for claim in claims:
        if not claim.get("stale"):
            continue
        days = int(claim["age_days"]) if "age_days" in claim else max_age
        tasks = ", ".join(claim["tasks"])
        warnings.append(
            f"Warning: {tasks} has been in progress by {claim['user']} since "
            f"{claim['since_date']} ({days} days, over the {max_age}-day mark). "
            "It is not cleared. To release it, say release claim."
        )
    return warnings


def add_claim(
    root: Path,
    branch: str,
    tasks,
    user: str,
    since: datetime | None = None,
    age_days: int | None = None,
    now: datetime | None = None,
) -> dict:
    """Add or refresh a claim. Another user's claim on the same task is refused."""
    now = now or now_utc()
    when = since or now
    tokens = task_tokens(tasks)
    if not tokens:
        return {"ok": False, "code": "tasks", "line": "a claim needs at least one T#"}
    branch = (branch or "").strip()
    user = (user or "").strip()
    if not branch:
        return {"ok": False, "code": "branch", "line": "a claim needs a branch"}
    if not user:
        return {"ok": False, "code": "user", "line": "a claim needs a user"}
    loaded = load_claims(root, now=now, age_days=age_days)
    kept: list[dict] = []
    conflicts = []
    for claim in loaded["claims"]:
        overlap = [task for task in tokens if task in claim["tasks"]]
        if not overlap:
            kept.append(claim)
            continue
        if claim["user"] != user:
            conflicts.append({"tasks": overlap, "claim": claim})
            kept.append(claim)
            continue
        remain = [task for task in claim["tasks"] if task not in tokens]
        if remain:
            kept.append({**claim, "tasks": remain})
    if conflicts:
        who = conflicts[0]["claim"]["user"]
        held = ", ".join(conflicts[0]["tasks"])
        return {
            "ok": False,
            "code": "claimed",
            "line": f"{held} is in progress by {who} since {conflicts[0]['claim']['since_date']}",
            "conflicts": conflicts,
            "claims": loaded["claims"],
        }
    added = {
        "branch": branch,
        "tasks": tokens,
        "user": user,
        "since": format_when(when),
        "when": when,
        "since_date": date_of(when),
        "age_days": 0.0,
        "stale": False,
        "phrase": f"in progress by {user} since {date_of(when)}",
    }
    # Merge with an existing same-branch, same-user, same-time claim.
    merged = False
    out = []
    for claim in kept:
        if (
            claim["branch"] == branch
            and claim["user"] == user
            and claim["since"] == added["since"]
        ):
            tasks_all = list(claim["tasks"])
            for task in tokens:
                if task not in tasks_all:
                    tasks_all.append(task)
            out.append({**claim, "tasks": tasks_all})
            merged = True
        else:
            out.append(claim)
    if not merged:
        out.append(added)
    max_age = age_days if age_days is not None else loaded["max_age_days"]
    file_age = max_age if max_age != DEFAULT_AGE_DAYS else loaded["file_age_days"]
    path = write_claims(root, out, age_days=file_age, notes=loaded["notes"])
    parsed = load_claims(root, now=now, age_days=age_days)
    return {
        "ok": True,
        "action": "add",
        "path": str(path),
        "added": {k: v for k, v in added.items() if k != "when"},
        "claims": parsed["claims"],
        "warnings": age_warnings(parsed["claims"], parsed["max_age_days"]),
        "commit_message": f"Claim {', '.join(tokens)} on {branch}",
        "card": {
            "words": ["yes", "stop"],
            "recommended": "yes",
            "action": "commit and push claims.md only",
        },
    }


def clear_claim(
    root: Path,
    branch: str | None = None,
    tasks=None,
    age_days: int | None = None,
    now: datetime | None = None,
) -> dict:
    now = now or now_utc()
    tokens = task_tokens(tasks) if tasks else []
    branch = (branch or "").strip() or None
    loaded = load_claims(root, now=now, age_days=age_days)
    if not loaded["claims"]:
        return {
            "ok": True,
            "action": "clear",
            "path": loaded["path"],
            "cleared": [],
            "claims": [],
            "commit_message": "Clear the build-walk claim",
            "card": {
                "words": ["yes", "stop"],
                "recommended": "yes",
                "action": "commit and push the cleared claims.md",
            },
        }
    cleared: list[dict] = []
    kept: list[dict] = []
    for claim in loaded["claims"]:
        if branch and claim["branch"] != branch:
            kept.append(claim)
            continue
        if tokens:
            hit = [task for task in claim["tasks"] if task in tokens]
            remain = [task for task in claim["tasks"] if task not in tokens]
            if hit:
                cleared.append({**claim, "tasks": hit})
            if remain:
                kept.append({**claim, "tasks": remain})
            elif not hit and not branch:
                kept.append(claim)
            continue
        if branch or not tokens:
            if branch is None and tokens:
                kept.append(claim)
                continue
            # clear this claim (matching branch, or all when neither filter?)
            # When only --branch, clear that branch. When no branch and no
            # tasks, refuse: too broad, except --all.
            cleared.append(claim)
            continue
        kept.append(claim)
    if not branch and not tokens:
        return {
            "ok": False,
            "code": "clear",
            "line": "name a branch, a T#, or pass --all to clear every claim",
        }
    file_age = loaded["file_age_days"]
    path = write_claims(root, kept, age_days=file_age, notes=loaded["notes"])
    parsed = load_claims(root, now=now, age_days=age_days)
    labels = []
    for item in cleared:
        labels.extend(item["tasks"])
    named = ", ".join(labels) if labels else (branch or "claims")
    return {
        "ok": True,
        "action": "clear",
        "path": str(path),
        "cleared": cleared,
        "claims": parsed["claims"],
        "commit_message": f"Clear the claim on {named}",
        "card": {
            "words": ["yes", "stop"],
            "recommended": "yes",
            "action": "commit and push the cleared claims.md",
        },
    }


def clear_all(root: Path, age_days: int | None = None, now: datetime | None = None) -> dict:
    now = now or now_utc()
    loaded = load_claims(root, now=now, age_days=age_days)
    path = write_claims(root, [], age_days=None, notes=None)
    return {
        "ok": True,
        "action": "clear",
        "path": str(path),
        "cleared": loaded["claims"],
        "claims": [],
        "commit_message": "Clear the build-walk claims",
        "card": {
            "words": ["yes", "stop"],
            "recommended": "yes",
            "action": "commit and push the cleared claims.md",
        },
    }


def apply_to_rows(rows: list[dict], claims: list[dict]) -> list[dict]:
    """Mark claimed, unfinished tasks as held in progress. Mutates rows."""
    by_task = {}
    for claim in claims:
        for task in claim["tasks"]:
            by_task[task] = claim
    for row in rows:
        task = row.get("task")
        if not task or task not in by_task:
            continue
        if row.get("bucket") == "done":
            continue
        claim = by_task[task]
        row["bucket"] = "waiting"
        row["held"] = True
        row["claim"] = True
        row["reason"] = claim["phrase"]
        row["who"] = claim["user"]
        row["claim_since"] = claim.get("since")
        row["claim_stale"] = bool(claim.get("stale"))
    return rows


def _task_map(text: str) -> dict[str, tuple[int, str]]:
    found = {}
    for index, line in enumerate((text or "").splitlines()):
        match = TASK_LINE.match(line)
        if match:
            found[f"T{int(match.group(2))}"] = (index, line)
    return found


def _ends_nl(text: str) -> bool:
    return bool(text) and text.endswith("\n")


def preserve_claimed(before: str, after: str, claimed: list[str]) -> dict:
    """Restore claimed task lines: no renumber, reorder, rewrite, or removal.

    The exact original line comes back. A claimed T# that was dropped is
    reinserted next to the previous surviving neighbor, or at its old index.
    A line whose T# changed but whose body matches a claimed line is the
    original T# again. Other tasks may change. The reply lists the kept ids.
    """
    tokens = task_tokens(claimed)
    if not tokens:
        return {"ok": True, "text": after, "kept": [], "changed": False, "line": "no claimed tasks were kept"}
    before_lines = (before or "").splitlines()
    after_lines = (after or "").splitlines()
    original = _task_map(before)
    claimed_set = [token for token in tokens if token in original]
    if not claimed_set:
        return {"ok": True, "text": after, "kept": [], "changed": False, "line": "no claimed tasks were kept"}

    bodies = {}
    for token in claimed_set:
        _idx, line = original[token]
        match = TASK_LINE.match(line)
        if match:
            bodies[match.group(3)] = token

    rewritten = list(after_lines)
    for index, line in enumerate(rewritten):
        match = TASK_LINE.match(line)
        if not match:
            continue
        new_id = f"T{int(match.group(2))}"
        body = match.group(3)
        if new_id in claimed_set:
            rewritten[index] = original[new_id][1]
            continue
        owner = bodies.get(body)
        if owner and owner in claimed_set and new_id not in claimed_set:
            rewritten[index] = original[owner][1]

    present = set(_task_map("\n".join(rewritten)))
    missing = [token for token in claimed_set if token not in present]
    for token in missing:
        old_index, line = original[token]
        insert_at = None
        for prior in range(old_index - 1, -1, -1):
            prior_match = TASK_LINE.match(before_lines[prior])
            if not prior_match:
                continue
            prior_id = f"T{int(prior_match.group(2))}"
            current = _task_map("\n".join(rewritten))
            if prior_id in current:
                insert_at = current[prior_id][0] + 1
                break
        if insert_at is None:
            insert_at = min(old_index, len(rewritten))
        rewritten.insert(insert_at, line)

    current = _task_map("\n".join(rewritten))
    claimed_positions = [(current[token][0], token) for token in claimed_set if token in current]
    expected_order = list(claimed_set)
    actual_order = [token for _idx, token in sorted(claimed_positions)]
    if actual_order != expected_order:
        positions = sorted(idx for idx, _token in claimed_positions)
        for position, token in zip(positions, expected_order):
            rewritten[position] = original[token][1]

    text_out = "\n".join(rewritten)
    if _ends_nl(after) or (not after and _ends_nl(before)):
        text_out = text_out + "\n"
    kept_line = "Kept claimed tasks: " + ", ".join(claimed_set) + "."
    return {
        "ok": True,
        "text": text_out,
        "kept": claimed_set,
        "changed": text_out != after,
        "line": kept_line,
    }


def cmd_add(args: argparse.Namespace) -> int:
    if getattr(args, "headless", False) and not getattr(args, "yes", False):
        return fail("headless", "a headless run stops. The words are yes and stop.")
    try:
        result = add_claim(
            Path(args.root),
            args.branch,
            args.tasks,
            args.user,
            since=parse_when(args.since) if args.since else None,
            age_days=args.age_days,
        )
    except ValueError as exc:
        return fail("tasks", str(exc))
    return emit(result, 0 if result.get("ok") else 2)


def cmd_clear(args: argparse.Namespace) -> int:
    if getattr(args, "headless", False) and not getattr(args, "yes", False):
        return fail("headless", "a headless run stops. The words are yes, stop, and release claim.")
    if args.all:
        result = clear_all(Path(args.root), age_days=args.age_days)
    else:
        try:
            result = clear_claim(
                Path(args.root),
                branch=args.branch,
                tasks=args.tasks,
                age_days=args.age_days,
            )
        except ValueError as exc:
            return fail("tasks", str(exc))
    return emit(result, 0 if result.get("ok") else 2)


def cmd_list(args: argparse.Namespace) -> int:
    now = parse_when(args.now) if args.now else now_utc()
    loaded = load_claims(Path(args.root), now=now, age_days=args.age_days)
    warnings = age_warnings(loaded["claims"], loaded["max_age_days"])
    return emit({
        "ok": True,
        "path": loaded["path"],
        "exists": loaded["exists"],
        "claims": loaded["claims"],
        "ids": claimed_ids(loaded["claims"]),
        "max_age_days": loaded["max_age_days"],
        "warnings": warnings,
    })


def cmd_preserve(args: argparse.Namespace) -> int:
    before = Path(args.before).read_text(encoding="utf-8")
    after_path = Path(args.after)
    after = after_path.read_text(encoding="utf-8")
    if args.tasks:
        try:
            claimed = task_tokens(args.tasks)
        except ValueError as exc:
            return fail("tasks", str(exc))
    else:
        loaded = load_claims(Path(args.root) if args.root else after_path.parent)
        claimed = claimed_ids(loaded["claims"])
    result = preserve_claimed(before, after, claimed)
    if args.write and result.get("changed"):
        after_path.write_text(result["text"], encoding="utf-8")
        result["wrote"] = str(after_path)
    return emit(result)


def cmd_stamp_strip(args: argparse.Namespace) -> int:
    text = Path(args.path).read_text(encoding="utf-8") if args.path else sys.stdin.read()
    stripped = strip_claim_lines(text)
    if args.write and args.path:
        Path(args.path).write_text(stripped, encoding="utf-8")
    return emit({"ok": True, "text": stripped, "changed": stripped != text.replace("\r\n", "\n").replace("\r", "\n")})


def _tasks_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--tasks", default=None, help="T# or a comma-separated list")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    add_p = sub.add_parser("add")
    add_p.add_argument("--root", required=True)
    add_p.add_argument("--branch", required=True)
    add_p.add_argument("--tasks", required=True)
    add_p.add_argument("--user", required=True)
    add_p.add_argument("--since", default=None)
    add_p.add_argument("--age-days", type=int, default=None)
    add_p.add_argument("--yes", action="store_true")
    add_p.add_argument("--headless", action="store_true")
    add_p.set_defaults(func=cmd_add)

    clear_p = sub.add_parser("clear")
    clear_p.add_argument("--root", required=True)
    clear_p.add_argument("--branch", default=None)
    _tasks_arg(clear_p)
    clear_p.add_argument("--all", action="store_true")
    clear_p.add_argument("--age-days", type=int, default=None)
    clear_p.add_argument("--yes", action="store_true")
    clear_p.add_argument("--headless", action="store_true")
    clear_p.set_defaults(func=cmd_clear)

    list_p = sub.add_parser("list")
    list_p.add_argument("--root", required=True)
    list_p.add_argument("--now", default=None)
    list_p.add_argument("--age-days", type=int, default=None)
    list_p.set_defaults(func=cmd_list)

    pres = sub.add_parser("preserve")
    pres.add_argument("--before", required=True)
    pres.add_argument("--after", required=True)
    pres.add_argument("--root", default=None)
    pres.add_argument("--tasks", default=None)
    pres.add_argument("--write", action="store_true")
    pres.set_defaults(func=cmd_preserve)

    strip_p = sub.add_parser("stamp-strip")
    strip_p.add_argument("--path", default=None)
    strip_p.add_argument("--write", action="store_true")
    strip_p.set_defaults(func=cmd_stamp_strip)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
