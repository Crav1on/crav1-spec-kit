---
name: crav1-specs-to-ado
description: >-
  Turn picked feature candidates into Azure Boards Features. Check az and
  the Feature type first. Preview the form, then create or update only
  after the user says yes. Record the id on the spec or on the landscape
  table. Later skill. Not a starter option.
disable-model-invocation: true
icon: cloud-upload
color: blue
---

# Specs to Azure Boards

You turn picked candidates into Azure Boards Features. The spec stays the source. A create or an update runs only after the user says yes, because it goes out in the user’s name.

Command: `/crav1-specs-to-ado`.

This is cross-cutting. It is not a lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. The seven starter options stay unchanged.

Spark, specify, plan, and verify do not run it. It is not started automatically.

CLI checks and the `az` calls: [references/azure-boards.md](references/azure-boards.md) (drop-in: `.cursor/skills/crav1/crav1-specs-to-ado/references/azure-boards.md`; plugin: this skill’s `references/azure-boards.md`). Do not show those commands in the chat.

## Check first

Before the candidate list:

1. Take the Azure DevOps org and project as [references/azure-boards.md](references/azure-boards.md) says. `docs/environments/marks.md` first, then Azure DevOps URLs in `docs/system/repos.md`.
2. Check that `az` works, including the default install paths, the same way `/crav1-whats-known-about` does.
3. Check that the project has the Feature work item type. If it does not, say so and stop. Do not create another type.

On a failure, state the issue, suggest a fix such as `az login`, and offer Retry or Skip. Skip stops this command. Say the Azure Boards calls did not run, and why. Do not install. Do not log in. Do not run `az login`.

Do not ask for a typed path. Do not guess the org or the project.

## Candidates

Run `/crav1-feature-candidates` and show that list. The rules in that skill are the rules for the rows (drop-in: `.cursor/skills/crav1/crav1-feature-candidates/SKILL.md`; plugin: sibling `skills/crav1-feature-candidates/SKILL.md`).

The user picks one or more by number, or all. Every row stays listed. Do not drop one to keep the list short. Use the questions tool when it is available and the list fits. Otherwise the numbered table is the choice, and the reply is the numbers or all.

Stop until they pick. Do not preview a row they did not pick.

## Preview

After the user picks, and before any form, read the project’s Feature fields once. Follow [references/azure-boards.md](references/azure-boards.md). When the type has Acceptance Criteria (`Microsoft.VSTS.Common.AcceptanceCriteria`), the checks go there. When it does not, the checks go in the Description. A failed field read is the same failure as the other `az` checks. State the issue, suggest a fix, and offer Retry or Skip. Do not guess. Do not preview until the read succeeds.

For each pick, show the Azure Boards form in plain words. The label on the form is **Create** when no id is recorded, or **Update #<id>** when `work-item.md` or the landscape table already records one.

| Form field | What to show |
| --- | --- |
| Title | The candidate title |
| State | New |
| Area | default |
| Value area | Business |
| Iteration | blank. The user’s team sets it |
| Priority | blank. The user’s team sets it |
| Target Date | The date the spec states, or blank |
| Tags | The slice name, then the code repos that slice involves |
| Description | Goals, status, and open questions, in two to four sentences that stand alone. When the type has no Acceptance Criteria field and the spec has checks, the Acceptance checks list follows those sentences |
| Acceptance Criteria | The spec’s checks when the type has that field, or blank. When the type does not have the field, this row is not on the form |

Tags come from `docs/system/repos.md`: the repos that slice involves (the feature-index Repos cell, or a repo the spec or the plan names). Never tag the repo that holds the specs. A docs repo and a spec repo stay off the tag list.

The checks are the acceptance checks in that `spec.md` and nothing else. Do not invent a check. Do not copy a task. When the spec has no checks, Acceptance Criteria is blank when the type has that field, and the Description has no Acceptance checks list when it does not. A questions-only candidate has blank acceptance and its questions in the description.

