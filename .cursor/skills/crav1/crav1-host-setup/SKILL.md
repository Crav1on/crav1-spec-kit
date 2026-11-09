---
name: crav1-host-setup
description: >-
  Use when the user asks for a host setting that does not live in the repo,
  such as a branch policy, required build, reviewers, an approval or a
  variable group. Drafts a checked-in az or gh script and manual steps, runs
  it after a yes, reads it back and commits it. Secrets stay manual.
disable-model-invocation: true
icon: settings
color: blue
---

# Host setup

Change one host setting the user describes, the same way a small code fix is made: drafted, shown, changed until right, applied after a yes, checked, committed.

Command: `/crav1-host-setup`.

Read [references/host-setup.md](references/host-setup.md) every run. It is the shared rule for the script, the manual steps, secrets, the confirm wording and what done means. The plan route uses the same file, so both produce the same script.

This is cross-cutting. It is not a lane. It does not need a spec. It runs only when this turn names a setting to add, change or check. It does not hunt for missing settings.

## What they asked

Restate the ask in one line: the setting, the host (Azure DevOps or GitHub), the organization or owner, project, repository and branch. Take what the message, `docs/system/repos.md` or the git remote already say. Ask once, with options, only for what is still missing. Do not guess a pipeline: when the setting needs one and several fit, list them (the repo's pipeline YAML, or `az pipelines list` when signed in) and ask.

If the ask is something the host reads from the repo (pipeline YAML, a template, an environment named in YAML, infrastructure as code), say it is code, not host setup, and name the lane: `/crav1-build-tasks` when a plan task covers it, else `/crav1-fix-bug` for a broken one or `/crav1-spark-to-spec` for new work. Stop.

If the ask is several related settings tied to a feature, or needs a decision beyond the setting, suggest moving it into a spec (`/crav1-add-to-spec` for an existing spec, `/crav1-spark-to-spec` for a new one) and ask once: **Move it to a spec** or **Do it here**.

## Read first

Read the live setting before drafting, when signed in (`az account show` or `gh auth status`). Say what is there now in one line. When it already matches, say so, write no `apply` command, offer to commit only the `check` part, and stop on no.

Not signed in: draft anyway, say the read was skipped, and do not apply.

## Draft

Write the script as the reference says: `infra/ado/<name>.sh` or `infra/github/<name>.sh`, a what and why comment above every command, `apply` and `check` parts, no secret values. Generate the manual steps from those comments.

Show, in this order:

1. One line: the setting and its scope (branch, repository or the whole project).
2. The script.
3. The manual steps.
4. What changes for people once it is live, for example "pull requests into develop then need a green build of orders-api-ci before they can merge".
5. The confirm block from the reference, word for word.

## Iterate

A reply with edits redrafts the script, regenerates the manual steps and shows all of it again with the confirm block. Keep going until yes or stop. `stop` or `no` writes nothing and runs nothing.

The user may choose `manual` instead of yes: then do not run the script. They do the steps; when they say done, run `check` only.

## Apply and check

On yes: guard the branch first (skill `crav1-create-feature-branch`, `references/code-branch.md`; on a base branch offer a work branch, for example `chore/<name>`). Write the script, run `apply`, then `check`. Report each `check` line.

- All `ok`: done.
- Any `missing`: not done. Say what differs and offer to redraft. Never call it done.
- Permission or sign-in failure: stop, name the missing permission or sign-in. Never retry another way.

## Commit

After the check, commit the script on the work branch with a short message naming the setting. Commit only the script (and its generated steps, when the repo keeps them next to it). Do not push. Name `/crav1-open-pr` as next.

When a spec covers this setting, say which one and suggest `/crav1-add-to-spec` to record it; do not edit the spec here.

When a pull request thread asked for this setting, name `/crav1-pr-status` so it can read the setting back and close the point. Do not post on the thread.

## Choice words

Exact words for bots and scripted runs: `yes` / `manual` / `stop` for the confirm; `spec` / `here` for the move question; `check` to only read the live setting and report. A headless run with no person never applies: it drafts, shows and stops with `Host setup not applied. Run it after a yes.`

## Output

- The setting, scope and what was there before
- The script path and the manual steps
- Applied or not, and each `check` line
- The commit, or why there is none
- `Next: /crav1-open-pr, because the script is on a work branch and not on a pull request yet.` When a thread asked for the setting, say that in the reason. Do not also name pr-status. Add the Uncommitted line when the script is not committed. Do not run the next step.

## Hard rules

- Never apply without an explicit yes to the shown script in this turn.
- Never handle a secret value. Service connections and secret variables are manual; `check` confirms them by name.
- Done only when `check` reads the live setting back as `ok`.
- Host-facing text (script comments, output, commit message) is kit-neutral: no specs, tasks or kit commands.
- No pipeline applies the script. The kit runs it.
- Do not push, open a pull request or post on a thread.

## Run ending (1.122.0)

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says.
