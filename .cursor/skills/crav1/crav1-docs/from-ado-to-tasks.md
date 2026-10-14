# From Azure Boards to tasks

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when the tasks of a spec are already in Azure Boards, sent by [From tasks to Azure Boards](from-tasks-to-ado.md), and the user wants what changed there back in the spec and `tasks.md`.

This is cross-cutting. It is not its own lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

It is a later skill. It is not a starter option. When the user asks for startup options, that ask names only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-existing-to-specs`, `/crav1-environment-read`, and `/crav1-fix-bug`. It does not run this command. The six starter options stay unchanged.

Reading the Feature itself back is [From Azure Boards to specs](from-ado-to-specs.md).

## First prompt

New chat.

```text
/crav1-ado-sync
```

Or name a spec, for example `/crav1-ado-sync email-service`, or `all`.

## Steps

### Check first

The org and the project come from `docs/environments/marks.md`, or from the Azure DevOps URLs in `docs/system/repos.md`, the same way as `/crav1-ado-sync`. If `az` fails, the command states the issue, suggests a fix such as `az login`, and offers a skip. It does not install `az` and it does not log in.

### Pick a spec

The list shows the specs whose `work-item.md` has task lines, plus **All**. A spec without task lines points at `/crav1-ado-sync`.

### Read back and compare

For every recorded task the command reads State, title, description, acceptance, Assigned To, the discussion, and the history. It shows only what differs from the spec and `tasks.md`, with who changed it and when when the history shows that. For example:

```text
T1 (#1234): Enable the day-ahead use case on dev
- State: Done (the task owner, date). tasks.md box is not ticked.
- Comment (a reviewer, date): "Can we also run it on test before Friday?"
```

It then lists **New under the Feature**: child items in Azure Boards that no task line records.

Each id is read in its own home, the `(ADO: <org>/<project>)` tag on its line. An id not found there is reported as moved or missing, and the command asks before searching other projects.

### Keep or dismiss

Each difference is kept or dismissed, one at a time. Dismiss is for this run only; the next run asks again. A kept change goes into the spec and `tasks.md` through `/crav1-add-to-spec`, quoted as `From ADO <date>. <who>.`

- A task that is in the done state in Azure Boards (the `Azure Boards task done state` line in `docs/environments/marks.md`) ticks its `tasks.md` box only when the user says yes.
- A task that was reopened in Azure Boards while its box is ticked unticks the box only when the user says yes.
- Active or another in-progress state is not shown as a difference. People set it, and the kit leaves it alone.
- A new child item is added as a task only on yes. It gets the next `T<n>` in `tasks.md` and a line `Work item: <id> — task: T<n> <short title>` in `work-item.md`. Ids never go into `tasks.md`.

### Reply comments

When a task's discussion asks something the spec already answers, the command drafts a reply. It strips file paths, line numbers, spec references, and kit names, keeps code repo names, and never mentions the specs repo. It posts only on yes. The command never writes a field back to Azure Boards.

## What gets written

Only the kept changes: the spec, `tasks.md`, and `work-item.md` lines for added tasks. The command names each file, says it is not committed yet, and does not commit.

## After

```text
/crav1-finalize-commit
```

Commit mentions keep the Feature id. When a commit clearly implements one recorded task, its task id is added too; when it is unclear, the commit skills ask. See [Data layout](concepts/data-layout.md).

Reference page: [ado-sync](reference/skills/crav1-ado-sync.md)
