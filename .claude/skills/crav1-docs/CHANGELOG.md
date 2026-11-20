# Changelog

Notable changes to **CRAV1 Spec Kit** (`crav1`). Version matches `plugins/crav1/.cursor-plugin/plugin.json`.

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

The newest 15 releases are above. The full changelog is https://github.com/Crav1on/crav1-spec-kit/blob/main/CHANGELOG.md.
