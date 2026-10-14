# Start build-tasks (isolated chat)

This skill is the **command**. You are the parent. Do **not** implement the task in this chat.

1. Persist commit style (below).
2. Immediately delegate to the **crav1-build-task-agent** subagent (`.cursor/agents/crav1-build-task-agent.md` or this plugin’s `agents/crav1-build-task-agent.md`). That isolated run is the “new chat” for this `T#`. All phases (implement → commit → verify → optional fix) stay in **that** worker. Do not split phases into more chats.

Several tasks on **one** spec: tell them `/crav1-build-tasks` instead of launching many workers yourself. Several **specs**: `/crav1-build-features` (serial slugs).

## Style (rule from now on)

Follow this skill’s [references/style-persist.md](references/style-persist.md). If you must ask, this turn is **style only** — no worker yet.

Then, **only if this chat is a standalone `/crav1-build-tasks`** (the user invoked this skill, not `/crav1-build-tasks`): follow [references/tool-approvals.md](references/tool-approvals.md) — pause with directions, wait for `continue` / `click` / `stop`. If `/crav1-build-tasks` launched you or passed `approvals: already-done`, **skip** that pause.

**Branch:** before the worker, follow `/crav1-create-feature-branch` (drop-in: `.cursor/skills/crav1/crav1-create-feature-branch/SKILL.md`; plugin: sibling `skills/crav1-create-feature-branch/SKILL.md`) **Build** prompt. If that prompt is needed, this turn is branch only (after style). If you are on `spec/<slug>`, stop (no worker) and follow **Build on a spec-only branch**. Pass `branch: already-done` to the worker. Workers must not create branches.

## Find the work

Spec folder: user @-mention, else most recently edited `docs/specs/` excluding `_template/`. Need `tasks.md` or stop (`/crav1-plan-from-spec`).

**T#:** the id they named, else the first `- [ ]`. If all checked, stop (`/crav1-verify-build-against-spec` or `/crav1-build-tasks`).

## What to pass the worker

- Spec folder paths (`spec.md`, `tasks.md`, `plan.md`, `verify.md` if any)
- `T#`
- `resume: start` (or `fix` / `ready` / `stop` if this is a follow-up after a gate)
- `approvals: already-done` after the standalone pause (or when the orchestrator passed that)
- `branch: already-done` (parent already ran `/crav1-create-feature-branch`)
- Point it at [references/run.md](references/run.md)

Instruct it to follow `run.md` and end with the STATUS block. Do not do the implement/verify work in your own voice.

## After it returns

Show the worker’s recap and STATUS.

| STATUS | You do |
| --- | --- |
| `done` | Show the **done** TL;DR. Then one line: Next (optional): `/crav1-open-pr` when you want to push and open the PR. Do not run it. Stop. |
| `needs_fix` | Ask `fix` / `stop`. `fix` → launch the **same** worker again with `resume: fix`. `stop` → end. |
| `needs_ready` | Ask them to refresh the live host, then `ready` / `stop`. `ready` → worker with `resume: ready`. |
| `needs_dependency` | Show the BLOCKER line first. Ask start / skip / stop for that dependency. `start` → same worker with `resume: dependency-start`; `skip` → `resume: dependency-skip`; `stop` → end. Headless: use the two-pass questions file. |
| `blocked` / `failed` | Show DETAIL. Do not start another `T#`. |

After this standalone run ends (any STATUS, or they `stop`), follow **tool-approvals.md → Undo**. Do not undo if this invocation skipped the pause (`approvals: already-done` from build-tasks).

Do not start `/crav1-build-tasks` unless they asked. Do not ask whether to run `/crav1-refresh-system-notes`.
