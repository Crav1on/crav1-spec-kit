---
name: crav1-intake-to-specs
description: >-
  Turn mixed intake (notes, diagrams, screenshots, optional code as context)
  into docs/system/ (including glossary.md) plus one spec slug per v0 feature.
  When that folder exists, write glossary.md if it is missing, or append only
  words that are not already rows. Do not rewrite existing glossary rows. A
  meaning the source does not state is `to be researched`. That same pass
  adds what is new to the short description, the diagram, and how the parts
  connect. Do not rewrite what is already there. Use when 1–N files
  or a dump may imply several features or repos. Do not write application code.
disable-model-invocation: true
icon: layers
color: purple
---

# Intake to specs

You are the **parent**. Partition intake, confirm the map, interview only mushy slices, write `docs/system/`, then delegate **one slug per worker**. Do not implement. Do not specify in your own voice as a substitute for workers when there is more than one feature slug.

This command is a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. Every other skill is a later skill.

One feature and one repo after Map: you may write that slug yourself (ideas-to-spec Write artifacts) **and** still write a thin `docs/system/`. Do not skip the landscape.

Worker: `.claude/agents/crav1-intake-slice-agent.md` (plugin: `agents/crav1-intake-slice-agent.md`). Protocol: this skill’s [references/worker.md](references/worker.md).

Read `references/diagrams.md` before writing landscape diagrams. Read `crav1-ideas-to-spec` `references/formats.md` only when exporting (drop-in: `.claude/skills/crav1-ideas-to-spec/references/formats.md`; plugin: sibling `skills/crav1-ideas-to-spec/references/formats.md`).

## Intake (no required structure)

Everything after `/crav1-intake-to-specs` and every `@` is **intake**. Do not ask them to label folders as intent vs context.

| Kind | Examples | Role |
| --- | --- | --- |
| **Intent** | Notes, briefs, markdown, screenshots, whiteboard photos, diagrams, PDFs, chat blob | Extract slices from this |
| **Context** | Existing app code, other repos, “something like this” | Constraints and patterns; not a second product spec |

Default if they only `@` a codebase and did **not** say extract-as-is: **new system, this code is context.** Extract-as-is is an explicit override; still partition into landscape + feature slugs, never one mega-spec. Named repos and no intake files, when the job is one architecture spec of what the code shows, is `/crav1-repos-to-spec`. Do not partition that job into feature slugs.

A one-liner with no files: tell them `/crav1-spark-to-spec`. A single unstructured pile that is clearly **one** feature and **one** repo: `/crav1-ideas-to-spec` is enough; you may continue here anyway (thin landscape is still required).

## Map (first response, no files yet)

1. Label each `@` **intent** or **context** (they can flip a label).
2. Propose **v0 vs later**.
3. Propose **feature slugs** (each will be `docs/specs/<slug>/`). Prefer cutting hunches not needed to demo v0.
4. Propose **repo map** (1–N): purpose, create vs already exists, what must not cross a repo boundary. Status `proposed` until a URL exists.
5. Publish bulk assumptions **A1…** (program-level only: primary user, system-level v0 demo, shared non-goals, accepted repo boundaries, export format if named, constraints already in the dump).
6. Flag each slug **ready** or **mushy**. Mushy if that slug lacks who/job/outcome, lacks a demoable done-state, contradicts itself, depends on an unaccepted repo split, or is mostly “later” mixed into v0. They may override.
7. Ask **output format(s)** unless already named in intake (`EARS` default if they say use your default). Do not emit every format.

Stop. Confirming the map confirms bulk assumptions unless they edit them. Do not write files. Do not interview ready slugs.

## Mushy interview (still no files; parent only)

Skip this phase if every accepted v0 slug is ready.

Still in this chat. **Never** in workers. Questions **only** for mushy slugs. Do not re-ask landscape questions (system user, system demo, repo boundaries, export format, shared stack). **At most 5 questions per mushy slug.** Prefer options.

If they say “use assumptions” on a mushy slug, it becomes **ready**; leftovers are Open questions in that spec.

Stop until answers exist (or bulk-assume) for every mushy v0 slug you will write.

## Landscape

**Branch first** if a git repo with commits exists. Follow `/crav1-feature-branch` (drop-in: `.claude/skills/crav1-feature-branch/SKILL.md`; plugin: sibling `skills/crav1-feature-branch/SKILL.md`). Intake uses one branch for the dump (landscape kebab or `system`). Do not write `docs/system/` until the branch choice is done or skipped.

Write `docs/system/` from this skill’s `assets/` (same shape as `docs/system/_template/`):

| File | What |
| --- | --- |
| `landscape.md` | What this is, v0 vs later, bulk `A#`s, how the parts connect (one line per connection the intake already states), feature index (fill paths after workers) |
| `repos.md` | 1–N repos: purpose, proposed vs exists, URL when they have one, and the `Synced at` column. Fill that cell only for a repo this run read as a whole, as under **Synced at** below. |
| `diagrams.md` | System context across repos (follow `references/diagrams.md`) |
| `glossary.md` | From `assets/glossary.md`, in this same pass. See the glossary rules below. |
| `adr/` | Cross-cutting choices only (`assets/adr.md`). Hunches with no alternative → constraints on `landscape.md`, not ADRs. Status `proposed` until they accept |

