# crav1-merge-pr: azure devops

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

### Azure DevOps (`az`)

Treat the remote or the pull request URL as Azure DevOps when it matches `dev.azure.com` or `*.visualstudio.com` (HTTPS or SSH). Read org, project, and repository from that URL when you can:

| Shape | Org / project / repo |
| --- | --- |
| `https://dev.azure.com/<org>/<project>/_git/<repo>` | path segments |
| `https://<org>@dev.azure.com/<org>/<project>/_git/<repo>` | path segments (ignore the userinfo) |
| `https://<org>.visualstudio.com/<project>/_git/<repo>` | host label is the org |
| `git@ssh.dev.azure.com:v3/<org>/<project>/<repo>` | path after `v3/` |
| `git@vs-ssh.visualstudio.com:v3/<org>/<project>/<repo>` | path after `v3/` |
| `<org>@vs-ssh.visualstudio.com:v3/<org>/<project>/<repo>` | path after `v3/` |

`ssh://` URLs use the same path segments. Strip a trailing `.git`. Percent-decode project and repository when the URL encoded them. A collection segment such as `DefaultCollection` stays in the web URL; it is not the project name.

Use `az repos pr` only when **all** of these are true:

1. `az` is on `PATH` (on Windows, `az.cmd` counts).
2. The azure-devops extension works or can be used. `az repos pr list -h` exits 0, or the first `az repos pr` call succeeds. Microsoft documents that this extension installs automatically the first time an `az repos pr` command runs (Azure CLI 2.30.0 or higher). If that first call still cannot run `az repos pr`, the extension is not usable.
3. The CLI is already authenticated for a non-interactive call. A show or list call for this pull request that returns without an auth error counts. `az account show` exiting 0 is a hint, not proof. An `AZURE_DEVOPS_EXT_PAT` the user already set is a credential for that call. Do not print it. A dialog box or a browser Microsoft sign-in is not a merge path. Do not run `az login`, `az devops login`, a device-code flow, or a web login. Do not create a token. See **Auth notes**.

Prefer org, project, and repository parsed from the pull request URL, else the remote. Project and repository fill the REST fallback and the web UI. `az repos pr show`, `az repos pr policy list`, and `az repos pr update` do not take `--project` or `--repository`. A pull request id is unique in the organization. Pass `--org` and `--id`, and pass `--detect false`.

- `--org` is the organization URL, for example `https://dev.azure.com/<org>` or `https://<org>.visualstudio.com`
- `--id` is the pull request id

`--detect` is documented as "Automatically detect organization" (`true` or `false`; default `true`). From a local Azure Repos checkout it reads **that** git remote and overrides `az devops configure` defaults. Command flags win over detection. Use `--detect true` and omit `--org` **only** when the URL did not yield the organization **and** this command runs in a local checkout of that same remote. Otherwise do not use `--detect true`. Do not pass `--project` or `--repository` on show, policy list, or update.

**Merge** then uses the Azure DevOps steps. If `az` is missing, the extension is not usable, the CLI is not already authenticated, or show/update fails, print the Azure DevOps fallback below. Do not invent a merge commit hash. Do not run `az rest`.

### Azure DevOps (Read it first)

```text
az repos pr show --org <org-url> --id <n> --detect false --output json
az repos pr policy list --org <org-url> --id <n> --detect false --output json
```

Use the `--detect true` form from **Host** only in the case Host allows, and omit only `--org`.

`status` must be `active`. That is the open set, including drafts.

Keep `title`, source branch (`headRefName` or `sourceRefName`), and target branch (`baseRefName` or `targetRefName`). Strip a `refs/heads/` prefix when you show the branches.



### Azure DevOps (What must pass)

Stop unless all of these are true after the ready step:

| Check | Pass | Stop and report |
| --- | --- | --- |
| `mergeStatus` | `succeeded` | `conflicts`, `failure`, `rejectedByPolicy`, `queued`, or anything else |
| Required reviewers | `isRequired` and vote `10` or `5` | vote `0`, `-5`, or `-10` on a required reviewer |
| Blocking policies | enabled and `isBlocking`, status `approved` or `notApplicable` | `queued`, `rejected`, `broken`, `running`, or any other status |

