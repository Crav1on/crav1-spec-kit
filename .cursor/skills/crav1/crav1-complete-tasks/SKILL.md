---
name: crav1-complete-tasks
description: >-
  Orchestrate isolated /crav1-complete-task workers for a T# range or all
  unchecked tasks. Persist commit style as a rule first. Ask once whether
  they pause for Approvals & Execution (then restore at the end). Launch one
  worker per T# without another pause. Relay fix/ready gates only.
disable-model-invocation: true
icon: list
color: green
---

# Orchestrate complete-task workers

You **manage** the batch. You do **not** implement, verify, or `git commit` in this chat. Each `T#` runs in its own isolated **crav1-complete-task** worker (the “new chat” for that task).

Command: `/crav1-complete-tasks`. One task: `/crav1-complete-task`.

Worker: `.cursor/agents/crav1-complete-task.md` (plugin: `agents/crav1-complete-task.md`). Protocol: `crav1-complete-task` [references/run.md](../crav1-complete-task/references/run.md). Style: [style-persist.md](../crav1-complete-task/references/style-persist.md). Approvals: [tool-approvals.md](../crav1-complete-task/references/tool-approvals.md).

## Which tasks

Spec folder: user @-mention, else most recently edited `docs/specs/` excluding `_template/`. Need `tasks.md` or stop (`/crav1-plan-from-spec`).

| They typed | Queue |
| --- | --- |
| `T1-T3` / `T1–T3` | Inclusive ids that exist in `tasks.md` |
| `T1, T2, T5` | Those ids, tasks.md order |
| No range / “all” / “rest” | Every remaining `- [ ]` |

Skip `[x]` unless they named a checked id (then say it is already done). Unknown ids: list, continue. Empty queue: stop.

## Style once (rule from now on)

Before the first worker, follow **style-persist.md**. If you must ask, this turn is style only.

Do not ask again per `T#`. Workers must not ask style.

## Tool approvals (once for the batch)

Those **Allow / Stop** buttons on each worker are Cursor, not kit `fix`/`stop`. Follow [tool-approvals.md](../crav1-complete-task/references/tool-approvals.md) **once before the first worker** (pause, directions, wait for `continue` / `click` / `stop`).

When you launch a worker, pass **`approvals: already-done`**. Workers and `/crav1-complete-task` must **not** pause again.

After `continue`, do not treat IDE Allow/Stop as a reason to halt the board. After `click`, still do not re-ask per `T#`.

## Batch loop (you stay in this chat)

Keep a short board: queued / running / done / blocked.

For each `T#` **one at a time**:

1. Launch **crav1-complete-task** with spec folder, this `T#`, `resume: start`, `approvals: already-done`, and “style persist is already set.”
2. Wait until that worker returns a STATUS block. Do not implement in parallel. Do not start `T+1` while this worker is open.
3. Handle STATUS:

| STATUS | Orchestrator |
| --- | --- |
| `done` | Mark done. Next queued `T#`. |
| `needs_fix` | Ask the user `fix` / `stop` (this is their input). `fix` → **same T#** worker with `resume: fix` (still that task’s chat/worker, new launch is OK). Repeat until `done` or they `stop`. |
| `needs_ready` | Ask them to refresh the host, then `ready` / `stop`. `ready` → worker `resume: ready`. |
| `blocked` / `failed` | **End the batch.** Do not launch the next `T#`. |
| User `stop` | End the batch. |

Do not skip a blocked `T#` unless they explicitly say skip.

You may summarize each worker briefly on the board. Do not redo their implement/verify.

## After the batch

TL;DR: finished `T#`s, blocked `T#` + why, not started, commits the workers reported.

If every selected task is `done`: one sentence that the requested slice is demoable (other unchecked `T#`s may remain if they passed a range).

Then follow **tool-approvals.md → Undo** once (restore the mode they wrote at the pause). Do not undo after each `T#`.

## Hard rules

- This chat is orchestration only: no product edits, no `git commit`, no push, no PR, no `spec.md` edits.
- One worker per `T#` at a time. All phases of that `T#` belong to that worker, not to extra chats.
- Do not flatten the batch into one implement pass in this chat.
