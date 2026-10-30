# Meeting to specs

Minutes, a transcript, an email, or a chat thread can hold requirements that have not reached a spec yet. You extract the items that matter, match them to specs that already exist, and ask the user about every item in one batch.

Command: the fact branch of `/crav1-add-to-spec`.

This is cross-cutting. It is not a lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. The seven starter options stay unchanged.

Other skills do not run this one. Spark, specify, plan, and verify do not run it. It is not started automatically.

This is not `/crav1-bundle-to-specs`. Intake starts a landscape and new feature slugs from a dump. It does not match items against specs that already exist. This command does not create a slug and does not seed `docs/system/`.

This is not the fact branch of `/crav1-add-to-spec` used on the whole input. Add-to-spec takes one piece of new information for one existing spec. This command extracts many items, matches them, and hands one kept addition to that skill.

This is not `/crav1-what-do-we-know-about-this`. A question about the status of one feature, slice, or resource, with no minutes, email, or chat, is that command. This command takes minutes, a transcript, an email, or a chat thread.

## Input

Everything after the fact branch of `/crav1-add-to-spec`, and every `@`, is the input. Minutes, a transcript, a Teams or Zoom export, an email, or a pasted Slack or Teams chat thread are the same input. An email or a chat thread is accepted as well as minutes or a transcript. There is no required shape.

If the message has no input and no `@`, stop. Ask with options only. Use the questions tool when it is available. The options are only:

1. **Paste the minutes, transcript, email, or chat in the next message**
2. **@ a file** (minutes, a transcript, a Teams or Zoom export, an email, or a chat thread)

Stop until the user picks and the input is in the chat. Do not scan the repo for a file. Do not guess a file. Do not ask for a typed path.

## Kind and date

The kind comes from what the input shows. Do not guess.

- `meeting` — minutes, a transcript, or a Teams or Zoom export
- `email` — email headers such as From, To, Subject, or Sent
- `chat` — a pasted Slack or Teams chat thread, with chat-style handles and timestamps

If the kind is not clear, ask once per run. Options only. Use the questions tool when it is available. The options are only:

1. **Meeting**
2. **Email**
3. **Chat**

Stop until the user picks. Do not extract until the kind is known. One kind for the run. It applies to every item.

The date comes from the input. The meeting date, an email's sent date, or one date the chat thread shows for the whole thread is the date. Do not invent a date. Do not pick one message time and call it the date.

When the input shows no date, ask once per run whether to add one. Options only. Use the questions tool when it is available. The options are only:

1. **Give a date**
2. **Skip**

Stop until the user picks. A date the user gives is used. If they pick give a date and the reply has no date, stop until they give one. Skip means no date. Do not ask again after skip. One date for the run, or none. It applies to every item.

## Extract

Read this skill's `branches/meeting/references/extract-and-match.md` now, before you go on.

## Match

This step is in the same file, this skill's `branches/meeting/references/extract-and-match.md`.

## Duplicate check (1.61.0)

This step is in the same file, this skill's `branches/meeting/references/extract-and-match.md`.

## Answers to open questions

Read this skill's `branches/meeting/references/open-question-answers.md` now, before you go on.

## Recommendation

This step is in the same file, this skill's `branches/meeting/references/open-question-answers.md`.

## Build state

Read this skill's `branches/meeting/references/build-state.md` now, before you go on.

## The list

Show every item before the first question. Number `M1`, `M2`, … On a new run, start at `M1`. Nothing is dropped to keep the list short.

```text
M1 — addition
Quote: "<their words>"
Speaker: <name, or omitted>
Time: <time, or omitted>
Source: <kind> <date>, or <kind>
Fits: docs/specs/<slug>/ — <title line when spec.md has one>
Also fits: docs/specs/<slug>/ — <title line>
Answers: "<question>" on docs/specs/<slug>/
Possible answer to: "<question>" on docs/specs/<slug>/. The question stays open.
State: <state>. <short reason that names the evidence>.
Recommended: Keep.
```

The kind is `meeting`, `email`, or `chat`. When the run has a date, `Source` is `<kind> <date>` (for example `email 2026-10-06`). When it does not, `Source` is `<kind>` (for example `meeting`). Omit `Speaker` and `Time` when the input does not show them. Omit `Also fits` when only one spec fits. Omit `State` when `Fits` is `none`. A new feature, a bug, or an unclear item uses `Fits: none` when no spec fits. Omit `Answers` and `Possible answer to` when the item answers no open question. An `answer` item shows `Linked without a question.` instead of a recommendation.

On every later turn, list every item again. Mark the ones already answered `kept`, `left`, or `dismissed`. The ones not answered stay on the list. Do not remove a line to keep the list short.

## In one batch (1.70.0)

