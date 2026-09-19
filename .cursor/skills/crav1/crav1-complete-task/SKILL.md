---
name: crav1-complete-task
description: >-
  Start one T# implement-to-done in an isolated worker chat (subagent). Persist
  commit style as a Cursor rule (same as finalize-commit onward). Auto-commit
  after each phase. Use for a single task end-to-end, or /crav1-complete-task.
  Several T#s: /crav1-complete-tasks (orchestrates these workers).
disable-model-invocation: true
icon: play
color: green
---

# Start complete-task (isolated chat)

This skill is the **command**. You are the parent. Do **not** implement the task in this chat.

1. Persist commit style (below).
2. Immediately delegate to the **crav1-complete-task** subagent (`.cursor/agents/crav1-complete-task.md` or this plugin’s `agents/crav1-complete-task.md`). That isolated run is the “new chat” for this `T#`. All phases (implement → commit → verify → optional fix) stay in **that** worker. Do not split phases into more chats.

Several tasks: tell them `/crav1-complete-tasks` instead of launching many workers yourself.

## Style (rule from now on)

Follow this skill’s [references/style-persist.md](references/style-persist.md). If you must ask, this turn is **style only** — no worker yet.

Then follow [references/tool-approvals.md](references/tool-approvals.md) (`auto` vs `click`). If you must ask, that turn is **approvals only** — no worker yet. After `auto`, do not treat IDE Allow/Stop as a kit gate.

## Find the work

Spec folder: user @-mention, else most recently edited `docs/specs/` excluding `_template/`. Need `tasks.md` or stop (`/crav1-plan-from-spec`).

**T#:** the id they named, else the first `- [ ]`. If all checked, stop (`/crav1-verify-spec` or `/crav1-complete-tasks`).

## What to pass the worker

- Spec folder paths (`spec.md`, `tasks.md`, `plan.md`, `verify.md` if any)
- `T#`
- `resume: start` (or `fix` / `ready` / `stop` if this is a follow-up after a gate)
- Point it at [references/run.md](references/run.md)

Instruct it to follow `run.md` and end with the STATUS block. Do not do the implement/verify work in your own voice.

## After it returns

Show the worker’s recap and STATUS.

| STATUS | You do |
| --- | --- |
| `done` | Show the **done** TL;DR. Stop. |
| `needs_fix` | Ask `fix` / `stop`. `fix` → launch the **same** worker again with `resume: fix`. `stop` → end. |
| `needs_ready` | Ask them to refresh the live host, then `ready` / `stop`. `ready` → worker with `resume: ready`. |
| `blocked` / `failed` | Show DETAIL. Do not start another `T#`. |

Do not start `/crav1-complete-tasks` unless they asked.
