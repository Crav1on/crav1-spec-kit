#!/usr/bin/env python3
"""Progress file for /crav1-tighten-and-plan-ready-to-build (kit 1.139.0).

The spec, plan, and tasks stay the source of truth. This script only tracks
where the guided walk is, which version of each file a step covered, and which
ready-check rows belong to which step. It does not edit those files, does not
apply a playbook, and does not start a build. It never writes verify.md.
build-map.md stays with /crav1-tasks-ready-to-build.

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
  walk_progress.py resume --root <spec-folder>
  walk_progress.py playbook-status --root <spec-folder> --playbook <file>
  walk_progress.py readiness --root <spec-folder>
  walk_progress.py readiness --json <file> [--root <spec-folder>]
  walk_progress.py unlinked --root <spec-folder>
  walk_progress.py ack-stamps --root <spec-folder> --yes
  walk_progress.py spec-finding --root <spec-folder> --id P2 --text "<finding>"
      [--tag spec|plan] [--choice tighten-spec|open-point] [--yes]
  walk_progress.py resolve-stamps --root <spec-folder> --yes
      [--settle-stamps] [--ours-root <folder> --theirs-root <folder>]
  walk_progress.py restamp-covered --root <spec-folder> --yes

readiness --root builds the rows from task_order.py and question_blocks.py
and adds the Reviewed warnings. It also compares tasks.md with verify.md.
Do not hand-build that JSON. spec-finding offers one jump back for a spec
finding, or records an open point when that finding already jumped. A plan
tag writes nothing.

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
JUMP_CHOICE = "run /crav1-tighten-spec on just that finding now (Recommended)"
POINT_CHOICE = "keep it as an open point and continue"
FINDING_ID = re.compile(r"^P[1-9][0-9]*$")
JUMP_RESULTS = {"jumped", "open-point"}


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


def normalize_text(kind: str, text: str) -> str:
    """Content used for a stamp. LF, and progress marks removed.

    spec: a Match Branch line loses `(PR n)` and a trailing `merged`.
    tasks: a checkbox is `[ ]`, and a PR or `(done)` note on that line is
    dropped. plan, verify, playbook, and questions: line endings only.
    A branch name, `(into …)`, `(spec branch)`, `(branch:)`, and `(map:)` stay.
    """
    text = _lf_text(text or "")
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
    for name in ("stable_question_id", "question_identity"):
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


def _diff_questions(stored: str | None, text: str) -> dict:
    """Which questions must be asked again.

    A settled question stays settled when an Answered line is added or a new
    answered question appears. A new open question, a removed open question,
    or a word change on the same stable id reopens resolve-open-questions.
    """
    prev_open, prev_answered = _parse_question_ids(stored)
    current = []
    for question in _iter_questions(text):
        ident, word, answered = _question_identity(question["text"], question["marks"])
        current.append({"id": ident, "word": word, "answered": answered})
    curr_all = {row["id"]: row for row in current}
    curr_open = {row["id"]: row for row in current if not row["answered"]}
    changed: list[dict] = []
    reopen = False
    answered_events = False

    def note(ident: str, reason: str, does_reopen: bool) -> None:
        nonlocal reopen
        changed.append({"id": ident, "reason": reason})
        if does_reopen:
            reopen = True

    for ident, row in curr_open.items():
        if ident not in prev_open:
            note(ident, "reopened" if ident in prev_answered else "new", True)
        elif prev_open[ident] != row["word"]:
            note(ident, "reworded", True)
    for ident, word in prev_open.items():
        if ident in curr_open:
            continue
        row = curr_all.get(ident)
        if row and row["answered"] and row["word"] == word:
            answered_events = True
            continue
        if row and row["answered"]:
            note(ident, "reworded", True)
            continue
        note(ident, "removed", True)
    for ident, row in curr_all.items():
        if not row["answered"] or ident in prev_open:
            continue
        if ident not in prev_answered:
            answered_events = True
        elif prev_answered[ident] != row["word"]:
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


def section_effect(root: Path, steps: dict) -> dict:
    """What a spec edit invalidates, from the recorded section stamps.

    Inactive when no recorded step has `Section stamps` (a walk recorded
    before 1.148.0). Those steps keep the 1.137 whole-body rule.
    """
    baseline = None
    # Extras keep the version they saw. The baseline is the latest locked step.
    for step in list(ORDER) + list(EXTRAS):
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
    if "open-questions" in changed and resolve.get("question_ids"):
        qdiff = _diff_questions(resolve.get("question_ids"), text)
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
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == f"Walk: {WALK}":
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
            if jump.get("open") != TIGHTEN_SPEC_PATH:
                fail("progress-file", f"jump-back {jump['id']} does not name {TIGHTEN_SPEC_PATH}")
        elif jump["result"] != "open-point":
            fail("progress-file", f"open point {jump['id']} result is not open-point")
    return {"slice": slice_line, "steps": steps, "acks": acks, "jumps": jumps}


def load(root: Path) -> dict:
    path = progress_path(root)
    if not path.is_file():
        return {"slice": None, "steps": {}, "acks": [], "jumps": []}
    data = parse_progress(path.read_text(encoding="utf-8"))
    data.setdefault("acks", [])
    data.setdefault("jumps", [])
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
        lines.append("")


def render(slice_label: str, steps: dict, acks: list | None = None, jumps: list | None = None) -> str:
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
    if not raw or raw == "none":
        return set()
    return {part for part in raw.split() if part and part != "none"}


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
    text = render(label, data["steps"], data.get("acks"), data.get("jumps"))
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
    effect = section_effect(root, steps or {}) if body.get("section_stamps") else None
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
        steps["resolve-open-questions"]["kept_questions"] = kept_question_line(root)
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
        steps["resolve-open-questions"]["kept_questions"] = kept_question_line(root)
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
        body["kept_questions"] = kept_question_line(root)
        body["question_ids"] = now.get("question_ids") or "none"
    body["content_stamp"] = CONTENT_STAMP


def write_progress(root: Path, data: dict, slice_label: str | None = None) -> None:
    label = slice_label or data["slice"] or f"docs/specs/{root.name}/"
    if not str(label).endswith("/"):
        label = f"{label}/"
    progress_path(root).write_text(
        render(label, data["steps"], data.get("acks"), data.get("jumps")),
        encoding="utf-8",
    )


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
    data = load(root)
    effect = section_effect(root, data["steps"])
    rows = []
    continue_from = None
    for step in ORDER:
        body = data["steps"].get(step)
        if body is None and step == "playbook" and args.no_playbook:
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
                if effect["reopen_line"] and step in effect["reopen_steps"]:
                    impact = effect["reopen_line"]
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
    emit({
        "ok": True,
        "source_of_truth": "spec.md, plan.md, and tasks.md",
        "progress_file": PROGRESS_NAME,
        "steps": rows,
        "continue_from": continue_from,
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
                "result": jump["result"],
                "continue": [part for part in jump["continue"].split(", ") if part],
            }
            for jump in data.get("jumps") or []
        ],
    })


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
    playbook = resolve_playbook(root, args.playbook)
    data = load(root) if root.is_dir() else {"steps": {}}
    body = data["steps"].get("playbook")
    text, raw = _read_pair(playbook)
    now = stamp_file(playbook, "playbook")
    if body is None:
        emit({
            "ok": True,
            "status": "not-recorded",
            "already_applied": False,
            "offer": "show-changes",
            "note": "No progress line for this playbook. Use the apply compare. Do not treat it as already applied.",
        })
        return
    same_path = same_playbook_path(root, body["playbook"], args.playbook, playbook)
    same_hash = now != "missing" and stamp_matches(
        body.get("playbook_version"), text, "playbook",
        body.get("content_stamp") == CONTENT_STAMP,
        raw_bytes=raw, path=playbook, part="file",
    )
    if same_path and same_hash and body["result"] in APPLIED:
        emit({
            "ok": True,
            "status": "already-applied",
            "already_applied": True,
            "offer": "skip-or-reapply",
            "result": body["result"],
            "note": (
                "Ask once: skip (Recommended) or reapply, even when the file has not changed. "
                "Do not move on without that question."
            ),
        })
        return
    if same_path and same_hash and body["result"] == "skipped":
        emit({
            "ok": True,
            "status": "already-skipped",
            "already_applied": False,
            "offer": "skip-or-apply",
            "result": body["result"],
        })
        return
    emit({
        "ok": True,
        "status": "changed" if same_path else "different-file",
        "already_applied": False,
        "offer": "show-changes",
        "result": body.get("result"),
    })


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


def unlinked(args: argparse.Namespace) -> None:
    """Kept-open questions that still have no Blocks line. Writes nothing."""
    root = Path(args.root)
    spec = root / "spec.md"
    if not spec.is_file():
        fail("spec", f"no spec.md in {root}")
    questions = blocks_mod().kept_open(spec.read_text(encoding="utf-8"))
    missing = [{"text": q["text"]} for q in questions if q["mark"] == "missing"]
    emit({"ok": True, "count": len(missing), "questions": missing})


def classify(row: dict, resolve_kept: bool = False, resolve_recorded: bool = False) -> dict | None:
    bucket = str(row.get("bucket") or "")
    reason = str(row.get("reason") or "")
    warning = str(row.get("warning") or "")
    text = f"{reason} {warning}".lower()
    task = row.get("task")
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
            "why": why + " The walk does not invent a step for this.",
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
            body["kept_questions"] = kept_question_line(root)
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
    write_progress(root, data)
    emit({
        "ok": True,
        "wrote": PROGRESS_NAME,
        "cleared": args.step,
        "confirmation": "nothing new",
        "changed": drift,
    })


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
    for step in ORDER:
        body = data["steps"].get(step)
        if not body:
            continue
        drift = affected_drift(root, step, body, data["steps"])
        if drift:
            hits.append(reopen_hit(step, drift))
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


def branch_report(root: Path, rows: list[dict]) -> dict | None:
    """Ready and held tasks grouped by the build-map row (1.133.0).

    The branch is the one `build_map.py --recommend` prints. Missing files
    leave the report empty so the caller keeps the older line.
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
    built = map_mod().build(
        root.name,
        spec,
        plan,
        tasks,
        work,
        verify,
        resolve_recorded=resolve_ever_recorded(root),
        repo=map_mod().find_repo(root),
    )
    return map_mod().report_by_branch(built, rows)


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


