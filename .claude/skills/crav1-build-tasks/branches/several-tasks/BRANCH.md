# Orchestrate build-tasks workers

You **manage** the batch. You do **not** implement, verify, or `git commit` in this chat. Each `T#` runs in its own isolated **crav1-build-task-agent** worker (the “new chat” for that task).

Command: `/crav1-build-tasks`. One task: the one task branch of `/crav1-build-tasks`. Several specs (serial): `/crav1-build-features`.

Worker: `.claude/agents/crav1-build-task-agent.md` (plugin: `agents/crav1-build-task-agent.md`). Protocol: the one task branch of `crav1-build-tasks` [references/run.md](../../../crav1-build-tasks/branches/one-task/references/run.md). Style: [style-persist.md](../../../crav1-build-tasks/branches/one-task/references/style-persist.md). Approvals: [tool-approvals.md](../../../crav1-build-tasks/branches/one-task/references/tool-approvals.md).

## Which tasks

Spec folder: the user's @-mention, or the one folder `scripts/resolve_spec.py` prints (skill `crav1-tasks-ready-to-build`). Several matches: list them and stop. Do not pick the most recently edited tree. Need `tasks.md` or stop (`/crav1-plan-from-spec`).

| They typed | Queue |
| --- | --- |
| `T1-T3` / `T1–T3` | Inclusive ids that exist in `tasks.md`, in dependency order |
| `T1, T2, T5` | Those ids, in dependency order |
| No range / “all” / “rest” | Every remaining `- [ ]`, in dependency order |

Skip `[x]` unless they named a checked id (then say it is already done). Unknown ids: list, continue. Empty queue: stop.

**Dependency order (1.103.0).** Order the queue with `/crav1-tasks-ready-to-build` **Dependency order** (its `scripts/task_order.py` when Python runs; pick the interpreter as `crav1-docs/reference/running-scripts.md` says), not by task number. A recorded-merged task is under Needs tick, not Ready. Before each worker, run `scripts/tick_only.py` for that `T#`. When it reports tick-only, pass `--yes`, tick `[x]`, and start no worker, whatever the ready-check result, including `not-ready`. Do not re-implement. When the result is `not-ready`, do not start a worker and end the batch after that tick. Then check the next queued task with `walk_progress.py readiness --root` (skill `crav1-tighten-and-plan-ready-to-build`). When `result` is `ready` or `ready-partial`, start tasks in `can_start`. When `result` is `not-ready`, end the batch. A gate with `refused` true is held: say its `reason` and do not ask to build it anyway. Skip it and continue with the next task in `can_start` that does not depend on a held task. A task that only waits on a task this batch has not ticked still waits its turn. A cycle, or an `(after:)` that names no task, still ends the batch with that reason, and the question (build it anyway or pick another) stays for that blocker.

## Style once (rule from now on)

Before the first worker, follow **style-persist.md**. If you must ask, this turn is style only.

Do not ask again per `T#`. Workers must not ask style.

**Branch:** before tool approvals and the first worker, follow `/crav1-create-feature-branch` (skill `crav1-create-feature-branch`, `references/task-branch.md`) **Build** prompt. On a base branch it has no Stay and a headless run stops before any worker unless it has `new branch` (1.99.0, skill `crav1-create-feature-branch`, `references/code-branch.md`). If needed, that turn is branch only. Permissions are the next turn, on their own card. If an answer is missing or belongs on the other card, re-ask that one question (`scripts/ask_order.py`). Do not guess. If on `spec/<slug>`, stop (no workers) and follow **Build on a spec-only branch**. Pass `branch: already-done` on every worker. Workers must not create branches.

**Task branches (1.140.0).** Each task's branch is the first line of `scripts/build_map.py --recommend T#` (skill `crav1-tasks-ready-to-build`). A branch on the task line wins over the plan step. A merged or deleted branch is not that line. A missing sub-branch is offered as **Create X from <spec branch> (Recommended)** and gets its `(into …)` marker after the yes, as `references/task-branch.md` says. Work in queue order (dependency order). When that name is not the checkout and the branch exists, switch to it before its worker, only on a clean tree (workers commit, so it should be clean). Starting a range or all-tasks run is consent to use each task's recommended branch; do not ask per task when the branch exists. When the name exists nowhere, use the task-branch card once. Do not invent a different recommended name, and do not create it without a yes. A task whose recommended name is a base branch is `blocked: branch X is a base branch`; never switch to it. When X exists only as `origin/X`, `git checkout X` makes the local branch. A dirty tree stops the run before the switch. A name for another repo is blocked here with `belongs to <repo>`.

