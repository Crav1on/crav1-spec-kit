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

Print a findings table in that same reply, immediately before the card. The card is never asked without it. Columns, in order: Id, Issue, Options, Recommendation. One row per item. The issue is one line. Options are the letters or words for that item. Recommendation is the choice `yes` will apply, such as `A add a test` or `keep`.

The card text is self-contained. It names every item as `<id> <one-line issue>: <recommendation>`, for example `P4 tasks miss the 400 path: A add a test`. It still makes sense if the table scrolled away. The question text is the `Card:` line from the command below. `yes (Recommended)` applies every recommendation on that line. A skill whose options are already **Accept all recommendations (Recommended)** and **Go through them one by one** keeps those labels. The question text still names every item. Typed changes stay on the card's free-text answer.

Never write `table above`, `the table recommends`, or `as in the table` unless that table is in this reply. Do not use those phrases on the card. The card does not point at the table. It repeats each item. Never ask the card without the table.

Build the table and the card with one command. Print its stdout in the reply. The table is the first part. The card question is the `Card:` line, word for word. If the command fails, or it prints no table, do not ask the card.

`<interpreter> -X utf8 <skill crav1-tighten-plan>/scripts/batch_offer.py --title "Tighten-plan batch" --items <file>`

`<file>` is JSON, a list of objects with `id`, `issue`, `options`, and `recommendation`. The interpreter is [Running a kit script](running-scripts.md). On Windows it is `python`. Elsewhere it is `python3`. Set `PYTHONUTF8=1` and pass `-X utf8`.

A card that is one yes for one action, such as post this text or run this script, is not this batch. One question per item, when that question already names the item and the recommendation, is not this batch. Do not collapse those questions into a card that says `table above`. Collapsing them onto one card makes it this batch.
