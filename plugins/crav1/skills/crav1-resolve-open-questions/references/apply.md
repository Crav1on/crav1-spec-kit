# apply <file> (1.110.0)

Reads back a playbook report (`report-playbook-short` or `report-playbook-full` from `/crav1-what-do-we-know-about-this`) after someone filled it in. The file may have been edited by people who do not use the kit, so read it plainly and forgive small format slips.

## Read the file

- Its date and kit version come from the `Report:` line under the title. No date: say so and treat every item as possibly stale.
- Two layouts, both read the same way:
  - **Item blocks (1.115.1):** each item is a bullet `**N<n>:**`, `**C<n>:**` or `**K<n>:**` with indented lines under it. Its fill-in line is the `Answer:` (N, C) or `Change:` (K) line under that bullet, up to the next item; the item number comes from the bullet. Under an N or C item, `Change:` is the report's proposed change, not an answer.
  - **Older files (1.110.0 to 1.115.0):** a table, then separate `N<n> Answer:`, `C<n> Answer:` and `K<n> Change:` lines.
- N and C answers: `yes` (or `ok`, `accept`) means the item's recommended answer. Empty means not answered: leave that question open.
- K changes: empty means the decision stays.
- Each item's spec line or Where line and `Recorded in Step <n>`, to find the spec and the words to match.

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

Nothing is written until the user confirms the whole list with one `yes` (or picks items). End the list with this block, word for word except the examples:

> **Reply yes** (or "confirm") to write it as shown.
> To change something first, reply with your edits, for example "only 1 and 3" or "skip K2".
> A filled playbook is written to `docs/playbooks/<topic>.md` on that yes. A git commit still waits for `/crav1-finalize-commit`.

After the yes or the edits, then:
- N answers: patch the open question as this skill's answer path does (one batch).
- C answers: settle the `**Conflict:**` line as this skill's conflict path does.
- K changes: write through `/crav1-add-to-spec`'s rules (show the change, then write).
- Never edit the filled file itself. Do not change its `Answer:` or `Change:` lines. The copy under `docs/playbooks/` is a separate write.

## Copy into the repo (1.120.0)

Run `scripts/playbook_store.py` in this skill after the yes, when at least one filled line is being written. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. The first report stays outside the project. This copy is not a git commit.

1. Run `prepare`. `draft` means no filled `Answer:` or `Change:` line outside a code fence. Say so and do not copy. The outside file stays where it is.
2. `propose-name`: the file name comes from the report subject, lowercase kebab-case (`CC Process 1.0` becomes `cc-process-1-0.md`). Show that name once, in the confirm, before the first copy. The user may reply with a different kebab-case name. Pass the confirmed name as `--name`. Later applies do not ask. The name stays fixed.
3. Same playbook: a `Docs path: docs/playbooks/<topic>.md` line in the file wins. Otherwise the one file under `docs/playbooks/` whose title subject matches. Two subject matches: stop and list them. Do not guess. A later apply reuses that path and ignores a different `--name`.
4. `ask-overwrite`: the committed file was edited in the repo after the last apply. `Applied as:` does not match the other lines. Show the diff. Pass `--overwrite` only after the user says yes to that overwrite.
5. `write --yes` copies the file to `docs/playbooks/<topic>.md`, stamps `Docs path:` and `Applied as:`, and leaves `Answer:` and `Change:` lines as they were. Reapply overwrites that same file. Git history keeps the earlier copy once someone commits.
6. For each spec this apply changed, pass `--spec`. The script writes one `Playbook: docs/playbooks/<topic>.md` line on that spec, after the title, replacing an older playbook line.
7. Read-back of `Answer:` and `Change:` works on the committed copy the same way as on the outside file. Add the Uncommitted line when the user wants the file in git. Do not commit from this skill.

End with what changed, per spec, what was skipped and why, what is still open, and the `docs/playbooks/` path when a copy was written. Suggest rerunning the playbook report to refresh it.
