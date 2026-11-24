# Retire spec: Retire branch

Read only when `SKILL.md` routes here (`retire`). Moved word for word from `SKILL.md` in 1.106.0; the rules are unchanged. The shared sections in `SKILL.md` still apply. A `references/…` or `assets/…` path is relative to the skill folder, not this branch.

## Retire

1. Move `docs/specs/<slug>/` to `docs/specs/retired/<slug>/`. Create `docs/specs/retired/` when it is missing.
2. Add as the first line of the moved `spec.md`: `Retired: <YYYY-MM-DD>, <reason>`.
3. Leave the pointer at the old path.
4. Remove that slug's row from `## Feature index` in `docs/system/landscape.md`.
5. Search `docs/` (specs, plans, tasks, notes, system notes) for links to the old path or the slug. Do not rewrite them. List each one as `link to fix: <file>:<line>` in the closing message.

Every skill that scans specs skips `docs/specs/retired/`.
