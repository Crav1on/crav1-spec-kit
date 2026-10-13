---
name: crav1-ado-to-tasks
description: >-
  Read back the Azure Boards child work items that a spec's work-item.md
  records as task lines. Show only what differs from the spec and
  tasks.md, and new children of the Feature. Kept changes go in through
  /crav1-add-to-spec. Ticks a box or adds a task only after a yes. Never
  writes a field to Azure Boards. Later skill. Not a starter option.
disable-model-invocation: true
icon: cloud-download
color: blue
---

# Azure Boards to tasks

You read the task work items in Azure Boards and show what differs from the spec and its `tasks.md`. You write the spec and `tasks.md` only through `/crav1-add-to-spec`, and only for what the user kept. You post a comment only after the user says yes.

Command: `/crav1-ado-to-tasks`.

This is cross-cutting. It is not a lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. The seven starter options stay unchanged.

Spark, specify, plan, and verify do not run it. It is not started automatically. `/crav1-tasks-to-ado` may name it and does not run it.

This command reads Azure Boards. It does not create or update a work item. It never writes a field back. The only write to Azure Boards is a discussion comment the user accepted.

CLI checks and the `az` calls: [../crav1-specs-to-ado/references/azure-boards.md](../crav1-specs-to-ado/references/azure-boards.md) (drop-in: `.cursor/skills/crav1/crav1-specs-to-ado/references/azure-boards.md`; plugin: sibling `skills/crav1-specs-to-ado/references/azure-boards.md`) and [../crav1-tasks-to-ado/references/child-items.md](../crav1-tasks-to-ado/references/child-items.md) for the children of a Feature. Do not show those commands in the chat.

## Which spec

Everything after the command is the pointer. A named slug reads that spec. **All** reads every spec. With no pointer, list the specs whose `docs/specs/<slug>/work-item.md` has task lines (`Work item: <id> — task: T<n> <short title>`, see [work-item-mention.md](../crav1-draft-commit-message/references/work-item-mention.md)), plus **All**. Use the questions tool when it is available. Stop until the user picks. Skip `_template`.

A spec with no task lines has nothing to read back. Say so and name `/crav1-tasks-to-ado`. Do not run it.

## Read

Check `az`, the org, and the project the same way `/crav1-specs-to-ado` does. On a failure, state the issue, suggest a fix such as `az login`, and offer Retry or Skip. Skip stops this command. Say the Azure Boards calls did not run, and why.

Read the child type's fields once, as `/crav1-tasks-to-ado` does, to know where acceptance lives.

For every recorded task id, read State, title, description, Acceptance Criteria (or the `Acceptance` paragraph in the Description when the type has no such field), Assigned To, discussion comments, and history. Strip HTML before comparing. Do not drop an id to keep the list short.

Then read the children of the spec's Feature in each home (each Feature line in `work-item.md`). A child whose id has no task line is **new**.

Read each id in its own home: the `(ADO: <org>/<project>)` tag on its line, or for an older line without one the marks.md org and project, as [work-item-homes.md](../crav1-specs-to-ado/references/work-item-homes.md) (drop-in: `.cursor/skills/crav1/crav1-specs-to-ado/references/work-item-homes.md`; plugin: sibling `skills/crav1-specs-to-ado/references/work-item-homes.md`) says. An id not found in its home is reported as **moved or missing**, with that home. Ask before searching the other projects `az` can read; never search on your own. A deleted id is reported as missing. Do not guess another work item. Do not match on the title.

## What to show

One block per task, `T<n>` and its id. Only what differs from the spec and `tasks.md`, or is new. A field that matches is left out. A comment the spec already quotes is left out. Each difference names the date and who changed it when the history or the comment shows them. When it shows no person, say the name is not in the history. Do not invent a person or a date.

When nothing differs, say that task matches.

Then one block **New under the Feature**: each new child with its id, type, title, State, and Assigned To.

## Keep or dismiss

The user takes each difference one at a time: keep or dismiss. Use the questions tool when it is available. One question per difference. Dismiss is for this run only. The next run starts fresh. Do not write a dismissals file.

A kept change goes to the spec and `tasks.md` through `/crav1-add-to-spec`. The quote starts with `From ADO <date>. <who>.` when the history shows them, else `From ADO <date>.` The impact check in that skill still runs.

**State.** Compare the State with the `tasks.md` box, using the done state saved for the task's home in `docs/environments/marks.md` (`Azure Boards task done state (<project>): <state>`, or the older line without a project; when the line is missing, Closed, Done, or Resolved count as done).

- Done in Azure Boards and the box is open: show who closed it and when from the history, and ask once for that task: tick the box, or leave it. Tick only on yes, through `/crav1-add-to-spec`.
- Reopened in Azure Boards (not done now, done before in the history) and the box is ticked: show both sides and ask: untick the box, or leave it. Untick only on yes, through `/crav1-add-to-spec`.
- Active, Resolved, or another in-progress state with an open box is not a difference. Leave it out.

Do not tick or untick a box on your own. Never write a State back to Azure Boards. That is `/crav1-tasks-to-ado`, and only on a yes.

**New children.** For each new child, ask: add it as a task, or leave it. On yes, `/crav1-add-to-spec` adds the task to `tasks.md` with the next `T<n>`, in words from the work item, stripped as below. Then append its line to `work-item.md`: `Work item: <id> — task: T<n> <short title> (ADO: <org>/<project>)`, with the home it was read from. Never write an id into `tasks.md`.

## Reply comment

When a task's discussion asks a question and the spec already answers it, draft a reply from that answer:

```text
Post comment on <id>: <text>
```

Strip it the same way `/crav1-tasks-to-ado` strips: no file paths, no line numbers, no spec references, no `docs/sources/` paths, no kit or skill names, never the specs repo. Code repo names stay. The user can change the text, post it, or skip it. A change that adds a fact goes into the spec first, through `/crav1-add-to-spec`. Post only on yes. When the spec has no answer, offer the question as an open question for the spec instead.

## Stop

Report what was kept, ticked, added, posted, and dismissed. When a file changed, name it, say it is not committed yet, and name `/crav1-finalize-commit`. Do not run it. Do not plan. Do not implement. Do not commit. Do not create or update a work item.
