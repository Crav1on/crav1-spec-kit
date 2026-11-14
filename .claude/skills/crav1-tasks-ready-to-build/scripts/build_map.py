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
on the remote is not offered. A name that does not exist yet is offered
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
  build_map.py <spec-dir> --recommend T1
  build_map.py --root <docs/specs> [--scope <words>] [--chat] [--stdout]

On Windows the interpreter is python. Elsewhere it is python3. Then py -3.
Set PYTHONUTF8=1 and pass -X utf8. The Store alias message
`Python was not found` means that command was not found.
Standard library only. Writes build-map.md in the spec folder unless --stdout.
With no flag, prints only the one-line path of that file.
"""
import importlib.util
import pathlib
import re
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
PIPELINE = re.compile(r"(?<![\w-])pipeline runs(?![\w-])")
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
    """The word build-map selects the map. The remaining words are the scope."""
    raw = (text or "").strip()
    raw = re.sub(r"^/crav1-tasks-ready-to-build\b", "", raw).strip()
    mode = "map" if WORD.search(raw) else "report"
    raw = WORD.sub(" ", raw)
    pipeline = bool(PIPELINE.search(raw))
    raw = PIPELINE.sub(" ", raw)
    scope = re.sub(r"\s+", " ", raw).strip()
    if scope.startswith("@"):
        scope = scope[1:].strip()
    return {"mode": mode, "scope": scope, "pipeline_runs": pipeline}


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
    text = re.sub(r"`+", " ", text)
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


def run_entries(labels, branch_name, slug=None, open_labels=None):
    """Run next entries for one ready branch (1.155.0); shared in walk_ending.py."""
    return _ending_mod().run_entries(labels, branch_name, slug=slug, open_labels=open_labels)


def short_name(rest, work_title=None, trim=True):
    """A task's short name: its work-item title, else the text up to the first cut.

    Cuts are ` (`, `, in `, and the end of the sentence, whichever comes first.
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
    text = MARKER.sub(" ", rest or "")
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


def branch_fate(name, spec_text, tasks_text, repo, stated):
    """`ok`, `absent`, `merged`, `deleted`, or `unchecked`.

    `absent` means the name is not on disk and was not checked out here, so
    it can be created. `merged` means git proves the tip is already in the
    base or the default branch. A recorded merge in the specs is not enough
    to skip the name when git is missing, offline, or shows the tip is not
    contained. `deleted` means the branch was checked out here and is now
    gone locally and on every remote. `unchecked` means git could not tell
    (no repo, or no tips and not a recorded deletion). No fetch.
    """
    if not name:
        return "absent"
    if repo is None:
        return "unchecked"
    tips = _branch_tips(repo, name)
    if tips and any(_strictly_contained(repo, tip, base) for tip in tips for base in _base_tips(repo, stated)):
        return "merged"
    if tips:
        return "ok"
    if _reflog_mentions(repo, name):
        return "deleted"
    if not tips:
        return "absent"
    return "ok"


def _why(name, fate):
    if fate == "merged":
        return f"{name} is already merged"
    if fate == "deleted":
        return f"{name} was deleted locally and on the remote"
    if fate == "unchecked":
        return f"could not check whether {name} is merged"
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
    wait, then says to fix one of those lines in tasks.md.
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
    return f"Loop: {head}: {body}. Fix one of these lines in tasks.md."


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


def verify_sha(text, task_id):
    """A commit sha on the verify row for this task, or None."""
    if not text:
        return None
    tid = f"T{task_id}"
    for line in text.splitlines():
        if not re.search(rf"\b{re.escape(tid)}\b", line):
            continue
        match = SHA.search(line)
        if match:
            return match.group(1)[:12]
    return None


def done_evidence(task, branch_name, prs, verify_text):
    """PR link, else the recorded branch, else a verify commit, else the row branch."""
    direct = task_pr(task.get("rest") or "")
    if direct:
        return direct
    recorded = task.get("map") or task.get("branch") or committed_later(task.get("rest") or "")
    for key in (recorded, branch_name):
        if key and key in prs:
            return prs[key]
    if recorded:
        return recorded
    sha = verify_sha(verify_text, task["id"])
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


