# When they pick commit

1. Confirm git works (same PATH fallback as the draft skill).
2. **Files:** commit **staged** files if the index is non-empty. If the index is empty, ask whether to `git add` the intended file set from the draft. Do not add `agent-tools/`, `artifacts/`, `bin/`, `obj/`, or other build output. After `strip-trailers` in this run, also stage the new hook and its project rule by path, and nothing else unstaged ([references/trailer-hook.md](trailer-hook.md)).
3. **Message:** `git commit` with Summary as the subject (`-m`) and Description as the body (second `-m`, or a HEREDOC). The body is the Description paste, including a trailing work-item mention when the draft has one. Do not add `Co-authored-by`, `Made-with: Cursor`, or other trailers yourself. Do not drop the mention line.
4. Read `git log -1 --format=%B`. Compare to the drafted Summary + Description. The mention, when the draft has one, is the last line of that Description. A last line of `#<id>` or `AB#<id>` is the work-item mention, not an added line.
5. Show the new hash, subject, and `git status` short result.
5a. **Fetch and check (1.81.0, 1.123.0, stamp conflicts 1.139.0, build progress 1.142.0, kit copies 1.208.0).** Fetch. When behind the upstream, merge with `git pull --no-rebase --no-commit` (no auto-commit, no rebase) and resolve kit-file conflicts by the kit's rules. Installed kit copies that are pristine releases are settled to the newer release by `scripts/kit_merge.py settle`. A `walk-progress.md` conflict that is only version lines is settled in that same merge. A `build-progress` file that is only hash lines is settled the same way. A notes index rebuild goes into that same merge commit. The merge commit is `scripts/kit_merge.py commit` (`git commit --no-edit --cleanup=strip`). This run makes at most two commits: the drafted commit, and that merge commit. Otherwise check any unpushed merge for lines either side added that the merge dropped. Read [references/pull.md](pull.md) for both. Never push; the Run next in step 7 names the push.
5b. **Push on `commit-push` (1.199.0).** Only when the invocation said `commit-push` and step 5a ended with nothing lost: `git push` (with `-u <remote> <branch>` when there is no upstream). No force. Rejected: show the error and the `git pull --no-rebase` advice, and stop. Pushed: the ending says the branch is in step with origin and has no push entry.
6. If the message has any line that was **not** in the draft (a `Co-authored-by`, `Signed-off-by`, `Generated with` or other trailer from Cursor, Claude Code or another tool), read [references/added-lines.md](added-lines.md).
7. After the commit message is settled (including a one-time strip of added lines), end with Run next, never a `Next:` line (1.171.0). Run next starts with one reason line, then each label on its own line above its command, and each command alone in its code span (reason line 1.195.0). An unfinished specify walk comes first. An unfinished build-progress file for this branch comes first too. A failed commit has no Run next.

   On a base branch or in the specs repo (a pull request cannot open from that branch into itself):

   Run next:
   The commit is only local.

   Push the specs repo:
   `git push`

   Unfinished spec walk: resume that walk before a build walk. The branch on a build walk is the working branch, never `main` or `master` unless that branch is checked out.

   Run next:
   The spec walk is not finished.

   Resume the spec walk:
   `/crav1-tighten-and-plan-ready-to-build orders-api`

   Unfinished build walk on this branch: a Run next entry, not a `Next:` line (1.157.0). The command resumes that walk: the branch for a `Run: whole branch` file, otherwise the file's first unticked `T#`.

   Run next:
   The build walk on this branch is not finished.

   Continue the build walk on feat/orders-cicd:
   `/crav1-build-walk orders-api feat/orders-cicd`

   On a feature branch with no unfinished walk and no pull request yet:

   Run next:
   The commit is only local and no pull request is open.

   Push and open the pull request:
   `/crav1-open-pr`

   When a pull request is already open:

   Run next:
   PR <n> does not have this commit yet.

   Push to PR <n> and comment:
   `/crav1-open-pr pr<n>`

   Do not run it. `Uncommitted:` follows in chat when files are still not committed.
8. If commit fails (hooks, empty index, identity), show the error. Keep the paste blocks, **then** offer the choices again (`commit` still first). Do not name `/crav1-open-pr` on a failed commit.

Do not `git commit --amend` for wording tweaks unless they asked. Amending **only** to restore the drafted message (strip added lines) is allowed as below.
