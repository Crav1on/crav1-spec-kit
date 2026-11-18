#!/usr/bin/env python3
"""Find where a technology shows up in the specs, check an answer's shape, and save a note (1.192.0).

Used by /crav1-explain-tech. Read-only except `save --yes`.

  route   --text "<words after the command>"       parse tech, scope, deeper, save
  find    --tech "<name>" [--scope <slug|topic|architecture>] [--alias <name>]...
  check   --input <answer.md> [--deeper] [--no-link-check]
  save    --tech "<name>" --spec <slug|architecture> --input <entry.json> [--yes]
  ending  --tech "<name>" [--deeper] [--not-in-spec] [--spec <slug>] [--saved <path>]

Global: --root <specs repo> (default: current folder). Exit 2 means refused; nothing was written.
"""
from __future__ import annotations

import argparse
import datetime as _dt
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

CHOICE_WORDS = ("deeper", "save")
SHORT_WORDS = (150, 250)
DEEPER_WORDS = (300, 900)
SECTIONS = ["What it is", "How it works", "Where it shows up", "Why it is used", "Main tradeoff", "One alternative"]
DEEPER_SECTIONS = SECTIONS[:5] + ["How it fits with the rest of the spec", "One alternative"]
ARCH = "docs/architecture"
DESIGNS = "docs/architecture/designs"  # read-only; a design topic mention is shown as not decided
SKIP_PARTS = {"_template", "inputs", "_compare", ".git", "node_modules"}
OWNER_LINE = re.compile(r"^\s*(?:[-*]\s+)?(?:Deciders|Owner|Owners|Decided by|Approver)s?:\s*(.+)$", re.I)


class Refused(Exception):
    pass


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "tech"


def anchor(heading: str) -> str:
    """GitHub-style heading anchor."""
    h = heading.strip().lower()
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def tech_pattern(names: list[str]) -> re.Pattern:
    """'Private Link' also matches private-link, PrivateLink and private_link."""
    alts = []
    for name in names:
        words = [w for w in re.split(r"[^A-Za-z0-9]+", name) if w]
        if words:
            alts.append(r"[\s\-_]?".join(re.escape(w) for w in words))
    if not alts:
        raise Refused("name the technology, for example: Service Bus")
    return re.compile(r"(?<![A-Za-z0-9])(?:" + "|".join(alts) + r")(?![A-Za-z0-9])", re.I)


def parse_route(text: str) -> dict:
    """[deeper] [save] <technology> [in <spec or topic>]"""
    words = text.split()
    deeper = "deeper" in words
    save = "save" in words
    rest = [w for w in words if w not in CHOICE_WORDS]
    scope = ""
    if "in" in rest[1:]:
        i = len(rest) - 1 - rest[::-1].index("in")
        if i > 0 and i < len(rest) - 1:
            scope, rest = " ".join(rest[i + 1:]), rest[:i]
    tech = " ".join(rest).strip()
    if not tech:
        raise Refused("missing technology. Name one, for example: /crav1-explain-tech Service Bus")
    return {"tech": tech, "scope": scope, "deeper": deeper, "save": save}


def _kind(rel: str) -> str:
    parts = rel.split("/")
    if rel.startswith(DESIGNS + "/"):
        return "design topic"
    if "adr" in parts:
        return "ADR"
    if rel.startswith("docs/specs/"):
        return {"spec.md": "spec", "plan.md": "plan", "tasks.md": "tasks", "notes.md": "notes"}.get(parts[-1], "spec file")
    if rel.startswith(ARCH + "/"):
        return "architecture spec"
    if rel.startswith("docs/system/"):
        return "system notes"
    return "doc"


