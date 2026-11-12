# Pull path and nothing-lost check (1.81.0, merge commit 1.123.0)

Read after a commit, and on the `pull` word. Never push, never rebase, never suggest a rebase.

This run makes at most two commits: the drafted commit, and one merge commit when the branch was behind. A notes index rebuild is part of that merge commit. It is never its own commit.

## Kit files

`docs/specs/**/spec.md`, `docs/architecture/spec.md`, `docs/system/*.md` and `docs/notes/**`. `docs/specs/<slug>/walk-progress.md` is neither of those: its hash lines are settled by the stamp rule in step 3. A `docs/specs/<slug>/build-progress/*.md` file is the same kind of file (1.142.0). Every other file is a code file: its conflicts stay with the user, as before. Say which ones, stop, and do not commit the merge.

## Fetch

`git fetch`, then compare `HEAD` with its upstream (`git rev-list --left-right --count HEAD...@{u}`). No upstream: say so in one line and stop; nothing is checked. Fetch fails (offline, not signed in): show the error, then run the nothing-lost check on local merges only.

- **Behind:** the pull path.
- **Not behind:** the nothing-lost check on every merge commit in `@{u}..HEAD`. None: say `Up to date. Ready to push.`

## Pull path

`pull` with uncommitted changes: stop and name `commit` instead; never stash.

1. `git pull --no-rebase --no-commit`. Never rebase. Never `git pull --no-rebase` without `--no-commit`: that auto-commits a clean merge, and the check below cannot run first. A clean merge stays uncommitted until the one merge commit in step 6.
2. Conflicts in kit files, resolved by rule:
   - Both sides added lines in the same spot: keep both, ours first, then theirs. A `**New:**` line, a glossary row or an open question goes in its sorted place instead, as `crav1-add-to-spec` `references/merge-safe.md` says (1.84.0).
   - Open questions are matched by their words, never by a `Q<n>`: the same question on both sides is one question, with both sides' `Pending:`, `Asked:`, `Answered:` lines under it (one `Blocks:` line; the newer one).
   - Approval needed items are matched by their words. Both sides' `Asked:`, `Pending:`, and `Approved:` lines stay under the item. Never drop an `Approved:` line. One `Holds:` line, the newer. One `Person:` line, the newer.
   - `Synced at`: one line per repo and branch (1.84.0); for the same repo and branch the newer date (then the later commit) wins; lines only one side has are kept, in sorted place (repo, then branch). An old `; `-joined line from a side not yet migrated counts as its entries, one line each.
   - Match `Branch:` lines (1.86.0): one line per branch; lines only one side has are kept, in sorted place (repo, then branch). The same branch on both sides is one line carrying both sides' markers (the newer `(PR <n>)` wins). An old `; `-joined line counts as its entries, one line each.
   - `docs/notes/index.md` and the month indexes: take either side, then rebuild. Never merge them by hand.
   - Both sides changed the same existing line in different ways (the same fact, said differently): ask the one question below.
3. `walk-progress.md` stamp conflicts (1.139.0). For each unmerged `docs/specs/<slug>/walk-progress.md`, run `walk_progress.py resolve-stamps --root <spec-folder> --yes` from `crav1-tighten-and-plan-ready-to-build` `scripts/`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Do not reimplement the hash. The same command is the rule whenever the kit finishes a merge that leaves this file conflicted, including `git merge <base>` after `/crav1-open-pr` or `/crav1-merge-pr` says to merge the base in. `/crav1-update-kit` does not merge this file.
   - **Stamp-only.** When every conflict hunk is only a hash line the script writes (`Spec version`, `Plan version`, `Tasks version`, `Verify version`, `Spec body`, `Questions version`, `Kept questions`, `Content stamp`, `Key`, or `Playbook:`), the script takes the upstream text and may rewrite those lines. `Done`, `Result`, and every other recorded line stay. It `git add`s the file. `--yes` is the yes already given to commit. Do not push. Say the script's `line` once.
   - **Restamp rule.** A hash line becomes the merged file's normalized hash only when at least one side's recorded hash matches that side's file, and every matching side differs from the merged file only by progress as 1.138.0 defines it (line endings, and for `spec.md` and `tasks.md` a checkbox or a `(PR n)` or `(done)` mark). Otherwise the upstream hash stays, so a real edit still reopens the steps that edit affects. When every hash on the step is that merged hash, the script writes `Content stamp: normalized`. An older step with no such line still matches. The script reads each side's file. It does not use the HEAD fallback.
   - **Mixed.** When any hunk touches `Done`, `Result`, a finding, a note, or any other recorded line, the script writes nothing. Show its `line`. It names the stamp-only hunks and the other hunks. Offer `settle stamps` / `stop`. `settle stamps` runs the command again with `--settle-stamps --yes`, which rewrites only the stamp hunks and leaves the other markers. Do not `git add` that file and do not commit the merge. `stop` leaves the merge unfinished. Do not abort it unless they ask.
   - **Build progress (1.142.0).** For each unmerged `docs/specs/<slug>/build-progress/*.md`, run `build_walk.py resolve-stamps --file <path> --yes` from `crav1-build-walk` `scripts/`. Hash lines are `Tasks version`, `Spec version`, `Plan version`, `Verify version`, and `Content stamp`. A `(live yes: …)` note is progress, as a checkbox is. The script takes the upstream side. A mixed hunk is not rewritten. Do not push.
