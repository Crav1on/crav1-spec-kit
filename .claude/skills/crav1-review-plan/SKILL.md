---
name: crav1-review-plan
description: >-
  Use after /crav1-plan-from-spec. Starts the crav1-plan-reviewer-agent
  subagent on plan.md and tasks.md against spec.md and returns P# issues for
  /crav1-tighten-plan. Writes only the Reviewed line. Does not write code.
disable-model-invocation: true
icon: search
color: orange
---

# Start plan reviewer

This skill is the **command**. You are the parent. Immediately delegate to the **crav1-plan-reviewer-agent** subagent. Load `.claude/agents/crav1-plan-reviewer-agent.md` (drop-in) or this plugin’s `agents/crav1-plan-reviewer-agent.md`. Do not review in your own voice as a substitute. Do not edit files, except the one `Reviewed:` line in **Record the review** below. Do not write application code. Do not resolve product questions (those belong on the spec).

## Find the spec folder

Use the folder the user @-mentions. Otherwise the most recently edited tree under `docs/specs/` excluding `_template/`. If several, ask which slug, then delegate.

Need `spec.md`, `plan.md`, and `tasks.md`. If plan/tasks are missing, stop (`/crav1-plan-from-spec`). Do not invent a plan in this command.

Pass the subagent these paths (read-only): `spec.md`, `plan.md`, `tasks.md`, plus `diagrams.md` / `adr/` if present. Also point it at this skill’s `assets/` (drop-in also `.claude/agent-assets/crav1-plan-reviewer-agent/`; plugin also `agent-assets/crav1-plan-reviewer-agent/`) for **expected plan/tasks shape**, not as the files under review.

## What to tell the subagent

Instruct it to follow its own prompt and the check rules in `crav1-plan-from-spec` [references/checks.md](../crav1-plan-from-spec/references/checks.md) (drop-in: `.claude/skills/crav1-plan-from-spec/references/checks.md`; plugin: sibling `skills/crav1-plan-from-spec/references/checks.md`), including **Linter, before Build**. A stale research finding that the plan left out of Risks is a plan issue. Stale research does not block the plan. A plan that never says whether this repo has a linter or checker for the code the tasks will touch is not complete. Finish with numbered **Issues for `/crav1-tighten-plan`** (`P1`, `P2`, …), one finding each. Mark any finding that is really a spec defect as **spec** (do not pretend the plan can fix it). No single global patch recommendation.

## Record the review

After the subagent returns, write one line in `plan.md`, right under the `# Plan:` title: `Reviewed: <today's date>, P# open: <n>`, where `<n>` is the number of plan and spec `P#`s it listed (0 when it found none). Replace an earlier `Reviewed:` line, and the template's comment about it, instead of adding a second line. Change nothing else in `plan.md` or `tasks.md`. Say in the recap that the line was written. `/crav1-tasks-ready-to-build` reads it. This skill does not commit.

## After it returns

Show the subagent’s review. Then tell them the next command is `/crav1-tighten-plan` to walk **plan** `P#`s one by one. Spec-tagged findings: `/crav1-tighten-spec` or `/crav1-resolve-open-questions` — do not start those in this turn unless they already asked.

When `## Linter` says this repo has no linter or checker for the code the tasks will touch, do not name Build (`/crav1-build-tasks`, `/crav1-build-features`). Stop before Build. The user decides to add the linter or to go on without one. Do not install one. A plan that already says none is complete on that point. Do not file a `P#` only because the answer is none.

Do not run `/crav1-review-pr`. Specify does not name the linter.
