# The reply

The verify chat reply is brief (1.168.0). One script builds it, the shared ending script of skill `crav1-tasks-ready-to-build` (this skill ships a wrapper). Write a small JSON state file in the system temp folder, then run, as `crav1-docs/reference/running-scripts.md` says:

```text
<interpreter> -X utf8 scripts/walk_ending.py --verify <state file> --vendor codex
```

Print its output once, as-is. Do not add a lead recap longer than one sentence, a `Next:` line, the TL;DR, a table, per-task bullets, branch or promotion detail. Those stay in `verify.md`.

## The state

`root` is the spec folder, for example `docs/specs/orders-api`. From it the script reads the counts (the TL;DR table), the tasks whose state changed (the Tasks overview against the committed `verify.md`, `git show HEAD:`), `tasks.md`, the uncommitted files this run wrote (`verify.md` by default; `written` lists more, such as `tasks.md` after a tick) and how far the specs repo is ahead of origin. You add only what you judged:

- `steps`: the next step from the case file, a list of `{"reason", "label", "command"}`. The reason once, the label on its own line, the command alone in its code span. One entry per ready branch when the case says so, with `heading` set to the branch.
- `plan_notes`: a plan note the user can settle now, such as `The plan says T24 to T26 may belong to another slice`. Catch up first gives `$crav1-tighten-plan <slug>`.
- `waiting`: only what the user cannot act on now, such as a person's review or a merge.
- `full`: `true` with the word `full`. The TL;DR and the Tasks overview follow the Result line.
- `walk`: `true` when `$crav1-build-walk` opened this skill. The walk owns Run next.

```json
{"root": "docs/specs/orders-api",
 "steps": [{"reason": "T6's four tests fail on stale asserts at the PR's tip.", "label": "Fix T6:", "command": "$crav1-fix-build-gaps orders-api T6"}],
 "plan_notes": ["The plan says T24 to T26 may belong to another slice"]}
```

## The shape

```text
Verify — orders-api

Result: 2 verified, 1 failed, 1 not implemented.

Changed since the last verify:
- T6 failed: 4 cursor tests fail at the PR's tip
- T44 row dropped: not in tasks.md

Run next:

**Catch up first**
The plan says T24 to T26 may belong to another slice. verify.md is not committed.

Settle the plan note in the plan:
`$crav1-tighten-plan orders-api`
Commit verify.md:
`$crav1-finalize-commit`
Then push the specs repo:
`git push`

---

T6's four tests fail on stale asserts at the PR's tip.

Fix T6:
`$crav1-fix-build-gaps orders-api T6`

Report: docs/specs/orders-api/verify.md
```

Catch up first is left out when nothing is behind. A run with no step and nothing behind says `Nothing needed now.` under Run next. With no previous `verify.md`, there are no changed-task lines. The commit is `$crav1-finalize-commit`, which never pushes, so the push is its own label and command.