def _stale_next(verify_text: str, ticked: set[str]) -> str | None:
    """A Next line is stale only when it names a ticked task (1.136.0)."""
    hits = []
    for line in (verify_text or "").splitlines():
        stripped = line.strip()
        if not stripped.lower().startswith("next:"):
            continue
        named = re.findall(r"\bT\d+\b", stripped)
        if any(tid in ticked for tid in named):
            hits.append(stripped)
    return " ".join(hits) if hits else None


def verify_gap_from(tasks_text: str, spec_text: str, verify_text: str, slug: str) -> dict:
    """verify.md is behind for a ticked task, or a merged task still Not implemented.

    A Next line is stale only when it names a ticked task. A merged task that
    is still unticked, and whose verify status is not Not implemented, is not
    behind: the checkbox is the only leftover. Merged tasks stay done for
    dependents. This does not write verify.md.
    """
    empty = {"behind": False, "tasks": [], "waiting": None, "stale_next": None}
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
            if tid in ticked and tid not in stale:
                stale.append(tid)
    if not stale:
        return empty
    ordered = sorted(stale, key=lambda tid: int(tid[1:]))
    ids = ", ".join(ordered)
    waiting = (
        f"Waiting: /crav1-verify-build-against-spec {slug} - "
        f"verify.md is behind tasks.md ({ids})"
    )
    return {"behind": True, "tasks": ordered, "waiting": waiting, "stale_next": stale_next}


