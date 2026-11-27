# Changelog

Notable changes to **CRAV1 Spec Kit** (`crav1`). Version matches `plugins/crav1/.cursor-plugin/plugin.json`.

## 1.210.0 (2026-11-27)

Kit 2.0 follows the newest published pre-release, and an update plan stays small.

- **Kit 2.0 pre-release.** When `kit2` is on, plan and apply install kit 2.0 from the newest published `v2.0.0-*` tag. The fetch uses the same short temp folder, `core.longpaths=true`, `core.autocrlf=false`, and clean check as `fetch`. When that lookup or fetch fails, the run uses the bundled tree and `kit2_line` says a newer 2.0 may exist. The line names the version that will be installed and the version installed now.
- **Already current.** When the installed `~/.crav1-2` engine already equals that version and `repo_writes` is 0, `card` is null. There is no install card. The ending says the repo kit is current and kit 2.0 is current, with nothing to do and no reload line.
- **Compact plan.** `files` carries the counts plus the changed lists (`update`, `merge`, `add`, `delete`, `clash`, `left_extra`). The unchanged list is omitted unless `--list-unchanged`. A plan where nothing changes stays under about 20 KB.
- **Script output.** Next to plan and apply, the update skill repeats the rule: never pipe or redirect the script output (`| python -c`, `| head`, `>`). Read it directly.

Docs and tests: update-kit walkthrough, glossary, data layout, and `scripts/tests/test_kit_1210.py`.

## 1.208.0 (2026-11-27)

Parallel kit updates settle on their own, a merge message stays clean, and an update ending says what changed.

- **Kit copies.** When a merge conflicts in installed kit copies and both sides are pristine published releases, `kit_merge.py settle` writes the newer release, including a file that release adds or deletes, checks the tree matches, runs the nothing-lost check, stages those paths, and says so in one line. A kit file that was edited by hand is named and left. The same command applies when `/crav1-open-pr` or `/crav1-merge-pr` says to merge the base in.
- **Merge message.** A merge the kit finishes is `kit_merge.py commit`: `git commit --no-edit --cleanup=strip`, so git's `# Conflicts:` list does not stay in the message.
- **Update ending.** The ending names what changed. A user-level kit 2.0 install with no repo files changed says kit 2.0 was installed in the user folder. The yes card does not offer a commit when the repo has nothing to commit.

Docs and tests: commit and update-kit walkthroughs, glossary, data layout, and `scripts/tests/test_kit_1208.py`.

## 1.207.0 (2026-11-27)

Decisions are written back through the spec, leftover wording is a patch, and cards name the item.

- **Decisions written back.** After an answer or a settled conflict, a check lists notes that still say the choice is open (`Possible answer`, `Waiting for`, `stands until`, `not a settlement`, a conflict line) and other lines that still carry the old date or the old option. A verbatim quote is left as it is. One card asks to mark the notes superseded and update the other lines, and shows the diff first.
- **Stale wording is a patch.** A plan-review finding that only restates old wording offers to update that wording, or to keep it as an open point. Yes patches those lines and confirms the diff. It does not rerun the whole spec skill. When only notes or question context changed and the reviewer reported no scope drift, the plan is not reviewed again. A finding about an open question's wording goes to the open-questions step.
- **Readable names.** A task, constraint, question, finding, or batch row is the plain name first and the code in parentheses, for example `Static-IP notes (P9)` or `Add login page (T3)`. A tight header uses a short name plus the code. The code stays searchable and typeable. A card does not repeat an On yes line that only restates the option. The background sentence is chat text before the card.
- **No silent clear.** Clearing a reopened step needs the token from that step's own reopen card. The clear is not folded into another step's card. A stale-research mark written since the last walk record counts as stale seen.
- **The right next step after a commit.** When the spec walk still has a reopened or unfinished step, the ending resumes that walk. Otherwise it resumes the build walk on the working branch, and it does not name main or master unless that branch is the one checked out.

Docs and tests: question cards, the tighten-and-plan walkthrough, glossary, and `scripts/tests/test_kit_1207.py`.

## 1.206.0 (2026-11-27)

Early-access flags for one repo, kept out of git. With no flag file, an update matches 1.205.0.

