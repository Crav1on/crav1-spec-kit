---
name: crav1-show-or-ask-open-questions
description: >-
  Opens with one question: show the cross-spec overview of open questions
  (who was asked, when, pending drafts, Blocks lines; read-only), or ask;
  skipped when the message says which. Ask: gather the open questions for
  one person, spec, or topic and draft a mail, agenda, chat message, or
  questions to ask out loud. Numbered, grouped by topic, plain words, with
  context. The draft never names a slug, path, or question id. English by
  default. Nothing is sent. Then asks whether they were asked: yes, no, or
  pending; yes and pending mark each question in the spec, and pending
  come back first next run. The personal-data check applies. Answers are
  linked back by the import skills. Cross-cutting. Not a starter option.
  Does not plan, implement, or commit.
disable-model-invocation: true
icon: message-circle-question
color: purple
---

# Ask open questions

## Opening question (1.56.0)

This skill was `/crav1-ask-open-questions`. Ask one question, with the questions tool when it is available:

1. **Show.** An overview of every open question across the specs. Read-only. See **Show** below.
2. **Ask.** Draft questions for one person, one spec, or one topic. Follow the rest of this file from **Input** onward (the rules that were `/crav1-ask-open-questions`).

Skip the question when the message says which: "show", "overview", "what is still open", or "who did we ask" is 1; a person, a channel, or "draft" is 2. The alias `/crav1-ask-open-questions` arrives with choice 2 already made.

When the message or the files make one option the better fit, list it first and end its label with ` (Recommended)`. Otherwise keep the order above with no label.

## Choice words

Exact words for bots and scripted runs. There are no `--flags`.

- Show or ask: `show` / `ask`.

When the invocation contains one of these words (for example `/crav1-show-or-ask-open-questions show`), take that choice and do not ask. This holds for a person, a bot, or a headless run.

When a choice is missing and the run is headless or started by a bot (no person in the chat to answer), do not guess. Stop and name the valid words, for example: `Missing choice. Use one of: show, ask.`

An alias passes its choice word.

## Show

Read `## Open questions` in every `docs/specs/<slug>/spec.md` (skip `_template`), with the lines under each question, as `crav1-add-to-spec` `references/open-questions.md` describes. Write nothing. Draft nothing. Send nothing.

- One section per spec with open questions, then one line per question that has no `Answered:` line: the question in plain words, then its marks: `Asked <date>, <channel> to <who>`, `Pending since <date> for <who>`, `Blocks T2, T4`, or `not asked yet`.
- An answered question still waiting on `/crav1-resolve-open-questions` is listed under **Answered, not resolved**.
- End with counts: open, asked, pending, not asked, answered not resolved; then by person: who has how many asked or pending.
- Next: `/crav1-show-or-ask-open-questions` with **Ask** for the ones not asked yet, or `/crav1-resolve-open-questions` for the answered ones. Do not run them.


The specs hold open questions that only someone outside the kit can answer, such as a partner, a customer, or a colleague. You gather those questions and draft them so the user can ask them by mail, in a meeting, or in a chat. You record whether they were asked. You never send anything.

Command: `/crav1-show-or-ask-open-questions`.

This is cross-cutting. It is not a lane. It may run from any lane. It does not move work into Specify, Plan, or Build.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. That ask names the list. It does not run this command.

This is not `/crav1-resolve-open-questions`. Resolve walks the questions with the user and writes the decisions into the spec. This command drafts the questions for someone else and writes only the asked and pending marks.

The record format, pending, answer links, and the asked-on date are shared with the import skills. Follow `crav1-add-to-spec` `references/open-questions.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/open-questions.md`; plugin: sibling `skills/crav1-add-to-spec/references/open-questions.md`).

## Input

Everything after the command, and every `@`, is the input. The user names one of these:

- **A person or a group.** For example `Arvid`, or `NRCC`. Questions waiting for that person, and questions routed via that person, are theirs. "NRCC via Arvid" is a question for Arvid.
- **A spec.** An `@` of a spec folder or its `spec.md`, or its title.
- **A topic.** A few words, such as `static IP` or `mTLS`.

They may also name the output kind and the language.

When the input names none of person, spec, or topic, stop and ask. Options only. Use the questions tool when it is available. The options are:

1. **A person** — gather the questions that person can answer. Reply with the name.
2. **A spec** — gather every open question on one spec. Reply with an `@` of the spec, or pick it.
3. **A topic** — gather open questions on that subject across all specs. Reply with the words.

## Pending first

