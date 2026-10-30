---
name: crav1-show-or-ask-open-questions
description: >-
  Use when the user wants an overview of open questions across specs, or to
  ask a person, spec, or topic about them. Drafts a mail, agenda, or chat
  message (never sent), then records who was asked. Does not plan, implement,
  or commit.
disable-model-invocation: true
icon: message-circle-question
color: purple
---

# Ask open questions

## Opening question (1.56.0)

This skill was `/crav1-ask-open-questions`. Ask one question, with the questions tool when it is available:

1. **Show.** An overview of every open question across the specs. Read-only. See **Show** below.
2. **Ask.** Draft questions for one person, one spec, or one topic. Follow the rest of this file from **Input** onward (the rules that were `/crav1-ask-open-questions`).

Skip the question when the message says which: "show", "overview", "what is still open", or "who did we ask" is 1; a person, a channel, or "draft" is 2.

## Choice words

Exact words for bots and scripted runs. There are no `--flags`.

- Show or ask: `show` / `ask`.
- After `ask`: `research` drafts a research request; read `references/research.md`.

When the invocation contains one of these words (for example `/crav1-show-or-ask-open-questions show`), take that choice and do not ask. This holds for a person, a bot, or a headless run.

When a choice is missing and the run is headless or started by a bot (no person in the chat to answer), do not guess. Stop and name the valid words, for example: `Missing choice. Use one of: show, ask.`

## Show

Read `## Open questions` in every `docs/specs/<slug>/spec.md` (skip `_template`), with the lines under each question, as `crav1-add-to-spec` `references/open-questions.md` describes. Write nothing. Draft nothing. Send nothing.

- One section per spec with open questions, then one line per question that has no `Answered:` line: its `Q#` (document order, display only, never written; 1.84.0), the question in plain words, then its marks: `Asked <date>, <channel> to <who>`, `Pending since <date> for <who>`, `Blocks T2, T4`, or `not asked yet`.
- An answered question still waiting on `/crav1-resolve-open-questions` is listed under **Answered, not resolved**.
- End with counts: open, asked, pending, not asked, answered not resolved; then by person: who has how many asked or pending.
- Next: `/crav1-show-or-ask-open-questions` with **Ask** for the ones not asked yet, or `/crav1-resolve-open-questions` for the answered ones. Do not run them.


The specs hold open questions that only someone outside the kit can answer, such as a partner, a customer, or a colleague. You gather those questions and draft them so the user can ask them by mail, in a meeting, or in a chat. You record whether they were asked. You never send anything.

Command: `/crav1-show-or-ask-open-questions`.

This is cross-cutting. It is not a lane. It may run from any lane. It does not move work into Specify, Plan, or Build.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. That ask names the list. It does not run this command.

This is not `/crav1-resolve-open-questions`. Resolve walks the questions with the user and writes the decisions into the spec. This command drafts the questions for someone else and writes only the asked and pending marks.

The record format, pending, answer links, and the asked-on date are shared with the import skills. Follow `crav1-add-to-spec` `references/open-questions.md` (drop-in: `.claude/skills/crav1-add-to-spec/references/open-questions.md`; plugin: sibling `skills/crav1-add-to-spec/references/open-questions.md`).

## Input

Everything after the command, and every `@`, is the input. The user names one of these:

- **A person or a group.** For example `Dana`, or `Finance`. Questions waiting for that person, and questions routed via that person, are theirs. "Finance via Dana" is a question for Dana.
- **A spec.** An `@` of a spec folder or its `spec.md`, or its title.
- **A topic.** A few words, such as `static IP` or `mTLS`.

They may also name the output kind and the language.

When the input names none of person, spec, or topic, stop and ask. Options only. The options are:

1. **A person** — gather the questions that person can answer. Reply with the name.
2. **A spec** — gather every open question on one spec. Reply with an `@` of the spec, or pick it.
3. **A topic** — gather open questions on that subject across all specs. Reply with the words.

## Pending first

Read `references/asked.md` ("Pending first") only when questions are already marked pending.

## Gather

Collect every open question that fits the selection.

Person, spec, topic, branch, and pull request (`pr71`, `#71`) follow `crav1-add-to-spec` `references/scope.md` (drop-in: `.claude/skills/crav1-add-to-spec/references/scope.md`; plugin: sibling `skills/crav1-add-to-spec/references/scope.md`).

Skip a question that already has a clear `Answered:` line. Say how many were skipped and why. Skip a question with an `Asked:` line for this person unless the user asks to ask again. Say how many were skipped and when they were asked.

Every question that fits stays listed. Nothing is dropped to keep the list short. When the same question sits on two specs, it is one question in the draft, and both specs get the mark.

Show the gathered list in the chat, numbered, each with its spec path. That list is for the user. The draft is not.

## Output kind

Read `references/drafting.md` ("Output kind") only when you write the draft.

## Language

Read `references/drafting.md` ("Language") only when you write the draft.

## Write the draft

Read `references/drafting.md` ("Write the draft") only when you write the draft.

## Asked?

Read `references/asked.md` ("Asked?") only when you ask whether the draft was sent.

## Parked and retired specs (1.60.0)

Read `references/asked.md` ("Parked and retired specs (1.60.0)") only when a spec is parked or retired.

## Stop

The only file this command writes is `docs/specs/<slug>/spec.md`, and in that file only the `Asked:` and `Pending:` lines under open questions, and the transfer data policy after a yes, as the personal-data check says. It does not write `docs/system/`, `plan.md`, `tasks.md`, `verify.md`, or a draft file. It does not send, post, or reply. It does not commit, push, or open a pull request.

End with:

- the draft kind, the language, and who it is for
- how many questions, from which specs (paths, for the user only)
- how many were skipped, and why
- which marks were written, or that none were
- when a mark was written, name `/crav1-finalize-commit`. Do not run it.
- when answers come back, `/crav1-add-to-spec` for a mail, minutes, a transcript, or a chat, or `/crav1-add-to-spec` for a larger dump. Those link the answers. Do not run them.

## Hard rules

- No person, spec, or topic: stop and ask. Options only.
- Pending questions come first. Mark as sent, keep pending, or drop the mark.
- Gather every question that fits. Nothing is dropped to keep the list short.
- Four kinds: mail, meeting agenda, chat message, meeting questions. Meeting questions lists all of them.
- Numbered, grouped by topic in plain words, with enough context.
- No spec slug, path, file, or question id in the draft.
- English by default, or the language named.
- The personal-data and secrets check runs on the draft.
- Nothing is sent.
- Yes writes `Asked:`. No writes nothing. Pending writes `Pending:` (ask research: no Asked? question). Only under the questions in the draft.
- Do not plan, implement, or commit.
