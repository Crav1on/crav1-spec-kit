# From a pull request's threads: where it stands

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when a pull request has comments and replies, and you want to know what is done, what is left and why, and what you owe. New in 1.97.0. A kit script this command runs uses the interpreter in [Running a kit script](reference/running-scripts.md).

This is cross-cutting. It is not a lane and not a bot. It is the same command family as [`$crav1-review-pr`](from-review-pr.md) and `$crav1-merge-pr`. A review judges the code; `$crav1-pr-status` tracks the conversation about it. It never posts, votes or merges.

## First prompt

```text
$crav1-pr-status pr42

Where does this pull request stand, and what do I owe?
```

A number, `#42`, `pr orders-api 42` or the URL. No pull request named and your branch has exactly one open: it uses that one and says so. Otherwise it asks which one.

## Choice words

| Word | Means |
| --- | --- |
| `as-reviewer` | Reviewer mode, whoever opened the pull request |
| `as-author` | Author mode |
| `since-last` | Only what changed since your last run |
| `no-code` | Threads only; no diff or commit check, so nothing is marked done |

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Read | — | Reads every thread and comment, the pushes and their commits, the files each push changed, and who is signed in, read-only (`crav1-add-to-spec` `references/pr-threads.md`). There is no `az repos pr thread list`; Azure DevOps is read with the `crav1-review-pr` Azure DevOps script, never with `az rest` or a hand-made token call (1.193.0). Never logs in |
| Mode | — | You opened the pull request: author mode. Otherwise reviewer mode. Unclear sign-in: it guesses and tells you how to switch. It never asks |
| Points | — | Reads the description too: since 1.176.0 its task lines name the tasks the pull request carries, and the merge order comes from the ready check's merge list and `build-progress/`, the questions from the spec's open questions (or it says plainly that the kit has none recorded). An older description with Merge order, Questions for reviewers and Not in this PR sections (1.98.0) is still read: `Order` lines, Points tagged `asked; from description <date>`, and follow-ups. Splits threads into points. Each gets one status: `done <sha>` (a commit after the request changed the lines), `agreed`, `declined` (with the reason), `open`, `waiting on <name>`, or `needs <name>` for someone outside the thread. No commit, no `done` |
| Flags | Read them | A thread resolved while the code is unchanged, and a done point whose thread is still active |
| Output | Read it | Verdict line with the points waiting on you first, then the points by status, flags, spec and decision candidates, follow-ups (drafts), merge order, drafted replies, `Next for you` (Now, After <name> answers, Later; 1.100.0), the merge-readiness line and `PR record: <path>` |
| Offers | One prompt | One question per thread status change (each its own yes) and one for the follow-ups. Spec candidates are not asked: the output names `$crav1-add-to-spec pr<n> candidates` for you to type (1.100.0). Signed out or headless: listed as text for the next run |
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

One pull request, one PR note, one record. `$crav1-pr-status`, `$crav1-review-pr`, `$crav1-add-to-spec` and `$crav1-merge-pr` all read and write the same `## PR record` section, one sorted line per item, so two people's runs rarely conflict:

```text
- Order: after PR 40 orders-api (feat/orders-queue) | merge order asked in thread 106, reply 2026-10-20 | 2026-10-27
- Point: general | needs Robin K. | Alex Doe | thread 106 | Merge order of feat/orders-queue
- Point: tests/test_retry_store.py:45 | done 3c9d2e1 | Sam Lee | thread 98; host fixed | Fixture could clean live tables
- Read: Alex Doe | 7b41a0c, push 6, newest comment 2026-10-26T15:03Z | 2026-10-27

A `Read: sweep` line on the same record is the watermark from `$crav1-update-specs-from-changes-and-prs`. It is not a person. `since-last` does not use it.
- Ready: no | 1 needs Robin K.; after PR 40 (not merged) | 2026-10-27 by pr-status
- State: active | 2026-10-27
```

`$crav1-merge-pr` reads the `Ready` line and stops on `no` unless you add `anyway`; host checks still apply. A project from before 1.97.0 runs `$crav1-add-to-spec migrate-formats` once ([install](install.md)).

A point that asked for a host setting, such as a required build on `develop`, becomes `done host` when the setting reads back live in this run (1.115.0). No commit is needed, and the skill never applies anything; when it is not set yet it names `$crav1-host-setup`.

## Shared pull-request steps (1.158.0)

`$crav1-pr-status` reads the pull request the same way as open-pr, merge-pr and review-pr, as [Shared pull-request steps](reference/pr-common.md) says. With no pull request named, `scripts/pr_common.py find --branch <current-branch>` looks for the one open pull request on the current branch; more than one, and it asks which. The output and the record are unchanged.

## What does not get written

No code, spec, plan or task edit. No reply posted, no vote, no merge. Replies are drafts. A thread status changes only on that thread's yes. Follow-ups are drafts; no work item is created. The only file it writes is the PR note in the specs repo, not committed.

## After

Since 1.177.1 a bare number is resolved with `--root` set to the specs repo root, and a record that names the number without its host is asked about instead of read on this checkout's remote.

The run ends as [How a run ends](reference/run-ending.md) says. Since 1.177.0 that is Run next, never a `Next:` line: a plain label, then the command alone in its code span, for the first thing nothing blocks. A bare number such as `82` is looked up in the kit's records before this checkout's remote, as [Shared pull-request steps](reference/pr-common.md) says. A step that waits on a person or another pull request is a `Waiting:` line. Candidates stay in the report; `$crav1-pr-status` names `$crav1-add-to-spec` when you take them. Follow-ups stay drafts for `$crav1-ado-sync`. Merge is `$crav1-merge-pr` only after `Ready: yes`.

Reference page: [pr-status](reference/skills/crav1-pr-status.md)

## 1.198.0 changes

`$crav1-pr-status` passes `--code-repo` to the threads script's since-last check, and the script finds the Azure DevOps organization in `docs/system/repos.md` when the remote names none. Every `--query` value is quoted for Windows. `$crav1-merge-pr` fetches the specs repo before it reads the PR note, and `$crav1-open-pr` offers Open PR only when the head is already pushed.

## 1.199.0 changes

When your drafted reply and a status change are for the same thread, `$crav1-pr-status` asks one card, `Post your reply in thread 195 and set it to fixed?`, and on yes runs `ado_threads.py reply --pr <n> --thread <id> --file <draft file> --status fixed --yes`, which replies inside the thread, sets it fixed and marks the draft posted in the PR note. Drafted replies carry their thread link, and their words match what the card does. A question that was answered and accepted is `answered` in the record, said as `answered; no code change`. The card comes before the ending, which is printed once; waiting on someone ends with a label and `$crav1-pr-status <pr> since-last` alone in its code span, and you are `you`. The run reads threads with `list --brief`, runs merged-since-sync once and the ready check only when the PR closes a task. `pr_common.py checks --ref <n>` passes the Azure DevOps organization to both `az` calls.
