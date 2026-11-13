---
name: crav1-build-features
description: >-
  Use to build several ready specs one after another in this checkout, each on
  feat/<slug> with the build-tasks loop. Serial, not parallel. For one slug
  use /crav1-build-tasks. Does not push or open a pull request.
disable-model-invocation: true
icon: list
color: green
---

# Orchestrate several features (serial)

You **manage** a queue of **slugs**. You do **not** implement, verify, or `git commit` in this chat.

Each slug is one feature: `docs/specs/<slug>/` + branch `feat/<slug>` created from the **into branch** (Merges into, else default; not from the previous feature). Inside a slug, reuse the build-tasks T# loop: one **crav1-build-task-agent** worker per `T#`, one at a time. Open `../crav1-build-tasks/branches/several-tasks/BRANCH.md` for that loop. Do not start `/crav1-build-tasks`.

This is **not** parallel. Two `feat/` branches cannot share this working tree. True parallel (handoff / worktrees / Cloud Agents) is **out of scope** for this skill.

Command: `/crav1-build-features`. One spec: `/crav1-build-tasks`. One task: `/crav1-build-tasks`.

Worker: `.cursor/agents/crav1-build-task-agent.md` (plugin: `agents/crav1-build-task-agent.md`). Protocol: `crav1-build-tasks` [references/run.md](../crav1-build-tasks/branches/one-task/references/run.md). Style: [style-persist.md](../crav1-build-tasks/branches/one-task/references/style-persist.md). Approvals: [tool-approvals.md](../crav1-build-tasks/branches/one-task/references/tool-approvals.md). The rule is [open-skill-file.md](../crav1-docs/reference/open-skill-file.md) (1.134.0). Do not start `/crav1-create-feature-branch`. The consent section below still covers the checkout.

Branch files, only when that case applies: on `spec/<anything>`, Open `../crav1-create-feature-branch/SKILL.md` at **Build on a spec-only branch** (do not open it otherwise). Before the first checkout of a slug, Open `../crav1-create-feature-branch/references/code-branch.md`. When `--recommend`'s first line is not `feat/<slug>`, read `references/task-branches.md` (it opens `../crav1-create-feature-branch/references/task-branch.md`). Do not open that file when the line is `feat/<slug>`.

## Which slugs

| They typed | Queue |
| --- | --- |
| `auth-login billing` / comma-separated | Those slugs, in that order |
| No names / “all” / “rest” | Every **ready** slug (below), `docs/specs/` directory order |

**Ready** (all must hold):

- Folder `docs/specs/<slug>/` with `spec.md`, `plan.md`, `tasks.md` (not `_template/`)
- At least one `- [ ]` in `tasks.md`
- Those spec files exist **on the default branch** (`git show <default>:docs/specs/<slug>/spec.md` works). If they exist only on `spec/<slug>` or only in this dirty tree, **skip** with reason: merge specify-only first
- Not a landscape-only path (`docs/system/` is not a slug)

If the queue has **0** slugs: stop. If it has **exactly 1**: stop and tell them `/crav1-build-tasks` with that spec attached.

Unknown names: list, continue with the rest. Empty after skips: stop.

## Overlap (warn, then continue)

Before the first worker, union `plan.md` **Files likely touched** for queued slugs. If two slugs share paths (or clearly the same area), **warn** with the paths. Serial still runs in listed order (later merge/PR conflict is their problem). Do not drop a slug unless they say drop/skip.

## Style once

Before anything else that needs git commit, follow **style-persist.md**. If you must ask, this turn is style only.

Do not ask again per slug or `T#`. Workers must not ask style.

## Consent to branches (once)

Starting this command **is** consent to use `feat/<slug>` from the **into branch** (Merges into, else default) for each queued slug, in order. Do **not** re-run the create-feature-branch questions tool per slug.

One confirm if they are still on the default branch or on an unrelated branch: **continue** (first/top) = proceed with that checkout plan; **stop** = abort. If already on `feat/<first-slug>`, start there.

If currently on `spec/<anything>`: stop. No workers. Open `../crav1-create-feature-branch/SKILL.md` at **Build on a spec-only branch**. Do not open that file otherwise.

## Tool approvals (once for the whole board)

Follow [tool-approvals.md](../crav1-build-tasks/branches/one-task/references/tool-approvals.md) **once before the first worker** (you are an orchestrator, same as build-tasks).

Pass **`approvals: already-done`** and **`branch: already-done`** to every worker. Workers and nested `/crav1-build-tasks` must **not** pause. Do not start a nested `/crav1-build-tasks` skill (it would pause again). Open `../crav1-build-tasks/branches/several-tasks/BRANCH.md` from this skill's folder and run that **T# loop** yourself, as [open-skill-file.md](../crav1-docs/reference/open-skill-file.md) says.

