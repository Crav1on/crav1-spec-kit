# crav1-pr-status: points and statuses

Read every run, from **Points and statuses** in `SKILL.md`. Record format: `crav1-add-to-spec` `references/pr-record.md`.

## Split threads into points

- A thread starts as one point: its first comment's request or question, at the thread's anchor (`path:line`, `path:start-end`, or `general` for a thread with no file).
- Split when one comment asks or answers several separate things: a numbered or bulleted list, or separate paragraphs about different lines or topics. A reply that answers points from several threads (for example one long general reply) is matched to each point by its words, file names and line numbers; each matched part is that point's reply.
- A point already in the record keeps its line: match by `thread <id>`, then by anchor and words. Never make a second Point for it.
- A record Point with no thread (from `/crav1-review-pr`, or `migrated`) is matched to a thread the same way; no match keeps it as it is, with `no thread` shown in the chat.

## Read the replies

For each point, read every reply in order. The **last** relevant message decides, unless a later push settles it.

| The last word on the point | Status |
| --- | --- |
| The other side says it will change it, "good point", "will fix", "agreed" | `agreed` |
| A commit after that reply touched the anchor (see **Verify in code**) | `done <sha>` |
| The other side says no, keeps it, "on purpose", "intended", with or without a reason | `declined` (keep the reason in the text) |
| A question to a named person, or "let me know what you think", "over to you" | `waiting on <that person>` |
| "Ask X", "check with X", "X has to decide", and X is not in the thread | `needs <X>` |
| No reply, a reply that doesn't settle it, or two people disagreeing | `open` |

`waiting on` names whoever must act next. A request with no reply is `waiting on <author>` in reviewer mode and `waiting on you` in author mode. A `declined` point the asker has not answered stays `declined`; reviewer mode lists it under **Waiting on you** with "accept or push back".

Never guess. When a reply is unclear, use `open` and quote the words that left it unclear. Keep the point's text plain and short; keep the reason with `declined`.

## Verify in code

Skip on `no code`; then a point that would need it says `agreed (code not checked)`.

1. The pushes (Azure DevOps iterations, GitHub commits) newer than the reply that agreed. For each, the files it changed (Azure DevOps iteration changes with `$compareTo`; GitHub `gh api repos/<o>/<r>/commits/<sha>`).
2. A push touched the anchor's file: diff that file between the commit the comment was made on (Azure DevOps `threadContext` with the iteration of the comment, GitHub `original_commit_id`) and the head, and check the anchored lines (moved lines are followed by their text, not only their number).
3. The lines changed in the asked direction: `done <short sha>`, the newest commit that changed them. Changed but not clearly as asked: stay `agreed`, say `changed in <sha>, check it`. Untouched: `agreed`.
4. A `general` point is `done` only when a commit message or the reply names it and the change is in the diff.

The code is read as `/crav1-review-pr` reads it: a sibling checkout of the code repo, else the two branches fetched after its fetch question. When neither is possible, say `code not checked` and do not use `done`.

## Flags

- `resolved, code unchanged`: host thread resolved (Azure DevOps `fixed`, `closed`, `wontFix`, `byDesign`; GitHub `isResolved`), status not `done` or `declined`, no push after the request touching the anchor. Azure DevOps `wontFix` or `byDesign` with a `declined` reply is not flagged.
- `done, thread still active`: status `done`, host thread `active` or `pending`, or GitHub not resolved.
- `outdated` (GitHub `isOutdated`, or Azure DevOps anchor lines gone): the anchor moved. Not a status; the point is checked at its text.

## Candidates

- **To spec or decision:** a point whose settled answer says how the system works or must work, accepts a limit for now, picks between real options, or drops a goal. `to decision` when real options were weighed (the ADR rule of `crav1-add-to-spec`); else `to spec`. A Point already `in spec <slug>` is not offered again.
- **Follow-up:** "later", "after <milestone>", "separate PR", "out of scope", or an accepted limit with a later fix named.
- **Order:** a thread or the description says this pull request must merge before or after another (by number, branch or URL). The other pull request's state is read with the same host tool; one `Order` line each, with the source.
