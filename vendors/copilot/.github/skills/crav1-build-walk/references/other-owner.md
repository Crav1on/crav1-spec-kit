# Other-owner mode

Read this when the pull request author, or a commit author on the branch, is not the current user. `scripts/build_walk.py owner --vendor copilot` reports that. An unnamed current user is not a switch. Ask who, and do not guess.

Confirm before switching. First one sentence that names the owner, for example `PR 71 on feat/orders-cicd is person A's.` Then this card:

Card: Should I add my work to their pull request?
- **Add to their pull request (Recommended)** (`switch`): build T5 on PR 71's branch so it lands in PR 71; I comment after each push and never merge it. Why: the branch is already theirs.
- **Keep it as my own** (`own`): build as usual, and I open and merge the pull request myself.
- **Stop** (`stop`): change nothing and end the walk here.

`switch` sets `Owner: other` in this branch's progress file. `own` keeps `Owner: self`. Do not switch before that word.

In other-owner mode the walk never opens a pull request, never merges the base into the branch, and never merges or completes the pull request. `allowed` from the script is false for those four. A phase that would have been one of them becomes a comment, or a wait, instead.

## A take-in task (1.186.0)

A task whose own work is taking the base into the branch is a take-in task: its line has `(take-in: develop)`, or, on a branch another person owns, its text says it takes in the base (`takes in develop`, `take in develop`, also `main` or `master`). The script infers that, so nobody adds the mark by hand. For that task, and only that task, `next` sets `allowed.take_in_base` true and returns the take-in `card`. The walk's own merge-base step stays forbidden, and `merge_pr` and `complete_pr` stay false.

After `take-in` (Recommended) on that card, the steps are the build steps:

1. `git fetch`, then `git merge --no-ff origin/<base>` on the branch. Never rebase and never force-push.
2. Resolve the conflicts inside the task's scope. A conflict outside it is a stop.
3. Run the whole suite and the linter. Write the task's `verify.md` row as `Implemented, verified, tick pending`.
4. Record `build <T#>` with the merge commit, then `verify` and `commit`.
5. Push after this run's yes, then one comment on the pull request, and record `comment`.

A check in the task that only the merge can pass, such as `the pull request is merged into develop`, waits with the tick. The ending names who merges: `Waiting: person A to merge pull request 7, then T2, T3 and T4 on feat/orders-fixes are ticked.`

After a push, write one pull request comment that says what was pushed. One push, one comment. Post it only after `yes`. The comment does not change the description.

`edit-description` is the only way to change the description, and only because this run asked. Without that word, leave the description as it is.

Ticks for tasks on this branch wait until that pull request is merged. The row stays `[ ]`. The Waiting line says it in plain words, for example `Waiting for person A to merge PR 71 before T5 is ticked.` Do not tick early.

Verify status in other-owner mode (1.171.0): after the build passes and is pushed, the worker writes the task's `verify.md` row as `Implemented, verified, tick pending` with the evidence it has (the local run, or the pipeline run at that commit), never `Not implemented`. The ready check already reads that status: the tick is the only leftover, and verify is not behind.
