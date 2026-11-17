#!/usr/bin/env python3
"""State machine for /crav1-design-architecture (1.181.0).

Owns the sandbox format under docs/architecture/designs/<topic>/ and every move:
create, status, resume, park, fan-out, lean, settle, question, answer, skip,
stage, compare, compare-topics, review, go-ahead, ending, route.

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
START_WORDS = ["resume", "park", "status", "fan-out", "stage-it", "go-ahead", "compare-topics", "prepare"]
HEADLESS_WORDS = ["resume", "park", "status", "prepare"]
HEADLESS_ALLOWED = {"status", "resume", "lean", "compare", "compare-topics", "route", "ending", "review"}
STATES = {"open", "leaning", "settled", "to-question", "to-research", "skipped", "reopened"}
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
    return {"topic": title, "ask": meta(head).get("Ask", "").strip('"'),
            "end_goal": sec.get("End goal", ""), "drivers": bullets(sec.get("Drivers", "")),
            "constraints": bullets(sec.get("Constraints", "")), "criteria": bullets(sec.get("Criteria", ""))}


def render_goal(g: dict) -> str:
    def bl(xs):
        return "\n".join(f"- {x}" for x in xs) if xs else "- none yet"
    return (f"# Goal: {g['topic']}\n\n- Ask: \"{g['ask']}\"\n\n## End goal\n\n{g['end_goal']}\n\n"
            f"## Drivers\n\n{bl(g['drivers'])}\n\n## Constraints\n\n{bl(g['constraints'])}\n\n"
            f"## Criteria\n\n{bl(g['criteria'])}\n")


DEC_KEYS = ["State", "Options shown", "Leaning", "Recommended", "Draft ADR", "Open question in", "Sources", "Reopened", "Reverses"]


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
    return {"title": first[len("# Design: "):] if first.startswith("# Design: ") else first,
            "topic": m.get("Topic", ""), "status": m.get("Status", "open"),
            "ask": m.get("Ask", "").strip('"'), "end_state": sec.get("End state", ""),
            "decisions": decisions, "drivers": bullets(sec.get("Drivers", "")),
            "ideas": bullets(sec.get("Ideas", ""))}


def render_design(d: dict) -> str:
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
    for q in sorted(qs, key=lambda x: x["text"].casefold()):
        lines.append(f"- {q['text']}")
        for k in ("decision", "kind", "research", "stage", "answer"):
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
            raise Refused(f"no topic {name} under {DESIGNS}")

    def designs(self) -> list[str]:
        d = self.dir / "designs"
        return sorted(p.name for p in d.iterdir() if (p / "design.md").is_file()) if d.is_dir() else []

    def ddir(self, design: str) -> Path:
        p = self.dir / "designs" / design
        if not (p / "design.md").is_file():
            raise Refused(f"no design {design} in topic {self.name}")
        return p

    def goal(self) -> dict:
        return parse_goal((self.dir / "goal.md").read_text(encoding="utf-8"))

    def design(self, design: str) -> dict:
        return parse_design((self.ddir(design) / "design.md").read_text(encoding="utf-8"))

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
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


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
        lines.append(f"- {n}: {settled} of {len(d['decisions'])} settled, status {d['status']}")
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
    if word in START_WORDS:
        return word
    if word:
        raise Refused("Unknown word " + word + ". Use one of: <idea text>, " + ", ".join(START_WORDS) + ".")
    return "idea" if a.idea else "ask"


def cmd_create(a, root: Path) -> dict:
    data = load_input(a.input)
    topic = slugify(a.topic)
    tdir = root / DESIGNS / topic
    if (tdir / "goal.md").exists():
        raise Refused(f"topic {topic} already exists; use resume")
    w = Writer(root, topic)
    goal = {"topic": topic, "ask": data.get("ask", ""), "end_goal": data.get("end_goal", ""),
            "drivers": data.get("drivers", []), "constraints": data.get("constraints", []),
            "criteria": data.get("criteria", [])}
    w.write(tdir / "goal.md", render_goal(goal))
    name = slugify(a.design or data.get("design", "first-design"))
    _new_design(root, topic, name, data.get("design_title", name.replace("-", " ")), goal["ask"],
                [{"title": x, "State": "open"} for x in data.get("decisions", [])], goal["drivers"], w)
    return {"topic": topic, "design": name, "branch": f"design/{topic}", "written": w.written}


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
                        "settled": [x["title"] for x in d["decisions"] if x["State"] == "settled"],
                        "open": [x["title"] for x in d["decisions"] if x["State"] != "settled"],
                        "questions": [q["text"] for q in t.questions(dn) if not q.get("answer")],
                        "stages": [s["name"] for s in t.stages(dn)]})
    return {"designs": out}


def cmd_resume(a, root: Path) -> dict:
    t = Topic(root, a.topic)
    name = t.current(a.design)
    d = t.design(name)
    w = Writer(root, t.name)
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
    if d["status"] == "parked":
        d["status"] = "open"
    if not a.headless:
        save_design(t, name, d, w)
        if reopened:
            for st in t.stages(name):
                st["state"] = "needs another look"
            if t.stages(name):
                w.write(t.ddir(name) / "stages.md", render_stages(name, [dict(s, state="needs another look") for s in t.stages(name)]))
    nxt = next((x["title"] for x in d["decisions"] if x["State"] == "reopened"), None) or \
        next((x["title"] for x in d["decisions"] if x["State"] in ("open", "leaning")), None)
    stage_work = [s["name"] for s in t.stages(name) if s.get("state") != "open" and s.get("state")]
    return {"topic": t.name, "design": name, "reopened": reopened, "next_decision": nxt,
            "stages_needing_work": stage_work, "written": w.written}


def cmd_park(a, root: Path) -> dict:
    t = Topic(root, a.topic)
    name = t.current(a.design)
    d = t.design(name)
    d["status"] = "parked"
    w = Writer(root, t.name)
    save_design(t, name, d, w)
    return {"topic": t.name, "design": name, "status": "parked", "written": w.written}


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
    return {"topic": t.name, "design": new, "mode": a.mode, "written": w.written}


def cmd_add_decision(a, root: Path) -> dict:
    t = Topic(root, a.topic)
    name = t.current(a.design)
    d = t.design(name)
    if any(x["title"].casefold() == a.title.casefold() for x in d["decisions"]):
        raise Refused("that decision is already listed")
    d["decisions"].append({"title": a.title, "State": "open"})
    w = Writer(root, t.name)
    save_design(t, name, d, w)
    return {"design": name, "written": w.written}


def cmd_lean(a, root: Path) -> dict:
    """Save options shown and a lean or recommendation. Allowed in prepare."""
    data = load_input(a.input)
    t = Topic(root, a.topic)
    name = t.current(a.design)
    d = t.design(name)
    dec = find_decision(d, a.decision)
    if dec["State"] == "settled":
        raise Refused("that decision is settled; reopen it with a choose word in chat first")
    if data.get("options"):
        dec["Options shown"] = ", ".join(o["name"] for o in data["options"])
    if data.get("recommended"):
        dec["Recommended"] = data["recommended"]
    if data.get("leaning") and not a.headless:
        dec["Leaning"] = data["leaning"]
    if dec["State"] in ("open", "reopened"):
        dec["State"] = "leaning" if dec.get("Leaning") else dec["State"]
    for drv in data.get("drivers", []):
        if drv not in d["drivers"]:
            d["drivers"].append(drv)
    for idea in data.get("ideas", []):
        if idea not in d["ideas"]:
            d["ideas"].append(idea)
    w = Writer(root, t.name)
    save_design(t, name, d, w)
    return {"design": name, "decision": dec["title"], "written": w.written}


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


def cmd_settle(a, root: Path) -> dict:
    data = load_input(a.input)
    t = Topic(root, a.topic)
    name = t.current(a.design)
    d = t.design(name)
    dec = find_decision(d, a.decision)
    reverses = data.get("reverses", "")
    if reverses and not a.revisit_yes:
        raise Refused(f"this choice reverses {reverses}; it is a revisit and needs a separate yes (--revisit-yes)")
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
    return {"design": name, "decision": dec["title"], "adr": str(adr_path.relative_to(root)), "written": w.written}


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
    qs = [x for x in t.questions(name) if x["text"] != a.text] + [q]
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
    return {"design": name, "stages": [s["name"] for s in stages], "written": w.written}


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
        if dec["State"] in ("open", "leaning", "skipped", "reopened"):
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
    findings = review(t, name, root)
    if findings and not a.accept_findings:
        return {"design": name, "findings": findings, "copied": False, "written": [],
                "note": "fix the findings in the sandbox or accept them, then run go-ahead again"}
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
    if adr_targets:
        block.append("Accepted ADRs: " + ", ".join(f"`{x[1]}`" for x in adr_targets))
    block += ["", d["end_state"]]
    stages = t.stages(name)
    if stages:
        block += ["", "Stages:"]
        for i, st in enumerate(stages, 1):
            block.append(f"{i}. {st['name']}: {st.get('reason', '')}" + (f" Waits on: {st['waits_on']}" if st.get("waits_on") else ""))
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
    return {"design": name, "findings": findings, "copied": True, "adrs": [str(x[1]) for x in adr_targets],
            "slice": slice_slug, "written": w.written}


# ---------------------------------------------------------------- endings
def ending(state: dict) -> str:
    """state: phase (design|go-ahead|merged), topic, slices, routed_requirement,
    research_topic, question_open, parked, waiting, uncommitted, reason"""
    topic = state["topic"]
    words = topic.replace("-", " ")
    phase = state.get("phase", "design")
    out = ["Run next:"]
    if phase == "go-ahead":
        out.append(state.get("reason") or "The chosen design has been reviewed, accepted, and copied on the design branch.")
        out.append("Do not plan until this pull request is merged. Merge with no tag.")
        out += ["", f"Push the {words} design branch:", f"`git push -u origin design/{topic}`", "",
                "Open the pull request for that branch:", f"`gh pr create --base main --head design/{topic}`"]
    elif phase == "merged":
        if state.get("slices"):
            s = state["slices"][0]
            out += [state.get("reason") or f"The {words} design is on main. The {s} spec still needs to be brought in line with the new ADRs.", "",
                    f"Bring the {s} spec in line with the design decisions:", f"`/crav1-tighten-spec {s}`"]
        elif state.get("no_slice"):
            out += [state.get("reason") or f"The {words} design is on main and no slice exists yet.", "",
                    "Plan the work from the architecture spec:", "`/crav1-plan-from-spec`"]
        elif state.get("routed_requirement"):
            out += ["A requirement came up during the design.", "", "Add the requirement to the spec:", "`/crav1-add-to-spec fact`"]
        elif state.get("research_topic"):
            out += ["A research point now sits in the architecture spec.", "", "Ask for the research:",
                    f"`/crav1-show-or-ask-open-questions ask research {state['research_topic']}`"]
        elif state.get("question_open"):
            out += ["An open question now sits in the architecture spec.", "", "Ask who has the answer:", "`/crav1-show-or-ask-open-questions ask`"]
        else:
            out = ["Run next: nothing needed now."]
    else:
        if state.get("routed_requirement"):
            out += ["A requirement came up during the design.", "", "Add the requirement to the spec:", "`/crav1-add-to-spec fact`"]
        elif state.get("research_topic"):
            out += ["A research point is open in the design.", "", "Ask for the research:",
                    f"`/crav1-show-or-ask-open-questions ask research {state['research_topic']}`"]
        elif state.get("parked") or state.get("open"):
            out += [state.get("reason") or ("The topic is parked." if state.get("parked") else "The end state is still being designed."), "",
                    f"Pick up the {words} designs:", f"`/crav1-design-architecture resume {topic}`"]
        else:
            out = ["Run next: nothing needed now."]
    tail = []
    if state.get("waiting"):
        tail.append(f"Waiting: {state['waiting']}")
    if state.get("uncommitted"):
        n = state["uncommitted"]
        tail.append(f"Uncommitted: {n} file{'s' if n != 1 else ''}.")
    if tail:
        out += [""] + tail
    return "\n".join(out) + "\n"


def cmd_ending(a, root: Path) -> str:
    return ending(load_input(a.input) | {"topic": a.topic})


# ---------------------------------------------------------------- cli
def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="design_run.py")
    p.add_argument("--root", default=".")
    p.add_argument("--headless", action="store_true", help="run without the user: prepare only")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("route")
    r.add_argument("--word", default="")
    r.add_argument("--idea", default="")
    c = sub.add_parser("create")
    c.add_argument("--topic", required=True)
    c.add_argument("--design")
    c.add_argument("--input")
    s = sub.add_parser("status")
    s.add_argument("--topic")
    rs = sub.add_parser("resume")
    rs.add_argument("--topic", required=True)
    rs.add_argument("--design")
    pk = sub.add_parser("park")
    pk.add_argument("--topic", required=True)
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
    ln = sub.add_parser("lean")
    ln.add_argument("--topic", required=True)
    ln.add_argument("--design")
    ln.add_argument("--decision", required=True)
    ln.add_argument("--input")
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
    e = sub.add_parser("ending")
    e.add_argument("--topic", required=True)
    e.add_argument("--input")
    a = p.parse_args(argv)
    root = Path(a.root)
    try:
        if a.headless and a.cmd not in HEADLESS_ALLOWED:
            raise Refused(f"a run without the user may only prepare; {a.cmd} needs the user")
        fn = {"route": lambda: cmd_route(a), "create": lambda: cmd_create(a, root), "status": lambda: cmd_status(a, root),
              "resume": lambda: cmd_resume(a, root), "park": lambda: cmd_park(a, root), "review": lambda: cmd_review(a, root),
              "fan-out": lambda: cmd_fan_out(a, root), "add-decision": lambda: cmd_add_decision(a, root),
              "lean": lambda: cmd_lean(a, root), "settle": lambda: cmd_settle(a, root), "question": lambda: cmd_question(a, root),
              "answer": lambda: cmd_answer(a, root), "skip": lambda: cmd_skip(a, root), "stage": lambda: cmd_stage(a, root),
              "compare": lambda: cmd_compare(a, root), "compare-topics": lambda: cmd_compare_topics(a, root),
              "go-ahead": lambda: cmd_go_ahead(a, root), "ending": lambda: cmd_ending(a, root)}[a.cmd]
        res = fn()
    except Refused as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(res if isinstance(res, str) else json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
