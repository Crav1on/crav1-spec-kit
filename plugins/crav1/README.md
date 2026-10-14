# crav1 (Cursor plugin)

You installed the **crav1** Cursor plugin from **CRAV1 Spec Kit**. Plugin id: `crav1`. This page is the short start **after** that Cursor plugin install. There is no public Cursor Marketplace listing. Cursor installs this plugin from this GitHub repo (team marketplace import or a local plugin).

Claude Code has no plugin and no marketplace. The slash commands are the same. Copy `.claude/` into a repository you own, or into `~/.claude` for a client project. Cloning the kit does not install it into another product. Where files go: [docs/install.md](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/install.md). A thin path from install through one task is [docs/first-run.md](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/first-run.md). For the full playbook, see [the method](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/concepts/method.md). Every page: [docs index](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/README.md).

Cursor Plan Mode is not `plan.md`. Claude Code plan mode is not those files either (same install doc). `/crav1-plan-from-spec` writes `plan.md` and `tasks.md`.

Type `/crav1` in Cursor Agent chat to list commands. On Claude Code, type the same `/crav1` in the session.

## Starter options

When you ask for startup options, these six are the only ways in. That ask names the list. It does not run a skill. It does not move work into a lane. Each starter still follows the rules it already has. Every other skill is a later skill.

| Starter | When |
| --- | --- |
| [`/crav1-spark-to-spec`](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/reference/skills/crav1-spark-to-spec.md) | One or two sentences |
| [`/crav1-ideas-to-spec`](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/reference/skills/crav1-ideas-to-spec.md) | A pile of ideas and technical hunches |
| [`/crav1-bundle-to-specs`](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/reference/skills/crav1-bundle-to-specs.md) | Mixed files, or more than one v0 feature |
| [`/crav1-existing-to-specs`](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/reference/skills/crav1-existing-to-specs.md) | Existing repos plus a dump to match |
| [`/crav1-existing-to-specs`](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/reference/skills/crav1-existing-to-specs.md) | You name the repos. It runs only then |
| [`/crav1-read-environment`](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/reference/skills/crav1-read-environment.md) | You name the host. It runs only then |
| [`/crav1-fix-bug`](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/reference/skills/crav1-fix-bug.md) | You name a real bug that already exists. It runs only then |

## What is in this plugin

Every skill and subagent, grouped by lane (Specify, Plan, Build, Cross-cutting), with what it reads, writes, and leaves alone, is in the [skills reference](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/reference/skills.md). Each command has its own page there, for example [`/crav1-spark-to-spec`](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/reference/skills/crav1-spark-to-spec.md), linked to its walkthrough.

