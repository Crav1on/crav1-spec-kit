---
name: crav1-keep-current
description: >-
  Update the picture in docs/system/ when something was added. Add what is
  new to the short description, the diagram, and how the parts connect.
  Do not rewrite what is already there. Do not design the change. Do not
  build it. Can run on its own. Spark, ideas, intake, match, and any
  sibling that already appends a glossary row run this same update and
  still do not rewrite existing glossary rows. The skill that reads named
  repos and writes one architecture spec is /crav1-repos-to-spec. Do not
  do that job.
disable-model-invocation: true
icon: refresh-cw
color: green
---

# Keep current

You update the picture in `docs/system/` when something was added. You add what is new to the short description, the diagram, and how the parts connect. You do not rewrite what is already there. You do not design the change. You do not build it.

This is cross-cutting. It is not its own lane. It does not move work into Specify, Plan, or Build.

This is not `/crav1-repos-to-spec`. That command reads the repos the user named and writes one architecture spec the lanes can extend, plus these notes. Do not do that job. Do not invent an architecture from code. Do not create a slug.

Spark, ideas, intake, match, match-dump, and code-into-specs run this picture update in the same pass that appends a glossary row. They follow [references/picture.md](references/picture.md) (drop-in: `.claude/skills/crav1-keep-current/references/picture.md`; plugin: this skill’s `references/picture.md`). They do not rewrite existing glossary rows. This command does not write glossary rows.

## From /crav1-environment-read

When `/crav1-environment-read` hands a confirmed system section, run only this section, then stop. That section is the source. Add only what is new to the picture, following [references/picture.md](references/picture.md). Each new sentence, node, edge, or connection line says `Seen in <host> <environment>.` When the line says `shared with prod`, `prod only`, or shape and connections only, keep that label. It does not say the code shows it. A connection is added only when that section says the environment shows it. Do not rewrite a line that is already there. Do not run the alone-read of the specs. Do not open an interview. Do not start Specify, Plan, or Build. If `docs/system/` is missing, write nothing.

## When the folder is missing

Run only when `docs/system/` already exists. If that folder is missing, stop. Point at the command that creates it. Do not seed the folder. Do not write the picture to fill the gap.

Point at one command when what they brought makes it obvious. Do not run it.

- One or two sentences: `/crav1-spark-to-spec`
- A pile of ideas: `/crav1-ideas-to-spec`
- Mixed files or several features: `/crav1-intake-to-specs`
- Repos plus a dump: `/crav1-match-to-specs`
- Named repos and no dump: `/crav1-repos-to-spec`

If they brought none of those, name those five commands and stop.

A caller that does not seed `docs/system/` (match-dump, code-into-specs) does nothing about the picture when that folder is missing.

## What was added

Alone: read each `docs/specs/<slug>/spec.md` (skip `_template`). What is new is a part or a connection that spec states and the picture does not. Skip a sentence marked inferred. If no spec folder exists, say so, write nothing, and stop. Do not invent the picture from the repo.

From a caller: what is new is only what that pass added. Do not open a second interview. Do not scan unrelated specs to redesign the paragraph.

A part or a connection the source does not state is not new.

## Write

Follow [references/picture.md](references/picture.md). Three places only:

- the short description in `docs/system/landscape.md`
- the context diagram in `docs/system/diagrams.md`
- `## How the parts connect` in `docs/system/landscape.md`

Do not add a feature-index row. Callers that own the index still add that row themselves. Do not edit `glossary.md`. Do not commit.

## Stop

Do not plan. Do not implement. Do not commit. Do not run `/crav1-explain`, `/crav1-plan-from-spec`, `/crav1-spark-to-spec`, or `/crav1-finalize-commit`.

Output only:

- What was added to the picture (file, and the sentence, node, edge, or connection line), or that the picture is current
- Next: `/crav1-finalize-commit` when a file changed (no push). When nothing was written, name no command. Do not run it.

## Style

Be concise. Add the smaller line. Do not fill gaps with an architecture you invented.
