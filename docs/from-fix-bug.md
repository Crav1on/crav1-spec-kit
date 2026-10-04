# From a bug that already exists

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when a **real bug** is already named.

A real bug is a verify failure on work that is already shipping, or a defect that comes in from outside.

This is cross-cutting. It is not its own lane. It is not a stretch of verify. It is not `/crav1-fix-from-verify` and not `/crav1-fix-live`. Those walk the inner loop on work that is still in Build. This command is an intake for a bug that already exists. Spark, specify, plan, and verify do not run it. It is not a skill that runs because a repo is new, and it is not started automatically.

When you ask for startup options, this command is one of the options in that list.

## First prompt

New chat. Name the bug in this message. Say where you saw it.

```text
/crav1-fix-bug

Bug: <what is wrong>
Seen: <verify | a report | production>

Name the lane. Do not edit code. Do not open a pull request.
```

That slash command *is* the prompt.

If the message does not name a bug, the command stops. It does not go hunting. It does not pick a bug.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Which bug | Named a real bug | Stops when none was named. Does not hunt |
| Real or not | — | A design gap found before Build stays in the spec. An unfinished task stays a task. A one-off flaky check is a note, unless it keeps blocking ship. A verify failure on work that is not shipping yet stays the inner loop |
| Where | Said verify, a report, or production, or pick from those three | Options only when the bug was named and the place was not. Does not guess |
| Lane | Read the four lines | Says where it was seen, names the bug, points at the spec or the shipped behavior it breaks, and names the lane. A spec miss goes to Specify. A plan miss goes to Plan. A verify miss or a broken implementation goes to Build |
| Stop | Glance | Does not start that lane. Does not edit code, open a pull request, or create an Azure Boards work item |

## What does not get written

No code edit. No `spec.md` edit. No `plan.md` edit. No `verify.md` edit. No pull request. No `work-item.md`. No Azure Boards work item.

## After

Start the lane it named in a later turn. Do not treat this command as that lane.