Read this skill's `branches/meeting/references/one-batch.md` now, before you go on.

## The full note (1.61.0)

Read this skill's `branches/meeting/references/after-the-list.md` now, before you go on.

## After each answer

This step is in the same file, this skill's `branches/meeting/references/after-the-list.md`.

## Stop

The only files this command writes are `docs/sources/YYYY-MM-DD-<slug>/` for a source a kept addition or a note quotes, the full note `docs/notes/YYYY-MM/YYYY-MM-DD-<slug>.md` and the generated indexes, a `.gitattributes` line after a yes, and the transfer data policy after a yes, as the imported-sources convention says. Do not write the source folder for a leave, a dismiss, a kept new feature, or a kept bug. Do not write a note for those. Do not write `docs/system/`, a spec, `plan.md`, `tasks.md`, `verify.md`, `explore.md`, `docs/environments/marks.md`, or a dismissals file. Do not commit. Do not push. Do not open a pull request.

Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, the repos and bundle branch of `/crav1-existing-to-specs`, `/crav1-plan-from-spec`, `/crav1-build-tasks`, `/crav1-verify-build-against-spec`, `/crav1-fix-bug`, the verify gaps branch of `/crav1-fix-build-gaps`, or `/crav1-finalize-commit`.

## Hard rules

- No input and no `@`: stop. Options only. Do not guess a file. An email or a chat thread is accepted as well as minutes or a transcript.
- The kind comes from what the input shows: `meeting`, `email`, or `chat`. Do not guess. If it is not clear, ask once: meeting, email, or chat.
- The date comes from the input. Do not invent one. If the input shows no date, ask once: give a date, or skip. Skip means no date.
- One kind and one date for the run. They apply to every item. The chat `Source` line is `<kind> <date>`, or `<kind>`. The spec `Source:` line is the source folder, written by the fact branch of `/crav1-add-to-spec` after the folder exists.
- Extract requirements, decisions, changes, open questions, and bugs. Each item is a quote. Include speaker and time when the input shows them.
- Read spec open questions first. A clear answer is linked without a question through the fact branch of `/crav1-add-to-spec`. An unclear or partial answer is shown as a possible answer and the question stays open. A question the input shows being asked gets an `Asked:` mark with the input's date. Follow `crav1-add-to-spec` `references/open-questions.md`. Answers that change spec lines name `/crav1-resolve-open-questions`. Do not run it.
- Drop small talk and status chatter. A dropped line is not an item.
- Match every item. Cases: addition, new feature, bug, or unclear. When more than one existing spec could fit, list every candidate.
- An item that matches a spec gets one `State:` line in the item block and in the question. `Fits: none` gets no state line. The line is informational. It is not written and it is not quote text.
- Every item stays listed. Nothing is dropped to keep the list short.
- One item at a time: keep, leave, or dismiss. Mark Leave as `(Recommended)` when the item fits no spec; it stays in the full note. Do not add an accept-all question. This skill does not have that pattern.
- Every run writes one full note `docs/notes/YYYY-MM/YYYY-MM-DD-<slug>.md` by source date, and regenerates the indexes. The same source again is not written twice.
- Dismiss is for this run only, and for noise. Start fresh on every run. Do not write a dismissals file. Do not remember a dismiss across runs.
- A kept addition goes to that spec through the fact branch of `/crav1-add-to-spec`. Before that handoff, when the source is not yet imported, follow this skill's `references/sources.md` (plugin: sibling `skills/crav1-add-to-spec/references/sources.md`). Its personal-data and secrets check is in that file; flagged items, the transfer data policy, and the one question are in `references/sources-flagged.md`, and a mail's images in `references/sources-mail.md` and `references/sources-binary.md`, all in `crav1-add-to-spec`. Write the source folder once. Pass the kind, the date, and that folder. The quote starts with `From <kind> <date>.` when there is a date, otherwise `From <kind>.` The impact check still runs there, including research, following this skill's `references/research-stale.md` (plugin: sibling `skills/crav1-add-to-spec/references/research-stale.md`). This skill does not run that check a second time. It does not write the stale block. Do not commit.
- A kept new feature names `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, or `/crav1-bundle-to-specs`. Do not run it. Do not create a slug. Do not write the source folder here. Do not write a note here. That next command follows the imported-sources convention when it quotes the source.
- A kept bug names `/crav1-fix-bug`. Do not run it.
- This command does not write a spec. The files it writes are the source folder for a kept addition or a note, the full note and the generated indexes, a `.gitattributes` line after a yes, and the transfer data policy after a yes. It does not commit. It never writes a secrets choice into that rule.
- Do not start Specify, Plan, or Build. Do not plan, implement, or commit.
- Later skill. Not a starter option. Asking for startup options names only the seven and does not run this command.
