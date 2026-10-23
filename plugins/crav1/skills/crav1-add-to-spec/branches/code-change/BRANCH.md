# Code into specs

You sort a code change that already landed onto specs that already exist. Then you write what belongs into the matching `spec.md` files, the same way the fact branch of `/crav1-add-to-spec` writes a quote. Then you check whether `docs/system/` or another spec has to change, and you report that impact. You do not silently rewrite those other files. The glossary append and the picture update are the exceptions: new glossary rows, and new picture lines, when `docs/system/` already exists. You do not rewrite existing glossary rows or existing picture lines. You do not write application code. You do not plan, implement, or commit.

This is not a mode of the repos and bundle branch of `/crav1-existing-to-specs`, the dump branch of `/crav1-add-to-spec`, or the fact branch of `/crav1-add-to-spec`. The repos and bundle branch creates spec folders from repos plus a dump. The dump branch sorts a later dump onto specs that already exist. The fact branch takes information already aimed at one named spec. This skill starts from a code change that already landed without spec, plan, or build. No dump is required. Do not send this job to those commands, and do not absorb theirs.

This is not the repos only branch of `/crav1-existing-to-specs`. That command reads the repos the user named and writes one architecture spec plus the system notes. This command sorts a change that already landed onto specs that already exist.

Do not copy the match worker that creates folders. Do not use `crav1-existing-to-specs` `branches/repos-and-bundle/references/slice.md`. Do not launch a worker. There is no slice subagent.

This skill does not watch the repo. It runs only when someone points it at a change. Do not schedule it, hook it, or run it again because new commits appeared.

This is not `/crav1-tighten-spec`. Tighten is for mushy wording. This skill is for a change that already landed. If the message is only “make this tighter” and brings no change, tell them `/crav1-tighten-spec` and do not edit.

This is not `/crav1-bundle-to-specs`, `/crav1-spark-to-spec`, or `/crav1-ideas-to-spec`. Those create the folders. Do not create a slug here. Do not invent a landscape from the diff alone.

A not-started spec (match status `not in the code`, or a thin spec) can keep taking information until planning. Adding what the change does does not start planning and does not write `plan.md` or `tasks.md`.

## Input

Everything after the fact branch of `/crav1-add-to-spec`, and every `@`, is the pointer: a commit, a commit range, a named branch, the diff of the current branch, or a pull request (1.65.0: its URL, or `PR <n>`), when they named one. The pointer may start with a repo from `docs/system/repos.md`, for example `orders-api feature/orders-openapi`; then the code is read from that repo's checkout (see **Which checkout**). No dump is required. Do not ask for notes, tickets, or a dump.

Do not ask for a slug first. An `@` of one spec folder is a hint for the sort, not a requirement. It does not limit the sort to that folder, and it does not replace the change.

## Specs (no sort yet)

Spec folders are `docs/specs/<slug>/` with a `spec.md`. Skip `_template`.

Read those folders before you sort. Do not ask which slug.

If there are no spec folders, stop. Point at the repos and bundle branch of `/crav1-existing-to-specs`. Do not invent a landscape from the diff alone. Do not create a slug. Do not seed `docs/system/`.

## Which checkout (1.64.0)

When the pointer names a repo that is not the open checkout, read the code from `../<repo>`, as `crav1-add-to-spec` `references/branches.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`) says under **Sibling checkout**. Ask for the path with options only when it is missing. A headless run stops: `No checkout found for <repo>. Name its path.` Never check out, fetch, commit, or write in that checkout. The note, the spec points and `Synced at` go into the spec repo.

## Change (no sort yet)

The change is one of these, when they named it:

- a commit (a hash they already gave, `HEAD`, or a subject that matches one commit)
- a commit range (`A..B`, `A...B`, or from one commit to another)
- a branch diff: a branch they named, or the current branch when they said this branch, the branch, or the branch diff. A branch diff starts at the branch's **fork point**, not at the default branch (below)
- a pull request (1.65.0): a URL, or `[<repo> ]PR <n>`, for example `orders-api PR 71`. A bare `pr71`, `pr 71`, `#71` or `pr <repo> 71` is this pointer too (1.76.0). Without `all`, comments are not read and the PR note's `## PR updates` sections are left as they are. Read it from the host, read-only, as **Pull request** below says. The change is its commits: the source branch diff from the pull request's target (the fork point search does not run; the target is the parent). A merged pull request whose source branch is gone uses its merge commit's second-parent range when git can reach it; otherwise say so and ask for a commit range, options only