- **Flag file.** `.crav1/flags.local.json`, for example `{"kit2": true}`. `.crav1/.gitignore` lists `flags.local.json`. The project's `.gitignore` is not changed. An unknown flag in the file is kept and reported. A file that cannot be read is one plain line, and the update continues with no flags.
- **Words.** `flags-list`, `flags-on <flag> [<flag> ...]`, and `flags-off <flag> [<flag> ...]`. `flags-on kit2` turns kit 2.0 on for this repo. A name that is not known is refused in one line that names the known flags. Known names in the same command are still applied.
- **kit2.** When the flag is on, the update also installs kit 2.0, or updates it, at user level from the release it is applying, through `v2/install.py`. When the flag is off and `~/.crav1-2/installed.json` exists, the update offers `uninstall-kit2`, which removes only the listed files, or `keep-kit2`. The result is one line. The update, add, and unchanged counts stay the same. With no flag file, nothing about kit 2.0 is printed.
- **Registry.** Known flags live in the update-kit flags module. Each entry has a one-line description and a status of `experimental` or `beta`. `kit2` is the first entry (`experimental`).
- **Dry run.** The maintainer dry run prints `Flags: none` or `Flags:` plus the flags that are on, and dry-runs the kit 2.0 step. With no flag file, the copy block is unchanged.

Docs and tests: update-kit walkthrough, glossary, data layout, and `scripts/tests/test_kit_1206.py`.

## 1.205.0 (2026-11-25)

Kit 1.x leaves a side-by-side kit 2.0 alone, and a 1.x update is never offered a 2.0 tag.

- **Update commit.** The kit commit stages the files the release ships. A `crav1-` name pattern is not the list, so a `crav1-2-` skill is not swept into `Update CRAV1 kit`. The command takes the release trees (`--old` and `--new`, or `--new` on add and `--old` on remove).
- **Left alone.** A skill or agent named `crav1-2-`, a `.crav1-2/` folder, and `sot/` are not written, staged, or deleted. `remove` already deletes only files in the release list. That list still leaves those paths in place for Cursor, Claude Code, Codex, and Copilot.
- **Lint and sync.** Kit-lint and the generators that used to match `crav1-*` now match `crav1-[a-z]`, so a `crav1-2-` name is not treated as a 1.x skill or agent.
- **Tags.** The latest tag is the newest published 1.x release. `v2.0.0` and `v2.0.0-alpha.1` are ignored.
- **Dry run.** The maintainer dry run prints a progress line on the console as each step starts, and a dot every few seconds when a step runs long. The copy block is unchanged.

Docs and tests: update-kit walkthrough, glossary, data layout, and `scripts/tests/test_kit_1205.py`.

## 1.204.0 (2026-11-25)

Codex installs into a consumer project. Copilot stays generated and is not installed.

- **Codex.** `/crav1-update-kit add codex` copies `vendors/codex/` into `.agents/skills/`, including `agents/openai.yaml` on each command-only skill. Commands in that copy are `$crav1-`. Each skill's first line reads `../crav1-docs/reference/kit-rules.md`. The project's `AGENTS.md` is not written.
- **Vendor list.** `.crav1/kit.json` holds `schema` 1 and the vendor names. The installer writes it. `add` and `remove` change it. A missing file is inferred from the marker files, and the same yes writes it. `detect` reports `vendors_from` as `kit.json` or `inferred`. An unknown name is refused.
- **Remove.** `/crav1-update-kit remove codex` deletes kit-owned files that still match the installed release. A local edit is a clash, with the same `keep` or `take` as any other tree. A file the release does not contain stays. Other vendors' folders stay.
- **Plan.** Counts come first, then at most 10 sample paths, and every clash. A second apply that finds the same files changes nothing. A normal update of Cursor and Claude Code does not write Codex when Codex is not listed.

Docs and tests: install, update-kit walkthrough, glossary, data layout, and `scripts/tests/test_kit_1204.py`.

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
- **Open count.** `plan_check.py open-count --review <file> --vendor copilot` prints `open: <n>` from the reviewer's `P#` lines. The walk uses that value. `reviewed --items` recomputes the Reviewed line from the items file.

Docs and tests: tighten-and-plan and spec-to-plan walkthroughs, glossary, data layout, and `scripts/tests/test_kit_1202.py`.

## 1.201.1 (2026-11-24)

Fixes for the design screen and the ready check. The rules were already the ones below; the scripts now follow them.

