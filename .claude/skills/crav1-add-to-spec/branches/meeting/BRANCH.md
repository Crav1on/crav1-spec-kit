# Meeting to specs

Minutes, a transcript, an email, or a chat thread can hold requirements that have not reached a spec yet. You extract the items that matter, match them to specs that already exist, and ask the user about one item at a time.

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

## Already noted

Read `docs/notes/` before the list, when that folder exists. Skip `_template`. Compare each item's quote to the quote in each note. The same words are the same item. The `From` label is not part of that compare.

When the quote is already in a note, the item shows `Already noted: docs/notes/<file>.md`. Do not offer it as a new note. Picking Note does not write a second file.

## Answers to open questions

Read `## Open questions` on every spec folder (skip `_template`), with the records under each question. Follow `crav1-add-to-spec` `references/open-questions.md` (drop-in: `.claude/skills/crav1-add-to-spec/references/open-questions.md`; plugin: sibling `skills/crav1-add-to-spec/references/open-questions.md`). Match by meaning. Matching works whether the question is asked, pending, or not marked.

- **Clear answer.** The item states the fact or the decision a spec open question asks for. The case is `answer`. The item shows `Answers: "<question>" on docs/specs/<slug>/` and `Linked without a question.` It is not asked keep, leave, dismiss, or note. Hand it to the fact branch of `/crav1-add-to-spec` as an answer link (see **Answer** under Keep). When it would change a spec line, also show `Then: /crav1-tighten-spec, then /crav1-resolve-open-questions for <slug>.`
- **Unclear or partial.** The item keeps its own case. It also shows `Possible answer to: "<question>" on docs/specs/<slug>/. The question stays open.` It is asked one at a time like any other item. Nothing is linked.
- **Asked in this input.** The input shows someone asking a spec open question. That is not an item. List it under `Asked in this <kind>` before the items, one line per question, with the spec. Its `Asked:` mark is written through the same handoff, with the date of this input. That date replaces a `Pending:` line, and an `Asked:` line from the user's yes, for the same person.

After a meeting, every question that was asked or pending for that meeting and got no clear answer goes back to open. Its asked mark stays, as the reference file says.

## Recommendation

Show one recommendation on the item and in the question. In the question, the recommended option comes first and its label ends with ` (Recommended)`; the question text does not repeat it. Do not pick for the user.

- **Keep** — the quote is a decision, a clarification, information, or an answer for an existing spec.
- **Note** — the quote is worth keeping, and it is not those. Exploration with no feature yet, input that may feed several features, technical debt, and general information gathering are this case. A mail that maps tables and views when no spec covers it is this case. The item line is `Recommended: Note.`
- **Dismiss** — the quote is only noise: a greeting, scheduling, or thanks.

This skill asks one item at a time. It does not have an accept-all question. Do not add one. The recommendation is the suggested answer.

## Build state

An item that matches an existing spec gets one line. An item with `Fits: none` gets no state line.

Read the spec on `Fits:`. When `Also fits` is present, read each of those specs too. For each one, read in this order. Skip a file that is not there. A missing file is not a search.

1. `docs/specs/<slug>/spec.md`, including `## Match` when that heading is there
2. `plan.md` in that folder
3. `tasks.md` in that folder, the checkboxes
4. `verify.md` in that folder, when the file is present

Judge in this order. Stop at the first that fits.

1. **built** — `spec.md` already states the whole item as present, including a `## Match` line that covers it as done, or a checked task (`[x]`) covers the whole item, and no `verify.md` row for that coverage fails.
2. **partly built** — part of the item is covered that way and part is not. A `verify.md` fail on one part is this state. The reason names which part.
3. **planned** — `plan.md` describes the item, or an open task (`[ ]`) covers it, and it is not done.
4. **not built** — that `spec.md`, `plan.md`, and `tasks.md` do not cover the item. A failed `verify.md` row that is the only coverage is this state. Name that row.

A goal, a requirement, or an unchecked acceptance line that only says the item should exist is not built by itself.

When those files do not settle the state, one quick read-only look at the code that spec or plan names. A path in `spec.md`, including `## Match`, or in `plan.md`, is the code to open. Do not open a file they do not name. Do not search the codebase. When they name no path, do not look. A clear state from the files above is settled. Do not open code to overturn it.

A state that rests on that code, or a state that is still uncertain after the read, ends the reason with `(inference, not in the docs)`. A state the spec, plan, tasks, or verify file shows does not get that label. Never invent a file, a task number, a checkbox, or a quote.

One line:

```text
State: <state>. <short reason that names the evidence>.
```

Example: `State: partly built. Dev container done (task 4 checked); prod not in tasks.md.`

When more than one spec fits, the state word is the state of the spec on `Fits:`. The reason names each other spec when its state differs, with that spec’s path.