If they named one, that is the change. A named range is one change. Do not ask. Do not ask them to type a hash. Do not split one change into several runs.

If they did not name one, look at git, then ask with options only. Use the questions tool when it is available. Do not guess a change and start sorting. Do not ask them to type a hash.

- Default branch: the branch `origin/HEAD` points at, or `main` when that is the default you can see.
- Recent commits: a short list from `git log` on the current branch. Each option is that subject. A short hash may sit beside the subject so two subjects can be told apart. The choice is the option.
- Branch diff: one option, the diff of the current branch from its fork point (commits on this branch since it split off, as one change). If that diff is empty, do not offer it. Say the branch diff is empty.

Stop until they pick, when a pick is required. The pick is the change.

**Fork point (1.64.0).** Work out where the branch split off as `crav1-add-to-spec` `references/branches.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`) says under **Fork point**: the candidates are its `(into …)` branch, the repo's `Merges into` branch, the default branch, the integration branches on disk (`develop`, `development`, `dev`, `integration`) while the `Merges into` cell is empty, and the spec's other work branches; the one with the fewest own commits is the parent (another spec branch only when it isn't built on this branch and the split point is not already in a base candidate). The change is the commits from that split point to the branch tip, without merge commits (`git log --no-merges`). Use the refs on disk; never fetch. The report names the parent and split point used and the age of each remote copy it read. No fork point found: fall back to the default branch and say so; when that fails too, ask with options only (the repo's branches, plus **A commit range instead**). A headless run stops: `No fork point found for <branch>. Name a commit range.`

**Spec branch and sub-branches (1.68.0).** Follow `crav1-add-to-spec` `references/branches.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`) under **Spec branch and sub-branches**. A branch with an `(into …)` marker takes that branch as its parent. When the parent found is another spec branch and the branch has no marker, ask the into question in the same batch as the sort confirmation (1.70.0): "<branch> split off <parent>. Does it merge into <parent>?" A yes writes `(into <parent>)` on the branch's Match `Branch:` entry and `(spec branch)` on the parent's entry when it has no marker, with the confirmed writes. A no writes nothing and treats the branch as stacked. A headless run doesn't ask, writes nothing, treats the branch as stacked, and says so. List commits with `--no-merges`; a merge commit that changes code beyond its two sides goes on the sort to keep or drop. On a spec-branch read, commits already in a sub-branch note are dropped by the overlap check, and a squash-merged sub-branch is covered through the host PR or listed as `may already be in <note>`.

**Merges into (1.64.0).** When the parent is not the default branch, is not a spec branch, and the repo's `Merges into` cell is empty, ask one yes/no question in the same batch as the sort confirmation (1.70.0), so one answer confirms the sort and both questions: "Work in <repo> merges into <parent>. Record that in repos.md?" Yes writes `<parent>` in that repo's `Merges into` cell (add the column when `repos.md` exists and the column is missing; other rows stay empty). No writes nothing. Never create `repos.md` for this. A headless run doesn't ask, writes nothing, and says it used <parent>.

**Pull request (1.65.0).** For a pull request pointer, read it with `gh pr view <url> --json number,url,title,body,author,createdAt,state,baseRefName,headRefName,commits` (GitHub, `gh auth status` must succeed) or `az repos pr show --org <org-url> --id <n> --detect false --output json` (Azure DevOps, already signed in). Never log in. When neither can read it, stop and say which (`gh is not signed in`, `az is not signed in`, `no host check for this remote`). The code is read from the checkout as **Which checkout** says. Write or reuse its **PR note** (below).

For a **branch** pointer, also look for its pull request on the host when the remote is GitHub with `gh` signed in, or Azure DevOps with `az` signed in: `gh pr list --head <branch> --state all --json number,url`, or `az repos pr list --source-branch <branch> --status all --detect false --output json`, read-only. Exactly one pull request: write or reuse its PR note, and say `PR note: <path> (from PR <n> for this branch)`. Otherwise write no PR note and say why, one line: `no PR note: gh is not signed in`, `no PR note: no host check for this remote`, `no PR note: no PR for <branch>`, or `no PR note: <n> PRs for <branch>; name one as PR <n>`. Never ask for it, and never stop because of it. A commit or a range writes no PR note.

