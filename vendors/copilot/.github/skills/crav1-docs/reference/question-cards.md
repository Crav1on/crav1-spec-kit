# Question cards

A question card is one question in the questions tool (1.130.0). A batch confirm uses the same card.

The recommended choice is listed first and its label ends with ` (Recommended)`, for example `yes (Recommended)`.

Typed changes go through that card's free-text answer, and the hint lives on that option, for example `Type your changes, e.g. C1: keep it open`. An item the answer does not mention keeps its recommendation.

Never add an option that only tells the user to type somewhere else. There is no `Edits` option. Picking that kind of option opens no text field.

Keep a real option when it does something different, such as go through the items one by one, use an existing branch, or stop.

A multi-select of optional items includes a real option for taking none of them, for example `None, go to plan`. Skipping does not need typing.

A choice the card would tell the user to type, such as none, skip, or all, is a real option on that card. Do not leave that choice only in the question text.

A fifth real choice still goes under Other, as the asking rule says. That is not a separate option whose only job is to point at Other. None, skip, and all stay on the card. They are not the item that overflows.

When the questions tool is not available, the same reply still works: the recommended word, or the typed changes in that reply.

## Batch of several items (1.145.0)

A batch card applies one yes to each of several items: plan findings (`P#`), spec issues (`I#`), open questions and conflict lines (`Q#`, `C#`), meeting items (`M#`), dump or code-change sort lines, a map of slices, test suggestions, flagged source lines, or images in a mail.

Print a findings table in that same reply, immediately before the card. The card is never asked without it. Columns, in order: Id, Issue, Options, Recommendation. One row per item. The issue is one line. Options are plain words for that item, never letters or internal names (1.196.0). Recommendation is the choice `yes` will apply, such as `add a test` or `keep as written`.

The question is short (1.197.0): it is only the `Card:` line from the command below, such as `Tighten-plan batch: apply all 3 recommendations?`. Never put the items in the question. The items live in the bullets above the card, one per item as `<id> <one-line issue>. Why: … Yes: <recommendation>.`, and in the `On yes:` line under the question, which is the card's result-on-yes and names every item as `<id> <one-line issue>: <recommendation>`, for example `P4 tasks miss the 400 path: add a test`. That line still makes sense if the table scrolled away. `yes (Recommended)` applies every recommendation on that line. A skill whose options are already **Accept all recommendations (Recommended)** and **Go through them one by one** keeps those labels. Typed changes stay on the card's free-text answer.

Never write `table above`, `the table recommends`, or `as in the table` unless that table is in this reply. Do not use those phrases on the card. The card does not point at the table; its `On yes:` line repeats each item. Never ask the card without the table.

Build the table and the card with one command. Print its stdout in the reply. The table is the first part, then one background bullet per item (what, why, what yes does), then the card. The card question is the `Card:` line, word for word. If the command fails, or it prints no table, do not ask the card.

`<interpreter> -X utf8 <skill crav1-tighten-plan>/scripts/batch_offer.py --title "Tighten-plan batch" --items <file>`

`<file>` is JSON, a list of objects with `id`, `issue`, `options`, and `recommendation`. The interpreter is [Running a kit script](running-scripts.md). On Windows it is `python`. Elsewhere it is `python3`. Set `PYTHONUTF8=1` and pass `-X utf8`.

A card that is one yes for one action, such as post this text or run this script, is not this batch. One question per item, when that question already names the item and the recommendation, is not this batch. Do not collapse those questions into a card that says `table above`. Collapsing them onto one card makes it this batch.

## Card wording (1.164.0)

Every card the kit asks follows these seven rules.

1. **A short plain question.** No brackets and no kit terms such as other-owner mode, step name, `needs_yes`, or map mark. Name the thing itself: `Merge PR 71 into develop?`
2. **Each option says what happens.** A bare `yes` or `stop` is not enough. For example **Add to their pull request (Recommended)**: `Build T5 on PR 71's branch so it lands in PR 71.` The choice word stays the reply word, hyphen-only as before.
3. **The recommended option is first**, its label ends with ` (Recommended)`, and it says why in a few words, for example `Why: the branch is already theirs.`
4. **Background goes before the card**, in one short sentence, never inside the question. For example `PR 71 on feat/orders-cicd is person A's.`, then the card.
5. **Fewer cards.** Questions in a row that you would always answer together are one card, for example commit and push the walk's files. Never ask again for a yes that is already on record.
6. **Plain Waiting lines.** A Waiting line names who or what, and why: `Waiting for person A to approve T7`, not `needs_yes T7`.
7. **One question, written once (1.190.0).** A card asks one question; a second question gets its own card. Claude Code's question tool accepts several questions in one call; send one question per call, matching this rule (1.201.1). An option is written as meant: never one that corrects itself mid-sentence (`... no: on ...`, `... I mean ...`, `... actually ...`, `... or rather ...`). Rewrite it before the card is shown.

The rules above still hold: no `Edits` option, typed changes go in the free-text answer, a missing word is asked again, and the merge card names the pull request.

### How a skill file writes a card

```
Card: Should I add my work to their pull request?
- **Add to their pull request (Recommended)** (`switch`): build T5 on PR 71's branch so it lands in PR 71. Why: the branch is already theirs.
- **Keep it as my own** (`own`): build as usual, and I open and merge the pull request myself.
- **Stop** (`stop`): change nothing and end the walk here.
```

A script that prints a card uses the same shape: a `Card:` line, then numbered options, each with what happens.

`scripts/kit-lint.py` reads only `Card:` lines and the option lines right under them, so prose is not checked. It flags a question with brackets, an option that does not say what happens, a Recommended option that is not first, a kit term from its short list, options listed inline instead of in a `Card:` block, a question with two question marks, and an option that corrects itself mid-sentence (1.190.0). Since 1.200.0 it checks every skill. Whether an option really says what happens still needs a person to read it.

## Walk card rules (1.196.0)

These hold for the cards inside the spec walk: tighten-spec, tighten-plan, tighten-and-plan, the ready check and its reopen cards, and the pull-request sort and add-to-spec cards the walk asks.

1. **Batch cards: bullets above, short question, result on yes.** One background bullet per item above the card, `- P4 tasks miss the 400 path. Why: the spec names a 400 reply. Yes: add a test.` The question is short, `Tighten-plan batch: apply all 8 recommendations?`, and one `On yes:` line says what the yes does.
2. **Single cards name the item in its own words.** For example `Tick 'unit tests for the retry' (item 5, acceptance)?` The evidence and the quoted spec line go in a bullet above the card, not in the question.
3. **Plain labels.** No `A`/`B`/`C` letters and no internal names such as `tick-from-verify`, `park-risk` or `add-regression` on a card. The scripts map them: `LABELS` in `batch_offer.py`, `plan_check.py --vendor copilot` through it, and `PLAIN_LABELS` in `walk_progress.py --vendor copilot`.
4. **`suggest` only for wording findings.** A finding about behaviour, tasks, checks or prod never offers a suggestion option.
5. **Every card has a result-on-yes line** in the same place, right under the question: `On yes: …`.
6. **Still at most 4 options and one question per card.**

Left as they are, by design: the playbook card that is always asked, the open-pr card with the draft inside the question, pr-status's single closing prompt, and the meeting batch's fixed choice set.

If the host has no card tool, or allows fewer options, print the options as a numbered list with their choice words and wait for the reply.
