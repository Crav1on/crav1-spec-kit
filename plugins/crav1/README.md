# crav1

You installed the **crav1** Cursor plugin. This is the short start **after** install. For how to install (copy vs plugin vs local), see [docs/install.md](../../docs/install.md) in the kit repo. For the full playbook, see that repo’s README.

Type `/crav1` in Agent chat to list commands.

## What is in this plugin

**Specify**

- `/crav1-spark-to-spec` — one or two sentences → questions → `docs/specs/<slug>/spec.md`
- `/crav1-ideas-to-spec` — idea pile + technical hunches → spec, diagrams, ADRs, export format
- `/crav1-architecture-reviewer` — runs the architecture critic; numbered issues (`I#`)
- `/crav1-tighten-spec` — one issue at a time; you pick; it patches only that issue
- `/crav1-resolve-questions` — one Open question (`Q#`); keep or answer
- `/crav1-export-spec` — re-project `spec.md` (EARS, BDD, OpenSpec, YAML, JSON, BMAD)

**Build**

- `/crav1-plan-from-spec` — `plan.md` + `tasks.md` (no code)
- `/crav1-implement-task` — one `T#`, then its verify step
- `/crav1-complete-task` — isolated worker: one `T#` implement → commit → verify → optional fix (persist commit style)
- `/crav1-complete-tasks` — orchestrates one worker per `T#` (`T1-T3` or all unchecked)
- `/crav1-verify-spec` — TL;DR of implemented vs not, then `verify.md`
- `/crav1-fix-from-verify` — inner-loop gaps only (failed → unverified → `G#`); does not edit `spec.md`
- `/crav1-fix-live` — same queue, live-path hint (ports, proxy, SQL)

**Also**

- `/crav1-draft-commit-message` — GitKraken Summary/Description paste; does not commit unless you ask
- `/crav1-finalize-commit` — style if needed, then the draft, then copy / edit / rewrite / `git commit` (no push). If Cursor appends `Co-authored-by`, the skill strips it once from that unpushed commit.
- Subagent `crav1-spec-reviewer` — product/spec critique (invoke by asking to review the spec)
- Subagent `crav1-architecture-reviewer` — used by the slash command above
- Rule: specs live under `docs/specs/`

Templates ship inside each skill’s `assets/`. Copy `docs/specs/_template/` from the kit repo if you want a visible starter folder.

## How to use (first change)

Work in your **product** repo, not only the kit clone.

1. **New Agent chat.** Strong reasoning model for specify/plan.
2. **Specify.** Either:
   - `/crav1-spark-to-spec` plus a one- or two-sentence spark, or
   - `/crav1-ideas-to-spec` plus bullets of ideas and tech hunches.
3. Answer questions. Stop when v0 is demoable from the acceptance list.
4. `/crav1-architecture-reviewer` if there are real design hunches, then `/crav1-tighten-spec` **one issue at a time**.
5. `/crav1-resolve-questions` for leftover `Q#`s you still care about.
6. **New chat.** `/crav1-plan-from-spec`. You accept `plan.md` / `tasks.md`. Still no product code in that step.
7. `/crav1-implement-task` for **one** `T#`, or `/crav1-complete-task` for an isolated worker that takes that row through commit and verify (optional fix). Several rows: `/crav1-complete-tasks T1-T3` (orchestrator; one worker per task) or omit the range for all unchecked. Those two commands **pause once** with Settings directions (`continue` / `click`); complete-tasks does not pause again per `T#`. When the run ends they remind you how to restore the previous mode.
8. If you implemented by hand: `/crav1-verify-spec`. If something in the inner loop is wrong, `/crav1-fix-from-verify` (omit Gap to take the next). Unimplemented tasks go back to step 7, not the fix skill.
9. When you want a commit message: `/crav1-draft-commit-message` (paste into GitKraken) or `/crav1-finalize-commit` (edit, then copy or commit).

Do not start with “pick a stack and generate the app” unless the spec already says to. Quick typos and one-file bugs can skip this loop and use Agent mode directly.

## If `/crav1` is missing

Reload the window. Confirm **crav1** is installed in **Customize** (project or user). Drop-in installs need `.cursor/skills/crav1/` committed in this workspace.