Read `docs/specs/<slug>/spec.md` for every spec folder. Skip `_template`. Read `## Open questions`, leftover unresolved assumptions, and the records under each question.

When a question in this selection has a `Pending:` line, show those first, before any new question. One line per draft, as the reference file says, for example:

```text
Drafted for Arvid on 2026-10-11 (mail), not marked as sent yet. 5 questions.
```

Ask for each draft. Options, each explained:

1. **Mark as sent** — you sent it. The kit writes `Asked:` on those questions, with the date you give, or today when you give none.
2. **Keep pending** — not sent yet. The mark stays and is shown again next run.
3. **Drop the mark** — it will not be sent. The kit removes the pending mark. The questions are open as before.

Stop until the user picks. Do not mix pending questions silently into the new draft. When the user wants them in the new draft too, they say so.

## Gather

Collect every open question that fits the selection.

- **Person.** The question names that person as who can answer, says `waiting for <person>`, says `via <person>`, or has an `Asked:` or `Pending:` line for that person. A question whose who is a group the person speaks for (the user says so, or the question says `via <person>`) is included. Do not guess who can answer a question that names nobody. List those separately as `No one named`, and ask whether to include them.
- **Spec.** Every open question on that spec.
- **Topic.** Match by meaning across all specs. Spec titles and the question words weigh most.

Skip a question that already has a clear `Answered:` line. Say how many were skipped and why. Skip a question with an `Asked:` line for this person unless the user asks to ask again. Say how many were skipped and when they were asked.

Every question that fits stays listed. Nothing is dropped to keep the list short. When the same question sits on two specs, it is one question in the draft, and both specs get the mark.

Show the gathered list in the chat, numbered, each with its spec path. That list is for the user. The draft is not.

## Output kind

When the user did not name one, ask. Options only, each explained:

1. **Mail** — a short greeting, one line on why, the questions numbered and grouped by topic, and a thank-you. The user copies it into their own mail.
2. **Meeting agenda** — a title, the purpose, each topic as an agenda point with its questions under it, and the time to set aside when the user names it. For a booked meeting.
3. **Chat message** — a short opener and the numbered questions. No headings. For a team chat.
4. **Meeting questions** — every selected question as a numbered list to ask out loud, in a standup, a call, or a longer meeting. Grouped by topic. No agenda layout and no intro text. It lists all of them, not a short cut. Questions not answered in the meeting go back to open.

## Language

English by default. When the user names a language, write the draft in that language. The gathered list in the chat stays in the language of this chat. Quoted technical names, product names, and values stay as they are.

## Write the draft

- Number the questions 1, 2, 3, … across the whole draft.
- Group them by topic. The topic heading is plain words, such as `Network access` or `Certificates`.
- Each question carries enough context to be answered by someone who has not read the spec: what is being built in one clause when it helps, what is already known, and what exactly is needed. One question asks one thing.
- Do not name a spec slug, a spec path, a file, or an id such as `Q3 in <spec>`. Do not name the kit. That can be misunderstood. The kit keeps which question belongs to which spec in the spec records.
- A question marked as a decision is phrased as a choice to make, with the options the spec names.
- Do not add a question the specs do not have. Do not answer a question in the draft.

Before showing the draft, run the personal-data and secrets check on the drafted text, the same way as for other outbound text. Follow `crav1-add-to-spec` `references/sources.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/sources.md`; plugin: sibling `skills/crav1-add-to-spec/references/sources.md`), sections **Personal data**, **Secrets**, and **Transfer data policy**. A secret is always removed and is never a choice. Use the transfer data policy when it exists. When it does not, the check may ask once and may write it after a yes, as that file says. An item it cannot place is asked one at a time.

Show the draft in one block the user can copy. Under it, one line: `Nothing was sent.`

## Asked?

Ask once for the draft. Options only. Use the questions tool when it is available. Each option explained:

1. **Yes, asked** — you have sent it or asked it. The kit writes `Asked:` under each question in the spec, with today's date, the kind, and who.
2. **No** — not asking. The kit writes nothing.
3. **Pending** — you copied it and will send it later. The kit writes `Pending:` under each question, with today's date, the kind, and who. Next run shows it first.

When the user picks yes or pending, write the lines as the reference file says, with `Question <n>` from the draft. A question asked of the same person again replaces the earlier line for that person. When an import later shows the question being asked, that date replaces this one. Do not edit the question text. Do not edit any other line.

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
- Yes writes `Asked:`. No writes nothing. Pending writes `Pending:`. Only under the questions in the draft.
- Do not plan, implement, or commit.
