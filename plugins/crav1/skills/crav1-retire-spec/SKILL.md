---
name: crav1-retire-spec
description: >-
  Take one spec out of the work: retire it, merge it into another spec,
  park it, or convert it to a note. Opens with one question: retire
  (Recommended), merge, park, or convert to note; skips it when the
  wording answers; a headless or bot run with no choice word stops and
  lists the words. Always shows a summary of every change and waits for a
  yes before writing. Never deletes; a moved spec leaves a one-line
  pointer at its old path. Retire moves it to docs/specs/retired/. Merge
  takes a named target or suggests only real fits, each with a reason,
  and says "no good merge fit found" when none fits. Park adds a Parked
  mark in place; un-park re-reads the notes waiting for it. Convert to
  note writes docs/notes/YYYY-MM/ with a Source line and a landscape line. Removes
  the feature-index row on retire, merge, and convert.
disable-model-invocation: true
icon: archive
color: gray
---

# Retire spec

You take one spec out of the work, or bring a parked one back. You never delete a file. You write nothing until the user has seen the summary and said yes.

Command: `/crav1-retire-spec`.

This is cross-cutting. It is not its own lane. It may run from any lane, any time. It does not move work into Specify, Plan, or Build. It is not a starter option.

## Which spec

The spec is everything after `/crav1-retire-spec` that names a folder under `docs/specs/<slug>/`, or an `@` of that folder or its `spec.md`. Skip `_template` and `retired/`.

No spec named, or a name that matches more than one folder: ask with options only, one option per spec folder, labelled `docs/specs/<slug>/` and the spec's title line. A headless or bot run with no spec stops and says: `Missing spec. Name docs/specs/<slug>/.`

A spec that already has a `Parked:` line and the wording says un-park, unpark, resume, or pick up again: run **Un-park**. Do not ask the opening question.

## Opening question

Ask one question, with the questions tool when it is available. The recommended option is first:

1. **Retire (Recommended).** Done or dead. Moves to `docs/specs/retired/`.
2. **Merge.** Its content belongs in another spec.
3. **Park.** Not now. Stays in place, marked parked.
4. **Convert to note.** Reference knowledge, never going to be built.

Skip the question when the wording already answers it: "retire", "done", "dead", "drop" is 1; "merge into", "fold into" is 2; "park", "on hold", "not now" is 3; "convert to note", "just reference", "background" is 4.

Ask for a reason in the same turn when none was given. The reason is one short line. A headless or bot run with no reason writes `reason not given`.

## Choice words

Exact words for bots and scripted runs. There are no `--flags`.

- What to do: `retire` / `merge` / `park` / `convert to note`.

When the invocation contains one of these words (for example `/crav1-retire-spec park docs/specs/orders-export/ waiting on partner`), take that choice and do not ask. This holds for a person, a bot, or a headless run.

When a choice is missing and the run is headless or started by a bot (no person in the chat to answer), do not guess. Stop and name the valid words: `Missing choice. Use one of: retire, merge, park, convert to note.`

## Summary first

Before writing anything, show one summary: every file that will be created, moved, or changed, and the lines that will be added or removed, including the pointer, the feature-index row, the notes index row, and any landscape line. Then ask yes or no. Write nothing until yes. No writes nothing and stops.

A headless or bot run shows the summary and writes only when its invocation also says `yes`.

## Never delete

Nothing is deleted. A spec that moves leaves its `spec.md` at the old path as a one-line pointer:

```markdown
Moved: <retired | merged | converted> <YYYY-MM-DD>, see <new path>. Reason: <reason>
```

Other files in the old folder (`plan.md`, `tasks.md`, `verify.md`, and the rest) move with the spec. The old folder keeps only the pointer.

## Retire

1. Move `docs/specs/<slug>/` to `docs/specs/retired/<slug>/`. Create `docs/specs/retired/` when it is missing.
2. Add as the first line of the moved `spec.md`: `Retired: <YYYY-MM-DD>, <reason>`.
3. Leave the pointer at the old path.
4. Remove that slug's row from `## Feature index` in `docs/system/landscape.md`.
5. Search `docs/` (specs, plans, tasks, notes, system notes) for links to the old path or the slug. Do not rewrite them. List each one as `link to fix: <file>:<line>` in the closing message.

Every skill that scans specs skips `docs/specs/retired/`.

