# First 15 minutes

A thin path for someone new to **CRAV1 Spec Kit** (`crav1`). Full playbook: [README](../README.md). Install detail: [install.md](install.md). After a plugin install: [plugins/crav1/README.md](../plugins/crav1/README.md).

## 1. Pick an install path

Install into the **product repo** where the feature should land. Steps and trade-offs: [install.md](install.md).

- **Drop-in copy** — copy `.cursor/skills/crav1/`, `.cursor/agents/crav1-*.md`, `.cursor/agent-assets/crav1-*`, and `.cursor/rules/crav1.mdc` into that repo. Leave `.cursor/rules/kit-maintainer.mdc` in the kit repo.
- **Cursor plugin** — import [crav1-spec-kit](https://github.com/Crav1on/crav1-spec-kit) and install plugin `crav1` (team marketplace or a local copy of `plugins/crav1`).
- **Learning in this kit repo** — `.cursor/` is already present. Skip the copy and continue below.

Reload the window if `/crav1` does not appear (`Developer: Reload Window`).

## 2. Open the product repo

Open Agent chat in that repo. Use a strong reasoning model for specify and plan.

## 3. List commands

Type `/crav1`.

## 4. Spark to a spec

```text
/crav1-spark-to-spec

Spark: <one or two sentences>

Treat this as greenfield. Ask questions first.
```

On an existing app, `@` the code and say it is a feature on this app. Answer the questions (about seven). The skill writes `docs/specs/<slug>/spec.md`. On a brownfield repo it also asks for `feat/<slug>` (spec and build) or `spec/<slug>` (specify only).

## 5. Tighten

`/crav1-tighten-spec` walks one issue at a time. Then `/crav1-resolve-questions` for leftover Open questions you still care about.

## 6. Plan

Start a new chat. Run `/crav1-plan-from-spec`. Read `plan.md` and `tasks.md` and accept them. That step writes the plan and tasks only.

## 7. One task

`/crav1-implement-task` for one `T#` in `tasks.md`, then that task’s verify step.

## Where to go next

| Next | Where |
| --- | --- |
| Why this loop | [README](../README.md) |
| One-sentence spark in more depth | [from-nothing.md](from-nothing.md) |
| Pile of ideas and tech hunches | [from-ideas.md](from-ideas.md) · `/crav1-ideas-to-spec` |
| Several features or repos | [from-intake.md](from-intake.md) · `/crav1-intake-to-specs` |
| Prove a slice | `/crav1-verify-spec` |
| Push and open a pull request | `/crav1-open-pr` (after commits exist; does not merge) |
| Merge a named pull request | `/crav1-merge-pr` (only when that turn asks; merge commit only) |
| Broken install or skill | [SUPPORT.md](../SUPPORT.md) |
