# crav1-add-to-spec: PR candidates (1.100.0)

Read only on `pr<n> candidates`, from **Choice words** in `SKILL.md`.

## What it reads

1. Find the PR note as `references/scope.md` parses `pr<n>`, and read its `## PR record` as `references/pr-record.md` says. No PR note or no record: stop and say `No PR record for PR <n>; run /crav1-pr-status pr<n> first.`
2. Take the Points that `scripts/pr_common.py candidates --note <PR note> [--pick 1,3]` in `crav1-pr-status` (the shared PR script, the same rule pr-status offers from, 1.193.0) returns as `candidates`: `to spec` or `to decision` Points with no `in spec <slug>` tag, or whose newer answer is not in the spec yet (`in spec <slug> (question)`, or an `answered` date after the in-spec date). `pr<n> candidates 1,3` takes only those, numbered in record order. Never take a Point it skips.
3. None left (`none_left`): say `No open candidates in PR <n>.` and end with this Run next, then stop:

```text
Run next:
No spec or decision candidates are open in PR <n>.

Check the pull request for new replies and candidates:
`/crav1-pr-status pr<n>`
```
4. Read nothing else from the note as input: not the description, the threads, the drafted replies or the history sections. They may be read to understand a Point, never quoted.

## What it does

- Run the candidates as one `fact` dump, as `references/fact.md` says, with the PR note as the source (`From PR <n> record, <date>.`). The usual target-spec and impact questions apply.
- A `to decision` Point whose text says the decision is not made yet (`<name> decides`, `waiting on <name>`, an open question) goes in as an open question with `Pending: <name>`, as `references/open-questions.md` says, not as a spec line.
- After the spec is written, set `in spec <slug> <YYYY-MM-DD>` on each Point taken with `scripts/pr_points.py in-spec --note <PR note> --thread <id> --slug <slug> --date <YYYY-MM-DD> --yes`, one line per Point, in place (`references/pr-record.md` **Merge-safe rules**). It replaces a narrowed `in spec <slug> (question)` tag. A Point the user leaves out keeps its tag.
- Do not commit. The fact path's ending applies (`references/stop.md`). Add the Uncommitted line when a file changed.
