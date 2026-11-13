# Glossary

Words the kit uses in its skills and docs. Abbreviations are written in full first. Where a word is a folder or a file, [Data layout](data-layout.md) has the details.

## Abbreviations

| Short | In full | Meaning here |
| --- | --- | --- |
| SDD | Spec-driven development | The method: the spec, not chat history, is the source of truth. See [The method](method.md) |
| ADR | Architecture Decision Record | One decision with its real alternatives, under `adr/`. Written only when there was a real choice |
| MADR | Markdown Architectural Decision Records | The ADR template shape the kit uses |
| ADO | Azure DevOps | Microsoft's hosted service for repos, pipelines, and boards |
| Azure Boards | — | The work item part of Azure DevOps (ADO). The kit reads and writes Features there only after a yes |
| EARS | Easy Approach to Requirements Syntax | One export format for a spec |
| BDD | Behavior-driven development | One export format for a spec (Given, When, Then) |
| BMAD | BMAD Method | One export format for a spec, shaped for that method |
| PR | Pull request | A request to merge a branch, on GitHub or Azure Repos |
| CI | Continuous integration | The checks a host runs on each push or pull request |
| UI | User interface | |
| LLM | Large language model | The model an agent runs on |
| TL;DR | Too long; didn't read | The short answer first |
| SQL | Structured Query Language | Read-environment looks at SQL metadata only, never rows |
| SAS | Shared access signature | A storage token. Always treated as a secret |
| API | Application programming interface | |
| VPN | Virtual private network | |

## Words

**Starter option.** One of the six ways in: spark-to-spec, ideas-to-spec, bundle-to-specs, existing-to-specs, read-environment, fix-bug. Asking for startup options lists them and does not run one.

**Branch (of a skill).** One path inside a merged skill, kept in `branches/<id>/BRANCH.md` next to its `SKILL.md`. It holds the old skill's rules unchanged. The opening question picks the branch.

**Opening question.** The question a merged skill asks first, with options, to pick a branch. Skipped when the message already answers it or carries a choice word.

**Recommended option.** In any question with options, the option the kit recommends is listed first and its label ends with ` (Recommended)`, such as `Keep (Recommended)`. The question text does not repeat it as `Recommendation: X`. A question with no recommendation has no label.

**Choice word.** An exact word that answers a merged skill's opening question, such as `push tasks` for `/crav1-ado-sync`. A word in the invocation skips the question. A headless or bot run with no word stops and names the valid words. Listed under `choice_words` in `skills.yaml`. Not a `--flag`.

**Later skill.** Any skill that is not a starter option. Most run once specs already exist.

**Lane.** One of the groupings of skills: Starters, Specify, Plan, Build, and Cross-cutting. Inside each lane, skills sit in groups by phase. The [skills reference](../reference/skills.md) is organized this way, and [guild routing](../guild-routing.md) maps each skill to a lane.

**Comment as posted.** The review comment as the reviewers see it, saved word for word in the PR note's history next to the comment as drafted (the review-pr follow-ups note before 1.97.0). `/crav1-review-pr` finds it on the pull request or takes a paste, compares it with the draft, and tags drafted points left out `not posted <date>` in the PR record, still open. A re-review compares against it (1.67.0).

**Cross-cutting.** A skill that may run from any lane and does not move work into a lane.

**Spark.** One or two sentences about what to build. Input to `/crav1-spark-to-spec`.

**Dump.** A pile of notes, tickets, old docs, diagrams, or screenshots to sort onto specs.

**Intake.** One or more files that may describe a whole system with several v0 features.

