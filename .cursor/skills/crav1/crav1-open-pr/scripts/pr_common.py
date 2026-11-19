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
  resolve --ref <n-or-url> [--remote-url <url>] [--root <specs-repo>]...
          Which pull request a reference means (1.177.0). A bare number
          (`82`, `pr82`, `PR 82`, `#82`) is looked up in the kit's own
          records first: build-progress files, the merge list, PR notes
          and docs/system/repos.md. One record match wins; a record match
          and a different remote, or several records, is `ask`. Only with
          no record does it fall back to this checkout's remote. `tool`
          is the one CLI the resolved host needs (gh or az). --root may be
          the repo root, docs/specs or a spec folder (1.177.1). A record
          that names `PR <n>` without a URL takes its host from a
          `Code repo:` line or the only docs/system/repos.md row; with no
          host it is `ask`, never the remote.

The interpreter is crav1-docs/reference/running-scripts.md. The canonical
copy lives in skill crav1-open-pr; the other three skills ship a thin copy
that runs it.
"""
from __future__ import annotations

import argparse
import json
import os
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
NUMBER = re.compile(r"^(?:#|pr\s*#?|pull request\s+#?)?(?P<n>\d+)$", re.I)
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


# ---------- the Azure DevOps 4,000-character description (1.176.0) ----------

ADO_LIMIT = 4000
SHORTENED = "Task lines were shortened to fit."
_TASK_LINE = re.compile(r"^\s*[-*]\s+T\d+\b")


def _task_lines(lines: list[str]) -> list[int]:
    """Indexes of the task lines: `- T#` bullets, else the bullets under `### Tasks`."""
    found = [i for i, line in enumerate(lines) if _TASK_LINE.match(line)]
    if found:
        return found
    inside = False
    for i, line in enumerate(lines):
        if line.startswith("#"):
            inside = line.lstrip("#").strip().lower() == "tasks"
            continue
        if inside and line.lstrip().startswith(("- ", "* ")):
            found.append(i)
    return found


def _first_sentence(line: str) -> str:
    return re.split(r"(?<=[.!?])\s+(?=[A-Z`])", line, maxsplit=1)[0].rstrip()


def _cut_words(line: str, room: int) -> str:
    if len(line) <= room:
        return line
    cut = line[:room]
    return (cut.rsplit(" ", 1)[0] if " " in cut else cut).rstrip(" ,;:.")


def fit_body(text: str, limit: int = ADO_LIMIT) -> dict:
    """A guard for a PR description over `limit` characters (format B, 1.176.0).

    Only the task lines give way: first to the task name (the first
    sentence), then cut at a word. A plain `Task lines were shortened to
    fit.` line follows them. No link and no overflow comment is added; the
    summary, Verified and the work-item mention stay as written.
    """
    body = str(text or "").replace("\r\n", "\n")
    steps: list[str] = []

    def fits(value: str) -> bool:
        return len(value) <= limit

    if fits(body):
        return {"body": body, "length": len(body), "limit": limit, "fits": True, "trimmed": steps}
    lines = body.split("\n")
    tasks = _task_lines(lines)
    if tasks:
        for i in tasks:
            lines[i] = _first_sentence(lines[i])
        lines.insert(tasks[-1] + 1, SHORTENED)
        steps.append("task-names")
        body = "\n".join(lines)
        if not fits(body):
            over = len(body) - limit
            longest = max(len(lines[i]) for i in tasks)
            room = longest
            while over > 0 and room > 20:
                room -= 10
                over = len(body) - limit - sum(max(0, len(lines[i]) - room) for i in tasks)
            for i in tasks:
                lines[i] = _cut_words(lines[i], room)
            steps.append("task-cut")
            body = "\n".join(lines)
    return {"body": body, "length": len(body), "limit": limit, "fits": fits(body), "trimmed": steps}


def limit_of(out: dict) -> int:
    return int(out["limit"])


def cmd_fit(args) -> int:
    path = Path(args.body)
    text = path.read_text(encoding="utf-8-sig")
    out = fit_body(text, args.limit)
    if args.text:
        if not out["fits"]:
            print(f"Still {out['length']} characters after trimming; the limit is {limit_of(out)}.", file=sys.stderr)
            return 2
        sys.stdout.write(out["body"])
        return 0
    if not args.show:
        out.pop("body")
    return emit({"ok": out["fits"], **out}, 0 if out["fits"] else 2)


# ---------- resolve a pull request reference from the kit's records (1.177.0) ----------

PR_URL_ANY = re.compile(
    r"https?://(?:github\.com/[^/\s]+/[^/\s]+/pull/\d+"
    r"|(?:dev\.azure\.com/[^/\s]+|[^./\s]+\.visualstudio\.com)/[^/\s]+/_git/[^/\s]+/pullrequest/\d+)",
    re.I,
)
PR_NOTE_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-pr-(?P<repo>.+)-(?P<n>\d+)\.md$", re.I)
TOOL = {"github": "gh", "azure": "az"}


def _url_key(info: dict) -> tuple:
    keys = ("owner", "repo") if info.get("host") == "github" else ("org", "project", "repo")
    return (info.get("host"),) + tuple((info.get(k) or "").lower().removesuffix(".git") for k in keys) + (info.get("number"),)


def _repos_rows(root: Path) -> dict:
    """{repo name (lower): URL} from docs/system/repos.md."""
    path = root / "docs" / "system" / "repos.md"
    rows: dict = {}
    if not path.is_file():
        return rows
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        cells = [c.strip().strip("`") for c in raw.strip().strip("|").split("|")]
        if len(cells) < 4 or not cells[0] or cells[0].lower() in ("repo", "---") or set(cells[0]) <= {"-", ":"}:
            continue
        url = next((c for c in cells if c.lower().startswith(("http://", "https://", "git@"))), "")
        if url:
            rows[cells[0].lower()] = url
    return rows


def _pr_url_for(repo_url: str, number: int) -> str:
    info = host_of(repo_url)
    if info["host"] == "github":
        return f"https://github.com/{info['owner']}/{info['repo'].removesuffix('.git')}/pull/{number}"
    if info["host"] == "azure":
        return f"https://dev.azure.com/{info['org']}/{info['project']}/_git/{info['repo'].removesuffix('.git')}/pullrequest/{number}"
    return ""


def record_files(root: Path) -> list[tuple[str, Path]]:
    """(kind, path) for every record a bare number is looked up in."""
    out: list[tuple[str, Path]] = []
    specs = root / "docs" / "specs"
    if specs.is_dir():
        for slug in sorted(p for p in specs.iterdir() if p.is_dir() and not p.name.startswith("_")):
            for path in sorted((slug / "build-progress").glob("**/*.md")) if (slug / "build-progress").is_dir() else []:
                out.append(("build-progress", path))
            for name in ("build-map.md", "walk-progress.md"):
                if (slug / name).is_file():
                    out.append(("merge list", slug / name))
    notes = root / "docs" / "notes"
    if notes.is_dir():
        for path in sorted(notes.glob("**/*.md")):
            if PR_NOTE_NAME.match(path.name):
                out.append(("PR note", path))
    return out


BARE_PR = re.compile(r"\b(?:PR|pull request)\s*#?(\d+)\b", re.I)
REPO_FIELD = re.compile(r"^(?:Code repo|Repo):\s*`?([^`\s]+)`?\s*$", re.M | re.I)


def repo_root_of(path: Path) -> Path:
    """The specs repo root for a repo root, docs/specs, or a spec folder (1.177.1)."""
    here = Path(path).resolve()
    for p in (here, *here.parents):
        if (p / "docs" / "specs").is_dir() or (p / "docs" / "notes").is_dir() or (p / "docs" / "system" / "repos.md").is_file():
            return p
    return here


def _record_repo_url(text: str, repos: dict) -> str:
    """The code repo URL a record points at (1.177.1).

    A `Code repo:` or `Repo:` line (a URL, or a repos.md name), else the one
    row of docs/system/repos.md when there is exactly one. Empty when the
    host cannot be worked out.
    """
    m = REPO_FIELD.search(text or "")
    if m:
        value = m.group(1).strip()
        if host_of(value)["host"] in ("github", "azure"):
            return value
        if value.lower().removesuffix(".git") in repos:
            return repos[value.lower().removesuffix(".git")]
    if len(repos) == 1:
        return next(iter(repos.values()))
    return ""


def _branch_of(text: str, path: Path) -> str:
    m = re.search(r"^Branch:\s*(\S+)", text or "", re.M)
    return m.group(1) if m else path.stem.replace("--", "/")


def record_candidates(roots: list[Path], number: int, unhosted: list | None = None) -> list[dict]:
    """Every pull request numbered `number` that the kit's records name, one per URL.

    A record that names `PR <n>` without a URL gets its URL from the record's
    code repo (_record_repo_url, 1.177.1). When that cannot be worked out the
    record goes to `unhosted` instead.
    """
    found: dict = {}
    for root in [repo_root_of(r) for r in roots]:
        repos = _repos_rows(root)
        for kind, path in record_files(root):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rel = path.relative_to(root).as_posix()
            urls = []
            for raw in PR_URL_ANY.findall(text):
                ref = parse_ref(raw)
                if ref.get("status") == "ok" and ref.get("number") == number:
                    urls.append(ref)
            if kind == "PR note":
                m = PR_NOTE_NAME.match(path.name)
                if int(m.group("n")) == number and m.group("repo").lower() in repos:
                    built = _pr_url_for(repos[m.group("repo").lower()], number)
                    if built:
                        urls.append(parse_ref(built))
            elif not urls and any(int(n) == number for n in BARE_PR.findall(text)):
                built = _pr_url_for(_record_repo_url(text, repos), number)
                if built:
                    urls.append(parse_ref(built))
                elif unhosted is not None:
                    label = (f"build-progress for {_branch_of(text, path)}" if kind == "build-progress" else rel)
                    unhosted.append({"number": number, "host": None, "url": None, "tool": None,
                                     "sources": [rel], "label": f"PR {number} is in {label}"})
            for ref in urls:
                key = _url_key(ref)
                row = found.setdefault(key, {"host": ref["host"], "number": number, "url": ref["url"],
                                             "repo": ref.get("repo"), "tool": TOOL.get(ref["host"]), "sources": []})
                if rel not in row["sources"]:
                    row["sources"].append(rel)
    return list(found.values())


def _default_roots(repo: str | None) -> list[Path]:
    here = Path(repo or ".").resolve()
    for p in (here, *here.parents):
        if (p / "docs" / "specs").is_dir() or (p / "docs" / "notes").is_dir():
            return [p]
    return [here]


def resolve_ref(ref: str, remote_url: str | None = None, roots: list[Path] | None = None,
                remote_has_pr: bool = False) -> dict:
    """Which pull request `ref` means: the kit's records first, the remote last (1.177.0).

    The remote is a candidate beside a record only when `remote_has_pr` says
    this checkout's host already showed a pull request with that number.
    The script never asks a host itself.
    """
    text = (ref or "").strip()
    if GITHUB_PR.match(text) or AZURE_PR.match(text):
        out = parse_ref(text, remote_url)
        out["source"] = "url"
        out["tool"] = TOOL.get(out.get("host"))
        if out["status"] == "ok":
            out["line"] = f"PR {out['number']} is {out['url']}; use {out['tool']}."
        else:
            # A full URL names its host; the review reads it from the records or repos.md.
            out["line"] = out.get("line", "") + f" The URL names its host; use {out['tool']} for it."
        return out
    m = NUMBER.match(text)
    if not m:
        return {"status": "not-a-pr", "line": f"{text!r} is not a pull request number or URL. A branch name is not a pull request."}
    number = int(m.group("n"))
    unhosted: list = []
    cands = record_candidates(roots or [], number, unhosted)
    remote = host_of(remote_url)
    if not cands and unhosted:
        # 1.177.1: a record names the PR but not its host. Ask; never fall
        # back to this checkout's remote, which may be another host.
        first = unhosted[0]
        return {"status": "ask", "number": number, "candidates": unhosted, "tool": None,
                "line": f"{first['label']}, but its host isn't recorded. Ask for the pull request URL; "
                        "do not name or install a CLI until the host is known."}
    remote_pr = None
    if remote["host"] in ("github", "azure"):
        remote_pr = _pr_url_for(remote_url or "", number)
    if len(cands) == 1:
        c = cands[0]
        if remote_pr and remote_has_pr and not same_repo(parse_ref(c["url"]), host_of(remote_url)):
            options = [dict(c, label=f"PR {number} in the kit's records ({', '.join(c['sources'])})"),
                       {"host": remote["host"], "number": number, "url": remote_pr, "repo": remote.get("repo"),
                        "tool": TOOL.get(remote["host"]), "sources": ["this checkout's git remote"],
                        "label": f"PR {number} on this checkout's remote"}]
            return {"status": "ask", "number": number, "candidates": options,
                    "line": f"PR {number} could be {c['url']} (the kit's records) or {remote_pr} (this checkout's remote). Ask which one."}
        return {"status": "ok", "source": "records", **c,
                "line": f"PR {number} is {c['url']}, from {', '.join(c['sources'])}; use {c['tool']}."}
    if len(cands) > 1:
        return {"status": "ask", "number": number, "candidates": cands,
                "line": f"The kit's records name {len(cands)} pull requests numbered {number}: "
                        + "; ".join(c["url"] for c in cands) + ". Ask which one."}
    if remote_pr:
        return {"status": "ok", "source": "remote", "host": remote["host"], "number": number, "url": remote_pr,
                "repo": remote.get("repo"), "tool": TOOL.get(remote["host"]), "candidates": [],
                "line": f"No kit record names PR {number}; using this checkout's remote: {remote_pr}; use {TOOL.get(remote['host'])}."}
    return {"status": "needs-remote", "number": number, "candidates": [],
            "line": f"No kit record names PR {number} and this checkout has no single GitHub or Azure DevOps remote. Ask for the pull request URL."}


# 1.179.0: how long a host CLI may take. The first `az` call on Windows loads
# Python, the azure-devops extension and a token, so it gets 20 s; `gh` 8 s.
# CRAV1_HOST_TIMEOUT overrides both.
HOST_TIMEOUT = {"github": 8, "azure": 20}

# 1.179.0: why a host lookup gave no answer. Each code is one reason the
# ready check can name, with its fix, instead of a silent "no answer".
HOST_ERRORS = ("cli-missing", "cli-not-runnable", "timeout", "not-signed-in", "extension-missing",
               "not-found", "bad-output", "unknown-status", "host-error")
_EXTENSION_MISSING = re.compile(r"azure-devops|'repos' is misspelled|misspelled or not recognized"
                                r"|extension\b.*\bnot installed", re.I)
_NOT_SIGNED_IN = re.compile(r"\baz\s+(?:devops\s+)?login\b|AADSTS|TF400813|\b401\b|unauthori[sz]ed"
                            r"|not logged in|please run .*login|gh auth login|authentication (?:required|failed)"
                            r"|credentials? (?:have|has) expired|token .*expired", re.I)
_NOT_FOUND = re.compile(r"TF401180|does not exist|could not resolve to a pullrequest|no pull requests? found"
                        r"|\bnot found\b|\b404\b", re.I)


def host_timeout(host: str | None) -> int:
    """Seconds a host lookup may take: CRAV1_HOST_TIMEOUT, else 20 for az, 8 for gh (1.179.0)."""
    raw = os.environ.get("CRAV1_HOST_TIMEOUT", "").strip()
    if raw.isdigit() and int(raw) > 0:
        return int(raw)
    return HOST_TIMEOUT.get(host or "", 8)


def _host_cli(host: str | None) -> str | None:
    """The full path of the host's CLI, or None (1.179.0).

    On Windows `az` is `az.cmd` (or `az.bat`). shutil.which finds it, but
    starting the bare name `az` without a shell fails, so the lookup always
    runs the path which() returned.
    """
    tool = TOOL.get(host or "")
    if not tool:
        return None
    names = [tool, f"{tool}.cmd", f"{tool}.bat"] if host == "azure" else [tool, f"{tool}.exe"]
    for name in names:
        exe = shutil.which(name)
        if exe:
            return exe
    return None


def _host_env(host: str | None) -> dict:
    env = dict(os.environ)
    if host == "azure":
        # Never prompt to install the azure-devops extension and wait for input.
        env["AZURE_EXTENSION_USE_DYNAMIC_INSTALL"] = "no"
        env["AZURE_CORE_ONLY_SHOW_ERRORS"] = "true"
        env["AZURE_CORE_NO_COLOR"] = "true"
    else:
        env["GH_PROMPT_DISABLED"] = "1"
        env["NO_COLOR"] = "1"
    return env


def _first_line(text: str | None) -> str:
    for line in str(text or "").splitlines():
        line = line.strip()
        if line:
            return line[:200]
    return ""


def classify_host_error(stderr: str | None) -> str:
    """The error code for a failed host CLI call, from its stderr (1.179.0)."""
    text = str(stderr or "")
    if _EXTENSION_MISSING.search(text):
        return "extension-missing"
    if _NOT_SIGNED_IN.search(text):
        return "not-signed-in"
    if _NOT_FOUND.search(text):
        return "not-found"
    return "host-error"


def _host_call(host: str, args: list[str], repo: str | None, timeout: int | None) -> tuple[str | None, str | None, str]:
    """Run the host CLI read-only. (stdout, error code, detail); stdout is None on an error (1.179.0)."""
    exe = _host_cli(host)
    if not exe:
        return None, "cli-missing", f"{TOOL.get(host, host)} not found"
    limit = timeout or host_timeout(host)
    try:
        proc = subprocess.run([exe, *args], cwd=repo, capture_output=True, stdin=subprocess.DEVNULL,
                              encoding="utf-8", errors="replace", timeout=limit, check=False,
                              env=_host_env(host))
    except subprocess.TimeoutExpired:
        return None, "timeout", f"no answer within {limit} s"
    except (OSError, subprocess.SubprocessError) as exc:
        return None, "cli-not-runnable", _first_line(str(exc)) or type(exc).__name__
    if proc.returncode != 0:
        return None, classify_host_error(proc.stderr), _first_line(proc.stderr) or f"exit code {proc.returncode}"
    if not (proc.stdout or "").strip():
        return None, "bad-output", "empty output"
    return proc.stdout, None, ""


def _host_args(info: dict, fields: str) -> list[str]:
    host, number = info.get("host"), info.get("number")
    url = info.get("url") or ""
    if host == "github":
        args = ["pr", "view", str(number), "--json", fields]
        ref = host_of(url.split("/pull/")[0]) if "/pull/" in url else {}
        if ref.get("owner"):
            args += ["-R", f"{ref['owner']}/{ref['repo']}"]
        return args
    args = ["repos", "pr", "show", "--id", str(number), "--query", fields, "-o", "json", "--detect", "false"]
    ref = parse_ref(url) if url else {}
    if ref.get("org"):
        args += ["--organization", f"https://dev.azure.com/{ref['org']}"]
    return args


def host_lookup(info: dict, repo: str | None = None, timeout: int | None = None) -> dict:
    """One read-only lookup on the pull request's own host, with a reason (1.179.0).

    {"ok": state | None, "error": code | None, "detail": first stderr line}.
    `ok` is what host_state returns: {"state": "merged" | "closed" | "open",
    "sha", "date"} plus "author" when the host names who opened it. `error`
    is one of HOST_ERRORS when the host could not be read: cli-missing,
    cli-not-runnable, timeout, not-signed-in, extension-missing, not-found,
    bad-output, unknown-status, host-error. Both are None when the PR's host
    is not GitHub or Azure DevOps. Only the resolved host's CLI is tried, by
    its full path, with stdin closed, UTF-8 output and no prompts.
    """
    host, number = info.get("host"), info.get("number")
    if not number or host not in TOOL:
        return {"ok": None, "error": None, "detail": ""}
    if host == "github":
        fields = "state,mergeCommit,mergedAt,closedAt,author"
    else:
        fields = "{status:status,sha:lastMergeCommit.commitId,closed:closedDate,author:createdBy.displayName}"
    out, error, detail = _host_call(host, _host_args(info, fields), repo, timeout)
    if error:
        return {"ok": None, "error": error, "detail": detail}
    try:
        data = json.loads(out)
    except ValueError:
        return {"ok": None, "error": "bad-output", "detail": _first_line(out)}
    if not isinstance(data, dict):
        return {"ok": None, "error": "bad-output", "detail": _first_line(out)}
    if host == "github":
        raw = str(data.get("state") or "").upper()
        commit = data.get("mergeCommit") or {}
        sha = commit.get("oid") if isinstance(commit, dict) else None
        date = data.get("mergedAt") or data.get("closedAt")
        state = {"MERGED": "merged", "CLOSED": "closed", "OPEN": "open"}.get(raw)
    else:
        raw = str(data.get("status") or "").lower()
        sha = data.get("sha")
        date = data.get("closed")
        state = {"completed": "merged", "abandoned": "closed", "active": "open"}.get(raw)
    if not state:
        return {"ok": None, "error": "unknown-status", "detail": f"status {raw or 'missing'}"}
    sha = sha if isinstance(sha, str) and re.fullmatch(r"[0-9a-fA-F]{7,40}", sha) else None
    day = str(date)[:10] if date and re.match(r"\d{4}-\d{2}-\d{2}", str(date)) else None
    state_out = {"state": state, "sha": sha.lower() if sha else None, "date": day}
    who = data.get("author")
    if isinstance(who, dict):
        who = who.get("name") or who.get("login")
    if isinstance(who, str) and who.strip():
        state_out["author"] = " ".join(who.split())
    return {"ok": state_out, "error": None, "detail": ""}


def host_state(info: dict, repo: str | None = None, timeout: int | None = None) -> dict | None:
    """Whether a pull request merged, read-only from its own host (1.177.2).

    The `ok` part of host_lookup (1.179.0): {"state": "merged" | "closed" |
    "open", "sha", "date"}, plus "author" when the host names who opened it
    (1.178.0). GitHub MERGED and Azure DevOps completed are merged, CLOSED
    and abandoned are closed. None when the host could not be read;
    host_lookup says why.
    """
    return host_lookup(info, repo, timeout)["ok"]


def host_author(info: dict, repo: str | None = None, timeout: int | None = None) -> str | None:
    """Who opened a pull request, read-only from its own host (1.177.1).

    `gh pr view <n> --json author` for GitHub, `az repos pr show --id <n>`
    (createdBy.displayName) for Azure DevOps, run the same way as
    host_lookup (1.179.0: full CLI path, no prompts). None when the CLI is
    missing, not signed in, slow, or fails.
    """
    host, number = info.get("host"), info.get("number")
    if not number or host not in TOOL:
        return None
    fields = "author" if host == "github" else "createdBy.displayName"
    out, error, _detail = _host_call(host, _host_args(info, fields), repo, timeout)
    if error:
        return None
    try:
        data = json.loads(out)
    except ValueError:
        return None
    if isinstance(data, dict):
        author = data.get("author") or {}
        if isinstance(author, dict):
            name = author.get("name") or author.get("login")
        else:
            name = author if isinstance(author, str) else None
    else:
        name = data if isinstance(data, str) else None
    return name.strip() if isinstance(name, str) and name.strip() else None


def cmd_resolve(args) -> int:
    roots = [repo_root_of(Path(r)) for r in (args.root or [])] or _default_roots(args.repo)
    remote = args.remote_url if args.remote_url is not None else _remote_url(args.repo)
    out = resolve_ref(args.ref, remote, roots, args.remote_has_pr)
    out["note"] = "Read-only. Name only the tool for the resolved host; never ask to install or sign in to the other one."
    return emit(out, 0 if out.get("status") in ("ok", "ask") else 1)

# PR record candidates (1.193.0): one rule for /crav1-pr-status and /crav1-add-to-spec pr<n> candidates.
POINT_RE = re.compile(r"^- Point: (?P<anchor>[^|]*?) \| (?P<status>[^|]*?) \| (?P<owner>[^|]*?) \| (?P<tags>[^|]*?) \| (?P<text>.*)$")
IN_SPEC_RE = re.compile(r"^in spec (?P<slug>[a-z0-9][a-z0-9-]*)(?: (?P<date>\d{4}-\d{2}-\d{2}))?(?P<q> \(question\))?$")
DATE_TAG_RE = re.compile(r"^(?:answered|replied) (?P<date>\d{4}-\d{2}-\d{2})$")


def parse_point(line: str) -> dict | None:
    m = POINT_RE.match(line.rstrip("\n"))
    if not m:
        return None
    d = m.groupdict()
    d["tags"] = [] if d["tags"].strip() == "-" else [t.strip() for t in d["tags"].split(";") if t.strip()]
    return d


def point_line(p: dict) -> str:
    tags = "; ".join(p["tags"]) if p["tags"] else "-"
    return f"- Point: {p['anchor']} | {p['status']} | {p['owner']} | {tags} | {p['text']}"


def candidate_state(p: dict) -> dict:
    """Is a Point a spec or decision candidate? A to spec / to decision Point is one unless an
    `in spec <slug>` tag covers its newest answer: a narrowed tag `(question)`, or an in-spec date
    older than a later `answered` or `replied` date, makes it a candidate again."""
    kinds = [t for t in p["tags"] if t in ("to spec", "to decision")]
    if not kinds:
        return {"candidate": False, "why": "not tagged to spec or to decision"}
    ins = [IN_SPEC_RE.match(t) for t in p["tags"] if t.startswith("in spec ")]
    ins = [m for m in ins if m]
    if not ins:
        return {"candidate": True, "why": "not in a spec yet"}
    latest = max((m.group("date") for m in [DATE_TAG_RE.match(t) for t in p["tags"]] if m), default="")
    for m in ins:
        if m.group("q"):
            return {"candidate": True, "why": f"only the question is in spec {m.group('slug')}; a newer answer is not"}
        if latest and m.group("date") and latest > m.group("date"):
            return {"candidate": True, "why": f"answered {latest}, after it went into spec {m.group('slug')} on {m.group('date')}"}
    return {"candidate": False, "why": "already in spec " + ins[0].group("slug")}


def record_candidates_of(text: str) -> list[dict]:
    """Every Point in a PR note's record, numbered in record order, with its candidate state."""
    out, n = [], 0
    for i, line in enumerate(text.splitlines(), 1):
        p = parse_point(line)
        if not p:
            continue
        n += 1
        out.append(dict(p, number=n, line=i, **candidate_state(p)))
    return out