The line is informational. It does not change keep, leave, dismiss, or note. It is not written. It is not part of the quote handed to the fact branch of `/crav1-add-to-spec`. It is not part of the quote written to a note.

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
Recommended: Note.
Already noted: docs/notes/<file>.md
```

The kind is `meeting`, `email`, or `chat`. When the run has a date, `Source` is `<kind> <date>` (for example `email 2026-10-06`). When it does not, `Source` is `<kind>` (for example `meeting`). Omit `Speaker` and `Time` when the input does not show them. Omit `Also fits` when only one spec fits. Omit `State` when `Fits` is `none`. A new feature, a bug, or an unclear item uses `Fits: none` when no spec fits. Omit `Already noted` when the quote is not already in `docs/notes/`. Omit `Answers` and `Possible answer to` when the item answers no open question. An `answer` item shows `Linked without a question.` instead of a recommendation.

On every later turn, list every item again. Mark the ones already answered `kept`, `left`, `dismissed`, or `noted`. The ones not answered stay on the list. Do not remove a line to keep the list short.

## One at a time

Ask about one item. Use the questions tool when it is available. The question text names the item and the spec when one fits, then the same `State` line that is on the item. It does not say `Recommendation:`. The options are only these four. The recommended one comes first with ` (Recommended)` at the end of its label; the others keep this order:

- **Keep**
- **Leave**
- **Dismiss**
- **Note — keep it in the repo without tying it to a spec yet.**

```text
M1: dev and prod containers. Add this to <slug>?
State: partly built. Dev container done (task 4 checked); prod not in tasks.md.
```

Options: **Keep (Recommended)**, Leave, Dismiss, Note.

```text
M1: source-to-target mapping of the SQL tables. Note this, without a spec?
```

Options: **Note — keep it in the repo without tying it to a spec yet. (Recommended)**, Keep, Leave, Dismiss.

When `Fits` is `none`, the question has no `State` line. The options stay Keep, Leave, Dismiss, and Note.

Stop until the user picks. Do not write before that reply. Do not apply the next item in the same turn.

A batch (`M1 keep, M2 note`) applies only the items named in that batch, in order. An item with no mark stays unanswered. Do not treat silence as dismiss. When a keep needs a further question, ask that question and do not apply the rest of the batch in that turn. Note does not ask what kind of note it is. When Note must still run the imported-sources questions because the source folder is not written yet, ask those and do not apply the rest of the batch in that turn. When those questions are not needed, Note writes and the batch continues.

### Keep

Follow the case already on that item.

**Addition.** When one spec fits, and this source is not yet imported, follow the imported-sources convention before the handoff (drop-in: `.claude/skills/crav1-add-to-spec/references/sources.md`; plugin: sibling `skills/crav1-add-to-spec/references/sources.md`). That check flags personal data with a keep or redact recommendation. An item it cannot place has no recommendation and is asked one at a time. Secrets are redacted, by kind only, and are never a choice. When no transfer data policy exists, it asks once, then may write the rule after a yes. Claude Code project: `.claude/rules/crav1-transfer-data-policy.md`. It never writes a secrets choice into that file. For a mail, it lists each embedded image, inline or attached. It recommends convert to text when the image is a diagram, a table, or text that can be reproduced exactly, and compress otherwise. It asks once. Nothing is written to the source folder until every image has an answer. Auto-accept applies to those recommendations only when the transfer data policy clearly covers them. Write `docs/sources/YYYY-MM-DD-<slug>/` once for that source. Do not commit. A later kept addition from the same source reuses that folder. Do not ask those questions again. The policy questions are once per repo, as that file says.

Then hand the quote to the fact branch of `/crav1-add-to-spec` for that slug. Pass the quote after any redaction that convention made. Pass the kind and the date for this run, and the source folder. When there is no date, pass the kind and the folder. When the item is already noted, pass that note path so the note gets `Used by <slug>`. Do not pass the `State` line. It is not quote text. Do not pass the recommendation. Follow only the handoff **From the meeting branch of /crav1-add-to-spec** in that skill (drop-in: `.claude/skills/crav1-add-to-spec/SKILL.md`; plugin: sibling `skills/crav1-add-to-spec/SKILL.md`). One item. Then stop that handoff. The impact check still runs there, including research. That check follows `crav1-add-to-spec` `references/research-stale.md` (drop-in: `.claude/skills/crav1-add-to-spec/references/research-stale.md`; plugin: sibling `skills/crav1-add-to-spec/references/research-stale.md`). This skill does not run that check a second time. It does not write the stale block. Do not write the spec in this skill. Do not create a slug.

When more than one spec fits, ask which one before the handoff. Options only. One option per candidate, plus **Treat as a new feature**. Do not ask the user to type a slug. Stop until the user picks. A picked spec gets the addition handoff. Treat as a new feature follows the new-feature rule below.

**New feature.** Name the next command. Do not run it. Do not create a slug. Do not seed `docs/system/`. Do not write the source folder here.

- One kept new feature that is one or two sentences: `/crav1-spark-to-spec`
- One kept new feature that is a pile of ideas and technical hunches: `/crav1-ideas-to-spec`
- Two or more kept new features: `/crav1-bundle-to-specs`

When a later keep brings the new-feature count to two or more, the next command for those items is `/crav1-bundle-to-specs`. Say that in the recap. Do not run it.

**Bug.** Name `/crav1-fix-bug`. Do not run it. Do not name the lane. Do not edit code. Do not write `explore.md`.

**Unclear.** Ask with options only. One option per existing spec folder, labeled `docs/specs/<slug>/` and the title line when `spec.md` has one, plus **Treat as a new feature**. Do not ask the user to type a slug. Stop until the user picks. A picked spec gets the addition handoff. Treat as a new feature follows the new-feature rule. When no spec folder exists, treat the keep as a new feature and do not ask for a slug.

### Answer

An `answer` item is not asked. When this source is not yet imported, follow the imported-sources convention first, exactly as for a kept addition. Then hand it to the fact branch of `/crav1-add-to-spec` for that slug. Follow only the handoff **From an import: answer links and asked marks** in that skill. Pass the question, the quote after any redaction, who answered, the kind, the date, and the source folder. Pass the `Asked in this <kind>` lines for that spec in the same handoff. When a spec has only asked lines and no answer, hand those lines alone. They do not need a source folder. Do not write the spec in this skill. When the answer would change a spec line, name `/crav1-resolve-open-questions` for that slug. Do not run it.

When the imported-sources check asks a question, that question is this turn. Then continue with the next item.

### Note

Write the note. Do not ask what kind of note it is. Do not hand the quote to the fact branch of `/crav1-add-to-spec`. Do not create a slug. Do not name a starter.

When the item is already noted, write nothing. Say the path. Do not write a second file.

When the quote is not already noted, follow **Note file** below. Then stop that write. The next unanswered item is the next question.

### Leave

Write nothing. The item stays listed as left for this run. The next run starts fresh and can offer it again.

### Dismiss

Write nothing. Dismiss is for this run only. Do not write a dismissals file. Do not record the quote on a spec. The next run starts fresh and can offer the item again. Do not remember a dismiss across runs.

## Note file

A note is not owned by one spec. The home is `docs/notes/` in the product repo.

Create `docs/notes/` and `docs/notes/index.md` when they are missing. The shapes are this skill’s `assets/note.md` and `assets/index.md` (same files as `docs/notes/_template/note.md` and `docs/notes/_template/index.md`; drop-in: `.claude/skills/crav1-add-to-spec/branches/meeting/assets/`; plugin: this skill’s `assets/`).

One file per note: `docs/notes/YYYY-MM-DD-<slug>.md`. `YYYY-MM-DD` is the date this run already has. Do not invent a date. When the run has no date, the file is `docs/notes/undated-<slug>.md`. `<slug>` is a short name from the subject or the quote. Lowercase. Hyphens. Do not put a person's name in the slug. A second note on the same day gets its own slug. When that file already exists and the quote is different, pick another slug. Do not overwrite a note.

The note file has:

- a title
- the date, or `not shown` when the run has no date
- the quote, verbatim. It starts with `From <kind> <date>.` when there is a date, otherwise `From <kind>.` Keep the speaker and the time in the quote when the input showed them. Do not paraphrase.
- `Source: docs/sources/YYYY-MM-DD-<slug>/` when the input was imported. When it was not, omit that line.
- `## Used by`, with nothing under it

