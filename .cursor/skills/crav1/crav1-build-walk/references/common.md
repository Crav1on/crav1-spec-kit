# Build walk, shared rules

Read this once, from `SKILL.md`. A step file does not repeat it.

The walk opens a step skill by its sibling path, for example `../crav1-build-tasks/SKILL.md`, and follows that file. It does not start a slash command. A command-only refusal is not a reason to stop. The rule is `crav1-docs/reference/open-skill-file.md`.

## The ending

Print `ending` from `scripts/build_walk.py next --root <spec folder> --branch <branch>` (1.172.0; `--json <file>` since 1.150.0). `Run next:` is first. Each command is alone in a code span. The next line names the branch and the short task name. Then `Waiting:` when a step is blocked or waits on a yes, then `Uncommitted:` when files are uncommitted. The ending has no `Next:` line (1.157.0). The JSON `next` list keeps one sentence per Run next entry, as data; do not print it. Your own prose has no `Next:` line either (1.198.0): what comes next is only the Run next block.

Each Run next label follows the step the branch is on (1.198.0): `Merge PR 71 for T5:`, `Check PR 71's merge for T5:`, `Tick T5, now that PR 71 is merged:`, `Verify T5 Retry on feat/orders-retry:`. Only the build step says `Build`. Task names are short: the first sentence, at most 120 characters, cut at a word.

**Kit update (1.198.0).** When a newer kit release is out, `next` adds `kit_update` (`Kit update available: <installed> -> <latest>`) and one Run next entry, `/crav1-update-kit`. Say that line once at the walk's start. The check is read-only (one `git ls-remote`, 5 second timeout, cached 12 hours) and says nothing when offline, when the installed version is unknown, or in the kit repo itself.

The step skill's own suggestion is not printed. That includes `/crav1-open-pr` after a build or a commit, and `/crav1-review-pr` after a pull request opens.

A new session has no earlier reply. The command is `/crav1-build-walk` plus each `T#` on that branch. When `docs/specs` has more than one slice, the slug is on that same line. One slice needs no slug.

In `wait-merge` the current branch is not a Run next entry when the Waiting line says why (1.171.0); running the walk again would only reprint the wait. Two or more tasks on one entry use the branch form, `/crav1-build-walk <slug> <branch>`, never a comma list of T#s, with one task per line under it. The `next` output has `lead`: one sentence from phase and owner, such as `T5 is pushed to PR 71 and waits for its merge.`, that agrees with the Uncommitted line. Print only that before `Run next:`.

Another branch whose tasks can start is its own Run next block, laid out as `crav1-docs/reference/run-ending.md` says (1.164.0). Since 1.155.0 that is the next task, `/crav1-build-walk <slug> T#`, and, when the branch has two or more open tasks (`open_tasks`), a second entry for the whole branch, `/crav1-build-walk <slug> <branch>`, with `branch <branch>, every open task: …` underneath. The script groups readiness `can_start` by build-map branch when `root` is the spec folder, or reads `ready_branches` when that list is already in the JSON. It does not bury those branches in the because text.

## next JSON

`<file>` is one object. `tasks` is a list. Each item is a string `"T3"` or `"T3 Apply the CI build policy"`, or an object `{"id": "T3", "title": "Apply the CI build policy"}`. `id` may be `T3` or `3`. Both are `T3`. A string that is not a T#, or an object with no `id`, is an error: `{"ok": false, "code": "tasks", "line": "..."}`. The command exits non-zero and prints no traceback.

| Field | Meaning |
| --- | --- |
| `phase` | The step the walk is on: `build`, `verify`, `commit`, `open-pr`, `merge-base`, `merge-pr`, `tick`, `next-task`, `comment`, `wait-merge`, `approval`, `live-dry`, `live-yes`, `permission-refused`, `confirm-owner`. Omitted: the script derives it |
| `owner` | `self` or `other` |
| `branch` | The work branch, for example `feat/orders-api-record` |
| `tasks` | The tasks on this branch. Strings or `{id, title}` objects |
| `base` | The branch this one merges back into. Default `develop` |
| `pr` | The pull request number, when one is open |
| `slug` | The slice, for example `orders-api`. On the command when the repo has more than one slice |
| `root` | The spec folder. When set, readiness `can_start` is grouped by build-map branch |
| `spec_count` | How many slices are under `docs/specs`. `1` omits the slug |
| `ready_branches` | Optional list of `{branch, tasks}` that can start now. Used when `root` is omitted |
| `branches` | Grouping mode only. One object per ready branch, same shape as `ready_branches` |
| `mode` | `walk` or `grouping` |
| `waiting` | Optional Waiting line |
| `catch_up` | Optional. The ready check's `catch_up` text, or `{"slug", "behind", "orphans", "ahead"}`; it leads Run next as the `**Catch up first**` block (1.167.0) |
| `uncommitted` | Optional Uncommitted line |
| `next_branch` | The next branch when `phase` is `next-task` and no ready list is present |
| `next_tasks` | Tasks on `next_branch` |

