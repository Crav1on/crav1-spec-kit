#!/usr/bin/env python3
"""Build map for one slice (kit 1.140.0).

Groups the tasks onto branches, including tasks that are already done. The row name is the task branch, in this
order: a branch named on the task line (`(map: <branch>)`, else
`(branch: <branch>)`, else the name beside that T# in a leading Branches
paragraph, else a `feat/…` or `chore/…` name in the sentence, else
`committed later on <branch>`), else the plan step's `feat/<slug>-<words>`
name, else `feat/<slug>-<words>` from the task. An open task is never
placed under a branch git proves merged, or under a done sibling's
branch, when the task line or the Branches paragraph names another. A `from <base>` after the
task-line branch is that branch's base. The plan step is only the fallback
when the task line names no branch.
`--recommend T1` prints that name and does not write. The first line is the
branch. Later lines say where it came from (`source: task line`,
`source: build map`, or `source: new`), the `from:` base when the task line
states one, and `because:` when a merged or deleted branch was skipped.
A merged branch is not offered only when git proves its tip is already in
the base or the default branch. A recorded merge in the specs is not
enough to skip the name when git cannot tell, or shows the tip is not
contained. The task-line branch then stays. A branch deleted locally and
on the remote is not offered. A branch only on a remote (`origin/<name>`, or
`git ls-remote --heads`), or the head of an open pull request (`gh pr list`),
is offered with `because:` and a last `checkout: <name>` line, so the build
checks it out without asking (1.160.0). The branch is checked in the
code repo that holds it, which can be a separate checkout from the specs
repo: a repo prefix on `(map:)`/`(branch:)`, a Match `Branch: <repo> <name>`
line, or a `Repo:` line in tasks.md names it, and `--code-repo <path>`, the
specs repo, or a sibling checkout with that name is used. When that repo is
not found, the task-line branch is kept with `because: could not check
<repo> from here`; a branch is never called deleted from the wrong repo. A name that does not exist yet is offered
so it can be created. A fallback name is short and does not use a
person's name from the task line. Tasks that resolve to the same name
share a row.

A task id written in a step, or `(step: <n>)` on the task, is the link.
`(step:)` wins when both are present.

When the plan has no steps, or the steps name no task, each task gets
its own branch and the file says so. A done task stays in its wave, struck
through, with its pull request, branch, or commit. A wave whose every task
is done is wrapped in a details block. The rows stay in the file.

Waves are branch dependencies. Wave 1 does not wait for another open branch.
A later wave opens after the branches it waits for, and always sits in a
later wave than each of them. Branches that wait for each other are a loop:
the file names them and the task line behind each direction of the wait, and
they are listed under Blocked. A branch downstream of a loop keeps its own
wave and state. An `(after:)` that names no task is listed under Blocked too
(1.154.0). The Tasks field shows each task
as `T#` plus its short name. Other prose still drops task ids. The dangling
text left by a removed id is cleaned. The map is rewritten on every ready
check, so the ids match the tasks file.

Usage:
  build_map.py <spec-dir> [--chat] [--stdout]
  build_map.py <spec-dir> --recommend T1 [--code-repo <path>]
  build_map.py <spec-dir> --fix-loop [--pick N] [--yes] [--json]
  build_map.py --root <docs/specs> [--scope <words>] [--chat] [--stdout]

On Windows the interpreter is python. Elsewhere it is python3. Then py -3.
Set PYTHONUTF8=1 and pass -X utf8. The Store alias message
`Python was not found` means that command was not found.
Standard library only. Writes build-map.md in the spec folder unless --stdout.
With no flag, prints only the one-line path of that file.
"""
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

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


def _load(name):
    path = pathlib.Path(__file__).resolve().parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"crav1_build_map_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


task_order = _load("task_order")
question_blocks = _load("question_blocks")
task_state = _load("task_state")

STEP_LINE = re.compile(r"^(\d+)[.)]\s*(.*)$")
TASK_ID = re.compile(r"\bT(\d+)\b")
STEP_MARK = re.compile(r"\(step:\s*(\d+)\)")
MAP_MARK = re.compile(r"\(map:\s*([^)]*)\)", re.I)
BRANCH_MARK = re.compile(r"\(branch:\s*([^)]*)\)", re.I)
SPEC_MARK = re.compile(r"\(spec:\s*([^)]*)\)", re.I)
MARKER = re.compile(r"\((?:verify|spec|after|branch|step|map|question):[^)]*\)", re.I)
HOST_MARK = re.compile(r"\((?:host setup|manual,\s*secret)\)", re.I)
ONLY_IDS = re.compile(r"\(\s*(?:T\d+\s*,?\s*)+\)")
COMMITTED_LATER = re.compile(r"committed later on\s+`?([^\s`,.;)]+)`?", re.I)
WI_TASK = re.compile(r"task:\s*T(\d+)\s+(.+?)(?:\s+\(ADO:[^)]*\))?\s*$", re.I)
NAMED_BRANCH = re.compile(
    r"\b((?:feature|feat|hotfix|bugfix|fix|spec|chore|bug)/[A-Za-z0-9][A-Za-z0-9._/-]*)"
)
TICK_PATH = re.compile(r"`([^`\n]+)`")
WORD = re.compile(r"(?<![\w-])build-map(?![\w-])")
PIPELINE = re.compile(r"(?<![\w-])pipeline-runs(?![\w-])")
PAGE = re.compile(r"(?<![\w-])(open|export)-map(?![\w-])")
STOP = {
    "a", "an", "the", "and", "or", "of", "to", "for", "on", "in", "with",
    "from", "by", "its", "into",
}
NO_STEPS = "The plan has no steps, so this map uses one branch per task."
UNNAMED = "The plan steps do not name tasks, so this map uses one branch per task."
BY_STEP = "One branch per plan step."
SOME = "Some tasks are not named on a plan step, so each of those has its own branch."
MISSING_STEP = "A task names a plan step that is not in the plan, so that task has its own branch."
UNKNOWN_DEP = "a dependency that names no task"


def parse_invocation(text):
    """The word build-map selects the map. The remaining words are the scope.

    `open-map` or `export-map` sets page to open or export (1.163.0).
    """
    raw = (text or "").strip()
    raw = re.sub(r"^/crav1-tasks-ready-to-build\b", "", raw).strip()
    mode = "map" if WORD.search(raw) else "report"
    raw = WORD.sub(" ", raw)
    pipeline = bool(PIPELINE.search(raw))
    raw = PIPELINE.sub(" ", raw)
    page = PAGE.search(raw)
    page = page.group(1) if page else None
    raw = PAGE.sub(" ", raw)
    scope = re.sub(r"\s+", " ", raw).strip()
    if scope.startswith("@"):
        scope = scope[1:].strip()
    return {"mode": mode, "scope": scope, "pipeline_runs": pipeline, "page": page}


def scope_folder_names(scope):
    """Folder names a scope may mean. `cc 1.0` matches `cc 1.0`, `cc-1.0`, and `cc-1-0`."""
    text = (scope or "").strip()
    if not text:
        return []
    low = text.lower()
    names = [text, low]
    spaced = re.sub(r"\s+", "-", low)
    kebab = re.sub(r"[^a-z0-9]+", "-", low).strip("-")
    for name in (spaced, kebab):
        if name and name not in names:
            names.append(name)
    return names


def branch_token(value):
    """The branch in a mark. A repo prefix is the first word; the branch is the last."""
    parts = (value or "").replace("\r", " ").strip().split()
    return parts[-1].strip("`.,;:") if parts else ""


def clean_prose(text, names=None):
    """Drop kit marks and task ids. A known id becomes that task's short name.

    A removed id must not leave a dangling possessive, an empty pair of
    parentheses, a leading comma, or a double space.
    """
    names = names or {}
    text = MARKER.sub(" ", text or "")
    text = ONLY_IDS.sub(" ", text)

    def possess(match):
        name = names.get(int(match.group(1)))
        if not name:
            return " "
        return name + ("'" if name.endswith("s") else "'s")

    def bare(match):
        return names.get(int(match.group(1))) or " "

    text = re.sub(r"\bT(\d+)'s\b", possess, text)
    text = re.sub(r"\bT(\d+)\b", bare, text)
    text = re.sub(r"(^|\s)'s\b", r"\1", text)
    previous = None
    while previous != text:
        previous = text
        text = re.sub(r"\(\s*,\s*", "(", text)
        text = re.sub(r",\s*,+", ",", text)
        text = re.sub(r",\s*\)", ")", text)
        text = re.sub(r"\(\s*\)", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    return text.strip(" ,;")


def _trim80(text, ellipsis=False):
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= 80:
        return text
    cut = text[:80]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    cut = cut.rstrip(" ,;.") or text[:80].rstrip()
    if ellipsis and cut != text:
        return cut + "..."
    return cut


def _readable(text):
    """First readable words: marks, branch names, and empty ticks are dropped."""
    text = MARKER.sub(" ", text or "")
    text = HOST_MARK.sub(" ", text)
    text = NAMED_BRANCH.sub(" ", text)
    # 1.176.0: keep the code text and drop the stray space before , ; : . )
    text = re.sub(r"`+", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,;:.)])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\(\)", "", text)
    text = task_order.balance_parens(text)
    text = re.sub(r"\s+", " ", text).strip(" ,;.:")
    return text


def task_label(task_id, short):
    """`T#` plus the short name. The Tasks field and the ready check use this."""
    name = re.sub(r"\s+", " ", short or "").strip() or "work"
    return f"T{task_id} {name}"


def ready_next_line(labels, branch_name, slug=None):
    """One Next for a ready branch (1.152.0).

    Same shape as Run next: the command alone in a code span, with the slug
    when the caller passes one, and the branch and task names on the next
    line. The build-tasks sentence is a line of its own, not on the command.
    """
    entry = run_entry(labels, branch_name, slug=slug)
    return entry + "\n/crav1-build-tasks builds one task without the walk."


_ENDING = []


