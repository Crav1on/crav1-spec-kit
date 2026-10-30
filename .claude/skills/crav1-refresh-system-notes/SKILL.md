---
name: crav1-refresh-system-notes
description: >-
  Use when something was added and the docs/system/ picture (description,
  diagram, connections) should catch up, or when a docs/research/ note was
  updated and its stale points need checking. Adds only what is new. Does not
  design or build.
disable-model-invocation: true
icon: refresh-cw
color: green
---

# Keep current

You update the picture in `docs/system/` when something was added. You add what is new to the short description, the diagram, and how the parts connect. You do not rewrite what is already there. You do not design the change. You do not build it.

This is cross-cutting. It is not its own lane. It does not move work into Specify, Plan, or Build.

This is not `/crav1-existing-to-specs`. That command reads the repos the user named and writes one architecture spec the lanes can extend, plus these notes. Do not do that job. Do not invent an architecture from code. Do not create a slug.

Spark, ideas, intake, match, match-dump, and add-to-spec run this picture update in the same pass that adds a glossary row. They follow [references/picture.md](references/picture.md) (drop-in: `.claude/skills/crav1-refresh-system-notes/references/picture.md`; plugin: this skill’s `references/picture.md`). They do not rewrite existing glossary rows. This command does not write glossary rows.

## From /crav1-read-environment

When `/crav1-read-environment` hands a confirmed system section, run only [references/handoff-read-environment.md](references/handoff-read-environment.md), then stop.

## When the folder is missing

Run only when `docs/system/` already exists. If that folder is missing, stop. Point at the command that creates it. Do not seed the folder. Do not write the picture to fill the gap.

Point at one command when what they brought makes it obvious. Do not run it.

- One or two sentences: `/crav1-spark-to-spec`
- A pile of ideas: `/crav1-ideas-to-spec`
- Mixed files or several features: `/crav1-bundle-to-specs`
- Repos plus a dump: `/crav1-existing-to-specs`
- Named repos and no dump: `/crav1-existing-to-specs`

If they brought none of those, name those five commands and stop.

A caller that does not seed `docs/system/` (match-dump, add-to-spec) does nothing about the picture when that folder is missing.

## What was added

Alone: read each `docs/specs/<slug>/spec.md` (skip `_template`). What is new is a part or a connection that spec states and the picture does not. Skip a sentence marked inferred. If no spec folder exists, say so, write nothing, and stop. Do not invent the picture from the repo.

From a caller: what is new is only what that pass added. Do not open a second interview. Do not scan unrelated specs to redesign the paragraph.

A part or a connection the source does not state is not new.

## Pointed at a research note

When the user replaced a file under `docs/research/` and pointed this command at it, follow [references/research-note.md](references/research-note.md). It does not replace the picture update.

## Synced at

Reading spec files is not reading a repo. The alone path does not set `Synced at` from those files, and it does not stamp the docs repo because the picture was updated.

Each `Synced at` line is one repo and branch: the branch that was read, the seven-character short sha, and the date of that read (`YYYY-MM-DD`). Format and sorted place (repo, then branch) follow `crav1-add-to-spec` `references/merge-safe.md`. When that repo and branch already have a line, replace only that line. Leave every other line, and a `(dropped)` on them.

When this run reads a whole repo, set its line in the `## Synced at` section of `docs/system/repos.md`, for example `- orders-api main@abc1234, 2026-10-07`. That line is the only edit to `repos.md`. Touch only the repos this run read. Do not change Purpose, Status, URL, or Boundaries. When the section is missing, add it after the table. When that repo has no row, do not add one. Do not create `repos.md` when it is missing. Do not write a slice line for a repo this run read as a whole.

When this run reads only one slice, do not touch `repos.md`. Write or update that slice's `Synced at: <repo> <branch>@<short sha>, <date>` line in `spec.md`, after the title and before the first heading. That line is the only edit to `spec.md`.

When a branch's recorded SHA no longer exists or is not an ancestor of the branch tip, say `<branch>: branch rewritten since last read (was <sha>)` and measure drift for that branch from its fork point, as `crav1-add-to-spec` `references/branches.md` says (drop-in: `.claude/skills/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`). Never stop with an error for it. A code repo other than the open checkout is read from `../<repo>` under the same file's **Sibling checkout**.

Do not stamp a repo or a slice this run did not read. A repo or branch with no line keeps no line. A consumer measuring drift uses, for each repo and branch, the older of the repo line and the slice line, and no line means unknown, so fall back to spec file commit dates.

## Write

Follow [references/picture.md](references/picture.md). Three places only:

- the short description in `docs/system/landscape.md`
- the context diagram in `docs/system/diagrams.md`
- `## How the parts connect` in `docs/system/landscape.md`

Do not add a feature-index row. Callers that own the index still add that row themselves. Do not edit `glossary.md`.

## Stop

Do not plan. Do not implement. Do not commit. Do not run `/crav1-explain-existing-system`, `/crav1-plan-from-spec`, `/crav1-spark-to-spec`, or `/crav1-finalize-commit`. Do not clear a stale research mark except as `references/research-note.md` says. Do not ask the user whether the update resolves it.

Output only:

- What was added to the picture (file, and the sentence, node, edge, or connection line), or that the picture is current
- `Synced at` line in `repos.md` or slice line written, or that none was written
- Research: the short summary of what was cleared, narrowed, and routed where, each open question from the updated note and where it went, and when an older mark had no points, or that this run was not pointed at a research note
- Next: `/crav1-finalize-commit` when a file changed (no push). When nothing was written, name no command. Do not run it.

## Style

Be concise. Add the smaller line. Do not fill gaps with an architecture you invented.
