# Match dump to specs

You sort a later dump onto specs that already exist. Then you write the new bits into the matching `spec.md` files. Then you check whether `docs/system/` or another spec has to change, and you report that impact. You do not silently rewrite those other files. The glossary append and the picture update are the exceptions: new glossary rows, and new picture lines, when `docs/system/` already exists. You do not rewrite existing glossary rows or existing picture lines. You do not write application code. You do not plan, implement, or commit.

Read this skill's `references/dump-scope.md` only when the request may not be a dump: a fact for one named spec, repos plus a dump, a tighten request, a request to create specs, or a status question.

A not-started spec (match status `not in the code`, or a thin spec) can keep taking information until planning. Adding information does not start planning and does not write `plan.md` or `tasks.md`.

## Input

Everything after the fact branch of `/crav1-add-to-spec`, and every `@`, is the dump: notes, tickets, old docs, diagrams, screenshots. Size is not a limit. Do not ask them to shrink it. Do not split one dump into several runs. One dump may be a lot about one slug, or it may cover many slugs. Both are this command.

Do not ask for a slug first. A hint in the dump about where something belongs is evidence for the sort, not a requirement. If it names a slug, use that. If it does not, match by what it says. An `@` of one spec folder is that kind of hint. It does not limit the sort to that folder.

## Specs (no sort yet)

Spec folders are `docs/specs/<slug>/` with a `spec.md`. Skip `_template`.

Read those folders before you sort. Do not ask which slug.

If there are no spec folders, stop. Point at `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, or the repos and bundle branch of `/crav1-existing-to-specs`. Do not create a slug. Do not seed `docs/system/`.

## Duplicate check (1.61.0)

Read this skill's `branches/dump/references/duplicate-and-note.md` now, before you go on.

## Sort (no writes yet)

Read every existing `spec.md` (skip `_template`) and the dump. Then show three piles. Do not write files.

1. **Belongs to this spec** — new bits that are a decision, a clarification, information, or an answer for an existing slug. Name `docs/specs/<slug>/` and the heading the words would go under. Quote the dump. The line says `Recommendation: Keep.`
2. **Already in that spec** — the dump repeats what that `spec.md` already says. Name the slug and the heading. Do not plan a second copy.
3. **Does not fit any of them** — the dump’s words that match no existing spec. Exploration with no feature yet, technical debt, and general information gathering land here. They stay in the full note (1.61.0). Leave them on the list. Do not invent a slug.

Before the piles, read `## Open questions` on every spec with the records under each question. Follow this skill's `references/open-questions.md`. Match by meaning, whether the question is asked, pending, or not marked. A fact that clearly answers one goes on the **belongs** pile with `Answers: "<question>"` and `Linked with the sort.` There is no separate question for it. When it would change a spec line, the line also says `Then: /crav1-resolve-open-questions for <slug>.` A fact that only might answer, or answers part, keeps its pile and shows `Possible answer to: "<question>". The question stays open.` When the dump is a mail, a transcript, or a chat that shows a spec open question being asked, list it under `Asked in this dump` with the spec and the date the source shows. That is not a pile.

A greeting, scheduling, and thanks are noise. Drop them. They are not a pile. Dismiss stays for that noise. A dropped line is not on a pile.

A named slug in the dump is evidence. It does not skip the other piles. Something with no slug is sorted by what it says.

Split a passage that is partly new and partly already there. One fact is in one pile.

Put every fact you will treat as accepted on the sort. A fact you leave off stays inferred.

This skill does not ask keep, leave, or dismiss one fact at a time. It does not add an accept-all question. The recommendation is on the sort. The user confirms or edits the sort. That confirmation is the choice.

On an edit, the user can mark a fact keep, leave, or dismiss. Keep moves it to belongs. Leave and dismiss write nothing beyond the full note.

Stop. They confirm or edit the sort. Do not write files. That confirmation is the only stop before writes. Do not ask for a slug. Do not open a mushy interview, an architecture interview, or an export-format question. If they edit the sort, the edit is the confirmation. Do not ask again. Use their slugs and piles. A fact they struck, or that you never put on the sort, stays labeled inferred if it appears later. Confirming the sort confirms the facts they left on it.

## Write the full note (1.61.0)

This step is in the same file, this skill's `branches/dump/references/duplicate-and-note.md`.

## Write the new bits

