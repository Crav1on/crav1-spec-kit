# First 15 minutes

A thin path for someone new to **CRAV1 Spec Kit** (`crav1`) on Cursor or Claude Code. The slash commands are the same. The install is not. Full playbook: [The method](concepts/method.md). Every page: [docs index](README.md). Where files go: [install.md](install.md). After a Cursor plugin install: [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

## Starter options

When you ask for startup options, these seven are the only ways in. That ask names the list. It does not run a skill. It does not move work into a lane. Each starter still follows the rules it already has. Every other skill is a later skill.

| Starter | When |
| --- | --- |
| `/crav1-spark-to-spec` | One or two sentences |
| `/crav1-ideas-to-spec` | A pile of ideas and technical hunches |
| `/crav1-intake-to-specs` | Mixed files, or more than one v0 feature |
| `/crav1-match-to-specs` | Existing repos plus a dump to match |
| `/crav1-repos-to-spec` | You name the repos. It runs only then |
| `/crav1-environment-read` | You name the host. It runs only then |
| `/crav1-fix-bug` | You name a real bug that already exists. It runs only then |

The steps below are one thin path: a spark through one task. Pick another row in the table when that is the work in front of you.

## 1. Pick an install path

Install where the feature should land. Steps, host paths, and project versus user scope: [install.md](install.md).

- **Project drop-in** — commit the host tree (`.cursor/` or `.claude/`) in a repository you own.
- **User scope** — Cursor user plugin, or Claude Code `~/.claude/`. On a client project, use this unless that project asked for the kit in git.
- **Cursor plugin** — import [crav1-spec-kit](https://github.com/Crav1on/crav1-spec-kit) and install plugin `crav1` (team marketplace or local plugin). There is no public Cursor Marketplace listing. Claude Code has no plugin and no marketplace.
- **Learning in this kit repo** — the host trees are already present. Skip the copy and continue below.

If `/crav1` does not appear, reload or restart the host (see [install.md](install.md)).

## 2. Open the product repo

Open a chat in that repo. On Cursor that is Agent chat. On Claude Code, open a session in that repo. Use a strong reasoning model for specify and plan. The slash commands below are the same on either host.

## 3. List commands

Type `/crav1`.

## 4. Spark to a spec

```text
/crav1-spark-to-spec

Spark: <one or two sentences>

Treat this as greenfield. Ask questions first.
```

On an existing app, `@` the code and say it is a feature on this app. Answer the questions (about seven). The layout always includes `docs/system/`. The skill seeds a thin landscape when that folder is missing, including `glossary.md`, writes `docs/specs/<slug>/spec.md`, then adds one index row. An existing landscape stays in place. A missing `glossary.md` is filled. New glossary rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. On a brownfield repo it also asks for `feat/<slug>` (spec and build) or `spec/<slug>` (specify only).

## 5. Tighten

`/crav1-tighten-spec` walks one issue at a time. When the slice is partial or `## In the code` names paths, it reads the committed code on the repo and branch the spec names before wording issues. A spec with no code behind it skips that read. Then `/crav1-resolve-questions` for leftover Open questions the user still cares about.

## 6. Plan

Start a new chat. Run `/crav1-plan-from-spec`. Read `plan.md` and `tasks.md` and accept them. That step writes the plan and tasks only. When the spec is partial or `## In the code` names paths, it reads that repo and branch and lists each built piece before any task. Finish the gap, add a verify test, or leave it are the choices. A piece that already matches v0 is marked already there. The plan names a linter or checker when the repo has one for the code those tasks will touch, and Build is expected to leave that check green. When the repo has none, the plan says so and stops before Build. You decide to add the linter or to go on without one. The plan skill does not install one.

## 7. One task

`/crav1-implement-task` for one `T#` in `tasks.md`, then that task’s verify step.

## Where to go next

The starter options are the seven above. Asking for startup options names only the seven. Every other skill is a later skill.

| Next | Where |
| --- | --- |
| Why this loop | [The method](concepts/method.md) |
| The loop step by step | [From a draft spec to an accepted spec](from-draft-spec.md) → [From a spec to a plan](from-spec-to-plan.md) → [Build tasks](from-plan-to-build.md) → [Verify and fix](from-verify.md) → [From commit to merge](from-commit.md) |
| Prove a slice | `/crav1-verify-spec` |
| Push and open a pull request | `/crav1-open-pr` (after commits exist; does not merge; may name `/crav1-review-pr` and does not run it) |
| Merge a named pull request | `/crav1-merge-pr` (only when that turn asks; merge commit only; does not run the review) |
| Any other situation: a walkthrough for each starter and later skill | [Docs index](README.md#how-to-walkthroughs) |
| One command in full | [Skills reference](reference/skills.md) |
| Broken install or skill | [SUPPORT.md](../SUPPORT.md) |
