#!/usr/bin/env python3
"""State machine for /crav1-design-architecture (1.181.0, linked topics and goal changes 1.188.0,
stored order, notes, small fixes and design branches 1.189.0).

Owns the sandbox format under docs/architecture/designs/<topic>/ and every move:
create, status, resume, park, fan-out, lean, settle, question, answer, skip,
stage, compare, compare-topics, review, go-ahead, ending, route,
change-goal (1.188.0), revisit (1.188.0), note, small-fix, branch-behind and linked-behind (1.189.0), switch-branch and commit (1.190.0).

Before go-ahead every write stays inside the topic folder. A run without the
user (--headless) may only prepare: lean, compare, compare-topics, status.
Content comes in through --input <json file>. Prints plain text or JSON.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
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

DESIGNS = Path("docs/architecture/designs")
ARCH_SPEC = Path("docs/architecture/spec.md")
DECIDED = "## Decided, not built yet"
OPEN_Q = "## Open questions"
START_WORDS = ["resume", "park", "status", "fan-out", "stage-it", "go-ahead", "compare-topics", "prepare", "change-goal", "builds-on", "note", "small-fix", "screen", "next", "questions", "proposal", "stages", "end", "close", "reopen"]
TOPIC_WORDS = {"resume", "change-goal", "note", "small-fix", "park", "status", "go-ahead", "fan-out", "stage-it"}
HEADLESS_WORDS = ["resume", "park", "status", "prepare"]
HEADLESS_ALLOWED = {"status", "resume", "screen", "lean", "compare", "compare-topics", "route", "ending", "review", "note", "branch-behind", "linked-behind"}
CREATE_KEYS = {"ask", "end_goal", "drivers", "constraints", "criteria", "design", "design_title", "decisions", "notes"}
CHANGE_KEYS = {"ask", "end_goal", "drivers", "constraints", "criteria", "decisions", "renames", "drop_reasons", "reopen", "notes"}
INPUTS_DIR = "inputs"
_ROOT: list = []
_CMD: list = []
# The kit version this skill's files last changed in. SKILL.md carries the same marker (1.190.0).
SKILL_VERSION = "1.201.1"
SCRATCH_MOVES = {"ending", "lean", "settle", "stage", "compare", "compare-topics"}
GOAL_KEYS = {"ask", "end_goal", "drivers", "constraints", "criteria", "decisions"}
STATES = {"open", "leaning", "settled", "to-question", "to-research", "skipped", "reopened", "dropped"}
CONFIRMED = "## Confirmed"
STOP_WORDS = {"the", "and", "for", "with", "not", "from", "into", "that", "this", "are", "was", "but", "its", "any", "all", "can", "has", "have", "one", "two", "via", "per", "may", "must", "should", "only", "each", "out", "off", "own", "our", "use", "uses", "used"}
GUARDED_MARKS = ("Asked:", "Pending:", "Answered:", "Approved:", "Blocks:")


class Refused(Exception):
    pass


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "item"


def fhash(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()[:10] if path.is_file() else "missing"


def today() -> str:
    return _dt.date.today().isoformat()


def asset(name: str) -> str:
    return (Path(__file__).resolve().parent.parent / "assets" / name).read_text(encoding="utf-8")


# ---------------------------------------------------------------- write guard
class Writer:
    """Every file write goes through here. Pre-go-ahead: topic folder only."""

    def __init__(self, root: Path, topic: str, extra: set[str] | None = None):
        self.root = root.resolve()
        self.topic_dir = (self.root / DESIGNS / topic).resolve()
        self.extra = {str((self.root / e).resolve()) for e in (extra or set())}
        self.written: list[str] = []

    def allowed(self, path: Path) -> bool:
        p = path.resolve()
        if p == self.topic_dir or self.topic_dir in p.parents:
            return True
        return str(p) in self.extra

    def write(self, path: Path, text: str) -> None:
        if not self.allowed(path):
            raise Refused(f"refused: {path.relative_to(self.root) if path.resolve().is_relative_to(self.root) else path} is outside the design sandbox")
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_file() and path.read_text(encoding="utf-8") == text:
            return
        path.write_text(text, encoding="utf-8")
        self.written.append(str(path.resolve().relative_to(self.root)))


# ---------------------------------------------------------------- formats
def split_sections(text: str) -> tuple[str, dict[str, str], list[str]]:
    head, sections, order, cur = [], {}, [], None
    for line in text.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            order.append(cur)
            sections[cur] = []
        elif cur is None:
            head.append(line)
        else:
            sections[cur].append(line)
    return "\n".join(head), {k: "\n".join(v).strip("\n") for k, v in sections.items()}, order


def meta(head: str) -> dict[str, str]:
    out = {}
    for line in head.splitlines():
        m = re.match(r"^- ([A-Z][A-Za-z ]+): (.*)$", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def bullets(body: str) -> list[str]:
    return [l[2:].strip() for l in body.splitlines() if l.startswith("- ") and l[2:].strip() not in ("", "none yet")]


def parse_goal(text: str) -> dict:
    head, sec, _ = split_sections(text)
    title = head.splitlines()[0][len("# Goal: "):] if head.startswith("# Goal: ") else ""
    m = meta(head)
    decisions, dropped = [], {}
    for item in bullets(sec.get("Decisions", "")):
        dm = re.match(r"^(.*) \(dropped: (.*)\)$", item)
        if dm:
            dropped[dm.group(1)] = dm.group(2)
            decisions.append(dm.group(1))
        else:
            decisions.append(item)
    return {"topic": title, "ask": m.get("Ask", "").strip('"'), "builds_on": m.get("Builds on", ""),
            "end_goal": sec.get("End goal", ""), "drivers": bullets(sec.get("Drivers", "")),
            "constraints": bullets(sec.get("Constraints", "")), "criteria": bullets(sec.get("Criteria", "")),
            "decisions": decisions, "dropped": dropped, "fixed": bullets(sec.get(FIXED_HEAD, "")),
            "changes": sec.get("Goal changes", ""), "applied": bullets(sec.get("Applied inputs", ""))}


FIXED_HEAD = "Fixed from the base topic"


def render_goal(g: dict) -> str:
    def bl(xs):
        return "\n".join(f"- {x}" for x in xs) if xs else "- none yet"
    link = f"- Builds on: {g['builds_on']}\n" if g.get("builds_on") else ""
    out = (f"# Goal: {g['topic']}\n\n- Ask: \"{g['ask']}\"\n{link}\n## End goal\n\n{g['end_goal']}\n\n"
           f"## Drivers\n\n{bl(g['drivers'])}\n\n## Constraints\n\n{bl(g['constraints'])}\n\n"
           f"## Criteria\n\n{bl(g['criteria'])}\n")
    # 1.190.0: the decision order lives on each decision (Order: N); goal.md no longer stores a Decisions list.
    if g.get("builds_on"):
        out += (f"\n## {FIXED_HEAD}\n\nSettled in topic {g['builds_on']}. Fixed inputs here; a change goes to that topic as a revisit.\n\n"
                + bl(g.get("fixed", [])) + "\n")
    if g.get("changes"):
        out += "\n## Goal changes\n\n" + g["changes"].strip("\n") + "\n"
    if g.get("applied"):
        out += "\n## Applied inputs\n\nSaved goal files in inputs/ that are already in this goal.\n\n" + "\n".join(f"- {x}" for x in g["applied"]) + "\n"
    return out


DEC_KEYS = ["State", "Order", "Options shown", "Leaning", "Recommended", "Draft ADR", "Open question in", "Sources", "Reopened", "Reverses", "Dropped", "Renamed from", "Drivers", "Detail"]


def parse_design(text: str) -> dict:
    head, sec, _ = split_sections(text)
    first = head.splitlines()[0] if head else ""
    m = meta(head)
    decisions, cur = [], None
    for line in sec.get("Decisions", "").splitlines():
        if line.startswith("- "):
            cur = {"title": line[2:].strip(), "State": "open"}
            if cur["title"] != "none yet":
                decisions.append(cur)
        elif cur is not None and line.startswith("  - "):
            k, _, v = line[4:].partition(": ")
            cur[k.strip()] = v.strip()
    migrated = _ensure_order(decisions)
    return {"title": first[len("# Design: "):] if first.startswith("# Design: ") else first, "migrated": migrated,
            "topic": m.get("Topic", ""), "status": m.get("Status", "open"),
            "ask": m.get("Ask", "").strip('"'), "end_state": sec.get("End state", ""),
            "decisions": decisions, "drivers": bullets(sec.get("Drivers", "")),
            "ideas": bullets(sec.get("Ideas", "")), "small_fixes": bullets(sec.get("Small fixes", ""))}


def _order(dec: dict) -> int:
    try:
        return int(dec.get("Order", "0"))
    except ValueError:
        return 0


def _ensure_order(decs: list[dict]) -> bool:
    """Give every decision an Order: N. A file without them keeps its list position (migration)."""
    missing = [x for x in decs if x.get("title") != "none yet" and not _order(x)]
    if not missing:
        return False
    top = max((_order(x) for x in decs), default=0)
    for x in missing:
        top += 1
        x["Order"] = str(top)
    return True


def ordered(decs: list[dict]) -> list[dict]:
    return sorted(decs, key=lambda x: (_order(x), x["title"].casefold()))


def set_order(decs: list[dict], titles: list[str]) -> None:
    """Rewrite Order: N from a list of titles; the rest follow in their old order."""
    pos = {t: i for i, t in enumerate(titles, 1)}
    rest = [x for x in ordered(decs) if x["title"] not in pos]
    for x in decs:
        if x["title"] in pos:
            x["Order"] = str(pos[x["title"]])
    for i, x in enumerate(rest, len(pos) + 1):
        x["Order"] = str(i)


def render_design(d: dict) -> str:
    _ensure_order(d["decisions"])
    # 1.190.0: stored by title so parallel adds do not conflict; Order: N gives the order.
    decs = sorted(d["decisions"], key=lambda x: x["title"].casefold())
    lines = [f"# Design: {d['title']}", "", f"- Topic: {d['topic']}", f"- Status: {d['status']}",
             f"- Ask: \"{d['ask']}\"", "", "## End state", "", d["end_state"] or "Not designed yet.", "",
             "## Decisions", ""]
    if not decs:
        lines.append("- none yet")
    for dec in decs:
        if dec["title"] == "none yet":
            continue
        lines.append(f"- {dec['title']}")
        for k in DEC_KEYS:
            if dec.get(k):
                lines.append(f"  - {k}: {dec[k]}")
    lines += ["", "## Drivers", ""] + ([f"- {x}" for x in d["drivers"]] or ["- none yet"])
    lines += ["", "## Ideas", ""] + ([f"- {x}" for x in d["ideas"]] or ["- none yet"])
    if d.get("small_fixes"):
        lines += ["", "## Small fixes", "", "Accepted changes that need no design choice. Copied at go-ahead with no ADR.", ""]
        lines += [f"- {x}" for x in d["small_fixes"]]
    return "\n".join(lines) + "\n"


def parse_questions(text: str) -> list[dict]:
    qs, cur = [], None
    _, sec, _ = split_sections(text)
    for line in sec.get("Open", "").splitlines():
        if line.startswith("- "):
            cur = {"text": line[2:].strip()}
            qs.append(cur)
        elif cur is not None and line.startswith("  - "):
            k, _, v = line[4:].partition(": ")
            cur[k.strip().lower()] = v.strip()
    return [q for q in qs if q["text"] != "none yet"]


def render_questions(design: str, qs: list[dict]) -> str:
    lines = [f"# Open questions: {design}", "", "Sandbox only. Copied to the architecture spec at go-ahead when still open.", "", "## Open", ""]
    if not qs:
        lines.append("- none yet")
    for q in qs:  # the order they were asked (1.189.0)
        lines.append(f"- {q['text']}")
        for k in ("decision", "kind", "research", "stage", "answer", "asked"):
            if q.get(k):
                lines.append(f"  - {k.capitalize()}: {q[k]}")
    return "\n".join(lines) + "\n"


def parse_stages(text: str) -> list[dict]:
    out = []
    for block in re.split(r"^## ", text, flags=re.M)[1:]:
        lines = block.splitlines()
        name = re.sub(r"^Stage \d+: ", "", lines[0]).strip()
        st = {"name": name}
        for l in lines[1:]:
            if l.startswith("- "):
                k, _, v = l[2:].partition(": ")
                st[k.strip().lower().replace(" ", "_")] = v.strip()
        out.append(st)
    return out


def render_stages(design: str, stages: list[dict]) -> str:
    lines = [f"# Stages: {design}", "", "The user's named split of the designed end state, in order."]
    for i, st in enumerate(stages, 1):
        lines += ["", f"## Stage {i}: {st['name']}", "", f"- Reason: {st.get('reason', '')}"]
        if st.get("waits_on"):
            lines.append(f"- Waits on: {st['waits_on']}")
        lines.append(f"- State: {st.get('state', 'open')}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- topic access
class Topic:
    def __init__(self, root: Path, name: str):
        self.root, self.name = root, name
        self.dir = root / DESIGNS / name
        if not (self.dir / "goal.md").is_file():
            hint = branch_hint(root, name)
            raise Refused(hint or f"no topic {name} under {DESIGNS}")

    def designs(self) -> list[str]:
        d = self.dir / "designs"
        return sorted(p.name for p in d.iterdir() if (p / "design.md").is_file()) if d.is_dir() else []

    def ddir(self, design: str) -> Path:
        p = self.dir / "designs" / design
        if not (p / "design.md").is_file():
            raise Refused(f"no design {design} in topic {self.name}")
        return p

    def raw_goal(self) -> dict:
        return parse_goal((self.dir / "goal.md").read_text(encoding="utf-8"))

    def primary(self) -> str | None:
        names = self.designs()
        live = [n for n in names if self._design(n)["status"] == "chosen"] or \
            [n for n in names if self._design(n)["status"] != "rejected"]
        return live[0] if live else (names[0] if names else None)

    def goal(self) -> dict:
        """The goal; its decision list comes from the primary design's Order numbers (1.190.0)."""
        g = self.raw_goal()
        name = self.primary()
        if name:
            d = self.design(name)
            g["decisions"] = [x["title"] for x in ordered(d["decisions"])]
            g["dropped"] = {x["title"]: re.sub(r"^\d{4}-\d{2}-\d{2}: ", "", x.get("Dropped", "")) or "dropped"
                            for x in d["decisions"] if x["State"] == "dropped"}
        return g

    def _design(self, design: str) -> dict:
        return parse_design((self.ddir(design) / "design.md").read_text(encoding="utf-8"))

    def design(self, design: str) -> dict:
        d = self._design(design)
        if d.get("migrated"):
            old = self.raw_goal().get("decisions") or []
            if old:
                set_order(d["decisions"], old)
        return d

    def questions(self, design: str) -> list[dict]:
        p = self.ddir(design) / "questions.md"
        return parse_questions(p.read_text(encoding="utf-8")) if p.is_file() else []

    def stages(self, design: str) -> list[dict]:
        p = self.ddir(design) / "stages.md"
        return parse_stages(p.read_text(encoding="utf-8")) if p.is_file() else []

    def current(self, design: str | None) -> str:
        names = self.designs()
        if design:
            return design
        live = [n for n in names if self.design(n)["status"] in ("open", "parked")]
        if len(live) == 1 or (live and len(names) == 1):
            return live[0]
        if len(names) == 1:
            return names[0]
        raise Refused("several designs in this topic; name one with --design")


def find_decision(d: dict, title: str) -> dict:
    key = title.casefold().strip()
    for dec in d["decisions"]:
        if dec["title"].casefold() == key:
            return dec
    hits = [dec for dec in d["decisions"] if key in dec["title"].casefold()]
    if len(hits) == 1:
        return hits[0]
    raise Refused(f"no single decision matches the words: {title}")


