# When they pick commit

1. Confirm git works (same PATH fallback as the draft skill).
2. **Files:** commit **staged** files if the index is non-empty. If the index is empty, ask whether to `git add` the intended file set from the draft. Do not add `agent-tools/`, `artifacts/`, `bin/`, `obj/`, or other build output. After `strip trailers` in this run, also stage the new hook and its project rule by path, and nothing else unstaged ([references/trailer-hook.md](trailer-hook.md)).
3. **Message:** `git commit` with Summary as the subject (`-m`) and Description as the body (second `-m`, or a HEREDOC). The body is the Description paste, including a trailing work-item mention when the draft has one. Do not add `Co-authored-by`, `Made-with: Cursor`, or other trailers yourself. Do not drop the mention line.
4. Read `git log -1 --format=%B`. Compare to the drafted Summary + Description. The mention, when the draft has one, is the last line of that Description. A last line of `#<id>` or `AB#<id>` is the work-item mention, not an added line.
5. Show the new hash, subject, and `git status` short result.
5a. **Fetch and check (1.81.0, 1.123.0, stamp conflicts 1.139.0, build progress 1.142.0).** Fetch. When behind the upstream, merge with `git pull --no-rebase --no-commit` (no auto-commit, no rebase) and resolve kit-file conflicts by the kit's rules. A `walk-progress.md` conflict that is only version lines is settled in that same merge. A `build-progress` file that is only hash lines is settled the same way. A notes index rebuild goes into that same merge commit. This run makes at most two commits: the drafted commit, and that merge commit. Otherwise check any unpushed merge for lines either side added that the merge dropped. Read [references/pull.md](pull.md) for both. Never push; end with `Ready to push.`
6. If the message has any line that was **not** in the draft (a `Co-authored-by`, `Signed-off-by`, `Generated with` or other trailer from Cursor, Claude Code or another tool), read [references/added-lines.md](added-lines.md).
7. After the commit message is settled (including a one-time strip of added lines), follow Which step stays Next in run-ending.md (1.123.0, build walk 1.142.0). An unfinished specify walk comes first. An unfinished build-progress file for this branch comes first too. On a base branch, name a push, because a pull request cannot open from that branch into itself. A failed commit has no next line.

   Next: /crav1-build-walk, because that walk has not finished this branch.

   On a feature branch with no unfinished walk:

   Next: /crav1-open-pr, because the commit is not on a pull request yet.

   When a pull request is already open, name that same command to push to PR <n> and update its description or comment. Do not run it.
8. If commit fails (hooks, empty index, identity), show the error. Keep the paste blocks, **then** offer the choices again (`commit` still first). Do not name `/crav1-open-pr` on a failed commit.

Do not `git commit --amend` for wording tweaks unless they asked. Amending **only** to restore the drafted message (strip added lines) is allowed as below.
