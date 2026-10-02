# First 15 minutes

A thin path for someone new to **CRAV1 Spec Kit** (`crav1`). Full playbook: [README](../README.md). Install detail: [install.md](install.md). After a plugin install: [plugins/crav1/README.md](../plugins/crav1/README.md).

## 1. Pick an install path

Install where the feature should land. Steps, host paths, and project versus user scope: [install.md](install.md).

- **Project drop-in** — commit the host tree (`.cursor/` or `.claude/`) in a repository you own.
- **User scope** — Cursor user plugin, or Claude Code `~/.claude/`. On a client project, use this unless that project asked for the kit in git.
- **Cursor plugin** — import [crav1-spec-kit](https://github.com/Crav1on/crav1-spec-kit) and install plugin `crav1`. There is no Claude Code marketplace in this kit.
- **Learning in this kit repo** — the host trees are already present. Skip the copy and continue below.

If `/crav1` does not appear, reload or restart the host (see [install.md](install.md)).

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

On an existing app, `@` the code and say it is a feature on this app. Answer the questions (about seven). The layout always includes `docs/system/`. The skill seeds a thin landscape when that folder is missing, writes `docs/specs/<slug>/spec.md`, then adds one index row. An existing landscape stays in place. On a brownfield repo it also asks for `feat/<slug>` (spec and build) or `spec/<slug>` (specify only).

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
| Existing repos plus a dump to match | [from-match.md](from-match.md) · `/crav1-match-to-specs` |
| A later dump onto specs that already exist | [from-match-dump.md](from-match-dump.md) · `/crav1-match-dump-to-specs` |
| A code change that already landed, specs already exist | [from-code.md](from-code.md) · `/crav1-code-into-specs` |
| New information for one existing spec | [from-add.md](from-add.md) · `/crav1-add-to-spec` |
| Prove a slice | `/crav1-verify-spec` |
| Push and open a pull request | `/crav1-open-pr` (after commits exist; does not merge) |
| Merge a named pull request | `/crav1-merge-pr` (only when that turn asks; merge commit only) |
| Broken install or skill | [SUPPORT.md](../SUPPORT.md) |
