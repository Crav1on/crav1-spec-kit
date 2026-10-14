#!/usr/bin/env python3
"""Generate the kit order from docs/reference/workflow.yaml.

Writes docs/reference/workflow.md, the order block in .cursor/rules/crav1.mdc,
and every `you_run_next` value in docs/reference/skills.yaml.

  scripts/gen-workflow.py          write them
  scripts/gen-workflow.py --check  exit non-zero on drift

--check also fails when a route names a skill that does not exist, when a
skill in skills.yaml has no next steps from the routes, `also_next`, or
`override`, when the help rule is missing from crav1.mdc or its copies, and
when a walkthrough `## After` section names a skill that workflow.yaml
names in no route or `also_next` (an `override`-only skill, or no skill).
After writing, run scripts/gen-skill-docs.py and scripts/sync-crav1-plugin.sh.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WF = ROOT / "docs/reference/workflow.yaml"
WF_MD = ROOT / "docs/reference/workflow.md"
SKILLS = ROOT / "docs/reference/skills.yaml"
MDC = ROOT / ".cursor/rules/crav1.mdc"
RULE_COPIES = [MDC, ROOT / "plugins/crav1/rules/crav1.mdc", ROOT / ".claude/CLAUDE.md"]
START, END = "<!-- crav1-order:start -->", "<!-- crav1-order:end -->"
HELP_RULE = "call `/crav1-help` and quote its answer with its source. Never give an order from memory."


def slash(n: str) -> str:
    return f"/{n}"


def route_next(routes: list[dict]) -> dict[str, list[str]]:
    """Next steps each skill gets from the routes, in route order."""
    out: dict[str, list[str]] = {}

    def add(name: str, items: list[str]) -> None:
        lst = out.setdefault(name, [])
        for i in items:
            if i not in lst:
                lst.append(i)

    for r in routes:
        steps = r["steps"]
        for i, st in enumerate(steps):
            if st.get("loop_to"):
                nxt = [slash(st["loop_to"])]
            else:
                nxt = []
                for later in steps[i + 1:]:
                    label = later.get("as_next")
                    nxt += [label] if label else [slash(s) for s in later["skills"]]
                    if not later.get("optional"):
                        break
            then = st.get("then") or {}
            for name in st["skills"]:
                if name in then:
                    add(name, [slash(s) for s in then[name]])
                else:
                    add(name, nxt)
    return out


def you_run_next(wf: dict, names: list[str]) -> dict[str, list[str]]:
    rn = route_next(wf["routes"])
    also = wf.get("also_next") or {}
    over = wf.get("override") or {}
    out = {}
    for n in names:
        if n in over:
            out[n] = list(over[n])
            continue
        lst = list(rn.get(n, []))
        for a in also.get(n, []):
            if a not in lst:
                lst.append(a)
        out[n] = lst
    return out


def step_names(st: dict) -> str:
    return " or ".join(f"`{slash(s)}`" for s in st["skills"])


def kit_version() -> str:
    import json
    return json.loads((ROOT / "plugins/crav1/.cursor-plugin/plugin.json").read_text(encoding="utf-8"))["version"]


def render_md(wf: dict) -> str:
    o = [
        "# Workflow routes",
        "",
        "<!-- Generated from docs/reference/workflow.yaml by scripts/gen-workflow.py. Do not edit by hand. -->",
        "",
        f"Kit version: {kit_version()}",
        "",
        "This page is the one written source for the order of kit commands. `/crav1-help` answers from it and names the route it used. The `crav1.mdc` order lines and every skill's next step in the [skills reference](skills.md) are generated from the same file, [workflow.yaml](workflow.yaml).",
        "",
        "A route is an ordered list of steps for one situation. A step with more than one command means one of them. An optional step can be skipped when its condition does not hold.",
        "",
        "| Route | When |",
        "| --- | --- |",
    ]
    for r in wf["routes"]:
        o.append(f"| [{r['title']}](#{r['id']}) | {r['when']} |")
    for r in wf["routes"]:
        o += ["", f'<a id="{r["id"]}"></a>', "", f"## {r['title']}", "", r["when"], "", "| Step | Command | When |", "| --- | --- | --- |"]
        for i, st in enumerate(r["steps"], 1):
            when = st["when"]
            if st.get("optional"):
                when = "Optional. " + when
            if st.get("loop_to"):
                when += f" Then back to `{slash(st['loop_to'])}`."
            o.append(f"| {i} | {step_names(st)} | {when} |")
    return "\n".join(o) + "\n"


def order_block(wf: dict) -> str:
    lines = [START]
    for r in wf["routes"]:
        parts = []
        for st in r["steps"]:
            p = " or ".join(s.removeprefix("crav1-") for s in st["skills"])
            if st.get("optional"):
                p += " (optional)"
            parts.append(p)
        lines.append(f"- {r['title']}: " + " → ".join(parts) + ".")
    lines.append(
        "- The complete skills (complete-task, complete-tasks, complete-features) verify each task inside their worker, then go to open-pr. Full routes: `docs/reference/workflow.md` (kit repo or the plugin's `docs/`)."
    )
    lines.append(END)
    return "\n".join(lines)


def yaml_item(v: str) -> str:
    dumped = yaml.safe_dump([v], allow_unicode=True, width=10_000).strip()
    return dumped  # "- value" with quoting when needed


def rewrite_skills(text: str, nexts: dict[str, list[str]]) -> str:
    blocks = re.split(r"(?m)^(?=- name: )", text)
    out = []
    for b in blocks:
        m = re.match(r"- name: (\S+)", b)
        if m and m.group(1) in nexts:
            vals = nexts[m.group(1)]
            new = "  you_run_next: []\n" if not vals else "  you_run_next:\n" + "".join(f"  {yaml_item(v)}\n" for v in vals)
            b, k = re.subn(r"(?m)^  you_run_next:(?: \[\])?\n(?:  - .*\n)*", new, b, count=1)
        out.append(b)
    return "".join(out)


def rewrite_mdc(text: str, block: str) -> str:
    if START in text and END in text:
        return re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    return text


def after_check(route_skills: set[str]) -> list[str]:
    errs = []
    for f in sorted((ROOT / "docs").glob("from-*.md")):
        m = re.search(r"(?ms)^## After\b.*?(?=^## |\Z)", f.read_text(encoding="utf-8"))
        if not m:
            continue
        for n in sorted(set(re.findall(r"/(crav1-[a-z-]+)", m.group(0)))):
            if n not in route_skills:
                errs.append(f"{f.relative_to(ROOT)}: ## After names /{n}, which docs/reference/workflow.yaml does not name in a route or also_next")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    wf = yaml.safe_load(WF.read_text(encoding="utf-8"))
    skills_text = SKILLS.read_text(encoding="utf-8")
    names = [s["name"] for s in yaml.safe_load(skills_text)["skills"]]
    errs = []

    in_routes = set()
    for r in wf["routes"]:
        for st in r["steps"]:
            for s in st["skills"] + list((st.get("then") or {}).keys()) + ([st["loop_to"]] if st.get("loop_to") else []):
                in_routes.add(s)
                if s not in names:
                    errs.append(f"route {r['id']}: {s} is not a skill in skills.yaml")
    for key in ("also_next", "override"):
        for s in (wf.get(key) or {}):
            if s not in names:
                errs.append(f"{key}: {s} is not a skill in skills.yaml")
    named = set(in_routes)
    named |= set((wf.get("also_next") or {}).keys())
    named.add("crav1-help")  # any After section may point at help for the full order
    for vals in (wf.get("also_next") or {}).values():
        for v in vals:
            m = re.match(r"/(crav1-[a-z-]+)", v)
            if m:
                named.add(m.group(1))
                if m.group(1) not in names:
                    errs.append(f"also_next names /{m.group(1)}, which is not a skill")
    for n in names:
        if n not in in_routes and n not in (wf.get("also_next") or {}) and n not in (wf.get("override") or {}):
            errs.append(f"{n}: in no route, also_next, or override of workflow.yaml")

    nexts = you_run_next(wf, names)
    want = {
        WF_MD: render_md(wf),
        SKILLS: rewrite_skills(skills_text, nexts),
        MDC: rewrite_mdc(MDC.read_text(encoding="utf-8"), order_block(wf)),
    }
    if START not in want[MDC]:
        errs.append(".cursor/rules/crav1.mdc has no crav1-order markers")

    if args.check:
        for p, t in want.items():
            if not p.is_file() or p.read_text(encoding="utf-8") != t:
                errs.append(f"{p.relative_to(ROOT)} is stale; run scripts/gen-workflow.py")
        for p in RULE_COPIES:
            if not p.is_file() or HELP_RULE not in p.read_text(encoding="utf-8"):
                errs.append(f"{p.relative_to(ROOT)} is missing the /crav1-help rule")
        errs += after_check(named)
        for e in errs:
            print(e)
        if errs:
            return 1
        print("Workflow routes, you_run_next, crav1.mdc order, help rule, and After sections match docs/reference/workflow.yaml")
        return 0
    if errs:
        for e in errs:
            print(e)
        return 1
    for p, t in want.items():
        p.write_text(t, encoding="utf-8")
    print("Wrote docs/reference/workflow.md, you_run_next in skills.yaml, and the crav1.mdc order block")
    return 0


if __name__ == "__main__":
    sys.exit(main())