When the input was imported and the source folder is not written yet, follow the imported-sources convention before the note (drop-in: `.claude/skills/crav1-add-to-spec/references/sources.md`; plugin: sibling `skills/crav1-add-to-spec/references/sources.md`). That check flags personal data with a keep or redact recommendation. An item it cannot place has no recommendation and is asked one at a time. Secrets are redacted, by kind only, and are never a choice. When no transfer data policy exists, it asks once, then may write the rule after a yes. For a mail, it lists each embedded image and asks once. Nothing is written until those answers are in. Write `docs/sources/YYYY-MM-DD-<slug>/` once. A later note from the same source reuses that folder. Do not ask those questions again. Those questions are the imported-sources convention. They are not a question about what kind of note this is.

`docs/notes/index.md` gets one line for the new note: title, date, status `open`, and an empty used-by cell. The title links to the file. One line looks like `| [Source to target mapping](2026-10-06-source-to-target-mapping.md) | 2026-10-06 | open | |`. When the date is not shown, the date cell says `not shown`. Do not rewrite another row.

Do not commit.

## After each answer

Recap that one item: answer linked, kept as addition, kept as new feature, kept as bug, noted, left, or dismissed. Name the spec when a handoff ran. Name the note path when a note was written, or the path when it was already noted. Name the next command when one was named. Do not run that command.

