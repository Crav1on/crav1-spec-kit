# Approval holds

Read this when a spec has `## Approval needed`, or when a task is waiting on a person.

An item under `## Approval needed` names the person (`Person:`), what they approve, and the tasks it holds (`Holds: T2, T4`). It is not an open question. `Blocks:` does not apply.

- No matching `Approved:` line: those tasks are **Waiting**, `approval "<item>" Waiting for <who>`. Who is `Person:`. When that line is missing, who is `not named yet`, and the task still counts.
- `Holds: none` holds no task.
- No `Holds:` line: hold the `T#` ids in the item text that exist in `tasks.md`. The reason stays recorded when `Holds:` is written.
- A `Holds:` line that is neither tasks nor `none` holds nothing. Do not hold the whole slice.
- A matching `Approved:` line (same person) clears the hold. The item stays. The line stays.
- A task that waits on a held task is held too, `held, waits on T#`. Who is the person on the item.

Other tasks still start. The result is `ready-partial` when some can start and some are held, and `not-ready` only when nothing can start. The ready check does not tick the task. A live `apply` still needs the user's own yes in that build run.

When Python runs, `scripts/approval_needed.py <spec.md>` (skill `crav1-record-approval`) prints the items. `walk_progress.py readiness --root <spec-folder>` applies them. `task_order.py` lists the same tasks under Waiting on approval.
