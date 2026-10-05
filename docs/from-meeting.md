# From a meeting to specs

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when the user has **minutes or a transcript** (a file, a paste, or a Teams or Zoom export) and wants the decisions matched to specs that already exist.

This is cross-cutting. It is not its own lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

It is a later skill. It is not a starter option. When the user asks for startup options, that ask names only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. It does not run this command. The seven starter options stay unchanged.

[Intake](from-intake.md) starts a landscape and new feature slugs from a dump. It does not match items against specs that already exist. [Add](from-add.md) takes one piece of new information for one existing spec. This command extracts many items, matches them, and hands one kept addition to add-to-spec.

The command writes nothing itself. The transcript is not copied into the repo. Only a quote the user keeps as an addition reaches a spec, through `/crav1-add-to-spec`.

## First prompt

New chat. Paste the minutes, or `@` the file.

```text
/crav1-meeting-to-specs
@<minutes, transcript, or Teams or Zoom export>

Extract what matters for features. Match it to the specs we already have. Do not write a file.
```

That slash command *is* the prompt.

If the message has no minutes and no `@`, the command stops. Options only. It does not pick a file.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Minutes | Pasted or `@` a file | Stops when nothing was pointed at. Does not scan the repo. Does not guess |
| Extract | Read the list | Requirements, decisions, changes, open questions, and bugs. Each item is a quote. Speaker and time when the transcript shows them. Small talk is dropped |
| Match | Read every item | Addition, new feature, bug, or unclear. Every candidate spec stays listed. Skip `_template` |
| One at a time | Keep, leave, or dismiss | One item. Dismiss is for this run only. The next run starts fresh |
| Keep | Glance | Addition goes through `/crav1-add-to-spec`. New feature or bug only names the next command |
| Stop | Counts | Writes nothing itself. Does not start Specify, Plan, or Build |

## What gets written

This command writes no files. No `docs/system/`. No new spec folder. No marks. No dismissals file. The transcript stays out of the repo.

A kept addition is a quote on the existing `spec.md`, written by `/crav1-add-to-spec`. The quote starts with `From meeting <date>.` when the date is known, otherwise `From meeting.` The impact check still runs there. Other files change only when apply is picked.

A left item is not written. A dismissed item is not written. The next run can offer either again.

## After

A kept new feature names one next command. This command does not run it.

- One kept new feature that is one or two sentences: `/crav1-spark-to-spec`
- One kept new feature that is a pile of ideas and technical hunches: `/crav1-ideas-to-spec`
- Two or more kept new features: `/crav1-intake-to-specs`

A kept bug names `/crav1-fix-bug`. This command does not run it.

When a file changed and the user wants it in git:

```text
/crav1-finalize-commit
```

That puts the spec lines in git. No push. This command does not commit.