`conflicts` gets the same merge-the-base-in line as `DIRTY` above (1.66.0), never a rebase.

Do not call `az repos pr set-vote`. Do not vote for the user.

Before the complete call, read that same policy list for a merge-type restriction. Stop and print the Azure DevOps fallback, and do not call update, when an enabled blocking policy's `configuration.settings` sets `allowNoFastForward` to false, or sets the legacy `useSquashMerge` to true. That policy does not allow a no-fast-forward merge commit. Name the policy (`configuration.type.displayName` when it is present; merge-strategy type id `fa4e907d-c16b-4a4c-9dfa-4916e5d171ab`). Do not retry with another merge type. Do not pass `--bypass-policy`.

When those settings are absent, the table above is the whole policy check.

### Azure DevOps (Merge)

When **Host** says to use `az`, and the read and policy checks have passed, including the merge-type check above:

```text
az repos pr update --org <org-url> --id <n> --status completed --squash false --detect false --output json
```

`--squash false` is the no-fast-forward merge commit. On Azure DevOps, a non-squash completion without an explicit `mergeStrategy` is `noFastForward`. `--output` is a global flag so the completion body can be read. Do not pass `--project`, `--repository`, or `--merge-strategy`. `az repos pr update` does not accept them. Do not pass `--squash true`, `--bypass-policy`, `--bypass-policy-reason`, `--delete-source-branch`, `--transition-work-items`, `--auto-complete`, or `--merge-commit-message`.

If this command fails, stop. Do not retry. Do not try `--squash true`, `--status completed` alone, `--merge-strategy`, or any other strategy. A status-only complete copies completion options already on the pull request, and those can be squash. Print the Azure DevOps fallback. Do not claim the pull request was merged. Do not run `az rest`. Do not start a sign-in.

On success, fetch the pull request again and confirm it. Do not treat the update body as the last word. The update response can still say `status` `active` after a successful complete. Only the re-read counts.

```text
az repos pr show --org <org-url> --id <n> --detect false --output json
```

`status` must be `completed`. `lastMergeCommit.commitId` is the merge commit. Keep that hash. Do not invent one. If `status` is not `completed`, stop and say the state. If `lastMergeCommit.commitId` is empty, say the merge commit is not in the response yet. Do not guess. Do not continue.

Do not read `lastMergeCommit.parents` on the pull request. That array is null on a real Azure DevOps response even when the commit has parents, so a parent check cannot use it.

Count parents with git. Use the `git` from the top of this skill, the remote from **Which pull request**, and the target branch name without `refs/heads/`. `<commitId>` is `lastMergeCommit.commitId` from the re-read.

```text
git fetch <remote> <target>
git rev-list --parents -n 1 <commitId>
```

The line is `<commitId> <parent1> <parent2>` for a merge commit. Two ids after the commit id means a merge commit. One parent is not a merge commit.

If `git rev-list` exits non-zero, or does not print that commit id, git cannot see the commit. Fall back to the Azure DevOps commits API. This GET only counts parents. Do not use it to complete, update, or bypass the pull request. Do not run it when git already returned a parent count. Do not add an Authorization header. Do not print a token. Do not start a sign-in.

```text
az rest --method get --uri "https://dev.azure.com/<org>/<project>/_apis/git/repositories/<repo>/commits/<commitId>?api-version=7.1"
```

Use `https://<org>.visualstudio.com/...` when that is the host. Repository id from `repository.id` on the show payload when it is present; otherwise the repository name. Count the `parents` array. Two entries is a merge commit. One entry is not.

If that GET fails, or `parents` is missing, stop and say the merge type could not be verified. Name the commit id. Do not claim a no-fast-forward merge. Do not fast-forward local `main`. Do not treat the update body, or a null `lastMergeCommit.parents`, as proof.

If the commit does not have two parents, stop and report plainly: the pull request is completed, the hash, and the parent count. A branch policy may have forced squash or rebase. Do not fast-forward local `main`. Do not retry. Do not claim a no-fast-forward merge.
