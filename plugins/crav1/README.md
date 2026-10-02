# crav1

You installed the **crav1** Cursor plugin from **CRAV1 Spec Kit**. This is the short start **after** that plugin install. For how to install (Cursor copy vs plugin vs local, or the Claude Code `.claude/` drop-in), see [docs/install.md](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/install.md). In the kit repo, the same file is [docs/install.md](../../docs/install.md). A thin path from install through one task is [docs/first-run.md](https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/first-run.md) ([docs/first-run.md](../../docs/first-run.md) in the kit repo). For the full playbook, see that repo’s README.

This plugin and its marketplace are Cursor-only. Claude Code has no plugin in this kit. Its drop-in is the generated `.claude/` tree in the install doc. The host plan UI is not `plan.md`; `/crav1-plan-from-spec` writes `plan.md` and `tasks.md`.

Type `/crav1` in Agent chat to list commands.

## What is in this plugin

**Specify**

- `/crav1-spark-to-spec` — one or two sentences → questions → thin `docs/system/` when missing, then `docs/specs/<slug>/spec.md`, then one index row (greenfield, a feature on an existing app, or a later feature on an existing landscape). An existing landscape is left in place. On Azure Repos, one optional work-item id after a new spec folder
- `/crav1-feature-branch` — `feat/<slug>` (spec+build) or `spec/<slug>` then later `feat/<slug>` (specify while another feature builds); no push, no PR
- `/crav1-ideas-to-spec` — idea pile + technical hunches → thin `docs/system/` when missing, then spec, diagrams, ADRs, export format, then one index row. An existing landscape is left in place. On Azure Repos, one optional work-item id after a new spec folder
- `/crav1-intake-to-specs` — mixed intake → `docs/system/` + one spec per v0 feature. On Azure Repos, one optional work-item question listing the new slugs
- `/crav1-match-to-specs` — existing repos plus a dump → where the spec files go, then `docs/system/` and one spec per confirmed slice (done, partial, or not in the code). Does not plan, implement, or commit
- `/crav1-match-dump-to-specs` — a later dump, specs already exist → sort onto those specs (belongs, already there, or does not fit), then quote the new bits. Does not ask for a slug first. Does not create a slug. Does not plan, implement, or commit
- `/crav1-add-to-spec` — new information for one existing spec → add it to that spec, then report whether the landscape or another spec has to change. Does not rewrite those files unless asked. Does not plan, implement, or commit
- `/crav1-architecture-reviewer` — runs the architecture critic; numbered issues (`I#`)
- `/crav1-tighten-spec` — one issue at a time; you pick (or ask for a suggestion); it patches only that issue
- `/crav1-resolve-questions` — one Open question (`Q#`); keep or answer
- `/crav1-export-spec` — re-project `spec.md` (EARS, BDD, OpenSpec, YAML, JSON, BMAD)

**Build**

