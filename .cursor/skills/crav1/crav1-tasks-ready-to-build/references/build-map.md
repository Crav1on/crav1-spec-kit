# Build map (1.128.0)

Read this only when `scripts/build_map.py` cannot run. The script writes the file. Do not invent the map and do not hand-edit it.

Pick the interpreter as `crav1-docs/reference/running-scripts.md` says: `python3`, then `python`, then `py -3`. The Store alias message `Python was not found` means that command was not found. Try the next interpreter.

```text
<interpreter> <this skill folder>/scripts/build_map.py --root docs/specs
<interpreter> <this skill folder>/scripts/build_map.py --root docs/specs --scope "cc 1.0" --chat
<interpreter> <this skill folder>/scripts/build_map.py docs/specs/<slug>
```

`--chat` prints the short summary (the path and the waves). Without it the script prints one `Build map:` line per slice. Both write `docs/specs/<slug>/build-map.md`. `--stdout` prints and does not write. A folder with `spec.md` and no `tasks.md` is `no tasks yet (run /crav1-plan-from-spec)` and gets no file.

The file is committed with the spec. This command does not commit.

## What a row shows

Six things, and nothing else. No estimates. No file lists. No task ids anywhere in the file.

1. **Branch.** A short name in the kit's `feat/<slug>-<words>` shape. Words come from the step, with the small words dropped.
2. **Delivers.** One line, the step sentence, or the task titles when the branch is not the whole step.
3. **Tasks.** The task titles on that branch, separated by `;`.
4. **Waits for.** The other branches it waits for, or `none`. A dependency that names no task is `a dependency that names no task`.
5. **Question.** Each open question holding the branch, then who has the answer. Who comes from the question's own "Waiting for <who>" phrase, then the latest `Pending:` or `Asked:` line, otherwise `not named yet`.
6. **Ready now.** One of `ready`, `waiting on a question`, `waits in order`, `blocked`. A wait inside the same branch does not change this. `blocked` is a cycle, a dependency that names no task, a plan risk, or a missing plan.

Wave 1 is the branches that do not wait for another open branch. Wave 2 is what opens after those, and so on. A branch held only by a question can still sit in wave 1; Ready now says it is waiting. Blocked branches are listed under `## Blocked`, not in a wave. The flowchart at the top is `flowchart TD`. An arrow means the later branch waits for the earlier one.

## Grouping

Numbered items under `## Approach` are the plan steps. A step owns the tasks whose ids are written in that step. `(step: 1)` on a task line is the same link, and it wins when the step text names a different step. One branch per step.

`(map: feat/cancel-refund)` puts that task on the named branch instead. Tasks that name the same branch share it. Leave both marks off and the default stands.

When the plan has no steps, the file says `The plan has no steps, so this map uses one branch per task.` When the steps name no task, it says `The plan steps do not name tasks, so this map uses one branch per task.` A task the steps do not name gets its own branch, and the file says so. A cycle, or an `(after:)` that names no task, is listed under Blocked.

Done tasks are left out. When nothing is left, the file says `Nothing left to build.`
