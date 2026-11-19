# crav1-review-pr: posting

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Post it

After the paste-ready block, offer to post. One question. Use the questions tool when it is available. Say it posts under the user's own account as one comment, and name the vote it will set. Options: **post**, **I'll post it myself**, or **do not post** (1.67.0). Nothing posts without that yes. **I'll post it myself** ends the run with `When it's posted, say "posted" here, or run /crav1-review-pr <repo> <n> comment-posted.`

On yes (1.66.0):

1. Post the block as **one comment**. No inline threads. GitHub: one review whose body is the block, submitted with the vote (`gh api repos/<owner>/<repo>/pulls/<n>/reviews` with `body` and `event`). Azure DevOps: one pull request thread whose comment is the block, then the vote. Post with `scripts/ado_threads.py post --pr <n> --file <block file> --yes` (1.172.0): it always opens a new top-level thread and reads az output safely on Windows.
2. The vote follows the verdict: Changes needed is **Request changes** (GitHub) or **Wait for author** (Azure DevOps); Approve with comments is **Comment** or **Approve with suggestions**; Approve is **Approve**. Never Reject.
3. On a re-review, post the new block as a **new top-level thread** (Azure DevOps: `pullRequestThreads` POST with `parentCommentId` 0, the same as the open-pr comment) or as a new review (GitHub), so it shows at the top of the pull request (1.171.0). Never post a review round as a reply in an earlier thread: a resolved thread collapses and the reply is hard to find. Reply in an earlier thread only to answer a question asked in that thread.
4. Follow-ups are never posted. Only the review block is posted: never the kit record, the read-only context section or the context file (1.113.0).
5. Check the post with `scripts/ado_threads.py compare --pr <n> --draft <block file>` on Azure DevOps (1.172.0); `same: true` means the posted text matches. Save the posted text at once (1.67.0): the body the host returns, its URL and date, under `## Comment as posted, <YYYY-MM-DD> (by <name>)` with the source line `Posted from this review on the user's yes: <comment URL>. …` (`references/comment-as-posted.md`). A failed post saves nothing.
6. On GitHub, when the signed-in user is the pull request's author, the host does not allow Approve or Request changes: post with event `COMMENT` and say `GitHub doesn't allow a vote on your own PR; posted as a comment.`
7. Never resolve a thread. On a re-review, after posting, offer to resolve existing threads whose points are now fixed. Resolve only on that yes.

When a post fails, say what failed and what already posted. Do not retry by another route.

## Azure DevOps threads (1.172.0)

`scripts/ado_threads.py` is the one way to read and post threads, and since 1.193.0 also to read votes, pushes and the description and to set a thread's status. Do not hand-roll `az devops invoke` with a redirect to a file, `az rest`, or a token request: on Windows that writes the console code page and the JSON fails to load. Its output is always UTF-8 JSON with accented characters intact.

- `ado_threads.py pr --pr <n>`: title, state, description, created date and reviewer votes.
- `ado_threads.py iterations --pr <n>`: pushes with their dates and head commits.
- `ado_threads.py set-status --pr <n> --thread <id> --status <status> --yes`: one thread, after the user's yes, read back from the host.

- `ado_threads.py list --pr <n>` prints every thread with its status, file and comments.
- `ado_threads.py compare --pr <n> --draft <file>` says whether a posted comment matches the draft (line endings and trailing spaces ignored).
- `ado_threads.py post --pr <n> --file <file> --yes` posts a new top-level thread. Without `--yes` it only previews.
- Organization, project and repository come from the code repo's git remote (`--code-repo <path>`, default the current folder) since 1.182.0, so a post no longer returns 404 without them. `--org`, `--project` and `--repo` still override.

Add `--project`, `--repo` and `--org` when az has no defaults. It reads az's stdout as bytes and decodes UTF-8, then UTF-8 with a BOM, then cp1252.