- `/crav1-plan-from-spec` — `plan.md` + `tasks.md` (no code)
- `/crav1-review-plan` — critique plan/tasks vs spec; numbered `P#`s
- `/crav1-tighten-plan` — one plan `P#`; patches `plan.md` / `tasks.md` only
- `/crav1-implement-task` — one `T#`, then its verify step
- `/crav1-complete-task` — isolated worker: one `T#` implement → commit → verify → optional fix (persist commit style)
- `/crav1-complete-tasks` — orchestrates one worker per `T#` (`T1-T3` or all unchecked)
- `/crav1-complete-features` — several ready specs, **serial** (one `feat/<slug>` from default, then its T#s); one spec still `/crav1-complete-tasks`
- `/crav1-verify-spec` — TL;DR of implemented vs not, then `verify.md`
- `/crav1-fix-from-verify` — inner-loop gaps only (failed → unverified → `G#`); does not edit `spec.md`
- `/crav1-fix-live` — same queue, live-path hint (ports, proxy, SQL)

**Also**

- `/crav1-draft-commit-message` — GitKraken Summary/Description paste; does not commit unless you ask. An optional `docs/specs/<slug>/work-item.md` line is appended as the last description line
- `/crav1-finalize-commit` — style if needed, then the draft, then **commit** first, then copy / edit / rewrite / stop (no push). If Cursor appends `Co-authored-by`, the skill strips it once from that unpushed commit and keeps the work-item line.
- `/crav1-open-pr` — push the change branch only after an explicit yes, then open one pull request against the default branch (no merge, no commit). The body includes a Work item section when `work-item.md` exists. On Windows, a multi-line Azure DevOps description is `--description "@<file>"` (UTF-8 without BOM). A later merge is `/crav1-merge-pr`
- `/crav1-merge-pr` — merge one named pull request only when you explicitly ask in that turn; merge commit only (no squash, no rebase, no policy bypass). Two parents are confirmed with `git rev-list` after the completed re-read
- Subagent `crav1-spec-reviewer-agent` — product/spec critique (invoke by asking to review the spec)
- Subagent `crav1-architecture-reviewer-agent` — used by `/crav1-architecture-reviewer`
- Subagent `crav1-plan-reviewer-agent` — used by `/crav1-review-plan`
- Subagent `crav1-complete-task-agent` — worker for `/crav1-complete-task`, `/crav1-complete-tasks`, and `/crav1-complete-features` (one `T#`)
- Subagent `crav1-intake-slice-agent` — used by `/crav1-intake-to-specs` (one slug)
- Rule: specs live under `docs/specs/`; system landscape under `docs/system/`

Templates ship inside each skill’s `assets/`. Copy `docs/specs/_template/` and `docs/system/_template/` from the kit repo if you want visible starter folders.

## How to use (first change)

Work in your **product** repo, not only the kit clone.

1. **New Agent chat.** Strong reasoning model for specify/plan.
2. **Specify.** Either:
   - `/crav1-spark-to-spec` plus a one- or two-sentence spark, or
   - `/crav1-ideas-to-spec` plus one blob of ideas and tech hunches (no required structure), or
   - `/crav1-intake-to-specs` plus `@` files (notes, diagrams, optional code as context), or
   - `/crav1-match-to-specs` plus the repos that already make up the system and a dump to match (notes, tickets, old docs, diagrams, screenshots), or
   - `/crav1-match-dump-to-specs` plus a later dump when specs already exist (notes, tickets, old docs, diagrams, screenshots), or
   - `/crav1-add-to-spec` plus new information for one spec that already exists.
3. Answer questions (including branch: `feat/<slug>` or specify-only `spec/<slug>` on a brownfield repo). Stop when v0 is demoable from the acceptance list. After `/crav1-intake-to-specs` Index, run `/crav1-finalize-commit` if you want landscape + specs in git before review (intake only prompts; it does not commit). After `/crav1-match-to-specs`, run `/crav1-finalize-commit` the same way. Plan only a slice you choose to start. A slice that is not in the code is not planned by that command. After `/crav1-match-dump-to-specs`, run `/crav1-finalize-commit` the same way if those spec edits should be in git. Plan only a slice you choose. Anything that fit no spec stays listed.
4. `/crav1-architecture-reviewer` if there are real design hunches, then `/crav1-tighten-spec` **one issue at a time**.
5. `/crav1-resolve-questions` for leftover `Q#`s you still care about.
6. **New chat.** `/crav1-plan-from-spec`. You accept `plan.md` / `tasks.md`. Still no product code in that step. Optional: `/crav1-review-plan` then `/crav1-tighten-plan`. On `spec/<slug>`, do not implement; merge that branch first, then `/crav1-feature-branch` → `feat/<slug>`.
7. `/crav1-implement-task` for **one** `T#`, or `/crav1-complete-task` for an isolated worker. Several `T#`s on one spec: `/crav1-complete-tasks T1-T3`. Several specs, one after another: `/crav1-complete-features auth-login billing` (or omit names for all ready). complete-task / complete-tasks / complete-features **pause once** with Settings directions (`continue` / `click`); they do not pause again per `T#` or per slug. When the run ends they remind you how to restore the previous mode.
8. If you implemented by hand: `/crav1-verify-spec`. If something in the inner loop is wrong, `/crav1-fix-from-verify` (omit Gap to take the next). Unimplemented tasks go back to step 7, not the fix skill.
9. When you want a commit message: `/crav1-draft-commit-message` (paste into GitKraken) or `/crav1-finalize-commit` (draft, then **commit** first, or copy / edit).
10. When you want a pull request: `/crav1-open-pr` (push only if you say yes). It does not merge. Next (optional, later turn): `/crav1-merge-pr` when you explicitly ask to merge that named pull request. Merge commit only.

Optional Azure Boards link: `docs/specs/<slug>/work-item.md` with `Work item: <id>`. On Azure Repos, spark, ideas, and intake ask once after a new spec folder and write that line only if the user gives an id. The user can also add the file by hand. Commit skills append `#<id>` on Azure Repos or `AB#<id>` on GitHub as the last description line. `/crav1-open-pr` adds a Work item section. No file means those steps continue, with one hint on Azure Repos only. Creating the work item in Azure Boards is out of scope. See [docs/from-ideas.md](../../docs/from-ideas.md).

Do not start with “pick a stack and generate the app” unless the spec already says to. Quick typos and one-file bugs can skip this loop and use Agent mode directly.

## If `/crav1` is missing

Reload the window. Confirm **crav1** is installed in **Customize** (project or user). Drop-in installs need `.cursor/skills/crav1/` committed in this workspace.
