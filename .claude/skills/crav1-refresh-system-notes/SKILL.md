---
name: crav1-refresh-system-notes
description: >-
  Update the picture in docs/system/ when something was added: add what is
  new to the short description, the diagram, and how the parts connect,
  and do not rewrite what is there. A whole-repo read sets that repo's
  Synced at cell and touches only those repos; a one-slice read writes the
  slice Synced at line and leaves the column. Does not design or build the
  change. Can run on its own. Spark, ideas, intake, match, and siblings
  that append a glossary row run this same update without rewriting rows.
  Reading named repos into one architecture spec is /crav1-existing-to-specs,
  not this. When pointed at an updated note in docs/research/, checks each
  listed stale point, splits an older mark into its hits, and routes the
  note's open questions whose answer lies outside its owner, without
  asking. Clears the mark when every point is resolved; otherwise narrows
  it and routes each open point.
disable-model-invocation: true
icon: refresh-cw
color: green
---

# Keep current

You update the picture in `docs/system/` when something was added. You add what is new to the short description, the diagram, and how the parts connect. You do not rewrite what is already there. You do not design the change. You do not build it.

This is cross-cutting. It is not its own lane. It does not move work into Specify, Plan, or Build.

This is not `/crav1-existing-to-specs`. That command reads the repos the user named and writes one architecture spec the lanes can extend, plus these notes. Do not do that job. Do not invent an architecture from code. Do not create a slug.

Spark, ideas, intake, match, match-dump, and add-to-spec run this picture update in the same pass that appends a glossary row. They follow [references/picture.md](references/picture.md) (drop-in: `.claude/skills/crav1-refresh-system-notes/references/picture.md`; plugin: this skill’s `references/picture.md`). They do not rewrite existing glossary rows. This command does not write glossary rows.

## From /crav1-read-environment

When `/crav1-read-environment` hands a confirmed system section, run only this section, then stop. That section is the source. Add only what is new to the picture, following [references/picture.md](references/picture.md). Each new sentence, node, edge, or connection line says `Seen in <host> <environment>.` When the line says `shared with prod`, `prod only`, or shape and connections only, keep that label. It does not say the code shows it. A connection is added only when that section says the environment shows it. Do not rewrite a line that is already there. Do not run the alone-read of the specs. Do not open an interview. Do not start Specify, Plan, or Build. If `docs/system/` is missing, write nothing.

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

When the user replaced a file under `docs/research/` and pointed this command at it, follow the clear section of `crav1-add-to-spec` `references/research-stale.md` (drop-in: `.claude/skills/crav1-add-to-spec/references/research-stale.md`; plugin: sibling `skills/crav1-add-to-spec/references/research-stale.md`). Do not ask whether the update resolves the mark. Judge each listed point from the update's text. An older mark with no point lines is not one point. Split it as that file says. Also route the note's own open questions when the answer lies outside the note's owner. That still runs when the mark clears. Clear the mark only when every listed point is resolved, or when an older mark had no points and the update resolves the original quote. Otherwise narrow the mark and route each open point. When the older mark had no points and stays open, leave it as written. Record `Cleared <date>: updated note <path or commit>.` under `## Research findings` only when the mark clears, with one short line per point when the mark had points. Do not commit. Do not send anything. Drafts stay in the chat. This check does not replace the picture update. The picture still follows **Write**. The clear's writes on the note and on `spec.md` are part of this check. A `Synced at` line is not the only edit when this check writes.

## Synced at

Reading spec files is not reading a repo. The alone path does not set `Synced at` from those files, and it does not stamp the docs repo because the picture was updated.

When this run reads a whole repo, set that repo's `Synced at` cell in `docs/system/repos.md`. That cell is the only edit to `repos.md`. `Synced at` is `<branch>@<short sha>, <date>`. A repo may list several branches, separated by `; `. Example: `main@abc1234, 2026-10-07; develop@def5678, 2026-10-06`. The branch is the branch that was read. The short sha is seven characters. The date is the date of that read, `YYYY-MM-DD`. When that branch is already listed, replace that branch's entry. Leave every other branch in the cell. Touch only the repos this run read. Do not change Purpose, Status, URL, or Boundaries. When the column is missing, add it. Other repos' new cells stay empty. When that repo has no row, do not add one. Do not create `repos.md` when it is missing. Do not write a slice `Synced at` line for a repo this run read as a whole.

