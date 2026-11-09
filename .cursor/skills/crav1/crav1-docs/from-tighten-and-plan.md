# Tighten and plan until ready to build

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md).

Use this when a draft spec should be tightened and planned until the tasks are honestly ready to build. The command is [`/crav1-tighten-and-plan-ready-to-build`](reference/skills/crav1-tighten-and-plan-ready-to-build.md).

You can start with a playbook report, or without one. Both go through the same steps and the same ready check. The walk runs the existing skills. It does not replace them. It is guided only. You confirm each write before it happens.

This is cross-cutting. It may run from any lane. It is a later skill, not a starter option. It does not start Build.

The new-slice route is unchanged. You can still run each skill on its own. On that route the architecture review is optional. Inside this walk it always runs.

## First prompt

```text
/crav1-tighten-and-plan-ready-to-build
@docs/specs/<slug>/
```

With a playbook, add the report path on the next line. You do not type brackets.

## Steps

| Step | What you see |
| --- | --- |
| 1. Playbook, only when you named one | If this walk already applied that same file, you choose `skip` (Recommended) or `reapply`. Otherwise you see the changes. Nothing is written until you say yes. Apply is `/crav1-resolve-open-questions apply`. Kept items are written inside that apply. |
| 2. Architecture review | Always runs. It writes nothing. If there is nothing to critique, the walk says so. |
| 3. Tighten the spec | One issue at a time, as `/crav1-tighten-spec` already walks. No issues: it says so. |
| 4. Open questions | `/crav1-resolve-open-questions`. Nothing left to settle: it says so. |
| 5. Plan | `/crav1-plan-from-spec` writes `plan.md` and `tasks.md`. |
| 6. Plan review, then tighten | `/crav1-review-plan`, then `/crav1-tighten-plan`. |
| 7. Ready check | `/crav1-tasks-ready-to-build`. The walk stops here. |

A step with nothing to do says so and moves on.

Offered only when the spec needs them, not as fixed steps: the research helper, `/crav1-review-security`, `/crav1-model-data`, `/crav1-show-or-ask-open-questions`, and `/crav1-suggest-tests-for-code`. Security and tests stay optional. The walk does not run them unless you pick them.

## Progress

Beside the spec, `docs/specs/<slug>/walk-progress.md` records which steps are done, when, and the version of the spec, plan, and tasks each step covered. The ready check also records a `verify.md` version. The playbook is intake only.

When you come back, the walk says what changed and reopens only the steps that covered a file that changed. The spec, the plan, and the tasks stay the source of truth.

## When the check is not ready

Blocked rows and Needs verify rows are named back to a step. You can jump back, rerun those steps, and run the check again. A plan-review warning is not treated as ready.

Needs verify belongs to `/crav1-verify-build-against-spec`. That command is outside this walk. The walk names it and does not start it. It does not report ready while that row remains.

## What gets written

- `docs/specs/<slug>/walk-progress.md`, after a yes.
- Spec, plan, and task edits only inside the skill that owns them, after that skill's own yes.
- Playbook answers only through `/crav1-resolve-open-questions apply`, on yes.

Not written: application code. The playbook file is not edited. Nothing is committed.

## After

When the check is clear, the slice is ready to build. You run build yourself:

```text
/crav1-build-tasks
@docs/specs/<slug>/
```

This walk does not run `/crav1-build-tasks`. When the progress file should be committed, `/crav1-finalize-commit`.

Reference page: [tighten and plan, ready to build](reference/skills/crav1-tighten-and-plan-ready-to-build.md)
