# Conflict lines

Read only when the chosen specs hold a `**Conflict:**` line (1.111.0). A Conflict line sits under a decided line and says a newer source disagrees: `**Conflict:** "<new words>" (Full source: <note>) vs the line above`. `/crav1-add-to-spec` and the pull step of `/crav1-finalize-commit` write them. This skill settles them.

## List

Number `C1`, `C2`, … in document order, after the `Q#` list, for display only. Never write a `C#` into a file. A `C#: letter` answer maps to the conflict shown with that number; the patch finds it in `spec.md` by its words. Topic words or `<spec> C2` open one conflict, as they do for one question.

## One question per conflict

With the questions tool when available, at most 4 options. Show side by side:

- the decided line, who decided it and when (its source, the note it cites, or the commit that wrote it)
- the new quote, who said it and when (the note in `Full source:` and its source date)

Recommend one option and put it first, with ` (Recommended)` at the end of its label. Say why in one line. Prefer the newer source when it comes from the owner of that decision or answers the question the decided line left. Otherwise prefer the decided line.

1. **Take the new quote.** It replaces the decided line. The Conflict line is removed.
2. **Keep the decided line.** The Conflict line is removed. The note keeps its trace, with a short reason.
3. **Answer in my words.** The user's words replace the decided line. The Conflict line is removed.
4. **Keep it open.** Write nothing. The Conflict line stays.

## Write

Nothing is written until the user confirms the whole batch. One question card, as `crav1-docs/reference/question-cards.md` says. Follow **Batch of several items** in that file before this card. Print the findings table in this reply, then ask. The card names each item and its recommendation, for example `P4 tasks miss the 400 path: A add a test`. Never write `table above` unless that table is in this reply. Never ask the card without the table.

- `yes (Recommended)`: write it as shown.
- The card's free-text answer. Hint: `Type your changes, e.g. only C1` or `C2: keep it open`. An item that answer does not mention keeps what was shown.

Nothing gets committed either way. Do not add an `Edits` option.

After the yes or the typed answer, then, per settled conflict:

- Replace or keep the decided line as picked. Keep its existing source and add the new note as a second source when the new quote won. Keep the `Decided` date format the spec uses; the date is today.
- Remove the `**Conflict:**` line.
- Add a trace to the note named in `Full source:` as `crav1-add-to-spec` `references/notes.md` says, and run `scripts/notes_index.py` from that skill when a note changed. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says.

A headless or bot run lists the conflicts and settles none. Do not commit. End with what was settled, what stays open, and `/crav1-finalize-commit` when a file changed.