When this run reads only one slice, do not touch the repo column. Write or update a line in that slice's `spec.md`, after the title and before the first heading: `Synced at: <repo> <branch>@<short sha>, <date>`. That line is the only edit to `spec.md`. One line per repo. That line has one entry per branch read, separated by `; `, for example `Synced at: orders-api feat/orders-retry@155b5c4, 2026-10-19; develop@00344be, 2026-10-15`. When the branch read already has an entry, replace only that entry; a new branch adds an entry at the end. Leave the other entries, a `(dropped)` on them, and other repos' `Synced at` lines.

When a branch's recorded SHA no longer exists or is not an ancestor of the branch tip, say `<branch>: branch rewritten since last read (was <sha>)` and measure drift for that branch from its fork point, as `crav1-add-to-spec` `references/branches.md` says (drop-in: `.claude/skills/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`). Never stop with an error for it. A code repo other than the open checkout is read from `../<repo>` under the same file's **Sibling checkout**.

Do not stamp a repo or a slice this run did not read. An empty cell stays empty. A consumer measuring drift uses the older of the repo column and the slice line, for each branch its own entry, and an empty value means unknown, so fall back to spec file commit dates.

## Write

Follow [references/picture.md](references/picture.md). Three places only:

- the short description in `docs/system/landscape.md`
- the context diagram in `docs/system/diagrams.md`
- `## How the parts connect` in `docs/system/landscape.md`

Do not add a feature-index row. Callers that own the index still add that row themselves. Do not edit `glossary.md`. Do not commit.

## Notes month folders (1.61.0)

Since 1.61.0 notes live in `docs/notes/YYYY-MM/` by source date, with generated indexes. When this run finds notes flat in `docs/notes/` (any `*.md` there other than `index.md`), say so once and recommend the dry run first: `python3 <crav1-add-to-spec skill folder>/scripts/notes_index.py migrate-dry-run`, which prints the planned moves, source fills, and link rewrites and writes nothing (1.62.0). Then name the one-time move: `python3 <crav1-add-to-spec skill folder>/scripts/notes_index.py migrate` (drop-in: `.claude/skills/crav1-add-to-spec/scripts/notes_index.py`; Claude Code: `.claude/skills/crav1-add-to-spec/scripts/notes_index.py`). It moves each note into its month folder by source date (the note's date, else its filename date, else the date git first added it), adds front matter, fills `source` and `source_folder` from each note's own `Source:` lines and list items (`source_folder` is the first `docs/sources/` path, `source` that line; empty when there is none, never guessed; an empty `source_folder` is filled even when `source` is set), rebases every relative link inside a moved note (folders, any file type, trailing slash, anchors; URLs and root-style paths stay), rewrites every markdown link to a moved note, anchors kept, anywhere in the repo (specs including parked and retired, `docs/system/`, `docs/sources/` READMEs, other notes, `Full source:` and `Source:` lines) with correct relative paths, lists each file it changed, and rebuilds the indexes. Re-running it is safe: it changes nothing that is already right, and after a manual move it fixes stale links and empty source fields. Old spec lines keep their source lines; nothing is backfilled. Run it only when the user says yes. It is not a picture write.

## Stop

Do not plan. Do not implement. Do not commit. Do not run `/crav1-explain-existing-system`, `/crav1-plan-from-spec`, `/crav1-spark-to-spec`, or `/crav1-finalize-commit`. Do not clear a stale research mark except as the clear section says. Do not ask the user whether the update resolves it.

Output only:

- What was added to the picture (file, and the sentence, node, edge, or connection line), or that the picture is current
- `Synced at` cell or slice line written, or that none was written
- Research: the short summary of what was cleared, narrowed, and routed where, each open question from the updated note and where it went, and when an older mark had no points, or that this run was not pointed at a research note
- Next: `/crav1-finalize-commit` when a file changed (no push). When nothing was written, name no command. Do not run it.

## Style

Be concise. Add the smaller line. Do not fill gaps with an architecture you invented.
