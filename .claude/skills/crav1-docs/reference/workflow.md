# Workflow routes

<!-- Generated from docs/reference/workflow.yaml by scripts/gen-workflow.py. Do not edit by hand. -->

Kit version: 1.72.0

This page is the one written source for the order of kit commands. `/crav1-help` answers from it and names the route it used. The `crav1.mdc` order lines and every skill's next step in the [skills reference](skills.md) are generated from the same file, [workflow.yaml](workflow.yaml).

A route is an ordered list of steps for one situation. A step with more than one command means one of them. An optional step can be skipped when its condition does not hold.

| Route | When |
| --- | --- |
| [New slice](#new-slice) | You are starting a new feature from one or two sentences, a pile of ideas, or several files. |
| [New information on an existing slice](#new-info) | Minutes, a mail, a chat, or a new fact changes a spec that already exists, built or not. |
| [Bug](#bug) | Someone names a real bug. |
| [Outside pull request](#outside-pr) | A pull request was built outside the kit (its slug has no `plan.md` or `tasks.md`). |
| [Azure Boards sync](#ado-sync) | Specs and Azure Boards (ADO) should match. |

<a id="new-slice"></a>

## New slice

You are starting a new feature from one or two sentences, a pile of ideas, or several files.

| Step | Command | When |
| --- | --- | --- |
| 1 | `/crav1-spark-to-spec` or `/crav1-ideas-to-spec` or `/crav1-bundle-to-specs` | One or two sentences (spark), a pile of ideas and technical hunches (ideas), or mixed files or several v0 features (intake, then each slice follows this route). |
| 2 | `/crav1-create-feature-branch` | Optional. Before the first commit for the slice, on `feat/<slug>` (or `spec/<slug>` for specify only). |
| 3 | `/crav1-review-architecture` | Optional. When the spec touches structure, data, or integrations. |
| 4 | `/crav1-tighten-spec` | Always, before questions and the plan. |
| 5 | `/crav1-resolve-open-questions` | When `## Open questions` still has items. |
| 6 | `/crav1-ado-sync` | Optional. When the team tracks Features in Azure Boards. |
| 7 | `/crav1-plan-from-spec` | The spec is tight and its questions are answered or kept open on purpose. |
| 8 | `/crav1-review-plan` | Right after the plan is written. |
| 9 | `/crav1-tighten-plan` | After the plan review. |
| 10 | `/crav1-ado-sync` | Optional. When the Feature is in Azure Boards and the tasks should be too. |
| 11 | `/crav1-tasks-ready-to-build` | Optional. Any time, to see which tasks are ready, which are blocked and why. Read-only. |
| 12 | `/crav1-build-tasks` or `/crav1-build-features` | One task, a range, or all (build-tasks), or whole features (build-features). Each task runs in its own worker that implements, commits, and verifies it, so they go straight to the pull request. |
| 13 | `/crav1-verify-build-against-spec` | Against the spec and the plan, for the whole slice when you want one report. |
| 14 | `/crav1-fix-build-gaps` | Optional. When `verify.md` has a failure, or to fix it against the running host (fix-build-gaps asks which). Do not edit `spec.md` in this loop. Then back to `/crav1-verify-build-against-spec`. |
| 15 | `/crav1-finalize-commit` | When the slice verifies (it asks commit, or only write the message first). |
| 16 | `/crav1-open-pr` | To push and open the pull request. |
| 17 | `/crav1-review-pr` | Before the merge. |
| 18 | `/crav1-merge-pr` | When the review says ship and the host checks are green. |

<a id="new-info"></a>

## New information on an existing slice

Minutes, a mail, a chat, or a new fact changes a spec that already exists, built or not.

| Step | Command | When |
| --- | --- | --- |
| 1 | `/crav1-add-to-spec` | Minutes, a transcript, a mail, a chat, a dump, a code change, or one new fact (add-to-spec asks which). |
| 2 | `/crav1-tighten-spec` | Always, on each spec that changed. New text needs the same tightening as the first draft. |
| 3 | `/crav1-resolve-open-questions` | When the change added or answered open questions. Use `/crav1-show-or-ask-open-questions` for the ones someone else must answer. |
| 4 | `/crav1-plan-from-spec` | When the slice has `plan.md` or `tasks.md`, so the plan and the tasks follow the new spec. |
| 5 | `/crav1-ado-sync` | Optional. When the Feature or its tasks are in Azure Boards (push Features only when the Feature itself changed; push tasks for the tasks). |
| 6 | `/crav1-tasks-ready-to-build` | Optional. Any time, to see which tasks are ready after the change, which are blocked and why. Read-only. |
| 7 | `/crav1-build-tasks` | To build the tasks that are not built yet. Each task is verified inside its worker. |
| 8 | `/crav1-verify-build-against-spec` | For the whole slice when you want one report. |
| 9 | `/crav1-finalize-commit` | When the slice verifies. |

<a id="bug"></a>

## Bug

Someone names a real bug.

| Step | Command | When |
| --- | --- | --- |
| 1 | `/crav1-fix-bug` | The bug is named. It says which lane the fix belongs to. |
| 2 | `/crav1-tighten-spec` or `/crav1-plan-from-spec` or `/crav1-build-tasks` | The lane fix-bug named. Spec miss is Specify (tighten-spec), plan miss is Plan (plan-from-spec), code miss is Build (build-tasks). Tighten-spec and plan-from-spec then follow the New slice route from that step. |
| 3 | `/crav1-verify-build-against-spec` | After the fix is built. |
| 4 | `/crav1-fix-build-gaps` | Optional. When `verify.md` has a failure. Then back to `/crav1-verify-build-against-spec`. |
| 5 | `/crav1-finalize-commit` | When it verifies. |
| 6 | `/crav1-open-pr` | To push and open the pull request. |

<a id="outside-pr"></a>

## Outside pull request

A pull request was built outside the kit (its slug has no `plan.md` or `tasks.md`).

| Step | Command | When |
| --- | --- | --- |
| 1 | `/crav1-review-pr` | The pull request is open. |
| 2 | `/crav1-merge-pr` | When the review says ship. |
| 3 | `/crav1-refresh-system-notes` | After the merge, to bring its changes into the spec and `docs/system/`. |
| 4 | `/crav1-finalize-commit` | When refresh-system-notes changed a file. |

<a id="ado-sync"></a>

## Azure Boards sync

Specs and Azure Boards (ADO) should match.

| Step | Command | When |
| --- | --- | --- |
| 1 | `/crav1-ado-sync` | It asks which: suggest Features, push Features, push tasks (when the slice has `tasks.md`), pull task states, or pull spec changes from Features. |
| 2 | `/crav1-finalize-commit` | When the sync changed a file. |