4. Run `notes_index.py --check` from crav1-add-to-spec's `scripts/`. When it fails, on a conflict or on a clean merge, rebuild with `notes_index.py` (no extra arguments) and `git add` the indexes. Do not commit yet.
5. Run `scripts/nothing_lost.py` in this skill, with `--root` set to the repo. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Before the merge commit, the working tree is the merge. Do not say Nothing lost unless the script prints `"nothing_lost": true`. Lines lost: do not commit; list each line with its file and side, and restore them first.
6. One merge commit, and no other. Stage the rebuilt indexes with the merge. A settled `walk-progress.md` is already staged. A settled `build-progress` file is already staged. When the index was rebuilt, append `Rebuilt the notes index into this merge.` to the merge message, then commit that message once. Otherwise `git commit --no-edit`. Do not make a second commit for the index. Do not commit while a mixed `walk-progress.md` or `build-progress` conflict remains.
7. End, only when the script said nothing was lost: `Merged <upstream> into <branch>. Nothing lost. Ready to push.` When the index was rebuilt, say it is in the merge commit. The stamp line from step 3 was already said.

If the merge is already committed when you get here (an older pull that auto-committed), do not make another commit. When the index check fails, rebuild it, leave it uncommitted, and name it on the `Uncommitted:` line.

The question, only for a real disagreement, one per fact, with the two lines shown: `keep both` (theirs becomes `**Conflict:** "<their words>" (Full source: <their note, or their short sha>) vs the line above` under ours) / `mine` / `theirs` / `stop` (leave the merge unfinished, `git merge --abort` undoes it). Headless or bot run: write the `**Conflict:**` line and say so. When a `**Conflict:**` line was written, the end names `/crav1-resolve-open-questions <slug>` to settle it (1.111.0).

## Nothing-lost check

Run `scripts/nothing_lost.py`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Do not reimplement it in the chat, and do not say Nothing lost without its `"nothing_lost": true`.

The script checks a merge `M` with parents `P1` and `P2` and base `B = git merge-base P1 P2`. For each kit file either side changed, every line `git diff -U0 --ignore-cr-at-eol B P1 -- <file>` or `B P2` adds (the `+` lines) counts as kept when it is in `M`, in `HEAD` or in the working tree. A line missing from `M` but restored in a later commit or in the working tree is kept. Before the merge commit, `M` is the working tree. Pass `--merge <sha>` for a merge that is already committed. Compare through git, ignoring CR at line ends, so CRLF copies under `core.autocrlf true` do not look different.

Not counted as lost: a note index line when `notes_index.py --check` passes, and a `Synced at` line replaced by a newer one for the same repo and branch, and an old `; `-joined `Synced at` or Match `Branch:` line whose entries are all kept as separate lines.

Lines lost in a merge already committed: stop, list each line with its file and side (`ours <sha>` / `theirs <sha>`), and ask: `restore` (put them back after the kept lines, left uncommitted for this skill's commit step) / `show me` / `stop`. After `restore`, the restored lines go into this run's draft and commit, with the one confirm at the end (1.91.0). Never amend or rewrite the merge.