**Overlap (1.64.0).** List the change's commits, then compare them with every `kind: code change` note before you sort, as `references/notes.md` says under **Overlap and same change**. When every commit is already imported, take the existing `already imported` path. When some are, narrow the change to the new commits and say `<n> of <m> commits already in <note>; importing the other <k>` on the sort. A commit that is the same change under another SHA (rebased, cherry-picked) is `same change as <sha> in <note>`; when the old commit is no longer on disk, match on the note's commit line (same author date and subject) and say so. A commit that may be a squash of imported work, and that no merged PR on the host explains, is listed on the sort as `may already be in <note>` for them to keep or drop. When the branch's `Synced at` SHA is gone or no longer an ancestor of the tip, say `branch rewritten since last read (was <sha>)` and keep going; never stop with an error for it.

## Sort (no writes yet)

Read every existing `spec.md` (skip `_template`) and the change (its diff and its commit messages). Then show three piles. Do not write files.

1. **Belongs to this spec** — the change does something that spec does not already say. Name `docs/specs/<slug>/` and the heading the words would go under. Quote what the change does.
2. **Already described there** — that spec already says what the change does. Name the slug and the heading. Do not plan a second copy.
3. **Fits none of them** — what the change does that matches no existing spec. Leave it on the list. Do not invent a slug.

A named slug in the message is evidence. It does not skip the other piles. Something with no slug is sorted by what the change does.

Split a fact that is partly new and partly already described. One fact is in one pile.

Put every fact you will treat as accepted on the sort. A fact you leave off stays inferred.

Stop. They confirm or edit the sort. Do not write files. That confirmation is the only stop before writes. Do not ask for a slug. Do not open a mushy interview, an architecture interview, or an export-format question. If they edit the sort, the edit is the confirmation. Do not ask again. Use their slugs and piles. A fact they struck, or that you never put on the sort, stays labeled inferred if it appears later. Confirming the sort confirms the facts they left on it.

## Write what belongs

Edit only `docs/specs/<slug>/spec.md` for slugs in the confirmed **belongs** pile. Write them in this chat. Do not launch a worker.

For each of those files, write the same way the fact branch of `/crav1-add-to-spec` writes:

- Quote what the change does. The quote is the record. Do not replace it with a paraphrase. A reading you add that the change does not show is inferred or it stays out.
- Label what is new versus what was already there.
- Keep inferred facts labeled inferred. A fact you were not shown by the change, and that the file did not already say, is inferred or it stays out. A fact that was not on the confirmed sort stays inferred or stays out.
- Do not invent acceptance, architecture, or tasks to fill gaps. A proposed ADR or diagram edit later is only a change the diff requires.
- Do not change match status unless the change itself says the status changed.
- Do not write `plan.md`, `tasks.md`, `diagrams.md`, `adr/`, `export/`, `verify.md`, `fix-log.md`, or `work-item.md` in the spec folder.
- Do not replace the file with a template.

Labels, in the section the words belong to:

- `**New:** "…"` — what the change does, added this pass, in sorted place among the `**New:**` lines there (1.84.0, `references/merge-safe.md`).
- `**Already there:**` — do not paste a second copy. Leave the existing sentence. The **already described there** pile is the report, not a second paste.
- `**Inferred:**` — a connection you drew. Not an accepted fact.

When the file already has `## Trace`, append one line: what this pass marked new, already there, and inferred. Do not create `## Trace` only for that line.

A thin spec (match status `not in the code`, or only Match / What the dump says / In the code / Trace / Open questions) stays thin. Put the quote under the heading it belongs to. Add a heading only when the change is that content. Do not add Problem, Goals, Users and journeys, or Acceptance criteria to fill the file out. Do not add `## In the code` unless the change names code that is there.

A fuller spec keeps its headings. Place the quote in the section it extends. Add an acceptance checkbox only when the change states a check a stranger could run, and label that checkbox `**New:**`. That checkbox stays yes/no. Name unit, system, or browser only when that kind is already obvious from the source. Otherwise leave the kind for plan. Do not invent a test list. Do not turn a behavior into a checkbox the change did not state.

