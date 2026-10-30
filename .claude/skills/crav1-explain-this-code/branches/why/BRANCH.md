# Explain this code: What and why branch

Read only when `SKILL.md` routes here (`what and why`). Moved word for word from `SKILL.md` in 1.106.0; the rules are unchanged. The shared sections in `SKILL.md` still apply. A `references/…` or `assets/…` path is relative to the skill folder, not this branch.

## What and why

Everything in **What it does**, plus the reasons. A reason counts only when a source states it:

- the code itself (a comment, a docstring, a name that says it, an assert, a test that pins it)
- the specs (`docs/specs/<slug>/spec.md`)
- plan decisions (`docs/specs/<slug>/plan.md`)
- system notes (`docs/system/`, including `adr/`)
- commits (`git log` and `git blame` on the lines)

Quote or closely paraphrase, and name the source for each reason. When no source states a reason for a step, say `no stated reason found`. Never invent one, and do not offer a likely reason in its place.
