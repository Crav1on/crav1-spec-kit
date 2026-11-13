# Question holds (1.137.0)

Read this when a kept-open question has no `Blocks:` line, or when `spec.md` changed after resolve-open-questions was recorded.

A kept-open question is under `## Open questions` and has no `Answered:` line.

- `Blocks: T#` holds those tasks. The reason ends `(recorded)`.
- `Blocks: whole slice`, also `the whole slice` in any case, holds every unfinished task. The ready-check line says `Holds the whole slice.` The reason ends `(recorded)`, so the hold stays after resolve-open-questions is recorded and through an open-questions edit.
- `Blocks: none` holds no task.
- No `Blocks:` line: hold the `T#` ids named in the question text that exist in `tasks.md`. Ignore a `T#` that is not in `tasks.md`. The reason is `open question "<question>" (inferred from the text)`. Show that hold the same way as a `Blocks:` hold, and say it was inferred from the text.
- Hold the whole slice, `open question "<question>" blocks the whole slice (inferred)`, only when the text names no such task and `resolve-open-questions` has never been recorded for the slice.
- A question that already has a `Blocks:` line, or whose words are on `Kept questions:` for that step, stays Waiting when the spec drifts. A new or unparsed question jumps back to `/crav1-resolve-open-questions` only for the tasks it holds.
- A task that waits on a held task is held too (`held, waits on T#`).

`scripts/question_blocks.py <spec.md-or-spec-folder>` prints the marks. A folder uses `<folder>/spec.md` and sibling `plan.md` and `tasks.md` when those arguments are omitted. Pass `tasks.md` when it is present so the script can infer. Exit 0 on success, including when questions are found. Exit 2 only when a file is missing or cannot be read. The ready check also says whether resolve-open-questions is already recorded. This command, run on its own, does not, so a question that names no task still holds the slice.
