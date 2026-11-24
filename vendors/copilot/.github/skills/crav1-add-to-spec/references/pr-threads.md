# Reading a pull request's threads (1.97.0)

The one place for how the kit reads a pull request's comment threads, pushes and commits on each host. `/crav1-pr-status`, `/crav1-review-pr` (re-review and the posted-comment record) and `/crav1-add-to-spec` (`pr<n> all`) follow it. Read-only unless a step below says it changes a thread, and that step runs only after the user's yes for that one thread.

## Rules for every host

- Never log in, never start a device-code or browser sign-in, never create, print or echo a token. An `AZURE_DEVOPS_EXT_PAT` or `GH_TOKEN` the user already set is used as it is.
- Signed out or no CLI: follow **Signed out** in [pr-comments.md](pr-comments.md).
- Bot and system threads are not points: votes, pushes, policy and CI messages, reviewer changes, merge attempts. They are still read for **Pushes after a comment**.
- A thread's status on the host is a hint, never the verdict. Whether a point is done is decided from the code (`/crav1-pr-status` `references/classify.md`).
- Secrets in a comment are always redacted, by kind, before anything is written ([sources.md](sources.md)).

## Azure DevOps

`az repos pr` has no thread command. There is no `az repos pr thread list`. Azure DevOps pull requests are read and changed only through `scripts/ado_threads.py` in `crav1-review-pr` (1.193.0). Never use `az rest`, `az devops invoke` by hand, `curl`, or any call with a token you fetched yourself: on Windows a redirect writes the console code page and accented names come back broken. The script decodes UTF-8 first and its JSON keeps accented characters intact. Organization, project and repository come from the code repo's git remote (`--code-repo`); `--org`, `--project` and `--repo` override. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says.

Read the script's output as it is: `list --brief` for a summary, never ad hoc parsing of the full JSON. A thread's key is always `thread` (1.199.0).

```text
# threads, with thread and comment dates (published, updated) and status
ado_threads.py list --pr <n>
# one line per thread: thread id, status, file:line, last author, last 200 characters (1.199.0)
ado_threads.py list --pr <n> --brief
# reply inside thread <t>, then set it fixed; marks the drafted reply posted in the PR note (1.199.0)
ado_threads.py reply --pr <n> --thread <t> --file <reply file> --status fixed --note <PR note> --yes
# title, state, description, created date and reviewer votes
ado_threads.py pr --pr <n>
# pushes (iterations): id, date, head commit
ado_threads.py iterations --pr <n>
# files changed in push <i> compared with push <j>
ado_threads.py changes --pr <n> --iteration <i> --compare-to <j>
# what changed since your Read line and the description saved in the PR note
ado_threads.py since-last --pr <n> --note <PR note> --who <your name>
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

**Who is signed in.** `az account show --query "user.name" --output tsv` gives the sign-in name; compare it, case ignored, with the pull request's `createdBy.uniqueName` and each comment's `author.uniqueName`. With a PAT and no `az login`, use `git config user.email`, then `git config user.name` against `displayName`.

**Change a thread's status** (only after the user's yes for that one thread; never in a batch):

```text
ado_threads.py set-status --pr <n> --thread <id> --status <status> --yes
```

Without `--yes` it only previews. With it, the script sets the status, reads the thread again and reports the status the host now shows (`ok` is false when it differs). The status is one of `fixed`, `wontFix`, `closed`, `byDesign`, `active`, `pending`. No comment is added by this call.

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
