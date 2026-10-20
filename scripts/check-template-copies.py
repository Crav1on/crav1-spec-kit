#!/usr/bin/env python3
"""Fail when a skill's template copy drifts from the project templates (1.69.1).

Every file under a skill's assets/ in the drop-in tree (.cursor/skills/crav1/) whose
name matches a file in docs/<area>/_template/ must be byte-identical to one of the
templates with that name (spec and system templates may share a name, for example
adr.md and diagrams.md). Copies that are deliberately a different template are listed
in DIFFERENT with the reason. The plugin and Claude Code copies are checked by the
sync scripts, so only the drop-in tree is read here.

Usage: check-template-copies.py
"""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".cursor/skills/crav1"
DIFFERENT = {
    "crav1-bundle-to-specs/assets/spec.md": "the bundle spec adds Repos, Constraints and Assumptions",
    "crav1-existing-to-specs/branches/repos-only/assets/spec.md": "the architecture spec, not a feature spec",
    "crav1-existing-to-specs/branches/repos-and-bundle/assets/spec.md": "a matched slice spec with ## Match",
}
templates = {}
for t in (ROOT / "docs").glob("*/_template/*"):
    if t.is_file(): templates.setdefault(t.name, []).append(t)
errors, checked = [], 0
for f in sorted(SKILLS.glob("**/assets/**/*")):
    if not f.is_file() or f.name not in templates or "crav1-docs" in f.parts: continue
    rel = f.relative_to(SKILLS).as_posix()
    if rel in DIFFERENT: continue
    checked += 1
    body = f.read_bytes()
    if not any(body == t.read_bytes() for t in templates[f.name]):
        errors.append(f"{rel} differs from " + " and ".join(t.relative_to(ROOT).as_posix() for t in templates[f.name]))
for rel in DIFFERENT:
    if not (SKILLS / rel).is_file(): errors.append(f"DIFFERENT names {rel}, which does not exist")
if errors:
    print("Template copies that drifted from docs/*/_template/ (copy the template over, or list the file in DIFFERENT with a reason):")
    print("\n".join("  " + e for e in errors)); sys.exit(1)
print(f"Template copies match docs/*/_template/ ({checked} copies, {len(DIFFERENT)} deliberately different)")
