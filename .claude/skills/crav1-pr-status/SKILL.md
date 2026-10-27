---
name: crav1-pr-status
description: >-
  Show where one open pull request stands: every point raised in its
  threads, what is done in the code, what is agreed, declined, still open,
  waiting on someone or needing a third person, and who owes the next
  step. Reviewer or author mode by who opened the PR. Starts with a
  verdict line, the points waiting on you first. Flags threads resolved
  while the code is unchanged. Shows PR dependencies and merge order, and
  a merge-readiness line that /crav1-merge-pr reads. Later runs can show
  only what changed (since last). Writes the shared PR record in the PR
  note in the specs repo's docs/notes/YYYY-MM/. Drafts replies, never
  posts. Offers thread status changes one thread at a time, spec or
  decision points to /crav1-add-to-spec, and follow-up work items as
  drafts for /crav1-ado-sync. Cross-cutting. Read-only toward the code
  and the host except a thread status the user said yes to.
disable-model-invocation: true
icon: list-checks
color: orange
---

# PR status

Say where **one** named open pull request stands: what is done, what is left and why, and what each person owes. Then stop.

Command: `/crav1-pr-status`.

This is cross-cutting. It is not a lane and not a bot. It is the same command family as `/crav1-review-pr` and `/crav1-merge-pr`. A review judges the code; this skill tracks the conversation about it.

Run it when this turn names a pull request (number or URL) or clearly asks for its status. No pull request named and the current branch has exactly one open pull request: use it and say so. Otherwise ask which one (a prompt for a value the user left out; outside the budget). Do not pick the newest.

## Choice words

Exact words for bots and scripted runs. There are no `--flags`.

- Which pull request: `pr<n>`, `pr <n>`, `#<n>`, `pr <repo> <n>`, or the URL, parsed as `crav1-add-to-spec` `references/scope.md` says.
- Mode: `as reviewer`, `as author`. They override the mode the run would pick.
- `since last`: show only what changed since your last run.
- `no code`: threads only; no diff and no commit check. Points that would need the code to say `done` stay `agreed` and the output says `code not checked`.

A choice word answers its question; the run does not ask it.

## Asking (budget 1)

At most **one** prompt per run, the closing one included, as `crav1.mdc` says. A prompt may hold several questions, each with at most 4 options, the recommended one first.

- **Signed out** (no `gh` or `az` session that can read the pull request): the one prompt is the signed-out question of `crav1-add-to-spec` `references/pr-comments.md` **Signed out**. Then the offers at the end are listed as text, not asked; the next run asks them.
- Otherwise the one prompt is the closing prompt of `references/offers.md`, only when there is something to offer.
- Headless or bot runs ask nothing: the offers are listed as text, and the record is written.

## Read

Resolve the pull request, its host, the code repo and the specs repo as `/crav1-review-pr` does (**Specs repo and code repo**). Read everything as `crav1-add-to-spec` `references/pr-threads.md` says (drop-in: `.claude/skills/crav1-add-to-spec/references/pr-threads.md`; plugin: sibling `skills/crav1-add-to-spec/references/pr-threads.md`): the threads with every comment, the pushes with their commits, the files each push changed, and who is signed in. Never log in. Never print a token. Skip system and bot threads.

Then read the PR note and its `## PR record`, as `crav1-add-to-spec` `references/pr-record.md` says (drop-in: `.claude/skills/crav1-add-to-spec/references/pr-record.md`; plugin: sibling `skills/crav1-add-to-spec/references/pr-record.md`). No PR note yet: write it as `/crav1-review-pr` **PR note** does. An old follow-ups note is read as `migrated` Points; say once to run `/crav1-add-to-spec migrate formats`.

## Mode

Read `references/modes.md` ("Pick the mode") every run. In short: you opened the pull request, so author mode; otherwise reviewer mode. The choice word wins. When the signed-in name can't be read, guess without asking and say `Mode: reviewer (guessed; say as author to switch).`

## Points and statuses

Read `references/classify.md` every run. One thread can hold several points; split them. Each point gets exactly one of the six statuses:

