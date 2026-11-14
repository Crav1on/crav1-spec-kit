---
name: crav1-pr-status
description: >-
  Use when the user asks where one open pull request stands. Lists every
  thread point as done, agreed, declined, open, or waiting, who owes the next
  step, dependencies, and a merge-readiness line. `since last` shows only
  changes. Saves the PR record in the specs repo notes.
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

Resolve the pull request and its host as [pr-common.md](../crav1-docs/reference/pr-common.md) says (1.158.0; with no pull request named, `scripts/pr_common.py find --branch <current-branch>`), and the code repo and specs repo as `/crav1-review-pr` does (**Specs repo and code repo**). Read everything as `crav1-add-to-spec` `references/pr-threads.md` says (skill `crav1-add-to-spec`, `references/pr-threads.md`): the threads with every comment, the pushes with their commits, the files each push changed, and who is signed in. Skip system and bot threads.

Then read the PR note and its `## PR record`, as `crav1-add-to-spec` `references/pr-record.md` says (skill `crav1-add-to-spec`, `references/pr-record.md`). No PR note yet: write it as `/crav1-review-pr` **PR note** does. An old follow-ups note is read as `migrated` Points; say once to run `/crav1-add-to-spec migrate formats`.

## Mode

Read `references/modes.md` ("Pick the mode") every run. In short: you opened the pull request, so author mode; otherwise reviewer mode. The choice word wins. When the signed-in name can't be read, guess without asking and say `Mode: reviewer (guessed; say as author to switch).`

## Points and statuses

Read `references/classify.md` every run: it splits threads into points and gives each point exactly one of six statuses, `done <sha>`, `agreed`, `declined`, `open`, `waiting on <name>` or `needs <name>`. Never guess `done`: no commit, no `done`. When the text does not settle a status, use `open` and say why.

**Host settings (1.115.0).** A point that asks for a host setting is `done host` when that repo's host-setup script `check` part shows it live in this run. Read-only: never run `apply`. Not set yet, or not signed in: keep the status and name `/crav1-host-setup`. The full rule and the resolved-while-unchanged flags are in `references/classify.md` ("Statuses").

## Output

Read `references/output.md` every run and print in its **Order**: the heading, the `Verdict:` line, the points waiting on you first and then by status, flags, spec and decision candidates, follow-ups, merge order, drafted replies (not posted), the run ending, `Ready: yes | no | merged` with its reasons, and the `PR record:` line. `since last` prints only changes; see **Since last**.

## Since last

Read `references/since-last.md` only on `since last`, or when your `Read` line exists and the user asked what changed. Without your `Read` line, `since last` prints the full view and says `No earlier run of yours; showing everything.`

## Write the record

Every run writes the PR note's `## PR record` as `references/pr-record.md` says, merge-safe, each line in sorted place: one Point per point, `Order` lines, your `Read` line, the `Ready` line and the `State` line. A Point keeps its line; a changed status replaces that line where it is. Never delete a Point. The drafted replies go in a `## Replies as drafted, <date> (not posted)` history section, after the personal-data and secrets check. Then run the notes index generator (`scripts/notes_index.py` in `crav1-add-to-spec`), with the interpreter `crav1-docs/reference/running-scripts.md` names. Do not commit. The run ending's Uncommitted line covers the note.

Writing the record needs no yes: it is a note in the specs repo, as `/crav1-review-pr` writes its notes. When no specs repo is found, print the record with the path it would have.

## Hand-offs

Read `references/offers.md` only when there is something to offer.

Its **Hand-offs** section holds the three kinds: spec or decision candidates (name `/crav1-add-to-spec pr<n> candidates`; never run it or ask about it, 1.100.0), follow-up work items (drafts for `/crav1-ado-sync`, marked `follow-up` only on a yes; never create a work item), and thread status changes (one question and one yes per thread; never several threads on one yes).

## Hard rules

- Never post, reply, vote, approve or resolve on the host, except one thread status the user said yes to for that thread.
- Replies and messages to other people are drafts. Never send them.
- No edits to code, `spec.md`, `plan.md`, `tasks.md` or `verify.md`. The only writes are the PR note with its record, and the generated notes indexes.
- Read-only toward the code repo; the only git write is a fetch of the pull request's two branches, as `/crav1-review-pr` asks first.
- Never log in. Never print, echo or store a token. Redact secrets and personal data the way `/crav1-review-pr` does ([pr-common.md](../crav1-docs/reference/pr-common.md), "Signing in and secrets").
- Do not run `/crav1-review-pr`, `/crav1-merge-pr`, `/crav1-add-to-spec` or `/crav1-ado-sync`. Name them when they fit.
- No rebase advice; suggest merging the base into the branch.

## Run ending (1.122.0)

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says.
