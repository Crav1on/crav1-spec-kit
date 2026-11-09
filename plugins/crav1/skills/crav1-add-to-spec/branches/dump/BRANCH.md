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

End the sort with this block, word for word except the examples, as the last thing in the message:

> **Reply yes** (or "confirm") to write it as shown.
> To change something first, reply with your edits, for example "drop 13" or "leave out the Figure 3 inference".
> Nothing gets committed either way.

Stop. They confirm or edit the sort. Do not write files. That confirmation is the only stop before writes. Do not ask for a slug. Do not open a mushy interview, an architecture interview, or an export-format question. If they edit the sort, the edit is the confirmation. Do not ask again. Use their slugs and piles. A fact they struck, or that you never put on the sort, stays labeled inferred if it appears later. Confirming the sort confirms the facts they left on it.

## Write the full note (1.61.0)

This step is in the same file, this skill's `branches/dump/references/duplicate-and-note.md`.

## Write the new bits

Read this skill's `branches/dump/references/write-new-bits.md` now, before you go on.

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
- End as `crav1-docs/reference/run-ending.md` says. Do not run the next step. Do not list the plan. Add the Uncommitted line when a file changed and is not committed.
- A `Conflict:` line was written: `Next: /crav1-resolve-open-questions <slug>, because a Conflict line is unsettled.`
- An existing spec changed and no Conflict line was written: `Next: /crav1-tighten-spec <slug>, because the new information is not tightened yet.`
- Neither: `Next: nothing needed now.`

## Style

Be concise. Quote the dump. Prefer the smaller edit. Do not invent content to fill gaps. A missing `glossary.md` is written only when `docs/system/` already exists. New rows are appended to an existing glossary. Existing rows are not rewritten. The picture update adds what is new and does not rewrite what is already there.