def build(slug, spec_text, plan_text, tasks_text, work_item_text="", verify_text="", resolve_recorded=False, repo=None, claims_text=""):
    """Return markdown, a short chat summary, and the one-line pointer."""
    tasks = parse_tasks(tasks_text)
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
        task_order.apply_claim_holds(analysed, tasks, claims_text)
    rows = {row["id"]: row for row in analysed["rows"]}
    claimed_ids = {row["id"] for row in (analysed.get("waiting_in_progress") or [])}
    by_id = {task["id"]: task for task in tasks}
    step_by_n = {step["n"]: step for step in steps}
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
            fate = branch_fate(planned, spec_text, tasks_text, repo, base or line_base)
            if fate == "unchecked" and source == "task line" and planned in merged_branch_names(spec_text, tasks_text):
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
                    other_fate = branch_fate(name, spec_text, tasks_text, repo, other_base)
                    if other_fate not in ("merged", "deleted"):
                        picked_alt = name
                        break
                alt = step_name if source == "task line" and step_name and step_name != planned else None
                alt_fate = branch_fate(alt, spec_text, tasks_text, repo, None) if alt else None
                if picked_alt:
                    chosen, offer_source, offer_base = (
                        picked_alt,
                        "task line",
                        stated_base(task.get("rest") or "", picked_alt),
                    )
                elif alt and alt_fate not in ("merged", "deleted", "unchecked"):
                    chosen, offer_source, offer_base = alt, "build map", None
                elif source == "task line" and fate != "deleted" and repo is None:
                    # Offline: keep the task-line branch; do not invent a name.
                    chosen, offer_source, offer_base = planned, source, base
                    because = _why(planned, "unchecked")
                else:
                    chosen = _fresh_name(
                        slug,
                        task.get("rest") or task["title"],
                        used_names,
                        {planned, alt, picked_alt},
                        task_id=task["id"],
                    )
                    offer_source, offer_base = "new", line_base
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
            label = task_label(task["id"], plain)
            task["short"] = plain
            task["full"] = full
            task["label"] = label
            task["run_label"] = task_label(task["id"], full)
            if task["done"]:
                evidence = done_evidence(task, name, prs, verify_text)
                shorts.append(f"~~{plain}~~ ✓ done ({evidence})")
                shown.append(f"~~{label}~~ ✓ done ({evidence})")
            else:
                shorts.append(plain)
                shown.append(label)
        owners = {task.get("owner") for task in members}
        owner = next(iter(owners)) if len(owners) == 1 else None
        if (
            mode == "steps"
            and owner in step_names
            and all(not task_line_choice(task)[0] for task in members)
            and all(resolved[task["id"]] == step_names.get(owner) for task in members)
        ):
            deliver = clean_prose(step_by_n[owner]["body"], name_of) or "; ".join(shorts)
        else:
            deliver = "; ".join(shorts)
        areas = set()
        for task in members:
            areas.update(task.get("areas") or ())
        branches.append({
            "key": name,
            "name": name,
            "deliver": deliver or "work",
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
    for group in loops:
        open_ids = [
            task["id"]
            for name in group
            for task in by_name[name]["tasks"]
            if not task["done"]
        ]
        loop_rows.append({
            "branches": list(group),
            "line": loop_line(group, wait_why, id_branch),
            "tasks": sorted(open_ids),
        })
    for row in loop_rows:
        for name in row["branches"]:
            by_name[name]["loop_line"] = row["line"]

    loop_lines = [row["line"] for row in loop_rows]
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


def recommendation(slug, spec_text, plan_text, tasks_text, task_id, work_item_text="", repo=None, claims_text=""):
    """The branch to offer for one open task, or None when that task is not open.

    `name` is the branch. `source` is `task line`, `build map`, or `new`.
    `base` is the `from` base on the task line, or None. `because` is one
    plain line when a merged or deleted branch was skipped, or when git
    could not check a task-line branch, or None.
    """
    task_id = _task_number(task_id)
    if task_id is None:
        return None
    result = build(slug, spec_text, plan_text, tasks_text, work_item_text, repo=repo, claims_text=claims_text)
    offer = (result.get("offers") or {}).get(task_id)
    return dict(offer) if offer else None


def format_offer(offer):
    """The lines `--recommend` prints. The first line is the branch name."""
    lines = [offer["name"], f"source: {offer['source']}"]
    if offer.get("base"):
        lines.append(f"from: {offer['base']}")
    if offer.get("because"):
        lines.append(f"because: {offer['because']}")
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


def held_phrase(row):
    """The held reason on a ready-check line.

    An open question names the question and who has it. A task that only
    waits on a held task says `held, waits on T#`. The recorded or inferred
    tag stays off this line.
    """
    reason = (row.get("reason") or "").strip()
    who = (row.get("who") or "").strip() or "not named yet"
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
        return f'approval "{what}" Waiting for {who}.'
    match = re.search(r'open question "([^"]*)"', reason)
    if match:
        question = re.split(r"(?<=[.!?])\s", match.group(1).strip(), maxsplit=1)[0]
        note = ""
        if "blocks the whole slice (recorded)" in reason.lower():
            note = " Holds the whole slice."
        elif "inferred from the text" in reason.lower():
            note = " Inferred from the text."
        return f'open question "{question}" Waiting for {who}.{note}'
    return core or "held"


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
        labels = "; ".join(task.get("label") or task_label(task["id"], task.get("short")) for task, _row in group["items"])
        ready_lines.append(f"- `{group['branch']['name']}` ({_where(group['branch'])}): {labels}")
    held_lines = []
    for group in held_groups:
        bits = []
        for task, row in group["items"]:
            label = task.get("label") or task_label(task["id"], task.get("short"))
            bits.append(f"{label} — {held_phrase(row)}")
        held_lines.append(f"- `{group['branch']['name']}` ({_where(group['branch'])}): " + "; ".join(bits))
    next_lines = []
    run_lines = []
    ready_branches = []
    for group in ready_groups:
        labels = [
            task.get("run_label") or task.get("label") or task_label(task["id"], task.get("full") or task.get("short"))
            for task, _row in group["items"]
        ]
        open_tasks = [task for task in group["branch"].get("tasks") or [] if not task.get("done")]
        open_labels = [
            task.get("run_label") or task.get("label") or task_label(task["id"], task.get("full") or task.get("short"))
            for task in open_tasks
        ]
        entries = run_entries(labels, group["branch"]["name"], slug=slug, open_labels=open_labels)
        # next_lines carry the same entries as run_lines (1.155.0).
        for index, entry in enumerate(entries):
            if index == 0:
                next_lines.append(entry + "\n/crav1-build-tasks builds one task without the walk.")
            else:
                next_lines.append(entry)
        run_lines.extend(entries)
        ready_branches.append({
            "branch": group["branch"]["name"],
            "tasks": [
                {"id": f"T{task['id']}", "title": task.get("short") or ""}
                for task, _row in group["items"]
            ],
            "open_tasks": [
                {"id": f"T{task['id']}", "title": task.get("short") or ""}
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
        who = question.get("who") or "not named yet"
        if question.get("mark") == "inferred":
            parts.append(f"{short} — {who} (inferred from the text)")
        elif question.get("mark") == "whole":
            parts.append(f"{short} — {who} (holds the whole slice)")
        else:
            parts.append(f"{short} — {who}")
    return "; ".join(parts)


def _waits_line(branch, by_name):
    ordered = sorted(branch["waits"], key=lambda name: (by_name[name]["tasks"][0]["id"], name))
    parts = list(ordered)
    if branch["unknown"]:
        parts.append(UNKNOWN_DEP)
    return "; ".join(parts) if parts else "none"


def _ready_now(branch):
    if branch.get("loop"):
        return "blocked, in a loop"
    if branch["status"] == "held":
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


def _branch_block(branch, by_name, names=None):
    titles = "; ".join(branch.get("task_names") or []) or "work"
    lines = [
        f"### {branch['name']}",
        "",
        f"- Delivers: {branch['deliver']}",
        f"- Tasks: {titles}",
        f"- Waits for: {_waits_line(branch, by_name)}",
        f"- Question: {_question_line(branch['questions'], names)}",
        f"- Ready now: {_ready_now(branch)}",
    ]
    if branch.get("note"):
        lines.append(f"- {branch['note']}")
    lines.append("")
    return lines


def _mermaid_label(name):
    return name.replace('"', "'").replace("[", "(").replace("]", ")")


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
    number = 1

    def add_group(group_id, title, members):
        nonlocal number
        lines.append(f'  subgraph {group_id}["{_mermaid_label(title)}"]')
        lines.append("    direction TB")
        for branch in sorted(members, key=lambda item: item["tasks"][0]["id"]):
            node = f"b{number}"
            number += 1
            ids[branch["name"]] = node
            lines.append(f'    {node}["{_mermaid_label(branch["name"])}"]')
        lines.append("  end")

    for wave_number in sorted(waves):
        add_group(f"w{wave_number}", f"Wave {wave_number}", waves[wave_number])
    looped = [branch for branch in blocked if branch.get("loop")]
    others = [branch for branch in blocked if not branch.get("loop")]
    if looped:
        add_group("inloop", "In a loop", looped)
    if others:
        add_group("blocked", "Blocked", others)
    seen = set()
    for branch in branches:
        for dep in branch["waits"]:
            edge = (ids.get(dep), ids.get(branch["name"]))
            if edge in seen or None in edge:
                continue
            seen.add(edge)
            lines.append(f"  {edge[0]} --> {edge[1]}")
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


def run_dir(directory, chat=False, stdout=False, recommend=None):
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
        offer = recommendation(slug, spec, plan, tasks, recommend, work, repo=repo, claims_text=claims)
        if not offer:
            return f"No open task {recommend}.", 2
        return format_offer(offer), 0
    result = build(slug, spec, plan, tasks, work, verify, resolve_recorded=resolve_recorded, repo=repo, claims_text=claims)
    if not stdout:
        (directory / "build-map.md").write_text(result["markdown"], encoding="utf-8")
    if stdout and not chat:
        return result["markdown"], 0
    if chat:
        return result["summary"], 0
    return result["pointer"], 0


def main(argv):
    _utf8_stdout()
    if not argv or argv[0] in ("-h", "--help"):
        sys.stdout.write(__doc__ or "")
        if not (__doc__ or "").endswith("\n"):
            sys.stdout.write("\n")
        return 0
    chat = "--chat" in argv
    stdout = "--stdout" in argv
    args = [arg for arg in argv if arg not in ("--chat", "--stdout")]
    scope = ""
    root = None
    recommend = None
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
        text, code = run_dir(positional[0], recommend=recommend)
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
        text, code = run_dir(directory, chat=chat, stdout=stdout)
        if code:
            return code
        pieces.append(text.rstrip("\n"))
    sys.stdout.write("\n".join(pieces) + ("\n" if pieces else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