## Merge

**Target.** When the user named a target spec, use it. Do not suggest others.

When no target is named, suggest only specs that are a real fit, which can be none, one, or several. Each suggestion has a reason taken from what was read:

- a shared feature area (the same area or parent in the feature index, or the same title words)
- overlapping requirements (the same requirement, resource, or acceptance line in both specs)
- the same system in `docs/system/landscape.md` (both slices on the same line under `## How the parts connect`)
- links between them (one spec links to the other)

Best fit first, its label ending with ` (Recommended)`. Do not pad the list. A spec with no stated reason is not a fit. When none fits, say `no good merge fit found` and offer park, retire, or convert to note instead. A headless or bot run with no target stops and lists the fits with their reasons, or says `no good merge fit found`.

**Move.** Into the target `spec.md`:

- the content, under the target's matching headings, each block marked `(from <slug>)`
- each open question with its lines, marked `(from <slug>)`
- each decision, marked `(from <slug>)`

Do not rewrite the target's own lines. A requirement that already says the same thing is not copied again; list it as `already in target` in the summary.

Then move the source folder to `docs/specs/retired/<slug>/` with `Merged: <YYYY-MM-DD> into <target slug>, <reason>` as its first line, leave the pointer at the old path, and remove the source's feature-index row. Flag inbound links as in **Retire**.

## Park

Add as the first line of `spec.md`: `Parked: <YYYY-MM-DD>, <reason>`. Do not move the spec. Do not change the feature-index row.

While parked:

- `/crav1-plan-from-spec`, `/crav1-build-tasks`, `/crav1-build-features`, and the push branches of `/crav1-ado-sync` skip it and say `skipped: <slug> (parked)`.
- `/crav1-help` and `/crav1-show-or-ask-open-questions` list it as parked, with the count of notes waiting for it.
- `/crav1-add-to-spec` writes nothing into it. Input that matches it is saved as one note waiting for it (see that skill's **Parked specs**).

## Un-park

1. Find every note in `docs/notes/` (month folders and their generated indexes) with the slug in `waiting_for`, or an old `Waiting for <slug> (parked)` line.
2. Read each waiting note in full. Suggest what fits the spec now, including points that already went to other specs, when they matter to this one too. Match each point against every active spec as well, and say when another spec is now the better fit.
3. Show the summary: the `Parked:` line removed, each point to add, and each note that gets `Used by <slug>`.
4. On yes: remove the `Parked:` line, add the chosen points through the same rules as `/crav1-add-to-spec`, and on each waiting note move the slug from `waiting_for` to `used_by` (an old line becomes `Used by <slug>`). Run the notes index generator; do not hand-edit an index.

A waiting note is never marked absorbed. It stays open as the shared full source for any spec.

## Convert to note

1. Write `docs/notes/<YYYY-MM>/<YYYY-MM-DD>-<slug>.md` in the note shape (`docs/notes/_template/note.md`, see `crav1-add-to-spec` `references/notes.md`), dated by the spec's first commit date (the source date), with `imported` today. Front matter `kind: converted spec`, `source: docs/specs/<slug>/spec.md`. The title is the spec's title. Add `Source: docs/specs/<slug>/spec.md (converted <YYYY-MM-DD>)` and `Converted from spec, no research owner`. The body is the spec's content as it was.
2. Run the notes index generator so the note gets its index row. Do not hand-edit an index.
3. Add one line under `## How the parts connect` in `docs/system/landscape.md`: `<title>: reference only, see docs/notes/<YYYY-MM>/<YYYY-MM-DD>-<slug>.md`. Append only. Do not rewrite a line that is there.
4. Remove that slug's feature-index row.
5. Move the rest of the spec folder to `docs/specs/retired/<slug>/` and leave the pointer at the old path.

A converted note has no research owner. Skills that find it stale do not send a revisit request. They show it as stale and stop there.

## Stop

Do not delete a file. Do not edit a spec other than the one named and, for merge, the target. Do not run `/crav1-refresh-system-notes`, `/crav1-add-to-spec`, or any other skill. Naming one is not running it. Do not commit.

## Closing message

- What was done, with each path written.
- `link to fix:` lines for inbound links, or `no links found`.
- For park, how to un-park: `/crav1-retire-spec un-park docs/specs/<slug>/`.

## Style

Be concise. Plain words. Name every path.
