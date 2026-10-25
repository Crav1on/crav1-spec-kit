# Pull path and nothing-lost check (1.81.0)

Read after a commit, and on the `pull` word. Never push, never rebase, never suggest a rebase.

## Kit files

`docs/specs/**/spec.md`, `docs/architecture/spec.md`, `docs/system/*.md` and `docs/notes/**`. Every other file is a code file: its conflicts stay with the user, as before. Say which ones, stop, and do not commit the merge.

## Fetch

`git fetch`, then compare `HEAD` with its upstream (`git rev-list --left-right --count HEAD...@{u}`). No upstream: say so in one line and stop; nothing is checked. Fetch fails (offline, not signed in): show the error, then run the nothing-lost check on local merges only.

- **Behind:** the pull path.
- **Not behind:** the nothing-lost check on every merge commit in `@{u}..HEAD`. None: say `Up to date. Ready to push.`

## Pull path

`pull` with uncommitted changes: stop and name `commit` instead; never stash.

1. `git pull --no-rebase`. Clean merge: run the check on the new merge commit.
2. Conflicts in kit files, resolved by rule:
   - Both sides added lines in the same spot: keep both, ours first, then theirs. A `**New:**` line, a glossary row or an open question goes in its sorted place instead, as `crav1-add-to-spec` `references/merge-safe.md` says (1.84.0).
   - Open questions are matched by their words, never by a `Q<n>`: the same question on both sides is one question, with both sides' `Pending:`, `Asked:`, `Answered:` lines under it (one `Blocks:` line; the newer one).
   - `Synced at`: one line per repo and branch (1.84.0); for the same repo and branch the newer date (then the later commit) wins; lines only one side has are kept, in sorted place (repo, then branch). An old `; `-joined line from a side not yet migrated counts as its entries, one line each.
   - Match `Branch:` lines (1.86.0): one line per branch; lines only one side has are kept, in sorted place (repo, then branch). The same branch on both sides is one line carrying both sides' markers (the newer `(PR <n>)` wins). An old `; `-joined line counts as its entries, one line each.
   - `docs/notes/index.md` and the month indexes: take either side, then rebuild with `notes_index.py build` from crav1-add-to-spec's `scripts/`. Never merge them by hand.
   - Both sides changed the same existing line in different ways (the same fact, said differently): ask the one question below.
3. Run the check against the working tree before `git commit --no-edit`. Lines missing: do not commit; list them and restore them first.
4. End: `Merged <upstream> into <branch>. Nothing lost. Ready to push.`

The question, only for a real disagreement, one per fact, with the two lines shown: `keep both` (theirs becomes `**Conflict:** "<their words>" (Full source: <their note, or their short sha>) vs the line above` under ours) / `mine` / `theirs` / `stop` (leave the merge unfinished, `git merge --abort` undoes it). Headless or bot run: write the `**Conflict:**` line and say so.

## Nothing-lost check

For a merge `M` with parents `P1` and `P2` and base `B = git merge-base P1 P2`, for each kit file either side changed: every line `git diff -U0 --ignore-cr-at-eol B P1 -- <file>` or `B P2` adds (the `+` lines) counts as kept when it is in `M`, in `HEAD` or in the working tree: check all three (`git show M:<file>`, `git show HEAD:<file>`, the file on disk), never only `M:<file>`. A line missing from `M` but restored in a later commit or in the working tree is kept, so a merge whose dropped lines were put back is not reported again. Before the merge commit, `M` is the working tree. Compare through git, ignoring CR at line ends, so CRLF copies under `core.autocrlf true` do not look different.

Not counted as lost: a note index line when `notes_index.py --check` passes, and a `Synced at` line replaced by a newer one for the same repo and branch, and an old `; `-joined `Synced at` or Match `Branch:` line whose entries are all kept as separate lines.

Lines lost in a merge already committed: stop, list each line with its file and side (`ours <sha>` / `theirs <sha>`), and ask: `restore` (put them back after the kept lines, left uncommitted) / `show me` / `stop`. After `restore`, stop (1.90.5): no draft and no commit question in this run; name `/crav1-finalize-commit` to commit the restored lines. Never amend or rewrite the merge.
