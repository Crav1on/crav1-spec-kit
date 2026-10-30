# Meeting to specs: **Extract**, **Match**, **Duplicate check (1.61.0)**

Part of `branches/meeting/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.107.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

## Extract

Read the input. Extract what matters:

- a requirement
- a decision
- a change
- an open question
- a bug
- exploration with no feature yet
- input that may feed several features
- technical debt being identified
- general information gathering

A source-to-target mapping, a list that may feed several features, and debt being identified are items. They are worth keeping even when no spec covers them.

Each item is a quote. Use their words. Do not replace a quote with a paraphrase. When the input shows a speaker, include the speaker. When it shows a time, include the time. Do not invent a speaker, a time, or a date.

Drop small talk and status chatter. A greeting, scheduling, thanks, a status round, and "we will take that offline" with no decision are not items. A dropped line is not numbered and is not counted as extracted. Dismiss stays for that noise when a numbered item is only noise.

## Match

Spec folders are `docs/specs/<slug>/` with a `spec.md`. Skip `_template`.

Match every extracted item. The case is one of these:

- **addition** — the quote belongs to one or more existing specs
- **answer** — the quote clearly answers an open question on an existing spec. See **Answers to open questions**.
- **new feature** — the quote is a requirement, a decision, or a change for work no existing spec covers
- **bug** — the quote is a defect in something that already ships, or a defect reported from outside
- **unclear** — the quote matters and does not land in those three

A requirement change is an addition or a new feature. A report that something is broken is a bug.

When more than one existing spec could fit, list every candidate on that item. Do not pick one candidate for the user. Do not drop an item to keep the list short. Do not drop a candidate to keep the list short.

When no spec folder exists, an item that would have been an addition is a new feature. Do not create a slug. Do not seed `docs/system/`.

## Duplicate check (1.61.0)

Before the list, run the duplicate check in this skill's `references/notes.md`. The same source again (the same mail, or the same meeting date and title) is not imported twice: say `already imported on <date> as docs/notes/YYYY-MM/<file>.md`, and ask **Reuse the existing note (Recommended)** or **Skip**. Reuse runs the items only for specs that took nothing from that note yet. Skip stops.
