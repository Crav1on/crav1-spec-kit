#!/usr/bin/env python3
"""One shared ending for the ready check and the walks (kit 1.156.0).

The ready check (/crav1-tasks-ready-to-build), the tighten-and-plan ready
check, and /crav1-build-walk all end a run in the same shape, built here:

  1. Run next, first. A `**Catch up first**` block leads when verify.md
     is behind, has a row for a T# not in tasks.md, or the specs repo is
     ahead of origin (1.167.0). Then one block per ready branch (1.164.0): the bold
     branch, one plain sentence from its plan step, `<n> open tasks:` one
     per line in walk order, then `Run the whole branch:` and `Run only T#,
     the first task:`, each command alone in its code span on the line
     under its label. One open task: `Run T#:` and one command. A `---`
     line sits between two blocks (1.165.0).
  2. Held lines, then Branch runs status lines.
  3. Built (one line per task) and Left, for a branch run.
  4. Loop and other Waiting lines: only what the user cannot act on now
     (1.167.0).
  5. The not-ready reason (only when it is not already the Run next
     line), at most the one-line /crav1-build-tasks alternative, notes,
     and Uncommitted.
  A walk ending has no Next line (1.157.0). A not-ready ready check
  starts its ending with Run next, naming the first real next step
  (1.163.0). An agent never adds a Next line of its own.

The skills print the text these functions return, as-is. The ready check's
`reply` (header, counts, Result, ending, Source, Build map) is ready_reply().

Usage:
  walk_ending.py --json <state file>   prints compose() of that state
  walk_ending.py --verify <state file> prints the verify reply (1.168.0)
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ALTERNATIVE = "/crav1-build-tasks builds one task without the walk."
COUNT_COLUMNS = (
    ("Ready", "ready"),
    ("Waiting", "waiting"),
    ("Waits in order", "waits_in_order"),
    ("Blocked", "blocked"),
    ("Needs verify", "needs_verify"),
    ("Done", "done"),
)


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


# ---------- Run next entries ----------

def run_entry(labels, branch_name, slug=None):
    """One ready branch's next-task entry (1.150.0).

    The command is alone on its line, inside a code span, and is a complete
    invocation for a new session: the command, each T#, and the slug when
    the caller passes one. The label above it names each full task name and
    the branch (1.176.0: label above the command, no lowercase line under it).
    """
    ids = []
    names = []
    for label in labels:
        match = re.match(r"(T\d+)\s+(.*)", str(label).strip())
        if match:
            ids.append(match.group(1))
            names.append(f"{match.group(1)} {match.group(2).strip()}")
        else:
            token = str(label).strip()
            ids.append(token)
            names.append(token)
    ids_text = ", ".join(ids)
    command = f"/crav1-build-walk {slug} {ids_text}" if slug else f"/crav1-build-walk {ids_text}"
    return f"Build {_join(names)} on {branch_name}:\n`{command}`"


def branch_entry(open_labels, branch_name, slug=None):
    """The whole-branch entry (1.155.0), offered with two or more open tasks."""
    names = [str(label).strip() for label in open_labels or [] if str(label).strip()]
    command = f"/crav1-build-walk {slug} {branch_name}" if slug else f"/crav1-build-walk {branch_name}"
    return f"Build every open task on {branch_name} ({', '.join(names)}):\n`{command}`"


# Words a cut line must not end on (1.165.0).
DANGLING = frozenset(
    "a an the and or but nor of to in on at by for from with into onto via "
    "that which who whose when where than as if so its their his her our your".split()
)
PERSON_LEAD = re.compile(
    r"^(?:[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*){0,3})\s+"
    r"(?:builds|owns|writes|takes|handles|reviews|merges|leads|drives|implements)\b"
)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _plain(text):
    one = re.sub(r"[*_`]+", "", str(text or ""))
    return re.sub(r"\s+", " ", one).strip()


def shorten(text, limit=160):
    """Shorten one line at a clause end, else a word boundary (1.165.0).

    A line that fits is returned as is. Otherwise the cut is at the last
    `, ` `; ` or ` — ` that keeps at least half the limit, else at the last
    space. A dangling article, preposition or conjunction at the end is
    dropped, then `…` marks the cut. A word is never split.
    """
    one = _plain(text)
    if len(one) <= limit:
        return one
    room = one[: limit - 1]
    cut = -1
    for mark in (", ", "; ", " — ", " - "):
        cut = max(cut, room.rfind(mark))
    if cut < limit // 2:
        cut = room.rfind(" ")
    if cut <= 0:
        cut = len(room)
    head = room[:cut].rstrip(" ,;:—-")
    words = head.split(" ")
    while len(words) > 1 and words[-1].lower().strip(",;:") in DANGLING:
        words.pop()
    return " ".join(words).rstrip(" ,;:—-") + "…"


def _sentences(text):
    return [part.strip() for part in SENTENCE_SPLIT.split(_plain(text)) if part.strip()]


# A failed verify's reason in the Catch up first block (1.170.0).
FAILED_REASON_LIMIT = 200
RUN_DETAIL = re.compile(r"^(?:tests?\s+)?fail(?:s|ed)?\s+(at\s+[^:]{3,80}?):\s+", re.I)
CAUSE_WORDS = re.compile(
    r"\bmade\b.{0,60}\bstale\b|\bbecause\b|\bcaused\b|\bdue to\b|\bbroke\b|\bsince commit\b",
    re.I,
)
LOWER_LEAD = frozenset(
    "the a an all some most several every each no none one two three four five six "
    "seven eight nine ten test tests it its this these those both".split()
)
EARLIER_PASS = re.compile(r"^(?:earlier|previous|last)\s+(?:pass|run)\b", re.I)


def _clause_cut(sentence, limit):
    """A sentence cut at its last clause end that fits, or "" (1.170.0)."""
    one = sentence.rstrip(".!?")
    if len(one) + 1 <= limit:
        return one + "."
    room = one[: limit - 1]
    cut = -1
    for mark in ("; ", ", ", " — ", " - "):
        cut = max(cut, room.rfind(mark))
    if cut < 20:
        return ""
    head = _drop_dangling(room[:cut])
    return head + "." if len(head.split()) >= 3 else ""


def failed_reason(text, limit=FAILED_REASON_LIMIT):
    """A failed verify's Verify cell as one short reason (1.170.0).

    The cell's opening sentence, plus the sentence that names the cause
    (`3971963 made the asserts stale.`, `... because ...`) when there is
    one and it fits, about `limit` characters, cut only at a sentence end.
    Leading run detail (`fail at PR 7's tip abc1234: pipeline 6 run 251
    (Run tests, log 19), 110 failed, 173 passed.`) gives way to the next
    sentence, which keeps `at PR 7's tip abc1234` when it ends on `fail`.
    One sentence that is too long is cut at a clause end, else shortened
    at a word with `…`. The full cell stays in verify.md.
    """
    sentences = _sentences(text)
    if not sentences:
        return ""
    where = ""
    match = RUN_DETAIL.match(sentences[0])
    if match:
        where = match.group(1).strip()
        rest = sentences[0][match.end():].strip()
        if len(sentences) > 1:
            sentences = sentences[1:]
        elif rest:
            sentences = [rest]
    lead = sentences[0]
    if where and re.search(r"\bfail(?:s|ed)?[.!]?$", lead, re.I):
        lead = lead.rstrip(".!") + " " + where + "."
    if not lead.endswith((".", "!", "?")):
        lead += "."
    cause = ""
    for sentence in sentences[1:]:
        if EARLIER_PASS.match(sentence):
            continue
        if CAUSE_WORDS.search(sentence):
            cause = sentence if sentence.endswith((".", "!", "?")) else sentence + "."
            break
    if len(lead) > limit:
        cut = _clause_cut(lead, limit)
        lead = cut or shorten(lead, limit)
        cause = ""
    if cause and len(cause) > limit - len(lead) - 1:
        cut = _clause_cut(cause, limit - len(lead) - 1) if limit - len(lead) - 1 > 30 else ""
        cause = cut
    if cause and not CAUSE_WORDS.search(cause):
        cause = ""
    out = f"{lead} {cause}".strip() if cause else lead
    first = out.split(" ", 1)[0]
    if first.lower() in LOWER_LEAD and first[:1].isupper():
        out = out[:1].lower() + out[1:]
    return out


def step_heading(text):
    """A plan step's heading in plain words, or "" (1.165.0).

    The heading is a leading bold span (`**Export the receipt**`), or the
    words before ` — ` or a first `:` when they are short (at most eight
    words, no comma) and do not lead with a person.
    """
    raw = str(text or "").strip()
    match = re.match(r"\*\*([^*]{2,80})\*\*", raw)
    if match:
        head = match.group(1)
    else:
        plain = _plain(raw)
        match = re.match(r"(.{2,80}?)(?:\s+[—–]\s+|:\s)", plain)
        if not match:
            return ""
        head = match.group(1)
        if "," in head or len(head.split()) > 8:
            return ""
    head = _plain(head).strip(" .:;—–-")
    if not head or _fileish(head):
        return ""
    if re.match(r"^(?:[A-Z][\w'-]*\s+){0,3}[A-Z][\w'-]*\s+(?:builds|owns|writes)\b", head):
        return ""
    return head[:1].upper() + head[1:] + "."


# Branch description limits (1.166.0): up to three clean plan sentences,
# about 300 characters, cut only at a sentence end. A line built from task
# names stays near 160 characters.
DESCRIPTION_LIMIT = 300
TASK_SUMMARY_LIMIT = 160
FILE_EXT = re.compile(
    r"\.(?:md|markdown|ya?ml|py|json|bicep|cs|csproj|ts|js|txt|sh|ps1|xml|sql|toml|ini|cfg)$",
    re.I,
)
TASK_PREFIX = re.compile(r"^T\d+\s+")
ITEM_CUT = re.compile(r",\s|\s[—–]\s|\s(?:with|for|during|via|so that)\s")


def _fileish(text):
    """True when the text names a file or a path (1.166.0).

    `infra-orders/`, `docs/notes/x.md`, `cd-orders.yml`. A short upper-case
    pair such as `CI/CD` is not a path.
    """
    for token in str(text or "").split():
        tok = token.strip(",.;:()[]\"'`…")
        if not tok:
            continue
        if FILE_EXT.search(tok):
            return True
        if "/" in tok:
            if tok.endswith("/") or tok.count("/") >= 2 or "." in tok:
                return True
            if re.fullmatch(r"[a-z0-9_-]{4,}/[a-z0-9_.-]+", tok):
                return True
    return False


def _cap(text):
    return text[:1].upper() + text[1:] if text else text


# How a branch was made is a planning note, not a description (1.171.0):
# `The orders CI/CD branch, cut from develop after billing-ops.`
PLANNING_NOTE = re.compile(
    r"\b(?:cut|branched|branches|branch(?:es)? off|created|made|taken)\s+(?:off\s+|out\s+)?from\b"
    r"|\bafter\s+[\w./-]+\s+(?:merges|is merged|lands)\b"
    r"|\bfrom\s+(?:develop|main|master)\s+after\b",
    re.I,
)
ONLY_BRANCH = re.compile(r"^\s*the\s+.{0,60}\bbranch\s*\.?\s*$", re.I)


def planning_note(text):
    """True for a clause about how the branch was made, or one that only
    names the branch (1.171.0)."""
    text = str(text or "").strip()
    if not text:
        return False
    if PLANNING_NOTE.search(text):
        return True
    return bool(ONLY_BRANCH.match(text))


def _clean_sentence(sentence):
    """A plain description: ends with a full stop, no colon list, no person
    lead, no file or path list, and not a planning note (1.171.0)."""
    if not sentence.endswith("."):
        return False
    if planning_note(sentence):
        return False
    if ":" in sentence:
        return False
    if PERSON_LEAD.match(sentence):
        return False
    if _fileish(sentence):
        return False
    return len(sentence.split()) >= 3


def _drop_dangling(text):
    words = text.rstrip(" ,;:—–-.").split(" ")
    while len(words) > 1 and words[-1].lower().strip(",;:") in DANGLING:
        words.pop()
    return " ".join(words).rstrip(" ,;:—–-.")


def opening_clause(text, limit=DESCRIPTION_LIMIT):
    """A plan note trimmed to its opening clause, or "" (1.166.0).

    A step written as notes (`Orders CI/CD runs lint, tests and the deploy
    stages: infra first ...`) keeps the words before the first `:` or
    ` — `: `Orders CI/CD runs lint, tests and the deploy stages.` A clause
    about how the branch was made (`The orders CI/CD branch, cut from
    develop after billing-ops`) is a planning note and gives "" (1.171.0),
    so the step heading or the task names describe the branch. A person lead (`Person A builds PR 73: ...`) is dropped
    and the clause is taken from what follows. A trailing fragment (a short
    comma part such as `PR 73`, or a path) and a dangling word are dropped.
    The clause needs at least four words and no file or path.
    """
    one = _plain(text)
    if not one:
        return ""
    lead = PERSON_LEAD.match(one)
    if lead:
        if ":" not in one[lead.end():]:
            return ""
        one = one[lead.end():].split(":", 1)[1].strip()
    head = re.split(r":\s|:$|\s[—–]\s", one, maxsplit=1)[0]
    head = SENTENCE_SPLIT.split(head, maxsplit=1)[0]
    parts = [part.strip() for part in head.split(", ")]
    while len(parts) > 1 and (
        len(parts[-1].split()) < 3
        or _fileish(parts[-1])
        or re.fullmatch(r"(?:PR|T)\s?\d+", parts[-1])
    ):
        parts.pop()
    head = _drop_dangling(", ".join(parts))
    if len(head.split()) < 4 or _fileish(head) or PERSON_LEAD.match(head):
        return ""
    if planning_note(head):
        return ""
    if len(head) + 1 > limit:
        return ""
    return _cap(head) + "."


def _task_item(name):
    """A task name cut to its core words for a branch summary (1.166.0)."""
    match = ITEM_CUT.search(name)
    if match and len(name[: match.start()].split()) >= 2:
        name = name[: match.start()]
    return _drop_dangling(name)


def _join(items):
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + ", and " + items[-1]


def tasks_sentence(names, limit=TASK_SUMMARY_LIMIT):
    """One plain sentence from a branch's open task names, or "" (1.166.0).

    The last fallback for the branch description. A prefix every name
    shares (`Orders CI/CD:`) leads once and the rest are joined:
    `Orders CI/CD: infra Bicep, cd pipeline, ci lint and tests, and deploy
    README.` Each name keeps its words before a clause mark (`, `, ` with `,
    ` for ` ...). The line stays under `limit`, whole items only; items
    left out are counted (`and 2 more`).
    """
    items = [TASK_PREFIX.sub("", _plain(name)).strip() for name in names or []]
    items = [item for item in items if item and not PERSON_LEAD.match(item)]
    if not items:
        return ""
    if len(items) == 1:
        one = _drop_dangling(items[0])
        if len(one) + 1 > limit:
            one = shorten(one, limit).rstrip("…")
            one = _drop_dangling(one)
        return _cap(one) + "." if len(one.split()) >= 2 else ""
    prefix = ""
    heads = [item.split(":", 1)[0].strip() for item in items if ":" in item]
    if len(heads) == len(items) and len({head.lower() for head in heads}) == 1:
        prefix = heads[0] + ": "
        items = [item.split(":", 1)[1].strip() for item in items]
    elif len(heads) == len(items) or any(":" in item for item in items):
        items = [
            item.split(":", 1)[1].strip() if ":" in item and len(item.split(":", 1)[0].split()) <= 3 else item
            for item in items
        ]
    items = [_task_item(item) for item in items]
    items = [item for item in items if item]
    if not items:
        return ""
    # Only the line's first word is capitalised: `Add the pipeline and add
    # the test stage.` An acronym (`CI`, `README`) keeps its case.
    items = [items[0]] + [
        item[:1].lower() + item[1:] if re.match(r"[A-Z][a-z]", item) else item
        for item in items[1:]
    ]
    if not prefix:
        items[0] = _cap(items[0])
    for keep in range(len(items), 0, -1):
        shown = items[:keep]
        left = len(items) - keep
        if left:
            shown = shown + [f"{left} more"]
        line = prefix + _join(shown) + "."
        if len(line) <= limit:
            return line
    return ""


def about_sentence(text, limit=DESCRIPTION_LIMIT, names=None):
    """What a branch does, for its Run next block (1.164.0, 1.165.0, 1.166.0).

    In order, the first that gives a line:
      a. Up to three clean sentences from the start of the plan step (each
         ends with a full stop, no colon list, no person lead, no path),
         together at most about `limit` (300) characters. Cut only at a
         sentence end, never mid-sentence.
      b. The plan note trimmed to its opening clause (opening_clause()).
      c. The step's heading in plain words (step_heading()).
      d. One sentence from the branch's open task names (tasks_sentence()).
    "" only when there is no plan step and no usable task name. A person's
    name is never shown.
    """
    raw = str(text or "")
    if raw.strip():
        body = raw
        match = re.match(r"\s*\*\*[^*]{2,80}\*\*\s*[—–:.-]?\s*", raw)
        if match:
            body = raw[match.end():]
        picked = []
        for sentence in _sentences(body)[:3]:
            if not _clean_sentence(sentence):
                break
            if len(" ".join(picked + [sentence])) > limit:
                break
            picked.append(sentence)
        if picked:
            return _cap(" ".join(picked))
        for fallback in (opening_clause(body, limit), step_heading(raw)):
            if fallback:
                return fallback
    return tasks_sentence(names or [])


# A sentence that only points to a note (1.166.0): `The note
# docs/notes/x.md, in Open questions, question 5, says:`.
POINTER_WORDS = re.compile(r"\b(?:says|said|asks|writes|reads|note|notes|see|per|quote[sd]?)\b", re.I)
INLINE_QUOTE = re.compile(r":\s*[\"“]([^\"”]{8,})[\"”]")


def _pointer(sentence):
    """True for a sentence that ends with `:` or only points to a note."""
    one = sentence.strip()
    if one.endswith(":"):
        return True
    if one.endswith("?"):
        return False
    return _fileish(one) and bool(POINTER_WORDS.search(one))


def _unquote(text):
    return _plain(text).strip(" >\"“”'")


def question_text(text, limit=160, quote=None):
    """The quoted open question, short (1.165.0, 1.166.0).

    No markdown markers such as `**New:**`. The first sentence, unless it is
    a heading-like fragment (fewer than four words, such as `Client
    certificate.`) or a pointer to a note (a sentence that ends with `:`,
    or names a file and says `says`, `note`, `see` ...). For a pointer, the
    quoted question that follows: the blockquote under the bullet
    (`quote`), else text in quotes after the colon, else the first sentence
    ending in `?`. Cut at a clause end, never mid-word.
    """
    one = re.sub(r"\*\*[^*]{0,40}:\*\*\s*", "", str(text or ""))
    quoted = INLINE_QUOTE.search(one)
    inline = quoted.group(1) if quoted else ""
    if quoted:
        one = one[: quoted.start() + 1] + " " + one[quoted.end():]
    # A colon that ends a pointer ends its sentence too.
    units = []
    for sentence in _sentences(one):
        head, sep, tail = sentence.partition(": ")
        if sep and _pointer(head + ":") and (_fileish(head) or POINTER_WORDS.search(head)):
            units.extend([head + ":", tail.strip()] if tail.strip() else [head + ":"])
        else:
            units.append(sentence)
    units = [unit for unit in units if unit]
    if not units and not (quote or inline):
        return ""
    real = [u for u in units if not _pointer(u) and (len(u.split()) >= 4 or u.endswith("?"))]
    pointer = any(_pointer(u) for u in units)
    if pointer:
        for found in (_unquote(quote or ""), _unquote(inline)):
            if found:
                return shorten(found, limit)
        asked = [u for u in real if u.endswith("?")]
        if asked:
            return shorten(_unquote(asked[0]), limit)
        if real:
            return shorten(_unquote(real[0]), limit)
        return shorten(units[0], limit)
    pick = units[0] if units else _unquote(inline)
    if len(pick.split()) < 4 and not pick.endswith("?"):
        rest = units[1:]
        asked = [s for s in rest if s.endswith("?")]
        real = [s for s in rest if len(s.split()) >= 4]
        if asked:
            pick = asked[0]
        elif real:
            pick = real[0]
    return shorten(pick, limit)


def _task_id(label):
    match = re.match(r"(T\d+)\b", str(label).strip())
    return match.group(1) if match else str(label).strip()


def branch_block(branch_name, open_labels, first=None, slug=None, about=None, waits=None):
    """One ready branch in Run next (1.164.0, 1.165.0).

    The bold branch, one plain sentence from its plan step (left out when
    there is none), the open tasks one per line in the order the walk runs
    them, then each command alone in its code span under a label line: the
    whole branch first, then only the first task. A listed task that cannot
    start yet says why, `(waits on T5)`, from `waits` (T# to reason). When
    the first listed task cannot start, the task command names the first one
    that can and says so. One open task: `Run T#:` and one command.
    """
    waits = {str(key): str(value) for key, value in (waits or {}).items() if value}
    names = [str(label).strip() for label in open_labels or [] if str(label).strip()]
    first = str(first).strip() if first else (names[0] if names else "")
    if not names and first:
        names = [first]
    if not names:
        return ""
    lines = [f"**{branch_name}**"]
    # Always a description when there is a plan step or a usable task
    # name (1.166.0).
    sentence = about_sentence(about, names=names)
    if sentence:
        lines.append(sentence)
    count = len(names)
    lines.append(f"{count} open task{'' if count == 1 else 's'}:")
    for name in names:
        why = waits.get(_task_id(name))
        lines.append(f"- {name} ({why})" if why else f"- {name}")
    lines.append("")
    first_id = _task_id(first)
    task_cmd = f"/crav1-build-walk {slug} {first_id}" if slug else f"/crav1-build-walk {first_id}"
    if count == 1:
        lines.append(f"Run {first_id}:")
        lines.append(f"`{task_cmd}`")
    else:
        branch_cmd = f"/crav1-build-walk {slug} {branch_name}" if slug else f"/crav1-build-walk {branch_name}"
        lines.append("Run the whole branch:")
        lines.append(f"`{branch_cmd}`")
        if _task_id(names[0]) == first_id:
            lines.append(f"Run only {first_id}, the first task:")
        else:
            lines.append(f"Run only {first_id}, the first task that can start:")
        lines.append(f"`{task_cmd}`")
    return "\n".join(lines)


def run_entries(labels, branch_name, slug=None, open_labels=None, about=None, waits=None):
    """One Run next block per ready branch (1.164.0): see branch_block."""
    labels = [label for label in labels or [] if str(label).strip()]
    if not labels:
        return []
    opens = list(open_labels) if open_labels is not None else list(labels)
    return [branch_block(branch_name, opens, first=labels[0], slug=slug, about=about, waits=waits)]


BLOCK_RULE = "\n\n---\n\n"
VERIFY_COMMAND = "/crav1-verify-build-against-spec"
PUSH_COMMAND = "git push"
FIX_COMMAND = "/crav1-fix-build-gaps"


def _ids(ids):
    out = []
    for tid in ids or []:
        tid = str(tid).strip()
        if tid and tid not in out:
            out.append(tid)
    return sorted(out, key=lambda t: (int(t[1:]) if re.fullmatch(r"T\d+", t) else 10**9, t))


def catch_up_block(slug=None, behind=None, orphans=None, ahead=0, failed=None, uncommitted=None):
    """`**Catch up first**` for Run next (1.167.0), or "".

    Things behind that the user can fix now with one command each, before
    any branch: verify.md behind tasks.md (`behind`, T#s), a verify.md row
    for a T# that is not in tasks.md (`orphans`), and a specs repo ahead of
    origin (`ahead`, commits). The bold heading, one or two plain sentences
    of what is behind, then each command alone in its code span under its
    label. /crav1-verify-build-against-spec both checks the behind tasks
    and drops an orphan row, so those two share one command and one label.
    A built task whose verify failed (`failed`, T#s or dicts with `task` and
    `reason`, 1.169.0) gets its own `Fix T#:` label and
    /crav1-fix-build-gaps command, not a second verify. Empty when nothing
    is behind. The reason is failed_reason(), one short sentence or two
    (1.170.0), never the whole Verify cell.
    """
    fails = []
    for item in failed or []:
        if isinstance(item, dict):
            tid, why = str(item.get("task") or "").strip(), failed_reason(item.get("reason") or "")
        else:
            tid, why = str(item).strip(), ""
        if tid and tid not in [f[0] for f in fails]:
            fails.append((tid, why))
    behind = _ids(behind)
    orphans = _ids(orphans)
    try:
        ahead = int(ahead or 0)
    except (TypeError, ValueError):
        ahead = 0
    files = [str(f).strip() for f in uncommitted or [] if str(f).strip()]
    if not behind and not orphans and ahead <= 0 and not fails and not files:
        return ""
    sentences = []
    behind_text = _join(behind) if behind else ""
    orphan_text = _join(orphans) if orphans else ""
    rows = "a row" if len(orphans) == 1 else "rows"
    which = "which is not in tasks.md" if len(orphans) == 1 else "which are not in tasks.md"
    if behind and orphans:
        sentences.append(f"verify.md is behind for {behind_text}, and it has {rows} for {orphan_text}, {which}.")
    elif behind:
        sentences.append(f"verify.md is behind for {behind_text}.")
    elif orphans:
        sentences.append(f"verify.md has {rows} for {orphan_text}, {which}.")
    for tid, why in fails:
        sentences.append(f"{tid} failed verify: {why.rstrip('.')}." if why else f"{tid} failed verify.")
    unit = "commit" if ahead == 1 else "commits"
    # The push label already says how far ahead the specs repo is, so no
    # sentence repeats it (1.175.0).
    lines = ["**Catch up first**", ""]
    if sentences:
        lines[1:1] = [" ".join(sentences)]
    verify_cmd = f"{VERIFY_COMMAND} {slug}" if slug else VERIFY_COMMAND
    row_word = "row" if len(orphans) == 1 else "rows"
    if behind and orphans:
        lines.append(f"Check {behind_text} against the spec and remove the {orphan_text} {row_word}:")
        lines.append(f"`{verify_cmd}`")
    elif behind:
        lines.append(f"Check {behind_text} against the spec:")
        lines.append(f"`{verify_cmd}`")
    elif orphans:
        where = "it is" if len(orphans) == 1 else "they are"
        lines.append(f"Remove the {orphan_text} {row_word} ({where} in verify.md but not in tasks.md):")
        lines.append(f"`{verify_cmd}`")
    for tid, _why in fails:
        lines.append(f"Fix {tid}:")
        lines.append(f"`{FIX_COMMAND} {slug} {tid}`" if slug else f"`{FIX_COMMAND} {tid}`")
    if files:
        # 1.176.0: commit the walk's own changes before any push, on every result.
        count = len(files)
        noun = "file" if count == 1 else "files"
        # 1.180.0 (S3): the files are the slice's changed spec files, which
        # other skills may have written too, not only the walk's.
        lines.append(f"Commit the {count} changed spec {noun}:")
        lines.append("`/crav1-finalize-commit`")
        lines.append("Then push the specs repo:")
        lines.append(f"`{PUSH_COMMAND}`")
    elif ahead > 0:
        lines.append(f"Push the specs repo, which is {ahead} {unit} ahead of origin:")
        lines.append(f"`{PUSH_COMMAND}`")
    return "\n".join(lines)


def run_block(entries, catch_up=None) -> str:
    """`Run next:` and each entry (1.165.0, 1.167.0).

    A horizontal rule (`---`, with a blank line on each side so it never
    turns the line above into a heading) sits between two entries, so each
    branch block stands apart in any Markdown viewer. A catch-up block
    (catch_up_block()) comes first, with the same rule before the first
    branch block.
    """
    runs = [str(entry).strip("\n") for entry in entries or [] if str(entry).strip()]
    first = str(catch_up or "").strip("\n")
    if first.strip():
        runs = [first] + runs
    if not runs:
        return ""
    return "Run next:\n\n" + BLOCK_RULE.join(runs)


# ---------- The ending ----------

def _prefixed(text, word):
    text = str(text).strip()
    if not text:
        return ""
    return text if text.startswith(word + ":") else f"{word}: {text}"


_LIST_ITEM = re.compile(r"^\s*\d+\.\s")


def _join_after_list(lines: list[str]) -> str:
    """Join the bottom lines; a line after a numbered list gets a blank line first (1.177.0).

    Without it Markdown folds `Waiting: ...` into the merge list's last item.
    """
    out = ""
    prev_last = ""
    for line in lines:
        first = line.split("\n", 1)[0]
        if out:
            sep = "\n\n" if _LIST_ITEM.match(prev_last) and not _LIST_ITEM.match(first) else "\n"
            out += sep
        out += line
        prev_last = line.rsplit("\n", 1)[-1]
    return out


def compose(
    run=None,
    held=None,
    branch_runs=None,
    built=None,
    built_header=None,
    left=None,
    waiting=None,
    because=None,
    alternatives=None,
    notes=None,
    uncommitted=None,
    catch_up=None,
) -> str:
    """The one ending, in the shared order. Empty parts are left out.

    `catch_up` is a catch_up_block() text, or a dict of its keywords
    (`slug`, `behind`, `orphans`, `ahead`); it leads Run next (1.167.0).
    """
    parts: list[str] = []
    if isinstance(catch_up, dict):
        catch_up = catch_up_block(**{
            key: catch_up.get(key) for key in ("slug", "behind", "orphans", "ahead") if key in catch_up
        })
    block = run_block(run, catch_up)
    if block:
        parts.append(block)
    if held:
        parts.append("Held:\n" + "\n".join(str(line) for line in held))
    if branch_runs:
        parts.append("Branch runs:\n" + "\n".join(str(line) for line in branch_runs))
    if built:
        parts.append((built_header or "Built:") + "\n" + "\n".join(str(line) for line in built))
    if left:
        parts.append("Left:\n" + "\n".join(str(line) for line in left))
    if waiting:
        if isinstance(waiting, str):
            waiting = [_prefixed(waiting, "Waiting")]
        lines = [str(line) for line in waiting if str(line).strip()]
        if lines:
            parts.append(_join_after_list(lines))
    if because:
        parts.append(str(because))
    if alternatives:
        lines = [str(line) for line in alternatives if str(line).strip()]
        if lines:
            parts.append("\n".join(lines))
    for note in notes or []:
        if note:
            parts.append(str(note))
    if uncommitted:
        parts.append(_prefixed(uncommitted, "Uncommitted"))
    return "\n\n".join(parts)


# ---------- The ready-check reply ----------

def counts_table(counts: dict) -> str:
    slug = counts.get("slug") or ""
    head = "| Slice | " + " | ".join(name for name, _ in COUNT_COLUMNS) + " |"
    rule = "| --- |" + " --- |" * len(COUNT_COLUMNS)
    row = f"| {slug} | " + " | ".join(str(counts.get(key, 0)) for _, key in COUNT_COLUMNS) + " |"
    return "\n".join((head, rule, row))


def ready_reply(
    slug: str,
    result: str,
    counts: dict | None,
    ending: str,
    sources: list[str] | None = None,
    build_map: str | None = None,
    work_item: bool = False,
    next_line: str | None = None,
    stop: bool = False,
) -> str:
    """The whole brief ready-check reply. Print it verbatim (1.156.0)."""
    if stop:
        return ending or ""
    parts = [f"Tasks ready to build — {slug}"]
    if counts:
        parts.append(counts_table(counts))
    parts.append(f"Result: {result}")
    if ending:
        parts.append(ending)
    if next_line:
        parts.append(next_line)
    tail = []
    if work_item:
        tail.append("Task states in Azure Boards are not read here; /crav1-ado-sync brings them back.")
    if sources:
        tail.append(f"Source: docs/specs/{slug}/" + ", ".join(sources))
    if build_map:
        tail.append(f"Build map: {build_map}")
        # The zoomable page, label on its own line, command alone (1.164.0).
        # export-map stays inside build-map.md.
        tail.append("Zoom the map in your browser:")
        tail.append(f"`/crav1-tasks-ready-to-build {slug} open-map`")
    if tail:
        parts.append("\n".join(tail))
    return "\n\n".join(parts)


def not_ready_next(slug: str, counts: dict | None, question_first: bool) -> str | None:
    """The one Run next entry a ready check without branch blocks prints (references next-*)."""
    counts = counts or {}
    left = sum(int(counts.get(key, 0) or 0) for key in ("ready", "waiting", "waits_in_order", "blocked"))
    # Run next with the label above the command, never a Next: line (1.176.0).
    if left == 0 and not counts.get("needs_verify"):
        return "Nothing needed now."
    if left == 0:
        return (
            "Run next:\n\nVerify the built tasks, which aren't verified yet:\n"
            f"`/crav1-verify-build-against-spec {slug}`"
        )
    if question_first and not counts.get("ready"):
        return (
            "Run next:\n\nResolve the open question that blocks the first task:\n"
            f"`/crav1-resolve-open-questions {slug}`"
        )
    return None



# ---------- The verify reply (1.168.0) ----------

VERIFY_STATUSES = (
    ("tick_pending", "Implemented, verified, tick pending", "verified, tick pending"),
    # 1.182.0: the old on-branch wording is the same state as tick pending.
    ("tick_pending", "Implemented, verified on branch", "verified, tick pending"),
    ("verified", "Implemented, verified", "verified"),
    ("failed", "Implemented, verify failed", "failed"),
    ("not_implemented", "Not implemented", "not implemented"),
    ("unverified", "Claimed done, unverified", "unverified"),
    ("no_task", "Acceptance with no task", "acceptance with no task"),
)
TASK_LINE = re.compile(r"^\s*- \[(?: |x|X)\] (T\d+)\b")
FINALIZE_COMMAND = "/crav1-finalize-commit"


def _cells(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _section(text, prefix):
    """The lines under the `## <prefix>...` heading, up to the next `## `."""
    out, inside = [], False
    for line in str(text or "").splitlines():
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].strip().startswith(prefix)
            continue
        if inside:
            out.append(line)
    return out


def status_key(status):
    """The verify status key for a Status cell, or "" (1.168.0)."""
    plain = _plain(status).lower()
    for key, label, _word in VERIFY_STATUSES:
        if plain.startswith(label.lower()):
            return key
    return ""


def verify_counts(text):
    """Counts from verify.md's TL;DR table, by status key (1.168.0)."""
    counts = {}
    for line in _section(text, "TL;DR"):
        if not line.strip().startswith("|"):
            continue
        cells = _cells(line)
        if len(cells) < 2:
            continue
        key = ""
        for k, label, _word in VERIFY_STATUSES:
            if _plain(cells[0]).lower() == label.lower():
                key = k
        if key and cells[1].strip().isdigit():
            counts[key] = int(cells[1])
    return counts


def verify_tasks(text):
    """T# to (status key, Verify cell) from verify.md's Tasks overview, in file order."""
    rows = {}
    for line in _section(text, "Tasks"):
        if not line.strip().startswith("|"):
            continue
        cells = _cells(line)
        if len(cells) < 3 or not re.fullmatch(r"T\d+", _plain(cells[0])):
            continue
        verify = cells[3] if len(cells) > 3 else ""
        rows[_plain(cells[0])] = (status_key(cells[2]), _plain(verify))
    return rows


def result_line(counts):
    """`Result:` with the non-zero counts, verified first (1.168.0)."""
    counts = counts or {}
    parts = []
    for key, _label, word in VERIFY_STATUSES:
        n = int(counts.get(key, 0) or 0)
        if n:
            parts.append(f"{n} {word}")
    return "Result: " + (", ".join(parts) if parts else "no tasks checked") + "."


def verify_changes(previous, current, task_ids=None):
    """One line per task whose state changed since the last verify (1.168.0).

    `previous` and `current` are verify_tasks() maps. A status change gives
    `T6 failed: <its Verify cell, shortened>`. A row the new file no longer
    has gives `T44 row dropped: not in tasks.md`. No previous file: no lines.
    """
    if not previous:
        return []
    words = {key: word for key, _label, word in VERIFY_STATUSES}
    lines = []
    for tid, (key, verify) in current.items():
        before = previous.get(tid)
        if before is not None and before[0] == key:
            continue
        word = words.get(key, "checked")
        head = f"{tid} {word}" if before is not None else f"{tid} new, {word}"
        short = failed_reason(verify, 160).rstrip(".") if key == "failed" else shorten(verify, 120)
        lines.append(f"{head}: {short}" if verify else head)
    known = set(task_ids) if task_ids is not None else None
    for tid in previous:
        if tid not in current and (known is None or tid not in known):
            lines.append(f"{tid} row dropped: not in tasks.md")
    return lines


def verify_catch_up_block(slug=None, uncommitted=None, ahead=0, plan_notes=None):
    """`**Catch up first**` for the verify reply (1.168.0), or "".

    What the user can settle now with one command each: a plan note such as
    `T24 to T26 may belong to another slice` (`/crav1-tighten-plan`), then
    the files this run wrote and did not commit
    (`/crav1-finalize-commit`) and the push. Same layout as catch_up_block().
    """
    notes = [_plain(note).rstrip(".") + "." for note in plan_notes or [] if _plain(note)]
    files = [str(f).strip() for f in uncommitted or [] if str(f).strip()]
    try:
        ahead = int(ahead or 0)
    except (TypeError, ValueError):
        ahead = 0
    if not (notes or files or ahead > 0):
        return ""
    sentences = list(notes)
    if files:
        sentences.append(f"{_join(files)} {'is' if len(files) == 1 else 'are'} not committed.")
    unit = "commit" if ahead == 1 else "commits"
    # The push label already says how far ahead the specs repo is, so no
    # sentence repeats it (1.175.0).
    lines = ["**Catch up first**", ""]
    if sentences:
        lines[1:1] = [" ".join(sentences)]
    tail = f" {slug}" if slug else ""
    if notes:
        lines.append("Settle the plan note in the plan:" if len(notes) == 1 else "Settle the plan notes in the plan:")
        lines.append(f"`/crav1-tighten-plan{tail}`")
    if files:
        lines.append(f"Commit {_join(files)}:")
        lines.append(f"`{FINALIZE_COMMAND}`")
        lines.append("Then push the specs repo:")
        lines.append(f"`{PUSH_COMMAND}`")
    elif ahead > 0:
        lines.append(f"Push the specs repo, which is {ahead} {unit} ahead of origin:")
        lines.append(f"`{PUSH_COMMAND}`")
    return "\n".join(lines)


def step_block(step):
    """One verify next step (1.168.0): the reason once, then the label on its
    own line and the command alone in its code span. A dict with `reason`,
    `label`, `command` and an optional bold `heading`; no command: the
    reason only (`Nothing needed now.`)."""
    if isinstance(step, str):
        return step.strip()
    step = step or {}
    lines = []
    if step.get("heading"):
        lines.append(f"**{step['heading']}**")
    if step.get("reason"):
        lines.append(_plain(step["reason"]))
    command = str(step.get("command") or "").strip().strip("`")
    if command:
        if lines:
            lines.append("")
        lines.append(str(step.get("label") or "Run:").strip())
        lines.append(f"`{command}`")
    return "\n".join(lines)


def verify_reply(
    slug,
    counts=None,
    changes=None,
    steps=None,
    catch_up=None,
    waiting=None,
    report=None,
    walk=False,
    full_text=None,
):
    """The brief verify reply (1.168.0). Print it verbatim.

    The header, the Result line, one line per changed task, Run next (a
    Catch up first block, then each step), Waiting (only what the user
    cannot act on now), then `Report:`. With the word `full`, `full_text`
    (verify.md's TL;DR and Tasks overview) follows the Result line. When
    /crav1-build-walk opened verify (`walk`), the walk owns Run next.
    """
    parts = [f"Verify — {slug}", result_line(counts)]
    if full_text:
        parts.append(full_text.strip())
    lines = [str(line).strip() for line in changes or [] if str(line).strip()]
    if lines:
        parts.append("Changed since the last verify:\n" + "\n".join(f"- {line}" for line in lines))
    if not walk:
        if isinstance(catch_up, dict):
            catch_up = verify_catch_up_block(slug=slug, **{
                key: catch_up.get(key)
                for key in ("uncommitted", "ahead", "plan_notes")
                if key in catch_up
            })
        entries = [step_block(step) for step in steps or []]
        entries = [entry for entry in entries if entry.strip()]
        if not entries and not (catch_up or "").strip():
            entries = ["Nothing needed now."]
        parts.append(run_block(entries, catch_up))
    if waiting:
        if isinstance(waiting, str):
            waiting = [waiting]
        wait = [_prefixed(line, "Waiting") for line in waiting if str(line).strip()]
        if wait:
            parts.append("\n".join(wait))
    parts.append(f"Report: {report or f'docs/specs/{slug}/verify.md'}")
    return "\n\n".join(part for part in parts if part)


def _git(root, *args):
    import subprocess

    try:
        done = subprocess.run(
            ["git", *args], cwd=str(root), capture_output=True, text=True, encoding="utf-8", timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout if done.returncode == 0 else None


def _full_text(text):
    keep = []
    for prefix, title in (("TL;DR", "## TL;DR"), ("Tasks", "## Tasks — overview (dependency order)")):
        body = [line for line in _section(text, prefix) if not line.startswith("Next:") and not line.startswith("<!--")]
        while body and not body[0].strip():
            body.pop(0)
        while body and not body[-1].strip():
            body.pop()
        if body:
            keep.append(title + "\n\n" + "\n".join(body))
    return "\n\n".join(keep)


def _walk_progress_mod():
    import importlib.util

    here = Path(__file__).resolve().parent
    path = here.parent.parent / "crav1-tighten-and-plan-ready-to-build" / "scripts" / "walk_progress.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("crav1_walk_progress_for_verify", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def ready_branch_blocks(root, slug=None):
    """Run next branch blocks from the ready check (1.171.0).

    The same blocks the build walk prints: description, open tasks, the
    whole-branch entry and the first task. A task that waits on a merge is
    not here (readiness reads build-progress). Empty when nothing can start
    or the ready-check script is not installed.
    """
    mod = _walk_progress_mod()
    if mod is None:
        return []
    root = Path(root)
    try:
        branches = mod.ready_branches(root)
        cmd_slug = mod.command_slug(root) if slug is None else slug
    except Exception:  # noqa: BLE001 - a readiness failure leaves the steps empty
        return []
    blocks = []
    for branch in branches or []:
        tasks = branch.get("tasks") or []
        if not tasks:
            continue
        opens = branch.get("open_tasks") or tasks

        def label(task):
            return f"{task.get('id')} {task.get('title') or ''}".strip()

        waits = {task.get("id"): task.get("waits") for task in opens if task.get("waits")}
        block = branch_block(
            branch.get("branch") or "",
            [label(task) for task in opens],
            first=label(tasks[0]),
            slug=cmd_slug,
            about=branch.get("about"),
            waits=waits,
        )
        if block:
            blocks.append(block)
    return blocks


def verify_state(state):
    """The verify_reply() keywords from a state dict (1.168.0).

    `root` is the spec folder. The counts, the changed tasks and the
    Uncommitted files come from verify.md, the committed verify.md
    (`git show HEAD:`, or `previous`, a file path), tasks.md and git status.
    The skill adds only what it judged: `steps`, `plan_notes`, `waiting`,
    `walk`, `full`. With no `steps`, the branch blocks for what can start
    come from the ready check (1.171.0).
    """
    root = Path(state["root"])
    slug = state.get("slug") or root.name
    text = (root / "verify.md").read_text(encoding="utf-8") if (root / "verify.md").is_file() else ""
    if state.get("previous"):
        prev_path = Path(state["previous"])
        previous = prev_path.read_text(encoding="utf-8") if prev_path.is_file() else ""
    else:
        previous = _git(root, "show", "HEAD:./verify.md") or ""
    tasks_file = root / "tasks.md"
    task_ids = None
    if tasks_file.is_file():
        task_ids = [m.group(1) for m in (TASK_LINE.match(l) for l in tasks_file.read_text(encoding="utf-8").splitlines()) if m]
    changes = state.get("changes")
    if changes is None:
        changes = verify_changes(verify_tasks(previous), verify_tasks(text), task_ids)
    uncommitted = state.get("uncommitted")
    if uncommitted is None:
        uncommitted = []
        for name in state.get("written") or ["verify.md"]:
            out = _git(root, "status", "--porcelain", "--", name)
            if out and out.strip():
                uncommitted.append(name)
    ahead = state.get("ahead")
    if ahead is None:
        out = _git(root, "rev-list", "--count", "@{u}..HEAD")
        ahead = int(out.strip()) if out and out.strip().isdigit() else 0
    steps = state.get("steps") or []
    if not steps and not state.get("walk") and root.is_dir():
        # Build what is left: the branch blocks come from the ready check,
        # not from hand-written steps (1.171.0).
        steps = ready_branch_blocks(root, state.get("command_slug"))
    return {
        "slug": slug,
        "counts": verify_counts(text),
        "changes": changes,
        "steps": steps,
        "catch_up": {
            "uncommitted": uncommitted,
            "ahead": ahead,
            "plan_notes": state.get("plan_notes") or [],
        },
        "waiting": state.get("waiting") or [],
        "report": state.get("report") or f"docs/specs/{slug}/verify.md",
        "walk": bool(state.get("walk")),
        "full_text": _full_text(text) if state.get("full") else None,
    }


def main(argv=None) -> int:
    _utf8_stdout()
    parser = argparse.ArgumentParser(description="Compose the shared walk ending")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--json", help="state file with compose() keys")
    group.add_argument("--verify", help="state file for the verify reply (1.168.0): root, steps, ...")
    args = parser.parse_args(argv)
    if args.verify:
        state = json.loads(Path(args.verify).read_text(encoding="utf-8-sig"))
        print(verify_reply(**verify_state(state)))
        return 0
    state = json.loads(Path(args.json).read_text(encoding="utf-8"))
    keys = compose.__code__.co_varnames[: compose.__code__.co_argcount]
    print(compose(**{key: state[key] for key in keys if key in state}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
