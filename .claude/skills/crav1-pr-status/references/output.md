# crav1-pr-status: output

Read every run, from **Output** in `SKILL.md`. Plain words, short lines, no tables wider than five columns. Names as the host shows them; "you" for the signed-in user.

## Shape

```text
orders-api PR 42: Retry failed order writes (feat/orders-retry -> develop), you: reviewer, as of 2026-10-27
Mode: reviewer (you are Alex Doe; the PR is by Sam Lee).
Verdict: 2 waiting on you, 1 needs Robin K., 2 agreed (code checked: 1 done), 1 declined. Not ready to merge.

Waiting on you
1. src/orders/audit.py, general: 20 s timeouts accepted for the pilot; Sam asks what you think. Sam, 2026-10-20.
2. general: add a build policy to develop; Sam says feel free. Sam, 2026-10-20.

Needs someone else
3. general: merge order with feat/orders-queue (PR 40). Needs Robin K.; Sam asked you to check. 2026-10-20.

Agreed
4. src/orders/handler.py:238-244: fix the error path. Agreed 2026-10-20; changed in 3c9d2e1, check it.

Done
5. tests/test_retry_store.py:45: force the local emulator in the fixture. Done in 3c9d2e1.

Declined
6. src/orders/retry_store.py:401: random row key. Intended for traceability; a resend with the same id is a bug upstream. Accept or push back.

Flags
- Thread 112 (src/orders/handler.py:238): resolved, code unchanged since the request.

Spec and decision candidates
- Decision: drop "one shared database"; long term, one database per service.
Take them into a spec: `/crav1-add-to-spec pr42 candidates` (you type it; it only runs when you do).

Follow-ups (drafts for /crav1-ado-sync, not created)
- Restructure the src/orders/audit.py write path after the pilot (SQL last, or a separate per-minute trigger).

Order
- After PR 40 orders-api (feat/orders-queue): active. Source: thread 106, 2026-10-20.
- Merge order: PR 40, then PR 42.

Drafted replies (not posted)
- Thread 104 (src/orders/audit.py): "Agreed for the pilot. I'll add the restructure as a follow-up so it isn't lost."
- To Robin K. (not sent): "Hi Robin, Sam and I need the merge order of feat/orders-queue (PR 40) and PR 42. Plan: PR 40 into develop first. OK with you?"

Next for you
Now
- Post the drafted reply in thread 104 (in the note, under Replies as drafted, 2026-10-27).
- `/crav1-add-to-spec pr42 candidates`: 1 candidate.
- `/crav1-ado-sync`: the follow-up (restructure the audit write path).
After Robin K. answers the merge order (PR 40)
- If PR 40 first: wait for PR 40, then `/crav1-pr-status pr42 since last`.
- If PR 42 first: drop the Order line in the next run, then `/crav1-pr-status pr42 since last`.
Later
- When PR 40 is merged and Ready is yes: `/crav1-merge-pr pr42`.

Ready: no. 2 waiting on you; 1 needs Robin K.; 1 agreed, not done; after PR 40 (not merged).
PR record: `orders-api: docs/notes/2026-10/2026-10-08-pr-orders-api-71.md`
```

Local files, the `PR record:` line included, are named as a code span with the repo first: `` `orders-api: docs/notes/…` ``. Never as a Markdown link, `file://`, `vscode://` or an absolute path, in the shape or in closing prose. Web links only for things on the host (the pull request, a thread, a commit) (1.99.1).

## Next for you (1.100.0)

The last section before `Ready`, built from record lines, never from guesses:

- **Now**: steps nothing blocks, from `waiting on <you>` Points, drafted replies, open candidates and follow-ups. Commands follow the route order of `docs/reference/workflow.md`; that file is the source, so no `/crav1-help` call is needed.
- **After `<name>` answers `<point>`**: steps behind a `waiting on <name>` or `needs <name>` Point, one group per person. When the thread names the options, one `If <option>:` line per option with what it leads to; otherwise one line, and nothing made up.
- **Later**: steps behind an event: an `Order` pull request merged, `Ready: yes`, or a push.

Commands are named, never run. Empty groups are left out. `since last` shows steps that moved between groups.

Empty groups are left out, heading included. Within a group: oldest first, then by anchor.

## Verdict line

`Verdict: <counts>. <Ready | Not ready> to merge.` Counts in this order, zero counts left out: waiting on you, waiting on others (named when one), needs <name>, open, agreed (with `code checked: <n> done` or `code not checked`), done, declined. Nothing left: `Verdict: all <n> points done or settled. Ready to merge.`

## Merge readiness

`Ready: no` when any of these holds, each a reason:

- a point `open`, `waiting on …` or `needs …`;
- a point `agreed` but not `done`;
- a `resolved, code unchanged` flag;
- an `Order: after` pull request that is not merged;
- the host says draft, conflicts, or a required check or policy is failing (read-only, as `/crav1-merge-pr` reads them);
- `no code` was used and an agreed point has no commit check.

`declined` points the asker accepted, `done` points and follow-ups do not block. Otherwise `Ready: yes`. Merged or closed on the host: `Ready: merged` or `State: closed`, and no verdict. `/crav1-merge-pr` reads this line and stops on `no`.

## Drafted replies

First person, friendly, short, in the style of `/crav1-review-pr` **Comment style**. One per thread that waits on you, plus a message for each `needs <name>` you were asked to chase. Never posted, never sent. In the record they go in `## Replies as drafted, <date> (not posted)`, word for word, after the personal-data and secrets check.

## Errors

- Pull request not found, or the repo doesn't match: stop and name both.
- Host can't be read: say which call failed and what is shown from the record only, marked `from the record of <date>`.
