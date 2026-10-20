# crav1-what-do-we-know-about-this: match

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Match, one pass

One pass. Do not hunt through the whole codebase. Do not open a second search after the first comes back.

Places, in this order when the user did not `@` a path:

- spec titles in `docs/specs/<slug>/spec.md` (skip `_template`)
- `tasks.md` in those folders
- Match quotes (`## Match` in those `spec.md` files)
- `docs/system/`
- `docs/architecture/spec.md`
- `docs/environments/marks.md`
- one exact-name code query, then, only when that exact name misses, one key-word code query

An `@` of a spec folder or a code folder replaces that list. The search stays inside that path. Do not search specs outside a code folder they named. Say that the search stayed in the path.

**Exact name first.** A slug, a spec title, a function name, or a resource name is a whole token. Case-sensitive first. A case-insensitive hit counts only when it is the only hit.

**Key words when the exact name misses.** Match the key words against the same places. Spec titles and Match quotes weigh highest. A glossary row is a word, not a slice. A neighbor name is not a hit.

**One slice clearly wins.** Answer from it (case 1 or case 2) and name the path `docs/specs/<slug>/`.

**Two or more close hits.** List every one, one line each: the path and the title line. Ask which. Use the questions tool when it is available. One option per hit. Do not guess. Do not drop one to keep the list short. Stop until the user picks. Then answer from that slice.

**No slice.** Case 3.

Reading the winning slice is the answer, not a second pass. Read that `spec.md`, `plan.md` and `tasks.md` when they exist, `## Match`, `## Open questions`, and `## Research findings` when that heading is there. Read a `docs/research/` note those findings link to. A stale mark is shown as stale. Follow the readers section of `crav1-add-to-spec` `references/research-stale.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md`; plugin: sibling `skills/crav1-add-to-spec/references/research-stale.md`). Quote the mark. Name the path. Do not treat that research as current. Do not clear the mark. Use the hits the same pass already found in `docs/system/`, `docs/architecture/spec.md`, and `docs/environments/marks.md`.
