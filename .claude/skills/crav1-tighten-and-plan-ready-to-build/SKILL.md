---
name: crav1-tighten-and-plan-ready-to-build
description: >-
  Use when a spec should be tightened and planned until it is honestly
  ready to build, with or without a playbook. Guided walk only. Runs the
  existing specify and plan skills inside the walk and stops before build.
disable-model-invocation: true
icon: workflow
color: blue
---

# Tighten and plan, ready to build

The user wants one guided walk from a draft spec through the plan until the tasks are honestly ready to build. A playbook file may be named. Without one, the walk starts at the architecture review. Both routes then use the same steps and the same ready check.

Command: `/crav1-tighten-and-plan-ready-to-build`. The playbook path is an optional value after the command. A `docs/playbooks/<topic>.md` path is a playbook. Do not ask the user to type the characters `[playbook]`.

This walk is cross-cutting. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. That ask names the list. It does not run this command. The six starter options stay unchanged.

It does not replace the skills it runs. It does not start Build. It never runs `/crav1-build-tasks` or `/crav1-build-features`. Naming `/crav1-build-tasks` after a clear check is not running it.

## Route first (1.119.0)

Read [references/common.md](references/common.md) once. Then open only the file for the point you are at. Do not open the others yet.

- A `walk-progress.md` already beside the spec: read [references/progress.md](references/progress.md). Resume may report status. It does not start a step.
- A playbook path was given: read [references/playbook.md](references/playbook.md) and ask the step 1 question before any later step, including a read-only check such as readiness. No step runs until that choice is answered. No playbook: do not open that file. Say step 1 is skipped and go to step 2.
- Steps 2 through 6: read [references/steps.md](references/steps.md).
- Step 7: read [references/readiness.md](references/readiness.md). Do not open it, and do not run readiness, until the playbook choice is answered when a playbook was named.

A headless or bot run stops before any step. This walk is guided only. It does not guess a mode, and there is no automatic mode.

## Locked steps

The order matches the new-slice route from architecture review through the ready check. One difference is called out in [references/steps.md](references/steps.md): on that route the architecture review is optional, and inside this walk it always runs.

Open each file below from this skill's folder and follow it. Read [open-skill-file.md](../crav1-docs/reference/open-skill-file.md) once before the first one (1.134.0).

1. Playbook, only when a playbook was given. `skip` leaves it, `reapply` runs it again when this walk already applied that same file. Apply is in [references/playbook.md](references/playbook.md).
2. Open `../crav1-review-architecture/SKILL.md` (`/crav1-review-architecture`).
3. Open `../crav1-tighten-spec/SKILL.md` (`/crav1-tighten-spec`), one issue at a time, as that skill already walks.
4. Open `../crav1-resolve-open-questions/SKILL.md` (`/crav1-resolve-open-questions`).
5. Open `../crav1-plan-from-spec/SKILL.md` (`/crav1-plan-from-spec`), which writes `plan.md` and `tasks.md`.
6. Open `../crav1-review-plan/SKILL.md` (`/crav1-review-plan`), then Open `../crav1-tighten-plan/SKILL.md` (`/crav1-tighten-plan`). A spec-tagged finding is one jump-back card, then the walk continues. The rule is in [references/steps.md](references/steps.md) (1.135.0).
7. Open `../crav1-tasks-ready-to-build/SKILL.md` (`/crav1-tasks-ready-to-build`). That check rewrites `build-map.md`. This walk never writes `verify.md`.

A step with nothing to do says so, records that, and moves on. Optional offers are not steps. They are offered once, after open questions, when any apply. They are named in [references/steps.md](references/steps.md). After the plan, questions that still have no `Blocks:` line are offered there too, before that step is recorded.

## Stop

The spec, the plan, and the tasks stay the source of truth. `walk-progress.md` only records position. Do not edit `spec.md`, `plan.md`, or `tasks.md` from this skill, except a `Blocks:` line the pass after plan-from-spec writes after a yes, and the matching Risk sentence when that line is `Blocks: none` or `Blocks: whole slice`. An Approval needed item is written by plan-from-spec, not by this walk. A jump back is not that pass. It reruns the owning skill, even for a small patch. This walk does not edit those files on a jump back, and it does not write `Reviewed:`. Every other spec, plan, and task write happens inside the skill that owns it, after that skill's own yes.

A checkbox tick, a `(PR n)` or `(done)` note on that task line, or `(PR n)` on a Match `Branch:` line does not reopen a step and does not ask to clear (1.138.0). The rule is [references/progress.md](references/progress.md).

Do not report ready while a blocker, a reopened step, or an open assumption remains. A `ready-partial` result is not that report: some tasks can start, the held ones stay listed by build-map branch, and the walk records `Result: ready-partial` with no `not-ready` mark. The lists and the Next lines are in [references/readiness.md](references/readiness.md) (1.133.0). Do not start Build. This walk never writes `verify.md`. Do not create a git commit. Apply writes the playbook copy under `docs/playbooks/`; that write is not a git commit.

When the user stops partway, one line `Paused at <step>.` then the shared ending in [references/progress.md](references/progress.md). `Next` is this command, because the walk paused before `continue_from`.

## Run ending (1.122.0)

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says.
