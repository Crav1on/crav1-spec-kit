# From Azure Boards to specs

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when the user wants Azure Boards Features read back onto the specs.

This is cross-cutting. It is not its own lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

It is a later skill. It is not a starter option. When the user asks for startup options, that ask names only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. It does not run this command. The seven starter options stay unchanged.

Sending a Feature is [From specs to Azure Boards](from-specs-to-ado.md).

## First prompt

New chat. Name ids, or leave them out to read every id the specs already record.

```text
/crav1-ado-to-specs
```

Named ids:

```text
/crav1-ado-to-specs
52 81
```

That slash command *is* the prompt.

## What it reads

Ids come from every `docs/specs/<slug>/work-item.md` and from `## No spec yet in ADO` in `docs/system/landscape.md`, unless the user named ids. For each id it reads State, Priority, Target Date, Iteration, and Assigned To, plus discussion comments and history.

`az` is checked the same way as `/crav1-specs-to-ado`. A failure states the issue, suggests a fix such as `az login`, and offers a skip.

A deleted or missing id is reported as missing. The command does not guess another Feature.

## What the user sees

One block per Feature, and only what differs from the spec or is new. The user keeps or dismisses each change. Dismiss is for this run only. The next run starts fresh.

A kept change goes to the spec through `/crav1-add-to-spec`, labelled as coming from Azure Boards with the date and who changed it. An answer the user gives during the run goes into the spec first, labelled with the date as the user’s answer to the Azure Boards question.

A Feature with no spec yet suggests making the spec first, for example `/crav1-spark-to-spec`, from what was written on the Feature. The command does not run that starter.

When the Feature discussion asks a question and the spec already answers it, the command drafts a reply with no reference to the specs repo. It shows `Post comment on Feature <id>: <text>`. The user can change it, post it, or skip it. It is posted only on yes. When the spec has no answer, no reply is drafted. The question is offered as an open question for the spec instead.

The command does not create or update a Feature. It does not commit.