When the type has no Acceptance Criteria field and the spec has checks, the preview adds one plain line: this project’s Feature has no Acceptance Criteria field, so the checks are in the Description.

An **Update** also shows what would change. Compare the form with the work item `az boards work-item show` returns. Show only fields that differ. Do not reset State, Area, Iteration, Priority, or Assigned To when the spec does not state that field. Do not clear a target date the spec does not state. Tags to add are the slice name and the code repos that are missing. Do not remove a tag the form does not list.

The same field rule applies on an update. When the type has no Acceptance Criteria field, do not send that field. Put the checks in the Description. A re-run moves checks that were stored off the form into the Description. When the Description list already matches the spec’s checks, that is not a change.

### Nothing from the specs repo

Anything that would be sent — title, description, acceptance, tags, comment — must not mention the repo that holds the specs. No spec path, no link to that repo, no kit name, no skill name. Say the goal in the words the spec uses, without pointing at the file.

A commit mention `AB#` that already exists in a code repo stays as it is. Do not rewrite those commits. Do not put that mention into the Feature description.

The target date on the form is the date alone. The chat can still say which heading stated it. That heading is not copied into the Feature.

### Edits

Edits never happen in the preview. The spec is the source. When the user wants different words, a different date, or a different check, that change goes into the spec first through `/crav1-add-to-spec`. Then rebuild the preview from the spec. Do not patch the form in the chat and send that patch.

A `no spec yet` row has no spec to edit. Say so. Name `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, or `/crav1-intake-to-specs` and do not run it. Do not send a rewritten preview.

## Send

Ask after the previews. One at a time, or all of the reviewed picks together. Use the questions tool when it is available.

1. **Create** or **Update #<id>** for this one
2. **All reviewed**
3. **Skip this one**

Stop until they pick. Run `az boards work-item create` or `az boards work-item update` with `--type Feature` only on a yes. Follow [references/azure-boards.md](references/azure-boards.md). Do not show the command.

A skip sends nothing for that row. The spec stays as it is.

## Record

After a create, write the new id. This write is a required final step of the run. It is not optional.

**A spec.** Append one line to `docs/specs/<slug>/work-item.md`:

```text
Work item: 52 — <milestone or slice label>
```

The label is the milestone or slice name. An undated spec uses the spec title. The line format is [work-item-mention.md](../crav1-draft-commit-message/references/work-item-mention.md). Create the file when it is missing. Do not copy `docs/specs/_template/work-item.md`. Do not add the HTML comment. Do not put the id in `tasks.md`. When that id and label are already on a line, leave the line.

**No spec yet.** Append a row to `## No spec yet in ADO` in `docs/system/landscape.md`. Columns: Id, Title, Date. Create the heading and the table when they are missing. Do not rewrite other landscape sections. Do not rewrite an existing row. A row whose cells are all empty is the template placeholder. Replace that placeholder with the first real row. Do not treat the placeholder as a Feature. The Date cell is the target date the docs stated. When they stated none, the date is the day the row is written, and the report says it is the day the row was written, not a target date.

When a spec later covers a row in that table, move the id. An exact title match moves it: append the `work-item.md` line on that spec, then remove the landscape row. Leave the heading. When more than one spec could fit, ask. Do not guess. When none fits, leave the row.

An update does not mint a new id. It keeps the recorded line.

If the write fails, say so. Print the exact line to add. For a spec, that line is `Work item: <id> — <label>`. For no spec yet, print the table row: id, title, and date.

## Report

Say what was created and what was updated. One line each: the id, the title, and the spec slug or `no spec yet`. Say what was skipped.

When a create wrote a file, name that file. Say it is not committed yet and must be committed. Name `/crav1-finalize-commit`. Do not run it. Say that without that file a later run offers Create again and would make a duplicate.

Name `/crav1-ado-to-specs` as the later read-back. Do not run it.

Do not plan. Do not implement. Do not commit.
