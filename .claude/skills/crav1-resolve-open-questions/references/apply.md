# apply <file> (1.110.0)

Reads back a playbook report (`report-playbook-short` or `report-playbook-full` from `/crav1-what-do-we-know-about-this`) after someone filled it in. The file may have been edited by people who do not use the kit, so read it plainly and forgive small format slips.

## Read the file

- Its date and kit version come from the `Report:` line under the title. No date: say so and treat every item as possibly stale.
- Every `N<n> Answer:` line under Needs your answer. `yes` (or `ok`, `accept`) means the row's recommended answer. Empty means not answered: leave that question open.
- Every `K<n> Change:` line under Kept. Empty means the decision stays.
- Each row's spec line and `Recorded in Step <n>`, to find the spec and the words to match.

## Compare with the specs now (no edits)

1. **Staleness first.** List spec, plan and task changes since the report date (`git log --since=<date> -- docs/specs/`). Name them in one short block before the items, for example `Since 2026-10-31: the cancel-booking spec changed twice (PR #74, 2026-11-01)`.
2. Sort each filled item into one bucket:
   - **New:** the question is still open (found by its words, as `crav1-add-to-spec` `references/merge-safe.md` says) or the Kept decision is unchanged in the spec. It will be written.
   - **Already settled the same way:** the spec already says the same thing. Skip it.
   - **Conflicting:** the spec now says something else (answered since the report, or the decision changed). Do not write.
3. Show one table: item, bucket, the file's answer, what the spec says now.

## Conflicts

One question per conflict, with the questions tool when available, at most 4 options. Show the file's answer and the spec's current answer side by side, with who decided each and when (from the file, the spec line, the commit or pull request), and your recommendation first:
- keep the spec's answer (skip this item)
- take the file's answer (write it, replacing the spec's)
- keep it open (write neither; add the clash as an open question)

## Write

Nothing is written until the user confirms the whole list with one `yes` (or picks items). Then:
- N answers: patch the open question as this skill's answer path does (one batch).
- K changes: write through `/crav1-add-to-spec`'s rules (show the change, then write).
- Never edit the filled file itself.

End with what changed, per spec, what was skipped and why, and what is still open. Suggest rerunning the playbook report to refresh it.