Cloud Agents: skip the pause.

## Switch to a slug (before that slug’s first T#)

Into branch and base branches (1.99.0): Open `../crav1-create-feature-branch/references/code-branch.md` from this skill's folder. The into branch is the repo's `Merges into` branch (also read from a sibling specs repo), else the default branch.

1. When the working tree is dirty (anything other than `agent-tools/`), read `references/dirty-tree.md` before checkout. A clean tree skips it.
2. `git checkout feat/<slug>` if it exists, else `git switch -c feat/<slug> <into>` **from the into branch** (local, else `origin/<into>`), so a repo that merges into `develop` forks from `develop`, not `main`. Never create `feat/<slug>` from the previous feature branch.
3. If checkout fails, **block** this slug; do not start the next unless they skip.
4. Never `git push`. Never open a PR. Never `git commit` in this chat.

After a slug’s last worker, the tree should be clean (workers commit). Then switch to the next slug with this same procedure.

**Task branches (1.140.0).** Before each `T#`, the branch is the first line of `scripts/build_map.py docs/specs/<slug> --recommend T#` (skill `crav1-tasks-ready-to-build`). When that line is `feat/<slug>`, stay on it. Otherwise read `references/task-branches.md` before the worker. Do not open it when the line is `feat/<slug>`. A worker `needs_yes` is waiting, not blocked: read `references/needs-yes.md`. Do not open that file on `done`.

## Board (keep this updated)

```text
slug          branch           T#s      status
auth-login    feat/auth-login  T1–T4    running T2
billing       feat/billing     T1–T6    queued
```

Status: `queued` | `running` | `needs_fix` | `needs_ready` | `needs_dependency` | `done` | `blocked` | `skipped`.

The branch column shows each task's branch when tasks name one. A slug whose tasks are done but whose work branches are not all merged into their base shows `done (2 branches not merged)`, using the merged tests in skill `crav1-add-to-spec`, `references/branches.md`. A branch shared by several slugs is counted once on the board. This is report only.

## Per slug (you stay in this chat)

For each queued slug, after switch:

Open `../crav1-build-tasks/branches/several-tasks/BRANCH.md` and run that **T# loop** on **this** slug’s `tasks.md` (all remaining `- [ ]` unless they named a range **for that slug** — v1: all unchecked on that slug), in dependency order with its ready check before each `T#` (1.103.0). Do not start `/crav1-build-tasks`.

**Held (1.132.0).** The same gate as `/crav1-build-tasks`. `readiness` `result` `ready` or `ready-partial` starts tasks in `can_start`. A gate with `refused` true is refused with its reason. Do not ask to build it anyway. Skip it and continue with the next task that can start. When `result` is `not-ready`, do not start a worker on this slug.

1. Launch **crav1-build-task-agent** with this spec folder, this `T#`, `resume: start`, `approvals: already-done`, `branch: already-done`, style already set.
2. Wait for STATUS. Do not implement. Do not start `T+1` or the next slug while this worker is open.
3. Handle STATUS. `done`: next `T#` on **this** slug. If no unchecked left → slug `done`, switch to next slug. When STATUS is anything else, or the user says `skip-slug` or `stop`, read `references/worker-status.md`. Do not open it when every worker returns `done`.

## After the board

TL;DR: slugs `done` (with `n branches not merged` when that applies) / `blocked` + why / `skipped` / not started; which `feat/<slug>` tips you left on; commits workers reported.

Remind: **no push, no PR** from this skill. `Next: /crav1-open-pr, because the work is not on a pull request yet.` One pull request per `feat/<slug>`. Do not run it here. When the head's Match `Branch:` line ends in `(PR <n>)` or a pull request is known to be open for it, name it instead: `/crav1-open-pr` to push to PR <n> and update its description or comment.

Then **tool-approvals.md → Undo** once. Do not undo per slug or per `T#`.

## Picture offer

When this run marks a slug `done` on the board, or a slice on this board is marked `retired`, read `references/picture-offer.md` after the board TL;DR. Do not open it when no slug was marked done and none was marked retired.

## Parked and retired specs (1.60.0)

When a spec is under `docs/specs/retired/`, is only a `Moved:` pointer, or its `spec.md` has a `Parked:` line, read `references/parked.md`. Do not build it. Do not open that file for a ready slug.

## Hard rules

- Orchestration only: no product edits, no `git commit`, no push, no PR, no `spec.md` edits.
- Serial slugs. Serial `T#`s inside a slug. Never two workers at once.
- `feat/<slug>` always from the **into branch**, never from the previous feature. Never build on a base branch (1.99.0).
- Do not implement on `spec/<slug>`.
- Do not flatten the board into one implement pass.
- Do not invent Mode B (handoff/worktrees/Cloud Agents) in this skill.

## Run ending (1.122.0)

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says.