Expected headings when the file already uses the full spec shape: this skill’s `assets/spec.md` (same file as `docs/specs/_template/spec.md`; drop-in: `.cursor/skills/crav1/crav1-add-to-spec/branches/code-change/assets/spec.md`; plugin: this skill’s `assets/spec.md`). A match-shaped spec does not have to grow those headings.

The **fits none of them** pile is listed and left alone. Do not create a spec for it. If they say to create one, do not write a folder here. Point at the skill that creates a spec, and do not run it:

- one or two sentences for one feature: `/crav1-spark-to-spec`
- one unstructured pile for one feature: `/crav1-ideas-to-spec`
- several new features, or several repos: `/crav1-bundle-to-specs`
- repos that already make up the system, and this leftover is a slice to match: the repos and bundle branch of `/crav1-existing-to-specs`

## Synced at

Record the code commit this run actually read. This write is not an apply option. It happens with the confirmed writes. Do not stamp before that confirmation.

`Synced at` in `docs/system/repos.md` is one line per repo and branch, `- <repo> <branch>@<short sha>, <date>`, in its `## Synced at` section, for example `- orders-api main@abc1234, 2026-10-07` (1.84.0, `crav1-add-to-spec` `references/merge-safe.md`). The branch is the branch that was read. The short sha is seven characters, the commit the read ended at: that commit, the end of a range, or the tip of a branch diff. The date is the date of that read, `YYYY-MM-DD`.

A whole-repo read is a read that is not limited to one slice: more than one slice, a path that fits none, or a branch diff or checkout that is not confined to one slice. Set that repo's `Synced at` line in `repos.md` to the branch and commit actually read. When that repo and branch already have a line, replace only that line; a new one goes in sorted place (repo, then branch). Leave every other line. Touch only the repos this run read. Do not change Purpose, Status, URL, or Boundaries. When the `## Synced at` section is missing and `repos.md` exists, add it after the table. When that repo has no row, do not add one. Say the line was not written. Do not write a slice `Synced at` line for that whole-repo read. When `repos.md` is missing, do not create it. Say the column was not written.

A one-slice read is a change whose paths all belong to one slice. Do not touch the `## Synced at` section of `repos.md`. Write or update a line in that slice's `spec.md`, after the title and before the first heading: `Synced at: <repo> <branch>@<short sha>, <date>`. One line per repo and branch read (1.84.0): `Synced at: orders-api develop@00344be, 2026-10-15` and, on the next line, `Synced at: orders-api feat/orders-retry@155b5c4, 2026-10-19`. When that branch already has an entry, replace only that entry. A new branch adds an entry at the end. Leave the other lines and a `(dropped)` on them. A change from a branch diff also counts as a one-slice read of that branch when its paths fit one slice.

**Branch list (1.67.1).** With the same confirmed writes, a one-slice read of a work branch also adds that branch to the slice's Match `Branch:` list, the `- Branch:` line under `## Match` in `spec.md`. A base branch (the repo's `Merges into` branch or default branch) is never added. When the line is missing, write it as the first line under `## Match`, and add `## Match` at the end of the spec when it is missing too. When the branch is already listed, leave it. Otherwise add a new line in sorted place (repo, then branch), as `crav1-add-to-spec` `references/merge-safe.md` says. Prefix the repo (`<repo> <branch>`) when the read named a repo or the list already uses repo prefixes. Keep every other entry and its markers (`(into …)`, `(spec branch)`) as they are, and never remove a branch: a branch given up gets `(dropped)` on its `Synced at` line through `/crav1-tighten-spec`. Example: `- Branch: orders-api feat/orders-retry; orders-api feature/orders-openapi`. The report names the branch added, or says it was already listed. A whole-repo read does not touch any `Branch:` list.

Do not stamp a repo or a slice this run did not read. A repo or branch with no line keeps no line. A consumer measuring drift uses, for each repo and branch, the older of the repo line and the slice line, and no line means unknown, so fall back to spec file commit dates.

## Impact (before any other edit)

