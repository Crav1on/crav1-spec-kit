# crav1-plan-from-spec: writing tasks.md, Blocks lines, Left as committed

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.86.4; the rules are unchanged.

## Left as committed

In `plan.md`: **Left as committed** — only when the user left a piece. One line per piece: `Left as committed: <piece>.` Omit the heading when nothing was left. A left piece has no task.

## Blocks lines

The one exception to leaving `spec.md` alone. For each kept-open question under `## Open questions` that blocks only some of the new tasks, write one indented line under that question: `- Blocks: T2, T4`. Pick the tasks from the plan yourself; do not ask. Follow `crav1-add-to-spec` `references/open-questions.md` (drop-in: `.claude/skills/crav1-add-to-spec/references/open-questions.md`; plugin: sibling `skills/crav1-add-to-spec/references/open-questions.md`). Do not change the question or its other lines. On a re-plan that renumbers tasks, replace the `Blocks:` lines this plan wrote. A kept-open question with no `Blocks:` line blocks the whole slice for `/crav1-tasks-ready-to-build` (inferred). List each `Blocks:` line in the recap.

## tasks.md

Read this skill’s [references/checks.md](references/checks.md) before writing tasks (drop-in: `.claude/skills/crav1-plan-from-spec/references/checks.md`; plugin: this skill’s `references/checks.md`). Name the checks there. Do not write test code.

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
- When a task needs an earlier task to be done first, end its line with `(after: T1)` or `(after: T1, T3)`. Name only real needs. A task with no `(after: …)` has no recorded dependency, and `/crav1-tasks-ready-to-build` then treats every earlier unticked task as blocking it (inferred)
- A task that finishes or tests a built piece found only on one work branch ends its line with `(branch: <name>)`, after `(verify:)`, `(spec:)` and `(after:)`. When the spec spans repos, name the repo too: `(branch: orders-api feat/orders-retry)`. New work with no home gets no branch part, and there is no new question. With one branch or none, write no branch part. A task without one uses `feat/<slug>` as today
- No task is “and also the rest of the app”
