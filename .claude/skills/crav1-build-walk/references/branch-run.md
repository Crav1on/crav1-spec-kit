# Whole-branch run (1.155.0)

Read this when the invocation names a branch, for example `/crav1-build-walk orders-api feat/orders-cicd`, and nothing else. A `T#` still builds that task the usual way. The script is `scripts/branch_run.py` in this skill. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says.

`<interpreter> -X utf8 scripts/branch_run.py parse --root docs/specs --args "<what followed the command>"` says `task`, `branch`, or `pick`. Any other answer is a stop: say its `line`.

## Start

1. Fetch first, as [sync.md](sync.md) says.
2. `<interpreter> -X utf8 scripts/branch_run.py plan --root <spec-folder> --branch <branch> --user "<git user.name>"` lists the open tasks on that branch in task order, each with the stop that holds it.
3. `<interpreter> -X utf8 scripts/branch_run.py start --root <spec-folder> --branch <branch> --user "<name>"` (no `--yes`) shows what the run will do. Show the tasks in order, the first stop if there is one, and the claim line. Then one card:

   Card: Build every open task on feat/orders-cicd, in this order?
   - **Build them all (Recommended)** (`yes`): claim the tasks, build them one by one and push, pausing only at a real stop. Why: one yes covers the whole run.
   - **Stop** (`stop`): claim nothing and build nothing.

   A headless run stops and names `yes` and `stop`.
4. On `yes`, rerun `start` with `--yes`. It writes one claim line that names every open task on the branch, the `## Run` section of `build-progress/<branch>.md`, and this branch's one status line in `walk-progress.md`. Commit `claims.md`, `walk-progress.md`, and the progress file with `start`'s `commit_message` plus the work-item mention from `work-item.md`, and push. Do not open finalize-commit for that commit, and do not read `stack.md` unless the branch's `Cut from:` is not the base (1.176.0). This yes covers every commit and push in the run. There is no other card until a stop.

`start` returns `claimed` when someone else holds one of those tasks. Say who and since when, and stop.

## Each task

Before each task:

1. `<interpreter> -X utf8 scripts/repo_sync.py status --repo <repo>`. Behind or diverged: run `merge-upstream --yes` (merge, never rebase). A conflict is a stop: name the files.
2. `<interpreter> -X utf8 scripts/branch_run.py guard --root <spec-folder> --branch <branch> --user "<name>" --repo <repo>`. `stop: true` means someone else claimed or changed one of this run's tasks. Say its `line`, which names who and what, and stop.

Then build the task, as [steps.md](steps.md) step 1 says, for that one task. Run its tests and lint. Commit it with the persisted commit style. This run's start yes is the commit yes.

After the task, fill a JSON file and run `<interpreter> -X utf8 scripts/branch_run.py after --json <file>` with `task`, `next`, `next_stop` (the next task's `stop` from `plan`), `tests` (`green`, `red`, or `none`), `attempts`, `out_of_scope`, `done_in_session`, `hint_every`, and `command` (this run's command).

- `action: fix`: fix and test again. A fair try is three attempts unless the JSON says `fair_try`.
- `action: continue`: run `<interpreter> -X utf8 scripts/branch_run.py record --root <spec-folder> --branch <branch> --task <T#> --commit <sha> --tests <result> --code-repo <code repo> --push`. The specs repo is the git top level of `--root` (or `--specs-repo <path>`); the code repo is `--code-repo`, the same path as in `guard` (1.176.0). It checks both paths before it writes anything. It writes the task to the run section, updates this branch's status line in `walk-progress.md` (for example `running, T9 done, next T10`, or `stopped before merge` after the last task), commits the progress file, `claims.md`, `walk-progress.md` and `verify.md` in one specs-repo commit that ends with the work-item mention, pushes the work branch in the code repo and pushes the specs repo. Record the verify row before this command, so it is in the same commit: a task whose checks passed on this unmerged branch is `Implemented, verified on branch`, with the branch, the commit and the PR in the evidence (`verify_rows.py set --file <spec-folder>/verify.md --task <T#> --status "Implemented, verified on branch" --evidence "<checks> at <sha> on <branch>, PR <n> open"`), never `Not implemented`. A check that can only pass after the merge is pending, not failed (1.176.0). When specs and code are one repo, pass that repo as `--code-repo` or leave it out. Then print the single `line`, for example `T9 done, tests green, starting T10`, and go on. Do not ask.
- `stop: true`: record the task if it was built, then end as below.

The hint about a fresh session is part of the progress line after every `hint_every` tasks (default 3, or `Fresh session hint: every N tasks` in the run section). It is never a stop.

## One place to look (1.155.0)

`walk-progress.md` stays the one file every skill reads. A branch run owns one line there, and changes only that line:

```text
- Branch run: feat/orders-cicd: running, T9 done, next T10 (2026-11-14T09:40:00+01:00). Log: build-progress/feat--orders-cicd.md
```

The detailed log stays in the `## Run` section of the build-progress file. A stop partway writes `stopped at T4: <why>`, and the merge writes `merged`, with `<interpreter> -X utf8 scripts/branch_run.py status --root <spec-folder> --branch <branch> --state "<state>"`. The ready check and tighten-and-plan print every line that is not `merged`. When another session changed the file too, a merge conflict that is only these lines, or only hash lines, is settled with `<interpreter> -X utf8 scripts/walk_progress.py resolve-stamps --root <spec-folder> --yes` (skill `crav1-tighten-and-plan-ready-to-build`): each branch keeps its newest line.

## Stops

Only these stop the run: an open question on the next task; a stakeholder yes that is not recorded; a `(manual …)`, `(… secret)`, `(host setup)`, or `(Runs live)` step; tests or lint still red after a fair try; a wanted change outside the task's scope; someone else's claim or change; a sync conflict or a rejected push; and, always, the pull request merge. Do not stop for anything else, and never show a continue card between tasks.

A stop before the merge keeps the claim. `release-claim` clears it, as [claims.md](claims.md) says.

## Resume

Rerun the same command. `start` reads the run section, reports `resume: true`, `claim: reuse`, and the next open task. It writes no new claim and asks no new card. Tasks already in `- Built:` lines are not built again.

## The stop before the merge

When every task is built, open or update the pull request yourself: open `../crav1-open-pr/SKILL.md` and follow it. The start yes covers that push. Never merge here. The merge is the next run of this command, through the existing merge card in [steps.md](steps.md).

Build the ending with `<interpreter> -X utf8 scripts/branch_run.py ending --root <spec-folder> --branch <branch>` (1.176.0). It reads `build-progress/<branch>.md`, `tasks.md` and the ready check itself: the pull request, the base, what was built with full task names, the first stop, and the other ready branches. Do not hand-build a JSON file. Pass each note the user needs before the merge (an approver, a conflict, a limit) as `--note "<one sentence>"`; the script prints them under `Before the merge:` after what was built, so nothing goes above Run next. `--json <file>` still works for extra fields (`skipped`, `questions`, `verify_behind`), and a plain `"stop": "merge"` is accepted. Print it as is: Run next first, each command alone in its own code span on its own line (another ready branch gets its next task, plus the whole branch when it has two or more open tasks), then what was built, one line per task with its commit and test result, then what is left. A stop partway uses the same script with that `stop`.