When a confirmed quote comes from a mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original file, follow the imported-sources convention before that quote (this skill's `references/sources.md`). Its personal-data and secrets check is in that file; flagged items, the transfer data policy, and the one question are in `references/sources-flagged.md`, and a mail's images in `references/sources-mail.md` and `references/sources-binary.md`, all in `crav1-add-to-spec`. Write `docs/sources/YYYY-MM-DD-<slug>/` once per source. Add the `Source:` and `Trace:` lines from that file. Do not commit. A quote that is not from an imported source does not get a source folder. With `mail`, read `sources.md` and `sources-mail.md` before the sort. With `chat`, an exported chat file is an imported source; pasted chat text is not.

Edit `docs/specs/<slug>/spec.md` for slugs in the confirmed **belongs** pile. An imported source also writes its source folder, as that convention says. Write them in this chat. Do not launch a worker.

For each of those files:

- Quote their words. The quote is the record. Do not replace it with a paraphrase. For a diagram or screenshot, quote the text on it. A reading you add that the file does not state is inferred or it stays out.
- Label what is new versus what was already there.
- Keep inferred facts labeled inferred. A fact you were not told, and that the file did not already say, is inferred or it stays out. A fact that was not on the confirmed sort stays inferred or stays out.
- Do not invent acceptance, architecture, or tasks to fill gaps. A proposed ADR or diagram edit later is only a change their words require.
- Do not change match status unless the new information itself says the status changed.
- Do not write `plan.md`, `tasks.md`, `diagrams.md`, `adr/`, `export/`, `verify.md`, `fix-log.md`, or `work-item.md` in the spec folder.
- Do not replace the file with a template.

Labels, in the section the words belong to:

- `**New:** "…"` — their words, added this pass, in sorted place among the `**New:**` lines there (1.84.0, `references/merge-safe.md`).
- `**Already there:**` — do not paste a second copy. Leave the existing sentence. The **already** pile is the report, not a second paste.
- `**Inferred:**` — a connection you drew. Not an accepted fact.

When the file already has `## Trace`, append one line: what this pass marked new, already there, and inferred. Do not create `## Trace` only for that line. An imported source is the exception: the `Source:` and `Trace:` lines in the imported-sources convention are required, and `## Trace` is created when it is missing.

A thin spec stays thin, as **Thin spec** in `crav1-add-to-spec` `SKILL.md` says.

A fuller spec keeps its headings. Place the quote in the section it extends. Add an acceptance checkbox only when they stated a check a stranger could run, and label that checkbox `**New:**`. That checkbox stays yes/no. Name unit, system, or browser only when that kind is already obvious from the source. Otherwise leave the kind for plan. Do not invent a test list. Do not turn a wish into a checkbox.

Expected headings when the file already uses the full spec shape: this skill’s `assets/spec.md` (same file as `docs/specs/_template/spec.md`; this skill's `branches/dump/assets/spec.md`). A match-shaped spec does not have to grow those headings.

Read this skill's `references/dump-answers.md` only when the confirmed sort has a fact with `Answers:` or a line under `Asked in this dump`.

The full note is written under **Write the full note**. It does not become a spec. The **does not fit** pile is listed and left alone. Do not create a spec for it. If they say to create one, do not write a folder here. Point at the skill that creates a spec, and do not run it:

Read this skill's `references/dump-new-spec.md` for which skill to point at.

## Impact (before any other edit)

Read this skill's `branches/dump/references/impact.md` now, before you go on.

## Stop

Do not plan. Do not implement. Do not commit. Do not run `/crav1-finalize-commit` or `/crav1-plan-from-spec`.

Output only:

- Each `docs/specs/<slug>/spec.md` that gained a new quote
- The full note `docs/notes/YYYY-MM/YYYY-MM-DD-<slug>.md` this pass wrote or reused, its source date or `no source date`, and any duplicate or conflict found
- Each source folder `docs/sources/YYYY-MM-DD-<slug>/` this pass wrote, or that none was written
- The transfer data policy when this pass wrote it, or that none was written
- What was added (their quotes, labeled new) and what was already there
- Open questions: each answer linked, each possible answer left open, each asked mark written and where its date came from, and each `/crav1-resolve-open-questions` named, or none
- The does-not-fit list, left alone. If they asked for a new spec, which existing skill you pointed at
- An item already noted, with its path, and that no second file was written
- `glossary.md` when this turn created it or appended rows. If `docs/system/` was missing, say no glossary was written. If no new rows were appended, say so
- Picture lines added, or that the picture is current. If `docs/system/` was missing, say no picture was written
- Impact: nothing else, or the one-line edit list and which option they picked
- Research: each hit, whether it was marked, the note path and the findings line, or that none was marked. The revisit draft when one was written in the chat, or that none was drafted. The clear summary: what was cleared, narrowed, and routed where, each open question from the updated note and where it went, and when an older mark had no points, or that this run did not check an updated note
- Next: `/crav1-finalize-commit` if any file changed and they want those spec edits committed (no push). `/crav1-plan-from-spec` only for a slice they choose. Do not run either.

## Style

Be concise. Quote the dump. Prefer the smaller edit. Do not invent content to fill gaps. A missing `glossary.md` is written only when `docs/system/` already exists. New rows are appended to an existing glossary. Existing rows are not rewritten. The picture update adds what is new and does not rewrite what is already there.
