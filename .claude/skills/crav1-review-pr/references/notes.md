# crav1-review-pr: notes

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Follow-ups note

Follow-ups are not posted and not in the paste-ready block. The chat review still shows them, under **Follow-ups (not for this PR)**, then one line: `Follow-ups saved: docs/notes/YYYY-MM/<file>.md`.

When the review has at least one follow-up or question, write a note in `docs/notes/` of the specs repo, in the notes format of `crav1-add-to-spec` `references/notes.md` (1.61.0; `docs/notes/_template/note.md`; the same shape `/crav1-add-to-spec` writes, drop-in: `.claude/skills/crav1-add-to-spec/branches/meeting/assets/`; plugin: sibling `skills/crav1-add-to-spec/branches/meeting/assets/`):

- File: `docs/notes/YYYY-MM/review-pr-<n>-follow-ups.md`, in the month folder of the review date, where `<n>` is the pull request number. When two repos in this specs repo have the same pull request number, use `review-pr-<repo>-<n>-follow-ups.md`. A pull request in a repo other than the specs repo always uses `review-pr-<repo>-<n>-follow-ups.md` (1.65.0).
- Title: `Follow-ups from PR <n> (<repo>)`.
- Front matter: `kind: review-pr`, `source: PR <n> <repo>`, `source_date` and `imported` the review date, `pr_note:` the PR note's path (1.65.0), `used_by: []`.
- `From review <date>. PR <n>, <repo>, <PR title>.` then one bullet per follow-up: `<path>`, line `<n>`: the follow-up in plain words. Paths and lines are kept, because the note stays in the specs repo. Use `no line` when the follow-up has no line. A question asked in the comment is a bullet too, starting `Asked on the PR:` (1.66.0); a re-review adds `(answered on the PR <date>)` when the thread has an answer.
- After the bullets, the dated sections in time order (1.67.0): `## Comment as drafted, <YYYY-MM-DD>` with the paste-ready block, and `## Comment as posted, <YYYY-MM-DD> (by <name>)` with its source line and the posted text, each word for word in a code fence, after the personal-data and secrets check. A drafted point not in the posted comment gets a bullet ending `(Not in the posted comment, <YYYY-MM-DD>; still open.)`; a cut question keeps its `Asked on the PR:` line with the mark added. Never rewrite or remove a dated section. Details: `references/comment-as-posted.md`.
- Then run the notes index generator (`scripts/notes_index.py` in `crav1-add-to-spec`). Do not hand-edit an index.

**Re-review.** When the note for that pull request exists (in any month folder, or flat in `docs/notes/` from before 1.61.0), update it where it is. Do not write a second note. Set `imported` to this review's date, add new follow-ups and a new `## Comment as drafted` section, and mark one the code now addresses as `(done in <short sha>)`. Do not remove a line. Leave `used_by` as it is, then rerun the generator. When the review has no follow-ups and the note exists, leave the note.

**No follow-ups.** Still write the note when there is a paste-ready block (1.67.0): it holds the comment as drafted. A review with no block and no follow-ups writes no note.

When the specs repo is not in this workspace, write the note into the specs repo found as a sibling (see [Specs repo and code repo](../SKILL.md#specs-repo-and-code-repo-1650)), never commit it, and name its full path. When no specs repo is found, write nothing and print the note in the chat with the path it would have.

## PR note

Every review writes or reuses the **PR note**, whatever the follow-ups, as `crav1-add-to-spec` `references/notes.md` **PR note** says (drop-in: `.claude/skills/crav1-add-to-spec/references/notes.md`; plugin: sibling `skills/crav1-add-to-spec/references/notes.md`): one note per pull request, `kind: pull request`, `source: PR <n> <repo URL path>`, filed by the pull request's created date, a new `## Description as of <date>` section only when the description changed, the personal-data and secrets check, and the four image options. A pull request that `/crav1-open-pr` made gets one too. It goes in the same specs repo as the follow-ups note. Then one line: `PR note: <full path> (written | reused | updated: description changed)`.

The follow-ups come back through the existing note flow: `/crav1-ado-sync` reads open notes, and a spec that takes one adds itself to the note's `used_by`. Notes are never absorbed. This skill does not do that marking.

Writing the PR note and the follow-ups note are the only files this skill writes. It does not commit. Name `/crav1-finalize-commit` and do not run it.
