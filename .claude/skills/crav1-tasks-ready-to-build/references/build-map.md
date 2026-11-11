# Build map (1.129.0)

Read this only when `scripts/build_map.py` cannot run. The script writes the file. Do not invent the map and do not hand-edit it.

Pick the interpreter as `crav1-docs/reference/running-scripts.md` says: `python3`, then `python`, then `py -3`. The Store alias message `Python was not found` means that command was not found. Try the next interpreter.

```text
<interpreter> <this skill folder>/scripts/build_map.py --root docs/specs
<interpreter> <this skill folder>/scripts/build_map.py --root docs/specs --scope "cc 1.0" --chat
<interpreter> <this skill folder>/scripts/build_map.py docs/specs/<slug>
<interpreter> <this skill folder>/scripts/build_map.py docs/specs/<slug> --recommend T1
```

`--recommend T1` prints that open task's row branch and does not write the file. `/crav1-build-tasks` and the Build prompt use that line as option 1. It is the same name the file uses for the row.

`--chat` prints the short summary: the path, each wave's parallel count, then that wave's `Overlap:` lines, one per pair, in the same words as the file. Without it the script prints one `Build map:` line per slice. The ready-check list keeps that one line. Both write `docs/specs/<slug>/build-map.md`. `--stdout` prints and does not write. A folder with `spec.md` and no `tasks.md` is `no tasks yet (run /crav1-plan-from-spec)` and gets no file.

The file is committed with the spec. This command does not commit.

## What a row shows

Six things, and nothing else, plus one note when the task text names a different branch. No estimates. No file lists. No task ids anywhere in the file.

1. **Branch.** The task's branch, in this order: `(map: <branch>)`, else `(branch: <branch>)`, else the plan step's `feat/<slug>-<words>` name, else a branch named as `committed later on <branch>` when the task is not on a step, else `feat/<slug>-<words>` from the task. A repo prefix on a mark is dropped. Words in a generated name come from the step or the task, with the small words dropped.
2. **Delivers.** One line, the step sentence, or the short task names when the branch is not the whole step. A task id is replaced with that task's short name. A removed id does not leave a dangling `'s`, an empty `()`, a leading comma, or a double space.
3. **Tasks.** One short name per task, separated by `; `. The short name is the `task: T# <title>` line in the slice's `work-item.md` when that line exists. Otherwise it is the task text up to the first ` (`, `, in `, or sentence end, at most about 80 characters. Marks such as `(host setup)`, `(manual, secret)`, `(verify: …)`, `(spec: …)`, `(after: …)`, and branch prefixes are dropped.
4. **Waits for.** The other branches it waits for, or `none`. A dependency that names no task is `a dependency that names no task`.
5. **Question.** Each open question holding the branch, then who has the answer. Who comes from the question's own "Waiting for <who>" phrase, then the latest `Pending:` or `Asked:` line, otherwise `not named yet`.
6. **Ready now.** One of `ready`, `waiting on a question`, `waits in order`, `blocked`. A wait inside the same branch does not change this. `blocked` is a cycle, a dependency that names no task, a plan risk, or a missing plan.

When the row branch differs from a branch named in the task text (`(branch: …)`, `committed later on <branch>`, or another `feat/…` name), the row adds one line: `Task text names feat/orders-cicd; built on feat/orders-retry`. The row's own name is not listed. The note does not change Ready now or the wave.

Wave 1 is the branches that do not wait for another open branch. Wave 2 is what opens after those, and so on. A branch held only by a question can still sit in wave 1; Ready now says it is waiting. The wave heading is always `N branch, M can start now` or `N branches, M can start now`, including one branch (`Wave 1: 1 branch, 1 can start now`) and a wave where every branch can start (`Wave 1: 3 branches, 3 can start now`). A question hold lowers M (`Wave 1: 3 branches, 2 can start now`, or `Wave 1: 1 branch, 0 can start now`). That count is also the first part of each wave line in the `build-map` summary. Each `Overlap:` line for that wave follows it, one pair per line. Blocked branches are listed under `## Blocked`, not in a wave.

The flowchart is `flowchart LR`. Each wave is one subgraph, with `direction TB` inside, so the branches in a wave sit side by side across the page and one above another inside the wave. An arrow means the later branch waits for the earlier one.

Under a wave, an `Overlap:` line names a pair of branches in that wave that share a requirement or a path. A requirement is the text of `(spec: …)` on a task, compared with case folded and extra space collapsed. A path is a backtick span in the task line that contains `/` or a file extension, compared exactly as written. The plan's file list is not used. The note does not block, and it does not change Ready now or which wave a branch is in. A branch row still has the six fields above, and still no file list.

## Grouping

Numbered items under `## Approach` are the plan steps. A step owns the tasks whose ids are written in that step. `(step: 1)` on a task line is the same link, and it wins when the step text names a different step. One branch per step.

`(map: feat/cancel-refund)` puts that task on the named branch instead. `(branch: feat/orders-retry)` does the same when no `(map:)` is set. Tasks that resolve to the same name share it. Leave the marks off and the task stays on its plan step. A task that is not on a step and says `committed later on feat/orders-cicd` uses that branch.

When the plan has no steps, the file says `The plan has no steps, so this map uses one branch per task.` When the steps name no task, it says `The plan steps do not name tasks, so this map uses one branch per task.` A task the steps do not name gets its own branch, and the file says so. A cycle, or an `(after:)` that names no task, is listed under Blocked.

Done tasks are left out. When nothing is left, the file says `Nothing left to build.`
