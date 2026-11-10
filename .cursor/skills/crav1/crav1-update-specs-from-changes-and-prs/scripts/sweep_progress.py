#!/usr/bin/env python3
"""Progress file for /crav1-update-specs-from-changes-and-prs (kit 1.124.0).

The script is the state machine for one sweep. It does not fetch, does not
read a host, and does not edit a spec, a note, or repos.md. The skill does
that work and records the result here. The only file it writes is
docs/system/sweep-progress.md, and only with --yes.

Commands (JSON on stdout):

  scope --root <specs-repo> --specs-url <url> [--repo <name>]
  start --root <specs-repo> --flow manual-flow|auto-flow --specs-url <url>
      [--repo <name>] [--budget <minutes>] [--include-specs-comments yes|no]
      [--when <timestamp>] [--replace] --yes
  note-fetch --root <specs-repo> --repo <name>
      --result ok|local|failed|missing|signed-out
      [--open <n,n>] [--detail <text>] [--when <timestamp>] --yes
  add-item --root <specs-repo> --kind branch|pr --repo <name> --ref <ref>
      [--draft] [--closed-since] [--head-branch <branch>] --yes
  drop --root <specs-repo> --id <id> --yes
  begin-item --root <specs-repo> --id <id> [--now <timestamp>] --yes
  complete --root <specs-repo> --id <id>
      --outcome notes|synced-at|notes+synced-at|proposal|spec
      [--slug <slug[,slug]>] [--conflict] [--question] [--proposal <text>]
      [--now <timestamp>] --yes
  skip --root <specs-repo> --id <id> --reason <text> [--waiting]
      [--now <timestamp>] --yes
  pause --root <specs-repo> --yes
  finish --root <specs-repo> --yes
  resume --root <specs-repo> [--now <timestamp>]
  ending --root <specs-repo> [--files <n>] [--now <timestamp>]
  budget --root <specs-repo> [--now <timestamp>]
  read-line --head <sha> --push <n> --comment-time <token> --date <YYYY-MM-DD>

A write without --yes prints needs-yes and exits 2. A budget stop exits 3.
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


_utf8_stdout()

sys.dont_write_bytecode = True  # before any sibling import; no __pycache__ in the project (1.121.1)

PROGRESS_NAME = "sweep-progress.md"
DEFAULT_BUDGET_MINUTES = 20
HARD_STOP_MINUTES = 45  # well under the 50 minute cap
FLOWS = ("manual-flow", "auto-flow")
FETCH_RESULTS = ("ok", "local", "failed", "missing", "signed-out")
FETCH_BLOCKS = {"failed": "fetch failed", "missing": "no checkout"}
OUTCOMES = ("notes", "synced-at", "notes+synced-at", "proposal", "spec")
ITEM_STATUSES = ("pending", "current", "done", "collected", "dropped", "skipped")
BASE_NAMES = {"main", "master", "develop"}
HEADER_KEYS = (
    "Flow",
    "Scope",
    "Specs repo",
    "Specs comments",
    "Budget minutes",
    "Hard stop minutes",
    "Started",
    "Status",
    "Current",
    "Inventory at",
)
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SLUG_RE = re.compile(r"^[a-z0-9-]+$")
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WHEN_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$")


def emit(payload: dict, code: int) -> None:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    raise SystemExit(code)


def fail(error: str, message: str, code: int = 1) -> None:
    emit({"ok": False, "error": error, "message": message}, code)


def need_yes(args: argparse.Namespace) -> None:
    if not args.yes:
        fail("needs-yes", "Pass --yes to write docs/system/sweep-progress.md.", 2)


def parse_when(text: str) -> datetime:
    raw = text.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        fail("when", f"Timestamp {text!r} is not ISO 8601.")
    if parsed.tzinfo is None:
        fail("when", "Timestamp needs a timezone offset.")
    return parsed


def now_or(text: str | None) -> datetime:
    if text:
        return parse_when(text)
    return datetime.now(timezone.utc)


def stamp(moment: datetime) -> str:
    rendered = moment.isoformat(timespec="seconds")
    if not WHEN_RE.fullmatch(rendered):
        fail("when", f"Timestamp {rendered} is not a full offset timestamp.")
    return rendered


def plain(text: str, field: str, limit: int = 500) -> str:
    cleaned = " ".join(text.split())
    if not cleaned or "|" in cleaned:
        fail(field, f"{field} needs text without a '|' or a line break.")
    if len(cleaned) > limit:
        fail(field, f"{field} is longer than {limit} characters.")
    return cleaned


def canonical_url(url: str) -> str:
    text = url.strip().rstrip("/")
    if text.lower().endswith(".git"):
        text = text[:-4]
    ssh = re.match(r"(?i)git@github\.com:(.+)$", text)
    if ssh:
        text = "https://github.com/" + ssh.group(1)
    ssh_url = re.match(r"(?i)ssh://git@github\.com/(.+)$", text)
    if ssh_url:
        text = "https://github.com/" + ssh_url.group(1)
    azure = re.match(r"(?i)https://dev\.azure\.com/([^/]+)(.*)$", text)
    if azure:
        text = f"https://{azure.group(1)}.visualstudio.com{azure.group(2)}"
    return text.lower()


def host_of(url: str) -> str:
    folded = canonical_url(url)
    if "github.com" in folded:
        return "github"
    if "visualstudio.com" in folded or "dev.azure.com" in folded:
        return "azure"
    return "other"


def parse_repos(text: str) -> list[dict]:
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells:
            continue
        if all(cell and set(cell) <= set("-: ") for cell in cells):
            continue
        if cells[0] in {"", "Repo"}:
            continue
        while len(cells) < 6:
            cells.append("")
        name, _purpose, status, url, merges, _work = cells[:6]
        if not NAME_RE.fullmatch(name):
            continue
        rows.append(
            {
                "name": name,
                "status": status,
                "url": url.strip(),
                "merges_into": merges.strip(),
            }
        )
    return rows


def load_repos(root) -> list[dict]:
    path = root / "docs" / "system" / "repos.md"
    if not path.is_file():
        fail("no-repos", "docs/system/repos.md is missing.")
    return parse_repos(path.read_text(encoding="utf-8"))


def find_specs(rows: list[dict], specs_url: str) -> dict | None:
    want = canonical_url(specs_url)
    if not want:
        fail("specs-url", "Name the specs repo URL.")
    matches = [row for row in rows if row["url"] and canonical_url(row["url"]) == want]
    if len(matches) > 1:
        fail("specs-url-matches-several", "More than one repos.md row matches the specs repo URL.")
    return matches[0] if matches else None


def row_reason(row: dict) -> str | None:
    if row["status"].strip().lower() == "proposed":
        return "proposed"
    if not row["url"].strip():
        return "no url"
    return None


def is_base_branch(ref: str, merges_into: str) -> bool:
    if ref in BASE_NAMES or ref.startswith("release/"):
        return True
    return bool(merges_into) and ref == merges_into


def progress_path(root):
    return root / "docs" / "system" / PROGRESS_NAME


def blank_state() -> dict:
    return {
        "header": {key: "-" for key in HEADER_KEYS},
        "repos": [],
        "items": [],
        "proposals": [],
        "waiting": [],
        "last_inventory_at": "-",
        "last_open": [],
    }


def render(state: dict) -> str:
    lines = ["# Sweep progress", ""]
    for key in HEADER_KEYS:
        lines.append(f"{key}: {state['header'][key]}")
    lines += ["", "## Repos", ""]
    for repo in sorted(state["repos"], key=lambda row: row["name"].lower()):
        lines.append(
            f"- {repo['name']} | {repo['result']} | {repo['when']} | open {repo['open']} | {repo['detail']}"
        )
    lines += ["", "## Items", ""]
    for item in sorted(state["items"], key=lambda row: row["id"].lower()):
        lines.append(
            " | ".join(
                [
                    f"- {item['id']}",
                    item["status"],
                    item["kind"],
                    item["repo"],
                    item["ref"],
                    item["command"],
                    item["outcome"],
                    item["flags"],
                    item["extra"],
                ]
            )
        )
    lines += ["", "## Proposals", ""]
    for proposal in sorted(state["proposals"], key=lambda row: row["key"].lower()):
        lines.append(f"- {proposal['key']} | {proposal['slug']} | {proposal['text']}")
    lines += ["", "## Waiting", ""]
    for wait in sorted(state["waiting"], key=lambda row: (row["repo"].lower(), row["reason"])):
        lines.append(f"- {wait['repo']} | {wait['reason']} | {wait['detail']}")
    lines += ["", "## Last sweep", "", f"Inventory at: {state['last_inventory_at']}"]
    for name, opened in sorted(state["last_open"], key=lambda row: row[0].lower()):
        lines.append(f"- {name} | open {opened}")
    lines.append("")
    return "\n".join(lines)


def split_bullet(line: str, count: int, what: str) -> list[str]:
    if not line.startswith("- "):
        fail("unreadable", f"A {what} line does not start with '- '.")
    parts = [part.strip() for part in line[2:].split(" | ")]
    if len(parts) != count:
        fail("unreadable", f"A {what} line does not have {count} fields.")
    return parts


def parse_progress(text: str) -> dict:
    if not text.startswith("# Sweep progress\n"):
        fail("unreadable", "docs/system/sweep-progress.md is not a sweep progress file.")
    state = blank_state()
    section = "header"
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if line.startswith("# "):
            continue
        if section == "header":
            if not line.strip():
                continue
            if ": " not in line:
                fail("unreadable", f"Header line {line!r} has no value.")
            key, value = line.split(": ", 1)
            if key == "Inventory at" and section != "header":
                continue
            if key not in HEADER_KEYS:
                fail("unreadable", f"Unknown header {key}.")
            state["header"][key] = value
            continue
        if not line.strip():
            continue
        if section == "Repos":
            name, result, when, opened, detail = split_bullet(line, 5, "repo")
            if result not in FETCH_RESULTS or not opened.startswith("open "):
                fail("unreadable", "A repo line has a bad result or open list.")
            state["repos"].append(
                {
                    "name": name,
                    "result": result,
                    "when": when,
                    "open": opened[len("open ") :],
                    "detail": detail,
                }
            )
        elif section == "Items":
            fields = split_bullet(line, 9, "item")
            item = dict(
                zip(
                    ("id", "status", "kind", "repo", "ref", "command", "outcome", "flags", "extra"),
                    fields,
                )
            )
            if item["status"] not in ITEM_STATUSES:
                fail("unreadable", "An item has a bad status.")
            state["items"].append(item)
        elif section == "Proposals":
            key, slug, proposal = split_bullet(line, 3, "proposal")
            state["proposals"].append({"key": key, "slug": slug, "text": proposal})
        elif section == "Waiting":
            repo, reason, detail = split_bullet(line, 3, "waiting")
            state["waiting"].append({"repo": repo, "reason": reason, "detail": detail})
        elif section == "Last sweep":
            if line.startswith("Inventory at: "):
                state["last_inventory_at"] = line[len("Inventory at: ") :]
            elif line.startswith("- "):
                name, opened = split_bullet(line, 2, "last sweep")
                if not opened.startswith("open "):
                    fail("unreadable", "A last-sweep line has no open list.")
                state["last_open"].append((name, opened[len("open ") :]))
        else:
            fail("unreadable", f"Unknown section {section}.")
    if state["header"]["Flow"] not in FLOWS:
        fail("unreadable", "The progress file has no flow.")
    return state


def load_state(root, write: bool):
    path = progress_path(root)
    if not path.is_file():
        fail("no-run", "There is no docs/system/sweep-progress.md yet.")
    before = path.read_text(encoding="utf-8")
    state = parse_progress(before)
    return path, before, state


def save(path, before: str | None, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = render(state)
    if before is not None and rendered == before:
        return
    path.write_text(rendered, encoding="utf-8")


def header_view(state: dict) -> dict:
    return {
        "flow": state["header"]["Flow"],
        "scope": state["header"]["Scope"],
        "specs_repo": state["header"]["Specs repo"],
        "specs_comments": state["header"]["Specs comments"],
        "budget_minutes": int(state["header"]["Budget minutes"]),
        "hard_stop_minutes": int(state["header"]["Hard stop minutes"]),
        "started": state["header"]["Started"],
        "status": state["header"]["Status"],
        "current": None if state["header"]["Current"] == "-" else state["header"]["Current"],
        "inventory_at": state["header"]["Inventory at"],
    }


def elapsed_minutes(state: dict, moment: datetime) -> float:
    started = parse_when(state["header"]["Started"])
    delta = (moment - started).total_seconds() / 60
    return max(0.0, delta)


def budget_hit(state: dict, moment: datetime) -> bool:
    return elapsed_minutes(state, moment) >= int(state["header"]["Budget minutes"])


def repo_by_name(rows: list[dict], name: str) -> dict | None:
    for row in rows:
        if row["name"] == name:
            return row
    return None


def specs_name(state: dict) -> str | None:
    name = state["header"]["Specs repo"]
    return None if name == "-" else name


def comments_on(state: dict) -> bool:
    return state["header"]["Specs comments"] == "yes"


def allowed_repo(state: dict, rows: list[dict], name: str) -> dict:
    row = repo_by_name(rows, name)
    if row is None:
        fail("unknown-repo", f"{name} is not a row in repos.md.")
    reason = row_reason(row)
    if reason:
        fail("out-of-scope", f"{name} is {reason}.")
    scope = state["header"]["Scope"]
    specs = specs_name(state)
    if scope != "all" and name != scope:
        fail("out-of-scope", f"This run is scoped to {scope}.")
    if specs and name == specs and not comments_on(state):
        fail("specs-repo-out", "The specs repo is out of this run.")
    if scope == "all" and specs and name == specs and not comments_on(state):
        fail("specs-repo-out", "The specs repo is out of this run.")
    return row


def fetch_row(state: dict, name: str) -> dict | None:
    for repo in state["repos"]:
        if repo["name"] == name:
            return repo
    return None


def flag_join(flags: set[str]) -> str:
    if not flags:
        return "-"
    return ";".join(sorted(flags))


def flag_set(text: str) -> set[str]:
    if text == "-":
        return set()
    return {part for part in text.split(";") if part}


def item_id(kind: str, repo: str, ref: str) -> str:
    return f"{repo}/{kind}/{ref}"


def command_for(kind: str, repo: str, ref: str) -> str:
    if kind == "branch":
        return f"/crav1-add-to-spec code change {repo} {ref}"
    return f"/crav1-add-to-spec pr {repo} {ref} all"


def find_item(state: dict, ident: str) -> dict | None:
    for item in state["items"]:
        if item["id"] == ident:
            return item
    return None


def head_flag(ref: str) -> str:
    return f"head:{ref}"


def pr_covers(state: dict, repo: str, branch: str) -> str | None:
    token = head_flag(branch)
    for item in state["items"]:
        if item["repo"] == repo and item["kind"] == "pr" and token in flag_set(item["flags"]):
            return item["ref"]
    return None


def slugs_of(text: str) -> str:
    if text in {"", "-"}:
        return "-"
    parts = [part.strip() for part in text.split(",")]
    if not parts or any(not SLUG_RE.fullmatch(part) for part in parts):
        fail("slug", "A slug is lowercase letters, numbers, and hyphens.")
    return ",".join(parts)


def proposal_key(item: dict) -> str:
    if item["kind"] == "pr":
        return f"{item['repo']} pr {item['ref']}"
    return f"{item['repo']} branch {item['ref']}"


def add_waiting(state: dict, repo: str, reason: str, detail: str) -> None:
    for wait in state["waiting"]:
        if wait["repo"] == repo and wait["reason"] == reason and wait["detail"] == detail:
            return
    state["waiting"].append({"repo": repo, "reason": reason, "detail": detail})


def open_list(text: str | None) -> str:
    if not text:
        return "-"
    numbers = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if not part.isdigit():
            fail("open", "Open pull request numbers are digits.")
        numbers.append(int(part))
    if not numbers:
        return "-"
    return ",".join(str(number) for number in sorted(set(numbers)))


def counts(state: dict) -> dict:
    tally = {status: 0 for status in ITEM_STATUSES}
    for item in state["items"]:
        tally[item["status"]] += 1
    tally["proposals"] = len(state["proposals"])
    tally["waiting"] = len(state["waiting"])
    return tally


def pending_items(state: dict) -> list[dict]:
    return sorted(
        [item for item in state["items"] if item["status"] == "pending"],
        key=lambda row: row["id"].lower(),
    )


def question_slugs(state: dict) -> list[str]:
    found = []
    for item in state["items"]:
        flags = flag_set(item["flags"])
        if "conflict" not in flags and "question" not in flags:
            continue
        extra = item["extra"]
        if extra == "-" or extra.startswith("reason:"):
            continue
        for slug in extra.split(","):
            if slug not in found:
                found.append(slug)
    return sorted(found)


def ending_lines(state: dict, files: int) -> dict:
    pending = [item for item in state["items"] if item["status"] in {"pending", "current"}]
    flow = state["header"]["Flow"]
    scope = state["header"]["Scope"]
    scope_text = "" if scope == "all" else f" {scope}"
    command = f"/crav1-update-specs-from-changes-and-prs"
    if pending:
        noun = "item is" if len(pending) == 1 else "items are"
        nxt = (
            f"Next: {command} {flow}{scope_text}, because {len(pending)} {noun} still pending."
        )
    elif any("conflict" in flag_set(item["flags"]) or "question" in flag_set(item["flags"]) for item in state["items"]):
        slugs = question_slugs(state)
        target = " " + ", ".join(slugs) if slugs else ""
        nxt = (
            f"Next: /crav1-resolve-open-questions{target}, because this sweep left a conflict or an open question unsettled."
        )
    elif state["proposals"]:
        noun = "spec change is" if len(state["proposals"]) == 1 else "spec changes are"
        word = "a proposal" if len(state["proposals"]) == 1 else "proposals"
        nxt = (
            f"Next: {command} manual-flow{scope_text}, because {len(state['proposals'])} {noun} still {word}."
        )
    else:
        nxt = "Next: nothing needed now."
    waiting = [
        f"Waiting: {wait['repo']}, because {wait['reason']} ({wait['detail']})."
        for wait in sorted(state["waiting"], key=lambda row: (row["repo"].lower(), row["reason"]))
    ]
    uncommitted = None
    if files:
        noun = "file" if files == 1 else "files"
        uncommitted = f"Uncommitted: {files} {noun}; commit with /crav1-finalize-commit when ready."
    proposals = []
    for proposal in sorted(state["proposals"], key=lambda row: row["key"].lower()):
        where = "" if proposal["slug"] == "-" else f" on {proposal['slug']}"
        proposals.append(f"{proposal['key']}{where}: {proposal['text']}")
    return {"next": nxt, "waiting": waiting, "uncommitted": uncommitted, "proposals": proposals}


def public_item(item: dict) -> dict:
    return {
        "id": item["id"],
        "status": item["status"],
        "kind": item["kind"],
        "repo": item["repo"],
        "ref": item["ref"],
        "command": item["command"],
        "outcome": item["outcome"],
        "flags": item["flags"],
        "extra": item["extra"],
    }


def resume_payload(state: dict, moment: datetime) -> dict:
    nxt = None
    current = state["header"]["Current"]
    if current != "-":
        item = find_item(state, current)
        nxt = public_item(item) if item else None
    else:
        pending = pending_items(state)
        nxt = public_item(pending[0]) if pending else None
    left = int(state["header"]["Budget minutes"]) - elapsed_minutes(state, moment)
    return {
        "ok": True,
        "stop": budget_hit(state, moment),
        "minutes_left": round(left, 2),
        "next_item": nxt,
        "counts": counts(state),
        "closed_since_allowed": state["last_inventory_at"] != "-",
        "last_inventory_at": None if state["last_inventory_at"] == "-" else state["last_inventory_at"],
        "last_open": [{"repo": name, "open": opened} for name, opened in state["last_open"]],
        **header_view(state),
        **ending_lines(state, 0),
    }


def budget_args(text: str | None) -> tuple[int, bool, int | None]:
    if text is None:
        return DEFAULT_BUDGET_MINUTES, False, None
    if not text.isdigit() or int(text) < 1:
        fail("budget", "The budget is a whole number of minutes, at least 1.")
    requested = int(text)
    if requested > HARD_STOP_MINUTES:
        return HARD_STOP_MINUTES, True, requested
    return requested, False, requested


def scope_payload(rows: list[dict], specs_url: str, only: str | None) -> dict:
    specs = find_specs(rows, specs_url)
    specs_name_value = specs["name"] if specs else None
    out = []
    chosen = []
    for row in rows:
        reason = row_reason(row)
        if reason:
            out.append({"name": row["name"], "reason": reason})
            continue
        if specs_name_value and row["name"] == specs_name_value:
            continue
        chosen.append(row)
    if only:
        match = repo_by_name(rows, only)
        if match is None:
            fail("unknown-repo", f"{only} is not a row in repos.md.")
        reason = row_reason(match)
        if reason:
            fail("out-of-scope", f"{only} is {reason}.")
        chosen = [match]
    repos = []
    for row in chosen:
        comments_only = bool(specs_name_value and row["name"] == specs_name_value)
        repos.append(
            {
                "name": row["name"],
                "url": row["url"],
                "host": host_of(row["url"]),
                "merges_into": row["merges_into"] or None,
                "branches": not comments_only,
                "comments": True,
            }
        )
    specs_view = None
    if specs:
        included = any(repo["name"] == specs["name"] for repo in repos)
        specs_view = {
            "name": specs["name"],
            "url": specs["url"],
            "host": host_of(specs["url"]),
            "included": included,
            "branches": False,
            "comments": included,
        }
    return {"ok": True, "repos": repos, "out": out, "specs_repo": specs_view}


def archive(state: dict) -> None:
    state["last_inventory_at"] = state["header"]["Inventory at"]
    state["last_open"] = [(repo["name"], repo["open"]) for repo in state["repos"] if repo["result"] in {"ok", "local"}]
    state["repos"] = []
    state["items"] = []
    state["proposals"] = []
    state["waiting"] = []
    state["header"]["Current"] = "-"


def cmd_scope(args: argparse.Namespace) -> None:
    root = args.root
    rows = load_repos(root)
    emit(scope_payload(rows, args.specs_url, args.repo), 0)


def cmd_start(args: argparse.Namespace) -> None:
    need_yes(args)
    if args.flow not in FLOWS:
        fail("flow", "The flow is manual-flow or auto-flow.")
    root = args.root
    rows = load_repos(root)
    specs = find_specs(rows, args.specs_url)
    only = args.repo
    if only:
        match = repo_by_name(rows, only)
        if match is None:
            fail("unknown-repo", f"{only} is not a row in repos.md.")
        reason = row_reason(match)
        if reason:
            fail("out-of-scope", f"{only} is {reason}.")
    comments = args.include_specs_comments or "no"
    if comments not in {"yes", "no"}:
        fail("specs-comments", "Specs comments are yes or no.")
    naming_specs = bool(only and specs and only == specs["name"])
    if args.flow == "auto-flow" and comments == "yes" and not naming_specs:
        fail("auto-specs-out", "auto-flow leaves the specs repo out unless that repo is named.")
    if naming_specs:
        comments = "yes"
    preview = scope_payload(rows, args.specs_url, only)
    if not preview["repos"] and not (comments == "yes" and specs and not naming_specs):
        fail("nothing-in-scope", "No repos.md row with a URL is in scope.")
    if comments == "yes" and specs is None:
        fail("specs-repo-out", "repos.md has no row for the specs repo URL.")
    moment = stamp(now_or(args.when))
    minutes, clamped, requested = budget_args(args.budget)
    path = progress_path(root)
    fresh = blank_state()
    if path.is_file():
        before = path.read_text(encoding="utf-8")
        state = parse_progress(before)
        same = (
            state["header"]["Flow"] == args.flow
            and state["header"]["Scope"] == (only or "all")
            and state["header"]["Specs comments"] == comments
            and state["header"]["Specs repo"] == (specs["name"] if specs else "-")
        )
        if state["header"]["Status"] in {"running", "paused"} and not args.replace:
            if not same:
                fail(
                    "scope-differs",
                    "A sweep is already in progress for "
                    f"{state['header']['Flow']} {state['header']['Scope']}.",
                )
            for item in state["items"]:
                if item["status"] == "current":
                    item["status"] = "pending"
            state["header"]["Current"] = "-"
            state["header"]["Status"] = "running"
            state["header"]["Started"] = moment
            if args.budget is not None:
                state["header"]["Budget minutes"] = str(minutes)
            state["header"]["Hard stop minutes"] = str(HARD_STOP_MINUTES)
            save(path, before, state)
            emit({"ok": True, "resumed": True, "clamped": clamped, "requested_budget": requested, **resume_payload(state, parse_when(moment))}, 0)
        archive(state)
        fresh = state
        before_text = before
    else:
        before_text = None
    fresh["header"] = {
        "Flow": args.flow,
        "Scope": only or "all",
        "Specs repo": specs["name"] if specs else "-",
        "Specs comments": comments,
        "Budget minutes": str(minutes),
        "Hard stop minutes": str(HARD_STOP_MINUTES),
        "Started": moment,
        "Status": "running",
        "Current": "-",
        "Inventory at": moment,
    }
    save(path, before_text, fresh)
    emit(
        {
            "ok": True,
            "resumed": False,
            "clamped": clamped,
            "requested_budget": requested,
            "budget_minutes": minutes,
            "hard_stop_minutes": HARD_STOP_MINUTES,
        },
        0,
    )


def cmd_note_fetch(args: argparse.Namespace) -> None:
    need_yes(args)
    if args.result not in FETCH_RESULTS:
        fail("result", "Fetch result is ok, local, failed, missing, or signed-out.")
    root = args.root
    path, before, state = load_state(root, True)
    rows = load_repos(root)
    allowed_repo(state, rows, args.repo)
    detail = "-"
    if args.detail:
        detail = plain(args.detail, "detail", 200)
    elif args.result in FETCH_BLOCKS:
        fail("detail", "A failed fetch names the reason.")
    elif args.result == "signed-out":
        detail = "host signed out"
    when = stamp(now_or(args.when))
    opened = open_list(args.open)
    row = {
        "name": args.repo,
        "result": args.result,
        "when": when,
        "open": opened,
        "detail": detail,
    }
    state["repos"] = [repo for repo in state["repos"] if repo["name"] != args.repo]
    state["repos"].append(row)
    if args.result in FETCH_BLOCKS:
        add_waiting(state, args.repo, FETCH_BLOCKS[args.result], detail)
    if args.result == "signed-out":
        add_waiting(state, args.repo, "signed out", detail)
    save(path, before, state)
    emit({"ok": True, "repo": args.repo, "result": args.result}, 0)


def cmd_add_item(args: argparse.Namespace) -> None:
    need_yes(args)
    if args.kind not in {"branch", "pr"}:
        fail("kind", "An item is a branch or a pr.")
    if "|" in args.ref or not args.ref.strip() or " " in args.ref:
        fail("ref", "The ref has no spaces.")
    root = args.root
    path, before, state = load_state(root, True)
    rows = load_repos(root)
    row = allowed_repo(state, rows, args.repo)
    fetched = fetch_row(state, args.repo)
    if fetched is None:
        fail("not-fetched", f"{args.repo} has no fetch line yet.")
    if fetched["result"] in FETCH_BLOCKS:
        fail("fetch-failed", f"{args.repo} was skipped because the fetch did not succeed.")
    specs = specs_name(state)
    if args.kind == "branch" and specs and args.repo == specs:
        fail("specs-branches", "The specs repo's branches are never swept.")
    if args.kind == "pr" and fetched["result"] == "signed-out":
        fail("signed-out", f"{args.repo} is signed out, so its pull request threads are not read.")
    if args.kind == "pr" and not args.ref.isdigit():
        fail("ref", "A pull request ref is its number.")
    if args.kind == "branch" and is_base_branch(args.ref, row["merges_into"]):
        fail("base-branch", f"{args.ref} is a base branch.")
    if args.closed_since and state["last_inventory_at"] == "-":
        fail("no-earlier-sweep", "The first sweep has no closed-since list.")
    if args.kind == "branch":
        covered = pr_covers(state, args.repo, args.ref)
        if covered:
            fail("covered-by-pr", f"{args.ref} is the head of pull request {covered}.")
    ident = item_id(args.kind, args.repo, args.ref)
    existing = find_item(state, ident)
    if existing:
        emit({"ok": True, "id": ident, "status": existing["status"], "duplicate": True}, 0)
    flags = set()
    if args.draft:
        if args.kind != "pr":
            fail("draft", "A draft mark belongs on a pull request.")
        flags.add("draft")
    if args.closed_since:
        if args.kind != "pr":
            fail("closed-since", "Closed-since belongs on a pull request.")
        flags.add("closed-since")
    if args.head_branch:
        if args.kind != "pr":
            fail("head-branch", "A head branch belongs on a pull request.")
        if "|" in args.head_branch or " " in args.head_branch or ";" in args.head_branch:
            fail("head-branch", "The head branch has no spaces.")
        flags.add(head_flag(args.head_branch))
        for item in state["items"]:
            if (
                item["kind"] == "branch"
                and item["repo"] == args.repo
                and item["ref"] == args.head_branch
                and item["status"] in {"pending", "current"}
            ):
                item["status"] = "dropped"
                item["extra"] = f"reason: covered by pr {args.ref}"
                if state["header"]["Current"] == item["id"]:
                    state["header"]["Current"] = "-"
    state["items"].append(
        {
            "id": ident,
            "status": "pending",
            "kind": args.kind,
            "repo": args.repo,
            "ref": args.ref,
            "command": command_for(args.kind, args.repo, args.ref),
            "outcome": "-",
            "flags": flag_join(flags),
            "extra": "-",
        }
    )
    save(path, before, state)
    emit({"ok": True, "id": ident, "status": "pending", "duplicate": False, "command": command_for(args.kind, args.repo, args.ref)}, 0)


def require_item(state: dict, ident: str) -> dict:
    item = find_item(state, ident)
    if item is None:
        fail("unknown-item", f"{ident} is not in this sweep.")
    return item


def cmd_drop(args: argparse.Namespace) -> None:
    need_yes(args)
    path, before, state = load_state(args.root, True)
    item = require_item(state, args.id)
    if item["status"] not in {"pending", "current"}:
        fail("not-pending", f"{args.id} is already {item['status']}.")
    item["status"] = "dropped"
    if state["header"]["Current"] == item["id"]:
        state["header"]["Current"] = "-"
    save(path, before, state)
    emit({"ok": True, "id": args.id, "status": "dropped"}, 0)


def cmd_begin(args: argparse.Namespace) -> None:
    need_yes(args)
    path, before, state = load_state(args.root, True)
    item = require_item(state, args.id)
    moment = now_or(args.now)
    current = state["header"]["Current"]
    if current not in {"-", item["id"]}:
        fail("item-open", f"{current} is still the current item.")
    if item["status"] not in {"pending", "current"}:
        fail("not-pending", f"{args.id} is already {item['status']}.")
    if budget_hit(state, moment) and item["status"] != "current":
        fail("budget", "The budget is used. Finish the current item and stop.", 3)
    item["status"] = "current"
    state["header"]["Current"] = item["id"]
    save(path, before, state)
    emit({"ok": True, "id": item["id"], "stop": budget_hit(state, moment)}, 0)


def cmd_complete(args: argparse.Namespace) -> None:
    need_yes(args)
    if args.outcome not in OUTCOMES:
        fail("outcome", "Outcome is notes, synced-at, notes+synced-at, proposal, or spec.")
    path, before, state = load_state(args.root, True)
    item = require_item(state, args.id)
    if item["status"] != "current":
        fail("not-current", "begin-item before complete.")
    if args.outcome == "spec" and state["header"]["Flow"] == "auto-flow":
        fail("auto-no-spec", "auto-flow does not write a spec change.")
    if args.outcome == "proposal" and not args.proposal:
        fail("proposal", "A proposal needs its text.")
    flags = flag_set(item["flags"])
    if args.conflict:
        flags.add("conflict")
    if args.question:
        flags.add("question")
    item["flags"] = flag_join(flags)
    slug = slugs_of(args.slug or "-")
    if args.outcome == "proposal":
        text = plain(args.proposal, "proposal")
        item["status"] = "collected"
        item["outcome"] = "proposal"
        item["extra"] = slug
        key = proposal_key(item)
        state["proposals"] = [row for row in state["proposals"] if row["key"] != key]
        state["proposals"].append({"key": key, "slug": slug, "text": text})
    else:
        item["status"] = "done"
        item["outcome"] = args.outcome
        item["extra"] = slug
        state["proposals"] = [row for row in state["proposals"] if row["key"] != proposal_key(item)]
    state["header"]["Current"] = "-"
    moment = now_or(args.now)
    save(path, before, state)
    emit({"ok": True, "id": item["id"], "status": item["status"], "stop": budget_hit(state, moment)}, 0)


def cmd_skip(args: argparse.Namespace) -> None:
    need_yes(args)
    path, before, state = load_state(args.root, True)
    item = require_item(state, args.id)
    if item["status"] not in {"pending", "current"}:
        fail("not-pending", f"{args.id} is already {item['status']}.")
    reason = plain(args.reason, "reason", 200)
    item["status"] = "skipped"
    item["extra"] = f"reason: {reason}"
    if state["header"]["Current"] == item["id"]:
        state["header"]["Current"] = "-"
    if args.waiting:
        add_waiting(state, item["repo"], "rate limit", reason)
    moment = now_or(args.now)
    save(path, before, state)
    emit({"ok": True, "id": item["id"], "status": "skipped", "stop": budget_hit(state, moment)}, 0)


def cmd_pause(args: argparse.Namespace) -> None:
    need_yes(args)
    path, before, state = load_state(args.root, True)
    if state["header"]["Current"] != "-":
        fail("item-open", "Finish the current item before pausing.")
    state["header"]["Status"] = "paused"
    save(path, before, state)
    emit({"ok": True, "status": "paused", **ending_lines(state, 0)}, 0)


def cmd_finish(args: argparse.Namespace) -> None:
    need_yes(args)
    path, before, state = load_state(args.root, True)
    if state["header"]["Current"] != "-" or pending_items(state):
        fail("pending", "Items are still pending.")
    state["header"]["Status"] = "finished"
    save(path, before, state)
    emit({"ok": True, "status": "finished"}, 0)


def cmd_resume(args: argparse.Namespace) -> None:
    _path, _before, state = load_state(args.root, False)
    emit(resume_payload(state, now_or(args.now)), 0)


def cmd_ending(args: argparse.Namespace) -> None:
    if args.files < 0:
        fail("files", "The file count is zero or more.")
    _path, _before, state = load_state(args.root, False)
    emit({"ok": True, **ending_lines(state, args.files)}, 0)


def cmd_budget(args: argparse.Namespace) -> None:
    _path, _before, state = load_state(args.root, False)
    moment = now_or(args.now)
    emit(
        {
            "ok": True,
            "stop": budget_hit(state, moment),
            "elapsed_minutes": round(elapsed_minutes(state, moment), 2),
            "budget_minutes": int(state["header"]["Budget minutes"]),
            "hard_stop_minutes": HARD_STOP_MINUTES,
        },
        0,
    )


def cmd_read_line(args: argparse.Namespace) -> None:
    if not SHA_RE.fullmatch(args.head):
        fail("head", "The head is a hex sha of at least 7 characters.")
    if not args.push.isdigit():
        fail("push", "The push count is a whole number.")
    if args.comment_time != "none" and (not args.comment_time or any(ch.isspace() for ch in args.comment_time)):
        fail("comment-time", "The comment time is one token, or none.")
    if not DATE_RE.fullmatch(args.date):
        fail("date", "The date is YYYY-MM-DD.")
    line = f"- Read: sweep | {args.head}, push {args.push}, newest comment {args.comment_time} | {args.date}"
    emit({"ok": True, "line": line}, 0)


def build() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sweep progress file")
    sub = parser.add_subparsers(dest="command", required=True)

    def shared(command: argparse.ArgumentParser, yes: bool = False) -> None:
        command.add_argument("--root", type=lambda value: __import__("pathlib").Path(value))
        if yes:
            command.add_argument("--yes", action="store_true")

    scope = sub.add_parser("scope")
    shared(scope)
    scope.add_argument("--specs-url", required=True)
    scope.add_argument("--repo")
    scope.set_defaults(func=cmd_scope)

    start = sub.add_parser("start")
    shared(start, True)
    start.add_argument("--flow", required=True)
    start.add_argument("--specs-url", required=True)
    start.add_argument("--repo")
    start.add_argument("--budget")
    start.add_argument("--include-specs-comments", choices=("yes", "no"))
    start.add_argument("--when")
    start.add_argument("--replace", action="store_true")
    start.set_defaults(func=cmd_start)

    fetch = sub.add_parser("note-fetch")
    shared(fetch, True)
    fetch.add_argument("--repo", required=True)
    fetch.add_argument("--result", required=True)
    fetch.add_argument("--open")
    fetch.add_argument("--detail")
    fetch.add_argument("--when")
    fetch.set_defaults(func=cmd_note_fetch)

    add = sub.add_parser("add-item")
    shared(add, True)
    add.add_argument("--kind", required=True)
    add.add_argument("--repo", required=True)
    add.add_argument("--ref", required=True)
    add.add_argument("--draft", action="store_true")
    add.add_argument("--closed-since", action="store_true")
    add.add_argument("--head-branch")
    add.set_defaults(func=cmd_add_item)

    drop = sub.add_parser("drop")
    shared(drop, True)
    drop.add_argument("--id", required=True)
    drop.set_defaults(func=cmd_drop)

    begin = sub.add_parser("begin-item")
    shared(begin, True)
    begin.add_argument("--id", required=True)
    begin.add_argument("--now")
    begin.set_defaults(func=cmd_begin)

    complete = sub.add_parser("complete")
    shared(complete, True)
    complete.add_argument("--id", required=True)
    complete.add_argument("--outcome", required=True)
    complete.add_argument("--slug")
    complete.add_argument("--conflict", action="store_true")
    complete.add_argument("--question", action="store_true")
    complete.add_argument("--proposal")
    complete.add_argument("--now")
    complete.set_defaults(func=cmd_complete)

    skip = sub.add_parser("skip")
    shared(skip, True)
    skip.add_argument("--id", required=True)
    skip.add_argument("--reason", required=True)
    skip.add_argument("--waiting", action="store_true")
    skip.add_argument("--now")
    skip.set_defaults(func=cmd_skip)

    pause = sub.add_parser("pause")
    shared(pause, True)
    pause.set_defaults(func=cmd_pause)

    finish = sub.add_parser("finish")
    shared(finish, True)
    finish.set_defaults(func=cmd_finish)

    resume = sub.add_parser("resume")
    shared(resume)
    resume.add_argument("--now")
    resume.set_defaults(func=cmd_resume)

    ending = sub.add_parser("ending")
    shared(ending)
    ending.add_argument("--files", type=int, default=0)
    ending.add_argument("--now")
    ending.set_defaults(func=cmd_ending)

    budget = sub.add_parser("budget")
    shared(budget)
    budget.add_argument("--now")
    budget.set_defaults(func=cmd_budget)

    read = sub.add_parser("read-line")
    read.add_argument("--head", required=True)
    read.add_argument("--push", required=True)
    read.add_argument("--comment-time", required=True)
    read.add_argument("--date", required=True)
    read.set_defaults(func=cmd_read_line)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build().parse_args(argv)
    if getattr(args, "root", None) is not None and not args.root.is_dir():
        fail("root", "The specs repo root is not a directory.")
    args.func(args)


if __name__ == "__main__":
    main()