- **Design screen.** Run next comes first, with one reason line. A topic that exists only on `design/<topic>` offers the switch card. `resume --json` leaves the files unchanged, including a parked Status. Dated proposal pages under `docs/architecture/proposals/` count. Waiting lines name each person once, with the date recorded on the question, and stay near 120 characters. When every open decision is waiting on named people, Run next names the open-questions command and the proposal. A parked screen has no Park command. An ended screen's one command is `reopen`. Run `scripts/design_run.py --vendor copilot` from the repo root.
- **Script output.** Do not pipe a script's output, in bash or in PowerShell. A pipe such as `| head` can cut an ending off at a lone `{`.
- **Task names.** A `from <base>` clause and parenthesised marks such as `(manual, secret, …)` are not the task name. The name is the outcome after that clause.
- **Claims.** `claims.py add` leaves `claims.md` unchanged until `--yes`. A second start on the same claim keeps the original since time.
- **Ready check.** A `--text` read that does not pass `--write-map` does not add a `PR author` line. A merged pull request is still recorded, as in 1.177.2. A free-text mention such as `(PR 12)` or `(PR 7 merged into develop)` does not mark a task done; only a tick or the kit mark `(PR n, merged)` or `(PR n) merged` does. A task with `(after: T#)` stays held while T#'s pull request is open, and the held line says `waits for PR <n> to merge`. A task that says `(after: PR 87)`, or whose text says `after PR 87 merges`, stays held the same way until the host says PR 87 is merged. The ready check, the build map and the walk ending all say `waits for PR 87 to merge`. When the code repo is not recorded, the check uses the same one-time repo question as 1.177.2. `/crav1-plan-from-spec` and `/crav1-tighten-plan` write `(after: PR N)` for that prose: `plan_check.py order --vendor copilot` names the line, and `plan_check.py after-pr --yes --vendor copilot` writes the mark. A pull request the host says is merged is cleared with `/crav1-build-walk <slug> T#`. A blocked line names only the tasks that wait on that block. Claude Code sends one question per question-tool call.

Docs and tests: design, build-walk and ready-check walkthroughs, data layout, question cards, install, running scripts, and `scripts/tests/test_kit_12011.py`.

## 1.201.0 (2026-11-22)

A vendor table, with no change to a Cursor and Claude Code update.

- **Vendor table.** `vendors.json` in the update-kit skill lists, for each host, the folders the kit owns, the frontmatter a skill needs, the command prefix, and extra files. The Cursor and Claude Code rows reproduce the 1.200 allow-list. Codex and Copilot are listed and are not installed or generated.
- **Same plan.** `collect_kit` and the kit-path checks read that table. A plan and an apply on an existing Cursor and Claude Code repo match 1.200 byte for byte.
- **Report.** `update_kit.py detect --vendor copilot` adds `vendors`. `update_kit.py vendors --root . --vendor copilot` lists each vendor's folder and skill count and writes nothing.
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
- **Kit update line.** `update_kit.py available --vendor copilot` and both walks' starts say `Kit update available: <installed> -> <latest>` with `/crav1-update-kit`; read-only, short timeout, silent offline.
- **Fewer cards.** One yes pushes and opens the pull request; Open PR only appears only when the head is pushed. `Not yet` on the merge card also commits and pushes the walk's specs files.
- **Dependency containers.** New `dep_check.py containers` finds docker or podman containers, stopped ones and a stopped podman machine, and recommends starting them; install only when nothing exists. A worker runs only the tests that do not need a down dependency, then reports the blocker.
- **Ready-check ending.** Not-ready with tasks that can start names the hard hit and those tasks. Your own pushed task waits for its PR's merge. `Resume the walk` appears only for held questions and names who answers. A repeated question is shown once and cut near 120 characters. A result that only reflects waits is recorded without a card. A lone build-map change is `Commit the updated build map:`.
- **Small fixes.** No `Next:` lines in walk prose. pr-status finds the Azure DevOps organization in `repos.md`. merge-pr fetches before the PR-note check. Every Windows `--query` value is quoted. Build-walk cards show plain labels.

Docs and tests: build walk, tighten and plan, verify, update kit and pr-status walkthroughs; `scripts/tests/test_kit_1198.py`.

## 1.197.0 (2026-11-20)

Fixes from a live spec walk: cleaner batch cards, a prod lint that judges each check, release gates, quieter acceptance checks and a scoped plan review.

