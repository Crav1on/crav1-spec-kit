# Ask open questions

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when the specs hold open questions that only someone else can answer: a partner, a customer, or a colleague. The command gathers those questions for one person, one spec, or one topic, and drafts them for you to send or ask. It records whether you asked. Nothing is sent by the kit.

This is not `/crav1-resolve-open-questions`. Resolve walks the questions with you and writes your decisions into the spec. This command drafts the questions for someone else and writes only the asked and pending marks.

## First prompt

```text
/crav1-show-or-ask-open-questions

The open questions for <a person, one spec, or a topic>, as a mail.
```

Name a person (`Alex`, or a group), a spec (`@docs/specs/<slug>/`), or a topic (`static IP`). You can also name the kind of draft and the language.

## Steps

| Step | You | Agent |
| --- | --- | --- |
| Who or what | Name a person, a spec, or a topic | With none of them, stops and asks, with options only |
| Pending first | For each earlier draft: mark as sent, keep pending, or drop the mark | Shows drafts still marked `Pending:` before anything new. Mark as sent writes `Asked:` with the date you give, or today |
| Gather | Glance at the list | Reads `## Open questions` and unresolved assumptions on every spec. Lists every question that fits, numbered, with its spec path. Skips questions already answered, and questions already asked of this person unless you ask again, and says how many and why. Nothing is dropped to keep the list short |
| Kind | Pick mail, meeting agenda, chat message, or meeting questions | Asks only when you did not name one. Meeting questions lists every selected question to ask out loud |
| Draft | Copy it | Numbered, grouped by topic in plain words, with enough context for someone who has not read the spec. No spec name, path, file, or question id. English unless you named a language. The personal-data and secrets check runs on the draft. Ends with `Nothing was sent.` |
| Asked? | Yes, no, or pending | Yes writes `Asked:` under each question. Pending writes `Pending:`, shown first next run. No writes nothing |

## Parked and retired specs

Specs in `docs/specs/retired/` are skipped. A parked spec is still listed, marked `(parked)`, and its questions can still be asked. A note waiting for a parked spec is shown as `waiting for parked <slug>`, not counted as open work ([retire spec](from-retire-spec.md)).

## What gets written

Only lines under the drafted questions in `docs/specs/<slug>/spec.md`:

```text
- <question>
  - Pending: drafted <date> for <who>, <channel>. Not marked as sent yet. Question <n> of that draft.
  - Asked: <date>, <channel> to <who>. Question <n>. Date from <the user's yes | email <date> | meeting <date> | chat <date>>.
```

The transfer data policy, after a yes, when the personal-data check asks for it. See [Data policy](concepts/data-policy.md).

Not written: the question text, any other spec line, `docs/system/`, plan, tasks, or code. Not sent. Not committed.

## After

When a mark was written:

```text
/crav1-finalize-commit
```

When answers come back, bring the mail, minutes, transcript, or chat to [`/crav1-add-to-spec`](from-add-to-spec-meeting.md), or a larger dump to [`/crav1-add-to-spec`](from-add-to-spec-dump.md). Those write an `Answered:` line with the quote and its source under the question. Then [`/crav1-resolve-open-questions`](from-draft-spec.md) offers that answer first. The marks are explained in [Data layout](concepts/data-layout.md#open-question-marks).

Reference page: [show-or-ask-open-questions](reference/skills/crav1-show-or-ask-open-questions.md)
