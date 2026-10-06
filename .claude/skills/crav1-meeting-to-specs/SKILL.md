---
name: crav1-meeting-to-specs
description: >-
  Extract requirements, decisions, changes, open questions, and bugs from
  minutes or a transcript. Match each quote to existing specs. The user
  takes them one at a time: keep, leave, or dismiss. Dismiss is for this
  run only. A kept addition goes to that spec through /crav1-add-to-spec.
  A kept new feature or bug only names the next command. Writes nothing
  itself. Does not start Specify, Plan, or Build. Cross-cutting. Not a
  starter option.
disable-model-invocation: true
icon: messages-square
color: purple
---

# Meeting to specs

Minutes and transcripts hold requirements that have not reached a spec yet. You extract the items that matter, match them to specs that already exist, and ask the user about one item at a time.

Command: `/crav1-meeting-to-specs`.

This is cross-cutting. It is not a lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. The seven starter options stay unchanged.

Other skills do not run this one. Spark, specify, plan, and verify do not run it. It is not started automatically.

This is not `/crav1-intake-to-specs`. Intake starts a landscape and new feature slugs from a dump. It does not match items against specs that already exist. This command does not create a slug and does not seed `docs/system/`.

This is not `/crav1-add-to-spec` used on the whole meeting. Add-to-spec takes one piece of new information for one existing spec. This command extracts many items, matches them, and hands one kept addition to that skill.

This is not `/crav1-whats-known-about`. A question about the status of one feature, slice, or resource, with no minutes, is that command. This command takes minutes or a transcript.

## Input

Everything after `/crav1-meeting-to-specs`, and every `@`, is the minutes or the transcript. A file, a paste, or a Teams or Zoom export is the same input. There is no required shape.

If the message has no minutes and no `@`, stop. Ask with options only. Use the questions tool when it is available. The options are only:

1. **Paste the minutes or transcript in the next message**
2. **@ a file** (minutes, a transcript, or a Teams or Zoom export)

Stop until the user picks and the minutes are in the chat. Do not scan the repo for a transcript. Do not guess a file. Do not ask for a typed path.

## Extract

Read the minutes. Extract only what matters for features:

- a requirement
- a decision
- a change
- an open question
- a bug

Each item is a quote. Use their words. Do not replace a quote with a paraphrase. When the transcript shows a speaker, include the speaker. When it shows a time, include the time. Do not invent a speaker, a time, or a date.

Drop small talk and status chatter. A greeting, scheduling, a status round, and "we will take that offline" with no decision are not items. A dropped line is not numbered and is not counted as extracted.

## Match

Spec folders are `docs/specs/<slug>/` with a `spec.md`. Skip `_template`.

Match every extracted item. The case is one of these:

- **addition** — the quote belongs to one or more existing specs
- **new feature** — the quote is a requirement, a decision, or a change for work no existing spec covers
- **bug** — the quote is a defect in something that already ships, or a defect reported from outside
- **unclear** — the quote matters and does not land in those three

A requirement change is an addition or a new feature. A report that something is broken is a bug.

When more than one existing spec could fit, list every candidate on that item. Do not pick one candidate for the user. Do not drop an item to keep the list short. Do not drop a candidate to keep the list short.

When no spec folder exists, an item that would have been an addition is a new feature. Do not create a slug. Do not seed `docs/system/`.

## The list

Show every item before the first question. Number `M1`, `M2`, … On a new run, start at `M1`. Nothing is dropped to keep the list short.

```text
M1 — addition
Quote: "<their words>"
Speaker: <name, or omitted>
Time: <time, or omitted>
Source: meeting <date>, or meeting
Fits: docs/specs/<slug>/ — <title line when spec.md has one>
Also fits: docs/specs/<slug>/ — <title line>
```

Omit `Speaker` and `Time` when the transcript does not show them. Omit `Also fits` when only one spec fits. A new feature, a bug, or an unclear item uses `Fits: none` when no spec fits.

On every later turn, list every item again. Mark the ones already answered `kept`, `left`, or `dismissed`. The ones not answered stay on the list. Do not remove a line to keep the list short.

## One at a time

Ask about one item. Use the questions tool when it is available. The options are only:

1. **Keep**
2. **Leave**
3. **Dismiss**

Stop until the user picks. Do not write before that reply. Do not apply the next item in the same turn.

A batch (`M1 keep, M2 leave`) applies only the items named in that batch, in order. An item with no mark stays unanswered. Do not treat silence as dismiss. When a keep needs a further question, ask that question and do not apply the rest of the batch in that turn.

