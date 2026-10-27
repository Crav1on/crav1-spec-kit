# From a pull request's threads: where it stands

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when a pull request has comments and replies, and you want to know what is done, what is left and why, and what you owe. New in 1.97.0.

This is cross-cutting. It is not a lane and not a bot. It is the same command family as [`/crav1-review-pr`](from-review-pr.md) and `/crav1-merge-pr`. A review judges the code; `/crav1-pr-status` tracks the conversation about it. It never posts, votes or merges.

## First prompt

```text
/crav1-pr-status pr42

Where does this pull request stand, and what do I owe?
```

A number, `#42`, `pr orders-api 42` or the URL. No pull request named and your branch has exactly one open: it uses that one and says so. Otherwise it asks which one.

## Choice words

| Word | Means |
| --- | --- |
| `as reviewer` | Reviewer mode, whoever opened the pull request |
| `as author` | Author mode |
| `since last` | Only what changed since your last run |
| `no code` | Threads only; no diff or commit check, so nothing is marked done |

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Read | — | Reads every thread and comment, the pushes and their commits, the files each push changed, and who is signed in, read-only (`crav1-add-to-spec` `references/pr-threads.md`). There is no `az repos pr thread list`; Azure DevOps is read through its REST API with `az devops invoke` or `az rest`. Never logs in |
| Mode | — | You opened the pull request: author mode. Otherwise reviewer mode. Unclear sign-in: it guesses and tells you how to switch. It never asks |
| Points | — | Splits threads into points. Each gets one status: `done <sha>` (a commit after the request changed the lines), `agreed`, `declined` (with the reason), `open`, `waiting on <name>`, or `needs <name>` for someone outside the thread. No commit, no `done` |
| Flags | Read them | A thread resolved while the code is unchanged, and a done point whose thread is still active |
| Output | Read it | Verdict line with the points waiting on you first, then the points by status, flags, spec and decision candidates, follow-ups (drafts), merge order, drafted replies, the merge-readiness line and `PR record: <path>` |
| Offers | One prompt | One question per thread status change (each its own yes), one for the spec candidates, one for the follow-ups. Signed out or headless: listed as text for the next run |
| Record | — | Writes the PR note's `## PR record` in the specs repo; not committed |

## Example (made-up names)

```text
orders-api PR 42: Retry failed order writes (feat/orders-retry -> develop), you: reviewer, as of 2026-10-27
Verdict: 1 waiting on you, 1 needs Robin K., 1 agreed (code checked: 1 done), 1 declined. Not ready to merge.

Waiting on you
1. src/orders/audit.py: 20 s timeouts accepted for the pilot; Sam asks what you think. Sam, 2026-10-20.

Needs someone else
2. general: merge order with feat/orders-queue (PR 40). Needs Robin K. 2026-10-20.

Done
3. tests/test_retry_store.py:45: force the local emulator in the fixture. Done in 3c9d2e1.

Declined
4. src/orders/retry_store.py:401: random row key. Intended for traceability. Accept or push back.

Ready: no. 1 waiting on you; 1 needs Robin K.; after PR 40 (not merged).
PR record: docs/notes/2026-10/2026-10-17-pr-orders-api-42.md
```

## The shared PR record

One pull request, one PR note, one record. `/crav1-pr-status`, `/crav1-review-pr`, `/crav1-add-to-spec` and `/crav1-merge-pr` all read and write the same `## PR record` section, one sorted line per item, so two people's runs rarely conflict:

```text
- Order: after PR 40 orders-api (feat/orders-queue) | merge order asked in thread 106, reply 2026-10-20 | 2026-10-27
- Point: general | needs Robin K. | Alex Doe | thread 106 | Merge order of feat/orders-queue
- Point: tests/test_retry_store.py:45 | done 3c9d2e1 | Sam Lee | thread 98; host fixed | Fixture could clean live tables
- Read: Alex Doe | 7b41a0c, push 6, newest comment 2026-10-26T15:03Z | 2026-10-27
- Ready: no | 1 needs Robin K.; after PR 40 (not merged) | 2026-10-27 by pr-status
- State: active | 2026-10-27
```

`/crav1-merge-pr` reads the `Ready` line and stops on `no` unless you add `anyway`; host checks still apply. A project from before 1.97.0 runs `/crav1-add-to-spec migrate formats` once ([install](install.md)).

## What does not get written

No code, spec, plan or task edit. No reply posted, no vote, no merge. Replies are drafts. A thread status changes only on that thread's yes. Follow-ups are drafts; no work item is created. The only file it writes is the PR note in the specs repo, not committed.

## After

- Spec or decision candidates: `/crav1-add-to-spec`, on your yes in the run.
- Follow-ups: `/crav1-ado-sync`.
- Review the code again: `/crav1-review-pr`.
- Merge when `Ready: yes`: `/crav1-merge-pr`.

Reference page: [pr-status](reference/skills/crav1-pr-status.md)
