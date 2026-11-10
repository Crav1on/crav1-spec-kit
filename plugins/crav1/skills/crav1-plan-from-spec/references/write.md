# crav1-plan-from-spec: writing tasks.md, Blocks lines, Left as committed

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.86.4; the rules are unchanged.

## Left as committed

In `plan.md`: **Left as committed** — only when the user left a piece. One line per piece: `Left as committed: <piece>.` Omit the heading when nothing was left. A left piece has no task.

## Blocks lines

The one exception to leaving `spec.md` alone. Once `tasks.md` exists, every kept-open question gets one decision. Follow skill `crav1-add-to-spec`, `references/open-questions.md`. Do not change the question or its other lines. At most one `Blocks:` line; a new one replaces it. On a re-plan that renumbers tasks, replace the `Blocks:` lines this plan wrote.

- It blocks some of the new tasks: write `- Blocks: T2, T4`. Pick the tasks from the plan. Do not ask. The risk entry is the question's first sentence, then `kept open; blocks T2, T4 until resolved.` Do not write "do not implement until resolved" on that entry. When the risk does not repeat that first sentence, add `(question: <first words>)` so the link stays.
- It blocks no current task: write `- Blocks: none`, or `- Blocks: none (later phase)` when the reason is that short. Do not ask. The risk entry is the question's words, then `kept open; does not block the current tasks.` Do not write "do not implement until resolved" on that entry.
- You cannot tell whether it is current work or later: ask once, in one short batch, for every such question together. Not one question at a time. Each option is `current` or `later`, with no recommendation. `later` writes `Blocks: none` and the risk wording above. `current` writes `Blocks: T#` when it blocks some tasks, with `kept open; blocks T2, T4 until resolved.`, or no line when it blocks the whole current slice. Only a question with no `Blocks:` line keeps "do not implement until resolved".

A kept-open question with no `Blocks:` line still blocks the whole slice for `/crav1-tasks-ready-to-build` (inferred). `Blocks: none` blocks no task. Any `Blocks:` line wins over Risk wording. List each `Blocks:` line in the recap.

## tasks.md

Read this skill’s [references/checks.md](references/checks.md) before writing tasks (this skill's `references/checks.md`). Name the checks there. Do not write test code.

Independently testable slices. Bad: “add authentication.” Good: “POST `/register` rejects invalid email (verify: unit — empty email is rejected; unit — malformed email is rejected) (spec: invalid email).”

```markdown
# Tasks

- [ ] T1: <what> (verify: <kind> — <named check>) (spec: <REQ or acceptance>)
```

Rules:

- Each task maps to at least one spec acceptance line, REQ, or kept security check
- Every v0 acceptance line maps to at least one task (or an explicit “covered by T#”), or the trace says `already there` or `left as committed`
- Every kept security check (`docs/system/security.md` or a Security section on the spec) maps to a task, or the trace says which task already covers it
- Each verify note names the kind and the checks, per `references/checks.md`
- Order so each task can be verified before the next depends on it
- When a task needs an earlier task to be done first, end its line with `(after: T1)` or `(after: T1, T3)`. Name only real needs. A task with no `(after: …)` has no recorded dependency, and `/crav1-tasks-ready-to-build` then treats the task just before it as blocking it (inferred). Build, status and verify follow the `(after: …)` graph (dependency order, 1.103.0), not task number, so when the order is not simply T1, T2, T3…, give every task after T1 its `(after: …)`
- A task that finishes or tests a built piece found only on one work branch ends its line with `(branch: <name>)`, after `(verify:)`, `(spec:)` and `(after:)`. When the spec spans repos, name the repo too: `(branch: orders-api feat/orders-retry)`. New work with no home gets no branch part, and there is no new question. With one branch or none, write no branch part. A task without one uses `feat/<slug>` as today
- Build map (1.128.0), optional. Leave these off unless the plan is overriding the default of one branch per Approach step. End a task line with `(step: 1)` when that step's text does not already name the task. End it with `(map: feat/cancel-refund)` when that task is built on a different branch from its step. Tasks that share a `(map:)` branch share the branch. Do not invent either mark for the default.
- No task is “and also the rest of the app”