def load_input(path: str | None) -> dict:
    """JSON from a file, or from stdin when the path is `-` (1.200.0). Never a shell heredoc."""
    if not path:
        return {}
    if path == "-":
        return json.loads(sys.stdin.read())
    p = Path(path)
    if _CMD and _CMD[0] in SCRATCH_MOVES and _in_inputs(p):
        raise Refused(f"{_CMD[0]} input is scratch: write it in the session's temp folder, not in {INPUTS_DIR}/, "
                      f"which holds only the user's own saved goal files: {path}")
    return json.loads(p.read_text(encoding="utf-8"))


def _in_inputs(p: Path) -> bool:
    """Is this file inside docs/architecture/designs/<topic>/inputs/?"""
    parts = p.resolve().parts
    for i in range(len(parts) - 3):
        if parts[i:i + 3] == ("docs", "architecture", "designs") and i + 4 < len(parts) and parts[i + 4] == INPUTS_DIR:
            return True
    return False


def _rel_input(root: Path, topic: str, p: Path) -> str | None:
    """inputs/<file> when p is in this topic's inputs/ folder, else None."""
    folder = (root / DESIGNS / topic / INPUTS_DIR).resolve()
    try:
        return f"{INPUTS_DIR}/{p.resolve().relative_to(folder).as_posix()}"
    except ValueError:
        return None


def ensure_inputs(root: Path, topic: str, w) -> None:
    """Topics from before 1.189.0 have no inputs/ folder: create it on the first save, no question (1.190.0)."""
    readme = root / DESIGNS / topic / INPUTS_DIR / "README.md"
    if not readme.is_file():
        w.write(readme, f"# Saved inputs: {topic}\n\nThe user's own saved goal files for this topic, such as a revised goal to apply with change-goal. "
                        "Scratch input (ending state, lean and settle drafts) goes in the session's temp folder, never here.\n")


def pending_goal_inputs(root: Path, topic: str, applied: list[str]) -> list[dict]:
    """Saved goal files in inputs/ that goal.md does not list as applied (1.190.0)."""
    folder = root / DESIGNS / topic / INPUTS_DIR
    out = []
    for f in sorted(folder.glob("*.json")) if folder.is_dir() else []:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict) or not (set(data) & GOAL_KEYS) or set(data) - (CREATE_KEYS | CHANGE_KEYS):
            continue
        ref = f"{INPUTS_DIR}/{f.name}@{fhash(f)}"
        if ref not in applied:
            out.append({"path": f"{INPUTS_DIR}/{f.name}", "ref": ref})
    return out


def check_keys(data: dict, allowed: set, move: str) -> None:
    unknown = sorted(k for k in data if k not in allowed)
    if unknown:
        raise Refused(f"{move} does not know the input key{'s' if len(unknown) > 1 else ''} {', '.join(unknown)}; "
                      f"known keys: {', '.join(sorted(allowed))}. Put anything else under notes, which is saved with note.")


def _decision_items(items: list) -> list[dict]:
    """Decision titles as strings, or {"title": ..., "detail": true} for a detail decision (1.189.0)."""
    out = []
    for i, x in enumerate(items, 1):
        if isinstance(x, dict):
            dec = {"title": x["title"], "State": "open", "Order": str(i)}
            if x.get("detail"):
                dec["Detail"] = "yes"
            out.append(dec)
        else:
            out.append({"title": x, "State": "open", "Order": str(i)})
    return out


def _git(root: Path, *args: str):
    import subprocess
    try:
        return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", timeout=15)
    except Exception:
        return None


def current_branch(root: Path) -> str | None:
    out = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
    if out is None or out.returncode != 0:
        return None
    return out.stdout.strip()


def branch_exists(root: Path, branch: str) -> str:
    """'local', 'origin' or '' for a branch name."""
    for ref, where in ((f"refs/heads/{branch}", "local"), (f"refs/remotes/origin/{branch}", "origin")):
        out = _git(root, "rev-parse", "--verify", "--quiet", ref)
        if out is not None and out.returncode == 0:
            return where
    return ""


def branch_hint(root: Path, topic: str) -> str:
    """Run next text when the topic lives on its design branch and this branch is another one."""
    cur = current_branch(root)
    branch = f"design/{topic}"
    if cur is None or cur == branch or not branch_exists(root, branch):
        return ""
    return switch_card(root, topic, cur)


def _behind(root: Path, ref: str) -> int | None:
    out = _git(root, "rev-list", "--count", f"HEAD..{ref}")
    if out is None or out.returncode != 0:
        return None
    return int(out.stdout.strip() or 0)


def _ref_ok(root: Path, ref: str) -> bool:
    out = _git(root, "rev-parse", "--verify", "--quiet", ref)
    return out is not None and out.returncode == 0


_DEFAULT: dict = {}


def default_branch(root: Path) -> tuple[str, str]:
    """The repo's default branch as a remote ref, resolved once per repo (1.191.0).

    origin/HEAD when set; else origin/main, then origin/master when they exist.
    Returns (ref, "") or ("", reason) when there is none; never raises."""
    key = str(Path(root).resolve())
    if key in _DEFAULT:
        return _DEFAULT[key]
    found = ("", "")
    out = _git(root, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if out is not None and out.returncode == 0 and out.stdout.strip().startswith("refs/remotes/"):
        ref = out.stdout.strip()[len("refs/remotes/"):]
        if _ref_ok(root, ref):
            found = (ref, "")
    if not found[0]:
        for ref in ("origin/main", "origin/master"):
            if _ref_ok(root, ref):
                found = (ref, "")
                break
    if not found[0]:
        found = ("", "no default branch found (origin/HEAD is not set and there is no origin/main or origin/master), "
                     "so the design branch was not compared with it")
    if out is not None:  # cache only inside a git repository
        _DEFAULT[key] = found
    return found


def default_name(root: Path, fallback: str = "main") -> str:
    """The default branch's short name for text (master, main, develop ...)."""
    ref, _ = default_branch(root)
    return ref.split("/", 1)[1] if ref else fallback


def branch_behind(root: Path, topic: str, do_fetch: bool = True) -> dict:
    """Is design/<topic> behind the default branch (origin/HEAD, 1.191.0), or behind design/<base> for a linked topic? (1.189.0)

    Mirrors the build walk's code-behind: behind offers a merge on a yes card,
    never a silent merge and never a rebase. {"state": "in-step" | "behind" |
    "not-on-design-branch" | "no-repo" | "offline", "behind": {ref: n}, "card", "ending"}.
    """
    branch = f"design/{topic}"
    cur = current_branch(root)
    if cur is None:
        return {"state": "no-repo", "behind": {}, "card": None, "ending": None}
    if cur != branch:
        return {"state": "not-on-design-branch", "branch": cur, "behind": {}, "card": None, "ending": None,
                "line": f"This is {cur}, not {branch}, so the design branch was not compared."}
    line = ""
    if do_fetch and not os.environ.get("CRAV1_NO_FETCH"):
        remotes = _git(root, "remote")
        if remotes is not None and "origin" in remotes.stdout.split():
            out = _git(root, "fetch", "-q", "origin")
            if out is None or out.returncode != 0:
                line = "origin could not be fetched; compared with the local copies."
            _DEFAULT.pop(str(Path(root).resolve()), None)
    refs = []
    dref, skipped = default_branch(root)
    if dref:
        refs.append(dref)
    goal_p = root / DESIGNS / topic / "goal.md"
    base = parse_goal(goal_p.read_text(encoding="utf-8")).get("builds_on") if goal_p.is_file() else ""
    if base:
        for ref in (f"design/{base}", f"origin/design/{base}"):
            if _ref_ok(root, ref):
                refs.append(ref)
                break
    behind = {r: n for r in refs if (n := _behind(root, r))}
    out = {"state": "behind" if behind else "in-step", "branch": branch, "behind": behind, "card": None, "ending": None}
    if dref:
        out["default_branch"] = dref
    else:
        out["skipped"] = skipped
    if line:
        out["line"] = line
    if not behind:
        return out
    what = " and ".join(f"{r} ({n} commit{'s' if n != 1 else ''})" for r, n in behind.items())
    out["line"] = f"{branch} is behind {what}."
    out["card"] = {"question": f"Merge {' and '.join(behind)} into {branch} before going on?",
                   "words": ["yes", "stop"], "recommended": "yes",
                   "options": [{"word": "yes", "label": "Merge it in (Recommended)",
                                "action": f"git merge --no-ff {' then '.join(behind)} into {branch}; never a rebase"},
                               {"word": "stop", "label": "Stop", "action": "merge nothing; the design branch stays as it is"}]}
    lines = ["Run next:", f"{branch} is behind {what}. Merge it in before going on; never rebase.", ""]
    for r in behind:
        name = r.split("/", 1)[1] if r == dref else r
        lines += [f"Merge {name} into the design branch:", f"`git merge --no-ff {r}`", ""]
    out["ending"] = "\n".join(lines).rstrip("\n") + "\n"
    return out


def cmd_branch_behind(a, root: Path) -> dict:
    status = branch_behind(root, slugify(a.topic), do_fetch=not a.no_fetch)
    if not a.yes or status["state"] != "behind":
        return status
    if a.headless:
        raise Refused("a run without the user does not merge; ask yes or stop on the card")
    merged = []
    for ref in status["behind"]:
        out = _git(root, "merge", "--no-ff", "--no-edit", ref)
        if out is None or out.returncode != 0:
            files = _git(root, "diff", "--name-only", "--diff-filter=U")
            names = [x for x in (files.stdout.split("\n") if files else []) if x.strip()]
            if not names:
                msg = ((out.stderr or out.stdout) if out else "git did not run").strip().splitlines()
                raise Refused(f"could not merge {ref} into {status['branch']}: {msg[0] if msg else 'unknown error'}. Nothing was merged.")
            _git(root, "merge", "--abort")
            raise Refused("\n".join(["Run next:", f"Merging {ref} into {status['branch']} conflicts in: {', '.join(names) or 'unknown files'}. "
                                     "Nothing was merged. Resolve the conflicts in those files, then commit the merge.", "",
                                     f"Merge {ref} into the design branch and resolve the conflicts:", f"`git merge --no-ff {ref}`"]) + "\n")
        merged.append(ref)
    return {"state": "in-step", "branch": status["branch"], "merged": merged, "behind": {}, "card": None, "ending": None,
            "line": f"Merged {' and '.join(merged)} into {status['branch']}."}


def linked_branches(root: Path, base: str) -> list[str]:
    """Linked topics whose committed goal.md on design/<linked> says Builds on: <base>."""
    out = _git(root, "for-each-ref", "--format=%(refname:short)", "refs/heads/design/")
    if out is None or out.returncode != 0:
        return []
    found = []
    for br in out.stdout.split():
        topic = br[len("design/"):]
        if topic == base:
            continue
        g = _git(root, "show", f"{br}:{(DESIGNS / topic / 'goal.md').as_posix()}")
        if g is not None and g.returncode == 0 and parse_goal(g.stdout).get("builds_on") == base:
            found.append(topic)
    return found


def linked_behind(root: Path, base: str) -> dict:
    """After a committed change to a base topic: which linked design branches are behind design/<base>? (1.189.0)"""
    bb = f"design/{base}"
    if current_branch(root) is None or not _ref_ok(root, bb):
        return {"state": "no-repo" if current_branch(root) is None else "no-base-branch", "behind": {}, "card": None, "ending": None}
    behind = {}
    for topic in linked_branches(root, base):
        out = _git(root, "rev-list", "--count", f"design/{topic}..{bb}")
        n = int(out.stdout.strip() or 0) if out is not None and out.returncode == 0 else 0
        if n:
            behind[f"design/{topic}"] = n
    res = {"state": "behind" if behind else "in-step", "base_branch": bb, "behind": behind, "card": None, "ending": None}
    if not behind:
        return res
    what = ", ".join(f"{b} ({n} commit{'s' if n != 1 else ''})" for b, n in behind.items())
    res["line"] = f"Linked design branches behind {bb}: {what}."
    res["card"] = {"question": f"Merge {bb} into {', '.join(behind)}?", "words": ["yes", "stop"], "recommended": "yes",
                   "options": [{"word": "yes", "label": "Merge it into each (Recommended)",
                                "action": f"switch to each branch, git merge --no-ff {bb}, switch back to {bb}; never a rebase"},
                               {"word": "stop", "label": "Stop", "action": "merge nothing; the linked branches stay as they are"}]}
    lines = ["Run next:", f"{what} {'is' if len(behind) == 1 else 'are'} behind {bb}. Merge the base into each; never rebase.", ""]
    for b in behind:
        lines += [f"Switch to {b}:", f"`git switch {b}`", "", f"Merge {bb} into it:", f"`git merge --no-ff {bb}`", ""]
    lines += [f"Switch back to {bb}:", f"`git switch {bb}`"]
    res["ending"] = "\n".join(lines) + "\n"
    return res


def cmd_linked_behind(a, root: Path) -> dict:
    base = slugify(a.topic)
    status = linked_behind(root, base)
    if not a.yes or status["state"] != "behind":
        return status
    if a.headless:
        raise Refused("a run without the user does not merge; ask yes or stop on the card")
    dirty = _git(root, "status", "--porcelain")
    if dirty is not None and dirty.stdout.strip():
        raise Refused("commit the base topic's change first; the working tree has uncommitted files")
    bb, start = status["base_branch"], current_branch(root)
    merged, conflict = [], None
    for b in status["behind"]:
        sw = _git(root, "switch", "-q", b)
        if sw is None or sw.returncode != 0:
            conflict = {"branch": b, "files": [], "error": (sw.stderr if sw else "").strip()}
            break
        out = _git(root, "merge", "--no-ff", "--no-edit", bb)
        if out is None or out.returncode != 0:
            files = _git(root, "diff", "--name-only", "--diff-filter=U")
            names = [x for x in (files.stdout.split("\n") if files else []) if x.strip()]
            _git(root, "merge", "--abort")
            conflict = {"branch": b, "files": names, "error": "" if names else ((out.stderr or out.stdout) if out else "").strip()}
            break
        merged.append(b)
    _git(root, "switch", "-q", start or bb)
    left = [b for b in status["behind"] if b not in merged and (not conflict or b != conflict["branch"])]
    res = {"base_branch": bb, "merged": merged, "untouched": left, "conflict": conflict}
    if conflict:
        b = conflict["branch"]
        why = f"conflicts in: {', '.join(conflict['files'])}" if conflict["files"] else f"failed: {conflict['error'] or 'unknown error'}"
        res["ending"] = "\n".join(["Run next:", f"Merging {bb} into {b} {why}. Nothing was merged there" +
                                   (f"; {', '.join(left)} {'was' if len(left) == 1 else 'were'} left untouched." if left else "."), "",
                                   f"Switch to {b}:", f"`git switch {b}`", "",
                                   f"Merge {bb} into it and resolve the conflicts:", f"`git merge --no-ff {bb}`"]) + "\n"
    return res


def _with_linked(res: dict, root: Path, topic: str) -> dict:
    st = linked_behind(root, topic)
    if st["state"] == "behind":
        res["linked_sync"] = st
    return res


def _with_sync(res: dict, a, root: Path, topic: str) -> dict:
    """resume and every move that starts work on a topic report whether the design branch is behind."""
    st = branch_behind(root, topic, do_fetch=not getattr(a, "no_fetch", False))
    if st["state"] in ("behind", "not-on-design-branch") or st.get("line"):
        res["branch_sync"] = st
    return res


def _version_key(v: str) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3]) if v else ()


def _stated_version(text: str) -> str:
    m = re.search(r"^Kit version: (\d+\.\d+\.\d+)", text, re.M)
    return m.group(1) if m else ""


