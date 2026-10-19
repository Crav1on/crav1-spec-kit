#!/usr/bin/env python3
"""Generate the marks tables in docs/concepts/data-layout.md from docs/reference/marks.yaml.

  scripts/gen-marks.py          write the tables
  scripts/gen-marks.py --check  exit non-zero on drift

docs/reference/marks.yaml is the single source for every mark and line format
the kit writes in a product repo. --check fails when:

- the generated blocks in data-layout.md differ from marks.yaml,
- an entry is missing a field, has a duplicate id, an unknown group, or a bad version,
- an example does not fully match its `pattern`,
- a skill or agent in written_by or read_by does not exist, or does not mention
  the mark in its files (`mention` regex, default: the literal text of `format`
  before the first `<` or `[`). A skill's files are every .md under
  .cursor/skills/crav1/<skill>/; an agent's file is .cursor/agents/<agent>.md.

After writing, run scripts/sync-crav1-plugin.sh so the crav1-docs copies match.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MARKS = ROOT / "docs/reference/marks.yaml"
LAYOUT = ROOT / "docs/concepts/data-layout.md"
SKILLS_DIR = ROOT / ".cursor/skills/crav1"
AGENTS_DIR = ROOT / ".cursor/agents"

GROUPS = {
    "spec": "`spec.md` lines",
    "open-questions": "Open question marks",
    "research": "Research and stale marks",
    "plan": "`plan.md` and `tasks.md`",
    "system": "`docs/system/`",
    "environments": "`docs/environments/marks.md`",
    "work-items": "`work-item.md`",
    "notes": "Notes and sources",
}
REQUIRED = ["id", "name", "group", "files", "format", "pattern", "examples", "meaning", "written_by", "read_by", "since"]
BLOCKS = {
    "all": ("<!-- crav1-marks:start -->", "<!-- crav1-marks:end -->"),
    "readiness": ("<!-- crav1-readiness:start -->", "<!-- crav1-readiness:end -->"),
}
NOTE = "<!-- Generated from docs/reference/marks.yaml by scripts/gen-marks.py. Do not edit by hand. -->"


def cell(s: str) -> str:
    return s.replace("|", "\\|")


def code(s: str) -> str:
    s = cell(s)
    return f"`` {s} ``" if "`" in s else f"`{s}`"


def where(files: list[str]) -> str:
    out = []
    for f in files:
        path, _, rest = f.partition(" (")
        out.append(code(path) + (f" ({cell(rest)}" if rest else ""))
    return "; ".join(out)


def who(names: list[str]) -> str:
    if not names:
        return "—"
    return ", ".join(f"`/{n}`" if not n.endswith("-agent") else f"`{n}`" for n in names)


def render_all(marks: list[dict]) -> str:
    out = [BLOCKS["all"][0], NOTE, ""]
    for g, title in GROUPS.items():
        rows = [m for m in marks if m["group"] == g]
        if not rows:
            continue
        out += [f"### {title}", "", "| Mark | Format | Where | Written by | Read by | Since |", "| --- | --- | --- | --- | --- | --- |"]
        for m in rows:
            out.append(
                f"| {cell(m['name'])} | {code(m['format'])} | {where(m['files'])} | {who(m['written_by'])} | {who(m['read_by'])} | {m['since']} |"
            )
        out.append("")
    out.append(BLOCKS["all"][1])
    return "\n".join(out)


def render_readiness(marks: list[dict]) -> str:
    out = [BLOCKS["readiness"][0], NOTE, "", "| Mark | Where | Written by | Meaning |", "| --- | --- | --- | --- |"]
    for m in marks:
        if m.get("readiness"):
            fmt = m["format"].strip()
            fmt = fmt[2:] if fmt.startswith("- ") else fmt
            out.append(f"| {code(fmt)} | {where(m['files'])} | {who(m['written_by'])} | {cell(m['meaning'])} |")
    out.append(BLOCKS["readiness"][1])
    return "\n".join(out)


def replace_block(text: str, key: str, block: str) -> str | None:
    start, end = BLOCKS[key]
    if start not in text or end not in text:
        return None
    return re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: block, text, flags=re.S)


def default_mention(fmt: str) -> str:
    lit = re.split(r"[<\[]", fmt, maxsplit=1)[0].strip()
    return re.escape(lit) if lit else ""


def files_of(name: str) -> list[Path] | None:
    d = SKILLS_DIR / name
    if d.is_dir():
        return sorted(d.rglob("*.md"))
    a = AGENTS_DIR / f"{name}.md"
    if a.is_file():
        return [a]
    return None


def validate(marks: list[dict]) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()
    cache: dict[str, str] = {}
    for m in marks:
        mid = m.get("id", "?")
        for f in REQUIRED:
            if f not in m:
                errs.append(f"{mid}: missing field `{f}`")
        if mid in seen:
            errs.append(f"{mid}: duplicate id")
        seen.add(mid)
        if m.get("group") not in GROUPS:
            errs.append(f"{mid}: unknown group {m.get('group')!r}")
        if not re.fullmatch(r"\d+\.\d+\.\d+", str(m.get("since", ""))):
            errs.append(f"{mid}: since must be x.y.z")
        try:
            pat = re.compile(m.get("pattern", ""))
        except re.error as e:
            errs.append(f"{mid}: bad pattern ({e})")
            continue
        if not m.get("examples"):
            errs.append(f"{mid}: needs at least one example")
        for ex in m.get("examples") or []:
            if not pat.fullmatch(ex):
                errs.append(f"{mid}: example does not match its pattern: {ex!r}")
        mention = m.get("mention") or default_mention(m.get("format", ""))
        if not mention:
            errs.append(f"{mid}: set `mention`; the format has no literal text before its first placeholder")
            continue
        mre = re.compile(mention)
        for role in ("written_by", "read_by"):
            for n in m.get(role) or []:
                fs = files_of(n)
                if fs is None:
                    errs.append(f"{mid}: {role} names {n}, which is not a skill folder or agent")
                    continue
                if n not in cache:
                    cache[n] = "\n".join(p.read_text(encoding="utf-8") for p in fs)
                if not mre.search(cache[n]):
                    errs.append(f"{mid}: {role} names {n}, but its files never mention /{mention}/")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    marks = yaml.safe_load(MARKS.read_text(encoding="utf-8"))["marks"]
    errs = validate(marks)
    text = LAYOUT.read_text(encoding="utf-8")
    new = text
    for key, block in (("all", render_all(marks)), ("readiness", render_readiness(marks))):
        r = replace_block(new, key, block)
        if r is None:
            errs.append(f"{LAYOUT.relative_to(ROOT)} has no {BLOCKS[key][0]} markers")
        else:
            new = r
    if args.check:
        if new != text:
            errs.append(f"{LAYOUT.relative_to(ROOT)} is stale; run scripts/gen-marks.py")
        for e in errs:
            print(e)
        if errs:
            return 1
        print(f"Marks tables match docs/reference/marks.yaml ({len(marks)} marks); examples match; every writer and reader mentions its marks")
        return 0
    for e in errs:
        print(e)
    if any("markers" in e for e in errs):
        return 1
    LAYOUT.write_text(new, encoding="utf-8")
    print("Wrote the marks tables in docs/concepts/data-layout.md" + (" (with errors above)" if errs else ""))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