def verify_gap(root: Path) -> dict:
    empty = {"behind": False, "tasks": [], "waiting": None, "stale_next": None}
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


def _oq_row(tid: str, question: dict, whole: bool, kept: set[str]) -> dict:
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
        "kept": bool(question.get("recorded")) or question.get("key") in kept,
        "inferred_text": question.get("mark") == "inferred",
    }
    if question.get("who"):
        row["who"] = question["who"]
    return row


def _question_row(blocks: dict, tid: str, kept: set[str]) -> dict | None:
    slice_q = None
    for question in blocks.get("questions") or []:
        if question.get("mark") in ("tasks", "inferred") and tid in (question.get("tasks") or []):
            return _oq_row(tid, question, whole=False, kept=kept)
        if question.get("blocks_slice") and slice_q is None:
            slice_q = question
    if slice_q is not None:
        return _oq_row(tid, slice_q, whole=True, kept=kept)
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


def build_rows(root: Path) -> list[dict]:
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
    for task in tasks:
        task["ticked"] = task["done"]
        task["merged"] = _task_merged(rests.get(task["id"], ""), merged_branches)
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
        question = _question_row(blocks, tid, kept)
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
        tail = f" ({', '.join(whos)}; {unnamed} not named yet)"
    elif whos:
        tail = f" ({', '.join(whos)})"
    elif unnamed:
        tail = f" ({unnamed} not named yet)"
    else:
        tail = ""
    return f"Waiting: {count} tasks wait on {noun}{tail}."


