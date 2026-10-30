# crav1-review-pr: notes

Read only when the pointer in `SKILL.md` sends you here. Since 1.97.0 a review writes one note per pull request, the PR note, and keeps its follow-ups, questions and comment texts in that note's `## PR record` and history. There is no separate follow-ups note.

## PR record

Follow-ups are not posted and not in the paste-ready block. The chat review still shows them, under **Follow-ups (not for this PR)**, then one line: `PR record: docs/notes/YYYY-MM/<file>.md`.

Write the record as `crav1-add-to-spec` `references/pr-record.md` says (skill `crav1-add-to-spec`, `references/pr-record.md`), merge-safe, each line in sorted place:

- One Point per finding of the paste-ready block (Blocker, Bug, Test to add): status `open`, owner the pull request's author, tag `from review-pr <date>`, the anchor from the point's link (path and line range, `general` for the overview, `branch <name>`), the point in plain words.
- One Point per follow-up: status `follow-up`, owner `-`. Paths and lines are kept, because the note stays in the specs repo. Use the path alone, or `general`, when the follow-up has no line.
- One Point per question asked in the comment: status `waiting on <author>`, tag `asked`. A re-review adds `answered <date>` when the thread has an answer, and leaves the status to `/crav1-pr-status`.
- `State: <host state> | <date>`.
- History, in sorted place by date (1.67.0): `## Comment as drafted, <YYYY-MM-DD>` with the paste-ready block, and `## Comment as posted, <YYYY-MM-DD> (by <name>)` with its source line and the posted text, each word for word in a code fence, after the personal-data and secrets check. A drafted point not in the posted comment gets the tag `not posted <YYYY-MM-DD>` on its Point and keeps its status. Never rewrite or remove a dated section. Details: `references/comment-as-posted.md`.
- Then run the notes index generator (`scripts/notes_index.py` in `crav1-add-to-spec`). Do not hand-edit an index.

**Re-review.** Read the record first. Do not write a second note. Set `imported` to this review's date, add Points for new findings and follow-ups, a new `## Comment as drafted` section, and set a Point the code now addresses to `done <short sha>`. Never delete a Point. Leave `used_by` as it is, then rerun the generator.

**Old follow-ups note.** A `review-pr-[<repo>-]<n>-follow-ups.md` note from before 1.97.0 is still read: its bullets count as `migrated` Points and its comment sections as history. Do not write to it. Say once: `Old follow-ups note found; run /crav1-add-to-spec migrate formats.`

When the specs repo is not in this workspace, write the note into the specs repo found as a sibling (see [Specs repo and code repo](../SKILL.md#specs-repo-and-code-repo-1650)), never commit it, and name its full path. When no specs repo is found, write nothing and print the record in the chat with the path it would have.

## PR note

Every review writes or reuses the **PR note** as `crav1-add-to-spec` `references/notes.md` **PR note** says (skill `crav1-add-to-spec`, `references/notes.md`): one note per pull request, `kind: pull request`, `source: PR <n> <repo URL path>`, filed by the pull request's created date, a new `## Description as of <date>` section only when the description changed, the personal-data and secrets check, and the four image options. A pull request that `/crav1-open-pr` made gets one too. Then one line: `PR note: <full path> (written | reused | updated: description changed)`.

The follow-ups come back through the existing note flow: `/crav1-ado-sync` reads `follow-up` Points as open items, and a spec that takes one adds itself to the note's `used_by`. Notes are never absorbed. This skill does not do that marking. For the status of every thread, name `/crav1-pr-status` and do not run it.

Writing the PR note is the only file this skill writes. It does not commit. Name `/crav1-finalize-commit` and do not run it.
