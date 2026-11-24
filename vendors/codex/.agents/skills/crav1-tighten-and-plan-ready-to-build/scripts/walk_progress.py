#!/usr/bin/env python3
"""Progress file for /crav1-tighten-and-plan-ready-to-build (kit 1.146.0).

The spec, plan, and tasks stay the source of truth. This script only tracks
where the guided walk is, which version of each file a step covered, and which
ready-check rows belong to which step. It does not edit those files, does not
apply a playbook, and does not start a build. It never writes verify.md.
readiness --write-map writes build-map.md in the same format as
/crav1-tasks-ready-to-build. Without that flag it writes nothing.

A later step inside the walk leaves earlier steps done. An optional extra
the walk itself runs is recorded with `- Extra:` when it finishes, and that
record does the same. `cover` is optional: it counts a write made outside
this walk as part of the walk, and does not name an extra. A change that
nobody recorded or covered reopens only the steps that change affects.

Usage (JSON on stdout):
  walk_progress.py version --root <spec-folder>
  walk_progress.py record --root <spec-folder> --slice docs/specs/<slug> --step <id>
      --result <result> --yes [--when <full timestamp>] [--playbook <file>]
  walk_progress.py cover --root <spec-folder> --yes
  walk_progress.py clear --root <spec-folder> --step <id> --yes
  walk_progress.py start --root <spec-folder-or-slug> [--playbook <file>]
  walk_progress.py resume --root <spec-folder>
  walk_progress.py playbook-status --root <spec-folder> --playbook <file>
  walk_progress.py readiness --root <spec-folder> [--write-map] [--full|--text]
  walk_progress.py readiness --json <file> [--root <spec-folder>]
  walk_progress.py unlinked --root <spec-folder>
  walk_progress.py ack-stamps --root <spec-folder> --yes
  walk_progress.py spec-finding --root <spec-folder> --id P2 --text "<finding>"
      [--tag spec|plan] [--choice tighten-spec|add-to-spec|open-point|already-done] [--yes]
      [--kind code-drift|spec-text] [--pr N] [--branch B] [--expect "<words>"] [--code-repo <path>]
  walk_progress.py code-drift --root <spec-folder> --code-repo <path> [--branch B] [--pr N --merged <sha>]
  walk_progress.py resolve-stamps --root <spec-folder> --yes
      [--settle-stamps] [--ours-root <folder> --theirs-root <folder>]
  walk_progress.py restamp-covered --root <spec-folder> --yes

readiness --root builds the rows from task_order.py and question_blocks.py
and adds the Reviewed warnings. It also compares tasks.md with verify.md.
Brief is the default (1.156.0): result, a counts row, the ending, the
finished reply, and claim warnings. --brief is accepted and changes nothing.
--full prints the complete JSON, only on an explicit ask. --text prints
only the reply, to show as-is. --write-map writes
build-map.md through build_map.py and does not write verify.md. Do not
hand-build that JSON. start resolves a folder or a slug
the way resolve_spec.py does and returns resume and playbook-status together.
spec-finding offers one jump back for a spec finding, or records an open
point when that finding already jumped. A close reword of a recorded finding
is offered as that finding, and --new keeps it separate. The first-seen Key
stays. Later wordings are Alias. A plan tag writes nothing.
Since 1.194.0 a code finding (unrecorded commits, a merged PR, Synced at or
In the code drift, new PR comments) recommends /crav1-add-to-spec; wording,
structure, diagrams and constraints stay with /crav1-tighten-spec, the
default when unclear. A finding spec.md already covers is offer
already-fixed, with a note and no card. code-drift offers add-to-spec
before the plan review when the spec's record is behind the code.

record, cover, and clear without --yes write nothing and exit 2.
record takes one step per call and stamps Done itself. --when, when passed,
must be a full timestamp. Do not pass --when from the walk.
Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime


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

from pathlib import Path

WALK = "tighten-and-plan-ready-to-build"
PROGRESS_NAME = "walk-progress.md"
RESULTS = ("done", "nothing-to-do", "skipped", "applied", "reapplied", "ready", "ready-partial", "not-ready")
# The ready check records ready, ready-partial, or not-ready. An older Result: done still reads.
READY_RESULTS = ("ready", "ready-partial", "not-ready", "nothing-to-do")
READY_ONLY = ("ready", "ready-partial", "not-ready")
NOT_NAMED = "not named yet"
APPLIED = {"applied", "reapplied"}

# Locked step order. Playbook is intake only. Step 6 is one step that runs
# review-plan and then tighten-plan. The ready check also records verify.md,
# because that file decides Needs verify.
ORDER = (
    "playbook",
    "review-architecture",
    "tighten-spec",
    "resolve-open-questions",
    "plan-from-spec",
    "review-and-tighten-plan",
    "tasks-ready-to-build",
)
COVERS = {
    "playbook": ("playbook",),
    "review-architecture": ("spec",),
    "tighten-spec": ("spec",),
    "resolve-open-questions": ("spec",),
    "plan-from-spec": ("spec", "plan", "tasks"),
    "review-and-tighten-plan": ("spec", "plan", "tasks"),
    "tasks-ready-to-build": ("spec", "plan", "tasks", "verify"),
}
FILE_OF = {
    "spec": "spec.md",
    "plan": "plan.md",
    "tasks": "tasks.md",
    "verify": "verify.md",
}
LABEL = {
    "spec": "Spec version",
    "plan": "Plan version",
    "tasks": "Tasks version",
    "verify": "Verify version",
}
IMPACT = {
    "spec": "The spec changed since this step, so the step no longer covers the current spec.",
    "plan": "The plan changed since this step, so the step no longer covers the current plan.",
    "tasks": "The tasks changed since this step, so the step no longer covers the current tasks.",
    "verify": "verify.md changed since the ready check, so the check no longer covers it.",
    "playbook": "The playbook file changed since this step. The playbook is intake only.",
    "questions": (
        "The open questions changed since this step, so resolve-open-questions "
        "no longer covers them."
    ),
}
# A verify.md edit is recorded (COVERS) and does not reopen the ready check (1.136.0).
# Only this walk's record, or clear --yes, rewrites walk-progress.md.
RESTAMP = (
    "Only the walk's record or `clear --yes` restamps walk-progress.md. "
    "/crav1-tasks-ready-to-build only writes build-map.md."
)

# Which file change reopens a step (1.123.0). Narrower than COVERS.
# review-architecture is handled in affects_of: once a later step covers the
# spec, a spec change does not send the walk back to the architecture review.
# plan-from-spec writes the plan from the spec, so a hand edit of the plan
# reopens the plan review, not the step that wrote the plan.
# verify stays in COVERS so the ready check still snapshots its hash. It is
# not in AFFECTS: a verify-only change does not reopen this step (1.136.0).
AFFECTS = {
    "playbook": ("playbook",),
    "review-architecture": ("spec",),
    "tighten-spec": ("spec",),
    "resolve-open-questions": ("spec", "questions"),
    "plan-from-spec": ("spec",),
    "review-and-tighten-plan": ("spec", "plan", "tasks"),
    "tasks-ready-to-build": ("spec", "plan", "tasks"),
}
# Versions since 1.138.0 ignore line endings and progress marks. The line
# `Content stamp: normalized` says so. An older step has no such line.
CONTENT_STAMP = "normalized"
# Full product of progress variants. Above this, undo one slot at a time.
_UNDO_CAP = 1 << 14
_TASK_LINE = re.compile(r"^(\s*- \[)([ xX])(\] T\d+\b)(.*)$")
_BRANCH_LINE = re.compile(r"^(?:- )?Branch:\s+\S", re.I)
_PR_PAREN = re.compile(r"\s*\(PR\s+\d+(?:,\s*merged)?\)", re.I)
_TRAILING_MERGED = re.compile(r"(?i)\s+merged$")
_TRAILING_DONE = re.compile(r"(?i)\s+\(done\)$")

# An edit confined to ## Open questions does not reopen these steps (1.137.0).
# They compare Spec body. resolve-open-questions also compares Questions version.
BODY_SPEC_STEPS = frozenset({
    "tighten-spec",
    "plan-from-spec",
    "review-and-tighten-plan",
    "tasks-ready-to-build",
})
STEP_COMMAND = {
    "playbook": "/crav1-tighten-and-plan-ready-to-build",
    "review-architecture": "/crav1-review-architecture",
    "tighten-spec": "/crav1-tighten-spec",
    "resolve-open-questions": "/crav1-resolve-open-questions",
    "plan-from-spec": "/crav1-plan-from-spec",
    "review-and-tighten-plan": "/crav1-review-plan",
    "tasks-ready-to-build": "/crav1-tasks-ready-to-build",
}
DONE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$")

# Optional extras the walk can offer. They are not locked steps. Recording
# one when the walk finishes it counts that write as inside the walk.
EXTRAS = (
    "review-security",
    "research",
    "model-data",
    "show-or-ask-open-questions",
    "suggest-tests-for-code",
)
for _extra in EXTRAS:
    COVERS[_extra] = ("spec", "plan", "tasks")
    AFFECTS[_extra] = ()

# Ready-check rows. The command is the skill that owns the fix. can_jump_back
# is false when that skill is outside this walk.
JUMP = {
    "plan-from-spec": "/crav1-plan-from-spec",
    "resolve-open-questions": "/crav1-resolve-open-questions",
    "review-plan": "/crav1-review-plan",
    "tighten-plan": "/crav1-tighten-plan",
}

# One jump back from a spec-tagged plan finding (1.135.0). The path is the
# sibling file the walk opens. A second sighting of the same finding is an
# open point. This script does not edit spec.md and does not write verify.md.
TIGHTEN_SPEC_PATH = "../crav1-tighten-spec/SKILL.md"
CONTINUE_JUMP = "plan-from-spec, review-and-tighten-plan, tasks-ready-to-build"
CONTINUE_POINT = "review-and-tighten-plan, tasks-ready-to-build"
JUMP_CHOICE = "Fix it in the spec first (Recommended)"
POINT_CHOICE = "Keep it as an open point and go on"
FINDING_ID = re.compile(r"^P[1-9][0-9]*$")
JUMP_RESULTS = {"jumped", "open-point", "already-fixed"}
# The owner of a spec finding (1.194.0). A finding about code the spec has not
# recorded (unrecorded commits, a merged PR, Synced at or In the code drift,
# new PR comments) is /crav1-add-to-spec's. Wording, structure, diagrams and
# constraints stay /crav1-tighten-spec's, which is also the default when unclear.
ADD_TO_SPEC_PATH = "../crav1-add-to-spec/SKILL.md"
ADD_CHOICE = "Record the code in the spec first (Recommended)"
# Plain labels for walk cards (1.196.0): no letters, no internal ids. Plan and spec
# resolution ids map through LABELS in crav1-tighten-plan/scripts/batch_offer.py.
PLAIN_LABELS = {
    "tighten-spec": JUMP_CHOICE,
    "add-to-spec": ADD_CHOICE,
    "open-point": POINT_CHOICE,
    "review-now": "Review the plan as it is",
    "rerun": "Redo the step",
    "nothing new": "Skip redoing the step",
}
FINDING_KINDS = ("code-drift", "spec-text")
DRIFT_WORDS = re.compile(
    r"(?i)\b(?:merged?|unrecorded|not recorded|has not recorded|hasn't recorded|not in the spec yet|"
    r"synced at|in the code|new (?:pr )?(?:comments?|replies|threads?)|new commits?|commits? after|"
    r"drift|behind the code|sync)\b"
)
SPEC_TEXT_WORDS = re.compile(
    r"(?i)\b(?:wording|reword|structure|heading|section order|diagrams?|edge|constraints?|acceptance|"
    r"ambiguous|vague|contradicts?|unclear|typo)\b"
)
SHA_TOKEN = re.compile(r"\b(?=[0-9a-f]*[0-9])(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b")
MERGE_SHA = re.compile(r"(?i)\bmerged?\b[^.;]*?\b(?:at|as|in)\s+([0-9a-f]{7,40})\b")
PR_IN_TEXT = re.compile(r"(?i)\bPR\s*#?(\d+)\b")
SYNCED_LINE = re.compile(r"^Synced at:\s*(?:(?P<repo>\S+)\s+)?(?P<branch>\S+)@(?P<sha>[0-9a-f]{7,40})", re.M)


def version_of(path: Path) -> str:
    if not path.is_file():
        return "missing"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def version_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _hash12(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()[:12]


def _lf_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _ending_hashes(lf_text: str) -> set[str]:
    """SHA-256 prefixes of the LF text and the same text with CRLF."""
    lf = lf_text.encode("utf-8")
    crlf = lf_text.replace("\n", "\r\n").encode("utf-8")
    return {_hash12(lf), _hash12(crlf)}


def _task_rest_stripped(rest: str) -> str:
    """Drop a PR or done note the kit writes on a task line. Keep the title."""
    rest = _PR_PAREN.sub("", rest)
    rest = _TRAILING_DONE.sub("", rest)
    rest = _TRAILING_MERGED.sub("", rest)
    rest = re.sub(r"[ \t]{2,}", " ", rest)
    return rest.rstrip()


def _strip_branch_progress(line: str) -> str:
    """Drop (PR n) and a trailing merged word. Keep the branch and its markers."""
    line = _PR_PAREN.sub("", line)
    line = _TRAILING_MERGED.sub("", line)
    line = re.sub(r"[ \t]{2,}", " ", line)
    return line.rstrip()


def _task_canonical(line: str) -> str:
    match = _TASK_LINE.match(line)
    if not match:
        return line
    rest = _task_rest_stripped(match.group(4))
    return f"{match.group(1)} {match.group(3)}{rest}"


_CLAIM_LINE = re.compile(r"^\s*In progress:\s+", re.I)
_CLAIM_AGE_LINE = re.compile(r"^\s*Claim max age:\s*\d+\s*days?\s*$", re.I)


def _strip_claim_lines(text: str) -> str:
    """Claim lines are not part of a content stamp (1.151.0)."""
    return "\n".join(
        line
        for line in (text or "").split("\n")
        if not _CLAIM_LINE.match(line) and not _CLAIM_AGE_LINE.match(line)
    )


def normalize_text(kind: str, text: str) -> str:
    """Content used for a stamp. LF, and progress marks removed.

    spec: a Match Branch line loses `(PR n)` and a trailing `merged`.
    tasks: a checkbox is `[ ]`, and a PR or `(done)` note on that line is
    dropped. plan, verify, playbook, and questions: line endings only.
    A branch name, `(into …)`, `(spec branch)`, `(branch:)`, and `(map:)` stay.
    In progress: and Claim max age: lines are ignored (1.151.0).
    """
    text = _strip_claim_lines(_lf_text(text or ""))
    if kind not in ("spec", "tasks"):
        return text
    lines = text.split("\n")
    out = []
    for line in lines:
        if kind == "tasks" and _TASK_LINE.match(line):
            out.append(_task_canonical(line))
        elif kind == "spec" and _BRANCH_LINE.match(line):
            out.append(_strip_branch_progress(line))
        else:
            out.append(line)
    return "\n".join(out)


def _task_options(line: str) -> list[str]:
    match = _TASK_LINE.match(line)
    if not match:
        return [line]
    rest = match.group(4)
    stripped = _task_rest_stripped(rest)
    rests = [rest] if rest == stripped else [rest, stripped]
    boxes = [" ", "x"]
    if match.group(2) == "X":
        boxes.append("X")
    out = []
    for box in boxes:
        for item in rests:
            out.append(f"{match.group(1)}{box}{match.group(3)}{item}")
    return list(dict.fromkeys(out))


def _line_options(line: str, kind: str) -> list[str]:
    if kind == "tasks" and _TASK_LINE.match(line):
        return _task_options(line)
    if kind == "spec" and _BRANCH_LINE.match(line):
        stripped = _strip_branch_progress(line)
        if stripped == line:
            return [line]
        return [line, stripped]
    return [line]


def _iter_product(options: list[list[str]]):
    if not options:
        yield []
        return
    indexes = [0] * len(options)
    while True:
        yield [options[i][indexes[i]] for i in range(len(options))]
        cursor = len(options) - 1
        while cursor >= 0:
            indexes[cursor] += 1
            if indexes[cursor] < len(options[cursor]):
                break
            indexes[cursor] = 0
            cursor -= 1
        else:
            return


def _stripped_lines(lines: list[str], kind: str) -> list[str]:
    """Notes removed. Checkboxes stay as they are now."""
    out = []
    for line in lines:
        if kind == "tasks" and _TASK_LINE.match(line):
            match = _TASK_LINE.match(line)
            rest = _task_rest_stripped(match.group(4))
            out.append(f"{match.group(1)}{match.group(2)}{match.group(3)}{rest}")
        elif kind == "spec" and _BRANCH_LINE.match(line):
            out.append(_strip_branch_progress(line))
        else:
            out.append(line)
    return out


def _hash_undo(stored: str, lf_text: str, kind: str) -> bool:
    """True when some progress variant of this text hashes to an old stamp.

    The product of checkbox and PR-note choices is tried when it is at most
    16384. Above that, each line is undone on its own, and once with every
    PR note removed and one checkbox flipped. That covers one tick and any
    number of added `(PR n)` marks. Two or more checkbox edits on a long
    task list are not proved here. The caller then tries HEAD once.
    """
    lines = lf_text.split("\n")
    options = [_line_options(line, kind) for line in lines]
    product = 1
    over = False
    for opts in options:
        product *= len(opts)
        if product > _UNDO_CAP:
            over = True
            break

    def hits(candidate: str) -> bool:
        return stored in _ending_hashes(candidate)

    if not over:
        for combo in _iter_product(options):
            if hits("\n".join(combo)):
                return True
        return False
    if hits("\n".join(lines)):
        return True
    stripped = _stripped_lines(lines, kind)
    if hits("\n".join(stripped)):
        return True
    for index, opts in enumerate(options):
        for alt in opts:
            if alt == lines[index]:
                continue
            trial = list(lines)
            trial[index] = alt
            if hits("\n".join(trial)):
                return True
            trial = list(stripped)
            trial[index] = alt
            if hits("\n".join(trial)):
                return True
    return False


def _git_blob(path: Path) -> bytes | None:
    """HEAD blob for this path, once. Missing git or a missing blob is None."""
    repo = None
    for base in [path.parent, *path.parents]:
        if (base / ".git").exists():
            repo = base
            break
        if str(base) == path.anchor:
            break
    if repo is None:
        return None
    try:
        rel = path.resolve().relative_to(repo.resolve()).as_posix()
    except (OSError, ValueError):
        return None
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "show", f"HEAD:{rel}"],
            capture_output=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def _git_undo(stored: str, path: Path | None, kind: str, piece: str, part: str) -> bool:
    """One compare against HEAD. Match when that blob is the stored stamp
    and its normalized text equals the current piece."""
    if path is None or not path.is_file():
        return False
    blob = _git_blob(path)
    if blob is None:
        return False
    try:
        old = blob.decode("utf-8")
    except UnicodeDecodeError:
        return False
    old_lf = _lf_text(old)
    if part == "spec_body":
        old_piece, _questions = spec_parts(old_lf)
    elif part == "questions":
        _body, old_piece = spec_parts(old_lf)
    else:
        old_piece = old_lf
        if _hash12(blob) == stored and normalize_text(kind, old) == normalize_text(kind, piece):
            return True
    if stored not in _ending_hashes(old_piece) and _hash12(old_piece.encode("utf-8")) != stored:
        return False
    return normalize_text(kind, old_piece) == normalize_text(kind, piece)


def stamp_matches(
    stored: str | None,
    text: str | None,
    kind: str,
    normalized_stamp: bool,
    raw_bytes: bytes | None = None,
    path: Path | None = None,
    part: str = "file",
) -> bool:
    """True when the stored version still covers this text.

    A `Content stamp: normalized` step compares the normalized text. An older
    step compares the raw bytes, then the other line ending, then one
    hash-undo over progress variants, then HEAD once. A progress-only edit
    matches. A sentence change does not.
    """
    if stored in (None, "missing"):
        return text is None
    if text is None:
        return False
    if stored == version_text(normalize_text(kind, text)):
        return True
    if normalized_stamp:
        return False
    if raw_bytes is not None and _hash12(raw_bytes) == stored:
        return True
    lf = _lf_text(text)
    if stored in _ending_hashes(lf):
        return True
    if _hash_undo(stored, lf, kind):
        return True
    return _git_undo(stored, path, kind, lf, part)


def _cut_heading(lines: list[str], heading: str) -> tuple[list[str], list[str]]:
    """Drop one `## ` section. The section runs through the line before the next heading."""
    start = None
    want = heading.strip().lower()
    for i, line in enumerate(lines):
        if line.strip().lower() == want:
            start = i
            break
    if start is None:
        return lines, []
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return lines[:start] + lines[end:], lines[start:end]


def spec_without_approval(text: str) -> str:
    """The spec with `## Approval needed` removed.

    Recording or editing that section does not change the spec stamp, so it
    does not reopen a walk step (1.141.0).
    """
    if not text:
        return ""
    kept, _section = _cut_heading(text.splitlines(keepends=True), "## approval needed")
    return "".join(kept)


def spec_parts(text: str) -> tuple[str, str]:
    """Split spec text into the body and the Open questions section.

    The section runs from its heading through the line before the next
    `## ` heading. A spec with no such section has an empty questions part.
    `## Approval needed` is removed from the body and is not part of the
    questions part, so an edit there reopens no step (1.141.0).
    """
    if not text:
        return "", ""
    lines = text.splitlines(keepends=True)
    body_lines, questions = _cut_heading(lines, "## open questions")
    body_lines, _approval = _cut_heading(body_lines, "## approval needed")
    return "".join(body_lines), "".join(questions)


# Which spec section reopens which walk steps (1.148.0).
# The first step in a tuple is the owner. Later steps are there only when
# that section is what the plan was written from. A change reopens that
# set, not every later step, and not resolve-open-questions unless the
# question's words or its stable id changed.
# An unknown heading uses REQUIREMENT_STEPS. That is the safe default:
# a new constraint must still reopen the plan.
REQUIREMENT_STEPS = (
    "tighten-spec",
    "plan-from-spec",
    "review-and-tighten-plan",
    "tasks-ready-to-build",
)
QUESTION_STEPS = ("resolve-open-questions",)
# These sections may change without reopening. add-to-spec can restamp.
RESTAMP_SLUGS = frozenset({"match", "in-the-code"})
# Approval needed is omitted from the stamp entirely (1.141.0).
_SKIP_SECTIONS = frozenset({"approval-needed"})
SECTION_STEPS = {
    "preamble": REQUIREMENT_STEPS,
    "problem": REQUIREMENT_STEPS,
    "goals": REQUIREMENT_STEPS,
    "non-goals": REQUIREMENT_STEPS,
    "users-and-journeys": REQUIREMENT_STEPS,
    "acceptance-criteria": REQUIREMENT_STEPS,
    "constraints": REQUIREMENT_STEPS,
    "requirements": REQUIREMENT_STEPS,
    "scope": REQUIREMENT_STEPS,
    "decisions": REQUIREMENT_STEPS,
    "background": REQUIREMENT_STEPS,
    "context": REQUIREMENT_STEPS,
    "what-the-dump-says": REQUIREMENT_STEPS,
    "trace": REQUIREMENT_STEPS,
    "research-findings": REQUIREMENT_STEPS,
    "open-questions": QUESTION_STEPS,
    "match": (),
    "in-the-code": (),
}
SECTION_TITLES = {
    "preamble": "the spec introduction",
    "problem": "Problem",
    "goals": "Goals",
    "non-goals": "Non-goals",
    "users-and-journeys": "Users and journeys",
    "acceptance-criteria": "Acceptance criteria",
    "constraints": "Constraints",
    "requirements": "Requirements",
    "scope": "Scope",
    "decisions": "Decisions",
    "background": "Background",
    "context": "Context",
    "what-the-dump-says": "What the dump says",
    "trace": "Trace",
    "research-findings": "Research findings",
    "open-questions": "Open questions",
    "match": "Match",
    "in-the-code": "In the code",
}
_HEADING = re.compile(r"^##\s+(.+?)\s*$")
_SYNCED_LINE = re.compile(r"^Synced at:\s+\S", re.I)
_SECTION_VALUE = re.compile(r"^(?:none|[a-z0-9-]+@[0-9a-f]{12}(?: [a-z0-9-]+@[0-9a-f]{12})*)$")
_QUESTION_ID_VALUE = re.compile(
    r"^(?:none|[A-Za-z0-9._-]+@[0-9a-f]{12}(?:=a)?(?: [A-Za-z0-9._-]+@[0-9a-f]{12}(?:=a)?)*)$"
)
_ID_MARK = re.compile(r"^(?:Id|Qid|Stable id):\s*([A-Za-z0-9._-]+)\s*$", re.I)


def section_slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (title or "").strip().lower()).strip("-")
    return slug or "section"


def section_title(slug: str) -> str:
    if slug in SECTION_TITLES:
        return SECTION_TITLES[slug]
    text = slug.replace("-", " ").strip()
    return text[:1].upper() + text[1:] if text else slug


def spec_section_map(text: str) -> list[tuple[str, str]]:
    """(slug, normalized hash) in document order.

    The preamble is the text before the first heading, without `Synced at`
    lines. Those lines are a sync stamp, not a requirement. `## Approval
    needed` is omitted. Duplicate headings are joined in order.
    """
    lines = _lf_text(text or "").split("\n")
    blocks: list[tuple[str, list[str]]] = [("preamble", [])]
    for line in lines:
        match = _HEADING.match(line)
        if match:
            blocks.append((section_slug(match.group(1)), [line]))
        else:
            blocks[-1][1].append(line)
    ordered: list[str] = []
    chunks: dict[str, list[str]] = {}
    for slug, chunk in blocks:
        if slug in _SKIP_SECTIONS:
            continue
        if slug == "preamble":
            chunk = [item for item in chunk if not _SYNCED_LINE.match(item.strip())]
            # A Synced at line leaves a blank line behind. That blank is not a requirement.
            raw_preamble = re.sub(r"\n{3,}", "\n\n", "\n".join(chunk))
            chunk = raw_preamble.split("\n")
        if slug not in chunks:
            ordered.append(slug)
            chunks[slug] = []
        chunks[slug].extend(chunk)
    out = []
    for slug in ordered:
        raw = "\n".join(chunks[slug])
        out.append((slug, version_text(normalize_text("spec", raw))))
    return out


def section_stamp_line(text: str | None) -> str:
    if text is None:
        return "none"
    parts = [f"{slug}@{hashed}" for slug, hashed in spec_section_map(text)]
    return " ".join(parts) if parts else "none"


def _parse_section_stamps(value: str | None) -> dict[str, str]:
    if not value or value == "none":
        return {}
    out: dict[str, str] = {}
    for part in value.split():
        slug, _, hashed = part.partition("@")
        if slug and hashed:
            out[slug] = hashed
    return out


def _changed_slugs(stored: str | None, text: str) -> list[str]:
    old = _parse_section_stamps(stored)
    current = spec_section_map(text)
    new = {slug: hashed for slug, hashed in current}
    changed = [slug for slug, hashed in current if old.get(slug) != hashed]
    changed.extend(slug for slug in old if slug not in new)
    return changed


def _word_hash(text: str) -> str:
    """Hash of the question's words. Stays a word hash if question_key becomes a stable id."""
    norm = re.sub(r"\s+", " ", (text or "").strip().lower())
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:12]


def _iter_questions(text: str) -> list[dict]:
    """Every question bullet, including ones that already have Answered:."""
    lines = _lf_text(text or "").split("\n")
    start = None
    for index, line in enumerate(lines):
        if line.strip().lower() == "## open questions":
            start = index + 1
            break
    if start is None:
        return []
    questions: list[dict] = []
    current: dict | None = None
    for line in lines[start:]:
        if line.startswith("## "):
            break
        if line.startswith("- ") and not line.startswith("  "):
            body = line[2:].strip()
            current = {"text": body, "marks": []} if body else None
            if current:
                questions.append(current)
            continue
        if current is not None and line.startswith("  - "):
            current["marks"].append(line[4:].strip())
    return questions


def _lookup_stable_id(text: str, marks: list[str]) -> str | None:
    """A stable id from an Id mark, or from question_blocks when 1.146.0 provides one.

    question_key is used only when it is no longer the word hash, which is
    how a later kit can publish a stable id without a new function name.
    """
    for mark in marks or []:
        match = _ID_MARK.match(mark.strip())
        if match:
            return match.group(1)
    try:
        mod = blocks_mod()
    except SystemExit:
        return None
    for name in ("question_stable_key", "stable_question_id", "question_identity"):
        fn = getattr(mod, name, None)
        if not callable(fn):
            continue
        try:
            found = fn(text, marks)
        except TypeError:
            found = fn(text)
        if found and re.fullmatch(r"[A-Za-z0-9._-]+", str(found)):
            return str(found)
    key_fn = getattr(mod, "question_key", None)
    if callable(key_fn):
        key = str(key_fn(text) or "")
        if key and key != _word_hash(text) and re.fullmatch(r"[A-Za-z0-9._-]+", key):
            return key
    return None


def _question_identity(text: str, marks: list[str]) -> tuple[str, str, bool]:
    word = _word_hash(text)
    stable = _lookup_stable_id(text, marks)
    answered = any(mark.startswith("Answered:") for mark in marks or [])
    return (stable or word), word, answered


def question_id_line(text: str | None) -> str:
    if not text:
        return "none"
    parts = []
    for question in _iter_questions(text):
        ident, word, answered = _question_identity(question["text"], question["marks"])
        token = f"{ident}@{word}" + ("=a" if answered else "")
        parts.append(token)
    return " ".join(parts) if parts else "none"


def _parse_question_ids(value: str | None) -> tuple[dict[str, str], dict[str, str]]:
    """Open ids and answered ids, each mapping id to the word hash."""
    open_ids: dict[str, str] = {}
    answered: dict[str, str] = {}
    if not value or value == "none":
        return open_ids, answered
    for part in value.split():
        answered_mark = part.endswith("=a")
        core = part[:-2] if answered_mark else part
        ident, _, word = core.partition("@")
        if not ident or not word:
            continue
        if answered_mark:
            answered[ident] = word
        else:
            open_ids[ident] = word
    return open_ids, answered


def _stable_key_of(text: str) -> str | None:
    try:
        fn = getattr(blocks_mod(), "question_stable_key", None)
    except SystemExit:
        return None
    if not callable(fn):
        return None
    found = str(fn(text) or "")
    if found and re.fullmatch(r"[A-Za-z0-9._-]+", found):
        return found
    return None


def _close_reword_ids(prev_rows: list[dict], curr_rows: list[dict], stored_rows: list[dict]) -> set[str]:
    """Ids of one close reword. Two close questions are not merged (1.146.0)."""
    try:
        mod = blocks_mod()
    except SystemExit:
        return set()
    sim = getattr(mod, "question_similarity", None)
    if not callable(sim):
        return set()
    close = float(getattr(mod, "CLOSE_QUESTION", 0.86))
    stored_text = {}
    for row in stored_rows or []:
        for key in (row.get("stable"), row.get("key")):
            if key and row.get("text"):
                stored_text[key] = row["text"]
    same: set[str] = set()
    for prev in prev_rows:
        ptext = stored_text.get(prev["id"]) or ""
        if not ptext:
            continue
        hits = [curr for curr in curr_rows if sim(ptext, curr.get("text") or "") >= close]
        if len(hits) != 1:
            continue
        curr = hits[0]
        back = [
            other for other in prev_rows
            if sim(stored_text.get(other["id"]) or "", curr.get("text") or "") >= close
        ]
        if len(back) == 1:
            same.add(prev["id"])
            same.add(curr["id"])
    return same


def _diff_questions(stored: str | None, text: str, stored_rows: list[dict] | None = None) -> dict:
    """Which questions must be asked again.

    A settled question stays settled when an Answered line is added or a new
    answered question appears. The stable key from 1.146.0 ignores a refreshed
    commit list, so that edit does not reopen. One close reword of a stored
    question stays that question. A new open question, a removed open question,
    or a word change on an explicit id reopens resolve-open-questions.
    """
    prev_open, prev_answered = _parse_question_ids(stored)
    current = []
    for question in _iter_questions(text):
        ident, word, answered = _question_identity(question["text"], question["marks"])
        current.append({
            "id": ident,
            "word": word,
            "answered": answered,
            "text": question["text"],
        })
    curr_all = {row["id"]: row for row in current}
    curr_open = {row["id"]: row for row in current if not row["answered"]}
    fresh_prev = [
        {"id": ident, "word": word}
        for ident, word in prev_open.items()
        if ident not in curr_open and not (
            curr_all.get(ident) and curr_all[ident]["answered"]
        )
    ]
    fresh_curr = [row for ident, row in curr_open.items() if ident not in prev_open]
    same = _close_reword_ids(fresh_prev, fresh_curr, stored_rows or [])
    changed: list[dict] = []
    reopen = False
    answered_events = False

    def note(ident: str, reason: str, does_reopen: bool) -> None:
        nonlocal reopen
        changed.append({"id": ident, "reason": reason})
        if does_reopen:
            reopen = True

    for ident, row in curr_open.items():
        if ident in same:
            continue
        if ident not in prev_open:
            note(ident, "reopened" if ident in prev_answered else "new", True)
        elif prev_open[ident] != row["word"]:
            # Same stable key: only a commit list, a PR number, or a date moved.
            if _stable_key_of(row["text"]) == ident:
                continue
            note(ident, "reworded", True)
    for ident, word in prev_open.items():
        if ident in same or ident in curr_open:
            continue
        row = curr_all.get(ident)
        if row and row["answered"] and row["word"] == word:
            answered_events = True
            continue
        if row and row["answered"]:
            if _stable_key_of(row["text"]) == ident:
                answered_events = True
                continue
            note(ident, "reworded", True)
            continue
        note(ident, "removed", True)
    for ident, row in curr_all.items():
        if not row["answered"] or ident in prev_open or ident in same:
            continue
        if ident not in prev_answered:
            answered_events = True
        elif prev_answered[ident] != row["word"] and _stable_key_of(row["text"]) != ident:
            note(ident, "reworded", True)
    return {
        "reopen": reopen,
        "answered_only": answered_events and not reopen,
        "changed": changed,
    }


def _architecture_absorbs(steps: dict) -> bool:
    """True when the architecture review is the latest recorded spec step."""
    if "review-architecture" not in steps:
        return False
    own = ORDER.index("review-architecture")
    for later in ORDER[own + 1:]:
        if later in steps and "spec" in AFFECTS.get(later, ()):
            return False
    return True


def _steps_for_slugs(changed: list[str], question_reopen: bool, steps: dict) -> tuple[list[str], bool]:
    """Recorded steps to reopen, and whether a requirement section changed."""
    wanted: list[str] = []

    def add(step: str) -> None:
        if step not in wanted:
            wanted.append(step)

    requirement = False
    for slug in changed:
        if slug == "open-questions":
            if question_reopen:
                add("resolve-open-questions")
            continue
        if slug in RESTAMP_SLUGS:
            continue
        owners = SECTION_STEPS.get(slug, REQUIREMENT_STEPS)
        if owners == REQUIREMENT_STEPS or "tighten-spec" in owners:
            requirement = True
        for step in owners:
            add(step)
    if _architecture_absorbs(steps) and "tighten-spec" in wanted:
        add("review-architecture")
    recorded = [step for step in ORDER if step in wanted and step in steps]
    return recorded, requirement


def _body_hash(text: str) -> str:
    body, _questions = spec_parts(_lf_text(text))
    return version_text(normalize_text("spec", body))


def section_effect(root: Path, steps: dict, own: dict | None = None) -> dict:
    """What a spec edit invalidates, from the recorded section stamps.

    Inactive when no recorded step has `Section stamps` (a walk recorded
    before 1.148.0). Those steps keep the 1.137 whole-body rule.
    With `own`, the baseline is that one step's own stamps (1.176.0), so a
    step recorded again after a spec edit compares against its fresh stamps,
    not against a later step's older ones.
    """
    baseline = None
    if own is not None and own.get("section_stamps") and own.get("section_stamps") != "none":
        baseline = own
    # Extras keep the version they saw. The baseline is the latest locked step.
    for step in ([] if baseline is not None else list(ORDER) + list(EXTRAS)):
        if step in EXTRAS and baseline is not None:
            break
        body = steps.get(step) or {}
        if body.get("section_stamps"):
            baseline = body
    empty = {
        "active": False,
        "changed_slugs": [],
        "titles": [],
        "reopen_steps": [],
        "reopen_line": None,
        "changed_questions": [],
        "restamp_only": False,
        "question_reopen": False,
        "requirement_hit": False,
    }
    if baseline is None:
        return empty
    spec_text, _raw = _read_pair(root / "spec.md")
    text = spec_text or ""
    changed = _changed_slugs(baseline.get("section_stamps"), text)
    resolve = steps.get("resolve-open-questions") or {}
    qdiff = {"reopen": False, "answered_only": False, "changed": []}
    if "open-questions" in changed and (resolve.get("question_ids") or resolve.get("question_rows")):
        qdiff = _diff_questions(
            resolve.get("question_ids"), text, resolve.get("question_rows") or [],
        )
    elif "open-questions" in changed and resolve:
        qdiff = {"reopen": True, "answered_only": False, "changed": []}
    reopen, requirement = _steps_for_slugs(changed, bool(qdiff["reopen"]), steps)
    titles = [section_title(slug) for slug in changed]
    body_differs = False
    stored_body = baseline.get("spec_body")
    if stored_body and stored_body not in (None, "missing") and text:
        body_differs = stored_body != _body_hash(text)
    if not changed and body_differs:
        titles = ["Synced at"]
    restamp_slugs = set(RESTAMP_SLUGS)
    only_restamp = all(
        slug in restamp_slugs or (slug == "open-questions" and qdiff["answered_only"])
        for slug in changed
    )
    restamp_only = bool(titles) and not reopen and only_restamp and (
        "open-questions" not in changed or bool(qdiff["answered_only"])
    )
    line = None
    if titles:
        names = ", ".join(reopen) if reopen else "none"
        line = f"Changed: {', '.join(titles)}. Reopen: {names}."
    return {
        "active": True,
        "changed_slugs": changed,
        "titles": titles,
        "reopen_steps": reopen,
        "reopen_line": line,
        "changed_questions": qdiff["changed"],
        "restamp_only": restamp_only,
        "question_reopen": bool(qdiff["reopen"]),
        "requirement_hit": requirement,
    }


def _read_pair(path: Path) -> tuple[str | None, bytes | None]:
    if not path.is_file():
        return None, None
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8")
    return text, raw


def stamp_file(path: Path, kind: str) -> str:
    text, _raw = _read_pair(path)
    if text is None:
        return "missing"
    return version_text(normalize_text(kind, text))


def versions(root: Path, playbook: Path | None = None) -> dict:
    out = {key: stamp_file(root / name, key) for key, name in FILE_OF.items()}
    spec_text, _raw = _read_pair(root / "spec.md")
    if spec_text is None:
        out["spec_body"] = "missing"
        out["questions"] = "missing"
        out["section_stamps"] = "none"
        out["question_ids"] = "none"
    else:
        lf = _lf_text(spec_text)
        out["spec"] = version_text(normalize_text("spec", spec_without_approval(lf)))
        body, questions = spec_parts(lf)
        out["spec_body"] = version_text(normalize_text("spec", body))
        out["questions"] = version_text(normalize_text("questions", questions))
        out["section_stamps"] = section_stamp_line(lf)
        out["question_ids"] = question_id_line(lf)
    if playbook is not None:
        out["playbook"] = stamp_file(playbook, "playbook")
    return out


def fail(code: str, message: str, status: int = 1) -> None:
    json.dump({"ok": False, "code": code, "message": message}, sys.stdout)
    sys.stdout.write("\n")
    raise SystemExit(status)


def emit(payload: dict) -> None:
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")


def progress_path(root: Path) -> Path:
    return root / PROGRESS_NAME


# One status line per whole-branch build run (1.155.0). The detailed log is
# the branch's build-progress file. Two sessions may each update their own
# line; a conflict that is only these lines is settled by the newest time.
BRANCH_RUN_LINE = re.compile(
    r"^- Branch run: (?P<branch>\S+): (?P<state>.+?) \((?P<when>\d{4}-\d{2}-\d{2}T[^)\s]+)\)\. "
    r"Log: (?P<log>build-progress/\S+\.md)$"
)
BRANCH_RUNS_HEADING = "## Branch runs"


def parse_branch_run(line: str) -> dict | None:
    match = BRANCH_RUN_LINE.fullmatch((line or "").strip())
    if not match:
        return None
    return {key: match.group(key) for key in ("branch", "state", "when", "log")}


def branch_run_line(run: dict) -> str:
    return f"- Branch run: {run['branch']}: {run['state']} ({run['when']}). Log: {run['log']}"


def _newer(left: dict, right: dict) -> dict:
    """The later of two status lines for one branch. A tie keeps the right side."""
    try:
        from datetime import datetime as _dt
        a = _dt.fromisoformat(left["when"])
        b = _dt.fromisoformat(right["when"])
        return left if a > b else right
    except (ValueError, TypeError):
        return right


def merge_branch_runs(ours: dict, theirs: dict) -> dict:
    out = dict(theirs or {})
    for branch, run in (ours or {}).items():
        out[branch] = _newer(run, out[branch]) if branch in out else run
    return out


ACK_LINE = re.compile(
    r"^Acknowledged stamp: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}) \(([^)]+)\)$"
)


def _parse_ack(line: str) -> dict:
    match = ACK_LINE.fullmatch(line)
    if not match:
        fail("progress-file", f"ack line is not a shared stamp: {line}")
    names = [part.strip() for part in match.group(2).split(",") if part.strip()]
    known = set(ORDER) | set(EXTRAS)
    if len(names) < 2 or any(name not in known for name in names):
        fail("progress-file", f"ack line needs the steps that share the stamp: {line}")
    return {"when": match.group(1), "steps": names}


def _ack_line(when: str, names: list[str]) -> str:
    return f"Acknowledged stamp: {when} ({', '.join(names)})"


def _take_jump_line(current: dict, line: str) -> None:
    key, _, value = line.partition(": ")
    if not value:
        fail("progress-file", f"line has no value: {line}")
    if key == "Done":
        current["when"] = value
    elif key == "Finding":
        current["finding"] = value
    elif key == "Result":
        if value not in JUMP_RESULTS:
            fail("progress-file", f"unknown jump result {value}")
        current["result"] = value
    elif key == "Open":
        current["open"] = value
    elif key == "Continue":
        current["continue"] = value
    elif key == "Key":
        current["key"] = value
    elif key == "Topic":
        current["topic"] = value
    elif key == "Alias":
        parts = value.split()
        if not parts or any(not _HEX12.fullmatch(part) for part in parts):
            fail("progress-file", f"alias is not 12 hex: {line}")
        current["aliases"] = parts
    else:
        fail("progress-file", f"unknown line: {line}")


def parse_progress(text: str) -> dict:
    """Parse the progress file. A line the format does not allow is an error."""
    steps: dict[str, dict] = {}
    acks: list[dict] = []
    jumps: list[dict] = []
    current: dict | None = None
    kind: str | None = None
    slice_line = None
    branch_runs: dict[str, dict] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == f"Walk: {WALK}":
            continue
        if line.startswith("- Branch run: "):
            run = parse_branch_run(line)
            if run is None:
                fail("progress-file", f"branch run line is not branch: state (time). Log: file: {line}")
            branch_runs[run["branch"]] = run
            current = None
            kind = None
            continue
        if line.startswith("Slice: "):
            slice_line = line[len("Slice: "):]
            continue
        if line.startswith("Acknowledged stamp: "):
            acks.append(_parse_ack(line))
            continue
        if line.startswith("- Jump-back: ") or line.startswith("- Open point: "):
            label, _, fid = line.partition(": ")
            if not FINDING_ID.fullmatch(fid):
                fail("progress-file", f"jump id is not a P#: {line}")
            current = {
                "kind": "jump-back" if label == "- Jump-back" else "open-point",
                "id": fid,
            }
            jumps.append(current)
            kind = "jump"
            continue
        if line.startswith("- Step: "):
            step = line[len("- Step: "):]
            if step not in ORDER:
                fail("progress-file", f"unknown step {step}")
            current = {"step": step}
            steps[step] = current
            kind = "step"
            continue
        if line.startswith("- Extra: "):
            step = line[len("- Extra: "):]
            if step not in EXTRAS:
                fail("progress-file", f"unknown extra {step}")
            current = {"step": step, "extra": True}
            steps[step] = current
            kind = "step"
            continue
        if current is None:
            fail("progress-file", f"line outside a step: {line}")
        if kind == "jump":
            _take_jump_line(current, line)
            continue
        key, _, value = line.partition(": ")
        if not value:
            fail("progress-file", f"line has no value: {line}")
        if key == "Done":
            current["when"] = value
        elif key == "Result":
            if value not in RESULTS:
                fail("progress-file", f"unknown result {value}")
            current["result"] = value
        elif key == "Playbook":
            path, sep, hashed = value.rpartition("@")
            if not sep or not path:
                fail("progress-file", f"playbook line is not path@hash: {line}")
            current["playbook"] = path
            current["playbook_version"] = hashed
        elif key in LABEL.values():
            token = next(name for name, label in LABEL.items() if label == key)
            current[token] = value
        elif key == "Spec body":
            current["spec_body"] = value
        elif key == "Questions version":
            current["questions"] = value
        elif key == "Kept questions":
            current["kept_questions"] = value
        elif key == "Section stamps":
            if not _SECTION_VALUE.fullmatch(value):
                fail("progress-file", f"section stamps are not slug@hash: {line}")
            current["section_stamps"] = value
        elif key == "Question ids":
            if not _QUESTION_ID_VALUE.fullmatch(value):
                fail("progress-file", f"question ids are not id@hash: {line}")
            current["question_ids"] = value
        elif key == "Question":
            parts = value.split(" ", 2)
            if len(parts) < 3 or not _HEX12.fullmatch(parts[0]) or not _HEX12.fullmatch(parts[1]):
                fail("progress-file", f"question line is not two keys and text: {line}")
            current.setdefault("question_rows", []).append({
                "key": parts[0],
                "stable": parts[1],
                "text": parts[2],
            })
        elif key == "Content stamp":
            if value != CONTENT_STAMP:
                fail("progress-file", f"unknown content stamp: {line}")
            current["content_stamp"] = value
        else:
            fail("progress-file", f"unknown line: {line}")
    for step, body in steps.items():
        for need in ("when", "result"):
            if need not in body:
                fail("progress-file", f"step {step} has no {need}")
        for token in COVERS[step]:
            if token == "playbook":
                if "playbook" not in body or "playbook_version" not in body:
                    fail("progress-file", f"step {step} has no playbook line")
            elif token not in body:
                fail("progress-file", f"step {step} has no {LABEL[token]}")
    for jump in jumps:
        for need in ("when", "finding", "result", "continue", "key"):
            if need not in jump:
                fail("progress-file", f"{jump['kind']} {jump['id']} has no {need}")
        if jump["kind"] == "jump-back":
            if jump["result"] != "jumped":
                fail("progress-file", f"jump-back {jump['id']} result is not jumped")
            if jump.get("open") not in (TIGHTEN_SPEC_PATH, ADD_TO_SPEC_PATH):
                fail("progress-file", f"jump-back {jump['id']} does not name {TIGHTEN_SPEC_PATH} or {ADD_TO_SPEC_PATH}")
        elif jump["result"] not in ("open-point", "already-fixed"):
            fail("progress-file", f"open point {jump['id']} result is not open-point")
    return {"slice": slice_line, "steps": steps, "acks": acks, "jumps": jumps, "branch_runs": branch_runs}


def load(root: Path) -> dict:
    path = progress_path(root)
    if not path.is_file():
        return {"slice": None, "steps": {}, "acks": [], "jumps": [], "branch_runs": {}}
    data = parse_progress(path.read_text(encoding="utf-8"))
    data.setdefault("acks", [])
    data.setdefault("jumps", [])
    data.setdefault("branch_runs", {})
    return data


def _render_stamp(lines: list[str], body: dict) -> None:
    if body.get("content_stamp"):
        lines.append(f"  Content stamp: {body['content_stamp']}")


def _render_jumps(lines: list[str], jumps: list | None) -> None:
    for jump in jumps or []:
        title = "Jump-back" if jump["kind"] == "jump-back" else "Open point"
        lines.append(f"- {title}: {jump['id']}")
        lines.append(f"  Done: {jump['when']}")
        lines.append(f"  Finding: {jump['finding']}")
        lines.append(f"  Result: {jump['result']}")
        if jump.get("open"):
            lines.append(f"  Open: {jump['open']}")
        lines.append(f"  Continue: {jump['continue']}")
        lines.append(f"  Key: {jump['key']}")
        if jump.get("topic"):
            lines.append(f"  Topic: {jump['topic']}")
        if jump.get("aliases"):
            lines.append(f"  Alias: {' '.join(jump['aliases'])}")
        lines.append("")


def render(slice_label: str, steps: dict, acks: list | None = None, jumps: list | None = None, branch_runs: dict | None = None) -> str:
    lines = ["# Walk progress", "", f"Walk: {WALK}", f"Slice: {slice_label}", ""]
    for ack in acks or []:
        lines.append(_ack_line(ack["when"], ack["steps"]))
    if acks:
        lines.append("")
    for step in ORDER:
        body = steps.get(step)
        if not body:
            continue
        lines.append(f"- Step: {step}")
        lines.append(f"  Done: {body['when']}")
        lines.append(f"  Result: {body['result']}")
        if step == "playbook":
            lines.append(f"  Playbook: {body['playbook']}@{body['playbook_version']}")
        else:
            for token in COVERS[step]:
                lines.append(f"  {LABEL[token]}: {body[token]}")
            if "spec_body" in body:
                lines.append(f"  Spec body: {body['spec_body']}")
            if "questions" in body:
                lines.append(f"  Questions version: {body['questions']}")
            if "kept_questions" in body:
                lines.append(f"  Kept questions: {body['kept_questions']}")
            if "question_ids" in body:
                lines.append(f"  Question ids: {body['question_ids']}")
            if "section_stamps" in body:
                lines.append(f"  Section stamps: {body['section_stamps']}")
            for row in body.get("question_rows") or []:
                lines.append(f"  Question: {row['key']} {row['stable']} {row['text']}")
        _render_stamp(lines, body)
        lines.append("")
    for step in EXTRAS:
        body = steps.get(step)
        if not body:
            continue
        lines.append(f"- Extra: {step}")
        lines.append(f"  Done: {body['when']}")
        lines.append(f"  Result: {body['result']}")
        for token in COVERS[step]:
            lines.append(f"  {LABEL[token]}: {body[token]}")
        if "spec_body" in body:
            lines.append(f"  Spec body: {body['spec_body']}")
        if "questions" in body:
            lines.append(f"  Questions version: {body['questions']}")
        if "section_stamps" in body:
            lines.append(f"  Section stamps: {body['section_stamps']}")
        _render_stamp(lines, body)
        lines.append("")
    _render_jumps(lines, jumps)
    if branch_runs:
        lines.append(BRANCH_RUNS_HEADING)
        lines.append("")
        for branch in sorted(branch_runs):
            lines.append(branch_run_line(branch_runs[branch]))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def playbook_mod():
    import importlib.util

    path = Path(__file__).resolve().parents[2] / "crav1-resolve-open-questions" / "scripts" / "playbook_store.py"
    spec = importlib.util.spec_from_file_location("playbook_store", path)
    if spec is None or spec.loader is None:
        fail("playbook", f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def question_record_list(root: Path) -> list[dict]:
    """Exact key, stable key, and text for each kept-open question.

    The stable key ignores a refreshed commit list. Old progress files have
    no Question lines and still match on the exact key.
    """
    spec = root / "spec.md"
    if not spec.is_file():
        return []
    tasks_path = root / "tasks.md"
    task_ids = None
    if tasks_path.is_file():
        task_ids = blocks_mod().task_ids_from_tasks(tasks_path.read_text(encoding="utf-8"))
    questions = blocks_mod().kept_open(
        spec.read_text(encoding="utf-8"),
        task_ids=task_ids,
        resolve_recorded=True,
    )
    rows = []
    for question in questions:
        text = question.get("text") or ""
        key = question.get("key") or blocks_mod().question_key(text)
        stable = question.get("stable_key") or blocks_mod().question_stable_key(text)
        if key and text:
            rows.append({"key": key, "stable": stable, "text": text})
    return rows


def _store_questions(root: Path, body: dict) -> None:
    body["kept_questions"] = kept_question_line(root)
    body["question_rows"] = question_record_list(root)


def kept_question_line(root: Path) -> str:
    """Question keys present when resolve-open-questions is recorded.

    A later outside edit keeps these questions Waiting. `none` means the
    section had no kept-open question.
    """
    spec = root / "spec.md"
    if not spec.is_file():
        return "none"
    tasks_path = root / "tasks.md"
    task_ids = None
    if tasks_path.is_file():
        task_ids = blocks_mod().task_ids_from_tasks(tasks_path.read_text(encoding="utf-8"))
    questions = blocks_mod().kept_open(
        spec.read_text(encoding="utf-8"),
        task_ids=task_ids,
        resolve_recorded=True,
    )
    keys: list[str] = []
    for question in questions:
        key = question.get("key") or blocks_mod().question_key(question.get("text") or "")
        if key and key not in keys:
            keys.append(key)
    return " ".join(keys) if keys else "none"


def kept_question_keys(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    body = load(root)["steps"].get("resolve-open-questions") or {}
    raw = str(body.get("kept_questions") or "")
    keys = set()
    if raw and raw != "none":
        keys.update(part for part in raw.split() if part and part != "none")
    for row in body.get("question_rows") or []:
        if row.get("key"):
            keys.add(row["key"])
        if row.get("stable"):
            keys.add(row["stable"])
    return keys


def question_rows_of(root: Path) -> list[dict]:
    if not root.is_dir():
        return []
    body = load(root)["steps"].get("resolve-open-questions") or {}
    return list(body.get("question_rows") or [])


def resolve_ever_recorded(root: Path) -> bool:
    """True when resolve-open-questions has a progress line, drifted or not."""
    if not root.is_dir():
        return False
    return "resolve-open-questions" in load(root)["steps"]


def current_tokens(root: Path, step: str, playbook: Path | None) -> dict:
    got = versions(root)
    out = {}
    for token in COVERS[step]:
        if token == "playbook":
            if playbook is None:
                fail("playbook", "the playbook step needs --playbook")
            recorded, hashed = playbook_mod().recorded_playbook(root, playbook)
            out["playbook"] = recorded
            out["playbook_version"] = stamp_file(hashed, "playbook")
        else:
            out[token] = got[token]
    if "spec" in COVERS[step]:
        out["spec_body"] = got["spec_body"]
        out["questions"] = got["questions"]
        out["section_stamps"] = got.get("section_stamps") or "none"
    if step == "resolve-open-questions":
        out["kept_questions"] = kept_question_line(root)
        out["question_ids"] = got.get("question_ids") or "none"
        out["question_rows"] = question_record_list(root)
    out["content_stamp"] = CONTENT_STAMP
    return out


def done_stamp(when: str | None) -> str:
    """The script writes Done. A passed --when must already be a full timestamp."""
    if when is None or when == "":
        return datetime.now().astimezone().isoformat(timespec="seconds")
    if not DONE_RE.fullmatch(when):
        fail(
            "when",
            "Done is a full timestamp YYYY-MM-DDTHH:MM:SS+HH:MM, "
            "for example 2026-11-09T10:19:09+01:00. Omit --when and the script stamps it.",
        )
    return when


def _one_step(values) -> str:
    """One step id. A comma, 'and', or a repeated --step is refused."""
    if isinstance(values, str):
        values = [values]
    parts: list[str] = []
    for value in values or []:
        parts.extend(part for part in re.split(r"\s*,\s*|\s+\band\b\s+", value) if part)
    if len(parts) != 1:
        fail(
            "one-step",
            "record takes one step per call. Record the step that just finished, "
            "then record the next step in its own call.",
        )
    return parts[0]


def record_unchanged(root: Path, step: str, result: str, playbook: Path | None = None) -> bool:
    """True when a record would only restamp Done or Verify version (1.171.0).

    The step is already recorded with the same Result, and every other
    version it stores is the same. Then the record is skipped: no card, no
    write, and walk-progress.md stays clean.
    """
    if root is None or not Path(root).is_dir():
        return False
    try:
        previous = load(Path(root))["steps"].get(step)
    except Exception:  # noqa: BLE001 - an unreadable file is not unchanged
        return False
    if not previous or previous.get("result") != result:
        return False
    try:
        now = current_tokens(Path(root), step, playbook)
    except Exception:  # noqa: BLE001
        return False
    for key, value in now.items():
        if "verify" in str(key).lower():
            continue
        if key in previous and previous.get(key) != value:
            return False
        if key not in previous:
            return False
    return True


def record_quiet(root: Path | None, result: str, hits: list[dict]) -> str | None:
    """1.198.0: `Recorded: not-ready (was ready-partial).` when the new result only reflects waits.

    The step is recorded with another result, and every hit is a wait on
    someone else or on a merge (no blocker, no reopened step, no jump back).
    Then the walk records without a card and says this one line. None
    otherwise, so the record card is asked as before.
    """
    if root is None or not Path(root).is_dir():
        return None
    try:
        previous = (load(Path(root))["steps"].get("tasks-ready-to-build") or {}).get("result")
    except Exception:  # noqa: BLE001
        return None
    if not previous or previous == result or previous not in READY_ONLY:
        return None
    # 1.199.0: your own pushed task waiting for its merge is a merge wait too.
    if any(hit.get("kind") != "waiting" and not hit.get("merge") for hit in hits):
        return None
    return f"Recorded: {result} (was {previous})."


def record(args: argparse.Namespace) -> None:
    step = _one_step(args.step)
    if step not in COVERS:
        fail("step", f"unknown step {step}")
    if args.result not in RESULTS:
        fail("result", f"result must be one of {', '.join(RESULTS)}")
    if step == "tasks-ready-to-build" and args.result not in READY_RESULTS:
        fail(
            "result",
            "tasks-ready-to-build records Result: ready, Result: ready-partial, "
            "or Result: not-ready, from the readiness output. "
            "An older Result: done still reads.",
        )
    if step != "tasks-ready-to-build" and args.result in READY_ONLY:
        fail("result", "ready, ready-partial, and not-ready are only for tasks-ready-to-build")
    if not args.yes:
        fail(
            "needs-yes",
            "record writes the progress file only with --yes, after the line was shown and confirmed",
            status=2,
        )
    root = Path(args.root)
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    if step == "tasks-ready-to-build" and record_unchanged(root, step, args.result, Path(args.playbook) if args.playbook else None):
        # Only Done or Verify version would change (1.171.0): no write.
        emit({"ok": True, "wrote": None, "step": step, "result": args.result, "unchanged": True, "line": "Record unchanged."})
        return
    data = load(root)
    previous = data["steps"].get(step)
    result = args.result
    kept_done = False
    # A reopened step with nothing new is clear, not a fresh nothing-to-do.
    # nothing-to-do does not replace an earlier done Result.
    if previous and result == "nothing-to-do":
        drift = affected_drift(root, step, previous, data["steps"])
        if drift:
            fail(
                "use-clear",
                f"{step} is reopened. Run clear --step {step} --yes when nothing new. "
                "Do not record nothing-to-do.",
            )
        if previous.get("result") == "done":
            result = "done"
            kept_done = True
    body = {"when": done_stamp(args.when), "result": result}
    body.update(current_tokens(root, step, Path(args.playbook) if args.playbook else None))
    # A write inside the walk updates versions already recorded. Done and
    # Result stay. An extra the walk just finished updates every locked
    # step, because the extra is not itself a place in the locked order.
    if step in EXTRAS:
        restamp_recorded(root, data["steps"], set(COVERS[step]))
    else:
        restamp_earlier(root, data["steps"], step)
    data["steps"][step] = body
    label = args.slice or data["slice"] or f"docs/specs/{root.name}/"
    if not str(label).endswith("/"):
        label = f"{label}/"
    text = render(label, data["steps"], data.get("acks"), data.get("jumps"), data.get("branch_runs"))
    progress_path(root).write_text(text, encoding="utf-8")
    payload = {"ok": True, "wrote": PROGRESS_NAME, "step": step, "result": result, "when": body["when"]}
    if kept_done:
        payload["kept_done"] = True
    emit(payload)


def _shared_groups(steps: dict) -> list[tuple[str, list[str]]]:
    grouped: dict[str, list[str]] = {}
    for step in list(ORDER) + list(EXTRAS):
        body = steps.get(step)
        if not body or "when" not in body:
            continue
        grouped.setdefault(body["when"], []).append(step)
    return [(when, names) for when, names in grouped.items() if len(names) >= 2]


def _ack_covers(acks: list, when: str, names: list[str]) -> bool:
    wanted = set(names)
    for ack in acks:
        if ack.get("when") == when and wanted <= set(ack.get("steps") or []):
            return True
    return False


def done_stamp_warning(steps: dict, acks: list | None = None) -> str | None:
    """Set when two or more steps share a Done stamp that is not acknowledged."""
    pending = [
        (when, names)
        for when, names in _shared_groups(steps)
        if not _ack_covers(acks or [], when, names)
    ]
    if not pending:
        return None
    bits = [f"{', '.join(names)} share Done {when}" for when, names in pending]
    return (
        "Record each step when it finishes, one record per call. "
        + "; ".join(bits)
        + ". Acknowledge that shared stamp once with "
        "walk_progress.py ack-stamps --root <spec-folder> --yes."
    )


def _split_ready(body: dict) -> bool:
    return "spec_body" in body and "questions" in body


def _piece_match(root: Path, body: dict, token: str, part: str) -> bool:
    """Whether one recorded version still covers the file, body, or questions."""
    normalized = body.get("content_stamp") == CONTENT_STAMP
    name = FILE_OF[token]
    path = root / name
    text, raw = _read_pair(path)
    kind = token
    piece = text
    raw_bytes = raw if part == "file" else None
    if text is not None and token == "spec" and part == "file":
        # Approval needed is not part of the spec stamp (1.141.0).
        piece = spec_without_approval(text)
    if text is not None and part != "file":
        body_text, questions = spec_parts(_lf_text(text))
        piece = body_text if part == "spec_body" else questions
        kind = "spec" if part == "spec_body" else "questions"
    stored = body.get("spec_body" if part == "spec_body" else "questions" if part == "questions" else token)
    return stamp_matches(
        stored, piece, kind, normalized, raw_bytes=raw_bytes, path=path, part=part,
    )


def hash_drift(root: Path, step: str, body: dict, steps: dict | None = None) -> list[str]:
    """Covered files whose content differs from the version this step recorded.

    Progress marks do not count: a task checkbox, a PR or done note on that
    task line, and `(PR n)` or a trailing merged word on a Match Branch line.
    Line endings do not count.     When Spec body and Questions version are
    recorded, a change confined to ## Open questions reopens
    resolve-open-questions only. The other spec steps compare Spec body.
    `## Approval needed` is in neither stamp, so editing it reopens no step.
    A step with `Section stamps` (1.148.0) reopens only when a changed
    section names this step. Match, In the code, a Synced at line, and an
    already-answered question do not. A requirement section reopens
    tighten-spec and the plan steps, not resolve, unless the question ids
    changed too.
    A step recorded before that split still compares the whole-file spec.
    An older step has no Content stamp line. It still matches a progress-only
    edit, by raw bytes, by the other line ending, by one hash-undo, or by
    one compare with HEAD.
    """
    changed = []
    if step == "playbook":
        path = Path(body["playbook"])
        if not path.is_file():
            alt = find_playbook(root, body["playbook"])
            path = alt if alt is not None else path
        text, raw = _read_pair(path)
        normalized = body.get("content_stamp") == CONTENT_STAMP
        if not stamp_matches(
            body.get("playbook_version"), text, "playbook", normalized,
            raw_bytes=raw, path=path, part="file",
        ):
            changed.append("playbook")
        return changed
    # 1.176.0: each step compares against its own newest stamps. A step that
    # was recorded again after a spec edit is no longer reopened by a later
    # step's older stamps.
    effect = section_effect(root, steps or {}, own=body) if body.get("section_stamps") else None
    for token in COVERS[step]:
        if token == "spec" and effect and effect["active"]:
            if step in effect["reopen_steps"]:
                questions_only = (
                    step == "resolve-open-questions" and not effect["requirement_hit"]
                )
                if questions_only:
                    changed.append("questions")
                else:
                    changed.append("spec")
                    if step == "resolve-open-questions" and effect["question_reopen"]:
                        changed.append("questions")
            continue
        if token == "spec" and _split_ready(body):
            body_same = _piece_match(root, body, "spec", "spec_body")
            questions_same = _piece_match(root, body, "spec", "questions")
            if step in BODY_SPEC_STEPS:
                if not body_same:
                    changed.append("spec")
            elif step == "resolve-open-questions":
                if not body_same:
                    changed.append("spec")
                if not questions_same:
                    changed.append("questions")
            elif not _piece_match(root, body, "spec", "file"):
                changed.append("spec")
            continue
        if not _piece_match(root, body, token, "file"):
            changed.append(token)
    return changed


def affects_of(step: str, steps: dict) -> tuple[str, ...]:
    """Files that reopen this step. Later spec steps supersede the architecture review."""
    if step == "review-architecture":
        own = ORDER.index(step)
        for later in ORDER[own + 1:]:
            if later in steps and "spec" in AFFECTS[later]:
                return ()
    return AFFECTS[step]


def affected_drift(root: Path, step: str, body: dict, steps: dict) -> list[str]:
    """Drift that reopens the step. A file it merely recorded does not."""
    affects = set(affects_of(step, steps))
    return [token for token in hash_drift(root, step, body, steps) if token in affects]


def _restamp_body(body: dict, name: str, now: dict, tokens: set[str]) -> None:
    touched = False
    for token in COVERS[name]:
        if token == "playbook" or token not in tokens:
            continue
        body[token] = now[token]
        touched = True
    if "spec" in tokens and "spec" in COVERS[name]:
        body["spec_body"] = now["spec_body"]
        body["questions"] = now["questions"]
        if now.get("section_stamps"):
            body["section_stamps"] = now["section_stamps"]
        touched = True
    if touched:
        body["content_stamp"] = CONTENT_STAMP


def restamp_earlier(root: Path, steps: dict, step: str) -> None:
    """Bring earlier locked steps' covered versions up to the current files.

    Done and Result stay. Tokens this step does not cover stay, and the
    playbook line stays. The playbook is intake only. Recorded extras keep
    the version they saw.
    """
    now = versions(root)
    covered = set(COVERS[step])
    for earlier in ORDER[:ORDER.index(step)]:
        body = steps.get(earlier)
        if not body:
            continue
        _restamp_body(body, earlier, now, covered)
    if "spec" in covered and "resolve-open-questions" in steps and ORDER.index(step) > ORDER.index("resolve-open-questions"):
        _store_questions(root, steps["resolve-open-questions"])
        steps["resolve-open-questions"]["question_ids"] = now.get("question_ids") or "none"


def restamp_recorded(root: Path, steps: dict, tokens: set[str]) -> None:
    """An extra finished inside the walk. Update locked steps already recorded.

    Done and Result stay. Extras keep the version they saw.
    """
    now = versions(root)
    for name in ORDER:
        body = steps.get(name)
        if not body:
            continue
        _restamp_body(body, name, now, tokens)
    if "spec" in tokens and "resolve-open-questions" in steps:
        _store_questions(root, steps["resolve-open-questions"])
        steps["resolve-open-questions"]["question_ids"] = now.get("question_ids") or "none"


def refresh_versions(root: Path, step: str, body: dict) -> None:
    """Set one step's recorded versions to the files on disk. Done stays."""
    if step == "playbook":
        path = Path(body["playbook"])
        if not path.is_file():
            alt = find_playbook(root, body["playbook"])
            path = alt if alt is not None else path
        body["playbook_version"] = stamp_file(path, "playbook")
        body["content_stamp"] = CONTENT_STAMP
        return
    now = versions(root)
    for token in COVERS[step]:
        body[token] = now[token]
    if "spec" in COVERS[step]:
        body["spec_body"] = now["spec_body"]
        body["questions"] = now["questions"]
        body["section_stamps"] = now.get("section_stamps") or "none"
    if step == "resolve-open-questions":
        _store_questions(root, body)
        body["question_ids"] = now.get("question_ids") or "none"
    body["content_stamp"] = CONTENT_STAMP


def write_progress(root: Path, data: dict, slice_label: str | None = None) -> None:
    label = slice_label or data["slice"] or f"docs/specs/{root.name}/"
    if not str(label).endswith("/"):
        label = f"{label}/"
    progress_path(root).write_text(
        render(label, data["steps"], data.get("acks"), data.get("jumps"), data.get("branch_runs")),
        encoding="utf-8",
    )


def set_branch_run(root: Path, branch: str, state: str, when: str | None = None) -> dict:
    """Write or replace the one status line for a branch run (1.155.0).

    Only that line changes. Steps, acks, and jumps stay as they are.
    """
    from datetime import datetime as _dt
    state = " ".join((state or "").split()).rstrip(".")
    if not branch or not state:
        fail("branch-run", "a branch run needs --branch and --state")
    when = when or _dt.now().astimezone().replace(microsecond=0).isoformat()
    data = load(root)
    log = f"build-progress/{branch.replace('/', '--')}.md"
    run = {"branch": branch, "state": state, "when": when, "log": log}
    if parse_branch_run(branch_run_line(run)) is None:
        fail("branch-run", f"not a usable status line: {branch_run_line(run)}")
    data["branch_runs"][branch] = run
    write_progress(root, data)
    return {"ok": True, "line": branch_run_line(run), "path": str(progress_path(root))}


def branch_run_lines(root: Path | None, include_merged: bool = False) -> list[str]:
    """Status lines the ready check prints. A merged run is left out."""
    if root is None:
        return []
    path = progress_path(root)
    if not path.is_file():
        return []
    data, _err = _try_parse(path.read_text(encoding="utf-8"))
    if not data:
        return []
    out = []
    for branch in sorted(data.get("branch_runs") or {}):
        run = data["branch_runs"][branch]
        if run["state"] == "merged" and not include_merged:
            continue
        state = run["state"]
        if str(state).strip().lower() == "stopped before merge":
            # 1.176.0: say what is true, built with its PR open.
            log = Path(root) / str(run.get("log") or "")
            prs = _PROGRESS_PR.findall(log.read_text(encoding="utf-8")) if log.is_file() else []
            if prs:
                state = f"built, PR {prs[-1]} open"
        out.append(f"- {branch}: {state} (log: {run['log']})")
    return out


def cmd_branch_status(args: argparse.Namespace) -> None:
    if not args.yes:
        fail("needs-yes", "branch-status writes walk-progress.md only with --yes", 2)
    emit(set_branch_run(Path(args.root), args.branch, args.state, args.when))


def find_playbook(root: Path, recorded: str) -> Path | None:
    direct = Path(recorded)
    if direct.is_file():
        return direct
    for base in [root, *root.parents]:
        candidate = base / recorded
        if candidate.is_file():
            return candidate
        # A repo-relative docs/playbooks path is found from the repo, which is
        # the parent of docs/, not from inside the spec folder (1.120.0).
        if base.name == "docs":
            repo_candidate = base.parent / recorded
            if repo_candidate.is_file():
                return repo_candidate
            break
        if str(base) == "/":
            break
    return None


def resume(args: argparse.Namespace) -> None:
    root = Path(args.root)
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    emit(resume_payload(root, args.no_playbook))


# The one reference the next step needs (1.164.0). The walk opens only this file.
READ_FOR = {
    "playbook": "references/playbook.md",
    "review-architecture": "references/steps.md",
    "tighten-spec": "references/steps.md",
    "resolve-open-questions": "references/steps.md",
    "plan-from-spec": "references/steps.md",
    "review-and-tighten-plan": "references/steps.md",
    "tasks-ready-to-build": "references/readiness.md",
}


def read_for(step: str | None) -> str:
    """The reference file for continue_from; every step done is the ready check."""
    return READ_FOR.get(step or "", "references/readiness.md")


def resume_payload(root: Path, no_playbook: bool) -> dict:
    data = load(root)
    effect = section_effect(root, data["steps"])
    rows = []
    continue_from = None
    for step in ORDER:
        body = data["steps"].get(step)
        if body is None and step == "playbook" and no_playbook:
            row = {"id": step, "status": "skipped", "result": "skipped"}
            rows.append(row)
            continue
        if body is None:
            status = "not-started"
            row = {"id": step, "status": status}
        else:
            drift = affected_drift(root, step, body, data["steps"])
            if drift:
                status = "reopen"
                impact = " ".join(IMPACT[token] for token in drift)
                own_effect = section_effect(root, data["steps"], own=body) if body.get("section_stamps") else effect
                if own_effect["reopen_line"] and step in own_effect["reopen_steps"]:
                    impact = own_effect["reopen_line"]
                if step == "tasks-ready-to-build":
                    impact = impact + " " + RESTAMP
                row = {
                    "id": step,
                    "status": status,
                    "result": body["result"],
                    "changed": drift,
                    "impact": impact,
                }
                if step == "resolve-open-questions" and effect["changed_questions"]:
                    row["changed_questions"] = effect["changed_questions"]
            else:
                status = "keep"
                row = {"id": step, "status": status, "result": body["result"]}
        if continue_from is None and status in ("not-started", "reopen"):
            continue_from = step
        rows.append(row)
    for step in EXTRAS:
        body = data["steps"].get(step)
        if not body:
            continue
        rows.append({
            "id": step,
            "status": "keep",
            "result": body["result"],
            "extra": True,
        })
    book = data["steps"].get("playbook")
    return {
        "ok": True,
        "source_of_truth": "spec.md, plan.md, and tasks.md",
        "progress_file": PROGRESS_NAME,
        "steps": rows,
        "continue_from": continue_from,
        "read": read_for(continue_from),
        "playbook": book.get("playbook") if book else None,
        "done_stamp_warning": done_stamp_warning(data["steps"], data.get("acks")),
        "reopen_line": effect["reopen_line"],
        "changed_sections": effect["titles"],
        "reopen_steps": effect["reopen_steps"],
        "changed_questions": effect["changed_questions"],
        "restamp_only": effect["restamp_only"],
        "spec_findings": [
            {
                "id": jump["id"],
                "key": jump["key"],
                "topic": jump.get("topic") or "",
                "aliases": list(jump.get("aliases") or []),
                "result": jump["result"],
                "continue": [part for part in jump["continue"].split(", ") if part],
            }
            for jump in data.get("jumps") or []
        ],
        "branch_runs": [
            branch_run_line(data["branch_runs"][name]) for name in sorted(data.get("branch_runs") or {})
        ],
        "has_steps": bool(data["steps"]),
    }


def resolve_playbook(root: Path, given: str) -> Path:
    path = Path(given)
    if path.is_file():
        return path
    found = find_playbook(root, given)
    return found if found is not None else path


def same_playbook_path(root: Path, recorded: str, given: str, resolved: Path) -> bool:
    if recorded == given:
        return True
    if resolved.is_file():
        try:
            recorded_rel, _hashed = playbook_mod().recorded_playbook(root, resolved)
        except SystemExit:
            raise
        except Exception:
            recorded_rel = ""
        if recorded_rel == recorded:
            return True
        found = find_playbook(root, recorded)
        try:
            if found is not None and found.resolve() == resolved.resolve():
                return True
        except OSError:
            return False
    try:
        return Path(recorded).resolve() == Path(given).resolve()
    except OSError:
        return False


def playbook_status(args: argparse.Namespace) -> None:
    root = Path(args.root)
    emit(playbook_payload(root, args.playbook))


def playbook_payload(root: Path, playbook_arg: str) -> dict:
    playbook = resolve_playbook(root, playbook_arg)
    data = load(root) if root.is_dir() else {"steps": {}}
    body = data["steps"].get("playbook")
    text, raw = _read_pair(playbook)
    now = stamp_file(playbook, "playbook")
    if body is None:
        return {
            "ok": True,
            "status": "not-recorded",
            "already_applied": False,
            "offer": "show-changes",
            "note": "No progress line for this playbook. Use the apply compare. Do not treat it as already applied.",
        }
    same_path = same_playbook_path(root, body["playbook"], playbook_arg, playbook)
    same_hash = now != "missing" and stamp_matches(
        body.get("playbook_version"), text, "playbook",
        body.get("content_stamp") == CONTENT_STAMP,
        raw_bytes=raw, path=playbook, part="file",
    )
    if same_path and same_hash and body["result"] in APPLIED:
        return {
            "ok": True,
            "status": "already-applied",
            "already_applied": True,
            "offer": "skip-or-reapply",
            "result": body["result"],
            "note": (
                "Ask once, with the already-applied card, even when the file has not changed: skip (Recommended) keeps it as it is, reapply applies it again. "
                "Do not move on without that question."
            ),
        }
    if same_path and same_hash and body["result"] == "skipped":
        return {
            "ok": True,
            "status": "already-skipped",
            "already_applied": False,
            "offer": "skip-or-apply",
            "result": body["result"],
        }
    return {
        "ok": True,
        "status": "changed" if same_path else "different-file",
        "already_applied": False,
        "offer": "show-changes",
        "result": body.get("result"),
    }


def resolve_mod():
    return _load_script("crav1-tasks-ready-to-build", "resolve_spec.py", "resolve-spec")


def _specs_roots() -> list[Path]:
    found: list[Path] = []
    cwd = Path.cwd()
    for base in [cwd, *cwd.parents]:
        candidate = base / "docs" / "specs"
        if candidate.is_dir():
            found.append(candidate)
            break
        if str(base) == base.anchor:
            break
    return found


def resolve_start(raw: str) -> dict:
    """A spec folder, or a slug the way resolve_spec.py matches one."""
    text = (raw or "").strip()
    if not text:
        return {
            "ok": False,
            "code": "none",
            "matches": [],
            "nearest": [],
            "query": text,
            "message": "Pass --root with a spec folder or a slug.",
        }
    path = Path(text)
    if path.is_dir() and (path / "spec.md").is_file() and path.name not in ("_template", "retired"):
        return {
            "ok": True,
            "code": "folder",
            "slug": path.name,
            "folder": str(path),
            "how": "folder",
            "matches": [{"slug": path.name, "how": "folder"}],
        }
    if path.is_dir():
        return {
            "ok": False,
            "code": "root",
            "matches": [],
            "query": text,
            "message": f"{path} is not a spec folder. Pass a slug or docs/specs/<slug>.",
        }
    roots = _specs_roots()
    if not roots:
        return {
            "ok": False,
            "code": "none",
            "matches": [],
            "nearest": [],
            "query": text,
            "message": "No specs folder at docs/specs. From the repo root pass --root docs/specs/<slug>.",
        }
    last = None
    for specs in roots:
        result = resolve_mod().resolve(str(specs), text)
        last = result
        if result.get("ok") or result.get("code") == "several":
            return result
    return last or {
        "ok": False,
        "code": "none",
        "matches": [],
        "nearest": [],
        "query": text,
    }


def start(args: argparse.Namespace) -> None:
    """Resume and playbook status in one call. --root is a folder or a slug."""
    found = resolve_start(args.root)
    if not found.get("ok"):
        emit(found)
        raise SystemExit(2)
    folder = Path(found["folder"])
    if not folder.is_dir():
        fail("root", f"not a folder: {folder}")
    sync = preflight_sync(folder, skip=getattr(args, "skip_sync", False))
    if sync.get("stop"):
        emit({
            "ok": True,
            "stop": True,
            "sync": sync,
            "slug": found.get("slug") or folder.name,
            "folder": str(folder),
            "ending": sync.get("ending"),
            "line": sync.get("line"),
        })
        return
    # 1.197.0: when the spec was found by its playbook name, use that playbook (no second start run).
    playbook_arg = args.playbook or (_resolved_playbook(folder, args.root) if "playbook" in str(found.get("how") or "") else None)
    payload = {
        "ok": True,
        "slug": found.get("slug") or folder.name,
        "folder": str(folder),
        "how": found.get("how") or "folder",
        "sync": sync,
        "resume": resume_payload(folder, no_playbook=not playbook_arg),
        "playbook_status": None,
    }
    kit = _kit_update(folder)
    if kit:
        payload["kit_update"] = kit["line"]
        payload["kit_update_run"] = kit["run"]
    if playbook_arg:
        payload["playbook"] = playbook_arg
        payload["playbook_status"] = playbook_payload(folder, playbook_arg)
    emit(payload)


def _kit_update(folder: Path) -> dict | None:
    """1.198.0: `Kit update available: <installed> -> <latest>`, read-only, silent when offline."""
    try:
        top = _git_out(folder, "rev-parse", "--show-toplevel")
        mod = _load_script("crav1-update-kit", "update_kit.py", "walk_update_kit")
        return mod.update_available(Path(top.strip()) if top else folder)
    except Exception:  # noqa: BLE001 - never stop the walk for this line
        return None


def _resolved_playbook(folder: Path, query: str) -> str | None:
    """The playbook path the spec names whose file name matched the start query."""
    spec = folder / "spec.md"
    if not spec.is_file():
        return None
    mod = resolve_mod()
    raws = [m.group(1).strip().strip("`").strip() for m in mod.PLAYBOOK.finditer(spec.read_text(encoding="utf-8"))]
    raws = [r for r in raws if r]
    want = mod.norm(Path(str(query)).name)
    hits = [r for r in raws if mod.norm(Path(r.replace("\\", "/")).stem) == want]
    if len(hits) == 1:
        return hits[0]
    return raws[0] if len(raws) == 1 else None


def _load_script(folder: str, filename: str, code: str):
    import importlib.util

    path = Path(__file__).resolve().parents[2] / folder / "scripts" / filename
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    if spec is None or spec.loader is None:
        fail(code, f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def blocks_mod():
    return _load_script("crav1-tasks-ready-to-build", "question_blocks.py", "blocks")


def approval_mod():
    return _load_script("crav1-record-approval", "approval_needed.py", "approval")


def claims_mod():
    return _load_script("crav1-build-walk", "claims.py", "claims")


def sync_mod():
    return _load_script("crav1-build-walk", "repo_sync.py", "sync")


def unlinked(args: argparse.Namespace) -> None:
    """Kept-open questions that still have no Blocks line. Writes nothing."""
    root = Path(args.root)
    spec = root / "spec.md"
    if not spec.is_file():
        fail("spec", f"no spec.md in {root}")
    questions = blocks_mod().kept_open(spec.read_text(encoding="utf-8"))
    missing = [{"text": q["text"]} for q in questions if q["mark"] == "missing"]
    emit({"ok": True, "count": len(missing), "questions": missing})


_OWN_PUSHED = re.compile(
    r"\bpushed\b.*\bwaits? (?:for|on) (?:its|the) (?:merge|pull request|pr)\b"
    r"|\bwaits? (?:for|on) (?:its|the) (?:pull request'?s? |pr'?s? )?merge\b", re.I)


def classify(row: dict, resolve_kept: bool = False, resolve_recorded: bool = False) -> dict | None:
    bucket = str(row.get("bucket") or "")
    reason = str(row.get("reason") or "")
    warning = str(row.get("warning") or "")
    text = f"{reason} {warning}".lower()
    task = row.get("task")
    if bucket == "needs-verify" and "verify failed" in text:
        # A failed verify is fixed, not verified again (1.169.0).
        return {
            "task": task,
            "bucket": "needs-verify",
            "step": None,
            "command": "/crav1-fix-build-gaps",
            "can_jump_back": False,
            "outside_walk": True,
            "kind": "blocker",
            "failed": True,
            "why": f"{task or 'A task'} failed verify. /crav1-fix-build-gaps fixes it, outside this walk. Do not start it. Do not report ready.",
        }
    if bucket == "needs-verify" or "needs verify" in text or "no verify.md" in text:
        return {
            "task": task,
            "bucket": "needs-verify",
            "step": None,
            "command": "/crav1-verify-build-against-spec",
            "can_jump_back": False,
            "outside_walk": True,
            "kind": "blocker",
            "why": "Needs verify belongs to /crav1-verify-build-against-spec, which is outside this walk. Do not start it. Do not report ready.",
        }
    # Blocks: none blocks no task, and that line wins over Risk wording (1.125.0).
    if "blocks: none" in text or "blocks no task" in text or "blocks no current" in text:
        return None
    if "plan review unknown" in text:
        return _hit(task, "assumption", "review-plan", "The ready check assumed a plan review. Run /crav1-review-plan, then /crav1-tighten-plan.")
    if "p# open" in text or "open p#" in text:
        return _hit(task, "assumption", "tighten-plan", "The plan review still has open P# items. Run /crav1-tighten-plan.")
    if bucket != "done" and (row.get("own_pr_open") or (row.get("own_claim") and _OWN_PUSHED.search(text))):
        # 1.199.0: your own task, pushed and waiting for its pull request to
        # merge, is waiting, never an unrecognized blocker.
        hit = _waiting(row)
        hit["merge"] = True
        hit["own"] = True
        hit["step"] = None
        hit["who"] = None
        pr = row.get("own_pr_open")
        hit["pr"] = pr
        wait = f"waits for PR {pr}'s merge" if pr else "waits for its pull request to merge"
        hit["why"] = f"{task or 'The task'} is yours and {wait}. It is not offered in Run next."
        return hit
    if bucket == "waits-in-order":
        return None
    if bucket in ("ready", "done") and not warning:
        return None
    if bucket == "ready" and warning:
        return _hit(task, "assumption", None, f"Unrecognized ready warning: {warning}")
    if "no tasks" in text:
        return _hit(task, "blocker", "plan-from-spec", "There is no tasks.md. Run /crav1-plan-from-spec.")
    if "no plan" in text:
        return _hit(task, "blocker", "plan-from-spec", "There is no plan.md. Run /crav1-plan-from-spec.")
    if row.get("loop") or text.startswith("in a loop"):
        # A branch in a loop is blocked in the map and here (1.154.0). Other
        # tasks can still start, so this hit alone does not force not-ready.
        hit = _hit(task, "blocker", "tighten-plan", LOOP_WHY)
        hit["loop"] = True
        return hit
    if row.get("deadlock"):
        # 1.180.0 (M4): a task that waits on its own PR's merge is Blocked.
        hit = _hit(task, "blocker", "tighten-plan", row["deadlock"] + " Fix the order with /crav1-tighten-plan.")
        hit["deadlock"] = True
        return hit
    if row.get("merge_wait"):
        hit = _waiting(row)
        hit["merge"] = True
        hit["step"] = None
        hit["who"] = None
        hit["why"] = f"{task or 'The task'} is pushed and {merge_wait_phrase(row['merge_wait'])}. It is not offered in Run next."
        return hit
    if row.get("release_gate"):
        hit = _waiting(row)
        hit["release"] = True
        hit["step"] = None
        hit["who"] = None
        hit["why"] = f"{task or 'The task'} {row['release_gate']}. It is not offered in Run next."
        return hit
    if row.get("approval") or "approval needed" in text:
        return _waiting(row)
    if "open question" in text:
        # A Blocks line, a question already recorded as waiting, or a hold
        # inferred from the question text stays waiting through spec drift.
        # A new or unparsed question jumps back only for the tasks it holds.
        if _question_stays(row, resolve_kept, resolve_recorded):
            return _waiting(row)
        return _hit(task, "blocker", "resolve-open-questions", "An open question blocks the work. Run /crav1-resolve-open-questions.")
    if "plan risk" in text:
        return _hit(task, "blocker", "tighten-plan", "A plan risk blocks the work. Run /crav1-review-plan, then /crav1-tighten-plan.")
    # A task that depends on a held task is held too, even with no question
    # of its own (1.132.0). That is waiting, not a jump back.
    if "in progress by" in text:
        return _waiting(row)
    # Built by someone, waits for the PR to merge, is waiting (1.180.0, M5).
    if row.get("claim_built") or task_state_mod().is_waiting_reason(text):
        return _waiting(row)
    if "held, waits on" in text:
        return _waiting(row)
    # A cycle, or an after: that names no task, is a blocker. Waiting on a
    # real earlier task is the order, not a blocker (1.126.0).
    if "cycle" in text or "names no task" in text:
        return _hit(task, "blocker", "tighten-plan", "A task dependency is blocked. Fix the (after:) marks with /crav1-tighten-plan.")
    if re.search(r"waits on\s+t\d+", text):
        return None
    return _hit(task, "blocker", None, f"Unrecognized blocker: {reason or bucket}")


def _question_stays(row: dict, resolve_kept: bool, resolve_recorded: bool = False) -> bool:
    """True when this question stays Waiting instead of jumping back.

    Before resolve-open-questions is recorded, an open question is still a
    jump back. After that record, a Blocks line, a question already recorded
    as waiting, or a hold inferred from the text stays Waiting through drift.
    """
    if resolve_kept:
        return True
    if not resolve_recorded:
        return False
    if row.get("kept") or row.get("inferred_text"):
        return True
    reason = (row.get("reason") or "").lower()
    if "(recorded)" in reason or "inferred from the text" in reason:
        return True
    return False


def _waiting(row: dict) -> dict:
    who = row.get("who")
    if isinstance(who, str):
        who = who.strip() or None
    else:
        who = None
    if not who:
        who = NOT_NAMED
    approval = bool(row.get("approval"))
    if approval:
        why = (
            "An Approval needed item holds this task until a matching Approved line is recorded. "
            "Do not jump back to resolve-open-questions."
        )
        step = None
    else:
        why = (
            "Resolve-open-questions already covers this spec. "
            "The question waits on someone else. Do not jump back."
        )
        step = "resolve-open-questions"
    return {
        "task": row.get("task"),
        "bucket": "waiting",
        "step": step,
        "command": None,
        "can_jump_back": False,
        "outside_walk": False,
        "kind": "waiting",
        "who": who,
        "asked": bool(row.get("asked")),
        "approval": approval,
        "reason": row.get("reason"),
        "why": why,
    }


def _hit(task, kind: str, command_key: str | None, why: str) -> dict:
    if command_key is None:
        return {
            "task": task,
            "bucket": kind,
            "step": None,
            "command": None,
            "can_jump_back": False,
            "outside_walk": False,
            "kind": kind,
            "why": why.rstrip().rstrip(".") + ". The walk does not invent a step for this.",
        }
    step = "review-and-tighten-plan" if command_key in ("review-plan", "tighten-plan") else command_key
    return {
        "task": task,
        "bucket": kind,
        "step": step,
        "command": JUMP[command_key],
        "can_jump_back": True,
        "outside_walk": False,
        "kind": kind,
        "why": why,
    }


def cover(args: argparse.Namespace) -> None:
    """Count the current spec, plan, tasks, and verify as part of the walk.

    Optional. For a write made outside this walk. An extra the walk itself
    just ran is recorded with `- Extra:` instead. The playbook line stays.
    Cover does not add an extra line.
    """
    if not args.yes:
        fail("needs-yes", "cover writes the progress file only with --yes", status=2)
    root = Path(args.root)
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    data = load(root)
    if not data["steps"]:
        fail("progress-file", "no walk progress to cover")
    now = versions(root)
    covered = []
    for step, body in data["steps"].items():
        if step == "playbook":
            continue
        for token in COVERS[step]:
            body[token] = now[token]
        if "spec" in COVERS[step]:
            body["spec_body"] = now["spec_body"]
            body["questions"] = now["questions"]
            body["section_stamps"] = now.get("section_stamps") or "none"
        if step == "resolve-open-questions":
            _store_questions(root, body)
            body["question_ids"] = now.get("question_ids") or "none"
        body["content_stamp"] = CONTENT_STAMP
        covered.append(step)
    write_progress(root, data)
    emit({"ok": True, "wrote": PROGRESS_NAME, "covered": covered})


def clear(args: argparse.Namespace) -> None:
    """Refresh one reopened step after a one-line 'nothing new' confirmation.

    Done and Result stay. Other steps stay as they are.
    """
    if args.step not in COVERS:
        fail("step", f"unknown step {args.step}")
    if not args.yes:
        fail("needs-yes", "clear writes the progress file only with --yes", status=2)
    root = Path(args.root)
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    data = load(root)
    body = data["steps"].get(args.step)
    if body is None:
        fail("step", f"{args.step} is not recorded")
    drift = affected_drift(root, args.step, body, data["steps"])
    if not drift:
        fail("not-reopened", f"{args.step} is not reopened")
    refresh_versions(root, args.step, body)
    still = affected_drift(root, args.step, body, data["steps"])
    if still:
        # 1.176.0: never report a clear that did not clear.
        fail(
            "still-reopened",
            f"{args.step} still reads reopened after the refresh ({', '.join(still)}); "
            f"run {STEP_COMMAND.get(args.step, args.step)} again instead",
        )
    write_progress(root, data)
    emit({
        "ok": True,
        "wrote": PROGRESS_NAME,
        "cleared": args.step,
        "confirmation": "nothing new",
        "changed": drift,
    })


# Plain names for the clear-or-rerun card (1.164.0): no step ids, stamps, or commands.
STEP_PLAIN = {
    "playbook": "the playbook",
    "review-architecture": "the architecture review",
    "tighten-spec": "the spec tightening",
    "resolve-open-questions": "the open questions",
    "plan-from-spec": "the plan",
    "review-and-tighten-plan": "the plan review",
    "tasks-ready-to-build": "the ready check",
}
CHANGE_PLAIN = {
    "spec": "the spec changed",
    "plan": "the plan changed",
    "tasks": "the tasks changed",
    "verify": "verify.md changed",
    "playbook": "the playbook file changed",
    "questions": "the open questions changed",
}


def reopen_card(step: str, drift: list[str], recommend_rerun: bool, stale_seen: bool = False) -> dict:
    """The clear-or-rerun card for one reopened step, in plain words (1.164.0).

    `rerun` jumps back to the step's skill; `nothing new` runs clear --yes.
    1.195.0: when the walk saw anything stale (code drift, a merge since sync,
    a stale research mark), rerun is recommended, never `nothing new`.
    """
    name = STEP_PLAIN.get(step, "this step")
    changes = [CHANGE_PLAIN[token] for token in drift if token in CHANGE_PLAIN] or ["a file changed"]
    said = changes[0] if len(changes) == 1 else ", ".join(changes[:-1]) + " and " + changes[-1]
    rerun = {
        "id": "rerun",
        "label": f"Redo {name}",
        "text": f"Run {name} again on the current files, then the walk goes on.",
    }
    skip = {
        "id": "nothing new",
        "label": f"Skip redoing {name}",
        "text": f"Keep {name} as done and go straight on, because the change does not affect it.",
    }
    if recommend_rerun or stale_seen:
        rerun["label"] += " (Recommended)"
        rerun["text"] += (" Why: this walk saw something stale, so the step may be out of date."
                          if stale_seen and not recommend_rerun else " Why: the change can affect it.")
        options = [rerun, skip]
    else:
        skip["label"] += " (Recommended)"
        skip["text"] += " Why: only the files around it changed."
        options = [skip, rerun]
    return {
        "step": step,
        "background": f"{name[:1].upper()}{name[1:]} reopened because {said}.",
        "question": f"Skip redoing {name}?",
        "options": options,
        "result": (f"On yes: {name} runs again on the current files." if options[0]["id"] == "rerun"
                   else f"On yes: {name} stays done and the walk goes on."),
    }


CHANGED_FILE = {
    "spec": "the spec",
    "plan": "plan.md",
    "tasks": "tasks.md",
    "questions": "the open questions in the spec",
    "playbook": "the playbook",
    "verify": "verify.md",
}


def _and_list(items: list[str]) -> str:
    items = [item for item in items if item]
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def reopen_titles(step: str, slugs: list[str], titles: list[str]) -> list[str]:
    """Only sections that can reopen `step` are named (1.180.0, S1).

    Match and In the code own no steps, so they never reopen tighten-spec
    and are not named in its reason. With no slugs (Synced at only) the
    titles stay as they are.
    """
    if not slugs:
        return titles
    return [section_title(slug) for slug in slugs if step in SECTION_STEPS.get(slug, (step,))]


def reopen_reason(step: str, drift: list[str], titles: list[str] | None = None) -> str:
    """Why a step reopened, in one plain sentence (1.175.0).

    Names the changed spec sections when the section stamps say which, else
    the changed files. A build walk's own files (claims.md, walk-progress.md,
    build-progress, verify.md, task ticks) never reopen a step, so the
    sentence always names a real edit.
    """
    command = STEP_COMMAND.get(step, f"/crav1-{step}")
    real = [title for title in titles or [] if title and title != "Synced at"]
    if real and "spec" in drift:
        noun = "section" if len(real) == 1 else "sections"
        what = f"The spec's {_and_list(real)} {noun} changed"
        others = [CHANGED_FILE[token] for token in drift if token not in ("spec", "questions") and token in CHANGED_FILE]
        if others:
            what += f", and so did {_and_list(others)}"
    else:
        files = [CHANGED_FILE.get(token, token) for token in drift] or ["a covered file"]
        what = f"{_and_list(files)[:1].upper()}{_and_list(files)[1:]} changed"
    return f"{what} after {command} was last recorded in walk-progress.md."


def reopen_hit(step: str, drift: list[str]) -> dict:
    why = " ".join(IMPACT[token] for token in drift)
    why += " Jump back and rerun this step, or clear it with nothing new."
    if step == "tasks-ready-to-build":
        why += " " + RESTAMP
    return {
        "task": None,
        "bucket": "reopened",
        "step": step,
        "command": STEP_COMMAND[step],
        "can_jump_back": True,
        "outside_walk": False,
        "kind": "blocker",
        "clear": "nothing new",
        "changed": drift,
        "why": why,
    }


def reopened_hits(root: Path) -> list[dict]:
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    data = load(root)
    hits = []
    titles = None
    for step in ORDER:
        body = data["steps"].get(step)
        if not body:
            continue
        drift = affected_drift(root, step, body, data["steps"])
        if drift:
            hit = reopen_hit(step, drift)
            try:
                effect = section_effect(root, data["steps"], own=body)
                titles = list(effect.get("titles") or []) if effect.get("active") else []
                titles = reopen_titles(step, effect.get("changed_slugs") or [], titles)
            except Exception:  # noqa: BLE001 - the reason is words only
                titles = []
            hit["reason"] = reopen_reason(step, drift, titles)
            hits.append(hit)
    return hits


def order_mod():
    import importlib.util

    path = Path(__file__).resolve().parents[2] / "crav1-tasks-ready-to-build" / "scripts" / "task_order.py"
    spec = importlib.util.spec_from_file_location("task_order_rows", path)
    if spec is None or spec.loader is None:
        fail("order", f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def map_mod():
    import importlib.util

    path = Path(__file__).resolve().parents[2] / "crav1-tasks-ready-to-build" / "scripts" / "build_map.py"
    spec = importlib.util.spec_from_file_location("build_map_rows", path)
    if spec is None or spec.loader is None:
        fail("map", f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_ENDING_MOD: list = []


def ending_mod():
    """The shared walk ending (1.156.0), skill crav1-tasks-ready-to-build scripts/walk_ending.py."""
    if not _ENDING_MOD:
        import importlib.util

        path = Path(__file__).resolve().parents[2] / "crav1-tasks-ready-to-build" / "scripts" / "walk_ending.py"
        spec = importlib.util.spec_from_file_location("walk_ending_wp", path)
        if spec is None or spec.loader is None:
            fail("ending", f"cannot load {path}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _ENDING_MOD.append(mod)
    return _ENDING_MOD[0]


_MAP_CACHE: dict = {}


def map_built(root: Path) -> dict | None:
    """The same build the map writes, shared by the ready check (1.154.0).

    The rows, the held lines, and build-map.md all read this one judgement,
    so a branch in a loop is blocked in each of them. Missing files return
    None.
    """
    if root is None or not root.is_dir():
        return None
    tasks_path = root / "tasks.md"
    if not tasks_path.is_file():
        return None
    plan_path = root / "plan.md"
    spec_path = root / "spec.md"
    verify_path = root / "verify.md"
    work_path = root / "work-item.md"
    tasks = tasks_path.read_text(encoding="utf-8")
    spec = spec_path.read_text(encoding="utf-8") if spec_path.is_file() else ""
    plan = plan_path.read_text(encoding="utf-8") if plan_path.is_file() else None
    work = work_path.read_text(encoding="utf-8") if work_path.is_file() else ""
    verify = verify_path.read_text(encoding="utf-8") if verify_path.is_file() else ""
    recorded = resolve_ever_recorded(root)
    key = (str(root.resolve()), tasks, spec, plan, work, verify, recorded)
    cached = _MAP_CACHE.get(key)
    if cached is not None:
        return cached
    mod = map_mod()
    built = mod.build(
        root.name,
        spec,
        plan,
        tasks,
        work,
        verify,
        resolve_recorded=recorded,
        repo=mod.find_repo(root),
    )
    _MAP_CACHE.clear()
    _MAP_CACHE[key] = built
    return built


def branch_report(root: Path, rows: list[dict]) -> dict | None:
    """Ready and held tasks grouped by the build-map row (1.133.0).

    The branch is the one `build_map.py --recommend` prints. Missing files
    leave the report empty so the caller keeps the older line.
    """
    built = map_built(root)
    if built is None:
        return None
    return map_mod().report_by_branch(built, rows, slug=command_slug(root))


LOOP_WHY = "Two or more branches wait for each other. The ready check offers a fix under the Loop line; say `fix-loop` to apply it."


def loop_offer(root: Path | None) -> dict:
    """The fix offer for the first loop (1.161.0): a Run next entry, the card, every fix.

    The fix numbers run across all loops, so `fix-loop 3` always names the
    same fix the Loop lines print.
    """
    empty = {"entries": [], "card": None, "fixes": []}
    if root is None:
        return empty
    try:
        built = map_built(root)
    except Exception:  # noqa: BLE001 - a map failure must not hide the rows
        return empty
    loops = (built or {}).get("loops") or []
    if not loops:
        return empty
    fixes = [fix for row in loops for fix in row.get("fixes") or []]
    first = (loops[0].get("fixes") or [None])[0]
    entries = []
    if first:
        slug = command_slug(root)
        words = " ".join(bit for bit in (slug, first["word"]) if bit)
        # Label above the command (1.174.0), like every other Run next entry.
        entries.append(_run_entry(f"/crav1-tasks-ready-to-build {words}", str(first["summary"])))
    return {"entries": entries, "card": loops[0].get("card"), "fixes": fixes}


def fix_loop_cmd(args: argparse.Namespace) -> None:
    """Apply one loop fix after a yes (1.161.0). Without --yes this writes nothing."""
    root = Path(args.root)
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    out, code = map_mod().fix_loop(root, pick=args.pick, yes=args.yes)
    _MAP_CACHE.clear()
    if code == 0 and out.get("wrote"):
        command = " ".join(bit for bit in ("/crav1-tasks-ready-to-build", command_slug(root)) if bit)
        out["reply"] = out["line"] + "\n\nRun next:\n\n" + "Rerun the ready check with the fix in place:\n" + f"`{command}`"
    else:
        out["reply"] = out.get("line") or "\n".join(bit for bit in (out.get("change"), out.get("message")) if bit)
    if getattr(args, "text", False):
        print(out["reply"])
        if code:
            raise SystemExit(code)
        return
    emit(out)
    if code:
        raise SystemExit(code)


def apply_loop_holds(root: Path | None, rows: list[dict]) -> list[str]:
    """Block the open tasks on a branch caught in a loop (1.154.0).

    The judgement is the map's own, so the ready check and build-map.md
    agree. Done and Needs verify rows keep their state. Tasks on other
    branches keep theirs too: ready, waiting on a question, or waits in
    order. Returns the plain Loop lines for the ending.
    """
    if root is None:
        return []
    try:
        built = map_built(root)
    except Exception:  # noqa: BLE001 - a map failure must not hide the rows
        return []
    if not built:
        return []
    holds = map_mod().loop_holds(built)
    for row in rows:
        num = re.fullmatch(r"T(\d+)", str(row.get("task") or ""))
        if not num or int(num.group(1)) not in holds:
            continue
        if row.get("bucket") in ("done", "needs-verify"):
            continue
        row["bucket"] = "blocked"
        row["loop"] = True
        row["reason"] = "in a loop: " + holds[int(num.group(1))]
    return list(built.get("loop_lines") or [])


REVIEWED_RE = re.compile(r"^Reviewed:\s*.*?P# open:\s*(\d+)", re.M)


def reviewed_warning(plan_text: str) -> str | None:
    if not plan_text.strip():
        return "plan review unknown (inferred), run /crav1-review-plan"
    match = REVIEWED_RE.search(plan_text)
    if not match:
        return "plan review unknown (inferred), run /crav1-review-plan"
    count = int(match.group(1))
    if count > 0:
        return f"plan review has {count} open P# (recorded), see /crav1-tighten-plan"
    return None


def _pr_merged(text: str) -> bool:
    """A pull request recorded on this line is merged. Local text only."""
    return bool(re.search(r"\(PR\s+\d+", text or "", re.I) and re.search(r"\bmerged\b", text or "", re.I))


def _merged_branches(spec_text: str) -> set[str]:
    names: set[str] = set()
    mod = map_mod()
    for line in (spec_text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            stripped = stripped[2:].strip()
        if not stripped.lower().startswith("branch:"):
            continue
        if not _pr_merged(stripped):
            continue
        body = stripped.split(":", 1)[1]
        cleaned = re.sub(r"\([^)]*\)", " ", body)
        cleaned = re.sub(r"\bmerged\b", " ", cleaned, flags=re.I)
        token = mod.branch_token(cleaned)
        if token:
            names.add(token)
    return names


def _task_merged(rest: str, branches: set[str]) -> bool:
    if _pr_merged(rest):
        return True
    mod = map_mod()
    for mark in re.finditer(r"\((?:branch|map):\s*([^)]+)\)", rest or "", re.I):
        token = mod.branch_token(mark.group(1))
        if token and token in branches:
            return True
    return False


def _task_rests(text: str) -> dict[int, str]:
    rests = {}
    for line in (text or "").splitlines():
        match = order_mod().TASK.match(line)
        if match:
            rests[int(match.group(2))] = match.group(3)
    return rests


def _overview_status(text: str | None, tid: str) -> str | None:
    """Status cell on the verify tasks table, or None when that row is absent."""
    if not text:
        return None
    in_tasks = False
    for line in text.splitlines():
        if line.startswith("## Tasks"):
            in_tasks = True
            continue
        if in_tasks and line.startswith("## "):
            break
        if not in_tasks or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] == tid and len(cells) >= 3 and cells[2] not in ("Status", "---"):
            return cells[2]
    return None


def _not_implemented(status: str | None) -> bool:
    return bool(status) and "not implemented" in status.lower()


def _tldr_not_implemented(text: str | None, tid: str) -> bool:
    if not text:
        return False
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or cells[0].lower() != "not implemented":
            continue
        blob = " ".join(cells[1:])
        if re.search(rf"\b{re.escape(tid)}\b", blob):
            return True
    return False


def _listed_not_implemented(text: str | None, tid: str) -> bool:
    status = _overview_status(text, tid)
    if status is not None:
        return _not_implemented(status)
    return _tldr_not_implemented(text, tid)


def _built_ids(tasks_text: str, spec_text: str) -> dict[str, dict]:
    """Tasks that are ticked, or whose pull request is recorded merged."""
    branches = _merged_branches(spec_text)
    rests = _task_rests(tasks_text)
    built = {}
    for task in order_mod().parse(tasks_text):
        tid = f"T{task['id']}"
        rest = rests.get(task["id"], "")
        merged = _task_merged(rest, branches)
        if task["done"] or merged:
            built[tid] = {"done": task["done"], "merged": merged, "id": task["id"]}
    return built


def _row_status(text: str | None, tid: str) -> str | None:
    """The task's own verify.md status: the tasks table row, else any table row."""
    status = _overview_status(text, tid)
    if status is not None:
        return status
    for line in (text or "").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] == tid and len(cells) >= 3 and cells[2] not in ("Status", "---"):
            return cells[2]
    return None


def _verify_current(text: str | None, tid: str) -> bool:
    """verify.md is current for a task whose own row says Verified or Failed (1.169.0).

    Not implemented, claimed done or unverified, and no row at all are not
    current. Tick pending rows read as verified.
    """
    status = (_row_status(text, tid) or "").lower()
    if not status or "not implemented" in status:
        return False
    if "unverified" in status or "claimed" in status:
        return False
    return "verified" in status or "failed" in status


def _verify_failed(text: str | None, tid: str) -> bool:
    status = (_row_status(text, tid) or "").lower()
    return "failed" in status and "not implemented" not in status


def _failed_reason(text: str | None, tid: str) -> str:
    """The Verify cell of a failed row, as a short reason, or ""."""
    in_tasks = False
    for line in (text or "").splitlines():
        if line.startswith("## Tasks"):
            in_tasks = True
            continue
        if in_tasks and line.startswith("## "):
            break
        if not in_tasks or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] == tid and len(cells) >= 4:
            reason = cells[3].strip()
            if reason and reason not in ("—", "-", "fail", "failed"):
                return reason
    return ""


def _stale_next(verify_text: str, ticked: set[str]) -> str | None:
    """A Next line is stale only for a ticked task whose row is not current.

    1.136.0 flagged every ticked task the line named. Right after a fresh
    verify that line names the tasks verify just checked, so a Verified or
    Failed row now means verify is current (1.169.0). Verify no longer
    writes a Next line; older files that have one still read.
    """
    hits = []
    for line in (verify_text or "").splitlines():
        stripped = line.strip()
        if not stripped.lower().startswith("next:"):
            continue
        named = re.findall(r"\bT\d+\b", stripped)
        if any(tid in ticked and not _verify_current(verify_text, tid) for tid in named):
            hits.append(stripped)
    return " ".join(hits) if hits else None


def _orphan_verify_ids(verify_text: str, task_ids: set[str]) -> list[str]:
    """T# rows in the verify.md tasks table that do not exist in tasks.md."""
    found: list[str] = []
    in_tasks = False
    for line in (verify_text or "").splitlines():
        if line.startswith("## Tasks"):
            in_tasks = True
            continue
        if in_tasks and line.startswith("## "):
            break
        if not in_tasks or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or not re.fullmatch(r"T\d+", cells[0]):
            continue
        if len(cells) < 3 or cells[2] in ("Status", "---"):
            continue
        tid = cells[0]
        if tid not in task_ids and tid not in found:
            found.append(tid)
    return found


def verify_gap_from(tasks_text: str, spec_text: str, verify_text: str, slug: str) -> dict:
    """verify.md is behind for a ticked task, or a merged task still Not implemented.

    A Next line is stale only when it names a ticked task. A merged task that
    is still unticked, and whose verify status is not Not implemented, is not
    behind: the checkbox is the only leftover. Merged tasks stay done for
    dependents. This does not write verify.md.
    """
    empty = {
        "behind": False, "tasks": [], "waiting": None, "stale_next": None,
        "orphan_tasks": [], "orphan_waiting": None, "failed": [],
    }
    if not verify_text.strip() or not tasks_text.strip():
        return empty
    built = _built_ids(tasks_text, spec_text)
    ticked = {tid for tid, info in built.items() if info["done"]}
    stale: list[str] = []
    for tid in built:
        if _listed_not_implemented(verify_text, tid):
            stale.append(tid)
    stale_next = _stale_next(verify_text, ticked)
    if stale_next:
        for tid in re.findall(r"\bT\d+\b", stale_next):
            if tid in ticked and tid not in stale and not _verify_current(verify_text, tid):
                stale.append(tid)
    # A built task whose row says verify failed goes to fix-build-gaps (1.169.0).
    failed = [
        {"task": tid, "reason": _failed_reason(verify_text, tid)}
        for tid in sorted(built, key=lambda t: int(t[1:]))
        if tid not in stale and _verify_failed(verify_text, tid)
    ]
    task_ids = {f"T{task['id']}" for task in order_mod().parse(tasks_text)}
    orphans = _orphan_verify_ids(verify_text, task_ids)
    orphan_waiting = None
    if orphans:
        listed = ", ".join(orphans)
        orphan_waiting = (
            f"Waiting: verify.md has a row for {listed}, which is not in tasks.md. "
            "Fix it with /crav1-verify-build-against-spec, which drops that row."
        )
    if not stale and not orphans and not failed:
        return empty
    if not stale:
        return {
            "behind": False, "tasks": [], "waiting": None, "stale_next": stale_next,
            "orphan_tasks": orphans, "orphan_waiting": orphan_waiting, "failed": failed,
        }
    ordered = sorted(stale, key=lambda tid: int(tid[1:]))
    ids = ", ".join(ordered)
    waiting = (
        f"Waiting: /crav1-verify-build-against-spec {slug} - "
        f"verify.md is behind tasks.md ({ids})"
    )
    return {
        "behind": True, "tasks": ordered, "waiting": waiting, "stale_next": stale_next,
        "orphan_tasks": orphans, "orphan_waiting": orphan_waiting, "failed": failed,
    }


def verify_gap(root: Path) -> dict:
    empty = {
        "behind": False, "tasks": [], "waiting": None, "stale_next": None,
        "orphan_tasks": [], "orphan_waiting": None,
    }
    if root is None or not root.is_dir():
        return empty
    verify_path = root / "verify.md"
    tasks_path = root / "tasks.md"
    if not verify_path.is_file() or not tasks_path.is_file():
        return empty
    spec_path = root / "spec.md"
    spec_text = spec_path.read_text(encoding="utf-8") if spec_path.is_file() else ""
    return verify_gap_from(
        tasks_path.read_text(encoding="utf-8"),
        spec_text,
        verify_path.read_text(encoding="utf-8"),
        _slug(root),
    )


def _verify_for(text: str | None, tid: str) -> tuple[str, str | None]:
    if not text:
        return "needs-verify", "no verify.md row"
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or cells[0] != tid or len(cells) < 3:
            continue
        status = cells[2].lower()
        if "verified on branch" in status:
            return "needs-verify", "verified on a branch that is not merged"
        if "unverified" in status or "claimed" in status:
            return "needs-verify", "claimed done, unverified"
        if "failed" in status:
            return "needs-verify", "verify failed"
        if "verified" in status:
            return "done", None
        return "needs-verify", "no verify.md row"
    for line in text.splitlines():
        if not re.search(rf"\b{re.escape(tid)}\b", line):
            continue
        low = line.lower()
        if "unverified" in low or "claimed done" in low:
            return "needs-verify", "claimed done, unverified"
        if "verify failed" in low:
            return "needs-verify", "verify failed"
        if "implemented, verified" in low:
            return "done", None
    return "needs-verify", "no verify.md row"


def _question_alias(question: dict, kept: set[str], stored: list[dict], excluded: set[str], task_ids) -> tuple[bool, dict | None]:
    """Whether this question is one already kept, and a note when the words moved.

    Exact key: kept, no note. Stable key: a refreshed commit list. One close
    wording: the same question. Two close wordings are not merged. Blocks
    tasks that name different T# ids are not the same question.
    """
    key = question.get("key") or ""
    stable = question.get("stable_key") or ""
    if key and key in excluded:
        return False, None
    if key and key in kept:
        return True, None
    text = question.get("text") or ""
    if stable and stable in kept:
        matched = next(
            (row for row in stored if row.get("stable") == stable or row.get("key") == stable),
            None,
        )
        return True, {
            "how": "stable",
            "key": key,
            "text": text,
            "matched": (matched or {}).get("text") or "",
            "similarity": 1.0,
        }
    hits = []
    current_tasks = set(question.get("tasks") or [])
    for row in stored:
        if row.get("key") in excluded:
            continue
        sim = blocks_mod().question_similarity(text, row.get("text") or "")
        if sim < FINDING_CLOSE:
            continue
        named = set(blocks_mod()._text_tasks(row.get("text") or "", task_ids))
        if current_tasks and named and current_tasks.isdisjoint(named):
            continue
        hits.append((sim, row))
    if len(hits) != 1:
        return False, None
    sim, row = hits[0]
    return True, {
        "how": "similar",
        "key": key,
        "text": text,
        "matched": row.get("text") or "",
        "similarity": round(sim, 3),
    }


def _oq_row(tid: str, question: dict, whole: bool, kept: set[str], alias_kept: set[str] | None = None) -> dict:
    sentence = str(question.get("text") or "").strip()
    if question.get("mark") == "inferred":
        reason = f'open question "{sentence}" (inferred from the text)'
    elif question.get("mark") == "whole":
        reason = f'open question "{sentence}" blocks the whole slice (recorded)'
    elif whole:
        reason = f'open question "{sentence}" blocks the whole slice (inferred)'
    else:
        reason = f'open question "{sentence}" (recorded)'
    row = {
        "bucket": "blocked",
        "task": tid,
        "reason": reason,
        "asked": bool(question.get("asked")),
        "kept": bool(question.get("recorded")) or question.get("key") in kept or question.get("key") in (alias_kept or set()),
        "inferred_text": question.get("mark") == "inferred",
    }
    if question.get("who"):
        row["who"] = question["who"]
    if question.get("quote"):
        row["quote"] = question["quote"]
    return row


def _question_row(blocks: dict, tid: str, kept: set[str], alias_kept: set[str] | None = None) -> dict | None:
    slice_q = None
    for question in blocks.get("questions") or []:
        if question.get("mark") in ("tasks", "inferred") and tid in (question.get("tasks") or []):
            return _oq_row(tid, question, whole=False, kept=kept, alias_kept=alias_kept)
        if question.get("blocks_slice") and slice_q is None:
            slice_q = question
    if slice_q is not None:
        return _oq_row(tid, slice_q, whole=True, kept=kept, alias_kept=alias_kept)
    for risk in blocks.get("risks") or []:
        if not risk.get("blocks_slice"):
            continue
        short = str(risk.get("text") or "").strip()
        if short.startswith("- "):
            short = short[2:].strip()
        return {
            "bucket": "blocked",
            "task": tid,
            "reason": f'plan Risk "{short}" blocks the whole slice (inferred)',
        }
    return None


def build_rows(root: Path, excluded: set[str] | None = None, aliases: list | None = None) -> list[dict]:
    """Ready-check rows from the spec folder. The walk does not hand-build these."""
    tasks_path = root / "tasks.md"
    plan_path = root / "plan.md"
    spec_path = root / "spec.md"
    verify_path = root / "verify.md"
    if not tasks_path.is_file():
        return [{"bucket": "blocked", "task": None, "reason": "no tasks.md"}]
    order = order_mod()
    tasks = order.parse(tasks_path.read_text(encoding="utf-8"))
    if not tasks:
        return [{"bucket": "blocked", "task": None, "reason": "no tasks.md"}]
    plan_text = plan_path.read_text(encoding="utf-8") if plan_path.is_file() else ""
    spec_text = spec_path.read_text(encoding="utf-8") if spec_path.is_file() else ""
    rests = _task_rests(tasks_path.read_text(encoding="utf-8"))
    merged_branches = _merged_branches(spec_text)
    # 1.177.2: a build-progress file with a merge-pr result (from the walk,
    # /crav1-merge-pr, or the host check) makes its tasks done.
    walk_merged = merged_walk_tasks(root)
    for task in tasks:
        task["ticked"] = task["done"]
        task["merged"] = _task_merged(rests.get(task["id"], ""), merged_branches) or f"T{task['id']}" in walk_merged
        # A merged pull request is built, so later tasks do not wait on it.
        if task["merged"]:
            task["done"] = True
    analysed = order.analyse(tasks)
    by_reason = {row["id"]: row for row in analysed["rows"]}
    task_ids = [f"T{task['id']}" for task in tasks]
    recorded = resolve_ever_recorded(root)
    blocks = blocks_mod().analyse(
        spec_text,
        plan_text,
        task_ids=task_ids,
        resolve_recorded=recorded,
    )
    kept = kept_question_keys(root)
    stored_questions = question_rows_of(root)
    excluded = excluded or set()
    alias_kept: set[str] = set()
    for question in blocks.get("questions") or []:
        flagged, note = _question_alias(question, kept, stored_questions, excluded, task_ids)
        if flagged and question.get("key"):
            alias_kept.add(question["key"])
        if note is not None and aliases is not None:
            aliases.append(note)
    approval_holds = approval_mod().holds(spec_text, task_ids)
    verify_text = verify_path.read_text(encoding="utf-8") if verify_path.is_file() else None
    warning = reviewed_warning(plan_text) if plan_path.is_file() else None
    rows = []
    for task in tasks:
        tid = f"T{task['id']}"
        merged = task["merged"]
        if task["ticked"] or merged:
            # A built task that verify.md still calls not implemented is stale,
            # not Needs verify. The waiting line names the catch-up (1.135.0).
            if _listed_not_implemented(verify_text, tid):
                row = {"bucket": "done", "task": tid, "stale_verify": True}
                _attach_deps(row, task)
                rows.append(row)
                continue
            if task["ticked"]:
                bucket, reason = _verify_for(verify_text, tid)
                row = {"bucket": bucket, "task": tid}
                if reason:
                    row["reason"] = reason
                _attach_deps(row, task)
                rows.append(row)
                continue
            status = (_overview_status(verify_text, tid) or "").lower()
            if "unverified" in status or "claimed" in status or "failed" in status:
                bucket, reason = _verify_for(verify_text, tid)
                row = {"bucket": bucket, "task": tid}
                if reason:
                    row["reason"] = reason
            else:
                row = {"bucket": "done", "task": tid}
            _attach_deps(row, task)
            rows.append(row)
            continue
        if not plan_path.is_file():
            row = {"bucket": "blocked", "task": tid, "reason": "no plan.md (recorded)"}
            _attach_deps(row, task)
            rows.append(row)
            continue
        question = _question_row(blocks, tid, kept, alias_kept)
        if question:
            _attach_deps(question, task)
            rows.append(question)
            continue
        approval = approval_holds.get(tid)
        if approval:
            row = {
                "bucket": "blocked",
                "task": tid,
                "reason": f'approval needed "{approval.get("text") or ""}" (recorded)',
                "asked": bool(approval.get("asked")),
                "approval": True,
            }
            if approval.get("who"):
                row["who"] = approval["who"]
            _attach_deps(row, task)
            rows.append(row)
            continue
        dep = by_reason.get(task["id"])
        if dep and dep.get("reason"):
            reason = dep["reason"]
            # A wait on a real earlier task is the order. A cycle, or an
            # after: that names no task, stays blocked.
            if re.search(r"waits on\s+T\d+", reason) and "cycle" not in reason.lower() and "names no task" not in reason.lower():
                bucket = "waits-in-order"
            else:
                bucket = "blocked"
            row = {"bucket": bucket, "task": tid, "reason": reason}
            _attach_deps(row, task)
            rows.append(row)
            continue
        row = {"bucket": "ready", "task": tid}
        if warning:
            row["warning"] = warning
        _attach_deps(row, task)
        rows.append(row)
    return rows


def _attach_deps(row: dict, task: dict) -> None:
    row["deps"] = [f"T{dep}" for dep in task["deps"]]
    row["dep_recorded"] = bool(task["recorded"])


def resolve_is_keep(root: Path) -> bool:
    """True when resolve-open-questions is recorded against the current spec."""
    if not root.is_dir():
        return False
    data = load(root)
    body = data["steps"].get("resolve-open-questions")
    if not body:
        return False
    return not affected_drift(root, "resolve-open-questions", body, data["steps"])


def _slug(root: Path) -> str:
    data = load(root) if root.is_dir() else {"slice": None}
    parts = [part for part in str(data.get("slice") or "").strip("/").split("/") if part]
    if parts:
        return parts[-1]
    return root.name


def _only_spec(root: Path) -> bool:
    """True when this folder is the only slice under docs/specs."""
    parent = root.parent
    if parent.name != "specs" or parent.parent.name != "docs":
        return False
    found = []
    try:
        children = list(parent.iterdir())
    except OSError:
        return False
    for child in children:
        if not child.is_dir() or child.name.startswith("_") or child.name == "retired":
            continue
        if any((child / name).is_file() for name in ("spec.md", "plan.md", "tasks.md")):
            found.append(child)
    return len(found) == 1 and found[0].resolve() == root.resolve()


def command_slug(root: Path) -> str | None:
    """Slug for a fresh-session command, or None when the repo has one slice.

    A new chat has no earlier reply. The walk can see the repo. One slice
    under docs/specs is that slice, so the command does not repeat the slug.
    More than one slice, or a folder outside that layout, needs the slug.
    """
    if root is None or _only_spec(root):
        return None
    slug = _slug(root)
    return slug or None


def _git_user(root: Path | None) -> str | None:
    """`git config user.name` in the specs repo, or None."""
    if root is None:
        return None
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "config", "user.name"],
            capture_output=True, text=True, timeout=10, stdin=subprocess.DEVNULL,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    name = (proc.stdout or "").strip() if proc.returncode == 0 else ""
    return name or None


def apply_claims(root: Path | None, rows: list[dict], user: str | None = None, branch: str | None = None) -> dict:
    """Hold claimed tasks as in progress. Empty when there is no claims.md.

    A claim by `user` (else `git config user.name`), on `branch` when one is
    given, is yours: the task is not held, and says `in progress by you`
    (1.160.0). Someone else's claim still holds it.
    """
    empty = {"claims": [], "warnings": [], "ids": []}
    if root is None or not root.is_dir():
        return empty
    loaded = claims_mod().load_claims(root)
    claims = loaded.get("claims") or []
    if claims:
        claims_mod().apply_to_rows(rows, claims, user=user or _git_user(root), branch=branch)
        apply_built_claims(root, rows)
    apply_built_tasks(root, rows)
    cm = claims_mod()
    ticked = cm.ticked_ids(root) if hasattr(cm, "ticked_ids") else set()
    warnings = cm.age_warnings(claims, loaded.get("max_age_days") or 3, ticked)
    return {"claims": claims, "warnings": warnings, "ids": claims_mod().claimed_ids(claims)}


MERGE_WAIT_STEPS = {"comment", "wait-merge"}
_PROGRESS_STEP = re.compile(r"^- Step:\s*(\S+)", re.M)
_PROGRESS_PR = re.compile(r"\b(?:PR|pull request)\s+#?(\d+)", re.I)


def walk_built(root: Path | None) -> dict:
    """Tasks built on a branch walk that is not merged (1.175.0).

    From build-progress/*.md: a done `Step: build T#` or a `- Built: T#` row,
    while the file has no merge-pr result. Returns {"T9": {"branch", "pr"}}.
    """
    out: dict = {}
    if root is None or not (Path(root) / "build-progress").is_dir():
        return out
    try:
        walks = map_mod().progress_state(root)
    except Exception:  # noqa: BLE001 - a bad progress file must not hide the rows
        return out
    for branch, walk in (walks or {}).items():
        if walk.get("merged"):
            continue
        for num in sorted(walk.get("built") or ()):
            out[f"T{int(num)}"] = {"branch": branch, "pr": walk.get("pr")}
    return out


def built_claim_phrase(who: str, pr) -> str:
    """`built by person B, waits for PR 82 to merge` (1.175.0)."""
    who = (who or "").strip() or "someone"
    wait = f"waits for PR {pr} to merge" if pr else "waits for its pull request to merge"
    return f"built by {who}, {wait}"


def apply_built_claims(root: Path | None, rows: list[dict]) -> None:
    """Someone else's claim on a built task says built, not in progress (1.175.0).

    The claim stays until the merge (branch-run.md), so the task is still
    held. Only its words change: `built by <name>, waits for PR <n> to merge`
    instead of `in progress by <name> since <date>`.
    """
    built = walk_built(root)
    if not built:
        return
    for row in rows:
        task = row.get("task")
        if not task or task not in built or not row.get("claim") or row.get("own_claim"):
            continue
        if task_state_mod().row_state(row) == task_state_mod().DONE:
            continue
        row["claim_built"] = built[task]
        # The same merge wait as a verified-on-branch row, so the hold spreads
        # the same way whichever file mentioned it (1.180.0, M5).
        row.setdefault("merge_wait", {"branch": built[task].get("branch"), "pr": built[task].get("pr"), "owner": "other"})
        row["reason"] = built_claim_phrase(row.get("who") or "", built[task].get("pr"))


def apply_built_tasks(root: Path | None, rows: list[dict]) -> None:
    """A task already built on an unmerged branch is never startable (1.182.0).

    A done `Step: build T#` in a build-progress file counts whatever the
    header lists, so a second task added to a branch is built and waits for
    that branch's pull request, like the first. Your own claim on it no
    longer reads `T# is yours; the walk resumes it.`: it is waiting, held,
    and the Waiting line or merge list names the pull request.
    """
    built = walk_built(root)
    if not built:
        return
    for row in rows:
        task = row.get("task")
        if not task or task not in built or row.get("merge_wait"):
            continue
        if row.get("bucket") == "needs-verify" or task_state_mod().row_state(row) == task_state_mod().DONE:
            continue
        info = built[task]
        row["bucket"] = "waiting"
        row["held"] = True
        row["walk_built"] = True
        row["merge_wait"] = {"branch": info.get("branch"), "pr": info.get("pr"),
                             "owner": "other" if row.get("claim") and not row.get("own_claim") else "self"}
        if row.get("claim") and not row.get("own_claim") and row.get("who"):
            row["reason"] = built_claim_phrase(row["who"], info.get("pr"))
        else:
            row["reason"] = merge_wait_phrase(info)


_PR_HEADER = re.compile(r"^PR:\s*#?(\d+)\s*$", re.M | re.I)
PR_OPEN_STEPS = ("open-pr",)


def _file_pr(text: str) -> int | None:
    """The pull request a build-progress file is about (1.179.0).

    A header `PR: <n>` line, else the first PR named by the last `open-pr`
    step, else the last PR named by the last `comment` or `wait-merge` step,
    else the last PR named anywhere. A step that says `take in develop after
    PR 71` does not make PR 71 this file's PR when its own PR is named too.
    """
    head, _sep, _rest = (text or "").partition("\n- Step:")
    match = _PR_HEADER.search(head)
    if match:
        return int(match.group(1))
    blocks = re.split(r"(?m)^- Step:", text or "")[1:]
    steps = [(block.split(None, 1)[0].strip().lower() if block.split() else "", block) for block in blocks]
    for name, block in reversed(steps):
        if name in PR_OPEN_STEPS:
            prs = _PROGRESS_PR.findall(block)
            if prs:
                return int(prs[0])
    for name, block in reversed(steps):
        if name in MERGE_WAIT_STEPS:
            prs = _PROGRESS_PR.findall(block)
            if prs:
                return int(prs[-1])
    prs = _PROGRESS_PR.findall(text or "")
    return int(prs[-1]) if prs else None


def progress_merge_waits(root: Path | None) -> dict:
    """Tasks whose walk waits on a merge, from build-progress/<branch>.md (1.171.0).

    A branch whose last recorded step is `comment` or `wait-merge` is pushed
    and waits for its pull request to merge. Returns {"T5": {"branch", "pr",
    "owner", "step"}}. Empty when there is no build-progress folder.
    """
    out: dict = {}
    if root is None:
        return out
    folder = Path(root) / "build-progress"
    if not folder.is_dir():
        return out
    for path in sorted(folder.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        steps = _PROGRESS_STEP.findall(text)
        if not steps or steps[-1].strip().lower() not in MERGE_WAIT_STEPS:
            continue
        head = text.split("\n- Step:", 1)[0]
        tasks_line = re.search(r"^Tasks:\s*(.*)$", head, re.M)
        branch_line = re.search(r"^Branch:\s*(\S+)", head, re.M)
        owner_line = re.search(r"^Owner:\s*(\S+)", head, re.M)
        ids = re.findall(r"\bT(\d+)\b", tasks_line.group(1)) if tasks_line else []
        # 1.182.0: a task a build step names waits too, even when an older
        # header lists only the branch's first task.
        for task in task_state_mod().progress_tasks(text)["all"]:
            if task[1:] not in ids and str(int(task[1:])) not in ids:
                ids.append(task[1:])
        # 1.179.0: the file's own PR (its header, open-pr step or merge-wait
        # step), not the last PR mentioned anywhere in it.
        pr = _file_pr(text)
        for num in ids:
            out[f"T{int(num)}"] = {
                "branch": branch_line.group(1) if branch_line else path.stem.replace("--", "/"),
                "pr": pr,
                "owner": owner_line.group(1) if owner_line else "self",
                "step": steps[-1].strip().lower(),
            }
    return out


def _ids_span(ids: list[str]) -> str:
    """`T9 to T12` for a run of numbers, else `T9, T10 and T12` (1.175.0)."""
    nums = []
    for task in ids:
        match = re.fullmatch(r"T(\d+)", str(task).strip())
        if not match:
            return _task_ids_text(ids)
        nums.append(int(match.group(1)))
    if len(nums) > 2 and nums == list(range(nums[0], nums[0] + len(nums))):
        return f"T{nums[0]} to T{nums[-1]}"
    return _task_ids_text([f"T{n}" for n in nums])


_RUN_YES = re.compile(r"^Run yes:\s*(.+?),\s*\d{4}-\d{2}-\d{2}T", re.M)


def walk_owner(root: Path | None, branch: str, text: str = "") -> dict:
    """Who runs a branch walk, from claims.md and the progress file (1.175.0).

    The claim user on that branch, else the `Run yes:` name. `Owner: self`
    is relative to whoever ran the walk, so it is never used alone. Returns
    {"user": name or None, "tasks": [T#, ...]}.
    """
    user = None
    tasks: list[str] = []
    try:
        claims = (claims_mod().load_claims(root) or {}).get("claims") or [] if root is not None else []
    except Exception:  # noqa: BLE001 - a bad claims file is reported elsewhere
        claims = []
    for claim in claims:
        if (claim.get("branch") or "").strip() == branch:
            user = user or (claim.get("user") or "").strip() or None
            for task in claim.get("tasks") or []:
                if task not in tasks:
                    tasks.append(task)
    if user is None and text:
        match = _RUN_YES.search(text)
        if match:
            user = match.group(1).strip() or None
    return {"user": user, "tasks": tasks}


def walk_owner_waits(root: Path | None, user: str | None = None) -> list[str]:
    """Waiting lines for someone else's unfinished branch walk (1.175.0).

    `T9 to T12 are person B's, built, and wait for PR 82 to merge.` when
    every claimed task is built and the pull request is known, else
    `T9 to T12 are in progress by person B.` No continue offer.
    """
    out = []
    built = walk_built(root)
    for branch, info in _unfinished_walks(root, user).items():
        owner = info["owner"]
        if not owner["user"] or info["own"] is not False:
            continue
        tasks = owner["tasks"]
        names = _ids_span(tasks) if tasks else f"The tasks on {branch}"
        plural = len(tasks) != 1
        pr = info.get("pr")
        if tasks and pr and all(task in built for task in tasks):
            verb = "wait" if plural else "waits"
            be = "are" if plural else "is"
            out.append(f"Waiting: {names} {be} {owner['user']}'s, built, and {verb} for PR {pr} to merge.")
        else:
            be = "are" if plural or not tasks else "is"
            out.append(f"Waiting: {names} {be} in progress by {owner['user']}.")
    return out


def _unfinished_walks(root: Path | None, user: str | None = None) -> dict:
    """Branch runs that are not merged and not waiting on a merge (1.175.0).

    {branch: {"run", "owner", "own", "pr"}}. `own` is True when the walk's
    claim user is the local `git config user.name` (the claims `yours`
    check), False when it is someone else, None when no name is recorded.
    """
    out: dict = {}
    if root is None:
        return out
    path = progress_path(root)
    if not path.is_file():
        return out
    data, _err = _try_parse(path.read_text(encoding="utf-8"))
    if not data:
        return out
    local = None
    looked = False
    for branch in sorted(data.get("branch_runs") or {}):
        run = data["branch_runs"][branch]
        if str(run.get("state") or "").strip().lower() == "merged":
            continue
        log = Path(root) / str(run.get("log") or f"build-progress/{branch.replace('/', '--')}.md")
        text = ""
        if log.is_file():
            try:
                text = log.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                text = ""
            steps = _PROGRESS_STEP.findall(text)
            if steps and steps[-1].strip().lower() in MERGE_WAIT_STEPS:
                continue
            if steps and steps[-1].strip().lower() == "merge-pr":
                continue
        owner = walk_owner(root, branch, text)
        own = None
        if owner["user"]:
            if not looked:
                local = user or _git_user(root)
                looked = True
            own = bool(local) and claims_mod().same_person(owner["user"], local)
        else:
            head = text.split("\n- Step:", 1)[0]
            match = re.search(r"^Owner:\s*(\S+)", head, re.M)
            if match and match.group(1).strip().lower() == "other":
                own = False
        prs = _PROGRESS_PR.findall(text)
        out[branch] = {"run": run, "owner": owner, "own": own, "pr": int(prs[-1]) if prs else None}
    return out


def resume_walk_entries(root: Path | None, slug: str, user: str | None = None) -> list[str]:
    """Run next entries that continue an unfinished branch walk (1.174.0).

    A branch run in walk-progress.md that is not merged, whose own
    build-progress file is not at `comment` or `wait-merge` and whose owner
    is not someone else, is offered first: `Continue the build walk on
    <branch>:` above `/crav1-build-walk <slug> <branch>`. A walk that waits on
    a merge stays a Waiting line (1.171.0). Only your own walk is offered:
    the walk's claim user must match `git config user.name`, the same check
    as a claim that is yours (1.175.0). Someone else's walk is a Waiting
    line from walk_owner_waits().
    """
    out = []
    for branch, info in _unfinished_walks(root, user).items():
        if info["own"] is False:
            continue
        command = f"/crav1-build-walk {slug} {branch}" if slug else f"/crav1-build-walk {branch}"
        out.append(_run_entry(command, "", f"Continue the build walk on {branch}:"))
    return out


def merge_wait_phrase(info: dict) -> str:
    pr = info.get("pr")
    return f"waits for PR {pr} to merge" if pr else "waits for its pull request to merge"


def apply_progress_waits(root: Path | None, rows: list[dict]) -> dict:
    """A task pushed and waiting on a merge is waiting, not can start (1.171.0).

    Your own claim no longer offers it in Run next while its branch's
    build-progress file says the walk waits on the merge. Done and Needs
    verify rows keep their state.
    """
    waits = progress_merge_waits(root)
    for row in rows:
        task = row.get("task")
        if not task or task not in waits:
            continue
        if row.get("bucket") == "needs-verify" or task_state_mod().row_state(row) == task_state_mod().DONE:
            continue
        row["bucket"] = "waiting"
        row["held"] = True
        row["merge_wait"] = waits[task]
        if row.get("claim") and not row.get("own_claim") and row.get("who"):
            row["reason"] = built_claim_phrase(row["who"], waits[task].get("pr"))
        else:
            row["reason"] = merge_wait_phrase(waits[task])
    apply_built_tasks(root, rows)
    opened = progress_open_prs(root)
    for row in rows:
        task = row.get("task")
        if task in opened and row.get("own_claim") and not row.get("merge_wait"):
            row["own_pr_open"] = opened[task]
    fill_merge_prs(root, rows, opened)
    return waits


def fill_merge_prs(root: Path | None, rows: list[dict], opened: dict | None = None) -> None:
    """Name the pull request on a merge wait when it is known (1.199.0).

    From the branch's open-pr step, the branch run log in walk-progress.md,
    or another task waiting on the same branch, so the line reads
    `Waiting: PR 85 to merge, then ...`, not `the pull request`.
    """
    import os
    opened = opened if opened is not None else progress_open_prs(root)
    try:
        built = walk_built(root) or {}
    except Exception:  # noqa: BLE001
        built = {}
    waits = [row for row in rows if isinstance(row.get("merge_wait"), dict)]
    if not waits:
        return
    known = branch_pr_numbers(root) if any(not row["merge_wait"].get("pr") for row in waits) else {"tasks": {}, "branches": {}}
    for row in waits:
        if not row["merge_wait"].get("pr"):
            task = row.get("task")
            row["merge_wait"]["pr"] = (known["tasks"].get(task) or known["branches"].get(row["merge_wait"].get("branch"))
                                       or opened.get(task) or (built.get(task) or {}).get("pr"))
    by_branch = {row["merge_wait"]["branch"]: row["merge_wait"]["pr"] for row in waits
                 if row["merge_wait"].get("pr") and row["merge_wait"].get("branch")}
    for row in waits:
        info = row["merge_wait"]
        pr = info.get("pr") or by_branch.get(info.get("branch"))
        if not pr and info.get("branch") and not os.environ.get("CRAV1_NO_HOST_LOOKUP"):
            try:
                import importlib.util
                path = Path(__file__).resolve().parents[2] / "crav1-open-pr" / "scripts" / "pr_common.py"
                spec = importlib.util.spec_from_file_location("pr_common_host_1200", path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                pr = mod.pr_number_for_branch(str(info.get("branch")), str(root) if root else None)
            except Exception:
                pr = None
        if not pr:
            continue
        info["pr"] = pr
        reason = str(row.get("reason") or "")
        if "waits for its pull request to merge" in reason:
            row["reason"] = reason.replace("waits for its pull request to merge", f"waits for PR {pr} to merge")


_PR_NOTE = re.compile(r"\(PR\s+#?(\d+)\b", re.I)


def branch_pr_numbers(root: Path | None) -> dict:
    """A branch's pull request number from local files, read-only (1.199.0).

    The same places pr-status reads: the spec's Match `Branch:` line
    `(PR n)`, a task's `(PR n)` note in tasks.md (that task, and its
    `(branch: X)` branch), and any author's build-progress log for the
    branch. {"branches": {branch: n}, "tasks": {"T5": n}}. No host call.
    """
    out: dict = {"branches": {}, "tasks": {}}
    if root is None or not Path(root).is_dir():
        return out
    mod = map_mod()
    try:
        spec = (Path(root) / "spec.md").read_text(encoding="utf-8")
    except OSError:
        spec = ""
    for line in spec.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            stripped = stripped[2:].strip()
        if not stripped.lower().startswith("branch:"):
            continue
        match = _PR_NOTE.search(stripped)
        token = mod.branch_token(re.sub(r"\([^)]*\)", " ", stripped.split(":", 1)[1]))
        if match and token:
            out["branches"].setdefault(token, int(match.group(1)))
    try:
        tasks = (Path(root) / "tasks.md").read_text(encoding="utf-8")
    except OSError:
        tasks = ""
    for num, rest in _task_rests(tasks).items():
        match = _PR_NOTE.search(rest or "")
        if not match:
            continue
        out["tasks"][f"T{num}"] = int(match.group(1))
        for mark in re.finditer(r"\((?:branch|map):\s*([^)]+)\)", rest, re.I):
            token = mod.branch_token(mark.group(1))
            if token:
                out["branches"].setdefault(token, int(match.group(1)))
    try:
        walks = mod.progress_state(root) or {}
    except Exception:  # noqa: BLE001 - a bad progress file must not hide the rows
        walks = {}
    for branch, walk in walks.items():
        if walk.get("pr") and not walk.get("merged"):
            out["branches"].setdefault(branch, int(walk["pr"]))
    return out


def progress_open_prs(root: Path | None) -> dict:
    """Tasks on a branch whose pull request is open and not merged (1.198.0): {"T30": 85}.

    From build-progress/<branch>.md: a done `open-pr` step naming a PR, and no
    done `merge-pr` step. Your own claim there waits for that merge; the walk
    does not resume it.
    """
    out: dict = {}
    if root is None or not (Path(root) / "build-progress").is_dir():
        return out
    for path in sorted((Path(root) / "build-progress").glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        blocks = re.split(r"(?m)^- Step:", text)[1:]
        done = [block.split(None, 1)[0].lower() for block in blocks
                if block.split() and re.search(r"Result:\s*(done|merged)\b", block, re.I)]
        if "open-pr" not in done or "merge-pr" in done:
            continue
        pr = _file_pr(text)
        if not pr:
            continue
        head = text.split("\n- Step:", 1)[0]
        tasks_line = re.search(r"^Tasks:\s*(.*)$", head, re.M)
        ids = {f"T{int(n)}" for n in re.findall(r"\bT(\d+)\b", tasks_line.group(1))} if tasks_line else set()
        ids |= set(task_state_mod().progress_tasks(text)["all"])
        for task in ids:
            out[task] = pr
    return out


_PR_AUTHOR = re.compile(r"^(?:PR author|Opened by):\s*(.+?)\s*$", re.M | re.I)
_NOTE_AUTHOR = re.compile(r"^author:\s*['\"]?(.+?)['\"]?\s*$", re.M | re.I)


def pr_author(root: Path | None, pr, text: str = "") -> str | None:
    """Who opened a pull request, from the kit's own records (1.177.0).

    The PR note's front matter `author:` (`docs/notes/**/<date>-pr-<repo>-<n>.md`
    in the specs repo), else a `PR author:` or `Opened by:` line in the
    build-progress text. None when neither records it. A claim or the walk's
    owner is never the author: someone can add tasks to another's PR.
    """
    if root is None or not pr:
        return None
    here = Path(root).resolve()
    for base in [here, *here.parents]:
        notes = base / "docs" / "notes"
        if notes.is_dir():
            for note in sorted(notes.rglob(f"*-pr-*-{int(pr)}.md")):
                if note.name.endswith("-context.md"):
                    continue
                head = note.read_text(encoding="utf-8", errors="replace")
                if head.startswith("---"):
                    head = head.split("---", 2)[1] if head.count("---") >= 2 else ""
                    match = _NOTE_AUTHOR.search(head)
                    if match and match.group(1).strip():
                        return task_state_mod().clean_name(match.group(1)) or None
            break
    match = _PR_AUTHOR.search(text or "")
    # Stored names are cleaned on read too (1.180.0, S8).
    return (task_state_mod().clean_name(match.group(1)) or None) if match else None


_TASK_STATE = None


def task_state_mod():
    """skill crav1-tasks-ready-to-build scripts/task_state.py, the one owner of a task's state (1.180.0)."""
    global _TASK_STATE
    if _TASK_STATE is None:
        import importlib.util
        path = Path(__file__).resolve().parents[2] / "crav1-tasks-ready-to-build" / "scripts" / "task_state.py"
        spec = importlib.util.spec_from_file_location("task_state_wp", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _TASK_STATE = mod
    return _TASK_STATE


_PR_COMMON = None


def pr_common_mod():
    """skill crav1-open-pr scripts/pr_common.py, loaded once (1.177.1)."""
    global _PR_COMMON
    if _PR_COMMON is None:
        import importlib.util
        path = Path(__file__).resolve().parents[2] / "crav1-open-pr" / "scripts" / "pr_common.py"
        spec = importlib.util.spec_from_file_location("pr_common_wp", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _PR_COMMON = mod
    return _PR_COMMON


# 1.178.0: one host lookup per PR per run gives both the merge state and who
# opened it. host_pr_state fills this; host_pr_author reads it instead of
# asking the host a second time. readiness clears it at the start of a run.
_HOST_LOOKUPS: dict = {}
_HOST_SCOPE = {"on": False}


def _lookup_key(root, pr) -> tuple:
    try:
        return (str(Path(root).resolve()), int(pr))
    except (TypeError, ValueError):
        return (str(root), str(pr))


def host_pr_lookup(root: Path | None, pr) -> dict:
    """PR <n> on its own host, read-only, once per run (1.179.0).

    {"state": host state | {"state": "unhosted"} | None, "error": code |
    None, "detail": text}. `error` is set only when the PR's host is known
    and its CLI could not be read (pr_common.host_lookup: cli-missing,
    cli-not-runnable, timeout, not-signed-in, extension-missing, not-found,
    bad-output, unknown-status, host-error); `host` then names it. With
    CRAV1_NO_HOST_LOOKUP set, or no single host for the PR, both are None.
    Never raises.
    """
    import os
    empty = {"state": None, "error": None, "detail": ""}
    if root is None or not pr or os.environ.get("CRAV1_NO_HOST_LOOKUP"):
        return dict(empty)
    key = _lookup_key(root, pr)
    if _HOST_SCOPE["on"] and key in _HOST_LOOKUPS:
        return _HOST_LOOKUPS[key]
    info = host_pr_ref(root, pr)
    if info.get("status") != "ok":
        result = dict(empty, state={"state": "unhosted"} if info.get("status") == "unhosted" else None)
    else:
        try:
            pc = pr_common_mod()
            got = pc.host_lookup(info, str(pc.repo_root_of(Path(root))))
            result = {"state": got.get("ok"), "error": got.get("error"), "detail": got.get("detail") or "",
                      "host": info.get("host")}
        except Exception as exc:  # noqa: BLE001 - the lookup must never break the check
            result = {"state": None, "error": "cli-not-runnable", "detail": str(exc)[:200], "host": info.get("host")}
    if _HOST_SCOPE["on"]:
        _HOST_LOOKUPS[key] = result
    return result


def host_pr_author(root: Path | None, pr, record: bool = True, branch: str | None = None) -> str | None:
    """Who opened PR <n>, read-only from its own host, then recorded (1.177.1).

    1.179.0: the same single lookup as the merge state (host_pr_lookup).
    A found name is written as `PR author:` in that PR's build-progress file
    (record_pr_author). Never fails the ready check. CRAV1_NO_HOST_LOOKUP=1
    turns it off.
    """
    state = host_pr_lookup(root, pr).get("state") or {}
    name = state.get("author")
    if name and record:
        try:
            record_pr_author(Path(root), int(pr), name, branch)
        except Exception:  # noqa: BLE001 - recording never breaks the check
            pass
    return name


_AUTHOR_LINE = re.compile(r"^(?:PR author|Opened by):.*$", re.M | re.I)


def _progress_pick(root: Path, number: int, branch: str | None = None) -> tuple[Path | None, str, list]:
    """The build-progress file for PR <n>: (path, how, candidates) (1.179.0).

    1. The branch's own file (`build-progress/<branch>.md`, or a header
       `Branch: <branch>`).
    2. The one file whose own PR is <n> (_file_pr: header `PR:`, its open-pr
       step, its merge-wait step).
    3. The one file that names PR <n> anywhere.
    `how` is `branch`, `pr`, `mention`, `ambiguous` (several files match; path
    None, candidates listed) or `none`.
    """
    folder = Path(root) / "build-progress"
    if not folder.is_dir():
        return None, "none", []
    files = sorted(folder.glob("*.md"))
    texts: dict = {}
    for path in files:
        try:
            texts[path] = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
    if branch:
        own = folder / f"{branch.replace('/', '--')}.md"
        if own in texts:
            return own, "branch", [own]
        for path, text in texts.items():
            head = text.split("\n- Step:", 1)[0]
            match = re.search(r"^Branch:\s*(\S+)", head, re.M)
            if match and match.group(1) == branch:
                return path, "branch", [path]
    owners = [path for path, text in texts.items() if _file_pr(text) == int(number)]
    if len(owners) == 1:
        return owners[0], "pr", owners
    if len(owners) > 1:
        return None, "ambiguous", owners
    mentions = [path for path, text in texts.items()
                if int(number) in {int(n) for n in _PROGRESS_PR.findall(text)}]
    if len(mentions) == 1:
        return mentions[0], "mention", mentions
    if len(mentions) > 1:
        return None, "ambiguous", mentions
    return None, "none", []


def _new_progress_file(root: Path, branch: str) -> Path:
    """build-progress/<branch>.md with only its header (1.179.0)."""
    folder = Path(root) / "build-progress"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{branch.replace('/', '--')}.md"
    if not path.exists():
        path.write_text(f"# Build progress\n\nBranch: {branch}\n", encoding="utf-8")
    return path


def _set_header_line(path: Path, pattern: re.Pattern, line: str, after: tuple) -> None:
    """Replace or add one header line, before the first `- Step:` only (1.179.0)."""
    text = path.read_text(encoding="utf-8")
    head, sep, rest = text.partition("\n- Step:")
    if pattern.search(head):
        head = pattern.sub(line.replace("\\", "\\\\"), head, count=1)
    else:
        m = None
        for label in after:
            m = re.search(rf"^{label}:.*$", head, re.M | re.I)
            if m:
                break
        if m:
            head = head[:m.end()] + "\n" + line + head[m.end():]
        else:
            head = head.rstrip("\n") + "\n" + line + "\n"
    path.write_text(head + sep + rest, encoding="utf-8")


def record_pr_author(root: Path, number: int, name: str, branch: str | None = None) -> Path | None:
    """Write `PR author: <name>` into PR <n>'s own build-progress file (1.177.1).

    1.179.0: the file is picked by branch, then by the file's own PR
    (_progress_pick), never the first file that mentions the number; the
    line goes in the header only. With no file and a known branch, the
    branch's file is created. None when no file is found or several match.
    """
    # Cleaned on write (1.180.0, S8): no `Admin` prefix, no `(...)` tag.
    name = task_state_mod().clean_name(name)
    if not name:
        return None
    path, how, _cands = _progress_pick(Path(root), number, branch)
    if path is None:
        if how == "none" and branch:
            path = _new_progress_file(Path(root), branch)
        else:
            return None
    _set_header_line(path, _AUTHOR_LINE, f"PR author: {name}", ("Owner", "Branch"))
    return path


_NOT_A_NAME = {"self", "yours", "you", "someone else", "owner not recorded", "none", "-", "—", "unknown",
               "don't know", "dont know", "other", "others", "someone", "anyone", "nobody", "n/a", "tbd"}
# 1.179.0: `Owner: self | other` is the build-walk mode marker, never a name,
# so only `PR author:` and `Opened by:` lines name people.
_OWNER_LINE = _PR_AUTHOR
_GROUP_WORDS = re.compile(r"\b(?:team|teams|group|department|dept|board|committee|organi[sz]ation|org|company"
                          r"|vendor|supplier|customer|client|ops|support|management|staff|everyone)\b", re.I)


def is_group(name: str) -> bool:
    """A team or an organisation, not a person (1.179.0).

    `the project team`, `the vendor`, `Ops group`, or one all-caps word such
    as `CONTOSO`. The owner question offers people only.
    """
    name = " ".join(str(name or "").split())
    if not name:
        return True
    if name.lower().startswith("the ") or _GROUP_WORDS.search(name):
        return True
    words = name.split()
    return len(words) == 1 and len(name) > 1 and name.isupper()


def known_people(root: Path | None, rows: list[dict] | None = None) -> list[str]:
    """Names the kit already knows, the choices for the owner question (1.178.0).

    From claims.md (`In progress:` users), PR notes' front matter `author:`,
    build-progress `PR author:` and `Opened by:` lines, then the people
    open questions wait on (rows' `who` in the blocked or waiting buckets,
    1.179.0), in that order, once each (same_person). `self`, `other` and
    other placeholders are skipped, and so are teams and organisations
    (is_group). `Owner:` is the walk's mode marker, not a name (1.179.0).
    Read-only.
    """
    if root is None or not Path(root).is_dir():
        return []
    names: list[str] = []

    def add(value) -> None:
        name = task_state_mod().clean_name(str(value or "").strip().strip("`'\""))
        if not name or name.lower() in _NOT_A_NAME:
            return
        try:
            same = claims_mod().same_person
        except Exception:  # noqa: BLE001
            same = lambda a, b: (a or "").lower() == (b or "").lower()  # noqa: E731
        if any(same(name, other) for other in names):
            return
        names.append(name)

    try:
        for claim in claims_mod().load_claims(Path(root)).get("claims") or []:
            add(claim.get("user"))
    except (Exception, SystemExit):  # noqa: BLE001 - choices never break the question
        pass
    here = Path(root).resolve()
    for base in [here, *here.parents]:
        notes = base / "docs" / "notes"
        if notes.is_dir():
            for note in sorted(notes.rglob("*-pr-*.md")):
                head = note.read_text(encoding="utf-8", errors="replace")
                if head.startswith("---") and head.count("---") >= 2:
                    match = _NOTE_AUTHOR.search(head.split("---", 2)[1])
                    if match:
                        add(match.group(1))
            break
    folder = Path(root) / "build-progress"
    if folder.is_dir():
        for path in sorted(folder.glob("*.md")):
            head = path.read_text(encoding="utf-8", errors="replace").split("\n- Step:", 1)[0]
            for match in _OWNER_LINE.finditer(head):
                add(match.group(1))
    for row in rows or []:
        if not isinstance(row, dict) or row.get("bucket") not in ("blocked", "waiting"):
            continue
        who = row.get("who")
        for one in (who if isinstance(who, list) else [who]):
            if one and not is_group(str(one)):
                add(one)
    return names


def owner_choices(root: Path | None, rows: list[dict] | None = None) -> list[str]:
    """The owner question's choices: the known names, then `Don't know` (1.178.0).

    Never a literal `other` (1.179.0): the question's own Other field covers
    someone not listed.
    """
    return [name for name in known_people(root, rows) if name.lower() != "other"] + ["Don't know"]


def rerun_command(root: Path) -> str:
    """The ready check to run again in this same run after an answer (1.178.0)."""
    return f"walk_progress.py readiness --root {root} --write-map --text"


RERUN_LINE = ("Run the ready check again now, in this same run, and print its new reply. "
              "Do not end with the earlier reply's steps.")


HOST_NAME = {"azure": "Azure DevOps", "github": "GitHub"}
# 1.179.0: what each host error means, and the command that fixes it (None:
# nothing to run, only the ready check again).
HOST_FIX = {
    "cli-missing": ("{tool} is not installed", None),
    "cli-not-runnable": ("{tool} could not be started ({detail})", "{tool} --version"),
    "timeout": ("it did not answer within {seconds} s", None),
    "not-signed-in": ("not signed in", "{login}"),
    "extension-missing": ("the azure-devops extension is missing", "az extension add --name azure-devops"),
    "not-found": ("it has no such pull request ({detail})", None),
    "bad-output": ("its answer could not be read ({detail})", None),
    "unknown-status": ("it gave a status the kit does not know ({detail})", None),
    "host-error": ("it failed ({detail})", None),
}
HOST_FIX_LABEL = {
    "cli-missing": "Install {cli} ({link}), then check it runs:",
    "cli-not-runnable": "Check that {tool} runs in this shell:",
    "not-signed-in": "Sign in to {name}:",
    "extension-missing": "Add the Azure DevOps extension:",
}
HOST_CLI = {"azure": ("the Azure CLI", "https://aka.ms/installazurecli", "az login"),
            "github": ("the GitHub CLI", "https://cli.github.com", "gh auth login")}
COMMIT_LINE = "Commit this file with the specs so the answer is kept (it is not pushed for you)."


def host_reason(host: str | None, error: str, detail: str = "") -> str:
    """`not signed in`, `az is not installed`, ... for one host error (1.179.0)."""
    pc = pr_common_mod()
    tool = pc.TOOL.get(host or "", "the host CLI")
    text, _cmd = HOST_FIX.get(error, HOST_FIX["host-error"])
    return text.format(tool=tool, detail=(detail or "no detail").rstrip("."), seconds=pc.host_timeout(host))


def host_fix(host: str | None, error: str) -> tuple[str | None, str | None]:
    """(label, command) that fixes one host error, or (None, None) (1.179.0)."""
    pc = pr_common_mod()
    tool = pc.TOOL.get(host or "", "az")
    cli, link, login = HOST_CLI.get(host or "", HOST_CLI["azure"])
    _text, cmd = HOST_FIX.get(error, HOST_FIX["host-error"])
    if error == "cli-missing":
        cmd = f"{tool} --version"
    if not cmd:
        return None, None
    label = HOST_FIX_LABEL[error].format(cli=cli, link=link, tool=tool, name=HOST_NAME.get(host or "", "the host"))
    return label, cmd.format(tool=tool, login=login)


def host_fix_lines(unread: list[dict], slug: str | None) -> list[str]:
    """Catch-up lines for PRs whose host could not be read (1.179.0).

    One label per host and error, on its own line, above its command alone
    in a code span; then one `run the ready check again` entry. Errors with
    no fix command (timeout, not-found, ...) only say why in that last label.
    """
    groups: dict = {}
    for item in unread or []:
        groups.setdefault((item.get("host") or "azure", item.get("error") or "host-error"), []).append(item)
    if not groups:
        return []
    lines: list[str] = []
    plain: list[str] = []
    for (host, error), items in groups.items():
        prs = _prs_text([item["pr"] for item in items])
        why = host_reason(host, error, items[0].get("detail") or "")
        head = f"{HOST_NAME.get(host, 'The host')} was not reached for {prs}: {why}."
        label, cmd = host_fix(host, error)
        if cmd:
            lines.append(f"{head} {label}")
            lines.append(f"`{cmd}`")
        else:
            plain.append(head)
    again = "Then run the ready check again:" if lines else "Run the ready check again:"
    command = f"/crav1-tasks-ready-to-build {slug}" if slug else "/crav1-tasks-ready-to-build"
    lines.append(" ".join(plain + [again]))
    lines.append(f"`{command}`")
    return lines


def _commit_name(root: Path, path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return Path(path).name


def _ambiguous_reply(args, root: Path, cands: list) -> None:
    print(json.dumps({"status": "ambiguous", "pr": args.pr,
                      "files": [_commit_name(root, path) for path in cands],
                      "line": f"More than one build-progress file names PR {args.pr}. Ask which branch PR {args.pr} "
                              "is on, then run this again with --branch."},
                     indent=2, ensure_ascii=False))
    sys.exit(1)


def _answer_branch(args, root: Path) -> str | None:
    """The branch whose build-progress file takes an answer (1.179.0).

    --branch when given. Else, when several files claim the PR, stop with
    `ambiguous` and ask which branch; else the branch the ready check waits
    on for that PR (waiting_prs), which may be a file still to create.
    """
    if getattr(args, "branch", None):
        return args.branch
    _path, how, cands = _progress_pick(root, args.pr)
    if how == "ambiguous":
        _ambiguous_reply(args, root, cands)
    return waiting_prs(root).get(int(args.pr))


def cmd_pr_author(args) -> None:
    """`pr-author --root <spec-folder> --pr <n> [--name <who>] [--branch <b>]` (1.177.1).

    1.178.0: without --name and with no host answer, it lists the names the
    kit already knows as `choices` (then `Don't know`). After a recorded
    name, `rerun` is the ready check to run again in the same run.
    1.179.0: when the host could not be read at all, the status is
    `host-unread` with the reason and its fix, not a question about the
    owner. The answer goes into the PR's own build-progress file, picked by
    branch; `commit` names that file.
    """
    root = Path(args.root)
    name = args.name
    source = "you" if args.name else "host"
    if not name:
        got = host_pr_lookup(root, args.pr)
        name = (got.get("state") or {}).get("author")
        if not name and got.get("error"):
            try:
                rows = build_rows(root)
            except (Exception, SystemExit):  # noqa: BLE001 - choices are only a fallback
                rows = []
            host = got.get("host")
            label, cmd = host_fix(host, got["error"])
            why = host_reason(host, got["error"], got.get("detail") or "")
            print(json.dumps({"status": "host-unread", "pr": args.pr, "error": got["error"],
                              "detail": got.get("detail") or "", "fix": {"label": label, "command": cmd} if cmd else None,
                              "choices": owner_choices(root, rows),
                              "line": f"{HOST_NAME.get(host, 'The host')} could not be reached ({why}). Fix that and "
                                      f"run the ready check again, or say who opened PR {args.pr}."},
                             indent=2, ensure_ascii=False))
            sys.exit(1)
    if not name:
        try:
            rows = build_rows(root)
        except (Exception, SystemExit):  # noqa: BLE001 - choices never break the question
            rows = []
        print(json.dumps({"status": "not-found", "pr": args.pr, "choices": owner_choices(root, rows),
                          "line": f"The host did not say who opened PR {args.pr}. "
                          "Ask who opened it, offering these choices, then run this again with --name."},
                         indent=2, ensure_ascii=False))
        sys.exit(1)
    if name.strip().lower() in ("don't know", "dont know"):
        print(json.dumps({"status": "skipped", "pr": args.pr, "rerun": rerun_command(root), "line": RERUN_LINE},
                         indent=2, ensure_ascii=False))
        return
    branch = _answer_branch(args, root)
    path = record_pr_author(root, args.pr, name, branch)
    commit = _commit_name(root, path)
    print(json.dumps({"status": "recorded" if path else "no-record", "author": name, "source": source,
                      "file": str(path) if path else None, "commit": commit, "rerun": rerun_command(root),
                      "line": f"{COMMIT_LINE} {RERUN_LINE}" if path else RERUN_LINE},
                     indent=2, ensure_ascii=False))
    if not path:
        sys.exit(1)


def _progress_file_for(root: Path, number: int, branch: str | None = None) -> Path | None:
    """The build-progress file for PR <n> (1.177.2); None when none or several match.

    1.179.0: _progress_pick — the branch's own file, else the one file whose
    own PR is <n>, else the one file that names it.
    """
    return _progress_pick(root, number, branch)[0]


def waiting_prs(root: Path | None, user: str | None = None) -> dict:
    """{pr: branch} for every PR the ready check waits on to merge (1.177.2).

    The same two sources as open_prs (a walk at `comment` or `wait-merge`,
    and someone else's built walk with a known PR), without the owner lookup.
    """
    out: dict = {}
    if root is None or not Path(root).is_dir():
        return out
    for info in progress_merge_waits(root).values():
        if info.get("pr"):
            out.setdefault(int(info["pr"]), info["branch"])
    built = walk_built(root)
    for branch, info in _unfinished_walks(root, user).items():
        tasks = info["owner"]["tasks"]
        if info.get("pr") and tasks and all(task in built for task in tasks):
            out.setdefault(int(info["pr"]), branch)
    return out


def host_pr_ref(root: Path | None, pr) -> dict:
    """Where PR <n> lives, from the kit's records, read-only (1.177.2).

    {"status": "ok", "host", "url", ...} when resolve finds one host;
    {"status": "unhosted"} when a record names the PR but no `Code repo:`
    line or single docs/system/repos.md row gives its host; else the
    resolve status. Never raises.
    """
    try:
        pc = pr_common_mod()
        base = pc.repo_root_of(Path(root))
        info = pc.resolve_ref(str(pr), pc._remote_url(str(base)) or None, [base])
    except Exception:  # noqa: BLE001 - the lookup must never break the check
        return {"status": "error"}
    if info.get("status") == "ask" and info.get("candidates") and all(
            not c.get("host") for c in info["candidates"]):
        return {"status": "unhosted", "number": int(pr)}
    return info


def host_pr_state(root: Path | None, pr) -> dict | None:
    """PR <n>'s state on its own host, read-only (1.177.2). None when unread.

    1.179.0: host_pr_lookup says why when it is unread.
    """
    return host_pr_lookup(root, pr).get("state")


def merged_result_line(number: int, sha: str | None, date: str | None) -> str:
    """`merged (PR 71, merge commit 1a2b3c4d, merged on host 2026-11-14)` (1.177.2)."""
    bits = [f"PR {int(number)}"]
    if sha:
        bits.append(f"merge commit {sha}")
    bits.append(f"merged on host {date}" if date else "merged on host")
    return f"merged ({', '.join(bits)})"


def record_pr_merged(root: Path, number: int, sha: str | None = None, date: str | None = None,
                     branch: str | None = None) -> Path | None:
    """Add a merge-pr result for PR <n> to its build-progress file (1.177.2).

    The same shape as a /crav1-merge-pr or build-walk merge result, so the
    walk stops waiting, the map's done marks take the merge commit, and the
    file's tasks count as done. A branch run in walk-progress.md for that
    branch becomes `merged`. None when no build-progress file names the PR
    or the file already has a merge-pr result.
    """
    from datetime import datetime as _dt
    path = _progress_file_for(root, number, branch)
    if path is None:
        return None
    text = path.read_text(encoding="utf-8")
    steps = _PROGRESS_STEP.findall(text)
    if steps and steps[-1].strip().lower() == "merge-pr":
        return None
    when = _dt.now().astimezone().replace(microsecond=0).isoformat()
    block = (f"- Step: merge-pr\n  Done: {when}\n  Result: {merged_result_line(number, sha, date)}\n")
    text = text.rstrip("\n") + "\n\n" + block
    path.write_text(text, encoding="utf-8")
    head = text.split("\n- Step:", 1)[0]
    match = re.search(r"^Branch:\s*(\S+)", head, re.M)
    name = match.group(1) if match else path.stem.replace("--", "/")
    try:
        if progress_path(root).is_file():
            data, _err = _try_parse(progress_path(root).read_text(encoding="utf-8"))
            if data and name in (data.get("branch_runs") or {}):
                set_branch_run(Path(root), name, "merged")
    except (Exception, SystemExit):  # noqa: BLE001 - the progress log is the record
        pass
    return path


def sync_pr_states(root: Path | None, user: str | None = None) -> dict:
    """Ask each waiting PR's own host whether it merged, and record it (1.177.2).

    Read-only on the host (pr_common.host_state). A merged or completed PR
    gets a merge-pr result in its build-progress file (record_pr_merged), so
    this same ready check counts its tasks as done and drops it from the
    merge list. A PR closed without merging is listed in `closed`; nothing
    is recorded. A PR whose code repo is not recorded is in `unhosted`. A
    host that cannot be read changes nothing; 1.179.0 lists it in
    `host_unread` with the reason ({pr, branch, host, error, detail}).
    """
    out: dict = {"merged": [], "closed": [], "unhosted": [], "branches": {}, "host_unread": [], "files": []}
    # 1.180.0 (S8): stored `PR author:` lines are cleaned once, and every
    # file the check writes is named in its reply.
    out["cleaned"] = clean_stored_authors(root)
    for pr, branch in sorted(waiting_prs(root, user).items()):
        out["branches"][pr] = branch
        got = host_pr_lookup(root, pr)
        state = got.get("state")
        if not state:
            out.setdefault("unread", []).append(pr)
            if got.get("error"):
                # 1.179.0: the host was known but could not be read; say why.
                out["host_unread"].append({"pr": pr, "branch": branch, "host": got.get("host"),
                                           "error": got["error"], "detail": got.get("detail") or ""})
            continue
        if state.get("author"):
            # 1.178.0: the same lookup names who opened it; record it once.
            path = _progress_file_for(Path(root), pr, branch)
            text = path.read_text(encoding="utf-8", errors="replace") if path else ""
            wrote = None if pr_author(root, pr, text) else record_pr_author(Path(root), pr, state["author"], branch)
            if wrote:
                out.setdefault("owners", {})[pr] = task_state_mod().clean_name(state["author"])
                out["files"].append(Path(wrote).name)
        if state["state"] == "unhosted":
            out["unhosted"].append(pr)
        elif state["state"] == "merged":
            if record_pr_merged(Path(root), pr, state.get("sha"), state.get("date"), branch):
                out["merged"].append(pr)
                merged_file = _progress_file_for(Path(root), pr, branch)
                if merged_file is not None:
                    out["files"].append(Path(merged_file).name)
        elif state["state"] == "closed":
            out["closed"].append(pr)
    return out


def clean_stored_authors(root: Path | None) -> list[str]:
    """Rewrite stored `PR author:` / `Opened by:` lines with clean names (1.180.0, S8).

    `PR author: Admin Person A` becomes `PR author: Person A` and
    `PR author: Person B (Tag)` becomes `PR author: Person B`. Line endings
    are kept. Returns the names of the files rewritten.
    """
    folder = Path(root) / "build-progress" if root is not None else None
    if folder is None or not folder.is_dir():
        return []
    cleaned = []
    for path in sorted(folder.glob("*.md")):
        with open(path, encoding="utf-8", errors="replace", newline="") as handle:
            raw = handle.read()

        def fix(match: re.Match) -> str:
            label, name, end = match.group(1), match.group(2), match.group(3)
            return f"{label}{task_state_mod().clean_name(name)}{end}"

        new = re.sub(r"(?mi)^((?:PR author|Opened by):[ \t]*)([^\r\n]*?)([ \t]*\r?)$", fix, raw)
        if new != raw:
            with open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(new)
            cleaned.append(path.name)
    return cleaned


def recorded_line(pr_state: dict | None) -> str | None:
    """`Recorded: PR 71 merged; PR authors for PR 73 and PR 82 (in <files>).` (1.180.0, S8)."""
    state = pr_state or {}
    parts = []
    merged = state.get("merged") or []
    if merged:
        parts.append(_prs_text(merged) + " merged")
    owners = sorted((state.get("owners") or {}).keys())
    if owners:
        parts.append(("PR author for " if len(owners) == 1 else "PR authors for ") + _prs_text(owners))
    if state.get("cleaned"):
        parts.append("author names cleaned")
    files = []
    for name in list(state.get("files") or []) + list(state.get("cleaned") or []):
        if name not in files:
            files.append(name)
    if not parts:
        return None
    line = "Recorded: " + "; ".join(parts)
    if files:
        line += " (in build-progress/" + ", build-progress/".join(files) + ")"
    return line + "."


def _prs_text(prs: list) -> str:
    names = [f"PR {pr}" for pr in prs]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def pr_state_lines(state: dict) -> list[str]:
    """Waiting lines for closed and unhosted PRs (1.177.2)."""
    lines = []
    for pr in state.get("closed") or []:
        lines.append(f"Waiting: PR {pr} was closed without merging; its tasks are not done.")
    unhosted = state.get("unhosted") or []
    if unhosted:
        many = len(unhosted) > 1
        lines.append(f"Waiting: {_prs_text(unhosted)}: code repo not recorded, so the host was not asked "
                     f"whether {'they' if many else 'it'} merged.")
    return lines


def merged_walk_tasks(root: Path | None) -> set[str]:
    """T#s on the `Tasks:` line of a build-progress file with a merge result (1.177.2)."""
    out: set[str] = set()
    folder = Path(root) / "build-progress" if root is not None else None
    if folder is None or not folder.is_dir():
        return out
    try:
        walks = map_mod().progress_state(root)
    except Exception:  # noqa: BLE001
        return out
    for path in sorted(folder.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        head = text.split("\n- Step:", 1)[0]
        match = re.search(r"^Branch:\s*(\S+)", head, re.M)
        key = match.group(1) if match else path.stem.replace("--", "/")
        if not (walks.get(key) or {}).get("merged"):
            continue
        line = re.search(r"^Tasks:\s*(.*)$", head, re.M)
        out |= {f"T{int(n)}" for n in re.findall(r"\bT(\d+)\b", line.group(1))} if line else set()
        # 1.182.0: and every task a build step names.
        out |= set(task_state_mod().progress_tasks(text)["all"])
    return out


def code_repo_choices(root: Path) -> dict:
    """{name: URL} from docs/system/repos.md, the choices for `code-repo` (1.177.2)."""
    pc = pr_common_mod()
    return pc._repos_rows(pc.repo_root_of(Path(root)))


_CODE_REPO_LINE = re.compile(r"^(?:Code repo|Repo):.*$", re.M | re.I)


def record_code_repo(root: Path, number: int, url: str, branch: str | None = None) -> Path | None:
    """Write `Code repo: <url>` into PR <n>'s own build-progress file (1.177.2).

    1.179.0: the file is picked by branch, as record_pr_author does, and
    created for a known branch when none exists. None when no file is found
    or several match.
    """
    path, how, _cands = _progress_pick(Path(root), number, branch)
    if path is None:
        if how == "none" and branch:
            path = _new_progress_file(Path(root), branch)
        else:
            return None
    _set_header_line(path, _CODE_REPO_LINE, f"Code repo: {url}", ("PR author", "Owner", "Branch"))
    return path


def cmd_code_repo(args) -> None:
    """`code-repo --root <spec-folder> --pr <n> [--repo <name-or-url>] [--branch <b>]` (1.177.2).

    Without --repo it lists the docs/system/repos.md rows to offer. With it,
    a repos.md name or a GitHub or Azure DevOps repo URL is written as
    `Code repo: <url>` in that PR's build-progress file; the owner, state
    and bare-number lookups then use it. Run the ready check again after.
    1.179.0: the file is the PR's own (by branch); `commit` names it.
    """
    root = Path(args.root)
    choices = code_repo_choices(root)
    if not args.repo:
        print(json.dumps({"status": "choices", "pr": args.pr,
                          "choices": [{"name": k, "url": v} for k, v in choices.items()],
                          "line": f"Which repo is PR {args.pr} in?"}, indent=2, ensure_ascii=False))
        return
    value = args.repo.strip().strip("`")
    url = choices.get(value.lower().removesuffix(".git"))
    if not url and pr_common_mod().host_of(value)["host"] in ("github", "azure"):
        url = value
    if not url:
        print(json.dumps({"status": "unknown-repo", "repo": value,
                          "choices": [{"name": k, "url": v} for k, v in choices.items()],
                          "line": f"{value} is not a docs/system/repos.md row or a GitHub or Azure DevOps repo URL."},
                         indent=2, ensure_ascii=False))
        sys.exit(1)
    branch = _answer_branch(args, root)
    path = record_code_repo(root, args.pr, url, branch)
    print(json.dumps({"status": "recorded" if path else "no-record", "pr": args.pr, "url": url,
                      "file": str(path) if path else None, "commit": _commit_name(root, path),
                      "next": "Run the ready check again; it asks the PR's host whether it merged and who opened it.",
                      "rerun": rerun_command(root),
                      "line": f"{COMMIT_LINE} {RERUN_LINE}" if path else RERUN_LINE},
                     indent=2, ensure_ascii=False))
    if not path:
        sys.exit(1)


def open_prs(root: Path | None, user: str | None = None) -> dict:
    """Pull requests that wait to merge, from build-progress (1.176.0).

    {pr: {"branch", "tasks", "owner"}}. A walk at `comment` or `wait-merge`,
    and a walk whose claimed tasks are all built with a known PR (someone
    else's walk stopped before the merge). `owner` comes from who opened the
    PR (pr_author, 1.177.0): `yours` when that is the local git user, else
    that name. With no author recorded it is the claimer's name, or
    `owner not recorded` where it would have said `yours`, after the PR's
    own host was asked (host_pr_author, 1.177.1). `added` lists the
    tasks you claimed on someone else's PR.
    """
    out: dict = {}
    if root is None:
        return out
    local = None
    looked = False

    def owner_of(branch: str, text: str, fallback: str | None) -> str:
        nonlocal local, looked
        who = walk_owner(root, branch, text).get("user")
        if who:
            if not looked:
                local = user or _git_user(root)
                looked = True
            if local and claims_mod().same_person(who, local):
                return "yours"
            return who
        return "yours" if (fallback or "self").lower() == "self" else "someone else"

    def is_local(who: str | None) -> bool:
        nonlocal local, looked
        if not who:
            return False
        if not looked:
            local = user or _git_user(root)
            looked = True
        return bool(local) and claims_mod().same_person(who, local)

    def settle(entry: dict, pr, text: str, claimer: str) -> None:
        author = pr_author(root, pr, text)
        if not author and claimer == "yours":
            author = host_pr_author(root, pr, branch=entry.get("branch"))
        if author:
            entry["owner"] = "yours" if is_local(author) else author
            if entry["owner"] != "yours" and claimer == "yours":
                # 1.182.0: only the tasks you claimed on that branch are the
                # ones you added; the PR's own tasks are its author's.
                entry["added"] = list(entry["tasks"])
                entry["claimed"] = list(walk_owner(root, entry.get("branch") or "", text).get("tasks") or [])
        elif claimer == "yours":
            entry["owner"] = "owner not recorded"
        else:
            entry["owner"] = claimer

    for task, info in progress_merge_waits(root).items():
        pr = info.get("pr")
        if not pr:
            continue
        entry = out.setdefault(pr, {"branch": info["branch"], "tasks": [], "owner": None})
        if task not in entry["tasks"]:
            entry["tasks"].append(task)
        if entry["owner"] is None:
            log = Path(root) / "build-progress" / f"{info['branch'].replace('/', '--')}.md"
            text = log.read_text(encoding="utf-8") if log.is_file() else ""
            settle(entry, pr, text, owner_of(info["branch"], text, info.get("owner")))
    built = walk_built(root)
    for branch, info in _unfinished_walks(root, user).items():
        pr = info.get("pr")
        tasks = info["owner"]["tasks"]
        if not pr or not tasks or not all(task in built for task in tasks):
            continue
        entry = out.setdefault(pr, {"branch": branch, "tasks": [], "owner": None})
        for task in tasks:
            if task not in entry["tasks"]:
                entry["tasks"].append(task)
        if entry["owner"] is None:
            name = info["owner"]["user"]
            log = Path(root) / "build-progress" / f"{branch.replace('/', '--')}.md"
            text = log.read_text(encoding="utf-8") if log.is_file() else ""
            settle(entry, pr, text, "yours" if info["own"] else (name or "someone else"))
    for entry in out.values():
        claimed = entry.pop("claimed", None)
        mine = [task for task in claimed or [] if task in entry["tasks"]]
        if "added" in entry and mine:
            entry["added"] = mine
    return out


def _task_num(task: str) -> int:
    match = re.fullmatch(r"T(\d+)", str(task))
    return int(match.group(1)) if match else 10**9


_TASK_BRANCH_LINE = re.compile(r"^\s*[-*]\s*\[[ xX]\]\s*\**\s*(T\d+)\b.*?\(branch:\s*([^)]*)\)", re.M)


def apply_task_branches(root: Path | None, rows: list[dict]) -> None:
    """Each row's `(branch:)` from tasks.md as `task_branch` (1.180.0)."""
    path = Path(root) / "tasks.md" if root is not None else None
    if path is None or not path.is_file():
        return
    found = {f"T{int(m.group(1)[1:])}": m.group(2).strip().strip("`")
             for m in _TASK_BRANCH_LINE.finditer(path.read_text(encoding="utf-8", errors="replace"))}
    for row in rows:
        if row.get("task") in found:
            row.setdefault("task_branch", found[row["task"]])


def apply_merge_deadlocks(rows: list[dict]) -> list[str]:
    """Mark merge deadlocks Blocked (1.180.0, M4).

    Task X is on branch B, whose PR n is open, and depends on task Y, whose
    only way to done is PR n merging. X can never start, so it is Blocked,
    not in progress. Returns the plain lines, one per task.
    """
    by_task = {row.get("task"): row for row in rows if row.get("task")}
    lines = []
    for row in rows:
        task = row.get("task")
        branch = row.get("task_branch")
        if not task or not branch or row.get("bucket") == "done" or row.get("merge_wait"):
            continue
        for dep in row.get("deps") or []:
            info = (by_task.get(dep) or {}).get("merge_wait") or {}
            if (info.get("pr") and info.get("branch") == branch
                    and task_state_mod().row_state(by_task.get(dep) or {}) == task_state_mod().MERGE_WAIT):
                text = task_state_mod().deadlock_text(task, dep, info["pr"], branch)
                row["deadlock"] = text
                row["bucket"] = "blocked"
                row["reason"] = text
                lines.append(text)
                break
    return lines


# 1.197.0: a manual prod task waits for its release, never offered as the first task.
AFTER_RELEASE = re.compile(r"\(after-release:\s*([^)\s]+)\s*\)", re.I)
MANUAL_PROD_TASK = re.compile(r"\(manual,\s*(?:prod|production|prd)\b", re.I)
GATE_TASK = re.compile(r"^\s*-\s*\[ \]\s*(T\d+)\b(.*)$")


def release_gates(root: Path | None) -> dict[str, str]:
    """T# to its release gate phrase: an `(after-release: <branch>)` mark, or a `(manual, prod` task
    that a plan.md `## Risks` line names together with the word release."""
    if root is None:
        return {}
    tasks_path, plan_path = Path(root) / "tasks.md", Path(root) / "plan.md"
    if not tasks_path.is_file():
        return {}
    plan = plan_path.read_text(encoding="utf-8") if plan_path.is_file() else ""
    risks = plan.split("## Risks", 1)[1] if "## Risks" in plan else ""
    risks = re.split(r"\n## ", risks, maxsplit=1)[0]
    gates = {}
    for line in tasks_path.read_text(encoding="utf-8").splitlines():
        m = GATE_TASK.match(line)
        if not m:
            continue
        tid, rest = m.group(1), m.group(2)
        mark = AFTER_RELEASE.search(rest)
        if mark:
            gates[tid] = f"waits for the first release to {mark.group(1)} and a prod yes"
            continue
        if MANUAL_PROD_TASK.search(rest):
            for risk in risks.splitlines():
                if re.search(rf"\b{tid}\b", risk) and re.search(r"(?i)\breleases?\b", risk):
                    gates[tid] = "waits for the release its Risks line names and a prod yes"
                    break
    return gates


def apply_release_gates(root: Path | None, rows: list[dict]) -> None:
    gates = release_gates(root)
    for row in rows:
        task = row.get("task")
        if task in gates and row.get("bucket") in ("ready", "waits-in-order"):
            row["bucket"] = "waiting"
            row["held"] = True
            row["release_gate"] = gates[task]
            row["reason"] = gates[task]


def apply_walk_starts(root: Path, rows: list[dict], user: str | None = None) -> None:
    """Offer a task only when the walk can start it (1.186.0).

    The ready check and `/crav1-build-walk <slug> <T#>` ask the same
    `task_state.walk_start`. A ready row the walk would not start (pushed and
    waiting for its merge, done, or claimed by someone else) is held with
    the walk's reason instead of offered.
    """
    try:
        starts = task_state_mod().walk_starts(root, user)
    except (OSError, ValueError, KeyError):
        return
    for row in rows:
        task = row.get("task")
        if not task or task not in starts:
            continue
        found = starts[task]
        row["walk_start"] = found.get("phase")
        if row.get("bucket") == "ready" and found.get("phase") in ("wait-merge", "done", "claimed"):
            row["bucket"] = "waiting"
            row["reason"] = found.get("reason", "").rstrip(".")


def merge_order(rows: list[dict], prs: dict) -> list[dict]:
    """The PRs in merge order, each with what merging it unblocks (1.176.0).

    A PR whose tasks another PR's tasks depend on comes first. Ties go to the
    PR that unblocks more tasks, then the lower PR number. `ticks` are the
    PR's own tasks; `starts` are tasks held only by dependencies that can
    start once this PR and the ones before it are merged.
    """
    by_task = {row.get("task"): row for row in rows if row.get("task")}
    done = {task for task, row in by_task.items() if row.get("bucket") == "done"}
    in_pr = {task for info in prs.values() for task in info["tasks"]}

    def startable(merged: set[str]) -> set[str]:
        out = set()
        for task, row in by_task.items():
            if task in done or task in in_pr or row.get("bucket") in ("ready", "done", "needs-verify"):
                continue
            if "open question" in str(row.get("reason") or "") or row.get("claim") and not row.get("own_claim"):
                continue
            if row.get("deadlock"):
                continue
            deps = [dep for dep in row.get("deps") or [] if dep]
            if deps and any(dep in merged for dep in deps) and all(dep in done or dep in merged for dep in deps):
                out.add(task)
        return out

    needs: dict = {pr: set() for pr in prs}
    open_waits: dict = {pr: [] for pr in prs}
    for pr, info in prs.items():
        for task in info["tasks"]:
            for dep in (by_task.get(task) or {}).get("deps") or []:
                for other, oinfo in prs.items():
                    if other != pr and dep in oinfo["tasks"]:
                        needs[pr].add(other)
        # 1.180.0 (M2): an unfinished task on the PR's own branch counts too.
        # A branch with an open task that waits on another PR's task cannot
        # merge first, and says why.
        for task, row in by_task.items():
            if task in info["tasks"] or task in done or row.get("task_branch") != info.get("branch"):
                continue
            for dep in row.get("deps") or []:
                for other, oinfo in prs.items():
                    if other != pr and dep in oinfo["tasks"]:
                        needs[pr].add(other)
                        open_waits[pr].append((task, dep, other))
    order: list[dict] = []
    merged: set[str] = set()
    left = set(prs)
    while left:
        free = [pr for pr in left if not (needs[pr] & left)] or sorted(left)
        before = startable(merged)

        def gain(pr):
            return len(startable(merged | set(prs[pr]["tasks"])) - before)

        free.sort(key=lambda pr: (-gain(pr), int(pr)))
        pick = free[0]
        merged |= set(prs[pick]["tasks"])
        starts = sorted(startable(merged) - before, key=_task_num)
        order.append({"pr": pick, **prs[pick], "ticks": sorted(prs[pick]["tasks"], key=_task_num), "starts": starts,
                      "open_waits": sorted(open_waits[pick], key=lambda item: _task_num(item[0]))})
        left.discard(pick)
    return order


def host_unread_owner(host: str | None) -> str:
    """`owner unknown: Azure DevOps not reached` (1.179.0)."""
    return f"owner unknown: {HOST_NAME.get(host or '', 'the host')} not reached"


def _unnamed(owner: str | None) -> bool:
    """`owner not recorded` or `owner unknown: ...`: no person to name (1.179.0)."""
    return bool(owner) and (owner == "owner not recorded" or owner.startswith("owner unknown"))


def merge_order_block(rows: list[dict], prs: dict) -> str:
    """`Merge these PRs, in this order:` with one numbered PR per line (1.176.0)."""
    order = merge_order(rows, prs)
    if not order:
        return ""
    lines = ["Merge these PRs, in this order:"]
    for i, item in enumerate(order, 1):
        owner = item.get("owner") or "someone else"
        whose = owner if owner == "yours" or _unnamed(owner) else f"{owner}'s"
        if item.get("added"):
            whose += f", you added {_ids_span(item['added'])}"
        what = f"ticks {_ids_span(item['ticks'])}"
        if item["starts"]:
            verb = "can" if len(item["starts"]) > 1 else "can"
            what += f", then {_ids_span(item['starts'])} {verb} start"
        if item.get("open_waits"):
            waits = ", ".join(f"{task} waits on {dep} (PR {other})" for task, dep, other in item["open_waits"])
            what += f"; not ready to merge: {waits}"
        lines.append(f"{i}. PR {item['pr']} ({whose}, {item['branch']}): {what}.")
    return "\n".join(lines)


def own_merge_entry(order: list[dict]) -> str | None:
    """The Run next entry that merges your own pull requests first (1.177.0).

    When the merge list holds at least one PR that is yours, the ready check
    leads with `Merge your PRs 71 and 73 first:` above `/crav1-merge-pr 71`,
    the first of yours in list order. Only PRs you opened count; others'
    PRs stay in the merge list only (1.177.1). None when no listed PR is
    yours.
    """
    mine = [str(item["pr"]) for item in order if item.get("owner") == "yours"]
    if not mine:
        return None
    others = [item for item in order if item.get("owner") != "yours"]

    def _and(items: list[str]) -> str:
        return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]

    head = f"Merge your PR {mine[0]} first" if len(mine) == 1 else f"Merge your PRs {_and(mine)} first"
    return _run_entry(f"/crav1-merge-pr {mine[0]}", "", head + ":")


def ask_owners_entry(order: list[dict]) -> str | None:
    """The Run next entry that asks the PR owners to merge (1.177.1).

    Only when the merge list holds PRs and none is yours. `Ask the PR owners
    to merge, in this order:` and one line per owner, in list order:
    `- person B: PR 82`. PRs with no recorded owner share one line. None
    when a listed PR is yours (own_merge_entry leads) or the list is empty.
    """
    if not order or any(item.get("owner") == "yours" for item in order):
        return None
    groups: dict = {}
    for item in order:
        groups.setdefault(item.get("owner") or "someone else", []).append(f"PR {item['pr']}")

    def _and(items: list[str]) -> str:
        return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]

    lines = ["Ask the PR owners to merge, in this order:"]
    for owner, prs in groups.items():
        if owner == "owner not recorded":
            lines.append(f"- {_and(prs)} ({'owners' if len(prs) > 1 else 'owner'} not recorded)")
        elif _unnamed(owner):
            lines.append(f"- {_and(prs)} ({owner})")
        else:
            lines.append(f"- {owner}: {_and(prs)}")
    return "\n".join(lines)


def others_merge_waits(order: list[dict]) -> list[str]:
    """Waiting lines for listed PRs you did not open (1.177.0).

    Not printed by the ready check since 1.177.1: the merge list already
    names these PRs, and ask_owners_entry is the Run next entry for them.

    `Waiting: PR 71 and PR 73 are person A's; they unblock T8.` One line per
    owner, in list order. A PR with no recorded author says `owner not
    recorded`. Your own PRs are the Run next entry instead.
    """
    groups: dict = {}
    for item in order:
        owner = item.get("owner") or "someone else"
        if owner == "yours":
            continue
        groups.setdefault(owner, []).append(item)
    out = []
    for owner, items in groups.items():
        names = [f"PR {item['pr']}" for item in items]
        names = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
        many = len(items) > 1
        if owner == "owner not recorded":
            line = f"Waiting: {names} ({'owners' if many else 'owner'} not recorded)"
        else:
            line = f"Waiting: {names} {'are' if many else 'is'} {owner}'s"
        starts = sorted({t for item in items for t in item.get("starts") or []}, key=_task_num)
        ticks = sorted({t for item in items for t in item.get("ticks") or []}, key=_task_num)
        if starts:
            line += f"; {'they unblock' if many else 'it unblocks'} {_ids_span(starts)}."
        elif ticks:
            line += f"; {'they tick' if many else 'it ticks'} {_ids_span(ticks)}."
        else:
            line += "."
        out.append(line)
    return out


ON_BRANCH = "implemented, verified on branch"


def verified_on_branch(root: Path | None) -> set[str]:
    """T#s whose verify.md row says `Implemented, verified, tick pending`, or the old `Implemented, verified on branch` (1.176.0, 1.182.0)."""
    out: set[str] = set()
    if root is None or not (Path(root) / "verify.md").is_file():
        return out
    for line in (Path(root) / "verify.md").read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        # 1.182.0: `Implemented, verified, tick pending` is the same state;
        # it waits here only while its branch's walk is not merged.
        if len(cells) >= 3 and re.fullmatch(r"T\d+", cells[0]) and task_state_mod().is_waiting_status(cells[2]):
            out.add(cells[0])
    return out


def on_branch_phrase(branch: str, pr, who: str | None = None) -> str:
    """`verified on feat/x, waits for PR 71 to merge` (1.176.0), with `by <name>` for someone else."""
    by = f" by {who}" if who else ""
    wait = f"waits for PR {pr} to merge" if pr else "waits for its pull request to merge"
    return f"verified on {branch}{by}, {wait}"


def apply_verified_on_branch(root: Path | None, rows: list[dict]) -> None:
    """A task verified on an unmerged branch says so, not Not implemented (1.176.0)."""
    tasks = verified_on_branch(root)
    if not tasks:
        return
    waits = progress_merge_waits(root)
    built = walk_built(root)
    for row in rows:
        task = row.get("task")
        if task not in tasks or task_state_mod().row_state(row) == task_state_mod().DONE:
            continue
        info = waits.get(task) or built.get(task)
        if not info:
            continue
        who = row.get("who") if row.get("claim") and not row.get("own_claim") else None
        row["bucket"] = "waiting"
        row["held"] = True
        row["verified_on_branch"] = True
        row.setdefault("merge_wait", {"branch": info.get("branch"), "pr": info.get("pr"), "owner": "self" if not who else "other"})
        row["reason"] = on_branch_phrase(info.get("branch") or "its branch", info.get("pr"), who)


def merge_wait_lines(rows: list[dict]) -> list[str]:
    """Plain Waiting lines for tasks that wait on a merge (1.171.0)."""
    by_pr: dict = {}
    for row in rows:
        info = row.get("merge_wait")
        if not info or not row.get("task"):
            continue
        by_pr.setdefault(info.get("pr"), []).append(row["task"])
    lines = []
    for pr, tasks in by_pr.items():
        named = f"PR {pr}" if pr else "the pull request"
        joined = ", ".join(tasks[:-1]) + " and " + tasks[-1] if len(tasks) > 1 else tasks[0]
        lines.append(f"Waiting: {named} to merge, then {joined} {'are' if len(tasks) > 1 else 'is'} ticked.")
    return lines


def own_claim_line(rows: list[dict]) -> str | None:
    """Your own claimed tasks, in plain words (1.171.0)."""
    parts = []
    for row in rows:
        task = row.get("task")
        if not task or row.get("bucket") == "done":
            continue
        info = row.get("merge_wait")
        if not row.get("own_claim"):
            continue
        # 1.198.0: your own pushed task waits for its merge; the walk does not
        # resume it. Said only when the pull request is known.
        if info:
            # The Waiting line or merge list already names the wait (1.176.0).
            continue
        pr = row.get("own_pr_open")
        if pr:
            parts.append(f"{task} is yours and waits for PR {pr}'s merge.")
        else:
            parts.append(f"{task} is yours; the walk resumes it.")
    return " ".join(parts) or None


def preflight_sync(root: Path | None, skip: bool = False) -> dict:
    """Fetch the specs repo. Behind or diverged stops before a read or write."""
    if skip or root is None:
        return {"ok": True, "state": "skipped", "continue": True, "stop": False}
    return sync_mod().inspect(root, do_fetch=True)


def ready_branches(root: Path) -> list[dict]:
    """Tasks that can start, grouped by build-map branch.

    Empty when the ready check is not-ready. A not-ready list is not a start.
    """
    if root is None or not root.is_dir():
        return []
    rows = build_rows(root)
    apply_claims(root, rows)
    apply_progress_waits(root, rows)
    apply_verified_on_branch(root, rows)
    fill_merge_prs(root, rows)
    apply_loop_holds(root, rows)
    apply_release_gates(root, rows)  # 1.198.0: the build-walk ending uses this list
    resolve_kept = resolve_is_keep(root)
    resolve_recorded = resolve_ever_recorded(root)
    hits = []
    for row in rows:
        if isinstance(row, dict) and row.get("task"):
            # 1.180.0: the shared state, the one the build map colours from.
            row["state"] = task_state_mod().row_state(row)
        hit = classify(row, resolve_kept=resolve_kept, resolve_recorded=resolve_recorded)
        if hit:
            hits.append(hit)
            if hit["kind"] == "waiting":
                row["bucket"] = "waiting"
                # 1.202.0: the held line carries an own pull-request wait.
                # An empty reason used to print `— held` and leave the
                # sentence to a footer.
                if hit.get("own") and hit.get("pr"):
                    sentence = f"{row.get('task')} is yours and waits for PR {hit['pr']}'s merge."
                    current = str(row.get("reason") or "")
                    if "PR " not in current and "pull request" not in current.lower():
                        row["reason"] = sentence
            elif str(hit.get("why") or "").startswith("Unrecognized blocker"):
                # Never invisible (1.180.0, M5): counted as Blocked and printed.
                row["bucket"] = "blocked"
                row["unrecognized"] = True
    propagate_held(rows, hits)
    reopened, _replaced = _without_self_reopen(reopened_hits(root))
    hits.extend(reopened)
    result, _can_start, _held = slice_result(rows, hits)
    if result not in ("ready", "ready-partial"):
        return []
    report = branch_report(root, rows) or {}
    return report.get("ready_branches") or []


def _wait_phrase(waiting: list[dict], noun: str) -> str:
    tasks: list[str] = []
    whos: list[str] = []
    unnamed = 0
    for hit in waiting:
        task = hit.get("task")
        if task and task not in tasks:
            tasks.append(task)
        who = hit.get("who")
        if not who or who == NOT_NAMED:
            unnamed += 1
        elif who not in whos:
            whos.append(who)
    count = len(tasks) or len(waiting)
    if whos and unnamed:
        tail = f" ({', '.join(whos)}; nobody named for {unnamed})"
    elif whos:
        tail = f" ({', '.join(whos)})"
    elif unnamed:
        tail = f" (nobody named for {unnamed})"
    else:
        tail = ""
    line = f"Waiting: {count} tasks wait on {noun}{tail}."
    if noun != "open questions":
        return line
    bits = []
    for hit in waiting:
        reason = str(hit.get("reason") or "")
        match = re.search(r'open question "(.*?)"', reason)
        question = str(hit.get("question") or (match.group(1) if match else "")).strip()
        if not question:
            continue
        task = hit.get("task") or "a task"
        who = hit.get("who")
        if not who or who == NOT_NAMED:
            bits.append(f'{task} waits on "{question}" and nobody is named to answer it')
        else:
            bits.append(f'{task} waits on "{question}" from {who}')
    if not bits:
        return line
    return line[:-1] + ": " + "; ".join(bits) + "."


def _direct_question_or_approval(hit: dict) -> bool:
    """True when this hold is itself an open question or an approval.

    A task that only waits on another task, or is in progress, is not
    counted in the open-questions or approval waiting line (1.153.0).
    """
    if hit.get("propagated"):
        return False
    reason = (hit.get("reason") or "").lower()
    if "held, waits on" in reason or "in progress" in reason:
        return False
    if hit.get("approval") or "approval needed" in reason:
        return True
    if "open question" in reason:
        return True
    return False


def _waiting_lines(waiting: list[dict], slug: str) -> tuple[str | None, str | None]:
    if not waiting:
        return None, None
    direct = [hit for hit in waiting if _direct_question_or_approval(hit)]
    if not direct:
        return None, None
    questions = [hit for hit in direct if not hit.get("approval")]
    approvals = [hit for hit in direct if hit.get("approval")]
    parts = []
    if questions:
        parts.append(_wait_phrase(questions, "open questions"))
    if approvals:
        parts.append(_wait_phrase(approvals, "an approval"))
    line = " ".join(parts)
    if any(not hit.get("asked") for hit in direct):
        nxt = (
            f"/crav1-show-or-ask-open-questions {slug}, "
            "because the questions are not asked yet."
        )
    elif approvals:
        nxt = (
            f"/crav1-record-approval {slug}, "
            "because that yes is not on record yet."
        )
    elif questions:
        # 1.198.0: only when held questions exist, naming who answers them.
        from_whom = _answer_from(questions)
        nxt = (
            f"/crav1-tighten-and-plan-ready-to-build {slug}, "
            f"because the walk resumes when the answers{from_whom} arrive."
        )
    else:
        nxt = None
    return line, nxt


def _answer_from(questions: list[dict]) -> str:
    """` from person A and the project team` (1.198.0): short names, at most three."""
    names: list[str] = []
    for hit in questions:
        who = str(hit.get("who") or "").strip()
        who = re.sub(r"\s*\(.*?\)\s*", " ", who).strip(" ,.;")
        if not who or who == NOT_NAMED or who.lower() in (n.lower() for n in names):
            continue
        names.append(who)
    if not names:
        return ""
    if len(names) > 3:
        names = names[:3] + ["others"]
    return " from " + (names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1])


def propagate_held(rows: list[dict], hits: list[dict]) -> None:
    """A task that depends on a held task is held too (1.132.0).

    The dependency is the one tasks.md already records (`(after: …)`, or the
    task just before it). A cycle, or an after: that names no task, stays a
    blocker. A question that is still a jump back is not propagated: only a
    row already classified as waiting seeds the hold.
    """
    held: dict[str, dict] = {}
    for hit in hits:
        if hit.get("kind") != "waiting" or not hit.get("task"):
            continue
        held[hit["task"]] = hit
    changed = True
    while changed:
        changed = False
        for row in rows:
            task = row.get("task")
            if not task or task in held:
                continue
            if row.get("bucket") in ("needs-verify", "done"):
                continue
            reason = (row.get("reason") or "").lower()
            if "cycle" in reason or "names no task" in reason:
                continue
            if "no plan" in reason or "no tasks" in reason or "plan risk" in reason:
                continue
            deps = [dep for dep in row.get("deps") or [] if dep in held]
            if not deps:
                continue
            tag = "recorded" if row.get("dep_recorded") else "inferred"
            by_dep = {r.get("task"): r for r in rows if r.get("task")}
            merge_prs = {((by_dep.get(dep) or {}).get("merge_wait") or {}).get("pr") for dep in deps}
            if all((by_dep.get(dep) or {}).get("merge_wait") for dep in deps) and len(merge_prs) == 1:
                # 1.182.0: a task waiting on a built task waits on that
                # task's pull request, not on the task.
                pr = merge_prs.pop()
                named = f"PR {pr}" if pr else "its pull request"
                text = f"held, waits on {named} to merge ({', '.join(deps)}, {tag})"
            elif len(deps) == 1:
                text = f"held, waits on {deps[0]} ({tag})"
            else:
                text = "held, waits on " + ", ".join(deps) + f" ({tag})"
            # 1.180.0 (S6): every unfinished dependency is named, held ones
            # first, then the ones not built yet.
            by_id = {r.get("task"): r for r in rows if r.get("task")}
            unbuilt = [dep for dep in row.get("deps") or []
                       if dep and dep not in held and (by_id.get(dep) or {}).get("bucket") not in ("done", None)]
            if unbuilt:
                text += " and " + ", ".join(unbuilt) + " (not built)"
            row["bucket"] = "waiting"
            row["reason"] = text
            row["held"] = True
            source = held[deps[0]]
            if source.get("who"):
                row["who"] = source["who"]
            if "asked" in source:
                row["asked"] = source.get("asked")
            if source.get("approval"):
                row["approval"] = True
            hit = _waiting(row)
            hit["propagated"] = True
            hits.append(hit)
            held[task] = hit
            changed = True


def _resolve_reopen_only(hits: list[dict]) -> bool:
    """True when every hard hit is a reopened resolve-open-questions step."""
    hard = [hit for hit in hits if hit.get("kind") != "waiting"]
    if not hard:
        return False
    return all(
        hit.get("bucket") == "reopened" and hit.get("step") == "resolve-open-questions"
        for hit in hard
    )


def slice_result(rows: list[dict], hits: list[dict]) -> tuple[str, list, list]:
    """ready, ready-partial, or not-ready.

    ready-partial is some tasks that can start now and some that are held,
    with no other walk blocker. not-ready is when nothing can start, and also
    when a walk blocker other than a kept-open question is still open (a
    cycle, a missing task, no plan, needs verify, an assumption, a reopened
    step, or a question that is still a jump back). A reopened
    resolve-open-questions step alone does not force not-ready when some
    tasks can start (1.137.0).
    """
    hard = [hit for hit in hits if hit.get("kind") != "waiting" and not hit.get("loop")]
    # Needs verify is outside the walk and holds only that task: it never
    # hides tasks that can start (1.169.0). It still keeps the result from
    # being ready.
    verify_only = [hit for hit in hard if hit.get("bucket") == "needs-verify"]
    hard = [hit for hit in hard if hit.get("bucket") != "needs-verify"]
    looped = [row.get("task") for row in rows if row.get("loop") and row.get("task")]
    can_start = [row.get("task") for row in rows if row.get("bucket") == "ready" and row.get("task")]
    held = [row.get("task") for row in rows if row.get("bucket") == "waiting" and row.get("task")]
    resolve_only = bool(can_start) and _resolve_reopen_only([hit for hit in hits if not hit.get("loop")])
    if hard and not resolve_only:
        return "not-ready", can_start, held
    if can_start and (held or resolve_only or looped or verify_only):
        return "ready-partial", can_start, held
    if (held or looped or verify_only) and not can_start:
        return "not-ready", can_start, held
    return "ready", can_start, held


# The first real next step when a locked walk step was reopened (1.163.0).
# review-and-tighten-plan starts with tighten-plan, the command the user
# runs to finish that review.
REOPEN_NEXT = {
    "playbook": ("/crav1-tighten-and-plan-ready-to-build", "The playbook step was reopened"),
    "review-architecture": ("/crav1-review-architecture", "The architecture review was reopened"),
    "tighten-spec": ("/crav1-tighten-spec", "The spec was reopened for tightening"),
    "resolve-open-questions": ("/crav1-resolve-open-questions", "Open questions were reopened"),
    "plan-from-spec": ("/crav1-plan-from-spec", "The plan needs to be rewritten from the spec"),
    "review-and-tighten-plan": ("/crav1-tighten-plan", "The plan was reopened for review"),
    "tasks-ready-to-build": ("/crav1-tasks-ready-to-build", "The ready check was reopened"),
}


def _task_ids_text(ids) -> str:
    names = [task for task in ids or [] if task]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def _command_with_slug(command: str, slug: str) -> str:
    command = str(command).strip().strip("`")
    if slug and not command.startswith("git "):
        return f"{command} {slug}"
    return command


RUN_LABELS = {
    "/crav1-show-or-ask-open-questions": "Ask the open questions, which haven't been asked yet:",
    "/crav1-record-approval": "Record the approval, which is not on record yet:",
}


def _run_label(command: str, reason: str) -> str:
    """The label line above a Run next command (1.173.0).

    A sentence on its own line, capitalized and ending in a colon, so the
    command stands alone in its code span under it.
    """
    for prefix, label in RUN_LABELS.items():
        if command.split()[0:1] == [prefix]:
            return label
    text = str(reason).strip().rstrip(".:").strip()
    if not text:
        return "Run:"
    return text[0].upper() + text[1:] + ":"


REASON_LABELS = {
    "the walk resumes when the answers arrive.": "Resume the walk when the answers arrive:",
}


def _run_entry(command: str, reason: str, label: str | None = None) -> str:
    return f"{label or _run_label(command, reason)}\n`{command}`"


def _reopened_label(can_start: list, command: str) -> str:
    """`Finish the reopened /crav1-tighten-plan step:` (1.175.0).

    An action, with the step's command and without the slug. Which tasks
    wait, and why the step reopened, is the plain sentence above it
    (_reopened_why).
    """
    step = str(command).split()[0] if str(command).split() else str(command)
    return f"Finish the reopened {step} step:"


def _reopened_why(hit: dict | None, can_start: list) -> str:
    """One plain sentence: what changed, and which tasks wait (1.175.0)."""
    reason = str((hit or {}).get("reason") or "").strip().rstrip(".")
    ids = _task_ids_text(can_start)
    names = [task for task in can_start or [] if task]
    if not reason:
        reason = "A file this step covers changed after it was recorded"
    if ids:
        verb = "waits" if len(names) == 1 else "wait"
        return f"{reason}, so {ids} {verb}."
    return f"{reason}."


def _wait_until(lead: str, can_start: list, command: str) -> str:
    ids = _task_ids_text(can_start)
    if ids:
        return f"{lead}, so {ids} wait until {command} finishes."
    return f"{lead}, so the work waits until {command} finishes."


def _run_from_clause(text: str) -> str:
    """Turn 'command, because reason' (or a Next: line) into a Run next entry."""
    text = str(text).strip()
    if text.startswith("Next:"):
        text = text[len("Next:"):].strip()
    if ", because " in text:
        command, reason = text.split(", because ", 1)
        reason = reason.strip()
        label = REASON_LABELS.get(reason)
        resume = re.fullmatch(r"the walk resumes when the answers( from .+)? arrive\.", reason)
        if resume and not label:
            label = f"Resume the walk when the answers{resume.group(1) or ''} arrive:"
        return _run_entry(command.strip().strip("`"), reason, label)
    if text.startswith("`") and "\n" in text:
        return text
    return text


def _first_reopened_step(hits: list[dict]) -> str | None:
    reopened = [hit.get("step") for hit in hits if hit.get("bucket") == "reopened" and hit.get("step")]
    if not reopened:
        return None
    return next((step for step in ORDER if step in reopened), reopened[0])


def not_ready_because(result: str, rows: list[dict], hits: list[dict], can_start: list, slug: str = "") -> str | None:
    """Why the result is not-ready, in plain words (1.163.0).

    A hard hit (a reopened step, a jump-back question, a whole-slice hold)
    forces not-ready and still lists tasks whose bucket is ready. Those
    tasks wait until the first real next step finishes. A whole-slice
    question is named from its row.
    """
    if result != "not-ready":
        return None
    step = _first_reopened_step(hits)
    if step:
        command, lead = REOPEN_NEXT.get(step, (STEP_COMMAND.get(step, f"/crav1-{step}"), "An earlier step was reopened"))
        command = _command_with_slug(command, slug)
        return _wait_until(lead, can_start, command)
    for row in rows:
        reason = str(row.get("reason") or "")
        if "whole slice" in reason.lower():
            ids = _task_ids_text(can_start)
            if ids:
                return f"{reason.rstrip('.')}, so {ids} wait."
            return reason
    for hit in hits:
        if hit.get("kind") == "waiting" or hit.get("bucket") == "reopened":
            continue
        why = hit.get("why")
        if why:
            return why
    ids = _task_ids_text(can_start)
    if ids:
        return f"{ids} cannot start yet."
    return "not ready"


_INSTRUCTION = re.compile(r"^(Do not|Never|Jump back|The walk does not|/crav1-)", re.I)


def hard_hit_line(result: str, hits: list[dict], can_start: list) -> str | None:
    """1.198.0: the hard hit that forced not-ready while tasks can start, in plain words.

    `Not ready: T12 is blocked (the queue name is not decided). T3, T4 and T5
    can start once that is cleared.` None when nothing can start, or when a
    reopened step already leads Run next with its own reason.
    """
    if result != "not-ready" or not can_start:
        return None
    hard = [hit for hit in hits if hit.get("kind") != "waiting" and not hit.get("loop")
            and hit.get("bucket") != "needs-verify"]
    if not hard or any(hit.get("bucket") == "reopened" for hit in hard):
        return None
    hit = hard[0]
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", str(hit.get("why") or "")) if part.strip()]
    plain = next((part for part in sentences if not _INSTRUCTION.match(part)), "")
    plain = plain.rstrip(".")
    what = str(hit.get("bucket") or hit.get("kind") or "held").replace("-", " ")
    # 1.199.0: `T30 is blocked`, never `T30 is blocker`.
    what = {"blocker": "blocked", "assumption": "held by an assumption"}.get(what, what)
    if plain.lower().startswith("unrecognized blocker: "):
        plain = plain[len("unrecognized blocker: "):]
    who = hit.get("task") or "The slice"
    head = f"Not ready: {who} is {what}"
    if plain and plain.lower() not in head.lower():
        head += f" ({plain[:1].lower()}{plain[1:]})"
    ids = _task_ids_text(can_start)
    verb = "can" if ids else ""
    return f"{head}. {ids} {verb} start once that is cleared.".replace("  ", " ") if ids else head + "."


def not_ready_run(
    result: str,
    slug: str,
    hits: list[dict],
    can_start: list,
    waiting_next: str | None,
    gap: dict | None,
    sync: dict | None,
    offer: dict | None,
    counts: dict | None,
    because: str | None,
    question_first: bool,
    catch_up: bool = False,
) -> list[str]:
    """The first real next step when not-ready, as one Run next entry (1.163.0).

    With a catch-up block (1.167.0) the verify-behind and push entries are
    left out: that block already leads Run next with those commands.
    """
    if result != "not-ready":
        return []
    step = _first_reopened_step(hits)
    if step:
        command, lead = REOPEN_NEXT.get(step, (STEP_COMMAND.get(step, f"/crav1-{step}"), "An earlier step was reopened"))
        command = _command_with_slug(command, slug)
        hit = next((h for h in hits if h.get("bucket") == "reopened" and h.get("step") == step), None)
        why = _reopened_why(hit, can_start)
        return [why + "\n" + _run_entry(command, why, _reopened_label(can_start, command))]
    if offer and offer.get("entries"):
        return [str(offer["entries"][0])]
    if waiting_next:
        return [_run_from_clause(waiting_next)]
    gap = gap or {}
    counts = counts or {}
    left = sum(int(counts.get(key, 0) or 0) for key in ("ready", "waiting", "waits_in_order", "blocked"))
    if catch_up and (gap.get("behind") or gap.get("orphan_tasks") or gap.get("failed") or (sync and sync.get("state") == "ahead")):
        if question_first and not counts.get("ready"):
            command = _command_with_slug("/crav1-resolve-open-questions", slug)
            return [_run_entry(command, "that question blocks the first task.", "Resolve the open question that blocks the first task:")]
        return []
    if gap.get("behind") or (left == 0 and counts.get("needs_verify")):
        command = _command_with_slug("/crav1-verify-build-against-spec", slug)
        return [_run_entry(command, "verify.md is behind, so the built tasks need to be verified.", "Verify the built tasks, since verify.md is behind:")]
    if sync and sync.get("state") == "ahead":
        ahead = int(sync.get("ahead") or 1)
        unit = "commits" if ahead != 1 else "commit"
        reason = f"The specs repo is {ahead} {unit} ahead of origin."
        return [_run_entry("git push", reason, f"Push the specs repo, which is {ahead} {unit} ahead of origin:")]
    if question_first and not counts.get("ready"):
        command = _command_with_slug("/crav1-resolve-open-questions", slug)
        return [_run_entry(command, "that question blocks the first task.", "Resolve the open question that blocks the first task:")]
    return []


def line_for(result: str, can_start: list, held: list) -> str | None:
    if result != "ready-partial":
        return None
    ready = ", ".join(task for task in can_start if task) or "none"
    first = next((task for task in held if task), "the held tasks")
    return f"Ready: {ready}. Held from {first}."


def gates_for(rows: list[dict]) -> list[dict]:
    """Per-task build gate. A held task is refused. A ready task may start."""
    gates = []
    for row in rows:
        task = row.get("task")
        if not task or row.get("bucket") == "done":
            continue
        if row.get("bucket") == "waiting" or row.get("held"):
            gates.append({
                "task": task,
                "allow": False,
                "refused": True,
                "reason": row.get("reason") or "held",
            })
        elif row.get("bucket") == "ready" and row.get("own_claim"):
            # Your own claim never refuses the task (1.160.0).
            gates.append({"task": task, "allow": True, "refused": False, "reason": row.get("claim_phrase") or "in progress by you"})
        elif row.get("bucket") == "ready":
            gates.append({"task": task, "allow": True, "refused": False})
        else:
            gates.append({
                "task": task,
                "allow": False,
                "refused": False,
                "reason": row.get("reason") or row.get("bucket"),
            })
    return gates


READY_STEP = "tasks-ready-to-build"
REPLACED_RECORD = "The earlier tasks-ready-to-build record is replaced."


def _without_self_reopen(reopened: list[dict]) -> tuple[list[dict], str | None]:
    """The ready check does not block on its own stale record (1.150.0).

    Running readiness reads the current spec, plan, and tasks, so that
    step's staleness is cured by this run. Other reopened steps still block.
    When this step was the only reopen, the earlier record is replaced by
    the normal record confirm. Say that once.
    """
    others = [hit for hit in reopened if hit.get("step") != READY_STEP]
    own = any(hit.get("step") == READY_STEP for hit in reopened)
    replaced = REPLACED_RECORD if own and not others else None
    return others, replaced


def _alternative_lines(next_lines: list[str], run_lines: list[str]) -> list[str]:
    """Keep at most the one-line alternative; never a second copy of the command.

    The Run next block already has the walk command. A Next: line, or any
    line that repeats that command, is dropped (1.153.0).
    """
    commands = []
    for entry in run_lines or []:
        for line in str(entry).splitlines():
            text = line.strip().strip("`")
            if "/crav1-build-walk" in text:
                commands.append(text)
    out: list[str] = []
    for item in next_lines or []:
        text = str(item).strip()
        if not text:
            continue
        if text.startswith("Next:"):
            # Keep only a trailing alternative sentence, if present.
            kept = []
            for line in text.splitlines():
                if "build-tasks builds one task" in line and "/crav1-build-walk" not in line:
                    kept.append(line.strip())
            text = "\n".join(kept)
            if not text:
                continue
        if any(cmd and cmd in text for cmd in commands):
            kept = []
            for line in text.splitlines():
                if "build-tasks builds one task" in line and "/crav1-build-walk" not in line:
                    kept.append(line.strip())
            text = "\n".join(kept)
            if not text:
                continue
        if text not in out:
            out.append(text)
    return out


def compose_ending(
    result: str,
    run_lines: list[str],
    held_lines: list[str],
    waiting: list[str],
    next_lines: list[str],
    because: str | None,
    replaced: str | None,
    branch_runs: list[str] | None = None,
    catch_up: str | None = None,
    hard_line: str | None = None,
) -> str:
    """The reply for a walk ending. Print this text. Do not point at earlier output.

    Run next comes first, before any Waiting line, on ready, ready-partial,
    and not-ready when there is a next step. Each held line is in this text.
    The bottom keeps Waiting lines and at most a one-line alternative. The
    walk command appears only in the Run next block (1.153.0). A not-ready
    reason already used as the Run next line is not repeated below.
    """
    shown = result in ("ready", "ready-partial")
    alternatives = _alternative_lines(next_lines, run_lines if shown else [])
    return ending_mod().compose(
        run=run_lines if run_lines else None,
        held=held_lines,
        branch_runs=branch_runs,
        waiting=waiting,
        because=because if result == "not-ready" and because and not run_lines else None,
        alternatives=alternatives,
        notes=[replaced] if replaced else None,
        catch_up=catch_up or None,
        after_run=hard_line or None,
    )


def _porcelain(root: Path, paths: list[str], every_file: bool = False) -> list[str]:
    cmd = ["git", "-C", str(root), "status", "--porcelain"]
    if every_file:
        cmd.append("--untracked-files=all")
    try:
        proc = subprocess.run(cmd + ["--", *paths], capture_output=True, text=True, check=False, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return []
    if proc.returncode != 0:
        return []
    out = []
    for line in proc.stdout.splitlines():
        name = line[3:].strip().strip('"')
        if " -> " in name:
            name = name.split(" -> ", 1)[1]
        if name:
            out.append(Path(name).name)
    return out


def slice_uncommitted(root: Path | None) -> list[str]:
    """Files in the slice folder that git sees as changed or new (1.176.0), plus kit-written
    notes and sources under docs/notes and docs/sources (1.196.0, 1119d S9), so the count is
    every file the commit will take."""
    if root is None or not Path(root).is_dir():
        return []
    out = _porcelain(Path(root), ["."])
    docs = Path(root).resolve().parent.parent
    extra = [str(docs / name) for name in ("notes", "sources") if (docs / name).is_dir()]
    if extra:
        out += _porcelain(Path(root), extra, every_file=True)
    return out


def catch_up_for(slug: str, gap: dict | None, sync: dict | None, root: Path | None = None,
                 host_unread: list[dict] | None = None) -> str:
    """The `**Catch up first**` block for this check, or "" (1.167.0).

    verify.md behind (gap tasks), a verify.md row for a T# not in tasks.md
    (gap orphan_tasks), and a specs repo ahead of origin. Built by
    walk_ending.catch_up_block, the same text for every ending.
    """
    gap = gap or {}
    sync = sync or {}
    behind = list(gap.get("tasks") or []) if gap.get("behind") else []
    orphans = list(gap.get("orphan_tasks") or [])
    ahead = 0
    if sync.get("state") == "ahead":
        try:
            ahead = int(sync.get("ahead") or 1)
        except (TypeError, ValueError):
            ahead = 1
    failed = list(gap.get("failed") or [])
    files = slice_uncommitted(root)
    block = ending_mod().catch_up_block(slug or None, behind, orphans, ahead, failed=failed, uncommitted=files)
    # 1.179.0: a PR's host that could not be read gets its fix here, label
    # above command, so the merge list is not guessed from a silent failure.
    fix = host_fix_lines(host_unread or [], slug)
    if not fix:
        return block
    if not block:
        return "\n".join(["**Catch up first**", ""] + fix)
    return block + "\n" + "\n".join(fix)


def next_for(result: str, can_start: list, waiting_next: str | None) -> str | None:
    """Fallback when the branch report has no ready line (1.143.0).

    A ready or ready-partial slice names only the one-line alternative.
    The walk command lives in the Run next block, not here (1.153.0).
    A not-ready result may still name a waiting next step.
    """
    alt = "/crav1-build-tasks builds one task without the walk."
    if result == "ready":
        return alt
    if result == "ready-partial":
        ids = ", ".join(task for task in can_start if task)
        if not ids:
            return None
        return alt
    return waiting_next


def counts_for(rows: list[dict], slug: str = "") -> dict:
    """One counts row for the brief ready-check output (1.153.0)."""
    counts = {
        "ready": 0,
        "waiting": 0,
        "waits_in_order": 0,
        "blocked": 0,
        "needs_verify": 0,
        "done": 0,
    }
    for row in rows or []:
        if not row.get("task"):
            continue
        bucket = row.get("bucket") or ""
        if bucket == "ready":
            counts["ready"] += 1
        elif bucket == "waiting" or row.get("held"):
            counts["waiting"] += 1
        elif bucket == "waits-in-order":
            counts["waits_in_order"] += 1
        elif bucket == "blocked":
            counts["blocked"] += 1
        elif bucket == "needs-verify":
            counts["needs_verify"] += 1
        elif bucket == "done":
            counts["done"] += 1
    counts["slug"] = slug
    counts["line"] = (
        f"{slug}\tReady {counts['ready']}\tWaiting {counts['waiting']}\t"
        f"Waits in order {counts['waits_in_order']}\tBlocked {counts['blocked']}\t"
        f"Needs verify {counts['needs_verify']}\tDone {counts['done']}"
    )
    return counts


def brief_payload(out: dict) -> dict:
    """The short ready-check JSON: result, counts, ending, claim warnings."""
    brief = {
        "ok": out.get("ok", True),
        "result": out.get("result"),
        "counts": out.get("counts"),
        "ending": out.get("ending"),
        "claim_warnings": out.get("claim_warnings") or [],
        "stop": out.get("stop", False),
        "reply": out.get("reply") or out.get("ending") or "",
    }
    if out.get("build_map"):
        brief["build_map"] = out["build_map"]
    if out.get("build_map_wrote"):
        brief["build_map_wrote"] = out["build_map_wrote"]
    if out.get("line") and out.get("stop"):
        brief["line"] = out["line"]
    if out.get("reopen_cards"):
        brief["reopen_cards"] = out["reopen_cards"]
    if out.get("auto_clear"):
        brief["auto_clear"] = out["auto_clear"]
        brief["auto_clear_line"] = auto_clear_line(out["auto_clear"])
    return brief


def auto_clear_line(steps: list[str]) -> str:
    """One line for reopened steps cleared with no card (1.196.0)."""
    names = [STEP_PLAIN.get(step, "this step") for step in steps]
    said = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    verb = "stays" if len(names) == 1 else "stay"
    return (f"{said[:1].upper()}{said[1:]} reopened only because of a fact this walk just recorded, "
            f"and a finding already covers it; it {verb} done with no card." if len(names) == 1 else
            f"{said[:1].upper()}{said[1:]} reopened only because of a fact this walk just recorded, "
            f"and a finding already covers it; they {verb} done with no card.")


READ_FILES = ("spec.md", "plan.md", "tasks.md", "verify.md", "claims.md")


def _emit_readiness(args: argparse.Namespace, out: dict) -> None:
    """Brief by default (1.156.0). --full prints the complete JSON, --text the reply."""
    if getattr(args, "text", False):
        _utf8_stdout()
        print(out.get("reply") or out.get("ending") or "")
        return
    emit(out if getattr(args, "full", False) else brief_payload(out))


def reply_for(root: Path | None, out: dict) -> str:
    """The finished ready-check reply, from the shared ending (1.156.0)."""
    slug = _slug(root) if root is not None else ""
    if out.get("stop"):
        return ending_mod().ready_reply(slug, "not-ready", None, out.get("ending") or "", stop=True)
    sources = [name for name in READ_FILES if root is not None and (root / name).is_file()]
    build_map = None
    if out.get("build_map_wrote"):
        build_map = f"docs/specs/{slug}/build-map.md"
        if "build_map_changed" in out:
            build_map += " (updated)" if out["build_map_changed"] else " (unchanged, nothing new since the last write)"
    next_line = None
    # A not-ready ending already starts with Run next (1.163.0). Only keep a
    # trailing Next line when there is still no Run next block, and never
    # when the result is not-ready (those cases live in the ending).
    if not out.get("run_lines") and out.get("result") != "not-ready":
        question_first = any(
            _direct_question_or_approval(hit) and not hit.get("approval")
            for hit in out.get("waiting") or []
        )
        next_line = ending_mod().not_ready_next(slug, out.get("counts"), question_first)
    return ending_mod().ready_reply(
        slug,
        out.get("result") or "",
        out.get("counts"),
        out.get("ending") or "",
        sources=sources,
        build_map=build_map,
        work_item=root is not None and (root / "work-item.md").is_file(),
        next_line=next_line,
    )


def readiness(args: argparse.Namespace) -> None:
    """The ready check; host lookups are shared only within this one run (1.178.0)."""
    _HOST_LOOKUPS.clear()
    _HOST_SCOPE["on"] = True
    try:
        _readiness(args)
    finally:
        _HOST_SCOPE["on"] = False
        _HOST_LOOKUPS.clear()


def _readiness(args: argparse.Namespace) -> None:
    root = Path(args.root) if args.root else None
    built = False
    pr_state: dict = {"merged": [], "closed": [], "unhosted": []}
    sync = preflight_sync(root, skip=getattr(args, "skip_sync", False))
    if sync.get("stop"):
        stopped = {
            "ok": True,
            "stop": True,
            "ready": False,
            "result": "not-ready",
            "sync": sync,
            "ending": sync.get("ending"),
            "line": sync.get("line"),
            "can_start": [],
            "held": [],
            "run_lines": [],
            "next_lines": [],
            "held_lines": [],
            "claim_warnings": [],
            "counts": counts_for([], _slug(root) if root is not None else ""),
        }
        stopped["reply"] = reply_for(root, stopped)
        _emit_readiness(args, stopped)
        return
    if args.json:
        try:
            payload = json.loads(Path(args.json).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fail("readiness", f"cannot read rows: {exc}")
        rows = payload.get("rows")
        if not isinstance(rows, list):
            fail("readiness", "rows must be a list")
        claim_info = apply_claims(root, rows, getattr(args, "user", None), getattr(args, "branch", None)) if root is not None else {"claims": [], "warnings": [], "ids": []}
    elif root is not None:
        if not root.is_dir():
            fail("root", f"not a folder: {root}")
        # 1.177.2: ask each waiting PR's host whether it merged and record
        # it first, so this run's rows, merge list and Run next use it.
        pr_state = sync_pr_states(root, getattr(args, "user", None))
        aliases: list[dict] = []
        rows = build_rows(root, excluded=set(args.new_question or []), aliases=aliases)
        claim_info = apply_claims(root, rows, getattr(args, "user", None), getattr(args, "branch", None))
        built = True
    else:
        fail("readiness", "pass --root <spec-folder>, or --json <rows file>")
    loop_lines: list[str] = []
    deadlock_lines: list[str] = []
    if root is not None and root.is_dir():
        apply_task_branches(root, rows)
        apply_progress_waits(root, rows)
        apply_verified_on_branch(root, rows)
        fill_merge_prs(root, rows)  # 1.199.0: someone else's verified branch too
        loop_lines = apply_loop_holds(root, rows)
        deadlock_lines = apply_merge_deadlocks(rows)
        apply_walk_starts(root, rows, getattr(args, "user", None) or _git_user(root))
        apply_release_gates(root, rows)
    for row in rows:
        if not isinstance(row, dict):
            fail("readiness", "each row must be an object")
    resolve_kept = resolve_is_keep(root) if root is not None else False
    resolve_recorded = resolve_ever_recorded(root) if root is not None else False
    hits = []
    for row in rows:
        if isinstance(row, dict) and row.get("task"):
            # 1.180.0: the shared state, the one the build map colours from.
            row["state"] = task_state_mod().row_state(row)
        hit = classify(row, resolve_kept=resolve_kept, resolve_recorded=resolve_recorded)
        if hit:
            hits.append(hit)
            if hit["kind"] == "waiting":
                row["bucket"] = "waiting"
                # 1.202.0: the held line carries an own pull-request wait.
                # An empty reason used to print `— held` and leave the
                # sentence to a footer.
                if hit.get("own") and hit.get("pr"):
                    sentence = f"{row.get('task')} is yours and waits for PR {hit['pr']}'s merge."
                    current = str(row.get("reason") or "")
                    if "PR " not in current and "pull request" not in current.lower():
                        row["reason"] = sentence
            elif str(hit.get("why") or "").startswith("Unrecognized blocker"):
                # Never invisible (1.180.0, M5): counted as Blocked and printed.
                row["bucket"] = "blocked"
                row["unrecognized"] = True
    propagate_held(rows, hits)
    reopened_raw = reopened_hits(root) if root is not None else []
    reopened, replaced = _without_self_reopen(reopened_raw)
    hits.extend(reopened)
    blockers = [h for h in hits if h["kind"] == "blocker" and not h["outside_walk"]]
    outside = [h for h in hits if h["outside_walk"]]
    assumptions = [h for h in hits if h["kind"] == "assumption"]
    waiting = [h for h in hits if h["kind"] == "waiting"]
    unmapped = [h for h in hits if h["command"] is None and h["kind"] != "waiting"]
    jump = [h for h in hits if h["can_jump_back"]]
    result, can_start, held = slice_result(rows, hits)
    slug = _slug(root) if root is not None else ""
    because = not_ready_because(result, rows, hits, can_start, slug=slug)
    ready = result == "ready"
    waiting_line, waiting_next = _waiting_lines([h for h in waiting if not h.get("merge")], slug)
    report = branch_report(root, rows) if root is not None else None
    ready_lines = (report or {}).get("ready_lines") or []
    held_lines = (report or {}).get("held_lines") or []
    next_lines = (report or {}).get("next_lines") or []
    run_lines = (report or {}).get("run_lines") or []
    later = [hit for hit in reopened if hit.get("step") != "resolve-open-questions"]
    resolve_open = next(
        (hit for hit in reopened if hit.get("step") == "resolve-open-questions"),
        None,
    )
    resolve_waiting = None
    resolve_next = (
        "Run next:\nthat step needs a rerun or clear.\n\n"
        f"Settle the open questions:\n`/crav1-resolve-open-questions {slug}`"
    )
    if later and result != "not-ready":
        names = ", ".join(hit["step"] for hit in reopened)
        nxt = (
            f"Run next:\nrerun or clear {names}.\n\n"
            "Rerun or clear those steps:\n`/crav1-tighten-and-plan-ready-to-build`"
        )
        next_lines = []
    elif result in ("ready", "ready-partial") and next_lines:
        if resolve_open and result == "ready-partial":
            resolve_waiting = (
                f"Waiting: /crav1-resolve-open-questions {slug}, "
                "because that step needs a rerun or clear."
            )
            next_lines = list(next_lines) + [resolve_next]
        nxt = "\n".join(next_lines)
    else:
        nxt = next_for(result, can_start, waiting_next)
        next_lines = []
        if resolve_open and result == "ready-partial":
            resolve_waiting = (
                f"Waiting: /crav1-resolve-open-questions {slug}, "
                "because that step needs a rerun or clear."
            )
            nxt = f"{nxt}\n{resolve_next}" if nxt else resolve_next
            next_lines = [resolve_next]
    if result == "ready-partial" and report and report.get("line"):
        line = report["line"]
    else:
        line = line_for(result, can_start, held)
    gap = verify_gap(root) if root is not None else {
        "behind": False, "tasks": [], "waiting": None, "stale_next": None,
    }
    # What the user can fix now leads Run next as one block (1.167.0); the
    # Waiting lines keep only what waits on people or merges.
    host_unread = list(pr_state.get("host_unread") or [])
    # 1.180.0 (S3): the map is written before the uncommitted files are
    # counted, so a changed build-map.md is in the count.
    map_write = None
    if getattr(args, "write_map", False) and root is not None and root.is_dir():
        map_path = root / "build-map.md"
        map_before = map_path.read_text(encoding="utf-8") if map_path.is_file() else None
        map_text, map_code = map_mod().run_dir(root)
        if map_code:
            fail("build-map", map_text or "could not write build-map.md")
        map_after = map_path.read_text(encoding="utf-8") if map_path.is_file() else None
        map_write = (map_path, map_text, map_before, map_after)
    catch_up = catch_up_for(slug, gap, sync, root, host_unread)
    waiting_bits = list(loop_lines)
    # 1.176.0: one ordered merge list replaces the per-PR Waiting lines.
    merge_prs = open_prs(root, getattr(args, "user", None)) if root is not None and root.is_dir() else {}
    # 1.177.2: a PR closed without merging leaves the merge list.
    for pr in pr_state.get("closed") or []:
        merge_prs.pop(pr, None)
    # 1.179.0: a PR whose host could not be read is not "owner not recorded";
    # the host was never asked, so its owner is unknown until the fix.
    for item in host_unread:
        entry = merge_prs.get(item["pr"])
        if entry and entry.get("owner") in ("owner not recorded", "someone else", None):
            entry["owner"] = host_unread_owner(item.get("host"))
    merge_block = merge_order_block(rows, merge_prs) if merge_prs else ""
    if merge_block:
        # 1.177.1: the list is the only place PR waits live; no Waiting
        # line repeats a listed PR.
        waiting_bits.append(merge_block)
    else:
        waiting_bits.extend(line for line in merge_wait_lines(rows)
                            if not any(f"PR {pr} " in line for pr in pr_state.get("closed") or []))
    waiting_bits.extend(pr_state_lines(pr_state))
    if resolve_waiting:
        waiting_bits.append(resolve_waiting)
    if result == "not-ready" and not can_start and waiting_line:
        waiting_bits.append(waiting_line)
    offer = loop_offer(root) if loop_lines and root is not None and root.is_dir() else {"entries": [], "card": None, "fixes": []}
    question_first = any(
        _direct_question_or_approval(hit) and not hit.get("approval")
        for hit in waiting
    )
    if result in ("ready", "ready-partial"):
        shown_run = list(run_lines) + offer["entries"]
        # Questions not asked yet stay a Run next entry after the branch
        # blocks, never instead of them (1.169.0).
        if waiting_next and waiting_next.startswith("/crav1-show-or-ask-open-questions"):
            shown_run.append(_run_from_clause(waiting_next))
        alt = "/crav1-build-tasks builds one task without the walk."
        # The build-tasks hint moved to /crav1-help (1.176.0): the printed
        # ending no longer repeats it. `next` keeps it for callers.
        shown_next = []
        next_lines = []
        nxt = alt
    else:
        shown_run = not_ready_run(
            result, slug, hits, can_start, waiting_next, gap, sync, offer,
            counts_for(rows, slug), because, question_first,
            catch_up=bool(catch_up),
        )
        shown_next = []
        next_lines = []
        if catch_up:
            nxt = catch_up
        elif shown_run:
            nxt = shown_run[0]
        elif because:
            nxt = because
        else:
            nxt = next_for(result, can_start, waiting_next)
    run_status = branch_run_lines(root)
    local_user = getattr(args, "user", None)
    resume_entries = resume_walk_entries(root, command_slug(root) if root is not None and root.is_dir() else slug, user=local_user)
    for line in walk_owner_waits(root, local_user):
        if merge_block and ", built, and wait" in line or merge_block and ", built, and waits" in line:
            continue
        if line not in waiting_bits:
            waiting_bits.append(line)
    if resume_entries:
        shown_run = resume_entries + [entry for entry in shown_run if entry not in resume_entries]
        if result not in ("ready", "ready-partial") and not catch_up:
            nxt = shown_run[0]
    # 1.177.0: your own PRs in the merge list lead Run next, above the
    # resume entry; with none of yours the order stays as it was.
    own_merge = own_merge_entry(merge_order(rows, merge_prs)) if merge_block else None
    # 1.177.1: none of the listed PRs is yours: ask their owners to merge,
    # above the resume entry.
    nudge = ask_owners_entry(merge_order(rows, merge_prs)) if merge_block and not own_merge else None
    if nudge and nudge not in shown_run:
        shown_run = [nudge] + list(shown_run)
        if result not in ("ready", "ready-partial") and not catch_up:
            nxt = shown_run[0]
    if own_merge and own_merge not in shown_run:
        shown_run = [own_merge] + list(shown_run)
        if result not in ("ready", "ready-partial") and not catch_up:
            nxt = shown_run[0]
    if deadlock_lines:
        # 1.180.0 (M4): a merge deadlock leads Run next with the plan fix, and
        # each one is printed, never shown as in progress.
        fix = _run_entry(f"/crav1-tighten-plan {slug}".strip(), "",
                         "Fix the merge deadlock in the plan, since no merge can untangle it:")
        if fix not in shown_run:
            shown_run = [fix] + list(shown_run)
            if not catch_up:
                nxt = shown_run[0]
        waiting_bits = list(deadlock_lines) + [bit for bit in waiting_bits if bit not in deadlock_lines]
    # 1.199.0: the hard hit comes right after Run next, before Held.
    hard_line = hard_hit_line(result, hits, can_start)
    ending = compose_ending(
        result, shown_run, held_lines, waiting_bits, shown_next, because, replaced, run_status,
        catch_up=catch_up, hard_line=hard_line,
    )
    claim_info = claim_info if "claim_info" in locals() else {"claims": [], "warnings": [], "ids": []}
    warnings = list(claim_info.get("warnings") or [])
    if sync.get("state") in ("no-upstream", "offline") and sync.get("message"):
        ending = (ending + "\n\n" if ending else "") + sync["message"]
    if warnings:
        ending = (ending + "\n\n" if ending else "") + "\n".join(warnings)
    # 1.198.0: a not-ready result with tasks that can start names the hard hit
    # and those tasks, whatever leads Run next (catch-up, resume, merges).
    if hard_line and hard_line not in (ending or ""):
        ending = (ending + "\n\n" if ending else "") + hard_line
    own_line = own_claim_line([row for row in rows if row.get("own_claim")])
    if own_line:
        # 1.202.0: drop a sentence the Held lines already show.
        shown = "\n".join(held_lines)
        kept = [part for part in re.split(r"(?<=\.)\s+", own_line) if part and part not in shown]
        own_line = " ".join(kept) or None
    if own_line:
        ending = (ending + "\n\n" if ending else "") + own_line
    out = {
        "ok": True,
        "ready": ready,
        "result": result,
        "can_start": can_start,
        "held": held,
        "because": because,
        "hard_hit": hard_line,
        "line": line,
        "ready_lines": ready_lines,
        "held_lines": held_lines,
        "next_lines": next_lines,
        "run_lines": shown_run,
        "branch_runs": run_status,
        "ready_branches": (report or {}).get("ready_branches") or [] if result in ("ready", "ready-partial") else [],
        "ending": ending,
        "replaced": replaced,
        "gates": gates_for(rows),
        "next": nxt,
        "start_build": False,
        "blockers": blockers,
        "outside_walk": outside,
        "assumptions": assumptions,
        "unmapped": unmapped,
        "waiting": waiting,
        "waiting_line": waiting_line,
        "waiting_next": waiting_next,
        "resolve_waiting": resolve_waiting,
        "recommend_jump": bool(jump) and result == "not-ready",
        "reopen_cards": [
            reopen_card(h["step"], h.get("changed") or [], bool(jump) and result == "not-ready",
                        bool(getattr(args, "stale_seen", False)))
            for h in hits if h.get("bucket") == "reopened" and h.get("step")
            and h["step"] not in set(getattr(args, "covered", None) or [])
        ],
        "auto_clear": [h["step"] for h in hits if h.get("bucket") == "reopened" and h.get("step")
                       and h["step"] in set(getattr(args, "covered", None) or [])],
        "jump_back": jump,
        "reopened": reopened,
        "reopen_line": None,
        "changed_sections": [],
        "reopen_steps": [],
        "changed_questions": [],
        "restamp_only": False,
        "record_unchanged": bool(root is not None and record_unchanged(root, "tasks-ready-to-build", result)),
        "record_quiet": record_quiet(root, result, hits),
        "verify_behind": gap["behind"],
        "verify_stale": gap["tasks"],
        "verify_waiting": gap["waiting"],
        "stale_next": gap["stale_next"],
        "trust_stale_next": False,
        "sync": sync,
        "stop": False,
        "claims": claim_info.get("ids") or [],
        "claim_warnings": warnings,
        "counts": counts_for(rows, slug),
        "orphan_tasks": gap.get("orphan_tasks") or [],
        "orphan_waiting": gap.get("orphan_waiting"),
        "catch_up": catch_up,
        "loop_lines": loop_lines,
        "loop_card": offer["card"],
        "loop_fixes": offer["fixes"],
        "pr_state": {key: pr_state.get(key) or [] for key in ("merged", "closed", "unhosted")},
        "code_repo_unknown": [
            {"pr": pr, "branch": (pr_state.get("branches") or {}).get(pr)} for pr in pr_state.get("unhosted") or []
        ],
        # 1.178.0: the repo question comes first; who opened a PR is asked
        # only when its repo is known and the host lookup still named no one.
        "owner_unknown": [
            {"pr": pr, "branch": info.get("branch")} for pr, info in sorted(merge_prs.items())
            if info.get("owner") == "owner not recorded" and pr not in (pr_state.get("unhosted") or [])
        ],
        "owners_from_host": {str(k): v for k, v in (pr_state.get("owners") or {}).items()},
        # 1.179.0: PRs whose host was known but could not be read, with why.
        "host_unread": host_unread,
    }
    unread_prs = {item["pr"] for item in host_unread}
    out["owner_unknown"] = [item for item in out["owner_unknown"] if item["pr"] not in unread_prs]
    # 1.179.0: repo, then host, then owner. Who opened a PR is asked only
    # after its host answered and named no one.
    out["ask_first"] = ("code-repo" if out["code_repo_unknown"] else "host" if host_unread
                        else "pr-author" if out["owner_unknown"] else None)
    if out["owner_unknown"]:
        out["owner_choices"] = owner_choices(root, rows)
    if built:
        out["rows"] = rows
        out["question_aliases"] = aliases
    if map_write is not None:
        map_path, text, before, after = map_write
        out["build_map"] = text.strip()
        out["build_map_wrote"] = str(map_path) if after is not None else None
        # 1.177.2: say whether the write changed the map, so a no-op is not
        # mistaken for a failure.
        out["build_map_changed"] = after is not None and after != before
    if root is not None and root.is_dir():
        loaded = load(root)
        out["done_stamp_warning"] = done_stamp_warning(loaded["steps"], loaded.get("acks"))
        effect = section_effect(root, loaded["steps"])
        out["reopen_line"] = effect["reopen_line"]
        out["changed_sections"] = effect["titles"]
        out["reopen_steps"] = effect["reopen_steps"]
        out["changed_questions"] = effect["changed_questions"]
        out["restamp_only"] = effect["restamp_only"]
    out["reply"] = reply_for(root, out)
    recorded = recorded_line(pr_state)
    if recorded:
        out["recorded"] = recorded
        out["reply"] = out["reply"].rstrip("\n") + "\n\n" + recorded
    _emit_readiness(args, out)


def ack_stamps(args: argparse.Namespace) -> None:
    """Record that a shared Done stamp was seen, so the warning stops for it.

    A later stamp that two steps still share warns again. Show the line and
    pass --yes only after that yes. Without --yes this writes nothing.
    """
    root = Path(args.root)
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    data = load(root)
    if not data["steps"]:
        fail("progress-file", "no walk progress to acknowledge")
    pending = [
        (when, names)
        for when, names in _shared_groups(data["steps"])
        if not _ack_covers(data.get("acks") or [], when, names)
    ]
    if not pending:
        emit({"ok": True, "wrote": None, "lines": [], "message": "no shared stamp to acknowledge"})
        return
    lines = [_ack_line(when, names) for when, names in pending]
    if not args.yes:
        emit({
            "ok": False,
            "code": "needs-yes",
            "message": (
                "ack-stamps writes the progress file only with --yes, "
                "after the line was shown and confirmed"
            ),
            "lines": lines,
        })
        raise SystemExit(2)
    acks = list(data.get("acks") or [])
    for when, names in pending:
        acks.append({"when": when, "steps": list(names)})
    data["acks"] = acks
    write_progress(root, data)
    emit({"ok": True, "wrote": PROGRESS_NAME, "lines": lines})


FINDING_CLOSE = 0.86
SAME_CHOICE = "same recorded finding (Recommended)"
NEW_CHOICE = "this is new"
NEW_CHOICE_REC = "this is new (Recommended)"
VAGUE_TOPICS = frozenset({
    "spec", "plan", "task", "tasks", "finding", "issue", "note", "question",
})


def _finding_key(text: str) -> str:
    """First 12 hex of the exact normalized words. Old progress files use this."""
    norm = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:12]


def _norm_topic(text: str | None) -> str:
    raw = re.sub(r"[^a-z0-9]+", " ", (text or "").lower())
    raw = re.sub(r"\s+", " ", raw).strip()
    if len(raw) > 48:
        raw = raw[:48].rstrip()
    return raw


def _topic_ok(topic: str) -> bool:
    if len(topic) < 4 or topic in VAGUE_TOPICS:
        return False
    return re.fullmatch(r"[a-z0-9]+(?:[ -][a-z0-9]+)*", topic) is not None


def _jump_keys(jump: dict) -> set[str]:
    keys = set()
    if jump.get("key"):
        keys.add(jump["key"])
    for alias in jump.get("aliases") or []:
        keys.add(alias)
    return keys


def _family(jumps: list, text_key: str) -> tuple[str | None, list[str], str, str]:
    """First-seen key, aliases, topic, and recorded words for this text key."""
    first = None
    aliases: list[str] = []
    topic = ""
    finding = ""
    for jump in jumps:
        if text_key not in _jump_keys(jump):
            continue
        if first is None:
            first = jump.get("key")
            finding = jump.get("finding") or ""
        if jump.get("topic") and not topic:
            topic = jump["topic"]
        for alias in jump.get("aliases") or []:
            if alias not in aliases:
                aliases.append(alias)
    return first, aliases, topic, finding


def _remember_alias(jumps: list, first_key: str, new_key: str, topic: str) -> bool:
    """Point later wording at the first-seen key. Returns whether anything changed."""
    changed = False
    for jump in jumps:
        if jump.get("key") != first_key:
            continue
        aliases = list(jump.get("aliases") or [])
        if new_key and new_key != first_key and new_key not in aliases:
            aliases.append(new_key)
            jump["aliases"] = aliases
            changed = True
        if topic and not jump.get("topic"):
            jump["topic"] = topic
            changed = True
    return changed


def _close_findings(jumps: list, text: str, fid: str, topic: str) -> list[dict]:
    """Recorded findings a close reword might be. Exact keys are not listed.

    An explicit topic matches only the same P#. A different topic never matches,
    even when the words are close. Two hits stay two hits.
    """
    text_key = _finding_key(text)
    by_key: dict[str, dict] = {}
    for jump in jumps:
        if text_key in _jump_keys(jump):
            continue
        stored_topic = jump.get("topic") or ""
        if topic and stored_topic and topic != stored_topic:
            continue
        sim = blocks_mod().question_similarity(text, jump.get("finding") or "")
        same_topic = bool(topic and stored_topic and topic == stored_topic and jump.get("id") == fid)
        if not same_topic and sim < FINDING_CLOSE:
            continue
        key = jump.get("key") or ""
        row = by_key.get(key)
        if row is None or sim > row["similarity"]:
            by_key[key] = {
                "key": key,
                "id": jump.get("id"),
                "finding": jump.get("finding") or "",
                "similarity": round(sim, 3),
                "how": "topic" if same_topic else "similar",
                "topic": stored_topic,
            }
    return list(by_key.values())


def _same_or_new_offer(fid: str, close: list[dict]) -> dict:
    if len(close) == 1:
        hit = close[0]
        options = [
            {"id": "same", "label": SAME_CHOICE, "recommended": True, "match_key": hit["key"],
             "text": "Count it as the finding already recorded, so it is not jumped back twice. Why: the words are close."},
            {"id": "new", "label": NEW_CHOICE, "recommended": False,
             "text": "Record it as a new finding, then offer the jump back for it."},
        ]
        background = f"{fid} looks like the recorded finding \"{hit['finding']}\"."
        question = f"Is {fid} the same as that recorded finding?"
    else:
        options = [{"id": "new", "label": NEW_CHOICE_REC, "recommended": True,
                    "text": "Record it as a new finding, then offer the jump back for it. Why: more than one recorded finding is close."}]
        for hit in close[:3]:
            short = hit["finding"]
            if len(short) > 80:
                short = short[:77].rstrip() + "..."
            options.append({
                "id": "same",
                "label": f"same as {hit['id']}: {short}",
                "recommended": False,
                "match_key": hit["key"],
                "text": f"Count it as {hit['id']}, so it is not jumped back twice.",
            })
        background = f"{fid} is close to more than one recorded finding."
        question = f"Is {fid} new, or the same as one of them?"
    return {
        "ok": True,
        "offer": "same-or-new",
        "spec": True,
        "finding": fid,
        "matched": [hit["id"] for hit in close],
        "matches": close,
        "background": background,
        "question": question,
        "options": options,
        "already_jumped": False,
        "pause": False,
        "wrote": None,
    }


def _short_finding(text: str) -> str:
    one = re.sub(r"\s+", " ", text.strip())
    if len(one) > 160:
        return one[:157].rstrip() + "..."
    return one


def _continue_list(text: str) -> list[str]:
    return [part for part in text.split(", ") if part]


def _append_finding(root: Path, data: dict, kind: str, fid: str, text: str, key: str, result: str, continue_line: str, open_path: str | None = None, topic: str = "", aliases: list | None = None) -> None:
    jump = {
        "kind": kind,
        "id": fid,
        "when": done_stamp(None),
        "finding": _short_finding(text),
        "result": result,
        "continue": continue_line,
        "key": key,
    }
    if topic:
        jump["topic"] = topic
    if aliases:
        jump["aliases"] = list(aliases)
    if open_path:
        jump["open"] = open_path
    data.setdefault("jumps", []).append(jump)
    if not data.get("slice"):
        data["slice"] = f"docs/specs/{root.name}/"
    write_progress(root, data)


def finding_owner(text: str, kind: str | None = None, topic: str = "") -> str:
    """add-to-spec or tighten-spec (1.194.0). The kind hint wins; then words; unclear is tighten-spec."""
    if kind == "code-drift":
        return "add-to-spec"
    if kind == "spec-text":
        return "tighten-spec"
    words = f"{text} {topic.replace('-', ' ')}"
    if DRIFT_WORDS.search(words) and not SPEC_TEXT_WORDS.search(words):
        return "add-to-spec"
    return "tighten-spec"


def add_to_spec_command(text: str, pr: str | None = None, branch: str | None = None) -> str:
    if pr:
        return f"/crav1-add-to-spec pr{str(pr).lstrip('#').removeprefix('pr')}"
    if branch:
        return f"/crav1-add-to-spec {branch}"
    m = PR_IN_TEXT.search(text or "")
    return f"/crav1-add-to-spec pr{m.group(1)}" if m else "/crav1-add-to-spec"


def _norm_words(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _is_ancestor(code_repo: str | None, older: str, newer: str) -> bool:
    if not code_repo:
        return False
    try:
        done = subprocess.run(["git", "-C", code_repo, "merge-base", "--is-ancestor", older, newer],
                              capture_output=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return False
    return done.returncode == 0


def already_fixed(root: Path, text: str, owner: str, expect: str | None = None, code_repo: str | None = None) -> dict:
    """Does spec.md already cover the finding (1.194.0)? Re-reads spec.md and its Synced at lines.

    --expect names the words the fix leaves in the spec. A code finding with a
    merge commit is covered when a Synced at line shows that commit or a later
    one (a descendant, with --code-repo). Without a merge commit, every commit
    the finding names must be in the spec. Otherwise nothing can be checked."""
    spec_path = root / "spec.md"
    spec = spec_path.read_text(encoding="utf-8") if spec_path.is_file() else ""
    if expect:
        ok = _norm_words(expect) in _norm_words(spec)
        return {"checked": True, "covered": ok, "missing": [] if ok else [f"spec.md does not say: {expect}"],
                "note": f"spec.md already says: {expect}" if ok else None}
    if owner != "add-to-spec":
        return {"checked": False, "covered": False, "missing": ["nothing to check this against; pass --expect with the words the fix leaves"], "note": None}
    synced = [m.groupdict() for m in SYNCED_LINE.finditer(spec)]
    merge = MERGE_SHA.search(text or "")
    if merge:
        sha = merge.group(1).lower()
        for row in synced:
            have = row["sha"].lower()
            if have.startswith(sha) or sha.startswith(have) or _is_ancestor(code_repo, sha, have):
                where = f"{row['branch']}@{row['sha']}"
                return {"checked": True, "covered": True, "missing": [],
                        "note": f"Synced at shows {where}, at or after the merge commit {sha}."}
        shown = ", ".join(f"{r['branch']}@{r['sha']}" for r in synced) or "no Synced at line"
        return {"checked": True, "covered": False, "note": None,
                "missing": [f"Synced at shows {shown}, not the merge commit {sha} or later"]}
    shas = sorted({m.group(0).lower() for m in SHA_TOKEN.finditer(text or "")})
    if not shas:
        return {"checked": False, "covered": False, "note": None,
                "missing": ["the finding names no commit; pass --expect with the words the fix leaves"]}
    lower = spec.lower()
    missing = [sha for sha in shas if sha not in lower]
    if not missing:
        return {"checked": True, "covered": True, "missing": [], "note": f"spec.md records {', '.join(shas)}."}
    return {"checked": True, "covered": False, "note": None,
            "missing": [f"spec.md does not record {', '.join(missing)}"]}


def _already_fixed_offer(fid: str, check: dict) -> dict:
    return {
        "ok": True,
        "offer": "already-fixed",
        "spec": True,
        "finding": fid,
        "note": f"{fid} is already fixed in the spec: {check['note']}",
        "record": "spec-finding with the same --id and --text, --choice already-done --yes",
        "options": [],
        "already_jumped": False,
        "pause": False,
        "wrote": None,
    }


def _jump_back_offer(fid: str, owner: str = "tighten-spec", command: str = "/crav1-tighten-spec") -> dict:
    if owner == "add-to-spec":
        first = {"id": "add-to-spec", "label": ADD_CHOICE, "recommended": True,
                 "text": f"Open {command} for {fid} only, then the walk goes on with the plan. Why: the spec has not recorded that code yet."}
        path = ADD_TO_SPEC_PATH
    else:
        first = {"id": "tighten-spec", "label": JUMP_CHOICE, "recommended": True,
                 "text": f"Open /crav1-tighten-spec for {fid} only, then the walk goes on with the plan. Why: the plan is built from the spec."}
        path = TIGHTEN_SPEC_PATH
    return {
        "ok": True,
        "offer": "jump-back",
        "spec": True,
        "finding": fid,
        "owner": owner,
        "command": command,
        "background": f"{fid} is about the spec, not the plan.",
        "question": f"Fix {fid} in the spec now, before the plan goes on?",
        "result": f"On yes: {command} runs for {fid} only, then the walk goes on with the plan.",
        "options": [
            first,
            {"id": "open-point", "label": POINT_CHOICE, "recommended": False,
             "text": f"Record {fid} as an open point and go on; the spec stays as it is for now."},
        ],
        "path": path,
        "already_jumped": False,
        "pause": False,
        "wrote": None,
    }


def spec_finding(args: argparse.Namespace) -> None:
    """One jump-back card for a spec finding. A plan finding is left as it is.

    The same finding is the first-seen key, or an alias of a later wording.
    Exact words are not asked again. A close reword is offered as that
    finding, and --new keeps it separate. After a jump, a return is an open
    point and the walk continues. This writes walk-progress.md only with
    --yes. It does not write verify.md, spec.md, plan.md, or tasks.md.
    """
    tag = args.tag or "spec"
    if tag == "plan":
        emit({
            "ok": True,
            "offer": None,
            "spec": False,
            "behave_as_today": True,
            "pause": False,
            "wrote": None,
            "message": "A plan finding stays in /crav1-tighten-plan. This walk does not jump back for it.",
        })
        return
    if tag != "spec":
        fail("tag", "tag must be spec or plan")
    if not args.text or not str(args.text).strip():
        fail("finding", "a spec finding needs --text")
    if not FINDING_ID.fullmatch(args.id or ""):
        fail("finding", "id must be a P# such as P2")
    topic = _norm_topic(args.topic) if args.topic else ""
    if args.topic and not _topic_ok(topic):
        fail("topic", "topic is a short specific name, at least 4 letters, such as approver")
    root = Path(args.root)
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    data = load(root)
    key = _finding_key(args.text)
    jumps = data.get("jumps") or []
    if args.kind and args.kind not in FINDING_KINDS:
        fail("kind", "kind must be code-drift or spec-text")
    owner = finding_owner(args.text, args.kind, topic)
    command = add_to_spec_command(args.text, args.pr, args.branch) if owner == "add-to-spec" else "/crav1-tighten-spec"
    # 1.196.0 (1119d S3): a code-drift text passed as spec-text is asked, not routed silently.
    if args.kind == "spec-text" and not args.choice and finding_owner(args.text, None, topic) == "add-to-spec":
        drift_cmd = add_to_spec_command(args.text, args.pr, args.branch)
        emit({"ok": True, "offer": "kind-conflict", "spec": True, "finding": args.id, "kind_conflict": True,
              "background": f"{args.id} was passed as spec text, but it reads like code the spec has not recorded (a merge or commits).",
              "question": f"Is {args.id} about code the spec has not recorded?",
              "result": f"On yes: it goes to {drift_cmd}; otherwise to /crav1-tighten-spec.",
              "options": [
                  {"id": "add-to-spec", "label": "Yes, record the code (Recommended)", "recommended": True,
                   "text": f"Run the same command with --kind code-drift; {drift_cmd} records it. Why: merged work not marked merged is code drift."},
                  {"id": "tighten-spec", "label": "No, it is spec wording", "recommended": False,
                   "text": "Run the same command with --kind spec-text --choice tighten-spec --yes; /crav1-tighten-spec fixes the wording."},
              ],
              "pause": False, "wrote": None})
        return
    if args.choice == "already-done":
        check = already_fixed(root, args.text, owner, args.expect, args.code_repo)
        if not check["covered"]:
            offer = _jump_back_offer(args.id, owner, command)
            offer["still_missing"] = check["missing"]
            offer["message"] = f"The spec does not show {args.id} fixed yet: " + "; ".join(check["missing"]) + "."
            emit(offer)
            return
        if not args.yes:
            fail("needs-yes", "spec-finding writes the progress file only with --yes, after the card was answered", status=2)
        _append_finding(root, data, "open-point", args.id, args.text, key, "already-fixed", CONTINUE_POINT, topic=topic)
        emit({"ok": True, "offer": None, "spec": True, "finding": args.id, "key": key,
              "recorded": "already-fixed", "note": f"{args.id} is already fixed in the spec: {check['note']}",
              "pause": False, "continue": _continue_list(CONTINUE_POINT), "wrote": PROGRESS_NAME})
        return
    force_new = bool(args.new or args.choice == "new")
    if args.choice == "same":
        first, _aliases, _stored_topic, _finding = _family(jumps, key)
        if first is None:
            close = _close_findings(jumps, args.text, args.id, topic)
            if not close:
                fail("choice", "no recorded finding is close to this wording")
            if len(close) > 1:
                hits = [row for row in close if row["key"] == args.match_key]
                if len(hits) != 1:
                    fail("choice", "more than one recorded finding is close; pass --match-key")
                hit = hits[0]
            else:
                hit = close[0]
                if args.match_key and args.match_key != hit["key"]:
                    fail("choice", "--match-key is not the close finding")
            if not args.yes:
                fail(
                    "needs-yes",
                    "spec-finding writes the progress file only with --yes, after the card was answered",
                    status=2,
                )
            _remember_alias(jumps, hit["key"], key, topic or hit.get("topic") or "")
            first = hit["key"]
        elif not args.yes:
            fail(
                "needs-yes",
                "spec-finding writes the progress file only with --yes, after the card was answered",
                status=2,
            )
        else:
            _remember_alias(jumps, first, key, topic)
    elif not force_new:
        first, _aliases, _stored_topic, _finding = _family(jumps, key)
        if first is None:
            close = _close_findings(jumps, args.text, args.id, topic)
            if close:
                if args.choice in ("tighten-spec", "add-to-spec", "open-point"):
                    emit(_same_or_new_offer(args.id, close))
                    return
                emit(_same_or_new_offer(args.id, close))
                return
    first, aliases, stored_topic, recorded = _family(jumps, key)
    use_topic = stored_topic or topic
    if key != first and key not in aliases and first:
        aliases = list(aliases) + [key]
    jumped = any(first and item.get("key") == first and item["kind"] == "jump-back" for item in jumps)
    pointed = any(first and item.get("key") == first and item["kind"] == "open-point" for item in jumps)
    if jumped or pointed:
        payload = {
            "ok": True,
            "offer": None,
            "spec": True,
            "finding": args.id,
            "key": first,
            "already_jumped": jumped,
            "open_point": True,
            "pause": False,
            "continue": _continue_list(CONTINUE_POINT),
            "refused_second_jump": args.choice in ("tighten-spec", "add-to-spec"),
        }
        if key != first:
            payload["aliased"] = True
        if pointed:
            payload["already_recorded"] = True
            if key != first or (topic and not stored_topic):
                write_progress(root, data)
                payload["wrote"] = PROGRESS_NAME
            else:
                payload["wrote"] = None
            emit(payload)
            return
        if not args.yes:
            payload["needs_record"] = True
            payload["wrote"] = None
            emit(payload)
            return
        _append_finding(
            root, data, "open-point", args.id, recorded or args.text, first or key,
            "open-point", CONTINUE_POINT, topic=use_topic, aliases=aliases,
        )
        payload["recorded"] = "open-point"
        payload["wrote"] = PROGRESS_NAME
        emit(payload)
        return
    if args.choice in (None, "new", "same"):
        check = already_fixed(root, args.text, owner, args.expect, args.code_repo)
        if check["covered"]:
            emit(_already_fixed_offer(args.id, check))
            return
        emit(_jump_back_offer(args.id, owner, command))
        return
    if args.choice not in ("tighten-spec", "add-to-spec", "open-point"):
        fail("choice", "choice must be tighten-spec, add-to-spec, open-point, already-done, same, or new")
    if not args.yes:
        fail(
            "needs-yes",
            "spec-finding writes the progress file only with --yes, after the card was answered",
            status=2,
        )
    if args.choice in ("tighten-spec", "add-to-spec"):
        path = ADD_TO_SPEC_PATH if args.choice == "add-to-spec" else TIGHTEN_SPEC_PATH
        _append_finding(
            root, data, "jump-back", args.id, args.text, key, "jumped",
            CONTINUE_JUMP, path, topic=topic,
        )
        emit({
            "ok": True,
            "offer": None,
            "spec": True,
            "finding": args.id,
            "key": key,
            "recorded": "jump-back",
            "choice": args.choice,
            "command": add_to_spec_command(args.text, args.pr, args.branch) if args.choice == "add-to-spec" else "/crav1-tighten-spec",
            "path": path,
            "scoped_to": args.id,
            "pause": False,
            "continue": _continue_list(CONTINUE_JUMP),
            "wrote": PROGRESS_NAME,
        })
        return
    _append_finding(
        root, data, "open-point", args.id, args.text, key, "open-point",
        CONTINUE_POINT, topic=topic,
    )
    emit({
        "ok": True,
        "offer": None,
        "spec": True,
        "finding": args.id,
        "key": key,
        "recorded": "open-point",
        "choice": "open-point",
        "pause": False,
        "continue": _continue_list(CONTINUE_POINT),
        "wrote": PROGRESS_NAME,
    })


def _git_lines(code_repo: str, *args: str) -> list[str] | None:
    try:
        done = subprocess.run(["git", "-C", code_repo, *args], capture_output=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode != 0:
        return None
    return [line for line in done.stdout.decode("utf-8", "replace").splitlines() if line.strip()]


def short_ref(ref: str | None) -> str:
    return (ref or "").split("/", 1)[1] if (ref or "").startswith("origin/") else (ref or "")


NOTE_COMMITS = re.compile(r"^commits:\s*\[(?P<list>[^\]]*)\]", re.M)


def _recorded_shas(root: Path, spec: str) -> set[str]:
    """Commits the specs repo already records (1.195.0): any sha in spec.md, and every note's commits: list."""
    found = {m.group(0).lower() for m in SHA_TOKEN.finditer(spec)}
    notes = root.resolve().parent.parent / "notes"
    if notes.is_dir():
        for path in notes.rglob("*.md"):
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for m in NOTE_COMMITS.finditer(text):
                found.update(x.strip().strip("'\"").lower() for x in m.group("list").split(",") if x.strip())
    return {x for x in found if len(x) >= 7}


def _recorded(sha: str, known: set[str]) -> bool:
    sha = sha.lower()
    return any(sha.startswith(k) or k.startswith(sha) for k in known)


def _drift_base(code_repo: str, row: dict, synced: list[dict], base: str | None) -> str | None:
    """The branch a work branch merges into: --base, a Synced at base line, origin/develop, origin/main, origin/master."""
    names = [base] if base else []
    names += [r["branch"] for r in synced if r["branch"] in ("develop", "main", "master") and r is not row]
    names += ["develop", "main", "master"]
    sc = start_check_mod()
    for name in names:
        ref = sc.prefer_ref(code_repo, name)
        if ref:
            return ref
    return None


def start_check_mod():
    """The shared start-check helper in crav1-add-to-spec (1.196.0)."""
    return _load_script("crav1-add-to-spec", "start_check.py", "start-check")


_MERGE_FROM = re.compile(r"Merge (?:pull request #?\d+ from \S+?/|branch ')(?P<b>[^'\s]+)|Merged PR \d+: .*? \((?P<b2>[^)]+)\)", re.I)
_SPEC_PATH = re.compile(r"`([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+/?)`")


def _merge_source(commit: str) -> str | None:
    """The branch a merge commit's subject names, when it names one (1.199.0)."""
    m = _MERGE_FROM.search(commit)
    return (m.group("b") or m.group("b2")) if m else None


def _slice_paths(spec: str, code_repo) -> list[str]:
    """Repo paths the spec names in code spans that exist in the code repo (1.199.0)."""
    out = []
    for path in _SPEC_PATH.findall(spec or ""):
        if path.startswith(("docs/", "http")):
            continue
        if code_repo and (Path(code_repo) / path).exists():
            out.append(path)
    return sorted(set(out))


def code_drift(args: argparse.Namespace) -> None:
    """Is the spec's record behind the code (1.194.0)? Read-only, no fetch.

    For each `Synced at:` line in spec.md, counts the commits on the code
    repo's `origin/<branch>` (else `<branch>`) after that commit. `--merged
    <sha>` (a merged PR the walk already saw) is behind unless a Synced at
    commit is that one or later. Behind: one add-to-spec yes card, asked
    before the plan review, and a reviewer note so the reviewer does not echo
    the known drift as a new finding. Writes nothing."""
    root = Path(args.root)
    spec_path = root / "spec.md"
    if not spec_path.is_file():
        fail("root", f"no spec.md in {root}")
    spec = spec_path.read_text(encoding="utf-8")
    synced = [m.groupdict() for m in SYNCED_LINE.finditer(spec)]
    known = _recorded_shas(root, spec)
    sc = start_check_mod()
    fetched = sc.fetch(args.code_repo, getattr(args, "no_fetch", False))
    behind = []
    merged_tips = []
    unlisted: list[dict] = []
    slice_paths = _slice_paths(spec, args.code_repo)
    for row in synced:
        if args.branch and row["branch"] != args.branch:
            continue
        ref = None
        for cand in (f"origin/{row['branch']}", row["branch"]):
            if _git_lines(args.code_repo, "rev-parse", "--verify", "--quiet", cand) is not None:
                ref = cand
                break
        if not ref:
            continue
        allc = _git_lines(args.code_repo, "log", "--format=%h %s", f"{row['sha']}..{ref}") or []
        base_ref = _drift_base(args.code_repo, row, synced, args.base)
        own = allc
        if base_ref and base_ref != ref and row["branch"] not in ("develop", "main", "master"):
            own = _git_lines(args.code_repo, "log", "--format=%h %s", f"{row['sha']}..{ref}", f"^{base_ref}") or []
            # A merge commit that brings the base in is a base merge-in, not the branch's own work.
            ins = set(_git_lines(args.code_repo, "log", "--merges", "--format=%h", f"{row['sha']}..{ref}", f"^{base_ref}") or [])
            ins = {h for h in ins if _git_lines(args.code_repo, "merge-base", "--is-ancestor", f"{h}^2", base_ref) is not None}
            own = [c for c in own if c.split()[0] not in ins]
        merged_in = len(allc) - len(own)
        # 1.199.0: base commits merged in from branches the spec does not list
        # that touch this slice's files are drift too, not "merged in".
        if merged_in and slice_paths:
            listed = {r["branch"] for r in synced}
            own_set = {c.split()[0] for c in own}
            for commit in allc:
                short = commit.split()[0]
                if short in own_set or _recorded(short, known):
                    continue
                files = _git_lines(args.code_repo, "show", "--name-only", "--format=", short) or []
                source = _merge_source(commit)
                if source and source in listed:
                    continue
                if any(f.strip() and any(f.strip().startswith(pth) for pth in slice_paths) for f in files):
                    unlisted.append({"branch": row["branch"], "commit": commit, "from": source or "an unlisted branch"})
        # 1.196.0: a work branch whose tip is already in the base is merged; take it in
        # unless the merge (or a later commit) is already recorded.
        if base_ref and base_ref != ref and row["branch"] not in ("develop", "main", "master"):
            hit = sc.tip_merged(args.code_repo, ref, base_ref)
            if hit and not _recorded(hit["merge_short"], known) and not any(
                    _is_ancestor(args.code_repo, hit["merge"], r["sha"]) for r in synced):
                merged_tips.append({"branch": row["branch"], "sha": hit["merge_short"], "pr": hit["pr"],
                                    "base": short_ref(base_ref)})
        new = [c for c in own if not _recorded(c.split()[0], known)]
        if new:
            behind.append({"branch": row["branch"], "synced": row["sha"], "ref": ref, "base": base_ref,
                           "count": len(new), "total": len(allc), "already_recorded": len(own) - len(new),
                           "base_merge_ins": merged_in, "commits": new[:5]})
    merged = None
    if args.merged:
        sha = args.merged.lower()
        hit = any(r["sha"].lower().startswith(sha) or sha.startswith(r["sha"].lower())
                  or _is_ancestor(args.code_repo, sha, r["sha"]) for r in synced)
        if not hit:
            merged = {"sha": sha, "pr": args.pr}
    if not merged and merged_tips:
        first = merged_tips[0]
        merged = {"sha": first["sha"], "pr": first["pr"], "branch": first["branch"], "tip_merged": True}
        if not args.pr and first["pr"]:
            args.pr = first["pr"]
    if unlisted and not behind:
        first = unlisted[0]["branch"]
        behind.append({"branch": first, "synced": next(r["sha"] for r in synced if r["branch"] == first), "ref": first,
                       "base": None, "count": 0, "total": 0, "already_recorded": 0, "base_merge_ins": 0, "commits": []})
    if not behind and not merged:
        emit({"ok": True, "behind": False, "offer": None, "wrote": None, "fetch": fetched,
              "message": "The spec's Synced at lines are current with the code; no add-to-spec offer."})
        return
    target = args.branch or (behind[0]["branch"] if behind else (merged or {}).get("branch"))
    command = add_to_spec_command("", args.pr, target)
    parts = [f"{b['count']} commit{'s' if b['count'] != 1 else ''} on {b['branch']} after Synced at {b['synced']} not recorded yet"
             + (f" ({b['already_recorded'] + b['base_merge_ins']} more already recorded or merged in from {short_ref(b['base'])})"
                if b['already_recorded'] + b['base_merge_ins'] else "") for b in behind]
    parts = [part for part, b in zip(parts, behind) if b["count"]]
    if unlisted:
        n = len(unlisted)
        parts.append(f"{n} commit{'s' if n != 1 else ''} merged in from the base touch this slice's files "
                     f"and come from a branch the spec does not list")
    if merged:
        parts.append(f"PR {args.pr} merged at {merged['sha']}" if args.pr else f"a merge at {merged['sha']}")
    what = "; ".join(parts)
    emit({
        "ok": True,
        "behind": True,
        "offer": "add-to-spec",
        "drift": behind,
        "merged": merged,
        "merged_tips": merged_tips,
        "unlisted": unlisted[:5],
        "fetch": fetched,
        "command": command,
        "path": ADD_TO_SPEC_PATH,
        "background": f"The spec's record is behind the code: {what}.",
        "question": "Record those code changes in the spec before the plan review?",
        "result": f"On yes: {command} records them, then the plan is updated and reviewed.",
        "options": [
            {"id": "add-to-spec", "label": "Record the code changes first (Recommended)", "recommended": True,
             "text": f"Open {command} now, then update the plan for what it changed and start the plan review. Why: the review then reads a current spec."},
            {"id": "review-now", "label": PLAIN_LABELS["review-now"], "recommended": False,
             "text": "Start the plan review now; the spec stays behind the code and the walk names add-to-spec at the end."},
        ],
        "reviewer_note": f"Known and already offered: {what}. Do not report it as a new finding.",
        "wrote": None,
    })


# --- tickable (1.196.0) -----------------------------------------------------
_ACC_HEAD = re.compile(r"^##\s+Acceptance criteria\s*$", re.M | re.I)
_VERIFY_ACC_HEAD = re.compile(r"^##\s+Acceptance\b.*details\s*$", re.M | re.I)
_EVIDENCE_FILE = re.compile(r"[\w./-]+\.[A-Za-z0-9]{1,6}(?::\d+)?")
_TASK_OPEN = re.compile(r"^\s*-\s*\[( |x|X)\]\s*T(\d+)\b")
_ITEM_REF = re.compile(r"\bitem\s+(\d+)\b", re.I)


def _tick_words(text: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", " ", text.lower()).split())


def _section(text: str, head: re.Pattern) -> str:
    m = head.search(text)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"^##\s", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def _acceptance_lines(spec: str) -> list[dict]:
    out = []
    for line in _section(spec, _ACC_HEAD).splitlines():
        m = re.match(r"^\s*-\s*\[( |x|X)\]\s*(.*)$", line)
        if m and m.group(2).strip():
            out.append({"item": len(out) + 1, "text": m.group(2).strip(), "ticked": m.group(1).lower() == "x",
                        "line": line})
    return out


def _verify_acc_rows(verify: str) -> list[dict]:
    rows = []
    for line in _section(verify, _VERIFY_ACC_HEAD).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or not re.fullmatch(r"A\d+", cells[0]):
            continue
        rows.append({"id": cells[0], "acceptance": cells[1], "evidence": cells[2], "result": cells[3],
                     "tasks": re.findall(r"T\d+", cells[4])})
    return rows


def _row_passes_on_base(row: dict) -> bool:
    result = row["result"].lower()
    return result.startswith("pass") and "fail" not in result and "on branch" not in result and "feat/" not in result


def _match_item(row: dict, items: list[dict]) -> dict | None:
    ref = _ITEM_REF.search(row["acceptance"])
    if ref:
        n = int(ref.group(1))
        return next((i for i in items if i["item"] == n), None)
    want = _tick_words(row["acceptance"])
    if not want:
        return None
    hits = [i for i in items if _tick_words(i["text"]) == want
            or (len(want) >= 12 and (_tick_words(i["text"]).startswith(want) or want.startswith(_tick_words(i["text"]))))]
    return hits[0] if len(hits) == 1 else None


# --- review-packet (1.197.0): a scoped input for the plan reviewer, never the whole spec.
_PACKET_TASK = re.compile(r"^\s*-\s*\[( |x|X)\]\s*(T\d+)\b.*$")
_SPEC_REF = re.compile(r"\(spec:\s*([^)]+)\)", re.I)
QUICK_MAX_TASKS = 3
QUICK_MAX_LINES = 40
SECTION_MAX_LINES = 60


def _git_out(root: Path, *args: str) -> str | None:
    try:
        proc = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=20, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout if proc.returncode == 0 else None


def _changed_lines(root: Path, since: str | None) -> tuple[list[str], int]:
    """Added lines in tasks.md and plan.md since a ref (or uncommitted), and how many lines changed."""
    args = ["diff", "--unified=0"] + ([since] if since else ["HEAD"]) + ["--", "tasks.md", "plan.md"]
    out = _git_out(root, *args)
    if out is None:
        return [], -1
    added = [line[1:] for line in out.splitlines() if line.startswith("+") and not line.startswith("+++")]
    removed = [line for line in out.splitlines() if line.startswith("-") and not line.startswith("---")]
    return added, len(added) + len(removed)


def _packet_section(text: str, heading: str) -> str:
    m = re.search(rf"(?m)^##+\s+{re.escape(heading)}\s*$", text)
    if not m:
        return ""
    rest = text[m.start():]
    nxt = re.search(r"(?m)^##\s+", rest[3:])
    return rest[: nxt.start() + 3].rstrip() if nxt else rest.rstrip()


def _spec_range(spec_lines: list[str], ref: str) -> tuple[int, int] | None:
    """Line range (1-based, inclusive) of the spec section that holds the ref words."""
    want = _tick_words(ref)
    if not want:
        return None
    for idx, line in enumerate(spec_lines):
        if want in _tick_words(line):
            start = idx
            while start > 0 and not spec_lines[start].startswith("#"):
                start -= 1
            end = idx + 1
            while end < len(spec_lines) and not spec_lines[end].startswith("#") and end - start < SECTION_MAX_LINES:
                end += 1
            return start + 1, end
    return None


def review_packet(root: Path, since: str | None = None, tasks_arg: str | None = None) -> dict:
    spec_path, plan_path, tasks_path = root / "spec.md", root / "plan.md", root / "tasks.md"
    if not tasks_path.is_file():
        fail("root", f"no tasks.md in {root}")
    spec = spec_path.read_text(encoding="utf-8") if spec_path.is_file() else ""
    plan = plan_path.read_text(encoding="utf-8") if plan_path.is_file() else ""
    task_lines = {}
    for line in tasks_path.read_text(encoding="utf-8").splitlines():
        m = _PACKET_TASK.match(line)
        if m:
            task_lines[m.group(2)] = (m.group(1) == " ", line)
    if tasks_arg:
        wanted = [t.strip() for t in tasks_arg.split(",") if t.strip()]
        how, changed_n = "named", -1
    else:
        added, changed_n = _changed_lines(root, since)
        wanted = [m.group(2) for m in (_PACKET_TASK.match(a) for a in added) if m]
        how = "changed"
        if not wanted:
            wanted = [t for t, (is_open, _l) in task_lines.items() if is_open]
            how = "open"
    wanted = [t for t in dict.fromkeys(wanted) if t in task_lines]
    spec_lines = spec.splitlines()
    ranges = []
    for tid in wanted:
        for ref in _SPEC_REF.findall(task_lines[tid][1]):
            for part in re.split(r"[;,]", ref):
                rng = _spec_range(spec_lines, part)
                if rng and rng not in ranges:
                    ranges.append(rng)
    ranges.sort()
    parts = ["# Plan review packet", "", f"Tasks ({how}): " + (", ".join(wanted) or "none"), ""]
    parts += ["## Tasks", ""] + [task_lines[t][1] for t in wanted] + [""]
    for heading in ("Risks", "Linter"):
        sec = _packet_section(plan, heading)
        if sec:
            parts += [f"## plan.md {heading}", "", sec.split("\n", 1)[1].strip() if "\n" in sec else "", ""]
    parts += ["## spec.md sections (line ranges)", ""]
    for start, end in ranges:
        parts += [f"### spec.md lines {start}-{end}", ""] + spec_lines[start - 1:end] + [""]
    quick = bool(wanted) and len(wanted) <= QUICK_MAX_TASKS and 0 <= changed_n <= QUICK_MAX_LINES
    return {"tasks": wanted, "how": how, "spec_ranges": [f"{a}-{b}" for a, b in ranges],
            "spec_bytes": len(spec.encode("utf-8")), "changed_lines": changed_n, "quick": quick,
            "text": "\n".join(parts).rstrip() + "\n"}


def review_packet_cmd(args: argparse.Namespace) -> None:
    """Write the plan reviewer's input packet (1.197.0). The reviewer reads it, never spec.md whole."""
    root = Path(args.root)
    packet = review_packet(root, args.since, args.tasks)
    import tempfile
    # Outside the repo, so it is never committed or counted as uncommitted.
    out = Path(args.out) if args.out else Path(tempfile.gettempdir()) / f"crav1-review-packet-{root.resolve().name}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(packet.pop("text"), encoding="utf-8")
    mode = "quick" if packet["quick"] else "full"
    line = (f"Review packet: {len(packet['tasks'])} task{'s' if len(packet['tasks']) != 1 else ''}, "
            f"{len(packet['spec_ranges'])} spec section{'s' if len(packet['spec_ranges']) != 1 else ''}, {mode} review.")
    emit({"ok": True, **packet, "mode": mode, "path": str(out), "line": line})


def tickable_report(root: Path) -> dict:
    spec_path, verify_path, tasks_path = root / "spec.md", root / "verify.md", root / "tasks.md"
    if not spec_path.is_file():
        fail("root", f"no spec.md in {root}")
    spec = spec_path.read_text(encoding="utf-8")
    items = _acceptance_lines(spec)
    rows = _verify_acc_rows(verify_path.read_text(encoding="utf-8")) if verify_path.is_file() else []
    tasks = tasks_path.read_text(encoding="utf-8") if tasks_path.is_file() else ""
    open_tasks = {}
    for line in tasks.splitlines():
        m = _TASK_OPEN.match(line)
        if m and m.group(1) == " ":
            open_tasks[f"T{m.group(2)}"] = line
    found, cards, waiting = [], [], []
    for row in rows:
        item = _match_item(row, items)
        if item is None or item["ticked"]:
            continue
        files = sorted({f.split(":")[0] for f in _EVIDENCE_FILE.findall(row["evidence"])})
        passes = _row_passes_on_base(row)
        # 1.197.0: only a failing row, or a passing row with no evidence, is a question.
        # An untested or pending row waits on its tasks with no question.
        if passes and not files:
            cards.append({"item": item["item"], "text": item["text"], "row": row["id"], "result": row["result"],
                          "why": "passes with no evidence"})
            continue
        if not passes:
            if re.match(r"(?i)\s*fail", row["result"] or ""):
                cards.append({"item": item["item"], "text": item["text"], "row": row["id"], "result": row["result"],
                              "why": "failing"})
            else:
                waiting.append(item["item"])
            continue
        touching = [t for t in row["tasks"] if t in open_tasks]
        for tid, line in open_tasks.items():
            if tid not in touching and any(Path(f).name in line for f in files):
                touching.append(tid)
        found.append({"item": item["item"], "text": item["text"], "row": row["id"], "evidence_files": files,
                      "open_tasks_touching": touching, "action": "tick-recheck" if touching else "tick"})
    return {"items": found, "cards": cards, "waiting": waiting}


def _add_recheck(tasks: str, tid: str, note: str) -> str:
    out = []
    for line in tasks.splitlines(keepends=True):
        m = _TASK_OPEN.match(line)
        if m and f"T{m.group(2)}" == tid and note not in line:
            body = line.rstrip("\r\n")
            ending = line[len(body):]
            vm = re.search(r"\(verify:\s*([^)]*)\)", body)
            if vm:
                body = body[: vm.end() - 1] + f"; {note}" + body[vm.end() - 1:]
            else:
                body = body + f" (verify: {note})"
            line = body + ending
        out.append(line)
    return "".join(out)


def tickable(args: argparse.Namespace) -> None:
    """Acceptance items a passing verify row on the base already proves (1.196.0). Owned by tighten-spec.

    No card when the evidence is clear: the item is ticked. When a later open
    task touches the evidence files, it is still ticked now and that task's
    verify note gets `recheck item N (verify A#)`. Only a failing row, or a passing
    row with no evidence, is listed under `cards` (1.197.0); untested rows are `waiting`. Writes only with --write."""
    root = Path(args.root)
    report = tickable_report(root)
    wrote = []
    if args.write and report["items"]:
        spec_path = root / "spec.md"
        spec = spec_path.read_text(encoding="utf-8")
        items = {i["item"]: i for i in _acceptance_lines(spec)}
        for hit in report["items"]:
            line = items[hit["item"]]["line"]
            spec = spec.replace(line, line.replace("[ ]", "[x]", 1), 1)
        spec_path.write_text(spec, encoding="utf-8")
        wrote.append("spec.md")
        tasks_path = root / "tasks.md"
        if tasks_path.is_file() and any(h["open_tasks_touching"] for h in report["items"]):
            tasks = tasks_path.read_text(encoding="utf-8")
            for hit in report["items"]:
                for tid in hit["open_tasks_touching"]:
                    tasks = _add_recheck(tasks, tid, f"recheck item {hit['item']} (verify {hit['row']})")
            tasks_path.write_text(tasks, encoding="utf-8")
            wrote.append("tasks.md")
    line = None
    if report["items"]:
        parts = []
        for h in report["items"]:
            extra = f", recheck on {', '.join(h['open_tasks_touching'])}" if h["open_tasks_touching"] else ""
            parts.append(f"item {h['item']} ({h['row']}{extra})")
        verb = "Ticked" if args.write else "Can tick"
        n = len(parts)
        line = f"{verb} {n} acceptance item{'s' if n != 1 else ''} from verify: " + ", ".join(parts) + "."
    wait_n = len(report["waiting"])
    wait_line = (f"{wait_n} acceptance item{'s wait' if wait_n != 1 else ' waits'} on {'their' if wait_n != 1 else 'its'} tasks."
                 if wait_n else None)
    emit({"ok": True, **report, "line": line, "waiting_line": wait_line, "wrote": wrote or None})


# Hash lines resolve-stamps may rewrite (1.139.0). Done, Result, findings,
# notes, and Acknowledged stamp are recorded facts and are not in this set.
_STAMP_KEYS = frozenset({
    "Spec version",
    "Plan version",
    "Tasks version",
    "Verify version",
    "Spec body",
    "Questions version",
    "Kept questions",
    "Section stamps",
    "Question ids",
    "Content stamp",
    "Key",
    "Playbook",
})
_HEX12 = re.compile(r"^[0-9a-fA-F]{12}$")
_KEPT_VALUE = re.compile(r"^(?:none|[0-9a-fA-F]{12}(?: [0-9a-fA-F]{12})*)$")


def _stamp_label(line: str) -> str | None:
    text = line.strip()
    if not text:
        return ""
    if text.startswith("Playbook: "):
        _path, sep, hashed = text[len("Playbook: "):].rpartition("@")
        if sep and _path and _HEX12.fullmatch(hashed):
            return "Playbook"
        return None
    key, sep, value = text.partition(": ")
    if not sep or key not in _STAMP_KEYS:
        return None
    if key == "Content stamp":
        return key if value == CONTENT_STAMP else None
    if key == "Kept questions":
        return key if _KEPT_VALUE.fullmatch(value) else None
    if key == "Section stamps":
        return key if _SECTION_VALUE.fullmatch(value) else None
    if key == "Question ids":
        return key if _QUESTION_ID_VALUE.fullmatch(value) else None
    if value == "missing" or _HEX12.fullmatch(value):
        return key
    return None


def _is_stamp_line(line: str) -> bool:
    return _stamp_label(line) is not None


def _marker_kind(line: str) -> str | None:
    if line.startswith("<<<<<<<"):
        return "start"
    if line.startswith("|||||||"):
        return "base"
    if line.startswith("=======") and set(line.strip()) <= {"="}:
        return "mid"
    if line.startswith(">>>>>>>"):
        return "end"
    return None


def _parse_hunks(lines: list[str]) -> tuple[list[dict], str | None]:
    hunks: list[dict] = []
    i = 0
    while i < len(lines):
        kind = _marker_kind(lines[i])
        if kind is None:
            i += 1
            continue
        if kind != "start":
            return [], "conflict marker out of order"
        start = i
        i += 1
        ours: list[str] = []
        base: list[str] | None = None
        while i < len(lines) and _marker_kind(lines[i]) not in ("mid", "base"):
            if _marker_kind(lines[i]) in ("start", "end"):
                return [], "broken conflict marker"
            ours.append(lines[i])
            i += 1
        if i >= len(lines):
            return [], "conflict marker has no end"
        if _marker_kind(lines[i]) == "base":
            base = []
            i += 1
            while i < len(lines) and _marker_kind(lines[i]) != "mid":
                if _marker_kind(lines[i]) is not None:
                    return [], "broken conflict marker"
                base.append(lines[i])
                i += 1
        if i >= len(lines) or _marker_kind(lines[i]) != "mid":
            return [], "conflict marker has no separator"
        i += 1
        theirs: list[str] = []
        while i < len(lines) and _marker_kind(lines[i]) != "end":
            if _marker_kind(lines[i]) is not None:
                return [], "nested conflict marker"
            theirs.append(lines[i])
            i += 1
        if i >= len(lines):
            return [], "conflict marker has no end"
        i += 1
        hunks.append({
            "index": len(hunks) + 1,
            "start": start,
            "end": i,
            "ours": ours,
            "theirs": theirs,
            "base": base,
        })
    return hunks, None


def _enclosing_step(lines: list[str], start: int) -> str | None:
    i = start - 1
    while i >= 0:
        if lines[i].startswith(">>>>>>>"):
            while i >= 0 and not lines[i].startswith("<<<<<<<"):
                i -= 1
            i -= 1
            continue
        text = lines[i].strip()
        if text.startswith("- Step: "):
            return text[len("- Step: "):]
        if text.startswith("- Extra: "):
            return text[len("- Extra: "):]
        if text.startswith("- Jump-back: ") or text.startswith("- Open point: "):
            return text
        i -= 1
    return None


def _hunk_names(hunk: dict) -> list[str]:
    names: list[str] = []
    for line in hunk["ours"] + hunk["theirs"] + (hunk["base"] or []):
        text = line.strip()
        if not text:
            continue
        key = text.split(":", 1)[0].strip()
        if key not in names:
            names.append(key)
    return names


def _classify_hunk(hunk: dict, lines: list[str]) -> None:
    sides = hunk["ours"] + hunk["theirs"] + (hunk["base"] or [])
    hunk["step"] = _enclosing_step(lines, hunk["start"])
    hunk["lines"] = _hunk_names(hunk)
    filled = [line for line in sides if line.strip()]
    if filled and all(parse_branch_run(line) for line in filled):
        # Status lines only (1.155.0): settled by the newest time per branch.
        hunk["class"] = "stamp"
        hunk["step"] = "- Branch runs"
        hunk["status"] = True
        return
    stamp = all(_is_stamp_line(line) for line in sides)
    hunk["class"] = "stamp" if stamp and hunk["step"] else "blocked"


def _reconstruct(lines: list[str], hunks: list[dict], side: str) -> str:
    out: list[str] = []
    cursor = 0
    for hunk in hunks:
        out.extend(lines[cursor:hunk["start"]])
        out.extend(hunk[side])
        cursor = hunk["end"]
    out.extend(lines[cursor:])
    return "\n".join(out) + "\n"


def _try_parse(text: str) -> tuple[dict | None, str | None]:
    caught: dict[str, str] = {}

    def boom(code: str, message: str, status: int = 1) -> None:
        caught["message"] = message
        raise RuntimeError(message)

    original = globals()["fail"]
    globals()["fail"] = boom
    try:
        return parse_progress(text), None
    except RuntimeError:
        return None, caught.get("message", "progress file could not be read")
    finally:
        globals()["fail"] = original


def _find_repo(start: Path) -> Path | None:
    for base in [start, *start.parents]:
        if (base / ".git").exists():
            return base
        if base.parent == base:
            break
    return None


def _git_bytes(repo: Path, spec: str) -> bytes | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "show", spec],
            capture_output=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def _pair_from_bytes(blob: bytes | None) -> tuple[str | None, bytes | None]:
    if blob is None:
        return None, None
    try:
        return blob.decode("utf-8"), blob
    except UnicodeDecodeError:
        return blob.decode("utf-8", "replace"), blob


def _tree_from_folder(folder: Path | None) -> dict[str, tuple[str | None, bytes | None]]:
    tree: dict[str, tuple[str | None, bytes | None]] = {}
    for key, name in FILE_OF.items():
        tree[key] = _read_pair(folder / name) if folder is not None else (None, None)
    return tree


def _tree_from_git(repo: Path, rev: str, rel: str) -> dict[str, tuple[str | None, bytes | None]]:
    tree: dict[str, tuple[str | None, bytes | None]] = {}
    prefix = rel.strip("/")
    for key, name in FILE_OF.items():
        spec = f"{rev}:{prefix}/{name}" if prefix else f"{rev}:{name}"
        tree[key] = _pair_from_bytes(_git_bytes(repo, spec))
    return tree


def _has_conflict(text: str | None) -> bool:
    if not text:
        return False
    return any(line.startswith("<<<<<<<") for line in text.splitlines())


def _piece_text(text: str | None, part: str) -> str | None:
    if text is None:
        return None
    lf = _lf_text(text)
    if part == "spec_body":
        body, _questions = spec_parts(lf)
        return body
    if part == "questions":
        _body, questions = spec_parts(lf)
        return questions
    return lf


def _field_rows(step: str, body: dict) -> list[tuple[str, str, str]]:
    """(body key, part, kind) for hash fields this step records."""
    if step == "playbook":
        return [("playbook_version", "file", "playbook")]
    rows: list[tuple[str, str, str]] = []
    for token in COVERS.get(step, ()):
        if token == "playbook":
            continue
        if token in body:
            rows.append((token, "file", token))
    if "spec_body" in body:
        rows.append(("spec_body", "spec_body", "spec"))
    if "questions" in body:
        rows.append(("questions", "questions", "questions"))
    if "kept_questions" in body:
        rows.append(("kept_questions", "kept", "questions"))
    return rows


def _kept_line_from(spec_text: str | None, tasks_text: str | None) -> str:
    if not spec_text:
        return "none"
    task_ids = None
    if tasks_text is not None:
        task_ids = blocks_mod().task_ids_from_tasks(tasks_text)
    questions = blocks_mod().kept_open(
        spec_text,
        task_ids=task_ids,
        resolve_recorded=True,
    )
    keys: list[str] = []
    for question in questions:
        key = question.get("key") or blocks_mod().question_key(question.get("text") or "")
        if key and key not in keys:
            keys.append(key)
    return " ".join(keys) if keys else "none"


def _playbook_pair(body: dict, folder: Path | None, repo: Path | None, rev: str | None) -> tuple[str | None, bytes | None]:
    rel = body.get("playbook")
    if not rel:
        return None, None
    if folder is not None:
        direct = folder / rel
        if direct.is_file():
            return _read_pair(direct)
        found = find_playbook(folder, rel)
        if found is not None:
            return _read_pair(found)
    if repo is not None and rev:
        return _pair_from_bytes(_git_bytes(repo, f"{rev}:{rel}"))
    return None, None


def _field_matches(body: dict, field: str, part: str, kind: str, tree: dict, playbook: tuple[str | None, bytes | None]) -> bool:
    """1.138 stamp match against this side's file. No HEAD fallback.

    During a merge, HEAD is one side. The side file is passed in, so the
    HEAD lookup in stamp_matches would answer a different question.
    """
    normalized = body.get("content_stamp") == CONTENT_STAMP
    if field == "kept_questions":
        spec_text = tree.get("spec", (None, None))[0]
        tasks_text = tree.get("tasks", (None, None))[0]
        return body.get("kept_questions") == _kept_line_from(spec_text, tasks_text)
    if field == "playbook_version":
        text, raw = playbook
        return stamp_matches(
            body.get("playbook_version"), text, "playbook", normalized,
            raw_bytes=raw, path=None, part="file",
        )
    if part == "file":
        text, raw = tree.get(kind, (None, None))
        return stamp_matches(
            body.get(field), text, kind, normalized,
            raw_bytes=raw, path=None, part="file",
        )
    text, _raw = tree.get("spec", (None, None))
    piece = _piece_text(text, part)
    use_kind = "spec" if part == "spec_body" else "questions"
    return stamp_matches(
        body.get(field), piece, use_kind, normalized,
        raw_bytes=None, path=None, part=part,
    )


def _progress_only(part: str, kind: str, side_tree: dict, merged_tree: dict, ours_body: dict, theirs_body: dict) -> bool:
    """True when the merged piece differs from this side only by 1.138 progress."""
    if part == "kept":
        part = "questions"
        kind = "questions"
    if kind == "playbook":
        if ours_body.get("playbook") != theirs_body.get("playbook"):
            return False
        side = side_tree.get("playbook", (None, None))[0]
        merged = merged_tree.get("playbook", (None, None))[0]
        use_kind = "playbook"
    elif part == "file":
        side = side_tree.get(kind, (None, None))[0]
        merged = merged_tree.get(kind, (None, None))[0]
        use_kind = kind
    else:
        side = side_tree.get("spec", (None, None))[0]
        merged = merged_tree.get("spec", (None, None))[0]
        use_kind = "spec" if part == "spec_body" else "questions"
    if _has_conflict(side) or _has_conflict(merged):
        return False
    if side is None and merged is None:
        return True
    if side is None or merged is None:
        return False
    left = _piece_text(side, part)
    right = _piece_text(merged, part)
    if left is None or right is None:
        return False
    return normalize_text(use_kind, left) == normalize_text(use_kind, right)


def _merged_hash(field: str, part: str, kind: str, tree: dict, playbook: tuple[str | None, bytes | None]) -> str:
    if field == "kept_questions":
        spec_text = tree.get("spec", (None, None))[0]
        tasks_text = tree.get("tasks", (None, None))[0]
        return _kept_line_from(spec_text, tasks_text)
    if field == "playbook_version":
        text, _raw = playbook
        if text is None:
            return "missing"
        return version_text(normalize_text("playbook", text))
    if part == "file":
        text = tree.get(kind, (None, None))[0]
        if text is None:
            return "missing"
        return version_text(normalize_text(kind, _lf_text(text)))
    text = tree.get("spec", (None, None))[0]
    piece = _piece_text(text, part)
    if piece is None:
        return "missing"
    use_kind = "spec" if part == "spec_body" else "questions"
    return version_text(normalize_text(use_kind, piece))


def _human_field(field: str) -> str:
    if field == "spec_body":
        return "Spec body"
    if field == "questions":
        return "Questions version"
    if field == "kept_questions":
        return "Kept questions"
    if field == "playbook_version":
        return "Playbook"
    if field == "content_stamp":
        return "Content stamp"
    return LABEL.get(field, field)


def _join_steps(names: list[str]) -> str:
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + ", and " + names[-1]


def _decide_step(step: str, ours_body: dict, theirs_body: dict, ours: dict, theirs: dict, merged: dict, ours_play, theirs_play, merged_play) -> dict:
    """Restamp rule (1.139.0).

    Start from the upstream step. A hash line is rewritten to the merged
    file's normalized hash only when at least one side's recorded hash
    matches that side's file, and every matching side differs from the
    merged file only by progress (line endings, and for spec and tasks a
    checkbox or a PR or done mark). Otherwise the upstream hash stays, so
    a real edit still reopens the steps that edit affects. When every hash
    on the step is that merged normalized hash, write Content stamp.
    """
    rows = {row[0]: row for row in _field_rows(step, theirs_body)}
    for row in _field_rows(step, ours_body):
        rows.setdefault(row[0], row)
    differing = [rows[key] for key in rows if ours_body.get(key) != theirs_body.get(key)]
    restamped: list[str] = []
    kept: list[str] = []
    reopen = False
    for field, part, kind in differing:
        witnesses = []
        for body, tree, play in (
            (ours_body, ours, ours_play),
            (theirs_body, theirs, theirs_play),
        ):
            if _field_matches(body, field, part, kind, tree, play):
                witnesses.append((body, tree, play))
        progress = bool(witnesses) and all(
            _progress_only(part, kind, tree, merged, ours_body, theirs_body)
            for _body, tree, _play in witnesses
        )
        label = _human_field(field)
        if progress:
            theirs_body[field] = _merged_hash(field, part, kind, merged, merged_play)
            restamped.append(label)
        else:
            kept.append(label)
            if witnesses:
                reopen = True
    normalized_now = True
    for field, part, kind in rows.values():
        if field == "kept_questions":
            continue
        expect = _merged_hash(field, part, kind, merged, merged_play)
        if theirs_body.get(field) != expect:
            normalized_now = False
            break
    had_stamp = theirs_body.get("content_stamp") == CONTENT_STAMP
    if rows and normalized_now:
        if not had_stamp:
            restamped.append("Content stamp")
        theirs_body["content_stamp"] = CONTENT_STAMP
    elif not had_stamp:
        theirs_body.pop("content_stamp", None)
    return {"step": step, "restamped": restamped, "kept": kept, "reopen": reopen}


def _align_jump_keys(ours: dict, theirs: dict) -> list[dict]:
    actions = []
    ours_by = {(jump["kind"], jump["id"]): jump for jump in ours.get("jumps") or []}
    for jump in theirs.get("jumps") or []:
        twin = ours_by.get((jump["kind"], jump["id"]))
        if twin is None or twin.get("finding") != jump.get("finding"):
            continue
        recomputed = _finding_key(jump["finding"])
        if jump.get("key") != recomputed or twin.get("key") != recomputed:
            if jump.get("key") != twin.get("key") or jump.get("key") != recomputed:
                jump["key"] = recomputed
                title = "Jump-back" if jump["kind"] == "jump-back" else "Open point"
                actions.append({
                    "step": f"{title} {jump['id']}",
                    "restamped": ["Key"],
                    "kept": [],
                    "reopen": False,
                })
    return actions


def _report_line(actions: list[dict], path_name: str) -> str:
    restamped: dict[tuple[str, ...], list[str]] = {}
    kept: dict[tuple[str, ...], list[str]] = {}
    reopen = False
    for action in actions:
        if action["restamped"]:
            restamped.setdefault(tuple(action["restamped"]), []).append(action["step"])
        if action["kept"]:
            kept.setdefault(tuple(action["kept"]), []).append(action["step"])
            if action["reopen"]:
                reopen = True
    bits = []
    for labels, steps in restamped.items():
        bits.append(f"restamped {', '.join(labels)} on {_join_steps(steps)}")
    for labels, steps in kept.items():
        bits.append(f"kept upstream {', '.join(labels)} on {_join_steps(steps)}")
    if not bits:
        return f"Settled {path_name} stamp conflicts."
    line = f"Settled {path_name}: " + "; ".join(bits)
    if reopen:
        line += ", so a real edit still reopens the steps it affects"
    return line + "."


def _load_sides(args: argparse.Namespace, root: Path) -> tuple[dict, dict, dict, tuple, tuple, tuple, Path | None]:
    repo = _find_repo(root)
    ours_root = Path(args.ours_root) if args.ours_root else None
    theirs_root = Path(args.theirs_root) if args.theirs_root else None
    if (ours_root is None) != (theirs_root is None):
        fail("need-sides", "pass both --ours-root and --theirs-root, or neither to read HEAD and MERGE_HEAD")
    if ours_root is not None:
        ours = _tree_from_folder(ours_root)
        theirs = _tree_from_folder(theirs_root)
        merged = _tree_from_folder(root)
        return ours, theirs, merged, (ours_root, None, None), (theirs_root, None, None), (root, None, None), repo
    if repo is None:
        fail("need-sides", "walk-progress.md is not in a git repo; pass --ours-root and --theirs-root")
    git_dir = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--git-path", "MERGE_HEAD"],
        capture_output=True, text=True, check=False,
    )
    if git_dir.returncode != 0:
        fail("not-a-merge", "no merge in progress; pass --ours-root and --theirs-root")
    marker = Path(git_dir.stdout.strip())
    if not marker.is_absolute():
        marker = repo / git_dir.stdout.strip()
    if not marker.is_file():
        fail("not-a-merge", "no merge in progress; pass --ours-root and --theirs-root")
    try:
        rel = root.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        fail("root", "the spec folder is not inside the git repo")
    ours = _tree_from_git(repo, "HEAD", rel)
    theirs = _tree_from_git(repo, "MERGE_HEAD", rel)
    merged = _tree_from_folder(root)
    return (
        ours, theirs, merged,
        (None, repo, "HEAD"),
        (None, repo, "MERGE_HEAD"),
        (root, repo, None),
        repo,
    )


def _play_for(body: dict, where: tuple) -> tuple[str | None, bytes | None]:
    folder, repo, rev = where
    return _playbook_pair(body, folder, repo, rev)


def _apply_actions(ours_data: dict, theirs_data: dict, steps: set[str], ours, theirs, merged, ours_where, theirs_where, merged_where) -> list[dict]:
    actions = []
    for step in steps:
        if step.startswith("- "):
            continue
        ours_body = ours_data["steps"].get(step)
        theirs_body = theirs_data["steps"].get(step)
        if not ours_body or not theirs_body:
            actions.append({
                "step": step,
                "restamped": [],
                "kept": ["upstream step"],
                "reopen": False,
            })
            continue
        ours_play = _play_for(ours_body, ours_where)
        theirs_play = _play_for(theirs_body, theirs_where)
        merged_play = _play_for(theirs_body, merged_where)
        ours["playbook"] = ours_play
        theirs["playbook"] = theirs_play
        merged["playbook"] = merged_play
        actions.append(_decide_step(
            step, ours_body, theirs_body, ours, theirs, merged,
            ours_play, theirs_play, merged_play,
        ))
    actions.extend(_align_jump_keys(ours_data, theirs_data))
    return actions


def _steps_in(hunks: list[dict], kind: str) -> list[str]:
    seen: list[str] = []
    for hunk in hunks:
        if hunk["class"] != kind:
            continue
        name = hunk.get("step") or "(no step)"
        if name not in seen:
            seen.append(name)
    return seen


def _emit_exit(payload: dict, status: int) -> None:
    emit(payload)
    raise SystemExit(status)


def _stage_progress(root: Path, repo: Path | None) -> tuple[bool, str | None]:
    if repo is None:
        return False, "not a git repo"
    path = progress_path(root)
    try:
        rel = path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return False, "walk-progress.md is outside the git repo"
    proc = subprocess.run(
        ["git", "-C", str(repo), "add", "--", rel],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout).strip()
    return True, None


def _write_progress_bytes(path: Path, text: str, newline: str) -> None:
    if newline == "\r\n":
        text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    path.write_bytes(text.encode("utf-8"))


def resolve_stamps(args: argparse.Namespace) -> None:
    """Settle a walk-progress.md merge when every conflict is a hash line.

    Takes the upstream text, then recomputes a hash line from the merged
    spec, plan, tasks, or verify file only when the rule in _decide_step
    says so. --yes writes that file and git-adds it when no conflict marker
    remains. A hunk that touches Done, Result, or any other recorded line
    is not rewritten unless --settle-stamps is also set, and then only the
    stamp hunks are rewritten. The merge is not pushed.
    """
    root = Path(args.root)
    path = progress_path(root)
    if not path.is_file():
        _emit_exit({
            "ok": False,
            "code": "missing",
            "resolved": False,
            "line": f"No {PROGRESS_NAME} in {root}.",
        }, 1)
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        fail("progress-file", f"{PROGRESS_NAME} is not utf-8")
    lines = text.splitlines()
    hunks, error = _parse_hunks(lines)
    if error:
        _emit_exit({
            "ok": False,
            "code": "conflict-markers",
            "resolved": False,
            "line": f"{PROGRESS_NAME} has a broken conflict marker. {error}.",
        }, 1)
    if not hunks:
        _emit_exit({
            "ok": True,
            "code": "clean",
            "resolved": False,
            "wrote": None,
            "line": f"No stamp conflict in {PROGRESS_NAME}.",
        }, 0)
    for hunk in hunks:
        _classify_hunk(hunk, lines)
    blocked = [hunk for hunk in hunks if hunk["class"] != "stamp"]
    stamps = [hunk for hunk in hunks if hunk["class"] == "stamp"]

    def hunk_public(hunk: dict) -> dict:
        return {
            "index": hunk["index"],
            "step": hunk.get("step"),
            "class": hunk["class"],
            "lines": hunk["lines"],
        }

    if blocked and not args.settle_stamps:
        stamp_bits = [
            f"{hunk['index']} {hunk.get('step') or '(no step)'} ({', '.join(hunk['lines'])})"
            for hunk in stamps
        ]
        blocked_bits = [
            f"{hunk['index']} {hunk.get('step') or '(no step)'} ({', '.join(hunk['lines']) or 'unmarked'})"
            for hunk in blocked
        ]
        line = (
            f"{PROGRESS_NAME} is still conflicted. "
            f"Stamp-only hunks: {', '.join(stamp_bits) or 'none'}. "
            f"Other hunks: {', '.join(blocked_bits)}. "
            "Say settle stamps to resolve the stamp lines."
        )
        _emit_exit({
            "ok": False,
            "code": "mixed-conflict",
            "resolved": False,
            "wrote": None,
            "line": line,
            "stamp_hunks": [hunk_public(hunk) for hunk in stamps],
            "blocked_hunks": [hunk_public(hunk) for hunk in blocked],
            "offer": "settle stamps",
        }, 1)

    ours_text = _reconstruct(lines, hunks, "ours")
    theirs_text = _reconstruct(lines, hunks, "theirs")
    ours_data, ours_err = _try_parse(ours_text)
    theirs_data, theirs_err = _try_parse(theirs_text)
    if ours_data is None or theirs_data is None:
        detail = ours_err or theirs_err or "progress file could not be read"
        _emit_exit({
            "ok": False,
            "code": "progress-file",
            "resolved": False,
            "line": f"{PROGRESS_NAME} could not be settled. {detail}.",
        }, 1)
    ours_tree, theirs_tree, merged_tree, ours_where, theirs_where, merged_where, repo = _load_sides(args, root)
    step_names = []
    for hunk in stamps:
        name = hunk.get("step")
        if name and not name.startswith("- ") and name not in step_names:
            step_names.append(name)
    actions = _apply_actions(
        ours_data, theirs_data, set(step_names),
        ours_tree, theirs_tree, merged_tree,
        ours_where, theirs_where, merged_where,
    )
    line = _report_line(actions, PROGRESS_NAME)
    if not args.yes:
        _emit_exit({
            "ok": False,
            "code": "needs-yes",
            "resolved": False,
            "wrote": None,
            "line": line,
            "actions": actions,
            "message": "resolve-stamps writes the progress file only with --yes",
        }, 2)
    label = theirs_data.get("slice") or f"docs/specs/{root.name}/"
    merged_runs = merge_branch_runs(ours_data.get("branch_runs"), theirs_data.get("branch_runs"))
    theirs_data["branch_runs"] = merged_runs
    rendered = render(label, theirs_data["steps"], theirs_data.get("acks"), theirs_data.get("jumps"), merged_runs)
    if blocked:
        # A mixed file keeps its conflict markers. Only the stamp hunks change.
        written = _settle_stamp_hunks(lines, hunks, theirs_data)
        text_out = "\n".join(written).rstrip("\n") + "\n"
        _write_progress_bytes(path, text_out, newline)
        _emit_exit({
            "ok": False,
            "code": "mixed-conflict",
            "resolved": False,
            "settled_stamps": True,
            "staged": False,
            "wrote": PROGRESS_NAME,
            "line": line + " Other conflicts remain.",
            "actions": actions,
            "blocked_hunks": [hunk_public(hunk) for hunk in blocked],
            "offer": "stop",
        }, 1)
    _write_progress_bytes(path, rendered, newline)
    staged, stage_error = _stage_progress(root, repo)
    payload = {
        "ok": True,
        "code": "settled",
        "resolved": True,
        "staged": staged,
        "wrote": PROGRESS_NAME,
        "line": line,
        "actions": actions,
    }
    if stage_error and repo is not None:
        payload["stage_error"] = stage_error
    _emit_exit(payload, 0)


def _line_for_label(body: dict, label: str) -> str | None:
    if label == "Content stamp":
        if body.get("content_stamp"):
            return f"  Content stamp: {body['content_stamp']}"
        return None
    if label == "Playbook":
        return f"  Playbook: {body['playbook']}@{body['playbook_version']}"
    if label == "Kept questions":
        return f"  Kept questions: {body['kept_questions']}"
    if label == "Section stamps":
        if body.get("section_stamps"):
            return f"  Section stamps: {body['section_stamps']}"
        return None
    if label == "Question ids":
        if body.get("question_ids"):
            return f"  Question ids: {body['question_ids']}"
        return None
    if label == "Spec body":
        return f"  Spec body: {body['spec_body']}"
    if label == "Questions version":
        return f"  Questions version: {body['questions']}"
    if label == "Key":
        return None
    token = next((name for name, title in LABEL.items() if title == label), None)
    if token is None or token not in body:
        return None
    return f"  {label}: {body[token]}"


def _settle_stamp_hunks(lines: list[str], hunks: list[dict], data: dict) -> list[str]:
    out: list[str] = []
    cursor = 0
    for hunk in hunks:
        out.extend(lines[cursor:hunk["start"]])
        if hunk["class"] != "stamp":
            out.extend(lines[hunk["start"]:hunk["end"]])
        elif hunk.get("status"):
            ours = {r["branch"]: r for r in map(parse_branch_run, hunk["ours"]) if r}
            theirs = {r["branch"]: r for r in map(parse_branch_run, hunk["theirs"]) if r}
            merged = merge_branch_runs(ours, theirs)
            out.extend(branch_run_line(merged[name]) for name in sorted(merged))
        else:
            step = hunk.get("step") or ""
            body = data["steps"].get(step)
            labels: list[str] = []
            for line in hunk["theirs"] + hunk["ours"]:
                label = _stamp_label(line)
                if label and label not in labels:
                    labels.append(label)
            if body is None:
                out.extend(hunk["theirs"])
            else:
                for label in labels:
                    written = _line_for_label(body, label)
                    if written:
                        out.append(written)
                if body.get("content_stamp") and "Content stamp" not in labels:
                    window = "\n".join(lines[hunk["end"]:hunk["end"] + 8])
                    if "Content stamp:" not in window:
                        out.append(f"  Content stamp: {body['content_stamp']}")
        cursor = hunk["end"]
    out.extend(lines[cursor:])
    return out


def restamp_covered(args: argparse.Namespace) -> None:
    """Refresh spec stamps when the edit reopens no step (1.148.0).

    Match, In the code, a Synced at line, and an already-answered question.
    Done and Result stay. A requirement change is refused.
    """
    root = Path(args.root)
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    data = load(root)
    if not data["steps"]:
        fail("progress-file", "no walk progress to restamp")
    effect = section_effect(root, data["steps"])
    if not effect["restamp_only"]:
        fail("not-restamp", effect["reopen_line"] or "nothing to restamp")
    if not args.yes:
        emit({
            "ok": False,
            "code": "needs-yes",
            "reopen_line": effect["reopen_line"],
            "message": "restamp-covered writes the progress file only with --yes",
        })
        raise SystemExit(2)
    now = versions(root)
    stamped = []
    for step, body in data["steps"].items():
        if step == "playbook" or "spec" not in COVERS.get(step, ()):
            continue
        body["spec"] = now["spec"]
        body["spec_body"] = now["spec_body"]
        body["questions"] = now["questions"]
        body["section_stamps"] = now.get("section_stamps") or "none"
        if step == "resolve-open-questions":
            _store_questions(root, body)
            body["question_ids"] = now.get("question_ids") or "none"
        body["content_stamp"] = CONTENT_STAMP
        stamped.append(step)
    write_progress(root, data)
    emit({
        "ok": True,
        "wrote": PROGRESS_NAME,
        "restamped": stamped,
        "reopen_line": effect["reopen_line"],
        "reopen_steps": [],
    })


def cmd_version(args: argparse.Namespace) -> None:
    root = Path(args.root)
    emit({"ok": True, "versions": versions(root, Path(args.playbook) if args.playbook else None)})


def _bind_vendor(argv):
    """1.201.0: --vendor codex prints $crav1- commands. The default stays /."""
    source = sys.argv[1:] if argv is None else argv
    if "--vendor" not in source and not any(str(item).startswith("--vendor=") for item in source):
        return argv
    path = Path(__file__).resolve().parents[2] / "crav1-update-kit" / "scripts" / "vendor_prefix.py"
    if not path.is_file():
        print("Refused: --vendor needs the vendor table.", file=sys.stderr)
        raise SystemExit(2)
    import importlib.util
    spec = importlib.util.spec_from_file_location("crav1_vendor_prefix", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.install_from_argv(argv)


def main(argv: list[str] | None = None) -> None:
    _utf8_stdout()
    argv = _bind_vendor(argv)
    parser = argparse.ArgumentParser(description="Guided walk progress file")
    sub = parser.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("version")
    v.add_argument("--root", required=True)
    v.add_argument("--playbook")
    v.set_defaults(func=cmd_version)

    r = sub.add_parser("record")
    r.add_argument("--root", required=True)
    r.add_argument("--slice")
    r.add_argument("--step", action="append", required=True, help="One step id. More than one is refused.")
    r.add_argument("--result", required=True)
    r.add_argument("--when", help="Full timestamp. Omit to let the script stamp Done.")
    r.add_argument("--playbook")
    r.add_argument("--yes", action="store_true")
    r.set_defaults(func=record)

    c = sub.add_parser("cover")
    c.add_argument("--root", required=True)
    c.add_argument("--yes", action="store_true")
    c.set_defaults(func=cover)

    k = sub.add_parser("clear")
    k.add_argument("--root", required=True)
    k.add_argument("--step", required=True)
    k.add_argument("--yes", action="store_true")
    k.set_defaults(func=clear)

    st = sub.add_parser("start")
    st.add_argument("--root", required=True, help="Spec folder, or a slug, title, or playbook name.")
    st.add_argument("--playbook")
    st.add_argument("--skip-sync", action="store_true", help="Skip the fetch. Tests and an already-fetched copy.")
    st.set_defaults(func=start)

    s = sub.add_parser("resume")
    s.add_argument("--root", required=True)
    s.add_argument("--no-playbook", action="store_true")
    s.set_defaults(func=resume)

    p = sub.add_parser("playbook-status")
    p.add_argument("--root", required=True)
    p.add_argument("--playbook", required=True)
    p.set_defaults(func=playbook_status)

    d = sub.add_parser("readiness")
    d.add_argument("--json", help="Rows file. Omit with --root to build the rows from the spec folder.")
    d.add_argument("--root", help="Spec folder. Builds the rows when --json is omitted. Reopened steps block ready.")
    d.add_argument("--write-map", action="store_true", help="Write build-map.md in the standalone command's format.")
    d.add_argument("--brief", action="store_true", help="The default (1.156.0): result, the counts row, the ending, the reply, and claim warnings.")
    d.add_argument("--full", action="store_true", help="Print the complete JSON. Only on an explicit ask.")
    d.add_argument("--text", action="store_true", help="Print only the finished reply text, to show as-is.")
    d.add_argument("--new-question", action="append", default=[], help="Exact question key to treat as new, not as a recorded question.")
    d.add_argument("--skip-sync", action="store_true", help="Skip the fetch. Tests and an already-fetched copy.")
    d.add_argument("--user", default=None, help="Claim owner that is you. Default: git config user.name in the specs repo (1.160.0).")
    d.add_argument("--branch", default=None, help="The branch being walked. Your claim counts as yours only on this branch when given (1.160.0).")
    d.add_argument("--covered", action="append", default=[], help="A reopened step whose only change is a fact this walk just recorded and a finding covers: no card, clear it (1.196.0).")
    d.add_argument("--stale-seen", action="store_true", help="This walk saw something stale (code-drift behind, a merge since sync, a stale mark): reopen cards recommend rerun (1.195.0).")
    d.set_defaults(func=readiness)

    u = sub.add_parser("unlinked")
    u.add_argument("--root", required=True)
    u.set_defaults(func=unlinked)

    fl = sub.add_parser("fix-loop")
    fl.add_argument("--root", required=True, help="Spec folder.")
    fl.add_argument("--pick", type=int, default=1, help="The fix number the Loop lines print. `fix-loop` is 1, `fix-loop 2` is 2.")
    fl.add_argument("--yes", action="store_true", help="Write tasks.md and build-map.md. Only after the fix was shown and confirmed.")
    fl.add_argument("--text", action="store_true", help="Print only the reply.")
    fl.set_defaults(func=fix_loop_cmd)

    a = sub.add_parser("ack-stamps")
    a.add_argument("--root", required=True)
    a.add_argument("--yes", action="store_true")
    a.set_defaults(func=ack_stamps)

    f = sub.add_parser("spec-finding")
    f.add_argument("--root", required=True)
    f.add_argument("--id", required=True)
    f.add_argument("--text", required=True)
    f.add_argument("--tag", default="spec", help="spec offers a jump back. plan behaves as today.")
    f.add_argument("--choice", help="tighten-spec, add-to-spec, open-point, already-done, same, or new")
    f.add_argument("--kind", help="code-drift (add-to-spec owns it) or spec-text (tighten-spec owns it); unclear is tighten-spec")
    f.add_argument("--pr", help="the pull request a code-drift finding is about, e.g. 73")
    f.add_argument("--branch", help="the branch a code-drift finding is about")
    f.add_argument("--expect", help="words the fix leaves in spec.md; checks whether it is already fixed")
    f.add_argument("--code-repo", help="code checkout to tell whether a Synced at commit is after the merge commit (no fetch)")
    f.add_argument("--topic", help="Short stable topic, such as approver. Same P# and topic are one finding.")
    f.add_argument("--new", action="store_true", help="This wording is a new finding.")
    f.add_argument("--match-key", help="First-seen key when more than one recorded finding is close.")
    f.add_argument("--yes", action="store_true")
    f.set_defaults(func=spec_finding)

    cdr = sub.add_parser("code-drift", help="is the spec's record behind the code; one add-to-spec card before the plan review (1.194.0)")
    cdr.add_argument("--root", required=True)
    cdr.add_argument("--code-repo", required=True, help="the code checkout; fetched once, then refs on disk (1.196.0)")
    cdr.add_argument("--no-fetch", action="store_true", help="skip the one quiet fetch of origin")
    cdr.add_argument("--branch", help="only this Synced at branch")
    cdr.add_argument("--base", help="the branch work merges into (repos.md Merges into); commits merged in from it are not counted")
    cdr.add_argument("--pr", help="the merged pull request, e.g. 73")
    cdr.add_argument("--merged", help="its merge commit, when the walk already saw it merged")
    cdr.set_defaults(func=code_drift)

    rp = sub.add_parser("review-packet", help="scoped plan-reviewer input: changed tasks, their spec sections, Risks (1.197.0)")
    rp.add_argument("--root", required=True)
    rp.add_argument("--since", help="git ref; tasks added since it are the changed tasks")
    rp.add_argument("--tasks", help="T# list instead, such as T3,T7")
    rp.add_argument("--out", help="packet path; default a file in the system temp folder")
    rp.set_defaults(func=review_packet_cmd)
    tk = sub.add_parser("tickable", help="acceptance items a passing verify row proves; tick with no card (1.196.0)")
    tk.add_argument("--root", required=True)
    tk.add_argument("--write", action="store_true", help="tick them, and add recheck notes to touching open tasks")
    tk.set_defaults(func=tickable)

    bs = sub.add_parser("branch-status")
    bs.add_argument("--root", required=True)
    bs.add_argument("--branch", required=True)
    bs.add_argument("--state", required=True)
    bs.add_argument("--when")
    bs.add_argument("--yes", action="store_true")
    bs.set_defaults(func=cmd_branch_status)

    rs = sub.add_parser("resolve-stamps")
    rs.add_argument("--root", required=True)
    rs.add_argument("--yes", action="store_true")
    rs.add_argument("--settle-stamps", action="store_true")
    rs.add_argument("--ours-root")
    rs.add_argument("--theirs-root")
    rs.set_defaults(func=resolve_stamps)

    rc = sub.add_parser("restamp-covered")
    rc.add_argument("--root", required=True)
    rc.add_argument("--yes", action="store_true")
    rc.set_defaults(func=restamp_covered)

    pa = sub.add_parser("pr-author", help="Record who opened a pull request in its build-progress file (1.177.1).")
    pa.add_argument("--root", required=True, help="Spec folder.")
    pa.add_argument("--pr", required=True, type=int)
    pa.add_argument("--name", help="Who opened it, as the user said. Omit to ask the PR's own host, read-only.")
    pa.add_argument("--branch", help="The PR's branch, when several build-progress files name it (1.179.0).")
    pa.set_defaults(func=cmd_pr_author)

    cr = sub.add_parser("code-repo", help="Record which code repo a pull request is in (1.177.2).")
    cr.add_argument("--root", required=True, help="Spec folder.")
    cr.add_argument("--pr", required=True, type=int)
    cr.add_argument("--repo", help="A docs/system/repos.md name or a repo URL. Omit to list the choices.")
    cr.add_argument("--branch", help="The PR's branch, when several build-progress files name it (1.179.0).")
    cr.set_defaults(func=cmd_code_repo)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