def mark_answered(line: str, date: str) -> str:
    """A newer answer on a Point (1.193.0): add or move `answered <date>`, and narrow an older
    `in spec <slug>` tag to `in spec <slug> (question)` so the Point is a candidate again."""
    p = parse_point(line)
    if not p:
        raise ValueError("not a Point line")
    tags = [t for t in p["tags"] if not t.startswith("answered ")] + [f"answered {date}"]
    new = []
    for t in tags:
        m = IN_SPEC_RE.match(t)
        if m and not m.group("q") and not (m.group("date") and m.group("date") >= date):
            t = f"in spec {m.group('slug')} (question)"
        new.append(t)
    p["tags"] = new
    return point_line(p)


def mark_in_spec(line: str, slug: str, date: str) -> str:
    """After add-to-spec takes a Point: one `in spec <slug> <date>` tag, replacing a narrowed one."""
    p = parse_point(line)
    if not p:
        raise ValueError("not a Point line")
    p["tags"] = [t for t in p["tags"] if not (IN_SPEC_RE.match(t) and IN_SPEC_RE.match(t).group("slug") == slug)] + [f"in spec {slug} {date}"]
    return point_line(p)


def _pick(spec: str | None) -> set[int] | None:
    return {int(x) for x in spec.split(",") if x.strip()} if spec else None


