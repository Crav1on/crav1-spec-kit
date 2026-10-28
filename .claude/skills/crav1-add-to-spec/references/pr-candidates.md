# crav1-add-to-spec: PR candidates (1.100.0)

Read only on `pr<n> candidates`, from **Choice words** in `SKILL.md`.

## What it reads

1. Find the PR note as `references/scope.md` parses `pr<n>`, and read its `## PR record` as `references/pr-record.md` says. No PR note or no record: stop and say `No PR record for PR <n>; run /crav1-pr-status pr<n> first.`
2. Take every Point tagged `to spec` or `to decision` that has no `in spec <slug>` tag. `pr<n> candidates 1,3` takes only those, numbered in record order. None left: say `No open candidates in PR <n>.` and stop.
3. Read nothing else from the note as input: not the description, the threads, the drafted replies or the history sections. They may be read to understand a Point, never quoted.

## What it does

- Run the candidates as one `fact` dump, as `references/fact.md` says, with the PR note as the source (`From PR <n> record, <date>.`). The usual target-spec and impact questions apply.
- A `to decision` Point whose text says the decision is not made yet (`<name> decides`, `waiting on <name>`, an open question) goes in as an open question with `Pending: <name>`, as `references/open-questions.md` says, not as a spec line.
- After the spec is written, set `in spec <slug>` on each Point taken, with the host's edit tool, one edit per line, in place (`references/pr-record.md` **Merge-safe rules**). A Point the user leaves out keeps its tag.
- Do not commit; name `/crav1-finalize-commit`.
