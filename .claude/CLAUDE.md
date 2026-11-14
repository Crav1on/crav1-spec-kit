# crav1 kit

Specs, not chat history, are the source of truth. Put change work under `docs/specs/<change-id>/`; the layout always includes `docs/system/`.

When the user asks for startup options, name only these six: `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. Every other skill is a later skill. Naming the list runs nothing.

Type `/crav1` to list kit skills. Typical order, by route (generated from `docs/reference/workflow.yaml`):

<!-- crav1-order:start -->
- New slice: spark-to-spec or ideas-to-spec or bundle-to-specs → create-feature-branch (optional) → review-architecture (optional) → tighten-spec → resolve-open-questions → ado-sync (optional) → plan-from-spec → review-plan → tighten-plan → ado-sync (optional) → tasks-ready-to-build (optional) → build-walk (optional) → build-tasks or build-features → verify-build-against-spec → fix-build-gaps (optional) → finalize-commit → open-pr → review-pr → merge-pr.
- New information on an existing slice: add-to-spec → tighten-spec → resolve-open-questions → plan-from-spec → ado-sync (optional) → tasks-ready-to-build (optional) → build-tasks → verify-build-against-spec → finalize-commit.
- Bug: fix-bug → tighten-spec or plan-from-spec or build-tasks → verify-build-against-spec → fix-build-gaps (optional) → finalize-commit → open-pr.
- Before a pull request: review-pr → tighten-spec or plan-from-spec or build-tasks (optional) → finalize-commit → open-pr → pr-status (optional).
- Outside pull request: review-pr → pr-status (optional) → merge-pr → refresh-system-notes → finalize-commit.
- Azure Boards sync: ado-sync → finalize-commit.
- Repos vs specs: existing-to-specs → add-to-spec (optional) → tighten-spec (optional) → finalize-commit.
- The build skills verify each task inside their worker, then go to open-pr. `/crav1-build-walk` walks one task or a whole work branch through that path. `/crav1-tasks-ready-to-build` runs only when typed; for a plain question about which tasks are ready, name the command. Full routes: `crav1-docs/reference/workflow.md`.
<!-- crav1-order:end -->

Standing rules for every kit skill. The full text, with examples, is `crav1-docs/reference/standing-rules.md` (kit repo: `docs/reference/standing-rules.md`).

- The running skill's own `SKILL.md`, and the reference files it names, hold its rules. Follow them.
- A skill writes only what its rules say it writes. It commits, pushes, opens a pull request, or merges only where its own rules say so. Naming a next command is not running it.
- Before you suggest more than one next step, or when the user questions an order, call `/crav1-help` and quote its answer with its source. Never give an order from memory.
- A run ends with one `Next:` line, or, for the ready checks and the build walk, with the `Run next:` block first and no `Next:` line, as `crav1-docs/reference/run-ending.md` says (1.122.0, 1.157.0).
- A cross-cutting skill may run from any lane. It does not move work into a lane and does not start Specify, Plan, or Build.
- **Asking.** Never ask what the conversation, the files, or an earlier answer already settles. Pick an obvious default and state it. A choice word answers its question; choice words are plain words, never `--flags`. Batch the questions that remain, and confirm all writes once at the end with a single yes. Cards follow `crav1-docs/reference/question-cards.md`: at most 4 options, the recommended one first with ` (Recommended)`.
- **Git.** Never rebase. A branch that is behind is caught up by merging its base in. Implementation code is never written or committed on a base branch (main, master, develop, the `Merges into` branch, `release/*`); offer a work branch first (`crav1-create-feature-branch` `references/code-branch.md`). Specs and docs are exempt.
- **Files and scripts.** Edit kit files with the host's file edit tool; never an inline script that edits files. Run only the scripts a skill names, with the interpreter `crav1-docs/reference/running-scripts.md` picks and every required argument. Name a local file as a code span, never a link or an absolute path.
- Production data is never read. Where a skill reads a cloud environment, pre-prod, shared-with-prod, and prod-only resources are shape and connections only, after one yes.

Do not scaffold an application unless the user asked for one. Prefer editing the spec or plan when implementation drifts.

What each command reads and writes: `crav1-docs/reference/skills.md`.

On Claude Code this file is the project instruction (`.claude/CLAUDE.md`). A user-scope install uses the same text in `~/.claude/CLAUDE.md` and does not commit the kit into a client repo. Playbook paths that start with `.claude/` are the project drop-in. If that file is not in the repo, read the same path under `~/.claude/`.
