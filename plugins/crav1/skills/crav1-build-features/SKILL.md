---
name: crav1-build-features
description: >-
  Serial board: build several ready specs one slug after another in this
  checkout. Each slug is feat/<slug> from default, then the build-tasks
  T# loop. Not parallel. One slug: use /crav1-build-tasks. Do not push.
  Do not open a PR.
disable-model-invocation: true
icon: list
color: green
---

# Orchestrate several features (serial)

You **manage** a queue of **slugs**. You do **not** implement, verify, or `git commit` in this chat.

Each slug is one feature: `docs/specs/<slug>/` + branch `feat/<slug>` created from the **default** branch (not from the previous feature). Inside a slug, reuse the `/crav1-build-tasks` loop: one **crav1-build-task-agent** worker per `T#`, one at a time.

This is **not** parallel. Two `feat/` branches cannot share this working tree. True parallel (handoff / worktrees / Cloud Agents) is **out of scope** for this skill.

Command: `/crav1-build-features`. One spec: `/crav1-build-tasks`. One task: `/crav1-build-tasks`.

Worker: `.cursor/agents/crav1-build-task-agent.md` (plugin: `agents/crav1-build-task-agent.md`). Protocol: `crav1-build-tasks` [references/run.md](../crav1-build-tasks/branches/one-task/references/run.md). Style: [style-persist.md](../crav1-build-tasks/branches/one-task/references/style-persist.md). Approvals: [tool-approvals.md](../crav1-build-tasks/branches/one-task/references/tool-approvals.md). Branch rules: `/crav1-create-feature-branch` (drop-in: `.cursor/skills/crav1/crav1-create-feature-branch/SKILL.md`; plugin: sibling `skills/crav1-create-feature-branch/SKILL.md`).

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

Starting this command **is** consent to use `feat/<slug>` from **default** for each queued slug, in order. Do **not** re-run the create-feature-branch questions tool per slug.

One confirm if they are still on the default branch or on an unrelated branch: **continue** (first/top) = proceed with that checkout plan; **stop** = abort. If already on `feat/<first-slug>`, start there.

If currently on `spec/<anything>`: stop. No workers. Follow create-feature-branch **Build on a spec-only branch**.

## Tool approvals (once for the whole board)

Follow [tool-approvals.md](../crav1-build-tasks/branches/one-task/references/tool-approvals.md) **once before the first worker** (you are an orchestrator, same as build-tasks).

Pass **`approvals: already-done`** and **`branch: already-done`** to every worker. Workers and nested `/crav1-build-tasks` must **not** pause. Do not start a nested `/crav1-build-tasks` skill (it would pause again); run its **T# loop yourself**.

Cloud Agents: skip the pause.

## Switch to a slug (before that slug’s first T#)

Default branch: same detect as create-feature-branch (`origin/HEAD`, else `main` / `master` / `develop`).

1. Working tree dirty except `agent-tools/` → **do not checkout**. Tell them `/crav1-finalize-commit` (or they clean it). Wait. Never stash unless they ask.
2. `git checkout <default>` then `git checkout feat/<slug>` if it exists, else `git checkout -b feat/<slug>` **from default**. Never create `feat/<slug>` from the previous feature branch.
3. If checkout fails, **block** this slug; do not start the next unless they skip.
4. Never `git push`. Never open a PR. Never `git commit` in this chat.

After a slug’s last worker, the tree should be clean (workers commit). Then switch to the next slug with this same procedure.

**Task branches (1.64.0).** Inside a slug, a task that ends with `(branch: X)` is built on X: switch to X before its worker, only on a clean tree (`git checkout X`, which also makes the local branch from `origin/X`). Tasks without a branch part use `feat/<slug>` from default, as above. Starting the board is consent to these switches. When X exists nowhere, that task is `blocked` with the reason `branch X not found`; never create X. A `(branch: <repo> X)` for another repo is `blocked` with `belongs to <repo>`.

## Board (keep this updated)

