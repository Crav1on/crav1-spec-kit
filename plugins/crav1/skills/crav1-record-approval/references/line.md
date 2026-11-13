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

The show command prints `unblocks`. Those are the item's `Holds:` tasks. Say them in the chat. A matching line clears that hold on the next ready check. Other tasks were never held by this item.

## Script

Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. On Windows `<interpreter>` is `python` with `PYTHONUTF8=1`. Elsewhere it is `python3`. Pass `-X utf8`.

- `<interpreter> -X utf8 scripts/approval_needed.py show --root <spec-folder> --person "<person>" --source-date <date> --source "<source>" --quote "<quote>" --recorder "<recorder>" --accepted <date>` writes nothing. It prints the line, the constraint, and `unblocks`.
- `<interpreter> -X utf8 scripts/approval_needed.py write --root <spec-folder> --person "<person>" --source-date <date> --source "<source>" --quote "<quote>" --recorder "<recorder>" --accepted <date> --yes` appends the line. Without `--yes` it writes nothing.
- It keeps the file's line endings.

An item that already has the same line is left as it is.
