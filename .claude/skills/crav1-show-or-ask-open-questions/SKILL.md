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

1. **Show.** An overview of every open question across the specs. Read-only. Follow [branches/show/BRANCH.md](branches/show/BRANCH.md).
2. **Ask.** Draft questions for one person, one spec, or one topic. Follow [branches/ask/BRANCH.md](branches/ask/BRANCH.md) (the rules that were `/crav1-ask-open-questions`).

Skip the question when the message says which: "show", "overview", "what is still open", or "who did we ask" is 1; a person, a channel, or "draft" is 2.

## Choice words

Exact words for bots and scripted runs. There are no `--flags`.

- Show or ask: `show` / `ask`.
- After `ask`: `research` drafts a research request; read `references/research.md`.

When the invocation contains one of these words (for example `/crav1-show-or-ask-open-questions show`), take that choice and do not ask. This holds for a person, a bot, or a headless run.

When a choice is missing and the run is headless or started by a bot (no person in the chat to answer), do not guess. Stop and name the valid words, for example: `Missing choice. Use one of: show, ask.`

## Route (1.106.0)

Route first, load second. Pick the branch from the choice word or the answer to the opening question, then read only that branch file. Do not read the other branches.

- **Show** (`show`): follow [branches/show/BRANCH.md](branches/show/BRANCH.md).
- **Ask** (`ask`): follow [branches/ask/BRANCH.md](branches/ask/BRANCH.md).

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
