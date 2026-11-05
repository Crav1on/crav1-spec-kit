# Host setup (shared)

One reference for every route that changes an Azure DevOps or GitHub setting that does not live in the repo. `/crav1-host-setup` (ad hoc) and the plan route (`/crav1-plan-from-spec`, `/crav1-build-tasks`, `/crav1-build-features`, `/crav1-verify-build-against-spec`) all follow it, so both routes write the same script.

## Code or host setup

Anything the host reads from the repo is code: pipeline YAML, pipeline templates, environments named from YAML, Bicep and other infrastructure as code. Build it like any other code, on a branch and through a pull request.

Only a setting that exists nowhere but the host's project or repository settings is host setup:

| Setting | Azure DevOps | GitHub |
| --- | --- | --- |
| Build validation (required build) | `az repos policy build` | branch protection required checks |
| Required reviewers, minimum reviewers | `az repos policy required-reviewer`, `az repos policy approver-count` | branch protection reviews |
| Other branch policies (work items, comments, merge types) | `az repos policy work-item-linking`, `comment-required`, `merge-strategy` | branch protection or rulesets |
| Environment approvals and checks | `az devops invoke` (environment checks) | environment protection rules |
| Variable groups (non-secret values) | `az pipelines variable-group` | repository or environment variables |
| Service connections, secret variables | manual only, see **Secrets** | manual only |

When unsure whether a setting can live in the repo, prefer the repo.

## The script

One checked-in script per setting group, under `infra/ado/<name>.sh` (Azure DevOps) or `infra/github/<name>.sh` (GitHub), unless the repo already keeps such scripts elsewhere. `<name>` says what it sets, for example `develop-build-policy`.

- Bash, `set -euo pipefail`, with the organization, project, repository and branch as variables at the top. No values of secrets, ever.
- A comment block above every command: line 1 says **what** it sets in plain words, line 2 says **why**. The manual steps are generated from these comments, so keep them complete.
- Two parts, chosen by the first argument: `apply` runs the changes; `check` only reads. `check` prints one line per setting, `ok: <setting>` or `missing: <setting> (<what differs>)`, and exits non-zero when any line is `missing`.
- `apply` is idempotent: it reads first and updates an existing policy rather than adding a second one.
- Text is kit-neutral: the comments, output and commit message name the setting and its reason, never specs, tasks, plans or kit commands.

## Manual steps

Generate the manual steps from the script's comments, one numbered step per command: what to open (for example Project settings, Repositories, `<repo>`, Policies, `<branch>`), what to set, and what you should then see. Never write them by hand separately; when a comment changes, regenerate the steps. Show them with the script, so a person can do it by hand instead.

## Secrets

A service connection, a secret variable or any credential is always manual. The script's `check` part only confirms it exists by name (for example `az devops service-endpoint list` filtered by name, or a variable group variable listed as secret). The manual steps say what to create, its name, its scope and where. The kit never asks for, reads, prints or stores a secret value.

## Show, confirm, run

Before any `apply`, show the exact commands (the script's `apply` part with variables filled in), the scope of each (this branch, this repository, the whole project) and the manual steps. A project-wide setting says so in bold. Then ask, word for word:

> **Reply yes** (or "confirm") to run it as shown.
> To change something first, reply with your edits, for example "make it optional" or "only on develop".
> Nothing runs until you say yes.

Edits redraft the script and steps and show them again. Run `apply` only after yes, then run `check`. A command that fails for permission says which permission is missing and stops; it never retries with other credentials. Not signed in (`az account show` or `gh auth status` fails): stop and name the sign-in; do not run anything.

Headless or bot runs never apply: they write the script and steps and stop with `Host setup not applied. Run it after a yes.`

## Done means read back

A host-setup task or point is done only when `check` prints `ok` for every setting it owns, read from the live host in this run. A script that was written but not applied, or applied with a `missing` line, is not done. Record the check output (not the commands' tokens) as the evidence.

## Commit

Commit the script on a work branch (the code-branch guard applies), with a short message that names the setting, for example `Require a green build on develop`. Push and pull requests go through `/crav1-open-pr` as usual.
