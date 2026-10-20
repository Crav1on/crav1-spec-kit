# crav1-bundle-to-specs: landscape

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Landscape

**Branch first** if a git repo with commits exists. Follow `/crav1-create-feature-branch` (drop-in: `.claude/skills/crav1-create-feature-branch/SKILL.md`; plugin: sibling `skills/crav1-create-feature-branch/SKILL.md`). Intake uses one branch for the dump (landscape kebab or `system`). Do not write `docs/system/` until the branch choice is done or skipped.

Write `docs/system/` from this skill’s `assets/` (same shape as `docs/system/_template/`):

| File | What |
| --- | --- |
| `landscape.md` | What this is, v0 vs later, bulk `A#`s, how the parts connect (one line per connection the intake already states), feature index (fill paths after workers) |
| `repos.md` | 1–N repos: purpose, proposed vs exists, URL when they have one, and the `Synced at` column. Fill that cell only for a repo this run read as a whole, as under **Synced at** below. Add the `Work items go to` column when it is missing; leave its cells empty. Never fill a home here: the first Azure Boards skill that needs one asks ([work-item-homes.md](../../crav1-ado-sync/branches/push-features/references/work-item-homes.md)). |
| `diagrams.md` | System context across repos (follow `references/diagrams.md`) |
| `glossary.md` | From `assets/glossary.md`, in this same pass. See the glossary rules below. |
| `adr/` | Cross-cutting choices only (`assets/adr.md`). Hunches with no alternative → constraints on `landscape.md`, not ADRs. Status `proposed` until they accept |

**Glossary.** `glossary.md` is part of the landscape, not a feature spec. When `docs/system/` is missing, write it with the other landscape files. When `docs/system/` already exists, do not rewrite `repos.md` or existing ADRs except the `Synced at` cell of a repo this run read as a whole, and do not rewrite a short-description sentence, a diagram node, a diagram edge, or a connection line that is already there. If `glossary.md` is missing, write only that file. If it exists, append only new rows. The feature index and the picture update are filled in Index, not in that gap fill. Source is the intake already in hand. Do not run an extra interview. Do not invent terms, expansions, or definitions. Do not write TBD or to be decided. A row is only a word or abbreviation that intake already uses. When that same intake already says the expansion or meaning, put that text in Meaning. When it never says what the word means, set Meaning to `to be researched`. Skip ordinary English. A code identifier is not a row unless the intake already treats that word as a term. Write the file even when it has no rows. Do not rewrite, reorder, or edit existing rows. Do not change a Meaning cell that already has text.

No `tasks.md` here. No `git init`, remotes, or application code unless they **explicitly** asked in this chat to create repos.

**Synced at.** Where this run reads a repo, record the commit it actually read. Notes alone are not a repo read. `Synced at` is `<branch>@<short sha>, <date>`. A repo may list several branches, separated by `; `. Example: `main@abc1234, 2026-10-07; develop@def5678, 2026-10-06`. The branch is the branch that was read. The short sha is seven characters. The date is the date of that read, `YYYY-MM-DD`.

When this run reads a whole repo, set that repo's `Synced at` cell to the branch and commit actually read. When that branch is already listed, replace that branch's entry. Leave every other branch in the cell. Touch only the repos this run read. Do not change Purpose, Status, URL, or Boundaries. When the column is missing, add it. Other repos' new cells stay empty. Do not write a slice `Synced at` line for a repo this run read as a whole. Workers do not edit `repos.md`. The parent writes that cell.

When this run reads only one slice, do not touch the repo column. Write or update a line in that slice's `spec.md`, after the title and before the first heading: `Synced at: <repo> <branch>@<short sha>, <date>`. One line per repo. That line has one entry per branch read, separated by `; `, for example `Synced at: orders-api feat/orders-retry@155b5c4, 2026-10-19; develop@00344be, 2026-10-15`. When the branch read already has an entry, replace only that entry; a new branch adds an entry at the end. Leave the other entries, a `(dropped)` on them, and other repos' `Synced at` lines. When a worker writes that spec, pass the repo, branch, short sha, and date. The worker writes the line and does not read git to invent one.

Do not stamp a repo or a slice this run did not read. An empty cell stays empty. A consumer measuring drift uses the older of the repo column and the slice line, for each branch its own entry, and an empty value means unknown, so fall back to spec file commit dates.
