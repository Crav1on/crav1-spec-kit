# crav1-merge-pr: fallback

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Fallback (no merge)

Print the title, `source` → `target`, and the strategy line from **Show, then merge**. Then the filled commands. This printout is not a completed merge.

GitHub, or a remote that is not Azure DevOps:

```text
gh pr ready <n>
gh pr checks <n>
gh pr merge <n> --merge
gh pr view <n> --json mergeCommit --jq .mergeCommit.oid
```

Web UI: open the pull request. If it is a draft, choose **Ready for review**. Then **Merge pull request** → **Create a merge commit**. Do not choose **Squash and merge** or **Rebase and merge**. Do not use an admin override. Do not delete the branch unless the user asked in this turn.

Azure DevOps. Fill org, project, and repository from the URL or the remote when you have them. Name any you could not parse. Do not invent them. Repository id from `repository.id` on a show payload when you have it; otherwise the repository name from the URL.

Print the request and the web UI. Do not run it. Do not run `az rest`. That path depends on an `az login` session, which often is not authorized for an organization that belongs to a personal Microsoft account. Do not add an Authorization header. Do not print or echo a token. See **Auth notes**.

Draft, when it is still a draft:

```text
PATCH https://dev.azure.com/<org>/<project>/_apis/git/repositories/<repo>/pullrequests/<id>?api-version=7.1
Content-Type: application/json

{"isDraft": false}
```

Complete (merge commit). `lastMergeSourceCommit.commitId` is the pull request's current source head (`lastMergeSourceCommit` on the open pull request). Do not invent that SHA. If it could not be read, leave the placeholder and say so.

```text
PATCH https://dev.azure.com/<org>/<project>/_apis/git/repositories/<repo>/pullrequests/<id>?api-version=7.1
Content-Type: application/json

{
  "status": "completed",
  "lastMergeSourceCommit": { "commitId": "<lastMergeSourceCommit.commitId>" },
  "completionOptions": { "mergeStrategy": "noFastForward" }
}
```

Use `https://<org>.visualstudio.com/...` when that is the host. Do not set `bypassPolicy`, `deleteSourceBranch`, `squashMerge`, or `transitionWorkItems`.

Web UI: open `https://dev.azure.com/<org>/<project>/_git/<repo>/pullrequest/<id>` (or the `*.visualstudio.com` form). If it is a draft, **Publish**. Then **Complete**, then **Merge (no fast-forward)**. Do not choose **Squash commit**, **Rebase and fast-forward**, or **Semi-linear merge**. Leave bypass policies off. Do not delete the source branch unless the user asked in this turn. Do not change work-item links.

GitKraken stays **GUI paste only** when the user already uses it for this repo: complete the named pull request with a merge commit (no fast-forward). Do not squash. Do not rebase.

## Auth notes

The skill does not run `az login`, `az devops login`, a device-code flow, or a web login. It does not create a token. It does not print or echo a token. It does not put a token on a command line.

When the azure-devops extension crashes with `module 'keyring' has no attribute 'core'` (seen on Azure CLI 2.90.0), skip `az devops login`. The user sets a personal access token scoped to Code (Read & Write) in the `AZURE_DEVOPS_EXT_PAT` environment variable, then runs this skill again. Do not print or echo that value.

When a call returns `TF400813` after `az login`, the signed-in directory identity is not a member of the organization. That is common when the organization belongs to a personal Microsoft account. Do not run `az login` again. Use the same `AZURE_DEVOPS_EXT_PAT` route. Do not print or echo the token.

An `AZURE_DEVOPS_EXT_PAT` the user has already set is a credential for the `az repos pr` calls. A missing variable is not a prompt to invent one. Print the Azure DevOps fallback and these notes, and stop.
