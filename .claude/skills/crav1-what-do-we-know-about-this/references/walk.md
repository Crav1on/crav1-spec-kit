# Playbook walk (1.116.0, chat 1.117.0)

A guided walk in chat through one playbook report: one item at a time, the answers saved into the report as you go. Read this file only for `report-playbook-walk`, or when the user says yes to "Walk through it now?" after `report-playbook-full`. Never for any other report word.

## Start

- **After `report-playbook-full`:** the report file is written as usual and linked in chat. Then ask one question: `Walk through it now?` (yes, or later with `report-playbook-walk`). No answer or no: stop there.
- **`report-playbook-walk`:** resume after a pause. Find the existing playbook report for the question. Look in `docs/playbooks/` as well as the folder the report rules name. A path the user names under `docs/playbooks/` is the playbook. A `Docs path:` line names that committed copy. Otherwise the newest `<topic-slug>-report-playbook-*` file outside the project, or the file the user names or attaches. None found: say so, name `report-playbook-full`, and stop. Read it plainly, as `/crav1-resolve-open-questions apply` does (item blocks and the older table layout), and pick up at the first item whose `Answer:` (N, C) is empty or whose K item has not been walked. Say where you pick up in words, for example `Picking up at the deploy-order question (6 of 14 answered).` Do not speak the item id. The committed copy's `Answer:` and `Change:` lines read back the same way. That file carries `Docs path: docs/playbooks/<topic>.md`. Specs the apply touched get `Playbook: docs/playbooks/<topic>.md`.
- **Headless or bot run** (no person in the chat): never walk. Write the file as usual and end with how to resume: `To walk it in chat later: /crav1-what-do-we-know-about-this report-playbook-walk <question>`.

## In chat

Say the decision or the question so a reader can answer it without a legend. Do not use K, N or C item ids in the walk conversation, not even in parentheses. The report file keeps those ids. A jump still accepts `go to N9`; the reply names the item in words and does not repeat the id.

## Blocking answers first

Before the first step, list the answers that block several steps (for example the merge order, when a kept decision and an open question both decide it), one line each in words, with the steps they touch. Do not put an item id on that line. Offer to settle those first. `skip` takes them in Steps order like the rest.

## Order

Walk in Steps order. Each kept decision, open question and conflict comes up at the step where it matters (its `Recorded in Step <n>` or the step it changes). Items no step names come last. The user can jump at any time, for example `go to N9` or `go to Step 6`, and the walk goes on from there; skipped items stay unanswered.

## Each item

1. **Why this matters**, 2-3 lines: where it came from (the mail, meeting, pull request thread or spec line, with who and when) and what it changes in the steps one way or the other.
2. The decision or the question, in words, and the recommended answer with its reason (for a kept decision: the decision as it stands).
3. The replies, on one line: `yes` (take the recommendation, or keep the kept decision), your own answer, `more` (full background and the quotes), or add what you know.

`more` shows the full background and the source quotes, then asks again. Still no item id.

## When their words and the record do not match

Work out the intended outcome. Use the known facts and their words together. Offer one plausible reading and a recommendation, and say what that reading keeps and what it changes. Ask one focused follow-up at a time until the outcome is mutually clear. Then summarize and get an explicit yes before any accepted redraft or answer is written into the report.

The older record does not win by default. An uncertain recollection is not already decided. A missing note is not proof that no decision was made. Do not force a choice between the docs and the memory.

Those follow-ups are how the item gets understood. They do not count against the prompt budget.

## Replies and saving

- `yes`, an own answer, or a change to a kept decision: write it on that item's `Answer:` or `Change:` line in the report file right away, then move on. The file is the saved progress and the final record; do not print it each time. Do this only once the item is clear. When the section above applies, the explicit yes comes first.
- Added information: take it in, say in one line what it changes (or that it changes nothing), and update the item's recommendation when it moves. Then ask again.
- Never edit a spec, a plan, the tasks, `docs/system/` or code during the walk. The report file is the only file written.
- A pause or a stop leaves the item open. Say where the walk resumes. Do not write, and do not open a new product question to get back on track.

## Free flow

Stay on this item. The steps set the order; they are not a script. At any point the user may ask a question back, add information, push back on a recommendation, or change direction.

- A question or a push-back: answer it, then return to the same item.
- Do not list a route, and do not stitch two routes to fill a gap. Name at most one later skill, in one line. When no kit step covers the case, say the kit doesn't say. On an accepted redraft, that gap goes under Gaps.
- Do not start `/crav1-help`. An order question is answered from the steps already in this report.
- A change of direction: redraft only the parts it touches (Compose, Merge order, Steps, and the order diagram when the steps move). Show the change, iterate until it is clear, summarize, and write it into the report only after the explicit yes. Then carry on from the item where the walk was.
- Items the change makes moot: say which, and mark them on their fill-in line as `moot: <why>`.

## Reads

One pass applies only while matching the question to a slice. After the slice is chosen, reading that slice, the notes and code it names, and the read-only sources in `reports/common.md` is this skill. A pull-request thread may be read and tagged `Live read.` Do not run `/crav1-pr-status`; it writes a note in the project.

A merge trial is allowed only for an order this report already suggests, only outside the work tree, and labelled as a trial. Quote only a run that finished. Never checkout, commit, or push for a trial.

## End

When the last item is walked (or the user says `done`), show a short summary: the answers given, the kept-decision changes, the direction changes, and the items still open. Then offer apply, word for word except the examples:

> **Reply yes** (or "confirm") to run `/crav1-resolve-open-questions apply <this file>` and write these answers into the specs; it shows each change before writing. On that yes a filled playbook is also written to `docs/playbooks/<topic>.md`.
> To change something first, reply with your edits, for example "keep the third question open" or "drop the separate branch".
> A git commit still waits for `/crav1-finalize-commit`.

On yes, hand over to `/crav1-resolve-open-questions apply <this file>`: the one skill this command may start, and only on that yes. Apply writes filled, confirmed lines only (kept-decision changes, open-question answers, and conflict answers) and copies a filled playbook to `docs/playbooks/`. It does not run plan, build, or merge. It does not create a git commit. Empty lines stay open. A draft with no filled line is not copied. Stopping halfway is fine: the file keeps the answers, and `report-playbook-walk` picks up again, including from `docs/playbooks/`.

## Out of scope

Loops that drive several skills by themselves are not part of the walk.