When the addition handoff asks apply or leave, or asks whether to mark research stale, or asks to draft a revisit request, that question is this turn. Do not ask the next meeting item in that same turn.

Then ask the next unanswered item.

When every item has an answer, stop. Repeat the full list with kept, left, or dismissed on each line. Then the counts:

```text
Extracted: <n>
Answers linked: <n>
Possible answers shown: <n>
Asked marks: <n>
Kept as addition: <n>
Kept as new feature: <n>
Kept as bug: <n>
Noted: <n>
Left: <n>
Dismissed: <n>
Handoffs: docs/specs/<slug>/, or none
Notes: docs/notes/<file>.md, or none
Named, not run: <commands>, or none
```

Then the answer summary from the reference file: each answer linked, each possible answer left open, each asked mark and where its date came from, and each `/crav1-resolve-open-questions` named.

When the fact branch of `/crav1-add-to-spec` changed an existing spec, name the next steps from the **New information on an existing slice** route (`docs/reference/workflow.md#new-info`) for that slug: `/crav1-tighten-spec` first, then `/crav1-resolve-open-questions`, then `/crav1-plan-from-spec` when the slice has `plan.md` or `tasks.md`. A named `/crav1-resolve-open-questions` comes after `/crav1-tighten-spec`, never before it. For the full order, name `/crav1-help next`. Do not run any of them.

When the fact branch of `/crav1-add-to-spec` changed a file, or this command wrote a source folder or a note, name `/crav1-finalize-commit`. Do not run it. Do not commit the note.

## Stop

The only files this command writes are `docs/sources/YYYY-MM-DD-<slug>/` for a source a kept addition or a note quotes, `docs/notes/YYYY-MM-DD-<slug>.md` and `docs/notes/index.md` when the user picks Note, a `.gitattributes` line after a yes, and the transfer data policy after a yes, as the imported-sources convention says. Do not write the source folder for a leave, a dismiss, a kept new feature, or a kept bug. Do not write a note for those. Do not write `docs/system/`, a spec, `plan.md`, `tasks.md`, `verify.md`, `explore.md`, `docs/environments/marks.md`, or a dismissals file. Do not commit. Do not push. Do not open a pull request.

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
- One item at a time: keep, leave, dismiss, or note. Mark Note as `(Recommended)` and list it first when the item is worth keeping and is not a decision, a clarification, information, or an answer for an existing spec. Do not add an accept-all question. This skill does not have that pattern.
- Note writes `docs/notes/YYYY-MM-DD-<slug>.md` and one index line. It does not ask what kind of note it is. Read `docs/notes/` first. An item already noted is shown as already noted and is not written again.
- Dismiss is for this run only, and for noise. Start fresh on every run. Do not write a dismissals file. Do not remember a dismiss across runs.
- A kept addition goes to that spec through the fact branch of `/crav1-add-to-spec`. Before that handoff, when the source is not yet imported, follow `.claude/skills/crav1-add-to-spec/references/sources.md` (plugin: sibling `skills/crav1-add-to-spec/references/sources.md`). That check recommends keep or redact, redacts secrets, and may write the transfer data policy after a yes. For a mail, it lists each embedded image, inline or attached, recommends convert to text or compress, and asks once. Nothing is written to the source folder until every image has an answer. Auto-accept applies to those recommendations only when the transfer data policy clearly covers them. Write the source folder once. Pass the kind, the date, and that folder. The quote starts with `From <kind> <date>.` when there is a date, otherwise `From <kind>.` The impact check still runs there, including research, following `.claude/skills/crav1-add-to-spec/references/research-stale.md` (plugin: sibling `skills/crav1-add-to-spec/references/research-stale.md`). This skill does not run that check a second time. It does not write the stale block. Do not commit.
- A kept new feature names `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, or `/crav1-bundle-to-specs`. Do not run it. Do not create a slug. Do not write the source folder here. Do not write a note here. That next command follows the imported-sources convention when it quotes the source.
- A kept bug names `/crav1-fix-bug`. Do not run it.
- This command does not write a spec. The files it writes are the source folder for a kept addition or a note, the note file and `docs/notes/index.md` when the user picks Note, a `.gitattributes` line after a yes, and the transfer data policy after a yes. It does not commit. It never writes a secrets choice into that rule.
- Do not start Specify, Plan, or Build. Do not plan, implement, or commit.
- Later skill. Not a starter option. Asking for startup options names only the seven and does not run this command.
