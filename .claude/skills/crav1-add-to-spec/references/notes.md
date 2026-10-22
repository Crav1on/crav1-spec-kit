# Notes (1.61.0)

Every `/crav1-add-to-spec` input (fact, dump, code change, meeting) becomes **one note** that holds the full input and its source. Specs get only their own short points, each with a link to that note. This file is the rule for every skill that writes or reads `docs/notes/`.

## One note per input

- One input, one note. Do not split it. A meeting, a mail, a dump, a code change: the whole text (after the imported-sources redaction). A fact: the fact plus the passage around it, as the user gave it.
- The note is the shared full source. It is **never absorbed**. Do not ask an absorb question. Do not write `Absorbed by`. `used_by` grows as specs take points from it.
- There is no Note choice. Every input is noted, whatever happens to its points. An item that is left or dismissed stays in the full note; nothing extra is written for it.
- No "never used" flag. A note nobody has used yet is just a note.

## Where and named how

`docs/notes/YYYY-MM/YYYY-MM-DD-<slug>.md`. The date and the month folder are the **source date**: the meeting date, the mail's sent date, the commit date, the date a file or dump shows. When the source shows no date, use the import date, set `source_date: none`, and say `no source date, filed under the import date` in the report. `<slug>` is a short name from the subject: lowercase, hyphens, no person's name. Never overwrite a note; a clash on a different input picks another slug.

## Shape

The shape is this skill's `assets/note.md` (same file as `docs/notes/_template/note.md`): front matter `title`, `kind`, `source`, `source_date`, `imported`, `source_folder` (when imported), `commits` (code changes only, 1.64.0), `pr_note` (code-change and review-pr notes that came from a pull request, 1.65.0), `used_by`, `waiting_for`; then the title, a `Source date: … Imported: …` line, and the full input verbatim.

`source` names the input so it can be recognised again: the mail's subject, sender, and sent date; the meeting date and title; the file path; the commit SHA or range.

`commits` (1.64.0) lists the short SHAs a code-change note imported, oldest first, without merge commits: `commits: [155b5c4, 2c0e1a9]`. Other kinds leave it out or empty. Notes written before 1.64.0 have none; that is fine. From 1.64.1 the body of a code-change note starts with one commit line per imported commit, `<short sha> <author date> <subject>`, for example `155b5c4 2026-10-01T08:00:12+02:00 Retry an order call on timeout`.

## PR note (1.65.0)

A pull request's title and description are saved as **one note per pull request** in the specs repo, so specs can link to the description locally. `/crav1-review-pr` writes or reuses it on every run, `/crav1-merge-pr` after a merge, and the code-change branch of `/crav1-add-to-spec` when it is given a pull request, or a branch with exactly one pull request on the host. `/crav1-open-pr` does not write one: the body it drafts is its own summary of the spec, plan and verify; a later review or merge saves the description with any human edits. A pull request that `/crav1-open-pr` made gets a PR note from review and merge like any other.

- **Key.** `source: PR <n> <repo URL path>`: the number and the repository part of the pull request URL without the scheme, for example `source: PR 71 dev.azure.com/contoso/orders/orders-api` or `source: PR 12 github.com/orders-org/orders-specs`. Host, repo and number together are the duplicate check: before writing, look for a note with that `source` in every month folder. Found: reuse it. Never write a second note for one pull request.
- **File.** `docs/notes/YYYY-MM/YYYY-MM-DD-pr-<repo>-<n>.md`, filed by the pull request's **created date** (GitHub `createdAt`, Azure DevOps `creationDate`), which is its source date. `<repo>` is the repository name, lowercase, hyphens.
- **Front matter.** `title: PR <n> (<repo>): <pull request title>`, `kind: pull request`, `source`, `source_date` (the created date), `imported`, `used_by`, `waiting_for`.
- **Body.** The `Source date: … Imported: …` line; then the URL, the author as the host shows it, `<base> ← <head>`, and the state on this read; then `## Description as of <YYYY-MM-DD>` (the read date) and the description verbatim, after the check below. An empty description is written as `(no description)`.
- **Read again.** When the newest `## Description as of` section has the same text, change nothing but add `State on <date>: <state>` when the state changed. When the text differs, append a new `## Description as of <date>` section with the new text and set `imported`. Never remove or rewrite an earlier section.
- **Personal data and secrets.** Run the personal-data and secrets check of [sources.md](sources.md) on the description before it is written, with the transfer data policy (auto-accept or review). Secrets are always redacted, by kind; the note names the kind removed, never the value. There is no `docs/sources/` folder for a PR note: the host keeps the original, and the note's `source` and URL point at it. A headless run follows the two-pass rule there.
- **Images.** Each image in the description follows the four options of [sources.md](sources.md) **Images inside a mail** (one list, one question). Read an image only through the gh or az session that is already signed in. An image the kit cannot fetch or view is written as `[Image left out: <name>, not viewed]` and keeps its link. A compressed image is written next to the note as `<note file name>-<n>.webp`, a converted one as `<note file name>-<n>.md`. No new folder.
- **Read with.** GitHub: `gh pr view <n-or-url> --json number,url,title,body,author,createdAt,state,baseRefName,headRefName`. Azure DevOps: `az repos pr show --org <org-url> --id <n> --detect false --output json` (`title`, `description`, `creationDate`, `createdBy`, `status`, `sourceRefName`, `targetRefName`). Read-only. Never log in.
- **Links.** A code-change note that came from a pull request, and a review-pr follow-ups note, carry `pr_note: docs/notes/YYYY-MM/<file>.md`. A spec point taken from the description is followed by `Full source:` with the PR note's path, and the slug goes in the PR note's `used_by`.
- **Which specs repo.** The note goes into the specs repo (the checkout with `docs/specs/`): the open checkout, else the workspace folder with `docs/specs/`, else a sibling `../*/docs/system/repos.md` that has a row for the pull request's repo. Write it there without committing, and name the full path in the report. When no specs repo is found, write nothing and print the note with the path it would have.
- **PR updates (1.76.0).** `pr<n> all` appends `## PR updates as of <date>` sections (description and comment threads), as [pr-comments.md](pr-comments.md) says. Other runs leave them as they are.
- Run the notes index generator after the note changes.

