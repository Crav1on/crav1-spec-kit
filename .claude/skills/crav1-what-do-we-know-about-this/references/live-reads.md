# crav1-what-do-we-know-about-this: live reads

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

### Finding `az`

Try `az` on `PATH` first. On Windows, `az.cmd` on `PATH` counts.

Before reporting `az` as not installed, check the default install paths for the operating system where this command is running. Use the first path that exists.

- Windows: `C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd`, then `C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd`
- macOS: `/opt/homebrew/bin/az`, then `/usr/local/bin/az`
- Linux: `/usr/bin/az`, then `/usr/local/bin/az`

When one of those paths exists, use that path for every `az` call in this command. Do not install `az`.

When `az` is not on `PATH` and none of those paths exists, `az` is not installed.

### Azure resource settings and recent changes

Use `az` to list and show. Do not create, update, delete, deploy, start, stop, or set a resource. Do not switch subscription. One pass on the current account.

- `az account show` for the current account
- `az resource list` for a resource whose name matches the thing
- `az resource show` for that resource’s settings
- `az monitor activity-log list` for recent changes on that resource id

Recent changes are the operation name, the status, the time, and the caller when the log shows a name. No request body. No payload.

Do not print a secret, a key, a password, a connection string, or a token. A secret name may be cited. The secret value is not. A setting value is shown only when it is a resource id or a hostname, or when the resource is non-prod and the value is not a secret.

Do not read request logs, metrics, or traffic. Do not open a database. Do not open storage. Never a row. Never a blob.

A resource name that is not in the question and not in the repo answer: this live read does not apply. Say so. That is not a failure.

### Production

Production follows `/crav1-read-environment` (drop-in: `.claude/skills/crav1-read-environment/SKILL.md`, the pre-prod, shared, and prod-only rule; plugin: sibling `skills/crav1-read-environment/SKILL.md`).

Prod-only means the only mark is production. A similar name on another resource is not a twin. Pre-prod, shared-with-prod, and prod-only stay shape and connections only, after the same yes or no.

When a matched resource is pre-prod, shared with prod, or prod-only, ask before it is read. Use the questions tool when it is available. The options are only:

1. **Yes. Read these for shape and connections only.**
2. **No. Leave them unread.**

Stop until the user picks. One answer covers every such resource this pass listed.

Shape and connections means names, types, setting keys, routes the settings already show, timers, links, and secret names. A setting value is shown only when it is a resource id or a hostname. Say `prod only` on a prod-only resource. Say `Shape and connections only.` Never data. Never secret values. Never a row or a blob. A yes does not open a production database or production storage.

A no leaves those resources unread. The answer says they were not read.

A non-prod resource (dev, test, stage, uat, qa) is settings and recent changes, as above. It does not need that yes. It is still never data and never a secret value.

### Azure DevOps

Work items, open pull requests, and branches that touch the thing. Every fact from this read is tagged `Live read.`

The org and project come from the first source that names both:

1. The git remote, when it is Azure Repos (`dev.azure.com` or `*.visualstudio.com`).
2. `docs/environments/marks.md`, when that file already names the Azure DevOps org and project.
3. Azure DevOps URLs in `docs/system/repos.md`, when the git remote is not Azure Repos and `docs/environments/marks.md` does not name the org and project.

Do not ask for a typed path. Do not guess an org.

A recorded id is read in its own home: the `(ADO: <org>/<project>)` tag on its `work-item.md` line, or the `Work items go to` cell of the repo in `docs/system/repos.md`, as [work-item-homes.md](../../crav1-ado-sync/branches/push-features/references/work-item-homes.md) (drop-in: `.claude/skills/crav1-ado-sync/branches/push-features/references/work-item-homes.md`; plugin: sibling `skills/crav1-ado-sync/branches/push-features/references/work-item-homes.md`) says. An older line without a tag uses the pair above. An id not found there is reported as moved or missing with that home; ask before searching other projects. This command only reads: it does not ask for or write a home.

For source 3, read `docs/system/repos.md` when that file exists. An Azure DevOps URL matches `dev.azure.com` or `*.visualstudio.com` (HTTPS or SSH). Read the org and the project from the URL:

- `https://dev.azure.com/<org>/<project>/_git/<repo>` — path segments. Ignore userinfo such as `https://<org>@dev.azure.com/...`.
- `https://<org>.visualstudio.com/<project>/_git/<repo>` — the host label is the org.
- `git@ssh.dev.azure.com:v3/<org>/<project>/<repo>` — the path after `v3/`.
- `git@vs-ssh.visualstudio.com:v3/<org>/<project>/<repo>` and `<org>@vs-ssh.visualstudio.com:v3/<org>/<project>/<repo>` — the path after `v3/`.
- `ssh://` URLs use the same path segments.

Strip a trailing `.git`. A collection segment such as `DefaultCollection` is not the project.

When those URLs name one org and one project, use them. When `docs/system/repos.md` is missing, it has no Azure DevOps URL, or the URLs do not name one org and one project, this read does not apply. Say so under **Tracked elsewhere**. That is not a failure.

Use `az boards` and `az repos` to list and show, the same way for every source above. Pass that org and that project on the calls. The org is `https://dev.azure.com/<org>` or `https://<org>.visualstudio.com`, matching the URL. Do not substitute an org from `az devops configure`. Do not edit a work item, a pull request, or a branch. Do not pass `--work-items`. Do not create a work item.

- work items whose title contains the name
- open pull requests whose title or source branch touches the thing
- branches whose name touches the thing

### When a live read fails

The repo part is already done. A failure is `az` not installed after the default-path check, `az` not signed in, the `azure-devops` extension missing, or no access to the DevOps project. A read that does not apply is not a failure.

Show one prompt. State each failure. Suggest a fix when there is one. `az login`, then retry, when the login is missing. Name a missing `az` only after the default install paths have been checked. Name a missing `azure-devops` extension. Do not install. Do not log in. Do not run `az login`.

Use the questions tool when it is available. The options are only:

1. **Retry**
2. **Skip**

Stop until the user picks.

**Retry** runs the failed reads again. Keep a live fact that already succeeded. Do not ask another question in that turn. If the retry fails, show the same prompt again. Do not answer with a partial live read.

**Skip** gives the repo-only answer. One line says the live checks did not run, and why. Do not mix a partial live read into that answer.

Do not ask the production question in the same turn as the failure prompt. That question comes after the Azure list succeeds.
