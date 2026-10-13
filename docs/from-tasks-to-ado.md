# From tasks to Azure Boards

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when a spec already has its Feature in Azure Boards and the user wants that spec's tasks there too, as child work items of the Feature.

This is cross-cutting. It is not its own lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

It is a later skill. It is not a starter option. When the user asks for startup options, that ask names only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. It does not run this command. The seven starter options stay unchanged.

The Feature comes first, from [From specs to Azure Boards](from-specs-to-ado.md). The tasks come from the spec's `tasks.md`, written by [From a spec to a plan](from-spec-to-plan.md).

## First prompt

New chat.

```text
/crav1-tasks-to-ado
```

That slash command *is* the prompt.

## Steps

### Check first

The org and the project come from `docs/environments/marks.md`, or from the Azure DevOps URLs in `docs/system/repos.md`, the same way as `/crav1-specs-to-ado`. The command checks that `az` works, including the default install paths. If `az` fails, it states the issue, suggests a fix such as `az login`, and offers a skip. It does not install `az` and it does not log in.

### Work item homes

Each task goes to the home of its repo, from the **Work items go to** column in `docs/system/repos.md` (asked once per repo the first time, see [From specs to Azure Boards](from-specs-to-ado.md#work-item-homes)). A task with no clear repo is asked once, suggesting the spec's main repo. A task touching repos in different homes is asked: split it, or pick one. Its parent is the spec's Feature in that same home.

### Pick a spec, then tasks

The user picks one spec. Only specs whose `work-item.md` already records a Feature id are offered. A spec without one points at `/crav1-specs-to-ado`.

Every task in that spec's `tasks.md` is listed, numbered `T1`, `T2`, …, with `Update #<id>` next to a task that was sent before. The user picks by number, or all.

### Child type, once

On the first run the command reads the project's work item types and asks once which type a task becomes. It reads the project's process and backlog levels and marks the type directly under Feature as `(Recommended)` with one reason: User Story on Agile (a Task belongs under a User Story), Product Backlog Item on Scrum, Issue on Basic, Requirement on CMMI. Bug is recommended only when the team tracks bugs as requirements. When the levels cannot be read, it says so and gives no recommendation. It also reads that type's states and saves the done state, the one Azure Boards counts as completed (Closed on Agile, Done on Scrum and Basic). Both are saved as lines in `docs/environments/marks.md`:

```text
Azure Boards task type (bc-operations): User Story
Azure Boards task done state (bc-operations): Closed
```

The lines are kept per home. A line without `(<project>)` counts for the project in `docs/environments/marks.md`.

Later runs use those lines without asking. To change one, edit the line.

### Preview, then send

Each pick is shown as a form labelled **Create** or **Update #<id>**, as a child of the Feature. An update shows only the fields that changed.

| Field | What goes in |
| --- | --- |
| Title | A fuller title that says what the work is |
| State | New for an open box, the done state for a ticked box |
| Iteration, Priority | blank. The team sets them |
| Tags | The slice name, then the code repos the task touches. Never the specs repo |
| Assigned To | The task owner, when the docs state one |
| Description | What the task does, why, who is involved, decisions with quotes, names, and dates, related items, then open blockers or questions as bullets, or `none recorded` |
| Acceptance Criteria | The task's verify line in plain words. In the Description when the type has no such field |

Before the preview, file paths, line numbers, spec references such as `(spec: v0; Open questions 1)`, `docs/sources/` paths, and kit and skill names are stripped. Code repo names stay in the text. Nothing mentions the repo that holds the specs.

Example, for T1 of an email service spec:

- **Title:** Email service: enable the day-ahead use case on dev
- **Tags:** email-service; infra-email-service
- **Assigned To:** the task owner
- **Description:** The day-ahead use case only runs on test and prod today. In email-service the code limits it to those two environments, and the dev settings in infra-email-service have no configuration for it. This task enables it on dev so v0 runs on both dev and test. Decision: "v0 stays dev and test" (name, date). Related: the dev and test mailboxes are set up and tested (name, date, ticket number). Open blockers/questions: none recorded.
- **Acceptance Criteria:** A unit test shows a day-ahead message is routed to the day-ahead use case when the environment is dev.

The preview is not edited in place. A change goes into the spec or `tasks.md` first through `/crav1-add-to-spec`, and the preview is rebuilt.

### State

The kit sets only New and the done state. It never sets Active or Resolved; people do that in Azure Boards. It never sends Reason, so Azure Boards fills its default (Completed when an item closes on Agile).

- **Create:** an open box goes in as New, a ticked box as the done state.
- **Ticked since it was sent:** the preview offers moving the item to the done state.
- **Unticked, and the item is closed:** the preview offers to reopen it to New.
- **Disagreement the local history does not explain**, for example closed in Azure Boards while the box was never ticked: the preview shows both sides, with who changed what and when, and asks each time. Neither side wins on its own.

Each state change is its own line and its own yes. Without that yes the State stays as it is.

The user answers per task: **Create** or **Update #<id>**, **All reviewed**, or **Skip this one**. Nothing is sent without that yes, because it goes out in the user's name. The `az` command is not shown.

## What gets written

After a Create, one line per task is appended to that spec's `work-item.md`:

```text
Work item: 1234 — task: T1 Enable the day-ahead use case on dev (ADO: contoso/bc-operations)
```

A later run sees the line and offers **Update #1234**. Ids never go into `tasks.md`. On the first run the child type line is also appended to `docs/environments/marks.md`. The command reports what was created, updated, and skipped, names the files it wrote, and says they are not committed yet. Without `work-item.md` a later run offers Create again and would make a duplicate. It does not commit.

## After

Commit the files that hold the new ids:

```text
/crav1-finalize-commit
```

Reading the task items back onto the spec and `tasks.md` is [From Azure Boards to tasks](from-ado-to-tasks.md).

Reading a Feature back onto the specs is [From Azure Boards to specs](from-ado-to-specs.md).

Reference page: [tasks-to-ado](reference/skills/crav1-tasks-to-ado.md)