def cmd_candidates(args) -> int:
    text = Path(args.note).read_text(encoding="utf-8")
    pts = record_candidates_of(text)
    pick = _pick(args.pick)
    cands = [p for p in pts if p["candidate"] and (pick is None or p["number"] in pick)]
    return emit({"note": args.note, "candidates": cands,
                 "skipped": [{"number": p["number"], "why": p["why"]} for p in pts if not p["candidate"] and any(t in ("to spec", "to decision") for t in p["tags"])],
                 "none_left": not cands})


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
    ft = sub.add_parser("fit")
    ft.add_argument("--body", required=True, help="the PR body file, UTF-8")
    ft.add_argument("--limit", type=int, default=ADO_LIMIT)
    ft.add_argument("--text", action="store_true", help="print only the trimmed body, to redirect into the file you pass to create")
    ft.add_argument("--show", action="store_true", help="print the trimmed body in the JSON")
    b = sub.add_parser("behind")
    b.add_argument("--head", required=True)
    b.add_argument("--base", required=True)
    b.add_argument("--repo")
    r = sub.add_parser("resolve")
    r.add_argument("--ref", required=True)
    r.add_argument("--remote-url")
    r.add_argument("--root", action="append", help="the specs repo root (docs/specs or a spec folder also work) to read records from; repeatable")
    r.add_argument("--repo")
    r.add_argument("--remote-has-pr", action="store_true",
                   help="this checkout's host already showed a pull request with that number")
    cd = sub.add_parser("candidates", help="spec and decision candidates in a PR note's record (1.193.0)")
    cd.add_argument("--note", required=True)
    cd.add_argument("--pick", help="numbers in record order, e.g. 1,3")
    args = parser.parse_args(argv)
    if args.cmd == "parse":
        out = parse_ref(args.ref, args.remote_url)
        return emit(out, 0 if out.get("status") == "ok" else 1)
    if args.cmd == "host":
        return emit(host_of(args.remote_url))
    return {"find": cmd_find, "checks": cmd_checks, "claim": cmd_claim, "behind": cmd_behind, "fit": cmd_fit, "resolve": cmd_resolve,
            "candidates": cmd_candidates}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
