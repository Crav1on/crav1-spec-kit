# crav1 kit

Specs, not chat history, are the source of truth. Put change work under `docs/specs/<change-id>/`. The layout always includes `docs/system/`. Spark and ideas seed a thin landscape when that folder is missing, including `glossary.md`, and do not rewrite an existing one except new glossary rows and the picture update. They fill a missing `glossary.md` when the folder already exists, and append only new rows when the file exists. Intake writes the landscape, including `glossary.md`, and does not skip it. Existing glossary rows are not rewritten. The picture update adds what is new to the short description, the diagram, and how the parts connect, and does not rewrite what is already there. A meaning the source does not state is `to be researched`. `docs/system/repos.md` has a per-repo `Synced at` column, `<branch>@<short sha>, <date>`. A repo may list several branches, separated by `; `. Example: `main@abc1234, 2026-10-07; develop@def5678, 2026-10-06`. When `/crav1-refresh-system-notes`, `/crav1-existing-to-specs`, `/crav1-add-to-spec`, or `/crav1-bundle-to-specs` and `/crav1-ideas-to-spec` (where they read repos) read a whole repo, they set that repo's column to the branch and commit they actually read. They touch only the repos they read. When a run reads only one slice, it does not touch the repo column. It writes or updates `Synced at: <repo> <branch>@<short sha>, <date>` in that slice's `spec.md`. A consumer measuring drift uses the older of the repo column and the slice line, and an empty value means unknown, so fall back to spec file commit dates.

When the user asks for startup options, name only these six: `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. Every other skill is a later skill. That ask names the list. It does not run a skill and does not move work into a lane. Each starter still follows the rules it already has. `/crav1-existing-to-specs` still runs only when the user names repos. `/crav1-read-environment` still runs only when the user names the host. Naming production, prod, or live stops. `/crav1-fix-bug` still runs only when the user names a real bug.

Type `/crav1` to list kit skills. `/crav1-help` answers what to run next, in what order, and what a skill does, from the kit's own docs. Typical order, by route (generated from `docs/reference/workflow.yaml`):

<!-- crav1-order:start -->
- New slice: spark-to-spec or ideas-to-spec or bundle-to-specs → create-feature-branch (optional) → review-architecture (optional) → tighten-spec → resolve-open-questions → ado-sync (optional) → plan-from-spec → review-plan → tighten-plan → ado-sync (optional) → tasks-ready-to-build (optional) → build-tasks or build-features → verify-build-against-spec → fix-build-gaps (optional) → finalize-commit → open-pr → review-pr → merge-pr.
- New information on an existing slice: add-to-spec → tighten-spec → resolve-open-questions → plan-from-spec → ado-sync (optional) → tasks-ready-to-build (optional) → build-tasks → verify-build-against-spec → finalize-commit.
- Bug: fix-bug → tighten-spec or plan-from-spec or build-tasks → verify-build-against-spec → fix-build-gaps (optional) → finalize-commit → open-pr.
- Outside pull request: review-pr → merge-pr → refresh-system-notes → finalize-commit.
- Azure Boards sync: ado-sync → finalize-commit.
- The build skills (build-tasks, build-features) verify each task inside their worker, then go to open-pr. `/crav1-tasks-ready-to-build` can run any time to list ready and blocked tasks. Full routes: `docs/reference/workflow.md` (kit repo, or `crav1-docs/` next to the skills).
<!-- crav1-order:end -->

Standing rules for every kit skill:

- The running skill's own `SKILL.md`, and the reference files it names, hold its rules. Follow them. This file does not repeat them.
- A skill writes only what its rules say it writes. It commits, pushes, opens a pull request, or merges only where its own rules say so.
- Before you suggest more than one next step, or when the user questions an order, call `/crav1-help` and quote its answer with its source. Never give an order from memory.
- Naming a next command is not running it. A skill runs another skill only where its own rules say so.
- A cross-cutting skill may run from any lane. It does not move work into a lane and does not start Specify, Plan, or Build. A later skill is not a starter option.
- Production data is never read. Where a skill reads a cloud environment, pre-prod, shared-with-prod, and prod-only resources are shape and connections only, after one yes.
- Shared conventions live in `crav1-add-to-spec` `references/`: `sources.md` for imported sources under `docs/sources/`, the personal-data and secrets check, and the transfer data policy; `open-questions.md` for the `Pending:`, `Asked:`, and `Answered:` lines; and `research-stale.md` for stale marks on `docs/research/`. A quoted note in `docs/notes/` gets `Used by <slug>`. `Absorbed by <slug>` only after the user says yes.

Do not scaffold an application unless the user asked for one. Prefer editing the spec or plan when implementation drifts.

What each command reads, writes, and leaves alone: the skills reference, https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/reference/skills.md. Folders and marks: https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/concepts/data-layout.md. Full install paths: `docs/install.md` in the kit repo. After a plugin install, start with the plugin README.

On Claude Code this file is the project instruction (`.claude/CLAUDE.md`). A user-scope install uses the same text in `~/.claude/CLAUDE.md` and does not commit the kit into a client repo. Playbook paths that start with `.claude/` are the project drop-in. If that file is not in the repo, read the same path under `~/.claude/`.
