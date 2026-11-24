# Changelog

Notable changes to **CRAV1 Spec Kit** (`crav1`). Version matches `plugins/crav1/.cursor-plugin/plugin.json`.

## 1.203.0 (2026-11-24)

The installed docs bundle is a compact edition for the kit's skills. The human pages stay in `docs/`.

- **Compact `crav1-docs`.** `scripts/gen-compact-docs.py` writes the bundle from the same sources as the human pages: `skills.yaml` for each skill page, the skills list, and guild routing; `marks.yaml` for the mark lines; the human Markdown for walkthroughs and concepts. Version-led history stamps (`1.123.0:`) are dropped. Commands, choices, writes, thresholds, and card steps stay. Each compact page ends with a `human:` link to the matching page at the installed tag.
- **Unchanged rule files.** These nine are copied byte for byte: `running-scripts.md`, `run-ending.md`, `question-cards.md`, `open-skill-file.md`, `pr-common.md`, `workflow.md`, `standing-rules.md`, `workflow.yaml`, and `index.yaml`.
- **Left out of the bundle.** `skills.yaml` and `marks.yaml` (generator sources), and `proposals/`, `specs/`, `system/`, and `notes/` (no skill reads them from the bundle). Paths a skill cites stay.
- **`llms.txt`.** A repo-root index of the human `docs/` pages for tools outside the kit, generated with the bundle. It is not inside `crav1-docs`.
- **Plan shift.** The Codex install step in `docs/proposals/multi-vendor.md` moves from 1.203.0 to 1.204.0. Copilot moves to 1.205.0 and the bootstrap install to 1.206.0.

Docs and tests: install, help walkthrough, glossary, data layout, and `scripts/tests/test_compact_docs_1203.py`.

## 1.202.0 (2026-11-24)

Generated Codex and Copilot trees, plus three ready-check and plan-count fixes. Nothing here is installed.

- **Vendor trees.** `scripts/sync-crav1-vendors.py` writes `vendors/codex/` (`.agents/skills/`) and `vendors/copilot/` (`.github/skills/` plus `.github/instructions/crav1.instructions.md`). Each generated skill opens with the kit-rules line. Codex commands are `$crav1-` and its Run next script calls pass `--vendor codex`. Copilot keeps `/crav1-` and passes `--vendor copilot`. Command-only Codex skills get `agents/openai.yaml`. The project's `AGENTS.md` is not written. CI fails when a committed tree drifts, and kit-lint checks the per-vendor rules. Update still installs only Cursor and Claude Code.
- **Held list.** A task whose only wait is an `(after:)` on a task that is not built yet is listed under Held, with the reason on that line. An own pull-request wait is on the held line too. The same sentence is not printed again underneath.
- **Open count.** `plan_check.py open-count --review <file>` prints `open: <n>` from the reviewer's `P#` lines. The walk uses that value. `reviewed --items` recomputes the Reviewed line from the items file.

Docs and tests: tighten-and-plan and spec-to-plan walkthroughs, glossary, data layout, and `scripts/tests/test_kit_1202.py`.

## 1.201.1 (2026-11-24)

Fixes for the design screen and the ready check. The rules were already the ones below; the scripts now follow them.

- **Design screen.** Run next comes first, with one reason line. A topic that exists only on `design/<topic>` offers the switch card. `resume --json` leaves the files unchanged, including a parked Status. Dated proposal pages under `docs/architecture/proposals/` count. Waiting lines name each person once, with the date recorded on the question, and stay near 120 characters. When every open decision is waiting on named people, Run next names the open-questions command and the proposal. A parked screen has no Park command. An ended screen's one command is `reopen`. Run `scripts/design_run.py` from the repo root.
- **Script output.** Do not pipe a script's output, in bash or in PowerShell. A pipe such as `| head` can cut an ending off at a lone `{`.
- **Task names.** A `from <base>` clause and parenthesised marks such as `(manual, secret, …)` are not the task name. The name is the outcome after that clause.
- **Claims.** `claims.py add` leaves `claims.md` unchanged until `--yes`. A second start on the same claim keeps the original since time.
- **Ready check.** A `--text` read that does not pass `--write-map` does not add a `PR author` line. A merged pull request is still recorded, as in 1.177.2. A free-text mention such as `(PR 12)` or `(PR 7 merged into develop)` does not mark a task done; only a tick or the kit mark `(PR n, merged)` or `(PR n) merged` does. A task with `(after: T#)` stays held while T#'s pull request is open, and the held line says `waits for PR <n> to merge`. A task that says `(after: PR 87)`, or whose text says `after PR 87 merges`, stays held the same way until the host says PR 87 is merged. The ready check, the build map and the walk ending all say `waits for PR 87 to merge`. When the code repo is not recorded, the check uses the same one-time repo question as 1.177.2. `/crav1-plan-from-spec` and `/crav1-tighten-plan` write `(after: PR N)` for that prose: `plan_check.py order` names the line, and `plan_check.py after-pr --yes` writes the mark. A pull request the host says is merged is cleared with `/crav1-build-walk <slug> T#`. A blocked line names only the tasks that wait on that block. Claude Code sends one question per question-tool call.

Docs and tests: design, build-walk and ready-check walkthroughs, data layout, question cards, install, running scripts, and `scripts/tests/test_kit_12011.py`.

## 1.201.0 (2026-11-22)

A vendor table, with no change to a Cursor and Claude Code update.

- **Vendor table.** `vendors.json` in the update-kit skill lists, for each host, the folders the kit owns, the frontmatter a skill needs, the command prefix, and extra files. The Cursor and Claude Code rows reproduce the 1.200 allow-list. Codex and Copilot are listed and are not installed or generated.
- **Same plan.** `collect_kit` and the kit-path checks read that table. A plan and an apply on an existing Cursor and Claude Code repo match 1.200 byte for byte.
- **Report.** `update_kit.py detect` adds `vendors`. `update_kit.py vendors --root .` lists each vendor's folder and skill count and writes nothing.
- **Prefix.** A script that prints Run next takes `--vendor`. The default stays `/`. `--vendor codex` prints `$crav1-`.
- **Dry run.** The maintainer dry run takes `--add <vendor>` (repeatable). It plans and applies that vendor inside the temp worktree after the normal update, then lists each vendor's folder and skill count. The update plan step prints counts by kind and at most 10 sample paths.

Docs and tests: update-kit walkthrough, glossary, data layout, run-ending, and `scripts/tests/test_kit_1201.py`.

## 1.200.0 (2026-11-22)

One design-session start, shared ending checks, and a shorter dry run.

- **Design session.** `/crav1-design-architecture` with or without a topic, and with or without `resume`, opens the same status screen from the topic files. `resume` changes nothing. Park and end print `Session parked` or `Session ended` and `/crav1-design-architecture <topic>`. The session stays open across decisions, endings and commits. `next` is the guided card. A proposal and a briefing share one decisions section. Stage numbers start at 1. A routed requirement names the slice and the text, and that ending starts with Run next and a full `/crav1-add-to-spec` command. `settle-preview` recommends one by one and settles nothing. `stop and commit` commits only because this skill says that phrase is a yes.
- **Endings.** A shared check refuses a `Next:` line, a Waiting line that carries a command, and an Uncommitted line that names the commit command outside a code span. `/crav1-add-to-spec` and `/crav1-finalize-commit` print their endings from that helper. A design branch that is checked out or owns the change gets a stay card, and the card never offers the default branch. Question waits name the question and who it waits on when that text is known. A held line that waits on a pull request names the PR number. When local files have no number, a read-only host lookup may supply the one open pull request for that branch. The leftover `Next:` examples are gone, so the baseline is empty. Card wording is checked on every skill.
- **GitHub replies.** `gh_threads.py reply` previews a reply in a review thread and, after a yes, posts it and can resolve the thread. open-pr offers the same one-thread card.
- **Dry run.** The maintainer dry run summarises update detect and plan to a count and the changed files, and hides the spurious no-upstream line.

Docs and tests: design walkthrough, glossary, data layout, and `scripts/tests/test_kit_1200.py`.

## 1.199.0 (2026-11-20)

Thread replies from the kit, one re-check shape, an answered status, lighter PR runs, commit and push in one yes, and three build fixes.

- **Organization on checks.** `pr_common.py checks` passes the Azure DevOps organization to both `az` calls, from the PR URL or remote, else `docs/system/repos.md`.
- **Thread replies.** New `ado_threads.py reply` posts inside an existing thread, can set its status, and marks the drafted reply posted in the PR note. pr-status asks one card, `Post your reply in thread 195 and set it to fixed?`, and the draft's words match what the card does. Drafted replies carry their thread link.
- **One re-check shape.** Waiting on someone ends with a label and `/crav1-pr-status <pr> since-last` alone in its code span; Waiting lines carry no command. The card comes before the ending, which is printed once. The signed-in user is `you`.
- **Answered status.** A question that was answered and accepted is `answered` in the PR record, said as `answered; no code change`, never `done host`. New `ado_threads.py set-point` writes a Point by its thread.
- **Lighter runs.** pr-status runs merged-since-sync once, the ready check only when the PR closes a task, and reads threads with `ado_threads.py list --brief`. open-pr stops after one host read on someone else's up-to-date PR.
- **Commit and push.** `/crav1-finalize-commit commit-push` commits and pushes on one yes. `Uncommitted:` lines name the command in a code span.
- **Build fixes.** Branches that share a plan step no longer repeat its description. New `pipeline_trigger.py check` in merge-pr: a merge card names a deploy side effect only when a pipeline trigger covers the base. `code-drift` reports base commits from branches the spec does not list that touch the slice's files.

- **Ready-check waits.** Your own task that is pushed and waits for its pull request is `waiting`, never an unrecognized blocker: the result stays ready-partial, the other tasks go to Run next, and only waits changed means a quiet record. A real `Not ready: T12 is blocked (…)` line comes right after Run next, before Held, and a merge wait names its PR, `Waiting: PR 85 to merge, then …`.
- **PR number on someone else's branch.** A task verified on another person's branch names the branch's PR in the Waiting and held lines, from the Match `Branch:` line `(PR n)`, a task's `(PR n)` note, or any author's build-progress log; with none the wording stays.

Docs and tests: pr-status, commit, build walk and tighten-and-plan walkthroughs, readiness, run-ending, pr-record and data layout; `scripts/tests/test_kit_1199.py`. Maintainers get a dry-run tester for a kit pull request on a real project (CONTRIBUTING.md); it is not part of the kit, update never installs it, kit-lint keeps it out of skills and user docs, and it reports whether your repo is unchanged.

## 1.198.0 (2026-11-20)

Build-walk endings that follow the real step, checked facts, release gates in the build walk, a kit update line, fewer cards, container-aware dependency checks and ready-check ending fixes.

- **Step labels.** Build-walk Run next labels follow the step: `Merge PR 71 for T5:`, `Check PR 71's merge for T5:`, `Tick T5, now that PR 71 is merged:`. Task names are the first sentence, at most 120 characters.
- **Checked facts.** `next --code-repo` (or the progress header's `Code repo:`) counts commits behind the base before saying so; not behind skips to the merge. A `nothing-to-do` step moves on. The lead says only what was checked.
- **Record in one call.** `progress record --step build,verify,commit` and `--pr 71`. `next --task` falls back to the branch named in the task line or the map.
- **Release gate in the build walk.** Release-gated tasks are left out of the build-walk ending, and a manual task with no branch is listed alone, never under a generated branch name.
- **Kit update line.** `update_kit.py available` and both walks' starts say `Kit update available: <installed> -> <latest>` with `/crav1-update-kit`; read-only, short timeout, silent offline.
- **Fewer cards.** One yes pushes and opens the pull request; Open PR only appears only when the head is pushed. `Not yet` on the merge card also commits and pushes the walk's specs files.
- **Dependency containers.** New `dep_check.py containers` finds docker or podman containers, stopped ones and a stopped podman machine, and recommends starting them; install only when nothing exists. A worker runs only the tests that do not need a down dependency, then reports the blocker.
- **Ready-check ending.** Not-ready with tasks that can start names the hard hit and those tasks. Your own pushed task waits for its PR's merge. `Resume the walk` appears only for held questions and names who answers. A repeated question is shown once and cut near 120 characters. A result that only reflects waits is recorded without a card. A lone build-map change is `Commit the updated build map:`.
- **Small fixes.** No `Next:` lines in walk prose. pr-status finds the Azure DevOps organization in `repos.md`. merge-pr fetches before the PR-note check. Every Windows `--query` value is quoted. Build-walk cards show plain labels.

Docs and tests: build walk, tighten and plan, verify, update kit and pr-status walkthroughs; `scripts/tests/test_kit_1198.py`.

## 1.197.0 (2026-11-20)

Fixes from a live spec walk: cleaner batch cards, a prod lint that judges each check, release gates, quieter acceptance checks and a scoped plan review.

- **Whole labels only.** The batch label map replaces an option only when the whole option, or the part before its `:`, is an internal id. Words such as keep or ask inside option text stay as written.
- **Prod lint per item.** `plan_check.py lint` reads each verify item and its target: file names such as `main.prod.bicepparam`, PROD-like settings, unit and contract items, local compiles and read-only checks are not flagged. A `(manual, prod` task whose own text drops, deletes or changes data needs `owner:` and a Risks line.
- **Release gate.** A task marked `(after-release: main)`, or a manual prod task that a Risks line ties to a release, is Waiting in the ready check and is never offered as the first task. New mark in the data layout.
- **Quiet tickable.** `walk_progress.py tickable` asks only about a failing row or a passing row with no evidence. Untested and pending rows stay open with no question; one `waiting_line` counts them.
- **Small fixes.** `start` uses the playbook it found by name (no second run). The claims "Kept claimed tasks" line is gone when nothing changed. `start_check.py` reads the PR number from Azure DevOps `Merge pull request 82 from` subjects. Housekeeping says `Applying with no card` and `plan_check.py reviewed --items` leaves housekeeping out of the open count.
- **Card rules.** A batch question is only the short `Card:` line; the items live in the bullets and the `On yes:` line. Before a yes the walk says what it would change, never that it already did.
- **Fewer cards.** Plan-from-spec applies housekeeping refreshes with one summary line, and the ready check is recorded with no save card.
- **Scoped plan review.** New `walk_progress.py review-packet` writes the reviewer's input outside the repo: the changed tasks, their spec sections by line range, and the plan's Risks and Linter, with a quick mode for small changes. The reviewer runs in the foreground and never reads `spec.md` whole.
- **Local fast-forward card.** The build walk's card for a code base branch behind origin now reads `Your local develop in orders-api is 2 commits behind origin/develop. Update it locally before the build?`, with **Update local develop** and a result line that says nothing is pushed, then the work branch and task it builds. New `code-behind --branch --task`.
- **Bare PR numbers from a specs-only checkout.** When no record names the number and this checkout holds no code, `pr_common.py resolve` checks the code repos in `repos.md` read-only and uses the single match, otherwise asks with those repos listed. It never suggests installing a CLI before the host is known. `/crav1-review-pr` ends with a Run next block when the host is still unknown.

Docs and tests: the spec walk walkthrough, question cards, pr-common and marks; `scripts/tests/test_kit_1197.py`.

## 1.196.0 (2026-11-20)

Start checks that trust origin, claims that clear themselves, and fewer, plainer walk cards.

- **Shared start check.** New `crav1-add-to-spec` `scripts/start_check.py`: one quiet `git fetch --prune origin` per checkout, `origin/<branch>` before a stale local branch, and a tip that is already merged is found with its merge commit and PR. `merged_since_sync.py check` and `walk_progress.py code-drift` use it; `--no-fetch` skips the fetch.
- **Claims prune.** New `claims.py prune` clears claims whose tasks are all ticked or whose branch is merged into `origin/<base>`, with one summary line. It runs at the walk start and after `/crav1-merge-pr`. Unfinished claims are never cleared, finished claims get no age warning, and the "kept unchanged" lines are gone.
- **Prod verify rule.** Verify runs on DEV or TEST; prod checks are read-only (health, version, config, existence). A prod-write check is its own task with an owner, the user's yes and a Risks line. New `plan_check.py lint` flags both; tighten-plan recommends DEV or TEST.
- **Fewer cards.** `readiness --covered <step>` drops the reopen card when the reopen came only from a fact the walk just recorded and a finding covers it. Tighten-plan housekeeping applies with one summary line. The save rides on the step's last yes.
- **Plain walk cards.** Batch cards show one background bullet per item, a short question and an `On yes:` line. Labels are plain words with no letters or internal names (label maps in `plan_check`, `batch_offer` and `walk_progress`). `suggest` is offered only for wording findings.
- **Tickable at the start.** New `walk_progress.py tickable` ticks acceptance items whose verify row passes with evidence, in one line; when an open task touches the evidence it ticks now and adds a recheck line to that task's verify note.
- **Endings.** The run ending prints the script's block exactly, Catch up first included; tighten-spec's last `Next:` lines became Run next blocks.
- **Walk fixes.** A locked skill inside the walk prints no Run next or `Uncommitted:` line; `spec-finding` asks a `kind-conflict` card when code-drift text is passed as spec text; after a jump-back the walk follows its `continue` list; the plan reviewer runs in the foreground; the uncommitted count includes changed notes and sources.

Docs and tests: walkthroughs for the build walk and the spec walk; `scripts/tests/test_kit_1196.py`.

## 1.195.0 (2026-11-20)

Fixes from two live sessions: meeting imports, the spec walk's code checks, and the tighten cards.

- **Meeting Run next names every changed spec.** The first changed spec gets the command; the rest follow as `Also changed, not tightened: <slugs>.` When an edit reopens a spec's open walk, the command is `/crav1-tighten-and-plan-ready-to-build <slug>` with the reason `The new information reopened the walk.` The fact branch's ending (`references/stop.md`) routes the same way.
- **Save for later.** Meeting items get a fourth choice, save for later, which writes the slug (or `general` for team-workflow information) to a new note field `later_for`. `waiting_for` stays for parked specs only. `/crav1-help`, `/crav1-tighten-spec`, `/crav1-show-or-ask-open-questions` and `/crav1-retire-spec` list these notes as saved for later; `notes_index.py later --slug <slug>` lists them. New mark `later_for` in `marks.yaml`.
- **One batch rule for meetings.** One to four items get one question each; more than four always get the batch card. The recap's `Noted` count is gone (every input is noted) and `Saved for later` counts the new choice.
- **Reason lines in `/crav1-finalize-commit` endings.** Every Run next example in `references/commit.md` starts with its reason, for example `The commit is only local.`
- **`.docx` meeting imports.** New `crav1-add-to-spec` `scripts/docx_to_md.py`: `convert` keeps paragraphs, headings, list levels and bold and reads the created date from `docProps/core.xml`; `check` compares the words in order. Standard library only, no network. Named in `references/sources-binary.md` and the meeting branch.
- **The base, per branch.** `merged_since_sync.py check` finds each branch's base from `--base`, then the repo's `Merges into` in `docs/system/repos.md` (`--repos`), then a base `Synced at` line, then `origin/develop`, then the default branch, and reports `base` and `base_from`. Every caller passes `--base <Merges into>`.
- **Code drift at the walk start.** `/crav1-tighten-and-plan-ready-to-build` runs `walk_progress.py code-drift` right after merged-since-sync at the start; the run before the plan review is a recheck. New `readiness --stale-seen`: when anything stale was seen, every reopen card recommends rerun, never nothing new.
- **Only unrecorded commits count.** `code-drift` leaves out commits already named in the spec or in a note's `commits:` list, and base merge-ins, and reports `count`, `total`, `already_recorded` and `base_merge_ins`. New `--base`.
- **Tighten-spec: whether findings and sources.** A finding that asks whether something is so, with no deciding source, recommends ask or keep. A patch that contradicts a source line quotes it and is never the recommendation; ask or keep is always listed, also on the batch card.
- **One owner for acceptance ticks.** `/crav1-tighten-spec` ticks a spec acceptance box only through the new `tick-from-verify` resolution, which quotes the passing verify row. `/crav1-verify-build-against-spec` only reports the open box.
- **Tighten-plan batch cap.** `plan_check.py batch` puts at most 8 findings on one card and names the rest for the next card. A finding with `changes_tasks` (adds, removes or reorders tasks) never goes on a yes-to-all card; it gets its own card.

Docs and tests: walkthroughs for meetings, commit and the spec walk; data layout, glossary and marks; `scripts/tests/test_kit_1195.py`.

## 1.194.0 (2026-11-19)

Fixes for spec findings in `/crav1-tighten-and-plan-ready-to-build`, from a live walk.

- **The right owner on the jump-back card.** `walk_progress.py spec-finding` no longer always recommends `/crav1-tighten-spec`. A finding about code the spec has not recorded (unrecorded commits, a merged pull request, `Synced at` or `In the code` drift, new PR comments) recommends `/crav1-add-to-spec` with that pull request or branch; wording, structure, diagrams and constraints stay with tighten-spec, the default when unclear. `--kind code-drift|spec-text` is the hint, `--pr` or `--branch` the target; the recommended label, its text and the opened path name the right command.
- **Already fixed, no card.** Before the card, spec-finding re-reads `spec.md` and its `Synced at:` lines. A finding the spec already covers (the branch's `Synced at` shows the merge commit or later, `--code-repo` for later; or `--expect` words present) returns `already-fixed` with a one-line note and no card. A typed "already done" (`--choice already-done`) closes the finding only when the spec shows it, and otherwise returns the card with what is still missing.
- **Add-to-spec before the plan review.** New `walk_progress.py code-drift` reads refs on disk (no fetch): when commits sit after a `Synced at` commit, or a merged pull request is not recorded, the walk asks one add-to-spec yes card before the plan review, and passes the drift to the reviewer as known context, not as a finding to echo.
- **Merged since sync, one shared check.** New `crav1-add-to-spec` `scripts/merged_since_sync.py check` compares each branch in a spec's `Synced at:` lines with the base (the default branch, found as `design_run.py` does, or `--base`). When a branch merged since the recorded commit it asks ONE yes card: `PR <n> merged at <sha> with <k> commits the spec hasn't recorded. Take them in now?`. Yes runs the add-to-spec PR or branch step inline and `stamp --yes` moves `Synced at` to the merge; nothing is written without the yes, and headless runs only report. Used at the tighten-and-plan walk start, by `/crav1-pr-status`, the specs sweep (auto flow reports only), `/crav1-merge-pr` after a merge and `/crav1-build-walk` when a branch's pull request merged.
- `scripts/tests/test_kit_1194.py` and the walkthrough `docs/from-tighten-and-plan.md`.

## 1.193.0 (2026-11-19)

Fixes from a review session on the sweep, commit, review-pr, pr-status and add-to-spec.

- **Run next, not Next.** `/crav1-add-to-spec` (stop, PR comments, code-change, dump and meeting endings) and the sweep's `sweep_progress.py ending` end with Run next: `Run next:` first, the reason, the label on its own line and the command alone in its code span. `pr<n> candidates` with none left ends with a Run next naming `/crav1-pr-status pr<n>`. kit-lint fails on any `Next:` line in skill files and any script string that prints one; the skills not moved yet are listed with their counts in `scripts/next-line-baseline.tsv`, which may only shrink.
- **One candidates rule.** `pr_common.py candidates --note <PR note>` decides spec and decision candidates for both `/crav1-pr-status` and `/crav1-add-to-spec pr<n> candidates`. A newer settled answer on a Point already `in spec <slug>` narrows the tag to `in spec <slug> (question)` (`pr_common.py answered`), so the Point is offered again; taking it writes `in spec <slug> <date>` (`pr_common.py in-spec`).
- **Nothing in the spec before the yes.** In the sweep's manual flow only the note, the PR note and the Read line are written before the write card. `Synced at` waits for the yes: `sweep_progress.py synced-at` writes nothing without `--yes`, and the notes-only option writes no stamp.
- **commit-now can ask the mention.** With several Feature lines in `work-item.md` and none clearly matching, `/crav1-finalize-commit commit-now` asks one card from `work_item_pick.py` (at most 4 options plus a typed Other) and never copies a mention from `git log` or the previous commit.
- **ado_threads.py is the one Azure DevOps way.** New `pr` (description, votes), `iterations`, `changes`, `set-status --yes` (read back from the host) and `since-last` (against the PR note's Read line and saved description, never a temp file); `list` gives thread and comment dates. Output is UTF-8 JSON with accented characters intact. The add-to-spec, pr-status and review-pr docs no longer teach `az rest` or hand-made token calls.
- `scripts/tests/test_kit_1193.py` (mocked Azure DevOps responses with non-ASCII text); the sweep ending tests use the Run next form. Claim ages read `CRAV1_NOW` when set; snapshot-check and the claim tests pin it, so they no longer fail once a fixture claim is 3 days old.

## 1.192.0 (2026-11-18)

A new cross-cutting skill, `/crav1-explain-tech`, explains one technology tied to where the specs use it.

- **Short answer, fixed shape.** `/crav1-explain-tech <technology> [in <spec, topic or architecture>]` answers in about 150 to 250 words: what it is, how it works, where it shows up (links to the exact files and sections), why it is used, the main tradeoff and one alternative, then Run next. `deeper` gives 300 to 900 words and adds how it fits with the rest of the spec.
- **Read from the specs.** `explain_tech.py find` lists every mention in specs, plans, tasks, notes, the architecture spec, ADRs, design topics and system notes (also `private-link`, `PrivateLink`), with links, owners (ADR deciders, `Owner:` lines, `## Approval needed`) and the spec to save to. A technology the specs never mention is said plainly, with no spec link, and Run next names research.
- **Save only on request.** `save` (the word, or yes on the card) appends a dated `### <technology>` entry with the short explanation and links under `## Technology notes` in the spec's `notes.md` (created when missing). Links that are not in the specs are refused; nothing is written without the yes.
- **Checked shape.** `check` tests the sections, their order, the word count and every link; kit-lint runs it on the skill's sample answers and checks its Run next layout.
- Registered in the skills reference, guild routing (a Cross-cutting skill row and a choice-words row: `deeper`, `save`), the walkthrough `docs/from-explain-tech.md`, the glossary, and `scripts/tests/test_kit_1192.py`.

## 1.191.0 (2026-11-18)

`/crav1-design-architecture` works in repos whose default branch is not main.

- **Default branch, not origin/main.** The design branch check, the kit-behind check and the go-ahead base check resolve the repo's default branch once per run: `origin/HEAD`, else `origin/main`, then `origin/master`. With none, the check is skipped with a reason (`skipped`) and never fails. The merge card, its Run next (`Merge master into the design branch:`), the kit warning and the go-ahead ending (`gh pr create --base <branch>`) name that branch; never a rebase.
- `scripts/tests/test_kit_1191.py` (master default, origin/HEAD unset fallback, no default branch); the `design-branch-behind` snapshot now shows `default_branch`.

## 1.190.0 (2026-11-18)

Fixes for `/crav1-design-architecture` and `/crav1-update-kit` from a live design session.

- **Decision order on each decision.** `design.md` stores decisions by title, so parallel adds do not conflict, and each decision carries `Order: N` for the index line and resume (ties by title). The goal's decision list is built from those numbers and no longer stored in `goal.md`. `create`, `add-decision` and `change-goal` write the numbers; older files get them on read from their list position (or the old goal list).
- **Wrong branch.** A move on another branch, when the topic lives on `design/<topic>`, offers a yes card; the new `switch-branch --topic <t> --yes` switches itself and refuses, naming the paths, when the working tree is dirty.
- **Saved goal files.** `resume` lists goal files in the topic's `inputs/` that `goal.md` does not record under `## Applied inputs` and offers `change-goal` on a card. The skill never offers to recreate an existing topic.
- **Card wording.** kit-lint flags a card with two questions and an option that corrects itself mid-sentence (`no:`, `I mean`, `actually`, `or rather`); the rule is in the question cards reference.
- **Kit version check.** `resume` and `create` return `kit_check` when the stated kit version and the skill's files differ and offer `/crav1-update-kit`; the session never states a version it did not read. When the design branch's kit is behind origin/main's, `resume` writes nothing and offers the merge card first.
- **Update kit fetch.** `fetch` clones into a short temp folder by default, with `core.longpaths=true` and `core.autocrlf=false`, and refuses an incomplete checkout (git status not clean) before any plan.
- **Update kit ending.** The new `ending` move tells the user to reload the window after an update and names `/crav1-design-architecture resume <topic>` for open design topics.
- **Scratch input.** Ending state and lean, settle, stage and compare drafts go in the session's temp folder; those moves refuse input from `inputs/`, which holds only the user's saved goal files. Topics from before 1.189.0 get `inputs/` on the first save.
- **Uncommitted as a count.** The ending prints `Uncommitted: N files.`; `true` is counted from git status of the topic folder and text is refused.
- **Commit before the ending.** The new `commit --topic <t> --yes` commits the topic folder after the user's yes; the flow offers it before the ending, and `create --builds-on` refuses while the base topic has uncommitted files.
- **Linked topic route.** `/crav1-design-architecture builds-on <base> <idea>` routes to a linked create, and the ending prints that command; a test checks that every Run next command the script prints routes.
- Design snapshot `design-order-branch-commit` and `scripts/tests/test_kit_1190.py`.

## 1.189.0 (2026-11-18)

Fixes for `/crav1-design-architecture` from a review of a long live design session.

- **Stored order.** Decisions and open questions keep the order they were added, or the goal's order after `change-goal`, instead of being sorted by title. `resume` takes the first reopened decision, then the first open big decision, then detail decisions.
- **Endings with lists and true or false.** `ending` prints one `Waiting:` line per item when `waiting` is a list and reads `uncommitted` as a count, a list of paths, `true` (the topic folder) or text, so no raw `['a']` or `True` reaches the user. inputs.md documents each value type.
- **Lean drivers.** `lean` matches short driver names to the drivers already listed instead of appending duplicates, and keeps the names on the decision as `Drivers:`.
- **Cards.** At most 4 options and one question per card. Typed input (your idea, a point to discuss, `ask-me`, `to-question`, `to-research`, `skip-for-now`) goes through the free-text Other; no option only says to type. An empty Other is asked again. A `discuss` with no text gets likely talking points, not an open question. kit-lint now checks this skill's cards for option count, type-only options and two questions.
- **Inputs and notes in the topic folder.** Script input files go in `docs/architecture/designs/<topic>/inputs/`; an input outside the specs repo is refused. The new `note` move (allowed in prepare) appends scans, visions, scope lists and answers to the topic's `notes.md`, and the flow saves open discussion with it before parking.
- **Scope round.** Framing asks what else the change should cover and orders decisions big shape first, detail last; a detail decision (`"detail": true`) is proposed only after the big ones.
- **Planned work.** Step 1 reads `plan.md`, `tasks.md` and `build-map.md` of slices the ask touches; planned work is an input, and options name it under `Overlaps`.
- **Unknown input keys.** `create` and `change-goal` refuse unknown keys and name them; a documented `notes` key is saved with `note`.
- **Design branches.** `create` creates `design/<topic>` (from `design/<base>` for a linked topic) or refuses with `git switch` when it exists elsewhere. A move on a topic that lives on its design branch, run from another branch, refuses with a Run next naming `git switch design/<topic>`.
- **Design branch update.** `resume`, `create` on an existing design branch, `fan-out`, `stage`, `go-ahead` and `change-goal` fetch and check whether `design/<topic>` is behind `origin/main`, and a linked topic also behind `design/<base>`, the same way the build walk's `code-behind` checks a code branch. When behind, the result carries a yes or stop card; the new `branch-behind --topic <t> --yes` merges with `git merge --no-ff`, never a rebase. A conflict merges nothing and names the files, and a run without the user never merges. `--no-fetch` compares with local copies.
- **Base to linked update.** After a committed change to a base topic (settle, lean, `change-goal`, a revisit settled or reopened, go-ahead), the ending lists each linked topic whose `design/<linked>` branch is behind `design/<base>`, and those moves return one yes or stop card for all of them. `linked-behind --topic <base> --yes` switches to each, merges `design/<base>` with `git merge --no-ff`, and switches back; never a rebase. A conflict stops on that branch, names the files and leaves the rest untouched; a run without the user merges nothing.
- **Small fixes.** `small-fix` lists a change with no design choice under `## Small fixes` in `design.md`; go-ahead copies the list with the design, with no ADR.
- Design snapshots `design-order-notes-fixes`, `design-branch-behind` and `design-linked-behind` (snapshot-check steps may now run `git`), and `scripts/tests/test_kit_1189.py`.

## 1.188.0 (2026-11-18)

Changing a design topic's goal and building one topic on another, for `/crav1-design-architecture`.

- **`change-goal` changes a topic's goal in place.** `design_run.py change-goal --topic <t> --input <json> --reason "<why>"` returns the old and the new goal, the change lines and the decisions it would flag, and writes nothing; the agent shows them on a card. With `--yes` it rewrites `goal.md` (ask, end goal, drivers, constraints, criteria and a `## Decisions` order) and logs the date, the reason and each change under `## Goal changes`. Decisions can be added, dropped, renamed or reordered. A dropped decision stays in the design, marked `dropped` with its reason, and review no longer lists it as missing. A settled or leaning decision that is renamed, listed under `reopen`, or whose title, lean, recommendation or draft ADR outcome names a word from a removed constraint, criterion or driver is marked reopened, and `resume` continues there in the goal's order. Open questions and leans on the other decisions stay. A run without the user is refused. Step 0 routes a new goal for an existing topic here instead of recreating the topic.
- **Linked topics.** `create --topic <t> --builds-on <base>` records `Builds on: <base>` and lists the base topic's settled decisions under `## Fixed from the base topic`. The design branch is cut from `design/<base>` (`git switch design/<base>`, `git switch -c design/<t>`), and base updates come in with `git merge design/<base>`, never a rebase. `resume` re-reads the base and names the decisions it settled or reopened since the last run. Settling or adding a base decision in the linked topic is refused; the new `revisit --topic <t> --decision "<words>" --reason "<why>"` marks it reopened in the base topic and ends with Run next on the base. `status` shows links both ways. `go-ahead` on a linked topic waits until the base design is under `## Decided, not built yet` or `## Confirmed` in `docs/architecture/spec.md` on main (or `--base-merged` after the user confirms); the refusal is a Run next with a Waiting line naming the base topic's design pull request. The copied block says `Builds on: topic <base>`.
- `scripts/snapshot-check.py` runs design snapshots (`design-spec/` plus `steps.json`): `design-goal-change` and `design-linked-topics`, and `scripts/tests/test_kit_1188.py`.

## 1.187.0 (2026-11-18)

- **Task names stop at the verify items.** The walk lead, the ending under Run next, the ready check's open-task list and `build-map.md` showed the whole task line, checks included, such as `Build T8 PR 12 takes in develop after PR 10 merges, with the conflicts resolved; integration — ...; system — ... with api-doc.yaml in it) on feat/orders-api:`. One helper, `task_order.task_name`, now cuts at the first verify item (`; integration —`, `; contract —`, `; system —`, `; unit —`, a `(verify: ...)` block, `(regression`), drops unbalanced parentheses and tidies stray spaces such as `( x` and `develop ,`. The line reads `Build T8 PR 12 takes in develop after PR 10 merges, with the conflicts resolved on feat/orders-api:`. `tasks.md` titles, the build map's short and full names and the walk's task labels all use it.
- Snapshot `orders-api-verify-names` (with a golden walk ending) and `scripts/tests/test_kit_1187.py`.

## 1.186.0 (2026-11-17)

Starting an open task on someone else's pull request branch, found on a live build walk.

- **An open task on a waiting branch starts.** `/crav1-build-walk <slug> <T#>` stopped on `wait-merge` whenever the branch's other tasks were pushed and waiting for the merge, even for a task nobody had built or claimed. The task now decides, not the branch's last step: `build_walk.py next --task <T#>` starts an open, unclaimed task whose dependencies are done as new work, and `next --branch` picks it too. Wait-merge applies only once every task on the branch is pushed. `build_walk.py progress start-task` claims the task in `claims.md`, adds it to the header's `Tasks:` line and records `- Step: start <T#>`, after the start yes.
- **One answer for the ready check and the walk.** `task_state.walk_start` (and `task_state.py walk-start --root <spec> --task <T#>`) says whether the walk can start a task: `build`, `wait-merge`, `done`, `held`, `claimed` or `unknown`. The ready check offers `/crav1-build-walk <slug> <T#>` only when it can, and invariant I8 checks that every offered task starts in the walk.
- **A take-in task on another person's branch.** A task whose work is taking the base into the branch, marked `(take-in: develop)` or, on a branch another person owns, saying it takes in develop (the script infers it, so nobody adds the mark by hand), may merge the base into that branch: a yes card, `git merge --no-ff origin/<base>` (never a rebase), resolve, the whole suite and the linter, commit, push after yes, and one pull request comment. The walk's own merge-base step and the pull request merge stay off in other-owner mode.
- **The ending names who merges.** On another person's branch the Waiting line names the pull request's author, such as `Waiting: person A to merge pull request 7, then T2, T3 and T4 on feat/orders-fixes are ticked.`
- **A task that cannot start gets a card.** Held by a dependency, claimed by someone else, or not in `tasks.md`: the script returns a card (`check-ready` recommended, or `stop`) and an ending with Run next first, so the walk never offers choices in prose.
- Snapshot `other-owner-take-in` and `scripts/tests/test_kit_1186.py`.

## 1.185.0 (2026-11-17)

- **Nested lists in the build map.** Each branch block in `build-map.md` now lists `- Tasks:` and `- Waits for:` one item per nested sub-bullet instead of joining them with `; `. A done task keeps its strike-through and `✓ done (PR N)` on its own sub-bullet, and an empty list reads `Waits for: none` on one line. Question, Ready now and the Plan step note stay on one line.
- **Delivers merged into Tasks.** The Delivers bullet is gone; Tasks, with task ids, is the branch's one list. The Mermaid diagram is unchanged, and a map written by an older kit is rewritten once on the next ready check.

## 1.184.0 (2026-11-17)

- **Older progress files with a second task.** Kits before 1.182.0 recorded a second task's build as a plain `- Step: build` with the task only in the result, such as `Result: done (T47: orders-api af772f5 on feat/orders-cicd, tests only)`, and the same for its verify, commit and comment steps. `task_state.py` now treats a done plain build step whose result starts `done (T<n>:` as that task built and waiting for the merge. The walk names every task on the branch (`T43 and T47 are pushed to PR 73 and wait for its merge`, and the Waiting line names both), adds the task to the header the next time it writes the file, the ready check does not offer it, the merge list says the pull request ticks both, and dependants wait on the merge. A snapshot covers this file shape.

## 1.183.0 (2026-11-17)

- **A quieter build map.** `build-map.md` no longer shows the two sentences above the diagram that named `open-map` and `export-map`. The map starts with its heading and the grouping line, such as `One branch per plan step.` Both choice words still work and stay listed in the skill.

## 1.182.0 (2026-11-17)

Fixes from a live build walk: a second task on someone else's pull request branch is recorded and counted everywhere, Azure DevOps thread posts find their repository, one verify wording for verified-and-waiting, and the walk asks before it fast-forwards a branch or sets a commit hook.

- **A second task on an existing branch.** `build_walk.py progress record` refused `--step 'build T47'` on a progress file whose header listed only T43. It now accepts `build <task>` for any task and adds a task the header does not list to its `Tasks:` line. `task_state.py` counts any done build step naming a task as built and waiting for the merge, whatever the header says, so older files work too. The walk's lead and ending name both tasks, the ready check no longer offers an already-built task or says `T47 is yours; the walk resumes it.`, the merge list says the pull request ticks both, tasks that wait on it read `held, waits on PR 71 to merge (T47, recorded)`, and the build map counts both. A snapshot spec folder covers a second task added to another person's pull request branch.
- **Thread posts find the repository.** `ado_threads.py` reads the organization, project and repository from the code repo's git remote (`--code-repo`, default the current folder), so `post` no longer returns 404 without `--org`, `--project` and `--repo`. The flags still override.
- **One wording for verified and waiting.** `Implemented, verified on branch` and `Implemented, verified, tick pending` were the same state. Only `Implemented, verified, tick pending` is written now; `verify_rows.py set` rewrites an old row once when it touches the file, and `task_state.py` and the ready check read both.
- **One verify row keeps the spec stamp.** Writing one row with `verify_rows.py set` moved the whole-file `Spec stamp:`, so other rows looked verified against a spec they were not checked against. One row now leaves it; `--all-rows` on the last row of a full verify moves it.
- **Fast-forward is a choice.** Before building, the walk runs `repo_sync.py code-behind --repo <code repo>`. A code branch behind origin gets a card, `fast-forward` or `stop`, and is fast-forwarded only after `fast-forward`. A diverged branch stops with the merge in Run next, never a rebase.
- **The commit hook is asked, not set.** A teammate whose repo has `.githooks/commit-msg` but no `core.hooksPath` gets `turn-on-hook` / `skip-hook` in finalize-commit's choices prompt instead of a silent `git config core.hooksPath .githooks`, and the `strip-trailers` option names that line on the card.

## 1.181.0 (2026-11-17)

A new preview skill, `/crav1-design-architecture`, works out an architecture change with you: systems, environments, hosting, data flows, integrations and deployment. It compares real options one decision at a time in a sandbox and copies the chosen design into the architecture spec only at go-ahead.

- **New skill.** `/crav1-design-architecture` (cross-cutting, group Specify, preview). Idea text starts a topic; `resume`, `park`, `status`, `fan-out`, `stage-it`, `go-ahead`, `compare-topics` and `prepare` are the choice words, and each decision card uses `choose-a`, `choose-b`, `choose-c`, `choose-mine`, `discuss`, `add-my-idea`, `ask-me`, `to-question`, `to-research` and `skip-for-now`. Every option shows what changes, environments, cost, risks, fit with the drivers and what it reverses, with a reasoned recommendation first. Your own idea is its own option.
- **Sandbox.** Work lives in `docs/architecture/designs/<topic>/` on a design branch: `goal.md`, one or more designs with draft ADRs, questions, draft diagrams and stages, and `compare.md` once a topic fans out. One-off cross-topic comparisons go under `_compare/` only when asked. No other skill reads the sandbox.
- **Script.** `design_run.py` owns the folder format and every move, saves after each one (no cap per session), reopens a decision on resume when a source it relied on changed, and refuses writes outside the topic folder before go-ahead. A run without you may only prepare.
- **Go-ahead.** The chosen design is reviewed for gaps against the goal, conflicts and missing decisions, then copied as one block under `## Decided, not built yet` in `docs/architecture/spec.md` with a "Designed in" link. Its ADRs are copied as accepted and numbered, still-open questions go into that spec, and the ending names pushing the design branch and opening its pull request before any planning.
- **Open questions in the architecture spec.** `/crav1-show-or-ask-open-questions` and `/crav1-resolve-open-questions` also read `docs/architecture/spec.md`, and `/crav1-existing-to-specs` recheck moves parts of a Decided, not built yet block up to Confirmed once the code or the environment shows them.

## 1.180.0 (2026-11-17)

Fixes from a live session review. One shared module now decides a task's state, the ready check no longer hides a merge deadlock or a built-and-waiting task, the merge list follows the plan, tighten-plan's ending names the ready check, and owner names are cleaned where they are stored. Snapshot spec folders and an invariant checker guard the ready check's output.

- **One owner for a task's state.** `task_state.py` (in `crav1-tasks-ready-to-build/scripts/`) says whether a task is done, tick pending, waiting for a merge or open. The build map takes each task's state and each box colour from it (`apply_task_states`, `box_state`), the ready check stamps the same state on its rows, verify's tick uses it, and finalize-commit runs `scripts/task_state.py commit-check` (a thin wrapper) for the merged-but-not-ticked decision, so a task recorded merged on the host is no longer done in one place and unticked in another. Tests check all three agree on the snapshot folders.
- **Claimed rows keep their order.** `claims.py preserve --write` put claimed rows back in the `claims.md` order, moving rows in `tasks.md`. They now keep their file order, and the file keeps its line endings.
- **The merge list follows the plan.** An unfinished task on a pull request's own branch now counts toward that pull request's order. A pull request whose branch still has an open task waiting on another pull request is listed after it, with `not ready to merge: T46 waits on T8 (PR 73)`.
- **Tick pending is not a reason to stop.** Finalize-commit names a task recorded merged but not ticked, recommends `commit`, and puts the verify step (or the tick, once verify passes it) in Run next, all from `task_state.py commit-check`. Verify's tick offer is a labelled Run next step (`verify_rows.py tick`), never a line after the ending, and the `verify.md` template comment says so.
- **Merge deadlocks are Blocked.** A task that waits on a task that ticks only when its own branch's pull request merges is shown as Blocked, red on the map, with `/crav1-tighten-plan` first in Run next, not as in progress.
- **Built and waiting is waiting.** A task built by someone else and waiting for its pull request now holds its dependants the same way whichever file mentions it, and an unrecognized blocker is counted as Blocked and printed instead of dropped.
- **Tighten-plan ends with the ready check.** With no plan issue left, Run next names `/crav1-tasks-ready-to-build <slug>`, never `/crav1-build-tasks`, and uncommitted files are committed first inside Run next.
- **Smaller fixes.** A reopened step's reason names only the sections that can reopen it (not Match or In the code). The map is written before uncommitted files are counted, and the line reads `Commit the <n> changed spec files:`. Held lines name every unfinished dependency, held ones first, then `and T8 (not built)`.
- **Owner names.** A leading word such as `Admin` and a trailing `(...)` tag are dropped when a name is written and when it is read, two spellings of one person are listed once, stored `PR author:` lines are rewritten once, and the ready check's reply ends with a `Recorded:` line naming the files it wrote.
- **Snapshots and invariants.** `scripts/snapshot-check.py` runs the ready check on anonymised spec folders under `scripts/tests/snapshots/` and compares the reply, the map and the build-progress files with the expected ones (`--update` rewrites them). `task_invariants.py` checks that counts add up, nothing Blocked is hidden, a ticked task is never ready, the merge list keeps its order, deadlocks name the plan fix, no `Next:` line appears, and no owner name keeps its extras.

## 1.179.0 (2026-11-17)

Fixes from a live ready check on Windows. The ready check now reaches Azure DevOps, says why when it cannot instead of asking who opened a pull request, writes each answer into the right build-progress file, and offers people as owner choices.

- **Azure DevOps on Windows.** The host lookup found `az.cmd` but started the bare name `az`, which Windows cannot start without a shell, and the failure was treated as no answer. It now runs the full path `shutil.which` returned (`az.cmd` or `az.bat`), with stdin closed, UTF-8 output, `--detect false`, extension install prompts turned off, and a 20-second timeout for `az` (8 seconds for `gh`; `CRAV1_HOST_TIMEOUT` overrides both). A completed pull request is read as merged and leaves the merge list in the same run.
- **A reason instead of nothing.** One lookup (`host_lookup`) returns why a host could not be read: `cli-missing`, `cli-not-runnable`, `timeout`, `not-signed-in`, `extension-missing`, `not-found`, `bad-output`, `unknown-status` or `host-error`, with the first line the CLI printed.
- **Host before owner.** The `--full` JSON lists these pull requests under `host_unread`, and `ask_first` is `code-repo`, then `host`, then `pr-author`. A pull request whose host was not reached is not in the owner question; its merge-list line says `owner unknown: Azure DevOps not reached`. Catch up first names the reason and the fix, a label on its own line above `az login` or `az extension add --name azure-devops`, then `Run the ready check again:`. `pr-author` returns `status: host-unread` with the reason and the fix.
- **The right build-progress file.** `pr-author --name` and `code-repo --repo` wrote into the first file that mentioned the pull request number anywhere, so an answer for one pull request could land in another's file. They now pick the branch's own file, then the one file whose own pull request it is, write only in the header, return `ambiguous` (with `--branch` to choose) when several files match, and create the branch's file when none exists. The reply's `commit` names the file to commit. The merge wait takes the file's own pull request, not the last one it mentions.
- **Owner choices.** `Owner:` is the walk's mode marker (`self` or `other`), so it is no longer read as a name and `other` is never a choice. The people open questions wait on are added; teams and organisations, such as `the project team`, are not.

## 1.178.0 (2026-11-17)

Fixes from a live ready check and a kit update. The build map shows each branch's state in colour, the update no longer refuses a stale commit-style rule, and the ready check asks for the code repo first, reads the owner and merge state from the host in one lookup, and runs again after each answer.

- **Build-map colours.** Each branch box in the `build-map.md` diagram takes its worst task's state: green is done (solid edge), amber waits on a pull request or a question (dashed edge), red is truly blocked only, such as a loop, a failed check or a reopened step (thick edge), and blue is the default for ready or not started. The edge out of a box shows that box's state. A `Legend` subgraph names the four colours. Fills are dark and text, borders and edges are bright, so the map reads on a dark background. A build-progress step whose last `Result:` is `failed` or `reopened` turns its branch red.
- **Stale commit-style rules are fixed, not refused.** `/crav1-update-kit` planned a rewrite of a stale `draft-commit-style` rule that pointed to the removed `crav1-draft-commit-message` skill, then refused it with `Refused: ... is a project file.` because the writer and the commit only took kit-owned paths. Now the kit writes and commits these rules itself; a rule is committed only when it is removed or matches the current asset, so a hand edit is never swept in. A stale rule whose asset is gone from the new release is listed under `delete` and removed in the same yes.
- **Update ending is Run next.** `/crav1-update-kit` ends `Run next: nothing needed now.` instead of a `Next:` line.
- **Repo first, then one host lookup.** When a waiting pull request's code repo is not recorded, the skill asks for the repo first, offering the `docs/system/repos.md` rows. With the repo known, one read-only lookup on that host (`gh` or `az`, 8-second timeout) gives both who opened the pull request and whether it merged, and the owner is recorded as `PR author:` in its build-progress file. The skill asks who opened it only when that lookup names no one. The `--full` JSON adds `ask_first`, `owner_unknown` and `owners_from_host`.
- **The check runs again after an answer.** After `walk_progress.py code-repo` or `pr-author` records an answer, the skill runs the ready check again in the same run and prints the new reply. Both commands return a `rerun` field naming it.
- **Owner choices.** The owner question offers the names the kit already knows (people in `claims.md`, PR notes' `author:`, and build-progress `PR author:`, `Opened by:` and `Owner:` lines) besides `Don't know`. `pr-author` lists them under `choices` when the host names no one, and the `--full` JSON has them as `owner_choices`.

## 1.177.2 (2026-11-16)

Fixes for a specs repo and a code repo on different hosts, found on a live run. The ready check asks each waiting pull request's own host whether it merged and records the merge, a pull request whose code repo is not recorded is named and asked about once, and `--write-map` says whether the map changed.

- **Merge state from the host.** A pull request completed on Azure DevOps still read `waits for PR 71 to merge`, because the ready check only read the kit's records and git in the specs checkout. Now `walk_progress.py readiness` asks each waiting pull request's own host first, read-only with a short timeout and only the CLI for that host (`gh pr view <n> --json state,mergeCommit,mergedAt,closedAt` on GitHub, `az repos pr show --id <n>` on Azure DevOps), through `pr_common.py`, which stays read-only. A merged or completed pull request gets a `Step: merge-pr` result in its build-progress file, such as `Result: merged (PR 71, merge commit 1a2b3c4d5e6f, merged on host 2026-11-14)`, the same shape as a `/crav1-merge-pr` or build-walk merge, and its branch run becomes `merged`. In that same run its tasks count as done, it leaves the merge list, and the tasks that waited on it can start. A build-progress file with a merge-pr result now makes the tasks on its `Tasks:` line done in the ready check and the build map. A pull request closed or abandoned without merging reads `Waiting: PR 71 was closed without merging; its tasks are not done.` and leaves the merge list, with nothing recorded. When the host cannot be read, nothing changes.
- **Code repo not recorded.** When no `Code repo:` line names where a pull request lives and `docs/system/repos.md` has zero or several rows, the ready check says `Waiting: PR 71 and PR 73: code repo not recorded, so the host was not asked whether they merged.` and lists them under `code_repo_unknown`. `/crav1-tasks-ready-to-build` asks you once which repo they are in, offering the `repos.md` rows, records the answer with the new `walk_progress.py code-repo --root <spec-folder> --pr <n> --repo <name-or-url>` (`Code repo: <url>` in that pull request's build-progress file; without `--repo` it lists the choices), and runs the ready check again so the merge list and Run next show what merged. The owner, merge-state and bare-number lookups all use that line.
- **Build map says whether it changed.** `readiness --write-map` always rewrote `build-map.md`, but when nothing had changed the file stayed byte-identical and showed no git change, which looked like a failed write. The reply now ends `Build map: docs/specs/<slug>/build-map.md (updated)` or `(unchanged, nothing new since the last write)`.

## 1.177.1 (2026-11-16)

Fixes to the ready check's pull request lines and to bare-number lookup, found on a live run. The merge list is the only place a pull request waits, a missing PR owner is read from the PR's own host and recorded through the kit, Run next asks the owners to merge when none of the PRs is yours, and a bare number recorded without a URL no longer falls back to the wrong host.

- **No repeated Waiting lines.** `Waiting: PR 82 is person B's; it unblocks T13.` and `Waiting: PR 71 and PR 73 (owners not recorded); they unblock T8.` repeated the numbered `Merge these PRs, in this order:` list above them. The ready check no longer prints them; the open-questions Waiting line stays.
- **PR owner from the host.** When neither a PR note nor build-progress names who opened a pull request, the ready check asks that pull request's own host, read-only with a short timeout (`gh pr view <n> --json author` on GitHub, `az repos pr show --id <n>` on Azure DevOps, only the CLI for the host the records name), and records the name as `PR author:` in build-progress. The new `walk_progress.py pr-author --root <spec-folder> --pr <n> [--name <who>]` does that write. When the host does not say, the merge list still reads `owner not recorded` and `/crav1-tasks-ready-to-build` asks you once who opened it, then records your answer with the same command; you never edit a spec file.
- **Ask the owners to merge.** When the merge list holds pull requests and none of them is yours, Run next leads with `Ask the PR owners to merge, in this order:` and one line per owner, such as `- person B: PR 82`, above `Resume the walk when the answers arrive:`. Your own pull requests still lead with `Merge your PR 71 first:`.
- **Bare numbers from the repo root.** `pr_common.py resolve --ref pr82 --root .` from the specs repo root fell back to the checkout's GitHub remote although build-progress said `built, PR 82 open` for a pull request in an Azure DevOps code repo. `--root` may now be the repo root, `docs/specs` or a spec folder. A record that names `PR 82` without a URL takes its host from a `Code repo:` line or the only `docs/system/repos.md` row. With no host it answers `ask`, for example `PR 82 is in build-progress for feat/orders-cicd, but its host isn't recorded`, names no CLI to install, and never falls back to the remote. `/crav1-review-pr` and `/crav1-pr-status` pass the specs repo root as `--root`.

## 1.177.0 (2026-11-16)

A pull request named by bare number is looked up in the kit's own records before this checkout's remote, the PR skills name only the CLI of the host the pull request is on, and the four PR skills end with Run next instead of a `Next:` line. The ready check leads with merging your own pull requests and keeps Waiting out of the merge list. A minor release because the PR skills resolve and end differently.

- **A bare number is resolved from the kit's records first.** `/crav1-review-pr pr82` in a GitHub specs checkout, for a pull request that lives in an Azure DevOps code repo, read `82` as a pull request on the checkout's remote. Now `pr_common.py resolve --ref <ref>` (read-only, JSON with a `line`) accepts `82`, `pr82`, `PR 82` and `#82` and looks in the build-progress files, the merge list (`build-map.md`, `walk-progress.md`), the PR notes in `docs/notes/` and `docs/system/repos.md`. Exactly one match is the pull request, with its URL and host. Several matches, or a record plus a pull request with that number on this checkout's remote, are asked, with every candidate listed. Only with no record does the number mean this checkout's remote. `/crav1-review-pr`, `/crav1-pr-status`, `/crav1-merge-pr` and `/crav1-open-pr` use it, as `pr-common.md` and `which-pr.md` say.
- **Only the resolved host's CLI.** The PR skills never tell you to install or sign in to `gh` unless the resolved pull request is on GitHub, and never to set up `az` unless it is on Azure DevOps. A GitHub checkout whose records point to Azure DevOps takes the `az` path.
- **PR skills end with Run next.** The shared rule in `pr-common.md` and `run-ending.md` no longer says one `Next:` line. The four PR skills end with `Run next:`, a short reason, and the label above the command, then Waiting and Uncommitted; nothing needed is `Run next: nothing needed now.` The pr-status example, since-last and the plan-step references were moved too. kit-lint now fails on reference prose in a Run-next skill or `pr-common.md` that tells the skill to print a `Next:` line, and on a PR skill script that prints one.
- **Your merges come first.** When the ready check's `Merge these PRs, in this order:` list holds a pull request that is yours, Run next leads with it, for example `Merge your PRs 71 and 73 first:` above `/crav1-merge-pr 71` (the first of yours in list order), and the `Resume the walk when the answers arrive:` entry stays below it. With none of yours the order is unchanged. Each pull request you did not open gets a Waiting line instead, for example `Waiting: PR 71 and PR 73 are person A's; they unblock T8.`
- **A PR's owner is who opened it.** The merge list and Run next take a pull request's owner from the PR note's `author:` front matter, else a `PR author:` or `Opened by:` line in build-progress, never from a claim. `yours` only when that author is your git user. Tasks you added to someone else's PR read `PR 71 (person A's, you added T5): ticks T5.` With no author recorded the line says `owner not recorded` instead of `yours`.
- **Waiting stays out of the list.** A blank line now separates the numbered merge list from the `Waiting:` line under it, so Markdown no longer folds that line into the last item.

## 1.176.0 (2026-11-16)

Fixes found on two more real walks. A step recorded again after a spec edit stops reading reopened, the ready check lists pull requests in merge order, a whole-branch run keeps two repos apart and records verified-on-branch work honestly, the plan steps and the build walk end with the label above the command and no `Next:` line, the ready check offers commit before push, asked questions are not offered again, and task titles keep their code text. A minor release because the walk, the ready check and the plan steps read and end differently.

- **A re-recorded step clears its reopen.** Each walk step now compares the spec against its own newest section stamps. Before, every step compared against the stamps of the latest step in order, often the ready check from the day before, so after an outside spec edit `/crav1-tighten-spec` stayed reopened even after it was done and recorded again, resume kept sending you back to it, and the ready check blocked every task on it. Recording the step again now clears it, the later steps still reopen until they are recorded, and the reopen sentence names only the sections that changed since that step was recorded.
- **Clear really clears.** `walk_progress.py clear --step <id> --yes` now fails with `still-reopened` instead of reporting success when the step still reads reopened after the refresh. With the fix above, a clear after an outside edit leaves the step at keep.
- **No send-back for a settled spec finding.** The tighten-plan empty queue sent you to `/crav1-tighten-spec` for a spec finding that was already patched. Only an open, skipped or sent spec finding does now.
- **Linter named when it is.** The plan recap said build is not named when `## Linter` had a partial line such as `No linter or checker in this repo for the shell scripts` beside a line that names a tool, or a recorded choice to go on without one. Those count as named now.
- **Plan steps end with Run next.** The plan-from-spec recap, the tighten-plan empty queue and review-plan put a plain label on its own line above the command, for example `Review the plan, which is written and not reviewed yet:` above `/crav1-review-plan <slug>`. No `Next:` line.
- **Asked questions are not offered again.** A question whose text or marks say `Raised with <person>`, `Waiting for <person>`, `Sent to <person>` or `Asked <person>` counts as asked, so the ending no longer offers `Ask the open questions, which haven't been asked yet:` for it. `Waiting for the export to finish` is not a person and does not count.
- **Commit before push.** When the slice folder has uncommitted files, the Catch up first block says `Commit the walk's changes, <n> files:` above `/crav1-finalize-commit`, then `Then push the specs repo:` above `git push`, on every result. It used to offer only the push.
- **The same wait is said once.** A task you claimed that waits on a pull request is in the Held list and the Waiting line, and no longer also in a `T5 is yours and waits for PR 71's merge.` sentence.
- **The reply keeps its closing lines.** The ready-check reference now says to print `reply`, which is `ending` plus `Source:`, `Build map:` and `Zoom the map in your browser:`. Printing `ending` alone dropped them on a rerun.
- **Whole questions in the Held list.** A held task quotes its whole open question, never cut with `...`.
- **Task titles keep their code text.** A task name with code spans, such as ``Separate keys on PROD `orders-api`, as T18``, no longer reads `PROD orders-api , as T18`. Notes such as `(verify: ...)` with nested parentheses are removed whole, so no stray ` )` is left.
- **Build-walk endings.** The build walk, the whole-branch run and the ready check's branch entries put the label above the command, for example `Build T3 Record the decision on feat/orders-api:` above `/crav1-build-walk orders-api T3`, and never put a lowercase line such as `branch feat/orders-api, T3 ...` under it. The whole-branch ending also accepts a plain `stop` value such as `"merge"`. A ready check with no branch entries says `Nothing needed now.` or a Run next entry, never a `Next:` line.
- **Small fixes from a colleague's whole-branch run.** `repo_sync.py status` on a repo without `docs/specs` says `The repo at <folder> has no upstream`, not `The specs repo`. claims.md says a whole-branch start also commits `walk-progress.md` and its progress file, as branch-run.md does. steps.md says a whole-branch run follows branch-run.md for commits and pushes. The commit style rule's description names its real path, `crav1-finalize-commit/branches/message-only/references/style.md`.
- **Merge these PRs, in this order.** The ready check replaces the per-PR Waiting lines with one block: `Merge these PRs, in this order:`, then one numbered line per pull request with its owner (`yours` when the claim or `Run yes:` user is your git user, otherwise the name), its branch, the tasks merging it ticks and the tasks that can then start, for example `1. PR 71 (yours, feat/orders-readme): ticks T5, then T6 can start.` A PR that another PR's tasks depend on comes first; ties go to the one that lets more tasks start, then the lower PR number. Waiting on open questions stays its own line. Branch runs says `built, PR 82 open` instead of `stopped before merge` when the PR is known.
- **Two-repo record.** `branch_run.py record` keeps the specs repo and the code repo apart: `--code-repo` for the work branch push, `--specs-repo` (default: the git top level of `--root`) for the commit. The old `--repo` still works and is sorted by whether it holds the spec folder. Every path is checked before anything is written, so a wrong path no longer leaves a half-written run behind a raw Python error. The specs commit holds the progress file, `claims.md`, `walk-progress.md` and `verify.md`, and ends with the work-item mention from `work-item.md`. `--push` pushes the work branch and the specs repo.
- **Verified on branch.** A new verify status, `Implemented, verified on branch`, for a task whose checks passed on a work branch that is not merged. It was written as `Not implemented` with passing evidence. The ready check says `verified on feat/orders-readme, waits for PR 71 to merge` (with `by <name>` for someone else's walk), tick-only never ticks it, and it becomes tick pending once the merge is recorded. A check that can only pass after the merge is pending, not failed.
- **The branch-run ending reads build-progress.** `branch_run.py ending --root <spec-folder> --branch <branch>` reads the pull request, the base, what was built with full task names, the first stop and the other ready branches itself, so the agent no longer hand-builds JSON. `--note` lines print under `Before the merge:` after what was built, never above Run next. A plain `"stop": "merge"` and partial built rows no longer crash it.
- **Help uses the ready check's ending.** `/crav1-help status` takes its Run next from `walk_progress.py readiness --skip-sync --text` (read only), so help and the ready check recommend the same command, with no `Next:` line.
- **Pull request body, format B.** `/crav1-open-pr` writes a short fixed shape on GitHub and Azure DevOps that always fits: a 2–3 sentence summary of what the branch delivers, one line per task with its full name and what it does, one or two lines on how it was verified, and the work-item mention. No links at all (no spec, plan, verify or code links), no per-file Changes list, no walk recap, and no risks, merge order or questions sections; that detail lives in the commit messages. An update to an older format A description rewrites it to format B. On Azure DevOps `pr_common.py fit --body <file> --text` stays only as a guard for the 4,000-character limit: it shortens the task lines to the task name, then cuts them at a word, and adds the plain line `Task lines were shortened to fit.` It adds no link and no overflow comment, and never writes a file.
- **Smaller.** The one-task build ending has no `Next:` example left; branch-run.md says to commit the claim with `start`'s message and not to open finalize-commit or `stack.md` for it; `verify_rows.py set` keeps a CRLF file CRLF and re-sorts a count line only when its ids change.
- **Plan labels use the short title.** `branch_run.py plan` names each task by its title in `verify.md`, as the ready check does, for example `T10 Orders CI/CD: deploy pipeline`. Without a `verify.md` it uses the map's name, never the first 80 characters with `...`. The ending still shows the full name.
- **The build-tasks hint moved to help.** The ready check's ending no longer ends with `/crav1-build-tasks builds one task without the walk.`; `/crav1-help status` names `/crav1-build-tasks <T#>` instead. A Waiting line that repeats a Held entry stays out.
- **Update-kit fixes a stale commit-style rule.** A saved `draft-commit-style` or `draft-commit-gitlog` rule under `.cursor/rules/` or `.claude/rules/` is rewritten from the current message-only asset when it is the old release's copy or still names `crav1-draft-commit-message/`. It is listed under `update`, so it is in the same yes. A rule changed by hand is left and listed in `style_rules_left`.
- **Help todo layout.** Each `/crav1-help todo` item is the item, then a plain label, then the command alone in its code span. The `Next: <skill>` ending is gone.
- **Review and status read the short body.** `/crav1-review-pr` checks a format B description task by task (each task line against the diff, each change against a task line) and `/crav1-pr-status` reads its task lines as the tasks the pull request carries. Merge order now comes from the ready check's `Merge these PRs, in this order:` list and `build-progress/`, and questions from the spec's open questions, not from the description; with none recorded they say so plainly. Older descriptions with Changes, Merge order, Questions for reviewers and Not in this PR sections are still read for existing pull requests, but the kit no longer describes them as what it writes.
- **kit-lint.** It now runs the ending scripts on sample states and fails on a `Next:` line or a lowercase line under a command, and it checks the plan skills' files for `Next:` lines.
- Tests: `scripts/tests/test_review_batch_1176.py` and `scripts/tests/test_review_batch_1176b.py`; older tests now expect the new layout and the settled-finding rule.

## 1.175.0 (2026-11-16)

Fixes found on a ready check run after a colleague's build walk: Run next no longer offers to continue someone else's walk, built tasks under someone else's claim read built instead of in progress, a reopened step says why, and the Catch up first push entry is said once. A minor release because the ready check, the build map and the catch-up block read differently.

- **Continue only your own walk.** `Owner: self` in `build-progress/<branch>.md` is written relative to whoever ran the walk, so a colleague's walk read as yours and Run next offered `Continue the build walk on <branch>:`. Now the walk's claim user in `claims.md` (else the `Run yes:` name in its progress file) must match `--user` or `git config user.name`, the same comparison that makes a claim yours. Someone else's walk is a Waiting line: `Waiting: T9 to T12 are person B's, built, and wait for PR 82 to merge.`, or `Waiting: T9 to T12 are in progress by person B.` when the pull request is not known. No continue offer.
- **Built, not in progress.** A task claimed by someone else that is built on a branch that is not merged (a done `Step: build T#` or a `- Built: T#` row in `build-progress`) reads `built by <name>, waits for PR <n> to merge` in the Held list, the status and `build-map.md`, instead of `in progress by <name> since <date>`. The claim still holds the task until the merge.
- **A reopened step says why.** The Run next entry for a reopened step now has one plain sentence that names what changed and which tasks wait, such as `The spec's Constraints section changed after /crav1-tighten-spec was last recorded in walk-progress.md, so T9 waits.`, above an action label, `Finish the reopened /crav1-tighten-spec step:`. It was `The work waits until the reopened /crav1-tighten-spec step finishes:` with no reason. The reopen rule is unchanged: only a change to the spec, plan or tasks that a step covers reopens it, and a build walk's own files (claims.md, walk-progress.md, build-progress, verify.md) and task ticks never do. A regression test runs a whole build walk's file changes and checks that no step reopens.
- **Push said once.** The Catch up first block no longer has the sentence `The specs repo is 2 commits ahead of origin.` above a label that said the same. The label reads `Push the specs repo, which is 2 commits ahead of origin:` above `git push`.
- Tests: `scripts/tests/test_walk_owner_claims_1175.py`; four older tests now expect the new reopened entry, the push label and the own-walk check.

## 1.174.0 (2026-11-16)

Fixes found on a second real ready check: a done task keeps its merge commit instead of the later commit that ticked it, Run next offers to continue an unfinished branch walk first, a built branch no longer reads as waiting on its own tasks, the build map shows full names, and the pull ending puts its label above the command. A minor release because the build map and the ready check write and end differently.

- **Merge commit over the tick commit.** 1.173.0 read a branch's `build-progress` file top to bottom and kept the last `Result: done (...)` hash, so a `Step: tick T27` result such as `done (9f8e7d6, verify 5e4d3c2)` replaced the `Step: merge-pr` result `done (PR 80, 1a2b3c4, branch deleted)`. Now the hash comes from the `merge-pr` step. A tick or commit step's hash is used only when there is no merge result, no own `verify.md` row and no mark already on the map, so it never replaces a merge commit.
- **Continue an unfinished walk first.** When `walk-progress.md` lists a branch run that is not merged, such as `stopped before merge`, and its `build-progress` file is not at `comment`, `wait-merge` or `merge-pr`, Run next starts with `Continue the build walk on <branch>:` above `/crav1-build-walk <slug> <branch>`. A walk that waits on a merge, or someone else's walk, stays a Waiting line (1.171.0).
- **A branch never waits on its own tasks.** On `build-map.md`, a branch whose open tasks are all claimed or walked used to read `held, waits on T9; T10; T11; T12`. Now it reads `built, waits for PR 82 to merge` when its `build-progress` file shows every open task built and no merge, or `in progress` otherwise. A later branch still reads `held, waits on <branch>`.
- **Full names in the build map.** The `Delivers:` and `Tasks:` lines on `build-map.md` use full task names, never cut with `...`, like the chat Held list since 1.173.0.
- **Pull ending layout.** A behind or diverged specs repo ends with `Merge origin into your local branch, since they have diverged (never rebase):` (or `since it is behind`) above `git pull --no-rebase`, not a lowercase reason under the command. The loop-fix entry in the ready check puts its label above the command too.
- Tests: `scripts/tests/test_merge_hash_walk_1174.py`.

## 1.173.0 (2026-11-16)

Fixes found on a real ready check: the build map no longer swaps a done task's commit for another task's commit, Held names are full, the open-questions entry has its label above the command, and finalize-commit has no `Next:` line on any ending. A minor release because the build map, the ready check and finalize-commit write and end differently.

- **Done commits stay on their own task.** `readiness --write-map` and `build_map.py` took a done task's commit from the first line in `verify.md` that named the task and held any commit, so a `Date:` line such as `second run (T4 and T27 rechecked); T43 added from its build at local abc9d01` gave T4 and T27 the newer, unrelated T43 commit. Now the commit comes only from that task's own evidence: the `Result: done (...)` merge commit in its branch's `build-progress` file, else the task's own row in `verify.md`, preferring a merge commit there. A Date line, a gaps note or another task's row never counts. With no own commit, the mark already on `build-map.md` stays.
- **Full Held names.** Held and ready lines in the ready check use the full task name, never cut with `...`. Held questions may still be shortened.
- **Open-questions entry.** The Run next entry reads `Ask the open questions, which haven't been asked yet:` on its own line, then `/crav1-show-or-ask-open-questions <slug>` alone in its code span. Every Run next entry the readiness script builds now puts its label above the command, as a grammatical sentence: a reopened step reads `T1 waits until the reopened /crav1-tighten-plan step finishes:` (`T1 and T2 wait until ...` for several tasks, `The work waits until ...` for none), verify behind reads `Verify the built tasks, since verify.md is behind:`, a push reads `Push the specs repo, which is 2 commits ahead of origin:`, a blocking question reads `Resolve the open question that blocks the first task:`, and a resume reads `Resume the walk when the answers arrive:`.
- **Finalize-commit endings.** `commit`, `copy`, `stop` and a failed commit end with Run next or nothing, never a `Next:` line. A suggestion to throw an edit away is a plain sentence with the git command in a code span. Kit-lint fails on a `Next:` line anywhere in the finalize-commit skill.
- **Kit-rewritten files still ask.** A typed `commit` or `commit-now` still asks, with `stop` recommended, when the only changed files are kit-rewritten files (`build-map.md`, `walk-progress.md`, `build-progress/*`) whose values disagree with `verify.md` or `build-progress`.
- Tests: `scripts/tests/test_map_hashes_1173.py`.

## 1.172.0 (2026-11-16)

Walk tooling: the build walk reads its state from the files instead of hand-written JSON, Azure DevOps threads have one safe helper, the walk and review read fewer references, and a verify rerun checks only what moved. A minor release because the build walk, review-pr, open-pr, verify and the one-task build gain scripts and route differently.

- **Walk state from files.** `build_walk.py next --root <spec folder> --branch <branch>` reads phase, owner and pull request from `build-progress/<branch>.md`, full task names from `tasks.md`, and the Uncommitted line from `git status`. `--waiting`, `--who` and `--pr` add what the files do not hold; `--json <file>` still works.
- **Progress file by script.** `build_walk.py progress init --root --branch --owner --tasks --cut-from` writes the header, and `progress record --root --branch --step --result` adds one step with `Done` and the normalized stamps. Both preview without `--yes`. The walk never writes the file by hand.
- **Azure DevOps thread helper.** `crav1-review-pr/scripts/ado_threads.py list`, `compare --draft <file>` and `post --file <file> --yes`. It reads `az -o json` from stdout as bytes and decodes UTF-8, then UTF-8 with a BOM, then cp1252, so a Windows code page no longer breaks `json.load`. A post is always a new top-level thread (`parentCommentId` 0). Review-pr posting and the open-pr Windows section point at it.
- **Fewer reference reads.** At `comment` or `wait-merge` the walk prints `lead` and `ending` straight from the script and reads no reference. The one-task build skips `tool-approvals.md` when `approvals: already-done` is passed. Review-pr reads `comment-as-posted.md` only when the PR note's draft has no posted section.
- **Scoped verify.** `crav1-verify-build-against-spec/scripts/verify_rows.py scope` says which rows to verify again: a row whose branch or tip moved, a row with no recorded tip, or every row when spec.md, plan.md or tasks.md changed (a ticked checkbox does not count). The reply prints `kept_line`, such as `Kept from the last verify: T1, T3 (branch and tip unchanged).` `verify_rows.py set --task T# --status <status> --evidence <evidence> --branch <b> --tip <sha> --yes` writes one row, recounts the TL;DR and records the tip under `## Row tips`.
- Tests: `scripts/tests/test_walk_tooling_1172.py` (mocked az output with cp1252 bytes).

## 1.171.0 (2026-11-16)

Fixes found on a real build session: the walk no longer offers a task that only waits on someone else's merge, task names and branch descriptions read cleanly, and the last skills that still printed a `Next:` line end with Run next. A minor release because the ready check, the build walk, the verify reply, fix-build-gaps, finalize-commit, open-pr and review-pr read differently.

- **A task waiting on a merge is not offered.** The ready check reads `build-progress/<branch>.md`. A task whose branch's last step is `comment` or `wait-merge` is waiting (`Waiting: PR 71 to merge, then T5 is ticked.`), not in `can_start`, and tasks after it are held too. In `wait-merge` the build walk's ending has no entry for the current branch: the Waiting line says why, and Run next starts with the branches that can start. Before, `/crav1-build-walk <slug> T5` was offered again in the walk, the verify reply and the ready check, and only reprinted the wait.
- **Your own claim in plain words.** `In progress by you: T5. Your own claim does not hold it.` is now `T5 is yours; the walk resumes it.`, or `T5 is yours and waits for PR 71's merge.` The readiness reference agrees with the claims reference.
- **Full task names.** The ready branches in the readiness JSON carry the full task name, and the walk no longer strips the `...` of a shortened one, so a name never ends mid-phrase such as `metadata read from the`.
- **Branch descriptions.** A plan note about how the branch was made (`The orders CI/CD branch, cut from develop after billing-ops.`) is no longer a description; the step heading or the open task names describe it. The description follows the open tasks, not a sentence about a task that is already done.
- **One lead sentence.** `build_walk.py next` returns `lead`, one sentence from phase and owner, such as `T5 is pushed to PR 71 and waits for its merge.`, that agrees with the Uncommitted line. The walk prints only that before Run next, never `nothing to commit` above an Uncommitted line.
- **No comma command.** Two or more tasks on one Run next entry use the branch form, `/crav1-build-walk <slug> <branch>`, with one task per line under it, never `T43, T8`.
- **Re-reviews are new threads.** On Azure DevOps a re-review posts a new top-level thread, so it shows at the top of the pull request. It replies in an earlier thread only to answer a question asked there.
- **Run next in review-pr, fix-build-gaps, finalize-commit and open-pr.** No `Next:` line is left in these skills. Review-pr ends with `Commit the PR note:` and `/crav1-finalize-commit`, then `git push`, and shows Uncommitted in chat. Fix-build-gaps is one lead sentence and a Catch up first block (commit, then push to the pull request) before verify. Finalize-commit ends with `git push`, `/crav1-open-pr` or `/crav1-open-pr pr<n>` under a label. Open-pr ends with a `git push` catch-up when the specs repo is ahead, then `/crav1-review-pr <repo> <n>`.
- **The ready check's last reply is Run next.** The record card comes before the ending, so the final reply starts with Run next. When only the time or the verify version would change, `record_unchanged` is true, the card is skipped and `record` writes nothing (`Record unchanged.`).
- **Verify reply branch blocks from the ready check.** With no hand-written steps, `walk_ending.py --verify` builds the branch blocks from the ready check (`ready_branch_blocks`): description, open tasks and the whole-branch entry, the same as the build walk.
- **Other-owner verify status.** After a build on someone else's pull request passes and is pushed, the verify row says `Implemented, verified, tick pending`, not `Not implemented`.
- Tests: `scripts/tests/test_endings_readiness_1171.py`; four older tests now expect the wait-merge ending and the new claim line.

## 1.170.0 (2026-11-15)

The ready check's Catch up first line for a failed verify is short, and a hold with nobody named reads in plain words. A minor release because the ready check, the walk and the verify reply read differently; `verify.md` and the JSON are unchanged.

- **A short failed-verify reason.** `T6 failed verify: <reason>.` pasted the whole Verify cell from `verify.md`, a long paragraph of test names. The reason is now the cell's opening sentence, plus the sentence that names the cause (`... made the asserts stale.`, `... because ...`) when it fits, about 200 characters, cut only at a sentence end (a single long sentence is cut at a clause end). Leading run detail such as `fail at PR 7's tip abc1234: pipeline 6 run 251 (Run tests, log 19), 110 failed, 173 passed.` gives way to the next sentence, which keeps `at PR 7's tip abc1234`. Example: `T6 failed verify: four of the tests T6's verify rests on fail at PR 7's tip abc1234. 9f8e7d6 made the asserts stale.` The full cell stays in `verify.md` and in the readiness JSON for `/crav1-fix-build-gaps`. The verify reply's `T6 failed:` change line uses the same reason.
- **Nobody named, in plain words.** A held question with nobody named said `Waiting for not named yet.`; it now says `Nobody is named to answer it yet.` An approval says `Nobody is named to give it yet.`, the Waiting line says `(the partner; nobody named for 1)`, the build map's Question line says `nobody named yet`, and the build walk's approval stop says nobody is named to give the yes. The JSON `who` value is unchanged.
- `walk_ending.failed_reason()` is new; `catch_up_block()` and `verify_changes()` use it. The readiness, rules, approval-holds, build-map and verify-behind references, two walkthroughs, run-ending and the skill pages show it. Tests: `scripts/tests/test_short_reason_1170.py`; the 1.127.0 Waiting-line and build-map Question-line tests expect the new words.

## 1.169.0 (2026-11-15)

The ready check no longer says verify is behind right after a fresh verify, and a failed verify no longer hides the branches you can build. A minor release because the ready check and the tighten-and-plan ready check read differently, and the verify template drops a line. The build walk and the verify reply are unchanged.

- **A fresh verify is current.** An older `Next:` line in `verify.md` is stale only for a ticked task whose own row says Not implemented, claimed done or unverified, or that has no row. A row that says Verified or Failed means verify is current. In 1.168.0 a line like `Next: /crav1-fix-build-gaps <slug> T6, because ... T4 and T7 are verified.` flagged T4, T6 and T7 as behind.
- **A failed task goes to the fix.** A built task whose verify failed is in the Catch up first block as `T6 failed verify: <reason>.` (the reason is that row's Verify cell), with `Fix T6:` and `` `/crav1-fix-build-gaps <slug> T6` ``, not sent back to verify.
- **Ready branches always show.** Needs verify holds only its own task. With tasks that can start, the result is ready-partial and each ready branch keeps its block after the catch-up block and the `---` line. In 1.168.0 one failed task made the result not-ready and Run next kept only the catch-up block or the questions line. With nothing that can start the result stays not-ready. Questions that are not asked yet stay a `/crav1-show-or-ask-open-questions <slug>` entry after the branch blocks.
- **No Next line in verify.md.** The verify template and the spec reviewer's copy drop the TL;DR `Next:` line; the chat reply's Run next names the next step (1.168.0). Older files that still have one read as above.
- `walk_ending.catch_up_block()` takes `failed`; the readiness JSON's verify gap carries `failed`. The readiness, rules, verify-behind and tick-pending references, four walkthroughs, the glossary, data layout, run-ending and the skill pages show it. Tests: `scripts/tests/test_verify_current_1169.py`; the 1.135.0 test for a Next line over a verified row now expects it current.

## 1.168.0 (2026-11-15)

The verify reply gets the shared ending. A minor release because `/crav1-verify-build-against-spec` reads differently in chat; the live checks and `verify.md` are unchanged.

- **Run next, not a Next line.** The next step is the reason once (`T6's four tests fail on stale asserts at the PR's tip.`), then the label on its own line (`Fix T6:`) and the command alone in its code span (`` `/crav1-fix-build-gaps <slug> T6` ``). The six case references (fix, build, plan, tighten, open a pull request, nothing needed) give that shape. Build what is left names `/crav1-build-walk <slug> T#` per ready branch, like the ready check.
- **Catch up first.** What can be settled now leads Run next in the 1.167.0 layout: a plan note such as `T24 to T26 may belong to another slice` (`/crav1-tighten-plan <slug>`) and an uncommitted `verify.md` (`/crav1-finalize-commit`, then `git push`). That replaces the verify `Uncommitted:` line.
- **A brief reply.** `Verify — <slug>`, a `Result:` line with the counts, one line per task whose state changed since the last verify (`T6 failed: ...`, `T44 row dropped: not in tasks.md`), Run next, Waiting for what you cannot act on now, and `Report: docs/specs/<slug>/verify.md`. The TL;DR, tables, per-task bullets and branch detail stay in `verify.md`. The word `full` shows the TL;DR and Tasks overview in chat.
- **Fewer reads.** The skill names what it reads: spec, plan, tasks, the previous `verify.md`, and the reference a step names. It does not open `build-map.md`, `claims.md`, `walk-progress.md` or a log unless a step needs it.
- One builder: `walk_ending.verify_reply()` with `verify_state()`, `verify_catch_up_block()` and `step_block()`, run as `walk_ending.py --verify <state file>`. The script reads the counts and changed tasks from `verify.md` against the committed copy, and the uncommitted files and ahead count from git; the skill passes only the steps, plan notes and waits. The verify skill ships a `scripts/walk_ending.py` wrapper and a new `references/reply.md`. SKILL.md is 1,413 words (was 1,416).
- `run-ending.md`, the verify walkthrough and the skill pages show it. Tests: `scripts/tests/test_verify_ending_1168.py`.

## 1.167.0 (2026-11-15)

What you can fix now leads Run next as a Catch up first block, instead of sitting in Waiting lines at the bottom. A minor release because the ending reads differently in the ready check, the tighten-and-plan ready check and the build walk.

- **Catch up first.** verify.md behind tasks.md, a verify.md row for a T# that is not in tasks.md, and a specs repo ahead of origin are one `**Catch up first**` block at the top of Run next, before the branch blocks and in their layout: the bold heading, one or two plain sentences of what is behind (`verify.md is behind for T4 and T7, and it has a row for T44, which is not in tasks.md.`), then each command alone in its code span under its label (`Check T4 and T7 against the spec and remove the T44 row:` with `` `/crav1-verify-build-against-spec <slug>` ``, `Push the specs repo (2 commits ahead):` with `` `git push` ``), and a `---` line before the first branch block. Left out when nothing is behind. A not-ready ending puts the same block first and drops its separate verify or push entry.
- **One command for the stray row.** `/crav1-verify-build-against-spec` now says it writes one Tasks overview row per T# in `tasks.md` and drops a row for a T# that `tasks.md` does not have, naming it in the reply. The ready check therefore names only that command, and no longer `/crav1-tighten-plan`, which never wrote `verify.md`.
- **Waiting is for waits.** Waiting lines keep only what you cannot act on now, such as a person's answer or a merge.
- One shared builder, `walk_ending.catch_up_block()`, used by the ready check and the tighten-and-plan ready check (`catch_up` in the readiness JSON), and passed through by `/crav1-build-walk` and the branch run when their state carries `catch_up`.
- `run-ending.md`, the readiness, rules, verify-behind, next-verify and sync references, the build-walk state table, three walkthroughs and the skill pages show it. Tests: `scripts/tests/test_catch_up_block_1167.py`; two older tests now expect the block.

## 1.166.0 (2026-11-15)

Every Run next branch block has a description again, and a held question that points to a note shows the question itself. A minor release because the ending reads differently in the ready check, the tighten-and-plan ready check and the build walk.

- **A description under every branch.** 1.165.0 left the line out when the plan step's first sentence was not clean, so on a real plan most branches had none. Now the line between the bold branch and `<n> open tasks:` is, in order: up to three clean sentences from the plan step (each ends with a full stop, has no colon list, no person leading it and no file or path), about 300 characters at most and cut only at a sentence end, never mid-sentence; else the plan note trimmed to its opening clause, the words before the first `:` or ` — `, for example `The orders CI/CD branch, cut from develop after billing-ops.`; else the step's heading in plain words; else one sentence from the branch's open task names, a shared prefix once, for example `Orders CI/CD: infra Bicep, cd pipeline, ci lint and tests, and deploy README.`, about 160 characters. The line is left out only when the branch has no plan step and no usable task name.
- **No person's name.** A plan note that opens with a person, such as `Person A builds PR 73: GetReceipts answers 404 ...`, drops that lead and describes the work after it: `GetReceipts answers 404 for a cursor that matches no stored receipt.` A short trailing fragment such as `PR 73` is dropped too.
- **The quoted question, not the pointer.** A held question whose text ends with `:` or only points to a note, such as `The note docs/notes/x.md, in Open questions, question 5, says:`, shows the quoted question that follows: the `>` blockquote under the bullet in the spec, else the text in quotes after the colon, else the first sentence ending in `?`. The question's key and stored text do not change, so recorded answers still match. A question that quotes another one keeps its inner quotes on the held line.
- `run-ending.md`, the build-map fallback reference, the grouping reference, both walkthroughs and the skill page show the new rule. Tests: `scripts/tests/test_branch_description_1166.py`; three older tests now expect the description line.

## 1.165.0 (2026-11-15)

Fixes to the Run next ending from 1.164.0, found when it ran on a real plan. A minor release because the ending reads differently in the ready check, the tighten-and-plan ready check and the build walk.

- **Clear gaps between branches.** A `---` line, with a blank line on each side, now stands between two branch blocks in Run next, so the next branch's name never sits right under the previous command in a Markdown viewer.
- **The branch sentence is a description, not plan notes.** The line under a branch is the plan step's first sentence only when it is clean: it ends with a full stop, has no colon list and does not open with a person, such as `Person A builds PR 73: ...`. Otherwise it is the step's heading in plain words (a bold lead, or short words before ` — ` or `:`). Otherwise the line is left out. So a person's name no longer leads that line.
- **Cuts at a clause or a word.** A long branch sentence or held question is cut at a clause end, else at a word, never on a dangling word such as `the` or `that`. There is a bit more room, about 160 characters.
- **The question, not its heading.** A held question that opens with a short heading, such as `Client certificate.`, shows the question sentence (the one ending in `?`), or else the next real sentence.
- **The first task matches the list.** A branch's open tasks are listed in the order the walk runs them. A task that cannot start yet says why on its line, for example `- T8 Take in develop (waits on T5)`. When the first listed task cannot start, the task command says `Run only T43, the first task that can start:`.
- `run-ending.md`, the build-map fallback reference, the grouping reference and both walkthroughs show the new form. Tests: `scripts/tests/test_run_next_fixes_1165.py`.

## 1.164.0 (2026-11-15)

The kit's question cards now share one wording rule, and an automatic check holds the walks and the pull-request skills to it. A minor release because several cards and Waiting lines read differently, and settle-and-push asks one card instead of two.

- **The rule.** [Question cards](docs/reference/question-cards.md) gains **Card wording**: a short plain question with no brackets and no kit terms; each option says what happens if you pick it, for example `Build T5 on PR 71's branch so it lands in PR 71`; the recommended option is first, marked Recommended, and says why in a few words; background goes in one sentence before the card, never inside it; questions you would always answer together are one card, and a yes already on record is never asked again; Waiting lines name who or what and why, for example `Waiting for person A to approve T7` instead of `needs_yes T7`. The older rules stay: no `Edits` option, typed changes on the free-text answer, a missing word asked again, and the merge card names the pull request.
- **Always-loaded rule.** `crav1.mdc` keeps its one pointer to the page, now saying `plain question, options saying what happens`. It is 658 words.
- **Build walk.** The other-owner card asks `Should I add my work to their pull request?` after one sentence naming the owner, with **Add to their pull request (Recommended)**, **Keep it as my own** and **Stop**. The commit, merge, claim and branch-run cards name the action and its target, for example `Merge PR 71 into develop?`. Settle-and-push is one card: one yes commits the walk's files and pushes the specs repo. Script Waiting lines are plain, for example `Waiting: person A to merge pull request 71, then the tasks on feat/orders-cicd are ticked.` and `Waiting: your yes to run T5 Deploy live.`
- **Tighten and plan walk.** The playbook cards ask `This playbook is already applied. Apply it again?` or `This playbook was skipped before. Apply it now?`. The kept-open batch, jump-back and same-or-new cards say what each option does. `walk_progress.py spec-finding` prints a `background` sentence, a plain question such as `Fix P2 in the spec now, before the plan goes on?`, and a `text` for each option. The option labels and choice words are unchanged. The clear-or-rerun question for a reopened step comes from the new `reopen_cards` entry in the readiness output, for example `The plan review reopened because the tasks changed.` then `Skip redoing the plan review?`, with no stamps, `Done`/`Result` or commands in it. The record question says in words what will be saved, `Save the ready check as done?`, instead of quoting the `walk-progress.md` line. The playbook card says one plain sentence first and puts no step ids or brackets in the question. The claim note agrees in number: `In progress by you: T5. Your own claim does not hold it.`
- **Pull-request skills.** `/crav1-open-pr` asks `Post this comment on PR 71?`. `/crav1-pr-status` puts the thread facts in one sentence before each card, for example `Set thread 112 back to active?`. `/crav1-review-pr`'s fetch card names the older copy first.
- **Held list.** The ready-check ending lists each held task on its own line under its branch heading, instead of joining them with semicolons. The quoted open question is short: markdown markers such as `**New:**` are removed, and it keeps the first sentence, about 100 characters at most. No doubled punctuation such as `.;`.
- **Run next layout.** Each ready branch is one block in wave order: the branch in bold, one plain sentence of what it does from the plan step that owns it (left out when there is none), `2 open tasks:` with one task per line, then `Run the whole branch:` and its command, then `Run only T9, the first task:` and its command. A branch with one open task says `1 open task:`, then `Run T5:` and one command. Each label is on its own line and each command is alone in its code span. The slug rule, claimed tasks and the Held and Waiting lines are unchanged. The ready check, the tighten-and-plan ready check, the build walk and the branch run share it (`walk_ending.py` `branch_block`).
- **Zoom the map.** Under the `Build map:` line the ready-check reply adds `Zoom the map in your browser:` and the command `/crav1-tasks-ready-to-build <slug> open-map`, each on its own line. `export-map` stays inside `build-map.md`.
- **One lead sentence.** Before a ready-check or walk ending the reply has at most one short lead sentence of recap, then `Run next:` ([run-ending](docs/reference/run-ending.md), tighten-and-plan `readiness.md`).
- **Fewer reads.** `walk_progress.py start` and `resume` return `read`, the one reference the next step needs (`playbook.md`, `steps.md` or `readiness.md`). The tighten-and-plan walk opens only that file. `progress.md` is only for a stop or a clear.
- **PowerShell output.** [Running a kit script](docs/reference/running-scripts.md) says not to redirect a script's output with `>` or pipe its JSON into another program in PowerShell, and to read it directly, because PowerShell adds a BOM.
- **The check.** `scripts/kit-lint.py` reads `Card:` blocks in skill files and flags a question with brackets, an option that does not say what happens, a Recommended option that is not first, a kit term from a short list, and options listed inline in prose instead of a `Card:` block. Prose is not checked. It covers the build walk, the two ready checks, and the four pull-request skills; 1.165.0 extends it to the rest. Whether an option really says what happens still needs a person to read it.
- **Tests.** The check flags each problem and passes prose and fenced examples, the reworded skills pass it, the script cards (loop fix, jump-back, same-or-new) pass it, the build walk's Waiting lines carry no kit terms, held tasks are one per line with a short question, the Run next block has the new layout and the open-map line, `read` names an existing reference, and `crav1.mdc` stays at most 660 words.

## 1.163.0 (2026-11-15)

The kit's multi-word choice words are now one hyphenated word each, so a tool or a permission check cannot split them. A minor release because the words you say have changed, and the spaced forms are no longer accepted.

- **Ready check.** `fix-loop`, `fix-loop <n>`, `open-map` and `export-map` replace `fix loop`, `fix loop <n>`, `open map` and `export map`. The kit prints only the hyphenated forms: the Loop offer, the Run next entry, the map's heading line, the card, and the docs. Say `/crav1-tasks-ready-to-build <slug> open-map`, or `fix-loop` under a Loop line. The ready-check parser recognizes only the hyphenated words. A spaced `open map`, `export map` or `pipeline runs` is not a command. The script flags `--fix-loop` and `--export`, and the `walk_progress.py fix-loop` subcommand, stay as they are.
- **The other words.** The same rule applies across the kit: `release-claim`, `pipeline-runs`, `new-branch`, `one-task`, `all-tasks`, `repos-only`, `repos-and-bundle`, `one-spec`, `spec-per-feature`, `repos-vs-specs`, `code-change`, `edit-description`, `verify-gaps`, `live-gaps`, `message-only`, `commit-now`, `git-log` (the style word; the `git log` command is unchanged), `strip-trailers`, `keep-trailers`, `fetch-pr-branches`, `use-disk`, `stop-pr-review`, `comment-posted`, `newest-comment`, `skip-comment-record`, `as-reviewer`, `as-author`, `since-last`, `no-code`, `todo-next`, `todo-top N`, `whats-new`, `what-it-does`, `what-and-why`, `teach-the-language`, `convert-to-note`, `suggest-features`, `push-features`, `push-tasks`, `pull-tasks`, `pull-spec-changes`, `branches-all`, `branches-skip-stale` and `migrate-formats`. Spaced forms are not accepted. Stored note kinds (`kind: code change`), Read-line fields (`newest comment <timestamp>`), and status phrases such as `branch rewritten since last read` are unchanged.
- **Loop-fix preview.** `walk_progress.py fix-loop` without `--yes` still writes nothing and shows the card, but a successful preview now exits 0. A nonzero exit is only for a real error, such as a missing `tasks.md` or a fix number that does not exist.
- **Loop-fix Why line.** The `Why:` line is a plain reason, for example `Why: the plan step for feat/orders-dev-switch already describes this work.` It no longer lists the raw keywords that matched the plan step.
- **Reply once.** The ready-check skill tells the assistant to give the script's formatted reply once as the answer, not to paste the raw tool output and then repeat it, with at most one short lead sentence before it.
- **Not-ready Run next.** When the result is not-ready, the readiness ending starts with a `Run next:` entry for the first real next step: the command alone in a code span, and a one-line reason. Examples are `/crav1-tighten-plan <slug>` when the plan was reopened for review, `/crav1-verify-build-against-spec <slug>` when verify.md is behind, and `git push` when the specs repo is ahead. The old line `Reopened: review-and-tighten-plan. T5, T9, T43 stay in can_start and are not a start while the result is not-ready` is now plain words, for example `The plan was reopened for review, so T5, T9 and T43 wait until /crav1-tighten-plan finishes.`
- **Tests.** The parser accepts `open-map`, `export-map` and `pipeline-runs` and leaves a spaced form unrecognized, the Loop lines and the card say `fix-loop`, the map heading names the hyphenated commands, and the routing table lists the hyphenated words. A successful `fix-loop` preview exits 0, the `Why:` line has no keyword list, a not-ready ending starts with `Run next:` and a plain reason, and the ready-check skill tells the assistant to give the formatted reply once.

## 1.162.0 (2026-11-15)

The build map opens as a zoomable page in your browser, and exports as one file you can send. A minor release because the ready check gains the `open map` and `export map` choice words and a new script.

- **The problem.** A wide build map shrinks to fit the Markdown preview, so the diagram text gets small and hard to read. The preview cannot zoom into a diagram.
- **Open map.** `/crav1-tasks-ready-to-build <slug> open map` runs `scripts/open_build_map.py docs/specs/<slug>`. It renders the whole `build-map.md` as a dark page in a temp file and opens the browser: headings, text, lists, code spans, links, and the wave lists, which still fold. Each Mermaid diagram sits in place, unchanged, with zoom at the mouse wheel, drag to pan, and `-`, `+`, `Fit`, `100%` and `Fullscreen` buttons, plus `+`, `-` and `0` when it is focused. The text stays in a readable column. The diagram pane uses the full width of the browser window and refits when the window is resized while it is at Fit. The `.md` file is not changed.
- **Works offline.** The kit ships Mermaid 11.4.1 and marked 18.2.0 in `crav1-tasks-ready-to-build/scripts/vendor/`, with `VERSIONS.txt` and their MIT licences in `LICENSES.txt`. The open page loads them from there, and falls back to the same pinned versions on jsDelivr when the folder is missing.
- **Export map.** `export map` runs the script with `--export` and writes one self-contained HTML file with both libraries inside, about 2.6 MB, that works offline in any browser with nothing to install. The default is `<slug>-build-map-<YYYY-MM-DD>.html` in Downloads, else the current folder, else the temp folder. It is never written inside the specs repo, and an `--out` path inside it is refused. The page shows `Exported <date> from build-map.md`.
- **The map file.** `build-map.md` gets one line under its heading naming both commands. A branch whose every task is done says `Waited for:` instead of `Waits for:`, since nothing waits any more. Open branches keep `Waits for:`.
- **Tests.** The Mermaid blocks are found as the page draws them, a label holding `</script>` cannot break out of the page, the export has no external script or CDN address, the open page points at the vendor folder, the default export name uses the spec folder and today's date and is never inside the specs repo, the page CSS lets the diagram pane span the window, and a done branch says `Waited for:` while an open one says `Waits for:`.

## 1.161.0 (2026-11-15)

When two branches wait for each other, the kit works out the fix and applies it on a yes, instead of asking you to edit `tasks.md` by hand. A minor release because the ready check gains the `fix loop` choice word and `walk_progress.py` gains `fix-loop`.

- **The problem.** Since 1.154.0 a loop between branches ended with `Fix one of these lines in tasks.md.` Most people would not know which line to change, or that a `(map:)` mark is how to change it.
- **The offer.** Under the `Loop:` line the reply prints the fixes, best first, in plain words made from the tasks: what is wrong, the change, that the tasks stay the same and only the branch and pull request they go into change, and the order afterwards. For example: `Recommended fix (say `fix loop`): T14 and T15 are on feat/orders-cicd, but they wait for T13 on feat/orders-dev-switch, which itself waits for feat/orders-cicd to merge, so the two branches wait for each other. Build T14 and T15 on feat/orders-dev-switch instead, right after T13. The tasks stay the same; only the branch and pull request they go into change. Then feat/orders-cicd holds T9-T12 and merges first, and feat/orders-dev-switch runs T13, T14, T15, T16. Why: the plan step for feat/orders-dev-switch already describes this work (pipeline, repoint, delete, app).` Alternatives follow as `Other fix (say `fix loop 2`): …`.
- **How it chooses.** A move builds a task that waits across the loop, plus the tasks on its branch that wait on it, on the branch it waits for. It is kept only when that loop is gone and no new loop appears, and it never empties a branch or moves a done task. It is recommended when the target branch's plan step already describes the tasks. Dropping one wait is an alternative, or the only fix when the tasks themselves wait for each other, and it warns that it changes the build order. When no single change works, the line says so and names `/crav1-tighten-plan`.
- **Applying it.** Say `fix loop` or `fix loop <n>`, or pick the new Run next entry `/crav1-tasks-ready-to-build <slug> fix loop`. `walk_progress.py fix-loop --root <spec-folder> --pick <n>` writes nothing and prints a card: a plain question, the picked fix first and marked Recommended, each option saying what happens, and `Leave it`. With `--yes` it writes or replaces the `(map:)` mark on each moved task (keeping a repo word), or removes the one task from the `(after:)` mark, rebuilds `build-map.md`, and reports `No loop left.` or the next loop. Both files stay uncommitted. `spec.md` is never touched. `build_map.py <spec-dir> --fix-loop [--pick N] [--yes]` does the same.
- **At plan time.** `plan_check.py order` (`/crav1-plan-from-spec`, `/crav1-tighten-plan`) lists the same loops as `Branch loop:` lines with the same fixes. Tighten-plan offers them as a `P#` with the new `fix-loop` option, applied on the batch yes.
- **Docs.** Every page that said to fix a line in `tasks.md` now describes the offer. New reference `crav1-tasks-ready-to-build/references/loop-fix.md`.
- **Tests.** A loop with a clear move (the recommended fix moves T14 and T15, and the reply and card text carry the problem, the move, that only the branch and pull request change, and the order after); a loop where only dropping a wait works; a fix that would make a new loop is not offered; every offered fix leaves no loop; without a yes nothing is written; the yes writes the `(map:)` marks, replaces the old one with its repo word, and the rerun has no loop; a drop removes one wait; the readiness ending carries the fix word and card; `plan_check.py order` lists the branch loop; and no skill page asks for a hand edit.

## 1.160.0 (2026-11-14)

The branch offer finds a task branch that was deleted only on your computer, and the build uses it without asking. A minor release because `--recommend` reads the remote and gains a `checkout:` and a `repo:` line, and the ready check gains `--user` and `--branch`. Your own claim no longer holds a task, and claims are written in local time.

- **The bug.** A task line named `feature/orders-incoming-table`, the source branch of open PR 71 that the task had to land in. The specs live in a separate checkout from the code. `build_map.py --recommend` then said the branch `was deleted locally and on the remote` and offered a new branch named after the plan step, `feat/orders-pr-71-gets-readme` from develop. The branch was still on origin, so the build had to ask which branch to use.
- **Remotes are read for real.** `build_map.py` reads each remote with `git ls-remote --heads` once per run, besides the `origin/<name>` refs, and, when `gh` works, the open pull requests with `gh pr list`. A branch is called deleted on the remote only when a remote that could be read lacks it. A remote that cannot be reached is never taken as gone. `CRAV1_NO_REMOTE_CHECK=1` turns both reads off.
- **Origin only means use it.** When the task-line branch is only on a remote, `--recommend` keeps it as `source: task line`, says `because: feature/orders-incoming-table is on origin only; checkout creates the local tracking branch`, and prints a last `checkout: feature/orders-incoming-table` line. `/crav1-build-tasks`, `/crav1-build-walk` and the Build prompt in `/crav1-create-feature-branch` then check it out with no branch card.
- **The right repo.** The specs repo and the code repo can be separate checkouts, for example `specs-platform` next to `orders-ops`. That was the real cause of the bug: the branch was looked up in the specs repo, where the code branch never lives, and an old reflog entry there made it look deleted. The branch is now checked in the task's code repo, named by a repo prefix on `(map:)` or `(branch:)`, a Match `Branch: <repo> <branch>` line, or a `Repo:` line in tasks.md. That repo is `--code-repo <path>` when given, else the specs repo when its folder or origin has that name, else a sibling checkout with that name. `--recommend` prints `repo: ../orders-ops` before `checkout:` when it is not the specs repo. When the named repo is not found, the task-line branch is kept with `because: could not check orders-ops from here`. A branch is never called deleted unless it was checked in the right repo. The walk reuses that answer instead of checking the specs repo again.
- **An open pull request wins.** An open pull request whose head is the task-line branch beats merged and deleted, and a `PR n` on the task line picks that pull request. The `because:` line names it. Only a branch missing everywhere, with no open pull request, gets a new step-named branch, as before.
- **Your own claim does not hold you.** The ready check's gates refused a task whose claim was yours, so `/crav1-build-tasks` would not build what you had just claimed. `walk_progress.py readiness` now takes `--user` (default `git config user.name` in the specs repo) and `--branch` (the branch being walked). A claim by you, on that branch when given, keeps the task's own state: its gate has `refused` false, the reason is `in progress by you`, and the reply says `In progress by you: T#.` Someone else's claim still holds and refuses the task.
- **Claims in local time.** `claims.py` wrote `since` in UTC with microseconds. It now writes local time with the local offset, to the second, for example `2026-11-14T23:40:00+01:00`. Older UTC lines still read, and are written back in local time.
- **Tests.** With a bare origin in a temp repo: a branch deleted locally but still on origin is offered, with and without its `origin/` ref; a branch gone everywhere gets a new name; an open pull request head wins over a deleted or merged branch; another pull request's head does not count; and turning the remote check off keeps the old answer. With separate specs and code checkouts: a `Repo:` line, a repo prefix on `(branch:)`, or a Match `Branch:` line points at the sibling code repo, and its origin-only branch is offered with `repo: ../orders-ops`; a repo that cannot be found is never called deleted; `--code-repo` wins; a branch gone from the code repo still gets a new name; and the walk offer is not refused. Claims: your own claim is not refused, on the walked branch or with no branch given, and with the user read from git config; your claim on another branch and someone else's claim still refuse; `since` is local time to the second; and an old UTC line still reads.

## 1.159.0 (2026-11-14)

`/crav1-tighten-plan` and `/crav1-plan-from-spec` compute their own ordering, batches and endings, and both skill files are shorter. A minor release because both skills gain a script whose output they show as-is.

- **One script for both.** `scripts/plan_check.py` ships with `/crav1-plan-from-spec`, and `/crav1-tighten-plan` ships a thin copy that runs it. `order` prints the dependency waves from the `(after: …)` marks, using the same sort as the ready check, and names a loop, an `after:` that names no task, tasks whose order is only guessed from the file, and task lines with no verify kind or no `(spec: …)` mark. `recap` prints the plan-from-spec After writing recap in its usual order, ending with its one `Next` line. `queue` prints the tighten-plan index and counts, and the one empty-queue `Next` line once no plan finding is open. `batch` prints the findings table and its card line together, through the same `batch_offer.py` as before. `reviewed` lowers `P# open` on the Reviewed line, keeps the date, and never adds a line.
- **The same output.** Apart from the acceptance line below, the Next lines, the linter rule, the batch card with its table in the same reply, and the Reviewed line say exactly what they said before. The assistant still decides what is a finding, its tag, its options and its recommendation, and which built pieces and security checks apply. The script does the counting and the wording.
- **Acceptance check by meaning.** The recap line that lists acceptance lines with no matching task now reads `Check these acceptance lines, no task matched their wording:`. The script matches by wording only, so a reworded line can be listed even when a task covers it. The agent compares each listed line by meaning with the trace table and tasks first. When a task covers it, the agent adds or fixes the trace row or `(spec: …)` mark without asking. Only a line nothing covers is a gap, and the plan is not done until it has a task, is marked `already there`, or is `left as committed`. `references/recap.md` suggests spec ids such as `AC-1`, which make the match exact, and never requires them. `/crav1-tighten-plan` treats a reworded line a task already covers as a `fix-trace`, not a new task.
- **Shorter skill files.** tighten-plan drops from 1,396 to about 1,100 words and plan-from-spec from 1,433 to about 1,140. Every rule that left a skill file moved word for word: tighten-plan's plan shapes, empty-queue lines, Reviewed line and suggest step to `references/issues.md`; plan-from-spec's After writing list to `references/recap.md`, and its plan.md sections and host setup tasks to `references/write.md`.
- **Tests.** Each skill file stays under its new word cap, every moved rule can still be found word for word, the waves match the ready check's order, the recap and empty-queue Next lines match the references, the batch output is the same as `batch_offer.py` for the open plan findings, and the Reviewed line keeps its date and is never added.

## 1.158.0 (2026-11-14)

The four pull-request skills share one page and one script for the steps they have in common, and each skill file is shorter. A minor release because the four skills gain a shared reference and a shared script.

- **One page for the shared steps.** `/crav1-open-pr`, `/crav1-merge-pr`, `/crav1-pr-status` and `/crav1-review-pr` used to repeat the same plumbing: which pull request a number or URL names, the host order, Windows quoting, the open state, never logging in, never rebasing, and how a run ends. That now lives once in `docs/reference/pr-common.md`, shipped next to the skills as `crav1-docs/reference/pr-common.md`. Each skill points at it and keeps its own judgement. Where a skill's own rule differs, the skill wins.
- **One small script.** `scripts/pr_common.py` is read-only and does the lookups: `parse` (which host and number a reference names, and whether it matches this remote), `host`, `find` (the open pull requests for one branch, never picking the newest), `checks` (state, draft, and the checks as passing, failing and pending), `claim` (the `In progress:` lines for one branch in `claims.md`) and `behind` (commits behind and ahead of the base, with the advice to merge the base in, never rebase). The full script ships with `/crav1-open-pr`; the other three ship a thin copy that runs it.
- **Shorter skill files.** open-pr drops from 1,468 to about 1,140 words, merge-pr from 1,476 to about 1,130, pr-status from 1,495 to about 1,110, and review-pr from 1,542 to about 1,260. Every rule that left a skill file moved word for word into that skill's `references/` or the shared page: open-pr's checks before the draft (`references/checks.md`) and GitHub create steps (`references/github.md`), merge-pr's GitHub host and read steps and its Azure DevOps ready step, pr-status's status table, output order and hand-offs, and review-pr's Ship or not (`references/ship.md`).
- **Merging is unchanged.** `/crav1-merge-pr` still merges only when this turn names the pull request and asks to merge it, always with a merge commit (`gh pr merge --merge`, Azure Repos `--squash false`), never squash, rebase or a bypass, stops on `Ready: no` unless the turn says `anyway`, and prints nothing of its own for the next step when `/crav1-build-walk` opened it. It never writes or clears `claims.md`; the walk clears its own claim after the merge, as before.
- **Tests.** Each skill file stays under its new word cap, the shared script parses GitHub and Azure DevOps references, refuses a branch name and a mismatched repo, never picks the newest of several pull requests, sums up checks, reads claims without writing them, and gives merge-in advice only. The merge-pr yes gate, merge method, claim rule and walk ending are checked word for word.

## 1.157.0 (2026-11-14)

The rule file loaded into every session is short again, and every build-walk ending is only the Run next block. A minor release because the always-loaded rule and the walk ending change.

- **A shorter always-loaded rule.** `crav1.mdc` drops from about 1,175 to about 655 words, close to the 650 of 1.42.0. It keeps only what every session needs: specs are the source of truth, the six startup options, the generated order, follow the running skill's own rules, call `/crav1-help` for an order, how a run ends, asking (no re-asking, stated defaults, one batch, one final yes, at most four options, the recommended one first, plain choice words and never `--flags`), never rebase and catch up by merging the base in, no code on a base branch, edit with the host's edit tool, run only named scripts, name local files as code spans, never read production data, and do not scaffold.
- **Nothing lost.** The longer text of each rule, with its examples and edge cases, moved word for word to a new page, `docs/reference/standing-rules.md`, that ships next to the skills as `crav1-docs/reference/standing-rules.md`. The rule points at it. The interpreter order stays in `running-scripts.md`, the card rules in `question-cards.md`, and the base-branch rules in `code-branch.md`.
- **Walk endings are Run next only.** `/crav1-build-walk`, for one task or a whole branch, ends with the Run next block first, then what was built, what is left, and Waiting. The script no longer writes a `Next:` line under it. When a step is held (an Approval needed item, a live yes, a pull request still to merge, someone else's branch), the reason is a `Waiting:` line. With no work branch left, Run next is `/crav1-verify-build-against-spec`.
- **Commit after a paused walk.** When `/crav1-finalize-commit` finds an unfinished build walk on the branch, it now ends with a Run next entry holding the command that resumes it, `/crav1-build-walk <slug> <branch>` for a whole-branch run or `/crav1-build-walk <slug> T#` for one task, instead of a bare `Next: /crav1-build-walk` line.
- **Tests.** The rule stays at or under 700 words, every rule that moved can still be found word for word, the walk endings have no `Next:` line, held steps say why on a Waiting line, and no skill file shows a `Next: /crav1-build-walk` example.

## 1.156.0 (2026-11-14)

The ready check prints its own ending, the three walks share one ending, and the short reply is the default. A minor release because the readiness output, its default, and a choice word change.

- **The script prints the reply.** `walk_progress.py readiness --root <spec-folder> --write-map --text` prints the whole ready-check reply: the header, the counts row, `Result:`, the ending (Run next first, Held, Branch runs, Loop and Waiting lines, claim warnings), `Source:` and `Build map:`. The assistant shows it as-is and never adds a `Next:` line. When nothing can start, the script also prints the one Next line the reply keeps (resolve the question, verify, or nothing needed now).
- **A shorter skill.** `/crav1-tasks-ready-to-build` drops from 1,900 to about 960 words. It keeps the step order, the stops and the choice words. The rules it used to restate moved to `references/rules.md`, word for word, for when the script cannot run.
- **One shared ending.** The ready check, the tighten-and-plan ready check and `/crav1-build-walk` (in-walk and whole-branch endings) build their ending with one script, `scripts/walk_ending.py` in the ready-check skill, which each of the three skills ships. For the same ready branches, all three print the same Run next entries, word for word. The shape is one section in `run-ending.md`, and the tighten-and-plan and build-walk skills point at it instead of describing their own.
- **Brief by default.** `readiness` prints the short output unless asked for `--full`, which prints the complete JSON. `/crav1-build-tasks` asks for `--full` for its held-task check. In chat, the new word `full` (`/crav1-tasks-ready-to-build full <slug>`) adds the per-task lists and the Order line.
- **Tests.** The Run next entries match across the three skills for the same state, the ending order is shared, readiness is brief without a flag, the ready-check skill stays between 800 and 1,100 words, and no skill instruction asks for a Next line after the Waiting lines.

## 1.155.0 (2026-11-14)

`/crav1-build-walk` can build a whole branch in one run. A minor release because the walk gains a branch argument, a per-task push after one yes, a new section in the progress file, a status line in `walk-progress.md`, and a second Run next entry per branch.

- **Branch argument.** `/crav1-build-walk <slug> <branch>` builds every open task on that branch in task order. `/crav1-build-walk <slug> T5` still builds one task, as before.
- **Real stops only.** The run stops for an open question on the next task, a stakeholder yes that is not recorded, a manual, secret, host-setup, or Runs live step, tests or lint still red after a fair try (three tries), a change it wants outside the task's scope, and always before the pull request merge. Anything else keeps going: it commits each task and prints one line, such as `T9 done, tests green, starting T10`. There is no continue card between tasks.
- **Resume.** After each task the `## Run` section of `build-progress/<branch>.md` records `- Built: T9, commit <sha>, tests green` and `Next task:`. Running the same command in a new session continues from the next open task, builds nothing twice, and writes no new claim. Every three tasks (or `Fresh session hint: every N tasks`) the progress line suggests a fresh session. It is never a stop.
- **One claim for the branch.** After the start yes the run writes one `In progress:` line that names every open task on the branch, in the same format as 1.151.0, so the ready check and tighten-and-plan show all of them as in progress. Before each task it fetches: someone else's claim on, or change to, one of those tasks stops the run and says who and what. When the branch is only behind, it merges origin in (never a rebase) and continues. After each task it pushes the commit and the progress with no card, because the start yes covers the run. The claim stays at the stop before the merge and is cleared on merge as before. A stop partway keeps it unless you say `release claim`.
- **Ending.** At the stop before the merge the walk opens or updates the pull request itself and never merges. The reply is Run next first, each command alone in its own code span on its own line (the merge, through the existing yes, and the next ready branch), then each built task with its commit and test result, then what is left: skipped tasks and why, open questions, and verify rows that are behind.
- **One place to look.** `walk-progress.md` stays the one file every skill reads. A whole-branch run keeps one line there per branch, under `## Branch runs`, for example `- Branch run: feat/orders-cicd: running, T9 done, next T10 (2026-11-14T09:40:00+01:00). Log: build-progress/feat--orders-cicd.md`, then `stopped before merge`, `stopped at T4: <why>`, or `merged`. The line links to the detailed log in the branch's build-progress file. It is updated with each per-task push. The ready check and tighten-and-plan print the lines that are not merged. Recording a tighten-and-plan step keeps them, and a file with only these lines is not a paused walk. When two sessions change the file, a merge conflict that is only these lines, or only hash lines, is settled by `walk_progress.py resolve-stamps`, which keeps each branch's newest line.
- **Run next offers both.** The ready check, the tighten-and-plan ending, and the build-walk ending offer each ready branch's next task, `/crav1-build-walk <slug> T#`, and, when that branch has two or more open tasks, the whole branch, `/crav1-build-walk <slug> <branch>`, as a separate entry. Each command is alone in its own code span on its own line, with the branch and task names underneath. A branch with one open task gets only the T# entry. The T# entry now names only the next task, not every ready task on the branch, because the branch entry covers the rest. `next_lines` carry the same entries.
- **Script.** `scripts/branch_run.py` in the build-walk skill (`parse`, `plan`, `start`, `guard`, `after`, `record`, `ending`), with the kit wrapper `scripts/branch-run.py`.

## 1.154.0 (2026-11-14)

The build map and the ready check name a dependency loop in plain words, agree on what is blocked, and keep the wave order. The tighten-and-plan references stop asking for a Next line under the Waiting lines. A minor release because the map, the ready-check result, and the ending change.

- **Loops are named.** When branches wait for each other, the map and the ready-check ending (also `readiness --brief`) print one line per loop, for example `Loop: feat/orders-x and feat/orders-y wait for each other: T14 on feat/orders-x waits for T13 on feat/orders-y, and T13 on feat/orders-y waits for T12 on feat/orders-x. Fix one of these lines in tasks.md.` A wait that comes only from file order says it is the task just before, with no `(after:)` mark. The flowchart puts those branches in an `In a loop` group.
- **One judgement.** The ready check reads the loops from the same build the map writes. The open tasks on a branch in a loop are Blocked in the counts and in the map, and are not offered in Run next. Tasks on other branches keep their real state: ready, waiting on a question, or waits in order. When other tasks can start, the result is `ready-partial`; when only loop tasks are left, it is `not-ready`.
- **Wave order.** A branch is always in a later wave than each branch it waits for, unless both are in the same loop. Branches in one loop share a wave. A branch downstream of a loop keeps its own wave and state instead of being listed under Blocked.
- **Held label.** A held line shows the wave, or `in a loop`. It never shows `(blocked)`.
- **No stray Next line.** The tighten-and-plan skill, its readiness and progress references, the ready-check fallback in `build-map.md`, the walkthrough, the glossary, and `run-ending.md` now match 1.153.0: one Run next block at the top, the walk command only there, and no `Next:` line after the Waiting lines. A stop prints the walk command as a Run next entry. Kit lint fails when a skill file tells the agent to write a Next line after the Waiting or Held lines, or gives a `Next: /crav1-build-walk` example for the ready check.

## 1.153.0 (2026-11-13)

The ready check keeps an open task on its own branch, prints one Run next block, and stays short enough to read. A minor release because the map, the ending, and the script output all change.

- **Task-line branch.** The branch on the task line, or beside that T# in a leading Branches paragraph, is the map row for an open task even when it shares a plan step with a done task on an already-merged branch. An open task is never placed under a branch git proves merged, or under a done sibling's branch, when another name is written for it. Held lines use that same row.
- **One Run next.** The ready-check ending has exactly one Run next block, at the top. The walk command appears only there. The bottom keeps Waiting lines and at most a one-line `/crav1-build-tasks` alternative, with no second copy of the command and no `Next:` line. The reply must print that block verbatim and must never write a `Next:` line of its own.
- **Brief output.** `walk_progress.py readiness --root <folder> --brief` prints only the result, a counts row, the ending, and claim warnings, under 8 KB for a 45-task slice. `--full` (the default) still prints the complete JSON. The ready check calls the brief form. `build_map.py` with no flag still prints only the one-line path of the file it wrote.
- **Open-question count.** The Waiting line counts only tasks whose hold is itself an open question or an approval, and names only the people on those questions. A task that waits on another task is not counted there.
- **Orphan verify row.** A `verify.md` table row for a T# that is not in `tasks.md` is one Waiting line naming that T#, and the fix is `/crav1-verify-build-against-spec` or tighten. Report only; the check does not edit `verify.md`.

## 1.152.0 (2026-11-13)

The ready check keeps the branch on the task line, and its printed commands work in a new session. A minor release because the map, the Next lines, and the script commands a ready check runs all change.

- **Task-line branch.** A branch counts as merged only when git proves its tip is already in the base or the default branch. A line that only mentions a future merge, such as `(PR 12) to be merged into develop`, is not a recorded merge. When git cannot tell, or shows the tip is not in the base, the task-line branch stays. A fallback name is short and does not use a person's name from the task line.
- **Script paths.** Every skill whose docs run `scripts/repo_sync.py` or `scripts/claims.py` now ships a thin wrapper to the build-walk copy. `approval_needed.py`, `question_blocks.py`, `task_order.py`, and `build_map.py` accept a spec folder or a file. A missing file is a one-line error and a nonzero exit. `question_blocks.py` exits 0 when questions are found, and nonzero only for a real error. The documented-invocation check fails when a skill documents `scripts/<name>.py` and that file is not in the skill folder, unless the paragraph names another skill that has it.
- **Titles and Next.** A task label never prints blank. Leftover backticks fall back to the first readable words, or `work`. Short names cut at a word boundary with an ellipsis. Run next and the Next lines use the untrimmed name. Each Next line matches Run next: the command alone in a code span, with the slug when `docs/specs` has several slices, and the branch and task on the next line. `/crav1-build-tasks` stays on a line of its own.
- **Shorter output.** `task_order.py` prints short labels by default. Pass `--full` for the complete title.
- **Can start now.** The map summary's `M can start now` uses the same readiness rule: only a ready branch counts. A later wave that waits in order, a claimed branch, or a question hold is 0 for that branch. `Wave 2: 1 branch, 0 can start now` when it still waits on wave 1.
- **Claims on stop.** A mid-walk stop, such as before a merge step, does not clear the claim. The claim is cleared when the branch is merged or ticked, or the user says stop and is done with this walk, or `release claim`. This matches the build-walk skill text. A later ready check in a new session still holds that task as in progress.

## 1.151.0 (2026-11-13)

Two people can work on the same specs repo without one walk disappearing from the other. A minor release because the ready check, the tighten-and-plan walk, and `/crav1-build-walk` now fetch first, hold claimed tasks, and push the walk's files at the end.

- **Claim.** When `/crav1-build-walk` starts on a branch, it writes `In progress: feat/orders-api-host-setup, T27, person A, since 2026-11-13T15:50:00+01:00` in `docs/specs/<slug>/claims.md`. After one yes it commits and pushes only that file. The ready check and `/crav1-tasks-ready-to-build` hold those tasks as `in progress by <user> since <date>` and do not offer them in Run next. Tighten-and-plan, plan-from-spec, and tighten-plan leave claimed task lines unchanged (no renumber, reorder, rewrite, or removal), may change other tasks, and say once which claimed tasks were kept. The walk clears the claim, then commits and pushes after yes, when the branch is merged or ticked, or the user says stop or `release claim`. A claim older than three days (or `Claim max age: N days`) gets a warning and the clear words. It is never cleared on its own. Normalized content stamps ignore claim lines. The file is `claims.md`, not a section of `build-map.md`, because the ready check rewrites the map, and not `walk-progress.md` or `build-progress/`, which record position, not a shared lock.
- **Pull before reading.** `/crav1-build-walk`, `/crav1-tighten-and-plan-ready-to-build`, and the ready check fetch the specs repo first. Behind origin, they stop before reading or writing, and Run next is `git pull --no-rebase` (merge, never rebase). No upstream, or a failed fetch, is said once and the command continues. Ahead continues with a Waiting line to push. Diverged stops.
- **Settle and push.** When a walk branch finishes, or the user stops, the walk lists every uncommitted specs-repo file it or its step skills wrote (the progress file, notes and their indexes, `verify.md`, `build-map.md`, `tasks.md` ticks, `claims.md`), commits them with the persisted commit style, then one card to push, naming how many commits the specs repo is ahead. Files it did not write are listed and left uncommitted. If the branch is behind, it merges origin in first and never rebases. A conflict stops and names the files. After a successful push the ending says the specs repo is in step with origin. An unpushed repo is a Waiting line, never a buried note. A headless run stops and names `yes` and `stop`.

## 1.150.0 (2026-11-13)

The tighten-and-plan walk prints its ending in the reply, and the ready check no longer blocks on its own stale record. A minor release because the reply shape changes, and a reopened ready-check step no longer asks for a jump back before the record.

- **Ending.** `walk_progress.py readiness` returns `ending`. The reply prints that text. It includes each held line, one branch per line, with the T# , the short name, and who it waits on. The reply does not say above, listed above, or earlier output. This covers ready, ready-partial, not-ready, the waiting stop, and the stop ending.
- **Run next.** On ready and ready-partial, `Run next:` is first, before any Waiting line. Each ready branch is a code span with only the command. The command is a complete invocation for a new session: each T# on that branch, and the slug when `docs/specs` has more than one slice, for example `/crav1-build-walk orders-api T3`. One slice needs no slug. The next line names the branch and the short task name. A blank line separates branches. The full Next lines stay after that and still name `/crav1-build-tasks` for one task. The walk does not run either command.
- **Own step.** When tasks-ready-to-build is the only reopened step, readiness does not list it as a blocker. The result is ready, ready-partial, or not-ready from the rows. The reply says once that the earlier record is replaced, then the normal record confirm. Another reopened step still forces not-ready. `clear --step` with nothing new is unchanged.
- **Build walk ending.** `/crav1-build-walk` prints the same `Run next:` block. The command is alone in a code span and works in a new session: `/crav1-build-walk T3`, plus the slug when `docs/specs` has more than one slice. The next line names the branch and the short task name. Waiting and Uncommitted follow. The full Next line is last. Another branch whose tasks can start, from readiness `can_start` grouped by build-map branch, is its own Run next entry.
- **Progress file.** Recording a build-walk step commits `build-progress/<branch>.md` after the yes. When the step already commits other files, the progress file is in that same commit. Otherwise it is its own commit. The persisted commit style is used. Nothing is pushed.
- **Task id.** `T27` and `27` are the same id. A label does not print `TT27`.
- **next JSON.** `build_walk.py next --json <file>` takes an object. `tasks` may be `"T27"` or `{"id", "title"}`. The fields are `phase`, `owner`, `branch`, `tasks`, `base`, `pr`, `slug`, `root`, `spec_count`, and `ready_branches`. Bad input returns `{"ok": false, "code", "line"}` and does not traceback.

## 1.149.0 (2026-11-13)

Branch rules stay in the kit and load only when that case applies. A minor release because a typical run no longer reads the cases that do not apply. The rules are unchanged. Each file is named from `SKILL.md` with a load-when line. `/crav1-review-pr` is unchanged: its verdict and hard rules are what a review still reads, and the host differences are already one-line pointers.

- **Ready check.** `/crav1-tasks-ready-to-build` reads work branches, a sub-branch, promotion, a work item, a blocking plan risk, and a next line other than the ready list only when that case is true.
- **Verify.** `/crav1-verify-build-against-spec` reads the branch line, sub-branches, promotion, tick pending, a host-setup task, and one next line only when that case is true.
- **Several features.** `/crav1-build-features` opens the spec-branch skill only on `spec/<slug>`, and the task-branch file only when the recommended name exists nowhere. A dirty tree, a parked spec, a worker status other than `done`, and the picture question are separate files.
- **What we know.** `/crav1-what-do-we-know-about-this` reads the no-slice file only when nothing matches, and the report-writes file only for a `report-` word.
- **Commit.** `/crav1-finalize-commit` reads the commit steps only after `commit` or `commit now`.
- **Questions.** `/crav1-resolve-open-questions` reads the patch, a single named question, a stale point, and the empty-list ending only when that case applies.

## 1.148.0 (2026-11-13)

A spec edit during a tighten-and-plan walk reopens from the first step that owns the changed section. A minor release because resume no longer reopens every later step when the spec hash moves.

- **Section stamps.** `walk-progress.md` records `Section stamps` on each step that covers the spec, and `Question ids` on resolve-open-questions. Resume compares sections. `reopen_line` names what changed and which steps reopen. Say that line once.
- **Requirement sections.** Problem, Goals, Non-goals, Users and journeys, Acceptance criteria, Constraints, Requirements, Scope, Decisions, Background, Context, What the dump says, Trace, Research findings, the text before the first heading, and any other heading reopen tighten-spec, plan-from-spec, review-and-tighten-plan, and the ready check. They do not reopen resolve-open-questions when the question ids are unchanged. An unknown heading uses that same row, so a new constraint still reopens the plan.
- **Questions.** A new, removed, or reworded open question reopens only resolve-open-questions. Ask only the ids in `changed_questions`. The stable key from 1.146.0 (`question_stable_key`) ignores a refreshed commit list, and one close reword of a stored question stays that question. An explicit `Id:` mark still reopens when the words change. An `Answered:` line on the same words, or a new question that is already answered, does not reopen and does not re-ask.
- **No reopen.** `## Match` (including a renamed branch), `## In the code`, a `Synced at:` line, and `## Approval needed` do not reopen a step. When the change is only Match, In the code, Synced at, or an already-answered question, `/crav1-add-to-spec` offers Restamp. `walk_progress.py restamp-covered --root <spec-folder> --yes` refreshes the stamps. `Done` and `Result` stay. A step recorded before this release, with no `Section stamps` line, still uses the 1.137 rule.

## 1.147.0 (2026-11-13)

Install bundles keep a short changelog, and guild routing stays a short map. A minor release because the bundled changelog is a slice of the full file, and `/crav1-help` reads that slice in an install.

- **Bundled changelog.** The repo-root `CHANGELOG.md` stays the full history. Each install's `crav1-docs/CHANGELOG.md` (Cursor drop-in, Cursor plugin, Claude Code) keeps the newest 15 releases and ends with a line to the full file on GitHub. `scripts/slice-changelog.py` writes that slice. Sync and CI fail when a bundled copy is not that slice. `/crav1-update-kit` still reads the newest heading. `/crav1-help` `whats new` still reads the installed version's section. In an install, a version older than those 15 is named from the pointer line and is not fetched.
- **Guild routing.** Each skill note in the `routing` block of `docs/reference/skills.yaml` is a short purpose and handoff. A rule that decides which lane runs, or which command is named and not run, stays in the note. Procedure that already lives on that skill's reference page stays there. `docs/guild-routing.md` stays the lane tables plus those short notes. No skill's behavior changes.
- **Examples.** Customer example names in older notes are replaced with generic ones.

## 1.146.0 (2026-11-13)

A recorded finding stays recorded when the words move a little, and the tighten-and-plan walk no longer opens the ready-to-build skill to write the map. A minor release because the finding card, the walk's first command, and the ready check change.

- **Stable finding.** A spec finding keeps the first-seen `Key:`. A later wording that is the same point is an `Alias:`. Exact words are not asked again. A close reword asks `same recorded finding` or `this is new`. The same P# plus a short topic, such as `approver`, is that id. A different topic is not merged, and two close findings are not merged. An older `walk-progress.md` that has only `Key:` still matches those words.
- **Stable question.** A question recorded on the resolve step keeps an exact key and a stable key. The stable key ignores a refreshed commit list. One close reword of a stored question stays that question. Two close questions are not merged. Say `this is new` to split one. A `Blocks:` line still holds its tasks.
- **Ready check.** `/crav1-tighten-and-plan-ready-to-build` runs `walk_progress.py readiness --root <spec-folder> --write-map` and prints the script's lines. That writes `build-map.md` in the same format as `/crav1-tasks-ready-to-build`. The walk does not open that skill. `/crav1-tasks-ready-to-build` stays the standalone command.
- **One start command.** `walk_progress.py start --root <folder-or-slug>` resolves a spec folder or a slug the way `resolve_spec.py` does, and returns resume and playbook-status together. Add `--playbook <file>` when a playbook was named. The walk's first step uses that command.

## 1.145.0 (2026-11-13)

A batch card shows the findings it applies. A minor release because the reply before that card, and the card text, both change.

- **Findings table.** When one card applies a recommendation to each of several items, the reply prints a findings table immediately before the card. Columns are Id, Issue, Options, and Recommendation. The card is never asked without that table in the same reply. This covers `/crav1-tighten-plan`, `/crav1-tighten-spec` (including a small group answered as a batch), `/crav1-resolve-open-questions` (the question batch, conflict batch, and apply list), `/crav1-add-to-spec` (dump sort, code-change sort, a meeting collapsed onto one card, flagged lines, and images in a mail), `/crav1-suggest-tests-for-code` when the suggestions are one card, the map confirm in `/crav1-existing-to-specs`, the end card of a `/crav1-what-do-we-know-about-this` playbook walk, and the Blocks batch inside `/crav1-tighten-and-plan-ready-to-build`.
- **The card names each item.** The question text is self-contained, for example `P4 tasks miss the 400 path: A add a test`. It still makes sense if the table scrolled away. `yes (Recommended)` still applies every recommendation. Typed changes stay on the free-text answer.
- **No table above.** The card does not say `table above`, `the table recommends`, or `as in the table`. Those phrases are allowed only when the table is in that same reply, and the card still names each item.
- **Script.** `<interpreter> -X utf8 <skill crav1-tighten-plan>/scripts/batch_offer.py --title "Tighten-plan batch" --items <file>` prints the table and the `Card:` line together. The card line is built from the table rows. No rows, and the command prints no card. The rule is [Question cards](docs/reference/question-cards.md).

## 1.144.0 (2026-11-13)

A kit script command names the interpreter and every required argument. A minor release because the command a skill tells the assistant to run changes, and `resolve_spec.py` accepts a missing `--root`.

- **Interpreter.** On Windows the interpreter is `python`. Elsewhere it is `python3`. If that command is missing, or Windows prints the Store alias message `Python was not found`, try `py -3`, then the other name. Set `PYTHONUTF8=1` and pass `-X utf8`. Do not run `python3` alone. The rule is [Running a kit script](docs/reference/running-scripts.md). The silent finder tries `python` first on Windows.
- **Which spec.** The command is `<interpreter> -X utf8 <skill crav1-tasks-ready-to-build>/scripts/resolve_spec.py "<query>" --root docs/specs`. Verify, the ready check, build-tasks, record-approval, and the tighten-and-plan walk use that command. Several matches are listed and the run stops.
- **Default root.** When `--root` is omitted, `resolve_spec.py` uses `docs/specs` from the current directory, which is the repo root. A missing folder is an error that names `--root docs/specs`. Pass the flag anyway. A script that takes one spec folder, such as `walk_progress.py readiness --root <spec-folder>`, still requires that folder. A script that takes the repo root still defaults `--root` to `.`.
- **Other commands.** `build_map.py --recommend` names `docs/specs/<slug>`. `build_walk.py next` and `stack` pass `--json <file>`. `tick_only.py` passes `--root <spec-folder>` and the task id. Approval `show`, `write`, and `add-item` pass their required flags. Notes index and merge-safe migration use `<interpreter> -X utf8`, not `python3` alone.
- **Check.** `scripts/check-script-invocations.py` fails when a documented command hardcodes `python3` for a script with no Windows `python` command beside it, or omits a required flag. It scans skill instructions and current docs. The changelog and the generated reference pages are not scanned.

## 1.143.0 (2026-11-13)

A recorded yes is not a missing yes, and a ready slice's next step is the build walk. A minor release because the Waiting line for a blocked live command changes, and the tighten-and-plan ending names a different command.

- **Permission block.** When a live command, such as a `(Runs live)` task's `apply`, was refused by the coding assistant's own permission check, and the user's yes is already on record, `/crav1-build-tasks` and the live step of `/crav1-build-walk` do not say the yes is missing. Waiting says the yes is on record and the check blocked the command. The offer is only: run that exact command, or allow that one command and rerun. Next is the build step again after the command has run. The lines do not suggest working around the check. A yes that is not on record stays the missing-yes path. `scripts/permission_block.py` distinguishes the two.
- **Ready ending.** When `/crav1-tighten-and-plan-ready-to-build` finishes `ready`, or `ready-partial` with tasks that can start, each Next line recommends `/crav1-build-walk`, with the T number beside the short name and the branch, and names `/crav1-build-tasks` as the alternative for one task without the walk. The same `next_lines` are what `/crav1-tasks-ready-to-build` prints. A `not-ready` result does not recommend the walk. The walk still does not run either command.

## 1.142.0 (2026-11-12)

One guided walk for the build side of a slice. A minor release because `/crav1-build-walk` is a new command, a step skill's Next is replaced while that walk runs, and a live task records the user's own yes.

- **Command.** `/crav1-build-walk` is in the Build lane. It walks one work branch through build (`/crav1-build-tasks`), verify, `/crav1-finalize-commit`, `/crav1-open-pr`, merging the base into the branch, merging the pull request, the tick, and the next task. It opens those skills by file. It does not replace them. A step that writes, pushes, opens, or merges asks `yes` first. It never rebases.
- **One Next.** While one branch is in progress the reply has one `Next:` line, the walk's. A step skill's own Next, such as `/crav1-open-pr` after a build, is not printed. Started from a ready-to-build report, before a branch is chosen, the walk prints one Next per ready branch, with the T number beside the task name.
- **Progress.** One file per work branch, `docs/specs/<slug>/build-progress/<branch>.md`. The file name writes each `/` as `--`. Hashes follow the walk-progress rule: `Content stamp: normalized` ignores line endings, a checkbox, a `(PR n)` or `(done)` note, and a `(live yes: …)` note. A stamp-only merge conflict is settled by `build_walk.py resolve-stamps`. `/crav1-finalize-commit` runs that on the pull path. `/crav1-update-kit` leaves the file alone.
- **Other-owner mode.** When the pull request author or a commit author is someone else, the walk confirms before `switch`. In that mode it never opens a pull request, never merges the base into the branch, and never merges or completes the pull request. It posts one comment per push. It edits the description only on `edit description`. Ticks wait until that pull request is merged.
- **Stacking.** Work may continue on other branches while earlier branches are unmerged. A task that needs code from an unmerged branch is cut from that branch, not from `develop`. The progress file and the report show the merge list, child first, back into the branch it was cut from. A merged or deleted branch is not offered. The offer uses the 1.140.0 helper.
- **Runs live.** A task marked `(Runs live)` gets a script, a dry run (`check`), then the user's yes before the live run. The yes is `(live yes: <name>, <date>)` on the task line. Without that yes the script may be written and the task stays unticked. An unapproved `## Approval needed` item holds the task and the Next line is `/crav1-record-approval` or the draft request. An `Approved:` line does not replace the user's own yes.

## 1.141.0 (2026-11-12)

A named person's yes can be recorded, and it stays recorded. A minor release because the spec gains an Approval needed item, the ready check holds only the tasks that item names, and a new command writes the lasting line.

- **Approval needed.** `## Approval needed` sits beside `## Open questions`. An item names the person (`Person:`), what they approve, and the tasks it holds (`Holds: T4`). It is not a question to fold in. `/crav1-resolve-open-questions` does not walk it and does not remove it.
- **Approved.** The lasting line is `Approved: <person>, <source date>, <source>, "<quote>" (accepted by <recorder> <date>)`. The source date is the quote's date. The last date is the day this run accepted it. No skill removes the line. It is not the data-model stage line.
- **Record it.** `/crav1-record-approval` is command-only. It takes the person, the source, and the quote, shows the line, the constraint, and the tasks it unblocks, and writes only after `accept` in that run. An earlier quote does not count against a later constraint. The kit shows both and asks. Nothing is sent.
- **Where the item comes from.** `/crav1-plan-from-spec`, including the plan step of `/crav1-tighten-and-plan-ready-to-build`, reads a constraint such as `The partner gives a yes before the script is applied.` and adds the item linked to those tasks. When a build finds that yes missing, `/crav1-build-tasks` writes or offers the item instead of only a Waiting line. It does not write `Approved:`.
- **Ready check.** Tasks held by an unapproved item are Waiting on that person. Other tasks still start (`ready-partial`). A matching `Approved:` line clears the hold. A live `apply` still needs the user's own yes in that run, and the task stays unticked until `check` is ok. `task_order.py` lists the same tasks under Waiting on approval.
- **On record.** The build worker treats a named person's yes as on record when a matching `Approved:` line exists, and still when it was said in this chat or an `Answered:` line names it. `Answered:` is unchanged. Resolve still removes an `Answered:` line when it folds that question.
- **Ask.** `/crav1-show-or-ask-open-questions` can draft the approval request as a mail, a chat message, a meeting agenda, or a PR comment. It writes `Asked:` or `Pending:` under the item. It never sends.
- **Stamp.** An edit confined to `## Approval needed` does not reopen a tighten-and-plan step. The section is in neither the spec body nor the questions stamp.

## 1.140.0 (2026-11-12)

The branch offered for a task is the one named on that task's line. A merged or deleted branch is not offered. A minor release because the build card and the build map row change.

- **Task line wins.** A branch written on the task line wins over the plan step's generated `feat/<slug>-<words>` name. On the line, `(map:)` wins, then `(branch:)`, then a `feat/…` name in the sentence, then `committed later on`. `from <base>` after that name is the base, for example `feat/orders-host-setup-scripts from develop`. The plan step is only the fallback when the task line names no branch. Two tasks on one step keep their own branches. When the row is that task-line branch, the note points the other way: `Plan step names feat/orders-one-commit-cleanup-main; built on feat/orders-host-setup-scripts`. A `(map:)` row that is not the branch in the task text still says `Task text names feat/orders-cicd; built on feat/orders-retry`.
- **Merged or deleted.** `--recommend` does not offer a branch whose pull request is recorded merged, whose tip is already in its base or the default branch, or that was checked out here and is now gone locally and on every remote. A branch that only sits on the base, with no commits of its own, is still offered. A name that does not exist yet is offered so it can be created. When no candidate is usable, the offer is a new branch from the stated base. Local git only. No fetch. A task whose own line records the merge stays on that branch in the map. `--recommend` does not print that branch, including for that task, and the `because:` line says it is already merged.
- **The card.** The recommended option is first. The description says where the name came from: `From the task line.`, `From the build map.`, or `New.`. When a name was skipped, that description is one plain line, for example `New, because feat/orders-one-commit-cleanup-main is already merged.` The first line of `--recommend` is the branch. Later lines are `source`, `from`, and `because`. It does not write the map. CRLF and LF are the same text.

## 1.139.0 (2026-11-12)

A merge no longer stops when `walk-progress.md` conflicts only on version lines. A minor release because the pull path now settles those lines and can rewrite the stored hashes.

- **Stamp conflicts.** When `git pull --no-rebase --no-commit` leaves `docs/specs/<slug>/walk-progress.md` conflicted, and every conflict hunk is only a hash line (`Spec version`, `Plan version`, `Tasks version`, `Verify version`, `Spec body`, `Questions version`, `Kept questions`, `Content stamp`, `Key`, or `Playbook:`), `/crav1-finalize-commit` settles it. The same command is used when any kit merge leaves that file conflicted, including merging the base into a branch. `/crav1-update-kit` still does not merge the file.
- **Restamp rule.** The script takes the upstream text. `Done`, `Result`, and every other recorded line stay. A hash line becomes the merged file's normalized hash only when at least one side's recorded hash matches that side's file, and every matching side differs from the merged file only by progress (line endings, and for `spec.md` and `tasks.md` a checkbox or a `(PR n)` or `(done)` mark). Otherwise the upstream hash stays, so a real edit still reopens the steps that edit affects. When every hash on the step is that merged hash, the line `Content stamp: normalized` is written. An older step with no such line still matches a progress-only edit.
- **Mixed conflicts.** A hunk that also touches `Done`, `Result`, a finding, or any other recorded line is not rewritten. The run names the stamp-only hunks and the other hunks and offers `settle stamps`. That rewrites only the stamp hunks and leaves the rest. The merge is not committed, and nothing is pushed.
- **Script.** `walk_progress.py resolve-stamps --root <spec-folder> --yes`. It is line-ending neutral. On a full settle it `git add`s the file into the merge commit this run was already going to make. It does not push.

## 1.138.0 (2026-11-12)

Recording progress no longer reopens the tighten-and-plan walk. A minor release because the stamp, the clear question, and the not-ready wording change.

- **Progress is not content.** A task checkbox (`[ ]` / `[x]`), a `(PR n)` or `(done)` note on that task line, and `(PR n)` or a trailing `merged` on a Match `Branch:` line are ignored when the walk compares `spec.md` and `tasks.md`. CRLF and LF are the same text. The branch name, `(into …)`, `(spec branch)`, `(branch:)`, and `(map:)` still count. A sentence change, or a renamed branch, still reopens the steps that change affects.
- **No clear question.** When those are the only edits, resume stays `keep`. The walk does not ask to clear steps. The next `record` writes `Content stamp: normalized` and refreshes the stored hashes. `Done` and `Result` stay. Resume itself does not rewrite the file.
- **Older stamps.** A step with no `Content stamp` line still has the raw hash from that kit. An unchanged file matches. A progress-only edit matches too: raw bytes, then the other line ending, then one hash-undo over checkbox and `(PR n)` variants (the full set up to 16384, otherwise one line at a time, which covers one tick and added `(PR n)` marks), then `HEAD` once when that blob is the stored stamp. It does not walk git history. Two or more checkbox edits on a task list longer than 14 lines, when those bytes are not `HEAD`, still look like a content change until the next record writes the new line. Old files do not all reopen just because the hash moved.
- **not-ready and can_start.** A hard hit (a reopened step, a jump-back question, Needs verify, an assumption) forces `not-ready` and can still list ready-bucket tasks in `can_start`. Those tasks are not a start. `because` names the reopened steps, or the question when a row holds the whole slice. A checkbox tick plus `(PR n)` on a branch line is not that hit. With open questions that hold some tasks and leave others free, the result stays `ready-partial`.

## 1.137.0 (2026-11-12)

One new open question no longer freezes a slice that was already ready-partial. A minor release because question holds, the spec stamp, the tick path, and spec-folder matching all change.

- **Inferred holds.** A kept-open question with no `Blocks:` line holds the `T#` ids named in its text that exist in `tasks.md`. The hold is shown like a `Blocks:` hold, with a note that it was inferred from the text. The question holds the whole slice only when it names no such task and `resolve-open-questions` has never been recorded. A `T#` that is not in `tasks.md` is ignored.
- **Whole slice mark.** `/crav1-resolve-open-questions` writes `Blocks: whole slice` when a kept-open question holds the whole slice. The walk's Blocks offer before the plan review, and `/crav1-plan-from-spec` when current work blocks the whole slice, write the same mark. The Risk line is `kept open; blocks the whole slice until resolved.` A `Blocks:` line wins over Risk wording, so that line does not keep "do not implement until resolved". The ready check reads `whole slice` and `the whole slice` in any case as that recorded hold of every unfinished task. The line says `Holds the whole slice.` The hold stays after resolve is recorded and through an edit confined to `## Open questions`. A missing `Blocks:` line is unchanged.
- **Per-question keep.** A question that already has a `Blocks:` line, or whose words are on `Kept questions:` from the last resolve record, stays Waiting when `spec.md` changes. A new or unparsed question jumps back to `/crav1-resolve-open-questions` only for the tasks it holds. Other waiting tasks stay waiting.
- **Open questions do not reopen the plan.** `Spec body:` is the spec with `## Open questions` removed. `Questions version:` is that section. An edit confined to that section reopens resolve-open-questions and does not reopen tighten-spec, plan-from-spec, review-and-tighten-plan, or tasks-ready-to-build. A reopened resolve step alone does not force `not-ready` when some tasks can start. The result stays `ready-partial`, with a Waiting line and a Next line for that step. When later steps really are reopened, Next names them: `Next: rerun or clear <steps>.`
- **Tick only.** `/crav1-build-tasks` ticks a recorded-merged or already-verified `[ ]` row whatever the ready-check result, including `not-ready`. It starts no worker and does not re-implement. A `not-ready` result still starts no worker for any other task.
- **Which spec.** After an exact folder, playbook, title, or work-item match, one unique ordered token subsequence also matches (`cc 1.0` matches `cc-process-1-0`). Several matches are listed and the run stops. No match says so and lists the nearest slugs.

## 1.136.0 (2026-11-12)

A merged task that only needs its checkbox ticked no longer loops between verify and the ready check. A minor release because verify's Next line, the ready-check result, and the tick path all change.

- **Stale Next is a ticked task.** The ready check flags `verify.md` as behind when a ticked task is still `Not implemented`, when a `Next:` line names a ticked task, or when a merged task is still `Not implemented`. A merged task whose row is still `[ ]`, and whose only leftover is the tick, is not behind. Merged tasks stay done for later tasks and for `can_start`.
- **Tick pending.** `/crav1-verify-build-against-spec` uses **Implemented, verified, tick pending** when the evidence passed, the row is still `[ ]`, and the pull request is recorded merged. That status is not Not implemented. Next skips tasks the ready check already counts as done and names the first task that can start, one line per ready branch. The open checkbox stays a Gap. After a passed check the report may offer the tick. That needs a yes, on a visible line. The offer is an alternative exit.
- **Tick only.** `/crav1-build-tasks` for a recorded-merged or already-verified unticked row ticks `[x]` in `tasks.md`, starts no worker, and does not re-implement. That is allowed when the ready check is `ready` or `ready-partial`, including when the task is already done for `can_start`. It is not a way around a real `not-ready` blocker.
- **verify.md does not reopen the ready check.** `verify` stays in the files the ready check records, and it is no longer a change that reopens that step. A verify-only edit does not force `not-ready`. The result stays `ready` or `ready-partial`, and `verify_waiting` is shown when verify is behind. `/crav1-tasks-ready-to-build` only writes `build-map.md`. Only the walk's record or `clear --yes` restamps `walk-progress.md`.
- **Needs tick.** `task_order.py` treats a recorded-merged task as done, so it is not Ready and not Next. It lists that task under Needs tick. A Waits in order line includes the short title.
- **Which spec.** Verify, the ready check, build-tasks, and the tighten-and-plan walk resolve a named spec with one script: exact folder first (`orders 1.0` matches `orders-1-0`), then one unique playbook basename, spec title, or work-item name in `spec.md`. Several matches are listed and the run stops. Verify no longer picks the most recently edited tree.
- **Scripts.** [Running a kit script](docs/reference/running-scripts.md) has a silent Python finder for bash and PowerShell. It tries `python3`, `python`, and `py -3`, and treats the Windows Store message `Python was not found` as not found. Do not use `/tmp` as a portable path. `build_map.py --recommend`, given `tasks.md` or `spec.md`, says a spec folder is required and names the parent folder.

## 1.135.0 (2026-11-11)

A spec finding during the tighten-and-plan walk can jump back to the spec, and a stale verify file is called out at the ready check. A minor release because the walk no longer stops on that finding, and the ready check no longer trusts a Next line that names work already built.

- **Jump back to the spec.** When `/crav1-review-plan` inside `/crav1-tighten-and-plan-ready-to-build` finds a problem that is really a spec defect (the plan requires a named person's yes to stop a prod function app, and the spec names no approver), the walk asks one question card. The recommended option runs `/crav1-tighten-spec` on that finding now. The walk opens `../crav1-tighten-spec/SKILL.md` and follows it, with that skill's own confirms. It then reruns the plan for the parts that finding changed, reviews and tightens the plan, and runs the ready check. It does not pause. The other option keeps the finding as an open point and continues. The same finding is offered once. If it comes back, the walk records an open point and continues. `walk-progress.md` records `- Jump-back:` and `Continue:`. A plan finding that is not a spec defect stays in `/crav1-tighten-plan`.
- **verify.md behind.** The ready check compares `tasks.md` with `verify.md`. `build-map.md` stays the file `/crav1-tasks-ready-to-build` writes, and the walk's ready check still refreshes it. `verify.md` stays with `/crav1-verify-build-against-spec`. The walk never runs that command and never writes `verify.md`. When a task is ticked, or its pull request is recorded merged, and `verify.md` still lists it as not implemented, or the `Next:` line in `verify.md` names a task that is ticked or merged, the check flags `verify.md` as behind. It does not show that Next line. It adds `Waiting: /crav1-verify-build-against-spec orders-api - verify.md is behind tasks.md (T2, T45)`.

## 1.134.0 (2026-11-11)

A skill that runs another kit skill opens that skill's file. Command-only stays on. A minor release because a guided walk and several chaining skills change how they start the next skill.

- **Open the file.** Almost every kit skill has `disable-model-invocation: true`, so it runs when a person types the command. `/crav1-tighten-and-plan-ready-to-build` and the other skills that run a kit skill were trying to start that command. The host refused, and the run stopped. Those skills now name the file from this skill's folder, for example `../crav1-review-architecture/SKILL.md`, and the agent opens it with the file-read tool and follows it. It does not start a slash command or a skill tool. If a start is refused because the skill is command-only, the agent opens the file and continues. That refusal is not a reason to stop the walk.
- **One rule.** The path and the refusal rule live in [Opening another kit skill](docs/reference/open-skill-file.md). The same sibling path is the installed file on Claude Code (`.claude/skills/crav1-<name>/SKILL.md`), the Cursor drop-in (`.cursor/skills/crav1/crav1-<name>/SKILL.md`), and the Cursor plugin (`skills/crav1-<name>/SKILL.md`).
- **Who opens a file.** The walk's locked steps, extras, jump back, and playbook apply. `/crav1-build-features` for the T# loop and branch rules. `/crav1-update-specs-from-changes-and-prs` for each add-to-spec item. `/crav1-read-environment` for a confirmed system, architecture, match, or left-out section. `/crav1-suggest-tests-for-code` for a kept suggestion. Apply's kept items follow add-to-spec's fact rules.
- **Who does not.** `/crav1-fix-bug` still names the lane and does not open that skill. The add-to-spec PR record, merge-safe formats, and picture offer name other skills and do not open them. A `Next:` line is still not a start.
- **Command-only stays.** `disable-model-invocation: true` is unchanged on the step skills.

## 1.133.0 (2026-11-11)

The ready check groups tasks by the branch they will be built on, and the build map shows the task id with the short name. A minor release because both change what a ready check prints and what `build-map.md` contains.

- **By branch.** `/crav1-tasks-ready-to-build` and the tighten-and-plan ready check no longer print one flat list (`Ready now: T2, T45, T5, T6, T27`) and one Next line. Ready tasks and held tasks are grouped by the build-map row. The branch is the name `scripts/build_map.py --recommend` prints, so it matches the map. Branches are ordered by wave, then by the map's row order. Each ready branch gets its own Next line, for example `Next: /crav1-build-tasks T2 T5 T6` (on `feat/orders-api-record`), so those branches can start together. One ready branch is still one line. A held task stays with its branch and its reason: the open question and who has it, or `held, waits on T3`. The walk record is unchanged: `Result: ready-partial`, `ready`, or `not-ready`.
- **Task ids on the map.** 1.128.0 kept task ids out of `build-map.md`. The Tasks field now shows `T#` plus the short name, for example `T5 orders-api: require pipeline 6 as build validation`. A done task keeps the 1.132.0 strike and the pull request, with the id: `~~T5 short name~~ ✓ done ([PR 12](https://github.com/contoso/orders-api/pull/12))`. The ready-check report uses that same `T# short name` wherever it names a task. The map is rewritten on every ready check, so the ids match `tasks.md` and do not go stale. Prose outside the Tasks field still drops a task id, and a removed id still does not leave a dangling `'s`, an empty `()`, a leading comma, or a double space.

## 1.132.0 (2026-11-11)

The ready check can be partly ready, and the build map keeps finished tasks. A minor release because both change what a run records and what `/crav1-build-tasks` will start.

- **ready-partial.** `/crav1-tasks-ready-to-build` and the tighten-and-plan ready check now have a third result, beside `ready` and `not-ready`. When some tasks can start and some are held by an open question, the result is `ready-partial`. The tasks that can start are listed as ready, and the line says where the hold begins (`Ready: T1, T2. Held from T3.`). Held tasks stay under Waiting, each with its question and who has the answer. A task that depends on a held task is held too, through later tasks, with the reason `held, waits on T3`. The walk records `Result: ready-partial`, stamps `Done`, covers the step, and ends. It does not write `not-ready`. Next is `/crav1-build-tasks` for the tasks that can start. A later rerun, after the answers are in the spec, moves the held tasks to ready and can record `ready`. `not-ready` remains when nothing can start. A cycle, a missing task, no plan, Needs verify, an open plan-review warning, a reopened walk step, or a question that is still a jump back also records `not-ready`, because the walk still has that row.
- **Build gate.** `/crav1-build-tasks` and `/crav1-build-features` start the tasks `can_start` lists when the result is `ready` or `ready-partial`. A held task is refused with its reason. The run does not ask to build it anyway. When the result is `not-ready`, no worker starts.
- **Build map.** A ticked task stays in its wave. The row strikes the short name through and marks it done, with the pull request link, or the branch or commit when there is no pull request: `~~short name~~ ✓ done ([PR 12](https://github.com/contoso/orders-api/pull/12))`. The heading counts done tasks apart from the branches that can start. A wave whose every task is done is a `<details>` block (`Wave N done (K tasks)`). The rows stay in the file.
- **First jump on Windows.** [Install](docs/install.md) shows a PowerShell download next to the bash one. In Windows PowerShell 5.1, `curl` is an alias for `Invoke-WebRequest`, so the curl flags fail. On Windows, `python3` is often missing. Use `python` or `py`.
- **Line endings.** The three-way compare treats CRLF and LF as the same text. A local file that matches the old kit apart from line endings is a plain update, not a clash. A real edit on the same lines still clashes. The written file keeps that file's line endings (or `.gitattributes` `eol`, otherwise LF), so the update is not a whole-file line-ending diff. A copied template that matches the old release apart from line endings is still replaced. `fetch` clones with `core.autocrlf=false`.

## 1.131.0 (2026-11-11)

Update the installed kit from a published release, on the branch you are already on. A minor release because `/crav1-update-kit` is a new command.

- **Command.** `/crav1-update-kit`, optional `to vX.Y.Z`. With no version, the target is the latest published release tag. `main`, a branch, a commit, and an open pull request are refused in one line.
- **This branch only.** Before any write, the command names the branch, says only this branch gets the new kit, and says other branches stay on the old kit until you merge this branch into them. It says merge develop into the branch, and it never rebases. It suggests merging first or switching branch when this branch should not move, and it warns about uncommitted changes. It does not switch branches. It continues only after a yes in this run. An agent's yes does not count.
- **Files.** Kit-owned files are three-way merged against the previous release. Edits that do not overlap are combined. A clash shows both sides; the recommendation keeps the local side. A copied template is replaced only when it still matches the old release byte for byte. Specs, walk-progress, plans, tasks, notes, playbooks, and the build map are left alone, so a paused walk can stay put.
- **Plugin.** A Cursor plugin or a user-scope install is not a commit. The command compares the installed version with the latest release, says how to refresh or recopy, and still offers migration steps.
- **Bootstrap.** Each GitHub release attaches `crav1-update-kit.py` so an install that does not have the command yet can make the first jump. The release notes command attaches it, and `kit-update-asset.yml` attaches it when the release was created without the file. [Install](docs/install.md) has the steps.
- **Migrations.** After the kit files are replaced, version steps for the jump are dry-run and listed. They are written only on a separate yes, and they are not staged into the kit commit.
- **Commit.** One local commit, `Update CRAV1 kit vA to vB`, then stop. The script does not push. A push happens only when the user already asked for it in this run.
- **Version.** The installed version is `version` in `plugin.json`, or the `Kit version:` line in `crav1-docs/reference/workflow.md`.

## 1.130.0 (2026-11-11)

Fixes from a live tighten-and-plan walk. A minor release because a question card's typed answer moves onto the card's own free-text option.

- **The free-text answer.** On a question card, `yes (Recommended)` applies what was shown. Typed changes go on that card's own free-text answer, and the hint lives on that answer, for example `Type your changes, e.g. C1: keep it open`. An item the answer does not mention keeps its recommendation. The rule is [Question cards](docs/reference/question-cards.md).
- **No Edits option.** A batch confirm, a sort, a map, a conflict list, an apply list, a host-setup script, and a pull-request post use that card. They do not add `Edits`, `Change some`, or `Other name` as a choice whose only job is to say "type under Other". Go through them one by one, use an existing branch, stay, and stop stay when they do something different.
- **Branch name.** A typed branch name is that same card's free-text answer, hint `Type a branch name`. A label `Other name` with no branch is asked again.
- **Skipping is a button.** A multi-select of optional items includes a real option for taking none, for example `None, go to plan` on the tighten-and-plan extras card. A choice such as none, skip, or all is a real option. The card does not tell you to type that word.

## 1.129.0 (2026-11-11)

Fixes from a live one-task build and from the build map. A minor release because the branch prompt, a worker status, and the build map change.

- **One card at a time.** The branch question comes first, on its own card. A typed branch name on that card is the answer. There is no second card to collect a name. The permissions question (`continue`, `click`, or `stop`) comes after, on its own card. A missing answer, or an answer that belongs on the other card, is asked again. The run does not guess.
- **A yes is waiting.** When a live change needs a named person's yes that is not on record (host setup, or another approval gate), the worker returns `needs_yes`. The task stays unticked. The run ends with `Waiting: the partner's yes to turn off pipelines 7 and 24.` and `Next` to rerun that task after the yes. `blocked` stays for a real blocker.
- **The build map names the branch.** `/crav1-build-tasks` and the Build prompt offer the branch `scripts/build_map.py --recommend T#` prints, the same name as the map row. The order is `(map:)`, then `(branch:)`, then the plan step's `feat/<slug>-<words>` name, then `committed later on <branch>` when the task is not on a step. On that branch already, no prompt. A `(host setup)` option says the script will live on that branch, and says when the task text names a branch that is cut later. A different pick is written back as `(map: <picked>)` on the task, in the specs repo, and not committed.
- **Shell line endings.** When a build writes a new `.sh` file, the repo has no `*.sh` rule with `eol=lf`, and `core.autocrlf` is true or the host is Windows, the run offers `*.sh text eol=lf` in `.gitattributes`. It does not add the line without a yes.
- **Build map text.** A task id that is removed is replaced with the task's short name, or the phrase is cleaned. The file does not keep a dangling `'s`, an empty `()`, a leading comma, or a double space. The Tasks field is a short name: the `task: T#` title in `work-item.md` when that line exists, otherwise the task text up to the first ` (`, `, in `, or the end of the sentence, at most about 80 characters. Marks and branch prefixes are dropped.
- **Wave heading.** Every wave says how many can start, including one branch: `1 branch, 1 can start now`.
- **A mismatch stays visible.** When a row's branch differs from a branch named in the task text, the row has one line: `Task text names feat/orders-cicd; built on feat/orders-retry`.

## 1.128.0 (2026-11-10)

A build map: how the slice will actually be built, by branch, without task ids. A minor release because `/crav1-tasks-ready-to-build` now writes a file.

- **Build map.** Every run rewrites `docs/specs/<slug>/build-map.md`, next to the plan. The task list is unchanged apart from one line, `Build map: docs/specs/<slug>/build-map.md`. The word `build-map` shows only a short summary (the path and the waves). The same scope as the command follows the word, including a slice such as `cc 1.0`.
- **Grouping.** One branch per numbered step under `## Approach`. A task id in the step, or `(step: 1)` on the task, is the link. `(map: feat/cancel-refund)` puts that task on another branch. Tasks that name the same branch share it. No steps, or steps that name no task, means one branch per task, and the file says so.
- **Waves.** Wave 1 does not wait for another open branch. Later waves open after those. The heading says how many can run together (`3 branches, can run in parallel`, `1 branch`, or `3 branches, 2 can start now` when a question holds some). The `build-map` summary uses that same count. The flowchart is left to right, one subgraph per wave, so the branches in a wave sit side by side. A cycle, or an `(after:)` that names no task, is listed under Blocked.
- **Overlap.** Under a wave, a pair of branches that share a `(spec: …)` requirement, or a backtick path in the task line, gets an `Overlap:` note. The `build-map` summary repeats each note under that wave, one line per pair, in the same words. The ready-check list stays the one pointer line. The note does not block and does not change readiness or waves. A row still has the same six fields, and still no file list.
- **A row.** Six things: a short `feat/<slug>-<words>` branch name, one line on what it delivers, the task titles, the branches it waits for, any open question and who has the answer, and whether it is ready now (`ready`, `waiting on a question`, `waits in order`, or `blocked`). Who uses the 1.127.0 rule. No estimates and no file lists. Task ids stay out of the file.
- **Script.** `scripts/build_map.py` writes the file, reusing the task order and the question blocks. The interpreter is [Running a kit script](docs/reference/running-scripts.md).

## 1.127.0 (2026-11-10)

Fixes from a live tighten-and-plan walk and a live ready check on Windows. A minor release because the ready-check rows, the progress result, and how a kit script is started change.

- **Playbook first.** When a playbook is named, that question comes before any later step, including a read-only check such as readiness. Resume may report status. No step runs until the choice is answered.
- **Waiting who.** Who comes from the question's own "Waiting for" phrase, then the latest Pending or Asked line. When neither names anyone, who is "not named yet", and that task still counts. Example: `Waiting: 8 tasks wait on open questions (the partner, a colleague; 1 not named yet).`
- **Row buckets.** A task that only waits on an earlier real task is `waits-in-order`. A task held by an open question is `waiting`. Only a true blocker is `blocked`.
- **Ready result.** The ready check records `Result: ready` or `Result: not-ready`. Resume treats both as recorded. An older `Result: done` still reads.
- **Shared stamp.** `walk_progress.py ack-stamps --root <spec-folder> --yes` writes one `Acknowledged stamp:` line after a yes. The warning stays quiet for that stamp. A new shared stamp warns again. The warning names the command.
- **Interpreter.** A kit script tries `python3`, then `python`, then `py -3`. The Store alias message `Python was not found` means that command was not found. The rule is [Running a kit script](docs/reference/running-scripts.md). `/crav1-tasks-ready-to-build`, `/crav1-add-to-spec`, `/crav1-update-specs-from-changes-and-prs`, `/crav1-pr-status`, and `/crav1-verify-build-against-spec` point at it.
- **Ready list.** `/crav1-tasks-ready-to-build` and `task_order.py` split Ready, Waiting on a question, Waits in order, and Blocked. The text report and the JSON `waits_in_order` list use that split. A cycle, or an `(after:)` that names no task, stays Blocked.

## 1.126.0 (2026-11-10)

The tighten-and-plan walk can call a slice ready when later tasks only wait their turn, and a kept-open question that already waits on someone else is not a jump back. A minor release because the ready check, the risk wording, and how the walk records a step change.

- **Ready check.** A task that waits on an earlier real task is in order, not a blocker. Ready means the first task can start, the rest wait in order, and nothing else blocks. A cycle, or an `(after:)` that names no task, still blocks. `walk_progress.py readiness --root <spec-folder>` builds the rows from `task_order.py` and `question_blocks.py` and adds the `Reviewed:` warnings. The walk does not hand-build that JSON. `task_order.py --json` uses `T1` style ids.
- **Risk link.** A question with `Blocks: T2, T4` gets the risk line `kept open; blocks T2, T4 until resolved.` Only a question with no `Blocks:` line keeps "do not implement until resolved". A risk matches its question on the question's first sentence, or on `(question: <first words>)`, not on the whole line. The same Blocks tasks named in the risk also match. A risk that uses the phrase and matches no question says why as "no matching question".
- **Waiting.** When resolve-open-questions is already current, an open question is waiting, not a jump back. Who comes from the latest `Asked:` or `Pending:` line. The stop line is `Waiting: <n> tasks wait on open questions (<who>).` Next is `/crav1-show-or-ask-open-questions` when they are not asked yet, or the walk when the answers arrive. A jump back that cannot change anything is not Recommended.
- **Jump back.** It reruns the skill that owns the file, even for a small patch. The walk does not edit `spec.md`, `plan.md`, or `tasks.md`, and it does not write `Reviewed:`. A reopened step with nothing new is `clear --step <id> --yes`. A `nothing-to-do` record does not replace an earlier `done`.
- **Record.** Record each step when it finishes, one step per call. `record` refuses more than one step. Resume warns when two or more steps share a Done stamp. The script stamps the time.
- **Windows.** Kit scripts that print set stdout to UTF-8, and the task order falls back to `->` when that fails.

## 1.125.0 (2026-11-10)

A kept-open question can block no current task, and the tighten-and-plan walk asks the choices it was skipping. A minor release because the ready check, plan leftovers, and the walk's prompts change.

- **`Blocks: none`.** A line under a spec open question, optionally `Blocks: none (later phase)`. It blocks no current task. No `Blocks:` line still means the whole slice, so older specs behave as before. The whole-slice choice stays as no line.
- **Resolve.** When `tasks.md` exists, **None** writes `Blocks: none`. It no longer writes nothing. **The whole slice** still writes no line.
- **Plan.** Once `tasks.md` exists, a leftover that blocks some current tasks gets `Blocks: T#`. A leftover that blocks no current task gets `Blocks: none`, and its Risk line does not say "do not implement until resolved". When current or later is unclear, one short batch asks, not one question at a time.
- **Ready check.** `Blocks: none` blocks no task. Any `Blocks:` line wins over a Risk that says do not implement until resolved, so that wording does not infer a whole-slice block for that question.
- **Walk.** After the plan, and before that step is recorded, list kept-open questions that still have no `Blocks:` line and offer to set them, one by one or as one batch. The progress record shows its line and gets a yes, unless the step's own confirm already covered it. An extra's yes stays that confirm. An already-applied playbook still asks skip (Recommended) or reapply. Optional extras are offered once, after open questions, when the kept-open questions are known, and the walk does not pass that point when an extra applies. Show-or-ask is offered when a question is for someone else.

## 1.124.0 (2026-11-10)

One command to catch the specs up with changed branches and pull requests across the linked repos. A minor release because there is a new skill.

- **Added:** `/crav1-update-specs-from-changes-and-prs`, with `manual-flow` and `auto-flow`. An optional repo name narrows the run to one `docs/system/repos.md` row. It runs `/crav1-add-to-spec` for each item. It is not a new choice on add-to-spec.
- **Scope.** Every row with a URL that is not `proposed`, except the specs repo. Manual flow asks once whether to read that repo's pull request comments this time. Auto flow leaves it out unless the repo is named. Neither flow reads the specs repo's branches.
- **Inventory.** Unmerged branches with commits past `Synced at`, open pull requests including drafts, and pull requests closed since the last sweep, with their conversation and review threads. The first sweep has no earlier closed list. Base branches, Slack, mail, issues, and a new `/crav1-review-pr` are out.
- **Fetch.** Manual flow asks once before a read-only fetch. Auto flow fetches without asking. A repo whose fetch fails is skipped and listed under Waiting. The run continues. Nothing is pushed or deleted.
- **Pace.** Manual flow confirms the inventory, then goes one by one. Small groups are offered when there are more than eight items. A spec change is shown before it is written. Auto flow writes notes and `Synced at` only. Spec changes stay a proposal list.
- **State.** `docs/system/sweep-progress.md` holds the queue, so a stopped run resumes and does not redo a finished item. A pull request whose threads were read gets a `Read: sweep` line. A person's own `Read` line is left alone.
- **Budget.** 20 minutes unless you pass another number. The run will not go past 45. When the time is used it finishes the current item, saves its place, and the next line resumes the same command.
- **Ending.** Proposals first when there are any, then the shared Next, Waiting, and Uncommitted lines. The command does not commit, review, or resolve a question.

## 1.123.0 (2026-11-10)

The tighten-and-plan walk can finish, and a commit during that walk stays on the walk. A minor release because resume, the ready check, tighten-spec's batch, and the commit's next line change.

- **Walk progress.** A later step inside the walk does not reopen earlier steps. Recording a step updates the versions those earlier steps covered. An optional extra the walk itself offers and runs (a security review, research, a data model, show-or-ask, suggest-tests, and the same kind of extra) is recorded with `- Extra:` when it finishes. That record is automatic. The user does not run `cover` first. The extra's spec or plan write does not reopen earlier steps. `cover` stays optional, for a write made outside this walk that you want counted as part of the walk, and it does not name an extra. A hand edit, or `/crav1-add-to-spec` between sessions, reopens only the steps that change affects. A spec change does not reopen the architecture review once a later spec step is recorded. A plan or tasks edit does not reopen the step that wrote the plan from the spec; it reopens the plan review and the ready check. Plan steps follow the same inside-walk rule.
- **Ready check.** A reopened step blocks ready. The check names the step. Jump back and rerun it, or clear it with one line, `nothing new`.
- **Done time.** The progress script stamps each step's `Done` time itself, as a full timestamp.
- **Pause.** Stopping partway is one paused-at line, then Next (this walk, and the step it resumes at), Waiting only when that step is blocked, and Uncommitted. No long pause prose.
- **Tighten a large batch.** More than 8 issues: one line of counts first (issues to fix, open questions, small wording). The full list is not printed up front. Each time, one issue or a small group. One by one is always offered. An issue that only settles an open question goes to `/crav1-resolve-open-questions` as one line, with no menu.
- **Commit.** `/crav1-finalize-commit` makes at most two commits: the drafted commit, and one merge commit. The merge is `git pull --no-rebase --no-commit`, never a rebase and never an automatic merge commit. When the notes index check fails, the index is rebuilt into that merge commit and the message says so. `scripts/nothing_lost.py` is the nothing-lost check. Say nothing was lost only when it reports that.
- **Next after a commit.** An unfinished `walk-progress.md` points Next back at `/crav1-tighten-and-plan-ready-to-build`. On `main` or `master` (any base branch), Next is a push, because `/crav1-open-pr` cannot open a pull request from that branch into itself. On a feature branch, Next is `/crav1-open-pr`. The rule is in `docs/reference/run-ending.md`.

## 1.122.0 (2026-11-09)

A run ends with one next step. A minor release because what a skill prints at the end of a run changes.

Every skill ends with one `Next:` line: the step to run now, and a short reason. `Waiting:` is added only when a step is blocked, one short line each. A commit is not a step. When files changed and are not committed, the run adds `Uncommitted: 3 files; commit with /crav1-finalize-commit when ready.` A step that depends on the next step's result is not listed. Rules that already pick a first step, such as a Conflict line or new information on an existing slice, keep that choice and use this shape. Spark, ideas, and bundle keep their one `Left:` line. The rule is `docs/reference/run-ending.md`. A skill still only names the next step, unless it already runs that step.

## 1.121.1 (2026-11-09)

- A kit Python script that imports a helper no longer writes a `__pycache__/` folder beside that helper. The folder was showing up as untracked in the project, for example next to `playbook_store.py` when `/crav1-tighten-and-plan-ready-to-build` runs.

## 1.121.0 (2026-11-09)

Fixes from the first live `/crav1-model-data` auto run and its `report-data-model-full` export. A minor release because `revise`, the baseline, and the review export change behavior.

- **Added:** `revise` records a new version of a decision, worked example, question, or diagram, including the sources on a decision. It bumps the model revision, keeps the previous text in `history.md`, and sets the item back to proposed (a question stays open). A hand edit of a model file is refused until that change is redone with `revise`. During an open auto run, `revise` stays inside the current correction pass.
- **Changed:** Run the state script with `py -3` on Windows and `python3` elsewhere, and try the other if the first is missing. Content goes through `--input` or `--text-file`. `references/inputs.md` lists every command's fields and an example file. The script reads its own clock. The first auto proposal is a baseline and does not use a correction pass.
- **Changed:** `report-data-model-full` is built from the saved records. One title, each section once, one line when a section is empty, a run-ending line near the top, worked examples in their own section, obligations once, and ISO dates. The PDF carries the same prose. Diagrams are titled by name, wrap so the text stays readable, and a wide diagram gets a landscape page or numbered parts.
- **Fixed:** A history-window claim of can-reconstruct is an open question when the other source's coverage is unknown. Drift flags a recommendation that leans one way on an axis recorded as a tie.
- Older saved models and reviews still read. A model written before the content hashes has no hash section; the next script write records one.

## 1.120.0 (2026-11-09)

A filled playbook is copied into the repo when it is applied, so the team shares it from docs. A minor release because apply now writes a project file.

- The first write of `report-playbook-short` or `report-playbook-full` stays outside the project, in Downloads or else a temp folder. A draft with no filled `Answer:` or `Change:` line is not copied.
- On apply, `/crav1-resolve-open-questions apply <file>` copies a filled playbook to `docs/playbooks/<topic>.md`. The same copy runs at the end of a playbook walk and in step 1 of `/crav1-tighten-and-plan-ready-to-build`. Specs that apply changed link that file. `Answer:` and `Change:` lines still read back from the copy.
- The file name comes from the report subject, lowercase kebab-case (`CC Process 1.0` becomes `cc-process-1-0.md`). The name is shown once before the first copy. After that it stays fixed.
- The same playbook is the `Docs path:` line in the file, or else the one committed file whose title subject matches. Reapply overwrites that file. When the committed file was edited in the repo since `Applied as:`, the diff is shown and overwrite waits for a yes.
- `walk-progress.md` records the `docs/playbooks/` path, not the outside path, so resume works on any machine. The walk also accepts a `docs/playbooks/` path as its playbook argument.
- This write is not a git commit. `/crav1-finalize-commit` still does that.
- Already applied a playbook, then new mail landed in the specs: do not re-walk the playbook. Run `/crav1-tighten-and-plan-ready-to-build` with that playbook. Step 1 is skip or reapply, and reapply writes the `docs/playbooks/` copy when it is missing. The new questions are `/crav1-resolve-open-questions`. A fresh `report-playbook-full` only when the playbook's own decisions change. A playbook applied before 1.120.0 is reapplied to create the copy; answers already in the specs stay as they are.

## 1.119.0 (2026-11-09)

A guided walk from a draft spec through the plan until the tasks are honestly ready to build. A minor release because there is a new skill.

- **Added:** `/crav1-tighten-and-plan-ready-to-build`. One walk, with or without a playbook. It runs the existing architecture review, tighten, open questions, plan, plan review, and ready check. It does not replace those skills. Guided only. It stops at ready and does not start build.
- A playbook, when one is given, is step 1. If this walk already applied that same file, you choose skip or reapply. Otherwise it shows the changes and applies them only on yes, through `/crav1-resolve-open-questions apply`.
- `docs/specs/<slug>/walk-progress.md` records which steps are done, when, and the spec, plan, and tasks version each step covered. On resume, only a step whose covered file changed is reopened. The spec, plan, and tasks stay the source of truth.
- When the ready check is Blocked or Needs verify, the walk names the step for each row and can jump back. Needs verify stays outside the walk. An open plan-review warning is not treated as ready.

## 1.118.0 (2026-11-08)

A data model from the specs, and a review of the saved model. A minor release because there is a new skill and a new report word.

- **Added:** `/crav1-model-data`, with `manual-flow` and `auto-flow`. An optional scope guides discovery. Both flows use one state machine. Selection comes from the project's docs. The existing model is judged against the business need first. Manual flow confirms the business model before physical design. Auto flow shows a budget of 20 minutes and 5 shared correction passes before each run, then keeps every unconfirmed result a proposal. The saved model is `docs/data-model/<model>/`. An approval names the exact stage and revision.
- **Added:** `report-data-model-full` on `/crav1-what-do-we-know-about-this`. It reads the saved model and does not model again. It writes an immutable Markdown review and a PDF with the diagrams drawn. Review comments come back as proposed revisions, not as approval.
- Spec edits, schema, and migration code are offered, not written. There is no watcher between auto runs.

## 1.117.0 (2026-11-06)

A playbook walk stays in words, and a disagreement is worked out before anything is written. A minor release because the walk now asks differently and no longer starts help.

- The walk states each kept decision, open question and conflict in words. Item ids stay in the report. `go to N9` still jumps, and the reply does not repeat the id.
- When the user's words and the record do not match, the walk works out the intended outcome from the known facts and their words, one follow-up at a time, then summarizes and waits for an explicit yes before it writes. The older record does not win by default. An uncertain recollection is not already decided. A missing note is not proof that no decision was made.
- The walk stays on the current item. It does not stitch a route. `/crav1-what-do-we-know-about-this` does not start `/crav1-help`. The standing help rule yields while that skill is running.
- Apply stays the only other skill, at the end on yes, and only for filled confirmed lines. It does not run plan, build, or merge.
- One pass picks the slice. Later reads of that slice, including a read-only pull-request thread, are part of the skill. It does not run `/crav1-pr-status`. A labelled merge trial for an order the report already suggests stays outside the work tree. Quote only a finished run. Never checkout, commit, or push for a trial.
- A step whose command cannot be named yet is incomplete, under Gaps on a full playbook. No guessed range.
- The walk's own prompts, and follow-ups to understand what the user means, do not count against the prompt budget. Headless runs still never walk. A short playbook still does not walk.

## 1.116.0 (2026-11-05)

A guided walk through a playbook report in chat. A minor release because `report-playbook-full` now asks to walk after writing and there is a new report word.

- `report-playbook-full` writes the report as before, then asks *Walk through it now?*. The walk first offers to settle answers that block several steps (`skip` takes them in order), then goes in Steps order, one K, N or C item at a time, each with a short *Why this matters* and the recommendation. Reply `yes`, your own answer, `more` for the full background, or add what you know; jump with `go to N9`.
- Free flow: ask back, push back or change direction mid-walk; only the affected Compose, Merge order and Steps are redrafted, shown and agreed before the walk carries on.
- Each answer is saved into the report as it comes; nothing touches a spec during the walk. At the end, a summary and an offer to run `/crav1-resolve-open-questions apply` on your yes.
- New `report-playbook-walk` resumes an existing playbook report at the first unanswered item. Headless runs never walk; they write the file and say how to resume.

## 1.115.1 (2026-11-05)

- `report-playbook-short` and `report-playbook-full`: Kept, Needs your answer and conflict items are bullet blocks instead of tables, each with its `Change:` (K) or `Answer:` (N, C) line right under it, so there is no separate list of fill-in lines to match up. `/crav1-resolve-open-questions apply` reads the new layout and still reads files filled in with the older table layout.

## 1.115.0 (2026-11-05)

Host settings are built like code. A minor release because plan, build, verify and pr-status gain host setup tasks and a new skill.

- **Added:** `/crav1-host-setup`. Describe a host setting that does not live in the repo (a branch policy or required build, required reviewers, an environment approval, a variable group). It drafts a checked-in `az` or `gh` script under `infra/ado/` or `infra/github/`, with a what and why comment above every command, and generates the manual steps from those comments. You see the commands, their scope and the steps, reply with edits until it is right, then yes. It runs the script's `apply` part, reads the live setting back with its `check` part, and commits the script on a work branch. Headless runs never apply.
- **Added (shared reference):** `crav1-host-setup` `references/host-setup.md`, used by both the ad hoc and the plan route so they write the same script. Pipeline YAML, templates and infrastructure as code stay ordinary code. Service connections and secret values are always manual: the script only checks they exist by name. Host-facing text is kit-neutral.
- **Changed:** `/crav1-plan-from-spec` writes a host setting as its own task marked `(host setup)`. `/crav1-build-tasks` writes its script and runs it only after a yes. `/crav1-verify-build-against-spec` counts it verified only when `check` reads the setting back `ok` from the live host, and never applies. `/crav1-pr-status` marks a point that asked for a host setting `done host` when the setting reads back live. `/crav1-fix-bug` points a missing host setting at `/crav1-host-setup`.

## 1.114.3 (2026-11-05)

- `/crav1-review-pr` re-review: the drafted comment heading in the PR note is always plain `## Comment as drafted, <date>`, with no `(re-review)` suffix. A re-review tag goes only on the `## Kit record` heading.

## 1.114.2 (2026-11-04)

- `/crav1-review-pr`: recording the comment as posted (`comment posted`, `newest comment`, a paste) saves only the posted comment and never adds a `Comment as drafted` section. Drafted comments in the PR note are always in a four-backtick fence, never three.

## 1.114.1 (2026-11-04)

- `/crav1-review-pr` re-review: after a new push or a force-push, every file and line link is read again from the current head commit. A point whose code moved links its new lines; a point whose code is gone is fixed or no longer relevant. Lines are never copied from the earlier review, record or draft. Fixes re-reviews that still linked the old lines.

## 1.114.0 (2026-11-04)

- `/crav1-open-pr` on a branch that already has an open pull request: after the push (your yes, never a force-push) it shows the pull request, its author and the commits added since the description was written, then asks: **update description**, **add as comment**, **push only** or **stop**. On someone else's pull request, **add as comment** comes first. The comment says what was pushed and why and reads like a normal reviewer comment; an updated description keeps the same format and keeps lines a person wrote, listing what changes.
- Before anything is posted you see the exact text: **Reply yes** (or "confirm") to post it as shown, or reply with your edits (for example "drop the second bullet") to get a redraft. Nothing is posted until you say yes.
- Next-step lines in build-tasks, build-features, finalize-commit, verify-build-against-spec and help status name the pull request when the branch has one: `/crav1-open-pr` to push to PR 77 and update its description or comment. Otherwise they still say push and open the PR.

## 1.113.0 (2026-11-04)

- `/crav1-review-pr` shows only the review you can post: the verdict, the paste-ready block, one `Kit record:` line naming the PR note, and the post question. The 7 check lines, findings with lanes, info notes, suggestions, follow-ups and the next step after merge are no longer in the chat; they are saved in the PR note as the kit record.
- Context added in the same message (a mail, a meeting, a workshop plan) shapes the review (what comes first, what is left out, the questions it raises), but the review never mentions it, the kit or the specs. Below the review, after a line, a read-only section shows the kit record and what the context changed. It is also saved next to the PR note as `<date>-pr-<repo>-<n>-context`, linked from the PR note.
- Posting, also to Azure DevOps, only ever takes the review.

## 1.112.0 (2026-11-04)

- Playbook reports (`report-playbook-short`, `report-playbook-full`, still preview) list every **Conflict:** line in the covered specs under **Needs your answer** as C1, C2, …, after the questions: the decided line and the newer quote side by side, a recommended answer and why, a `C<n> Answer:` line, and the Step that records it. The answer step names every N and C it covers; `/crav1-resolve-open-questions <spec>` (or `apply <this file>`) settles the conflicts too.

## 1.111.2 (2026-11-04)

- `/crav1-add-to-spec` code-change branch: the **Write what belongs** section moved word for word into its own references file, read at the same point. No behavior change.

## 1.111.1 (2026-11-04)

- The sort in `/crav1-add-to-spec`, the map in `/crav1-existing-to-specs`, and the apply list and conflict batch in `/crav1-resolve-open-questions` now end with the same plain block: **Reply yes** (or "confirm") to write it as shown; to change something first, reply with your edits (for example "drop 13"); nothing gets committed either way. Wording only; no new behavior.

## 1.111.0 (2026-11-04)

- `/crav1-add-to-spec` writes a mail as text: `mail.md` in the source folder holds `From`, `To`, `Cc`, `Date`, `Subject` (and `Message-ID`) and the body word for word, quoted thread kept. The original mail file stays outside the repo; the README names its file name, date and Message-ID. Images in the mail keep the same per-image choice but become their own files next to the mail text, with a placeholder where each was shown. No mail is edited, split or re-encoded, and the `.gitattributes` question is gone. A pasted mail is written the same way. Mail files already in a project stay as they are.
- `/crav1-resolve-open-questions` also lists every **Conflict:** line after the open questions (no word needed), asks one question per conflict with the decided line and the new quote side by side and a recommendation first, and writes nothing until one confirm. Settling replaces or keeps the decided line, removes the Conflict line and adds a trace. `/crav1-add-to-spec` and the pull step of `/crav1-finalize-commit` name it when they write a Conflict line.

## 1.110.0 (2026-11-02)

- Playbook reports (`report-playbook-short`, `report-playbook-full`, still preview) only list; they no longer take answers in chat. The how-to blocks for **Kept** and **Needs your answer** sit above their tables, the "To change it" column is gone, and every row says `Recorded in Step <n>`. An early answer step runs `/crav1-resolve-open-questions` for the questions. Each item has a plain `Answer:` or `Change:` line, so the file can be filled in later or by people who do not use the kit. Compose is written out as bullets. Order diagrams follow a safe syntax (plain ASCII labels, no quotes or parentheses) so every viewer renders them. Short no longer caps the steps.
- `/crav1-resolve-open-questions apply <file>` reads back a filled-in playbook report. It names what changed in the specs since the report, sorts each answer as new, already settled the same way, or conflicting, asks one question per conflict (the file's answer next to the spec's, who decided each, a recommendation), and writes nothing until you confirm.
- Kit CI parses every mermaid block in templates and test goldens with mermaid 11.4.1.

## 1.109.2 (2026-10-31)

- Playbook reports (`report-playbook-short`, `report-playbook-full`, still preview): under **Kept** and **Needs your answer**, a short block says exactly what to write in chat (`change: K<n> <new decision>`; `yes N1–N<last>` or `N5: <your answer>`), that nothing needs to run first, and that the steps under Steps then write it, with an example. Kept items are numbered K1…, questions N1…. Compose keeps **From** and **To** to short names so the table stays readable. Each step is its own block (title, command in a code block, You should see, Done when); full keeps no cap on steps. Wording and layout only; no new behavior.

## 1.109.1 (2026-10-31)

- Playbook reports (`report-playbook-short`, `report-playbook-full`, still preview) read plainer: the spec, the plan, the tasks instead of file names. Kept decisions can be challenged and changed. Live reads keep out-of-scope items in a last **Out of scope** block. The merge order is marked suggested and can change; rebase is never offered as the kit's way, only named when someone suggested it. Compose includes a separate deploy (such as DEV Bicep) only when the docs describe it. Each step says what to type, what you should see, and when it is done, after a first line asking you to confirm your answers. Wording only; no new behavior.

## 1.109.0 (2026-10-31)

- `/crav1-what-do-we-know-about-this` adds two report words, **preview**: `report-playbook-short` and `report-playbook-full`. A playbook sorts a goal's decisions into **Kept**, **Needs your answer** (a recommended answer and why; `undecided` or `decided by <person>`, never a hand-off) and **Compose**, then lists the kit skills in order with a dependency-order Mermaid diagram. Short has at most 8 steps; full has no cap and adds where it stands, gaps and a second diagram when needed. Answers stay in the report until you confirm; then the named skills write them. Loads only `reports/common.md` and the chosen template; no report word stays free-form. Delivery and live reads follow 1.104.0.

## 1.108.1 (2026-10-30)

A patch with no behavior change.

### Kit

- **Changed (`/crav1-existing-to-specs recheck`):** no longer labelled preview. It has been used on a real repo and is treated as stable. Only labels in the skill, branch, help, reference pages and walkthroughs changed; no steps changed.

## 1.108.0 (2026-10-30)

A gap check of the repos against the specs that already exist. A minor release because it adds behavior.

### Kit

- **Added (`/crav1-existing-to-specs recheck`):** choice words `recheck` / `repos vs specs`. It compares the named repos (or every repo in `docs/system/repos.md`) with the existing specs. You can narrow it to a path, or with `since` to code changed after that repo's `Synced at`. It reports code no spec covers (with the nearest spec) and stale claims (paths under `## In the code` that are gone). It refreshes `## Code with no slice` in `docs/system/landscape.md`: lines still true stay, covered lines come off, new gaps are added, `## Dismissed` is kept. It writes nothing into any spec and never adds an open question. For each gap you can hand it to `/crav1-add-to-spec` after a yes, have it name a skill for a new spec, dismiss it, or leave it. It loads only `branches/recheck/BRANCH.md` (about 1,000 words) and two step references.
- **Added (route):** "Repos vs specs" in `workflow.yaml`, so `/crav1-help next` names recheck. `/crav1-add-to-spec` names it when asked for code not in any spec with no change named.
- **Tests:** `scripts/tests/test_recheck_1108.py`.

## 1.107.0 (2026-10-30)

Branch files load less, and four hand-kept copies are now generated. A minor release because six branches read different files.

### Kit

- **Changed (six branches, load path):** a `BRANCH.md` over 2,000 words now fails `scripts/check-kit-docs.py`. Later steps moved word for word into `branches/<name>/references/`, each left as a one-line pointer: `/crav1-existing-to-specs` repos only (5,237 to 1,766 words) and repos and bundle (2,171 to 1,517), `/crav1-add-to-spec` code change (4,967 to 1,918), meeting (4,324 to 1,775) and dump (2,626 to 1,896), and `/crav1-ado-sync` push tasks (2,286 to 1,563). The rules are unchanged.
- **Changed (guild routing):** `docs/guild-routing.md` is generated by `scripts/gen-skill-docs.py` from the lanes in `skills.yaml` and its new `routing` block, which holds the routing text word for word. The choice-word table now lists every skill's choice words, not a hand-kept subset. CI fails when the page is stale.
- **Changed (templates):** every skill template copy is written from `docs/specs/_template/` and `docs/system/_template/` by the new `scripts/gen-template-copies.py`, which `sync-crav1-plugin.sh` runs first. `scripts/template-copies.tsv` lists the 73 copies. The bundle spec is the base spec plus an insert; the architecture and matched-slice specs are their own files in `scripts/template-overlays/`. `check-template-copies.py` also fails on a stale or unlisted copy.
- **Changed (host copies):** skill files name each other host-neutral (this skill's `path`, or skill `crav1-other`, `path`) instead of a drop-in `.cursor/skills/crav1/…` path plus a plugin sibling path. The `.claude` copy now differs from `.cursor` in 20 files instead of 91, each naming a host-only path (rules, agents, a command line, the help docs folder). `scripts/tests/test_host_copies.py` pins that list.
- **Fixed (repo):** Python bytecode caches are no longer tracked.

## 1.106.0 (2026-10-30)

Skills load less before and during a run. A minor release because the skills read different files.

### Kit

- **Changed (all 38 skills, load path):** each `description` is now trigger text only, at most 60 words. Down from 4,149 words to 1,604 in total, and all of it loads up front for skill matching. The rules stay in each skill's body. `scripts/check-kit-docs.py` fails over 60 words.
- **Changed (`/crav1-help`, load path):** help reads the new generated `reference/index.yaml` first (one entry per skill: lane, starter, page, purpose), then only the `reference/skills/<name>.md` pages the answer needs. It no longer reads `skills.yaml` or `skills.md` whole (`skills.md` only for `list`). It opens `CHANGELOG.md` only for what's new, a release, or a version question, and then only the sections asked for. `scripts/gen-skill-docs.py` writes and checks the index.
- **Changed (routers):** `/crav1-retire-spec` (retire, merge, park and un-park, convert), `/crav1-show-or-ask-open-questions` (show, ask), `/crav1-explain-this-code` (what it does, what and why, teach the language) and `/crav1-glossary` (list, as-file, research, term) route first and read only one `branches/<mode>/BRANCH.md`. Mode sections moved word for word, so the rules are unchanged.
- **Changed (maintainer):** `AGENTS.md` cut from 7,783 to about 560 words: starters, layout, the route in one line each, and edit-then-sync. Per-skill behavior lives in the skills and `skills.yaml`. The 60-word description rule is added to `CONTRIBUTING.md` and `kit-maintainer.mdc`.
- **Tests:** `scripts/tests/test_help_index.py` (index, help load path, description cap) and `scripts/tests/test_routers_1106.py` (each router points at every branch, no mode section left inline).

## 1.105.1 (2026-10-30)

Kit CI runs less. A patch release because no skill behavior changes.

### Kit

- **Changed (CI):** `Drop-in, plugin, Claude sync, and docs checks` runs on push only for `main` and `develop`, as `Kit lint` already did, so a pull request push no longer runs it twice.
- **Changed (CI):** every kit workflow has a `concurrency` group per pull request or branch. A newer push to a pull request cancels the older run. Runs on `main` and `develop` are never cancelled.
- **Unchanged:** no `paths-ignore`. Every workflow checks docs (bundled `crav1-docs`, `skills.yaml`, links, docs-touched), so no docs-only change is safe to skip.

## 1.105.0 (2026-10-29)

`/crav1-glossary` no longer adds open questions to specs. The glossary is definitions only, so a word can no longer block a plan or a build. A minor release because it changes what the skill writes and asks.

### Kit

- **Changed (`/crav1-glossary research`, `/crav1-glossary <term>`):** a term found nowhere no longer becomes `What does <term> mean here?` with a `Pending:` line on a spec, and the skill no longer names `/crav1-show-or-ask-open-questions`. It offers what it may know, labelled `(inference, not in the docs)`, with **Correct** (the row is written as `Source: confirmed in chat (<date>)`) or **Needs research** (the row stays `to be researched`, with an optional research request drafted in the chat, nothing written or sent). Headless and bot runs list the guesses under **Guesses waiting**.
- **Changed (load path):** the not-found rules live in `references/not-found.md`, read only when a term is found nowhere.
- **Unchanged:** docs/ meanings are written right away with a file and line link; web meanings only after a yes; internal-only terms never go to the web; one prompt per run.
- **Tests:** glossary path unit tests (`scripts/tests/test_glossary_paths.py`) in kit CI; the proving-ground glossary replay seeds a spec that uses an unknown word and checks that the spec is untouched.
- **Docs:** the glossary walkthrough, guild routing, `skills.yaml` and regenerated skill pages.

## 1.104.0 (2026-10-29)

`/crav1-what-do-we-know-about-this` gains six report words that write a fixed Markdown report, and load paths become a standing kit rule. A minor release because it adds modes.

### Kit

- **Added (`/crav1-what-do-we-know-about-this report-<type>-<depth>`):** `report-feature-short`, `report-feature-full`, `report-change-short`, `report-change-full`, `report-build-short`, `report-build-full`. feature = what it does, flow, architecture; change = one pull request or branch, its pipelines and discussion; build = ready to build, gaps, and finish order in dependency order. short is one screen; full is every section.
- **Added (load path):** the skill routes first and reads only `reports/common.md` plus the one `reports/<type>-<depth>.md`. No report word stays the free-form answer and opens no report file. Diagrams are Mermaid wherever a picture helps, only those that file lists; C4 always in feature-full, in change-full only when architecture or pipelines matter.
- **Added (reports):** live reads as in the free-form answer, plus read-only sources the host already has; a source that needs a sign-in, a permission, or a missing tool is asked about first (Allow or Skip). `Live read.` and `(inference, not in the docs)` labels. The file goes outside the project, to Downloads when reachable, else a temp folder; the chat always links or attaches it.
- **Changed (`/crav1-what-do-we-know-about-this`):** focus rules moved word for word to `references/focus.md`, read only when a focus is named.
- **Added (maintainer):** **Load paths** is a standing rule in `kit-maintainer.mdc` and `CONTRIBUTING.md` for every skill added or changed.
- **Tests:** routing and progressive-loading unit tests (`scripts/tests/test_report_routing.py`) in kit CI.
- **Docs:** the walkthrough, `skills.yaml`, regenerated skill pages, glossary (**Load path**, **Report word**).

## 1.103.0 (2026-10-29)

Tasks are listed, built and verified in dependency order (the `(after: T#)` graph), not task number. A minor release because it changes what the build skills offer and run.

### Kit

- **Changed (`/crav1-tasks-ready-to-build`):** Ready and Blocked are in **dependency order**: wave by wave through the `(after: …)` graph, lowest number first inside a wave, with an `Order:` line such as `T1 → T2 → T7 → T3 | T6 → T4 → T5`. **Next** is the ready task that unblocks the most other unticked tasks (lowest number on a tie). A task with no `(after: …)` now waits only on the task just before it (inferred), not on every earlier task. Tasks that wait on each other in a loop are blocked, `cycle T3 → T7 → T3 (recorded)`.
- **Added (`scripts/task_order.py`, next to `/crav1-tasks-ready-to-build`):** the sort, standard library only. Prints Ready, Blocked, Order and Next for a `tasks.md`; `--failed T7` lists the tasks downstream of a failed one. The kit repo runs it as `scripts/task-order.py`, with unit and golden tests in CI.
- **Changed (`/crav1-build-tasks`, `/crav1-build-features`):** the opening question lists ready tasks in dependency order with Next as Recommended and says what comes after. A range or all-tasks run queues in dependency order, checks the next task is still ready before each worker, and stops at the first blocked one.
- **Changed (`/crav1-verify-build-against-spec`):** tasks are checked and listed in dependency order (`Tasks — overview (dependency order)`). A task downstream of a failed task keeps its status, and its Verify cell starts with `depends on T7 (failed)`.
- **Changed (`/crav1-plan-from-spec`):** the plan guide asks for `(after: …)` on every task after T1 when the order is not simply T1, T2, T3….
- **Docs:** the ready-to-build walkthrough, data layout, concept glossary (**Dependency order**), `skills.yaml`, regenerated skill pages, and the verify template heading.

## 1.102.0 (2026-10-28)

`/crav1-glossary` names the glossary file as plain text again, and a new `as-file` word writes the list to a file you can open. A minor release because it adds a mode.

### Kit

- **Added (`/crav1-glossary as-file`):** writes the whole list (file order, the `to be researched` rows last, the same count line) to `.crav1/glossary-list.md` at the repo root. The folder's own `.crav1/.gitignore` (`*`) keeps it out of git; it is never committed and the repo's `.gitignore` is not touched. The chat shows the count line and the path. The word is `as-file`, so `/crav1-glossary file` still looks up a term named `file`.
- **Changed (`/crav1-glossary`):** the list ends with `docs/system/glossary.md` as a code span, not a link, and names `/crav1-glossary as-file`.
- **Changed (crav1.mdc, CLAUDE.md):** **Naming local files** drops the 1.101.0 glossary link exception.
- **Docs:** help, the glossary walkthrough, `skills.yaml` and regenerated skill pages.

## 1.101.0 (2026-10-28)

A new skill, `/crav1-glossary`, shows the project glossary, answers one word, and fills the rows still `to be researched`. A minor release because it adds a skill.

### Kit

- **Added (`/crav1-glossary`):** no word shows the whole `docs/system/glossary.md` in the chat in file order (the `to be researched` rows stay last), with a count line and a link to the file; nothing is written and no file is created.
- **Added (`/crav1-glossary research`, `references/research.md`):** fills `to be researched` rows, docs/ first (written right away with a file and line link), then the web for public terms only, after the personal-data and secrets check; a web meaning is shown with its URL and written only after a yes; internal-only terms never go to the web. Found nowhere: an open question with `Pending:` on the spec that uses the word, or a drafted research request.
- **Added (`/crav1-glossary <term>`):** answers one term from its row, or researches it the same way, answers, and offers to add the row (written only on the yes).
- **Changed (crav1.mdc):** **Naming local files** allows the one glossary file link.
- **Changed (add-to-spec `research-stale.md`, `sources-rare.md`, glossary templates, help):** point to `/crav1-glossary` for `to be researched` rows.
- **Docs:** `skills.yaml`, regenerated skill pages, the glossary walkthrough, guild routing, first-run and AGENTS.

## 1.100.0 (2026-10-28)

pr-status names a short `/crav1-add-to-spec pr<n> candidates` command instead of asking a question it can't carry out, and ends with a **Next for you** list that separates what you can do now from what waits on someone. A minor release because pr-status output and add-to-spec choice words change.

### Kit

- **Added (add-to-spec, `references/pr-candidates.md`):** the `pr<n> candidates` choice word reads only the PR record's `to spec` / `to decision` Points not yet `in spec`, takes them in as one fact with the PR note as source (an unmade decision becomes an open question with `Pending: <name>`), and sets `in spec <slug>` on each.
- **Added (pr-status, `references/output.md`):** a **Next for you** section: Now / After <name> answers <point> / Later, built from record lines, with `If <option>:` lines only when the thread names the options.
- **Changed (pr-status, `references/offers.md`):** the spec-candidates question is gone from the closing prompt; add-to-spec joins the do-not-run list in `SKILL.md`.
- **Docs:** `skills.yaml`, regenerated skill pages and the pr-status walkthrough.

## 1.99.1 (2026-10-28)

Kit skills change files with the host's edit tool, so you see a diff, and name local files as code spans with the repo first instead of links. A patch: the same records get written and the same answers come back, only how a file is edited and how its name is printed change.

### Kit

- **Added (crav1.mdc):** an **Editing files** rule: kit files (specs, notes, records) are changed with the host's file edit tool; run only the scripts a skill names, never an inline `python -`, `node -e` or heredoc script that edits files.
- **Added (crav1.mdc):** a **Naming local files** rule: a local file is a code span, repo first when the run touched more than one repo, never a Markdown link, `file://`, `vscode://` or an absolute path. Web links only for things on the host.
- **Changed (add-to-spec, `references/pr-record.md`):** a PR record line is changed with the edit tool, one edit per line, found by reading the note; when the words match two lines, ask instead of guessing.
- **Changed (pr-status):** the closing line is `PR record: <repo>: <path>` as a code span, and `references/output.md` says local files are never links.

## 1.99.0 (2026-10-27)

Implementation code is never written or committed on a base branch any more. Every skill that writes or commits code follows one shared guard, and on `main`, `develop`, the `Merges into` branch or a `release/*` branch it offers a work branch first instead of building there. A minor release because prompts change, Stay is gone on a base, and headless runs stop there.

### Kit

- **Added (create-feature-branch, `references/code-branch.md`):** one definition of base and work branches for every code-writing skill. Base branches: the `Merges into` branch, the default branch, any `main`, `master`, `develop`, `development`, `dev` or `integration` that exists, and every `release/*`. Work branches: `feat/`, `feature/`, `bug/`, `bugfix/`, `fix/`, `hotfix/`, or a branch a spec names. Spec and doc writes, and the specs (source-of-truth) repo, are exempt.
- **Changed (create-feature-branch Build prompt):** on a base branch, at most 4 options and no Stay: **Create `feat/<slug>` from `<into>` (Recommended)**, **Use an existing branch** (the repo's non-base branches, the spec's own first; a pick the spec doesn't list is written to its Match `Branch:` list with `(into …)`), **Other name**, **Stop**. On a branch that is neither (`chore/x`, a detached checkout) Stay is offered in place of Other name. A release fix goes on `fix/<slug>` marked `(into release/x)`. A develop-flow repo now gets the prompt on `develop` even when `main` is the default.
- **Changed (build-tasks):** every path follows the guard; a task whose `(branch: X)` is a base branch is blocked; a headless run on a base stops before any code unless it has the new `new branch` choice word.
- **Added (worker):** `crav1-build-task-agent` checks before its first edit and before every commit, and returns `STATUS: blocked` with `on base branch <b>` even when the parent passed `branch: already-done`.
- **Changed (build-features):** `feat/<slug>` forks from the into branch (Merges into, else default), not `main`; a base task branch is blocked; a dirty base tree is carried onto the new branch instead of being sent to finalize-commit.
- **Added (fix-build-gaps):** a branch check before the first code edit, offering `fix/<slug>` from the into branch. `prompt_budget` 2 → 3; `new branch` choice word.
- **Changed (finalize-commit):** with code staged on a base branch the prompt becomes `Commit on a work branch?` (create `feat/<slug>` from the into branch and commit, an existing branch, another name, stop), also for `commit now`; `new branch` answers it. Docs-only commits on a base are unchanged.
- **Added (crav1.mdc):** a hard rule line for base branches.
- **Fixed (finalize-commit):** a reply that names neither `strip trailers` nor `keep trailers` leaves the trailer-hook question unanswered: it installs no hook and saves nothing, instead of being read as the Recommended `strip trailers`.
- **CI:** `scripts/check-code-branch.py` fails when a code-writing skill file doesn't point to the guard or the Build prompt offers Stay on a base.
- **Docs:** build, verify and commit walkthroughs, glossary, skills reference.

## 1.98.0 (2026-10-27)

`/crav1-open-pr` writes pull request descriptions in sections, with each change linked to its file and lines, instead of one paragraph. `/crav1-pr-status` reads the new sections, and `/crav1-review-pr` checks them point by point. A minor release because open-pr's output and pr-status's and review-pr's reading change.

### Kit

- **Changed (open-pr, format A):** the body is a 1–2 line summary, then `###` sections, each left out when empty: **Changes** (grouped by area when there are 2 or more, at most about 8 bullets; each starts with a link to the file and lines, then a bold short title and what changed and why in 1–3 sentences; the why comes only from the spec, a plan task, a commit message or a code comment, never invented), **Verified** (the check written out: what was run or compared, where, the result and the date), **Risks and rollback**, **Merge order** (replaces the 1.64.0 "also has unmerged branches" tail), **Not in this PR**, **Questions for reviewers** (never invented) and **Work item**, last. Plain Markdown, no tables.
- **Changed (open-pr links):** file and line links are pinned to the head commit, so they keep working after the branch is deleted: Azure DevOps `version=GC<sha>`, GitHub `blob/<sha>/<path>?plain=1#L<a>-L<b>`. Same link forms and encoding as `/crav1-review-pr`, with the commit in place of the branch.
- **Removed (open-pr):** the `## What / why`, `## Spec` and `## Verify` sections. The body has no Spec section and no link to `spec.md`, `plan.md`, `tasks.md`, `verify.md` or anything else under `docs/specs/`; the verify result is written out under Verified.
- **Added (open-pr):** when an infra, pipeline or PROD change states no rollback, the chat says `No rollback stated; add one in your edit if you want it.` The body does not. No new question: `prompt_budget` stays 1.
- **Changed (pr-status):** it also reads the description: `### Merge order` becomes `Order` lines, `### Questions for reviewers` becomes Points tagged `asked; from description <date>`, and `### Not in this PR` is offered as follow-ups (a `follow-up` Point only on a yes). open-pr still writes no PR note and no PR record. A body without those headings is read as before.
- **Changed (review-pr):** a format A description is compared with the diff bullet by bullet: a Changes bullet whose linked lines are not in the diff or do not do what it says, or a change no bullet covers, is the Body fix finding, naming the bullet or file. A choice the bullet's why calls deliberate, at the lines it links, or that Not in this PR names as left out, is not raised as a fault, unless it contradicts something written in the repo.
- **Docs:** commit, ideas and review-pr walkthroughs, the pr-status walkthrough, the PR record tags, and the open-pr and pr-status reference pages.

## 1.97.0 (2026-10-27)

A new `/crav1-pr-status` skill shows where one pull request stands: what is done, what is left and why, and what you owe. Review-pr, add-to-spec, merge-pr and pr-status now share one PR record in the PR note, and `migrate formats` moves the old review follow-ups notes into it. A minor release because review-pr and merge-pr behave differently.

### Kit

- **Added (pr-status):** `/crav1-pr-status pr<n>` (or a URL). It reads every thread, reply and push read-only and gives each point one status: done (only when a commit after the request changed its lines), agreed, declined, open, waiting on <name>, needs <name>. Reviewer mode, or author mode when you opened the pull request; `as reviewer` and `as author` switch. It prints a verdict line with the points waiting on you first, flags threads resolved while the code is unchanged, lists spec or decision candidates, follow-up drafts, dependent pull requests and merge order, drafted replies and a merge-readiness line. `since last` shows only what changed since your last run; `no code` skips the commit check. One prompt at most: a separate yes per thread status change, one for the spec candidates (handed to `/crav1-add-to-spec`), one for the follow-ups (drafts for `/crav1-ado-sync`, never created). Replies are never posted. Output goes to the chat and the PR note.
- **Added (PR threads):** one shared host reference, `crav1-add-to-spec` `references/pr-threads.md`, for reading threads, comments, pushes and who is signed in on Azure DevOps (`az devops invoke` or `az rest`) and GitHub, and for changing one thread's status. **Fixed:** review-pr's re-review named `az repos pr thread list`, which does not exist.
- **Changed (PR record, clean slate):** the PR note holds one shared `## PR record`: `Order`, `Point`, `Read`, `Ready` and `State` lines, one per item, in sorted place, merge-safe (`references/pr-record.md`). Review-pr writes its findings, follow-ups and questions there as Points (`not posted <date>` for a point cut from the posted comment, `done <sha>` on a re-review) and its comment history in the PR note; it no longer writes `review-pr-<n>-follow-ups.md`. Add-to-spec `pr<n> all` adds Points for new threads and `in spec <slug>` when a point is taken. Ado-sync suggest Features reads `follow-up` Points as open items. Help ranks PR points waiting on you.
- **Changed (merge-pr):** it reads the PR record's `Ready` line and stops on `no` unless the turn says `anyway` (host checks still apply); no record means it goes on with a hint. After the merge it sets `State` and `Ready` to merged.
- **Added (migration):** `/crav1-add-to-spec migrate formats` now gives every PR note its PR record (with a `State` line from the newest `State on` mention) and moves each review-pr follow-ups note into its PR note: one Point per bullet, text verbatim; the dated comment sections into the history by date; the intro and bullets under `## Review follow-ups, moved <date>`; front matter in one `Moved from` line; `used_by` and `waiting_for` merged. Then it deletes the old note, rewrites links to it and rebuilds the notes indexes. Idempotent; a nothing-lost check stops on any missing line (`LOST`, exit 2); the dry run prints a unified diff and writes nothing; it writes only on a yes.
- **Docs:** new walkthrough `docs/from-pr-status.md`, reference page, guild routing, glossary, data layout (PR record section and six new marks), install, and optional pr-status steps on the before-pr and outside-pr routes.

### Run the migration (each specs repo with PR notes)

In the agent: `/crav1-add-to-spec migrate formats` (dry run first, then one yes). Without an agent, from the specs repo root:

```text
python3 .cursor/skills/crav1/crav1-add-to-spec/scripts/merge_safe_migrate.py --dry-run
python3 .cursor/skills/crav1/crav1-add-to-spec/scripts/merge_safe_migrate.py
python3 .cursor/skills/crav1/crav1-add-to-spec/scripts/merge_safe_migrate.py --check
```

Claude Code: `.claude/skills/crav1-add-to-spec/scripts/`. Commit the result yourself.

## 1.96.1 (2026-10-27)

`/crav1-help` names its docs folder for each host and no longer opens with a line about which docs it used. A patch: help still reads the same docs and answers the same way.

### Kit

- **Changed (help):** the skill lists its docs folder per host: kit repo `docs/`; Cursor drop-in `.cursor/skills/crav1/crav1-docs/`; Cursor plugin `skills/crav1-docs/` in the plugin folder; Claude Code `.claude/skills/crav1-docs/` (user scope `~/.claude/skills/crav1-docs/`). It reads `<docs folder>/reference/…` directly, never `docs/reference/` at the root of a product repo, and never runs `ls`, `find` or a search for the docs. The Claude Code generator writes the Claude Code folders into the Claude copy (before, it listed the Cursor drop-in as `.claude/skills/crav1-docs/`).
- **Changed (help):** no opening line about which docs were used; the first line is the answer, and short answers stay at 5 lines plus `Source:`.

## 1.96.0 (2026-10-27)

One Asking bullet in crav1.mdc, two new pull request warnings in CI, and the attribution off switches each tool really documents. A minor release because the pull request rules change.

### Kit

- **Changed (crav1.mdc):** the three asking bullets are one **Asking** bullet, same rules, 241 → 236 words.
- **Added (CI):** `scripts/check-patch-behavior.py` warns when a patch release adds a new sentence with never, always, stop or ask to a SKILL.md or a `references/` file: bump the minor version, or say in the pull request body why it is still a patch. A warning, never a failure.
- **Changed (pull request rules):** no `Docs-not-needed:` line when the pull request regenerates docs or changes anything under `docs/` (the `Kit version:` stamp alone does not count). `scripts/check-docs-not-needed.py` warns when it does.
- **Changed (finalize-commit):** `references/added-lines.md` lists the off switch for the seven tools that document one (Cursor, Claude Code, Copilot in VS Code, Aider, Amp, Jules, Devin), each with its source. The other six rely on `strip trailers` and the trailer hook.

## 1.95.1 (2026-10-26)

Seven skills move sections word for word into `references/` so each SKILL.md is under 1,500 words. A patch because no rule changes.

### Kit

- **Moved:** spark-to-spec "Fill every section" rules → `references/spec-rules.md` (1,700 → 1,485 words); review-security design checks → new `references/design-exists.md` (1,648 → 1,483); read-environment look-inside hard rules → `references/look-inside.md` (1,614 → 1,499); review-pr GitHub read and second-section detail → `references/github.md`, `references/second-section.md` (1,563 → 1,481); finalize-commit choice words → `references/choice-words.md` (1,554 → 1,442); merge-pr GitHub pass table → `references/github.md` (1,547 → 1,381); retire-spec convert to note → `references/convert-to-note.md` (1,506 → 1,366). Each SKILL.md keeps a one-line pointer.

## 1.95.0 (2026-10-26)

Prompts at named stops now count, help answers are short, review-pr runs a fixed check list, and a new route covers review, fix, then open a pull request. A minor release because it changes behavior.

### Kit

- **Changed (crav1.mdc):** only a prompt for a value the user left out is outside a skill's prompt budget. A prompt at a stop the skill names now counts. Budgets raised to the real worst case: finalize-commit 1 → 3, review-pr 1 → 2, build-tasks 1 → 4, build-features 2 → 3, verify-build-against-spec 0 → 3.
- **Changed (help):** a skill, route, concept or free-form answer is at most 5 lines plus `Source:`. An action question gets one `Run /crav1-<skill> …` line with the reason, never a quote of the skill page.
- **Added (review-pr):** `references/checklist.md`, 7 checks shown one line each on every run, even when clean: spec and plan match, tests, secrets, infrastructure access per environment, environment parity, spec wording a bug touches, merge order.
- **Added (workflow):** the `before-pr` route: `/crav1-review-pr branch` → the lane each finding names (optional) → `/crav1-finalize-commit` → `/crav1-open-pr`.

## 1.94.0 (2026-10-26)

finalize-commit and the trailer hook strip a researched list of tool trailers, and keep everything else. A minor release because it changes which lines are stripped.

### Kit

- **Changed (finalize-commit, trailer hook):** the known tool trailers now cover Cursor, Claude Code / Anthropic (including `Claude-Session:`), GitHub Copilot, Aider, OpenAI Codex, Gemini, Jules, Devin, Windsurf / Codeium, Amazon Q, Cline, Sourcegraph Amp (including `Amp-Thread-ID:`) and JetBrains AI. Matching is on the tool's email or bot account, never on a first name, so a person called Claude stays.
- **Kept:** `Signed-off-by`, a real person's `Co-authored-by`, the work-item mention and any other line not in the list. A missed tool is added later.
- **Added (finalize-commit):** `references/tool-trailers.md`, the readable list; the hook holds the same list as patterns.
- **Fixed (finalize-commit):** `added-lines.md` no longer says the message is "exactly the draft, nothing more" while also keeping added lines.

## 1.93.1 (2026-10-26)

Three fixes. A patch release: no skill behavior changes.

### Kit

- **Fixed (help):** kit doc paths are written relative to the docs folder (`reference/workflow.yaml`, `concepts/…`, `README.md`), so an install no longer looks for `crav1-docs/docs/reference/…` first.
- **Fixed (Claude Code copy):** finalize-commit's product-files line no longer shows a `Cursor:` clause with `.claude/rules/…` paths. `sync-crav1-claude.py` drops that duplicate for the two-file form too.
- **CI:** `check-kit-docs.py` fails when any `workflow.md` `Kit version:` stamp differs from `plugin.json`. The stamp is now regenerated in the release commit.

## 1.93.0 (2026-10-26)

One shared asking rule, and a prompt budget per skill. A minor release because it changes how every skill counts its questions.

### Kit

- **Added (crav1.mdc):** the asking rule. A prompt is one turn that waits for the user and may hold several questions. A question has at most 4 options; a fifth goes under Other. Use the questions tool when it is available. A skill's prompt budget, the most prompts in one run with the closing yes included, is its `prompt_budget` in `skills.yaml`. A prompt for a value the user left out, or at a stop its skill names, is outside the budget.
- **Added (skills.yaml):** `prompt_budget` for every skill, taken from what each skill says today. Each skill page shows it under Prompts. `gen-skill-docs.py` fails when one is missing.
- **Changed (spark-to-spec):** "at most 7 clarifying questions" and "ask at most twice" no longer clash. The 7 questions go in one prompt; the budget is 3 prompts (the grouped prompt, the branch prompt alone only when the reply skipped it, and the Azure Repos work-item offer).
- **Removed (21 skills):** asking text the shared rule now covers: the per-skill `(Recommended)` paragraph, "use the questions tool when it is available", "at most 4 options per question", and the repeated Ask less sentence in read-environment and map-pipeline-environments. No other behavior changes.

## 1.92.0 (2026-10-26)

finalize-commit drops the 1.90.7 no `--trailer` line. A minor release because it changes a skill rule.

### Kit

- **Removed (finalize-commit):** the 1.90.7 rule "Never add `--trailer` to a `git commit` command". Cursor's agent adds that option on its own whatever the skill says, and the commit-msg hook and the after-commit check already strip tool trailers, so the line changed nothing.
- **Docs:** the commit page no longer mentions it.

## 1.91.0 (2026-10-26)

finalize-commit: restore commits in the same run, real co-authors stay, and the hook commit adds only its own files. A minor release because it changes behavior.

### Kit

- **Changed (finalize-commit):** after `restore` in the nothing-lost check, the restored lines go into this run's draft and commit with the one confirm at the end, as before 1.90.5. The 1.90.5 stop is removed.
- **Fixed (finalize-commit):** the amend that strips added lines removes only the known tool trailers from the hook's list (Cursor, Claude Code, Anthropic). A real person's `Co-authored-by` line stays.
- **Fixed (finalize-commit):** after `strip trailers`, only `.githooks/commit-msg` and the project `trailer-hook` rule are added by path to the commit, never other unstaged files.
- **Docs:** `skills.yaml` now covers the 1.90.5 changes it missed: the style question at most once per run, spark-to-spec's grouped prompt and no auto-run on a bare `yes`, and resolve-open-questions ending with the still-open titles.
- **Note:** 1.90.5 and 1.90.6 carried behavior changes and should have been minor releases.

## 1.90.7 (2026-10-25)

finalize-commit never adds its own trailer.

### Kit

- **Fixed (finalize-commit):** the skill never adds `--trailer` to a `git commit` command. The trailer hook stays as a backup.

## 1.90.6 (2026-10-25)

The trailer hook reaches teammates.

### Kit

- **Fixed (finalize-commit):** after `strip trailers`, the commit it makes includes `.githooks/commit-msg` and the project `trailer-hook` rule, so teammates get the hook when they pull. With `copy` or `stop` the two files are left ready to commit.

## 1.90.5 (2026-10-25)

Question budgets: fewer repeated and follow-on questions.

### Kit

- **Fixed (finalize-commit):** the commit style question is asked at most once per run, and after `restore` in the nothing-lost check the run stops instead of drafting a commit.
- **Fixed (resolve-open-questions):** a run that names one question (`Q2`, `orders Q3`, or matching words) stops after that answer and does not ask the next one.
- **Fixed (spark-to-spec):** the clarifying questions and the branch choice are one prompt, the branch is asked again alone only when the reply skipped it, and the closing decisions are a list, not a question.

## 1.90.4 (2026-10-25)

`/crav1-what-do-we-know-about-this` gives one paste-ready `ask research` line per matching open question.

### Kit

- **Fixed (what-do-we-know-about-this):** a gap matching several open questions ends with one `Next: /crav1-show-or-ask-open-questions ask research <the question's own words>` line per matching question, never one line for several.

## 1.90.3 (2026-10-25)

Ask research and the finalize-commit plain-text prompt no longer trip agents up.

### Kit

- **Fixed (show-or-ask-open-questions):** `ask research` writes the `Pending: drafted <date> for <who>, research.` mark without asking: no confirm, no yes/no, no `Asked?` question. The hard rules say so too.
- **Fixed (finalize-commit):** without a questions tool, the choices are numbered lists, one per question, ending with `Reply with choice words in one line, e.g. commit once strip trailers.`

## 1.90.2 (2026-10-25)

`/crav1-finalize-commit` stops re-asking about a merge whose dropped lines were restored.

### Kit

- **Fixed (finalize-commit):** the nothing-lost check counts a line either side of an unpushed merge added as kept when it is in the merge, in `HEAD` or in the working tree. A line restored in a later commit, with the merge still unpushed, is no longer reported again on every run.

## 1.90.1 (2026-10-25)

`/crav1-finalize-commit` lets hooks run when it strips added lines.

### Kit

- **Fixed (finalize-commit):** stripping added lines amends with `git commit --amend` without `--no-verify`, so the 1.90.0 trailer hook (`.githooks/commit-msg`) and other repo hooks run on the amend. If a hook fails the amend, the skill shows the error and stops; it never retries with `--no-verify`.

## 1.90.0 (2026-10-25)

`/crav1-finalize-commit` offers a shared hook that strips tool trailers.

### Kit

- **Added (finalize-commit):** once per repo, the existing single prompt adds "Strip tool trailers on every commit for this repo?" (`strip trailers` / `keep trailers`). The answer is saved in a `trailer-hook` rule next to the style rule, so it is not asked again. `strip trailers` writes a committed `.githooks/commit-msg` (POSIX sh) and runs `git config core.hooksPath .githooks`. A teammate whose repo has the hook but not the config gets that line on their first run, with no question.
- **Hook:** removes only the known tool trailers from Cursor, Claude Code and Anthropic. Human `Co-authored-by` lines and the work-item mention stay. The hook file is the single list of known trailers; `references/added-lines.md` points to it.
- **Scripts:** the Claude Code generator maps the `trailer-hook` rule to `.claude/rules/trailer-hook.md`.
- **Docs:** skills reference and the commit walkthrough say so.

## 1.89.0 (2026-10-25)

`/crav1-finalize-commit` never asks before the draft.

### Kit

- **Changed (finalize-commit):** the order line no longer shows a style menu first. With no saved style rule it drafts in the recommended style, shows the Summary and Description, then asks one prompt: commit / copy / change / stop, plus CRAV1 style or git log. A different style answer redrafts before anything is committed. Fixes the contradiction with "no opening question" (1.83.0).
- **Docs:** the finalize-commit skills reference says so.

## 1.88.0 (2026-10-23)

`/crav1-tasks-ready-to-build` is command-only.

### Kit

- **Changed (tasks-ready-to-build):** `disable-model-invocation: true`. It runs only when you type `/crav1-tasks-ready-to-build`; the agent no longer starts it from a plain question, and its description no longer loads in every chat. `/crav1-help` stays model-invocable, so kit questions still route to it.
- **Rules:** `crav1.mdc` (and the Claude Code copy) says the command is command-only and to name it for a plain question about ready tasks.
- **Docs:** skills reference, the tasks-ready-to-build walkthrough and guild routing say so.

## 1.87.0 (2026-10-23)

`/crav1-plan-from-spec`: kept-open questions become Risk entries without asking.

### Kit

- **Changed (plan-from-spec):** each kept-open question that does not block a first demo becomes its own entry under `## Risks` in `plan.md`, with "do not implement until resolved". The skill does not ask whether to park, keep, or answer it, and does not answer it silently; answering stays with `/crav1-resolve-open-questions`. It picks any `Blocks: T#` lines itself. The recap lists each parked question.
- **Docs:** skills reference and the spec-to-plan walkthrough say so.

## 1.86.5 (2026-10-23)

`/crav1-what-do-we-know-about-this` and `/crav1-map-pipeline-environments`: SKILL.md slimmed with pure moves. No rule changed.

### Kit

- **Moved (what-do-we-know-about-this):** the answer sections (Verdict through Source, **Unexplained**, the guess label, the open-question `Next:` line, the Skip line) to `references/answer.md`, word for word; the five live-read pointers are one list.
- **Moved (map-pipeline-environments):** the start questions to `references/start.md` and the per-section question options to `references/sections.md`, word for word.
- **Words read:** what-do-we-know-about-this `SKILL.md` 1,895 to 1,426; map-pipeline-environments `SKILL.md` 1,851 to 1,452.

## 1.86.4 (2026-10-23)

`/crav1-plan-from-spec`: SKILL.md slimmed with a pure move and dedupes. No rule changed.

### Kit

- **Moved:** the `tasks.md` format and rules, **Blocks lines**, and the **Left as committed** line format to `references/write.md`, word for word. SKILL.md keeps pointers and the one-exception note for `Blocks:` lines.
- **Deduped:** hard rules no longer repeat no-test-code, no linter install, no Build without a linter, and no rebuild or left-piece task (each stated in the body).
- **Words read:** plan-from-spec `SKILL.md` 1,736 to 1,344; new `references/write.md` 453, read before writing tasks.

## 1.86.3 (2026-10-23)

`/crav1-open-pr` and `/crav1-review-pr`: SKILL.md slimmed with pure moves and dedupes. No rule changed.

### Kit

- **Added:** shared `crav1-open-pr` `references/host.md` (GitHub `gh` and Azure DevOps `az` order and the `gh` rule), read by both skills. Each skill keeps its own `references/azure-devops.md`.
- **Moved (open-pr):** the base-branch steps to `references/base.md` (SKILL.md points at `crav1-add-to-spec` `references/branches.md` "Base branch and Merges into" for the into-branch order), **Open only** to `references/open-only.md`, the host section to the shared `references/host.md`; the duplicate branches.md path parenthetical is gone.
- **Moved (review-pr):** the choice words to `references/choice-words.md`, the first-section finding format to `references/first-section.md` ("Finding format"), the host section to the shared host reference.
- **Deduped (review-pr):** the hard rules no longer repeat "named PR only", "not the newest" and "no merge" (stated in the body); the secret rule is stated once. Version tags dropped from headings (and the matching reference headings).
- **Words read:** open-pr `SKILL.md` 1,744 to 1,295; review-pr `SKILL.md` 1,836 to 1,520.

## 1.86.2 (2026-10-23)

`/crav1-help`: SKILL.md slimmed with a pure move. No rule changed.

### Kit

- **Moved:** modes 2 to 5 (a skill name, "next" or a situation, a concept, list or one lane) and the **Neither** sources case to `references/modes.md`, word for word. SKILL.md keeps each mode's trigger and a pointer.
- **Words read:** help `SKILL.md` 1,713 to 1,096; `references/modes.md` 414 to 1,152, read only for those modes.

## 1.86.1 (2026-10-23)

`/crav1-tighten-plan`: SKILL.md slimmed with a pure move. No rule changed.

### Kit

- **Moved:** `## Resolution catalog (per plan issue)` table to `references/catalog.md`, word for word. SKILL.md keeps a pointer naming every resolution id and the no-`apply-notes` rule.
- **Words read:** tighten-plan `SKILL.md` 1,672 to 1,186; new `references/catalog.md` 525, read when building a `P#`'s options.

## 1.86.0 (2026-10-23)

Match `Branch:` lists are merge-safe. **After updating, run `/crav1-add-to-spec migrate formats` once more in each product repo** (or `merge_safe_migrate.py --dry-run`, then without it).

### Kit

- **Changed:** a spec's Match `Branch:` list is one line per branch, `- Branch: [<repo> ]<branch>` plus its markers (`(into …)`, `(spec branch)`, `(PR <n>)`), never `; `-joined. A new branch goes in sorted place (repo, then branch; no repo sorts first), and a marker is written only on that branch's own line. Writers: add-to-spec code change and the branches sweep, tighten-spec, open-pr, create-feature-branch. Readers (review-pr base lookup and the rest) still read an old joined line as its entries.
- **Changed:** `/crav1-finalize-commit` pull path: `Branch:` lines only one side has are kept in sorted place; the same branch on both sides is one line with both sides' markers; an old joined line whose entries all survive as lines is not lost.
- **Added:** `merge_safe_migrate.py` (and `migrate formats`) splits `; `-joined `Branch:` lists into sorted lines, markers kept, nothing lost, idempotent; selftest extended.
- **Docs:** `references/merge-safe.md`, `references/branches.md`, data layout, marks reference, skills reference, glossary, install and walkthroughs.
- **Proving ground:** D-series and B09 checks for one `Branch:` line per branch and the split.

## 1.85.0 (2026-10-23)

`/crav1-refresh-system-notes`: slimmer, rare cases in `references/`, no flat-notes nag.

### Kit

- **Removed:** the **Notes month folders** section. The command no longer looks for notes flat in `docs/notes/` or names `notes_index.py migrate-dry-run` / `migrate`. Old flat notes are still read; the move stays available by hand (`notes_index.py` is unchanged, it also builds the indexes).
- **Moved:** **Pointed at a research note** to `references/research-note.md` and **From /crav1-read-environment** to `references/handoff-read-environment.md`, with short pointers. Same rules.
- **Changed:** `Synced at` is said once and points at `crav1-add-to-spec` `references/merge-safe.md` for format and sorted place; one example; `Do not commit` only in **Stop**.
- **Docs:** walkthrough, skills reference, data layout and add-to-spec notes reference no longer say the refresh names the migration.
- **Words read:** refresh-system-notes `SKILL.md` 1,749 to 1,120.

## 1.84.0 (2026-10-23)

Merge-safe formats, so two people's kit runs rarely conflict. **After updating, run `/crav1-add-to-spec migrate formats` once in each product repo** (or `python3 <skills>/crav1-add-to-spec/scripts/merge_safe_migrate.py --dry-run`, then without `--dry-run`). See [install.md](docs/install.md#keeping-the-kit-updated).

### Kit

- **Changed:** `Synced at` is one line per repo and branch. In `spec.md`: `Synced at: <repo> <branch>@<short sha>, <date>`, no more `; `-joined entries. In `docs/system/repos.md`: the table's `Synced at` column is gone; a `## Synced at` section after the table holds `- <repo> <branch>@<short sha>, <date>` lines. A read replaces only its own line. Every writer (spark, ideas, bundle and its slice agent, existing-to-specs, add-to-spec code change and `branches`, refresh-system-notes, tighten-spec `mark-dropped`) and reader uses the new form.
- **Changed:** open questions are `- ` bullets found by their words. `Q#` is a display number only, never written; resolve-open-questions maps a `Q#: letter` answer to the question's words before it patches.
- **Changed:** fixed insert order. A new `Synced at` line (repo, then branch), open question (its words), `**New:**` line (date, then text) or glossary row (term) goes before the first existing one that sorts after it, not at the end. Appending always hits the same spot, so two people's additions collide; sorted places almost never do. Existing lines are never reordered.
- **Added:** `crav1-add-to-spec` `references/merge-safe.md` (the rules), `scripts/merge_safe_migrate.py` and the `migrate formats` choice word. The migration rewrites every spec and `repos.md` at once, keeps every line and entry, checks nothing was lost before writing (a file that would lose anything is left alone), keeps CRLF, and a second run changes nothing. `--selftest` runs in CI.
- **Changed:** `/crav1-finalize-commit` pull path: newest `Synced at` per repo and branch; sorted-place lines are merged into their place; the same open question on both sides is one question with both sides' marks. An old `; `-joined line whose entries all survive as lines is not counted as lost.
- **Docs:** repos template (all copies), data layout (new **Merge-safe formats** section), marks reference, skills reference, glossary, install, AGENTS.md and the walkthroughs.
- **Proving ground:** checks for per-branch `Synced at`, word-matched questions and the migration (idempotent, nothing lost).

## 1.83.0 (2026-10-23)

`/crav1-finalize-commit`: no opening question. It always drafts, then offers commit / copy / change / stop.

### Kit

- **Removed:** the commit-or-message opening question (1.56.0). Every run drafts the Summary and Description first; the first question is the commit / copy / change / stop choice (with the style question in the same call when style is not settled).
- **Kept:** `message only` as a choice word, now meaning draft and show with no commit, the same as `copy`. `commit` and `commit now` work as before.
- **Changed:** a headless or bot run with no choice word drafts and ends as `copy` instead of stopping with `Missing choice`.
- **Docs:** skills reference, workflow route 15 and `from-commit.md` (the paste-only example is `/crav1-finalize-commit message only`).
- **Proving ground:** A13 checks that the first question is the post-draft choice and that no opening question is asked.
- **Words read:** finalize-commit `SKILL.md` 1,499 to 1,429.

## 1.82.0 (2026-10-23)

`/crav1-finalize-commit`: the committed message is exactly what the skill drafted. Any trailer or line it did not write is stripped, not only Cursor's.

### Kit

- **Changed:** the Cursor attribution step is now **Added lines**. After the commit, any line the draft did not have is stripped once by amend when HEAD is ours and unpushed: Cursor's `Co-authored-by` / `Made-with`, Claude Code's `Generated with Claude Code` and `Co-Authored-By: Claude <noreply@anthropic.com>`, and any other `Co-authored-by`, `Signed-off-by` or tool line. The check compares against the draft, not a tool list. A trailer that comes back after one strip stops the run and names the tool's setting; there is no `keep` option any more. The work-item mention stays.
- **Renamed:** `references/attribution.md` to `references/added-lines.md`; `crav1-build-tasks` one-task `run.md`, `work-item-mention.md`, the skills reference, `from-commit.md`, `from-ideas.md` and `AGENTS.md` use the new wording.
- **Proving ground:** A13 gains a step where a Claude Code `Co-Authored-By` trailer is removed.
- **Words read:** finalize-commit `SKILL.md` 1,485 to 1,499; `references/added-lines.md` 315 (was `attribution.md`, 250).

## 1.81.2 (2026-10-23)

`/crav1-finalize-commit`: SKILL.md slimmed with moves and dedupes only. No rule changed.

### Kit

- **Moved:** `## Cursor attribution` to `references/attribution.md` and `## When they pick change` to `references/change.md`, word for word. SKILL.md keeps a short pointer for each and the attribution hard rule.
- **Deduped:** never push now sits in step 5a and the hard rules only (the hard rules also name never rebase); the choices-after-wording rule is stated once plus the hard rules; the push/PR sentence that repeated step 7 is gone; the duplicate plugin-path parentheticals are gone. Commit steps renumbered (pull check is 5a, attribution is 6).
- **Fixed:** leftover 1.56 wording (the self-wrapping line, the paste-only self-reference); the draft step links `branches/message-only/BRANCH.md` directly.
- **Pointer:** `crav1-build-tasks` one-task `run.md` now names `references/attribution.md`.
- **Words read:** finalize-commit `SKILL.md` 1,901 to 1,485; new `references/attribution.md` 250 and `references/change.md` 150, read only on that path.

## 1.81.1 (2026-10-23)

`/crav1-finalize-commit`: `pull.md` moved into `references/`. Pure move; no rule changed.

### Kit

- **Moved:** `crav1-finalize-commit/pull.md` to `crav1-finalize-commit/references/pull.md`, word for word; the SKILL.md pointer (step 6a) now names `references/pull.md`. A skill may now get a new `references/` folder when it follows the established pattern.
- **Scanned:** every other skill root. No other reference-type file sat outside `references/`; `branches/`, `assets/`, `scripts/` and the `crav1-docs/` tree stay as they are.
- **Words read:** unchanged (finalize-commit `SKILL.md` 1,901; `references/pull.md` 489).

## 1.81.0 (2026-10-23)

`/crav1-finalize-commit`: fetch after the commit, pull with a merge when behind, and never lose a line in a merge.

### Kit

- **Fetch after the commit.** When the branch is behind its upstream, the pull path runs `git pull --no-rebase` (never a rebase). Conflicts in specs, `docs/system/*.md` and notes are resolved by rule: both sides' added lines kept, ours first; one `Synced at` entry per branch, the newest; note indexes rebuilt with `notes_index.py`, never merged. Code file conflicts stay with the user.
- **Nothing-lost check.** Before the merge commit, every line either side added (against the merge base, CR at line ends ignored) must still be there, or nothing is committed. When not behind, the same check runs on every unpushed merge, so a merge resolved by hand that dropped one side's lines is listed, with restore / show me / stop. Never amends or rewrites the merge.
- **One question, only for a real disagreement:** keep both (a `**Conflict:**` line) / mine / theirs / stop. A headless run writes the `**Conflict:**` line.
- **`pull`.** `/crav1-finalize-commit pull` runs the pull path with no commit first; with uncommitted changes it stops and names `commit`.
- **Never pushes.** Ends with `Ready to push.`
- New `crav1-finalize-commit/pull.md` at the skill root (no new folder), read after a commit and on `pull`.
- **Words read:** finalize-commit `SKILL.md` 1,815 to 1,901 (+86); `pull.md` 489, read after a commit and on `pull`.

## 1.80.2 (2026-10-22)

`/crav1-review-pr`: a slimmer `SKILL.md`. Rare cases moved word for word into `references/`; no rule changed.

### Kit

- **Moved, each with a read-only-when pointer:** what other skills may do with this one (to `references/which-pr.md` **Other skills**); the stop when `gh` is not signed in (new `references/github.md` **GitHub not signed in**, in the existing folder); the branches-on-disk choice-word handling and its headless stop (to `references/azure-devops.md` **Branches on disk: choice words**); the record step's hard rule (to `references/comment-as-posted.md` **Record step rules**).
- **Kept on purpose:** the gate (only a named pull request), the read-only and no-edit rules, the secret rule, the finding format, ship or not, the verdict, never a rebase, post only after yes, and the other hard rules every review needs. The choice words stay listed. The description is unchanged (it carries the routing words).
- **Words read:** review-pr `SKILL.md` 1,983 to 1,836 (−147). The ~1,500 target would need moving common-path rules, so it stops here.

## 1.80.1 (2026-10-22)

`/crav1-review-pr`: the choice-words intro is back to the shared wording.

### Kit

- **Intro restored.** The review-pr choice words open again with "Exact words for bots and scripted runs. There are no `--flags`.", as in the other skills (1.80.0 had shortened it).
- **Pure move.** The record step's two headless stops (`Several comments could be the posted one. …` and `No posted comment found on PR <n>. …`) now live only in `references/comment-as-posted.md` **Headless and bot runs**, where they already stood word for word; `SKILL.md` keeps a read-only-when pointer. No rule changed.
- **Words read:** review-pr `SKILL.md` 2,000 to 1,983 (−17).

## 1.80.0 (2026-10-22)

`/crav1-review-pr branch`: review a branch before there is a pull request.

### Kit

- **`branch`.** `/crav1-review-pr branch feature/orders-retry` reviews a branch; no name means the current branch; a repo from `repos.md` may come first. A branch named without the word is still not a pull request.
- **Local diff.** No fetch. The base is the spec's Match `Branch:` entry and its `(into …)` / `(spec branch)` marker, then the repo's `Merges into`, then the default branch. One line shows the base, where it came from, the merge-base and the age of the remote copy. No base: one question with up to 4 likely bases and Other; a headless run stops and says how to name it.
- **Same checks.** Spec, plan, `verify.md`, the first-section secret rule, `F#` findings and suggestions. The body, linter and required-check state, the comment record and posting are skipped, said once. Verdict in the chat. No checkout, commit, push or post. When the base moved on, it suggests merging the base in, never a rebase.
- New `crav1-review-pr/references/branch.md`, read only on `branch`.
- **Words read:** review-pr `SKILL.md` 1,999 to 2,000 (+1: the new line, with the choice-words intro shortened to stay at the 2,000-word limit); `branch.md` 234, read only on `branch`; `which-pr.md` +10.

## 1.79.0 (2026-10-22)

`/crav1-add-to-spec branches`: import every open branch with something new, in one batch.

### Kit

- **`branches`.** On the code-change path, `/crav1-add-to-spec branches` (or `orders-api branches` for a repo in `repos.md`) lists, read-only and with no fetch, every local or remote-tracking branch that is not merged into its base and has commits not read yet (`Synced at` and the overlap check). Merged branches, branches with nothing new and the base branches are left out. No date cutoff.
- **Each line:** new commit count, last commit date, and the age of the remote copy. No commit in 3 months or more: `stale (no commits since <date>)`, as the Azure DevOps and GitHub Stale views say. Stale branches stay listed.
- **One question:** A) Yes, all, B) Yes, skip the stale ones, C) Name the ones I want, D) Stop. `branches all` and `branches skip stale` answer it up front; a headless run with neither stops and names them.
- **Import.** Each chosen branch runs the existing branch import (parent diff, overlap, PR note, `Synced at`, `Branch:` list). A shared commit is imported once. All sorts in one batch with one confirmation. A stale branch left out is named once as worth deleting on the host. Never deletes, pushes or fetches.
- New `crav1-add-to-spec/references/branches-sweep.md`, read only on `branches`.
- **Words read:** add-to-spec `SKILL.md` 831 to 845 (+14); `branches-sweep.md` 317, read only on `branches`.

## 1.78.0 (2026-10-22)

`/crav1-what-do-we-know-about-this` points a gap at `ask research`.

### Kit

- **Research next step.** When the answer has a gap (something unknown, or a guess marked `(inference, not in the docs)`) and that gap matches an open question in a spec, the answer ends with one line: `Next: /crav1-show-or-ask-open-questions ask research <a few words from that question>`. It adds the spec (`orders static IP`) only when the words would match more than one spec. No match: no line. It does not run the command and asks no questions.
- The skills reference and the what-do-we-know walkthrough say so.
- **Words read:** what-do-we-know `SKILL.md` 1,877 to 1,895 (+18).

## 1.77.0 (2026-10-22)

Open one question by its words or its `Q#`. `/crav1-show-or-ask-open-questions ask research` drafts a research request.

### Kit

- **One question.** In `/crav1-resolve-open-questions` and `/crav1-show-or-ask-open-questions`, topic words can narrow the list to one question: `/crav1-resolve-open-questions detailed static IP` opens only that one, with the detailed entry. `<spec> Q#` (`orders Q3`) works too. Several matches: one question listing up to 4, the rest under Other. The show overview prints each question's `Q#`, in the same document order resolve uses. No ids are written into specs. The rule is in `crav1-add-to-spec/references/scope.md`.
- **`ask research`.** `/crav1-show-or-ask-open-questions ask research static IP Alex` drafts one self-contained request that works in any tool: the question, why it matters, what is known so far, sources, who decides, and what to bring back. The personal-data and secrets check runs on it; nothing is sent. It writes the existing `Pending:` mark with channel `research` (shown as `Pending since <date> for Alex (research)`). The researcher is the typed name, else `git config user.name`, else no name (`Pending since <date>, research`). No question when the words match one question.
- **Back and todo.** The research note that comes back goes through `/crav1-add-to-spec` as before (answers linked, open points routed). `/crav1-help todo` ranks the mark as a pending draft under **Yours first**; an unnamed research mark counts as yours.
- New `crav1-show-or-ask-open-questions/references/research.md`, read only on `ask research`. No new folder.
- **Words read:** show-or-ask `SKILL.md` 1,312 to 1,324 (+12); resolve-open-questions 1,386 to 1,390 (+4); `scope.md` 485 to 507 (+22); `research.md` 243, read only on `ask research`; help `todo.md` +12.

## 1.76.1 (2026-10-22)

Fix: `/crav1-finalize-commit commit` no longer asks "Commit this message?".

### Kit

- **Bare `commit`.** The word `commit` in the invocation, the same word as the question's option, now works exactly like `commit now`: draft, show the message once, commit with no question. The same refusal for `agent-tools/` or build output (warn and offer the normal choices), and it never pushes. Typing nothing still asks.
- The skills reference, `/crav1-help` (from `skills.yaml`) and the commit walkthrough say so.
- **Words read:** finalize-commit `SKILL.md` 1,808 to 1,815 (+7).

## 1.76.0 (2026-10-22)

`/crav1-add-to-spec pr71 all`: new commits, the description and every comment thread of a pull request, in its PR note. `pr71` alone is enough for a code change.

### Kit

- **PR ref alone.** `pr71`, `pr 71`, `#71` or `pr <repo> 71` (parsed as `references/scope.md` says) means `code change`, so the word is not needed. Offline first and no questions, as before. Comments are not read, and an existing `## PR updates` section is left as it is.
- **`all` after a PR.** `/crav1-add-to-spec pr71 all` runs the code change (only new commits), then appends `## PR updates as of <date>` to the PR note: the description when it changed, then one heading per thread (`file:line` or Conversation, open or resolved) with each author as the host shows it, the date, the text verbatim and nested replies. Bot and system threads are skipped. The personal-data and secrets check runs on everything. A re-run appends only what is new or edited, plus one line per thread state change, and never rewrites an earlier section. A clear answer is linked as `Answered:`; a decision becomes a new open question; spec lines are never rewritten.
- **Read with.** GitHub: `gh pr view`, `gh api` pull comments and GraphQL `reviewThreads`. Azure DevOps: `az devops invoke` `pullRequestThreads`. Signed out: one question with the sign-in status, A) I've signed in, look it up, B) Paste the comments instead, C) Stop. No polling; a headless run reports and stops.
- **Not a seventh word.** The top-level words stay `fact` / `dump` / `code change` / `meeting` / `mail` / `chat`. `all` works only after a PR ref. The skills reference and `/crav1-help` show it as one line, `After a PR: all`.
- **Words read:** add-to-spec `SKILL.md` 806 to 831 (+25); new `references/pr-comments.md` 389, read only on `all`; code-change `BRANCH.md` +34; `notes.md` +28; help `SKILL.md` 1,699 to 1,713 (+14).

## 1.75.0 (2026-10-21)

`/crav1-help todo`: what to do next, ranked from the records. Scope by pull request, found offline first.

### Kit

- **`todo`, `todo next`, `todo top N`.** `/crav1-help` ranks every action the records imply, read-only, nothing stored: (1) a question that blocks otherwise ready tasks, (2) answered, not resolved, (3) a pending draft older than 3 days, (4) an ask older than 7 days, (5) a date in `## Constraints` within 14 days, (6) stale research with open points, (7) a decision for the team, (8) ready tasks, (9) a parked spec. Ties: more tasks unblocked, then older. Each line gives the spec, the reason with its age, and the next command. `todo next` is the top 5. A **Yours first** group comes from `git config user.name` or `todo for <name>`; no match, no group, no question. The rules are in `crav1-help/references/todo.md`, read only on `todo`.
- **Shared scope.** New `crav1-add-to-spec/references/scope.md`: person, spec and topic (moved word for word from `/crav1-show-or-ask-open-questions`), a branch (via `branches.md`), and a pull request as `pr71`, `pr 71`, `#71` or `pr <repo> 71`. `/crav1-help todo`, `/crav1-show-or-ask-open-questions` and `/crav1-resolve-open-questions` use it.
- **Pull request lookup, offline first.** (1) the PR note (`source: PR <n>` in the notes indexes, its `used_by` and head branch, or a `(PR <n>)` Branch entry), (2) the local git log (merge and squash subjects), (3) online only when gh or az is already signed in, or after one question with the sign-in status: A) I've signed in, look it up, B) Use a branch name instead, C) Stop. One re-check, no polling. A headless run reports and stops. The answer says which step found it.
- **`/crav1-open-pr` records the number.** With the URL, it adds ` (PR <n>)` to the head's Match `Branch:` entry in the spec, or adds that entry for `feat/<slug>` or `spec/<slug>`. Uncommitted. `branches.md` ignores the marker for branch rules.
- **Words read:** help `SKILL.md` 1,655 to 1,699 (+44, 5 in the description); `todo.md` 364 and `scope.md` 485, each read only when used; show-or-ask `SKILL.md` 1,394 to 1,312 (−82); resolve-open-questions 1,367 to 1,386 (+19); open-pr `after.md` +64; `branches.md` +31.

## 1.74.1 (2026-10-21)

Fix: the `/crav1-finalize-commit` question no longer fails with `InputValidationError`.

### Kit

- **At most 4 options per question.** The questions tool rejects a fifth option. `/crav1-finalize-commit` now offers `commit` / `copy` / `change` / `stop`; `change` covers edit and rewrite (say what to change, or say rewrite). `/crav1-resolve-open-questions` offers 2–4 letters. A fifth choice goes under Other. The same in the Cursor, Claude Code and plugin copies.
- **Message shown once.** The Summary and Description stay in the reply; the question prompt is just `Commit this message?`.
- The commit walkthrough, the ideas walkthrough, the skills reference, the message-only branch and the build-tasks worker name the new options.
- **Words read:** 47 fewer in finalize-commit `SKILL.md`, 10 more in resolve-open-questions `SKILL.md`.

## 1.74.0 (2026-10-21)

`/crav1-resolve-open-questions` can show more context per question. No new questions.

### Kit

- **`detailed`.** `/crav1-resolve-open-questions detailed` shows an extended entry for each question, before its options: Blocks (the spec line or section, plus `Blocks:` tasks), Why it matters, Known so far, Who can answer, Asked (status, who, channel, date), Sources, and Suggested when there is one. Without the word the list stays short, as before, and nothing is asked.
- The extended entry lives in the new `references/detailed.md`, read only on `detailed`. The skill description, the skills reference, guild routing and the draft-spec walkthrough name the word.
- **Words read:** 34 more in `SKILL.md` (6 of them in the description); `references/detailed.md` is 180 words, read only on `detailed`.

## 1.73.0 (2026-10-20)

`/crav1-finalize-commit` can commit in one go.

### Kit

- **`commit now`.** Drafts, shows the Summary and Description paste blocks, then runs `git commit` with no choice question. It never pushes. When `agent-tools/` or build output is in the file set, it warns and offers the normal choices instead.
- **Style words `crav1` and `git log`.** They answer the CRAV1-style vs git-log question for this commit, the same as `once` and `log-once`, so it is not asked. Saved style rules work as before.
- `/crav1-finalize-commit commit now crav1` asks no questions when files are staged. The headless `Missing choice` list, the skill description, the skills reference, guild routing and the commit walkthrough name the new words.
- **Words read:** 56 more in `SKILL.md` (12 of them in the description), 10 more in the message-only branch.

## 1.72.1 (2026-10-20)

Fix: the `/crav1-add-to-spec` opening question no longer sends a mail or a chat to the meeting path.

### Kit

- **Opening question.** A mail or a chat thread is now listed under option 2, **A dump** (`mail`, `chat`), and option 4, **A meeting**, is minutes or a transcript. When the question is skipped, a `.eml` or a chat export now counts as 2. The question still has four options. The skills reference says the same. `/crav1-add-to-spec meeting` still takes a mail or a chat when you name it.

## 1.72.0 (2026-10-20)

Two new choice words for `/crav1-add-to-spec`: `mail` and `chat`. No new questions.

### Kit

- **`mail` and `chat`.** Both run the dump branch. `/crav1-add-to-spec mail`, or a message that says "this mail", "this email" or "this chat", picks the word and skips the opening question. A mail is always an imported source: the run reads `references/sources.md` and `sources-mail.md` before the sort, and `Asked:` dates come from the mail. An exported chat file is an imported source too, with dates from the chat; pasted chat text is sorted as a plain dump. The headless `Missing choice` list, the skill description, the skills reference, guild routing and the dump walkthrough name the new words.
- **Words read:** 25 more in `SKILL.md` on every run (2 of them in the description); 24 more in the dump branch on dump, mail and chat runs.

## 1.71.3 (2026-10-20)

Leaner `/crav1-add-to-spec` dump runs, and a `SKILL.md` without the fact-only text. Text moved word for word; no rule or question changed.

### Kit

- **Fact text out of `SKILL.md`.** Input, Target, Imported sources, Add to that spec.md, Notes, Impact, Stop and Style moved to `references/fact.md`, read only for a fact or a handoff. `SKILL.md` keeps the opening, choice words, handoff pointers and two shared steps, **Thin spec** and **Research compare**, that the fact path and the dump branch both use. The handoff files, the meeting branch and `references/notes.md` now point at `fact.md`.
- **Dump branch split.** The "This is not" scope lines moved to `references/dump-scope.md`; the glossary, picture and `assets/system` lines to `dump-landscape.md`, read only when `docs/system/` exists; the `Answered:` and `Asked:` write to `dump-answers.md`; the new-spec pointer list to `dump-new-spec.md`. The research and thin-spec copies are now pointers to the shared steps in `SKILL.md`.
- **Fixed names.** The dump branch now names **Write the full note**, not the old **Write the notes** heading or a **Note** pile.
- **Words read:** pasted dump 6,367 to 4,453 (4,933 with `docs/system/` and answers); flagged mail 11,802 to 10,043; pasted transcript 9,385 to 7,471; `.docx` transcript 10,654 to 8,740; meeting 7,370 to 6,172. A fact run goes from 3,040 to 3,170, and a meeting with a kept addition from 7,726 to 7,884, because they now read `fact.md` and its header.

## 1.71.2 (2026-10-20)

Leaner imported-source runs in `/crav1-add-to-spec`. `references/sources.md` is split so a run reads only what its case needs. Text moved word for word; no rule, question or wording changed.

### Kit

- **Sources split.** `references/sources.md` keeps what every import needs: folder, README, the personal-data and secrets check, spec lines and do not commit, plus one routing line. The transfer data policy, the note and the list, and the one question for the recommendations moved to `sources-flagged.md`, read only when an item is flagged or a secret is found. Black-boxed text, Word files, dates, versions and conflicts, and headless runs moved to `sources-rare.md`. Temporary files, an image the kit cannot view, and duplicate images moved to `sources-binary.md`.
- **Pointers instead of copies.** The dump and meeting branches, the imported-sources handoff, `/crav1-existing-to-specs` (repos and bundle) and `/crav1-bundle-to-specs` no longer restate the personal-data, secrets, policy and image rules; each has one line pointing at the sources files.
- **Repointed.** `/crav1-show-or-ask-open-questions` and `/crav1-review-pr` read the transfer data policy from `sources-flagged.md`; `/crav1-verify-build-against-spec` and `/crav1-ado-sync` push features read headless runs from `sources-rare.md`.
- **Words read** (dump path, including its branch file): pasted dump 6,466 to 6,367; pasted transcript with nothing flagged 11,273 to 9,385; mail with flagged items 12,432 to 11,802; mail with images 13,080 to 12,635; `.docx` transcript 11,921 to 10,654.

## 1.71.1 (2026-10-20)

Leaner `/crav1-add-to-spec` runs. Its three biggest reference files are split so a run reads only the part it needs. Text moved word for word; no rule, question or wording changed.

### Kit

- **Research check.** `references/research-stale.md` keeps the check every kept quote runs (when to compare, what to read, what is a hit) plus Readers and Stop. Marking and the revisit request moved to `research-stale-mark.md`, read only on a hit. Clearing, narrowing, routing and answered-later moved to `research-stale-clear.md`, read only when a mark is cleared, narrowed or re-checked. Other skills that point at the clear or answered-later part now point at `research-stale-clear.md`.
- **Imported sources.** `references/sources.md` keeps the shared rules (folder, README, reading, versions, headless runs, personal data and secrets, spec lines). Mails and images inside a mail moved to `sources-mail.md`; binary files to `sources-binary.md`. A paste reads neither.
- **Handoffs.** `references/handoffs.md` is now one file per section (`handoffs-read-environment.md`, `handoffs-suggest-tests.md`, `handoffs-ado-push.md`, `handoffs-ado-pull.md`, `handoffs-meeting.md`, `handoffs-import-answers.md`, `handoffs-picture.md`, `handoffs-imported-sources.md`), each behind its own pointer in `SKILL.md`.
- **Words read.** A pasted dump reads about 3,000 words instead of 6,600. A mail import reads about 9,000 (9,650 with images) instead of about 14,300.

## 1.71.0 (2026-10-20)

Slimmer skills. Each `SKILL.md` keeps the common path; rare cases moved word for word into the skill's `references/`, behind a one-line pointer that says when to read them. No rule changed.

### Kit

- **Slimmed skills.** The 15 skills over about 2,000 words now load only what the usual run needs: `/crav1-review-pr` 6,728 to 1,999 words, `/crav1-read-environment` 6,234 to 1,666, `/crav1-merge-pr` 4,173 to 1,547, `/crav1-add-to-spec` 4,145 to 1,982, and the open-pr, map-pipeline-environments, what-do-we-know-about-this, tighten-spec, plan-from-spec, help, ideas-to-spec, spark-to-spec, bundle-to-specs, show-or-ask-open-questions and explain-existing-system skills. Moved: other hosts (Azure DevOps), fallbacks and sign-in notes, cross-repo and outside-the-kit cases, re-reviews, notes and posting, handoffs from other skills, the thin landscape and `Synced at` rules, and later phases. Each pointer reads `Read references/<file>.md ("<section>") only when <case>.`
- **Size warning.** `scripts/check-kit-docs.py` warns in CI when a `SKILL.md` is over 2,000 words. CONTRIBUTING says how to keep under it.

## 1.70.0 (2026-10-20)

Ask less. Skills stop asking what is already settled and ask the rest in one go. Examples use made-up names: the spec `orders-retry`, the code repo `orders-api`.

### Kit

- **Ask-less rule.** `crav1.mdc` gains one rule: never ask what the conversation, the files or an earlier answer already settles; pick an obvious default and say it in one line (`Using develop as the base (Merges into).`); gather the remaining questions into one batch; confirm all writes once at the end with a single yes. Choice words in the invocation still answer their question, and headless runs use the stated defaults. The landscape, glossary, picture and `Synced at` detail moved out of the rule file into the skills that write them; the rule file is now 762 words (was 867).
- **Batched question flows.** `/crav1-tighten-spec`, `/crav1-tighten-plan` and `/crav1-resolve-open-questions` show every issue at once with the recommended option first: `yes` takes every recommendation, `I1 B, I3 keep` overrides some, and answering one at a time still works. `/crav1-read-environment` and `/crav1-map-pipeline-environments` show all sections together and ask once. `/crav1-suggest-tests-for-code`, the meeting and code-change branches of `/crav1-add-to-spec` (sort, Merges into and the into marker in one confirmation), unplaced source items, the `/crav1-ado-sync` pulls, the repos-only branch of `/crav1-existing-to-specs` and `/crav1-finalize-commit` (style with the copy/edit/commit choice) do the same.
- **What's left line.** `/crav1-ideas-to-spec`, `/crav1-spark-to-spec` and `/crav1-bundle-to-specs` end with one plain line naming the next skill: `Left: 2 gaps to tighten, 3 open questions. Next: /crav1-tighten-spec orders-retry.`
- **Docs.** The read-environment, add-to-spec meeting, ado-sync pull-tasks and suggest-tests pages and `skills.yaml` describe the batch.

## 1.69.1 (2026-10-20)

Template copies that had drifted from the project templates.

### Kit

- **Note template in dump and meeting.** `/crav1-add-to-spec`'s dump and meeting branches carried an old `note.md` whose `kind:` list lacked `pull request` (in the main template since 1.65.0) and that had no `commits:` or `pr_note:` fields. They now match `docs/notes/_template/note.md`.
- **Notes index in dump and meeting.** Their `index.md` copies still had the pre-month layout; they now match `docs/notes/_template/index.md` (the generated top index with one row per month).
- **verify.md and fix-log.md templates.** `docs/specs/_template/verify.md` now has the BLOCKER, Branches, Sub-branches, Promotion and Skipped tests lines the skill's copy already had, and `docs/specs/_template/fix-log.md` has the skill's Next wording.
- **Drift check in CI.** `scripts/check-template-copies.py` fails when a skill's template copy differs from the template with the same name in `docs/*/_template/`; three copies that are deliberately a different template are listed with the reason.

## 1.69.0 (2026-10-20)

Setup 6: environment and release branches. Done stays "merged into the base branch"; how far the work has got after that is shown on its own line. Examples use made-up names: the code repo `orders-api`, the pipeline `orders-cd`.

### Kit

- **promotion.md.** A new `docs/environments/promotion.md`, next to marks.md, in the same four-field shape: `orders-api | develop | test | pipeline orders-cd, stage DeployTest`. The second field may be a pattern (`release/*`) or a tag pattern (`tag v*`). An environment word outside the known list states its place, `sandbox (after dev)`; without it the line is Unclear. Lines are appended, never rewritten. Format: `docs/environments-promotion.md`.
- **Branches section.** `/crav1-map-pipeline-environments` gains a fourth section after Unclear that proposes promotion.md lines from `trigger:` branch lists, stage `condition:` on `Build.SourceBranch`, classic artifact branch filters and `refs/tags/` triggers. Azure DevOps definitions only, no runs; confirmed section by section.
- **Promotion line.** `/crav1-help` status, `/crav1-verify-build-against-spec`, `/crav1-tasks-ready-to-build` and `/crav1-merge-pr` show `Promotion: on the branch that deploys to test (develop); not yet on the branch that deploys to prod (main).` Release patterns name the newest matching branch (`on release/2026.11 (deploys to prod)`), tag lines the newest matching tag or `not yet tagged`, and a fix made on a release branch shows `not back on develop`. Branch reach only, never "deployed to". Report only; done is unaffected.
- **Pipeline runs (optional).** When a pipeline-sourced line is behind the Promotion line, the report asks **Also check the latest pipeline runs?** The choice word `pipeline runs` skips the question. A headless run without it gives the git answer and `Pipeline runs not checked. Add the word: pipeline runs.` Azure DevOps only and read-only; with `az` signed out it says `az has no login` and keeps the git answer.
- **Marks and docs.** `marks.yaml` adds the promotion line (61 marks). The glossary gains promotion and branch reach; `from-map-pipeline-environments.md` gains a Branches section.

## 1.68.0 (2026-10-20)

Setup 4: a spec with its own long-lived branch and a short sub-branch per task, plus revert reporting. Examples use made-up names: the code repo `orders-api`, the spec branch `feat/orders-capacity`.

### Kit

- **Spec branch and into markers.** The Match `Branch:` list can mark the spec branch, `feat/orders-capacity (spec branch)`, and a sub-branch, `feat/orders-capacity-t3 (into feat/orders-capacity)`. When a read finds a branch that split off another spec branch, `/crav1-add-to-spec` code change, `/crav1-tighten-spec` and `/crav1-open-pr` ask one yes/no question, `feat/orders-capacity-t3 split off feat/orders-capacity. Does it merge into feat/orders-capacity?` A yes writes both markers. A no writes nothing, and a headless run doesn't ask, writes nothing, and treats the branch as stacked.
- **Sub-branches for tasks.** `/crav1-plan-from-spec` may name a sub-branch on a task. When it doesn't exist yet, `/crav1-create-feature-branch` and `/crav1-build-tasks` offer **Create it from the spec branch (Recommended)** and write the `(into …)` marker after the yes.
- **No double import.** The fork point honours `(into …)`. The commit list leaves out merge commits (a merge commit that changes code beyond its two sides is offered on the sort). Reading the spec branch after its sub-branches imports only its own commits; a squash-merged sub-branch is covered through the host PR or listed as `may already be in <note>`.
- **Open-pr base.** Into, then `Merges into`, then the default branch: a sub-branch's PR goes into its spec branch, the spec branch's into the base.
- **Progress and done.** Status in `/crav1-help`, `/crav1-verify-build-against-spec`, `/crav1-tasks-ready-to-build` and `/crav1-merge-pr` shows `Sub-branches: 1 of 2 merged into feat/orders-capacity.` and `left behind: feat/orders-capacity-t4 (not in feat/orders-capacity)`. Done counts the top-level branches only; sub-branches never block it.
- **Reverts.** A merged branch whose change was later undone on the base shows `feat/orders-retry: merged, reverted on develop (<sha>)`, found by a `This reverts commit` message or the reverse patch. Report only; done is unaffected.
- **Marks and docs.** `marks.yaml` adds `(spec branch)` and the written `(into …)` (60 marks). The glossary gains spec branch, sub-branch, into branch and reverted; `from-plan-to-build.md` gains a setup 4 section.

## 1.67.1 (2026-10-20)

Two bug fixes in the multi-branch work. Examples use made-up names: the code repo `orders-api`.

### Kit

- **Branch list filled in.** `/crav1-add-to-spec` code change wrote only the slice `Synced at` line, so the spec's Match `Branch:` list stayed empty. A one-slice read of a work branch now also adds that branch to the list, for example `- Branch: orders-api feat/orders-retry; orders-api feature/orders-openapi`. Base branches (the `Merges into` and default branch) are never added, an entry already there is left alone, and existing `(into …)` and `(spec branch)` markers stay. The report says whether the branch was added. `marks.yaml` lists add-to-spec as a writer of the Branch mark.
- **Copy ages.** `/crav1-help` status (and every Branches report) showed remote copy ages one day too high. Ages now count whole calendar days in local time from the commit's committer date, without counting the commit day: a commit made today is `today`, yesterday is `1 day old`.

## 1.67.0 (2026-10-19)

`/crav1-review-pr` keeps the comment you actually posted, next to the one it drafted, so the specs repo matches what reviewers see. Examples use made-up names: the code repo `orders-api` on GitHub, pull request 42.

### Kit

- **Comment as drafted and as posted.** The follow-ups note now keeps every paste-ready comment as `## Comment as drafted, <date>`, and the posted text as `## Comment as posted, <date> (by <name>)`, each word for word in a code fence. A source line says where the posted text came from (read from the PR thread, pasted in chat, or posted from this review), which draft it was compared with, and which `Description as of` section of the PR note the review read. An edit on the host adds a new `, edited` section. Dated sections are never rewritten. Every review with a paste-ready comment writes the note. The rules are in the new `crav1-review-pr` `references/comment-as-posted.md`.
- **Record step.** At the start of every run on a pull request with a drafted comment and nothing posted after it, the review looks read-only for the posted comment (GitHub reviews and conversation comments, Azure DevOps top-level threads or a reply in the earlier thread), by you and after the draft, that matches it. One match: it asks you to confirm. Several: you pick. None on a host it can read: one line, and the review goes on (it may not be posted yet). No `gh` or `az` session, or `comment posted` with nothing found: you paste it. The text goes through the personal-data and secrets check first.
- **Compare with the draft.** Points are paired by link and title and listed as drafted, changed, not in the posted comment, or added. A drafted point you left out stays in the note, ending `(Not in the posted comment, <date>; still open.)`. A cut question keeps its `Asked on the PR:` line with the mark added. An added question gets an `Asked on the PR:` line.
- **Re-review against the posted comment.** `### Since last time` lists only points the reviewers saw. When nothing was posted, the new comment has no `### Since last time`; the chat still says which drafted points are fixed or open. A finding you cut is shown in the chat with its mark and kept out of the new comment unless you include it.
- **Post it.** A third option, **I'll post it myself**. After a post on your yes, the text the host returns is saved at once. On GitHub, your own pull request gets a comment, because the host allows no vote there.
- **Choice words.** `comment posted` (only record the posted comment), `newest comment` and `skip comment record`. A headless run with several candidates or none stops and names them. No word posts.
- **Marks.** `marks.yaml` adds Comment as drafted, Comment as posted, the posted comment's source line and Not in the posted comment (1.67.0), plus Asked on the PR (1.66.0). The data layout tables are regenerated (58 marks).

### Docs

- From a pull request review: a new "Comment as posted" section, with Steps, Post it, Re-review and Follow-ups updated. Data layout: the follow-ups note's dated sections. Glossary: Comment as posted. The skills reference lists review-pr's choice words.

## 1.66.0 (2026-10-19)

A plainer, link-first pull request comment from `/crav1-review-pr`, posted as one comment, and merge-the-base-in advice everywhere instead of rebasing. Examples use made-up names: the code repo `orders-api` on Azure DevOps, pull request 42.

### Kit

- **Comment layout.** The paste-ready comment follows the new `crav1-review-pr` `references/comment-layout.md`. There's no verdict line in the block (the chat says `Verdict: …` above it), and the block opens with one short, plain line with no greeting or praise. The sections are **Blockers**, **Bugs**, **Tests to add with this PR**, and **A question** (or **Questions**); an empty section is left out. Each point starts with the host link to its file and line on the source branch (Azure DevOps `?path=…&version=GB<branch>&line=N&lineEnd=N&lineStartColumn=1&lineEndColumn=1`; GitHub `blob/<branch>/<path>?plain=1#LN`), then an indented paragraph. A point with no file line opens with the PR overview link, or a branch link for merge order. Each point has at most one fix and no tails. There are no follow-ups, no table, no closing line, and no HTML. It's in English unless you ask otherwise for that comment.
- **Verdict and posting.** Any Blocker or Bug gives Changes needed, and only tests to add or a question gives Approve with comments. After your yes it posts **one comment** (the GitHub review body, or one Azure DevOps thread), with no inline threads, and sets the matching vote: Request changes / Comment / Approve on GitHub, Wait for author / Approve with suggestions / Approve on Azure DevOps. It never rejects.
- **Chat lines.** `B` (bug), `T` (test to add) and `Q` (question) lines join F, I and S, so every point in the block has a chat line. A question is saved in the follow-ups note as `Asked on the PR: …`.
- **Re-review.** Earlier points go under `### Since last time`, read also from an earlier one-comment review's links.
- **Merge the base in, never rebase.** A merge-order point asks whether the other branch still goes first, then suggests merging the base into this branch. `/crav1-merge-pr` stops on a branch that is behind or has conflicts with `Merge <base> into <head> (resolve any conflicts there), push, then ask to merge again.` `/crav1-open-pr` answers a rejected push with `git pull --no-rebase`, never a force-push. Seeing that someone else rebased a branch is still reported.

### Docs

- From a pull request review: Paste-ready comment, Comment style, Post it and Re-review rewritten for the new layout. From commit to merge: "Behind, conflicts, or a rejected push". Glossary: Merge the base in. Data layout: questions in the follow-ups note.

## 1.65.0 (2026-10-19)

Review a code pull request from the specs repo, and save every pull request's description as a note in the specs repo. Examples use made-up names: the specs repo `orders-specs`, the code repo `orders-api` on Azure DevOps.

### Kit

- **Cross-repo review.** `/crav1-review-pr` works from the specs repo for a pull request in a repo listed in `docs/system/repos.md` (`/crav1-review-pr orders-api 71`, or the URL; matched on the `URL` cell), or with both repos open in one workspace. It reads the pull request from `gh` or `az`, read-only, and the spec, plan and `verify.md` from the specs repo's working tree, found by the head branch in `Synced at`, Match `Branch:` or task `(branch: …)`. A code pull request whose spec has `plan.md` gets the full checks. Another repo's part of a spec is not a miss; a new `I3 — info — other repos` note lists it with the Branches line. A mismatched repository still stops, now naming the three places it looked.
- **Azure DevOps diff from a sibling checkout.** When the code repo's copy of the pull request branches is missing or older than the pull request, one question: **Fetch only the PR's two branches (Recommended)**, **Use what's on disk** (with the copy's age and a warning), or **Stop**. Choice words for bots: `fetch pr branches`, `use disk`, `stop pr review`. No question when the copies match. This fetch is the one exception to the no-fetch rule for a sibling checkout in `references/branches.md`.
- **Notes into a specs repo next door.** Run from the code repo, the review finds the specs repo as a sibling with a `repos.md` row for this repo, writes its notes there without committing, and names the full path. A code repo pull request's follow-ups note is always `review-pr-<repo>-<n>-follow-ups.md`.
- **PR note.** One note per pull request, `kind: pull request`, keyed by `source: PR <n> <repo URL path>`, filed by the pull request's created date as `docs/notes/YYYY-MM/YYYY-MM-DD-pr-<repo>-<n>.md`. It holds the title, URL, author, base and head, state, and `## Description as of <date>` with the description after the personal-data and secrets check; images get the four options. A changed description is appended as a new dated section, never removed. `/crav1-review-pr` writes or reuses it on every review (also for pull requests `/crav1-open-pr` made), `/crav1-merge-pr` after a confirmed merge, and the code-change branch of `/crav1-add-to-spec` when given a pull request. `/crav1-open-pr` does not save one. Rules: `crav1-add-to-spec` `references/notes.md` **PR note**.
- **Code change from a pull request.** `/crav1-add-to-spec code change orders-api PR 71` (or the URL) imports the pull request's commits and links the code-change note to the PR note with `pr_note:`. Given a branch, it writes the PR note when a signed-in `gh` or `az` host shows exactly one pull request for that branch; otherwise it writes none and says why.
- Note template: `kind` gains `pull request`; new `pr_note:` field. `notes_index.py --selftest` covers a PR note and a linking code-change note.
- `docs/reference/marks.yaml`: new marks `note-kind`, `note-pr-source`, `note-pr-link`, `pr-description-as-of` (53 marks); `/crav1-review-pr` now reads `task-branch` and `merges-into`.
- `workflow.yaml`: `/crav1-review-pr` and `/crav1-merge-pr` may name `/crav1-finalize-commit` for the notes they wrote.

### Docs

- From a pull request review: "Specs in another repo" and "PR note". From a code change: "From a pull request". From commit to merge: "PR note". Glossary: PR note; specs repo, code repo. Data layout: the PR note, `pr_note`, and the generated marks tables.

## 1.64.1 (2026-10-19)

Fixes to the 1.64.0 fork point and rebase matching, found by the proving-ground multi-branch scenarios. Examples use made-up names.

### Kit fixes

- **Fork point before `Merges into` is filled.** While a repo's `Merges into` cell is empty, the integration branches on disk (`develop`, `development`, `dev`, `integration`) are fork-point candidates too. A branch cut from `develop` in a repo whose default is `main` now shows its own commits, not everything since `main`, and the code-change question to record `Merges into` is asked.
- **Stacked branches.** A spec branch built on top of the branch being read (it already contains its tip) is no longer taken as its parent, and another spec branch counts only when the split point is in none of the base candidates.
- **Rebase after a prune.** A code-change note's body now starts with one commit line per imported commit (`<short sha> <author date> <subject>`). When an imported commit is no longer on disk after a force push, a commit with the same author date and subject is reported as the same change and not imported again.
- `docs/reference/marks.yaml`: new mark `note-commit-line` (49 marks).

### Docs

- Glossary (fork point) and data layout (fork point before `Merges into`, same change after a rebase).

## 1.64.0 (2026-10-19)

One spec, many feature branches: setups 1 (main only), 2 (an integration branch such as `develop`), 3 (stacked branches) and 5 (one spec over several repos). Everything is report only and read-only git on the refs on disk; nothing fetches and nothing writes `Status:`. Examples use made-up names.

### Kit

- New `crav1-add-to-spec/references/branches.md`: the shared rules for work branches, base branch, fork point, merged, gone, rewritten and shared branches, the sibling checkout, and the Branches line.
- **Synced at per branch.** A slice `Synced at` line keeps one entry per branch, `; `-separated (`Synced at: orders-api feat/orders-retry@155b5c4, 2026-10-19; develop@00344be, 2026-10-15`). A new read replaces only that branch's entry. Every writer follows it: add-to-spec code change, bundle-to-specs (and its worker and slice agent), spark-to-spec, ideas-to-spec and refresh-system-notes. Drift is measured per branch.
- **Merges into.** `docs/system/repos.md` gets an optional `Merges into` column (empty means the default branch) in every template. The code-change branch of `/crav1-add-to-spec` offers to fill it after one yes when the fork point is not the default branch; a headless run writes nothing.
- **Fork point.** A branch diff starts where the branch split off (its `(into …)` branch, the repo's `Merges into` branch, the default branch, or another spec branch, by fewest own commits), not at the default branch. The report names the parent, the split point and the age of each remote copy. No fork point: fall back, then ask with options only; headless stops with `No fork point found for <branch>. Name a commit range.`
- **No double import.** Code-change notes get a `commits:` list. Before writing, the change's commits are compared with every code-change note, by SHA and by `git patch-id` (same change under another SHA). Imported commits are left out; a fully imported change takes the reuse-or-skip path. A squash merge counts as covered only through a merged PR on GitHub (`gh`) or Azure DevOps (`az`); otherwise it is listed as `may already be in <note>`.
- **Gone, rewritten, shared.** A deleted branch counts as merged when its recorded SHA or its `commits:` are in the base, or the host shows a merged PR (`merged, branch deleted`). Only a gone and unmerged branch gets the new `mark-dropped` offer in `/crav1-tighten-spec`, which ends its `Synced at` entry with `(dropped)`. A rebased or force-pushed branch says `branch rewritten since last read`, is matched by patch-id, and never errors. A branch in several specs is reported under each with `(also in <slug>)` and counted once across specs; one note serves every spec.
- **Branch list.** `/crav1-tighten-spec` and `/crav1-plan-from-spec` read every work branch without checkout; a yes on writing the branch adds to the Match `Branch:` list. Pieces only on an unmerged branch are labeled `only on <branch>, not merged`.
- **Task branch.** `/crav1-plan-from-spec` ends a task with `(branch: …)` (with the repo when the spec spans repos) when its piece lives on one branch. `/crav1-create-feature-branch` offers it first, marked (Recommended), and never creates it from default without asking. `/crav1-build-tasks` range and all-tasks runs and `/crav1-build-features` switch to each task's branch on a clean tree; a missing branch blocks that task. `/crav1-tasks-ready-to-build` shows it.
- **Other repos.** Code is read read-only from the sibling checkout `../<repo>`. When it is missing, the kit asks for the path with options only; headless stops with `No checkout found for <repo>. Name its path.`
- **Done across branches.** `/crav1-verify-build-against-spec`, `/crav1-help status`, `/crav1-tasks-ready-to-build` and the `/crav1-build-features` board report `Branches: <n> of <m> merged into <base>`; demoable needs every branch merged. `/crav1-merge-pr` says `<n> of <m> branches of <slug> now merged`. `/crav1-ado-sync` suggest-features counts unmerged branches as open work.
- **open-pr base.** `/crav1-open-pr` uses the head's `(into …)` marker (read only in 1.64.0), then the repo's `Merges into` branch (also from a sibling spec repo), then the default branch. It and `/crav1-review-pr` also find the spec from a spec that lists the head branch.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.64.0.

### Docs

- New `marks.yaml` entries: `(dropped)`, `(branch: …)`, `Merges into`, note `commits:`; the `Synced at` slice line and the Match `Branch:` list now allow several branches.
- Glossary: work branch, base branch / Merges into, fork point, dropped, branch rewritten since last read. Data layout: a "One spec, several branches" section, the `Merges into` column and the note `commits:` field.
- Walkthroughs: add-to-spec code change, spec to plan, plan to build and verify get a several-branches section.
- New `docs/reference/marks.yaml`: the single source for every mark and line format the kit writes in a product repo (44 marks), each with its files, format, pattern, examples, writers, readers, and the version it arrived in. Data layout gets a generated **All marks** section, and its **Readiness marks** table is generated from the same file.
- Data layout: the `docs/environments/marks.md` row now names both Azure Boards lines with their per-home form, `Azure Boards task type (<project>): <type>` and `Azure Boards task done state (<project>): <state>` (it said `Azure Boards task type:` only).
- Examples in docs and skills use made-up names (`orders-api`, `contoso/orders`, `Dana`) instead of names taken from a real project.

### CI

- `notes_index.py --selftest` checks that a code-change note keeps `commits:` through migrate.
- `scripts/gen-marks.py --check`: the marks tables match `marks.yaml`, every example matches its pattern, and every skill or agent listed as writer or reader mentions the mark.

## 1.63.0 (2026-10-16)

### Kit

- `notes_index.py migrate`: a moved note's own relative links are all rebased, not only `.md` targets: folders (`../sources/x/` becomes `../../sources/x/`), `.txt` and any other file, with or without a trailing slash, with anchors. Absolute URLs, root-style `docs/` paths, and anchor-only links stay as they are. Inbound links to a moved note keep their anchor (`note.md#part`).
- Source fill reads every `Source:` line and multi-item source lists (comma or semicolon items, `- item` bullets under `Source:` or `Sources:`). `source_folder` is the first `docs/sources/` path; `source` is that line or item verbatim. When none points into `docs/sources/`, `source` is the first one and `source_folder` stays empty. An empty `source_folder` is filled even when `source` is already set; a non-empty value is never overwritten.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.63.0.

### Docs

- Data layout and refresh-system-notes describe the full link rebase and the multi-line source fill.

### CI

- The `notes_index.py --selftest` step covers folder, `.txt`, bare, and anchored link rebases; URLs, root-style, and anchor-only links left alone; anchored inbound links; multiple `Source:` lines; a `Sources:` list filling `source_folder` when `source` is set; and idempotence.

## 1.62.0 (2026-10-16)

### Kit

- `notes_index.py migrate` rewrites references: every markdown link or path to a moved note anywhere in the repo (specs including parked and retired, `docs/system/`, `docs/sources/**/README.md`, other notes, `Full source:` and `Source:` lines) is updated to the month-folder path, keeping repo-root style or computing the correct relative path. A moved note's own relative links are rebased. Each changed file is listed.
- `migrate` fills front matter `source` (the `Source:` line verbatim) and `source_folder` (the `docs/sources/` path in it) from each note's existing `Source:` line; with no `Source:` line both stay empty, never guessed. `/crav1-add-to-spec`'s already-imported check matches on these fields.
- New mode `notes_index.py migrate-dry-run` prints the planned moves, source fills, and link rewrites and writes nothing. `/crav1-refresh-system-notes` recommends it before `migrate`.
- `migrate` is idempotent: a second run changes nothing; after a manual move it fixes stale flat-path links and empty source fields only.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.62.0.

### Docs

- Data layout: dry run, link rewrites, source fills.

### CI

- The `notes_index.py --selftest` step now covers link rewrites (including retired specs and source READMEs), source fill, an empty fill with no `Source:` line, dry run writing nothing, idempotence, and a manual move.

## 1.61.0 (2026-10-16)

### Kit

- `/crav1-add-to-spec`: every input (fact, dump, code change, meeting) becomes **one note** holding the full input and its source; a fact's note holds the fact plus the passage around it. Each matching spec gets only its own short points, each with `Full source: <note>`. Notes are never absorbed; `used_by` grows. The meeting branch's Note choice and the dump branch's Note pile are removed (a left item stays in the full note). The absorb question is gone; old `Absorbed by` lines are still read as used by. Rules in `crav1-add-to-spec` `references/notes.md`.
- Notes live in month folders `docs/notes/YYYY-MM/`, named and filed by the **source date** (meeting date, mail sent date, commit date), with `imported` recorded; no source date files under the import date and says so.
- Indexes are generated: `crav1-add-to-spec/scripts/notes_index.py` builds `docs/notes/index.md` (one row per month) and `docs/notes/YYYY-MM/index.md` from note front matter (`title`, `kind`, `source`, `source_date`, `imported`, `used_by`, `waiting_for`). `--check` fails on a stale index. Skills no longer hand-edit indexes.
- Duplicate check: the same source again says `already imported on <date> as <note>` and offers reuse or skip, never a second copy. The same point from another source adds a second source on the spec line. A disagreement is written as a `**Conflict:**` line, never an overwrite.
- Parked specs (1.60.0) fold into the general rule: nothing written, the slug goes in the note's `waiting_for`.
- Migration: `notes_index.py migrate` moves existing flat notes into month folders by source date, adds front matter, and rebuilds the indexes. `/crav1-refresh-system-notes` names it when it finds flat notes. Old spec lines keep their source lines; no backfill.
- Readers follow: `/crav1-ado-sync` (every note is input), `/crav1-review-pr` (follow-ups in `docs/notes/YYYY-MM/`), `/crav1-help` and `/crav1-show-or-ask-open-questions` (waiting counts from the indexes), `/crav1-retire-spec` (convert to note writes a month folder; un-park moves `waiting_for` to `used_by`), and the note write in `/crav1-bundle-to-specs`, `/crav1-ideas-to-spec`, `/crav1-spark-to-spec`, `/crav1-tighten-spec`, `/crav1-existing-to-specs`.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.61.0.

### Docs

- Data layout notes section rewritten; note and index templates; add-to-spec, dump, and meeting walkthroughs; review-pr, retire-spec, draft-spec, method, guild routing, glossary (note, notes index, source date).

### CI

- The docs job runs `notes_index.py --selftest` (build, check, migrate).

## 1.60.0 (2026-10-16)

### Kit

- New skill `/crav1-retire-spec` (cross-cutting, Keep the picture current, standalone, any time). Takes one spec out of the work. Opening question with choice words `retire` (Recommended), `merge`, `park`, `convert to note`; skipped when the wording answers; a headless or bot run with no word stops and lists the words. Always shows a summary of every change and waits for a yes. Never deletes: a moved spec leaves a one-line `Moved:` pointer at its old path.
- Retire: moves the spec to `docs/specs/retired/<slug>/` with `Retired: date, reason`, removes the feature-index row, and lists inbound links to fix. Every spec-scanning skill skips `docs/specs/retired/`.
- Merge: a named target, or only real fits with a reason each (shared feature area, overlapping requirements, same system in landscape, links), best first marked (Recommended); none fits says `no good merge fit found` and offers park, retire, or convert to note. Content, open questions, and decisions move over marked `(from <slug>)`.
- Park: a `Parked: date, reason` line in place. `/crav1-plan-from-spec`, `/crav1-build-tasks`, `/crav1-build-features`, and the push branches of `/crav1-ado-sync` skip it; `/crav1-help` and `/crav1-show-or-ask-open-questions` list it as parked with the count of waiting notes. Un-park (`/crav1-retire-spec un-park`) re-reads each waiting note in full, suggests what fits now, and adds the spec to `Used by`.
- `/crav1-add-to-spec`: input that matches a parked spec is saved once in full as a note with `Waiting for <slug> (parked)`. Active matching specs get their points plus a `Full source:` link and join `Used by`. The parked spec gets nothing written. Such notes are never absorbed. Open questions shows them as `waiting for parked <slug>`, not open work.
- Convert to note: writes `docs/notes/<date>-<slug>.md` with a `Source:` line and an index row, one line under `## How the parts connect` in landscape, and removes the feature-index row. A converted note has no research owner, so no revisit request.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.60.0.

### Docs

- New walkthrough [Retire, merge, park, or convert a spec](docs/from-retire-spec.md); skills reference page; guild routing (cross-cutting); docs index; README; glossary (parked spec, retired spec, pointer, waiting note); `workflow.yaml` override (no next step).

## 1.59.0 (2026-10-16)

### Kit

- New skill `/crav1-explain-this-code` (cross-cutting, Keep the picture current, standalone, any time). Explains a file, a function, a selection, or a PR diff, and asks what to explain when none is named. Opening question with choice words `what it does` (Recommended), `what and why`, `teach the language`; skipped when the wording answers; a headless or bot run with no word stops and lists the words. Reads only the code and the code it calls and never guesses. What and why takes reasons only from the code, specs, plan decisions, system notes, and commits, else `no stated reason found`. Teach the language adds idiom notes, a one-line comparison to a language the user knows, and topics to look up next. Every answer has a small mermaid flowchart built from what was read. Read-only, in chat; nothing is written to `docs/` or the kit layout.
- Save as .md: offered at the end. After showing the full path and asking, it writes `explain-this-code-<target>-<date>.md` to `~/Downloads` (`%USERPROFILE%\Downloads` on Windows) or a path the user names, never into the repo by default. The header names the paths covered and `<branch>@<short sha>`. The kit never reads or indexes it.
- `/crav1-help` names it apart from `/crav1-explain-existing-system` and compares the two.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.59.0.

### Docs

- New walkthrough [Explain this code](docs/from-explain-this-code.md); skills reference page; guild routing (cross-cutting); docs index; README; glossary (saved explanation); `workflow.yaml` override (no next step).

## 1.58.0 (2026-10-16)

### Breaking

- The 30 deprecated alias folders from 1.56.0 are removed (for example `/crav1-complete-task`, `/crav1-tasks-to-ado`, `/crav1-verify-spec`). Old names no longer run. Use the new name with its choice word, for example `/crav1-ado-sync push tasks`. The old-to-new table stays in the [docs index](docs/README.md#renamed-skills-1560), and `/crav1-help <old name>` answers "renamed to X, removed in 1.58.0".
- The walkthrough redirect notes at the old `docs/from-*.md` paths are removed.

### Kit

- Recommended option: any question with options that has a recommendation lists that option first and ends its label with ` (Recommended)`, for example `Note (Recommended)`. The question no longer also says `Recommendation: X`. The rule is in `crav1.mdc` and `CLAUDE.md`, and covers the merged skills' opening questions, keep/leave/dismiss/note, keep or redact and image options in the imported-sources check, suggested patch letters in tighten-spec and tighten-plan, and the create-feature-branch choice.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.58.0.

### Docs

- Guild routing (Recommended option), glossary (recommended option; alias entry removed), data policy, data layout, help walkthrough, README, CONTRIBUTING.md item 9, and `kit-maintainer.mdc`.

### CI

- `aliases` is gone from `skills.yaml`; `scripts/gen-skill-docs.py` no longer validates aliases or generates a Renamed skills section in the reference.

## 1.57.0 (2026-10-14)

### Kit

- Choice words for bots and scripted runs (no `--flags`). Every merged skill lists exact words for each option:
  - `/crav1-build-tasks`: `one task` / `range` / `all tasks`
  - `/crav1-fix-build-gaps`: `verify gaps` / `live gaps`
  - `/crav1-add-to-spec`: `fact` / `dump` / `code change` / `meeting`
  - `/crav1-ado-sync`: `suggest features` / `push features` / `push tasks` / `pull tasks` / `pull spec changes`
  - `/crav1-existing-to-specs`: `repos only` / `repos and bundle`, then `one spec` / `spec per feature`
  - `/crav1-finalize-commit`: `commit` / `message only`
  - `/crav1-show-or-ask-open-questions`: `show` / `ask`
- A word in the invocation takes that choice without asking, also for a bot or a headless run. A headless or bot run with no word stops and names the valid words instead of guessing.
- Aliases pass their choice word (for example `/crav1-tasks-to-ado` runs `/crav1-ado-sync push tasks`).
- Cleanups from 1.56.0: inside the merged skills' branches, references to sibling skills now name the branch in plain words (for example "the fact branch of `/crav1-add-to-spec`"), and the handoff headings in `/crav1-add-to-spec` name their branch. The build-task agent names the full `branches/one-task/references/run.md` path and the implement step.
- The `/crav1-add-to-spec` description again mentions Used by / Absorbed by on notes and the revisit-request draft.
- `/crav1-help <skill>` shows a merged skill's choice words.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.57.0.

### Docs

- `choice_words` in `skills.yaml`, a Choice words section on each merged skill's reference page, a choice-words table in guild routing, the glossary (choice word), the help walkthrough, the renamed-skills table, CONTRIBUTING.md item 9, and `kit-maintainer.mdc`.

### CI

- `scripts/gen-skill-docs.py --check` fails when a choice word is missing from its `SKILL.md`, or when an alias passes a word the new skill does not list.

## 1.56.0 (2026-10-14)

Skill names now say what each skill does, and related skills are merged. Old names keep working as aliases until 1.58.0.

### Kit

- Merged skills open with a question with options, not flags. The question is skipped when the message already answers it, and an old alias jumps straight to its choice. Each old skill's rules are kept verbatim as `branches/<id>/BRANCH.md` inside the merged skill.
- `/crav1-build-tasks` always runs each task in a worker. It asks one task, a range, or all, lists the ready ones, and ends at `/crav1-open-pr`.
- `/crav1-show-or-ask-open-questions` has a new read-only Show: every open question across the specs, with Asked, Pending, and who.
- `/crav1-finalize-commit` asks commit, or only write the message.
- Starter options are now six: `/crav1-existing-to-specs` covers repos only and repos plus a bundle.
- Subagents: `crav1-complete-task-agent` → `crav1-build-task-agent`, `crav1-architecture-reviewer-agent` → `crav1-review-architecture-agent`, `crav1-intake-slice-agent` → `crav1-bundle-slice-agent`.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.56.0.

| Old name | New name | Alias pre-answers |
| --- | --- | --- |
| `/crav1-implement-task` | `/crav1-build-tasks` | one task (the worker follows the implement branch) |
| `/crav1-complete-task` | `/crav1-build-tasks` | one task |
| `/crav1-complete-tasks` | `/crav1-build-tasks` | a range or all |
| `/crav1-complete-features` | `/crav1-build-features` | — |
| `/crav1-verify-spec` | `/crav1-verify-build-against-spec` | — |
| `/crav1-fix-from-verify` | `/crav1-fix-build-gaps` | verify report gaps |
| `/crav1-fix-live` | `/crav1-fix-build-gaps` | live-site gaps |
| `/crav1-match-dump-to-specs` | `/crav1-add-to-spec` | a dump |
| `/crav1-code-into-specs` | `/crav1-add-to-spec` | a code change |
| `/crav1-meeting-to-specs` | `/crav1-add-to-spec` | a meeting |
| `/crav1-feature-candidates` | `/crav1-ado-sync` | suggest Features |
| `/crav1-specs-to-ado` | `/crav1-ado-sync` | push Features |
| `/crav1-tasks-to-ado` | `/crav1-ado-sync` | push tasks |
| `/crav1-ado-to-tasks` | `/crav1-ado-sync` | pull tasks |
| `/crav1-ado-to-specs` | `/crav1-ado-sync` | pull spec changes |
| `/crav1-match-to-specs` | `/crav1-existing-to-specs` | repos plus a bundle (the second question is still asked) |
| `/crav1-repos-to-spec` | `/crav1-existing-to-specs` | repos only, one spec |
| `/crav1-intake-to-specs` | `/crav1-bundle-to-specs` | — |
| `/crav1-architecture-reviewer` | `/crav1-review-architecture` | — |
| `/crav1-resolve-questions` | `/crav1-resolve-open-questions` | — |
| `/crav1-ask-open-questions` | `/crav1-show-or-ask-open-questions` | ask |
| `/crav1-draft-commit-message` | `/crav1-finalize-commit` | only write the message |
| `/crav1-explain` | `/crav1-explain-existing-system` | — |
| `/crav1-whats-known-about` | `/crav1-what-do-we-know-about-this` | — |
| `/crav1-keep-current` | `/crav1-refresh-system-notes` | — |
| `/crav1-pipeline-environments` | `/crav1-map-pipeline-environments` | — |
| `/crav1-security-review` | `/crav1-review-security` | — |
| `/crav1-environment-read` | `/crav1-read-environment` | — |
| `/crav1-exploratory-test` | `/crav1-run-exploratory-test` | — |
| `/crav1-feature-branch` | `/crav1-create-feature-branch` | — |

Unchanged: spark-to-spec, ideas-to-spec, tighten-spec, plan-from-spec, review-plan, tighten-plan, fix-bug, help, tasks-ready-to-build, export-spec, suggest-tests-for-code, open-pr, review-pr, merge-pr. `/crav1-add-to-spec` keeps its name and is the fact choice.

### Alias removal plan

- 1.56.0 and 1.57.0: every old name is a deprecated alias (`aliases` in `skills.yaml`, `deprecated: true`). It says it was renamed and hands off.
- 1.58.0 (breaking): the alias folders and the walkthrough redirect notes are removed. Update saved prompts, rules, and scripts to the new names before then.

### Docs

- Walkthroughs renamed to the new names, with a redirect note at each old path. Glossary (alias, branch, opening question), data layout, guild routing, the README skills table, CONTRIBUTING.md item 9, `kit-maintainer.mdc`, and `/crav1-help` (an old name, or `help renamed`) are updated. The skills reference has a Renamed skills table.

### CI

- `scripts/gen-skill-docs.py --check` validates every alias: `deprecated: true`, `remove_in`, a real `renamed_to`, `disable-model-invocation: true`, and a hand-off line.

## 1.55.0 (2026-10-14)

### Kit

- `/crav1-help` has five more modes, all local, cited, and re-read on pushback:
  - Concept: `help work item homes`, `marks.md`, `stale marks`, from the glossary and `docs/concepts/`.
  - `list` shows every skill by lane and phase; `list <lane>` shows one lane, from `skills.yaml` and guild routing.
  - `status <slug>` or `where am I`: task counts with the `/crav1-tasks-ready-to-build` rules, the route step the slice is on, and the next step from `workflow.yaml`. It points to tasks-ready-to-build for the per-task list.
  - `compare A B` or `difference between A and B`, from `skills.yaml` and the reference pages.
  - `whats new` for the installed version, or `whats new since x.y`, from the bundled `CHANGELOG.md`.
- The usage guide (no input) lists every mode with an example.
- `CHANGELOG.md` is now bundled in every `crav1-docs/` copy.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.55.0.

### Docs

- [Ask the kit for help](docs/from-help.md) lists the new modes; the help reference, CONTRIBUTING.md item 8, and `kit-maintainer.mdc` are updated.

### CI

- The sync job fails when `crav1-docs/CHANGELOG.md` differs from `CHANGELOG.md` in any copy.

## 1.54.0 (2026-10-14)

### Kit

- New `/crav1-tasks-ready-to-build` (cross-cutting, read-only), at Rhea's request. For one slice or all, it shows summary counts, then Ready, Blocked (one reason each, recorded or inferred), Needs verify, a Done count, `Next: /crav1-implement-task T#`, and a `Source:` line. It can run any time. It never reads Azure Boards and names `/crav1-ado-to-tasks` for task states there.
- Rules: a ticked task is Done only when `verify.md` lists it as verified, otherwise Needs verify. A missing `plan.md` blocks. A kept-open question blocks the tasks its `Blocks:` line names, or the whole slice when it has none (inferred); a plan Risk that says do not implement until resolved blocks the whole slice (inferred). A task waits on its `(after: T#)` tasks, or on every earlier unticked task when none is recorded (inferred). An unknown plan review gives a warning to run `/crav1-review-plan`, not a block.
- New marks: `/crav1-review-plan` writes `Reviewed: <date>, P# open: <n>` under the plan title, and `/crav1-tighten-plan` lowers the count. `/crav1-plan-from-spec` writes optional `(after: T#)` on task lines and `Blocks: T#` under kept-open questions it parks as risks (its one exception to leaving `spec.md` alone). `/crav1-resolve-questions` asks which tasks a kept-open question blocks and writes `Blocks: T#`.
- `workflow.yaml`: tasks-ready-to-build is an optional step before build in the New slice and New information routes. `/crav1-help` says it can run any time, in its next answers and its skill answer.
- Templates: `plan.md` has a comment for the `Reviewed:` line, `tasks.md` shows `(after: T1)`.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.54.0.

### Docs

- New walkthrough [Tasks ready to build](docs/from-tasks-ready-to-build.md). [Data layout](docs/concepts/data-layout.md) has Readiness marks and `Blocks:` in open question marks; the [glossary](docs/concepts/glossary.md) has ready and blocking. The plan and draft walkthroughs, help, guild routing (Cross-cutting), and the docs index name the new marks and command. The `crav1-docs/` copies are updated.

## 1.53.0 (2026-10-14)

### Kit

- Every install now carries the kit docs next to the skills in a `crav1-docs/` folder: `.cursor/skills/crav1/crav1-docs/` (Cursor drop-in), `plugins/crav1/skills/crav1-docs/` (plugin), and `.claude/skills/crav1-docs/` (Claude Code drop-in, also `~/.claude/skills/crav1-docs/`). It is not a skill.
- `/crav1-help` reads `../crav1-docs/` from its own folder in every install, after the kit repo's own `docs/`. Only when that folder is missing does it answer from the skill files alone. On a drop-in, the newer-version notice reads the `Kit version:` line in `reference/workflow.md`.
- The plugin's `docs/` folder from 1.52.0 is replaced by `skills/crav1-docs/`.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.53.0.

### Docs

- Install, [Ask the kit for help](docs/from-help.md), guild routing, the plugin README, CONTRIBUTING.md item 8, and the help reference name `crav1-docs/`. [Workflow routes](docs/reference/workflow.md) states the kit version.

### CI

- The sync job fails when any of the three `crav1-docs/` copies differs from `docs/`, or when `plugins/crav1/docs/` exists. `scripts/gen-workflow.py --check` fails when the kit version on the workflow page differs from `plugin.json`.

## 1.52.0 (2026-10-14)

### Kit

- New `/crav1-help` (cross-cutting). Called with nothing, it shows a usage guide with example questions. With a skill name, it says what the skill does, when to use it, what it reads and writes, and its before and after steps. With `next` or a situation, it gives the route in order from `docs/reference/workflow.yaml`, marking each step from the slice's file state (open questions, `plan.md`, ticked tasks, `verify.md`, `work-item.md`). Other questions are answered from the docs, or with "the kit doesn't say". Every answer ends with `Source: <file>#<anchor>`. On pushback it re-reads the file and does not change the answer from memory.
- Help is local only: the kit repo's `docs/`, else the `docs/` bundled in the installed plugin. It never fetches answers from GitHub. When online, it reads the tag names once and says when a newer version is tagged.
- New `docs/reference/workflow.yaml` is the one written source for the order, with five routes: New slice, New information on an existing slice, Bug, Outside pull request, and Azure Boards sync. `scripts/gen-workflow.py` generates `docs/reference/workflow.md`, the order block in `crav1.mdc`, and every `you_run_next` in `skills.yaml`.
- `crav1.mdc` (and the plugin and Claude Code copies) now says: before you suggest more than one next step, or when the user questions an order, call `/crav1-help` and quote its answer with its source. Never give an order from memory.
- Order fixes: `/crav1-meeting-to-specs` and `/crav1-add-to-spec` name `/crav1-tighten-spec` before `/crav1-resolve-questions` after new information. Spark, ideas, and intake share the New slice route (optional feature branch and architecture review, then tighten). The complete skills verify inside their worker and go to `/crav1-open-pr`; implement-task goes to `/crav1-verify-spec`. The Azure Boards steps (specs-to-ado, tasks-to-ado) are in the order. `/crav1-merge-pr` names `/crav1-keep-current` after an outside pull request.
- The plugin now bundles the kit's `docs/` as `plugins/crav1/docs/`, so each release carries its own docs.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.52.0.

### Docs

- New walkthrough [Ask the kit for help](docs/from-help.md), the generated [Workflow routes](docs/reference/workflow.md) page, a glossary entry for route, help in guild routing (Cross-cutting) and the docs index, and the tighten-spec step in the meeting and add walkthroughs. Install and the plugin README say the plugin bundles `docs/`.

### CI

- `scripts/gen-workflow.py --check`: route skills exist, `you_run_next` matches the routes, the `crav1.mdc` order block matches, the workflow page is current, the `/crav1-help` rule is in `crav1.mdc`, its plugin copy, and `CLAUDE.md`, and walkthrough `## After` sections name only skills that `workflow.yaml` names.
- The sync job fails when `plugins/crav1/docs/` differs from `docs/`.

### Docs (PR 80)

- [From a pull request review](docs/from-review-pr.md) now covers the paste-ready comment, the comment style Thomas and Rhea agreed on (the default), posting after a yes, the verdict question, re-review, and the `review-pr-<repo>-<n>-follow-ups.md` name for the follow-ups note.
- The [glossary](docs/concepts/glossary.md) and [data layout](docs/concepts/data-layout.md) explain work item homes: the `Work items go to` column in `docs/system/repos.md`, one Feature per home, `(ADO: <org>/<project>)` on `work-item.md` id lines, and `Jira:` reserved. The data layout also lists the review follow-ups note.
- "Documented is part of done" now covers changes to existing skills too: update that skill's walkthrough and its glossary or data layout entries in the same pull request ([CONTRIBUTING.md](CONTRIBUTING.md) item 6, `kit-maintainer.mdc`).

### CI (PR 80)

- New check `scripts/check-skill-docs-touched.py` (workflow `skill-docs-touched.yml`) fails a pull request that changes any copy of a `SKILL.md` without a docs change for that skill outside `docs/reference/`. Opt out with the `docs-not-needed` label or a `Docs-not-needed: <reason>` line in the pull request body.

## 1.51.0 (2026-10-14)

### Kit

- `/crav1-review-pr`: follow-ups are no longer posted or pasted. The paste-ready block and the posted Azure DevOps or GitHub output (inline comments and summary) have only Blocker, Bugs, and Tests to add with this PR.
- Follow-ups, including choices the description calls deliberate, are saved as `docs/notes/review-pr-<n>-follow-ups.md` in the existing notes format: the PR, the repo, the date, and each follow-up with its file and line (paths kept, since the note stays in the specs repo), plus an `open` row in `docs/notes/index.md`. They come back through the note flow: `/crav1-feature-candidates` reads open notes, and specs mark them Used by or Absorbed by.
- The chat review still lists the follow-ups and says where the note was saved. A re-review updates the same note. No follow-ups, no note. When the specs repo is not in the workspace, the note is printed in the chat instead.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.51.0.

### Docs

- [From a pull request review](docs/from-review-pr.md) has a Follow-ups section, and the reference page describes the note.

## 1.50.0 (2026-10-14)

### Kit

- Work item homes per repo. New `crav1-specs-to-ado/references/work-item-homes.md`. The specs repo stays the source of truth and is not tied to a tracker; each implementation repo has its own home in a new `Work items go to` column of `docs/system/repos.md` (`ADO: <org>/<project>`; `Jira: <project>` reserved, nothing built). One home holds 1–N repos. The specs repo never has one.
- The home is asked the first time a skill needs it: the repo's own ADO project (suggested), every other project `az` can read, "same for all N new repos", or a typed answer. Headless runs use the two-pass questions file. Written only after the answer; changed only by editing the row. The repos and intake skills and every `repos.md` template add the column empty.
- `/crav1-specs-to-ado`: a spec whose repos are in several homes gets one Feature per home, each with only its own repos, each previewed and sent on its own yes, linked as Related in the same org or mentioned in plain text across orgs. A No spec yet row is asked its home too and records it in the Id cell.
- `/crav1-tasks-to-ado`: a task goes to its repo's home, parented to the Feature in that home. No clear repo asks once (suggesting the spec's main repo); repos in different homes ask split or pick. Child type and done state are saved per home: `Azure Boards task type (<project>): <type>`.
- `work-item.md` id lines end with `(ADO: <org>/<project>)`. Older lines are read as the marks.md org and project and get the tag on the next write without asking.
- `/crav1-ado-to-specs`, `/crav1-ado-to-tasks`, and `/crav1-whats-known-about` read each id in its own home; one not found is reported as moved or missing, and the kit asks before searching other projects.
- `work-item-mention.md` (commit drafts, `/crav1-open-pr` on Azure DevOps) strips the home tag and mentions only lines in the home of the repo being committed to.
- `docs/environments/marks.md` keeps the org; its project is only the fallback suggestion. Unchanged: nothing goes to ADO without a yes, Iteration and Priority blank, repo names kept and paths stripped, v1.48 State handling.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.50.0.

### Docs

- [From specs to Azure Boards](docs/from-specs-to-ado.md) has a Work item homes section; [From tasks to Azure Boards](docs/from-tasks-to-ado.md), [From Azure Boards to tasks](docs/from-ado-to-tasks.md), [Environment marks](docs/environments-marks.md), [From named repos](docs/from-repos.md), the `repos.md` template, and the reference pages describe homes.

## 1.49.0 (2026-10-13)

### Kit

- Local test dependency preflight. New `crav1-verify-spec/references/test-dependencies.md`: before any test command, detect the local dependencies the repo's tests, config, compose files, and README name (Azurite, database containers, Cosmos DB and other emulators), check each is running, and ask start (the repo's documented command or a default such as `azurite` or `docker compose up -d <service>`), skip the tests that need it, or stop.
- A test skipped for a missing dependency blocks verified. `/crav1-verify-spec` marks the task Claimed done, unverified and `/crav1-implement-task` leaves the box open, unless the user chose skip; then `verify.md` lists those tests under a new **Skipped tests** section with the dependency and why. Skips the preflight missed in the test output are treated the same way.
- Headless runs use the two-pass questions file in the system temp folder, and the missing dependency is a `BLOCKER:` line at the top of the summary.
- `/crav1-fix-from-verify` runs the preflight before re-proving a gap. The complete-task worker returns `STATUS: needs_dependency` with `resume: dependency-start` / `dependency-skip`; `/crav1-complete-task`, `/crav1-complete-tasks`, and `/crav1-complete-features` ask start, skip, or stop.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.49.0.

### Docs

- [Verify and fix](docs/from-verify.md) has a Local test dependencies section; [Build tasks](docs/from-plan-to-build.md) and the reference pages describe the preflight.

## 1.48.0 (2026-10-13)

### Kit

- `/crav1-tasks-to-ado` handles State. A ticked task is created in the done state, an open one as New. On an update, a box ticked since the item was sent offers moving it to the done state, and an unticked box on a closed item offers a reopen to New, each sent only on its own yes. A disagreement the `tasks.md` history does not explain shows both sides and asks each time. The kit never sets Active or Resolved and never sends Reason; Priority and Iteration stay unsent.
- The done state is the project's own name (Closed on Agile, Done on Scrum and Basic), read with the work item types (new call in `references/child-items.md`) and saved as `Azure Boards task done state: <state>` in `docs/environments/marks.md`. A project with only the type line gets the done-state line on the next run without a question.
- `/crav1-ado-to-tasks` uses that done state: done in Azure Boards ticks the box on a yes, reopened in Azure Boards unticks a ticked box on a yes, and an in-progress state is not shown as a difference. It still writes nothing back.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.48.0.

### Docs

- [From tasks to Azure Boards](docs/from-tasks-to-ado.md), [From Azure Boards to tasks](docs/from-ado-to-tasks.md), [Environment marks](docs/environments-marks.md), and both reference pages describe the State handling.

## 1.47.0 (2026-10-13)

### Kit

- `/crav1-tasks-to-ado`: the child type question now gives a recommendation. It reads the project's process and backlog levels (new calls in `references/child-items.md`) and puts the type on the requirement backlog level directly under Feature first, marked `(Recommended)` with one plain reason: User Story on Agile (a Task belongs under a User Story), Product Backlog Item on Scrum, Issue on Basic, Requirement on CMMI, or the inherited process's own requirement type. Bug is recommended only when the team tracks bugs as requirements. When the levels cannot be read, it says so and gives no recommendation. Before, it listed `Task` first with no mark.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.47.0.

### Docs

- [From tasks to Azure Boards](docs/from-tasks-to-ado.md), [Environment marks](docs/environments-marks.md), and the reference page describe the recommendation.

## 1.46.0 (2026-10-13)

### Kit

- New skill `/crav1-ado-to-tasks` (cross-cutting, later skill, not a starter). Pick a spec with task lines in `work-item.md`, or all. Every recorded task item is read back (State, title, description, acceptance, Assigned To, comments, history) and only what differs from the spec and `tasks.md` is shown, plus child items under the Feature that no task line records. Each difference is kept or dismissed, fresh every run; kept changes go in through `/crav1-add-to-spec`. A task Done in Azure Boards ticks its box only on a yes; a new child is added as a task and recorded in `work-item.md` only on a yes. It never writes a field back; reply comments are stripped and posted only on a yes.
- Work-item mentions (`work-item-mention.md`, used by `/crav1-draft-commit-message`, `/crav1-finalize-commit`, and `/crav1-open-pr`): task lines `Work item: <id> — task: T<n> …` were read as ordinary labelled lines, so a file with a Feature line and task lines asked between all of them and could mention only a task id. Task lines are now their own kind. The mention keeps the Feature id; a task id is added after it only when the change clearly implements one recorded task, the skill asks when unclear, and a task id is never the only mention. `/crav1-feature-candidates`, `/crav1-specs-to-ado`, and `/crav1-ado-to-specs` no longer treat task lines as Feature ids.
- `/crav1-tasks-to-ado` names `/crav1-ado-to-tasks` as the later read-back.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.46.0.

### Docs

- New walkthrough [From Azure Boards to tasks](docs/from-ado-to-tasks.md) and reference page, linked from the docs index, [From tasks to Azure Boards](docs/from-tasks-to-ado.md), the [data layout](docs/concepts/data-layout.md) (task lines and mentions), and guild routing.
- New walkthrough [From tasks to Azure Boards](docs/from-tasks-to-ado.md) for `/crav1-tasks-to-ado`, with a generic task example. Linked from the docs index, the skill's reference page, [From specs to Azure Boards](docs/from-specs-to-ado.md), the [data layout](docs/concepts/data-layout.md) (task lines in `work-item.md`), [Environment marks](docs/environments-marks.md) (the task type line), and the plugin README.

## 1.45.0 (2026-10-13)

### Kit

- New skill `/crav1-tasks-to-ado` (cross-cutting, later skill, not a starter). Pick one spec that already has a Feature id in `work-item.md`; every task in its `tasks.md` is listed and you pick by number or all. The child work item type is asked once and saved as `Azure Boards task type: <type>` in `docs/environments/marks.md`. Each task is previewed (Create or Update #id, only changed fields on an update) in the Feature layout: fuller title, State New, Iteration and Priority blank, slice and code repo tags, owner when stated, fuller description with decisions, quotes, names, and dates, open blockers or none recorded, and the verify line as acceptance. Paths, line numbers, spec references, and kit names are stripped; code repo names stay; the specs repo is never mentioned. Created only after a yes, as a child of the Feature, and recorded as `Work item: <id> — task: T<n> <short title>` in `work-item.md` (never in `tasks.md`). Uses the same `az` checks as `/crav1-specs-to-ado`, plus a new `references/child-items.md`.
- `/crav1-specs-to-ado` names `/crav1-tasks-to-ado` as the next step in its report and does not run it.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.45.0.

### Docs

- New reference page for `/crav1-tasks-to-ado`, the skills table, and guild routing updated.

## 1.44.0 (2026-10-13)

### Kit

- `/crav1-review-pr` comment style (agreed by Thomas and Rhea, 2026-10-12) for the paste-ready block, posted comments, and re-review replies: the user's own friendly first-person voice, the source kept vague ("me and my checks", never a tool, skill, or bot), a varied opening every time, soft wording with the same information, and the description read first so deliberate choices are acknowledged and moved to Follow-ups. The sections are now Blocker, Bugs, Tests to add with this PR, and Follow-ups (not for this PR), replacing blocking / should fix / nit. Each file links to the pull request files view (GitHub or Azure DevOps) with per-line remarks usable as inline comments. Posting on yes, the summary without the verdict line, the verdict options, and the re-review statuses are unchanged.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.44.0.

### Docs

- The review-pr reference page describes the comment style.

## 1.43.0 (2026-10-13)

### Kit

- Imported sources (`crav1-add-to-spec` `references/sources.md`, used by add-to-spec, intake, match, match-dump, and meeting): the transfer data policy is one shared policy for Cursor and Claude Code, written as both copies together and copied across when only one exists (conflicting copies: the user picks). Temporary files go to the system temp folder and are deleted even on failure. An image the kit cannot view is never guessed at: it is left out and flagged for Rhea or the user to check. New two-pass headless mode (questions to a temp file, answers on a second run). Partial extracts get a "Left out" list. Black-boxed PDF text is treated as redacted (`[redacted in source]`). Superseded versions are kept and marked "Superseded by"; only the newest is read. Source precedence: newest decided source wins, otherwise an open question, with a conflict pass after a multi-file intake. Plain uncontested facts are applied without asking and listed in the run summary. One folder per document. Ambiguous dates are never guessed. `.docx` tracked changes are accepted but flagged and comments listed with author and date. Exact duplicate images are stored once. New glossary terms are added freely; rewriting an existing row needs a yes.
- `/crav1-review-pr` ends with a paste-ready Markdown comment (verdict, findings by severity with file and line, suggested fix, no kit-internal details, English by default). After the user's yes it posts each finding as an inline comment on its line and a summary without the verdict line, then offers the verdict options (approve, comment, request changes). A re-review reads earlier findings from the pull request's threads and marks each Fixed (with the commit), Partly fixed, Still open, or No longer relevant, flags resolved-but-still-open threads, replies in existing threads, and resolves threads only after a yes.
- `/crav1-feature-candidates` uses the hand-made layout: titles that say what the work is, fixed labelled lines per candidate (Target date with source, Spec, Description, Open blockers/questions, Order/priority), and fuller descriptions with context, owners, related tasks, and dated quotes, with no invented facts.
- `/crav1-specs-to-ado` strips spec paths, `docs/sources/` folders, and spec references from the candidate text before the preview.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.43.0.

### Docs

- [Data policy](docs/concepts/data-policy.md): the shared policy and how imports handle the hard cases. Skill reference pages regenerated for review-pr, feature-candidates, and specs-to-ado.

## 1.42.0 (2026-10-11)

### Kit

- The always-on project instruction (`.cursor/rules/crav1.mdc`, the plugin copy, and the generated `.claude/CLAUDE.md`) is cut from about 5,150 words to about 650: standing rules plus pointers: the layout and `Synced at` rules, the seven starter options, the typical order, six standing rules that hold for every skill, and links to the skills reference and the data layout. The per-skill text it repeated already lives in each skill's `SKILL.md` and on its reference page.
- `/crav1-implement-task` and `/crav1-complete-task` now say in their own `SKILL.md` that they do not ask whether to run `/crav1-keep-current`. The project instruction said this before; the behavior is unchanged.
- [CONTRIBUTING.md](CONTRIBUTING.md) and the maintainer rule: a new skill is done only when it is documented (its `skills.yaml` entry and reference page, a walkthrough that links back, a docs index line for a new page, and a CHANGELOG entry). The maintainer rule also says the project instruction stays standing rules plus pointers.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.42.0.

### Docs

- The [README](README.md) is now a short landing page: what the kit is, the seven starter options with links to their reference pages and walkthroughs, a lane diagram, and one pointer to the docs index.
- New [docs index](docs/README.md), grouped by type (tutorial, how-to, reference, explanation) and by reader (spec writer, developer, guild bot, maintainer). It is the one map of every page. [docs/install.md](docs/install.md) and [docs/first-run.md](docs/first-run.md) point at it instead of keeping their own long lists.
- New [docs/concepts/](docs/concepts/): [the method](docs/concepts/method.md) (how the pieces fit together, the starting points, the working loop, setup, best practices, and minimal templates, moved from the README), [data layout](docs/concepts/data-layout.md) (every folder and file, who writes it, notes, sources, research stale marks, open question marks, `work-item.md`, and the spec sections the kit looks for), a [glossary](docs/concepts/glossary.md), and the [data policy](docs/concepts/data-policy.md) for personal data and secrets in imported sources.
- The README's per-skill paragraphs and its "already ships" list moved into a new `in_depth` field in [`docs/reference/skills.yaml`](docs/reference/skills.yaml), shown under Purpose on each skill page. The README's per-lane tables are gone; the [skills reference](docs/reference/skills.md) has them.
- [plugins/crav1/README.md](plugins/crav1/README.md) uses full GitHub links and points at the skills reference instead of its own per-skill list.
- The Skills row in [docs/install.md](docs/install.md) links to the skills reference instead of describing every command.
- Five walkthroughs for the core loop after a starter: [From a draft spec to an accepted spec](docs/from-draft-spec.md) (architecture-reviewer, tighten-spec, resolve-questions, feature-branch), [From a spec to a plan](docs/from-spec-to-plan.md) (plan-from-spec, review-plan, tighten-plan), [Build tasks](docs/from-plan-to-build.md) (implement-task, complete-task, complete-tasks, complete-features), [Verify and fix](docs/from-verify.md) (verify-spec, fix-from-verify, fix-live), and [From commit to merge](docs/from-commit.md) (draft-commit-message, finalize-commit, open-pr, merge-pr).
- New walkthrough [Ask open questions](docs/from-ask-open-questions.md) for `/crav1-ask-open-questions`, including the `Pending:` and `Asked:` marks it writes. Every skill except `/crav1-export-spec` (reference only) now has a walkthrough.
- [Feature candidates](docs/from-feature-candidates.md), [From specs to Azure Boards](docs/from-specs-to-ado.md), and [From Azure Boards to specs](docs/from-ado-to-specs.md) follow the same outline as the other walkthroughs: First prompt, Steps, What gets written, After.
- Every walkthrough links to the reference page of each skill it covers, and each reference page links to its walkthrough through the `walkthrough` field in `skills.yaml`. `scripts/gen-skill-docs.py --check` fails when a walkthrough does not link back.
- [From a meeting to specs](docs/from-meeting.md) no longer names specific meeting or chat tools.

## 1.41.0 (2026-10-11)

### Kit

- New data file [`docs/reference/skills.yaml`](docs/reference/skills.yaml) holds every skill and subagent: lane, group inside the lane, starter flag, use when, what it reads and writes, what it leaves alone, its exceptions, who calls it, what it calls, what you run next, its walkthrough, the release it first appeared in, and a first prompt. It was seeded from the behavior map and the README skills table and covers all 42 skills and 5 subagents.
- New generator `scripts/gen-skill-docs.py` writes [`docs/reference/skills.md`](docs/reference/skills.md) (one table grouped by lane, Starters, Specify, Plan, Build, and Cross-cutting, with the README phases as groups inside the lanes, plus a table of all five subagents) and one page per skill under `docs/reference/skills/`. Columns: Command (linked to its page), Starter, Use when, Reads, Writes (every side effect), You run next, Runs by itself, and Walkthrough. Each page has Purpose, Runs when, Reads, Writes, Does not, You run next / Runs by itself, Lane and group, Stage and since, First prompt, and Walkthrough.
- CI runs `scripts/gen-skill-docs.py --check` (generated pages match the YAML, every skill folder and subagent is in it, lanes match the guild-routing map) and the new `scripts/check-kit-docs.py` (every skill description in the three trees is within 1,024 characters, and `plugin.json` equals the newest CHANGELOG release heading). Both need PyYAML.
- The behavior map moved out of `.cursor/rules/kit-maintainer.mdc` into the reference. The maintainer rule now points at `docs/reference/` and says a new or changed skill updates `skills.yaml` and regenerates. `plugin.json` is 1.41.0 and follows the release tag from now on.

### Docs

- Stale claims fixed. `/crav1-meeting-to-specs` has four choices (keep, leave, dismiss, or note) and `/crav1-match-dump-to-specs` has four piles (belongs, already in, note, does not fit) in the README and [docs/install.md](docs/install.md). The README "already ships" list now has `/crav1-meeting-to-specs`, `/crav1-ask-open-questions`, `/crav1-feature-candidates`, `/crav1-specs-to-ado`, and `/crav1-ado-to-specs`. The README minimal plan template has `## Linter`, the same as `docs/specs/_template/plan.md`. The README layout block lists `docs/architecture/`, `docs/environments/`, `docs/notes/`, `docs/sources/`, `docs/research/`, and the extra files in a spec folder.
- The project instruction is no longer called short in the README, [docs/install.md](docs/install.md), the maintainer rule, or the catalog description.
- [docs/guild-routing.md](docs/guild-routing.md) sends the researcher's note to `docs/research/` with a line under `## Research findings`, the place every skill reads. The `docs/specs/<slug>/research.md` path is gone.
- The README skills table lists every side effect in Writes: worker code and commits for `/crav1-complete-task`, `/crav1-complete-tasks`, and `/crav1-complete-features`, the reply comment after a yes for `/crav1-ado-to-specs`, sources, stale marks, and answer links for the import skills, and the code read for a partial slice in `/crav1-tighten-spec`. The subagent table lists all five subagents.
- [plugins/crav1/README.md](plugins/crav1/README.md) lists the Plan skills under Plan, not Build, and names `/crav1-ask-open-questions` among the later skills. [docs/install.md](docs/install.md) and [docs/first-run.md](docs/first-run.md) link the walkthroughs they were missing.
- A specific git client is no longer named in the README, `AGENTS.md`, the plugin README, `from-ideas.md`, or `from-nothing.md`.
- Skill descriptions: `/crav1-complete-task`, `/crav1-complete-tasks`, and `/crav1-finalize-commit` use host-neutral wording. The six descriptions over 1,024 characters (add-to-spec, code-into-specs, keep-current, match-dump-to-specs, meeting-to-specs, repos-to-spec) are shortened with the same meaning. The plugin mirror and `.claude/` copies are regenerated.
- `plugins/crav1/.cursor-plugin/plugin.json` is at 1.40.0, so the line above about the version matching now holds. Its description and the catalog description cover the current kit.
- [CONTRIBUTING.md](CONTRIBUTING.md), [docs/install.md](docs/install.md), [docs/guild-routing.md](docs/guild-routing.md), and the README point at the skills reference instead of the behavior map.

## 1.40.0 (2026-10-11)

### Kit

- New cross-cutting skill `/crav1-ask-open-questions`. The user names a person, one spec, or a topic. It gathers the open questions on the specs for that selection. For a person, that includes questions routed via that person, for example a partner's questions that go through one contact. It drafts a mail, a meeting agenda, a chat message, or meeting questions to ask out loud in a standup, a call, or a longer meeting. Meeting questions lists every selected question, not a short cut, and has no agenda layout. The questions are numbered and grouped by topic in plain words, each with enough context to be answered. The draft never names a spec slug, a path, or a question id. The kit keeps which question came from which spec on the spec itself. The draft is in English, or in the language the user names. The personal-data and secrets check runs on the draft, the same as for other outbound text. Nothing is sent. It is a later skill. It is not a starter option.

- After the draft, the skill asks whether the questions were asked. Each option says what it does. Yes writes an `Asked:` line under each question, with the date, how, and who. No writes nothing. Pending writes a `Pending:` line with the date and who, for text copied now and sent later. On the next run, pending questions are shown first, for example `Drafted for person A on 2026-10-11 (mail), not marked as sent yet.` The user can mark them as sent, keep them pending, or drop the mark. They are not mixed silently into the new draft.

- When `/crav1-meeting-to-specs`, `/crav1-match-dump-to-specs`, or `/crav1-add-to-spec` import a mail, a transcript, minutes, or a chat, a clear answer to a spec open question is linked under that question with the quote and the source, and the question is marked answered. Meeting does not ask keep for it. Match-dump links it with the confirmed sort. An unclear or partial answer is shown as a possible answer and the question stays open. An answer that would change a spec line names `/crav1-resolve-questions`. An answer that settles a stale research point runs the existing research re-check. Matching works whether the question is asked, pending, or not marked.

- When the imported source shows a question being asked, the asked-on date is the mail's sent date, the meeting date, or the chat message's date. That replaces a pending mark, or a date from the user's yes. The user's yes date is used only when no source shows it. After a meeting, questions that got an answer are linked. The rest go back to open and keep their asked mark.

- `/crav1-resolve-questions` shows a linked answer with its source and offers it first. When the user picks an answer, the quote and source stay with the decision. The shared wording is [`.cursor/skills/crav1/crav1-add-to-spec/references/open-questions.md`](.cursor/skills/crav1/crav1-add-to-spec/references/open-questions.md).

### Docs

- [docs/guild-routing.md](docs/guild-routing.md) lists `/crav1-ask-open-questions` under Cross-cutting. The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc), [`.cursor/rules/crav1.mdc`](.cursor/rules/crav1.mdc), [AGENTS.md](AGENTS.md), the README Runnable pieces table, [docs/install.md](docs/install.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the skill and the answer links.

## 1.39.0 (2026-10-11)

### Kit

- When an updated note comes back for a stale mark, the kit also reads that note's own open questions. That is the Open questions section, and any line the note marks as needing a source or a confirmation. A question whose answer lies outside the note's owner is written on each spec whose Research findings link to the note. The question names who has the fact when the note says so. A decision is marked as a decision. The same meaning already on the spec is not written again. A question the note's owner can still answer stays in the note. This runs whether or not the mark had open points, and also when the mark clears. The end-of-run summary lists every one of those questions. The kit does not ask the user. It does not send anything. It does not commit.

- An older stale mark with no per-point lines is not one point. The kit splits it into the hits it was made from: the contradiction and answered-question lines named in the note's stale block, the spec's stale line, and the run that wrote them when that run is visible. It judges each hit. When those hits cannot be found, it judges the whole update against the original quote, and the summary says the older mark had no points. It does not rewrite that mark as a count of points.

- An open question about a spec line names the real source of the suggested wording. When the wording is in the note's owner's revisit answer, the question says so and includes that answer's date. It uses the owner's name when the note or the answer names them. When the wording is in the note, the question names that section. It does not attribute to the note what is only in the answer. The spec line stays.

- The check still does not ask the user. It still routes an open point the same four ways, and it still numbers a follow-up draft. Nothing is sent. Nothing is committed. The shared wording is [`.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md`](.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md). No new skill.

### Docs

- The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) records the note's own open questions and the split of an older mark. [docs/guild-routing.md](docs/guild-routing.md) notes the same. No new skill.

## 1.38.0 (2026-10-11)

### Kit

- The revisit request no longer says the mark is cleared when an updated note comes back. The question asks the note's owner to say, per point, resolved, partly, or not addressed, and why when it is still open. Examples are a partner who still has to confirm, a fact that is not in public sources, and a decision. The status line says the kit checks the updated note against each listed point when it comes back to `docs/research/`.

- When an updated note is written to `docs/research/` for a note with a stale mark, or the user replaces the file and points `/crav1-add-to-spec` or `/crav1-keep-current` at it, the kit judges each listed point from the update's text. It does not ask the user. Copying the note in does not clear the mark. When every point is resolved, the kit removes the stale block and the spec's stale line, and records `Cleared <date>: updated note <path or commit>.` under Research findings, with one short line per point on how it was resolved. Otherwise the mark stays and is narrowed to `Stale since <date>, N of M points open: <points>.` Resolved points are recorded with the update that resolved them.

- Each open point is routed from the owner's own reason. Research that missed it or got it wrong gets a follow-up revisit draft in the chat, for those points only, numbered `Follow-up N of this mark`. From follow-up 3 the draft says the point has been open a while and suggests a conversation instead of another note. The kit does not decide that. A fact someone else has (a partner, a customer, a document not yet read) becomes an open question on the spec, naming who can answer when the update or the note says so. It is not sent back to the owner. A decision (cost, which option) becomes an open question marked as a decision. When the update does not say why, the kit asks the owner once who can answer it. Each open point names where it waits: `waiting for the note's owner` or `open question on <slug>, waiting for <who>`. A spec line the update says to change becomes an open question with the owner's suggested wording quoted. The kit does not rewrite the spec.

- When that open question is later answered, by `/crav1-resolve-questions` or by a new source through the impact check, the kit re-checks the point and clears it when settled. The mark clears when no point is open. Keep open leaves the point. The run ends with one short summary of what was cleared, narrowed, and routed where. Everything is written in the files. Drafts only. Nothing is sent. Nothing is committed. The shared wording is [`.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md`](.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md). No new skill.

### Docs

- The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) records that the clear does not ask the user, and that `/crav1-resolve-questions` may re-check a stale point. [docs/guild-routing.md](docs/guild-routing.md) notes the same. No new skill.

## 1.37.0 (2026-10-11)

### Kit

- After a quote is kept, the impact check also covers research. `/crav1-meeting-to-specs` does this through the `/crav1-add-to-spec` handoff and does not run the check a second time. `/crav1-add-to-spec`, `/crav1-match-dump-to-specs`, and `/crav1-code-into-specs` compare the quote with notes in `docs/research/` and with `## Research findings` on the specs it touches, including notes those findings link to. Two hits are listed. A clear contradiction of a research line. A quote that answers an open question in the note or the findings. The new quote is shown next to the research line or the question. An unclear case is not marked. It stays an open question on the spec, as today.

- The research is marked only after the user says yes. The note gets a blockquote below the title and the owner line: `> Stale since <date>: <one line on what changed>. Source: docs/sources/YYYY-MM-DD-<slug>/`, or the input's source line when the quote was not imported. The note's own text is not changed. The spec's Research findings get `Stale since <date>: <one line>. See <note path>.` The skills do not commit.

- After the mark, the kit offers to draft a short revisit request in the chat for the note's owner, taken from the note. The draft names the note path and the owner, what changed, what it contradicts, a question asking the owner to revisit and whether the recommendation still holds, and the status. The kit drafts only. It does not send the request or contact anyone. When the note names no owner, it says so and drafts without one.

- When an updated note is written to `docs/research/`, or the user replaces the file and runs `/crav1-add-to-spec` or `/crav1-keep-current` pointed at it, the kit sees the stale block and asks whether the update resolves it. Yes removes the block and the spec's stale line, and records `Cleared <date>: updated note <path or commit>.` under Research findings. No leaves the mark. The skills do not commit.

- `/crav1-explain`, `/crav1-whats-known-about`, and `/crav1-feature-candidates` show a stale note as stale. `/crav1-plan-from-spec` lists stale research findings under Risks and does not block. `/crav1-tighten-spec` may name the mark as an issue. The shared wording is [`.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md`](.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md). No new skill.

### Docs

- The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) records the research check, the mark, the revisit draft, and the clear. [docs/guild-routing.md](docs/guild-routing.md) notes the same. No new skill.

## 1.36.0 (2026-10-11)

### Kit

- `/crav1-meeting-to-specs` and `/crav1-match-dump-to-specs` offer Note next to keep, leave, and dismiss. The choice is `Note — keep it in the repo without tying it to a spec yet.` Note is the recommended answer when the item is worth keeping and is not a decision, a clarification, information, or an answer for an existing spec. Exploration with no feature yet, input that may feed several features, technical debt, and general information gathering are that case. A mail that maps SQL tables and views when no spec covers it is that case. Dismiss stays for a greeting, scheduling, and thanks. There is no question after Note about what kind of note it is. Meeting still asks one item at a time and does not add an accept-all question. Match-dump still confirms the sort once. The recommendation is on that sort. Both read `docs/notes/` first. An item already noted is shown as already noted and is not written again.

- A note lives in the product repo at `docs/notes/YYYY-MM-DD-<slug>.md`, with `docs/notes/index.md`. The file has a title, a date, the quote verbatim (`From <kind> <date>.` when there is a date), a `Source:` line to `docs/sources/YYYY-MM-DD-<slug>/` when the input was imported, and an empty `## Used by`. The index line is title, date, status (`open` or `absorbed`), and used by. The folder and the index are created when missing. The templates are [docs/notes/_template/note.md](docs/notes/_template/note.md) and [docs/notes/_template/index.md](docs/notes/_template/index.md), and the same files in the skill `assets/`. The skills do not commit.

- A note is not owned by one spec. `/crav1-add-to-spec` writes `Used by <slug>` when a spec quotes a note, and updates the index. Status stays open. Many specs can be listed. `Absorbed by <slug>` only when one spec clearly takes the whole note, and only after the user says yes. Then status is absorbed. Partial use never closes the note. `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, and `/crav1-tighten-spec` do the same when they quote a note. `/crav1-feature-candidates` reads open notes as input, labelled as notes. A note is not a candidate by itself. No new skill.

### Docs

- The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) records the `docs/notes/` write, the Used by line, and the feature-candidates read. [docs/guild-routing.md](docs/guild-routing.md) notes the same. [README.md](README.md) names `docs/notes/` on the Writes cells that gained it. [docs/from-meeting.md](docs/from-meeting.md), [docs/from-match-dump.md](docs/from-match-dump.md), [docs/from-add.md](docs/from-add.md), and [docs/from-feature-candidates.md](docs/from-feature-candidates.md) name the same. No new skill.

## 1.35.0 (2026-10-10)

### Kit

- For a mail, each embedded image, inline or attached, is listed before the source folder is written. The same four options as a separate binary file apply to each image. The recommendation is convert to text when the image is a diagram, a table, or text that can be reproduced exactly, and compress otherwise. An image above about 10 MB still recommends leave it out. After the list, one question: accept all recommendations, go through them one by one with the recommendation shown, or change some by naming items. The transfer data policy `auto-accept` applies to these recommendations only when the rule text clearly covers them. The rule written today applies auto-accept to keep and redact. That line does not cover the four image options, so the question is still asked. Nothing is written to the source folder until every image has an answer. The skills do not commit. The shared reference is [`.cursor/skills/crav1/crav1-add-to-spec/references/sources.md`](.cursor/skills/crav1/crav1-add-to-spec/references/sources.md). No new skill.

- Convert to text removes that image part from the `.eml`, leaves a short placeholder that names the new file, and writes `<name>.md` in the same `docs/sources/YYYY-MM-DD-<slug>/` folder. The file has the image's text word for word, a Mermaid redraw for a diagram, and a markdown table for a table. The README notes the conversion and says the `.eml` is no longer the untouched original. Leave out removes the part, the placeholder says it was left out, and the README notes it. Compress replaces the part with the compressed image, with the same screenshot rules. Commit as-is leaves the part unchanged.

- The personal-data and secrets check also covers what is readable in an embedded image and in the converted text. A secret in an image is removed. Commit as-is is not available for that image.

### Docs

- The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) records the image ask on `/crav1-add-to-spec`, `/crav1-meeting-to-specs`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, and `/crav1-match-dump-to-specs`. [docs/guild-routing.md](docs/guild-routing.md) notes the same ask. [docs/from-meeting.md](docs/from-meeting.md) names it on a kept mail. No new skill.

## 1.34.0 (2026-10-10)

### Kit

- Imported sources recommend keep or redact before the files are written. Keep a work email of a person on From, To, or Cc, other than the sender, an office phone, and an office address. Redact a personal mobile, a private street address, and a private email. The sender's own email stays unflagged. An item the kit cannot place, such as a mobile that may be work or private, has no recommendation and is asked one at a time. Secrets are always redacted and are never a choice: connection strings, SAS tokens, API keys, passwords, private keys, and VPN configs. The list shows a secret by kind only, never the value. The same README note names the kind and does not paste the value.

- A note is shown once above the list. It is marked as not legal advice. Keeping a work mail as a project record fits, because a spec quote must trace to the source. Keep only what that trace needs. Where the repo is hosted matters. The client's or the employer's data and retention policy comes first. Removing something after it is pushed means rewriting git history.

- After the list, one question has three answers: accept all recommendations, go through them one by one with the recommendation shown on each, or change some by naming items to flip. Unplaced items are still asked one at a time, whatever is picked. Nothing is written until every flagged item has an answer. A redaction is noted in the README by kind, never by value. No unredacted copy is written. The skills do not commit.

- The first check with no rule asks once which types to check (personal data for now; the file allows more types later), whether to auto-accept the recommendations or review each run, and where the repo is hosted. It then offers to save that as the rule. Yes writes it. No uses the answers this run only. When the rule exists, the check applies it, shows one line naming the file and what it chose, shows the note once, and asks only about unplaced items, plus the accept question when the rule says review. The user changes it by editing or deleting the file. The skill never writes a secrets choice into it. Cursor: `.cursor/rules/crav1-transfer-data-policy.mdc`. Claude Code project: `.claude/rules/crav1-transfer-data-policy.md`. The template is [`.cursor/skills/crav1/crav1-add-to-spec/assets/crav1-transfer-data-policy.mdc`](.cursor/skills/crav1/crav1-add-to-spec/assets/crav1-transfer-data-policy.mdc). `/crav1-add-to-spec`, `/crav1-meeting-to-specs`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, and `/crav1-match-dump-to-specs` follow it. No new skill.

### Docs

- The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) records the rule write on those five skills. [docs/guild-routing.md](docs/guild-routing.md) notes the same check. [docs/install.md](docs/install.md) names the file a product repo may get, next to the commit-style rule. No new skill.

## 1.33.0 (2026-10-09)

### Kit

- `/crav1-specs-to-ado`, before the preview, reads the project's Feature fields. When the type has Acceptance Criteria (`Microsoft.VSTS.Common.AcceptanceCriteria`), the spec's checks go there. When it does not, as on Agile and Basic, the checks go in the Description as an Acceptance checks numbered list, that field is not sent, and the preview says so in one line. The same rule applies on Update, so a re-run moves checks that were stored off the form into the Description. A failed field read states the issue, suggests a fix, and offers a skip. It does not guess.

- After a Create, writing the new id into `docs/specs/<slug>/work-item.md` (with the milestone or slice label), or a row on the landscape “No spec yet in ADO” table when the item has no spec, is a required final step. The closing output names the file, says it is not committed yet, and names `/crav1-finalize-commit`. Without that file a later run offers Create again and would make a duplicate. If the write fails, the run says so and prints the line to add.

- `/crav1-ado-to-specs` reads the checks from Acceptance Criteria when the Feature type has that field, and from the Acceptance checks list in the Description when it does not, so a round trip that matches is not reported as a change. Discussion comments use api version `7.1-preview`. Current `az devops invoke` deletes `-preview` and parses the rest as a float, so `7.1-preview.4` fails. `7.1-preview` parses. No new skill.

### Docs

- The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) and [docs/guild-routing.md](docs/guild-routing.md) record the same three rules. [docs/from-specs-to-ado.md](docs/from-specs-to-ado.md) and [docs/from-ado-to-specs.md](docs/from-ado-to-specs.md) name them too. No new skill.

## 1.32.0 (2026-10-08)

### Kit

- `/crav1-tighten-spec`, when the slice is partial or `## In the code` names paths, reads the committed code on the repo and branch the spec names before wording issues, and treats that code as the current fact. It reads only that repo and branch. A different open checkout stops the run and names the right ones. A stub, for example a `.gitkeep` on `main`, is not the code. If the spec names no branch, it stops and asks which branch has the code. It does not assume `main` or the open checkout. After the user answers, that branch is the read. Writing the branch onto the spec is a yes or no, not a silent edit. A spec that is too thin for that read stops. Too thin means partial, status `done`, or `## In the code` without a repo or without paths, or neither marker on a spec that is not already a full spec with no code behind it. It names `/crav1-code-into-specs` when a change already landed on an existing spec, or `/crav1-match-to-specs` when the slice was never matched. It does not guess and it does not tighten. A disagreement between the tightened wording and the code is called out. The spec is not silently rewritten to match the code. A spec with no code behind it (match status `not in the code`, or a full spec that never claims existing code) skips the read and tightens as before. Finish the gap, add a verify test, and leave it are not choices here. Those belong to `/crav1-plan-from-spec`. No new skill. No version bump.

- `/crav1-plan-from-spec`, before any task is written, when the spec is partial or `## In the code` names paths, reads that same repo and branch and lists each built piece. Each choice says what it means and what it will do. Finish the gap: the code is partly there and v0 wants the rest; the task is that gap only; what already matches is not rebuilt. Add a verify test: the code stays as it is; the task checks what is already there; the feature does not change. Leave it: no task; the plan gets one line saying this piece was left as committed; a later run does not turn it into work unless the user says so. A piece that already matches v0 is not a choice. It is marked already there and gets no rebuild task. A disagreement, such as the spec says one environment and the code enables another, is its own line before any task exists, with the same three choices. The plan check and the plan reviewer treat `already there` and `left as committed` as not a missing task. No new skill. No version bump.

### Docs

- [docs/guild-routing.md](docs/guild-routing.md) and the behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) record one line per skill: what it reads, what it writes, and what it leaves alone, plus one short exception line. [README.md](README.md), [plugins/crav1/README.md](plugins/crav1/README.md), [docs/first-run.md](docs/first-run.md), [docs/from-nothing.md](docs/from-nothing.md), and [docs/from-ideas.md](docs/from-ideas.md) name the same read. [AGENTS.md](AGENTS.md) and [`.cursor/rules/crav1.mdc`](.cursor/rules/crav1.mdc) name it too. The words stay host-generic. No new skill. No version bump.

## 1.31.0 (2026-10-08)

### Kit

- Cross-cutting skills `/crav1-feature-candidates`, `/crav1-specs-to-ado`, and `/crav1-ado-to-specs`. Feature candidates reads the landscape (the spec index, Ideas, Way of working, and code with no slice), `repos.md`, the glossary, every spec’s milestones, slices, open questions, and actions, plus `plan.md`, `tasks.md`, and `verify.md` where they exist, and `docs/research/` and `docs/sources/` with each fact labelled by where it came from. It also reads each `work-item.md` and the landscape “No spec yet in ADO” table. A dated milestone or slice is one candidate. An undated spec with open work is one candidate. A spec that holds only open questions is marked questions only, and the questions sit in the description. An item with no spec is marked no spec yet. A spec that is done or retired with nothing open is skipped. A recorded id is shown. A target date is given only when the docs state it, with its source. Dated rows are ordered by date. Undated rows are left for the user’s team to prioritize. The chat list is a numbered table and a short block per row. The skill writes nothing unless the user asks for a file. Specs to Azure Boards takes the org and project from `docs/environments/marks.md` or from the Azure DevOps URLs in `docs/system/repos.md`, checks `az` including the default install paths, and checks that the project has the Feature work item type. On a failure it states the issue, suggests a fix such as `az login`, and offers a skip. It runs feature candidates, the user picks by number or all, and it previews the Feature form: title, State New, Area default, Value area Business, Iteration and Priority blank, Target Date only when the spec states it, tags for the slice name and the code repos it touches, a description that stands alone, and acceptance criteria only from the spec’s checks. Nothing sent mentions the specs repo. `AB#` mentions already in code repos stay as they are. A preview is not edited in place. A change goes into the spec through `/crav1-add-to-spec`, then the preview is rebuilt. Create or update runs only after the user says yes, one at a time or all reviewed together. The new id is written to that spec’s `work-item.md` with its milestone or slice label, or to a “No spec yet in ADO” row (id, title, date) when the item has no spec. When a spec is made later, the id moves into that spec’s `work-item.md`. Azure Boards to specs reads the recorded ids, or only the ids the user names: State, Priority, Target Date, Iteration, Assigned To, comments, and history. It shows only what differs or is new. A missing id is missing, with no guessed match. The user keeps or dismisses each change. Dismissals start fresh each run. A kept change goes through `/crav1-add-to-spec`, labelled as coming from Azure Boards with the date and who changed it. An answer the user gives during the run goes into the spec first, labelled with the date as the user’s answer to the Azure Boards question. A no-spec-yet Feature suggests making the spec first. A reply comment is drafted from the spec only when the spec answers the question, shown as `Post comment on Feature <id>: <text>`, and posted only on yes. `work-item.md` holds several ids, one line each with a milestone or slice label. The old single-line format is still read. The commit mention picks the id for the slice being worked and asks if that is unclear. The offer that records an id the user already has points at `/crav1-specs-to-ado` for creating a Feature. Guild routing lists the three skills under Cross-cutting. No new lane. Walkthroughs: [docs/from-feature-candidates.md](docs/from-feature-candidates.md), [docs/from-specs-to-ado.md](docs/from-specs-to-ado.md), and [docs/from-ado-to-specs.md](docs/from-ado-to-specs.md). No version bump.

### Docs

- [docs/from-feature-candidates.md](docs/from-feature-candidates.md), [docs/from-specs-to-ado.md](docs/from-specs-to-ado.md), and [docs/from-ado-to-specs.md](docs/from-ado-to-specs.md) walk the three Azure Boards skills for Cursor and Claude Code. The slash commands are the same. [docs/guild-routing.md](docs/guild-routing.md) lists them under Cross-cutting. They may run from any lane. They do not move work into Specify, Plan, or Build. They are later skills. They are not starter options. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the commands. The behavior map gains one line each. [docs/system/_template/landscape.md](docs/system/_template/landscape.md) gains `## No spec yet in ADO`. [docs/specs/_template/work-item.md](docs/specs/_template/work-item.md) holds one id per line. [docs/from-ideas.md](docs/from-ideas.md) points Feature creation at `/crav1-specs-to-ado`. No new lane. No version bump.

## 1.30.0 (2026-10-07)

### Kit

- Imported sources. A mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original file that a skill quotes into a spec is stored in the target project at `docs/sources/YYYY-MM-DD-<slug>/`, with the original files and a `README.md`. The README says what it is, the sender or the participants, the date and the time, and how it was converted. Spec `Source:` and `Trace:` lines link to that folder, so every verbatim quote traces to its original. A mail is a `.eml` text file with its CRLF line endings kept. If the project's `.gitattributes` lacks `*.eml -text`, the skill asks once, yes or no, before adding that line. For every binary file the skill asks which of four options to use and recommends one from the file type: commit as-is; compress, then commit (for a screenshot: crop off taskbars and app bars, no sharpening, WebP, and show samples at q70, q85, and lossless so the user picks the quality); convert to text and commit that instead, keeping the original outside the repo (for a document: `transcript.md`, word for word, with speakers and timestamps, checked word for word against the original); or leave it out and only reference where the original lives (the recommendation above about 10 MB). Git LFS (Large File Storage) is a note only, never an option, because it needs repo setup the kit does not do. The README records which option was used. Before the files are written, phone numbers, street addresses, personal emails beyond the sender, and similar details, for example in a mail signature, are flagged. The user keeps or redacts each item. A redaction is noted in the README, because the file is then no longer the untouched original. The skills write the files and do not commit. The shared reference is [`.cursor/skills/crav1/crav1-add-to-spec/references/sources.md`](.cursor/skills/crav1/crav1-add-to-spec/references/sources.md). `/crav1-meeting-to-specs` and `/crav1-add-to-spec` follow it. `/crav1-match-dump-to-specs`, `/crav1-intake-to-specs`, and `/crav1-match-to-specs` follow it when they quote those files. A short fact typed for one spec, an environment-read fact, a test suggestion, and a quote of repository code are not imported sources. No new skill. No version bump.

### Docs

- [docs/from-meeting.md](docs/from-meeting.md), [docs/from-add.md](docs/from-add.md), [docs/from-match-dump.md](docs/from-match-dump.md), [docs/from-intake.md](docs/from-intake.md), and [docs/from-match.md](docs/from-match.md) name the imported-sources folder `docs/sources/YYYY-MM-DD-<slug>/`. The behavior map records the same write on `/crav1-meeting-to-specs`, `/crav1-add-to-spec`, `/crav1-match-dump-to-specs`, `/crav1-intake-to-specs`, and `/crav1-match-to-specs`. [docs/guild-routing.md](docs/guild-routing.md), [README.md](README.md), [docs/install.md](docs/install.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the same folder. The skills write the files and do not commit. No new skill. No version bump.

## 1.29.0 (2026-10-07)

### Kit

- `docs/system/repos.md` has a per-repo `Synced at` column, `<branch>@<short sha>, <date>`. A repo may list several branches, separated by `; `. Example: `main@abc1234, 2026-10-07; develop@def5678, 2026-10-06`. When `/crav1-keep-current`, `/crav1-repos-to-spec`, `/crav1-code-into-specs`, or `/crav1-intake-to-specs` and `/crav1-ideas-to-spec` (where they read repos) read a whole repo, they set that repo's column to the branch and commit they actually read. They touch only the repos they read. When a run reads only one slice, it does not touch the repo column. It writes or updates `Synced at: <repo> <branch>@<short sha>, <date>` in that slice's `spec.md`. A consumer measuring drift uses the older of the repo column and the slice line, and an empty value means unknown, so fall back to spec file commit dates. Skills that write `repos.md` include the column. `/crav1-spark-to-spec` leaves the cell empty and writes the slice line when it read that slice's code. `/crav1-match-to-specs` leaves the cell empty. `/crav1-add-to-spec` and `/crav1-match-dump-to-specs` keep an existing cell and do not set it. No new folder. No version bump.

### Docs

- [docs/system/_template/repos.md](docs/system/_template/repos.md) adds the `Synced at` column and the drift sentence. [docs/from-ideas.md](docs/from-ideas.md), [docs/from-intake.md](docs/from-intake.md), [docs/from-nothing.md](docs/from-nothing.md), [docs/from-code.md](docs/from-code.md), [docs/from-repos.md](docs/from-repos.md), and [docs/from-keep-current.md](docs/from-keep-current.md) name the same stamp. The behavior map records it on the skills that write it. No new folder. No version bump.

## 1.28.0 (2026-10-07)

### Kit

- `/crav1-review-pr` treats a pull request with no `plan.md` or `tasks.md` for its slug as built outside the kit. That is an info note, not a fix finding. It does not report a missing `verify.md`. It still checks spec fit, the pull request body against the diff, the required green linter, and secrets. Instead of `verify.md`, it reads the test results that pull request's own pipeline already recorded and reports, as an info note, which tests ran, whether they passed, and which changed files no test touches. It does not run tests and it does not ask to. When the pipeline shows no test run, the note names the tests the pull request includes and tells the user they can run them manually and then rerun the review. A rerun only sees results the pipeline recorded, so a local run shows up only if the user pastes its output. The note states that these are the pull request's own tests, not a check against the spec. An outside pull request ends with one line naming `/crav1-keep-current` as the next step after the pull request merges, to bring its changes into the spec and `docs/system/`. The skill does not run it. A pull request that has a plan keeps the full plan and `verify.md` checks. Walkthrough: [docs/from-review-pr.md](docs/from-review-pr.md). No new folder. No version bump.

## 1.27.0 (2026-10-07)

### Kit

- `/crav1-whats-known-about` derives the Azure DevOps org and project from Azure DevOps URLs in `docs/system/repos.md` when the git remote is not Azure Repos and `docs/environments/marks.md` does not name them. It then reads work items, open pull requests, and branches read-only, the same way as the existing live-read path. Every fact is tagged as a live read. Before it reports the Azure CLI `az` as not installed, it checks the default install paths on Windows (`C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd` and `C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd`), macOS (`/opt/homebrew/bin/az` and `/usr/local/bin/az`), and Linux (`/usr/bin/az` and `/usr/local/bin/az`). When one of those paths is there, it uses that path. No new folder. No version bump.

## 1.26.0 (2026-10-07)

### Kit

- `/crav1-explain` stays read-only. On every run it compares the feature index with the system picture: the slice's node in `docs/system/diagrams.md` and its line under `## How the parts connect`. Names match only by slug, spec title, or main resource name. At the end of the answer it lists each slice that is missing entirely or partly, one line per slice, including done and retired, and shows that status. It names `/crav1-keep-current` and does not run it. When the picture has nothing on the question, it quotes the first paragraph of the matching slice's spec, labelled as coming from the spec, and names `/crav1-whats-known-about`. When no spec matches either, it says so and names that skill. It does not run it. No new folder. No version bump.

- Some commands ask once at the end of a run, yes or no: "The system picture may now be out of date. Run `/crav1-keep-current`?" They do not run `/crav1-keep-current`. `/crav1-complete-features` asks when a slice is marked done or retired. `/crav1-fix-bug` and `/crav1-fix-live` ask when the fix changes how the parts connect. `/crav1-environment-read` asks after `docs/environments/marks.md` lines are added. `/crav1-add-to-spec` asks once at the end of a handoff from environment-read or suggest-tests-for-code, not once per item. `/crav1-implement-task` and `/crav1-complete-task` do not ask. Spark, ideas, intake, match, match-dump, code-into-specs, and repos-to-spec still update the picture in their own pass. No new folder. No version bump.

### Docs

- [docs/from-explain.md](docs/from-explain.md) names the feature-index check and the spec-paragraph fallback on `/crav1-explain`. [docs/from-keep-current.md](docs/from-keep-current.md) names who asks before `/crav1-keep-current` and who still updates the picture in their own pass. [docs/from-fix-bug.md](docs/from-fix-bug.md), [docs/from-environment.md](docs/from-environment.md), and [docs/from-add.md](docs/from-add.md) name the same yes or no question. The behavior map records one line per skill. [docs/guild-routing.md](docs/guild-routing.md), [README.md](README.md), [docs/install.md](docs/install.md), [AGENTS.md](AGENTS.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the same checks. No new folder. No version bump.

## 1.25.0 (2026-10-06)

### Kit

- `/crav1-meeting-to-specs` shows a build-state line on each item that matches an existing spec. The line is `State: <state>.` plus a short reason that names the evidence. It is in the item block and in the keep, leave, or dismiss question. The states are built, partly built, planned, and not built. `Fits: none` has no state line. Evidence is the matched slice’s `spec.md` (including `## Match`), `plan.md`, `tasks.md` checkboxes, and `verify.md` when present. When those do not settle it, one read-only look at the code that spec or plan points to. No codebase-wide search. A code-based or uncertain state is labeled `(inference, not in the docs)`. The line does not change the options. It is not written. It is not passed to `/crav1-add-to-spec` as quote text. That handoff does not write a `State:` line. The skill still writes nothing itself. No new folder. No version bump.

### Docs

- [docs/from-meeting.md](docs/from-meeting.md) names the build-state line on `/crav1-meeting-to-specs`. The behavior map line now includes that slice’s `plan.md`, `tasks.md`, `verify.md`, and a read-only look at the code that spec or plan points to when those files do not settle the state. [docs/guild-routing.md](docs/guild-routing.md), [README.md](README.md), [docs/install.md](docs/install.md), [docs/from-add.md](docs/from-add.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the same line. No new folder. No version bump.

## 1.24.0 (2026-10-06)

### Kit

- `/crav1-meeting-to-specs` takes minutes, a transcript, a Teams or Zoom export, an email, or a pasted Slack or Teams chat thread. The kind is `meeting`, `email`, or `chat`, from what the input shows. It does not guess. If the kind is not clear, it asks once per run, options only: meeting, email, or chat. The date comes from the input. It does not invent one. When the input shows no date, it asks once per run, options only: give a date, or skip. A date the user gives is used. Skip means no date. One kind and one date apply to every item. The `Source` line is `<kind> <date>`, or `<kind>`. A kept addition handed to `/crav1-add-to-spec` starts the quote with `From <kind> <date>.` when there is a date, otherwise `From <kind>.` Speaker and time stay when the input shows them. The skill still writes nothing itself. Dismissals still start fresh each run. No new skill. No new folder. No version bump.

### Docs

- [docs/from-meeting.md](docs/from-meeting.md) says an email or a chat thread is accepted, and the quote label follows the kind and the date. The behavior map line for `/crav1-meeting-to-specs` names that input. [docs/guild-routing.md](docs/guild-routing.md), [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the same input. No new folder. No version bump.

## 1.23.0 (2026-10-06)

### Kit

- Cross-cutting skill `/crav1-whats-known-about`. The user asks about one feature, slice, resource, or not-yet-feature. The answer comes from the specs first. It reads only. It writes nothing. An exact name match runs first, across spec titles, `tasks.md`, Match quotes, `docs/system/`, `docs/architecture/spec.md`, and `docs/environments/marks.md`. A sentence uses the key words, with spec titles and Match quotes weighted highest. One pass. It does not hunt the whole codebase. An `@` keeps the search inside that path. One slice that wins is the answer, and the path is named. Two or more close hits are listed, one line each, and it asks which. It does not guess. No slice: it says so, shows what the repo, the code, and the environment notes know, and presents a candidate slice. A code-only hit, with no spec and no architecture note, shows what the code says and fills in Unexplained. It names `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, or `/crav1-intake-to-specs` and does not run them. Pasted minutes or a long dump names `/crav1-meeting-to-specs` or `/crav1-match-dump-to-specs` and stops. After the repo part it runs read-only live checks: Azure resource settings and recent changes with `az`, and Azure DevOps work items, open pull requests, and branches that touch the thing. Each live fact is tagged as a live read. Production follows the `/crav1-environment-read` rule: shape and connections only, after the same yes or no. It never reads data. A failed live read shows one prompt with the issue, a fix when there is one, and Retry or Skip. Skip is the repo-only answer, with a line that the live checks did not run and why. A focus still runs the full read and shows only those sections. The chat answer follows `assets/answer.md`. Empty sections are left out. A guess is labeled `(inference, not in the docs)`. It may name one skill. It does not run another skill. It does not start Specify, Plan, or Build. It may run from any lane. It is a later skill. It is not a starter option. When the user asks for startup options, name only the seven. That ask names the list and does not run this command. The seven starter options stay unchanged. It is not `/crav1-explain`. Explain reads `docs/system/` and does not open a spec to answer the question. Guild routing lists it under Cross-cutting. No new lane. Walkthrough: [docs/from-whats-known-about.md](docs/from-whats-known-about.md). No version bump.

### Docs

- [docs/from-whats-known-about.md](docs/from-whats-known-about.md) walks `/crav1-whats-known-about` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting. It may run from any lane. It does not move work into Specify, Plan, or Build. It is a later skill. It is not one of the seven starter options. [docs/from-explain.md](docs/from-explain.md) points at it. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. The behavior map gains one line. No new lane. No version bump.

## 1.22.0 (2026-10-05)

### Kit

- `/crav1-environment-read` can read a prod-only resource for shape and connections only, after one yes. Prod-only means the mark is production (name, group, tag, or `docs/environments/marks.md`) and no source on that same resource says non-prod or pre-prod. A different resource with a similar name is not a twin. The question is the same yes or no as pre-prod and shared-with-prod. A no lists them as not read, and a declined prod-only resource stays in Skipped. A yes reads names, types, setting keys, routes the settings already show, timers, links, and secret names. Never data. Never secret values. Never a row or a blob. Each Seen, System, Architecture, Match, and Links line says `Seen in <host> prod.` and `prod only`. Look-inside still never opens a production database or store. Naming production, prod, or live as the host still stops the read. No new skill. No new lane. No version bump.

## 1.21.0 (2026-10-05)

### Kit

- Cross-cutting skill `/crav1-meeting-to-specs`. Everything after the command, and every `@`, is the minutes or transcript (a file, a paste, or a Teams or Zoom export). If there is no pointer, it stops and asks. Options only. It does not guess. It extracts requirements, decisions, changes, open questions, and bugs. Each item is a quote. Speaker and time are included when the transcript shows them. Small talk and status chatter are dropped. It matches each item against existing `docs/specs/<slug>/` folders and skips `_template`. The cases are an addition to a named existing spec, a possible new feature, a bug, or unclear. When more than one existing spec could fit, every candidate stays listed. Nothing is dropped to keep the list short. The user takes items one at a time: keep, leave, or dismiss. Dismiss is for this run only. The next run starts fresh. It does not write a dismissals file and does not remember a dismiss across runs. A kept addition is handed to `/crav1-add-to-spec` for that slug, with a source label from the meeting and the date when it is known. The impact check still runs there. A kept new feature names `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, or `/crav1-intake-to-specs` and does not run it. A kept bug names `/crav1-fix-bug` and does not run it. An unclear keep asks which existing slug, or treats the item as a new feature. The skill writes nothing itself. It does not copy the transcript into the repo. It does not create a slug. It does not start Specify, Plan, or Build. It may run from any lane. It is a later skill. It is not a starter option. When the user asks for startup options, name only the seven. That ask names the list and does not run this command. The seven starter options stay unchanged. Guild routing lists it under Cross-cutting. No new lane. Walkthrough: [docs/from-meeting.md](docs/from-meeting.md). No version bump.

### Docs

- [docs/from-meeting.md](docs/from-meeting.md) walks `/crav1-meeting-to-specs` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting. It may run from any lane. It does not move work into Specify, Plan, or Build. It is a later skill. It is not one of the seven starter options. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. The behavior map gains one line. `/crav1-add-to-spec` gains a handoff section, and its caller list includes this skill. No new lane. No version bump.

## 1.20.0 (2026-10-05)

### Kit

- `/crav1-environment-read` can look inside a database or storage after the first read, and before any section. It asks first. A no leaves them unopened. SQL reads metadata only: schemas, table and view names, columns and types, keys and relationships, stored procedure and function names, and SQL Agent jobs or other scheduled jobs and triggers when they can be reached. The line for a job or a trigger is source, target, and schedule. Storage reads structure only: accounts or buckets, containers, file shares, queues, table names, prefixes to depth 2, public or private access, lifecycle, versioning, soft delete, and what points at it, including storage triggers. It lists prefixes, not files. It never reads a row or a blob, and it never reports a file count or a size. It never prints a connection string, a key, or a secret. Production is never opened. Pre-prod and shared-with-prod follow the existing yes and stay shape and connections only. When the databases have no clear environment, it says there are no clear database environments, then asks whether the environments are in the same database, then whether to read the schema. Before that second question, and before the storage question, it says how to reach it and how much setup is needed. `sqlcmd` is optional. The skill does not install a tool, and it does not create a login, a firewall rule, a role, a SAS token, or a key. Missing access stops that look-inside and names the gap. A schema, a name, or a prefix is evidence only when the whole-word token rule matches. Facts join the sections that already exist and say they were seen in that environment. Readers: [references/sql.md](.cursor/skills/crav1/crav1-environment-read/references/sql.md) and [references/storage.md](.cursor/skills/crav1/crav1-environment-read/references/storage.md). No new skill. No new lane. No new output section. No version bump.

### Docs

- [docs/from-environment.md](docs/from-environment.md) walks the SQL and storage look-inside on `/crav1-environment-read`. [docs/install.md](docs/install.md) lists `sqlcmd` as optional. The skill does not install it. [docs/guild-routing.md](docs/guild-routing.md) stays cross-cutting. The behavior map stays one line plus one exception. [README.md](README.md) and [plugins/crav1/README.md](plugins/crav1/README.md) name the look-inside. No new skill. No new lane. No version bump.

## 1.19.0 (2026-10-05)

### Kit

- Cross-cutting skill `/crav1-pipeline-environments`. The user names Azure DevOps, the org, and the project. A pipeline name is optional. If any of those three is missing, it stops and asks. Options only. It does not guess. It reads pipeline definitions with `az pipelines` and `az devops` (list and show only, with the `azure-devops` extension). It does not run, queue, edit, approve, or trigger a pipeline. It does not read builds, logs, test runs, boards, or repo files beyond the pipeline definition. Secrets are not printed. The stage name gives the environment, with the same whole-word rule as `/crav1-environment-read`. A deploy step marks the resource it names. The resource group is context on that line and the rest of the group is not marked. One environment proposes a `pipeline <name>, stage <stage>` line. A resource deployed by both a non-prod stage and a production stage is one line per stage, because the marks format has no `shared` word. An unclear stage or an unresolved variable proposes no mark. Confirmed lines are appended to `docs/environments/marks.md`. The file is created only then. An existing line is never rewritten. It does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`. If `az` is missing, the extension is missing, or there is no login, the stop names which. It does not install or log in. It names `/crav1-environment-read` and does not run it. It is a later skill. It is not a starter option. The seven starter options stay unchanged. Guild routing lists it under Cross-cutting. No new lane. Walkthrough: [docs/from-pipeline-environments.md](docs/from-pipeline-environments.md). No version bump.

### Docs

- [docs/from-pipeline-environments.md](docs/from-pipeline-environments.md) walks `/crav1-pipeline-environments` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting. It is a later skill. It is not one of the seven starter options. [docs/environments-marks.md](docs/environments-marks.md) points at the skill. The marks format stays four fields. There is no `shared` word. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. The behavior map gains one line. No new lane. No version bump.

## 1.18.0 (2026-10-05)

### Kit

- `/crav1-environment-read` reads every non-prod environment on the host the user named, in one pass. The user no longer picks dev or test. Naming production, prod, or live still stops the read. Seen lines keep their own environment (`Seen in Azure dev.`, `Seen in Azure test.`, and the same for stage, uat, qa, and pre-prod). Non-prod tokens are dev, development, test, testing, stage, staging, uat, and qa. Pre-prod is `preprod`, or the neighboring whole words `pre` then `prod` from `pre-prod` and `pre_prod`. `live` is production when it is a whole word. Pre-prod, and a resource marked both non-prod and production by different sources, are shape and connections only after one yes, and the mixed resource is labelled `shared with prod`. A resource whose only mark is production stays skipped. A fourth mark source is `docs/environments/marks.md` (format: [docs/environments-marks.md](docs/environments-marks.md)). The read appends only lines the user confirmed and never rewrites an existing line. Unmarked resources can be marked from shown evidence, strongest first, then from a group suggestion, then by the user per resource or per group. Triggers are connections and show the definition only. A missing CLI or login is named, with the install page and the login command. The skill does not install or log in, and it does not look inside databases or storage. `/crav1-pipeline-environments` appends the pipeline lines. This read does not run it. Guild routing stays cross-cutting. No new lane. No version bump.

### Docs

- [docs/from-environment.md](docs/from-environment.md) walks the host pass for `/crav1-environment-read`. [docs/environments-marks.md](docs/environments-marks.md) defines the `docs/environments/marks.md` line. [docs/guild-routing.md](docs/guild-routing.md) stays cross-cutting and says the user names the host. The behavior map says the skill appends confirmed marks and leaves the other files to their owners. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the host pass. No new lane. No version bump.

## 1.17.0 (2026-10-05)

### Kit

- Cross-cutting skill `/crav1-suggest-tests-for-code`. The user points at code that already exists, one repo or one area, not the whole system. It reads that code and suggests tests for what that code can actually break. A function gets a few checks. A page gets a browser check. A boundary gets an integration check. It does not dump every test type. Every suggestion stays listed. Nothing is dropped to keep the list short. The user takes them one at a time: keep, leave, or dismiss. Dismiss means it is not offered again. A kept suggestion goes onto the existing spec through `/crav1-add-to-spec`. Plan turns it into a task. It does not write the tests, change the code, or start Specify, Plan, or Build. It does not move work into a lane. It may run from any lane. It is a later skill. It is not a starter option. When the user asks for startup options, name only the seven. That ask names the list and does not run this command. The seven starter options stay unchanged. Guild routing lists it under Cross-cutting. No new lane. No new folder beyond the skill’s own files. Walkthrough: [docs/from-suggest-tests.md](docs/from-suggest-tests.md). No version bump.

### Docs

- [docs/from-suggest-tests.md](docs/from-suggest-tests.md) walks `/crav1-suggest-tests-for-code` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting. It may run from any lane. It does not move work into Specify, Plan, or Build. It is a later skill. It is not one of the seven starter options. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. The behavior map gains one line. No new lane. No version bump.

## 1.16.0 (2026-10-04)

### Kit

- Cross-cutting skill `/crav1-exploratory-test`. It runs after a build of a slice already exists. Pass one learns the slice by using it once. Pass two is no longer careful. It adds randomness: sometimes a double-click, a hover back and forth, repeating an action, or using the same control more than once. It follows what the last action showed. It lasts about as long as the first pass, long enough to provoke bugs, then it stops. That stop is named `matched the first pass`. It stops sooner when the user says stop. That stop is named `the user said stop`. It does not run forever. The user does not set a clock. It writes bugs to `docs/specs/<slug>/explore.md`. It does not write the checks the plan already named. It does not start Specify, Plan, or Build. It does not move work into a lane. A bug it finds is not sent to `/crav1-fix-bug` unless the user says so in that turn. It may run from any lane. It is a later skill. It is not a starter option. When the user asks for startup options, name only the seven. That ask names the list and does not run this command. Guild routing lists it under Cross-cutting. No new lane. Walkthrough: [docs/from-exploratory-test.md](docs/from-exploratory-test.md). No version bump.

### Docs

- [docs/from-exploratory-test.md](docs/from-exploratory-test.md) walks `/crav1-exploratory-test` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting. It may run from any lane, after a build of a slice already exists, and it does not move work into Specify, Plan, or Build. It is a later skill. It is not one of the seven starter options. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. The behavior map gains one line. No new lane. No version bump.

## 1.15.0 (2026-10-04)

### Kit

- When the user asks for startup options, the kit names only these seven: `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. Every other skill is a later skill. That ask names the list. It does not run a skill and does not move work into a lane. Each starter still follows the rules it already has. `/crav1-repos-to-spec` still runs only when the user names repos. `/crav1-environment-read` still runs only when the user names the host and a dev or test environment. `/crav1-fix-bug` still runs only when the user names a real bug. The list is in [docs/guild-routing.md](docs/guild-routing.md), [docs/first-run.md](docs/first-run.md), [docs/install.md](docs/install.md), [README.md](README.md), and [plugins/crav1/README.md](plugins/crav1/README.md). No new skill. No new lane. No new folder. No version bump.

## 1.14.0 (2026-10-04)

### Kit

- `/crav1-environment-read` now has an AWS reader and a Google Cloud reader, beside the Azure reader. The user names the host and the environment. The environment is dev or test. Never production. The user names the environment, not the subscription, the account, or the project. Each reader lists only what that named environment actually has. A resource marked production is skipped and listed as skipped. A resource with no environment mark stops and is not read. Any other host still stops and says it has no reader. Azure DevOps, GitHub, and CI stay out. The skill still only reads. After a confirmed section, the owning skill adds only what is new. A fact is marked seen in that environment. Existing lines are not rewritten. Guild routing stays cross-cutting. No new skill. No new lane. No new folder. No version bump.

## 1.13.0 (2026-10-04)

### Kit

- Cross-cutting skill `/crav1-environment-read`. The user names the host and the environment at the start. Examples: Azure dev, Google Cloud test, AWS dev. It does not guess the host. It never reads production. Each host has its own reader. The reader lists only what that named environment actually has. A host with no reader stops and says so. It does not pretend to read it. It does not read Azure DevOps, GitHub, or CI. The user names the environment, not the subscription, the account, or the project. The reader takes only a resource whose name, group, or tag says dev or test. Anything marked production is skipped and listed as skipped. A resource with no environment mark stops and asks. It is not read. The skill only reads. It does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`. A fact is marked seen in that environment, not as something the code shows. It does not become a link unless the environment shows the connection. Confirmation is one section at a time, with its own question and answer, and nothing is dropped to keep a section short. After the user confirms a section, the skill that already owns the file adds only what is new. System facts go to `docs/system`. Architecture facts go to `docs/architecture/spec.md`. A slice Match already owns goes on that feature spec. A left-out line the environment now shows comes off `docs/architecture/left-out.md`. Lines that are already there are not rewritten. It does not start Specify, Plan, or Build. Guild routing lists it under Cross-cutting. No new lane. Walkthrough: [docs/from-environment.md](docs/from-environment.md). No version bump.

## 1.12.0 (2026-10-04)

### Kit

- `/crav1-repos-to-spec` confirms the read in sections before any file is written. One section per named repo for confirmed facts, one section for inferred guesses, one section for links, and one section for left-out. Each section has its own question and its own answer. Every item stays listed. A guess stays out until that section’s answer accepts it, and then it is accepted from a guess, not a code fact. A guess that stays left out is written to `docs/architecture/left-out.md`, beside `docs/architecture/spec.md`. Each line says the guess and that the code does not show it. It is not a confirmed fact and it is not a link. A later re-read reads that file and checks the code for every line. When the code shows the fact or a real link, the line comes off that file and is written as a fact or a link. The left-out answer can accept a line, keep it left out, or dismiss it. Dismiss means it is not offered again. A link is written only when the code shows it. If none is found, that section says so and does not offer a guessed link. Confirming a guess does not turn it into a link. Guild routing stays cross-cutting. No new skill. No new lane. No new folder. No version bump.

## 1.11.0 (2026-10-04)

### Kit

- `/crav1-repos-to-spec` no longer stops when a real note is already in `docs/system/`. When `docs/architecture/spec.md` is missing, it writes that file and leaves existing system notes as they are. When the architecture spec or those notes are already there, a later re-read adds only what is new and does not rewrite lines that are already there. A fact the code shows is confirmed. A guess stays out until the user confirms it. A link is written only when the code shows it. It does not design the next feature, write application code, or start Specify, Plan, or Build. Guild routing stays cross-cutting. No new skill. No new lane. No version bump.

## 1.10.0 (2026-10-04)

### Kit

- `/crav1-repos-to-spec` writes the architecture spec at `docs/architecture/spec.md`. The folder is `docs/architecture/`. The file is `spec.md`. Later architecture files can sit beside it. It stays out of `docs/system` and out of `docs/specs`. `docs/specs` stays one folder per feature slug. `docs/system` stays the short picture. This file stays the one the lanes can extend. Confirmed versus inferred, links, and the stop before Specify, Plan, and Build are unchanged. Guild routing stays cross-cutting. No new lane. No version bump.

### Docs

- [docs/from-repos.md](docs/from-repos.md) says the architecture spec from `/crav1-repos-to-spec` is `docs/architecture/spec.md`. The behavior map line for that skill names the same path. Guild routing stays cross-cutting. No new lane. No version bump.

## 1.9.0 (2026-10-04)

### Kit

- Cross-cutting skill `/crav1-repos-to-spec`. The user names one or more repos. It reads those repos and writes one architecture spec the lanes can extend (`docs/architecture/spec.md`) and the `docs/system/` notes `/crav1-explain` reads. A fact the code shows is confirmed. A guess stays out of the spec until the user confirms it. A link between repos is written only when the code shows it. If none is found, it says so. It does not invent links. It does not design the next feature, write application code, or start Specify, Plan, or Build. A later re-read that only adds what is new is not this command. It is not `/crav1-code-into-specs`. Guild routing adds it under Cross-cutting. No new lane. Walkthrough: [docs/from-repos.md](docs/from-repos.md). No version bump.

### Docs

- [docs/from-repos.md](docs/from-repos.md) walks `/crav1-repos-to-spec` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting. No new lane. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. The behavior map gains one line. No version bump.

## 1.8.0 (2026-10-04)

### Kit

- Cross-cutting skills `/crav1-explain` and `/crav1-keep-current`. Explain reads the system notes spark, ideas, intake, or match already wrote (`docs/system/`). The first answer is a short TLDR. Longer goes one level deeper from the same notes. The user can point it at one part. A question about whether the system can do something is yes with a pointer, no, or that it is not written down. It does not guess, write a second document, teach, or start Specify, Plan, or Build. When the picture is older than the specs, it says so and names keep-current. It does not run it. Keep-current adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there. It does not design the change and does not build it. It can run on its own. Spark, ideas, intake, match, match-dump, and code-into-specs run that same picture update in the pass that already appends a glossary row. Existing glossary rows are not rewritten. Guild routing adds both skills under Cross-cutting. No new lane. Walkthroughs: [docs/from-explain.md](docs/from-explain.md) and [docs/from-keep-current.md](docs/from-keep-current.md). No version bump.

### Docs

- [docs/from-explain.md](docs/from-explain.md) walks `/crav1-explain`. [docs/from-keep-current.md](docs/from-keep-current.md) walks `/crav1-keep-current`. [docs/guild-routing.md](docs/guild-routing.md) lists both under Cross-cutting. No new lane. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the commands. The landscape starter gains `## How the parts connect`. The behavior map gains one line for each. No version bump.

- The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) records one line per skill on main: what it reads, what it writes, what it leaves alone, who calls it, and which skill or agent it calls. An agent is listed only when it runs a skill. The map covers main. Guild routing is unchanged. No version bump.

## 1.7.0 (2026-10-04)

### Kit

- Cross-cutting skill `/crav1-fix-bug` names one real bug the user already named. It runs only when that turn names one. If none is named, it stops. It does not go hunting. A real bug is a verify failure on work that is already shipping, or a defect that comes in from outside. A design gap found before Build stays in the spec. An unfinished task stays a task. A one-off flaky check is a note, unless it keeps blocking ship. It says where the bug was seen (verify, a report, or production), names the bug, points at the spec or the shipped behavior it breaks, and names the lane. A spec miss goes to Specify. A plan miss goes to Plan. A verify miss or a broken implementation goes to Build. It does not start that lane, edit code, open a pull request, or create an Azure Boards work item. It is not a lane and not a stretch of verify. When the user asks for startup options, it is one of the options in that list. It is an intake for a bug that already exists. It is not a skill that runs because a repo is new, and it is not started automatically. Spark, specify, plan, and verify do not run it. Guild routing lists it under Cross-cutting. No new lane. Walkthrough: [docs/from-fix-bug.md](docs/from-fix-bug.md). No version bump.

- The bundled commit-message style is named CRAV1 style. The rules are unchanged (hyphen bullets, a verb at the start of each line, no Conventional Commits prefixes). The file stays `references/style.md`. GitKraken remains the name of the app where a message is pasted. Skill replies and the docs use CRAV1 style for that choice. No version bump.

### Docs

- [docs/from-fix-bug.md](docs/from-fix-bug.md) walks `/crav1-fix-bug` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting and adds it to the startup options. It may run from any lane, only when the user names a real bug, and it does not move work into Specify, Plan, or Build. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. No new lane. No version bump.

## 1.6.0 (2026-10-04)

### Kit

- Cross-cutting skill `/crav1-review-pr` reads one named open pull request and says whether it can ship. It runs only when that turn names the pull request (number or URL) or clearly asks to review it. Any open pull request, not only a feature branch. If none is named, it asks which one and stops. It does not pick the newest. It reads the diff. It does not edit code, the spec, or the plan. It does not run the tests, vote, post a comment, install a linter, change branch protection, or merge. Before it says ship, five checks have to hold: the diff matches the spec, the plan’s named files and checks are in the diff, `verify.md` is quoted when it is already on the branch (and said to be missing when it is not), the pull request body matches that scope, and a linter or checker covers the code in the diff and is required and green. Each miss is its own finding (what is off, what could happen, decision ship, fix, or drop). Any fix or drop means the review does not say ship. It names the lane and does not start it: a spec miss is Specify, a plan miss is Plan, a verify miss or a file the plan already named but the diff lacks or a red or missing linter is Build, and a body mismatch is a rewrite of that pull request body, not a new spec. Suggestions do not block ship, except a secret in the diff, which is a first-section fix. A clean review says so and stops. `/crav1-open-pr` may name it and does not run it. `/crav1-merge-pr` does not run it. A review is not a merge ask. Merge still stops on its own when a required host check is red. Spark, specify, and verify do not run it. Guild routing lists it under Cross-cutting. Walkthrough: [docs/from-review-pr.md](docs/from-review-pr.md). No version bump.

- `/crav1-plan-from-spec` says whether this repo has a linter or checker for the code the tasks will touch, in `plan.md` under `## Linter`. When it has one, the plan names the tool and the command, and Build is expected to leave that check green. When it does not, the plan says so and stops before Build. The user decides to add the linter or to go on without one. The plan skill does not install one. Specify stays yes/no acceptance and does not name the linter. `/crav1-review-plan` and `/crav1-tighten-plan` use the same rule when they check that a plan is complete. A missing linter note is a plan `P#`. A plan that already says none is complete on that point and still stops before Build until the user chooses. No new plan skill. No version bump.

### Docs

- [docs/from-review-pr.md](docs/from-review-pr.md) walks `/crav1-review-pr` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting. It may run from any lane, only when the user names a pull request, and it does not move work into Specify, Plan, or Build. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. Plan pages say the plan names a linter before Build. No version bump.

## 1.5.0 (2026-10-04)

### Kit

- `/crav1-plan-from-spec` names the checks on each task verify note before any code. Kinds are unit, system, browser, and integration when two parts meet. Contract, load or speed, accessibility, and golden or property are named only when the thing being built needs them. An algorithm gets several checks, including corner cases. A change that touches behavior that already works names regression tests. Kept security checks in `docs/system/security.md` or a Security section map to a task, or the plan says which task already covers them. The plan does not invent product behavior, a performance goal, or test code. Smoke after deploy, chaos, and fuzzing for its own sake stay out. Specify stays a yes/no acceptance line and names unit, system, or browser only when that kind is already obvious from the source. It does not invent a test list. `/crav1-review-plan` and `/crav1-tighten-plan` use the same check rules. `/crav1-implement-task` writes the checks named on that verify note. `/crav1-verify-spec` is unchanged and remains the gate that says the named checks passed. No new skill. Guild routing is unchanged. No version bump.

### Docs

- [README.md](README.md) says acceptance stays yes or no, and that `/crav1-plan-from-spec` names the checks on each task verify note before code. The task starter matches that shape. Guild routing is unchanged.

## 1.4.0 (2026-10-04)

### Kit

- Cross-cutting skill `/crav1-security-review` asks whether the thing in front of it is secure, and only after architecture already exists (`docs/system/` or a spec that already describes the design). The same command covers the whole system, one existing spec, or the change in front of us. If the target is unclear, it asks with options only, one option per real target. Findings are risks and what should change (what is wrong, what could happen if it stays, the decision being asked), each marked confirmed or inferred, plus a plain-language check. One confirm, then it writes only the kept findings: `docs/system/security.md` for a system pass, or a Security section on that spec for a feature or a change. It does not invent an architecture, write exploit steps, plan, implement, or commit. Spark, plan, and verify do not run it. `/crav1-architecture-reviewer` may name it as an optional next step and does not run it. Guild routing lists it under Cross-cutting. Walkthrough: [docs/from-security.md](docs/from-security.md). No version bump.

### Docs

- [docs/from-security.md](docs/from-security.md) walks `/crav1-security-review` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting and says it sits after architecture exists, with the same command for the whole system, one spec, or one change. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. There is no public Cursor Marketplace listing.

- User-facing pages name Cursor and Claude Code on the first screen. The slash commands are the same. The install is not. Cursor installs plugin `crav1` from this GitHub repo (team marketplace import or a local plugin). There is no public Cursor Marketplace listing. Claude Code has no plugin and no marketplace; copy `.claude/` into a repository you own, or into `~/.claude` for a client project. Cloning the kit does not install it into another product. [docs/install.md](docs/install.md) stays the file-location guide. Skill behavior is unchanged. No version bump.

## 1.3.0 (2026-10-02)

### Kit

- Specify skills that write or read `docs/system/` now treat `glossary.md` as part of the landscape, not a feature spec. `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, and `/crav1-match-to-specs` seed it in the same pass as `landscape.md`, `repos.md`, and `diagrams.md` when `docs/system/` is missing, write only that file when the folder exists and the glossary is missing, and append only new rows when the file exists. `/crav1-match-dump-to-specs` and `/crav1-code-into-specs` do not seed `docs/system/`. They fill a missing `glossary.md` only when that folder already exists, from the dump or the landed change, and they append new rows when the file exists. `/crav1-add-to-spec` does not create a glossary and does not write a new row unless apply is chosen. A new row from the new information can be one listed edit. Existing glossary rows are not rewritten, reordered, or edited. Rows are words or abbreviations the source already uses. When that source already says the meaning, that text is used. When it does not, Meaning is `to be researched`. Ordinary English is skipped. No new slash command. Guild routing is unchanged. No version bump.

### Docs

- Walkthroughs that list system files now include `glossary.md`: [docs/from-nothing.md](docs/from-nothing.md), [docs/from-ideas.md](docs/from-ideas.md), [docs/from-intake.md](docs/from-intake.md), and [docs/from-match.md](docs/from-match.md). [docs/from-match-dump.md](docs/from-match-dump.md) and [docs/from-code.md](docs/from-code.md) say a missing glossary is a gap fill only when `docs/system/` already exists. The starter is [docs/system/_template/glossary.md](docs/system/_template/glossary.md).

## 1.2.0 (2026-10-02)

### Kit

- `/crav1-code-into-specs` sorts a code change that already landed onto specs that already exist. The change is a commit, a commit range, or the diff of the current branch against the default branch. If the user does not name one, it looks at git and asks with options only (recent commits, or the branch diff) and does not ask for a typed hash. No dump is required. It does not ask for a slug first. It shows three piles — belongs to this spec, already described there, or fits none — and writes what belongs only after that sort is confirmed. Quotes go into the matching `spec.md` files the same way `/crav1-add-to-spec` writes them. It does not create a slug. Leftovers stay listed. It does not invent a landscape from the diff, and it does not seed `docs/system/` when that folder is missing. It does not rewrite the landscape or other specs unless the user chooses apply. It does not plan, implement, or commit. It does not watch the repo. Guild routing lists it in Specify between `/crav1-match-dump-to-specs` and `/crav1-add-to-spec`. Those skills, and match, intake, spark, ideas, and tighten, are unchanged. Walkthrough: [docs/from-code.md](docs/from-code.md).

## 1.1.0 (2026-10-02)

### Kit

- `/crav1-match-dump-to-specs` sorts a later dump (notes, tickets, old docs, diagrams, screenshots) onto specs that already exist. It does not ask for a slug first. It shows three piles — belongs to this spec, already in that spec, or does not fit — and writes new bits only after that sort is confirmed. Quotes go into the matching `spec.md` files the same way `/crav1-add-to-spec` writes them. It does not create a slug. Leftovers stay listed. It does not seed `docs/system/` when that folder is missing, and it does not rewrite the landscape or other specs unless the user chooses apply. It does not plan, implement, or commit. Guild routing lists it in Specify between `/crav1-match-to-specs` and `/crav1-add-to-spec`. Those skills, and intake, spark, ideas, and tighten, are unchanged. Walkthrough: [docs/from-match-dump.md](docs/from-match-dump.md).

## 1.0.0

First release of the public-facing kit: the skills, dual install, and sync check on `main`, plus the product-name, first-run, contributing, and support docs shipped with this changelog. The GitHub repository stays private until the owner changes visibility. This changelog does not create a git tag.

### Kit

- MIT license. The copyright notice is in [LICENSE](LICENSE).
- Dual install, documented in [docs/install.md](docs/install.md):
  - Drop-in copy into a product repo: `.cursor/skills/crav1/`, `.cursor/agents/crav1-*.md`, `.cursor/agent-assets/crav1-*`, and `.cursor/rules/crav1.mdc`.
  - Cursor plugin at `plugins/crav1/` with catalog `.cursor-plugin/marketplace.json` (team marketplace or local plugin).
- Skill loop under `/crav1`: spark, ideas, or intake → spec → architecture review and tighten → resolve questions → plan → review-plan and tighten-plan → one task (`/crav1-implement-task`) or an isolated worker (`/crav1-complete-task`, `/crav1-complete-tasks`, serial `/crav1-complete-features`) → verify → fix-from-verify (and fix-live) → draft or finalize a commit message.
- Maintainer sync: edit `.cursor/`, then run `scripts/sync-crav1-plugin.sh`. GitHub Actions (`.github/workflows/drop-in-plugin-sync.yml`) fails the check when the drop-in tree and `plugins/crav1/` drift, and when `kit-maintainer.mdc` is present under the plugin.
- `/crav1-add-to-spec` adds new information to one existing `docs/specs/<slug>/spec.md`, then reports whether `docs/system/` or another spec has to change. It does not rewrite those other files unless the user chooses apply. It does not plan, implement, or commit. A not-started spec can keep taking information until planning. Guild routing gains this skill. `/crav1-match-to-specs`, `/crav1-intake-to-specs`, `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, and `/crav1-tighten-spec` are unchanged. Walkthrough: [docs/from-add.md](docs/from-add.md).
- `/crav1-match-to-specs` matches one or more repos that already make up a system, plus a dump, to `docs/system/` and one `docs/specs/<slug>/` per confirmed slice (`done`, `partial`, or `not in the code`). It asks where the spec files go before any map, uses one branch for the dump, and does not plan, implement, or commit. Not-started slices stay thin. Code with no slice is a landscape note. Guild routing gains this skill. `/crav1-intake-to-specs`, `/crav1-spark-to-spec`, and `/crav1-ideas-to-spec` are unchanged. Walkthrough: [docs/from-match.md](docs/from-match.md).
- `/crav1-spark-to-spec` and `/crav1-ideas-to-spec` seed a thin `docs/system/` when that folder is missing, including greenfield and brownfield, then write the spec, then add one landscape index row. Thin uses the same landscape, repos, diagram, and ADR templates as intake, filled from the repo in front of the agent. They do not run an intake interview, call `/crav1-intake-to-specs`, or respec the whole product. An existing `docs/system/` is not rewritten; only an index row is added, plus a repo and ADR row when a new repo is needed. Intake is unchanged and still writes `docs/system/`. Method docs say the layout always includes `docs/system/`. Guild routing lanes are unchanged.
- Claude Code drop-in beside the Cursor install. `.cursor/` stays the source. `scripts/sync-crav1-plugin.sh` still mirrors `plugins/crav1/` and now regenerates `.claude/` (`scripts/sync-crav1-claude.sh`). `scripts/sync-crav1-claude.sh --check` exits non-zero when the committed `.claude/` tree is stale, and the drop-in sync workflow runs that check. Skill names and guild routing are unchanged. No version bump, no release tag, no Claude Code marketplace. Kit commit `acdaa0d` is on main (PR #12). On Claude Code 2.1.286, in a private throwaway git repo, the generated `.claude/` drop-in was used for `/crav1-spark-to-spec`, `/crav1-plan-from-spec`, one implement task, and `/crav1-verify-spec`. The trial feature was a root `hello.txt` of exactly the five bytes `68 65 6c 6c 6f`. Verify passed. Nothing from that repo was pushed. Two frictions: a PowerShell byte-dump that uses a script block was blocked by Claude Code's permission check, and the same bytes were checked another way; the feature-branch skill wants a clean tree, and the branch was created with the kit files still untracked.
- `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, and `/crav1-intake-to-specs` offer once to write `docs/specs/<slug>/work-item.md` when they create a new spec folder and the git remote is Azure Repos (`dev.azure.com` or `*.visualstudio.com`, same detection as the work-item mention). The question is optional. An id (`52`, `#52`, or `AB#52`) writes one line, `Work item: <id>`. Intake asks once and lists the new slugs so the user can give an id per slug or skip. Skip writes nothing and does not ask again in that run. GitHub and other hosts are not asked. The skills do not create or look up a work item, do not call Azure DevOps or `az`, and do not pass `--work-items`. Shared steps: `crav1-draft-commit-message` `references/work-item-offer.md`.
- `/crav1-merge-pr` confirms an Azure DevOps merge commit by re-reading the pull request (`status` completed; the update response can still say `active`) and counting parents with `git rev-list --parents -n 1` on `lastMergeCommit.commitId`. It does not read `lastMergeCommit.parents`, which can be null. If git cannot see the commit, it GETs the commits API and counts the `parents` array, or it says the merge type could not be verified and does not claim a no-fast-forward merge. One parent still stops the skill.
- `/crav1-open-pr` on Windows writes the accepted Azure DevOps description to a temp file as UTF-8 without a BOM and passes `--description "@<file>"`, then deletes the file, so `cmd.exe` does not keep only the first line. Non-Windows still passes the body as one value. `--query` values that contain parentheses must be quoted for `cmd.exe`. `/crav1-merge-pr` does not pass a multi-line body to `az`.
- Cross-cutting skill `/crav1-merge-pr` merges one named pull request only when that turn explicitly asks (number or URL). Always a merge commit: GitHub `gh pr merge <n> --merge`; Azure Repos `az repos pr update --org <url> --id <n> --status completed --squash false --detect false` (a non-squash completion with no `mergeStrategy` is no-fast-forward). `az repos pr update` takes the id, not `--project`, `--repository`, or `--merge-strategy`. No squash, no rebase, no `--admin`, no `--bypass-policy`. A draft is marked ready only as part of that ask (`--draft false` on the same update command, without `--project` or `--repository`). After completion the skill reads the pull request again and requires `status` completed, then a two-parent commit via `git rev-list` (commits API if git cannot see it). If `az` is missing, the update fails, or a branch policy disallows `noFastForward`, the skill prints the REST PATCH (`status` completed, `completionOptions.mergeStrategy` `noFastForward`, `lastMergeSourceCommit` set to the source head) and the web UI steps, and does not run `az rest` to complete the pull request. A `keyring` crash (`module 'keyring' has no attribute 'core'`) or `TF400813` uses a Code Read & Write token in `AZURE_DEVOPS_EXT_PAT`; the skill does not print the token. After a confirmed merge it reports the merge commit hash and, when the tree is clean, fast-forwards local `main`. It does not delete a branch unless asked, and it does not change work-item links. `/crav1-open-pr` names it as a later explicit step and does not run it.
- Optional Azure Boards linking via `docs/specs/<slug>/work-item.md` (`Work item: <id>`). Spec skills may write that file when the user answers the Azure Repos offer. `/crav1-draft-commit-message` leaves the subject and description as drafted, then appends a blank line and the mention as the last description line (GitKraken paste includes it). `/crav1-finalize-commit` keeps that line through the HEAD check and the Cursor-attribution strip. `/crav1-open-pr` adds a `## Work item` section when the file resolves a mention, and its Spec section links that slug’s `spec.md`, `plan.md`, and `tasks.md`. The mention is `#<id>` on Azure Repos, `AB#<id>` on GitHub, and omitted on any other host unless the file already contains a full token. A missing file does not block. On Azure Repos only, the commit and pull-request skills print one hint. `/crav1-open-pr` still does not pass `--work-items`.
- Cross-cutting skill `/crav1-open-pr` pushes the change branch only after an explicit yes, then opens one pull request against the default branch. It does not commit, merge, force-push, or delete the branch. `/crav1-finalize-commit`, `/crav1-complete-task`, `/crav1-complete-tasks`, and `/crav1-complete-features` may name it as an optional next step; they do not run it. Workers stay no push / no PR.
- `/crav1-open-pr` creates an Azure DevOps pull request with `az repos pr create` when the remote is `dev.azure.com` or `*.visualstudio.com` and the Azure CLI is available. GitHub still uses `gh`. If `az` is missing, not logged in, or create fails, the skill prints commands and GitKraken GUI paste fields and does not claim a pull request was opened.
- Subagent files and `name:` values now end in `-agent` (`crav1-architecture-reviewer-agent`, `crav1-complete-task-agent`, `crav1-intake-slice-agent`, `crav1-plan-reviewer-agent`, `crav1-spec-reviewer-agent`) so the Cursor slash picker can tell them apart from skills. Skill commands stay `/crav1-architecture-reviewer` and `/crav1-complete-task`. Descriptions start with `Subagent.`

### Docs

- README leads with the product name **CRAV1 Spec Kit** (`crav1`) and keeps the spec-driven playbook.
- [docs/first-run.md](docs/first-run.md) — install through one task.
- [CONTRIBUTING.md](CONTRIBUTING.md) — consumers install from [docs/install.md](docs/install.md); contributors edit `.cursor/` and sync.
- [SUPPORT.md](SUPPORT.md) — GitHub Issues for a broken skill or install.
- [docs/install.md](docs/install.md) no longer says Claude Code is waiting on a trial.
- Plugin author name and marketplace owner name stay **Crav1**. There is no author email. Questions, bugs, and requests go to GitHub Issues on this repo ([SUPPORT.md](SUPPORT.md)). [LICENSE](LICENSE) is unchanged.
- [README.md](README.md), [docs/from-nothing.md](docs/from-nothing.md), [docs/from-ideas.md](docs/from-ideas.md), [docs/from-intake.md](docs/from-intake.md), and [docs/first-run.md](docs/first-run.md) describe the method (specs, `plan.md`, `tasks.md`, verify). Host file locations, slash-command install, and the note that each host’s plan UI is not `plan.md` are in [docs/install.md](docs/install.md). Guild routing is unchanged.
- [docs/from-ideas.md](docs/from-ideas.md), [docs/from-nothing.md](docs/from-nothing.md), and [docs/from-intake.md](docs/from-intake.md) describe the optional Azure Repos work-item offer when a spec folder is created. [AGENTS.md](AGENTS.md) and the README describe that offer, the merge-pr parent count, and the Windows `@file` description. Guild routing is unchanged.
- [docs/from-ideas.md](docs/from-ideas.md) documents the optional `docs/specs/<slug>/work-item.md` mention. Starter: [docs/specs/_template/work-item.md](docs/specs/_template/work-item.md).
- Guild routing map added: [docs/guild-routing.md](docs/guild-routing.md). Lanes are Specify, Plan, Build, and Cross-cutting for public reuse.
- [docs/guild-routing.md](docs/guild-routing.md) lists `/crav1-open-pr` under Cross-cutting.
- [docs/guild-routing.md](docs/guild-routing.md) lists `/crav1-merge-pr` under Cross-cutting (any lane, only on an explicit ask to merge a named pull request). Specify, Plan, and Build lane ownership is unchanged.
- Plugin author and marketplace owner display name is **Crav1**. The contact email is unchanged. [LICENSE](LICENSE) is unchanged.
- [docs/guild-routing.md](docs/guild-routing.md) adds Research as a cross-cutting helper (no slash command). A lane that must answer a technical question before Specify or Plan flags the process orchestrator or guild lead, who pauses that lane. The researcher writes `docs/specs/<slug>/research.md` (recommendation, trade-offs, confidence, link to the full study) and does not edit specs, plans, or code, or change the lane.
