# Reading a pull request's threads (1.97.0)

The one place for how the kit reads a pull request's comment threads, pushes and commits on each host. `/crav1-pr-status`, `/crav1-review-pr` (re-review and the posted-comment record) and `/crav1-add-to-spec` (`pr<n> all`) follow it. Read-only unless a step below says it changes a thread, and that step runs only after the user's yes for that one thread.

## Rules for every host

- Never log in, never start a device-code or browser sign-in, never create, print or echo a token. An `AZURE_DEVOPS_EXT_PAT` or `GH_TOKEN` the user already set is used as it is.
- Signed out or no CLI: follow **Signed out** in [pr-comments.md](pr-comments.md).
- Bot and system threads are not points: votes, pushes, policy and CI messages, reviewer changes, merge attempts. They are still read for **Pushes after a comment**.
- A thread's status on the host is a hint, never the verdict. Whether a point is done is decided from the code (`/crav1-pr-status` `references/classify.md`).
- Secrets in a comment are always redacted, by kind, before anything is written ([sources.md](sources.md)).

## Azure DevOps

`az repos pr` has no thread command. There is no `az repos pr thread list`. Threads, pushes and iterations are read through the REST API, with `az devops invoke` (preferred) or `az rest`. Pass `--org <org-url>` and `--detect false` where the command takes them. Docs: [Pull Request Threads](https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-request-threads?view=azure-devops-rest-7.1), [Pull Request Iterations](https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-request-iterations?view=azure-devops-rest-7.1), [Iteration Changes](https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-request-iteration-changes?view=azure-devops-rest-7.1), [`az repos pr`](https://learn.microsoft.com/en-us/cli/azure/repos/pr).

```text
# threads, with their comments
az devops invoke --org <org-url> --area git --resource pullRequestThreads --route-parameters project=<project> repositoryId=<repo> pullRequestId=<n> --api-version 7.1 --http-method GET --output json
# pushes (iterations), with their commits
az devops invoke --org <org-url> --area git --resource pullRequestIterations --route-parameters project=<project> repositoryId=<repo> pullRequestId=<n> --query-parameters includeCommits=true --api-version 7.1 --http-method GET --output json
# files changed in push <i> compared with push <j>
az devops invoke --org <org-url> --area git --resource pullRequestIterationChanges --route-parameters project=<project> repositoryId=<repo> pullRequestId=<n> iterationId=<i> --query-parameters '$compareTo=<j>' --api-version 7.1 --http-method GET --output json
# the same threads through az rest (the resource id is Azure DevOps itself)
az rest --method get --resource 499b84ac-1321-427f-aa17-267ca6975798 --url "https://dev.azure.com/<org>/<project>/_apis/git/repositories/<repo>/pullRequests/<n>/threads?api-version=7.1"
```

What each field gives:

| Need | Where |
| --- | --- |
| Thread status | `status`: `active`, `pending`, `fixed`, `wontFix`, `closed`, `byDesign`, `unknown`. `active` and `pending` are open; the rest are resolved |
| Where it points | `threadContext.filePath`, `rightFileStart.line`–`rightFileEnd.line` (the new side), `leftFileStart`/`leftFileEnd` (the old side). No `threadContext`: a general comment |
| Which push it was made on | `pullRequestThreadContext.iterationContext` (`firstComparingIteration`, `secondComparingIteration`), `changeTrackingId` |
| Replies | each comment's `id`, `parentCommentId` (0 is the first comment), `author.displayName`, `author.uniqueName`, `publishedDate`, `lastContentUpdatedDate`, `isDeleted` |
| System thread | a comment with `commentType` `system`, or a thread whose `properties.CodeReviewThreadType` is set (`RefUpdate`, `VoteUpdate`, `ReviewersUpdate`, `MergeAttempt`, …) |
| Pushes | iterations: `id`, `createdDate`, `sourceRefCommit.commitId`, `commits`. A `RefUpdate` thread also names `CodeReviewRefNewHeadCommit` and `CodeReviewRefNewCommits` |
| Files a push changed | iteration changes: `changeEntries[].item.path`, `changeTrackingId` |

`$iteration=<i>` (with `$baseIteration=<j>`) on the threads call maps each thread's lines to that push, so a line can be compared with today's code.

**Who is signed in.** `az account show --query user.name --output tsv` gives the sign-in name; compare it, case ignored, with the pull request's `createdBy.uniqueName` and each comment's `author.uniqueName`. With a PAT and no `az login`, use `git config user.email`, then `git config user.name` against `displayName`.

**Change a thread's status** (only after the user's yes for that one thread; never in a batch):

```text
az devops invoke --org <org-url> --area git --resource pullRequestThreads --route-parameters project=<project> repositoryId=<repo> pullRequestId=<n> threadId=<id> --api-version 7.1 --http-method PATCH --in-file <file with {"status": "<status>"}>
```

Write the one-line JSON file in a temp folder, delete it after the call, then read the thread again and report the status the host now shows. The status is one of `fixed`, `wontFix`, `closed`, `byDesign`, `active`, `pending`. No comment is added by this call.

## GitHub

```text
gh pr view <n-or-url> --json number,url,title,author,createdAt,state,headRefName,headRefOid,baseRefName,comments,reviews,commits
gh api --paginate repos/<owner>/<repo>/pulls/<n>/comments
gh api graphql -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){pullRequest(number:$n){reviewThreads(first:100){nodes{id isResolved isOutdated path line originalLine startLine diffSide resolvedBy{login} comments(first:100){nodes{databaseId author{login} body createdAt commit{oid} originalCommit{oid}}}}}}}}' -f o=<owner> -f r=<repo> -F n=<n>
gh api user --jq .login
```

Docs: [review comments](https://docs.github.com/en/rest/pulls/comments), [PullRequestReviewThread](https://docs.github.com/en/graphql/reference/objects#pullrequestreviewthread).

| Need | Where |
| --- | --- |
| Thread status | `isResolved` (resolved or open) and `isOutdated` (the lines changed since). GitHub has no fixed, won't fix or by design |
| Where it points | `path`, `line` (today), `originalLine`, `startLine`; REST `line`, `original_line`, `commit_id`, `original_commit_id` |
| Replies | REST `in_reply_to_id`; GraphQL `comments` in order |
| General comments | `gh pr view --json comments` and the bodies in `reviews` |
| Pushes | `commits` with their dates; `gh api repos/<owner>/<repo>/compare/<original_commit_id>...<head>` for one file since the comment |
| Who is signed in | `gh api user --jq .login`, compared with `author.login` |

**Resolve a thread** (only after the user's yes for that one thread): `gh api graphql -f query='mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{isResolved}}}' -f id=<thread node id>`. Reopen is `unresolveReviewThread`. GitHub can only resolve or reopen.

## Pushes after a comment

A point's code check uses the pushes after the reply that settled it: the iterations (Azure DevOps) or commits (GitHub) created after that reply's date. A push that changed the point's file is checked against the point's lines in today's diff. No later push touched the file: the point's code did not change since the reply.
