# Changelog

Notable changes to **CRAV1 Spec Kit** (`crav1`). Version matches `plugins/crav1/.cursor-plugin/plugin.json`.

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

The newest 15 releases are above. The full changelog is https://github.com/Crav1on/crav1-spec-kit/blob/main/CHANGELOG.md.