**Glossary.** `glossary.md` is part of the landscape, not a feature spec. When `docs/system/` is missing, write it with the other landscape files. When `docs/system/` already exists, do not rewrite `repos.md` or existing ADRs except the `Synced at` cell of a repo this run read as a whole, and do not rewrite a short-description sentence, a diagram node, a diagram edge, or a connection line that is already there. If `glossary.md` is missing, write only that file. If it exists, append only new rows. The feature index and the picture update are filled in Index, not in that gap fill. Source is the intake already in hand. Do not run an extra interview. Do not invent terms, expansions, or definitions. Do not write TBD or to be decided. A row is only a word or abbreviation that intake already uses. When that same intake already says the expansion or meaning, put that text in Meaning. When it never says what the word means, set Meaning to `to be researched`. Skip ordinary English. A code identifier is not a row unless the intake already treats that word as a term. Write the file even when it has no rows. Do not rewrite, reorder, or edit existing rows. Do not change a Meaning cell that already has text.

No `tasks.md` here. No `git init`, remotes, or application code unless they **explicitly** asked in this chat to create repos.

**Synced at.** Where this run reads a repo, record the commit it actually read. Notes alone are not a repo read. `Synced at` is `<branch>@<short sha>, <date>`. A repo may list several branches, separated by `; `. Example: `main@abc1234, 2026-10-07; develop@def5678, 2026-10-06`. The branch is the branch that was read. The short sha is seven characters. The date is the date of that read, `YYYY-MM-DD`.

When this run reads a whole repo, set that repo's `Synced at` cell to the branch and commit actually read. When that branch is already listed, replace that branch's entry. Leave every other branch in the cell. Touch only the repos this run read. Do not change Purpose, Status, URL, or Boundaries. When the column is missing, add it. Other repos' new cells stay empty. Do not write a slice `Synced at` line for a repo this run read as a whole. Workers do not edit `repos.md`. The parent writes that cell.

When this run reads only one slice, do not touch the repo column. Write or update a line in that slice's `spec.md`, after the title and before the first heading: `Synced at: <repo> <branch>@<short sha>, <date>`. One line per repo. Update the line for that repo. Leave other `Synced at` lines. When a worker writes that spec, pass the repo, branch, short sha, and date. The worker writes the line and does not read git to invent one.

Do not stamp a repo or a slice this run did not read. An empty cell stays empty. A consumer measuring drift uses the older of the repo column and the slice line, and an empty value means unknown, so fall back to spec file commit dates.

## Imported sources

When an intake file is a mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original that will be quoted into a spec, follow the imported-sources convention before the slice specs are written (drop-in: `.claude/skills/crav1-add-to-spec/references/sources.md`; plugin: sibling `skills/crav1-add-to-spec/references/sources.md`). Write each source folder once. Pass each folder path to the worker that quotes it. The worker writes the `Source:` and `Trace:` lines and does not import the file again. Do not commit. A file that is not an imported source does not get a folder.

## Slice specs

Launch **crav1-intake-slice-agent** once per accepted **v0** slug. Later items stay on the landscape as later — do not spec them now.

Pass exactly what [references/worker.md](references/worker.md) lists. Point the worker at this skill’s `assets/spec.md`, `assets/spec-diagrams.md`, and `assets/adr.md`, at `docs/system/` as written, and at ideas-to-spec `references/formats.md` + `references/diagrams.md` (sibling paths above).

Do not interview in workers. Do not pause for Approvals & Execution per slice. Ready slugs may run **in parallel**. Do not start a worker until that slug is ready (or bulk-assumed). Workers must not edit `docs/system/` except you (parent) during Index.

If Map is one feature and one repo, write that slug here using ideas-to-spec Write artifacts plus `## Repos`, `## Constraints`, `## Assumptions`, `## Trace` — still write thin `docs/system/` first.

## Index

After workers return, update `docs/system/landscape.md` feature index: slug → spec path → repos. Do not rewrite slice specs.

**Picture.** After the index, follow [picture.md](../crav1-keep-current/references/picture.md) (drop-in: `.claude/skills/crav1-keep-current/references/picture.md`; plugin: sibling `skills/crav1-keep-current/references/picture.md`). Add what this pass added to the short description, the diagram, and how the parts connect. Do not rewrite a sentence, a diagram node, a diagram edge, or a connection line that is already there. Do not run `/crav1-keep-current` as a second turn. When this pass seeded `docs/system/`, the seed fill of those three is the picture for what the intake already stated; the picture update still adds anything the new specs state that those three do not yet say. Workers do not edit the picture. Do not rewrite existing glossary rows.

Then output only:

- Paths written (`docs/system/`, each `docs/specs/<slug>/`, any source folder `docs/sources/YYYY-MM-DD-<slug>/`, plus any picture lines added)
- Ready vs interviewed slugs
- ADRs (landscape vs slice) vs still open
- 3–5 remaining arguments
- Next:
  - `/crav1-finalize-commit` — put landscape + specs in git (no push). Skip if they will rewrite this dump in the same chat.
  - If they chose `spec/<dump>`: no implement on that branch; PR/merge when they want, then `feat/<slug>` per feature to build
  - then **per slug** `/crav1-architecture-reviewer`, `/crav1-tighten-spec`, `/crav1-plan-from-spec` — not one plan for the universe

Do **not** run `/crav1-finalize-commit` yourself. Prompt it. Workers must not commit.

Then follow [work-item-offer.md](../crav1-draft-commit-message/references/work-item-offer.md) (plugin: sibling `skills/crav1-draft-commit-message/references/work-item-offer.md`) once, for every new spec folder this run created that still has no `work-item.md`. One question lists those slugs. Azure Repos only. Do not ask on GitHub or any other host. Do not ask again in this run if the user skips or does not answer. Slice workers do not ask and do not write `work-item.md`.

Still no application code. Still no `plan.md` unless they asked.

## Later features (tell them; do not do it in this command)

New work is `/crav1-spark-to-spec` or `/crav1-ideas-to-spec` with `@docs/system/` (and related specs). **New slug.** Do not re-run intake. New repo = landscape ADR + `repos.md` row, then the spec, then an index row.

## Style

Be concise. Quote their words when clustering. Prefer cutting scope to adding architecture or repos.
