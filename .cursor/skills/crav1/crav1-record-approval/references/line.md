# Approved line

Read this when `/crav1-record-approval` shows or writes the line.

## The line

```text
Approved: <person>, <source date>, <source>, "<quote>" (accepted by <recorder> <date>)
```

- `<person>` matches the item's `Person:` line. No comma in the name.
- `<source date>` is the date on the quote. Keep it.
- `<source>` is a pull-request or thread link, or `mail`, or `meeting`.
- `<quote>` is the source's words. Do not paraphrase. No double quote inside it.
- `<recorder>` and the last date are who accepted it in this run, and the day they accepted it.

Both dates stay. The source date is not replaced by the accepted date.

## The constraint

Read `## Constraints`. A line such as `The partner gives a yes before the CI build policy script is applied.` is the constraint. Show that line next to the quote. The quote does not satisfy the constraint until `accept` in this run. Do not write `Approved:` from the quote alone. Do not delete the constraint when you write the line.

When no constraint names this person, say so, and still ask before writing.

## What it unblocks

`scripts/approval_needed.py show` prints `unblocks`. Those are the item's `Holds:` tasks. Say them in the chat. A matching line clears that hold on the next ready check. Other tasks were never held by this item.

## Script

Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. The script is `scripts/approval_needed.py` beside this skill.

- `show` writes nothing. It prints the line, the constraint, and `unblocks`.
- `write --yes` appends the line. Without `--yes` it writes nothing.
- It keeps the file's line endings.

An item that already has the same line is left as it is.