## Indexes are generated

Do not edit `docs/notes/index.md` or `docs/notes/YYYY-MM/index.md` by hand. After writing or changing notes, run the generator from the product repo root:

- Cursor drop-in: `python3 .claude/skills/crav1-add-to-spec/scripts/notes_index.py`
- Plugin: this skill's `scripts/notes_index.py`
- Claude Code: `python3 .claude/skills/crav1-add-to-spec/scripts/notes_index.py`

`--check` exits 1 when an index differs from the front matter (a product repo can run it in CI). When Python cannot run, say the indexes need a rebuild and name the command; do not hand-edit.

## Writing the spec points

Each matching spec gets only its own short points, quoted as **Add to that spec.md** in `references/fact.md` says, each followed by `Full source: docs/notes/YYYY-MM/<file>.md`. Then add the slug to the note's `used_by`.

A **parked** spec (a `Parked:` line) gets nothing written. Add its slug to the note's `waiting_for`. Say `saved as a note for <slug> (parked)`. Un-park is `/crav1-retire-spec`; it moves the slug from `waiting_for` to `used_by`.

## Duplicate check (before writing)

Lookups for a spec follow the `Full source:` links. Matching new input and the duplicate check read the generated indexes and the note front matter.

- **Same source again** (the same mail, the same meeting date and title, the same file, the same commit), matched on each note's front matter `source` and `source_folder` (for a migrated note these come from its old `Source:` line; an empty field matches nothing): do not write a second note. Say `already imported on <imported date> as docs/notes/YYYY-MM/<file>.md`. Ask, options only: **Reuse the existing note (Recommended)** for specs that took nothing from it yet, or **Skip**. Reuse adds points and `used_by` only for those specs.
- **Overlap and same change (code changes, 1.64.0):** before writing, list the new change's commits and compare them with every `kind: code change` note. Use the note's `commits:` when it has one; otherwise expand its `source` SHA or range with git when those commits can still be reached; otherwise don't match on that note. A commit with a different SHA but the same diff (rebased, cherry-picked, force-pushed) is the same change: compare `git patch-id` and say `same change as <sha> in <note>`. When a note's commit is no longer on disk (pruned after a force push), patch-id can't be computed; match on its commit line instead (same author date and subject; a rebase keeps both) and say `same change as <sha> (old commit no longer on disk; matched by author date and subject)`. All commits already imported: the **same source again** path above. Some already imported: narrow the change to the new commits, say `<n> of <m> commits already in <note>; importing the other <k>` on the sort, and put only the new commits in `source` and `commits:`. No extra question; the sort confirmation covers it. A commit that may be a squash of imported commits counts as covered only when the host shows the matching PR merged as that commit (GitHub with `gh` or Azure DevOps with `az`, signed in, read-only); otherwise, and on any other host, list it as `may already be in <note>` for the user to keep or drop. One note serves every spec it feeds; never write a second note for the same commits. A missing or rewritten SHA never stops the run with an error.
- **Same point from a different source:** write the new note as usual. On the spec line that already says it, add the new note as a second source (`Full source: <first>; <second>`). Do not repeat the point.
- **Disagreement:** when the new source says something different about a point already on a spec, do not overwrite. Write the new point under the old one as `**Conflict:** "<new words>" (Full source: <note>) vs the line above`, and list it in the report for the user to decide.

## Old notes

Notes written before 1.61.0 (no front matter, flat in `docs/notes/`, maybe `Absorbed by`) are still read. `Absorbed by <slug>` counts as used by that slug; do not add new ones. Old spec lines keep their source lines; nothing is backfilled. The one-time move into month folders is `notes_index.py migrate`, after `notes_index.py migrate-dry-run` (named by `/crav1-refresh-system-notes`). It fills `source` and `source_folder` from the note's `Source:` line and rewrites links to moved notes across the repo.