def _waiting_lines(waiting: list[dict], slug: str) -> tuple[str | None, str | None]:
    if not waiting:
        return None, None
    questions = [hit for hit in waiting if not hit.get("approval")]
    approvals = [hit for hit in waiting if hit.get("approval")]
    parts = []
    if questions:
        parts.append(_wait_phrase(questions, "open questions"))
    if approvals:
        parts.append(_wait_phrase(approvals, "an approval"))
    line = " ".join(parts)
    if any(not hit.get("asked") for hit in waiting):
        nxt = (
            f"/crav1-show-or-ask-open-questions {slug}, "
            "because the questions are not asked yet."
        )
    elif approvals:
        nxt = (
            f"/crav1-record-approval {slug}, "
            "because that yes is not on record yet."
        )
    else:
        nxt = (
            f"/crav1-tighten-and-plan-ready-to-build {slug}, "
            "because the walk resumes when the answers arrive."
        )
    return line, nxt


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
            if len(deps) == 1:
                text = f"held, waits on {deps[0]} ({tag})"
            else:
                text = "held, waits on " + ", ".join(deps) + f" ({tag})"
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
    hard = [hit for hit in hits if hit.get("kind") != "waiting"]
    can_start = [row.get("task") for row in rows if row.get("bucket") == "ready" and row.get("task")]
    held = [row.get("task") for row in rows if row.get("bucket") == "waiting" and row.get("task")]
    resolve_only = bool(can_start) and _resolve_reopen_only(hits)
    if hard and not resolve_only:
        return "not-ready", can_start, held
    if can_start and (held or resolve_only):
        return "ready-partial", can_start, held
    if held and not can_start:
        return "not-ready", can_start, held
    return "ready", can_start, held


def not_ready_because(result: str, rows: list[dict], hits: list[dict], can_start: list) -> str | None:
    """Why the result is not-ready, when can_start is also filled.

    A hard hit (a reopened step, a jump-back question, a whole-slice hold)
    forces not-ready and still lists tasks whose bucket is ready. Those
    tasks are not a start. A whole-slice question is named from its row.
    """
    if result != "not-ready":
        return None
    bits = []
    reopened = [hit["step"] for hit in hits if hit.get("bucket") == "reopened" and hit.get("step")]
    if reopened:
        bits.append("Reopened: " + ", ".join(reopened))
    for row in rows:
        reason = str(row.get("reason") or "")
        if "whole slice" in reason.lower():
            bits.append(reason)
            break
    if not reopened and not any("whole slice" in bit.lower() for bit in bits):
        for hit in hits:
            if hit.get("kind") == "waiting" or hit.get("bucket") == "reopened":
                continue
            why = hit.get("why")
            if why and why not in bits:
                bits.append(why)
                break
    if can_start:
        ids = ", ".join(task for task in can_start if task)
        bits.append(f"{ids} stay in can_start and are not a start while the result is not-ready")
    return ". ".join(bits) if bits else "not ready"


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


def next_for(result: str, can_start: list, waiting_next: str | None) -> str | None:
    """Fallback when the branch report has no ready line (1.143.0).

    A ready or ready-partial slice recommends the build walk. build-tasks is
    named as the alternative for one task. A not-ready result does not.
    """
    alt = " /crav1-build-tasks builds one task without the walk."
    if result == "ready":
        return "/crav1-build-walk, because the slice is ready to build." + alt
    if result == "ready-partial":
        ids = ", ".join(task for task in can_start if task)
        if not ids:
            return None
        return f"/crav1-build-walk {ids}, because those tasks can start now." + alt
    return waiting_next