def scope_folders(root: Path, scope: str) -> list[Path]:
    if not scope:
        return [root / "docs/specs", root / ARCH, root / "docs/system"]
    s = slugify(scope)
    if s == "architecture":
        return [root / ARCH]
    for p in (root / "docs/specs" / s, root / DESIGNS / s):
        if p.is_dir():
            return [p]
    known = sorted(p.name for p in (root / "docs/specs").glob("*") if p.is_dir() and not p.name.startswith("_"))
    topics = sorted(p.name for p in (root / DESIGNS).glob("*") if p.is_dir() and not p.name.startswith("_"))
    raise Refused(f"no spec or design topic named {scope}. Specs: {', '.join(known) or 'none'}; "
                  f"design topics: {', '.join(topics) or 'none'}; or architecture")


def md_files(folders: list[Path]) -> list[Path]:
    out = []
    for f in folders:
        if f.is_dir():
            out += [p for p in sorted(f.rglob("*.md")) if not (set(p.relative_to(f).parts) & SKIP_PARTS)]
    return out


def headings(lines: list[str]) -> list[tuple[int, str]]:
    out, fence = [], False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fence = not fence
        elif not fence and (m := re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)):
            out.append((i, m.group(1)))
    return out


def find(root: Path, tech: str, scope: str = "", aliases: list[str] | None = None, limit: int = 40) -> dict:
    pat = tech_pattern([tech] + list(aliases or []))
    mentions, files, owners = [], {}, []
    for path in md_files(scope_folders(root, scope)):
        rel = path.relative_to(root).as_posix()
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        heads = headings(lines)
        hit_here = False
        for i, line in enumerate(lines):
            if not pat.search(line):
                continue
            hit_here = True
            files[rel] = files.get(rel, 0) + 1
            sec = [h for h in heads if h[0] <= i]
            title = sec[-1][1] if sec else ""
            link = f"{rel}#{anchor(title)}" if title and sec[-1][0] != 0 else rel
            mentions.append({"path": rel, "line": i + 1, "section": title, "link": link, "kind": _kind(rel),
                             "decided": not rel.startswith(DESIGNS + "/"), "text": line.strip()[:200]})
        if hit_here:
            owners += _owners(root, rel, lines)
    by_spec: dict[str, int] = {}
    for rel, n in files.items():
        parts = rel.split("/")
        key = parts[2] if rel.startswith("docs/specs/") else ("architecture" if rel.startswith(ARCH + "/") and not rel.startswith(DESIGNS) else "")
        if key:
            by_spec[key] = by_spec.get(key, 0) + n
    save_to = max(sorted(by_spec), key=lambda k: by_spec[k]) if by_spec else ""
    seen, uniq = set(), []
    for o in owners:
        if (o["who"], o["source"]) not in seen:
            seen.add((o["who"], o["source"]))
            uniq.append(o)
    return {"tech": tech, "scope": scope or "all specs", "in_spec": bool(mentions), "count": len(mentions),
            "files": [{"path": p, "kind": _kind(p), "mentions": n} for p, n in files.items()],
            "mentions": mentions[:limit], "more": max(0, len(mentions) - limit), "owners": uniq,
            "save_to": save_to, "notes_file": notes_path(save_to) if save_to else ""}


def _owners(root: Path, rel: str, lines: list[str]) -> list[dict]:
    """Who has the facts: Deciders/Owner lines in the file, and the spec's Approval needed names."""
    out = []
    for i, line in enumerate(lines):
        if (m := OWNER_LINE.match(line)) and m.group(1).strip() not in ("", "-", "<names>"):
            out.append({"who": m.group(1).strip(), "source": f"{rel}:{i + 1}"})
    if rel.startswith("docs/specs/"):
        spec = root / "/".join(rel.split("/")[:3]) / "spec.md"
        if spec.is_file():
            sl = spec.read_text(encoding="utf-8", errors="replace").splitlines()
            in_sec = False
            for i, line in enumerate(sl):
                if line.startswith("## "):
                    in_sec = line.strip() == "## Approval needed"
                    continue
                if in_sec and line.strip().startswith(("-", "*")) and len(line.strip()) > 2:
                    out.append({"who": line.strip()[1:].strip(), "source": f"{spec.relative_to(root).as_posix()}:{i + 1}"})
    return out


