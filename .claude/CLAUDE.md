# crav1 kit

Specs, not chat history, are the source of truth. Put change work under `docs/specs/<change-id>/`; the layout always includes `docs/system/`. The landscape, glossary, picture and `Synced at` rules live in the skills that write them (`/crav1-add-to-spec` `references/` and each starter's `SKILL.md`).

When the user asks for startup options, name only these six: `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. Every other skill is a later skill. That ask names the list. It does not run a skill and does not move work into a lane. Each starter still follows the rules it already has. `/crav1-existing-to-specs` still runs only when the user names repos. `/crav1-read-environment` still runs only when the user names the host. Naming production, prod, or live stops. `/crav1-fix-bug` still runs only when the user names a real bug.

Type `/crav1` to list kit skills. `/crav1-help` answers what to run next, in what order, and what a skill does, from the kit's own docs. Typical order, by route (generated from `docs/reference/workflow.yaml`):

<!-- crav1-order:start -->
- New slice: spark-to-spec or ideas-to-spec or bundle-to-specs → create-feature-branch (optional) → review-architecture (optional) → tighten-spec → resolve-open-questions → ado-sync (optional) → plan-from-spec → review-plan → tighten-plan → ado-sync (optional) → tasks-ready-to-build (optional) → build-tasks or build-features → verify-build-against-spec → fix-build-gaps (optional) → finalize-commit → open-pr → review-pr → merge-pr.
- New information on an existing slice: add-to-spec → tighten-spec → resolve-open-questions → plan-from-spec → ado-sync (optional) → tasks-ready-to-build (optional) → build-tasks → verify-build-against-spec → finalize-commit.
- Bug: fix-bug → tighten-spec or plan-from-spec or build-tasks → verify-build-against-spec → fix-build-gaps (optional) → finalize-commit → open-pr.
- Before a pull request: review-pr → tighten-spec or plan-from-spec or build-tasks (optional) → finalize-commit → open-pr → pr-status (optional).
- Outside pull request: review-pr → pr-status (optional) → merge-pr → refresh-system-notes → finalize-commit.
- Azure Boards sync: ado-sync → finalize-commit.
- Repos vs specs: existing-to-specs → add-to-spec (optional) → tighten-spec (optional) → finalize-commit.
- The build skills (build-tasks, build-features) verify each task inside their worker, then go to open-pr. `/crav1-tasks-ready-to-build` is command-only: it runs when typed, any time, to list ready and blocked tasks. For a plain question about which tasks are ready, name the command. Full routes: `docs/reference/workflow.md` (kit repo, or `crav1-docs/` next to the skills).
<!-- crav1-order:end -->

Standing rules for every kit skill:

- The running skill's own `SKILL.md`, and the reference files it names, hold its rules. Follow them. This file does not repeat them.
- A skill writes only what its rules say it writes. It commits, pushes, opens a pull request, or merges only where its own rules say so.
- Before you suggest more than one next step, or when the user questions an order, call `/crav1-help` and quote its answer with its source. Never give an order from memory.
- Naming a next command is not running it. A skill runs another skill only where its own rules say so.
- A cross-cutting skill may run from any lane. It does not move work into a lane and does not start Specify, Plan, or Build. A later skill is not a starter option.
- **Asking (1.70.0, 1.93.0).** Never ask what the conversation, the files, or an earlier answer already settles; use it and say so in one line. Where a default is obvious, pick it and state it (`Using develop as the base (Merges into).`). A choice word in the invocation answers its question; a headless run uses the stated defaults and stops only where its skill says so. Gather the questions that remain into one batch, not one per turn. A prompt is one turn that waits for the user; it may hold several questions. Confirm all writes once at the end with a single yes, listing what will be written. A question has at most 4 options; a fifth goes under Other. Use the questions tool when it is available. When a question with options has a recommendation, list that option first and end its label with ` (Recommended)`, for example `Note (Recommended)`; the question text does not also say `Recommendation: X`. This holds for every opening question, binary choice, review choice, and keep/leave/dismiss/note question. A question with no recommendation keeps its order and has no label. A skill's prompt budget, the most prompts in one run with the closing yes included, is its `prompt_budget` in `crav1-docs/reference/skills.yaml` next to the skills (kit repo: `docs/reference/skills.yaml`). A prompt for a value the user left out is outside the budget; every other prompt, including one at a stop, counts (1.95.0).
- **Base branches (1.99.0).** Implementation code is never written or committed on a base branch (main, master, develop, the `Merges into` branch, `release/*`); offer a work branch first, never Stay there. Specs and docs, and the specs repo, are exempt. Rules: `crav1-create-feature-branch` `references/code-branch.md`.
- **Editing files (1.99.1).** Kit files (specs, notes, records) are changed with the host's file edit tool, so the user sees a diff. Run only the scripts a skill names; never an inline `python -`, `node -e` or heredoc script that edits files.
- **Naming local files (1.99.1).** Name a local file as a code span, with the repo first when the run touched more than one repo (`` `orders-api: docs/notes/2026-10/2026-10-08-pr-orders-api-71.md` ``). Never as a Markdown link, `file://`, `vscode://` or an absolute path. Web links only for things on the host (a pull request, a thread, a commit).
- Production data is never read. Where a skill reads a cloud environment, pre-prod, shared-with-prod, and prod-only resources are shape and connections only, after one yes.
- Shared conventions live in `crav1-add-to-spec` `references/`: `sources.md` for imported sources under `docs/sources/`, the personal-data and secrets check, and the transfer data policy; `open-questions.md` for the `Pending:`, `Asked:`, and `Answered:` lines; and `research-stale.md` for stale marks on `docs/research/`. A quoted note in `docs/notes/` gets `Used by <slug>`. `Absorbed by <slug>` only after the user says yes.

Do not scaffold an application unless the user asked for one. Prefer editing the spec or plan when implementation drifts.

What each command reads, writes, and leaves alone: the skills reference, https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/reference/skills.md. Folders and marks: https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/concepts/data-layout.md. Full install paths: `docs/install.md` in the kit repo. After a plugin install, start with the plugin README.

On Claude Code this file is the project instruction (`.claude/CLAUDE.md`). A user-scope install uses the same text in `~/.claude/CLAUDE.md` and does not commit the kit into a client repo. Playbook paths that start with `.claude/` are the project drop-in. If that file is not in the repo, read the same path under `~/.claude/`.