def kit_check(root: Path) -> dict:
    """1.190.0: the stated kit version (workflow.md next to the skills) against this skill's files,
    and the specs repo's kit on this branch against the default branch's (1.191.0). Never guess a version."""
    here = Path(__file__).resolve().parent.parent
    wf = here.parent / "crav1-docs" / "reference" / "workflow.md"
    stated = _stated_version(wf.read_text(encoding="utf-8")) if wf.is_file() else ""
    skill_md = here / "SKILL.md"
    marker = re.search(r"Skill files: (\d+\.\d+\.\d+)", skill_md.read_text(encoding="utf-8")) if skill_md.is_file() else None
    skill = marker.group(1) if marker else ""
    out = {"stated": stated or "not found", "script": SKILL_VERSION, "skill_md": skill or "not found", "ok": True}
    problems = []
    if skill != SKILL_VERSION:
        problems.append(f"SKILL.md says skill files {skill or 'with no marker'}, the script is {SKILL_VERSION}")
    if not stated:
        problems.append("the stated kit version could not be read from crav1-docs/reference/workflow.md")
    elif _version_key(stated) < _version_key(SKILL_VERSION):
        problems.append(f"workflow.md states kit {stated}, older than these skill files ({SKILL_VERSION})")
    rel = ".cursor/skills/crav1/crav1-docs/reference/workflow.md"
    local = root / rel
    if local.is_file():
        repo_kit = _stated_version(local.read_text(encoding="utf-8"))
        out["repo_kit"] = repo_kit or "not found"
        dref, skipped = default_branch(root)
        main = _git(root, "show", f"{dref}:{rel}") if dref else None
        if dref:
            out["default_branch"] = dref
        elif skipped and current_branch(root) is not None:
            out["skipped"] = skipped
        if main is not None and main.returncode == 0:
            main_kit = _stated_version(main.stdout)
            out["main_kit"] = main_kit or "not found"
            if repo_kit and main_kit and _version_key(repo_kit) < _version_key(main_kit):
                out["kit_behind_main"] = True
                problems.append(f"this branch has kit {repo_kit}, {dref} has {main_kit}; merge {dref.split('/', 1)[1]} into the branch before the topic is touched")
    if problems:
        out.update(ok=False, problems=problems, run="/crav1-update-kit")
    return out


def switch_card(root: Path, topic: str, cur: str) -> str:
    branch = f"design/{topic}"
    return (f"the {topic} topic is on its design branch {branch}, not on {cur}. Offer the switch on a yes card; "
            f"after the yes run switch-branch --topic {topic} --yes, then run this move again")


def cmd_switch_branch(a, root: Path) -> dict:
    topic = slugify(a.topic)
    branch = f"design/{topic}"
    cur = current_branch(root)
    if cur is None:
        raise Refused("not a git repository; there is no design branch to switch to")
    if cur == branch:
        return {"branch": branch, "switched": False, "line": f"Already on {branch}."}
    where = branch_exists(root, branch)
    if not where:
        raise Refused(f"there is no branch {branch} here or on origin")
    card = {"question": f"Switch to {branch} and go on with the {topic.replace('-', ' ')} topic?", "words": ["yes", "stop"],
            "recommended": "yes",
            "options": [{"word": "yes", "label": "Switch (Recommended)", "action": f"git switch {branch}, then go on"},
                        {"word": "stop", "label": "Stop", "action": f"stay on {cur}; nothing changes"}]}
    if not a.yes:
        return {"branch": branch, "current": cur, "switched": False, "card": card}
    if a.headless:
        raise Refused("a run without the user does not switch branches; ask yes or stop on the card")
    dirty = _git(root, "status", "--porcelain")
    paths = [l[3:] for l in dirty.stdout.splitlines() if l.strip()] if dirty is not None else []
    if paths:
        raise Refused(f"the working tree has uncommitted changes, so nothing was switched: {', '.join(paths)}")
    out = _git(root, "switch", branch) if where == "local" else _git(root, "switch", "-c", branch, "--track", f"origin/{branch}")
    if out is None or out.returncode != 0:
        raise Refused(f"could not switch to {branch}: {(out.stderr if out else '').strip()}")
    return {"branch": branch, "switched": True, "line": f"Switched from {cur} to {branch}."}


def topic_dirty(root: Path, topic: str) -> list[str]:
    out = _git(root, "status", "--porcelain", "-uall", "--", (DESIGNS / topic).as_posix())
    if out is None or out.returncode != 0:
        return []
    return [l[3:] for l in out.stdout.splitlines() if l.strip()]