- Skills: `/crav1-…`. Type `/crav1` to list them.
- Help: `/crav1-help` answers what to run next, in what order, and what a command does, from the docs bundled in this plugin (`skills/crav1-docs/`), for this exact version. Every answer names its source.
- Docs: the kit's `docs/` for this release in `skills/crav1-docs/`, including [Workflow routes](skills/crav1-docs/reference/workflow.md).
- Subagents: `crav1-spec-reviewer-agent`, `crav1-review-architecture-agent`, `crav1-plan-reviewer-agent`, `crav1-build-task-agent`, and `crav1-bundle-slice-agent`. See [Subagents](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/reference/skills.md#subagents).
- Rule: specs live under `docs/specs/`; system landscape under `docs/system/`. Every folder the kit writes: [Data layout](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/concepts/data-layout.md).

Templates ship inside each skill’s `assets/`. Copy `docs/specs/_template/` and `docs/system/_template/` from the kit repo if you want visible starter folders.

## How to use (first change)

Work in your **product** repo, not only the kit clone.

1. **New chat.** On Cursor that is Agent chat. On Claude Code, open a session in the product repo. Strong reasoning model for specify/plan. The slash commands below are the same on either host.
2. **Start** with one starter option from the table above. Asking for startup options names only those six and does not run one. `/crav1-existing-to-specs` still runs only when you name the repos, `/crav1-read-environment` only when you name the host (naming production, prod, or live stops), and `/crav1-fix-bug` only when you name a real bug that already exists. What each starter reads and writes is on its page, linked from the table.

   Later skills, once specs already exist, are listed by lane in the [skills reference](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/reference/skills.md), each with its walkthrough. Those are not starter options.
3. Answer questions (including branch: `feat/<slug>` or specify-only `spec/<slug>` on a brownfield repo). Stop when v0 is demoable from the acceptance list. After `/crav1-bundle-to-specs` Index, run `/crav1-finalize-commit` if you want landscape + specs in git before review (intake only prompts; it does not commit). After `/crav1-existing-to-specs`, run `/crav1-finalize-commit` the same way. Plan only a slice you choose to start. A slice that is not in the code is not planned by that command. After `/crav1-add-to-spec`, run `/crav1-finalize-commit` the same way if those spec edits should be in git. Plan only a slice you choose. Anything that fit no spec stays listed. After `/crav1-add-to-spec`, run `/crav1-finalize-commit` only if those spec edits should be committed. Plan only a slice you choose. Anything that fit no spec stays listed. That command does not watch the repo.
4. `/crav1-review-architecture` if there are real design hunches, then `/crav1-tighten-spec` **one issue at a time**. Optional, when the design already exists: `/crav1-review-security`. Architecture review does not run it. Spark, plan, and verify do not run it.
5. `/crav1-resolve-open-questions` for leftover `Q#`s you still care about.
6. **New chat.** `/crav1-plan-from-spec`. You accept `plan.md` / `tasks.md`. Still no product code in that step. The plan names a linter or checker when the repo has one, and stops before Build when it does not. You decide to add the linter or to go on without one. The plan skill does not install one. Optional: `/crav1-review-plan` then `/crav1-tighten-plan`. On `spec/<slug>`, do not implement; merge that branch first, then `/crav1-create-feature-branch` → `feat/<slug>`.
7. `/crav1-build-tasks` for **one** `T#`, or `/crav1-build-tasks` for an isolated worker. Several `T#`s on one spec: `/crav1-build-tasks T1-T3`. Several specs, one after another: `/crav1-build-features auth-login billing` (or omit names for all ready). build-tasks / build-features **pause once** (`continue` / `click`). On Cursor that pause points at Settings. On Claude Code it is the permission prompt ([docs/install.md](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/install.md)). They do not pause again per `T#` or per slug. When the run ends they remind you how to restore the previous mode.
8. If you implemented by hand: `/crav1-verify-build-against-spec`. If something in the inner loop is wrong, `/crav1-fix-build-gaps` (omit Gap to take the next). Unimplemented tasks go back to step 7, not the fix skill.
9. When you want a commit message: `/crav1-finalize-commit` (paste into your git client) or `/crav1-finalize-commit` (draft, then **commit** first, or copy / edit).
10. When you want a pull request: `/crav1-open-pr` (push only if you say yes). It does not merge. Next (optional, later turn): `/crav1-review-pr` when you name that pull request. Open-pr does not run it. Merge is `/crav1-merge-pr` when you explicitly ask to merge that named pull request. Merge commit only. A review is not a merge ask. Merge still stops when a required host check is red.

Optional Azure Boards link: `docs/specs/<slug>/work-item.md`, one id per line (`Work item: <id>` or `Work item: <id> — <label>`). A single unlabeled line is still read. The mention picks the line whose label matches the slice being worked, and asks when that is unclear. On Azure Repos, spark, ideas, and intake ask once after a new spec folder and write a line only if the user gives an id. The user can also add the file by hand. Commit skills append `#<id>` on Azure Repos or `AB#<id>` on GitHub as the last description line. `/crav1-open-pr` adds a Work item section. No file means those steps continue, with one hint on Azure Repos only. Creating a Feature is `/crav1-ado-sync`. Sending a spec's tasks as children of that Feature is `/crav1-ado-sync` ([docs/from-tasks-to-ado.md](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/from-tasks-to-ado.md)). See [docs/from-ideas.md](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/from-ideas.md) and [docs/from-specs-to-ado.md](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/from-specs-to-ado.md).

Do not start with “pick a stack and generate the app” unless the spec already says to. Quick typos and one-file bugs can skip this loop. On Cursor, use Agent mode directly. On Claude Code, use a normal session in that repo.

## If `/crav1` is missing

On Cursor: reload the window. Confirm **crav1** is installed in **Customize** (project or user). Drop-in installs need `.cursor/skills/crav1/` committed in this workspace.

On Claude Code there is no plugin. If the command is missing, see [docs/install.md](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/install.md) (restart after a new skills directory). Project skills live under `.claude/skills/`.
