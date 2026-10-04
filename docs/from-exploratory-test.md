# From a built slice, exploratory test

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when a **build of a slice already exists** and the user wants that slice used, then used again with randomness, and the bugs written down.

This is cross-cutting. It is not its own lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

It is a later skill. It is not a starter option. When the user asks for startup options, that ask names only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. It does not run this command.

Pass one learns the slice by using it once. Pass two is no longer careful. It adds randomness: sometimes a double-click, a hover back and forth, repeating an action, or using the same control more than once. It follows what the last action showed. It lasts about as long as the first pass, long enough to provoke bugs, then it stops. That stop is named `matched the first pass`. It stops sooner when the user says stop. That stop is named `the user said stop`. The user does not set a clock. The second pass does not run forever.

It does not write the checks the plan already named. A bug it finds is not sent to `/crav1-fix-bug` unless the user says so in that turn.

## First prompt

New chat. Point at the slice that already has a build.

```text
/crav1-exploratory-test
@docs/specs/<slug>/

Use the slice once, then again with randomness. Write down bugs. Do not start Specify, Plan, or Build.
```

That slash command *is* the prompt.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Slice | Named the slice, or pick from the slices that have a build | Stops when no slice has a build. Does not start Build |
| Pass one | — | Uses the slice once and counts the actions. Learns how the slice works |
| Pass two | — | No longer careful. Sometimes a double-click, a hover back and forth, a repeated action, or the same control more than once. Follows what the last action showed |
| Stop | Say stop to end sooner | Stops when the second pass has gone on about as long as the first. The stop name is `matched the first pass`. The user saying stop ends it sooner. That stop name is `the user said stop`. The user does not set a clock |
| Bugs | Read `explore.md` | Writes what broke. Leaves the plan’s checks in the plan |

## What gets written

`docs/specs/<slug>/explore.md` in the slice folder that already exists. Bugs from using the slice, the action count from pass one, and the stop name.

No `spec.md` edit. No `plan.md` edit. No `tasks.md` edit. No `verify.md` edit. No application code. The checks the plan already named stay where they are.

## After

The run is done when the stop name is written. A bug stays in `explore.md`.

Send a bug to `/crav1-fix-bug` only in a turn where the user says so. This command does not start Specify, Plan, or Build.

When the file changed and the user wants it in git:

```text
/crav1-finalize-commit
```
