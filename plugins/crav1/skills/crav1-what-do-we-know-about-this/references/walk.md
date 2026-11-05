# Playbook walk (1.116.0)

A guided walk in chat through one playbook report: one item at a time, the answers saved into the report as you go. Read this file only for `report-playbook-walk`, or when the user says yes to "Walk through it now?" after `report-playbook-full`. Never for any other report word.

## Start

- **After `report-playbook-full`:** the report file is written as usual and linked in chat. Then ask one question: `Walk through it now?` (yes, or later with `report-playbook-walk`). No answer or no: stop there.
- **`report-playbook-walk`:** resume after a pause. Find the existing playbook report for the question (the newest `<topic-slug>-report-playbook-*` file in the folder the report rules name, or the file the user names or attaches). None found: say so, name `report-playbook-full`, and stop. Read it plainly, as `/crav1-resolve-open-questions apply` does (item blocks and the older table layout), and pick up at the first item whose `Answer:` (N, C) is empty or whose K item has not been walked. Say where you pick up, for example `Picking up at Step 4, N9 (6 of 14 answered).`
- **Headless or bot run** (no person in the chat): never walk. Write the file as usual and end with how to resume: `To walk it in chat later: /crav1-what-do-we-know-about-this report-playbook-walk <question>`.

## Blocking answers first

Before the first step, list the answers that block several steps (for example the merge order, when a K and an N item both decide it), one line each with the steps they touch. Offer to settle those first. `skip` takes them in Steps order like the rest.

## Order

Walk in Steps order. Each K, N and C item comes up at the step where it matters (its `Recorded in Step <n>` or the step it changes). Items no step names come last. The user can jump at any time, for example `go to N9` or `go to Step 6`, and the walk goes on from there; skipped items stay unanswered.

## Each item

1. **Why this matters**, 2-3 lines: where it came from (the mail, meeting, pull request thread or spec line, with who and when) and what it changes in the steps one way or the other.
2. The item and the recommended answer with its reason (for K: the decision as it stands).
3. The replies, on one line: `yes` (take the recommendation, or keep the K decision), your own answer, `more` (full background and the quotes), or add what you know.

`more` shows the full background and the source quotes, then asks again.

## Replies and saving

- `yes`, an own answer, or a K change: write it on that item's `Answer:` or `Change:` line in the report file right away, then move on. The file is the saved progress and the final record; do not print it each time.
- Added information: take it in, say in one line what it changes (or that it changes nothing), and update the item's recommendation when it moves. Then ask again.
- Never edit a spec, a plan, the tasks, `docs/system/` or code during the walk. The report file is the only file written.

## Free flow

The steps set the order; they are not a script. At any point the user may ask a question back, add information (for example `Arvid also said X in today's meeting`), push back on a recommendation, or change direction (for example `I want a separate branch with a build just for the CI/CD changes`).

- A question or a push-back: answer it, then return to the same item.
- A change of direction: redraft only the parts it touches (Compose, Merge order, Steps, and the order diagram when the steps move). Show the change as before and after, and iterate until the user says yes. Then write it into the report file and carry on from the item where the walk was.
- Items the change makes moot: say which, and mark them on their fill-in line as `moot: <why>`.

## End

When the last item is walked (or the user says `done`), show a short summary: the answers given, the K changes, the direction changes, and the items still open. Then offer apply, word for word except the examples:

> **Reply yes** (or "confirm") to run `/crav1-resolve-open-questions apply <this file>` and write these answers into the specs; it shows each change before writing.
> To change something first, reply with your edits, for example "N3: keep it open" or "drop the CI/CD branch".
> Nothing gets committed either way.

On yes, hand over to `/crav1-resolve-open-questions apply <this file>`: the one skill this command may start, and only on that yes. Stopping halfway is fine: the file keeps the answers, and `report-playbook-walk` picks up again.

## Out of scope

Loops that drive several skills by themselves are not part of the walk.
