#!/usr/bin/env python3
"""UI screens, their sign-off, and the plan gate (kit 1.211.0).

The written Markdown is the source of truth: `ui/design.md` (look, layout,
tokens) and `ui/experience.md` (screens, states, interactions, checks) in a
slice folder `docs/specs/<slug>/`. A screen is a `### <name> (S<n>)` heading.
The same heading in `ui/design.md` holds that screen's layout. A mock under
`ui/mock/` is never read here: it is not a plan input.

Each screen gets one `## Approval needed` item in `spec.md`, written through
skill `crav1-record-approval` `scripts/approval_needed.py` (`add_item`). The
item carries a `Screen:` mark with per-screen hashes:

  - Screen: S1, version <12 hex>, shape name=<6> path=<6> layout=<6> states=<6> interactions=<6> checks=<6> other=<6>

`version` hashes the screen's text with spacing collapsed. `shape` hashes each
part with a spelling-tolerant key per word, so a typo, a case change, or
punctuation keeps the shape. A changed shape is a material change: it names
the parts that changed. A material change to an approved screen clears that
screen's yes: `sync --yes` appends `Cleared: <date>, material change: <why>`.
An `Approved:` line above the last `Cleared:` line no longer counts. The
`Approved:` line itself is never removed and never written here.

Usage (JSON on stdout, except --text):
  ui_screens.py status --root <spec-folder>
  ui_screens.py gate   --root <spec-folder> [--text]
  ui_screens.py sync   --root <spec-folder> [--person "<who>"] [--today YYYY-MM-DD] [--yes]
  ui_screens.py touches --root <spec-folder> --text "<the change>"
  ui_screens.py trace  --root <spec-folder>

status, gate, touches and trace write nothing. sync without --yes prints what
it would write and writes nothing. sync refuses while a binary file is under
ui/. Exit 0 on success, 2 on a missing spec or bad input. Standard library
only. Line endings of spec.md stay as they were.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from datetime import date
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

PARTS = ("name", "path", "layout", "states", "interactions", "checks", "other")
PART_WORDS = {
    "name": "the screen's name",
    "path": "its path or window",
    "layout": "the layout in ui/design.md",
    "states": "the states",
    "interactions": "the interactions",
    "checks": "the UI acceptance checks",
    "other": "the other screen notes",
}
SCREEN_HEAD = re.compile(r"^###\s+(?P<name>.+?)\s+\((?P<id>S\d+)\)\s*$")
SUB_HEAD = re.compile(r"^####\s+(?P<title>.+?)\s*$")
PATH_LINE = re.compile(r"^\s*(?:-\s+)?(?:Path|Window|Route):\s*\S", re.I)
CHECK_LINE = re.compile(r"^\s*-\s+\[[ xX]\]\s+(?P<text>.+?)\s*\((?P<id>S\d+-C\d+)\)\s*$")
COMMENT = re.compile(r"<!--.*?-->", re.S)
SCREEN_MARK = re.compile(r"^Screen:\s*(?P<id>S\d+),\s*version\s+(?P<version>[0-9a-f]{12}),\s*shape\s+(?P<shape>.+)$")
UI_NONE = re.compile(r"^(?:-\s+)?UI:\s*none\b(?P<why>.*)$", re.I | re.M)
TASK_LINE = re.compile(r"^\s*-\s*\[( |x|X)\]\s*T(\d+)\s*:\s*(.*)$")
SPEC_MARK = re.compile(r"\(spec:\s*([^)]*)\)", re.I)
VOWELS = set("aeiouy")
# Words that say a slice has a user-facing surface. Only a hint: the design
# step asks once when the spec names one and no ui/ file or UI: none exists.
UI_WORDS = re.compile(
    r"(?i)\b(?:screens?|buttons?|dashboards?|dialogs?|modals?|user interface|ui|"
    r"click(?:s|ed|ing)?|web page|browser|layout|tooltip|sidebar|toolbar)\b"
)
TEXT_SUFFIXES = {
    ".md", ".html", ".htm", ".css", ".js", ".mjs", ".txt", ".puml", ".plantuml",
    ".mmd", ".json", ".yaml", ".yml", ".svg",
}
BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico", ".tif", ".tiff",
    ".heic", ".pdf", ".psd", ".sketch", ".fig", ".zip", ".mp4", ".mov", ".webm",
}


def _emit(payload) -> None:
    text = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False, indent=1)
    if not text.endswith("\n"):
        text += "\n"
    try:
        sys.stdout.write(text)
    except UnicodeEncodeError:
        sys.stdout.write(text.encode("ascii", "replace").decode("ascii"))
    sys.stdout.flush()


def _fail(code: str, message: str) -> int:
    _emit({"ok": False, "code": code, "message": message})
    return 2


def _load_approval():
    """skill crav1-record-approval scripts/approval_needed.py, the one item writer."""
    here = Path(__file__).resolve()
    path = here.parents[2] / "crav1-record-approval" / "scripts" / "approval_needed.py"
    if not path.is_file():
        raise SystemExit(f"approval_needed.py not found: {path}")
    spec = importlib.util.spec_from_file_location("crav1_approval_needed_ui", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_bytes().decode("utf-8")


# ---------- parsing ----------

def _lines_outside_fences(text: str):
    """(line, in_fence) pairs. A heading inside a code fence is not a heading."""
    fence = None
    for line in (text or "").splitlines():
        stripped = line.strip()
        if fence is None and (stripped.startswith("```") or stripped.startswith("~~~")):
            fence = stripped[:3]
            yield line, True
            continue
        if fence is not None:
            if stripped.startswith(fence):
                fence = None
            yield line, True
            continue
        yield line, False


def screen_sections(text: str) -> dict[str, dict]:
    """Screen id -> {name, lines}. Placeholder names such as `<Screen name>` are skipped."""
    found: dict[str, dict] = {}
    current = None
    for line, fenced in _lines_outside_fences(COMMENT.sub("", text or "")):
        if not fenced:
            head = SCREEN_HEAD.match(line)
            if head:
                name = head.group("name").strip()
                if "<" in name or ">" in name:
                    current = None
                    continue
                current = {"name": name, "lines": []}
                found.setdefault(head.group("id"), current)
                continue
            if line.startswith("## ") or line.startswith("# ") or (line.startswith("### ") and not head):
                current = None
                continue
        if current is not None:
            current["lines"].append(line)
    return found


def _split_experience(lines: list[str]) -> dict[str, list[str]]:
    parts = {"path": [], "states": [], "interactions": [], "checks": [], "other": []}
    where = "other"
    fenced_state = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            fenced_state = not fenced_state
            parts[where].append(line)
            continue
        if not fenced_state:
            sub = SUB_HEAD.match(line)
            if sub:
                title = sub.group("title").strip().lower()
                if title.startswith("state"):
                    where = "states"
                elif title.startswith("interaction"):
                    where = "interactions"
                elif title.startswith(("check", "ui acceptance", "acceptance")):
                    where = "checks"
                else:
                    where = "other"
                    parts["other"].append(line)
                continue
            if PATH_LINE.match(line):
                parts["path"].append(line)
                continue
        parts[where].append(line)
    return parts


def _collapse(lines: list[str]) -> str:
    return re.sub(r"\s+", " ", "\n".join(lines)).strip()


def word_key(word: str) -> str:
    """A spelling-tolerant key. Short words and words with a digit stay exact."""
    w = word.lower()
    if len(w) <= 2 or any(c.isdigit() for c in w):
        return w
    consonants = sorted({c for c in w if c.isalpha() and c not in VOWELS})
    return w[0] + "".join(consonants)


def shape_of(text: str) -> str:
    words = re.findall(r"#?[A-Za-z0-9]+", text or "")
    return " ".join(word_key(w) for w in words)


def _h(text: str, n: int) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:n]


def screens(root: Path) -> list[dict]:
    """Every screen in ui/experience.md (and layout-only screens in ui/design.md), in id order."""
    exp = screen_sections(_read(root / "ui" / "experience.md"))
    des = screen_sections(_read(root / "ui" / "design.md"))
    ids = sorted(set(exp) | set(des), key=lambda s: int(s[1:]))
    out = []
    for sid in ids:
        e = exp.get(sid) or {"name": des[sid]["name"], "lines": []}
        parts = _split_experience(e["lines"])
        parts["layout"] = des.get(sid, {}).get("lines", [])
        name = e["name"]
        texts = {"name": name}
        for key in PARTS[1:]:
            texts[key] = _collapse(parts[key])
        version = _h("\n\x1f".join(texts[p] for p in PARTS), 12)
        shape = {p: _h(shape_of(texts[p]), 6) for p in PARTS}
        checks = []
        for line in parts["checks"]:
            m = CHECK_LINE.match(line)
            if m:
                checks.append({"id": m.group("id"), "text": m.group("text").strip()})
        out.append({
            "id": sid,
            "name": name,
            "label": f"{name} ({sid})",
            "version": version,
            "shape": shape,
            "checks": checks,
            "in_design": sid in des,
            "in_experience": sid in exp,
            "states_text": texts["states"],
        })
    return out


def screen_mark(screen: dict) -> str:
    shape = " ".join(f"{p}={screen['shape'][p]}" for p in PARTS)
    return f"Screen: {screen['id']}, version {screen['version']}, shape {shape}"


def parse_screen_mark(mark: str) -> dict | None:
    m = SCREEN_MARK.match((mark or "").strip())
    if not m:
        return None
    shape = {}
    for piece in m.group("shape").split():
        key, _, value = piece.partition("=")
        if key and value:
            shape[key] = value
    return {"id": m.group("id"), "version": m.group("version"), "shape": shape}


def classify(stored: dict | None, current: dict | None) -> dict:
    """unchanged, minor, material, or removed, with the reason in plain words."""
    if current is None:
        return {"kind": "removed", "why": "the screen is no longer in ui/experience.md or ui/design.md"}
    if stored is None:
        return {"kind": "new", "why": "no sign-off item names this screen yet"}
    if stored["version"] == current["version"]:
        return {"kind": "unchanged", "why": "the screen's text is the same"}
    changed = [p for p in PARTS if stored["shape"].get(p) != current["shape"][p]]
    if not changed:
        return {
            "kind": "minor",
            "why": "only spelling, case, punctuation or spacing changed; the words, their order, "
                   "the layout, states, interactions, checks, name and path are the same",
        }
    named = [PART_WORDS[p] for p in changed]
    text = named[0] if len(named) == 1 else ", ".join(named[:-1]) + " and " + named[-1]
    return {"kind": "material", "why": f"{text} changed", "parts": changed}


# ---------- spec items ----------

def _approval_section(text: str) -> tuple[int, int] | None:
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.strip().lower() == "## approval needed"), None)
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return start, end


def screen_items(spec_text: str) -> dict[str, dict]:
    """Screen id -> the Approval needed item that carries its Screen: mark."""
    an = _load_approval()
    rows = an.items(spec_text, None)
    out: dict[str, dict] = {}
    for row in rows:
        stored = None
        for mark in row.get("marks_all") or []:
            parsed = parse_screen_mark(mark)
            if parsed:
                stored = parsed
        if stored:
            out.setdefault(stored["id"], {**row, "stored": stored})
    return out


def ui_presence(root: Path, spec_text: str, found: list[dict]) -> dict:
    if found:
        return {"ui": "yes", "why": f"ui/experience.md names {len(found)} screen(s)"}
    none = UI_NONE.search(spec_text or "")
    if none:
        reason = none.group("why").strip(" -—:()") or "no user-facing surface"
        return {"ui": "no", "why": f"spec.md says UI: none ({reason})"}
    if (root / "ui").is_dir():
        return {"ui": "unclear", "why": "ui/ exists but names no screen yet"}
    body = COMMENT.sub("", spec_text or "")
    words = sorted({m.group(0).lower() for m in UI_WORDS.finditer(body)})
    if words:
        return {"ui": "unclear", "why": "spec.md names " + ", ".join(words[:5]) + " and has no ui/ files and no UI: none line"}
    return {"ui": "no", "why": "spec.md names no screen and there are no ui/ files"}


def binaries(root: Path) -> list[str]:
    """Files under ui/ that are not text. Screenshots are never stored in the repo."""
    folder = root / "ui"
    if not folder.is_dir():
        return []
    out = []
    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        suffix = path.suffix.lower()
        if suffix in BINARY_SUFFIXES:
            out.append(rel)
            continue
        try:
            head = path.read_bytes()[:4096]
        except OSError:
            continue
        if b"\x00" in head:
            out.append(rel)
            continue
        if suffix not in TEXT_SUFFIXES:
            try:
                head.decode("utf-8")
            except UnicodeDecodeError:
                out.append(rel)
    return out


def status(root: Path) -> dict:
    spec_text = _read(root / "spec.md")
    found = screens(root)
    presence = ui_presence(root, spec_text, found)
    items = screen_items(spec_text) if spec_text else {}
    by_id = {s["id"]: s for s in found}
    rows = []
    for screen in found:
        item = items.get(screen["id"])
        change = classify(item["stored"] if item else None, screen)
        if item is None:
            state = "new"
        elif item.get("approved"):
            state = "approved" if change["kind"] in ("unchanged", "minor") else "changed"
        else:
            state = "waiting"
        rows.append({
            "id": screen["id"],
            "label": screen["label"],
            "state": state,
            "change": change["kind"],
            "why": change["why"],
            "item": item["text"] if item else None,
            "who": item.get("who") if item else None,
            "checks": screen["checks"],
        })
    for sid, item in items.items():
        if sid not in by_id:
            rows.append({
                "id": sid,
                "label": sid,
                "state": "removed",
                "change": "removed",
                "why": classify(item["stored"], None)["why"],
                "item": item["text"],
                "who": item.get("who"),
                "checks": [],
            })
    return {
        "ok": True,
        **presence,
        "screens": rows,
        "approved": [r["label"] for r in rows if r["state"] == "approved"],
        "waiting": [r["label"] for r in rows if r["state"] in ("waiting", "new", "changed")],
        "binaries": binaries(root),
    }


# ---------- gate (plan-from-spec and the walk's plan step) ----------

def _run_next(slug: str, design_first: bool) -> str:
    design = ("Design the screens and add one sign-off item per screen:", f"/crav1-design-ui {slug}")
    record = ("Record each screen's yes as an Approved line:", "/crav1-record-approval")
    first, second = (design, record) if design_first else (record, design)
    if not design_first:
        second = ("Or change a screen first:", second[1])
    return f"Run next:\n\n{first[0]}\n`{first[1]}`\n{second[0]}\n`{second[1]}`"


def gate(root: Path) -> dict:
    data = status(root)
    slug = root.name
    lines: list[str] = []
    if data["binaries"]:
        lines.append("A binary file is under ui/: " + ", ".join(data["binaries"])
                     + ". Screenshots are never stored in the repo; describe what they show in ui/experience.md and remove the file.")
    if data["ui"] == "no":
        ok = not data["binaries"]
        lines.insert(0, f"No UI step: {data['why']}.")
        return {**data, "ok": ok, "plan": "whole slice" if ok else "stop", "lines": lines,
                "run_next": None if ok else _run_next(slug, True)}
    rows = data["screens"]
    approved = [r for r in rows if r["state"] == "approved"]
    held = [r for r in rows if r["state"] in ("new", "waiting", "changed")]
    for r in rows:
        if r["state"] == "changed":
            lines.append(f"{r['label']}: its yes was cleared, {r['why']} (a material change).")
        elif r["state"] == "approved" and r["change"] == "minor":
            lines.append(f"{r['label']}: the yes stays, {r['why']}.")
        elif r["state"] == "removed":
            lines.append(f"{r['label']}: {r['why']}; it is not planned.")
    if not approved or data["binaries"]:
        if data["ui"] == "unclear":
            lines.insert(0, f"The UI step has not run: {data['why']}. /crav1-design-ui asks once whether it applies.")
        elif not approved:
            lines.insert(0, "No UI screen is signed off yet, so plan.md and tasks.md are not written.")
        design_first = data["ui"] == "unclear" or any(r["state"] in ("new", "changed") for r in rows) or not rows
        return {**data, "ok": False, "plan": "stop", "lines": lines, "run_next": _run_next(slug, design_first)}
    lines.insert(0, "Plan covers the signed-off screens: " + ", ".join(r["label"] for r in approved) + ".")
    if held:
        lines.append("Not planned until their yes: " + ", ".join(r["label"] for r in held) + ".")
    return {**data, "ok": True, "plan": "approved screens", "lines": lines, "run_next": None}


def gate_text(result: dict) -> str:
    out = list(result["lines"])
    if result.get("run_next"):
        out += ["", result["run_next"]]
    return "\n".join(out) + "\n"


# ---------- sync (the design step's one write) ----------

def _item_bounds(lines: list[str], start: int, end: int, sid: str) -> tuple[int, int] | None:
    """Bullet index and last mark index of the item whose Screen: mark names sid."""
    bullet = None
    for i in range(start + 1, end):
        raw = lines[i]
        if raw.startswith("- "):
            bullet = i
            continue
        if bullet is not None and raw.startswith("  - "):
            parsed = parse_screen_mark(raw[4:].strip())
            if parsed and parsed["id"] == sid:
                last = bullet
                for j in range(bullet + 1, end):
                    if lines[j].startswith("- ") or lines[j].startswith("## "):
                        break
                    if lines[j].strip():
                        last = j
                return bullet, last
    return None


def item_title(screen: dict, person: str) -> str:
    return (f"UI screen {screen['label']}: {person} approves its layout, states and interactions "
            f"in ui/design.md and ui/experience.md")


def sync_plan(root: Path, person: str | None) -> dict:
    data = status(root)
    found = {s["id"]: s for s in screens(root)}
    actions = []
    for row in data["screens"]:
        screen = found.get(row["id"])
        if row["state"] == "new":
            actions.append({"id": row["id"], "do": "add-item", "label": row["label"],
                            "line": f"New screen {row['label']}: its own sign-off item; earlier yeses stay."})
        elif row["state"] == "changed":
            actions.append({"id": row["id"], "do": "clear", "label": row["label"], "why": row["why"],
                            "line": f"{row['label']}: material change ({row['why']}). Its yes is cleared; it needs a new yes."})
        elif row["state"] == "approved" and row["change"] == "minor":
            actions.append({"id": row["id"], "do": "refresh", "label": row["label"],
                            "line": f"{row['label']}: not a material change ({row['why']}). The yes stays."})
        elif row["state"] == "waiting" and row["change"] != "unchanged":
            actions.append({"id": row["id"], "do": "refresh", "label": row["label"],
                            "line": f"{row['label']}: still waiting for its yes; the item now names the current text."})
        elif row["state"] == "removed":
            actions.append({"id": row["id"], "do": "none", "label": row["label"],
                            "line": f"{row['id']}: {row['why']}. Its item stays; it is not planned."})
        if screen and row["state"] == "changed" and screen["name"] not in (row.get("item") or ""):
            actions[-1]["rename"] = screen["label"]
    needs_person = any(a["do"] == "add-item" for a in actions) and not (person or "").strip()
    return {"ok": not data["binaries"] and not needs_person, "actions": actions, "binaries": data["binaries"],
            "needs_person": needs_person, "status": data}


def apply_sync(root: Path, person: str | None, today: str) -> dict:
    plan = sync_plan(root, person)
    if plan["binaries"]:
        return {**plan, "ok": False, "code": "binaries",
                "message": "A binary file is under ui/. Remove it first; the text in ui/experience.md is what gets approved."}
    if plan["needs_person"]:
        return {**plan, "ok": False, "code": "person", "message": "sync needs --person for a new screen's item"}
    spec_path = root / "spec.md"
    text = _read(spec_path)
    an = _load_approval()
    found = {s["id"]: s for s in screens(root)}
    nl = an.newline_of(text)
    wrote = []
    for action in plan["actions"]:
        screen = found.get(action["id"])
        if action["do"] == "add-item" and screen:
            text, state = an.add_item(
                text, person.strip(), "", [], title=item_title(screen, person.strip()),
                holds_text=f"none (UI screen {screen['id']}; the plan waits for this yes)",
                extra_marks=[screen_mark(screen)], screen=screen["id"],
            )
            if state == "wrote":
                wrote.append(action["line"])
            continue
        if action["do"] not in ("clear", "refresh") or not screen:
            continue
        bounds = _approval_section(text)
        if bounds is None:
            continue
        lines = text.splitlines(keepends=True)
        where = _item_bounds(lines, bounds[0], bounds[1], screen["id"])
        if where is None:
            continue
        bullet, last = where
        for k in range(bullet + 1, last + 1):
            if lines[k].startswith("  - ") and parse_screen_mark(lines[k][4:].strip()):
                lines[k] = f"  - {screen_mark(screen)}{nl}"
        if action["do"] == "clear":
            if not lines[last].endswith(("\n", "\r\n")):
                lines[last] += nl
            lines.insert(last + 1, f"  - Cleared: {today}, material change: {action['why']}{nl}")
            if action.get("rename"):
                head = re.match(r"^- UI screen (.+?\(S\d+\)):", lines[bullet])
                if head:
                    lines[bullet] = lines[bullet].replace(head.group(1), action["rename"], 1)
        text = "".join(lines)
        wrote.append(action["line"])
    if wrote:
        spec_path.write_bytes(text.encode("utf-8"))
    return {**plan, "ok": True, "wrote": wrote}


# ---------- touches (add-to-spec and the walk warn) ----------

def touches(root: Path, change: str) -> dict:
    data = status(root)
    low = (change or "").lower()
    hits = []
    for row in data["screens"]:
        if row["state"] != "approved":
            continue
        name = row["label"].rsplit(" (", 1)[0].lower()
        if re.search(rf"\b{re.escape(row['id'].lower())}\b", low) or (name and name in low):
            hits.append(row)
    lines = [
        f"This change touches the signed-off screen {r['label']}. Its yes stays until /crav1-design-ui "
        f"records the change: a material change (layout, states, interactions, or its name or path) clears it, "
        f"a typo or a non-UI edit keeps it."
        for r in hits
    ]
    return {"ok": True, "touched": [r["label"] for r in hits], "lines": lines}


# ---------- trace (plan recap and review-plan) ----------

def trace(root: Path) -> dict:
    data = status(root)
    tasks_text = _read(root / "tasks.md")
    marks = " ".join(m.group(1) for m in SPEC_MARK.finditer(tasks_text))
    ui_kind = [f"T{m.group(2)}" for m in map(TASK_LINE.match, tasks_text.splitlines())
               if m and re.search(r"\(verify:\s*ui\b", m.group(3), re.I)]
    untraced = []
    unapproved = []
    for row in data["screens"]:
        for check in row["checks"]:
            named = re.search(rf"\b{re.escape(check['id'])}\b", marks)
            if row["state"] == "approved" and not named:
                untraced.append(f"{check['text']} ({check['id']})")
            if row["state"] != "approved" and named:
                unapproved.append(f"{check['id']} of {row['label']}, which is not signed off")
    lines = ["UI checks with no task: " + ("none" if not untraced else "; ".join(untraced))]
    if unapproved:
        lines.append("Tasks for screens with no yes: " + "; ".join(unapproved))
    return {"ok": not untraced and not unapproved, "untraced": untraced, "unapproved": unapproved,
            "ui_tasks": ui_kind, "lines": lines}


# ---------- command line ----------

def _args(argv: list[str]) -> dict:
    out = {"yes": False, "text_flag": False}
    i = 0
    while i < len(argv):
        token = argv[i]
        if token == "--yes":
            out["yes"] = True
            i += 1
            continue
        if token == "--text" and (i + 1 >= len(argv) or argv[i + 1].startswith("--")):
            out["text_flag"] = True
            i += 1
            continue
        if token.startswith("--") and i + 1 < len(argv):
            out[token[2:].replace("-", "_")] = argv[i + 1]
            i += 2
            continue
        i += 1
    return out


def _bind_vendor(argv):
    """1.201.0: --vendor codex prints $crav1- commands. The default stays /."""
    if "--vendor" not in argv and not any(str(item).startswith("--vendor=") for item in argv):
        return argv
    path = Path(__file__).resolve().parents[2] / "crav1-update-kit" / "scripts" / "vendor_prefix.py"
    if not path.is_file():
        print("Refused: --vendor needs the vendor table.", file=sys.stderr)
        raise SystemExit(2)
    spec = importlib.util.spec_from_file_location("crav1_vendor_prefix", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.install_from_argv(argv)


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        _emit(__doc__ or "")
        return 0
    argv = _bind_vendor(argv)
    command, args = argv[0], _args(argv[1:])
    if not args.get("root"):
        return _fail("missing", f"{command} needs --root <spec-folder>")
    root = Path(args["root"])
    if not (root / "spec.md").is_file():
        return _fail("spec", f"no spec.md in {root}")
    if command == "status":
        _emit(status(root))
        return 0
    if command == "gate":
        result = gate(root)
        _emit(gate_text(result) if args["text_flag"] else result)
        return 0
    if command == "sync":
        today = args.get("today") or date.today().isoformat()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", today):
            return _fail("today", "--today is YYYY-MM-DD")
        if not args["yes"]:
            plan = sync_plan(root, args.get("person"))
            plan.pop("status", None)
            _emit({**plan, "wrote": [], "note": "Nothing written. Pass --yes after the user's yes."})
            return 0
        result = apply_sync(root, args.get("person"), today)
        result.pop("status", None)
        _emit(result)
        return 0 if result.get("ok") else 2
    if command == "touches":
        if "text" not in args:
            return _fail("missing", "touches needs --text \"<the change>\"")
        _emit(touches(root, args["text"]))
        return 0
    if command == "trace":
        _emit(trace(root))
        return 0
    return _fail("command", f"unknown command {command}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
