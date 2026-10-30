---
name: crav1-retire-spec
description: >-
  Use when one spec should leave the work. Retire, merge into another spec,
  park, or convert to a note. Shows every change and waits for a yes. Never
  deletes; a moved spec leaves a pointer.
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

A spec that already has a `Parked:` line and the wording says un-park, unpark, resume, or pick up again: run **Un-park** ([branches/park/BRANCH.md](branches/park/BRANCH.md)). Do not ask the opening question.

## Opening question

Ask one question. The recommended option is first:

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

## Route (1.106.0)

Route first, load second. Pick the branch from the choice word or the answer to the opening question, then read only that branch file. Do not read the other branches.

- **Retire** (`retire`): follow [branches/retire/BRANCH.md](branches/retire/BRANCH.md).
- **Merge** (`merge`): follow [branches/merge/BRANCH.md](branches/merge/BRANCH.md).
- **Park and un-park** (`park`, or un-park): follow [branches/park/BRANCH.md](branches/park/BRANCH.md).
- **Convert to note** (`convert to note`): follow [branches/convert/BRANCH.md](branches/convert/BRANCH.md).

## Stop

Do not delete a file. Do not edit a spec other than the one named and, for merge, the target. Do not run `/crav1-refresh-system-notes`, `/crav1-add-to-spec`, or any other skill. Naming one is not running it. Do not commit.

## Closing message

- What was done, with each path written.
- `link to fix:` lines for inbound links, or `no links found`.
- For park, how to un-park: `/crav1-retire-spec un-park docs/specs/<slug>/`.

## Style

Be concise. Plain words. Name every path.
