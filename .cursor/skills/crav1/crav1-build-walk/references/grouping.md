# Ready branches

Read this when no branch is chosen, including when the user started from a ready-to-build report.

Run `scripts/build_walk.py next --json <file>` with `"mode": "grouping"`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Each ready branch is one parallel piece of work. The report prints one next line per branch. The line names each task as `T#` plus the short name, then the branch.

```text
Next: /crav1-build-walk T3 Apply the CI build policy, because that work is on feat/orders-host-setup-scripts.
```

One branch is still one line. A task that needs code from an unmerged branch is not offered as a second ready branch on `develop`. `SKILL.md` sends that case to the stack file. Do not open it from here.

The branch name is `scripts/build_map.py --recommend` through `build_walk.py offer`. A merged or deleted branch is not offered. The card says where the name came from: the task line, the build map, or new. A `because:` line is the description when a name was skipped, for example `New, because feat/orders-one-commit-cleanup-main is already merged.`

Pick one branch, then stop this file. The next turn reads progress, not this file. One checkout follows one branch.