**Ready (task).** A task that can be built now: `plan.md` exists, no open question or plan Risk blocks it, the tasks it waits on are ticked, and it is not ticked itself. A ticked task that `verify.md` does not list as verified is **needs verify**, not done. A task that waits on a held task is **held** too, with the reason `held, waits on T3`. `/crav1-tasks-ready-to-build` lists them. Since 1.132.0 the ready check result is `ready`, `ready-partial` (some tasks can start, some are held), or `not-ready` (nothing can start). Since 1.133.0 that report groups the ready tasks and the held tasks by build-map branch, and names each task as `T#` plus its short name. See [Readiness marks](data-layout.md#readiness-marks).

**Build map.** The file `docs/specs/<slug>/build-map.md`. It shows how the slice will be built, one branch per plan step, in waves, with a flowchart that puts each wave side by side. The row branch is a branch named on the task line (`(map:)`, else `(branch:)`, else a `feat/…` name in the sentence, else `committed later on`), else the plan step's `feat/<slug>-<words>` name, else a name from the task (1.140.0). A merged branch, or a branch deleted locally and on the remote, is not what `--recommend` prints. A task whose own line records the merge stays on that branch in the map. `/crav1-build-tasks` offers the name `--recommend` prints. The wave heading is always `N branches, M can start now`, including `1 branch, 1 can start now`. An overlap note names two branches in one wave that share a requirement or a path. It does not change readiness. The row names the branch, what it delivers, each task as `T#` plus a short name, what it waits for, any open question and who has the answer, and whether it is ready now. A short name is the work-item title when `work-item.md` has `task: T# <title>`, otherwise the task text up to the first parenthesis, `, in `, or the end of the sentence. When the task text names a different branch, the row adds `Task text names feat/x; built on feat/y`. When the row is the task-line branch and the plan step's name differs, the row adds `Plan step names feat/x; built on feat/y` (1.140.0). Since 1.133.0 the Tasks field shows the id, for example `T5 orders-api: require pipeline 6 as build validation`, and a done task is `~~T5 short name~~ ✓ done` with its pull request, branch, or commit. The map is rewritten on every ready check, so the ids match `tasks.md`. Prose outside that field still drops a task id. A removed id does not leave a dangling possessive or an empty pair of parentheses. `/crav1-tasks-ready-to-build` rewrites it every run. The word `build-map` shows the short summary: how many branches can start in each wave, then that wave's overlap notes. Since 1.128.0. Since 1.132.0 a ticked task stays in its wave, and the heading counts those done tasks apart from the branches that can start. A wave whose every task is done is a `<details>` block. The rows stay in the file.

**Build walk.** `/crav1-build-walk` (1.142.0). One guided walk of one work branch: build, verify, commit, open the pull request, merge the base into the branch, merge the pull request, tick, then the next task. It opens those skills by file. While one branch is in progress there is one Next line, and the step skill's own Next is not printed. Started from a ready-to-build report, each ready branch has its own Next, with the T number beside the task name. It asks `yes` before a write, a push, an open, or a merge. It never rebases. Since 1.143.0 a live command the assistant's permission check refuses, after the user's yes is on record, is not a missing yes.

**Build progress.** The file `docs/specs/<slug>/build-progress/<branch>.md` (1.142.0). One file per work branch. The file name writes each `/` as `--`. It records the step, `Owner:`, `Cut from:`, the merge list, and normalized hashes with `Content stamp: normalized`. A checkbox, a `(PR n)` or `(done)` note, and `(live yes: …)` do not change the hash. It is not `walk-progress.md`. The spec, plan, and tasks stay the source of truth.

**Other-owner mode.** The build walk's mode after `switch`, when the pull request author or a commit author is someone else (1.142.0). The walk never opens a pull request, never merges the base into the branch, and never merges or completes the pull request. One comment per push. The description changes only on `edit description`. Ticks wait until that pull request is merged.

**Runs live.** The task mark `(Runs live)` (1.142.0). The build runs a live change. The walk writes the script, runs a dry run, then asks for the user's yes. That yes is `(live yes: <name>, <date>)` on the task line. Without it the task stays unticked. An `Approved:` line does not replace that yes.

**Merge list.** The ordered lines in a build-progress file (1.142.0). A branch that was cut from an unmerged branch merges back into that branch before the parent merges onward. `Merge list: none` means the branch was cut from the base.

**Approval needed.** A sibling section of `## Open questions` on `spec.md` (1.141.0). Each item names the person (`Person:`), what they approve, and the tasks it holds (`Holds: T4`). With no matching `Approved:` line those tasks are waiting on that person and other tasks can still start. `/crav1-plan-from-spec` adds the item from a constraint such as `The partner gives a yes before the script is applied.` `/crav1-build-tasks` adds it when a build finds that yes missing. `/crav1-record-approval` writes the lasting line `Approved: <person>, <source date>, <source>, "<quote>" (accepted by <recorder> <date>)` only after `accept` in that run. The source date stays. An earlier quote does not count by itself. No skill removes an `Approved:` line. This is not the data-model line `Approved: business-model r<n>, <date>`. See [Data layout](data-layout.md#approval-needed).

**Blocking.** What keeps a task from being ready, with one reason: a kept-open question (its `Blocks:` line names the task, `Blocks: none` blocks no task, or it has no line and holds the `T#` ids in its text, or the whole slice only when no task is named and resolve-open-questions has never been recorded), a plan Risk that says do not implement until resolved when that risk matches no question or matches a question with no `Blocks:` line, or an earlier task that is not ticked (from `(after: T#)`, or task order when none is recorded). A risk matches on the question's first sentence, a `(question: <first words>)` tag, or the same Blocks tasks named in the risk (1.126.0). A reason from a written mark is **recorded**; a fallback is **inferred**. Since 1.125.0 any `Blocks:` line wins over that Risk wording. Since 1.127.0 a wait on a real earlier task is **waits in order**, a task held by an open question is **waiting**, and only a cycle, a missing task, a plan risk, or a missing plan is **blocked**. The slice is ready when the first task can start and nothing else blocks. Since 1.132.0 a dependent of a held task is held too. The check is `ready-partial` when some tasks can start and some are held, and `not-ready` when nothing can start. Since 1.141.0 an unapproved `## Approval needed` item is the same kind of hold, named for that person, and a matching `Approved:` line clears it.

**Dependency order.** The order tasks are listed, built and verified in since 1.103.0: the `(after: T#)` graph wave by wave (a task with no `(after: …)` waits on the task just before it), lowest number first inside a wave, not plain task number. Since 1.133.0 the ready check groups ready tasks and held tasks by build-map branch, in wave order then map order, and prints one `Next:` line per branch that can start. Since 1.143.0 that line recommends `/crav1-build-walk` and names `/crav1-build-tasks` for one task without the walk. Tasks that wait on each other in a loop are blocked as a cycle.

**Load path.** The files a skill reads for one run, since 1.104.0: `SKILL.md` routes first, then only the chosen path's file (one report, one branch, one reference) is read. Other paths stay closed. Since 1.106.0 `/crav1-retire-spec`, `/crav1-show-or-ask-open-questions`, `/crav1-explain-this-code` and `/crav1-glossary` route to one `branches/<mode>/BRANCH.md`, and `/crav1-help` reads `reference/index.yaml` and one `reference/skills/<name>.md` page, opening `CHANGELOG.md` only for a release question.

**Report word.** `report-<type>-<depth>` on `/crav1-what-do-we-know-about-this` (1.104.0): type `feature`, `change`, `build`, or `playbook`; depth `short` or `full`, plus `report-playbook-walk` (1.116.0) and `report-data-model-full` (1.118.0). Feature, change, build, and playbook reports are written outside the project. A playbook's first write stays there. On apply, a filled playbook is copied to `docs/playbooks/<topic>.md` (1.120.0). A draft with no filled answer is not copied. `report-data-model-full` reads one saved data model and writes an immutable Markdown review and a PDF under that model. It does not model again. A full playbook can be walked in chat (1.117.0): the chat states each item in words and does not use the report's item ids, and `go to N9` still jumps. When the user's words and the record disagree, the walk works out the intended outcome with them before anything new is written.

**Committed playbook.** The copy of a playbook report at `docs/playbooks/<topic>.md`, written when `/crav1-resolve-open-questions apply` runs (1.120.0), including at the end of a playbook walk and in step 1 of `/crav1-tighten-and-plan-ready-to-build`. The file name comes from the report subject, lowercase and kebab-case (`CC Process 1.0` becomes `cc-process-1-0.md`). The name is shown once before the first copy and then stays fixed. The same playbook is the file's `Docs path:` line, or else the one committed file whose title subject matches. Reapply overwrites that file. When `Applied as:` does not match, the file was edited in the repo and the diff is shown before overwrite. Specs the apply touched link it with `Playbook: docs/playbooks/<topic>.md`. `Answer:` and `Change:` lines read back from the committed copy. This write is not a git commit.

**Data model.** The saved model for one scope, under `docs/data-model/<model>/`. Confirmed snapshots, proposed revisions, questions, comparisons, review exports, and (1.121.0) `history.md` for the previous text of a revised item are separate. An `Approved:` line names one stage and one revision. The state script records a content hash of the model files and refuses a hand edit. See [Data layout](data-layout.md).

**Flow word.** `manual-flow` or `auto-flow` on `/crav1-model-data` (1.118.0). The scope after it is an optional value. Both flows use the same modeling rules. Manual flow confirms the business model before physical design. Auto flow continues after a budget approval and leaves unconfirmed results as proposals.

**Correction pass.** One cycle in an auto flow: find an issue, revise the proposal, revalidate what that change affects. The default budget is 5 passes, shared by the whole run, plus 20 minutes. The first proposal is a baseline and does not use a pass (1.121.0). A `revise` of a recorded item during an open run stays inside the current pass. The run shows the budget before it starts. A new run does not inherit the old count.

**Route.** An ordered list of commands for one situation, such as a new slice or new information on an existing slice. Each step says when it applies, and some are optional. The routes live in `docs/reference/workflow.yaml` and are shown in [Workflow routes](../reference/workflow.md). `/crav1-help` answers order questions from them.

**Run ending.** The last lines of a skill's chat, since 1.122.0. `Next:` is one line, the single step to run now and why. `Waiting:` is one line per step that is blocked, or that waits on a person's yes and is not a blocker (1.129.0), naming who or what it waits on. Since 1.143.0 a recorded yes that the assistant's permission check refused is a Waiting line that says the yes is on record, not that it is missing. `Uncommitted:` is a trailing reminder when files changed and are not committed, not a step. A later step that depends on `Next` is not listed. Every skill follows [How a run ends](../reference/run-ending.md), including `/crav1-export-spec`.

**Kit script.** A `.py` file a skill names. Since 1.127.0 the interpreter is `python3`, then `python`, then `py -3` on Windows. The Store alias message `Python was not found` means that command was not found. See [Running a kit script](../reference/running-scripts.md).

**Command-only.** A kit skill whose frontmatter says `disable-model-invocation: true`. It runs when a person types the slash command. Since 1.134.0 another skill that runs it opens that skill's file with the file-read tool and follows it. The path is the sibling `../crav1-<name>/SKILL.md` from the running skill's folder. That sibling is `.claude/skills/crav1-<name>/SKILL.md` on Claude Code, `.cursor/skills/crav1/crav1-<name>/SKILL.md` in the Cursor drop-in, and `skills/crav1-<name>/SKILL.md` in the Cursor plugin. A refusal because the skill is command-only is not a reason to stop. See [Opening another kit skill](../reference/open-skill-file.md). `/crav1-help` and `/crav1-update-kit` are not command-only.

**Kit update.** `/crav1-update-kit` (1.131.0). Replaces the installed kit on the current branch with a published release. The default target is the latest published release. It asks before it writes, commits, or pushes. The commit message is `Update CRAV1 kit vA to vB`. Other branches keep the previous kit until this branch is merged into them.

**Published release.** A `vX.Y.Z` tag on the kit's GitHub releases. `/crav1-update-kit` accepts only that. `main`, a branch, a commit, and an open pull request are refused.

**Walk progress.** The file `docs/specs/<slug>/walk-progress.md` written by `/crav1-tighten-and-plan-ready-to-build` (1.119.0). It records which locked steps are done, when, and the version of the spec, plan, and tasks each step covered. The ready check also records a `verify.md` version. The playbook line is intake only. Since 1.120.0 that line is the `docs/playbooks/` path, not a file outside the repo, and the walk accepts a `docs/playbooks/` path as its playbook argument. The spec, plan, and tasks stay the source of truth. Since 1.123.0 the script stamps each `Done` time itself. A later step inside the walk leaves earlier steps done. An optional extra the walk itself runs is recorded with `- Extra:` when it finishes, and that write does not reopen earlier steps. `cover` is optional and only counts a write made outside the walk. A hand edit or `/crav1-add-to-spec` between sessions reopens only the steps that change affects. A reopened step blocks the ready check until it is rerun or cleared with `nothing new`. Since 1.127.0 the ready check records `Result: ready` or `Result: not-ready`, an older `Result: done` still reads, and `Acknowledged stamp:` quiets one shared Done warning. Since 1.132.0 it also records `Result: ready-partial` when some tasks can start and some are held. That result is covered, and it is not a `not-ready` mark. Since 1.135.0 a spec finding during plan review records `- Jump-back:` with `Continue:`, and the same finding coming back records `- Open point:`. Since 1.137.0 `Spec body:` and `Questions version:` split the spec stamp, so an edit confined to `## Open questions` reopens only resolve-open-questions. Since 1.141.0 `## Approval needed` is in neither stamp, so editing it reopens no step. That step alone does not force `not-ready` when some tasks can start. `Kept questions:` names questions that stay Waiting through that drift. Since 1.138.0 `Content stamp: normalized` means the hashes ignore line endings and progress marks: a task checkbox, a `(PR n)` or `(done)` note on that task line, and `(PR n)` on a Match `Branch:` line. Those edits do not reopen a step and do not ask to clear. An older step has no such line. A progress-only edit still matches. The next record writes the line. Since 1.139.0 a merge conflict that is only those hash lines is settled by `walk_progress.py resolve-stamps`. `Done` and `Result` stay. A hash becomes the merged file's hash only when it matched that side and the merge differs by progress alone. A real edit keeps the upstream hash, so the walk reopens the steps that edit affects.

**Jump-back.** One question card during `/crav1-tighten-and-plan-ready-to-build` when plan review finds a spec defect (1.135.0). The recommended option runs `/crav1-tighten-spec` on that finding only, by opening `../crav1-tighten-spec/SKILL.md`. The walk then continues through the plan and the ready check. It does not pause. The same words are offered once. A plan finding stays in `/crav1-tighten-plan`.

**Open point.** A spec finding the tighten-and-plan walk will not jump back for again (1.135.0). Recorded as `- Open point:` in `walk-progress.md`. The walk continues.

**verify.md behind.** The ready check's flag when `verify.md` still lists a ticked task as not implemented, when its `Next:` line names a ticked task, or when a merged task is still `Not implemented` (1.136.0). A merged task whose row is still `[ ]`, and whose only leftover is the tick, is not behind. The check prints `Waiting: /crav1-verify-build-against-spec <slug> - verify.md is behind tasks.md (T2)` and does not print that Next line. A verify-only change does not force `not-ready`. The walk and the ready check do not write `verify.md`. Only the walk's record or `clear --yes` restamps `walk-progress.md`.

**Tick pending.** The verify status **Implemented, verified, tick pending** (1.136.0). The evidence passed, the `tasks.md` row is still `[ ]`, and the pull request is recorded merged. It is not Not implemented. The open checkbox is a Gap. Verify may tick that one row after a yes. `/crav1-build-tasks` can tick it with no worker whatever the ready-check result, including `not-ready`. That tick does not start a worker and does not re-implement.

**Needs tick.** The `task_order.py` section for a recorded-merged task that is still unticked (1.136.0). The task is done for dependency order, so it is not Ready and not Next.

**Slice, slug.** A slice is one feature's spec folder. Its slug is the folder name under `docs/specs/`.

**v0.** The first version of a feature. Intake writes one spec per confirmed v0 feature.

**Landscape, picture.** The system notes in `docs/system/`: the short description, the diagram, how the parts connect, and the feature index. Refresh-system-notes keeps the picture up to date.

**Feature index.** The table in `docs/system/landscape.md` with one row per slice and its status.

**Glossary rows.** The words a source already uses, in `docs/system/glossary.md`. New rows are added in sorted place by term. Existing rows are not rewritten. A meaning the source does not state is `to be researched`. `/crav1-glossary` shows the rows, answers one word, and fills `to be researched` rows: from `docs/` with a file and line link, or from the web for public terms after a yes (1.101.0). `/crav1-glossary as-file` writes the list to `.crav1/glossary-list.md`, ignored by git (1.102.0).

**Match status.** Under a spec's `## Match`: done, partial, not in the code, or retired.

**Note.** One full input (fact plus passage, dump, code change, meeting) and its source in `docs/notes/YYYY-MM/`, filed by source date (1.61.0). Specs link it as `Full source:`; `used_by` records which specs took points. Never absorbed. Older notes may still say `Absorbed by`.

**PR note.** One note per pull request in the specs repo's `docs/notes/YYYY-MM/`, filed by the pull request's created date, `kind: pull request`, holding its title and description (a changed description is appended as a dated section). Written by `/crav1-review-pr`, `/crav1-merge-pr`, and the code-change branch of `/crav1-add-to-spec` (1.65.0), and `/crav1-pr-status` (1.97.0). It holds the PR record.

**PR record.** The PR note's `## PR record` section: one merge-safe line per point, dependent pull request, reader, readiness and state, shared by `/crav1-pr-status`, `/crav1-review-pr`, `/crav1-add-to-spec` and `/crav1-merge-pr`. `/crav1-merge-pr` stops on `Ready: no` unless you say `anyway` (1.97.0).

**Specs repo, code repo.** The specs repo is the checkout with `docs/specs/`; a code repo is a repo in its `docs/system/repos.md`. `/crav1-review-pr` reviews a code repo's pull request from the specs repo, or with both open (1.65.0).

**Notes index.** The generated `docs/notes/index.md` and `docs/notes/YYYY-MM/index.md`, built from note front matter by `notes_index.py`. Never hand-edited.

**Source date.** The date of the original (meeting date, mail sent date, commit date). It names the note file and its month folder; the import date is recorded as `imported`.

**Parked spec.** A spec with a `Parked: date, reason` line, set by `/crav1-retire-spec park`. Plan, build, and ado-sync push skip it. Add-to-spec writes nothing into it; matching input becomes a waiting note.

**Retired spec.** A spec moved to `docs/specs/retired/` by `/crav1-retire-spec` (retire or merge). Every spec-scanning skill skips that folder.

**Pointer.** The one-line `Moved:` `spec.md` left at a spec's old path when it is retired, merged, or converted. Nothing is deleted.

**Waiting note.** A note in `docs/notes/YYYY-MM/` with the slug in `waiting_for`: the full input that matched a parked spec. Never absorbed; it stays the shared full source and `Used by` grows as specs use it.

**Saved explanation.** The optional `explain-this-code-<target>-<date>.md` that `/crav1-explain-this-code` writes when the user says yes to Save as .md: in the Downloads folder by default, or a path the user names, never into the repo by default. Its header names the paths covered and `<branch>@<short sha>`. Not a note: the kit never reads or indexes it.

**Imported source.** The original of a mail, transcript, minutes, chat, screenshot, or diagram, kept in `docs/sources/` so a quote can be checked. See [Data policy](data-policy.md).

**Research note, stale mark, point.** A research note lives in `docs/research/`. When a later quote changes what it says, the note gets a `Stale since` mark after a yes, and each spec that relies on it gets one `Point:` line per hit.

**Open question marks.** `Pending:`, `Asked:`, `Answered:`, and `Blocks:` lines under a spec's open question, including `Blocks: none` when the question blocks no current task (1.125.0). Since 1.137.0 a missing `Blocks:` line holds `T#` ids named in the question text. `Blocks: whole slice` holds every unfinished task and stays after resolve-open-questions is recorded. See [Data layout](data-layout.md#open-question-marks).

**Environment marks.** Confirmed lines in `docs/environments/marks.md` saying which environment a cloud resource belongs to. See [Environment marks](../environments-marks.md).

**Production (prod).** The live environment. The kit never reads production data. Pre-prod, resources shared with prod, and prod-only resources are read for shape and connections only, after one yes.

**Work item home.** Where the work items for one implementation repo go, written as `ADO: <org>/<project>` in the `Work items go to` column of `docs/system/repos.md`. The first Azure Boards skill that needs a repo's home asks for it once, suggesting the repo's own project, and never guesses it. A spec whose repos are in several homes gets one Feature in each home. `Jira: <project>` is reserved for later and is not read yet. See [Data layout](data-layout.md#work-item-homes).

**Sweep progress.** The file `docs/system/sweep-progress.md` for one sweep of the linked repos. It lists the current run's items and which are done, so a stopped run resumes. Written only by `scripts/sweep_progress.py` in `/crav1-update-specs-from-changes-and-prs`. A `Read: sweep` line on a PR note is that sweep's watermark and is not a person's `Read` line. Since 1.124.0.

**Synced at.** The branch, short commit, and date a repo was last read. In `docs/system/repos.md` it is one line per repo and branch under `## Synced at`, `- orders-api main@abc1234, 2026-10-07`. A one-slice read writes a line on that slice's `spec.md` instead, one per repo and branch: `Synced at: orders-api develop@00344be, 2026-10-15`, and `Synced at: orders-api feat/orders-retry@155b5c4, 2026-10-19` on the next line. A new read replaces only its own line (1.84.0).

**Work branch.** A branch that holds part of a spec's work and still has to merge: named in the spec's `Synced at` lines, its Match `Branch:` list, or a task's `(branch: …)`, minus base branches and `(dropped)` entries. A spec is done across branches when every work branch is merged into its base. A branch may serve several specs; it is reported under each and counted once.

**Spec branch.** A spec's long-lived work branch, usually `feat/<slug>`, that its task sub-branches merge into before it merges into the base branch (setup 4). Marked `(spec branch)` on the Match `Branch:` list after a yes. Since 1.68.0.

**Sub-branch.** A short branch for one task, for example `feat/orders-capacity-t3`, that merges into the spec branch, not the base. It counts toward the `Sub-branches:` progress line only, never toward done; one that never merged once the spec branch reached the base is reported as `left behind`. Since 1.68.0.

**Into branch.** The branch a work branch merges into: its `(into <branch>)` marker on the Match `Branch:` list, else the repo's `Merges into` branch, else the default branch. It is the branch's fork point and its pull request base. The kit offers the marker with a yes/no question and writes it after a yes (1.68.0); a headless run writes nothing and treats the branch as stacked.

**Reverted.** A merged branch whose change was later undone on the base branch (a `This reverts commit` message or the reverse patch). Shown as `merged, reverted on <base> (<sha>)`; report only, it never blocks done. Since 1.68.0.

**Promotion.** How far merged work has got along a repo's environment chain (dev, test, prod), read from `docs/environments/promotion.md` and shown as the `Promotion:` status line. Report only; done stays merged into the base branch. Since 1.69.0. See [environments-promotion.md](../environments-promotion.md).

**Branch reach.** The Promotion test: the work is contained in a branch (or a matching release branch or tag) that a promotion.md line says deploys to an environment. It is not deployment proof; the wording is "on the branch that deploys to prod", never "deployed to prod". The optional `pipeline runs` check reads the latest successful Azure DevOps runs. Since 1.69.0.

**Base branch / Merges into.** Implementation code is never built on one (1.99.0): `main`, `master`, `develop`, the `Merges into` branch and `release/*` all count. The branch a repo's work merges into: the `Merges into` cell in `docs/system/repos.md` (for example `develop`), else the default branch. A base branch is never counted as a work branch.

**Fork point.** Where a branch split off: the closest of its repo's base branches (while the `Merges into` cell is empty, also `develop`, `development`, `dev` or `integration` when they exist) and the spec's other branches, by fewest own commits. A branch diff starts there, not at the default branch.

**Merge the base in.** How the kit says to bring a branch up to date with its base (the pull request's target, else the repo's `Merges into` branch, else the default branch): merge the base into the branch and resolve conflicts there. The kit never suggests a rebase or a force-push. Seeing that someone else rebased a branch is still reported (see Branch rewritten since last read) (1.66.0).

**Nothing-lost check.** `/crav1-finalize-commit` (1.81.0) checks a merge against both of its parents: every line either side added to a spec, a system file or a note must still be there, in the merge, in `HEAD` or in the working tree, so a dropped line restored in a later commit is not reported again (1.90.2). Line endings are ignored. A rebuilt note index and a `Synced at` line replaced by a newer one for the same branch do not count as lost. Since 1.123.0 the check is `scripts/nothing_lost.py` in that skill. Say nothing was lost only when it reports that. The pull merges with `--no-commit` and makes one merge commit. A notes index rebuild is folded into that commit.

**Merge-safe formats.** The 1.84.0 rules that keep two people's kit runs from conflicting: one `Synced at` line per repo and branch, one Match `Branch:` line per branch (1.86.0), open questions found by their words, and new `**New:**` lines, open questions and glossary rows put in **sorted place** (before the first existing one that sorts after them) instead of at the end. Projects made before 1.84.0 run `/crav1-add-to-spec migrate formats` once. See [Data layout](data-layout.md#merge-safe-formats-1840).

**Dropped.** A `(dropped)` at the end of a `Synced at` line: the branch is gone, was never merged, and was given up after a yes in `/crav1-tighten-spec`. A gone branch whose work is in the base counts as merged and is never offered dropped.

**Branch rewritten since last read.** What status says when a branch's recorded SHA no longer exists or is no longer in the branch (a rebase or force push). Commits are matched by content (`git patch-id`), so nothing is imported twice.

**Left out.** A guess from the code that stays out of the architecture spec, listed in `docs/architecture/left-out.md`.

**Work item.** An Azure Boards id in `docs/specs/<slug>/work-item.md`. Commit and pull request skills turn it into a mention.

**`T#`, `P#`, `I#`, `G#`, `Q#`, `A#`.** Numbered items: tasks in `tasks.md`, plan findings from review-plan, architecture issues from review-architecture, gaps from verify, open questions in a spec, and bulk assumptions in the landscape. `Q#` is a display number only, counted in document order and never written; the kit finds a question by its words (1.84.0).

**Inner loop.** A gap that can be fixed and re-proved in the working tree. Fix-build-gaps takes these one at a time.

**Worker, subagent.** An isolated helper a skill starts for one piece of work, such as one task or one intake slug. The five subagents are listed in the [skills reference](../reference/skills.md#subagents).

**Persist rule, commit-style rule.** A project rule the commit skills write when you choose a commit style onward. Delete it to choose again.

**Transfer data policy.** The once-per-repo rule for the personal-data check. See [Data policy](data-policy.md).

**Guild, guild bot.** A team of agents that routes kit work by lane, with a process orchestrator or guild lead that pauses a lane and hands questions to the researcher. See [guild routing](../guild-routing.md).
