# Standing rules, in full

The always-loaded rule, `crav1.mdc`, keeps only the rules every session needs, in short form (1.157.0). This page holds each of those rules in full, with its examples and edge cases, word for word as the rule said them before 1.157.0. A skill's own `SKILL.md` and references still hold that skill's rules.

## Specs and the landscape

Specs, not chat history, are the source of truth. Put change work under `docs/specs/<change-id>/`; the layout always includes `docs/system/`. The landscape, glossary, picture and `Synced at` rules live in the skills that write them (`/crav1-add-to-spec` `references/` and each starter's `SKILL.md`).

## Startup options

When the user asks for startup options, name only these six: `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. Every other skill is a later skill. That ask names the list. It does not run a skill and does not move work into a lane. Each starter still follows the rules it already has. `/crav1-existing-to-specs` still runs only when the user names repos. `/crav1-read-environment` still runs only when the user names the host. Naming production, prod, or live stops. `/crav1-fix-bug` still runs only when the user names a real bug.

## Help and the order

Before you suggest more than one next step, or when the user questions an order, call `/crav1-help` and quote its answer with its source. Never give an order from memory. While `/crav1-what-do-we-know-about-this` is the running skill, do not start `/crav1-help`; answer from the steps already in its report, or say the kit doesn't say (1.117.0).

## How a run ends

A run ends with one `Next:` line, as `crav1-docs/reference/run-ending.md` says (1.122.0). Since 1.157.0 the ready checks and `/crav1-build-walk` end with the `Run next:` block first and no `Next:` line; every other skill keeps one `Next:` line.

## Asking

**Asking (1.70.0, 1.93.0).** Never ask what the conversation, the files, or an earlier answer already settles; use it and say so in one line. Where a default is obvious, pick it and state it (`Using develop as the base (Merges into).`). A choice word in the invocation answers its question; a headless run uses the stated defaults and stops only where its skill says so. Gather the questions that remain into one batch, not one per turn. A prompt is one turn that waits for the user; it may hold several questions. Confirm all writes once at the end with a single yes, listing what will be written. A question has at most 4 options; a fifth goes under Other. A typed change uses that card's free-text answer, and the hint lives on that option (1.130.0). The rule is `crav1-docs/reference/question-cards.md` (kit repo: `docs/reference/question-cards.md`). Use the questions tool when it is available. When a question with options has a recommendation, list that option first and end its label with ` (Recommended)`, for example `Note (Recommended)`; the question text does not also say `Recommendation: X`. This holds for every opening question, binary choice, review choice, and keep/leave/dismiss/note question. A question with no recommendation keeps its order and has no label. A skill's prompt budget, the most prompts in one run with the closing yes included, is its `prompt_budget` in `crav1-docs/reference/skills.yaml` next to the skills (kit repo: `docs/reference/skills.yaml`). A prompt for a value the user left out is outside the budget; every other prompt, including one at a stop, counts (1.95.0).

Choice words are plain words, never `--flags` (1.157.0, from the maintainer rule for merged skills).

## Git

Never rebase. A branch that is behind is caught up by merging its base in (`git pull --no-rebase`, or `git merge <base>` after a yes), as `/crav1-finalize-commit` and `/crav1-build-walk` already say (1.157.0).

**Base branches (1.99.0).** Implementation code is never written or committed on a base branch (main, master, develop, the `Merges into` branch, `release/*`); offer a work branch first, never Stay there. Specs and docs, and the specs repo, are exempt. Rules: `crav1-create-feature-branch` `references/code-branch.md`.

## Editing files

**Editing files (1.99.1).** Kit files (specs, notes, records) are changed with the host's file edit tool, so the user sees a diff. Run only the scripts a skill names; never an inline `python -`, `node -e` or heredoc script that edits files.

## Kit scripts

**Kit scripts (1.144.0).** On Windows the interpreter is `python`. Elsewhere it is `python3`. If that command is missing, or Windows prints `Python was not found`, try `py -3`, then the other name. Set `PYTHONUTF8=1` and pass `-X utf8`. A command includes every argument the script requires. Do not run `python3` alone. The rule is `crav1-docs/reference/running-scripts.md` (kit repo: `docs/reference/running-scripts.md`).

## Naming local files

**Naming local files (1.99.1).** Name a local file as a code span, with the repo first when the run touched more than one repo (`` `orders-api: docs/notes/2026-10/2026-10-08-pr-orders-api-71.md` ``). Never as a Markdown link, `file://`, `vscode://` or an absolute path. Web links only for things on the host (a pull request, a thread, a commit).

## Shared conventions

Shared conventions live in `crav1-add-to-spec` `references/`: `sources.md` for imported sources under `docs/sources/`, the personal-data and secrets check, and the transfer data policy; `open-questions.md` for the `Pending:`, `Asked:`, and `Answered:` lines; and `research-stale.md` for stale marks on `docs/research/`. A quoted note in `docs/notes/` gets `Used by <slug>`. `Absorbed by <slug>` only after the user says yes.

## Where the detail lives

What each command reads, writes, and leaves alone: the skills reference, https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/reference/skills.md. Folders and marks: https://github.com/Crav1on/crav1-spec-kit/blob/main/docs/concepts/data-layout.md. Full install paths: `docs/install.md` in the kit repo. After a plugin install, start with the plugin README.