### Keep

Follow the case already on that item.

**Addition.** When one spec fits, hand the quote to `/crav1-add-to-spec` for that slug. Follow only the handoff **From /crav1-meeting-to-specs** in that skill (drop-in: `.claude/skills/crav1-add-to-spec/SKILL.md`; plugin: sibling `skills/crav1-add-to-spec/SKILL.md`). One item. Then stop that handoff. The impact check still runs there. Do not write the spec in this skill. Do not create a slug.

When more than one spec fits, ask which one before the handoff. Options only. One option per candidate, plus **Treat as a new feature**. Do not ask the user to type a slug. Stop until the user picks. A picked spec gets the addition handoff. Treat as a new feature follows the new-feature rule below.

**New feature.** Name the next command. Do not run it. Do not create a slug. Do not seed `docs/system/`. Do not write a file.

- One kept new feature that is one or two sentences: `/crav1-spark-to-spec`
- One kept new feature that is a pile of ideas and technical hunches: `/crav1-ideas-to-spec`
- Two or more kept new features: `/crav1-intake-to-specs`

When a later keep brings the new-feature count to two or more, the next command for those items is `/crav1-intake-to-specs`. Say that in the recap. Do not run it.

**Bug.** Name `/crav1-fix-bug`. Do not run it. Do not name the lane. Do not edit code. Do not write `explore.md`.

**Unclear.** Ask with options only. One option per existing spec folder, labeled `docs/specs/<slug>/` and the title line when `spec.md` has one, plus **Treat as a new feature**. Do not ask the user to type a slug. Stop until the user picks. A picked spec gets the addition handoff. Treat as a new feature follows the new-feature rule. When no spec folder exists, treat the keep as a new feature and do not ask for a slug.

### Leave

Write nothing. The item stays listed as left for this run. The next run starts fresh and can offer it again.

### Dismiss

Write nothing. Dismiss is for this run only. Do not write a dismissals file. Do not record the quote on a spec. The next run starts fresh and can offer the item again. Do not remember a dismiss across runs.

## After each answer

Recap that one item: kept as addition, kept as new feature, kept as bug, left, or dismissed. Name the spec when a handoff ran. Name the next command when one was named. Do not run that command.

When the addition handoff asks apply or leave, that question is this turn. Do not ask the next meeting item in that same turn.

Then ask the next unanswered item.

When every item has an answer, stop. Repeat the full list with kept, left, or dismissed on each line. Then the counts:

```text
Extracted: <n>
Kept as addition: <n>
Kept as new feature: <n>
Kept as bug: <n>
Left: <n>
Dismissed: <n>
Handoffs: docs/specs/<slug>/, or none
Named, not run: <commands>, or none
```

When `/crav1-add-to-spec` changed a file, name `/crav1-finalize-commit`. Do not run it.

## Stop

Do not write a file. Do not copy the transcript into the repo. Do not write `docs/system/`, a spec, `plan.md`, `tasks.md`, `verify.md`, `explore.md`, `docs/environments/marks.md`, or a dismissals file. Do not commit. Do not push. Do not open a pull request.

Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-plan-from-spec`, `/crav1-implement-task`, `/crav1-complete-task`, `/crav1-verify-spec`, `/crav1-fix-bug`, `/crav1-fix-from-verify`, or `/crav1-finalize-commit`.

## Hard rules

- No minutes and no `@`: stop. Options only. Do not guess a file.
- Extract requirements, decisions, changes, open questions, and bugs. Each item is a quote. Include speaker and time when the transcript shows them.
- Drop small talk and status chatter. A dropped line is not an item.
- Match every item. Cases: addition, new feature, bug, or unclear. When more than one existing spec could fit, list every candidate.
- Every item stays listed. Nothing is dropped to keep the list short.
- One item at a time: keep, leave, or dismiss.
- Dismiss is for this run only. Start fresh on every run. Do not write a dismissals file. Do not remember a dismiss across runs.
- A kept addition goes to that spec through `/crav1-add-to-spec`. The impact check still runs there.
- A kept new feature names `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, or `/crav1-intake-to-specs`. Do not run it. Do not create a slug.
- A kept bug names `/crav1-fix-bug`. Do not run it.
- This command writes no files. The transcript is not copied into the repo. Only a quote the user keeps as an addition reaches a spec, through `/crav1-add-to-spec`.
- Do not start Specify, Plan, or Build. Do not plan, implement, or commit.
- Later skill. Not a starter option. Asking for startup options names only the seven and does not run this command.