def readiness(args: argparse.Namespace) -> None:
    root = Path(args.root) if args.root else None
    built = False
    if args.json:
        try:
            payload = json.loads(Path(args.json).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fail("readiness", f"cannot read rows: {exc}")
        rows = payload.get("rows")
        if not isinstance(rows, list):
            fail("readiness", "rows must be a list")
    elif root is not None:
        if not root.is_dir():
            fail("root", f"not a folder: {root}")
        rows = build_rows(root)
        built = True
    else:
        fail("readiness", "pass --root <spec-folder>, or --json <rows file>")
    for row in rows:
        if not isinstance(row, dict):
            fail("readiness", "each row must be an object")
    resolve_kept = resolve_is_keep(root) if root is not None else False
    resolve_recorded = resolve_ever_recorded(root) if root is not None else False
    hits = []
    for row in rows:
        hit = classify(row, resolve_kept=resolve_kept, resolve_recorded=resolve_recorded)
        if hit:
            hits.append(hit)
            if hit["kind"] == "waiting":
                row["bucket"] = "waiting"
    propagate_held(rows, hits)
    reopened = reopened_hits(root) if root is not None else []
    hits.extend(reopened)
    blockers = [h for h in hits if h["kind"] == "blocker" and not h["outside_walk"]]
    outside = [h for h in hits if h["outside_walk"]]
    assumptions = [h for h in hits if h["kind"] == "assumption"]
    waiting = [h for h in hits if h["kind"] == "waiting"]
    unmapped = [h for h in hits if h["command"] is None and h["kind"] != "waiting"]
    jump = [h for h in hits if h["can_jump_back"]]
    result, can_start, held = slice_result(rows, hits)
    because = not_ready_because(result, rows, hits, can_start)
    ready = result == "ready"
    slug = _slug(root) if root is not None else ""
    waiting_line, waiting_next = _waiting_lines(waiting, slug)
    report = branch_report(root, rows) if root is not None else None
    ready_lines = (report or {}).get("ready_lines") or []
    held_lines = (report or {}).get("held_lines") or []
    next_lines = (report or {}).get("next_lines") or []
    later = [hit for hit in reopened if hit.get("step") != "resolve-open-questions"]
    resolve_open = next(
        (hit for hit in reopened if hit.get("step") == "resolve-open-questions"),
        None,
    )
    resolve_waiting = None
    resolve_next = (
        f"Next: /crav1-resolve-open-questions {slug}, "
        "because that step needs a rerun or clear."
    )
    if later:
        names = ", ".join(hit["step"] for hit in reopened)
        nxt = f"Next: rerun or clear {names}."
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
    out = {
        "ok": True,
        "ready": ready,
        "result": result,
        "can_start": can_start,
        "held": held,
        "because": because,
        "line": line,
        "ready_lines": ready_lines,
        "held_lines": held_lines,
        "next_lines": next_lines,
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
        "jump_back": jump,
        "reopened": reopened,
        "reopen_line": None,
        "changed_sections": [],
        "reopen_steps": [],
        "changed_questions": [],
        "restamp_only": False,
        "verify_behind": gap["behind"],
        "verify_stale": gap["tasks"],
        "verify_waiting": gap["waiting"],
        "stale_next": gap["stale_next"],
        "trust_stale_next": False,
    }
    if built:
        out["rows"] = rows
    if root is not None and root.is_dir():
        loaded = load(root)
        out["done_stamp_warning"] = done_stamp_warning(loaded["steps"], loaded.get("acks"))
        effect = section_effect(root, loaded["steps"])
        out["reopen_line"] = effect["reopen_line"]
        out["changed_sections"] = effect["titles"]
        out["reopen_steps"] = effect["reopen_steps"]
        out["changed_questions"] = effect["changed_questions"]
        out["restamp_only"] = effect["restamp_only"]
    emit(out)


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


def _finding_key(text: str) -> str:
    norm = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:12]


def _short_finding(text: str) -> str:
    one = re.sub(r"\s+", " ", text.strip())
    if len(one) > 160:
        return one[:157].rstrip() + "..."
    return one


def _continue_list(text: str) -> list[str]:
    return [part for part in text.split(", ") if part]


def _append_finding(root: Path, data: dict, kind: str, fid: str, text: str, key: str, result: str, continue_line: str, open_path: str | None = None) -> None:
    jump = {
        "kind": kind,
        "id": fid,
        "when": done_stamp(None),
        "finding": _short_finding(text),
        "result": result,
        "continue": continue_line,
        "key": key,
    }
    if open_path:
        jump["open"] = open_path
    data.setdefault("jumps", []).append(jump)
    if not data.get("slice"):
        data["slice"] = f"docs/specs/{root.name}/"
    write_progress(root, data)