The new quotes are already in the matching specs. Read `docs/system/` when it exists (`landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`, `adr/`) and every other `docs/specs/<slug>/spec.md` (skip `_template`). Other means a spec that did not just receive a new quote, plus any heading on a spec you did edit that the confirmed sort did not already cover. Check whether what the change does contradicts or extends the landscape, a repo row, a diagram, an ADR, or another spec.

Also compare each kept quote with research. Follow `crav1-add-to-spec` `references/research-stale.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md`; plugin: sibling `skills/crav1-add-to-spec/references/research-stale.md`). Read `docs/research/*.md` and `## Research findings` on the specs this quote touches, and the notes those findings link to. List a clear contradiction and an answered open question. An unclear case is not a hit. Ask before any new mark. Write the stale block and the findings line only after the user says yes. Then offer the revisit draft. The kit drafts only. It does not send it. It does not contact the note's owner. This question is not an apply option. When it is open, ask it before the landscape question. Do not ask both in the same turn. Do not commit. A kept quote that answers a point already waiting is re-checked there too. That re-check does not ask. Any kit skill that writes a file under `docs/research/` follows the clear section of that same skill, `references/research-stale-clear.md`. That check does not ask the user. An older mark with no point lines is not one point. The note's own open questions are routed when the answer lies outside the note's owner, including when the mark clears.

Section names for that read, not a file to paste over what exists: this skill’s `assets/system/` (same files as `docs/system/_template/`, including `glossary.md`; drop-in: `.cursor/skills/crav1/crav1-add-to-spec/branches/code-change/assets/system/`; plugin: this skill’s `assets/system/`).

Do not edit anything outside the confirmed belongs writes in this step, except the `Synced at` stamp above, the glossary gap, the picture update below, a research mark that `crav1-add-to-spec` `references/research-stale.md` already allowed after a yes, or a clear, a narrowed mark, a resolved line, or an open question that the same file says to write. The clear does not wait for a yes. Do not seed `docs/system/` when it is missing. Say it is missing and that this command does not create it. Do not invent a landscape from the diff alone. When that folder is missing, do nothing about a glossary and do nothing about the picture. The research check still runs. The research mark is not a landscape edit.

**Glossary.** When `docs/system/` is missing, do nothing about a glossary. When it exists and `glossary.md` is missing, write only that file from `assets/system/glossary.md`. When `glossary.md` already exists, append only words or abbreviations the change uses that are not already rows. Do not rewrite, reorder, or edit existing rows. A new row goes in sorted place by term, not at the end (1.84.0, `crav1-add-to-spec` `references/merge-safe.md`). Do not change a Meaning cell that already has text. Source is the landed change. Do not invent terms, expansions, or definitions. Do not write TBD or to be decided. A row is only a word or abbreviation that change already uses. When that same change already says the expansion or meaning, put that text in Meaning. When the change never says what it means, set Meaning to `to be researched`. Skip ordinary English. A code identifier is not a row unless the change already treats that word as a term. Write the file even when it has no rows. This write is not an apply option, and it does not rewrite any other landscape file except the `Synced at` stamp above and the picture update below. Do not list a rewrite of existing rows.

**Picture.** When `docs/system/` is missing, do nothing about the picture. When it exists, follow [picture.md](../../../crav1-refresh-system-notes/references/picture.md) (drop-in: `.cursor/skills/crav1/crav1-refresh-system-notes/references/picture.md`; plugin: sibling `skills/crav1-refresh-system-notes/references/picture.md`). Source is the confirmed new quotes, not a sentence marked inferred. Add what those quotes added to the short description, the diagram, and how the parts connect. Do not rewrite a sentence, a diagram node, a diagram edge, or a connection line that is already there. Do not run `/crav1-refresh-system-notes` as a second turn. This write is not an apply option. Do not invent a part from the diff. Do not rewrite existing glossary rows.

Do not edit `plan.md` or `tasks.md` when they exist, and do not list them as proposed edits. One line in the report when they exist: they were left alone. Adding what the change does does not start planning.

Report:

- If nothing else is affected, say so. Do not ask. `docs/system/` and the specs outside those writes stay as they are.
- If something else is affected, stop and ask. Options only. Use the questions tool when it is available.
  1. **Apply the listed edits**
  2. **Leave the other files alone**
- List each proposed edit in one line: the file, and what would change. One line per file change. No surrounding rewrite.

