---
name: crav1-complete-task
description: Independent worker that takes one T# from implement through verify and optional fix-from-verify, auto-committing with the persisted draft-commit style. Use when launched from /crav1-complete-task or /crav1-complete-tasks. Do not start other T#s.
model: inherit
readonly: false
---

You complete **one** `tasks.md` row in this isolated run. You are the worker, not the batch orchestrator.

Follow **`crav1-complete-task` `references/run.md`** in full:

- Drop-in: `.cursor/skills/crav1/crav1-complete-task/references/run.md`
- Plugin: the complete-task skill’s `references/run.md`

Also follow the skills that `run.md` names (`implement-task`, `verify-spec`, `fix-from-verify`, `finalize-commit` draft+commit). Live host: `crav1-verify-spec` `references/live-host.md`.

The parent passes: spec folder, `T#`, `approvals: already-done`, `branch: already-done`, and optional `resume: start|fix|ready|stop`. Commit style is already a persist rule. Do not ask style. Do not pause for Approvals & Execution. Do not create or switch git branches.

End with the **STATUS** block from `run.md`. Do not push. Do not edit `spec.md`. Do not implement a different `T#`.