def notes_path(spec: str) -> str:
    return f"{ARCH}/notes.md" if spec == "architecture" else f"docs/specs/{spec}/notes.md"


def _body(text: str) -> str:
    """The answer without its Run next block and any card after it."""
    cut = re.search(r"^Run next", text, re.M)
    return text[:cut.start()] if cut else text


def count_words(text: str) -> int:
    t = re.sub(r"\]\([^)]*\)", "]", text)          # links: keep the text, drop the target
    t = re.sub(r"[#*_`>|]", " ", t)
    return len(re.findall(r"[A-Za-z0-9][\w'’.-]*", t))


def check(text: str, deeper: bool = False, root: Path | None = None) -> dict:
    body = _body(text)
    n = count_words(body)
    lo, hi = DEEPER_WORDS if deeper else SHORT_WORDS
    problems = []
    if not lo <= n <= hi:
        problems.append(f"{n} words; a {'deeper' if deeper else 'short'} answer is {lo} to {hi}")
    want = DEEPER_SECTIONS if deeper else SECTIONS
    pos = []
    for label in want:
        m = re.search(rf"^(?:#+\s+|\*\*){re.escape(label)}", body, re.M | re.I)
        if not m:
            problems.append(f"missing section: {label}")
        else:
            pos.append(m.start())
    if pos != sorted(pos):
        problems.append("sections are out of order: " + ", ".join(want))
    if re.search(r"^Next:", text, re.M):
        problems.append("a Next: line; endings use Run next")
    if "Run next" not in text:
        problems.append("no Run next block")
    if root is not None:
        for target in re.findall(r"\]\(([^)\s]+)\)", body):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            path, _, frag = target.partition("#")
            f = root / path
            if not f.is_file():
                problems.append(f"link to a file that does not exist: {target}")
            elif frag and frag not in {anchor(h) for _, h in headings(f.read_text(encoding='utf-8').splitlines())}:
                problems.append(f"link to a section that does not exist: {target}")
    return {"words": n, "ok": not problems, "problems": problems}


def _check_link(root: Path, link: str) -> None:
    path, _, frag = link.partition("#")
    f = root / path
    if not path.startswith("docs/") or not f.is_file():
        raise Refused(f"link {link} is not a file in the specs; a note only links what was read")
    if frag and frag not in {anchor(h) for _, h in headings(f.read_text(encoding="utf-8").splitlines())}:
        raise Refused(f"link {link} names a section that is not in {path}")


def plan_save(root: Path, tech: str, spec: str, entry: dict, today: str) -> dict:
    spec = slugify(spec)
    if spec != "architecture" and not (root / "docs/specs" / spec / "spec.md").is_file():
        if (root / DESIGNS / spec).is_dir():
            raise Refused(f"{spec} is a design topic; save a note there with /crav1-design-architecture note {spec}")
        raise Refused(f"no spec named {spec} (docs/specs/{spec}/spec.md), and not architecture")
    if spec == "architecture" and not (root / ARCH / "spec.md").is_file():
        raise Refused("there is no docs/architecture/spec.md")
    summary = (entry.get("summary") or "").strip()
    if not summary:
        raise Refused("the note needs the short explanation as summary")
    unknown = set(entry) - {"summary", "links"}
    if unknown:
        raise Refused(f"unknown keys in the note input: {', '.join(sorted(unknown))}")
    links = list(entry.get("links") or [])
    for link in links:
        _check_link(root, link)
    rel = notes_path(spec)
    target = root / rel
    head = f"### {tech.strip()} ({today})"
    old = target.read_text(encoding="utf-8") if target.is_file() else ""
    if head in old:
        raise Refused(f"{rel} already has a note for {tech} from {today}")
    lines = [head, "", summary]
    if links:
        lines += [""] + [f"- [{l}]({os.path.relpath(root / l.partition('#')[0], target.parent).replace(os.sep, '/')}"
                         + (f"#{l.partition('#')[2]}" if "#" in l else "") + ")" for l in links]
    block = "\n".join(lines) + "\n"
    if not old:
        title = "Architecture" if spec == "architecture" else spec
        new = f"# Notes: {title}\n\n## Technology notes\n\n{block}"
    elif not re.search(r"^## Technology notes\s*$", old, re.M):
        new = old.rstrip("\n") + "\n\n## Technology notes\n\n" + block
    else:
        m = re.search(r"^## Technology notes\s*$", old, re.M)
        nxt = re.search(r"^## ", old[m.end():], re.M)
        end = m.end() + nxt.start() if nxt else len(old)
        new = old[:end].rstrip("\n") + "\n\n" + block + ("\n" + old[end:] if nxt else "")
    return {"path": rel, "created": not old, "entry": block, "new": new}


