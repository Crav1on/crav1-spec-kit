# crav1-pr-status: output

Read every run, from **Output** in `SKILL.md`. Plain words, short lines, no tables wider than five columns. Names as the host shows them; "you" for the signed-in user.

## Order

Moved word for word from `SKILL.md` in 1.158.0; the rules are unchanged.

Print, in this order:

1. The heading: `<repo> PR <n>: <title> (<source> -> <target>), you: <mode>, as of <date>`.
2. **Verdict line**: counts by status, the points waiting on you first, for example `Verdict: 2 waiting on you, 1 needs Robin K., 3 agreed (code checked: 1 done), 1 declined.`
3. **Waiting on you**, oldest first, then the other points grouped by status, one line each: anchor, status, owner, the point in plain words, the evidence (who said what, when; the commit).
4. **Flags**: resolved while the code is unchanged, and done with the thread still active.
5. **Spec and decision candidates** (see **Hand-offs**).
6. **Follow-ups** (drafts).
7. **Order**: pull requests this one depends on or that depend on it, and the merge order.
8. **Drafted replies (not posted)**: one per thread that waits on you.
9. **Run ending** (1.177.0): `Run next:` with the label above the command, then `Waiting:` lines, then `Uncommitted:` when the note is not committed. See "Run ending" below.
10. **Merge readiness**: `Ready: yes | no | merged`, with the reasons.
11. `PR record: <repo>: <path>`, as a code span.

`since-last` prints only changes; see **Since last**.

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
Take them into a spec: `$crav1-add-to-spec pr42 candidates` (you type it; it only runs when you do).

Follow-ups (drafts for $crav1-ado-sync, not created)
- Restructure the src/orders/audit.py write path after the pilot (SQL last, or a separate per-minute trigger).

Order
- After PR 40 orders-api (feat/orders-queue): active. Source: thread 106, 2026-10-20.
- Merge order: PR 40, then PR 42.

Drafted replies (not posted)
- Thread 104 (src/orders/audit.py, https://dev.azure.com/contoso/Orders/_git/orders-api/pullrequest/71?discussionId=104): "Agreed for the pilot. I'll add the restructure as a follow-up so it isn't lost."
- To Robin K. (not sent): "Hi Robin, Sam and I need the merge order of feat/orders-queue (PR 40) and PR 42. Plan: PR 40 into develop first. OK with you?"

Run next:
Thread 104 is waiting on you.

Check PR 71 again after Robin K. answers the merge order:
`$crav1-pr-status pr71 since-last`

Waiting: Robin K., to answer the merge order.
Waiting: PR 40 to merge and Ready to say yes, before PR 42 can merge.
Uncommitted: 1 file; commit and push with `$crav1-finalize-commit commit-push`.

Ready: no. 2 waiting on you; 1 needs Robin K.; 1 agreed, not done; after PR 40 (not merged).
PR record: `orders-api: docs/notes/2026-10/2026-10-08-pr-orders-api-71.md`
```

Local files, the `PR record:` line included, are named as a code span with the repo first: `` `orders-api: docs/notes/…` ``. Never as a Markdown link, `file://`, `vscode://` or an absolute path, in the shape or in closing prose. Web links only for things on the host (the pull request, a thread, a commit) (1.99.1).

## Run ending (1.122.0, 1.177.0)

The last lines before `Ready`, as `crav1-docs/reference/run-ending.md` says. Build the old Now / After / Later groups in your head, from record lines, never from guesses, then print the shape and not the groups.

- **Now** (not printed as a heading): steps nothing blocks, from `waiting on <you>` Points, drafted replies, open candidates and follow-ups. Order them by `docs/reference/workflow.md`, then oldest, then anchor. That file is the source, so no help call is needed.
- `Run next:` is the first Now item: one short reason, then a label on its own line and the command alone in its code span on the next line. Now empty and the next step is to check again after someone answers (1.199.0): the label `Check PR 84 again after person A answers:` above `` `$crav1-pr-status pr84 since-last` ``, the one shape `crav1-docs/reference/run-ending.md` names. Nothing to check again either: `Run next: nothing needed now.`
- A Now item that is not first stays in the report section that already lists it (candidates, follow-ups, drafted replies). It is not a second Run next entry and not a `Waiting` line.
- **After `<name>` answers** and **Later** become `Waiting:` lines. One line per blocked step: the step, and who or what it waits on. When the thread names options, keep them in the Order section. One Waiting line for that person, not one line per option. Nothing made up. A Waiting line never carries a command (1.199.0). The signed-in user is `you`, never their name in the third person: `Waiting: you, to accept the settings answer in thread 195.`
- `Uncommitted:` when the PR note changed and is not committed, with the command in a code span (1.199.0): `` Uncommitted: 1 file; commit and push with `$crav1-finalize-commit commit-push`. `` Do not put the commit command in Run next.

Commands are named, never run. `since-last` uses the same shape for steps that moved. Nothing new: `Run next: nothing needed now.` Never a `Next:` line (1.177.0).

## Verdict line

`Verdict: <counts>. <Ready | Not ready> to merge.` Counts in this order, zero counts left out: waiting on you, waiting on others (named when one), needs <name>, open, agreed (with `code checked: <n> done` or `code not checked`), done, answered, declined. Nothing left: `Verdict: all <n> points done or settled. Ready to merge.`

## Merge readiness

`Ready: no` when any of these holds, each a reason:

- a point `open`, `waiting on …` or `needs …`;
- a point `agreed` but not `done`;
- a `resolved, code unchanged` flag;
- an `Order: after` pull request that is not merged;
- the host says draft, conflicts, or a required check or policy is failing (read-only, as `$crav1-merge-pr` reads them);
- `no-code` was used and an agreed point has no commit check.

`declined` points the asker accepted, `answered` and `done` points and follow-ups do not block (1.199.0: say `answered; no code change`, never `done host`, for an answered question). Otherwise `Ready: yes`. Merged or closed on the host: `Ready: merged` or `State: closed`, and no verdict. `$crav1-merge-pr` reads this line and stops on `no`.

## Drafted replies

First person, friendly, short, in the style of `$crav1-review-pr` **Comment style**. One per thread that waits on you, plus a message for each `needs <name>` you were asked to chase. Each reply carries its thread link (`…/pullrequest/<n>?discussionId=<id>`; `ado_threads.py reply --pr <n> --thread <id> --file <draft file>` prints it as `link`) so it can be pasted in one click. A reply is posted only through its thread's reply card in [offers.md](offers.md) (1.199.0), and its words match what that card does. Messages to other people are never sent. In the record they go in `## Replies as drafted, <date> (not posted)`, word for word, after the personal-data and secrets check.

## Errors

- Pull request not found, or the repo doesn't match: stop and name both.
- Host can't be read: say which call failed and what is shown from the record only, marked `from the record of <date>`.