Do not silently rewrite `docs/system/` or specs the sort did not already write. The glossary write above is one exception: a missing file, or new rows appended to an existing file. The picture update is the other: new lines on the short description, the diagram, and how the parts connect. The `Synced at` stamp above is the third: the repo line on a whole-repo read, or the slice line on a one-slice read. Apply the other edits only if they pick apply, and only the lines you listed. If they pick leave, do not edit those files. Do not rewrite existing glossary rows or existing picture lines either way. Do not list the picture lines again as an apply option.

## Full note (1.61.0)

Every run writes **one note** for the change, as `crav1-add-to-spec` `references/notes.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/notes.md`; plugin: sibling `skills/crav1-add-to-spec/references/notes.md`) says. It holds the full commit messages, the list of changed files, and the diff hunks the kept quotes come from. Path `docs/notes/YYYY-MM/YYYY-MM-DD-<slug>.md` by the **commit date** (the newest commit of a range). Front matter `kind: code change`, `source` the SHA or range, and `commits:` the short SHAs this note imported, oldest first, without merge commits (`commits: [155b5c4, 2c0e1a9]`). The body starts with one commit line per imported commit, `<short sha> <author date> <subject>` (1.64.1), before the full messages, files and hunks. After a narrowed overlap, `source` and `commits:` hold only the new commits. When the change came from a pull request (named, or the one pull request of the branch), the note also gets `pr_note:` with the PR note's path (1.65.0).

**PR note (1.65.0).** Write or reuse the pull request's note as `references/notes.md` **PR note** says: one note per pull request, `kind: pull request`, keyed by `source: PR <n> <repo URL path>`, filed by its created date, a new `## Description as of <date>` section only when the description changed, after the personal-data and secrets check and the four image options. A spec point taken from the description gets `Full source:` with the PR note's path, and the slug goes in its `used_by`. Each kept quote is followed by `Full source: docs/notes/YYYY-MM/<file>.md`, and the slug goes in `used_by`; a matching parked spec gets nothing and goes in `waiting_for`. The same commit or range again, or a change whose commits are all already in notes (by SHA or the same change by `git patch-id`), is `already imported on <date> as <note>`, reuse or skip; never a second copy. One note may feed several specs: reuse adds the other spec to `used_by`. Run `scripts/notes_index.py` after the note changes. Do not hand-edit an index.

## Stop

Do not plan. Do not implement. Do not commit. Do not run `/crav1-finalize-commit` or `/crav1-plan-from-spec`. Do not watch the repo.

Output only:

- The change (which commit, range, or branch diff), and for a branch diff the parent, the split point, the commit count and the age of each remote copy read
- PR note: the path and written, reused, or updated; or `no PR note: <why>` for a branch
- Overlap: commits already imported and in which note, same changes by patch-id, `may already be in` lines, and `branch rewritten since last read` when it applied
- `Merges into` written, declined, or not asked (headless)
- Each `docs/specs/<slug>/spec.md` that gained a new quote
- What was added (what the change does, labeled new) and what was already described there
- The fits-none list, left alone. If they asked for a new spec, which existing skill you pointed at
- `glossary.md` when this turn created it or appended rows. If `docs/system/` was missing, say no glossary was written. If no new rows were appended, say so
- Picture lines added, or that the picture is current. If `docs/system/` was missing, say no picture was written
- `Synced at` line in `repos.md` or slice line written, or that none was written
- Match `Branch:` entry added, already listed, or not written (base branch or whole-repo read)
- Impact: nothing else, or the one-line edit list and which option they picked
- Research: each hit, whether it was marked, the note path and the findings line, or that none was marked. The revisit draft when one was written in the chat, or that none was drafted. The clear summary: what was cleared, narrowed, and routed where, each open question from the updated note and where it went, and when an older mark had no points, or that this run did not check an updated note
- Next: `/crav1-finalize-commit` only if any file changed and they want those spec edits committed (no push). `/crav1-plan-from-spec` only for a slice they choose. Do not run either.

## Style

Be concise. Quote what the change does. Prefer the smaller edit. Do not invent content to fill gaps. A missing `glossary.md` is written only when `docs/system/` already exists. New rows are appended to an existing glossary. Existing rows are not rewritten. The picture update adds what is new and does not rewrite what is already there.