def ending(tech: str, deeper: bool = False, not_in_spec: bool = False, spec: str = "", saved: str = "") -> str:
    t = tech.strip()
    out = ["Run next:"]
    if saved:
        out += [f"The {t} note is saved in {saved} and not committed.", "",
                "Commit the note:", "`/crav1-finalize-commit`", "", "Uncommitted: 1 file."]
        return "\n".join(out) + "\n"
    if not_in_spec:
        out += [f"{t} is not in the specs, so the answer above is general.", "",
                f"Ask for research on {t}:", f"`/crav1-show-or-ask-open-questions ask research {slugify(t)}`"]
        return "\n".join(out) + "\n"
    out.append("Nothing else is needed for this answer." if deeper else f"This was the short answer on {t}.")
    if not deeper:
        out += ["", f"Explain {t} in more depth:", f"`/crav1-explain-tech deeper {t}`"]
    if spec:
        out += ["", f"Save this explanation to the {spec} notes:", f"`/crav1-explain-tech save {t} in {spec}`"]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("route")
    r.add_argument("--text", required=True)
    f = sub.add_parser("find")
    f.add_argument("--tech", required=True)
    f.add_argument("--scope", default="")
    f.add_argument("--alias", action="append", default=[])
    c = sub.add_parser("check")
    c.add_argument("--input", required=True)
    c.add_argument("--deeper", action="store_true")
    c.add_argument("--no-link-check", action="store_true")
    s = sub.add_parser("save")
    s.add_argument("--tech", required=True)
    s.add_argument("--spec", required=True)
    s.add_argument("--input", required=True)
    s.add_argument("--yes", action="store_true")
    e = sub.add_parser("ending")
    e.add_argument("--tech", required=True)
    e.add_argument("--deeper", action="store_true")
    e.add_argument("--not-in-spec", action="store_true")
    e.add_argument("--spec", default="")
    e.add_argument("--saved", default="")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    try:
        if a.cmd == "route":
            res = parse_route(a.text)
        elif a.cmd == "find":
            res = find(root, a.tech, a.scope, a.alias)
        elif a.cmd == "check":
            res = check(Path(a.input).read_text(encoding="utf-8"), a.deeper, None if a.no_link_check else root)
        elif a.cmd == "save":
            plan = plan_save(root, a.tech, a.spec, json.loads(Path(a.input).read_text(encoding="utf-8")), _dt.date.today().isoformat())
            res = {"path": plan["path"], "created": plan["created"], "entry": plan["entry"], "written": []}
            if not a.yes:
                res["card"] = {"question": f"Save the {a.tech} explanation to {plan['path']}?", "words": ["yes", "not-now"],
                               "recommended": "yes",
                               "options": [{"word": "yes", "label": "Save it (Recommended)", "action": f"append a dated Technology notes entry to {plan['path']}"},
                                           {"word": "not-now", "label": "Not now", "action": "write nothing; the answer stays in the chat"}]}
            else:
                target = root / plan["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(plan["new"], encoding="utf-8")
                res["written"] = [plan["path"]]
        else:
            sys.stdout.write(ending(a.tech, a.deeper, a.not_in_spec, a.spec, a.saved))
            return 0
    except Refused as exc:
        sys.stderr.write(f"Refused: {exc}\n")
        return 2
    json.dump(res, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
