# Comment as posted (1.67.0)

The user often edits the paste-ready comment before posting it. So `/crav1-review-pr` keeps both texts in the PR note (1.97.0; before that, in a separate follow-ups note): the comment as drafted and the comment as posted. It compares them, and it marks drafted points that were left out without dropping them. Re-review then compares against what the reviewers actually saw. Examples use made-up names: the code repo `orders-api` on GitHub (`github.com/contoso/orders-api`), the source branch `feat/orders-retry`, pull request 42, the user Alex Doe.

## What the PR note holds

The PR note is `docs/notes/YYYY-MM/YYYY-MM-DD-pr-<repo>-<n>.md` ([PR record](../SKILL.md#pr-record)). After its `## PR record` section come the dated history sections, in sorted place by date (`crav1-add-to-spec` `references/pr-record.md`). Never rewrite or remove a dated section.

### The comment as drafted

Every review that ends with a paste-ready block saves it in the note:

```text
## Comment as drafted, <YYYY-MM-DD>
```

Then the block word for word, inside a code fence one backtick longer than any fence in the block (four backticks when the block has none). It is saved after the personal-data and secrets check (below). A re-review that drafts again adds a new section, even on the same date.

### The comment as posted

```text
## Comment as posted, <YYYY-MM-DD> (by <name>)
<source line>
```

Then the posted text word for word, in a code fence the same way.

- **Date:** the date the host gives for the post (GitHub review `submitted_at` or comment `created_at`; Azure DevOps comment `publishedDate`), in the user's time zone. For pasted text, the paste date, unless the user gives one.
- **`by <name>`:** the author's name as the host shows it: Azure DevOps `displayName`; GitHub the profile name, else the login. For pasted text: the signed-in host account's name, else git `user.name` in the specs repo. Never an email address or the Azure DevOps `uniqueName`.
- **Source line**, one of:
  - `Read from the PR thread: <comment URL>. Draft compared: <YYYY-MM-DD | none>. Description reviewed: as of <YYYY-MM-DD> (PR note).`
  - `Pasted in chat. Draft compared: <YYYY-MM-DD | none>. Description reviewed: as of <YYYY-MM-DD> (PR note).`
  - `Posted from this review on the user's yes: <comment URL>. Draft compared: <YYYY-MM-DD>. Description reviewed: as of <YYYY-MM-DD> (PR note).`
  - Add ` Verbatim except: <kind> removed.` when the check redacted something, and ` Edited on the host.` for an edit.
  - `Description reviewed` names the newest `## Description as of` section of the PR note at review time. That shows which description the comment answered.
- **Edited later on the host:** add a new section `## Comment as posted, <edit date> (by <name>), edited`, with the edited text and ` Edited on the host.` in the source line. Keep the earlier section.

The `## Description as of` sections are not changed. They keep the author's description.

## The record step

Run it at the start of **every** run on a pull request whose PR note (or old follow-ups note) has a `Comment as drafted` section with no `Comment as posted` section after it, or has a posted section the host may have edited since. Run it before the review. The `comment posted` choice word runs only this step and no review. In the same chat, the user saying "posted" (or pasting the text) after **I'll post it myself** runs it too.

### Finding the comment on the host

Use the signed-in `gh` or `az` session only, read-only. Never log in.

- **GitHub:**
  - Review bodies: `gh api repos/<owner>/<repo>/pulls/<n>/reviews` (`body`, `user.login`, `submitted_at`, `html_url`).
  - PR conversation comments: `gh api repos/<owner>/<repo>/issues/<n>/comments` (`body`, `user.login`, `created_at`, `updated_at`, `html_url`).
  - A hand post can be either. Inline review comments are not candidates.
  - The signed-in user: `gh api user -q .login`.
  - Edited means `updated_at` is later than `created_at`, or the body differs from the saved text.
- **Azure DevOps:**
  - Threads, as `crav1-add-to-spec` `references/pr-threads.md` says (1.97.0): `az rest --method get --resource 499b84ac-1321-427f-aa17-267ca6975798 --uri "<org-url>/<project>/_apis/git/repositories/<repo>/pullRequests/<n>/threads?api-version=7.1"`.
  - A candidate is a comment with `commentType` `text` (not `system`) on a thread without `threadContext` (not inline). It is either the first comment of a thread, or the user's reply in the thread of an earlier posted comment (a re-review).
  - Fields: `content`, `author.displayName`, `author.uniqueName`, `publishedDate`, `lastContentUpdatedDate`.
  - The signed-in user: `az account show --query user.name`, compared with `uniqueName`.
  - Edited means `lastContentUpdatedDate` is later than `publishedDate`.
- **Another host, no `gh` or `az`, or not signed in:** ask the user to paste the comment, with the options **paste it** and **not posted yet**.

### Picking it

1. Candidates are by the signed-in user and posted on or after the newest draft date.
2. A candidate matches when at least half of the drafted point links are in it, or its text similarity to the draft is 0.6 or more.
3. **One match:** show its date, first line and URL, then ask `Is this the comment you posted? Options: save it / not this one / paste it`. A comment this skill posted is saved without asking.
4. **Several:** list them (date, first line, points matched) as options, plus **paste it**. The user may pick more than one when they split the comment. Each pick gets its own section, in post order.
5. **None by the user:** show candidates by other authors only if they match.
6. **Nothing matches on a host that could be read:** in the automatic step, say `No posted comment found on PR <n>; nothing recorded.` and go on with the review. The comment may simply not be posted yet, so do not ask every run. After `comment posted` or "posted", ask for a paste instead.
7. **Pasted, and the host can be read too:** save the host text, and say so when the two differ.

## Comparing with the draft

- A **point** is a bullet under a section heading (`### Blockers`, `### Bugs`, `### Tests to add with this PR`, `### A question` or `### Questions`, `### Since last time`). Its key is its link target (path and line range, PR overview or branch), plus its bold title when it has one. Points with the same key are paired by text similarity.
- Each drafted point is one of **as drafted**, **changed** or **not in the posted comment**. A posted point with no drafted pair is **added**. The opening, the verdict, a closing line and a files link are compared but never marked.
- **Chat**, right after saving:

```text
Comment as posted (2026-10-19, by Alex Doe): saved in docs/notes/2026-10/2026-10-17-pr-orders-api-42.md
Compared with the draft of 2026-10-19: 5 points as drafted, 1 changed, 1 not in the posted comment, 1 added; opening changed.
- Changed: Bugs, src/orders/retry_store.py, lines 4–5
- Not in the posted comment: Tests to add with this PR, src/orders/retry_store.py, line 9 (still open)
- Added: A question, "Should the retry count be configurable?"
```

- **In the note:**
  - A drafted point that is not in the posted comment keeps its record Point and gets the tag `not posted <date>` (1.97.0): ``- Point: src/orders/retry_store.py:9 | open | Alex Doe | from review-pr 2026-10-19; not posted 2026-10-19 | An idempotency test for the row key``. It is never dropped.
  - A cut question keeps its Point (`waiting on <author>`, `asked`), with the tag added. No rewrite.
  - Changed points keep their Point as it is; the saved text is the record.
  - An added question gets a Point (`waiting on <author>`, `asked`). Other added points get an `open` Point.
  - Later, a point the code fixed gets status `done <short sha>`, and a point a later posted comment carries loses `not posted` and gets `posted <YYYY-MM-DD>`.
- **Posted text that doesn't split into points** (rewritten freely): save it word for word, mark nothing, and say `The posted comment doesn't follow the layout, so I can't match points; saved as is.`
- Follow-ups are never in the comment, so they never get the mark.

## Re-review

- Earlier points come from the newest `Comment as posted` section, after the record step has caught any edit. Comments and answers by other people on the host still count.
- No posted section: read the host's review comments as before. When the host has none, nothing was posted, so the new comment is a first-review comment with no `### Since last time`. The chat still goes through the points of the newest `Comment as drafted` section (fixed, partly fixed, still open, no longer relevant) under `compared with the draft; nothing posted was found`.
- `### Since last time` lists only points the reviewers saw.
- A new finding that matches a Point tagged `not posted` is shown in the chat with its mark and kept out of the new comment, unless the user says to include it.

## Personal data and secrets

Before anything is written, run the personal-data and secrets check of `crav1-add-to-spec` `references/sources.md`, with `references/sources-flagged.md` when an item is flagged, on the drafted block and on the posted text, fetched or pasted. Use the transfer data policy (auto-accept or review), the same as the PR note's description (drop-in: `.claude/skills/crav1-add-to-spec/references/sources.md`; plugin: sibling `skills/crav1-add-to-spec/references/sources.md`).

- Secrets are always redacted by kind. The note names the kind, never the value.
- Personal data follows the policy.
- A headless run follows the two-pass rule there.
- The comparison runs on the redacted text, so a redaction is never a change.

## Headless and bot runs

The choice words are in [Choice words](../SKILL.md#choice-words-1650). With no word:

- **One match:** save it without asking.
- **Several:** stop with `Several comments could be the posted one. Use one of: newest comment, skip comment record.`
- **None, or the host can't be read,** after `comment posted`: stop with `No posted comment found on PR <n>. Paste it in chat, or use: skip comment record.` In the automatic step, print `No posted comment found on PR <n>; nothing recorded.` and go on; nothing to paste in a headless run.

Posting stays interactive only. There is no choice word that posts.

## Example note (made-up names)

`````markdown
- Asked on the PR: The retry log goes to a SQL table here, but the folder README says Blob files only. Do we want an explicit exception, or to drop that goal? (Not in the posted comment, 2026-10-19; still open.)
- `src/orders/retry_store.py`, line 9: an idempotency test for the row key. (Not in the posted comment, 2026-10-19; still open.)
- Asked on the PR: Should the retry count be configurable?

## Comment as drafted, 2026-10-19

````markdown
I've looked through the PR and run it through my checks. This is what I found:

### Bugs

- [src/orders/retry_store.py, line 9](https://github.com/contoso/orders-api/blob/feat/orders-retry/src/orders/retry_store.py?plain=1#L9)

  The row key is random for every write. Maybe the key could be built from the file name and revision?

### Tests to add with this PR

- [src/orders/retry_store.py, line 9](https://github.com/contoso/orders-api/blob/feat/orders-retry/src/orders/retry_store.py?plain=1#L9)

  An idempotency test: the same file name and revision twice should give one row.

### A question

- [src/orders/retry notes.md, line 4](https://github.com/contoso/orders-api/blob/feat/orders-retry/src/orders/retry%20notes.md?plain=1#L4)

  The retry log goes to a SQL table here, but the folder README says Blob files only. Do we want an explicit exception, or to drop that goal?
````

## Comment as posted, 2026-10-19 (by Alex Doe)
Read from the PR thread: https://github.com/contoso/orders-api/pull/42#issuecomment-1001. Draft compared: 2026-10-19. Description reviewed: as of 2026-10-18 (PR note).

````markdown
I've looked through the PR and run it through my checks. This is what I found:

### Bugs

- [src/orders/retry_store.py, line 9](https://github.com/contoso/orders-api/blob/feat/orders-retry/src/orders/retry_store.py?plain=1#L9)

  The row key is random for every write. Maybe the key could be built from the file name and revision?

### A question

- [PR 42 overview](https://github.com/contoso/orders-api/pull/42)

  Should the retry count be configurable?
````
`````

## Record step rules

Moved word for word from `SKILL.md` in 1.80.2.

- The record step only reads the host (the signed-in `gh` or `az` session) or takes a paste. Never rewrite or remove a `## Comment as drafted` or `## Comment as posted` section; an edit on the host is a new `, edited` section.