def spec_finding(args: argparse.Namespace) -> None:
    """One jump-back card for a spec finding. A plan finding is left as it is.

    The same finding (the same words) is offered once. After that jump, a
    return is an open point and the walk continues. This writes walk-progress.md
    only with --yes. It does not write verify.md, spec.md, plan.md, or tasks.md.
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
    root = Path(args.root)
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    data = load(root)
    key = _finding_key(args.text)
    jumps = data.get("jumps") or []
    jumped = any(item.get("key") == key and item["kind"] == "jump-back" for item in jumps)
    pointed = any(item.get("key") == key and item["kind"] == "open-point" for item in jumps)
    if jumped or pointed:
        payload = {
            "ok": True,
            "offer": None,
            "spec": True,
            "finding": args.id,
            "already_jumped": jumped,
            "open_point": True,
            "pause": False,
            "continue": _continue_list(CONTINUE_POINT),
            "refused_second_jump": args.choice == "tighten-spec",
        }
        if pointed:
            payload["already_recorded"] = True
            payload["wrote"] = None
            emit(payload)
            return
        if not args.yes:
            payload["needs_record"] = True
            payload["wrote"] = None
            emit(payload)
            return
        _append_finding(root, data, "open-point", args.id, args.text, key, "open-point", CONTINUE_POINT)
        payload["recorded"] = "open-point"
        payload["wrote"] = PROGRESS_NAME
        emit(payload)
        return
    if not args.choice:
        emit({
            "ok": True,
            "offer": "jump-back",
            "spec": True,
            "finding": args.id,
            "question": (
                f"{args.id} is a spec finding. Jump back to /crav1-tighten-spec "
                "for this finding only, or keep it as an open point and continue?"
            ),
            "options": [
                {"id": "tighten-spec", "label": JUMP_CHOICE, "recommended": True},
                {"id": "open-point", "label": POINT_CHOICE, "recommended": False},
            ],
            "path": TIGHTEN_SPEC_PATH,
            "already_jumped": False,
            "pause": False,
            "wrote": None,
        })
        return
    if args.choice not in ("tighten-spec", "open-point"):
        fail("choice", "choice must be tighten-spec or open-point")
    if not args.yes:
        fail(
            "needs-yes",
            "spec-finding writes the progress file only with --yes, after the card was answered",
            status=2,
        )
    if args.choice == "tighten-spec":
        _append_finding(
            root, data, "jump-back", args.id, args.text, key, "jumped",
            CONTINUE_JUMP, TIGHTEN_SPEC_PATH,
        )
        emit({
            "ok": True,
            "offer": None,
            "spec": True,
            "finding": args.id,
            "recorded": "jump-back",
            "choice": "tighten-spec",
            "path": TIGHTEN_SPEC_PATH,
            "scoped_to": args.id,
            "pause": False,
            "continue": _continue_list(CONTINUE_JUMP),
            "wrote": PROGRESS_NAME,
        })
        return
    _append_finding(root, data, "open-point", args.id, args.text, key, "open-point", CONTINUE_POINT)
    emit({
        "ok": True,
        "offer": None,
        "spec": True,
        "finding": args.id,
        "recorded": "open-point",
        "choice": "open-point",
        "pause": False,
        "continue": _continue_list(CONTINUE_POINT),
        "wrote": PROGRESS_NAME,
    })


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
    rendered = render(label, theirs_data["steps"], theirs_data.get("acks"), theirs_data.get("jumps"))
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
            body["kept_questions"] = kept_question_line(root)
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


def main(argv: list[str] | None = None) -> None:
    _utf8_stdout()
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
    d.set_defaults(func=readiness)

    u = sub.add_parser("unlinked")
    u.add_argument("--root", required=True)
    u.set_defaults(func=unlinked)

    a = sub.add_parser("ack-stamps")
    a.add_argument("--root", required=True)
    a.add_argument("--yes", action="store_true")
    a.set_defaults(func=ack_stamps)

    f = sub.add_parser("spec-finding")
    f.add_argument("--root", required=True)
    f.add_argument("--id", required=True)
    f.add_argument("--text", required=True)
    f.add_argument("--tag", default="spec", help="spec offers a jump back. plan behaves as today.")
    f.add_argument("--choice", help="tighten-spec or open-point")
    f.add_argument("--yes", action="store_true")
    f.set_defaults(func=spec_finding)

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

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