- **Whole labels only.** The batch label map replaces an option only when the whole option, or the part before its `:`, is an internal id. Words such as keep or ask inside option text stay as written.
- **Prod lint per item.** `plan_check.py lint --vendor copilot` reads each verify item and its target: file names such as `main.prod.bicepparam`, PROD-like settings, unit and contract items, local compiles and read-only checks are not flagged. A `(manual, prod` task whose own text drops, deletes or changes data needs `owner:` and a Risks line.
- **Release gate.** A task marked `(after-release: main)`, or a manual prod task that a Risks line ties to a release, is Waiting in the ready check and is never offered as the first task. New mark in the data layout.
- **Quiet tickable.** `walk_progress.py tickable --vendor copilot` asks only about a failing row or a passing row with no evidence. Untested and pending rows stay open with no question; one `waiting_line` counts them.
- **Small fixes.** `start` uses the playbook it found by name (no second run). The claims "Kept claimed tasks" line is gone when nothing changed. `start_check.py` reads the PR number from Azure DevOps `Merge pull request 82 from` subjects. Housekeeping says `Applying with no card` and `plan_check.py reviewed --items --vendor copilot` leaves housekeeping out of the open count.
- **Card rules.** A batch question is only the short `Card:` line; the items live in the bullets and the `On yes:` line. Before a yes the walk says what it would change, never that it already did.
- **Fewer cards.** Plan-from-spec applies housekeeping refreshes with one summary line, and the ready check is recorded with no save card.
- **Scoped plan review.** New `walk_progress.py review-packet --vendor copilot` writes the reviewer's input outside the repo: the changed tasks, their spec sections by line range, and the plan's Risks and Linter, with a quick mode for small changes. The reviewer runs in the foreground and never reads `spec.md` whole.
- **Local fast-forward card.** The build walk's card for a code base branch behind origin now reads `Your local develop in orders-api is 2 commits behind origin/develop. Update it locally before the build?`, with **Update local develop** and a result line that says nothing is pushed, then the work branch and task it builds. New `code-behind --branch --task`.
- **Bare PR numbers from a specs-only checkout.** When no record names the number and this checkout holds no code, `pr_common.py resolve` checks the code repos in `repos.md` read-only and uses the single match, otherwise asks with those repos listed. It never suggests installing a CLI before the host is known. `/crav1-review-pr` ends with a Run next block when the host is still unknown.

Docs and tests: the spec walk walkthrough, question cards, pr-common and marks; `scripts/tests/test_kit_1197.py`.

## 1.196.0 (2026-11-20)

Start checks that trust origin, claims that clear themselves, and fewer, plainer walk cards.

- **Shared start check.** New `crav1-add-to-spec` `scripts/start_check.py`: one quiet `git fetch --prune origin` per checkout, `origin/<branch>` before a stale local branch, and a tip that is already merged is found with its merge commit and PR. `merged_since_sync.py check` and `walk_progress.py code-drift --vendor copilot` use it; `--no-fetch` skips the fetch.
- **Claims prune.** New `claims.py prune` clears claims whose tasks are all ticked or whose branch is merged into `origin/<base>`, with one summary line. It runs at the walk start and after `/crav1-merge-pr`. Unfinished claims are never cleared, finished claims get no age warning, and the "kept unchanged" lines are gone.
- **Prod verify rule.** Verify runs on DEV or TEST; prod checks are read-only (health, version, config, existence). A prod-write check is its own task with an owner, the user's yes and a Risks line. New `plan_check.py lint --vendor copilot` flags both; tighten-plan recommends DEV or TEST.
- **Fewer cards.** `readiness --covered <step>` drops the reopen card when the reopen came only from a fact the walk just recorded and a finding covers it. Tighten-plan housekeeping applies with one summary line. The save rides on the step's last yes.
- **Plain walk cards.** Batch cards show one background bullet per item, a short question and an `On yes:` line. Labels are plain words with no letters or internal names (label maps in `plan_check`, `batch_offer` and `walk_progress`). `suggest` is offered only for wording findings.
- **Tickable at the start.** New `walk_progress.py tickable --vendor copilot` ticks acceptance items whose verify row passes with evidence, in one line; when an open task touches the evidence it ticks now and adds a recheck line to that task's verify note.
- **Endings.** The run ending prints the script's block exactly, Catch up first included; tighten-spec's last `Next:` lines became Run next blocks.
- **Walk fixes.** A locked skill inside the walk prints no Run next or `Uncommitted:` line; `spec-finding` asks a `kind-conflict` card when code-drift text is passed as spec text; after a jump-back the walk follows its `continue` list; the plan reviewer runs in the foreground; the uncommitted count includes changed notes and sources.

Docs and tests: walkthroughs for the build walk and the spec walk; `scripts/tests/test_kit_1196.py`.

The newest 15 releases are above. The full changelog is https://github.com/Crav1on/crav1-spec-kit/blob/main/CHANGELOG.md.
