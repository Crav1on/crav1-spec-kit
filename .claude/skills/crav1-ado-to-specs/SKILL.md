---
name: crav1-ado-to-specs
description: >-
  Read Azure Boards Features that the specs already record. Show only what
  differs or is new. Kept changes go to the spec through /crav1-add-to-spec.
  A reply comment is posted only after the user says yes. Later skill.
  Not a starter option.
disable-model-invocation: true
icon: cloud-download
color: blue
---

# Azure Boards to specs

You read Azure Boards and show what differs from the specs. You write the spec only by handing a kept change to `/crav1-add-to-spec`. You post a comment only after the user says yes.

Command: `/crav1-ado-to-specs`.

This is cross-cutting. It is not a lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. The seven starter options stay unchanged.

Spark, specify, plan, and verify do not run it. It is not started automatically.

This command reads Azure Boards. It does not create a Feature. It does not update a Feature field. The only write to Azure Boards is a discussion comment the user accepted.

CLI checks and the `az` calls: [../crav1-specs-to-ado/references/azure-boards.md](../crav1-specs-to-ado/references/azure-boards.md) (drop-in: `.claude/skills/crav1-specs-to-ado/references/azure-boards.md`; plugin: sibling `skills/crav1-specs-to-ado/references/azure-boards.md`). Do not show those commands in the chat.

## Which ids

Everything after the command is the pointer.

When the user names ids, read those ids only.

When they name none, collect every id recorded in:

- each `docs/specs/<slug>/work-item.md` except `_template` (every line [work-item-mention.md](../crav1-draft-commit-message/references/work-item-mention.md) accepts)
- the `## No spec yet in ADO` table in `docs/system/landscape.md`

Skip a file that has no usable line. Do not drop an id to keep the list short. When the set is empty, say so and stop. Do not search Azure Boards for a title.

## Read

Check `az`, the org, and the project the same way `/crav1-specs-to-ado` does. On a failure, state the issue, suggest a fix such as `az login`, and offer Retry or Skip. Skip stops this command. Say the Azure Boards calls did not run, and why.

For each id, read State, Priority, Target Date, Iteration, and Assigned To with `az boards work-item show`. Read discussion comments and history with `az devops invoke --area wit --resource comments` and `--resource updates`. Follow the reference.

A deleted or missing id is reported as missing. Do not guess another work item. Do not match on the title.

## What to show

One block per Feature. The block holds only what differs from the spec or is new.

Compare State, Priority, Target Date, Iteration, Assigned To, title, description, acceptance criteria, tags, comments, and history with the spec that records the id (the `work-item.md` label picks the milestone or slice). A field the spec does not mention is new. A field that matches is left out. A comment that the spec already quotes is left out.

Each difference names the date and who changed it when the history or the comment shows them. When the history shows no person, say the name is not in the history. Do not invent a person or a date.

When nothing differs, say that Feature matches the spec.

A `no spec yet` id has no spec to compare. The block is what Azure Boards holds: title, State, Priority, Target Date, Iteration, Assigned To, and the discussion. Then suggest making the spec first, for example `/crav1-spark-to-spec`, from what was written on the Feature. Also name `/crav1-ideas-to-spec` or `/crav1-intake-to-specs` when the Feature text is a pile or several features. Do not run them. Do not create a slug.

## Keep or dismiss

The user takes each difference one at a time: keep or dismiss. Use the questions tool when it is available. One question per difference. Do not drop one to keep the list short.

Dismiss is for this run only. The next run starts fresh. Do not write a dismissals file.

A kept change goes to that spec through `/crav1-add-to-spec`. The quote starts with `From ADO <date>. <who>.` when the history shows a date and a person. When a person is missing, `From ADO <date>.` The quote is the field and the new value. Do not replace it with a paraphrase. The impact check in that skill still runs.

A kept change on a `no spec yet` Feature does not go to a spec. The suggestion to make the spec stays. Do not write `spec.md` here.

## Answers

An answer the user gives during the run goes into the spec first through `/crav1-add-to-spec`, before any comment is posted. The quote starts with `From the user <date>. Answer to the ADO question.` The date is the date of this run. Do not invent a different date. The quote is their words.

A `no spec yet` Feature has no spec for that answer. Say so. Name the starter that would make the spec. Do not run it. Do not post a comment that states a new fact the spec does not hold.

## Reply comment

When the Feature discussion asks a question and the spec already answers it, draft a reply from that answer. The draft has no spec path, no link to the specs repo, no kit name, and no skill name.

Show it as one line:

```text
Post comment on Feature <id>: <text>
```

The user can change the text, post it, or skip it. Use the questions tool when it is available. A change to the text that adds a fact still goes into the spec first, through `/crav1-add-to-spec`, before the post.

Post only on yes. Follow the comment call in the Azure Boards reference. Do not show the command.

When the spec has no answer, draft no reply. Offer the question as an open question for the spec. Keep sends it through `/crav1-add-to-spec` under Open questions, with the same `From ADO` label. Dismiss leaves the spec as it is.

## Stop

Do not plan. Do not implement. Do not commit. Do not create or update a Feature. Name `/crav1-finalize-commit` when a spec file changed. Do not run it.
