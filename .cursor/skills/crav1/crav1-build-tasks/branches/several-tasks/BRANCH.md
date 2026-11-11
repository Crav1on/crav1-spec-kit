# Orchestrate build-tasks workers

You **manage** the batch. You do **not** implement, verify, or `git commit` in this chat. Each `T#` runs in its own isolated **crav1-build-task-agent** worker (the “new chat” for that task).

Command: `/crav1-build-tasks`. One task: the one task branch of `/crav1-build-tasks`. Several specs (serial): `/crav1-build-features`.

Worker: `.cursor/agents/crav1-build-task-agent.md` (plugin: `agents/crav1-build-task-agent.md`). Protocol: the one task branch of `crav1-build-tasks` [references/run.md](../../../crav1-build-tasks/branches/one-task/references/run.md). Style: [style-persist.md](../../../crav1-build-tasks/branches/one-task/references/style-persist.md). Approvals: [tool-approvals.md](../../../crav1-build-tasks/branches/one-task/references/tool-approvals.md).

## Which tasks

Spec folder: user @-mention, else most recently edited `docs/specs/` excluding `_template/`. Need `tasks.md` or stop (`/crav1-plan-from-spec`).

| They typed | Queue |
| --- | --- |
| `T1-T3` / `T1–T3` | Inclusive ids that exist in `tasks.md`, in dependency order |
| `T1, T2, T5` | Those ids, in dependency order |
| No range / “all” / “rest” | Every remaining `- [ ]`, in dependency order |

Skip `[x]` unless they named a checked id (then say it is already done). Unknown ids: list, continue. Empty queue: stop.

**Dependency order (1.103.0).** Order the queue with `/crav1-tasks-ready-to-build` **Dependency order** (its `scripts/task_order.py` when Python runs; pick the interpreter as `crav1-docs/reference/running-scripts.md` says), not by task number. Before each worker, check the next queued task again with its rules: when it is still blocked (it waits on a task that is not ticked, an open question, or a cycle), end the batch there with that reason. Do not jump to a later queued task.

## Style once (rule from now on)

Before the first worker, follow **style-persist.md**. If you must ask, this turn is style only.

Do not ask again per `T#`. Workers must not ask style.

**Branch:** before tool approvals and the first worker, follow `/crav1-create-feature-branch` (skill `crav1-create-feature-branch`, `references/task-branch.md`) **Build** prompt. On a base branch it has no Stay and a headless run stops before any worker unless it has `new branch` (1.99.0, skill `crav1-create-feature-branch`, `references/code-branch.md`). If needed, that turn is branch only. Permissions are the next turn, on their own card. If an answer is missing or belongs on the other card, re-ask that one question (`scripts/ask_order.py`). Do not guess. If on `spec/<slug>`, stop (no workers) and follow **Build on a spec-only branch**. Pass `branch: already-done` on every worker. Workers must not create branches.

**Task branches (1.129.0).** Each task's branch is the name `scripts/build_map.py --recommend T#` prints (skill `crav1-tasks-ready-to-build`), the same name as its build map row. A missing sub-branch is offered as **Create X from <spec branch> (Recommended)** and gets its `(into …)` marker after the yes, as `references/task-branch.md` says. Work in queue order (dependency order). When that name is not the checkout and the branch exists, switch to it before its worker, only on a clean tree (workers commit, so it should be clean). Starting a range or all-tasks run is consent to use each task's recommended branch; do not ask per task when the branch exists. When the name exists nowhere, use the task-branch card once. Do not invent a different recommended name, and do not create it without a yes. A task whose recommended name is a base branch is `blocked: branch X is a base branch`; never switch to it. When X exists only as `origin/X`, `git checkout X` makes the local branch. A dirty tree stops the run before the switch. A name for another repo is blocked here with `belongs to <repo>`.

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
| `needs_yes` | Not blocked. Leave the task unticked and do not launch the next `T#`. End with `Waiting: <who>'s yes to <what>.` and `Next: /crav1-build-tasks <T#>, because that yes is not on record yet.` |
| `blocked` / `failed` | **End the batch.** Do not launch the next `T#`. A missing yes is `needs_yes`, not this row. |
| User `stop` | End the batch. |

Do not skip a blocked `T#` unless they explicitly say skip. A `needs_yes` task is not blocked. A `NOTES:` line is the optional `.gitattributes` offer from the one-task branch. Accept is `resume: eol` on that worker. Skip adds nothing.

You may summarize each worker briefly on the board. Do not redo their implement/verify.

## After the batch

TL;DR: finished `T#`s, blocked `T#` + why, not started, commits the workers reported.

`Next: /crav1-open-pr, because the work is not on a pull request yet.` When the head's Match `Branch:` line ends in `(PR <n>)` or a pull request is known to be open for it, name it instead: `/crav1-open-pr` to push to PR <n> and update its description or comment. Do not run it from this skill.

If every selected task is `done`: one sentence that the requested slice is demoable (other unchecked `T#`s may remain if they passed a range).

Then follow **tool-approvals.md → Undo** once (restore the mode they wrote at the pause). Do not undo after each `T#`.

## Hard rules

- This chat is orchestration only: no product edits, no `git commit`, no push, no PR, no `spec.md` edits.
- One worker per `T#` at a time. All phases of that `T#` belong to that worker, not to extra chats.
- Do not flatten the batch into one implement pass in this chat.
