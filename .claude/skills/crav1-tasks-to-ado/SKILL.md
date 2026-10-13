---
name: crav1-tasks-to-ado
description: >-
  Send the tasks of one spec to Azure Boards as child work items of that
  spec's Feature. Check az first. The child type is asked once and saved
  in docs/environments/marks.md. List every task, preview the form, then
  create or update only after the user says yes. Record the id in
  work-item.md. Later skill. Not a starter option.
disable-model-invocation: true
icon: list-checks
color: blue
---

# Tasks to Azure Boards

You turn the tasks of one spec into Azure Boards work items, each a child of that spec's Feature. The spec stays the source. A create or an update runs only after the user says yes, because it goes out in the user’s name.

Command: `/crav1-tasks-to-ado`.

This is cross-cutting. It is not a lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. The seven starter options stay unchanged.

Spark, specify, plan, and verify do not run it. It is not started automatically. `/crav1-specs-to-ado` may name it and does not run it.

CLI checks and the `az` calls: the same file `/crav1-specs-to-ado` uses, [azure-boards.md](../crav1-specs-to-ado/references/azure-boards.md) (drop-in: `.claude/skills/crav1-specs-to-ado/references/azure-boards.md`; plugin: sibling `skills/crav1-specs-to-ado/references/azure-boards.md`), plus [references/child-items.md](references/child-items.md) for the child type and the parent link. Do not show those commands in the chat.

## Check first

1. Take the Azure DevOps org and project as `azure-boards.md` says. `docs/environments/marks.md` first, then Azure DevOps URLs in `docs/system/repos.md`.
2. Check that `az` works, including the default install paths, the same way `/crav1-specs-to-ado` does.

On a failure, state the issue, suggest a fix such as `az login`, and offer Retry or Skip. Skip stops this command. Say the Azure Boards calls did not run, and why. Do not install. Do not log in. Do not run `az login`. Do not guess the org or the project.

## Which spec

The user picks one spec. List the specs whose `docs/specs/<slug>/work-item.md` records a Feature id (a `Work item: <id> — <label>` line that is not a task line). Skip `_template`. Use the questions tool when it is available and the list fits. Stop until they pick.

A spec with no Feature id is not offered. When the user names one, say it has no Feature in Azure Boards yet and name `/crav1-specs-to-ado`. Do not run it. When the spec records several Feature ids, ask which Feature these tasks belong to. Do not guess.

## Which tasks

Read that spec's `tasks.md`. List every task, numbered as the file numbers them (`T1`, `T2`, …), one line each: the number, the task's own short wording, and `Update #<id>` when `work-item.md` already records it. Every task stays listed. Do not drop one to keep the list short. A spec with no `tasks.md`, or with no tasks, says so and stops. Name `/crav1-plan-from-spec`. Do not run it.

The user picks by number, or all. Stop until they pick. Do not preview a task they did not pick.

## Child type

Read the child work item type from the line in `docs/environments/marks.md`:

```text
Azure Boards task type: <type>
```

When the line is there, use it. Do not ask. The user changes it by editing that line.

When the line is missing, read the project's work item types as [references/child-items.md](references/child-items.md) says, and ask once which type a task becomes. Options only: the returned types, with `Task` first when the project has it, then `Product Backlog Item` or `User Story` when present. Use the questions tool when it is available. Stop until they pick. Then append that line to `docs/environments/marks.md`. Create the file when it is missing. Do not rewrite other lines.

Then read that type's fields once, as `azure-boards.md` reads the Feature fields, to see whether it has Acceptance Criteria.

## Preview

For each pick, show the Azure Boards form in plain words. The label is **Create** when no id is recorded for that task, or **Update #<id>** when `work-item.md` records one. The layout follows the Feature layout from `/crav1-feature-candidates`.

| Form field | What to show |
| --- | --- |
| Type | The saved child type |
| Parent | The Feature id |
| Title | A fuller title that says what the work is: the area, then the task, for example `Email service: enable the day-ahead use case on dev` |
| State | New |
| Iteration | blank. The user’s team sets it |
| Priority | blank. The user’s team sets it |
| Tags | The slice name, then the code repos this task touches |
| Assigned To | The task owner when the spec, the task, or the plan states one. Otherwise blank |
| Description | Fuller context that stands alone: what the task does, why, who is involved, decisions with short quotes, names, and dates, and related items. Then **Open blockers/questions** as bullets with who and when where the docs say, or `none recorded` |
| Acceptance Criteria | The task's verify line in plain words. When the type has no Acceptance Criteria field, this row is not on the form and the line goes at the end of the Description |

Tags come from `docs/system/repos.md`: the code repos the task or the plan names for it, else the slice's repos. Never tag the repo that holds the specs.

Use only what the docs state. Do not invent an owner, a quote, a date, a decision, or a check. When the task has no verify line, Acceptance Criteria is blank and the preview says so.

### Example

Generic, for the shape only:

- **Title:** `Email service: enable the day-ahead use case on dev`
- **Tags:** `email-service; infra-email-service`
- **Assigned To:** `<task owner>`
- **Description:** The day-ahead use case only runs on test and prod today. In email-service the code limits it to those two environments, and the dev settings in infra-email-service have no configuration for it. This task enables it on dev so v0 runs on both dev and test. Decision: "v0 stays dev and test" (<name>, <date>). Related: the dev and test mailboxes are set up and tested (<name>, <date>, ticket <number>). Open blockers/questions: none recorded.
- **Acceptance Criteria:** A unit test shows a day-ahead message is routed to the day-ahead use case when the environment is dev.

### Strip before the preview

Remove file paths, line numbers, spec references such as `(spec: v0; Open questions 1)`, `docs/sources/` paths, and kit and skill names from every field. Code repo names stay in the text, for example "In email-service the code limits it…". Never mention the repo that holds the specs, and do not link to it. The preview is what will be sent, so it must already be stripped. A commit mention `AB#` in a code repo stays as it is and is not copied in.

### Update

An **Update** shows only the fields that differ from what `az boards work-item show` returns. Do not reset State, Iteration, Priority, or Assigned To when the docs do not state that field. Tags add what is missing and remove nothing. Do not change the parent link when it already points at the Feature. When it points elsewhere, say so and ask. Do not guess.

### Edits

Edits never happen in the preview. When the user wants different words, an owner, or a different check, that change goes into the spec or `tasks.md` first through `/crav1-add-to-spec`. Then rebuild the preview. Do not patch the form in the chat and send that patch.

## Send

Ask after the previews. Use the questions tool when it is available.

1. **Create** or **Update #<id>** for this one
2. **All reviewed**
3. **Skip this one**

Stop until they pick. Create or update only on a yes, as [references/child-items.md](references/child-items.md) says, with the parent link to the Feature. Do not show the command. A skip sends nothing for that task.

## Record

After a create, append one line to `docs/specs/<slug>/work-item.md`. This is a required final step of the run.

```text
Work item: <id> — task: T<n> <short title>
```

A re-run reads these lines and offers **Update #<id>** for that task. An update keeps the line. Never write an id into `tasks.md`. When the line is already there, leave it. If the write fails, say so and print the exact line to add.

## Report

Say what was created, what was updated, and what was skipped. One line each: the id, the title, and `T<n>`.

When the run wrote `work-item.md` or `docs/environments/marks.md`, name each file. Say it is not committed yet and must be committed. Name `/crav1-finalize-commit`. Do not run it. Say that without `work-item.md` a later run offers Create again and would make a duplicate.

Do not plan. Do not implement. Do not commit.
