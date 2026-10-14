# Build tasks

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when `plan.md` and `tasks.md` are accepted. Build one task `T#` at a time, in this chat or in an isolated worker. Prefer a fresh chat so the build is not mixed with the exploration that came before. If the agent drifts, revert, tighten the plan, and build again instead of patching in follow-ups.

| You want | Command |
| --- | --- |
| One task, here, and watch the diff | `/crav1-build-tasks T1` |
| One task, start to commit, in an isolated worker | `/crav1-build-tasks T1` |
| Several tasks on one spec | `/crav1-build-tasks T1-T3` (or all unchecked) |
| Several ready specs, one after another | `/crav1-build-features <slug-a> <slug-b>` (or all ready) |

## First prompt

```text
/crav1-build-tasks T1
@docs/specs/<slug>/
```

## Steps

| Step | You | Agent |
| --- | --- | --- |
| Branch | Pick the branch when asked | Each command calls `/crav1-create-feature-branch` before code. `/crav1-build-features` makes `feat/<slug>` from the default branch per slug without asking again |
| Linter gate | When `## Linter` says none and you have not chosen to go on, decide first | Stops with no code until you choose |
| Approvals (worker commands) | Answer the one pause: `continue` or `click` | `/crav1-build-tasks`, and `/crav1-build-features` pause once for the host's tool-approval setting, not per task or per slug. When the run ends they say how to restore it |
| Commit style (worker commands) | Pick a commit style once when asked | Writes the commit-style rule once when it is missing. Workers then commit without asking |
| Build | Watch the diff | `/crav1-build-tasks` writes the code and the checks the row names, runs that verify step, and marks the row `[x]` only when it passes. A worker (`crav1-build-task-agent`) does the same in isolation: implement, commit, verify, and an optional fix |
| Batch stop | Answer the worker | `/crav1-build-tasks` stops the batch when a worker needs you. `/crav1-build-features` runs specs one after another, never in parallel, and with one ready slug points at `/crav1-build-tasks` |
| Picture | Say yes or no | `/crav1-build-features` asks once whether to run `/crav1-refresh-system-notes` when a slice is marked done or retired, and does not run it. The other build commands do not ask |

Before the tests run, the kit checks their local dependencies (Azurite, a database container, an emulator) and asks start, skip, or stop for one that is down. A task whose tests skipped for a missing dependency is not ticked unless you chose skip. See [Local test dependencies](from-verify.md#local-test-dependencies).

## What gets written

- The code and checks for each task, and `[x]` on that row in `tasks.md` after its verify passes.
- Worker commands also write `verify.md`, `fix-log.md` when a fix runs, and the commits, plus the commit-style rule once.
- `/crav1-build-features`: a `feat/<slug>` checkout per slug.

Not written: `spec.md`, other tasks. No push, no pull request.

## After

Prove the slice against the spec: [Verify and fix](from-verify.md). Then [From commit to merge](from-commit.md).

Reference pages: [build-tasks](reference/skills/crav1-build-tasks.md) · [build-tasks](reference/skills/crav1-build-tasks.md) · [build-tasks](reference/skills/crav1-build-tasks.md) · [build-features](reference/skills/crav1-build-features.md) · [subagents](reference/skills.md#subagents)
