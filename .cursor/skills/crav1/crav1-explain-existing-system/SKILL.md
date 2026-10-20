---
name: crav1-explain-existing-system
description: >-
  Read the system notes spark, ideas, intake, match, or existing-to-specs
  already wrote (docs/system/). First answer is a short TLDR. Longer goes
  one level deeper from the same notes. The user can point at one part, or
  ask whether the system can do something. Yes points at the note. No says
  no. When the picture has nothing on the question, quote the first
  paragraph of the matching slice's spec, labelled as coming from the spec,
  and name /crav1-what-do-we-know-about-this. When no spec matches either, say so
  and name that skill. Does not guess, write a second document, teach, or
  start Specify, Plan, or Build. On every run, compare the feature index
  with each slice's diagram node and its connection line. List each slice
  that is missing entirely or partly, including done and retired, and name
  /crav1-refresh-system-notes. Do not run it. A stale research note is shown
  as stale. Read-only.
disable-model-invocation: true
icon: message-circle
color: blue
---

# Explain

You read the system notes already in `docs/system/` and answer from those notes. The first answer is a short TLDR. You do not guess. You do not write a second document. You do not teach. You do not start Specify, Plan, or Build. You stay read-only. You do not write a file.

This is cross-cutting. It is not its own lane. It does not move work into Specify, Plan, or Build.

This is not `/crav1-what-do-we-know-about-this`. That command answers one feature, slice, resource, or not-yet-feature from the specs first. This command reads `docs/system/`. When the picture has nothing on the question, it quotes the first paragraph of the matching slice's spec, labelled as coming from the spec, and names `/crav1-what-do-we-know-about-this`. It does not run that command. It does not answer the question from the spec.

The notes are the files in `docs/system/` (skip `_template`): `landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`, `adr/`, and `security.md` when that file exists. The picture is three places in those notes: the short description (the paragraph under `# System landscape`, before the first `##`), the context diagram in `diagrams.md`, and `## How the parts connect` in `landscape.md`.

## When the notes are missing

Read `references/missing.md` ("When the notes are missing") only when docs/system/ has no notes.

## What they asked

Everything after `/crav1-explain-existing-system`, and every `@`, is the pointer.

Three asks:

1. **The whole system** — no pointer, and they did not ask whether the system can do something. TLDR of the short description.
2. **One part** — they named a heading, a file under `docs/system/`, a repo row, a feature-index slug, or a diagram node. TLDR of that part only.
3. **Can it** — they asked whether the system can do something. Yes, no, or not written down.

A can-it question uses the notes. A pointer on that same message limits the search to that part. If the part never mentions it, say that is not written down. Do not search the rest of the notes unless they also asked about the whole system. Then follow **When the picture has nothing on the question**.

If the pointer names something the notes do not contain, say that part is not written down. Do not search the repo to find it. Then follow **When the picture has nothing on the question**.

## First answer

A few sentences. Quote the notes. Do not open the next heading.

- **Whole system:** the short description only. When that paragraph is still the template sentence, say the short description is not written down. Then follow **When the picture has nothing on the question**.
- **One part:** that part only. When the part is a heading with no lines under it, say that part is not written down. Then follow **When the picture has nothing on the question**.
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

The feature-index check still runs at the end of a longer answer.

## Can it

Search the notes for that thing. A glossary row is a word, not a yes. A neighbor feature is not a yes. Code is not a note.

- **Yes** — a note states the system does it. Say yes. Point at the file and the heading, the diagram node, the connection line, or the index row. The pointer is the line that says it. Do not retell a spec.
- **No** — a note states the system does not (later, out of scope, a non-goal, or an explicit no). Say no. Point at that line.
- **Not written down** — the notes never mention it. Say that is not written down. Do not infer a yes. Then follow **When the picture has nothing on the question**.

## When the picture has nothing on the question

Read `references/missing.md` ("When the picture has nothing on the question") only when the picture says nothing about the question.

## Feature index and the picture

Read `references/picture.md` ("Feature index and the picture") only when you use the feature index or the picture.

## Research marked stale

Read `references/missing.md` ("Research marked stale") only when research is marked stale.

## Stop

Do not write a file. Do not invent a second document. Do not teach how to build it. Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-plan-from-spec`, `/crav1-build-tasks`, `/crav1-refresh-system-notes`, `/crav1-what-do-we-know-about-this`, or `/crav1-finalize-commit`.

Output only the answer, the spec quote when the picture has nothing on the question, the feature-index list when a slice is missing from the picture, and each stale research mark this run found.

## Style

Be concise. Prefer the note’s words. Do not fill a gap with a guess.
