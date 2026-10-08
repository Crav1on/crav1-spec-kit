# Azure Boards calls

Shared by `/crav1-specs-to-ado` and `/crav1-ado-to-specs`.

Drop-in: `.claude/skills/crav1-specs-to-ado/references/azure-boards.md`. Plugin: this skill’s `references/azure-boards.md`. From `/crav1-ado-to-specs`: sibling `skills/crav1-specs-to-ado/references/azure-boards.md`.

The chat does not show these commands. The user sees the form, the diff, or `Post comment on Feature <id>: <text>`.

Pass `--detect false` on every `az` call. Do not run `az devops configure`. Do not substitute an org from `az devops configure`. Do not print a token, a secret, or a password.

## Finding `az`

Try `az` on `PATH` first. On Windows, `az.cmd` on `PATH` counts.

Before reporting `az` as not installed, check the default install paths for the operating system where this command is running. Use the first path that exists.

- Windows: `C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd`, then `C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd`
- macOS: `/opt/homebrew/bin/az`, then `/usr/local/bin/az`
- Linux: `/usr/bin/az`, then `/usr/local/bin/az`

When one of those paths exists, use that path for every `az` call in the command. Do not install `az`.

When `az` is not on `PATH` and none of those paths exists, `az` is not installed.

## Org and project

Take the org and the project from the first source that names both:

1. `docs/environments/marks.md`, when that file names the Azure DevOps org and project (an Azure DevOps URL, or both names written in the file).
2. Azure DevOps URLs in `docs/system/repos.md`.

An Azure DevOps URL matches `dev.azure.com` or `*.visualstudio.com` (HTTPS or SSH):

- `https://dev.azure.com/<org>/<project>/_git/<repo>` — path segments. Ignore userinfo such as `https://<org>@dev.azure.com/...`.
- `https://<org>.visualstudio.com/<project>/_git/<repo>` — the host label is the org.
- `git@ssh.dev.azure.com:v3/<org>/<project>/<repo>` — the path after `v3/`.
- `git@vs-ssh.visualstudio.com:v3/<org>/<project>/<repo>` and `<org>@vs-ssh.visualstudio.com:v3/<org>/<project>/<repo>` — the path after `v3/`.
- `ssh://` URLs use the same path segments.

Strip a trailing `.git`. A collection segment such as `DefaultCollection` is not the project.

The org flag is `https://dev.azure.com/<org>` or `https://<org>.visualstudio.com`, matching the URL.

Do not ask for a typed path. Do not guess an org. Do not read the org from the git remote of the docs repo. When the two sources name different pairs, ask which pair. Options only. One option per pair. Do not guess. When neither source names one org and one project, that is a failure. Offer skip.

## Failure

A failure is `az` not installed after the default-path check, `az` not signed in, the `azure-devops` extension missing, no access to the project, or no org and project in the two sources above.

State the issue. Suggest a fix when there is one.

- `az` not installed: point at `https://learn.microsoft.com/cli/azure/install-azure-cli`. Do not install it.
- Extension missing: `az extension add --name azure-devops`. Point at `https://learn.microsoft.com/azure/devops/cli/`. Do not install it.
- No login: `az login`. Do not run it. Do not log in.
- No org and project: say `docs/environments/marks.md` and `docs/system/repos.md` do not name them.

Offer skip. Use the questions tool when it is available. The options are only:

1. **Retry**
2. **Skip**

Stop until the user picks. **Skip** stops the command. Say the Azure Boards calls did not run, and why. Do not create, update, or post.

Check in this order: `az` installed, then `az extension show --name azure-devops`, then `az account show`. The Feature type check comes after those pass.

## Feature type

```text
az boards work-item type list --organization <org-url> --project <project> --detect false -o json
```

The project has the type when a returned name is `Feature`. If it does not, say the project has no Feature work item type, and stop. That stop is not the skip prompt. Do not create a type. Do not create a work item of another type.

## Create and update

Create:

```text
az boards work-item create --type Feature --title "<title>" --organization <org-url> --project <project> --detect false --fields "System.State=New" "Microsoft.VSTS.Common.ValueArea=Business" "System.Description=<html>" "Microsoft.VSTS.Common.AcceptanceCriteria=<html>" "System.Tags=<tags>" "Microsoft.VSTS.Scheduling.TargetDate=<YYYY-MM-DD>"
```

Omit `Microsoft.VSTS.Scheduling.TargetDate` when the spec states no target date. Omit `Microsoft.VSTS.Common.AcceptanceCriteria` when the spec has no checks. Omit `System.AreaPath`, `System.IterationPath`, and `Microsoft.VSTS.Common.Priority`. Area stays the project default. Iteration and Priority stay blank so the user’s team can set them.

Update:

```text
az boards work-item update --id <id> --organization <org-url> --project <project> --detect false --fields "<only fields the user accepted>"
```

Do not send State, Area, Iteration, Priority, or Assigned To on an update unless the accepted diff includes that field. Do not clear a target date the spec does not state. Tags on an update add the slice name and the code repos that are missing. Do not remove a tag the form does not list.

Description and Acceptance Criteria are HTML. Turn the plain paragraphs into `<p>` paragraphs. Escape `<`, `>`, and `&`. No links. No paths. No kit names. No skill names.

Tags are semicolon-separated. The slice name, then each code repo the slice involves. Never the repo that holds the specs.

## Show, comments, and history

Show:

```text
az boards work-item show --id <id> --organization <org-url> --project <project> --detect false -o json
```

Read `System.State`, `Microsoft.VSTS.Common.Priority`, `Microsoft.VSTS.Scheduling.TargetDate`, `System.IterationPath`, `System.AssignedTo`, plus title, description, acceptance criteria, and tags when comparing.

Comments:

```text
az devops invoke --area wit --resource comments --route-parameters project=<project> workItemId=<id> --organization <org-url> --detect false --api-version 7.1-preview.4 -o json
```

History:

```text
az devops invoke --area wit --resource updates --route-parameters project=<project> id=<id> --organization <org-url> --detect false --api-version 7.1 -o json
```

A not-found id is missing. Do not search by title.

Post a comment only after the user says yes:

```text
az devops invoke --area wit --resource comments --route-parameters project=<project> workItemId=<id> --organization <org-url> --detect false --http-method POST --api-version 7.1-preview.4 --in-file <body.json> -o json
```

The body is `{"text":"<p>...</p>"}`. The text is the accepted reply. No docs-repo path, link, kit name, or skill name. Delete the body file after the call. Do not print the body file path in the chat.
