#!/usr/bin/env python3
"""Kit lint (no model, seconds). Usage: kit-lint.py [kit-dir]
- every relative Markdown link in a skill (SKILL.md and references/) points at a file that exists
- each SKILL.md has front matter with name == its folder and a description that says when to use it
- docs/reference/skills.yaml lists exactly the skill folders, each with a numeric prompt_budget
- the .cursor, .claude and plugin copies of each skill have the same files
"""
import os, re, sys, glob
kit = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("KIT_DIR", "."))
errs = []
SK = os.path.join(kit, ".cursor", "skills", "crav1")
skills = sorted(d for d in os.listdir(SK) if os.path.exists(os.path.join(SK, d, "SKILL.md")))
for s in skills:
    root = os.path.join(SK, s)
    text = open(os.path.join(root, "SKILL.md"), encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m: errs.append(f"{s}: SKILL.md has no front matter"); continue
    fm = m.group(1)
    name = re.search(r"^name:\s*(\S+)", fm, re.M)
    if not name or name.group(1).strip("'\"") != s: errs.append(f"{s}: front matter name is {name.group(1) if name else 'missing'}, not the folder name")
    desc = re.search(r"^description:[ \t]*(.*(?:\n[ \t]+.*)*)", fm, re.M)
    if not desc or len(desc.group(1).strip()) < 40: errs.append(f"{s}: description missing or under 40 characters")
    elif not re.search(r"\b(use|when|after|before)\b", desc.group(1), re.I): print(f"WARN  {s}: description does not say when to use it")
    for md in [os.path.join(root, "SKILL.md")] + glob.glob(os.path.join(root, "references", "**", "*.md"), recursive=True):
        body = re.sub(r"```.*?```", "", open(md, encoding="utf-8").read(), flags=re.S)
        body = re.sub(r"`[^`\n]*`", "", body)
        for tgt in re.findall(r"\]\(([^)\s]+)\)", body):
            if re.match(r"^(https?:|mailto:|#|<|\{)", tgt) or "<" in tgt: continue
            p = os.path.normpath(os.path.join(os.path.dirname(md), tgt.split("#")[0]))
            if not os.path.exists(p) and not os.path.exists(os.path.join(root, tgt.split("#")[0])): errs.append(f"{os.path.relpath(md, kit)}: broken link {tgt}")
y = os.path.join(kit, "docs", "reference", "skills.yaml")
if os.path.exists(y):
    names, cur, budgets = [], None, {}
    for line in open(y, encoding="utf-8"):
        m = re.match(r"^- name: (\S+)", line)
        if m: cur = m.group(1); names.append(cur); continue
        m = re.match(r"^  prompt_budget: (\S+)", line)
        if m and cur: budgets[cur] = m.group(1)
    for n in sorted(set(skills) - set(names)): errs.append(f"skills.yaml: no entry for skill {n}")
    agents = {os.path.basename(a)[:-3] for a in glob.glob(os.path.join(kit, ".cursor", "agents", "**", "*.md"), recursive=True)}
    for n in sorted(set(names) - set(skills) - agents): errs.append(f"skills.yaml: entry {n} has no skill folder")
    for n in names:
        if n in budgets and not budgets[n].isdigit(): errs.append(f"skills.yaml: {n} prompt_budget is not a number ({budgets[n]})")
else: errs.append("docs/reference/skills.yaml missing")
def files(r): return sorted(os.path.relpath(os.path.join(a, f), r) for a, _, fs in os.walk(r) for f in fs if "__pycache__" not in a)
for other in (os.path.join(kit, ".claude", "skills", "crav1"), os.path.join(kit, "plugins", "crav1", "skills")):
    if not os.path.isdir(other): continue
    for s in skills:
        if not os.path.isdir(os.path.join(other, s)): errs.append(f"{os.path.relpath(other, kit)}: no copy of {s}"); continue
        a, b = set(files(os.path.join(SK, s))), set(files(os.path.join(other, s)))
        if a != b: errs.append(f"{os.path.relpath(other, kit)}/{s}: files differ ({', '.join(sorted(a ^ b)[:3])})")
for e in errs: print("FAIL  " + e)
print(f"kit lint: {len(skills)} skills, {len(errs)} problem(s)")
sys.exit(1 if errs else 0)
