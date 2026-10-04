# From code that already exists, suggest tests

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when the user points at **code that already exists**, one repo or one area, and wants tests suggested for what that code can actually break.

This is cross-cutting. It is not its own lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

It is a later skill. It is not a starter option. When the user asks for startup options, that ask names only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. It does not run this command. The seven starter options stay unchanged.

A function gets a few checks. A page gets a browser check. A boundary gets an integration check. The command does not dump every test type. Every suggestion stays listed. Nothing is dropped to keep the list short. The user takes them one at a time: keep, leave, or dismiss. Dismiss means it is not offered again. A kept suggestion goes onto the existing spec through `/crav1-add-to-spec`. Plan turns it into a task. This command does not write the tests, change the code, or start Specify, Plan, or Build.

## First prompt

New chat. Point at one repo or one area. Name the spec when one folder is the target.

```text
/crav1-suggest-tests-for-code
@<one repo or one area>
@docs/specs/<slug>/

Suggest tests for what this code can break. Do not write the tests. Do not change the code.
```

That slash command *is* the prompt.

If the message points at the whole system, the command stops. If it points at no code, it stops. It does not pick an area.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Code | Pointed at one repo or one area | Stops when the pointer is the whole system, several repos, or no code. Does not scan the repo to pick an area |
| Spec | Named one existing spec, or pick from the spec folders | Stops when no spec exists. Does not create a slug. Does not create a folder |
| List | Read every suggestion | A function gets a few unit checks. A page gets a browser check. A boundary gets an integration check. Every suggestion stays listed |
| One at a time | Keep, leave, or dismiss | One suggestion. Keep goes onto that spec through `/crav1-add-to-spec`. Leave is offered again. Dismiss is not offered again |
| Stop | Glance | Does not write the tests, change the code, or start Specify, Plan, or Build |

No existing spec: the command stops and points at the starter that fits. It does not run that starter.

## What gets written

A kept suggestion is an acceptance line on the existing `spec.md`, written by `/crav1-add-to-spec`.

A dismissed suggestion is one line under `## Dismissed test suggestions` on that same spec, so the next run does not offer it. It is not acceptance. Plan does not turn it into a task.

A left suggestion is not written. The next run offers it again when that code can still break that way.

No test code. No application code. No `plan.md`. No `tasks.md`. No new folder.

## After

Plan turns a kept suggestion into a task when the user runs plan:

```text
/crav1-plan-from-spec
```

This command does not run it.

When a file changed and the user wants it in git:

```text
/crav1-finalize-commit
```

That puts the spec lines in git. No push. This command does not commit.
