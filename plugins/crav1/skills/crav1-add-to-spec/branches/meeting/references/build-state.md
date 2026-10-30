# Meeting to specs: **Build state**

Part of `branches/meeting/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.107.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

## Build state

An item that matches an existing spec gets one line. An item with `Fits: none` gets no state line.

Read the spec on `Fits:`. When `Also fits` is present, read each of those specs too. For each one, read in this order. Skip a file that is not there. A missing file is not a search.

1. `docs/specs/<slug>/spec.md`, including `## Match` when that heading is there
2. `plan.md` in that folder
3. `tasks.md` in that folder, the checkboxes
4. `verify.md` in that folder, when the file is present

Judge in this order. Stop at the first that fits.

1. **built** — `spec.md` already states the whole item as present, including a `## Match` line that covers it as done, or a checked task (`[x]`) covers the whole item, and no `verify.md` row for that coverage fails.
2. **partly built** — part of the item is covered that way and part is not. A `verify.md` fail on one part is this state. The reason names which part.
3. **planned** — `plan.md` describes the item, or an open task (`[ ]`) covers it, and it is not done.
4. **not built** — that `spec.md`, `plan.md`, and `tasks.md` do not cover the item. A failed `verify.md` row that is the only coverage is this state. Name that row.

A goal, a requirement, or an unchecked acceptance line that only says the item should exist is not built by itself.

When those files do not settle the state, one quick read-only look at the code that spec or plan names. A path in `spec.md`, including `## Match`, or in `plan.md`, is the code to open. Do not open a file they do not name. Do not search the codebase. When they name no path, do not look. A clear state from the files above is settled. Do not open code to overturn it.

A state that rests on that code, or a state that is still uncertain after the read, ends the reason with `(inference, not in the docs)`. A state the spec, plan, tasks, or verify file shows does not get that label. Never invent a file, a task number, a checkbox, or a quote.

One line:

```text
State: <state>. <short reason that names the evidence>.
```

Example: `State: partly built. Dev container done (task 4 checked); prod not in tasks.md.`

When more than one spec fits, the state word is the state of the spec on `Fits:`. The reason names each other spec when its state differs, with that spec’s path.

The line is informational. It does not change keep, leave, dismiss, or note. It is not written. It is not part of the quote handed to the fact branch of `/crav1-add-to-spec`. It is not part of the quote written to a note.
