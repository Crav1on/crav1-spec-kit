# From a spec to a plan

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when `spec.md` is accepted. The plan is two files in the spec folder, `plan.md` (how: constraints, approach, files, linter, risks, trace) and `tasks.md` (small tasks you can test one at a time). They are in git so teammates and later chats see them. The host plan UI is not a substitute.

## First prompt

New chat. Strong reasoning model.

```text
/crav1-plan-from-spec
@docs/specs/<slug>/

The spec is accepted. Write plan.md and tasks.md. Do not write code.
```

## Steps

| Step | You | Agent |
| --- | --- | --- |
| Built pieces (partial slices) | For each built piece: finish the gap, add a verify test, or leave it | When the spec is partial or `## In the code` names paths, reads that repo and branch first. A piece that already matches v0 is marked already there and is not a choice. A piece you leave gets one line under `## Left as committed` and no task |
| Plan | When a leftover might be current work or later, answer `current` or `later` in one batch | Writes `plan.md` and `tasks.md`. Each task row names its check before any code: `(verify: <kind> — <named check>) (spec: …)`. Each question you kept open becomes its own entry under Risks. One that blocks some current tasks says `kept open; blocks T2, T4 until resolved.` One that blocks no current task gets `Blocks: none` and does not say "do not implement until resolved". Only a question with no `Blocks:` line keeps that phrase. Stale research findings are listed under Risks and do not block |
| Linter | When the plan says there is no linter for the code the tasks touch: add one, or go on without | `## Linter` names the repo's linter or checker. When there is none, the plan stops before Build until you choose. It does not install one |
| Review (optional) | `/crav1-review-plan` | Starts the `crav1-plan-reviewer-agent` subagent. Numbered findings `P#` in chat. Writes nothing |
| Tighten (optional) | `/crav1-tighten-plan`, then answer every `P#` in one batch (`yes` takes the recommendations) | Patches only the picked issue in `plan.md` or `tasks.md`. A finding about the spec goes back to `/crav1-tighten-spec` |
| Accept | Read `plan.md` and `tasks.md`. Edit them if needed. Say they are accepted | — |

Treat the plan as a design review. Wrong files, missing constraints, and oversized tasks are cheaper to fix here than after a large diff. A task that cannot be verified is not ready to build.

On a `spec/<slug>` branch, do not build. Merge that branch first, then `/crav1-create-feature-branch` to `feat/<slug>`.

## What gets written

- `docs/specs/<slug>/plan.md` and `tasks.md`. `/crav1-plan-from-spec` ends a task line with `(after: T1)` when the task needs an earlier one done first. Optional `(step: 1)` links a task to an Approach step, and optional `(map: feat/cancel-refund)` puts that task on another branch (1.128.0). Leave both off for one branch per step.
- On `spec.md`, `Blocks: T#` under a kept-open question that blocks some of the new tasks, and `Blocks: none` under one that blocks no current task, written by `/crav1-plan-from-spec`. The risk line for `Blocks: T2, T4` is `kept open; blocks T2, T4 until resolved.` Only a question with no line keeps "do not implement until resolved". No line still means the whole slice.
- `/crav1-review-plan`: one `Reviewed: <date>, P# open: <n>` line under the plan title. `/crav1-tighten-plan` lowers `<n>` as `P#`s are fixed.
- Matching OpenSpec export files, only when those already exist.
- Tighten-plan: only the picked issue.

Not written: other `spec.md` lines, application code, any linter install. These marks feed [Tasks ready to build](from-tasks-ready-to-build.md); see [Readiness marks](concepts/data-layout.md#readiness-marks).

## One spec, several branches (1.64.0)

When the spec's work sits on several branches (its `Synced at` lines, its Match `Branch:` list, or task `(branch: …)` parts), `/crav1-plan-from-spec` reads every one of them in the Built pieces step without checking any out, and labels a piece that only exists on an unmerged branch `only on feat/orders-retry, not merged`. A task that finishes or tests such a piece ends with `(branch: feat/orders-retry)`; with the repo too when the spec spans repos (`(branch: orders-api feat/orders-retry)`). Code in another repo is read from `../<repo>`.

`/crav1-tighten-spec` reads the same branches. A yes on "write the branch onto the spec?" adds a `Branch:` line in sorted place (1.86.0) instead of replacing the list. A listed branch that is gone and was never merged is offered `(dropped)`; a deleted branch whose work is already in the base is reported as `merged, branch deleted` and isn't offered.

## Host setup tasks (1.115.0)

A requirement that is a host setting with no file in the repo (a branch policy, required build, reviewers, an approval, a variable group) becomes its own task marked `(host setup)`, verified by reading the live setting back. Pipeline YAML and infrastructure as code stay ordinary tasks. See [Set up a host setting](from-host-setup.md).

## After

See which tasks are ready, any time: `/crav1-tasks-ready-to-build`. Then build one task, or several: [Build tasks](from-plan-to-build.md).

Reference pages: [plan-from-spec](reference/skills/crav1-plan-from-spec.md) · [review-plan](reference/skills/crav1-review-plan.md) · [tighten-plan](reference/skills/crav1-tighten-plan.md)

The run ends as [How a run ends](reference/run-ending.md) says: one `Next:` line, `Waiting:` only when a step is blocked, and `Uncommitted:` when files changed and are not committed.
