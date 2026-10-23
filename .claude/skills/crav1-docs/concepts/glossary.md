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

**Comment as posted.** The review comment as the reviewers see it, saved word for word in the review-pr follow-ups note next to the comment as drafted. `/crav1-review-pr` finds it on the pull request or takes a paste, compares it with the draft, and marks drafted points left out as `Not in the posted comment`, still open. A re-review compares against it (1.67.0).

**Cross-cutting.** A skill that may run from any lane and does not move work into a lane.

**Spark.** One or two sentences about what to build. Input to `/crav1-spark-to-spec`.

**Dump.** A pile of notes, tickets, old docs, diagrams, or screenshots to sort onto specs.

**Intake.** One or more files that may describe a whole system with several v0 features.

**Ready (task).** A task that can be built now: `plan.md` exists, no open question or plan Risk blocks it, the tasks it waits on are ticked, and it is not ticked itself. A ticked task that `verify.md` does not list as verified is **needs verify**, not done. `/crav1-tasks-ready-to-build` lists them. See [Readiness marks](data-layout.md#readiness-marks).

**Blocking.** What keeps a task from being ready, with one reason: a kept-open question (its `Blocks:` line names the task, or it has none and blocks the whole slice), a plan Risk, or an earlier task that is not ticked (from `(after: T#)`, or task order when none is recorded). A reason from a written mark is **recorded**; a fallback is **inferred**.

**Route.** An ordered list of commands for one situation, such as a new slice or new information on an existing slice. Each step says when it applies, and some are optional. The routes live in `docs/reference/workflow.yaml` and are shown in [Workflow routes](../reference/workflow.md). `/crav1-help` answers order questions from them.

**Slice, slug.** A slice is one feature's spec folder. Its slug is the folder name under `docs/specs/`.

**v0.** The first version of a feature. Intake writes one spec per confirmed v0 feature.

**Landscape, picture.** The system notes in `docs/system/`: the short description, the diagram, how the parts connect, and the feature index. Refresh-system-notes keeps the picture up to date.

**Feature index.** The table in `docs/system/landscape.md` with one row per slice and its status.

**Glossary rows.** The words a source already uses, in `docs/system/glossary.md`. New rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`.

**Match status.** Under a spec's `## Match`: done, partial, not in the code, or retired.

**Note.** One full input (fact plus passage, dump, code change, meeting) and its source in `docs/notes/YYYY-MM/`, filed by source date (1.61.0). Specs link it as `Full source:`; `used_by` records which specs took points. Never absorbed. Older notes may still say `Absorbed by`.

**PR note.** One note per pull request in the specs repo's `docs/notes/YYYY-MM/`, filed by the pull request's created date, `kind: pull request`, holding its title and description (a changed description is appended as a dated section). Written by `/crav1-review-pr`, `/crav1-merge-pr`, and the code-change branch of `/crav1-add-to-spec` (1.65.0).

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

**Open question marks.** `Pending:`, `Asked:`, `Answered:`, and `Blocks:` lines under a spec's open question. See [Data layout](data-layout.md#open-question-marks).

**Environment marks.** Confirmed lines in `docs/environments/marks.md` saying which environment a cloud resource belongs to. See [Environment marks](../environments-marks.md).

**Production (prod).** The live environment. The kit never reads production data. Pre-prod, resources shared with prod, and prod-only resources are read for shape and connections only, after one yes.

**Work item home.** Where the work items for one implementation repo go, written as `ADO: <org>/<project>` in the `Work items go to` column of `docs/system/repos.md`. The first Azure Boards skill that needs a repo's home asks for it once, suggesting the repo's own project, and never guesses it. A spec whose repos are in several homes gets one Feature in each home. `Jira: <project>` is reserved for later and is not read yet. See [Data layout](data-layout.md#work-item-homes).

**Synced at.** The branch, short commit, and date a repo was last read, as `<branch>@<short sha>, <date>`, in `docs/system/repos.md`. A one-slice read writes a `Synced at` line on that slice instead. Since 1.64.0 that line holds one entry per branch read, `; `-separated, and a new read replaces only that branch's entry: `Synced at: orders-api feat/orders-retry@155b5c4, 2026-10-19; develop@00344be, 2026-10-15`.

**Work branch.** A branch that holds part of a spec's work and still has to merge: named in the spec's `Synced at` entries, its Match `Branch:` list, or a task's `(branch: …)`, minus base branches and `(dropped)` entries. A spec is done across branches when every work branch is merged into its base. A branch may serve several specs; it is reported under each and counted once.

**Spec branch.** A spec's long-lived work branch, usually `feat/<slug>`, that its task sub-branches merge into before it merges into the base branch (setup 4). Marked `(spec branch)` on the Match `Branch:` list after a yes. Since 1.68.0.

**Sub-branch.** A short branch for one task, for example `feat/orders-capacity-t3`, that merges into the spec branch, not the base. It counts toward the `Sub-branches:` progress line only, never toward done; one that never merged once the spec branch reached the base is reported as `left behind`. Since 1.68.0.

**Into branch.** The branch a work branch merges into: its `(into <branch>)` marker on the Match `Branch:` list, else the repo's `Merges into` branch, else the default branch. It is the branch's fork point and its pull request base. The kit offers the marker with a yes/no question and writes it after a yes (1.68.0); a headless run writes nothing and treats the branch as stacked.

**Reverted.** A merged branch whose change was later undone on the base branch (a `This reverts commit` message or the reverse patch). Shown as `merged, reverted on <base> (<sha>)`; report only, it never blocks done. Since 1.68.0.

**Promotion.** How far merged work has got along a repo's environment chain (dev, test, prod), read from `docs/environments/promotion.md` and shown as the `Promotion:` status line. Report only; done stays merged into the base branch. Since 1.69.0. See [environments-promotion.md](../environments-promotion.md).

**Branch reach.** The Promotion test: the work is contained in a branch (or a matching release branch or tag) that a promotion.md line says deploys to an environment. It is not deployment proof; the wording is "on the branch that deploys to prod", never "deployed to prod". The optional `pipeline runs` check reads the latest successful Azure DevOps runs. Since 1.69.0.

**Base branch / Merges into.** The branch a repo's work merges into: the `Merges into` cell in `docs/system/repos.md` (for example `develop`), else the default branch. A base branch is never counted as a work branch.

**Fork point.** Where a branch split off: the closest of its repo's base branches (while the `Merges into` cell is empty, also `develop`, `development`, `dev` or `integration` when they exist) and the spec's other branches, by fewest own commits. A branch diff starts there, not at the default branch.

**Merge the base in.** How the kit says to bring a branch up to date with its base (the pull request's target, else the repo's `Merges into` branch, else the default branch): merge the base into the branch and resolve conflicts there. The kit never suggests a rebase or a force-push. Seeing that someone else rebased a branch is still reported (see Branch rewritten since last read) (1.66.0).

**Nothing-lost check.** `/crav1-finalize-commit` (1.81.0) checks a merge against both of its parents: every line either side added to a spec, a system file or a note must still be there. Line endings are ignored. A rebuilt note index and a `Synced at` entry replaced by a newer one for the same branch do not count as lost. The pull path runs the check before it commits the merge; an unpushed merge made outside the kit is checked after a commit or on `pull`.

**Dropped.** A `(dropped)` at the end of a `Synced at` entry: the branch is gone, was never merged, and was given up after a yes in `/crav1-tighten-spec`. A gone branch whose work is in the base counts as merged and is never offered dropped.

**Branch rewritten since last read.** What status says when a branch's recorded SHA no longer exists or is no longer in the branch (a rebase or force push). Commits are matched by content (`git patch-id`), so nothing is imported twice.

**Left out.** A guess from the code that stays out of the architecture spec, listed in `docs/architecture/left-out.md`.

**Work item.** An Azure Boards id in `docs/specs/<slug>/work-item.md`. Commit and pull request skills turn it into a mention.

**`T#`, `P#`, `I#`, `G#`, `Q#`, `A#`.** Numbered items: tasks in `tasks.md`, plan findings from review-plan, architecture issues from review-architecture, gaps from verify, open questions in a spec, and bulk assumptions in the landscape.

**Inner loop.** A gap that can be fixed and re-proved in the working tree. Fix-build-gaps takes these one at a time.

**Worker, subagent.** An isolated helper a skill starts for one piece of work, such as one task or one intake slug. The five subagents are listed in the [skills reference](../reference/skills.md#subagents).

**Persist rule, commit-style rule.** A project rule the commit skills write when you choose a commit style onward. Delete it to choose again.

**Transfer data policy.** The once-per-repo rule for the personal-data check. See [Data policy](data-policy.md).

**Guild, guild bot.** A team of agents that routes kit work by lane, with a process orchestrator or guild lead that pauses a lane and hands questions to the researcher. See [guild routing](../guild-routing.md).