## Yes before a write

A step that writes, pushes, opens, or merges shows the action in one sentence, then one card that names the action and its target:

Card: Commit these 3 files on feat/orders-cicd?
- **Commit them (Recommended)** (`yes`): commit the files shown, then the walk opens the commit step. Why: the step is done and checked.
- **Stop here** (`stop`): write nothing and pause the walk at this step.

Show each option by its plain label only (1.198.0). The word in backticks (`yes`, `stop`, `fast-forward`, `dependency-skip`) is the answer's id, never a `yes:` or `stop:` prefix on the label. A script card's `result` is plain text under the card, such as `On yes: fast-forwards your local develop. Nothing is pushed.`

`yes` does that action and then the walk opens the step skill. `stop` does not. There is no Edits option. A missing word is asked again. Do not guess.

The card that merges names the pull request number:

Card: Merge PR 71 into develop?
- **Merge PR 71 (Recommended)** (`yes`): merge PR 71 now, then the walk opens the merge step. Why: its checks are green and the record says ready.
- **Not yet** (`stop`): leave PR 71 open, commit and push the walk's specs files, and pause the walk.

`Not yet` covers the specs-repo settle in [sync.md](sync.md) (1.198.0): no second card for that push.

That `yes` is the explicit ask `/crav1-merge-pr` requires. The walk opens `../crav1-merge-pr/SKILL.md` only after it.

Never rebase. A branch that is behind is fixed by merging the base into it, after `yes`.

The specs repo is fetched before this walk reads the spec folder, and a claim is pushed when it starts on a branch (1.151.0). Those rules are [sync.md](sync.md) and [claims.md](claims.md).

## Script

`scripts/build_walk.py` in this skill. The interpreter is `crav1-docs/reference/running-scripts.md`. The kit repo wrapper is `scripts/build-walk.py`. Pass state with `--root` and `--branch`, or as `--json` (see State from files). The script does not push, open, merge, or run a live change.

## State from files (1.172.0)

`scripts/build_walk.py next --root docs/specs/<slug> --branch <branch>` builds the next JSON itself: `phase` and `owner` from the last step in `build-progress/<branch>.md` (a `done` step moves to the next step in order; `comment` done is `wait-merge`), `pr` from that file, task names from `tasks.md`, `uncommitted` from `git status` of the spec folder, and `root`, so readiness fills the other branches. `--waiting`, `--who` and `--pr` add what the files do not hold. `--code-repo <checkout>` (or the progress header's `Code repo:` line) lets it check whether the branch is really behind its base before it says so (1.198.0): not behind skips to the merge, and an unknown count is phrased as a check, not a fact. Do not hand-write the JSON or rerun the script only to add `uncommitted`.

The progress file is written by the script, never by hand:

- `build_walk.py progress init --root <spec> --branch <branch> --owner self --tasks T3,T4 --cut-from develop --yes` writes the header.
- `build_walk.py progress record --root <spec> --branch <branch> --step build --result done --yes` adds one step with `Done`, `Result` and the normalized stamps. `--step build,verify,commit` records several steps with the same result in one call, and `--pr 71` adds `(PR 71)` to an `open-pr` result (1.198.0). A `nothing-to-do` (or `skipped`, `not needed`) result moves the walk on like `done`.

Without `--yes` each prints a preview and writes nothing. Never write the progress file or the next JSON by hand.

When the progress file's last step is `comment` or `wait-merge` and no task on that branch can start, the walk only waits on a merge: print `lead` and `ending` from `next --root --branch` and stop, with no other reference read.

## Starting a task on a waiting branch (1.186.0)

`next --root <spec> --task <T#>` asks `task_state.walk_start`, the same answer the ready check uses before it offers a task. The ready check offers `/crav1-build-walk <slug> <T#>` only when that answer is startable (invariant I8). Wait-merge applies only once every task on the branch is pushed: an open, unclaimed task whose dependencies are done starts as new work, and `next --branch` picks it too. The JSON then has `start` (`task`, `claim_needed`, `header_needed`, `take_in`, and the `command`). After the start yes, run that one command:

- `build_walk.py progress start-task --root <spec> --branch <branch> --task <T#> --user "<name>" --yes` writes the `In progress:` line in `claims.md`, adds the task to the header's `Tasks:` line, and records `- Step: start <T#>`. A second call writes nothing new. The steps that follow are that task's.

A named task that cannot start (`phase: cannot-start`: held by an open dependency, claimed by someone else, or not in `tasks.md`) gets the script's `card` (`check-ready` recommended, or `stop`) and an `ending` with Run next first and the Waiting line. Print those as they are. The walk passes `approvals: already-done` to the one-task build, which then does not open `tool-approvals.md`.
