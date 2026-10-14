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
| SQL | Structured Query Language | Environment-read looks at SQL metadata only, never rows |
| SAS | Shared access signature | A storage token. Always treated as a secret |
| API | Application programming interface | |
| VPN | Virtual private network | |

## Words

**Starter option.** One of the seven ways in: spark-to-spec, ideas-to-spec, intake-to-specs, match-to-specs, repos-to-spec, environment-read, fix-bug. Asking for startup options lists them and does not run one.

**Later skill.** Any skill that is not a starter option. Most run once specs already exist.

**Lane.** One of the groupings of skills: Starters, Specify, Plan, Build, and Cross-cutting. Inside each lane, skills sit in groups by phase. The [skills reference](../reference/skills.md) is organized this way, and [guild routing](../guild-routing.md) maps each skill to a lane.

**Cross-cutting.** A skill that may run from any lane and does not move work into a lane.

**Spark.** One or two sentences about what to build. Input to `/crav1-spark-to-spec`.

**Dump.** A pile of notes, tickets, old docs, diagrams, or screenshots to sort onto specs.

**Intake.** One or more files that may describe a whole system with several v0 features.

**Ready (task).** A task that can be built now: `plan.md` exists, no open question or plan Risk blocks it, the tasks it waits on are ticked, and it is not ticked itself. A ticked task that `verify.md` does not list as verified is **needs verify**, not done. `/crav1-tasks-ready-to-build` lists them. See [Readiness marks](data-layout.md#readiness-marks).

**Blocking.** What keeps a task from being ready, with one reason: a kept-open question (its `Blocks:` line names the task, or it has none and blocks the whole slice), a plan Risk, or an earlier task that is not ticked (from `(after: T#)`, or task order when none is recorded). A reason from a written mark is **recorded**; a fallback is **inferred**.

**Route.** An ordered list of commands for one situation, such as a new slice or new information on an existing slice. Each step says when it applies, and some are optional. The routes live in `docs/reference/workflow.yaml` and are shown in [Workflow routes](../reference/workflow.md). `/crav1-help` answers order questions from them.

**Slice, slug.** A slice is one feature's spec folder. Its slug is the folder name under `docs/specs/`.

**v0.** The first version of a feature. Intake writes one spec per confirmed v0 feature.

**Landscape, picture.** The system notes in `docs/system/`: the short description, the diagram, how the parts connect, and the feature index. Keep-current keeps the picture up to date.

**Feature index.** The table in `docs/system/landscape.md` with one row per slice and its status.

**Glossary rows.** The words a source already uses, in `docs/system/glossary.md`. New rows are appended. Existing rows are not rewritten. A meaning the source does not state is `to be researched`.

**Match status.** Under a spec's `## Match`: done, partial, not in the code, or retired.

**Note.** A fact kept for later in `docs/notes/`, not tied to a spec yet. `Used by` and `Absorbed by` record which specs took it.

**Imported source.** The original of a mail, transcript, minutes, chat, screenshot, or diagram, kept in `docs/sources/` so a quote can be checked. See [Data policy](data-policy.md).

**Research note, stale mark, point.** A research note lives in `docs/research/`. When a later quote changes what it says, the note gets a `Stale since` mark after a yes, and each spec that relies on it gets one `Point:` line per hit.

**Open question marks.** `Pending:`, `Asked:`, `Answered:`, and `Blocks:` lines under a spec's open question. See [Data layout](data-layout.md#open-question-marks).

**Environment marks.** Confirmed lines in `docs/environments/marks.md` saying which environment a cloud resource belongs to. See [Environment marks](../environments-marks.md).

**Production (prod).** The live environment. The kit never reads production data. Pre-prod, resources shared with prod, and prod-only resources are read for shape and connections only, after one yes.

**Work item home.** Where the work items for one implementation repo go, written as `ADO: <org>/<project>` in the `Work items go to` column of `docs/system/repos.md`. The first Azure Boards skill that needs a repo's home asks for it once, suggesting the repo's own project, and never guesses it. A spec whose repos are in several homes gets one Feature in each home. `Jira: <project>` is reserved for later and is not read yet. See [Data layout](data-layout.md#work-item-homes).

**Synced at.** The branch, short commit, and date a repo was last read, as `<branch>@<short sha>, <date>`, in `docs/system/repos.md`. A one-slice read writes a `Synced at` line on that slice instead.

**Left out.** A guess from the code that stays out of the architecture spec, listed in `docs/architecture/left-out.md`.

**Work item.** An Azure Boards id in `docs/specs/<slug>/work-item.md`. Commit and pull request skills turn it into a mention.

**`T#`, `P#`, `I#`, `G#`, `Q#`, `A#`.** Numbered items: tasks in `tasks.md`, plan findings from review-plan, architecture issues from architecture-reviewer, gaps from verify, open questions in a spec, and bulk assumptions in the landscape.

**Inner loop.** A gap that can be fixed and re-proved in the working tree. Fix-from-verify takes these one at a time.

**Worker, subagent.** An isolated helper a skill starts for one piece of work, such as one task or one intake slug. The five subagents are listed in the [skills reference](../reference/skills.md#subagents).

**Persist rule, commit-style rule.** A project rule the commit skills write when you choose a commit style onward. Delete it to choose again.

**Transfer data policy.** The once-per-repo rule for the personal-data check. See [Data policy](data-policy.md).

**Guild, guild bot.** A team of agents that routes kit work by lane, with a process orchestrator or guild lead that pauses a lane and hands questions to the researcher. See [guild routing](../guild-routing.md).
