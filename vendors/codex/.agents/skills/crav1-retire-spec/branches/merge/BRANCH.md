# Retire spec: Merge branch

Read only when `SKILL.md` routes here (`merge`). Moved word for word from `SKILL.md` in 1.106.0; the rules are unchanged. The shared sections in `SKILL.md` still apply. A `references/…` or `assets/…` path is relative to the skill folder, not this branch.

## Merge

**Target.** When the user named a target spec, use it. Do not suggest others.

When no target is named, suggest only specs that are a real fit, which can be none, one, or several. Each suggestion has a reason taken from what was read:

- a shared feature area (the same area or parent in the feature index, or the same title words)
- overlapping requirements (the same requirement, resource, or acceptance line in both specs)
- the same system in `docs/system/landscape.md` (both slices on the same line under `## How the parts connect`)
- links between them (one spec links to the other)

Best fit first, its label ending with ` (Recommended)`. Do not pad the list. A spec with no stated reason is not a fit. When none fits, say `no good merge fit found` and offer park, retire, or convert to note instead. A headless or bot run with no target stops and lists the fits with their reasons, or says `no good merge fit found`.

**Move.** Into the target `spec.md`:

- the content, under the target's matching headings, each block marked `(from <slug>)`
- each open question with its lines, marked `(from <slug>)`
- each decision, marked `(from <slug>)`

Do not rewrite the target's own lines. A requirement that already says the same thing is not copied again; list it as `already in target` in the summary.

Then move the source folder to `docs/specs/retired/<slug>/` with `Merged: <YYYY-MM-DD> into <target slug>, <reason>` as its first line, leave the pointer at the old path, and remove the source's feature-index row. Flag inbound links as in **Retire**.