| Status | Means |
| --- | --- |
| `done <sha>` | The change is in the code; a commit after the request touched the anchor. Needs the commit. |
| `agreed` | The other side said yes or will do it; no commit shows it yet. |
| `declined` | The other side will not do it; the reason is kept. |
| `open` | Still being discussed, or not answered. |
| `waiting on <name>` | The last message asks that person or hands them the next step. |
| `needs <name>` | Someone outside the thread has to act or answer. |

A point that belongs to later work keeps its status and is also offered as a follow-up. Never guess `done`: no commit, no `done`. When the text does not settle a status, use `open` and say why.

**Resolved while the code is unchanged.** A thread the host shows as resolved (Azure DevOps `fixed`, `closed`, `wontFix`, `byDesign`; GitHub resolved) whose point is not `done`, `declined` or settled in the thread, with no push after the request touching its anchor, is flagged `resolved, code unchanged`. The opposite, `done` in the code while the thread is still active, is flagged `done, thread still active`. Both are offered as a status change.

## Output

Read `references/output.md` every run. Print, in this order:

1. The heading: `<repo> PR <n>: <title> (<source> -> <target>), you: <mode>, as of <date>`.
2. **Verdict line**: counts by status, the points waiting on you first, for example `Verdict: 2 waiting on you, 1 needs Robin K., 3 agreed (code checked: 1 done), 1 declined.`
3. **Waiting on you**, oldest first, then the other points grouped by status, one line each: anchor, status, owner, the point in plain words, the evidence (who said what, when; the commit).
4. **Flags**: resolved while the code is unchanged, and done with the thread still active.
5. **Spec and decision candidates** (see **Hand-offs**).
6. **Follow-ups** (drafts).
7. **Order**: pull requests this one depends on or that depend on it, and the merge order.
8. **Drafted replies (not posted)**: one per thread that waits on you.
9. **Merge readiness**: `Ready: yes | no | merged`, with the reasons.
10. `PR record: <path>`.

`since last` prints only changes; see **Since last**.

## Since last

Read `references/since-last.md` only on `since last`, or when your `Read` line exists and the user asked what changed. Without your `Read` line, `since last` prints the full view and says `No earlier run of yours; showing everything.`

## Write the record

Every run writes the PR note's `## PR record` as `references/pr-record.md` says, merge-safe, each line in sorted place: one Point per point, `Order` lines, your `Read` line, the `Ready` line and the `State` line. A Point keeps its line; a changed status replaces that line where it is. Never delete a Point. The drafted replies go in a `## Replies as drafted, <date> (not posted)` history section, after the personal-data and secrets check. Then run the notes index generator (`scripts/notes_index.py` in `crav1-add-to-spec`). Do not commit; name `/crav1-finalize-commit`.

Writing the record needs no yes: it is a note in the specs repo, as `/crav1-review-pr` writes its notes. When no specs repo is found, print the record with the path it would have.

## Hand-offs

Read `references/offers.md` only when there is something to offer.

- **Spec or decision candidates.** A point that settles how the system works, accepts a limit for now, or drops a goal is a candidate. The record tags it `to spec` or `to decision`. On a yes, run `/crav1-add-to-spec` with the candidate text and the PR note as its source; that skill writes the spec lines, and the Point gets `in spec <slug>`.
- **Follow-up work items.** A point accepted for later becomes a drafted item for `/crav1-ado-sync` (title and description, in the format of that skill's push branch). The record marks its Point `follow-up` only on a yes. Never create a work item.
- **Thread status changes.** One question per thread, each its own yes. Only a yes sets that one thread's status on the host, as `references/pr-threads.md` says. Never several threads on one yes.

## Hard rules

- Never post, reply, vote, approve or resolve on the host, except one thread status the user said yes to for that thread.
- Replies and messages to other people are drafts. Never send them.
- No edits to code, `spec.md`, `plan.md`, `tasks.md` or `verify.md`. The only writes are the PR note with its record, and the generated notes indexes.
- Read-only toward the code repo; the only git write is a fetch of the pull request's two branches, as `/crav1-review-pr` asks first.
- Never log in. Never print, echo or store a token. Redact secrets and personal data the way `/crav1-review-pr` does.
- Do not run `/crav1-review-pr`, `/crav1-merge-pr` or `/crav1-ado-sync`. Name them when they fit.
- No rebase advice; suggest merging the base into the branch.
