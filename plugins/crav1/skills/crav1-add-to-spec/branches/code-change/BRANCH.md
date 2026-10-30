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

When the pointer names a repo that is not the open checkout, read the code from `../<repo>`, as this skill's `references/branches.md` says under **Sibling checkout**. Ask for the path with options only when it is missing. A headless run stops: `No checkout found for <repo>. Name its path.` Never check out, fetch, commit, or write in that checkout. The note, the spec points and `Synced at` go into the spec repo.

## Change (no sort yet)

Read this skill's `branches/code-change/references/change.md` now, before you go on.

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

Expected headings when the file already uses the full spec shape: this skill’s `assets/spec.md` (same file as `docs/specs/_template/spec.md`; this skill's `branches/code-change/assets/spec.md`). A match-shaped spec does not have to grow those headings.

The **fits none of them** pile is listed and left alone. Do not create a spec for it. If they say to create one, do not write a folder here. Point at the skill that creates a spec, and do not run it:

- one or two sentences for one feature: `/crav1-spark-to-spec`
- one unstructured pile for one feature: `/crav1-ideas-to-spec`
- several new features, or several repos: `/crav1-bundle-to-specs`
- repos that already make up the system, and this leftover is a slice to match: the repos and bundle branch of `/crav1-existing-to-specs`

## Synced at

Read this skill's `branches/code-change/references/synced-at.md` now, before you go on.

## Impact (before any other edit)

Read this skill's `branches/code-change/references/impact.md` now, before you go on.

## Full note (1.61.0)

Read this skill's `branches/code-change/references/full-note.md` now, before you go on.

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
