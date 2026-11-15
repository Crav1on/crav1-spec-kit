# Ready branches

Read this when no branch is chosen, including when the user started from a ready-to-build report.

Run `scripts/build_walk.py next --json <file>` with `"mode": "grouping"`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Each ready branch is one parallel piece of work. The ending prints one Run next entry per branch, and no `Next:` line (1.157.0). The line names each task as `T#` plus the short name, then the branch.

```text
Run next:

`/crav1-build-walk T3`
branch feat/orders-host-setup-scripts, T3 Apply the CI build policy
```

Each branch is one Run next block (1.164.0): the bold branch, its open tasks, then `Run the whole branch:` and `Run only T#, the first task:` when it has two or more open tasks, or `Run T#:` with one. Each command is alone in the code span. A `---` line stands between two blocks, tasks are listed in walk order, and a task that cannot start yet says why, `(waits on T5)` (1.165.0). A task that needs code from an unmerged branch is not offered as a second ready branch on `develop`. `SKILL.md` sends that case to the stack file. Do not open it from here.

The branch name is `scripts/build_map.py docs/specs/<slug> --recommend T#` (skill `crav1-tasks-ready-to-build`) through `build_walk.py offer`. A merged or deleted branch is not offered. A task-line branch that is only on origin, or is the head of an open pull request, prints a `checkout:` line: `git checkout <name>` makes the local tracking branch, with no card, in the `repo:` checkout when one is printed (1.160.0). The card says where the name came from: the task line, the build map, or new. A `because:` line is the description when a name was skipped, for example `New, because feat/orders-one-commit-cleanup-main is already merged.`

Pick one branch, then stop this file. The next turn reads progress, not this file. One checkout follows one branch.
