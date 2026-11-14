# Build walk, shared rules

Read this once, from `SKILL.md`. A step file does not repeat it.

The walk opens a step skill by its sibling path, for example `../crav1-build-tasks/SKILL.md`, and follows that file. It does not start a slash command. A command-only refusal is not a reason to stop. The rule is `crav1-docs/reference/open-skill-file.md`.

## The ending

Print `ending` from `scripts/build_walk.py next --json <file>` (1.150.0). `Run next:` is first. Each command is alone in a code span. The next line names the branch and the short task name. Then `Waiting:` when a step is blocked or waits on a yes, then `Uncommitted:` when files are uncommitted. The ending has no `Next:` line (1.157.0). The JSON `next` list keeps one sentence per Run next entry, as data; do not print it.

The step skill's own suggestion is not printed. That includes `/crav1-open-pr` after a build or a commit, and `/crav1-review-pr` after a pull request opens.

A new session has no earlier reply. The command is `/crav1-build-walk` plus each `T#` on that branch. When `docs/specs` has more than one slice, the slug is on that same line. One slice needs no slug.

Another branch whose tasks can start is its own Run next entry. Since 1.155.0 that is the next task, `/crav1-build-walk <slug> T#`, and, when the branch has two or more open tasks (`open_tasks`), a second entry for the whole branch, `/crav1-build-walk <slug> <branch>`, with `branch <branch>, every open task: …` underneath. The script groups readiness `can_start` by build-map branch when `root` is the spec folder, or reads `ready_branches` when that list is already in the JSON. It does not bury those branches in the because text.

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
| `uncommitted` | Optional Uncommitted line |
| `next_branch` | The next branch when `phase` is `next-task` and no ready list is present |
| `next_tasks` | Tasks on `next_branch` |

## Yes before a write

A step that writes, pushes, opens, or merges shows the action, then one card. `yes` (Recommended) does that action and then the walk opens the step skill. `stop` does not. There is no Edits option. A missing word is asked again. Do not guess.

The card that merges names the pull request number. That `yes` is the explicit ask `/crav1-merge-pr` requires. The walk opens `../crav1-merge-pr/SKILL.md` only after it.

Never rebase. A branch that is behind is fixed by merging the base into it, after `yes`.

The specs repo is fetched before this walk reads the spec folder, and a claim is pushed when it starts on a branch (1.151.0). Those rules are [sync.md](sync.md) and [claims.md](claims.md).

## Script

`scripts/build_walk.py` in this skill. The interpreter is `crav1-docs/reference/running-scripts.md`. The kit repo wrapper is `scripts/build-walk.py`. Pass state as `--json`. The script does not push, open, merge, or run a live change.
