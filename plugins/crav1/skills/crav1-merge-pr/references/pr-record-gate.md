# crav1-merge-pr: PR record gate (1.97.0)

Read only when the pointer in `SKILL.md` sends you here.

## Find the record

Look for the pull request's PR note in the specs repo (found as **After it merged** says: this checkout with `docs/specs/`, else the workspace folder with `docs/specs/`, else a sibling `../*/docs/system/repos.md` with a row for this repo). Search the month `docs/notes/YYYY-MM/index.md` files, then the notes themselves, for `source: PR <n>` with this repo. Read its `## PR record` section, as `crav1-add-to-spec` `references/pr-record.md` says (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/pr-record.md`; plugin: sibling `skills/crav1-add-to-spec/references/pr-record.md`). Read-only.

## The Ready line

- **No PR note, no record, or no `Ready:` line:** go on. Say once: `No merge-readiness line for PR <n>; /crav1-pr-status writes one.`
- **`Ready: yes`:** go on. Show the line.
- **`Ready: no | <why> | …`:** stop before **Show, then merge**. Show the line, then each reason on its own line, then: `The PR record says this pull request is not ready. Run /crav1-pr-status to refresh it, or add the word anyway to merge regardless.` Do not merge.
- **`Ready: merged`:** the record says it is merged already; the host read in **Read it first** decides. When the host says open, say the record is wrong and go on as for `no`.
- **Stale** (a push or a comment on the host is newer than the line's date, from **Read it first**): add `(stale since <date>)` to the line. A stale `no` still stops; a stale `yes` goes on with the note.

`anyway` in this turn skips only this gate: the line is shown with `Merging anyway, as asked.` and the run goes on. It never skips a required check, branch policy or review in **What must pass**. Headless or bot runs follow the same rule: without `anyway`, `Ready: no` stops.

## After the merge

Where **After it merged** writes the PR note, write the record instead of a `State on <date>` header line: `- State: merged | <date>` and `- Ready: merged | <merge short sha> | <date> by merge-pr`, each replacing the existing line in place, or added in sorted place, as `references/pr-record.md` says. Add the `## PR record` section when the note has none. Points are left as they are.