def _ending_mod():
    """The shared walk ending, beside this script (1.156.0)."""
    if not _ENDING:
        path = pathlib.Path(__file__).resolve().parent / "walk_ending.py"
        spec = importlib.util.spec_from_file_location("walk_ending_bm", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _ENDING.append(mod)
    return _ENDING[0]


def run_entry(labels, branch_name, slug=None):
    """One ready branch in the Run next block (1.150.0); shared in walk_ending.py."""
    return _ending_mod().run_entry(labels, branch_name, slug=slug)


def branch_entry(open_labels, branch_name, slug=None):
    """The whole-branch Run next entry (1.155.0); shared in walk_ending.py."""
    return _ending_mod().branch_entry(open_labels, branch_name, slug=slug)


def run_entries(labels, branch_name, slug=None, open_labels=None, about=None, waits=None):
    """Run next block for one ready branch (1.164.0); shared in walk_ending.py."""
    return _ending_mod().run_entries(labels, branch_name, slug=slug, open_labels=open_labels, about=about, waits=waits)


def branch_block(branch_name, open_labels, first=None, slug=None, about=None, waits=None):
    return _ending_mod().branch_block(branch_name, open_labels, first=first, slug=slug, about=about, waits=waits)


def _names_done(text, done_tasks):
    """True when a step's opening sentence is about a done task (1.171.0).

    It names the done T#, or its opening words match the done task's name.
    """
    text = str(text or "")
    first = re.split(r"(?<=[.!?])\s", text.strip(), maxsplit=1)[0].lower()
    if not first:
        return False
    for task in done_tasks:
        if re.search(rf"\bT{task['id']}\b", first, re.I):
            return True
        for name in (task.get("full"), task.get("short")):
            words = re.findall(r"\w+", str(name or "").lower())
            if len(words) < 4:
                continue
            probe = " ".join(words[:4])
            if probe in " ".join(re.findall(r"\w+", first)):
                return True
        lead = " ".join(re.findall(r"\w+", first)[:4])
        full = " ".join(re.findall(r"\w+", str(task.get("full") or task.get("short") or "").lower()))
        if len(lead.split()) >= 4 and lead in full:
            return True
    return False


def short_name(rest, work_title=None, trim=True):
    """A task's short name: its work-item title, else the text up to the first cut.

    Cuts are the first verify item (1.187.0), ` (`, `, in `, and the end of
    the sentence, whichever comes first.
    Kit marks, branch prefixes, and leftover backticks are dropped. The
    result is never blank. When `trim` is true the name is at most 80
    characters, cut at a word boundary with an ellipsis.
    """
    def finish(text):
        cleaned = _readable(text)
        if not cleaned:
            cleaned = _readable(rest)
        if not cleaned:
            return "work"
        if trim:
            return _trim80(cleaned, ellipsis=True) or "work"
        return cleaned

    if work_title and _readable(work_title):
        return finish(work_title)
    # 1.187.0: stop at the first verify item, the same cut as task_order.task_name.
    text = task_order.cut_verify(rest or "")
    text = MARKER.sub(" ", text)
    text = HOST_MARK.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    cuts = []
    for pattern in (r" \(", r", in ", r"\.(?:\s|$)"):
        match = re.search(pattern, text)
        if match:
            cuts.append(match.start())
    if cuts:
        text = text[:min(cuts)]
    text = NAMED_BRANCH.sub(" ", text)
    return finish(text)


def work_item_titles(text):
    """`task: T# <title>` lines from work-item.md. The ADO suffix is not part of the title."""
    titles = {}
    for line in (text or "").splitlines():
        match = WI_TASK.search(line.strip())
        if match:
            titles[int(match.group(1))] = re.sub(r"\s+", " ", match.group(2)).strip()
    return titles


def committed_later(rest):
    match = COMMITTED_LATER.search(rest or "")
    if not match:
        return None
    token = branch_token(match.group(1))
    return token or None


def branches_named_in_text(rest):
    """Branch names written on the task line, in the order they appear."""
    found = []

    def add(token):
        token = branch_token(token)
        if token and token not in found:
            found.append(token)

    for match in BRANCH_MARK.finditer(rest or ""):
        add(match.group(1))
    for match in COMMITTED_LATER.finditer(rest or ""):
        add(match.group(1))
    for match in NAMED_BRANCH.finditer(rest or ""):
        add(match.group(1).rstrip(".,;:"))
    for match in MAP_MARK.finditer(rest or ""):
        add(match.group(1))
    return found


def mismatch_note(row, rests, step_name=None):
    """One note when the row is not the only branch in view. Otherwise None.

    A branch in the task text that is not the row stays
    `Task text names feat/x; built on feat/y`. When the row is the task-line
    branch and the plan step's name is the other one, the note points that
    way: `Plan step names feat/step; built on feat/y`.
    """
    named = []
    for rest in rests:
        for token in branches_named_in_text(rest):
            if token != row and token not in named:
                named.append(token)
    if named:
        if len(named) == 1:
            listed = named[0]
        elif len(named) == 2:
            listed = f"{named[0]} and {named[1]}"
        else:
            listed = ", ".join(named[:-1]) + ", and " + named[-1]
        return f"Task text names {listed}; built on {row}"
    if step_name and step_name != row:
        return f"Plan step names {step_name}; built on {row}"
    return None


def sentence_branch(rest):
    """A branch written in the task sentence, outside the marks and `committed later on`."""
    text = BRANCH_MARK.sub(" ", rest or "")
    text = MAP_MARK.sub(" ", text)
    text = COMMITTED_LATER.sub(" ", text)
    match = NAMED_BRANCH.search(text)
    if not match:
        return None
    return match.group(1).rstrip(".,;:")


def stated_base(rest, branch):
    """The `from <base>` written after this branch on the task line, or None."""
    if not branch:
        return None
    match = re.search(
        re.escape(branch) + r"\s+from\s+`?([A-Za-z0-9][A-Za-z0-9._/-]*)`?",
        rest or "",
        re.I,
    )
    if not match:
        return None
    return match.group(1).rstrip(".,;:")


def paragraph_branches(text):
    """Branch named for each task in a leading Branches paragraph.

    A clause such as `chore/merge-main-into-develop` (T4) assigns that
    branch to T4. Ranges such as (T9–T12) and possessives such as
    (T1's and T45's) assign the preceding named branch. A T# that
    appears only as `after T4` outside the clause's first parentheses
    is not assigned.
    """
    mapping = {}
    if not text:
        return mapping
    match = re.search(r"^Branches\b", text, re.I | re.M)
    if not match:
        return mapping
    rest = text[match.start():]
    stop = re.search(r"^\s*-\s*\[[ xX]\]\s*T\d+", rest, re.M)
    if stop:
        rest = rest[:stop.start()]
    heading = re.search(r"^##?\s+", rest[1:], re.M)
    if heading:
        rest = rest[: heading.start() + 1]
    found = list(NAMED_BRANCH.finditer(rest))
    for i, hit in enumerate(found):
        name = hit.group(1).rstrip(".,;:")
        end = found[i + 1].start() if i + 1 < len(found) else len(rest)
        clause = rest[hit.end():end]
        paren = re.search(r"\(([^)]*)\)", clause)
        if not paren:
            continue
        for tm in re.finditer(r"T(\d+)(?:'s)?(?:\s*[–-]\s*T?(\d+))?", paren.group(1), re.I):
            start_id = int(tm.group(1))
            end_id = int(tm.group(2)) if tm.group(2) else start_id
            if end_id < start_id:
                start_id, end_id = end_id, start_id
            if end_id - start_id > 40:
                continue
            for tid in range(start_id, end_id + 1):
                mapping[tid] = name
    return mapping


def task_line_choice(task, paragraph_branch=None, avoid=None):
    """Branch named on the task line, and its stated base.

    `(map:)` wins, then `(branch:)`, then the Branches-paragraph name
    for this task when it is not in `avoid`, then a branch in the
    sentence (preferring one not in `avoid`), then `committed later on`.
    Returns `(None, None)` when the line and paragraph name none.
    `avoid` is branch names an open task must not sit on when another
    name exists: a done sibling's branch, or a branch git already merged.
    """
    rest = task.get("rest") or ""
    skipped = set(avoid or ())
    if task.get("map"):
        return task["map"], stated_base(rest, task["map"])
    if task.get("branch"):
        return task["branch"], stated_base(rest, task["branch"])
    named = branches_named_in_text(rest)
    candidates = list(named)
    if paragraph_branch and paragraph_branch not in candidates:
        candidates.append(paragraph_branch)
    if not candidates:
        return None, None
    preferred = [name for name in candidates if name not in skipped]
    pool = preferred or list(candidates)
    if paragraph_branch and paragraph_branch in preferred:
        chosen = paragraph_branch
    elif preferred and skipped:
        # A predecessor on the line was skipped; the later name is usually
        # this task's own branch (`after feat/merged, on chore/own`).
        chosen = preferred[-1]
    elif preferred:
        chosen = preferred[0]
    elif paragraph_branch and paragraph_branch in pool:
        chosen = paragraph_branch
    else:
        chosen = pool[0]
    return chosen, stated_base(rest, chosen)


# A recorded merge ties `merged` to the PR mark itself, as in `(PR 78, merged)`
# or `(PR 78) merged`. A future line such as `(PR 12) ... to be merged into
# develop` is not a recorded merge.
_PR_MERGED = re.compile(r"\(PR\s+\d+\s*(?:,\s*merged|merged|\)\s*merged)\b", re.I)


def _pr_merged_line(line):
    return bool(_PR_MERGED.search(line or ""))


def task_records_merge(task):
    """This task's own line records its pull request as merged."""
    return _pr_merged_line(task.get("rest") or "")


def merged_branch_names(*texts):
    """Branch names a line records as merged. Local text only. No network."""
    found = []
    for text in texts:
        for line in (text or "").splitlines():
            if not _pr_merged_line(line):
                continue
            for token in branches_named_in_text(line):
                if token not in found:
                    found.append(token)
            if "branch:" in line.lower():
                body = re.sub(r"\([^)]*\)", " ", line.split(":", 1)[-1])
                token = branch_token(body)
                if token and token not in found:
                    found.append(token)
    return found


def _git(repo, *args):
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def find_repo(start):
    """The git work tree that holds `start`, or None. Does not fetch."""
    if not start:
        return None
    path = pathlib.Path(start).resolve()
    if path.is_file():
        path = path.parent
    for parent in [path, *path.parents]:
        if (parent / ".git").exists():
            return parent
    return None


def _rev(repo, ref):
    if not ref or str(ref).startswith("-"):
        return None
    return _git(repo, "rev-parse", "--verify", "--quiet", ref)


def _branch_tips(repo, name):
    """Tips of the local branch and every remote-tracking ref with this name."""
    if not name or name.startswith("-"):
        return []
    tips = []
    local = _rev(repo, f"refs/heads/{name}")
    if local:
        tips.append(local.strip())
    listed = _git(repo, "for-each-ref", "--format=%(objectname) %(refname)", "refs/remotes") or ""
    suffix = "/" + name
    for line in listed.splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2 and parts[1].endswith(suffix):
            tip = parts[0].strip()
            if tip and tip not in tips:
                tips.append(tip)
    return tips


def _base_tips(repo, stated):
    """Tips of the stated base and the default branch. Equal tips are kept once."""
    names = []
    if stated and not str(stated).startswith("-"):
        names.append(stated)
    symbolic = _git(repo, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if symbolic:
        names.append(symbolic.strip().split("refs/remotes/")[-1].split("/", 1)[-1])
    else:
        for candidate in ("main", "master"):
            if _rev(repo, f"refs/heads/{candidate}") or _rev(repo, f"refs/remotes/origin/{candidate}"):
                names.append(candidate)
                break
    tips = []
    seen = set()
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        for ref in (f"refs/heads/{name}", f"refs/remotes/origin/{name}"):
            tip = _rev(repo, ref)
            if tip and tip.strip() not in tips:
                tips.append(tip.strip())
    return tips


def _strictly_contained(repo, tip, base_tip):
    """True when `tip` is already in `base_tip` and the two are not the same commit.

    A branch cut from the base and not yet committed has the same tip. That
    branch is not merged.
    """
    if not tip or not base_tip or tip == base_tip:
        return False
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor", tip, base_tip],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return proc.returncode == 0


def _reflog_mentions(repo, name):
    text = _git(repo, "reflog", "show", "-n", "800", "--format=%gs", "HEAD") or ""
    return re.search(rf"(?<![\w./-]){re.escape(name)}(?![\w./-])", text) is not None


# Remote heads and open pull requests, read once per build (1.160.0).
_REMOTE_CACHE = {}


def _remote_check_off():
    return os.environ.get("CRAV1_NO_REMOTE_CHECK", "").strip() not in ("", "0")


def _ls_remote(repo, remote):
    """`git ls-remote --heads <remote>` that never prompts for a login. None when it fails."""
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "never"
    env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes")
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "ls-remote", "--heads", remote],
            capture_output=True,
            stdin=subprocess.DEVNULL,
            text=True,
            timeout=15,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def _remote_heads(repo):
    """Remote name to the set of branch heads it really has, from `git ls-remote --heads`.

    Read once per build. A remote that cannot be reached is left out, so a
    branch is never called gone from a remote nobody could read.
    """
    key = ("heads", str(repo))
    if key in _REMOTE_CACHE:
        return _REMOTE_CACHE[key]
    found = {}
    if not _remote_check_off():
        for remote in (_git(repo, "remote") or "").split():
            if remote.startswith("-"):
                continue
            listed = _ls_remote(repo, remote)
            if listed is None:
                continue
            heads = {}
            for line in listed.splitlines():
                parts = line.split("\t", 1)
                if len(parts) == 2 and parts[1].startswith("refs/heads/"):
                    heads[parts[1][len("refs/heads/"):].strip()] = parts[0].strip()
            found[remote] = heads
    _REMOTE_CACHE[key] = found
    return found


def _gh_command():
    value = os.environ.get("CRAV1_GH")
    if value is not None:
        return value.strip() or None
    return shutil.which("gh")


def _open_prs(repo):
    """Open pull requests as (number, head branch), from `gh pr list`. Empty when gh is missing or fails."""
    key = ("prs", str(repo))
    if key in _REMOTE_CACHE:
        return _REMOTE_CACHE[key]
    found = []
    gh = None if _remote_check_off() else _gh_command()
    if gh:
        try:
            proc = subprocess.run(
                [gh, "pr", "list", "--state", "open", "--limit", "200", "--json", "number,headRefName"],
                cwd=str(repo),
                capture_output=True,
                stdin=subprocess.DEVNULL,
                text=True,
                timeout=20,
            )
            if proc.returncode == 0:
                for row in json.loads(proc.stdout or "[]"):
                    head = str(row.get("headRefName") or "").strip()
                    if head and row.get("number") is not None:
                        found.append((int(row["number"]), head))
        except (OSError, subprocess.TimeoutExpired, ValueError, TypeError):
            found = []
    _REMOTE_CACHE[key] = found
    return found


TASK_PR = re.compile(r"(?<![\w/])PR\s*#?(\d+)\b|/(?:pull|pullrequest)/(\d+)", re.I)


def task_pr_numbers(rest):
    """Pull request numbers written on a task line, such as `PR 71`."""
    numbers = []
    for match in TASK_PR.finditer(rest or ""):
        number = int(match.group(1) or match.group(2))
        if number not in numbers:
            numbers.append(number)
    return numbers


def open_pr_for(repo, name, numbers=None):
    """The open pull request whose head is `name`, or None. A number on the task line is preferred."""
    if repo is None or not name:
        return None
    heads = [number for number, head in _open_prs(repo) if head == name]
    if not heads:
        return None
    for number in numbers or []:
        if number in heads:
            return number
    return heads[0]


def _remote_only(repo, name):
    """The remote that has `name` when the local branch is gone, or None."""
    listed = _git(repo, "for-each-ref", "--format=%(refname)", "refs/remotes") or ""
    for line in listed.splitlines():
        ref = line.strip()
        if ref.endswith("/" + name) and ref.count("/") >= 3:
            remote = ref[len("refs/remotes/"):][: -len(name) - 1]
            if remote and "/" not in remote:
                return remote
    for remote, heads in _remote_heads(repo).items():
        if name in heads:
            return remote
    return None


# The code repo for a task (1.160.0). The specs repo and the code repo can be
# separate checkouts. A branch is only checked in the repo that holds it.
CODE_REPO_LINE = re.compile(r"^\s*(?:[-*]\s+)?(?:\*\*)?Repo:(?:\*\*)?\s*(.+?)\s*$", re.I | re.M)
MATCH_BRANCH_LINE = re.compile(r"^\s*(?:[-*]\s+)?(?:\*\*)?Branch:(?:\*\*)?\s*(.+?)\s*$", re.I | re.M)
NOT_FOUND = "not found"


def _repo_word(value):
    """A repo name from `orders-ops`, `contoso/orders-ops`, or a clone URL."""
    words = [word.strip("`<>.,;:()") for word in (value or "").split()]
    words = [word for word in words if word]
    if not words:
        return None
    plain = [word for word in words if "://" not in word and "@" not in word]
    word = plain[0] if plain else words[0]
    word = word.rstrip("/")
    if word.endswith(".git"):
        word = word[:-4]
    word = re.split(r"[/:]", word)[-1]
    return word or None


def _mark_repo(value):
    """The repo word in `(branch: <repo> <name>)`, or None when the mark is only a branch."""
    parts = (value or "").replace("\r", " ").split()
    return _repo_word(parts[0]) if len(parts) >= 2 else None


def task_repo_name(task, spec_text, tasks_text, branch):
    """The repo a task's branch lives in, or None when nothing names one.

    In order: a repo prefix on `(map:)` or `(branch:)`, a Match `Branch:`
    line in the spec that names this branch with a repo, then a `Repo:`
    line in tasks.md.
    """
    rest = task.get("rest") or ""
    for mark in (MAP_MARK, BRANCH_MARK):
        found = mark.search(rest)
        if found and branch_token(found.group(1)) == branch:
            name = _mark_repo(found.group(1))
            if name:
                return name
    for line in MATCH_BRANCH_LINE.findall(spec_text or ""):
        words = re.sub(r"\(.*?\)", " ", line).split()
        if len(words) >= 2 and words[-1].strip("`.,;:") == branch:
            name = _repo_word(words[0])
            if name and name != branch:
                return name
    found = CODE_REPO_LINE.search(tasks_text or "")
    if found:
        return _repo_word(found.group(1))
    return None


def _origin_name(repo):
    url = (_git(repo, "remote", "get-url", "origin") or "").strip()
    return _repo_word(url) if url else None


def _relative_repo(specs_repo, task_repo):
    """The code repo as a path from the specs repo, or None when it is the specs repo."""
    if not task_repo or task_repo == NOT_FOUND or specs_repo is None:
        return str(task_repo) if task_repo and task_repo != NOT_FOUND and specs_repo is None else None
    if pathlib.Path(task_repo).resolve() == pathlib.Path(specs_repo).resolve():
        return None
    try:
        return os.path.relpath(str(task_repo), str(specs_repo)).replace(os.sep, "/")
    except ValueError:
        return str(task_repo)


def resolve_code_repo(specs_repo, name, explicit=None):
    """The checkout that holds repo `name`, `NOT_FOUND`, or `specs_repo` when no repo is named.

    `explicit` (`--code-repo PATH`) wins. Otherwise the specs repo when its
    folder or its origin has that name, else a sibling checkout with that
    folder name, else `NOT_FOUND`. Never guesses another repo.
    """
    if explicit:
        found = find_repo(explicit)
        return found if found else NOT_FOUND
    if not name:
        return specs_repo
    if specs_repo is None:
        return None
    low = name.lower()
    if specs_repo.name.lower() == low or (_origin_name(specs_repo) or "").lower() == low:
        return specs_repo
    parent = specs_repo.parent
    try:
        children = list(parent.iterdir())
    except OSError:
        children = []
    for child in children:
        if child.is_dir() and child.name.lower() == low and (child / ".git").exists():
            return child
    for child in children:
        if child.is_dir() and child != specs_repo and (child / ".git").exists():
            if (_origin_name(child) or "").lower() == low:
                return child
    return NOT_FOUND


def branch_fate(name, spec_text, tasks_text, repo, stated, prs=None):
    """`ok`, `remote`, `absent`, `merged`, `deleted`, or `unchecked`.

    `absent` means the name is not on disk, not on any remote, and was not
    checked out here, so it can be created. `remote` means the local branch
    is missing but a remote has it (a remote-tracking ref, or `git ls-remote`
    shows it), or an open pull request has it as its head; checkout creates
    the local tracking branch (1.160.0). `merged` means git proves the tip is
    already in the base or the default branch. A recorded merge in the specs
    is not enough to skip the name when git is missing, offline, or shows the
    tip is not contained. `deleted` means the branch was checked out here and
    is now gone locally and on every remote that could be read. An open pull
    request whose head is the name wins over `merged` and `deleted`.
    `unchecked` means git could not tell. `prs` are the pull request numbers
    on the task line. No fetch: remotes are read with `git ls-remote`.
    """
    if not name:
        return "absent"
    if repo is None:
        return "unchecked"
    local = _rev(repo, f"refs/heads/{name}") if not name.startswith("-") else None
    tips = _branch_tips(repo, name)
    if tips and any(_strictly_contained(repo, tip, base) for tip in tips for base in _base_tips(repo, stated)):
        if open_pr_for(repo, name, prs):
            return "ok" if local else "remote"
        return "merged"
    if local:
        return "ok"
    if not name.startswith("-") and _remote_only(repo, name):
        return "remote"
    if open_pr_for(repo, name, prs):
        return "remote"
    if _reflog_mentions(repo, name):
        return "deleted"
    return "absent"


def _why(name, fate, repo=None, prs=None):
    if fate == "merged":
        return f"{name} is already merged"
    if fate == "deleted":
        return f"{name} was deleted locally and on the remote"
    if fate == "unchecked":
        return f"could not check whether {name} is merged"
    if fate == "remote":
        number = open_pr_for(repo, name, prs)
        remote = _remote_only(repo, name) if repo is not None else None
        where = f"on {remote} only" if remote else "not local"
        if number:
            return f"{name} is {where} and PR {number} is open from it; checkout creates the local tracking branch"
        return f"{name} is {where}; checkout creates the local tracking branch"
    return None


PERSON_NAME = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b")


def drop_names(text):
    """Drop capitalized person-name sequences from free text used in a slug."""
    return PERSON_NAME.sub(" ", text or "")


def _fresh_name(slug, label, used, avoided, task_id=None):
    """A short fallback branch. Never built from a person's name."""
    blocked = set(used) | {name for name in avoided if name}
    slug_part = kebab(slug, 4)
    label_part = kebab(drop_names(label), 2, fallback="")
    if label_part:
        base = f"feat/{slug_part}-{label_part}"
    elif task_id is not None:
        base = f"feat/{slug_part}-t{task_id}"
    else:
        base = f"feat/{slug_part}-work"
    name = base
    n = 2
    while name in blocked:
        name = f"{base}-{n}"
        n += 1
    used.add(name)
    return name


def kebab(text, limit=4, fallback="work"):
    words = re.findall(r"[a-z0-9]+", clean_prose(drop_names(text)).lower())
    words = [w for w in words if w not in STOP]
    if not words:
        return fallback
    return "-".join(words[:limit])


def _section(text, heading):
    lines = (text or "").splitlines()
    start = None
    want = heading.strip().lower()
    for i, line in enumerate(lines):
        if line.strip().lower() == want:
            start = i + 1
            break
    if start is None:
        return []
    out = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        out.append(line)
    return out


def parse_steps(plan_text):
    steps = []
    current = None
    for line in _section(plan_text, "## Approach"):
        match = STEP_LINE.match(line.strip())
        if match and match.group(2).strip():
            if current:
                steps.append(current)
            current = {"n": int(match.group(1)), "parts": [match.group(2).strip()]}
        elif match and not match.group(2).strip():
            if current:
                steps.append(current)
            current = None
        elif current is not None:
            part = line.strip()
            if part:
                current["parts"].append(part)
    if current:
        steps.append(current)
    for step in steps:
        step["body"] = " ".join(step["parts"])
        step["ids"] = [int(n) for n in TASK_ID.findall(step["body"])]
    return steps


def task_areas(rest):
    """Shared work a branch can collide on. A note only; it does not change readiness.

    A requirement is the text of `(spec: …)`, case folded. A path is a backtick
    span that contains `/` or a file extension, compared exactly as written.
    """
    areas = set()
    for match in SPEC_MARK.finditer(rest or ""):
        token = clean_prose(match.group(1)).lower()
        if token:
            areas.add(("requirement", token))
    for match in TICK_PATH.finditer(rest or ""):
        path = match.group(1).strip()
        if " " in path:
            continue
        if "/" in path or re.search(r"\.[A-Za-z0-9]+$", path):
            areas.add(("path", path))
    return areas


def parse_tasks(text):
    parsed = task_order.parse(text or "")
    extras = []
    for line in (text or "").splitlines():
        match = task_order.TASK.match(line)
        if not match:
            continue
        rest = match.group(3)
        step = STEP_MARK.search(rest)
        mapped = MAP_MARK.search(rest)
        marked = BRANCH_MARK.search(rest)
        extras.append({
            "step": int(step.group(1)) if step else None,
            "map": branch_token(mapped.group(1)) if mapped else None,
            "branch": branch_token(marked.group(1)) if marked else None,
            "areas": task_areas(rest),
            "rest": rest,
        })
    for task, extra in zip(parsed, extras):
        task.update(extra)
    return parsed


def _first_sentence(text):
    return question_blocks._first_sentence(text or "")


def _questions_for(task_id, questions):
    token = f"T{task_id}"
    holding = []
    for question in questions:
        if question["mark"] == "none":
            continue
        if question["mark"] in ("tasks", "inferred"):
            if token in question["tasks"]:
                holding.append(question)
        elif question["blocks_slice"]:
            holding.append(question)
    return holding


def _suggest(slug, label, used):
    base = f"feat/{kebab(slug, 6)}-{kebab(label)}"
    name = base
    n = 2
    while name in used:
        name = f"{base}-{n}"
        n += 1
    used.add(name)
    return name


def _branch_loops(order, waits):
    """Groups of branches that wait for each other (1.154.0).

    Each group is a strongly connected set of two or more branches in the
    branch wait graph, listed in map order. A branch in no group is not in
    a loop.
    """
    order = list(order)
    names = set(order)
    rank = {name: index for index, name in enumerate(order)}
    index_of, low, on_stack, stack, groups = {}, {}, set(), [], []
    counter = [0]

    def strong(node):
        index_of[node] = low[node] = counter[0]
        counter[0] += 1
        stack.append(node)
        on_stack.add(node)
        for dep in waits.get(node, ()):
            if dep not in names:
                continue
            if dep not in index_of:
                strong(dep)
                low[node] = min(low[node], low[dep])
            elif dep in on_stack:
                low[node] = min(low[node], index_of[dep])
        if low[node] == index_of[node]:
            group = []
            while True:
                item = stack.pop()
                on_stack.discard(item)
                group.append(item)
                if item == node:
                    break
            if len(group) > 1:
                groups.append(sorted(group, key=lambda name: rank[name]))

    for node in order:
        if node not in index_of:
            strong(node)
    return sorted(groups, key=lambda group: rank[group[0]])


def _waves(order, waits, loops):
    """Wave per branch: one more than the latest wave it waits for (1.154.0).

    The branches in one loop share a wave. Every other wait puts the later
    branch in a strictly later wave, so a branch never sits in a wave at or
    before a branch it waits for. Branches downstream of a loop still get a
    wave instead of disappearing into Blocked.
    """
    comp = {name: name for name in order}
    for group in loops:
        for name in group:
            comp[name] = group[0]
    members = {}
    for name in order:
        members.setdefault(comp[name], []).append(name)
    deps = {key: set() for key in members}
    for name in order:
        for dep in waits.get(name, ()):
            if dep in comp and comp[dep] != comp[name]:
                deps[comp[name]].add(comp[dep])
    wave = {}
    for key in members:
        if key in wave:
            continue
        work = [(key, False)]
        while work:
            node, ready = work.pop()
            if node in wave:
                continue
            if ready:
                wave[node] = 1 + max((wave[dep] for dep in deps[node]), default=0)
                continue
            work.append((node, True))
            for dep in deps[node]:
                if dep not in wave:
                    work.append((dep, False))
    return {name: wave[comp[name]] for name in order}


def _loop_link(edge, id_branch):
    """`T14 on feat/x waits for T13 on feat/y` for one wait inside a loop."""
    task_id, dep_id, recorded = edge
    text = (
        f"T{task_id} on {id_branch[task_id]['name']} waits for "
        f"T{dep_id} on {id_branch[dep_id]['name']}"
    )
    if not recorded:
        text += " (the task just before it, no (after:) mark)"
    return text


def loop_line(group, why, id_branch):
    """The plain warning for one loop (1.154.0).

    It names the branches and the task line behind each direction of the
    wait. The offer to fix it follows on its own lines (1.161.0).
    """
    if len(group) == 2:
        head = f"{group[0]} and {group[1]} wait for each other"
    else:
        head = ", ".join(group[:-1]) + f" and {group[-1]} wait for each other in a loop"
    links = []
    for name in group:
        for dep in group:
            if dep == name:
                continue
            edges = why.get((name, dep)) or []
            if not edges:
                continue
            text = _loop_link(edges[0], id_branch)
            if len(edges) > 1:
                more = ", ".join(f"T{edge[0]}" for edge in edges[1:])
                text += f" (also {more})"
            links.append(text)
    if len(links) > 1:
        body = ", ".join(links[:-1]) + ", and " + links[-1]
    else:
        body = links[0] if links else "the waits close a loop"
    return f"Loop: {head}: {body}."


# ---------- loop fixes (1.161.0) ----------

FIX_WORD = re.compile(r"[a-z0-9]+")
FIX_STOP = STOP | {"t", "be", "is", "are", "it", "this", "that", "after", "before", "then", "so", "as", "at"}


def _fix_tokens(text):
    text = NAMED_BRANCH.sub(" ", text or "")
    text = MARKER.sub(" ", text)
    text = TASK_ID.sub(" ", text)
    return {word for word in FIX_WORD.findall(text.lower()) if word not in FIX_STOP and (len(word) > 1 or word.isdigit())}


def _assign_waits(tasks, assign, deps_of=None):
    """Branch waits for one assignment of task ids to branches."""
    waits = {}
    for task in tasks:
        name = assign.get(task["id"])
        if name is None:
            continue
        waits.setdefault(name, [])
        deps = (deps_of or {}).get(task["id"], task["deps"])
        for dep in deps:
            other = assign.get(dep)
            if other is None or other == name:
                continue
            if other not in waits[name]:
                waits[name].append(other)
    return waits


def _loop_sets(names, waits):
    present = [name for name in names if name in waits]
    return {frozenset(group) for group in _branch_loops(present, waits)}


def _ids_text(ids):
    ids = [f"T{i}" for i in ids]
    if len(ids) <= 1:
        return "".join(ids)
    return ", ".join(ids[:-1]) + " and " + ids[-1]


def _runs_text(ids):
    """`T9-T12` for a run of consecutive ids, as the steering example reads."""
    ids = sorted(ids)
    parts, start, prev = [], None, None
    for task_id in ids + [None]:
        if start is None:
            start = prev = task_id
            continue
        if task_id is not None and task_id == prev + 1:
            prev = task_id
            continue
        if prev - start >= 2:
            parts.append(f"T{start}-T{prev}")
        else:
            parts.extend(f"T{i}" for i in range(start, prev + 1))
        start = prev = task_id
    return ", ".join(parts)


def _order_text(group, assign, waits):
    """`Then A holds T9-T12 and merges first, and B runs T13, T14, T15, T16.`"""
    first = [name for name in group if not any(dep in group for dep in waits.get(name, ()))]
    bits = []
    for name in sorted(group, key=lambda n: (n not in first, group.index(n))):
        ids = sorted(task_id for task_id, branch in assign.items() if branch == name)
        if not ids:
            continue
        if name in first:
            bits.append(f"{name} holds {_runs_text(ids)} and merges first")
        else:
            bits.append(f"{name} runs {', '.join(f'T{i}' for i in ids)}")
    if not bits:
        return ""
    if len(bits) == 1:
        return f"Then {bits[0]}."
    return "Then " + ", ".join(bits[:-1]) + ", and " + bits[-1] + "."


def _task_cycle(tasks, deps_of=None):
    """Task ids on a wait cycle between tasks, after an optional change of waits."""
    ids = {task["id"] for task in tasks}
    deps = {task["id"]: (deps_of or {}).get(task["id"], task["deps"]) for task in tasks}
    return set(task_order._cycles(ids, deps))


def _followers(start, src, tasks, assign):
    """The start task plus the open tasks on src that wait on it, directly or through each other."""
    moved = [start]
    changed = True
    while changed:
        changed = False
        for task in tasks:
            if task["id"] in moved or assign.get(task["id"]) != src:
                continue
            if any(dep in moved for dep in task["deps"]):
                moved.append(task["id"])
                changed = True
    return sorted(moved)


def loop_fixes(group, tasks, assign, desc, names):
    """Candidate fixes for one loop, best first (1.161.0).

    A move builds a task, plus the tasks on its branch that wait on it, on
    the branch it waits for. A drop lets one task start without one wait. A
    fix is kept only when that loop is gone and no new loop appears.
    """
    group = list(group)
    gset = set(group)
    by_id = {task["id"]: task for task in tasks}
    before = _loop_sets(names, _assign_waits(tasks, assign))
    mine = {task["id"] for task in tasks if assign.get(task["id"]) in gset}
    # A loop between tasks themselves is not broken by moving a task: only
    # dropping a wait on it helps.
    task_cycle = bool(_task_cycle(tasks) & mine)
    keep = before - {frozenset(group)}
    moves, seen = [], set()
    for task in tasks:
        src = assign.get(task["id"])
        if task["done"] or src not in gset:
            continue
        for dep in task["deps"]:
            target = assign.get(dep)
            if target not in gset or target == src:
                continue
            moved = _followers(task["id"], src, tasks, assign)
            key = (tuple(moved), target)
            if key in seen:
                continue
            seen.add(key)
            if task_cycle or any(by_id[i]["done"] for i in moved):
                continue
            if len(moved) >= sum(1 for branch in assign.values() if branch == src):
                continue
            new = dict(assign)
            for task_id in moved:
                new[task_id] = target
            waits = _assign_waits(tasks, new)
            if not _loop_sets(names, waits) <= keep:
                continue
            words = set()
            for task_id in moved:
                words |= _fix_tokens(by_id[task_id].get("rest") or by_id[task_id]["title"])
            shared = sorted(words & _fix_tokens(desc.get(target, "")))
            overlap = len(shared) / len(words) if words else 0.0
            cross = sorted({d for i in moved for d in by_id[i]["deps"] if assign.get(d) == target})
            moves.append({
                "kind": "move",
                "tasks": moved,
                "source": src,
                "target": target,
                "trigger": task["id"],
                "waits_for": cross,
                "shared": shared,
                "overlap": overlap,
                "assign": new,
                "waits": waits,
            })
    moves.sort(key=lambda fix: (-fix["overlap"], len(fix["tasks"]), -fix["trigger"]))
    drops = []
    for task in tasks:
        src = assign.get(task["id"])
        if task["done"] or src not in gset:
            continue
        for dep in task["deps"]:
            other = assign.get(dep)
            if other not in gset or other == src:
                continue
            deps_of = {task["id"]: [d for d in task["deps"] if d != dep]}
            waits = _assign_waits(tasks, assign, deps_of)
            if not _loop_sets(names, waits) <= keep:
                continue
            if task_cycle and _task_cycle(tasks, deps_of) & mine:
                continue
            drops.append({
                "kind": "drop",
                "tasks": [task["id"]],
                "task": task["id"],
                "dep": dep,
                "recorded": bool(task.get("recorded")),
                "source": src,
                "target": other,
                "assign": dict(assign),
                "waits": waits,
            })
    good = [fix for fix in moves if fix["overlap"] > 0]
    weak = [fix for fix in moves if fix["overlap"] <= 0]
    ordered = good + weak[:1] + drops if good else weak[:1] + drops + weak[1:]
    fixes = ordered[:3]
    problem = _problem_text(group, tasks, assign)
    for fix in fixes:
        fix["problem"] = problem
        fix.update(_fix_words(fix, group))
    return fixes


def _problem_text(group, tasks, assign):
    """One plain sentence on why the branches wait for each other."""
    by_id = {task["id"]: task for task in tasks}
    links = []
    for task in tasks:
        src = assign.get(task["id"])
        if src not in group:
            continue
        for dep in task["deps"]:
            other = assign.get(dep)
            if other in group and other != src:
                links.append((task["id"], src, dep, other))
                break
    if not links:
        return "These branches wait for each other."
    if len(group) == 2 and len(links) >= 2:
        (a, a_src, a_dep, a_other), (b, b_src, b_dep, b_other) = links[-1], links[0]
        if a_src == b_src:
            b = next((link for link in links if link[1] != a_src), links[0])
            b, b_src, b_dep, b_other = b
        return (
            f"T{a} is on {a_src}, but it waits for T{a_dep} on {a_other}, which itself waits "
            f"for {a_src} to merge (T{b} waits for T{b_dep}), so the two branches wait for each other."
        )
    parts = [f"T{t} on {s} waits for T{d} on {o}" for t, s, d, o in links]
    return "; ".join(parts) + ", so these branches wait for each other."


def _fix_words(fix, group):
    """Plain words for one fix: the problem, the change, what stays, the new order."""
    order = _order_text(group, fix["assign"], fix["waits"])
    if fix["kind"] == "move":
        ids = fix["tasks"]
        them = "they" if len(ids) > 1 else "it"
        problem = (
            f"{_ids_text(ids)} {'are' if len(ids) > 1 else 'is'} on {fix['source']}, but {them} "
            f"wait{'' if len(ids) > 1 else 's'} for {_ids_text(fix['waits_for'])} on {fix['target']}, "
            f"which itself waits for {fix['source']} to merge, so the two branches wait for each other."
        ) if len(group) == 2 else fix["problem"]
        after = max(fix["waits_for"]) if fix["waits_for"] else None
        change = f"Build {_ids_text(ids)} on {fix['target']} instead" + (f", right after T{after}." if after else ".")
        stays = "The tasks stay the same; only the branch and pull request they go into change."
        if fix["overlap"] >= 0.34:
            why = f"the plan step for {fix['target']} already describes this work."
        else:
            why = f"{_ids_text(ids)} wait{'' if len(ids) > 1 else 's'} for work on {fix['target']}."
        label = f"Build {_ids_text(ids)} on {fix['target']}"
        detail = " ".join(bit for bit in (problem, change, stays, order) if bit)
        brief = " ".join(bit for bit in (change, stays, order) if bit)
        return {"label": label, "why": why, "detail": detail, "brief": brief,
                "summary": f"builds {_ids_text(ids)} on {fix['target']}, so the loop is gone"}
    task, dep = fix["task"], fix["dep"]
    if len(group) == 2:
        fix["problem"] = (
            f"T{task} is on {fix['source']}, but it waits for T{dep} on {fix['target']}, which itself "
            f"waits for {fix['source']} to merge, so the two branches wait for each other."
        )
    where = "" if fix["recorded"] else f" (T{task} has no (after:) mark, so it waits for the task just before it)"
    change = f"Let T{task} start without waiting for T{dep}{where}."
    stays = "No task moves branch, but this changes the build order: check that T{0} is safe to build before T{1} is merged.".format(task, dep)
    label = f"Let T{task} start without waiting for T{dep}"
    detail = " ".join(bit for bit in (fix["problem"], change, stays, order) if bit)
    brief = " ".join(bit for bit in (change, stays, order) if bit)
    return {"label": label, "why": "it changes the build order, so it is only a fallback.", "detail": detail, "brief": brief,
            "summary": f"lets T{task} start without waiting for T{dep}, so the loop is gone"}


def fix_choice(number):
    return "fix-loop" if number == 1 else f"fix-loop {number}"


def fix_lines(fixes, start=1):
    """The offer under a Loop line: every fix in plain words with its choice word."""
    lines = []
    for offset, fix in enumerate(fixes):
        number = start + offset
        head = "Recommended fix" if offset == 0 else "Other fix"
        text = fix["detail"] if offset == 0 else fix["brief"]
        lines.append(f"{head} (say `{fix_choice(number)}`): {text} Why: {fix['why']}")
    if not fixes:
        lines.append(
            "No single change breaks this loop. Run /crav1-tighten-plan and say which wait should go."
        )
    return lines


def _fix_public(fix, number):
    """The JSON shape of one fix: no internal maps."""
    out = {key: value for key, value in fix.items() if key not in ("assign", "waits")}
    out["number"] = number
    out["word"] = fix_choice(number)
    return out


def loop_card(fixes, start=1, size=2):
    """The question card: a plain question, the recommended fix first, each option saying what happens."""
    if not fixes:
        return None
    options = []
    for offset, fix in enumerate(fixes):
        label = fix["label"] + (" (Recommended)" if offset == 0 else "")
        options.append({"label": label, "word": fix_choice(start + offset), "text": f"{fix['detail']} Why: {fix['why']}"})
    options.append({"label": "Leave it", "word": "stop", "text": "Change nothing. Both branches stay blocked."})
    who = "Two branches wait for each other, so neither can start." if size == 2 else f"{size} branches wait for each other in a loop, so none can start."
    return {"question": f"{who} How should I fix it?", "options": options}


PR_NUM = re.compile(r"\(PR\s+(\d+)\)", re.I)
HTTP_URL = re.compile(r"https://[^\s)>\"']+")
SHA = re.compile(r"\b([0-9a-f]{7,40})\b", re.I)


def pull_requests(spec_text):
    """Branch token to a PR link, or `PR n` when the spec has no repo URL.

    A Match `Branch:` line ending in `(PR n)` is the link. A URL on that line,
    or a URL elsewhere in the spec whose path contains the repo prefix, becomes
    a Markdown link. Azure DevOps URLs use `/pullrequest/`. No network read.
    """
    text = spec_text or ""
    urls = [url.rstrip(").,") for url in HTTP_URL.findall(text)]
    found = {}
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            stripped = stripped[2:].strip()
        if not stripped.lower().startswith("branch:"):
            continue
        body = stripped.split(":", 1)[1].strip()
        pr = PR_NUM.search(body)
        if not pr:
            continue
        number = pr.group(1)
        cleaned = re.sub(r"\([^)]*\)", " ", body)
        token = branch_token(cleaned)
        if not token:
            continue
        found[token] = _pr_evidence(number, body, urls)
    return found


def _join_pr(url, number):
    base = url.rstrip("/")
    low = base.lower()
    if "dev.azure.com" in low or "visualstudio.com" in low or "/_git/" in low:
        return f"[PR {number}]({base}/pullrequest/{number})"
    return f"[PR {number}]({base}/pull/{number})"


def _pr_evidence(number, body, urls):
    line_urls = [url.rstrip(").,") for url in HTTP_URL.findall(body)]
    for url in line_urls:
        low = url.lower().rstrip("/")
        if low.endswith(f"/pull/{number}") or low.endswith(f"/pullrequest/{number}"):
            return f"[PR {number}]({url.rstrip('/')})"
    for url in line_urls:
        return _join_pr(url, number)
    raw = re.sub(r"\([^)]*\)", " ", body).split()
    repo = raw[0].lower() if len(raw) >= 2 and "/" not in raw[0] else ""
    if repo:
        for url in urls:
            low = url.lower()
            if "/pull/" in low or "/pullrequest/" in low:
                continue
            if repo in low:
                return _join_pr(url, number)
    return f"PR {number}"


def task_pr(rest):
    """A pull request URL written on the task line, as a Markdown link."""
    for url in HTTP_URL.findall(rest or ""):
        url = url.rstrip(").,")
        match = re.search(r"/(?:pull|pullrequest)/(\d+)", url, re.I)
        if match:
            return f"[PR {match.group(1)}]({url})"
    return None


OWN_SHA = re.compile(r"(?<![0-9A-Za-z])((?=[0-9a-f]*\d)[0-9a-f]{7,40})(?![0-9A-Za-z])")
MERGE_SHA = re.compile(r"merge\w*\D{0,40}?(?<![0-9A-Za-z])((?=[0-9a-f]*\d)[0-9a-f]{7,40})(?![0-9A-Za-z])", re.I)
ROW_LEAD = re.compile(r"^[\s|>*_`\-]*(?:\[[ xX]\]\s*)?[*_`]*T(\d+)\b")


def _pick_sha(text):
    """The merge commit on a line when one is named, else the first commit."""
    merged = MERGE_SHA.search(text or "")
    if merged:
        return merged.group(1)[:12]
    found = OWN_SHA.search(text or "")
    return found.group(1)[:12] if found else None


def verify_sha(text, task_id):
    """A commit sha on this task's own verify row, or None (1.173.0).

    Only a row whose first cell or first word is this task id counts. A
    Date line, a gaps note, or another task's row that merely mentions the
    id never lends its commit to this task.
    """
    if not text:
        return None
    for line in text.splitlines():
        lead = ROW_LEAD.match(line)
        if not lead or int(lead.group(1)) != int(task_id):
            continue
        sha = _pick_sha(line)
        if sha:
            return sha
    return None


def progress_shas(directory):
    """Merge commits from build-progress/*.md, as {task id: sha} (1.173.0).

    A file counts for the tasks on its own `Tasks:` line. The commit comes
    from the `Result:` line of that file's `Step: merge-pr` (1.174.0). A tick
    or commit step's hash is only a fallback, kept under ("tick", key), and
    never replaces a merge hash, wherever it sits in the file.
    """
    found = {}
    folder = pathlib.Path(directory) / "build-progress"
    if not folder.is_dir():
        return found
    for path in sorted(folder.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        ids = []
        branch = None
        merge_sha = None
        other_sha = None
        step = ""
        for line in text.splitlines():
            stripped = line.strip().lstrip("-").strip()
            lower = stripped.lower()
            if lower.startswith("tasks:"):
                ids = [int(n) for n in re.findall(r"\bT(\d+)\b", stripped)]
            elif lower.startswith("branch:") and branch is None:
                branch = stripped.split(":", 1)[1].strip()
            elif lower.startswith("step:"):
                step = stripped.split(":", 1)[1].strip().lower()
            elif re.match(r"result:\s*(done|merged)\b", stripped, re.I):
                picked = _pick_sha(stripped.split(":", 1)[1])
                if not picked:
                    continue
                if step.startswith("merge-pr") or step.startswith("merge pr"):
                    merge_sha = picked
                elif other_sha is None:
                    other_sha = picked
        # 1.182.0: a task a build step names counts too, header or not.
        for extra in task_state.progress_tasks(text)["all"]:
            if int(extra[1:]) not in ids:
                ids.append(int(extra[1:]))
        for sha, wrap in ((merge_sha, lambda key: key), (other_sha, lambda key: ("tick", key))):
            if not sha:
                continue
            for task_id in ids:
                found.setdefault(wrap(task_id), sha)
            if branch:
                found.setdefault(wrap(branch), sha)
    return found


def progress_state(directory):
    """Each branch's walk from build-progress/*.md, as {branch: state} (1.174.0).

    A state is {"built": {task ids}, "pr": number or None, "merged": bool,
    "tasks": {ids on the header's Tasks: line, plus any task a build step
    names (1.182.0)}, "failed": bool} (tasks:
    1.177.2). `failed` (1.178.0) is true when a step's last `Result:` is
    failed or reopened (a failed check, a reopened step), so the map's box
    turns red.
    A task counts as built from a done `Step: build T#` or a `- Built: T#`
    run row. The pull request is the last `PR <n>` the file names.
    """
    found = {}
    folder = pathlib.Path(directory) / "build-progress"
    if not folder.is_dir():
        return found
    for path in sorted(folder.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        branch = None
        built = set()
        merged = False
        step = ""
        listed = set()
        last_result: dict = {}
        for line in text.splitlines():
            stripped = line.strip()
            lower = stripped.lower()
            if lower.startswith("tasks:") and not step and not listed:
                listed = {int(n) for n in re.findall(r"\bT(\d+)\b", stripped)}
            elif lower.startswith("branch:") and branch is None:
                branch = stripped.split(":", 1)[1].strip()
            elif lower.startswith("- step:"):
                step = stripped.split(":", 1)[1].strip().lower()
            elif lower.startswith("- built:"):
                built.update(int(n) for n in re.findall(r"\bT(\d+)\b", stripped.split(",", 1)[0]))
            elif re.match(r"result:\s*(failed|fail|reopened)\b", stripped, re.I):
                last_result[step] = "failed"
            elif re.match(r"result:\s*(done|merged)\b", stripped, re.I):
                last_result[step] = "done"
                if step.startswith("build "):
                    built.update(int(n) for n in re.findall(r"\bt(\d+)\b", step))
                elif step.startswith("merge-pr"):
                    merged = True
        # 1.182.0: any build step naming a task makes it built (waiting for
        # the merge) and one of the branch's tasks, whatever the header lists.
        named = task_state.progress_tasks(text)
        built.update(int(task[1:]) for task in named["built"])
        listed.update(int(task[1:]) for task in named["all"])
        prs = re.findall(r"\b(?:PR|pull request)\s+#?(\d+)", text, re.I)
        key = branch or path.stem.replace("--", "/")
        failed = any(value == "failed" for value in last_result.values())
        # 1.180.0: the walk's last step is comment or wait-merge, the same
        # rule the ready check uses for tasks that wait on the merge.
        waits = step in ("comment", "wait-merge") and not merged
        found[key] = {"built": built, "pr": int(prs[-1]) if prs else None, "merged": merged, "tasks": listed,
                      "failed": failed and not merged, "wait_merge": waits}
    return found


def map_marks(map_text):
    """The done marks already on build-map.md, as {task id: evidence} (1.173.0)."""
    marks = {}
    for match in re.finditer(r"~~T(\d+)\b[^~\n]*~~ ✓ done \(", map_text or ""):
        start = match.end()
        depth = 1
        index = start
        while index < len(map_text) and depth:
            char = map_text[index]
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            elif char == "\n":
                break
            index += 1
        if depth == 0:
            marks.setdefault(int(match.group(1)), map_text[start:index - 1])
    return marks


def done_evidence(task, branch_name, prs, verify_text, progress=None, existing=None):
    """PR link, else the recorded branch, else the task's own commit, else the old mark.

    The commit is the merge commit from the branch's build-progress file, else
    the commit on the task's own verify row (1.173.0). A commit another task
    or branch names is never used. With no own commit, an existing done mark
    stays as it was. A tick or commit step's hash comes after that (1.174.0),
    and only then the row branch is written.
    """
    direct = task_pr(task.get("rest") or "")
    if direct:
        return direct
    recorded = task.get("map") or task.get("branch") or committed_later(task.get("rest") or "")
    for key in (recorded, branch_name):
        if key and key in prs:
            return prs[key]
    if recorded:
        return recorded
    progress = progress or {}
    sha = progress.get(task["id"]) or progress.get(branch_name)
    if sha:
        return sha
    sha = verify_sha(verify_text, task["id"])
    if sha:
        return sha
    kept = (existing or {}).get(task["id"])
    if kept:
        return kept
    # A tick or commit step's hash only when there is no merge result, no
    # verify row and no earlier mark (1.174.0).
    sha = progress.get(("tick", task["id"])) or progress.get(("tick", branch_name))
    if sha:
        return sha
    return branch_name


def _explicit(task):
    """(map:) wins over (branch:). Either one names the row instead of the step."""
    if task.get("map"):
        return task["map"]
    if task.get("branch"):
        return task["branch"]
    return None


def apply_task_states(tasks, walks):
    """Each task's state from task_state.py, the decision the ready check and
    finalize-commit use (1.180.0); done follows from it. Returns {T#: state}.

    1.177.2: a walk with a merge-pr result (the walk, /crav1-merge-pr, or the
    ready check's host check) makes the tasks on its Tasks: line done.
    """
    merged_ids = {int(n) for walk in (walks or {}).values() if walk.get("merged") for n in walk.get("tasks") or ()}
    built_ids = {int(n) for walk in (walks or {}).values() if not walk.get("merged") for n in walk.get("built") or ()}
    built_ids |= {int(n) for walk in (walks or {}).values() if walk.get("wait_merge") for n in walk.get("tasks") or ()}
    out = {}
    for task in tasks:
        state = task_state.task_state(task["done"], task["id"] in merged_ids, None, task["id"] in built_ids)
        task["state"] = state["state"]
        task["done"] = state["counts_done"]
        out[f"T{task['id']}"] = state["state"]
    return out


def build(slug, spec_text, plan_text, tasks_text, work_item_text="", verify_text="", resolve_recorded=False, repo=None, claims_text="", code_repo=None, progress=None, existing=None, walks=None):
    """Return markdown, a short chat summary, and the one-line pointer."""
    _REMOTE_CACHE.clear()
    tasks = parse_tasks(tasks_text)
    # 1.177.2: a walk with a merge-pr result (the walk, /crav1-merge-pr, or
    # the ready check's host check) makes the tasks on its Tasks: line done.
    apply_task_states(tasks, walks)
    titles = work_item_titles(work_item_text)
    name_of = {
        task["id"]: short_name(task.get("rest") or task["title"], titles.get(task["id"]))
        for task in tasks
    }
    full_of = {
        task["id"]: short_name(task.get("rest") or task["title"], titles.get(task["id"]), trim=False)
        for task in tasks
    }
    steps = parse_steps(plan_text if plan_text is not None else "")
    has_plan = plan_text is not None
    task_ids = [f"T{task['id']}" for task in tasks]
    questions = question_blocks.kept_open(
        spec_text or "",
        task_ids=task_ids,
        resolve_recorded=resolve_recorded,
    )
    risks = question_blocks.risks(plan_text or "", questions) if has_plan else []
    risk_blocks = any(row["blocks_slice"] for row in risks)
    analysed = task_order.analyse(tasks)
    if claims_text:
        built_open = {}
        for walk in (walks or {}).values():
            if walk.get("merged"):
                continue
            for task_id in walk.get("built") or ():
                built_open[int(task_id)] = walk.get("pr")
        task_order.apply_claim_holds(analysed, tasks, claims_text, built=built_open)
    rows = {row["id"]: row for row in analysed["rows"]}
    claimed_ids = {row["id"] for row in (analysed.get("waiting_in_progress") or [])}
    by_id = {task["id"]: task for task in tasks}
    step_by_n = {step["n"]: step for step in steps}
    # The order the walk runs tasks in, and what an open task still waits on
    # (1.165.0): Run next lists a branch's tasks in this order.
    walk_pos = {task_id: index for index, task_id in enumerate(analysed.get("order") or [])}
    for task in tasks:
        task["walk"] = walk_pos.get(task["id"], 10**6)
        task["waits_on"] = [
            dep for dep in task.get("deps") or []
            if dep in by_id and not by_id[dep]["done"]
        ]
    mentioned = {}
    for step in steps:
        for task_id in step["ids"]:
            mentioned.setdefault(task_id, step["n"])

    prs = pull_requests(spec_text or "")
    # Done tasks stay on the map (1.132.0). They are not dropped.
    open_tasks = list(tasks)
    linked = []
    missing_step = False
    for task in open_tasks:
        owner = task["step"] if task["step"] is not None else mentioned.get(task["id"])
        task["owner"] = owner
        if owner is None:
            continue
        if owner not in step_by_n:
            missing_step = True
            task["owner"] = None
            continue
        linked.append(task)

    if not steps:
        grouping = NO_STEPS
        mode = "fallback"
    elif not linked:
        grouping = UNNAMED
        mode = "fallback"
    else:
        grouping = BY_STEP
        notes = []
        loose = [
            task for task in open_tasks
            if not task["map"] and task.get("owner") not in step_by_n
        ]
        if any(task["step"] is None for task in loose):
            notes.append(SOME)
        if missing_step:
            notes.append(MISSING_STEP)
        if notes:
            grouping = grouping + " " + " ".join(notes)
        mode = "steps"

    used_names = set()
    step_names = {}
    if mode == "steps":
        for step in steps:
            if any(task.get("owner") == step["n"] for task in open_tasks):
                step_names[step["n"]] = _suggest(slug, step["body"], used_names)

    paragraph = paragraph_branches(tasks_text)
    done_branches = set()
    for task in open_tasks:
        if task["done"] or task_records_merge(task):
            name, _base = task_line_choice(task, paragraph.get(task["id"]))
            if name:
                done_branches.add(name)

    resolved = {}
    offers = {}
    for task in open_tasks:
        avoid = None if (task["done"] or task_records_merge(task)) else done_branches
        line_name, line_base = task_line_choice(task, paragraph.get(task["id"]), avoid)
        step_name = step_names.get(task.get("owner")) if mode == "steps" else None
        if line_name:
            planned, source, base = line_name, "task line", line_base
        elif step_name:
            planned, source, base = step_name, "build map", None
        else:
            planned = _suggest(slug, task.get("rest") or task["title"], used_names)
            source, base = "new", None
        chosen, offer_source, offer_base = planned, source, base
        because = None
        checkout = None
        chosen_fate = None
        task_repo = repo
        # A ticked task stays on the branch where that work landed. So does a
        # task whose own line records the merge: the map shows that branch.
        # The offer skips only a name git proves merged or deleted (1.152.0).
        # The task-line branch always wins over an invented name when git
        # cannot tell, or shows the tip is not in the base.
        # An open task is never placed under a branch git proves merged when
        # the task line or the Branches paragraph names another branch, and
        # is never grouped under a done sibling's branch when it has its own
        # name (1.153.0).
        if not task["done"]:
            pr_numbers = task_pr_numbers(task.get("rest") or "")
            repo_name = task_repo_name(task, spec_text, tasks_text, planned)
            task_repo = resolve_code_repo(repo, repo_name, code_repo)
            if task_repo == NOT_FOUND:
                # Never call a branch deleted from a repo that does not hold it.
                fate = "unreachable"
                because = f"could not check {repo_name or 'the code repo'} from here"
                task_repo = None
            else:
                fate = branch_fate(planned, spec_text, tasks_text, task_repo, base or line_base, pr_numbers)
            chosen_fate = fate
            if fate == "unreachable":
                pass
            elif fate == "remote":
                because = _why(planned, fate, task_repo, pr_numbers)
                checkout = planned
            elif fate == "unchecked" and source == "task line" and planned in merged_branch_names(spec_text, tasks_text):
                because = _why(planned, fate)
            elif fate in ("merged", "deleted"):
                because = _why(planned, fate)
                others = []
                for name in branches_named_in_text(task.get("rest") or ""):
                    if name != planned and name not in others:
                        others.append(name)
                para = paragraph.get(task["id"])
                if para and para != planned and para not in others:
                    others.insert(0, para)
                picked_alt = None
                for name in others:
                    other_base = stated_base(task.get("rest") or "", name)
                    other_fate = branch_fate(name, spec_text, tasks_text, task_repo, other_base, pr_numbers)
                    if other_fate not in ("merged", "deleted"):
                        picked_alt = name
                        break
                alt = step_name if source == "task line" and step_name and step_name != planned else None
                alt_fate = branch_fate(alt, spec_text, tasks_text, task_repo, None) if alt else None
                if picked_alt:
                    chosen, offer_source, offer_base = (
                        picked_alt,
                        "task line",
                        stated_base(task.get("rest") or "", picked_alt),
                    )
                    chosen_fate = other_fate
                    if other_fate == "remote":
                        because = because + "; " + _why(picked_alt, other_fate, task_repo, pr_numbers)
                        checkout = picked_alt
                elif alt and alt_fate not in ("merged", "deleted", "unchecked"):
                    chosen, offer_source, offer_base = alt, "build map", None
                    chosen_fate = alt_fate
                elif source == "task line" and fate != "deleted" and task_repo is None:
                    # Offline: keep the task-line branch; do not invent a name.
                    chosen, offer_source, offer_base = planned, source, base
                    because = _why(planned, "unchecked")
                    chosen_fate = "unchecked"
                else:
                    chosen = _fresh_name(
                        slug,
                        task.get("rest") or task["title"],
                        used_names,
                        {planned, alt, picked_alt},
                        task_id=task["id"],
                    )
                    offer_source, offer_base = "new", line_base
                    chosen_fate = "absent"
        on_map = planned if (task["done"] or task_records_merge(task)) else chosen
        if source == "task line" and on_map == line_name:
            used_names.add(on_map)
        elif offer_source == "task line":
            used_names.add(chosen)
        resolved[task["id"]] = on_map
        if not task["done"]:
            offers[task["id"]] = {
                "name": chosen,
                "source": offer_source,
                "base": offer_base,
                "because": because,
                "checkout": checkout if checkout == chosen else None,
                "fate": chosen_fate,
                "repo": str(task_repo) if task_repo else None,
                "code_repo": _relative_repo(repo, task_repo),
            }
        task["step_name"] = step_name

    groups = {}
    for task in open_tasks:
        groups.setdefault(resolved[task["id"]], []).append(task)

    branches = []
    for name, members in sorted(groups.items(), key=lambda item: (min(task["id"] for task in item[1]), item[0])):
        members = sorted(members, key=lambda task: task["id"])
        shorts = []
        shown = []
        for task in members:
            plain = name_of.get(task["id"]) or "work"
            full = full_of.get(task["id"]) or plain
            # build-map.md shows full names, never cut with "..." (1.174.0).
            label = task_label(task["id"], full)
            task["short"] = plain
            task["full"] = full
            task["label"] = label
            task["run_label"] = task_label(task["id"], full)
            if task["done"]:
                evidence = done_evidence(task, name, prs, verify_text, progress, existing)
                shorts.append(f"~~{full}~~ ✓ done ({evidence})")
                shown.append(f"~~{label}~~ ✓ done ({evidence})")
            else:
                shorts.append(full)
                shown.append(label)
        owners = {task.get("owner") for task in members}
        owner = next(iter(owners)) if len(owners) == 1 else None
        if (
            mode == "steps"
            and owner in step_names
            and all(not task_line_choice(task)[0] for task in members)
            and all(resolved[task["id"]] == step_names.get(owner) for task in members)
        ):
            deliver = clean_prose(step_by_n[owner]["body"], full_of) or "; ".join(shorts)
        else:
            deliver = "; ".join(shorts)
        # One plain sentence for Run next (1.164.0): the plan step that owns
        # every task on this branch, even when the task lines name the branch.
        about = ""
        # The description follows the open tasks (1.171.0): the plan step that
        # owns every open task, and not a sentence about a done task.
        open_members = [task for task in members if not task["done"]] or members
        open_owners = {task.get("owner") for task in open_members}
        about_owner = next(iter(open_owners)) if len(open_owners) == 1 else None
        if mode == "steps" and about_owner in step_by_n:
            about = clean_prose(step_by_n[about_owner]["body"], full_of) or ""
            if about and _names_done(about, [task for task in members if task["done"]]):
                about = ""
        areas = set()
        for task in members:
            areas.update(task.get("areas") or ())
        branches.append({
            "key": name,
            "name": name,
            "deliver": deliver or "work",
            "about": about or "",
            "tasks": members,
            "task_ids": [task["id"] for task in members],
            "task_names": shown,
            "areas": areas,
            "note": mismatch_note(
                name,
                [task.get("rest") or "" for task in members],
                step_names.get(owner) if owner in step_names else None,
            ),
        })

    id_branch = {}
    for branch in branches:
        for task_id in branch["task_ids"]:
            id_branch[task_id] = branch

    names = [branch["name"] for branch in branches]
    waits = {branch["name"]: [] for branch in branches}
    wait_why = {}
    unknown = {branch["name"]: False for branch in branches}
    holding = {branch["name"]: [] for branch in branches}
    task_blocked = {branch["name"]: False for branch in branches}
    for branch in branches:
        seen_q = set()
        for task in branch["tasks"]:
            if not task["done"]:
                questions_here = _questions_for(task["id"], questions) if has_plan or spec_text else _questions_for(task["id"], questions)
                if not has_plan:
                    task_blocked[branch["name"]] = True
                elif questions_here:
                    for question in questions_here:
                        marker = question["text"]
                        if marker not in seen_q:
                            seen_q.add(marker)
                            holding[branch["name"]].append(question)
                elif risk_blocks:
                    task_blocked[branch["name"]] = True
                else:
                    reason = (rows.get(task["id"]) or {}).get("reason") or ""
                    low = reason.lower()
                    if "cycle" in low or "names no task" in low:
                        task_blocked[branch["name"]] = True
                    if "names no task" in low:
                        unknown[branch["name"]] = True
            for dep in task["deps"]:
                if dep not in by_id:
                    unknown[branch["name"]] = True
                    task_blocked[branch["name"]] = True
                    continue
                other = id_branch.get(dep)
                if other is None or other["name"] == branch["name"]:
                    continue
                wait_why.setdefault((branch["name"], other["name"]), []).append(
                    (task["id"], dep, bool(task.get("recorded")))
                )
                if other["name"] not in waits[branch["name"]]:
                    waits[branch["name"]].append(other["name"])

    loops = _branch_loops(names, waits)
    cycles = {name for group in loops for name in group}
    for branch in branches:
        name = branch["name"]
        finished = bool(branch["tasks"]) and all(task["done"] for task in branch["tasks"])
        if finished and has_plan and name not in cycles and not task_blocked[name]:
            status = "done"
        elif not has_plan or task_blocked[name] or name in cycles:
            status = "blocked"
        elif holding[name]:
            status = "waiting on a question"
        elif waits[name]:
            status = "waits in order"
        else:
            status = "ready"
        branch["status"] = status
        branch["waits"] = waits[name]
        branch["unknown"] = unknown[name]
        branch["questions"] = holding[name]
        branch["cycle"] = name in cycles
        branch["loop"] = name in cycles
        branch["held_on"] = []

    by_name = {branch["name"]: branch for branch in branches}
    for branch in branches:
        if branch["status"] != "waits in order" or branch["unknown"]:
            continue
        if branch["waits"] and all(by_name[name]["status"] == "done" for name in branch["waits"]):
            branch["status"] = "ready"
    for branch in branches:
        open_ids = [task["id"] for task in branch["tasks"] if not task["done"]]
        if open_ids and all(task_id in claimed_ids for task_id in open_ids) and branch["status"] == "ready":
            branch["status"] = "held"
            branch["held_on"] = [f"T{task_id}" for task_id in open_ids]
        # A branch never waits on its own tasks (1.174.0). Claimed or walked,
        # it reads built and waiting for its pull request, or in progress.
        walk = (walks or {}).get(branch["name"])
        branch["failed"] = bool(open_ids and walk and walk.get("failed"))
        if open_ids and branch["status"] in ("ready", "held") and (
            branch["status"] == "held" and set(branch["held_on"]) <= {f"T{task_id}" for task_id in open_ids}
            or (walk and not walk.get("merged") and walk.get("built"))
        ):
            branch["status"] = "held"
            branch["held_on"] = []
            built = set((walk or {}).get("built") or ())
            pr = (walk or {}).get("pr")
            deadlock = merge_deadlock(branch["tasks"], built, pr) if walk and not walk.get("merged") else None
            if deadlock:
                # 1.180.0 (M4): an open task waits on a task that ticks only
                # when this branch's own PR merges. Blocked, red on the map.
                branch["status"] = "blocked"
                branch["deadlock"] = deadlock
                branch["held_text"] = deadlock
            elif built and all(task["state"] == task_state.MERGE_WAIT for task in branch["tasks"] if not task["done"]):
                branch["held_text"] = f"built, waits for PR {pr} to merge" if pr else "built, waits for its pull request to merge"
            else:
                branch["held_text"] = "in progress"
    held_names = {branch["name"] for branch in branches if branch["status"] in ("waiting on a question", "held")}
    changed = True
    while changed:
        changed = False
        for branch in branches:
            if branch["name"] in held_names or branch["status"] in ("blocked", "done"):
                continue
            deps = [name for name in branch["waits"] if name in held_names]
            if not deps:
                continue
            branch["status"] = "held"
            branch["held_on"] = deps
            held_names.add(branch["name"])
            changed = True

    # One shared wave rule (1.154.0): a loop shares one wave, every other
    # wait is strictly later, and a branch downstream of a loop keeps its
    # own state and wave instead of going under Blocked.
    wave = _waves(names, waits, loops)
    for branch in branches:
        branch["wave"] = wave[branch["name"]]
        if branch["name"] in cycles or branch["status"] == "blocked":
            branch["section"] = "blocked"
        else:
            branch["section"] = "wave"
    loop_rows = []
    assign = {task_id: branch["name"] for task_id, branch in id_branch.items()}
    desc = {}
    for branch in branches:
        bits = []
        for task in branch["tasks"]:
            owner = task.get("owner")
            if owner in step_by_n and step_by_n[owner]["body"] not in bits:
                bits.append(step_by_n[owner]["body"])
        for step in steps:
            if branch["name"] in step["body"] and step["body"] not in bits:
                bits.append(step["body"])
        # The plan step is the branch's own description. Without one, the
        # branch's task names are all there is (no longer shown as Delivers
        # in the map since 1.185.0).
        desc[branch["name"]] = " ".join(bits) or branch["deliver"]
    number = 1
    for group in loops:
        open_ids = [
            task["id"]
            for name in group
            for task in by_name[name]["tasks"]
            if not task["done"]
        ]
        fixes = loop_fixes(group, tasks, assign, desc, names)
        line = loop_line(group, wait_why, id_branch)
        offer = fix_lines(fixes, number)
        loop_rows.append({
            "branches": list(group),
            "line": line,
            "tasks": sorted(open_ids),
            "fixes": [_fix_public(fix, number + index) for index, fix in enumerate(fixes)],
            "fix_lines": offer,
            "card": loop_card(fixes, number, len(group)),
        })
        number += len(fixes)
    for row in loop_rows:
        for name in row["branches"]:
            by_name[name]["loop_line"] = row["line"]

    loop_lines = [text for row in loop_rows for text in [row["line"], *row["fix_lines"]]]
    markdown = _render(slug, grouping, branches, by_name, risks, has_plan, risk_blocks, name_of, loop_lines)
    pointer = f"Build map: docs/specs/{slug}/build-map.md"
    summary = _summary(slug, pointer, branches, loop_lines)
    return {
        "loops": loop_rows,
        "loop_lines": loop_lines,
        "markdown": markdown,
        "summary": summary,
        "pointer": pointer,
        "branches": branches,
        "grouping": grouping,
        "offers": offers,
    }


def recommended_branches(slug, spec_text, plan_text, tasks_text, work_item_text=""):
    """Open task id to the build-map row branch. The same names `build` writes."""
    result = build(slug, spec_text, plan_text, tasks_text, work_item_text)
    found = {}
    for branch in result["branches"]:
        for task in branch["tasks"]:
            if task["done"]:
                continue
            found[task["id"]] = branch["name"]
    return found


def _task_number(task_id):
    try:
        return int(task_id)
    except (TypeError, ValueError):
        match = re.search(r"(\d+)", str(task_id or ""))
        if not match:
            return None
        return int(match.group(1))


def recommendation(slug, spec_text, plan_text, tasks_text, task_id, work_item_text="", repo=None, claims_text="", code_repo=None):
    """The branch to offer for one open task, or None when that task is not open.

    `name` is the branch. `source` is `task line`, `build map`, or `new`.
    `base` is the `from` base on the task line, or None. `because` is one
    plain line when a merged or deleted branch was skipped, or when git
    could not check a task-line branch, or None.
    """
    task_id = _task_number(task_id)
    if task_id is None:
        return None
    result = build(slug, spec_text, plan_text, tasks_text, work_item_text, repo=repo, claims_text=claims_text, code_repo=code_repo)
    offer = (result.get("offers") or {}).get(task_id)
    return dict(offer) if offer else None


def format_offer(offer):
    """The lines `--recommend` prints. The first line is the branch name."""
    lines = [offer["name"], f"source: {offer['source']}"]
    if offer.get("base"):
        lines.append(f"from: {offer['base']}")
    if offer.get("because"):
        lines.append(f"because: {offer['because']}")
    if offer.get("code_repo"):
        lines.append(f"repo: {offer['code_repo']}")
    if offer.get("checkout"):
        lines.append(f"checkout: {offer['checkout']}")
    return "\n".join(lines)


def recommended_branch(slug, spec_text, plan_text, tasks_text, task_id, work_item_text="", repo=None, claims_text=""):
    """The branch `--recommend` offers for one open task, or None."""
    offer = recommendation(slug, spec_text, plan_text, tasks_text, task_id, work_item_text, repo=repo, claims_text=claims_text)
    return offer["name"] if offer else None


def _task_num(token):
    match = re.fullmatch(r"T(\d+)", str(token or "").strip())
    if match:
        return int(match.group(1))
    try:
        return int(token)
    except (TypeError, ValueError):
        return None


# Who for a hold that names nobody (1.170.0). An older "not named yet"
# value reads the same; the line says so in plain words.
NO_WHO = frozenset({"", "not named yet", "nobody named yet", "none", "nobody"})
NOBODY_ANSWERS = "Nobody is named to answer it yet."
NOBODY_GIVES = "Nobody is named to give it yet."
NOBODY_SHORT = "nobody named yet"


def held_phrase(row):
    """The held reason on a ready-check line.

    An open question names the question and who has it. A task that only
    waits on a held task says `held, waits on T#`. The recorded or inferred
    tag stays off this line.
    """
    reason = (row.get("reason") or "").strip()
    who = (row.get("who") or "").strip()
    if who.lower() in NO_WHO:
        who = ""
    core = re.sub(
        r"\s*\((?:recorded|inferred|inferred from the text)\)\s*$",
        "",
        reason,
    ).strip()
    if core.lower().startswith("held, waits on"):
        return core
    match = re.search(r'approval needed "([^"]*)"', reason, re.I)
    if match:
        what = re.split(r"(?<=[.!?])\s", match.group(1).strip(), maxsplit=1)[0]
        wait = f"Waiting for {who}." if who else NOBODY_GIVES
        return f'approval "{what}" {wait}'
    # Greedy to the last quote before the tag (1.166.0): a question that
    # quotes another one keeps its inner quotes.
    match = re.search(r'open question "(.*)"(?=\s+\(|\s+blocks the whole slice|\s*$)', reason)
    if match:
        # Held lines quote the whole question, never cut with "..." (1.176.0).
        question = short_question(match.group(1), limit=100000, quote=row.get("quote"))
        note = ""
        if "blocks the whole slice (recorded)" in reason.lower():
            note = " Holds the whole slice."
        elif "inferred from the text" in reason.lower():
            note = " Inferred from the text."
        wait = f"Waiting for {who}." if who else NOBODY_ANSWERS
        return f'open question "{question}" {wait}{note}'
    return core or "held"


def short_question(text, limit=160, quote=None):
    """The quoted open question, short (1.164.0, 1.165.0, 1.166.0): see
    walk_ending.question_text. A heading-like first sentence, or a pointer
    to a note, gives way to the question itself (the blockquote `quote`
    when there is one), and a long line is cut at a clause end."""
    return _ending_mod().question_text(text, limit, quote=quote)


def _branch_order(branches):
    """Wave order, then the map's row order (lowest first task id)."""
    def key(branch):
        section = 0 if branch.get("section") == "wave" else 1
        wave = branch.get("wave") if branch.get("wave") is not None else 10**9
        first = branch["tasks"][0]["id"] if branch.get("tasks") else 10**9
        return (section, wave, first, branch["name"])

    return sorted(branches, key=key)


def _where(branch):
    """Where a ready or held line sits: `wave N`, or `in a loop` (1.154.0).

    Every branch has a wave now. Only a branch caught in a loop says so.
    """
    if branch.get("loop"):
        return "in a loop"
    if branch.get("wave") is not None:
        return f"wave {branch['wave']}"
    return "blocked"


def loop_holds(built):
    """Open task id to its loop line, from the same build the map writes.

    The ready check uses this so a task on a branch in a loop is blocked in
    both the map and the check (1.154.0). Tasks on other branches keep their
    own state.
    """
    holds = {}
    for row in (built or {}).get("loops") or []:
        for task_id in row["tasks"]:
            holds.setdefault(task_id, row["line"])
    return holds


def wait_reason(task, row=None):
    """Why an open task on a ready branch cannot start yet (1.165.0).

    `waits on T5` for open tasks it comes after, `held` for an open
    question or approval, else `can't start yet`.
    """
    deps = task.get("waits_on") or []
    if deps:
        return "waits on " + ", ".join(f"T{dep}" for dep in deps)
    if row and (row.get("held") or row.get("bucket") == "waiting"):
        return "held"
    return "can't start yet"


def _full_label(task):
    """`T#` plus the full task name, never cut with an ellipsis (1.173.0)."""
    return task.get("run_label") or task_label(task["id"], task.get("full") or task.get("short"))


def report_by_branch(built, rows, slug=None):
    """Group ready and held tasks by the build-map row.

    The branch is the row `build()` writes, which is the name `--recommend`
    prints. Branches are ordered by wave, then map order. Tasks inside a
    branch stay in map order. A task is `T#` plus its short name.
    """
    by_num = {}
    for branch in built.get("branches") or []:
        for task in branch["tasks"]:
            by_num[task["id"]] = (branch, task)

    rows_by_num = {}
    for row in rows or []:
        num = _task_num(row.get("task"))
        if num is not None:
            rows_by_num.setdefault(num, row)
    ready = []
    held = []
    for row in rows or []:
        num = _task_num(row.get("task"))
        if num is None or num not in by_num:
            continue
        if row.get("bucket") == "ready":
            ready.append((num, row))
        elif row.get("bucket") == "waiting" or row.get("held"):
            held.append((num, row))

    def gather(pairs):
        buckets = {}
        for num, row in pairs:
            branch, task = by_num[num]
            buckets.setdefault(branch["name"], {"branch": branch, "items": []})
            buckets[branch["name"]]["items"].append((task, row))
        groups = []
        for branch in _branch_order(built.get("branches") or []):
            group = buckets.get(branch["name"])
            if not group:
                continue
            group["items"].sort(key=lambda pair: pair[0]["id"])
            groups.append(group)
        return groups

    ready_groups = gather(ready)
    held_groups = gather(held)
    ready_lines = []
    for group in ready_groups:
        labels = "; ".join(_full_label(task) for task, _row in group["items"])
        ready_lines.append(f"- `{group['branch']['name']}` ({_where(group['branch'])}): {labels}")
    held_lines = []
    for group in held_groups:
        # One task per line under its branch heading (1.164.0).
        rows = [f"- `{group['branch']['name']}` ({_where(group['branch'])}):"]
        for task, row in group["items"]:
            label = _full_label(task)
            phrase = re.sub(r"([.!?])[.;]+", r"\1", held_phrase(row))
            rows.append(f"  - {label} — {phrase}")
        held_lines.append("\n".join(rows))
    next_lines = []
    run_lines = []
    ready_branches = []
    for group in ready_groups:
        labels = [
            task.get("run_label") or task.get("label") or task_label(task["id"], task.get("full") or task.get("short"))
            for task, _row in group["items"]
        ]
        # Walk order (1.165.0): the first listed task is the one the walk
        # runs first. A task that cannot start says why on its line.
        open_tasks = sorted(
            (task for task in group["branch"].get("tasks") or [] if not task.get("done")),
            key=lambda task: (task.get("walk", 10**6), task["id"]),
        )
        ready_ids = {task["id"] for task, _row in group["items"]}
        open_labels = [
            task.get("run_label") or task.get("label") or task_label(task["id"], task.get("full") or task.get("short"))
            for task in open_tasks
        ]
        waits = {f"T{task['id']}": wait_reason(task, rows_by_num.get(task["id"])) for task in open_tasks if task["id"] not in ready_ids}
        firsts = [task for task in open_tasks if task["id"] in ready_ids]
        if firsts:
            first = firsts[0]
            labels = [first.get("run_label") or first.get("label") or task_label(first["id"], first.get("full") or first.get("short"))]
        entries = run_entries(labels, group["branch"]["name"], slug=slug, open_labels=open_labels, about=group["branch"].get("about"), waits=waits)
        # next_lines carry the same entries as run_lines (1.155.0).
        for index, entry in enumerate(entries):
            if index == 0:
                next_lines.append(entry + "\n/crav1-build-tasks builds one task without the walk.")
            else:
                next_lines.append(entry)
        run_lines.extend(entries)
        ready_branches.append({
            "branch": group["branch"]["name"],
            "about": group["branch"].get("about") or "",
            "tasks": [
                {"id": f"T{task['id']}", "title": task.get("full") or task.get("short") or ""}
                for task in (firsts or [task for task, _row in group["items"]])
            ],
            "open_tasks": [
                {"id": f"T{task['id']}", "title": task.get("full") or task.get("short") or "", "waits": waits.get(f"T{task['id']}") or ""}
                for task in open_tasks
            ],
        })
    parts = []
    if ready_lines:
        parts.append("Ready now")
        parts.extend(ready_lines)
    if held_lines:
        parts.append("Held")
        parts.extend(held_lines)
    return {
        "ready_lines": ready_lines,
        "held_lines": held_lines,
        "next_lines": next_lines,
        "run_lines": run_lines,
        "ready_branches": ready_branches,
        "loop_lines": list(built.get("loop_lines") or []),
        "line": "\n".join(parts) if parts else None,
    }


def _question_line(questions, names=None):
    if not questions:
        return "none"
    parts = []
    for question in questions:
        short = clean_prose(_first_sentence(question["text"]), names) or "open question"
        who = question.get("who") or ""
        if who.strip().lower() in NO_WHO:
            who = NOBODY_SHORT
        if question.get("mark") == "inferred":
            parts.append(f"{short} — {who} (inferred from the text)")
        elif question.get("mark") == "whole":
            parts.append(f"{short} — {who} (holds the whole slice)")
        else:
            parts.append(f"{short} — {who}")
    return "; ".join(parts)


def _waits_items(branch, by_name):
    """The branches this one waits for, in task order (1.185.0: one per sub-bullet)."""
    ordered = sorted(branch["waits"], key=lambda name: (by_name[name]["tasks"][0]["id"], name))
    parts = list(ordered)
    if branch["unknown"]:
        parts.append(UNKNOWN_DEP)
    return parts


def _waits_line(branch, by_name):
    parts = _waits_items(branch, by_name)
    return "; ".join(parts) if parts else "none"


def _list_bullet(label, items, empty="none"):
    """`- Label:` with one nested sub-bullet per item, or one line when empty (1.185.0)."""
    if not items:
        return [f"- {label}: {empty}"]
    return [f"- {label}:"] + [f"  - {item}" for item in items]


def merge_deadlock(tasks, built, pr):
    """`blocked, merge deadlock: T8 waits on T43, which ticks only when PR 73 merges` or None (1.180.0)."""
    if not pr or not built:
        return None
    for task in tasks or ():
        if task.get("done") or task["id"] in built:
            continue
        for dep in task.get("deps") or ():
            if dep in built:
                return "blocked, " + task_state.deadlock_text(f"T{task['id']}", f"T{dep}", pr).rstrip(".").replace("Merge", "merge", 1)
    return None


def _ready_now(branch):
    if branch.get("deadlock"):
        return branch["deadlock"]
    if branch.get("loop"):
        return "blocked, in a loop"
    if branch["status"] == "held":
        if branch.get("held_text"):
            return branch["held_text"]
        return "held, waits on " + "; ".join(branch.get("held_on") or [])
    return branch["status"]


def parallel_phrase(members):
    """How many branches in a wave can start now, and how many tasks are done.

    Always `N branch(es), M can start now`. Only a branch whose status is
    `ready` counts as able to start, the same rule as the ready check: a
    question hold, a hold that waits on one, a claimed branch, a branch
    that waits in order, a blocked branch, and a branch whose tasks are
    all done are not a start. When the wave has done tasks, the heading
    adds `, K done`.
    """
    count = len(members)
    start = sum(1 for branch in members if branch["status"] == "ready")
    done_tasks = sum(1 for branch in members for task in branch["tasks"] if task.get("done"))
    noun = "branch" if count == 1 else "branches"
    text = f"{count} {noun}, {start} can start now"
    if done_tasks:
        text += f", {done_tasks} done"
    return text


def overlap_lines(members):
    """Pairs in one wave that share a requirement or a path. A note only."""
    ordered = sorted(members, key=lambda branch: (branch["tasks"][0]["id"], branch["name"]))
    lines = []
    for index, left in enumerate(ordered):
        for right in ordered[index + 1:]:
            shared = sorted(set(left.get("areas") or ()) & set(right.get("areas") or ()))
            if not shared:
                continue
            requirements = [token for kind, token in shared if kind == "requirement"]
            paths = [token for kind, token in shared if kind == "path"]
            bits = []
            if requirements:
                bits.append("both cover " + " and ".join(requirements))
            if paths:
                bits.append("both name " + " and ".join(f"`{path}`" for path in paths))
            lines.append(f"Overlap: {left['name']} and {right['name']} " + "; ".join(bits) + ".")
    return lines


def _render(slug, grouping, branches, by_name, risks, has_plan, risk_blocks, names=None, loop_lines=None):
    # 1.183.0: no page line above the diagram; open-map and export-map
    # still work and are listed in the skill's choice words.
    lines = ["# Build map", "", grouping, ""]
    for line in loop_lines or []:
        lines.append(line)
        lines.append("")
    diagram = _mermaid(branches, by_name)
    lines.extend(["```mermaid", diagram, "```", ""])
    if branches:
        lines.append("An arrow means the later branch waits for the earlier one.")
        lines.append("")
    else:
        lines.append("Nothing left to build.")
        lines.append("")
    if not has_plan:
        lines.append("Held: no plan.md.")
        lines.append("")
    elif risk_blocks:
        texts = []
        for risk in risks:
            if not risk["blocks_slice"]:
                continue
            short = clean_prose(risk["text"], names)
            if short and short not in texts:
                texts.append(short)
        detail = "; ".join(texts) if texts else "do not implement until resolved"
        lines.append(f"Held: a plan risk blocks the whole slice ({detail}).")
        lines.append("")
    waves = {}
    blocked = []
    for branch in branches:
        if branch["section"] == "blocked":
            blocked.append(branch)
        else:
            waves.setdefault(branch["wave"], []).append(branch)
    for number in sorted(waves):
        members = sorted(waves[number], key=lambda item: item["tasks"][0]["id"])
        block = [f"## Wave {number}: {parallel_phrase(members)}", ""]
        for note in overlap_lines(members):
            block.append(note)
            block.append("")
        for branch in members:
            block.extend(_branch_block(branch, by_name, names))
        tasks = [task for branch in members for task in branch["tasks"]]
        if tasks and all(task.get("done") for task in tasks):
            count = len(tasks)
            noun = "task" if count == 1 else "tasks"
            lines.append("<details>")
            lines.append(f"<summary>Wave {number} done ({count} {noun})</summary>")
            lines.append("")
            lines.extend(block)
            lines.append("</details>")
            lines.append("")
        else:
            lines.extend(block)
    if blocked:
        lines.append("## Blocked")
        lines.append("")
        for branch in sorted(blocked, key=lambda item: item["tasks"][0]["id"]):
            lines.extend(_branch_block(branch, by_name, names))
    text = "\n".join(lines).rstrip() + "\n"
    return text


def waits_label(branch):
    """`Waited for` on a branch whose every task is done, else `Waits for` (1.162.0)."""
    tasks = branch.get("tasks") or []
    if tasks and all(task.get("done") for task in tasks):
        return "Waited for"
    return "Waits for"


def _branch_block(branch, by_name, names=None):
    # 1.185.0: list bullets nest one item per sub-bullet instead of joining
    # with "; ", and Delivers is gone: Tasks (with task ids) is the one list.
    lines = [f"### {branch['name']}", ""]
    lines += _list_bullet("Tasks", list(branch.get("task_names") or []), empty="work")
    lines += _list_bullet(waits_label(branch), _waits_items(branch, by_name))
    lines += [
        f"- Question: {_question_line(branch['questions'], names)}",
        f"- Ready now: {_ready_now(branch)}",
    ]
    if branch.get("note"):
        lines.append(f"- {branch['note']}")
    lines.append("")
    return lines


def _mermaid_label(name):
    return name.replace('"', "'").replace("[", "(").replace("]", ")")


# Build-map colours (1.178.0). Each box takes its worst task's state: red
# (truly blocked: a loop, a failed check, a reopened step, no plan), then
# amber (waits on a pull request or a question), then blue (ready or not
# started, the default), then green (every task done). The edge out of a
# box shows that box's state: solid green, dashed amber, thick red, plain
# blue. Fills are dark and text, borders and edges are bright, so the map
# reads on a dark background and stays readable on a light one.
MAP_STATES = ("blocked", "waiting", "todo", "done")
MAP_CLASSES = {
    "done": "fill:#14532d,stroke:#4ade80,stroke-width:2px,color:#f0fdf4",
    "waiting": "fill:#78350f,stroke:#fbbf24,stroke-width:2px,color:#fffbeb",
    "blocked": "fill:#7f1d1d,stroke:#f87171,stroke-width:3px,color:#fef2f2",
    "todo": "fill:#1e3a8a,stroke:#60a5fa,stroke-width:2px,color:#eff6ff",
}
MAP_EDGE_COLOURS = {"done": "#4ade80", "waiting": "#fbbf24", "blocked": "#f87171", "todo": "#60a5fa"}
MAP_EDGE_ARROWS = {"done": "-->", "waiting": "-.->", "blocked": "==>", "todo": "-->"}
MAP_EDGE_WIDTH = {"done": "2px", "waiting": "2px", "blocked": "4px", "todo": "2px"}
MAP_LEGEND = (
    ("done", "Done"),
    ("waiting", "Waits on a PR or question"),
    ("blocked", "Blocked"),
    ("todo", "Ready or not started"),
)
MAP_GROUP_STYLE = "fill:transparent,stroke:#94a3b8,stroke-width:1px,color:#cbd5e1"


def map_state(branch):
    """One of done, waiting, blocked, todo: the box colour (1.178.0).

    Blocked only for a truly blocked branch: in a loop, the Blocked section,
    or a walk whose last result failed or was reopened. Waiting for a
    question hold, a branch built and waiting for its pull request, or a
    hold on another branch that waits. Done when every task is done. Else
    todo (ready, waits in order, in progress).
    """
    # 1.180.0: the colour is task_state.box_state, from each task's state.
    return task_state.box_state(branch)


def _mermaid(branches, by_name):
    if not branches:
        return "flowchart LR\n  none[\"Nothing left to build\"]"
    waves = {}
    blocked = []
    for branch in branches:
        if branch["section"] == "blocked":
            blocked.append(branch)
        else:
            waves.setdefault(branch["wave"], []).append(branch)
    lines = ["flowchart LR"]
    ids = {}
    states = {}
    number = 1

    def add_group(group_id, title, members):
        nonlocal number
        lines.append(f'  subgraph {group_id}["{_mermaid_label(title)}"]')
        lines.append("    direction TB")
        for branch in sorted(members, key=lambda item: item["tasks"][0]["id"]):
            node = f"b{number}"
            number += 1
            ids[branch["name"]] = node
            states[node] = map_state(branch)
            lines.append(f'    {node}["{_mermaid_label(branch["name"])}"]')
        lines.append("  end")
        groups.append(group_id)

    groups = []

    for wave_number in sorted(waves):
        add_group(f"w{wave_number}", f"Wave {wave_number}", waves[wave_number])
    looped = [branch for branch in blocked if branch.get("loop")]
    others = [branch for branch in blocked if not branch.get("loop")]
    if looped:
        add_group("inloop", "In a loop", looped)
    if others:
        add_group("blocked", "Blocked", others)
    lines.append('  subgraph legend["Legend"]')
    lines.append("    direction TB")
    for index, (state, label) in enumerate(MAP_LEGEND, 1):
        lines.append(f'    key{index}["{label}"]')
    lines.append("  end")
    groups.append("legend")
    seen = set()
    edges = []
    for branch in branches:
        for dep in branch["waits"]:
            edge = (ids.get(dep), ids.get(branch["name"]))
            if edge in seen or None in edge:
                continue
            seen.add(edge)
            state = states.get(edge[0], "todo")
            edges.append(state)
            lines.append(f"  {edge[0]} {MAP_EDGE_ARROWS[state]} {edge[1]}")
    for state in MAP_STATES:
        lines.append(f"  classDef {state} {MAP_CLASSES[state]}")
    for index, (state, _label) in enumerate(MAP_LEGEND, 1):
        states[f"key{index}"] = state
    for state in MAP_STATES:
        nodes = [node for node, value in states.items() if value == state]
        if nodes:
            lines.append(f"  class {','.join(nodes)} {state}")
    for group in groups:
        lines.append(f"  style {group} {MAP_GROUP_STYLE}")
    lines.append("  linkStyle default stroke:#60a5fa,stroke-width:2px")
    for index, state in enumerate(edges):
        lines.append(f"  linkStyle {index} stroke:{MAP_EDGE_COLOURS[state]},stroke-width:{MAP_EDGE_WIDTH[state]}")
    return "\n".join(lines)


def _short_list(items, limit=6):
    if len(items) <= limit:
        return ", ".join(items)
    extra = len(items) - limit
    return ", ".join(items[:limit]) + f", and {extra} more"


def _summary(slug, pointer, branches, loop_lines=None):
    lines = [f"Build map — {slug}", pointer]
    lines.extend(loop_lines or [])
    if not branches:
        lines.append("Nothing left to build.")
        return "\n".join(lines)
    waves = {}
    blocked = []
    for branch in branches:
        label = f"{branch['name']} ({_ready_now(branch)})"
        if branch["section"] == "blocked":
            blocked.append((branch["tasks"][0]["id"], label))
        else:
            waves.setdefault(branch["wave"], []).append((branch["tasks"][0]["id"], branch, label))
    numbers = sorted(waves)
    if blocked and 1 not in waves:
        lines.append("Wave 1: none")
    for number in numbers:
        ordered = sorted(waves[number], key=lambda item: item[0])
        members = [branch for _, branch, _ in ordered]
        labels = [label for _, _, label in ordered]
        lines.append(f"Wave {number}: {parallel_phrase(members)} — {_short_list(labels)}")
        lines.extend(overlap_lines(members))
    if blocked:
        labels = [label for _, label in sorted(blocked)]
        lines.append("Blocked: " + _short_list(labels))
    return "\n".join(lines)


def _read(path):
    file = pathlib.Path(path)
    if not file.is_file():
        return None
    return file.read_text(encoding="utf-8")


def slice_dirs(root, scope=""):
    root = pathlib.Path(root)
    if scope:
        scope_path = pathlib.Path(scope)
        if scope_path.is_dir():
            return [scope_path]
        if not scope_path.is_absolute():
            candidate = root / scope
            if candidate.is_dir():
                return [candidate]
            docs = pathlib.Path("docs/specs") / scope
            if docs.is_dir():
                return [docs]
        names = set(scope_folder_names(scope))
        found = []
        if root.is_dir():
            for child in sorted(root.iterdir()):
                if child.is_dir() and child.name in names:
                    found.append(child)
        return found
    if not root.is_dir():
        return []
    out = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name in ("_template", "retired"):
            continue
        out.append(child)
    return out


def run_dir(directory, chat=False, stdout=False, recommend=None, code_repo=None):
    directory = pathlib.Path(directory)
    slug = directory.name
    tasks = _read(directory / "tasks.md")
    if tasks is None:
        return f"no tasks yet (run /crav1-plan-from-spec): {slug}", 0
    spec = _read(directory / "spec.md") or ""
    plan = _read(directory / "plan.md")
    work = _read(directory / "work-item.md") or ""
    verify = _read(directory / "verify.md") or ""
    claims = _read(directory / "claims.md") or ""
    progress = directory / "walk-progress.md"
    resolve_recorded = False
    if progress.is_file():
        resolve_recorded = "- Step: resolve-open-questions" in progress.read_text(encoding="utf-8")
    repo = find_repo(directory)
    if recommend:
        offer = recommendation(slug, spec, plan, tasks, recommend, work, repo=repo, claims_text=claims, code_repo=code_repo)
        if not offer:
            return f"No open task {recommend}.", 2
        return format_offer(offer), 0
    progress_hashes = progress_shas(directory)
    existing = map_marks(_read(directory / "build-map.md") or "")
    result = build(slug, spec, plan, tasks, work, verify, resolve_recorded=resolve_recorded, repo=repo, claims_text=claims, code_repo=code_repo, progress=progress_hashes, existing=existing, walks=progress_state(directory))
    if not stdout:
        (directory / "build-map.md").write_text(result["markdown"], encoding="utf-8")
    if stdout and not chat:
        return result["markdown"], 0
    if chat:
        return result["summary"], 0
    return result["pointer"], 0


AFTER_MARK = re.compile(r"\(after:\s*([^)]*)\)", re.I)


def _line_with_map(line, target):
    """Write or replace the (map: ...) mark. A repo word before the old branch is kept."""
    found = MAP_MARK.search(line)
    if found:
        words = found.group(1).split()
        prefix = " ".join(words[:-1])
        mark = f"(map: {prefix + ' ' if prefix else ''}{target})"
        return line[: found.start()] + mark + line[found.end():]
    return line.rstrip() + f" (map: {target})"


def _line_without_wait(line, dep):
    found = AFTER_MARK.search(line)
    if not found:
        return line.rstrip() + " (after: )"
    kept = [token for token in re.findall(r"T\d+", found.group(1)) if token != f"T{dep}"]
    return line[: found.start()] + f"(after: {', '.join(kept)})" + line[found.end():]


def apply_fix_text(tasks_text, fix):
    """tasks.md with one fix written: (map:) marks for a move, one wait removed for a drop."""
    targets = set(fix["tasks"])
    out = []
    for line in (tasks_text or "").splitlines(keepends=True):
        match = task_order.TASK.match(line.rstrip("\r\n"))
        if match and int(match.group(2)) in targets:
            ending = line[len(line.rstrip("\r\n")):]
            body = line.rstrip("\r\n")
            if fix["kind"] == "move":
                body = _line_with_map(body, fix["target"])
            else:
                body = _line_without_wait(body, fix["dep"])
            line = body + ending
        out.append(line)
    return "".join(out)


def fix_loop(directory, pick=1, yes=False, code_repo=None):
    """Offer or apply one loop fix (1.161.0). Returns (dict, exit code).

    Without yes it writes nothing, returns the change it would make, and
    exits 0. A nonzero exit is only for a real error (no tasks.md, no such
    fix). With yes it writes tasks.md, rebuilds build-map.md, and reports
    what is left: no loop, or the next loop with its own fixes. It never
    touches spec.md and commits nothing.
    """
    directory = pathlib.Path(directory)
    slug = directory.name
    tasks_path = directory / "tasks.md"
    tasks = _read(tasks_path)
    if tasks is None:
        return {"ok": False, "code": "tasks", "message": f"no tasks.md in {directory}"}, 2
    spec = _read(directory / "spec.md") or ""
    plan = _read(directory / "plan.md")
    work = _read(directory / "work-item.md") or ""
    verify = _read(directory / "verify.md") or ""
    claims = _read(directory / "claims.md") or ""
    repo = find_repo(directory)
    built = build(slug, spec, plan, tasks, work, verify, repo=repo, claims_text=claims, code_repo=code_repo)
    fixes = [fix for row in built["loops"] for fix in row["fixes"]]
    if not built["loops"]:
        return {"ok": True, "wrote": None, "loops": [], "line": "No loop to fix. The branches do not wait for each other."}, 0
    chosen = next((fix for fix in fixes if fix["number"] == pick), None)
    if chosen is None:
        words = ", ".join(f"`{fix['word']}`" for fix in fixes) or "none"
        return {"ok": False, "code": "pick", "message": f"No fix {pick}. The fixes are {words}."}, 2
    if chosen["kind"] == "move":
        change = f"tasks.md: {_ids_text(chosen['tasks'])} now carry (map: {chosen['target']}), so they are built on {chosen['target']}."
    else:
        change = f"tasks.md: T{chosen['task']} no longer waits for T{chosen['dep']} in its (after:) mark."
    if not yes:
        row = next((row for row in built["loops"] if chosen in row["fixes"]), built["loops"][0])
        card = dict(row.get("card") or {})
        options = list(card.get("options") or [])
        mine = [option for option in options if option.get("word") == chosen["word"]]
        rest = [option for option in options if option.get("word") != chosen["word"]]
        for option in rest:
            option["label"] = option["label"].replace(" (Recommended)", "")
        if mine and "(Recommended)" not in mine[0]["label"]:
            mine[0]["label"] += " (Recommended)"
        card["options"] = mine + rest
        lines = [f"Change: {change}", f"Card: {card.get('question', '')}"]
        for index, option in enumerate(card["options"], start=1):
            lines.append(f"{index}. {option['label']} (`{option['word']}`): {option['text']}")
        return {
            "ok": True,
            "code": "needs-yes",
            "fix": chosen,
            "change": change,
            "card": card,
            "line": "\n".join(lines),
            "message": "fix-loop writes tasks.md only with --yes, after the fix was shown and confirmed.",
        }, 0
    new_text = apply_fix_text(tasks, chosen)
    with open(tasks_path, "w", encoding="utf-8", newline="") as handle:
        handle.write(new_text)
    after = build(slug, spec, plan, new_text, work, verify, repo=repo, claims_text=claims, code_repo=code_repo, progress=progress_shas(directory), existing=map_marks(_read(directory / "build-map.md") or ""), walks=progress_state(directory))
    (directory / "build-map.md").write_text(after["markdown"], encoding="utf-8")
    lines = [f"Wrote {change}", "Rebuilt build-map.md."]
    if after["loops"]:
        lines.append("Another loop is left:")
        lines.extend(after["loop_lines"])
    else:
        lines.append("No loop left. The branches no longer wait for each other.")
    lines.append(f"Uncommitted: docs/specs/{slug}/tasks.md, docs/specs/{slug}/build-map.md")
    return {
        "ok": True,
        "wrote": ["tasks.md", "build-map.md"],
        "fix": chosen,
        "change": change,
        "loops": after["loops"],
        "lines": lines,
        "line": "\n".join(lines),
    }, 0


def main(argv):
    _utf8_stdout()
    if not argv or argv[0] in ("-h", "--help"):
        sys.stdout.write(__doc__ or "")
        if not (__doc__ or "").endswith("\n"):
            sys.stdout.write("\n")
        return 0
    if "--fix-loop" in argv:
        rest = [arg for arg in argv if arg not in ("--fix-loop", "--yes", "--json")]
        pick = 1
        if "--pick" in rest:
            at = rest.index("--pick")
            try:
                pick = int(rest[at + 1])
            except (IndexError, ValueError):
                sys.stdout.write("--pick takes a fix number.\n")
                return 2
            del rest[at:at + 2]
        if len(rest) != 1:
            sys.stdout.write("Name one spec folder with --fix-loop.\n")
            return 2
        out, code = fix_loop(rest[0], pick=pick, yes="--yes" in argv)
        if "--json" in argv:
            sys.stdout.write(json.dumps(out, indent=2) + "\n")
        else:
            sys.stdout.write((out.get("line") or out.get("change") or out.get("message") or "") + "\n")
        return code
    chat = "--chat" in argv
    stdout = "--stdout" in argv
    args = [arg for arg in argv if arg not in ("--chat", "--stdout")]
    scope = ""
    root = None
    recommend = None
    code_repo = None
    positional = []
    i = 0
    while i < len(args):
        if args[i] == "--scope" and i + 1 < len(args):
            scope = args[i + 1]
            i += 2
            continue
        if args[i] == "--root" and i + 1 < len(args):
            root = args[i + 1]
            i += 2
            continue
        if args[i] == "--code-repo" and i + 1 < len(args):
            code_repo = args[i + 1]
            i += 2
            continue
        if args[i] == "--recommend" and i + 1 < len(args):
            recommend = args[i + 1]
            i += 2
            continue
        positional.append(args[i])
        i += 1
    if recommend is not None:
        if len(positional) != 1:
            sys.stdout.write("Name one spec folder with --recommend.\n")
            return 2
        given = pathlib.Path(positional[0])
        if given.is_file() and given.name in ("tasks.md", "spec.md"):
            sys.stdout.write(
                "A spec folder is required. Pass the parent folder: "
                + str(given.parent)
                + "\n"
            )
            return 2
        text, code = run_dir(positional[0], recommend=recommend, code_repo=code_repo)
        sys.stdout.write(text + ("\n" if text and not text.endswith("\n") else ""))
        return code
    if root is not None:
        dirs = slice_dirs(root, scope)
        if scope and not dirs:
            sys.stdout.write(f"No slice named {scope}.\n")
            return 0
    elif len(positional) == 1:
        dirs = [pathlib.Path(positional[0])]
    else:
        sys.stdout.write(__doc__ or "")
        return 2
    pieces = []
    for directory in dirs:
        text, code = run_dir(directory, chat=chat, stdout=stdout, code_repo=code_repo)
        if code:
            return code
        pieces.append(text.rstrip("\n"))
    sys.stdout.write("\n".join(pieces) + ("\n" if pieces else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
