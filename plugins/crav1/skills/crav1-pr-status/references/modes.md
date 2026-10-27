# crav1-pr-status: modes

Read every run, from **Mode** in `SKILL.md`.

## Pick the mode

1. A choice word in this turn (`as reviewer`, `as author`) wins. Say `Mode: <mode> (as asked).`
2. Else compare the signed-in user with the pull request's author, as `crav1-add-to-spec` `references/pr-threads.md` **Who is signed in** says:
   - GitHub: `gh api user -q .login` against `author.login`.
   - Azure DevOps: `az account show --query user.name` against `createdBy.uniqueName`, case ignored. A PAT run (`AZURE_DEVOPS_EXT_PAT`) has no `user.name`: use git `user.email`, then `user.name` against `createdBy.uniqueName` and `createdBy.displayName`.
   - Same person: **author**. Otherwise: **reviewer**. Say `Mode: <mode> (you are <name>; the PR is by <author>).`
3. The name can't be read (signed out, pasted threads): guess without asking. **Reviewer** when a comment in the threads is by the git `user.name`, else **author** when the source branch's commits are by the git `user.email`, else **reviewer**. Say `Mode: <mode> (guessed; say as <other> to switch).`

Never ask for the mode. It does not use the budget.

## What changes by mode

The points and their statuses are the same in both modes. The mode decides whose side "you" is on, which points come first and what is drafted.

| | Reviewer mode | Author mode |
| --- | --- | --- |
| You | a reviewer (or anyone who is not the author) | the person who opened the pull request |
| Waiting on you | answers the author asked you for, decisions handed to you, a declined point you must accept or push back on, a `needs <name>` you were asked to chase | every reviewer request with no reply or no commit yet, every question to you, every `agreed` point not yet `done` |
| Shown next | `agreed` points, to check in the code | points waiting on reviewers |
| Drafted replies | your answer, your acceptance or push-back, the message to the third person | your answer, `Done in <sha>` for a `done` point, a reason for a `declined` point |
| Status changes offered | resolve threads you opened whose point is `done` or settled | reactivate a thread resolved while the code is unchanged; on GitHub, resolve a thread you answered (the host decides who may) |
| Merge readiness | `no` while a point you raised is `open` or `agreed` | `no` while any reviewer point is `open`, `agreed` or `waiting on` you |

Owners are named as the host shows them. "You" is used in the chat; the record holds the name.