```text
slug          branch           T#s      status
auth-login    feat/auth-login  T1–T4    running T2
billing       feat/billing     T1–T6    queued
```

Status: `queued` | `running` | `needs_fix` | `needs_ready` | `needs_dependency` | `done` | `blocked` | `skipped`.

The branch column shows each task's branch when tasks name one. A slug whose tasks are done but whose work branches are not all merged into their base shows `done (2 branches not merged)`, using the merged tests in `crav1-add-to-spec` `references/branches.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`). A branch shared by several slugs is counted once on the board. This is report only.

## Per slug (you stay in this chat)

For each queued slug, after switch:

Run the build-tasks **T# loop** on **this** slug’s `tasks.md` (all remaining `- [ ]` unless they named a range **for that slug** — v1: all unchecked on that slug).

1. Launch **crav1-build-task-agent** with this spec folder, this `T#`, `resume: start`, `approvals: already-done`, `branch: already-done`, style already set.
2. Wait for STATUS. Do not implement. Do not start `T+1` or the next slug while this worker is open.
3. Handle STATUS:

| STATUS | Orchestrator |
| --- | --- |
| `done` | Next `T#` on **this** slug. If no unchecked left → slug `done`, switch to next slug. |
| `needs_fix` | Ask `fix` / `skip-slug` / `stop`. `fix` → same `T#` worker `resume: fix`. |
| `needs_ready` | Ask them to refresh the live host, then `ready` / `skip-slug` / `stop`. `ready` → `resume: ready`. |
| `needs_dependency` | Show the BLOCKER line at the top. Ask start / skip / `skip-slug` / stop. `start` → `resume: dependency-start`; `skip` → `resume: dependency-skip`. Headless: two-pass questions file. |
| `blocked` / `failed` | Slug `blocked`. **End the board.** Do not start the next slug. |
| User `skip-slug` | Mark skipped. Switch to next slug (if any). |
| User `stop` | End the board. |

Do not skip a blocked slug unless they `skip-slug`.

## After the board

TL;DR: slugs `done` (with `n branches not merged` when that applies) / `blocked` + why / `skipped` / not started; which `feat/<slug>` tips you left on; commits workers reported.

Remind: **no push, no PR** from this skill. Next (optional): `/crav1-open-pr` when you want to push and open the PR (one PR per `feat/<slug>`; do not run it here).

Then **tool-approvals.md → Undo** once. Do not undo per slug or per `T#`.

## Picture offer

When this run marks a slug `done` on the board, or a slice on this board is marked `retired`, ask once at the end, after the board TL;DR. A slice is marked `retired` when the user says it is retired in this run, or that slug’s feature-index Notes or `## Match` status says `retired`. Do not write `retired` into a file. Do not edit `spec.md`.

Ask once for the board, not once per slug. The question is exactly:

The system picture may now be out of date. Run `/crav1-refresh-system-notes`?

Options are yes and no. Use the questions tool when it is available. Do not run `/crav1-refresh-system-notes`. A yes waits for a later turn. A no ends without that command.

Do not ask when no slug was marked done and none was marked retired. Do not add this question to `/crav1-build-tasks`.

## Parked and retired specs (1.60.0)

Skip every spec under `docs/specs/retired/`, and every old-path `spec.md` that is only a `Moved:` pointer. A spec whose `spec.md` has a `Parked:` line is parked: do not build it, and leave it off the board's to-build list. Say `skipped: <slug> (parked)` and name `/crav1-retire-spec un-park docs/specs/<slug>/`. Do not remove the mark.

## Hard rules

- Orchestration only: no product edits, no `git commit`, no push, no PR, no `spec.md` edits.
- Serial slugs. Serial `T#`s inside a slug. Never two workers at once.
- `feat/<slug>` always from **default**, never from the previous feature.
- Do not implement on `spec/<slug>`.
- Do not flatten the board into one implement pass.
- Do not invent Mode B (handoff/worktrees/Cloud Agents) in this skill.
