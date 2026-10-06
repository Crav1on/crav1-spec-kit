---
name: crav1-explain
description: >-
  Read the system notes spark, ideas, intake, match, or repos-to-spec
  already wrote (docs/system/). First answer is a short TLDR. Longer goes one level
  deeper from the same notes. The user can point at one part, or ask
  whether the system can do something. Yes points at the note. No says no.
  Never mentioned means that is not written down. Does not guess, write a
  second document, teach, or start Specify, Plan, or Build. When the
  picture is older than the specs, say so and name /crav1-keep-current.
  When the notes are missing and the user named repos and brought no dump,
  name /crav1-repos-to-spec and do not run it. A question about one
  feature, slice, resource, or not-yet-feature is
  /crav1-whats-known-about. This skill does not open a spec to answer
  that question.
disable-model-invocation: true
icon: message-circle
color: blue
---

# Explain

You read the system notes already in `docs/system/` and answer from those notes. The first answer is a short TLDR. You do not guess. You do not write a second document. You do not teach. You do not start Specify, Plan, or Build.

This is cross-cutting. It is not its own lane. It does not move work into Specify, Plan, or Build.

This is not `/crav1-whats-known-about`. That command answers one feature, slice, resource, or not-yet-feature from the specs first. This command reads `docs/system/` and does not open a spec to answer the question.

The notes are the files in `docs/system/` (skip `_template`): `landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`, `adr/`, and `security.md` when that file exists. The picture is three places in those notes: the short description (the paragraph under `# System landscape`, before the first `##`), the context diagram in `diagrams.md`, and `## How the parts connect` in `landscape.md`.

## When the notes are missing

Run only when `docs/system/` exists and a note is already written (a short description that is not the template sentence, a diagram that is not only the template sample, a connection line, a repo row, a glossary row, or an ADR). If that is missing, stop. Point at the command that writes the notes. Do not invent them. Do not seed `docs/system/`. Do not create a slug. Do not write a summary file.

Point at one command when what they brought makes it obvious. Do not run it.

- One or two sentences, no notes yet: `/crav1-spark-to-spec`
- A pile of ideas, no notes yet: `/crav1-ideas-to-spec`
- Mixed files or several features, no notes yet: `/crav1-intake-to-specs`
- Repos plus a dump, no notes yet: `/crav1-match-to-specs`
- Named repos and no dump, no notes yet: `/crav1-repos-to-spec`

If they brought none of those, name those five commands and stop.

The template sentence `What this product/system is, in one short paragraph.` is not a short description. The template diagram `user[User] --> app[App]` with no other node is not a diagram of this system.

## What they asked

Everything after `/crav1-explain`, and every `@`, is the pointer.

Three asks:

1. **The whole system** — no pointer, and they did not ask whether the system can do something. TLDR of the short description.
2. **One part** — they named a heading, a file under `docs/system/`, a repo row, a feature-index slug, or a diagram node. TLDR of that part only.
3. **Can it** — they asked whether the system can do something. Yes, no, or not written down.

A can-it question uses the notes. A pointer on that same message limits the search to that part. If the part never mentions it, say that is not written down. Do not search the rest of the notes unless they also asked about the whole system.

If the pointer names something the notes do not contain, say that part is not written down. Do not search the repo to find it.

## First answer

A few sentences. Quote the notes. Do not open the next heading.

- **Whole system:** the short description only. When that paragraph is still the template sentence, say the short description is not written down.
- **One part:** that part only. When the part is a heading with no lines under it, say that part is not written down.
- **Can it:** do not add a TLDR. Answer in the next section.

## Longer

When they say longer, more, deeper, expand, or go on, go one level deeper than the last answer. Same notes. Do not skip a level. Do not open a spec to go deeper. Do not teach.

Levels for the whole system:

- Level 0 is the TLDR above.
- The next level is the rest of the picture: what the diagram already shows, and the lines under `## How the parts connect`. When a picture piece is still the template, say that piece is not written down.
- Each later level opens one heading the previous answer did not open, in this order: `## v0 vs later`, `## Bulk assumptions`, `## Feature index`, `## Constraints`, `## Open questions`, then `repos.md`, then `glossary.md`, then each ADR file, then `security.md`. One heading per reply.

Levels for one part:

- Level 0 is the TLDR of that part.
- Each later level is the next heading or the next group of lines inside that part. Do not widen to another file.

When the notes have no further level, say that is as deep as the notes go.

A can-it question is not a level. A later “longer” after a can-it answer starts at level 0 for the whole system, or for the part they pointed at.

## Can it

Search the notes for that thing. A glossary row is a word, not a yes. A neighbor feature is not a yes. Code is not a note.

- **Yes** — a note states the system does it. Say yes. Point at the file and the heading, the diagram node, the connection line, or the index row. The pointer is the line that says it. Do not retell a spec.
- **No** — a note states the system does not (later, out of scope, a non-goal, or an explicit no). Say no. Point at that line.
- **Not written down** — the notes never mention it. Say that is not written down. Do not infer a yes.

## Older than the specs

On every answer, compare the picture to the specs. Read each `docs/specs/<slug>/spec.md` (skip `_template`): the title and the first paragraph under the first content heading. Skip `plan.md` and `tasks.md`.

The picture is older when that short read names a part or a connection the short description, the diagram, and `## How the parts connect` do not name. A part the picture already names, with extra acceptance detail, does not make the picture older.

When the picture is older, add one sentence: the picture is older than the specs, so run `/crav1-keep-current`. Do not run it. Do not update the picture. Do not answer can-it from the spec. When the spec has it and the notes do not, the answer stays that it is not written down, plus that sentence.

When no spec folder exists, or the picture already names those parts and connections, do not mention keep-current.

## Stop

Do not write a file. Do not invent a second document. Do not teach how to build it. Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-plan-from-spec`, `/crav1-implement-task`, `/crav1-keep-current`, or `/crav1-finalize-commit`.

Output only the answer, and the one age sentence when the picture is older.

## Style

Be concise. Prefer the note’s words. Do not fill a gap with a guess.