## Tool approvals (once for the batch)

Those **Allow / Stop** buttons on each worker are Cursor, not kit `fix`/`stop`. Follow [tool-approvals.md](../../../crav1-build-tasks/branches/one-task/references/tool-approvals.md) **once before the first worker** (pause, directions, wait for `continue` / `click` / `stop`).

When you launch a worker, pass **`approvals: already-done`**. Workers and the one task branch of `/crav1-build-tasks` must **not** pause again.

After `continue`, do not treat IDE Allow/Stop as a reason to halt the board. After `click`, still do not re-ask per `T#`.

## Batch loop (you stay in this chat)

Keep a short board: queued / running / done / blocked, with each task's branch when tasks name one.

For each `T#` **one at a time**:

1. Launch **crav1-build-task-agent** with spec folder, this `T#`, `resume: start`, `approvals: already-done`, `branch: already-done`, and “style persist is already set.”
2. Wait until that worker returns a STATUS block. Do not implement in parallel. Do not start `T+1` while this worker is open.
3. Handle STATUS:

| STATUS | Orchestrator |
| --- | --- |
| `done` | Mark done. Check the next queued `T#` is ready (above), then start it. |
| `needs_fix` | Ask the user `fix` / `stop` (this is their input). `fix` → **same T#** worker with `resume: fix` (still that task’s chat/worker, new launch is OK). Repeat until `done` or they `stop`. |
| `needs_ready` | Ask them to refresh the host, then `ready` / `stop`. `ready` → worker `resume: ready`. |
| `needs_dependency` | Show the BLOCKER line at the top. Ask start / skip / stop. `start` → worker `resume: dependency-start`; `skip` → `resume: dependency-skip`; `stop` → end. Headless: two-pass questions file. |
| `needs_yes` | Not blocked. Leave the task unticked and do not launch the next `T#`. Offer the Approval needed item as skill `crav1-build-tasks`, `references/approval-needed.md` says. End with `Waiting: <who>'s yes to <what>.` |
| `permission_refused` | Not a missing yes. The user's yes is on record and the assistant's permission check blocked the command. Follow `references/permission-block.md`. Leave the task unticked and do not launch the next `T#`. |
| `blocked` / `failed` | **End the batch.** Do not launch the next `T#`. A missing yes is `needs_yes`, not this row. A permission refusal with the yes on record is `permission_refused`, not this row. |
| User `stop` | End the batch. |

Do not skip a blocked `T#` unless they explicitly say skip. A `needs_yes` task is not blocked. A `NOTES:` line is the optional `.gitattributes` offer from the one-task branch. Accept is `resume: eol` on that worker. Skip adds nothing.

You may summarize each worker briefly on the board. Do not redo their implement/verify.

## After the batch

TL;DR: finished `T#`s, blocked `T#` + why, not started, commits the workers reported.

`Next: /crav1-open-pr, because the work is not on a pull request yet.` When the head's Match `Branch:` line ends in `(PR <n>)` or a pull request is known to be open for it, name it instead: `/crav1-open-pr` to push to PR <n> and update its description or comment. Do not run it from this skill.

When `/crav1-build-walk` opened this skill, do not print that line. The walk prints its one line (1.142.0).

If every selected task is `done`: one sentence that the requested slice is demoable (other unchecked `T#`s may remain if they passed a range).

Then follow **tool-approvals.md → Undo** once (restore the mode they wrote at the pause). Do not undo after each `T#`.

## Hard rules

- This chat is orchestration only: no product edits, no `git commit`, no push, no PR. The one `spec.md` write is an Approval needed item, as skill `crav1-build-tasks`, `references/approval-needed.md` says. Do not write `Approved:`.
- One worker per `T#` at a time. All phases of that `T#` belong to that worker, not to extra chats.
- Do not flatten the batch into one implement pass in this chat.