def cmd_commit(a, root: Path) -> dict:
    """1.190.0: commit the topic folder after the user's yes, before the ending."""
    topic = slugify(a.topic)
    Topic(root, topic)
    if current_branch(root) is None:
        raise Refused("not a git repository; nothing to commit")
    paths = topic_dirty(root, topic)
    if not paths:
        return {"topic": topic, "committed": False, "paths": [], "line": "Nothing to commit in the topic folder."}
    msg = f"Design {topic}: {a.message.strip() if a.message else 'save design work'}"
    card = {"question": f"Commit the {len(paths)} design file{'s' if len(paths) != 1 else ''} of {topic} now?",
            "words": ["yes", "not-now"], "recommended": "yes",
            "options": [{"word": "yes", "label": "Commit (Recommended)", "action": f"git commit with the message '{msg}'"},
                        {"word": "not-now", "label": "Not now", "action": "leave the files uncommitted; the ending says how many"}]}
    words = str(getattr(a, "words", "") or "")
    skill_text = (Path(__file__).resolve().parents[1] / "SKILL.md").read_text(encoding="utf-8")
    try:
        import importlib.util
        path = Path(__file__).resolve().parents[2] / "crav1-tasks-ready-to-build" / "scripts" / "run_ending.py"
        spec = importlib.util.spec_from_file_location("run_ending_commit", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        allowed = mod.commit_yes(bool(a.yes), words, skill_text)
    except Exception:
        allowed = bool(a.yes) and words.strip().lower() != "stop and commit"
    if not allowed:
        out = {"topic": topic, "committed": False, "paths": paths, "message": msg, "card": card}
        if words.strip().lower() == "stop and commit":
            out["line"] = "Stop and commit is not a yes here. Show the commit card."
        return out
    if a.headless:
        raise Refused("a run without the user does not commit; ask yes or not-now on the card")
    add = _git(root, "add", "--", (DESIGNS / topic).as_posix())
    com = _git(root, "commit", "-m", msg) if add is not None and add.returncode == 0 else add
    if com is None or com.returncode != 0:
        raise Refused(f"could not commit: {((com.stderr or com.stdout) if com else '').strip()}")
    return {"topic": topic, "committed": True, "paths": paths, "message": msg}


def ensure_design_branch(root: Path, topic: str, base: str = "") -> dict:
    """create: be on design/<topic>; create it (from design/<base> for a linked topic) when missing."""
    branch = f"design/{topic}"
    cur = current_branch(root)
    if cur is None:
        return {"branch": branch, "branch_state": "not a git repository; the design branch is not checked"}
    if cur == branch:
        return {"branch": branch, "branch_state": "already on it"}
    if branch_exists(root, branch):
        raise Refused(switch_card(root, topic, cur))
    start = []
    if base:
        bb = f"design/{base}"
        if cur != bb:
            if not branch_exists(root, bb):
                raise Refused(f"the base topic's design branch {bb} is not here; fetch it first")
            start = [bb] if branch_exists(root, bb) == "local" else [f"origin/{bb}"]
    out = _git(root, "switch", "-c", branch, *start)
    if out is None or out.returncode != 0:
        raise Refused(f"could not create {branch}: {(out.stderr if out else '').strip()}")
    return {"branch": branch, "branch_state": f"created from {start[0] if start else cur}"}


# ---------------------------------------------------------------- compare
def compare_text(t: Topic, scores: dict | None = None) -> str:
    goal = t.goal()
    old = {}
    p = t.dir / "compare.md"
    if p.is_file():
        rows = [l for l in p.read_text(encoding="utf-8").splitlines() if l.startswith("| ") and not l.startswith("| Criterion") and not l.startswith("| ---")]
        names = []
        for l in p.read_text(encoding="utf-8").splitlines():
            if l.startswith("| Criterion"):
                names = [c.strip() for c in l.strip("|").split("|")][1:]
        for l in rows:
            cells = [c.strip() for c in l.strip("|").split("|")]
            for n, v in zip(names, cells[1:]):
                old.setdefault(n, {})[cells[0]] = v
    designs = t.designs()
    for n, sc in (scores or {}).items():
        for crit, v in sc.items():
            old.setdefault(n, {})[crit] = v
    lines = [f"# Compare: {t.name}", "", "Designs in this topic scored against the shared criteria in goal.md.", "",
             "| Criterion | " + " | ".join(designs) + " |", "| --- |" + " --- |" * len(designs)]
    for crit in goal["criteria"]:
        lines.append(f"| {crit} | " + " | ".join(old.get(n, {}).get(crit, "unknown") for n in designs) + " |")
    lines += ["", "## Decisions", ""]
    for n in designs:
        d = t.design(n)
        settled = sum(1 for x in d["decisions"] if x["State"] == "settled")
        live = [x for x in d["decisions"] if x["State"] != "dropped"]
        lines.append(f"- {n}: {settled} of {len(live)} settled, status {d['status']}")
    return "\n".join(lines) + "\n"


def refresh_compare(t: Topic, w: Writer, scores: dict | None = None) -> None:
    if len(t.designs()) > 1 or (t.dir / "compare.md").is_file():
        w.write(t.dir / "compare.md", compare_text(t, scores))


# ---------------------------------------------------------------- moves
def cmd_route(a) -> str:
    word = (a.word or "").strip()
    if a.headless:
        if not word and not a.idea:
            raise Refused("Missing choice. Use one of: <idea text>, " + ", ".join(HEADLESS_WORDS) + ".")
        return "prepare" if word not in ("status", "park", "resume") else word
    if word == "builds-on":
        parts = (a.idea or "").split(None, 1)
        if len(parts) < 2:
            raise Refused("builds-on needs the base topic and the idea text: builds-on <base> <idea text>")
        return "builds-on"
    if word in ("resume", "screen"):
        return "screen"
    if word in START_WORDS:
        return word
    if word:
        raise Refused("Unknown word " + word + ". Use one of: <idea text>, " + ", ".join(START_WORDS) + ".")
    return "idea" if a.idea else "ask"


def cmd_create(a, root: Path) -> dict:
    data = load_input(a.input)
    check_keys(data, CREATE_KEYS, "create")
    topic = slugify(a.topic)
    tdir = root / DESIGNS / topic
    if (tdir / "goal.md").exists():
        raise Refused(f"topic {topic} already exists; use resume")
    base = slugify(a.builds_on) if getattr(a, "builds_on", None) else ""
    if base == topic:
        raise Refused("a topic cannot build on itself")
    if base and topic_dirty(root, base):
        raise Refused(f"commit the base topic {base} first; its folder has uncommitted files: {', '.join(topic_dirty(root, base))}")
    branch = ensure_design_branch(root, topic, base)
    if base:
        Topic(root, base)
    w = Writer(root, topic)
    goal = {"topic": topic, "ask": data.get("ask", ""), "end_goal": data.get("end_goal", ""),
            "drivers": data.get("drivers", []), "constraints": data.get("constraints", []),
            "criteria": data.get("criteria", []), "builds_on": base,
            "fixed": base_fixed(root, base) if base else []}
    rel = _rel_input(root, topic, Path(a.input)) if a.input else None
    if rel:
        goal["applied"] = [f"{rel}@{fhash(Path(a.input))}"]
    w.write(tdir / "goal.md", render_goal(goal))
    name = slugify(a.design or data.get("design", "first-design"))
    _new_design(root, topic, name, data.get("design_title", name.replace("-", " ")), goal["ask"],
                _decision_items(data.get("decisions", [])), goal["drivers"], w)
    if data.get("notes"):
        _write_note(root, topic, "notes from the goal input", data["notes"], "other", w)
    save_session(root, topic, status="open", mode="session", step="frame")
    res = {"topic": topic, "design": name, "branch": f"design/{topic}", "branch_state": branch["branch_state"], "written": w.written,
           "status_line": status_line(topic, "open", ""), "session": "open"}
    ensure_inputs(root, topic, w)
    if branch["branch_state"] == "already on it":
        _with_sync(res, a, root, topic)
    kc = kit_check(root)
    if not kc["ok"]:
        res["kit_check"] = kc
    if base:
        res |= {"builds_on": base, "branch_from": f"design/{base}", "fixed": goal["fixed"],
                "git": [f"git switch design/{base}", f"git switch -c design/{topic}"],
                "update_from_base": f"git merge design/{base}"}
    return res


def _new_design(root, topic, name, title, ask, decisions, drivers, w, end_state="", ideas=None):
    ddir = root / DESIGNS / topic / "designs" / name
    if (ddir / "design.md").exists():
        raise Refused(f"design {name} already exists")
    d = {"title": title, "topic": topic, "status": "open", "ask": ask, "end_state": end_state,
         "decisions": decisions, "drivers": drivers, "ideas": ideas or []}
    w.write(ddir / "design.md", render_design(d))
    w.write(ddir / "questions.md", render_questions(name, []))
    w.write(ddir / "diagrams.md", f"# Draft diagrams: {name}\n\nSandbox only. Not the live system or slice diagrams.\n")
    (ddir / "adr").mkdir(parents=True, exist_ok=True)


def save_design(t: Topic, name: str, d: dict, w: Writer) -> None:
    w.write(t.ddir(name) / "design.md", render_design(d))


def cmd_status(a, root: Path) -> dict:
    base = root / DESIGNS
    topics = sorted(p.name for p in base.iterdir() if (p / "goal.md").is_file()) if base.is_dir() else []
    if a.topic:
        topics = [a.topic]
    out = []
    for tn in topics:
        t = Topic(root, tn)
        for dn in t.designs():
            d = t.design(dn)
            out.append({"topic": tn, "design": dn, "status": d["status"],
                        "settled": [x["title"] for x in ordered(d["decisions"]) if x["State"] == "settled"],
                        "open": [x["title"] for x in ordered(d["decisions"]) if x["State"] != "settled"],
                        "questions": [q["text"] for q in t.questions(dn) if not q.get("answer")],
                        "stages": [s["name"] for s in t.stages(dn)]})
    links = {}
    every = sorted(p.name for p in base.iterdir() if (p / "goal.md").is_file()) if base.is_dir() else []
    for tn in every:
        b = Topic(root, tn).goal().get("builds_on")
        if b:
            links.setdefault(tn, {"builds_on": "", "built_on_by": []})["builds_on"] = b
            links.setdefault(b, {"builds_on": "", "built_on_by": []})["built_on_by"].append(tn)
    links = {k: v for k, v in links.items() if not a.topic or k == a.topic}
    return {"designs": out, "links": links} if links else {"designs": out}


def cmd_resume(a, root: Path):
    """resume is an alias of the status screen (1.200.0). --json keeps the old payload for callers that read fields."""
    if not getattr(a, "as_json", False):
        return screen_text(root, slugify(a.topic))
    return _resume_json(a, root)


def _resume_json(a, root: Path) -> dict:
    t = Topic(root, a.topic)
    kc = kit_check(root)
    if kc.get("kit_behind_main") and not a.skip_kit_check:
        st = branch_behind(root, t.name, do_fetch=not getattr(a, "no_fetch", False))
        return {"topic": t.name, "kit_check": kc, "branch_sync": st, "written": [],
                "note": f"the design branch's kit is behind {kc.get('default_branch', 'the default branch')}: offer the merge card (branch-behind --yes) before the topic is touched"}
    name = t.current(a.design)
    d = t.design(name)
    w = Writer(root, t.name)
    # Status, including parked, stays as it is on disk (1.201.1). A source
    # that changed still marks that decision reopened, which is the resume
    # record, not a status change.
    reopened = []
    for dec in d["decisions"]:
        if dec["State"] != "settled" or not dec.get("Sources"):
            continue
        changed = []
        for src in [s.strip() for s in dec["Sources"].split(",") if s.strip()]:
            path, _, h = src.rpartition("@")
            if fhash(root / path) != h:
                changed.append(path)
        if changed:
            dec["State"] = "reopened"
            dec["Reopened"] = f"{', '.join(changed)} changed since the last save"
            reopened.append({"decision": dec["title"], "changed": changed})
    if reopened and not a.headless:
        save_design(t, name, d, w)
        for st in t.stages(name):
            st["state"] = "needs another look"
        if t.stages(name):
            w.write(t.ddir(name) / "stages.md", render_stages(name, [dict(s, state="needs another look") for s in t.stages(name)]))
    ordered = goal_order(t.goal(), d)
    big = [x for x in ordered if not x.get("Detail")]
    detail = [x for x in ordered if x.get("Detail")]
    nxt = (reopened[0]["decision"] if reopened else None) or \
        next((x["title"] for x in ordered if x["State"] == "reopened"), None) or \
        next((x["title"] for x in big if x["State"] in ("open", "leaning")), None) or \
        next((x["title"] for x in detail if x["State"] in ("open", "leaning")), None)
    stages = t.stages(name)
    stage_work = [s["name"] for s in stages if s.get("state") != "open" and s.get("state")]
    if reopened:
        stage_work = [s["name"] for s in stages]
    res = {"topic": t.name, "design": name, "reopened": reopened, "next_decision": nxt,
           "stages_needing_work": stage_work, "written": w.written}
    _with_sync(res, a, root, t.name)
    if not kc["ok"]:
        res["kit_check"] = kc
    g = t.goal()
    pend = pending_goal_inputs(root, t.name, g.get("applied", []))
    if pend:
        res["pending_goal_inputs"] = pend
        res["pending_note"] = ("a saved goal file is not applied yet: offer change-goal with it on a card; "
                               "never recreate the topic")
    if g.get("builds_on"):
        base = g["builds_on"]
        now = base_fixed(root, base) if (root / DESIGNS / base / "goal.md").is_file() else g["fixed"]
        res["builds_on"] = base
        res["base_settled_since"] = [x for x in now if x not in g["fixed"]]
        res["base_reopened_since"] = [x for x in g["fixed"] if x.split(": ", 1)[0] not in {y.split(": ", 1)[0] for y in now}]
        res["fixed"] = now
        if now != g["fixed"] and not a.headless:
            w.write(t.dir / "goal.md", render_goal(dict(g, fixed=now)))
            res["written"] = w.written
    return res


def _now() -> str:
    """A date, not a clock time, so a saved session stays comparable (1.200.0)."""
    return today()


def session_path(root: Path, topic: str) -> Path:
    return root / DESIGNS / topic / "session.json"


def load_session(root: Path, topic: str) -> dict:
    """session.json is the source of truth. A missing file reads as open (1.200.0)."""
    path = session_path(root, topic)
    data = {"status": "open", "mode": "session", "topic": topic, "branch": f"design/{topic}",
            "decision": "", "step": "", "updated": ""}
    if path.is_file():
        try:
            saved = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            saved = {}
        if isinstance(saved, dict):
            data.update({k: saved.get(k, data.get(k, "")) for k in ("status", "mode", "decision", "step", "updated")})
    if data.get("status") not in ("open", "parked", "ended"):
        data["status"] = "open"
    if data.get("mode") not in ("session", "guided"):
        data["mode"] = "session"
    return data


def save_session(root: Path, topic: str, **fields) -> dict:
    data = load_session(root, topic)
    data.update(fields)
    data["topic"] = topic
    data["branch"] = f"design/{topic}"
    data["updated"] = _now()
    w = Writer(root, topic)
    w.write(session_path(root, topic), json.dumps(data, indent=2) + "\n")
    data["written"] = w.written
    return data


def plain_command(topic: str, word: str = "") -> str:
    """The one invocation shape (1.200.0): `/crav1-design-architecture <topic>` and an optional word."""
    if not topic:
        return "/crav1-design-architecture"
    if word:
        return f"/crav1-design-architecture {topic} {word}"
    return f"/crav1-design-architecture {topic}"


def status_line(topic: str, status: str = "open", step: str = "") -> str:
    park = f"`{plain_command(topic, 'park')}`"
    back = f"`{plain_command(topic)}`"
    if status == "parked":
        return f"Design session parked: {topic}. Open: {back}"
    if status == "ended":
        return f"Design session ended: {topic}. Reopen: `{plain_command(topic, 'reopen')}`"
    extra = f" Step: {step}." if step else ""
    return f"Design session open: {topic}.{extra} Park: {park}"


def _topics(root: Path) -> list[str]:
    base = root / DESIGNS
    if not base.is_dir():
        return []
    return sorted(p.name for p in base.iterdir() if (p / "goal.md").is_file() and not p.name.startswith("_"))


def _next_open(root: Path, topic: str) -> str:
    try:
        t = Topic(root, topic)
        name = t.current(None)
        d = t.design(name)
    except Refused:
        return ""
    ordered_decs = goal_order(t.goal(), d)
    big = [x for x in ordered_decs if not x.get("Detail")]
    detail = [x for x in ordered_decs if x.get("Detail")]
    return (next((x["title"] for x in ordered_decs if x["State"] == "reopened"), None)
            or next((x["title"] for x in big if x["State"] in ("open", "leaning", "to-question", "to-research")), None)
            or next((x["title"] for x in detail if x["State"] in ("open", "leaning", "to-question", "to-research")), None)
            or "")


def _open_questions(root: Path, topic: str) -> list[dict]:
    try:
        t = Topic(root, topic)
        name = t.current(None)
    except Refused:
        return []
    return [q for q in t.questions(name) if not q.get("answer")]


def _uncommitted_count(root: Path, topic: str) -> int:
    try:
        return len(topic_dirty(root, topic))
    except Exception:
        return 0


_OWNER_VERB = re.compile(r"^(.+?)\s+(?:decides|decide|has|knows|owns|answers|answer)\b", re.I)
_WAIT_MAX = 120


def design_branch_ref(root: Path, topic: str) -> str:
    """A design/<topic> ref whose tree holds this topic's goal.md, when we are not on it (1.201.1)."""
    branch = f"design/{topic}"
    if current_branch(root) == branch:
        return ""
    where = branch_exists(root, branch)
    if where == "local":
        refs = [branch]
    elif where == "remote":
        refs = [f"origin/{branch}"]
    else:
        refs = [branch, f"origin/{branch}"]
    path = f"{DESIGNS.as_posix()}/{topic}/goal.md"
    for ref in refs:
        out = _git(root, "cat-file", "-e", f"{ref}:{path}")
        if out is not None and out.returncode == 0:
            return ref
    return ""


def _owner_name(raw: str) -> str:
    raw = re.split(r"\s*;\s*", (raw or "").strip(), maxsplit=1)[0].strip()
    found = _OWNER_VERB.match(raw)
    return (found.group(1) if found else raw).strip()


def _question_view(item: dict) -> dict:
    text = (item.get("text") or "").strip()
    found = re.search(r"\s*\(([^)]*)\)\s*$", text)
    who_raw = found.group(1).strip() if found else ""
    body = text[: found.start()].strip() if found else text
    return {"body": body.rstrip("."), "who": _owner_name(who_raw), "asked": (item.get("asked") or "").strip()}


def _fit_line(prefix: str, bodies: list[str]) -> str:
    bodies = [b for b in bodies if b] or ["an open question"]
    text = f"{prefix}{'; '.join(bodies)}."
    if len(text) <= _WAIT_MAX:
        return text
    room = _WAIT_MAX - len(prefix)
    kept: list[str] = []
    used = 0
    for body in bodies:
        extra = len(body) if not kept else 2 + len(body)
        if used + extra > room:
            break
        kept.append(body)
        used += extra
    more = len(bodies) - len(kept)
    if not kept:
        text = f"{prefix}{bodies[0][: max(1, room - 1)].rstrip()}…"
    else:
        text = f"{prefix}{'; '.join(kept)}"
        if more:
            note = f" (+{more} more)"
            if len(text) + len(note) <= _WAIT_MAX:
                text += note
    if len(text) > _WAIT_MAX:
        text = text[: _WAIT_MAX - 1].rstrip() + "…"
    if not text.endswith((".", "…")):
        text += "."
    return text


def _waiting_lines(questions: list[dict]) -> list[str]:
    """One line per person and recorded date. The name appears once (1.201.1)."""
    groups: dict[tuple, list] = {}
    order: list[tuple] = []
    for item in (_question_view(q) for q in questions):
        key = (item["who"] or "someone not named", item["asked"])
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(item["body"])
    lines = []
    for who, date in order:
        prefix = f"Waiting: {who}" + (f", asked {date}" if date else "") + ": "
        lines.append(_fit_line(prefix, groups[(who, date)]))
    return lines


def _live_decisions(root: Path, topic: str) -> list[dict]:
    try:
        t = Topic(root, topic)
        d = t.design(t.current(None))
    except Refused:
        return []
    return [x for x in d.get("decisions") or [] if x.get("State") not in ("settled", "dropped")]


def _proposal_pages(root: Path, topic: str) -> list[str]:
    folder = root / DESIGNS / topic
    names = ["proposal.html", "proposal.md", "briefing.html", "briefing.md"]
    pages = [str((folder / name).relative_to(root).as_posix()) for name in names if (folder / name).is_file()]
    dated = root / "docs" / "architecture" / "proposals"
    if not dated.is_dir():
        return pages
    slug = topic.lower()
    spaced = slug.replace("-", " ")
    for path in sorted(dated.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in (".html", ".md"):
            continue
        rel = path.relative_to(root).as_posix()
        blob = rel.lower()
        if slug in blob:
            pages.append(rel)
            continue
        try:
            head = path.read_text(encoding="utf-8", errors="ignore")[:8192].lower()
        except OSError:
            continue
        if slug in head or (spaced and spaced in head):
            pages.append(rel)
    return pages


def screen_facts(root: Path, topic: str) -> dict:
    """Read session.json and the topic files. Writes nothing (1.200.0, 1.201.1)."""
    topic = slugify(topic) if topic else ""
    facts = {"topic": topic, "topics": _topics(root), "where": "none", "status": "", "next_decision": "",
             "questions": [], "uncommitted": 0, "proposals": [], "needs": "", "commands": [], "waits": [],
             "reason": "", "card": ""}
    if not topic:
        facts["needs"] = "Start a topic, or open one that already exists." if facts["topics"] else "Start a topic."
        facts["reason"] = "No topic was named."
        facts["commands"] = [("Start a topic", "/crav1-design-architecture <idea text>")]
        facts["commands"] += [(f"Open {name.replace('-', ' ')}", plain_command(name)) for name in facts["topics"]]
        return facts
    if not (root / DESIGNS / topic / "goal.md").is_file():
        ref = design_branch_ref(root, topic)
        if ref:
            cur = current_branch(root) or "this branch"
            facts["where"] = "other-branch"
            facts["branch"] = f"design/{topic}"
            facts["needs"] = f"{topic} is on its design branch."
            facts["reason"] = f"The {topic.replace('-', ' ')} topic is on design/{topic}, not on {cur}."
            facts["commands"] = [("Switch to the design branch", plain_command(topic))]
            facts["card"] = "\n".join([
                f"Switch to design/{topic} and go on with the {topic.replace('-', ' ')} topic?",
                "- **Switch (Recommended)** (`yes`): git switch, then go on.",
                f"- **Stop** (`stop`): stay on {cur}; nothing changes.",
            ])
            return facts
        facts["where"] = "missing"
        facts["needs"] = f"{topic} is not a topic yet."
        facts["reason"] = f"{topic} is not a topic yet."
        facts["commands"] = [("Start this topic", "/crav1-design-architecture <idea text>")]
        facts["commands"] += [(f"Open {name.replace('-', ' ')}", plain_command(name)) for name in facts["topics"]]
        return facts
    sess = load_session(root, topic)
    try:
        design_status = Topic(root, topic).design(Topic(root, topic).current(None))["status"]
    except Refused:
        design_status = "open"
    status = sess.get("status") or "open"
    if design_status == "parked" and status == "open" and not session_path(root, topic).is_file():
        status = "parked"
    facts["status"] = status
    facts["where"] = "parked" if status == "parked" else ("ended" if status == "ended" else "open")
    facts["next_decision"] = _next_open(root, topic)
    facts["questions"] = _open_questions(root, topic)
    facts["uncommitted"] = _uncommitted_count(root, topic)
    facts["proposals"] = _proposal_pages(root, topic)
    facts["step"] = sess.get("decision") or facts["next_decision"]
    facts["waits"] = _waiting_lines(facts["questions"])
    live = _live_decisions(root, topic)
    waiting_on_people = bool(live) and all(x.get("State") in ("to-question", "to-research") for x in live)
    facts["waiting_on_people"] = waiting_on_people
    commands = []
    if status == "ended":
        facts["needs"] = "The session is ended."
        facts["reason"] = "The session is ended. Reopen it to work on it again."
        commands = [("Reopen the topic", plain_command(topic, "reopen"))]
    elif waiting_on_people:
        facts["needs"] = "The open decisions are waiting on named people."
        parked = " The session is parked." if status == "parked" else ""
        facts["reason"] = "The open decisions are waiting on named people." + parked
        commands = [
            ("Ask the open questions", "/crav1-show-or-ask-open-questions"),
            ("Edit the proposal", plain_command(topic, "proposal")),
        ]
        if status == "open":
            commands.append(("Park", plain_command(topic, "park")))
    elif facts["next_decision"]:
        facts["needs"] = f"{facts['next_decision']} is still open."
        if status == "parked":
            facts["reason"] = f"The session is parked. The next open decision is {facts['next_decision']}."
        else:
            facts["reason"] = f"The next open decision is {facts['next_decision']}."
        commands.append(("Next decision", plain_command(topic, "next")))
        if facts["questions"]:
            commands.append(("Show open questions", plain_command(topic, "questions")))
        commands.append(("Edit the proposal", plain_command(topic, "proposal")))
        commands.append(("Write stages", plain_command(topic, "stages")))
        if status == "open":
            commands.append(("Park", plain_command(topic, "park")))
    else:
        facts["needs"] = "Every decision is settled."
        facts["reason"] = "The session is parked." if status == "parked" else "Every decision is settled."
        commands.append(("Write stages", plain_command(topic, "stages")))
        commands.append(("Edit the proposal", plain_command(topic, "proposal")))
        commands.append(("Review go-ahead", plain_command(topic, "go-ahead")))
        if facts["questions"]:
            commands.append(("Show open questions", plain_command(topic, "questions")))
        if status == "open":
            commands.append(("Park", plain_command(topic, "park")))
    facts["commands"] = commands
    return facts


def _blocks(commands: list[tuple[str, str]], reason: str = "") -> str:
    parts = ["Run next:", reason or "The session is open.", ""]
    for label, command in commands:
        parts += [f"{label}:", f"`{command}`", ""]
    return "\n".join(parts).rstrip() + "\n"


def screen_text(root: Path, topic: str) -> str:
    """The one start (1.200.0). Fresh and resume both print this. Writes nothing."""
    facts = screen_facts(root, topic)
    blocks = _blocks(facts["commands"], facts.get("reason") or "")
    if facts["where"] in ("none", "missing"):
        listed = ", ".join(facts["topics"]) if facts["topics"] else "none"
        where = "no topic yet" if facts["where"] == "none" else f"{facts['topic']} is not a topic yet"
        lines = [blocks.rstrip(), "", f"Where: {where}.", f"Topics: {listed}.", "", f"Needs doing: {facts['needs']}"]
        return "\n".join(lines) + "\n"
    if facts["where"] == "other-branch":
        lines = [blocks.rstrip(), "", (facts.get("card") or "").rstrip(), "", f"Needs doing: {facts['needs']}"]
        return "\n".join(lines) + "\n"
    topic = facts["topic"]
    step = facts["step"] if facts["where"] == "open" else ""
    lines = [blocks.rstrip(), "", status_line(topic, facts["status"], step), ""]
    if facts["where"] == "parked":
        where = f"{topic} is parked."
    elif facts["where"] == "ended":
        where = f"{topic} is ended."
    elif facts.get("waiting_on_people"):
        where = "topic open. The open decisions are waiting on named people."
    elif facts["next_decision"]:
        where = f"topic open. Next decision: {facts['next_decision']}."
    else:
        where = "topic open. Every decision is settled."
    lines.append(f"Where: {where}")
    if facts["waits"]:
        lines.extend(facts["waits"])
    else:
        lines.append("Waiting: nothing.")
    n = facts["uncommitted"]
    lines.append(uncommitted_count_line(n) if n else "Uncommitted: none.")
    if facts["proposals"]:
        lines.append("Proposal: " + ", ".join(facts["proposals"]) + ".")
    else:
        lines.append("Proposal: none.")
    lines += ["", f"Needs doing: {facts['needs']}"]
    return "\n".join(lines) + "\n"


def uncommitted_count_line(n: int) -> str:
    noun = "file" if n == 1 else "files"
    return f"Uncommitted: {n} {noun}; commit with `/crav1-finalize-commit` when ready."


def cmd_screen(a, root: Path) -> str:
    return screen_text(root, getattr(a, "topic", "") or "")


def cmd_next(a, root: Path) -> dict:
    """Enter the next decision. The only way the guided card flow starts (1.200.0)."""
    topic = slugify(a.topic)
    if not (root / DESIGNS / topic / "goal.md").is_file():
        if design_branch_ref(root, topic):
            raise Refused(switch_card(root, topic, current_branch(root) or "this branch"))
        raise Refused(f"{topic} is not a topic yet; the status screen offers how to start one")
    title = _next_open(root, topic)
    if not title:
        return {"topic": topic, "next_decision": "", "status_line": status_line(topic, "open", ""),
                "note": "Every decision is settled. The status screen offers stages, the proposal and go-ahead."}
    t = Topic(root, topic)
    name = t.current(None)
    d = t.design(name)
    if d.get("status") == "parked":
        d["status"] = "open"
        w = Writer(root, topic)
        save_design(t, name, d, w)
    save_session(root, topic, status="open", mode="guided", decision=title, step="next")
    return {"topic": topic, "design": name, "next_decision": title, "mode": "guided",
            "status_line": status_line(topic, "open", title),
            "note": "Show the decision card for this decision. Nothing is settled until a choose word."}


def cmd_questions(a, root: Path) -> str:
    topic = slugify(a.topic)
    qs = _open_questions(root, topic)
    save_session(root, topic, status="open", mode="session", step="questions")
    lines = [status_line(topic, "open", ""), ""]
    if not qs:
        lines.append("No open questions.")
    else:
        lines.append("Open questions:")
        for q in qs:
            lines.append(f"- {q.get('text')}")
    lines += ["", "Run next:", "These are the open questions.", "", "Back to the session:", f"`{plain_command(topic)}`"]
    return "\n".join(lines) + "\n"


def _shared_section(root: Path, topic: str) -> str:
    """One source for the proposal and the briefing (1.200.0)."""
    path = root / DESIGNS / topic / "shared.md"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip() + "\n"
    try:
        t = Topic(root, topic)
        d = t.design(t.current(None))
    except Refused:
        return "## Shared decisions\n\n- none yet\n"
    lines = ["## Shared decisions", ""]
    settled = [x for x in ordered(d["decisions"]) if x.get("State") == "settled"]
    open_ones = [x for x in ordered(d["decisions"]) if x.get("State") not in ("settled", "dropped")]
    if not settled and not open_ones:
        lines.append("- none yet")
    for dec in settled:
        lines.append(f"- decided: {dec['title']}")
    for dec in open_ones:
        lines.append(f"- proposed: {dec['title']}")
    return "\n".join(lines) + "\n"


def _svg_from_mermaid(text: str) -> str:
    """A self-contained SVG. No remote font and no private path (1.200.0)."""
    labels = []
    for line in str(text or "").splitlines():
        line = line.strip()
        if not line or line.startswith("%%") or line.lower().startswith("flowchart") or line.lower().startswith("graph"):
            continue
        labels.append(re.sub(r"[\[\]{}()]", " ", line)[:80])
    if not labels:
        labels = ["diagram"]
    rows = []
    for i, label in enumerate(labels[:12]):
        y = 20 + i * 36
        safe = (label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        rows.append(f'<rect x="10" y="{y}" width="460" height="28" class="box"/><text x="20" y="{y + 18}">{safe}</text>')
    height = 28 + len(rows) * 36
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="{height}" role="img">'
            f'<style>.box{{fill:#f4f4f4;stroke:#444}}.decided{{fill:#e7f5ee}}.proposed{{fill:#f6f6f6}}</style>'
            + "".join(rows) + "</svg>")


def _proposal_markdown(root: Path, topic: str, briefing: bool = False) -> str:
    title = "Briefing" if briefing else "Proposal"
    shared = _shared_section(root, topic)
    stages = ""
    try:
        t = Topic(root, topic)
        name = t.current(None)
        parsed = t.stages(name)
    except Refused:
        parsed = []
    if parsed:
        lines = ["## Stages", ""]
        for i, st in enumerate(parsed, 1):
            lines.append(f"{i}. {st.get('name')} — {st.get('reason', '')}")
        stages = "\n".join(lines) + "\n"
    return f"# {title}: {topic}\n\n{shared}\n{stages}"


def _proposal_html(markdown: str) -> str:
    parts = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Proposal</title>',
             "<style>body{font-family:Georgia,serif;margin:2rem;color:#222} .decided{border-left:4px solid #146c43;padding-left:.6rem} .proposed{border-left:4px solid #6c757d;background:#f6f6f6;padding-left:.6rem} pre{white-space:pre-wrap}</style>",
             "</head><body>"]
    for line in markdown.splitlines():
        if line.startswith("# "):
            parts.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            parts.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("- decided:"):
            parts.append(f'<p class="decided">{line[2:]}</p>')
        elif line.startswith("- proposed:"):
            parts.append(f'<p class="proposed">{line[2:]}</p>')
        elif line[:2].rstrip(".").isdigit() or (line[:1].isdigit() and ". " in line[:4]):
            parts.append(f"<p>{line}</p>")
        elif line.startswith("```mermaid"):
            parts.append("<!-- diagram -->")
        elif line.strip() == "```":
            continue
        elif line.strip():
            parts.append(f"<p>{line}</p>")
    parts.append("</body></html>\n")
    return "\n".join(parts)


def publish_proposal(root: Path, topic: str, briefing: bool = False) -> dict:
    topic = slugify(topic)
    w = Writer(root, topic)
    md = _proposal_markdown(root, topic, briefing=False)
    html = _proposal_html(md)
    folder = root / DESIGNS / topic
    w.write(folder / "proposal.md", md if md.endswith("\n") else md + "\n")
    w.write(folder / "proposal.html", html)
    if briefing:
        bmd = _proposal_markdown(root, topic, briefing=True)
        w.write(folder / "briefing.md", bmd if bmd.endswith("\n") else bmd + "\n")
        w.write(folder / "briefing.html", _proposal_html(bmd))
    save_session(root, topic, status="open", mode="session", step="proposal")
    return {"topic": topic, "written": w.written, "current": True}


def proposal_current(root: Path, topic: str) -> bool:
    folder = root / DESIGNS / topic
    md = folder / "proposal.md"
    if not md.is_file():
        return False
    return md.read_text(encoding="utf-8") == (_proposal_markdown(root, topic) if _proposal_markdown(root, topic).endswith("\n") else _proposal_markdown(root, topic) + "\n")


def cmd_proposal(a, root: Path) -> dict:
    topic = slugify(a.topic)
    if not (root / DESIGNS / topic / "goal.md").is_file():
        raise Refused(f"{topic} is not a topic yet")
    if getattr(a, "check", False) and not a.yes:
        return {"topic": topic, "current": proposal_current(root, topic)}
    if not a.yes and not getattr(a, "check", False):
        return {"topic": topic, "preview": True, "current": proposal_current(root, topic),
                "note": "Add --yes to write proposal.md and proposal.html from the shared decisions."}
    if getattr(a, "check", False):
        fresh = publish_proposal(root, topic, briefing=getattr(a, "briefing", False))
        return {"topic": topic, "current": True, "written": fresh["written"]}
    return publish_proposal(root, topic, briefing=getattr(a, "briefing", False))


def cmd_stages_list(a, root: Path) -> str:
    topic = slugify(a.topic)
    try:
        t = Topic(root, topic)
        parsed = t.stages(t.current(None))
    except Refused:
        parsed = []
    save_session(root, topic, status="open", mode="session", step="stages")
    lines = [status_line(topic, "open", ""), ""]
    if not parsed:
        lines.append("No stages yet. The user names and divides them.")
    else:
        for i, st in enumerate(parsed, 1):
            lines.append(f"{i}. {st.get('name')} — {st.get('reason', '')}")
    lines += ["", "Run next:", "These are the stages.", "", "Back to the session:", f"`{plain_command(topic)}`"]
    return "\n".join(lines) + "\n"


def cmd_end(a, root: Path) -> str:
    topic = slugify(a.topic)
    if not (root / DESIGNS / topic / "goal.md").is_file():
        raise Refused(f"{topic} is not a topic yet")
    save_session(root, topic, status="ended", mode="session", step="end")
    return "\n".join(["Session ended", "", f"`{plain_command(topic)}`", ""]) 


def cmd_reopen(a, root: Path) -> str:
    """Open an ended session again and print the status screen (1.201.1)."""
    topic = slugify(a.topic)
    if not (root / DESIGNS / topic / "goal.md").is_file():
        if design_branch_ref(root, topic):
            raise Refused(switch_card(root, topic, current_branch(root) or "this branch"))
        raise Refused(f"{topic} is not a topic yet")
    t = Topic(root, topic)
    name = t.current(None)
    d = t.design(name)
    if d.get("status") in ("parked", "ended"):
        d["status"] = "open"
        save_design(t, name, d, Writer(root, topic))
    save_session(root, topic, status="open", mode="session", step="reopen")
    return screen_text(root, topic)


def cmd_park(a, root: Path) -> dict:
    t = Topic(root, a.topic)
    name = t.current(a.design)
    d = t.design(name)
    d["status"] = "parked"
    w = Writer(root, t.name)
    save_design(t, name, d, w)
    save_session(root, t.name, status="parked", mode="session", step="park")
    text = "\n".join(["Session parked", "", f"`{plain_command(t.name)}`", ""])
    return {"topic": t.name, "design": name, "status": "parked", "written": w.written, "screen": text}


def cmd_fan_out(a, root: Path) -> dict:
    t = Topic(root, a.topic)
    w = Writer(root, t.name)
    new = slugify(a.name)
    if a.mode == "copy":
        src = t.ddir(t.current(a.design))
        sd = parse_design((src / "design.md").read_text(encoding="utf-8"))
        _new_design(root, t.name, new, a.title or new.replace("-", " "), sd["ask"],
                    [{k: v for k, v in dec.items() if k not in ("Draft ADR",)} | ({"State": "open"} if dec["State"] == "settled" else {}) for dec in sd["decisions"]],
                    sd["drivers"], w, sd["end_state"], sd["ideas"])
        qs = parse_questions((src / "questions.md").read_text(encoding="utf-8")) if (src / "questions.md").is_file() else []
        w.write(t.ddir(new) / "questions.md", render_questions(new, qs))
    else:
        g = t.goal()
        _new_design(root, t.name, new, a.title or new.replace("-", " "), g["ask"], [], g["drivers"], w)
    refresh_compare(t, w)
    if not (t.dir / "compare.md").is_file():
        w.write(t.dir / "compare.md", compare_text(t))
    return _with_sync({"topic": t.name, "design": new, "mode": a.mode, "written": w.written}, a, root, t.name)


def cmd_add_decision(a, root: Path) -> dict:
    t = Topic(root, a.topic)
    name = t.current(a.design)
    d = t.design(name)
    guard_base(t, d, a.title)
    if any(x["title"].casefold() == a.title.casefold() for x in d["decisions"]):
        raise Refused("that decision is already listed")
    nxt = max((_order(x) for x in d["decisions"]), default=0) + 1
    d["decisions"].append({"title": a.title, "State": "open", "Order": str(nxt)} | ({"Detail": "yes"} if a.detail else {}))
    w = Writer(root, t.name)
    save_design(t, name, d, w)
    return {"design": name, "written": w.written}


def cmd_lean(a, root: Path) -> dict:
    """Save options shown and a lean or recommendation. Allowed in prepare."""
    data = load_input(a.input)
    t = Topic(root, a.topic)
    name = t.current(a.design)
    d = t.design(name)
    guard_base(t, d, a.decision)
    dec = find_decision(d, a.decision)
    if dec["State"] == "settled":
        raise Refused("that decision is settled; reopen it with a choose word in chat first")
    if dec["State"] == "dropped":
        raise Refused("that decision was dropped from the goal; add it back with change-goal first")
    if data.get("options"):
        dec["Options shown"] = ", ".join(o["name"] for o in data["options"])
    if data.get("recommended"):
        dec["Recommended"] = data["recommended"]
    if data.get("leaning") and not a.headless:
        dec["Leaning"] = data["leaning"]
    if dec["State"] in ("open", "reopened"):
        dec["State"] = "leaning" if dec.get("Leaning") else dec["State"]
    named = []
    for drv in data.get("drivers", []):
        hit = match_driver(drv, d["drivers"])
        if hit is None:
            d["drivers"].append(drv)
        named.append(drv)
    if named:
        dec["Drivers"] = "; ".join(named)
    for idea in data.get("ideas", []):
        if idea not in d["ideas"]:
            d["ideas"].append(idea)
    w = Writer(root, t.name)
    save_design(t, name, d, w)
    return _with_linked({"design": name, "decision": dec["title"], "written": w.written}, root, t.name)


def _driver_key(text: str) -> str:
    return re.split(r" \(|: |\. ", text.strip(), maxsplit=1)[0].strip().rstrip(".").casefold()


def match_driver(name: str, drivers: list[str]) -> str | None:
    """A lean names drivers by their short name; match it to a driver already listed (1.189.0)."""
    key = _driver_key(name)
    if not key:
        return None
    for drv in drivers:
        if _driver_key(drv) == key or drv.casefold().startswith(name.strip().rstrip(".").casefold()):
            return drv
    return None


def match_option(chosen: str, options: list) -> str:
    """A unique short prefix ('Your idea', 'A') selects the option. Exit 2 lists the names (1.200.0)."""
    names = [str(o.get("name") if isinstance(o, dict) else o) for o in options]
    text = chosen.strip()
    if text in names:
        return text
    hits = [name for name in names if name.casefold().startswith(text.casefold())] if text else []
    if len(hits) == 1:
        return hits[0]
    raise Refused("chosen option does not match one option. Accepted: " + ", ".join(names))


def _adr_text(data: dict, dec_title: str, deciders: str) -> str:
    tpl = asset("adr.md")
    chosen = data["chosen"]
    opts = data["options"]
    names = [o["name"] for o in opts]
    if chosen not in names:
        raise Refused(f"chosen option {chosen} is not among the options shown")
    body = tpl.replace("# ADR NNNN: Title", f"# ADR NNNN: {data.get('adr_title', dec_title)}")
    body = body.replace("- Status: proposed", "- Status: draft").replace("- Date: YYYY-MM-DD", f"- Date: {today()}")
    body = body.replace("- Deciders: ", f"- Deciders: {deciders}")
    body = body.replace("What forces a choice? Phrase it as a question if you can.", data.get("context", dec_title))
    body = body.replace("## Decision drivers\n\n- \n", "## Decision drivers\n\n" + ("".join(f"- {x}\n" for x in data.get("drivers", [])) or "- none\n"))
    body = body.replace("## Considered options\n\n- Option A\n- Option B\n",
                        "## Considered options\n\n" + "".join(f"- {o['name']}{' (your idea)' if o.get('yours') else ''}\n" for o in opts))
    body = body.replace('Chosen option: "…", because …', f'Chosen option: "{chosen}", because {data.get("why", "")}')
    body = body.replace("- Good, because\n- Bad, because\n\n### Confirmation",
                        "".join(f"- Good, because {x}\n" for x in data.get("good", [])) + "".join(f"- Bad, because {x}\n" for x in data.get("bad", [])) + "\n### Confirmation")
    pros = "## Pros and cons of the options\n"
    for o in opts:
        pros += f"\n### {o['name']}\n\n" + "".join(f"- Good, because {x}\n" for x in o.get("good", [])) + "".join(f"- Bad, because {x}\n" for x in o.get("bad", []))
        if o["name"] != chosen:
            pros += f"- Not chosen: {o.get('not_chosen', 'see Decision outcome')}\n"
    body = re.sub(r"## Pros and cons of the options\n.*?(?=\n## More information)", pros.rstrip("\n") + "\n", body, flags=re.S)
    return body


def cmd_settle_preview(a, root: Path) -> dict:
    """A lean preview. The recommended option is one by one, and a yes settles nothing (1.200.0)."""
    t = Topic(root, a.topic)
    name = t.current(getattr(a, "design", None))
    d = t.design(name)
    if getattr(a, "one_at_a_time", False):
        raise Refused("one at a time was asked; there is no settle batch")
    open_ones = [dec for dec in ordered(d["decisions"]) if dec.get("State") not in ("settled", "dropped")]
    named = []
    for q in t.questions(name):
        text = str(q.get("text") or "")
        if q.get("answer"):
            continue
        if re.search(r"\((?!nobody\b|not named)[^)]+\)\s*$", text, re.I):
            named.append(text)
    if named:
        raise Refused("a listed decision waits on " + ", ".join(named) + "; settle one by one")
    return {
        "topic": t.name,
        "settled": False,
        "preview": True,
        "decisions": [dec["title"] for dec in open_ones],
        "card": {
            "question": "Settle the open decisions one by one?",
            "recommended": "one-by-one",
            "words": ["one-by-one", "stop"],
            "options": [
                {"word": "one-by-one", "label": "One by one (Recommended)",
                 "action": "show the next decision card; this yes settles nothing"},
                {"word": "stop", "label": "Stop", "action": "settle nothing"},
            ],
        },
        "note": "Nothing is settled until a choose-* word is picked on one decision.",
    }


def cmd_settle(a, root: Path) -> dict:
    data = load_input(a.input)
    t = Topic(root, a.topic)
    name = t.current(a.design)
    d = t.design(name)
    guard_base(t, d, a.decision)
    dec = find_decision(d, a.decision)
    if dec["State"] == "dropped":
        raise Refused("that decision was dropped from the goal; add it back with change-goal first")
    if dec["State"] == "reopened" and not a.revisit_yes:
        raise Refused("this decision was reopened; settle needs --revisit-yes, even when the choice stays the same")
    reverses = data.get("reverses", "")
    if reverses and not a.revisit_yes:
        raise Refused(f"this choice reverses {reverses}; it is a revisit and needs a separate yes (--revisit-yes)")
    data["chosen"] = match_option(str(data.get("chosen") or ""), data.get("options") or [])
    w = Writer(root, t.name)
    deciders = data.get("deciders") or _git_user(root)
    slug = slugify(data.get("adr_slug") or data.get("adr_title") or dec["title"])
    adr_path = t.ddir(name) / "adr" / f"{slug}.md"
    w.write(adr_path, _adr_text(data, dec["title"], deciders))
    dec["State"] = "settled"
    dec["Draft ADR"] = f"designs/{name}/adr/{slug}.md"
    dec["Options shown"] = ", ".join(o["name"] for o in data["options"])
    dec.pop("Leaning", None)
    dec.pop("Reopened", None)
    if reverses:
        dec["Reverses"] = reverses + " (revisit, yes given)"
    if data.get("sources"):
        dec["Sources"] = ", ".join(f"{s}@{fhash(root / s)}" for s in data["sources"])
    if data.get("end_state"):
        d["end_state"] = data["end_state"]
        if t.stages(name):
            w.write(t.ddir(name) / "stages.md", render_stages(name, [dict(s, state="needs another look") for s in t.stages(name)]))
    for o in data["options"]:
        if o.get("yours"):
            idea = f"{o['name']}. (yours, on: {dec['title']})"
            if idea not in d["ideas"]:
                d["ideas"].append(idea)
    save_design(t, name, d, w)
    if data.get("diagram"):
        dp = t.ddir(name) / "diagrams.md"
        cur = dp.read_text(encoding="utf-8") if dp.is_file() else f"# Draft diagrams: {name}\n"
        head = f"## {dec['title']}"
        cur = re.sub(rf"\n{re.escape(head)}\n.*?(?=\n## |\Z)", "", cur, flags=re.S).rstrip("\n") + "\n"
        cur += f"\n{head}\n\n```mermaid\n{data['diagram'].strip()}\n```\n"
        w.write(dp, cur)
    refresh_compare(t, w, data.get("scores"))
    return _with_linked({"design": name, "decision": dec["title"], "adr": str(adr_path.relative_to(root)), "written": w.written}, root, t.name)


def _git_user(root: Path) -> str:
    try:
        import subprocess
        out = subprocess.run(["git", "config", "user.name"], cwd=root, capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or "not named yet"
    except Exception:
        return "not named yet"


def cmd_question(a, root: Path) -> dict:
    t = Topic(root, a.topic)
    name = t.current(a.design)
    d = t.design(name)
    if not re.search(r"\([^)]*\)\s*$", a.text):
        raise Refused("an open question ends with who has the fact or who decides, in brackets")
    q = {"text": a.text, "kind": a.kind}
    if a.decision:
        dec = find_decision(d, a.decision)
        q["decision"] = dec["title"]
        dec["State"] = "to-research" if a.kind == "research" else "to-question"
        dec["Open question in"] = "questions.md"
    if a.research:
        q["research"] = a.research
    if a.stage:
        q["stage"] = a.stage
    qs = t.questions(name)
    pos = next((i for i, x in enumerate(qs) if x["text"] == a.text), None)
    if pos is None:
        q["asked"] = today()
        qs.append(q)
    else:
        q["asked"] = qs[pos].get("asked") or today()
        qs[pos] = q
    w = Writer(root, t.name)
    w.write(t.ddir(name) / "questions.md", render_questions(name, qs))
    save_design(t, name, d, w)
    return {"design": name, "written": w.written}


def cmd_answer(a, root: Path) -> dict:
    t = Topic(root, a.topic)
    name = t.current(a.design)
    qs = t.questions(name)
    hits = [q for q in qs if a.question.casefold() in q["text"].casefold()]
    if len(hits) != 1:
        raise Refused("no single open question matches those words")
    hits[0]["answer"] = a.text
    d = t.design(name)
    if hits[0].get("decision"):
        dec = find_decision(d, hits[0]["decision"])
        if dec["State"] in ("to-question", "to-research"):
            dec["State"] = "open"
    w = Writer(root, t.name)
    w.write(t.ddir(name) / "questions.md", render_questions(name, qs))
    save_design(t, name, d, w)
    return {"design": name, "written": w.written}


def cmd_skip(a, root: Path) -> dict:
    t = Topic(root, a.topic)
    name = t.current(a.design)
    d = t.design(name)
    find_decision(d, a.decision)["State"] = "skipped"
    w = Writer(root, t.name)
    save_design(t, name, d, w)
    return {"design": name, "written": w.written}


def cmd_stage(a, root: Path) -> dict:
    data = load_input(a.input)
    t = Topic(root, a.topic)
    name = t.current(a.design)
    stages = data.get("stages", [])
    if not stages:
        raise Refused("no stages given; staging is optional")
    for st in stages:
        if not st.get("name") or not st.get("reason"):
            raise Refused("every stage needs a name and a reason")
    w = Writer(root, t.name)
    w.write(t.ddir(name) / "stages.md", render_stages(name, [dict(s, state=s.get("state", "open")) for s in stages]))
    return _with_sync({"design": name, "stages": [s["name"] for s in stages], "written": w.written}, a, root, t.name)


def cmd_compare(a, root: Path) -> dict:
    t = Topic(root, a.topic)
    w = Writer(root, t.name)
    w.write(t.dir / "compare.md", compare_text(t, load_input(a.input).get("scores")))
    return {"topic": t.name, "written": w.written}


def cmd_compare_topics(a, root: Path) -> dict:
    data = load_input(a.input)
    if not a.asked:
        raise Refused("a cross-topic comparison runs only when the user asks (--asked)")
    crit = data.get("criteria") or []
    if not crit:
        raise Refused("name the criteria the user picked")
    topics = [Topic(root, x) for x in a.topics]
    name = "-".join(t.name for t in topics)
    path = root / DESIGNS / "_compare" / f"{name}.md"
    w = Writer(root, "_compare")
    cols = [f"{t.name}/{d}" for t in topics for d in t.designs()]
    scores = data.get("scores", {})
    lines = [f"# One-off comparison: {' and '.join(t.name for t in topics)}", "",
             f"- Date: {today()}", "- Criteria: picked by the user for this comparison only.", "",
             "| Criterion | " + " | ".join(cols) + " |", "| --- |" + " --- |" * len(cols)]
    for c in crit:
        lines.append(f"| {c} | " + " | ".join(scores.get(col, {}).get(c, "unknown") for col in cols) + " |")
    w.write(path, "\n".join(lines) + "\n")
    return {"written": w.written}


def review(t: Topic, name: str, root: Path) -> list[dict]:
    """Go-ahead review: gaps against the goal, conflicts, missing decisions."""
    g, d = t.goal(), t.design(name)
    found = []
    text = (d["end_state"] + " " + " ".join(x["title"] for x in d["decisions"])).casefold()
    for crit in g["criteria"]:
        words = [w for w in re.findall(r"[a-z0-9]+", crit.casefold()) if len(w) > 3]
        if words and not any(w in text for w in words):
            found.append({"kind": "gap", "text": f"criterion not covered by the end state: {crit}"})
    for dec in d["decisions"]:
        if dec["State"] in ("open", "leaning", "skipped", "reopened"):  # dropped is not missing
            found.append({"kind": "missing-decision", "text": f"not settled: {dec['title']}"})
    envs = root / "docs" / "environments"
    known = {p.stem.casefold() for p in envs.glob("*.md")} if envs.is_dir() else set()
    for env in sorted(set(re.findall(r"\b(dev|test|staging|prod|uat|qa)\b", d["end_state"].casefold()))):
        if known and env not in known:
            found.append({"kind": "conflict", "text": f"the end state uses environment {env}, which docs/environments/ does not show"})
    return found


def cmd_review(a, root: Path) -> dict:
    t = Topic(root, a.topic)
    name = t.current(a.design)
    return {"design": name, "findings": review(t, name, root)}


def _next_adr_number(folder: Path) -> int:
    nums = [int(m.group(1)) for p in folder.glob("*.md") if (m := re.match(r"^(\d{4})-", p.name))] if folder.is_dir() else []
    return max(nums, default=0) + 1


def _confirmed(text: str) -> str:
    m = re.search(r"^## Confirmed\n(.*?)(?=^## |\Z)", text, flags=re.S | re.M)
    return m.group(1).strip() if m else ""


def _marks(text: str) -> list[str]:
    return [l for l in text.splitlines() if l.strip().lstrip("- ").startswith(GUARDED_MARKS)]


def cmd_go_ahead(a, root: Path) -> dict:
    t = Topic(root, a.topic)
    name = t.current(a.design)
    base = t.goal().get("builds_on")
    if base and not (a.base_merged or base_on_main(root, base)):
        raise Refused(waiting_base_text(root, t.name, base))
    findings = review(t, name, root)
    if findings and not a.accept_findings:
        return _with_sync({"design": name, "findings": findings, "copied": False, "written": [],
                           "note": "fix the findings in the sandbox or accept them, then run go-ahead again"}, a, root, t.name)
    d = t.design(name)
    if d["status"] == "chosen":
        raise Refused("this design already had go-ahead; nothing written")
    slice_slug = a.slice
    adr_dir = Path("docs/specs") / slice_slug / "adr" if slice_slug else Path("docs/system/adr")
    diag = Path("docs/specs") / slice_slug / "diagrams.md" if slice_slug else Path("docs/system/diagrams.md")
    drafts = sorted((t.ddir(name) / "adr").glob("*.md"))
    num = _next_adr_number(root / adr_dir)
    adr_targets = []
    for i, p in enumerate(drafts):
        adr_targets.append((p, adr_dir / f"{num + i:04d}-{p.stem}.md"))
    extra = {str(ARCH_SPEC), str(diag)} | {str(x[1]) for x in adr_targets}
    w = Writer(root, t.name, extra)
    designed_in = f"docs/architecture/designs/{t.name}/designs/{name}/"
    spec_p = root / ARCH_SPEC
    spec = spec_p.read_text(encoding="utf-8") if spec_p.is_file() else "# Architecture\n"
    before_confirmed, before_marks = _confirmed(spec), _marks(spec)
    block = [f"### {d['title']} (topic {t.name})", "", f"Designed in: `{designed_in}`"]
    if base:
        block.append(f"Builds on: topic {base}")
    if adr_targets:
        block.append("Accepted ADRs: " + ", ".join(f"`{x[1]}`" for x in adr_targets))
    block += ["", d["end_state"]]
    stages = t.stages(name)
    if stages:
        block += ["", "Stages:"]
        for i, st in enumerate(stages, 1):
            block.append(f"{i}. {st['name']}: {st.get('reason', '')}" + (f" Waits on: {st['waits_on']}" if st.get("waits_on") else ""))
    if d.get("small_fixes"):
        block += ["", "Small fixes (no design choice):"] + [f"- {x}" for x in d["small_fixes"]]
    block_txt = "\n".join(block).rstrip() + "\n"
    head = f"### {d['title']} (topic {t.name})"
    if head in spec:
        raise Refused("this design is already copied under Decided, not built yet")
    if DECIDED in spec:
        spec = re.sub(rf"^{re.escape(DECIDED)}\n", f"{DECIDED}\n\n{block_txt}", spec, count=1, flags=re.M)
        spec = re.sub(r"\n{3,}", "\n\n", spec)
    else:
        sec = f"{DECIDED}\n\nApproved designs that are not built yet. Recheck moves a part up to Confirmed once the code or the environment shows it.\n\n{block_txt}\n"
        if re.search(rf"^{OPEN_Q}$", spec, re.M):
            spec = re.sub(rf"^{OPEN_Q}$", sec + OPEN_Q, spec, count=1, flags=re.M)
        else:
            spec = spec.rstrip("\n") + "\n\n" + sec
    open_qs = [q for q in t.questions(name) if not q.get("answer")]
    if open_qs:
        lines = "".join(f"- {q['text']}\n" for q in open_qs)
        if not re.search(rf"^{OPEN_Q}$", spec, re.M):
            spec = spec.rstrip("\n") + f"\n\n{OPEN_Q}\n\n"
        m = re.search(rf"^{OPEN_Q}\n(.*?)(?=^## |\Z)", spec, flags=re.S | re.M)
        body = m.group(1).rstrip("\n")
        body = "\n".join(l for l in body.splitlines() if l.strip() != "-")
        spec = spec[:m.start(1)] + (body.rstrip("\n") + "\n" if body.strip() else "\n") + lines + ("\n" if m.end(1) < len(spec) else "") + spec[m.end(1):]
    if _confirmed(spec) != before_confirmed or _marks(spec) != before_marks:
        raise Refused("go-ahead would change Confirmed or a question mark line; nothing written")
    for p, target in adr_targets:
        txt = p.read_text(encoding="utf-8")
        txt = re.sub(r"^# ADR NNNN:", f"# ADR {target.name[:4]}:", txt, flags=re.M)
        txt = txt.replace("- Status: draft", "- Status: accepted")
        if slice_slug is None:
            txt = txt.replace("- Spec: `../spec.md`", "- Spec: `../../architecture/spec.md`")
        txt = txt.replace("- Spec:", f"- Designed in: `{designed_in}`\n- Spec:", 1)
        w.write(root / target, txt)
    w.write(spec_p, spec.rstrip("\n") + "\n")
    ddraft = t.ddir(name) / "diagrams.md"
    blocks = re.findall(r"```mermaid\n.*?```", ddraft.read_text(encoding="utf-8"), flags=re.S) if ddraft.is_file() else []
    if blocks:
        lp = root / diag
        live = lp.read_text(encoding="utf-8") if lp.is_file() else "# Diagrams\n"
        live = live.rstrip("\n") + f"\n\n## {d['title']} (planned)\n\nDesigned in: `{designed_in}`. Dashed parts are planned and not built yet.\n\n" + "\n\n".join(blocks) + "\n"
        w.write(lp, live)
    d["status"] = "chosen"
    save_design(t, name, d, w)
    for other in t.designs():
        if other != name:
            od = t.design(other)
            if od["status"] != "rejected":
                od["status"] = "rejected"
                save_design(t, other, od, w)
    refresh_compare(t, w)
    return _with_linked(_with_sync({"design": name, "findings": findings, "copied": True, "adrs": [str(x[1]) for x in adr_targets],
                                    "slice": slice_slug, "written": w.written}, a, root, t.name), root, t.name)


# ---------------------------------------------------------------- goal changes (1.188.0)
def goal_order(g: dict, d: dict) -> list[dict]:
    """Decisions in the goal's order when the goal lists one, else as stored."""
    return ordered(d["decisions"])


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9][a-z0-9.+#-]*[a-z0-9+#]|[a-z0-9]", text.casefold())
            if len(w) >= 3 and w not in STOP_WORDS}


def _settled_text(t: Topic, design: str, dec: dict) -> str:
    """Title, lean, recommendation and the draft ADR's decision outcome."""
    parts = [dec["title"], dec.get("Leaning", ""), dec.get("Recommended", "")]
    ref = dec.get("Draft ADR", "")
    if ref:
        p = t.dir / ref
        if p.is_file():
            m = re.search(r"^## Decision outcome\n(.*?)(?=^## |\Z)", p.read_text(encoding="utf-8"), flags=re.S | re.M)
            if m:
                parts.append(m.group(1))
    return " ".join(parts)


def plan_goal_change(t: Topic, data: dict, reason: str) -> dict:
    """Work out the new goal, the change lines and which decisions it touches.

    Touches, in this order: the decision is dropped; it is renamed; the input
    lists it under `reopen`; or it is settled or leaning and its title, lean,
    recommendation or draft ADR decision outcome names a word from a removed
    constraint, criterion or driver that no kept goal line still uses.
    """
    old = t.goal()
    designs = [n for n in t.designs() if t.design(n)["status"] != "rejected"]
    first = t.design(designs[0]) if designs else {"decisions": []}
    old_list = old["decisions"] or [x["title"] for x in first["decisions"]]
    new = dict(old)
    for k in ("ask", "end_goal", "drivers", "constraints", "criteria"):
        if k in data:
            new[k] = data[k]
    renames = {k: v for k, v in (data.get("renames") or {}).items()}
    live_old = [x for x in old_list if x not in old["dropped"]]
    want = list(data.get("decisions") or [renames.get(x, x) for x in live_old])
    renamed_to = set(renames.values())
    dropped_now = [x for x in live_old if renames.get(x, x) not in want and x not in renamed_to]
    reasons = data.get("drop_reasons") or {}
    dropped = {k: v for k, v in old["dropped"].items() if k not in want}
    for x in dropped_now:
        dropped[x] = reasons.get(x, reason)
    new["decisions"] = want + [x for x in old_list if x in dropped and x not in want]
    new["dropped"] = dropped
    changes = []
    for k, label in (("drivers", "driver"), ("constraints", "constraint"), ("criteria", "criterion")):
        for x in old[k]:
            if x not in new[k]:
                changes.append(f"Removed {label}: {x}")
        for x in new[k]:
            if x not in old[k]:
                changes.append(f"Added {label}: {x}")
    if new["ask"] != old["ask"]:
        changes.append("Changed the ask")
    if new["end_goal"] != old["end_goal"]:
        changes.append("Changed the end goal")
    for o, n in renames.items():
        changes.append(f"Renamed decision: {o} to {n}")
    for x in want:
        if x in old["dropped"]:
            changes.append(f"Added back decision: {x}")
        elif x not in [renames.get(y, y) for y in live_old]:
            changes.append(f"Added decision: {x}")
    for x in dropped_now:
        changes.append(f"Dropped decision: {x} ({dropped[x]})")
    kept_old = [renames.get(x, x) for x in live_old if x not in dropped_now]
    if [x for x in want if x in kept_old] != kept_old:
        changes.append("Reordered decisions: " + ", ".join(want))
    removed = [x for k in ("drivers", "constraints", "criteria") for x in old[k] if x not in new[k]]
    kept_text = " ".join([new["end_goal"]] + new["drivers"] + new["constraints"] + new["criteria"])
    keywords = sorted(set().union(*[_words(x) for x in removed]) - _words(kept_text)) if removed else []
    reopen = {x.casefold() for x in data.get("reopen", [])}
    flagged, per_design = [], {}
    for dn in designs:
        d = t.design(dn)
        hits = []
        for dec in d["decisions"]:
            title = dec["title"]
            if title in dropped_now:
                continue
            why = ""
            if title in renames:
                why = f"renamed from {title}"
            elif title.casefold() in reopen:
                why = "listed to look at again"
            elif dec["State"] in ("settled", "leaning") and keywords:
                found = sorted(_words(_settled_text(t, dn, dec)) & set(keywords))
                if found:
                    why = "names " + ", ".join(found) + " from a removed goal line"
            if why and (dec["State"] in ("settled", "leaning") or title.casefold() in reopen):
                hits.append((title, why))
                flagged.append({"design": dn, "decision": renames.get(title, title), "why": why})
        per_design[dn] = hits
    for f in flagged:
        changes.append(f"Needs another look: {f['decision']} ({f['why']})")
    return {"old": dict(old, decisions=old_list), "new": new, "changes": changes, "flagged": flagged, "dropped": dropped_now,
            "renames": renames, "keywords": keywords, "designs": designs, "per_design": per_design}


def _goal_view(g: dict) -> dict:
    return {k: g.get(k) for k in ("ask", "end_goal", "drivers", "constraints", "criteria")} | {
        "decisions": [x + (" (dropped)" if x in g.get("dropped", {}) else "") for x in g.get("decisions", [])]}


def cmd_change_goal(a, root: Path) -> dict:
    data = load_input(a.input)
    check_keys(data, CHANGE_KEYS, "change-goal")
    notes = data.pop("notes", None)
    if not a.reason or not a.reason.strip():
        raise Refused("a goal change needs a reason (--reason)")
    t = Topic(root, a.topic)
    plan = plan_goal_change(t, data, a.reason.strip())
    if not plan["changes"]:
        raise Refused("the new goal is the same as the old one; nothing written")
    view = {"topic": t.name, "old": _goal_view(plan["old"]), "new": _goal_view(plan["new"]),
            "changes": plan["changes"], "flagged": plan["flagged"], "dropped": plan["dropped"]}
    if not a.yes:
        return _with_sync(view, a, root, t.name) | {"preview": True, "written": [],
                       "note": "show old and new goal on a card; after the user's yes run change-goal again with --yes"}
    w = Writer(root, t.name)
    new = plan["new"]
    ensure_inputs(root, t.name, w)
    src = Path(a.input)
    rel = _rel_input(root, t.name, src)
    if rel is None:
        n = 1
        while (root / DESIGNS / t.name / INPUTS_DIR / f"goal-change-{n}.json").exists():
            n += 1
        target = root / DESIGNS / t.name / INPUTS_DIR / f"goal-change-{n}.json"
        w.write(target, src.read_text(encoding="utf-8"))
        src, rel = target, f"{INPUTS_DIR}/{target.name}"
    new["applied"] = list(plan["old"].get("applied", [])) + [f"{rel}@{fhash(src)}"]
    entry = [f"- {today()}: {a.reason.strip()}"] + [f"  - {c}" for c in plan["changes"]] + [f"  - Input: {rel}"]
    new["changes"] = ("\n".join(entry) + ("\n" + plan["old"]["changes"].strip("\n") if plan["old"]["changes"].strip() else ""))
    w.write(t.dir / "goal.md", render_goal(new))
    renames = plan["renames"]
    for dn in plan["designs"]:
        d = t.design(dn)
        hits = dict(plan["per_design"].get(dn, []))
        for dec in d["decisions"]:
            title = dec["title"]
            if title in plan["dropped"]:
                dec["State"] = "dropped"
                dec["Dropped"] = f"{today()}: {new['dropped'][title]}"
                continue
            if dec["State"] == "dropped" and title in new["decisions"] and title not in new["dropped"]:
                dec["State"] = "open"
                dec.pop("Dropped", None)
            if title in hits:
                dec["State"] = "reopened"
                dec["Reopened"] = f"goal changed {today()}: {hits[title]}"
            if title in renames:
                dec["Renamed from"] = title
                dec["title"] = renames[title]
        have = {y["title"] for y in d["decisions"]}
        for x in new["decisions"]:
            if x not in new["dropped"] and x not in have:
                d["decisions"].append({"title": x, "State": "open"})
        set_order(d["decisions"], new["decisions"])
        save_design(t, dn, d, w)
        if hits and t.stages(dn):
            w.write(t.ddir(dn) / "stages.md", render_stages(dn, [dict(s, state="needs another look") for s in t.stages(dn)]))
    if notes:
        _write_note(root, t.name, f"notes with the goal change: {a.reason.strip()}", notes, "other", w)
    refresh_compare(t, w)
    return _with_linked(view | {"preview": False, "written": w.written}, root, t.name)


# ---------------------------------------------------------------- linked topics (1.188.0)
def _chosen_option(t: Topic, dec: dict) -> str:
    p = t.dir / dec.get("Draft ADR", "")
    if dec.get("Draft ADR") and p.is_file():
        m = re.search(r'^Chosen option: "([^"]*)"', p.read_text(encoding="utf-8"), flags=re.M)
        if m:
            return m.group(1)
    return "settled"


def base_fixed(root: Path, base: str) -> list[str]:
    """The base topic's settled decisions, one line each: `<title>: <chosen> (<design>)`."""
    t = Topic(root, base)
    names = [n for n in t.designs() if t.design(n)["status"] == "chosen"] or \
        [n for n in t.designs() if t.design(n)["status"] != "rejected"]
    out = []
    for n in names:
        d = t.design(n)
        for dec in goal_order(t.goal(), d):
            if dec["State"] == "settled":
                out.append(f"{dec['title']}: {_chosen_option(t, dec)} ({n}, {dec.get('Draft ADR', '')})")
    return out


def _base_titles(t: Topic) -> list[str]:
    return [x.split(": ", 1)[0] for x in t.goal().get("fixed", [])]


def guard_base(t: Topic, d: dict, words: str) -> None:
    """A linked topic may not settle or change a decision settled in its base topic."""
    base = t.goal().get("builds_on")
    if not base:
        return
    key = words.casefold().strip()
    if any(x["title"].casefold() == key for x in d["decisions"]):
        return
    hits = [x for x in _base_titles(t) if x.casefold() == key] or [x for x in _base_titles(t) if key in x.casefold()]
    if len(hits) == 1:
        raise Refused(f"{hits[0]} is settled in the base topic {base}; this topic may not settle or change it. "
                      f"Offer a revisit to {base}: revisit --topic {t.name} --decision \"{hits[0]}\" --reason \"<why>\"")


def cmd_revisit(a, root: Path) -> dict:
    t = Topic(root, a.topic)
    base = t.goal().get("builds_on")
    if not base:
        raise Refused(f"topic {t.name} does not build on another topic; settle the decision here")
    if not a.reason or not a.reason.strip():
        raise Refused("a revisit needs a reason (--reason)")
    bt = Topic(root, base)
    w = Writer(root, base)
    hit = None
    for dn in bt.designs():
        d = bt.design(dn)
        if d["status"] == "rejected":
            continue
        try:
            dec = find_decision(d, a.decision)
        except Refused:
            continue
        dec["State"] = "reopened" if dec["State"] in ("settled", "leaning") else dec["State"]
        dec["Reopened"] = f"revisit from topic {t.name} {today()}: {a.reason.strip()}"
        save_design(bt, dn, d, w)
        hit = {"design": dn, "decision": dec["title"]}
        break
    if not hit:
        raise Refused(f"no single decision in the base topic {base} matches the words: {a.decision}")
    if bt.stages(hit["design"]):
        w.write(bt.ddir(hit["design"]) / "stages.md", render_stages(hit["design"], [dict(s, state="needs another look") for s in bt.stages(hit["design"])]))
    return {"topic": t.name, "base": base, "revisit": hit, "base_branch": f"design/{base}",
            "ending": revisit_text(t.name, base, hit["decision"]), "written": w.written}


def base_on_main(root: Path, base: str) -> bool:
    """The base topic's design block is in the architecture spec on main (its design PR merged)."""
    import subprocess
    dref, _ = default_branch(root)
    refs = [dref, dref.split("/", 1)[1]] if dref else ["origin/main", "main", "origin/master", "master"]
    for ref in refs:
        try:
            out = subprocess.run(["git", "show", f"{ref}:{ARCH_SPEC.as_posix()}"], cwd=root, capture_output=True,
                                 text=True, encoding="utf-8", timeout=10)
        except Exception:
            return False
        if out.returncode == 0:
            sections = "".join(x.group(1) for x in re.finditer(rf"^(?:{re.escape(DECIDED)}|{re.escape(CONFIRMED)})\n(.*?)(?=^## |\Z)", out.stdout, flags=re.S | re.M))
            return f"(topic {base})" in sections
    return False


def waiting_base_text(root: Path, topic: str, base: str) -> str:
    words, bwords = topic.replace("-", " "), base.replace("-", " ")
    dn = default_name(root)
    bt = Topic(root, base)
    chosen = any(bt.design(n)["status"] == "chosen" for n in bt.designs())
    if chosen:
        why = f"The {words} design builds on {base}, whose design pull request is not merged into {dn} yet. Go-ahead here waits for that merge."
        waiting = f"the {base} design pull request (design/{base}) to merge into {dn}."
        lead, cmd = f"Open the {words} session:", plain_command(topic)
    else:
        why = f"The {words} design builds on {base}, which has not had go-ahead yet. Go-ahead here waits until the {base} design pull request is merged."
        waiting = f"go-ahead on {base} and its design pull request (design/{base}) merged into {dn}."
        lead, cmd = f"Open the {bwords} session:", plain_command(base)
    return "\n".join([f"Waiting: {waiting}", "", "Run next:", why, "", lead, f"`{cmd}`"]) + "\n"


def revisit_text(topic: str, base: str, decision: str) -> str:
    bwords = base.replace("-", " ")
    return "\n".join(["Run next:", f"{decision} is marked for another look in the base topic {base}. Settle it there, then merge design/{base} into design/{topic}.",
                      "", f"Open the {bwords} session:", f"`{plain_command(base)}`"]) + "\n"


# ---------------------------------------------------------------- endings
def _requirement_command(value) -> tuple[str, str]:
    """(reason, command) for a routed requirement. Never the bare word fact (1.200.0)."""
    if isinstance(value, dict):
        slug = str(value.get("slice") or value.get("slug") or "").strip()
        text = " ".join(str(value.get("text") or "").split())
        if not slug or not text or text == "fact":
            raise Refused("a routed requirement needs a slice and the requirement text")
        return "A requirement came up during the design.", f"/crav1-add-to-spec {slug} {text}"
    text = " ".join(str(value or "").split())
    if not text or text in ("1", "true", "True", "fact"):
        raise Refused("a routed requirement needs a slice and the requirement text")
    return "A requirement came up during the design.", f"/crav1-add-to-spec {text}"


def ending(state: dict) -> str:
    """state: phase (design|go-ahead|merged), topic, slices, routed_requirement,
    research_topic, question_open, parked, waiting, uncommitted, reason.

    A design that is still open stays open: this prints a checkpoint and the
    status line. It does not end the session (1.200.0).
    """
    topic = state["topic"]
    words = topic.replace("-", " ")
    phase = state.get("phase", "design")
    dn = state.get("default_branch") or "main"
    waiting = [f"Waiting: {x}" for x in _as_list(state.get("waiting"))]
    lead = state.get("checkpoint") or state.get("reason") or ""
    head: list[str] = []
    if lead and phase == "design" and not state.get("parked"):
        head.append(lead if lead.lower().startswith("checkpoint") else f"Checkpoint: {lead}")
    if waiting and phase == "design":
        head += ([""] if head else []) + waiting
    if phase == "design" and state.get("open") and not state.get("parked") and not state.get("routed_requirement"):
        step = state.get("step") or ""
        head += ([""] if head else []) + [status_line(topic, "open", step)]

    def block(reason: str, entries: list[tuple[str, str]]) -> list[str]:
        out = ["Run next:", reason, ""]
        for label, command in entries:
            out += [label, f"`{command}`", ""]
        return out

    if phase == "go-ahead":
        reason = state.get("reason") or "The chosen design has been reviewed, accepted, and copied on the design branch. Do not plan until this pull request is merged. Merge with no tag."
        body = block(reason, [(f"Push the {words} design branch:", f"git push -u origin design/{topic}"),
                              ("Open the pull request for that branch:", f"gh pr create --base {dn} --head design/{topic}")])
    elif phase == "merged":
        if state.get("slices"):
            s = state["slices"][0]
            reason = state.get("reason") or f"The {words} design is on {dn}. The {s} spec still needs to be brought in line with the new ADRs."
            body = block(reason, [(f"Bring the {s} spec in line with the design decisions:", f"/crav1-tighten-spec {s}")])
        elif state.get("no_slice"):
            reason = state.get("reason") or f"The {words} design is on {dn} and no slice exists yet."
            body = block(reason, [("Plan the work from the architecture spec:", "/crav1-plan-from-spec")])
        elif state.get("routed_requirement"):
            reason, command = _requirement_command(state["routed_requirement"])
            body = block(reason, [("Add the requirement to the spec:", command)])
        elif state.get("research_topic"):
            body = block("A research point now sits in the architecture spec.",
                         [("Ask for the research:", f"/crav1-show-or-ask-open-questions ask research {state['research_topic']}")])
        elif state.get("question_open"):
            body = block("An open question now sits in the architecture spec.",
                         [("Ask who has the answer:", "/crav1-show-or-ask-open-questions ask")])
        else:
            body = ["Run next: nothing needed now."]
    else:
        if state.get("routed_requirement"):
            _why, command = _requirement_command(state["routed_requirement"])
            reason = f"A requirement came up on design/{topic}. Add it from this branch."
            body = block(reason, [("Add the requirement to the spec:", command),
                                  (f"Open the {words} session:", plain_command(topic))])
        elif state.get("research_topic"):
            body = block("A research point is open in the design.",
                         [("Ask for the research:", f"/crav1-show-or-ask-open-questions ask research {state['research_topic']}"),
                          (f"Open the {words} session:", plain_command(topic))])
        elif state.get("builds_on"):
            base = state["builds_on"]
            idea = (state.get("idea") or "").strip()
            if not idea:
                raise Refused("a builds-on ending needs the idea text for the linked topic")
            reason = state.get("reason") or f"The next topic builds on {base}; commit {base} first, then start it."
            body = block(reason, [(f"Start the linked topic on top of {base}:", f"/crav1-design-architecture builds-on {base} {idea}")])
        elif state.get("parked"):
            body = ["Session parked.", ""] + block(state.get("reason") or "The topic is parked.", [("Open the session:", plain_command(topic))])
        elif state.get("open"):
            reason = state.get("reason") or "The end state is still being designed."
            body = block(reason, [(f"Open the {words} session:", plain_command(topic))])
        else:
            body = ["Run next: nothing needed now."]
    if phase != "design":
        if waiting:
            head = waiting + [""]
        else:
            head = []
    unc = _uncommitted(state.get("uncommitted"), topic)
    tail = [unc] if unc else []
    parts = [ln for ln in head + body + tail if ln is not None]
    # Drop the trailing blank the block leaves, then one newline.
    while parts and parts[-1] == "":
        parts.pop()
    return "\n".join(parts) + "\n"


def _as_list(value) -> list[str]:
    """waiting: a string is one line, a list is one line per item (1.189.0)."""
    if value is None or value is False or value == "":
        return []
    if isinstance(value, (list, tuple)):
        return [str(x).strip() for x in value if str(x).strip()]
    if value is True:
        return []
    return [str(value).strip()]


def _uncommitted(value, topic: str) -> str:
    """uncommitted: a count, or a list of paths that is counted (1.190.0). true is counted by cmd_ending."""
    if value is None or value is False or value == 0 or value == []:
        return ""
    if isinstance(value, bool) or isinstance(value, str):
        raise Refused("uncommitted takes a count of files (or a list of paths); true is counted from git status by the ending move")
    if isinstance(value, (list, tuple)):
        value = len(value)
    return uncommitted_count_line(int(value))


def _note_text(body) -> str:
    if isinstance(body, (list, tuple)):
        return "\n".join(f"- {x}" for x in body)
    if isinstance(body, dict):
        return "\n".join(f"- {k}: {v}" for k, v in body.items())
    return str(body).strip()


def _write_note(root: Path, topic: str, title: str, body, kind: str, w: Writer) -> str:
    path = root / DESIGNS / topic / "notes.md"
    cur = path.read_text(encoding="utf-8") if path.is_file() else (
        f"# Notes: {topic}\n\nDiscussion kept with the topic: scans, visions, scope lists and answers not yet in a decision.\n")
    cur = cur.rstrip("\n") + f"\n\n## {today()} {kind}: {title}\n\n{_note_text(body)}\n"
    w.write(path, cur)
    return str(path.relative_to(root).as_posix())


def cmd_note(a, root: Path) -> dict:
    t = Topic(root, a.topic)
    data = load_input(a.input)
    body = a.text if a.text else data.get("text", data.get("items"))
    if not body:
        raise Refused("a note needs text (--text, or text or items in --input)")
    w = Writer(root, t.name)
    ensure_inputs(root, t.name, w)
    path = _write_note(root, t.name, a.title, body, a.kind, w)
    return {"topic": t.name, "note": path, "written": w.written}


def cmd_small_fix(a, root: Path) -> dict:
    t = Topic(root, a.topic)
    name = t.current(a.design)
    d = t.design(name)
    text = a.text.strip()
    if not text:
        raise Refused("a small fix needs text")
    if text in d["small_fixes"]:
        raise Refused("that small fix is already listed")
    d["small_fixes"].append(text)
    w = Writer(root, t.name)
    save_design(t, name, d, w)
    return {"design": name, "small_fixes": d["small_fixes"], "written": w.written}


def cmd_ending(a, root: Path) -> str:
    state = load_input(a.input) | {"topic": a.topic}
    if state.get("uncommitted") is True:
        if current_branch(root) is None:
            raise Refused("uncommitted takes a count of files; there is no git status to count here")
        state["uncommitted"] = len(topic_dirty(root, slugify(a.topic)))
    state.setdefault("default_branch", default_name(root))
    text = ending(state)
    problems = []
    try:
        import importlib.util
        path = Path(__file__).resolve().parents[2] / "crav1-tasks-ready-to-build" / "scripts" / "run_ending.py"
        spec = importlib.util.spec_from_file_location("run_ending_design", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        problems = mod.check_ending(text)
    except Exception:
        problems = []
    if problems:
        raise Refused("ending failed its own check: " + "; ".join(problems))
    st = linked_behind(root, slugify(a.topic))
    if st["state"] == "behind":
        text = text.rstrip("\n") + "\n\n" + st["line"].replace("Linked design branches behind", "Behind") + "\n"
    return text


# ---------------------------------------------------------------- cli
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


def main(argv=None) -> int:
    argv = _bind_vendor(argv)
    p = argparse.ArgumentParser(prog="design_run.py")
    p.add_argument("--root", default=".")
    p.add_argument("--headless", action="store_true", help="run without the user: prepare only")
    p.add_argument("--no-fetch", action="store_true", help="compare the design branch with local copies only")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("route")
    r.add_argument("--word", default="")
    r.add_argument("--idea", default="")
    c = sub.add_parser("create")
    c.add_argument("--topic", required=True)
    c.add_argument("--design")
    c.add_argument("--input")
    c.add_argument("--builds-on", dest="builds_on")
    cg = sub.add_parser("change-goal")
    cg.add_argument("--topic", required=True)
    cg.add_argument("--input", required=True)
    cg.add_argument("--reason", required=True)
    cg.add_argument("--yes", action="store_true")
    rvs = sub.add_parser("revisit")
    rvs.add_argument("--topic", required=True)
    rvs.add_argument("--decision", required=True)
    rvs.add_argument("--reason", required=True)
    s = sub.add_parser("status")
    s.add_argument("--topic")
    rs = sub.add_parser("resume")
    rs.add_argument("--topic", required=True)
    rs.add_argument("--design")
    rs.add_argument("--json", dest="as_json", action="store_true", help="print the field payload; the default is the status screen")
    rs.add_argument("--skip-kit-check", action="store_true", help="go on although the branch's kit is behind the default branch")
    scn = sub.add_parser("screen")
    scn.add_argument("--topic", default="")
    nx = sub.add_parser("next")
    nx.add_argument("--topic", required=True)
    qs = sub.add_parser("questions")
    qs.add_argument("--topic", required=True)
    en = sub.add_parser("end")
    en.add_argument("--topic", required=True)
    cl = sub.add_parser("close")
    cl.add_argument("--topic", required=True)
    prp = sub.add_parser("proposal")
    prp.add_argument("--topic", required=True)
    prp.add_argument("--yes", action="store_true")
    prp.add_argument("--check", action="store_true")
    prp.add_argument("--briefing", action="store_true")
    stg = sub.add_parser("stages-list")
    stg.add_argument("--topic", required=True)
    pk = sub.add_parser("park")
    pk.add_argument("--topic", required=True)
    ro = sub.add_parser("reopen")
    ro.add_argument("--topic", required=True)
    pk.add_argument("--design")
    rv = sub.add_parser("review")
    rv.add_argument("--topic", required=True)
    rv.add_argument("--design")
    f = sub.add_parser("fan-out")
    f.add_argument("--topic", required=True)
    f.add_argument("--design")
    f.add_argument("--name", required=True)
    f.add_argument("--mode", choices=["copy", "blank"], required=True)
    f.add_argument("--title")
    ad = sub.add_parser("add-decision")
    ad.add_argument("--topic", required=True)
    ad.add_argument("--design")
    ad.add_argument("--title", required=True)
    ad.add_argument("--detail", action="store_true", help="a detail decision: proposed after the big ones")
    nt = sub.add_parser("note")
    nt.add_argument("--topic", required=True)
    nt.add_argument("--title", required=True)
    nt.add_argument("--kind", choices=["scan", "vision", "scope", "answers", "goal", "other"], default="other")
    nt.add_argument("--text")
    nt.add_argument("--input")
    bb = sub.add_parser("branch-behind")
    bb.add_argument("--topic", required=True)
    bb.add_argument("--yes", action="store_true", help="merge after the user's yes; never with --headless")
    lb = sub.add_parser("linked-behind")
    lb.add_argument("--topic", required=True, help="the base topic")
    lb.add_argument("--yes", action="store_true", help="merge into every listed branch after one yes; never with --headless")
    sw = sub.add_parser("switch-branch")
    sw.add_argument("--topic", required=True)
    sw.add_argument("--yes", action="store_true")
    co = sub.add_parser("commit")
    co.add_argument("--topic", required=True)
    co.add_argument("--message")
    co.add_argument("--yes", action="store_true")
    co.add_argument("--words", default="", help="the user's words; 'stop and commit' is a yes only when the skill says so")
    sf = sub.add_parser("small-fix")
    sf.add_argument("--topic", required=True)
    sf.add_argument("--design")
    sf.add_argument("--text", required=True)
    ln = sub.add_parser("lean")
    ln.add_argument("--topic", required=True)
    ln.add_argument("--design")
    ln.add_argument("--decision", required=True)
    ln.add_argument("--input")
    sp = sub.add_parser("settle-preview")
    sp.add_argument("--topic", required=True)
    sp.add_argument("--design")
    sp.add_argument("--one-at-a-time", action="store_true")
    sp.add_argument("--yes", action="store_true", help="accepted and still settles nothing")
    se = sub.add_parser("settle")
    se.add_argument("--topic", required=True)
    se.add_argument("--design")
    se.add_argument("--decision", required=True)
    se.add_argument("--input", required=True)
    se.add_argument("--revisit-yes", action="store_true")
    q = sub.add_parser("question")
    q.add_argument("--topic", required=True)
    q.add_argument("--design")
    q.add_argument("--decision")
    q.add_argument("--text", required=True)
    q.add_argument("--kind", choices=["question", "research"], default="question")
    q.add_argument("--research")
    q.add_argument("--stage")
    an = sub.add_parser("answer")
    an.add_argument("--topic", required=True)
    an.add_argument("--design")
    an.add_argument("--question", required=True)
    an.add_argument("--text", required=True)
    sk = sub.add_parser("skip")
    sk.add_argument("--topic", required=True)
    sk.add_argument("--design")
    sk.add_argument("--decision", required=True)
    st = sub.add_parser("stage")
    st.add_argument("--topic", required=True)
    st.add_argument("--design")
    st.add_argument("--input", required=True)
    cm = sub.add_parser("compare")
    cm.add_argument("--topic", required=True)
    cm.add_argument("--input")
    ct = sub.add_parser("compare-topics")
    ct.add_argument("--topics", nargs=2, required=True)
    ct.add_argument("--input", required=True)
    ct.add_argument("--asked", action="store_true")
    g = sub.add_parser("go-ahead")
    g.add_argument("--topic", required=True)
    g.add_argument("--design")
    g.add_argument("--slice")
    g.add_argument("--accept-findings", action="store_true")
    g.add_argument("--base-merged", action="store_true", help="the base topic's design pull request is merged")
    e = sub.add_parser("ending")
    e.add_argument("--topic", required=True)
    e.add_argument("--input")
    a = p.parse_args(argv)
    root = Path(a.root)
    _ROOT[:] = [root]
    _CMD[:] = [a.cmd]
    _DEFAULT.clear()  # resolve the default branch once per run (1.191.0)
    try:
        if a.headless and a.cmd not in HEADLESS_ALLOWED:
            raise Refused(f"a run without the user may only prepare; {a.cmd} needs the user")
        fn = {"route": lambda: cmd_route(a), "create": lambda: cmd_create(a, root), "status": lambda: cmd_status(a, root),
              "resume": lambda: cmd_resume(a, root), "screen": lambda: cmd_screen(a, root), "next": lambda: cmd_next(a, root),
              "questions": lambda: cmd_questions(a, root), "proposal": lambda: cmd_proposal(a, root),
              "stages-list": lambda: cmd_stages_list(a, root),
              "end": lambda: cmd_end(a, root), "close": lambda: cmd_end(a, root),
              "park": lambda: cmd_park(a, root), "reopen": lambda: cmd_reopen(a, root),
              "settle-preview": lambda: cmd_settle_preview(a, root),
              "review": lambda: cmd_review(a, root),
              "fan-out": lambda: cmd_fan_out(a, root), "add-decision": lambda: cmd_add_decision(a, root),
              "lean": lambda: cmd_lean(a, root), "settle": lambda: cmd_settle(a, root), "question": lambda: cmd_question(a, root),
              "answer": lambda: cmd_answer(a, root), "skip": lambda: cmd_skip(a, root), "stage": lambda: cmd_stage(a, root),
              "compare": lambda: cmd_compare(a, root), "compare-topics": lambda: cmd_compare_topics(a, root),
              "go-ahead": lambda: cmd_go_ahead(a, root), "ending": lambda: cmd_ending(a, root),
              "change-goal": lambda: cmd_change_goal(a, root), "revisit": lambda: cmd_revisit(a, root),
              "note": lambda: cmd_note(a, root), "small-fix": lambda: cmd_small_fix(a, root),
              "branch-behind": lambda: cmd_branch_behind(a, root), "linked-behind": lambda: cmd_linked_behind(a, root),
              "switch-branch": lambda: cmd_switch_branch(a, root), "commit": lambda: cmd_commit(a, root)}[a.cmd]
        res = fn()
    except Refused as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(res if isinstance(res, str) else json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
