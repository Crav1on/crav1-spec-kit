# Set up a host setting

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not).

Use this when you need a setting on Azure DevOps or GitHub that does not live in the repo: a branch policy or required build, required reviewers, an environment approval, or a variable group. The kit treats it like code. It writes a checked-in script, shows it, and runs it only after your yes.

Pipeline YAML, templates and infrastructure as code are not host setup. They are code and are built through the usual lanes.

## First prompt

```text
/crav1-host-setup

Require a green build of orders-api-ci on develop in orders-api.
```

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Ask | Say what the setting should do | Restates the setting, host, repository and branch. Asks only for what is missing, with options. Routes repo-readable things to their lane and offers a spec for a larger ask |
| Read | — | Reads the live setting when signed in and says what is there now |
| Draft | Read the script and the steps | Writes `infra/ado/<name>.sh` (or `infra/github/<name>.sh`) with a what and why comment above each command, `apply` and `check` parts, and the manual steps generated from those comments. Shows the scope and what changes for people |
| Iterate | Reply with edits, or yes, `manual` or stop | Redrafts and shows it again until yes. Nothing runs before yes |
| Apply | — | On a work branch, runs `apply`, then `check`, and reports each line. Done only when every line is `ok` |
| Commit | — | Commits the script with a short message naming the setting. Does not push |

## Secrets

Service connections and secret variables are always manual. The script only checks they exist by name, and the steps say what to create and where. The kit never asks for or sees a value.

## From a plan

A plan task marked `(host setup)` follows the same rules inside [Build tasks](from-plan-to-build.md), and [Verify and fix](from-verify.md) counts it done only when the live setting reads back `ok`. `/crav1-pr-status` closes a pull request point that asked for the setting once it reads it back live. During a build, a yes that is not on record is waiting, not blocked, and the task stays unticked. The script is committed on the branch the build map names for that task.

## After

```text
Next: /crav1-open-pr, because the script is on a work branch and not on a pull request yet.
```

A thread that asked for the setting is named in that reason. `/crav1-pr-status` comes after the pull request exists. See [How a run ends](reference/run-ending.md).

Reference page: [host-setup](reference/skills/crav1-host-setup.md)
