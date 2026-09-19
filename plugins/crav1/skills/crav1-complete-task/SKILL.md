---
name: crav1-complete-task
description: >-
  One tasks.md row from implement through done: implement-task, commit,
  verify-spec, commit; if inner-loop verify issues, offer a fix-from-verify
  loop (commit after each fix) then verify-spec again. Ask commit style once
  for the run. Auto-commit after showing the message. Stop when input is
  required. Use for one T# end-to-end, or /crav1-complete-task. Several T#s:
  /crav1-complete-tasks.
disable-model-invocation: true
icon: play
color: green
---

# Complete one task

You drive **one** `T#` from implement to done. You do not invent a second workflow. You **follow** these skills in order (drop-in `.cursor/skills/crav1/<name>/SKILL.md` or this plugin’s sibling `skills/<name>/SKILL.md`):

`crav1-implement-task` → loop-commit → `crav1-verify-spec` → loop-commit → (optional) fix loop → `crav1-verify-spec` again.

Command: `/crav1-complete-task`. Several tasks: `/crav1-complete-tasks`.

When `/crav1-complete-tasks` called you, **do not** re-ask style. Use the run style it already set.

## Before work

Spec folder: user @-mention, else most recently edited `docs/specs/` tree excluding `_template/`. Need `tasks.md` or stop (`/crav1-plan-from-spec`).

**Which `T#`:** the id they named, else the first `- [ ]`. If all checked, stop and run `crav1-verify-spec` only if they asked to complete a task that is already done; otherwise tell them `/crav1-verify-spec` or `/crav1-complete-tasks`.

## Commit style (once per run)

If a parent already set **run style**, skip this.

Else follow `crav1-draft-commit-message` style rules (`once` / `onward` / `log-once` / `log-onward`, persist files). This turn is **style only** if you must ask — no implement yet.

Treat `once` / `log-once` as **this entire complete-task run** (every loop-commit below), not a single commit. `onward` / `log-onward` still write the persist files.

Do not re-ask style between implement, verify, and fix commits.

## Loop-commit (not the interactive finalize menu)

After a step that may have changed files:

1. If the tree is clean, skip. Say skipped.
2. Follow `crav1-finalize-commit` **draft** (run style already chosen) and its **commit** + **Cursor attribution** sections.
3. Show Summary/Description, then **`commit` immediately**. Do **not** offer copy / edit / rewrite / stop. This run is unattended except the gates below.
4. Do not push.

If commit fails or attribution comes back after one strip: **stop**. That needs them.

## Gate: stop and wait

Stop the run (do not start the next phase or the next `T#`) if:

- `crav1-implement-task` would stop (open parked Q, non-goal, playbook-only with no scaffold ask, missing `tasks.md`)
- That task’s **row verify failed** or you could not run it (box stays `[ ]`)
- Spec disagrees with the code → `/crav1-tighten-spec`, do not edit `spec.md`
- `crav1-fix-from-verify` would stop (spec frozen, empty inner-loop you already handled, non-goal)
- Commit / attribution needs them
- Live host must be refreshed and they have to do it (see `crav1-verify-spec` `references/live-host.md`) — wait for `ready` or `stop`
- They said `stop`

## Phase A — implement

Follow **`crav1-implement-task`** for this `T#` only (its one-task-per-turn rule yields to this orchestrator for **phases**, not for extra `T#`s).

Then loop-commit.

If the row did not go `[x]`, **stop**. Recap. Do not verify-spec as if the task shipped.

## Phase B — verify-spec

If Phase A changed a **hosted** API/UI, follow `crav1-verify-spec` `references/live-host.md` first (restart/wait, or gate on `ready`). Then follow **`crav1-verify-spec`** in full (`verify.md` + chat TL;DR).

Then loop-commit if `verify.md` or related files changed.

**Inner-loop** means the `crav1-fix-from-verify` queue: verify failed → claimed/unverified → wiring `G#`. **Not implemented** other `T#`s are **not** inner-loop (expected on a single-task run).

- If inner-loop is **empty**: Phase D (done TL;DR). Do not ask to fix.
- If inner-loop is **non-empty**: **stop and ask** (questions tool OK). This is the only verify gate.

| Id | Choice |
| --- | --- |
| `fix` | Enter the fix loop (Phase C) |
| `stop` | End the run. They still have `verify.md` |

Do not start Phase C until they pick `fix`.

## Phase C — fix loop

While they are in this loop:

1. Follow **`crav1-fix-from-verify`** with **no Gap** (one inner-loop item).
2. Loop-commit.
3. If that skill says the inner-loop queue is **empty** → follow **`crav1-verify-spec`** again, loop-commit if needed, then:
   - inner-loop still non-empty → **same options** (`fix` / `stop`)
   - inner-loop empty → Phase D
4. If the queue is not empty after the fix, continue at (1) **without** asking again (they already picked `fix`). Keep going until the queue is empty or a gate fires.

Do not implement a new `T#` inside Phase C.

## Phase D — done TL;DR (chat only)

When inner-loop is empty after Phase B or after a clean re-verify:

```text
T#: <id> <title> — done
Implement verify: pass
Spec verify: inner-loop empty
Commits: <hashes or “none”>
Left unchecked: <other T#s or none>
```

One short paragraph if something is still **not implemented** (other tasks). Do not start those here.

## Hard rules

- One `T#` of product work per `/crav1-complete-task` invocation.
- Do not edit `spec.md`. Do not push. Do not open a PR.
- Do not skip loop-commit when the tree is dirty after a phase.
- Unimplemented tasks are `/crav1-complete-tasks` or `/crav1-implement-task`, not fix-from-verify.
