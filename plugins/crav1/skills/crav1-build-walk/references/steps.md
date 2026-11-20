# Steps on one branch

Read this when a branch is chosen and the other route files do not apply. Open each file from this skill's folder. Follow it. Do not start the slash command.

Own mode, in order. A step with nothing to do says so, records `nothing-to-do`, and moves on.

1. Build the tasks on this branch. First check the code branch against origin (1.182.0): `<interpreter> -X utf8 scripts/repo_sync.py code-behind --repo <code repo> --branch <work branch> --task <T#>`. Behind: show its `card` (`fast-forward` or `stop`), which says the update is local and nothing is pushed (1.197.0), with each option's `result` line, and fast-forward only on `fast-forward`, with `--yes`; never fast-forward or pull silently. Diverged: stop and print its `ending`. In step, ahead, no upstream or offline: go on. Then open `../crav1-build-tasks/SKILL.md`. One worker per `T#`. A `(Runs live)` task follows the live file first; do not open that file from here when `SKILL.md` already sent you there.
2. Verify. Open `../crav1-verify-build-against-spec/SKILL.md`.
3. Commit. Show the commit card, then on `yes` open `../crav1-finalize-commit/SKILL.md`.
4. Open the pull request. On `yes`, open `../crav1-open-pr/SKILL.md`. That one yes is its push-and-open choice (1.198.0): show the draft, then push when the head is not on the remote yet and open the pull request, with no second card. An edit they ask for still gets the draft again first.
5. Merge the base into the branch. Name the base (`develop` when that is the into branch). On `yes`, `git merge <base>`. Never rebase. A branch that is not behind records `nothing-to-do`.
6. Merge the pull request. The `yes` card names the number. Then open `../crav1-merge-pr/SKILL.md`. If checks are red, or the PR record says not ready, wait. Do not invent a merge.
7. Tick a recorded-merged row that is still `[ ]`. On `yes`, follow the tick-only path in `../crav1-build-tasks/SKILL.md`. Do not re-implement.
8. The next task. Each branch whose tasks can start is its own Run next entry. None left, the one entry is verify (1.157.0):

```text
Run next:

`/crav1-verify-build-against-spec orders-capacity`
```

Other-owner mode skips steps 4, 5, and 6. After the commit, a push that already has a pull request gets one comment, posted after `yes`. The description stays unless this run said `edit-description`. The tick waits until that pull request is merged.

After you follow a step skill, do not print its Next line. Print `ending` from `build_walk.py next --json <file>` for the new phase. Pass `root` as the spec folder so another branch that can start is its own Run next entry.

Record the step in this branch's progress file after `yes`, with `Content stamp: normalized`. Commit that file in the same turn. When this step already commits other files, include `build-progress/<branch>.md` in that commit. Otherwise commit the progress file on its own after the yes. Use the persisted commit style. Nothing is pushed on that commit. The end-of-walk push is [sync.md](sync.md), after the last step or `stop`. A whole-branch run follows [branch-run.md](branch-run.md) for its commits and pushes instead.
