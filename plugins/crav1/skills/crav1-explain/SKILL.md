---
name: crav1-explain
description: >-
  Read the system notes spark, ideas, intake, match, or repos-to-spec
  already wrote (docs/system/). First answer is a short TLDR. Longer goes
  one level deeper from the same notes. The user can point at one part, or
  ask whether the system can do something. Yes points at the note. No says
  no. When the picture has nothing on the question, quote the first
  paragraph of the matching slice's spec, labelled as coming from the spec,
  and name /crav1-whats-known-about. When no spec matches either, say so
  and name that skill. Does not guess, write a second document, teach, or
  start Specify, Plan, or Build. On every run, compare the feature index
  with each slice's diagram node and its connection line. List each slice
  that is missing entirely or partly, including done and retired, and name
  /crav1-keep-current. Do not run it. Read-only.
disable-model-invocation: true
icon: message-circle
color: blue
---

# Explain

You read the system notes already in `docs/system/` and answer from those notes. The first answer is a short TLDR. You do not guess. You do not write a second document. You do not teach. You do not start Specify, Plan, or Build. You stay read-only. You do not write a file.

This is cross-cutting. It is not its own lane. It does not move work into Specify, Plan, or Build.

This is not `/crav1-whats-known-about`. That command answers one feature, slice, resource, or not-yet-feature from the specs first. This command reads `docs/system/`. When the picture has nothing on the question, it quotes the first paragraph of the matching slice's spec, labelled as coming from the spec, and names `/crav1-whats-known-about`. It does not run that command. It does not answer the question from the spec.

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

Then run **Feature index and the picture** before you finish, whenever `docs/system/landscape.md` can be read.

## What they asked

Everything after `/crav1-explain`, and every `@`, is the pointer.

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

The picture has nothing on the question when the notes never mention what they asked. That is a can-it answer that is not written down, a named part the notes do not contain, or a whole-system answer whose short description is still the template sentence.

Match a slice by whole name only. The names that count are the slug, the spec title, and the main resource name, the same three as **Feature index and the picture**. The question matches a slice only when it uses one of those whole names. A shorter piece, a longer name that only contains it, a synonym, or a similar spelling is not a match.

When one slice matches, quote the first paragraph of that `docs/specs/<slug>/spec.md`. The first paragraph is the first block of prose after the title line. Skip a heading. Do not quote a table. Label it `From the spec (docs/specs/<slug>/spec.md):` and then the paragraph. Name `/crav1-whats-known-about`. Do not run it. The quote is labelled as coming from the spec. It is not the picture's answer.

When more than one slice matches that whole name, do not pick one. Name each slug. Name `/crav1-whats-known-about`. Do not run it. Do not quote.

When no spec matches either, say the picture has nothing on the question and no spec matches. Name `/crav1-whats-known-about`. Do not run it. Do not guess a slice.

When the spec has no prose paragraph, say the spec has no first paragraph, and still name `/crav1-whats-known-about`. Do not run it.

## Feature index and the picture

On every run, at the end of the answer, compare `## Feature index` in `docs/system/landscape.md` with the picture. Run this check on a longer answer too. When the notes are missing and `docs/system/landscape.md` can still be read, run it before you finish. When that file cannot be read, there is no list. Do not invent slices. Do not name `/crav1-keep-current` for this check.

The picture for this check is two places only: the slice's node in `docs/system/diagrams.md`, and its line under `## How the parts connect` in `landscape.md`. The short description is not this check.

Read every index row that has a slug. Skip a row whose slug cell is empty. Include a row whose Notes say `done` or `retired`. Include a spec whose `## Match` status says `done` or `retired`. Do not skip those slices.

Names that count, and only these:

- the slug
- the spec title, the `#` line of `docs/specs/<slug>/spec.md`
- the main resource name: the Repos cell on that index row, and the `Repo:` line under `## Match` when that line is there

A diagram node matches when its id or its label is that slug, that spec title, or that main resource name, as that whole name. A connection line matches when that line names the same whole name as its own token. A shorter piece, a longer name that only contains it, a synonym, or a similar spelling is not a match. Do not fuzzy-match.

A slice is missing entirely when neither the node nor the line matches. It is missing partly when one matches and the other does not. A slice with both a matching node and a matching line is not listed.

This check may read the title line, the feature-index row, and the Match `Status:` and `Repo:` lines. It does not answer the question from the rest of the spec.

At the end of the answer, list each missing slice, one line per slice. Show the status on the line. Copy the Notes cell. When `## Match` has a `Status:` line, show that word too if the Notes cell does not already say it. `done` and `retired` stay visible. When the Notes cell is empty and there is no Match status, the status is `no status`.

- `<slug> — <status> — missing the diagram node and the connection line`
- `<slug> — <status> — missing the connection line`
- `<slug> — <status> — missing the diagram node`

When the list has one or more slices, name `/crav1-keep-current`. Do not run it. Do not update the picture. When the list is empty, do not name keep-current for this check.

## Stop

Do not write a file. Do not invent a second document. Do not teach how to build it. Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-plan-from-spec`, `/crav1-implement-task`, `/crav1-keep-current`, `/crav1-whats-known-about`, or `/crav1-finalize-commit`.

Output only the answer, the spec quote when the picture has nothing on the question, and the feature-index list when a slice is missing from the picture.

## Style

Be concise. Prefer the note’s words. Do not fill a gap with a guess.
