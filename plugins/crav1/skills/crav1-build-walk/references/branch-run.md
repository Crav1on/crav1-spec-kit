# Whole-branch run (1.155.0)

Read this when the invocation names a branch, for example `/crav1-build-walk orders-api feat/orders-cicd`, and nothing else. A `T#` still builds that task the usual way. The script is `scripts/branch_run.py` in this skill. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says.

`<interpreter> -X utf8 scripts/branch_run.py parse --root docs/specs --args "<what followed the command>"` says `task`, `branch`, or `pick`. Any other answer is a stop: say its `line`.

## Start

1. Fetch first, as [sync.md](sync.md) says.
2. `<interpreter> -X utf8 scripts/branch_run.py plan --root <spec-folder> --branch <branch> --user "<git user.name>"` lists the open tasks on that branch in task order, each with the stop that holds it.
3. `<interpreter> -X utf8 scripts/branch_run.py start --root <spec-folder> --branch <branch> --user "<name>"` (no `--yes`) shows what the run will do. Show the tasks in order, the first stop if there is one, and the claim line. Then one card: `yes` (Recommended) or `stop`. A headless run stops and names `yes` and `stop`.
4. On `yes`, rerun `start` with `--yes`. It writes one claim line that names every open task on the branch and the `## Run` section of `build-progress/<branch>.md`. Commit `claims.md` and the progress file, and push. This yes covers every commit and push in the run. There is no other card until a stop.

`start` returns `claimed` when someone else holds one of those tasks. Say who and since when, and stop.

## Each task

Before each task:

1. `<interpreter> -X utf8 scripts/repo_sync.py status --repo <repo>`. Behind or diverged: run `merge-upstream --yes` (merge, never rebase). A conflict is a stop: name the files.
2. `<interpreter> -X utf8 scripts/branch_run.py guard --root <spec-folder> --branch <branch> --user "<name>" --repo <repo>`. `stop: true` means someone else claimed or changed one of this run's tasks. Say its `line`, which names who and what, and stop.

Then build the task, as [steps.md](steps.md) step 1 says, for that one task. Run its tests and lint. Commit it with the persisted commit style. This run's start yes is the commit yes.

After the task, fill a JSON file and run `<interpreter> -X utf8 scripts/branch_run.py after --json <file>` with `task`, `next`, `next_stop` (the next task's `stop` from `plan`), `tests` (`green`, `red`, or `none`), `attempts`, `out_of_scope`, `done_in_session`, `hint_every`, and `command` (this run's command).

- `action: fix`: fix and test again. A fair try is three attempts unless the JSON says `fair_try`.
- `action: continue`: run `<interpreter> -X utf8 scripts/branch_run.py record --root <spec-folder> --branch <branch> --task <T#> --commit <sha> --tests <result> --repo <repo> --push`. It writes the task to the run section, commits it, and pushes the branch. Then print the single `line`, for example `T9 done, tests green, starting T10`, and go on. Do not ask.
- `stop: true`: record the task if it was built, then end as below.

The hint about a fresh session is part of the progress line after every `hint_every` tasks (default 3, or `Fresh session hint: every N tasks` in the run section). It is never a stop.

## Stops

Only these stop the run: an open question on the next task; a stakeholder yes that is not recorded; a `(manual …)`, `(… secret)`, `(host setup)`, or `(Runs live)` step; tests or lint still red after a fair try; a wanted change outside the task's scope; someone else's claim or change; a sync conflict or a rejected push; and, always, the pull request merge. Do not stop for anything else, and never show a continue card between tasks.

A stop before the merge keeps the claim. `release claim` clears it, as [claims.md](claims.md) says.

## Resume

Rerun the same command. `start` reads the run section, reports `resume: true`, `claim: reuse`, and the next open task. It writes no new claim and asks no new card. Tasks already in `- Built:` lines are not built again.

## The stop before the merge

When every task is built, open or update the pull request yourself: open `../crav1-open-pr/SKILL.md` and follow it. The start yes covers that push. Never merge here. The merge is the next run of this command, through the existing merge card in [steps.md](steps.md).

Build the ending with `<interpreter> -X utf8 scripts/branch_run.py ending --json <file>` (`slug`, `branch`, `pr`, `base`, `stop`, `built`, `skipped`, `questions`, `verify_behind`, `ready_branches`). Print it as is: Run next first, each command alone in its own code span on its own line, then what was built, one line per task with its commit and test result, then what is left. A stop partway uses the same script with that `stop`.
