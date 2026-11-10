# crav1-review-pr: notes

Read only when the pointer in `SKILL.md` sends you here. Since 1.97.0 a review writes one note per pull request, the PR note, and keeps its follow-ups, questions and comment texts in that note's `## PR record` and history. There is no separate follow-ups note.

## PR record

Follow-ups are not posted and not in the paste-ready block. Since 1.113.0 the chat does not show them either: the PR note's `## Kit record, <YYYY-MM-DD>` section holds the check lines, findings, info notes, suggestions, follow-ups (under **Follow-ups (not for this PR)**) and the next step, word for word as the review worked them out, and `Context: <path>` when a context file was written (`references/output.md`). The chat shows one line: `Kit record: docs/notes/YYYY-MM/<file>.md`.

Write the record as `crav1-add-to-spec` `references/pr-record.md` says (skill `crav1-add-to-spec`, `references/pr-record.md`), merge-safe, each line in sorted place:

- One Point per finding of the paste-ready block (Blocker, Bug, Test to add): status `open`, owner the pull request's author, tag `from review-pr <date>`, the anchor from the point's link (path and line range, `general` for the overview, `branch <name>`), the point in plain words.
- One Point per follow-up: status `follow-up`, owner `-`. Paths and lines are kept, because the note stays in the specs repo. Use the path alone, or `general`, when the follow-up has no line.
- One Point per question asked in the comment: status `waiting on <author>`, tag `asked`. A re-review adds `answered <date>` when the thread has an answer, and leaves the status to `/crav1-pr-status`.
- `State: <host state> | <date>`.
- History, in sorted place by date (1.67.0): `## Comment as drafted, <YYYY-MM-DD>` with the paste-ready block, and `## Comment as posted, <YYYY-MM-DD> (by <name>)` with its source line and the posted text, each word for word in a code fence (four backticks for a draft, 1.114.2), after the personal-data and secrets check. A drafted point not in the posted comment gets the tag `not posted <YYYY-MM-DD>` on its Point and keeps its status. Never rewrite or remove a dated section. A record-only run never adds a drafted section (1.114.2). The drafted heading is always plain `## Comment as drafted, <YYYY-MM-DD>`, on a re-review too: never add a suffix such as `(re-review)`; a re-review tag goes on the `## Kit record` heading only (1.114.3). Details: `references/comment-as-posted.md`.
- Then run the notes index generator (`scripts/notes_index.py` in `crav1-add-to-spec`). Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Do not hand-edit an index.

**Re-review.** Read the record first. Do not write a second note. Set `imported` to this review's date, add Points for new findings and follow-ups, a new `## Comment as drafted` section, and set a Point the code now addresses to `done <short sha>`. Never delete a Point. Leave `used_by` as it is, then rerun the generator.

**Old follow-ups note.** A `review-pr-[<repo>-]<n>-follow-ups.md` note from before 1.97.0 is still read: its bullets count as `migrated` Points and its comment sections as history. Do not write to it. Add once to the kit record: `Old follow-ups note found; run /crav1-add-to-spec migrate formats.`

When the specs repo is not in this workspace, write the note into the specs repo found as a sibling (see [Specs repo and code repo](../SKILL.md#specs-repo-and-code-repo-1650)), never commit it, and name its full path. When no specs repo is found, write nothing; the chat line says `Kit record: not saved, no specs repo`.

## PR note

Every review writes or reuses the **PR note** as `crav1-add-to-spec` `references/notes.md` **PR note** says (skill `crav1-add-to-spec`, `references/notes.md`): one note per pull request, `kind: pull request`, `source: PR <n> <repo URL path>`, filed by the pull request's created date, a new `## Description as of <date>` section only when the description changed, the personal-data and secrets check, and the four image options. A pull request that `/crav1-open-pr` made gets one too. Then add to the kit record: `PR note: <full path> (written | reused | updated: description changed)`.

The follow-ups come back through the existing note flow: `/crav1-ado-sync` reads `follow-up` Points as open items, and a spec that takes one adds itself to the note's `used_by`. Notes are never absorbed. This skill does not do that marking. For the status of every thread, name `/crav1-pr-status` in the kit record and do not run it.

Writing the PR note (and the context file, `references/output.md`) is the only file this skill writes. It does not commit. The kit record's Uncommitted line covers the note. Do not run a commit. The chat review does not list a next step; 1.113.0 keeps later steps in the kit record.
