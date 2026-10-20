# crav1-show-or-ask-open-questions: drafting

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Output kind

When the user did not name one, ask. Options only, each explained:

1. **Mail** — a short greeting, one line on why, the questions numbered and grouped by topic, and a thank-you. The user copies it into their own mail.
2. **Meeting agenda** — a title, the purpose, each topic as an agenda point with its questions under it, and the time to set aside when the user names it. For a booked meeting.
3. **Chat message** — a short opener and the numbered questions. No headings. For a team chat.
4. **Meeting questions** — every selected question as a numbered list to ask out loud, in a standup, a call, or a longer meeting. Grouped by topic. No agenda layout and no intro text. It lists all of them, not a short cut. Questions not answered in the meeting go back to open.

## Write the draft

- Number the questions 1, 2, 3, … across the whole draft.
- Group them by topic. The topic heading is plain words, such as `Network access` or `Certificates`.
- Each question carries enough context to be answered by someone who has not read the spec: what is being built in one clause when it helps, what is already known, and what exactly is needed. One question asks one thing.
- Do not name a spec slug, a spec path, a file, or an id such as `Q3 in <spec>`. Do not name the kit. That can be misunderstood. The kit keeps which question belongs to which spec in the spec records.
- A question marked as a decision is phrased as a choice to make, with the options the spec names.
- Do not add a question the specs do not have. Do not answer a question in the draft.

Before showing the draft, run the personal-data and secrets check on the drafted text, the same way as for other outbound text. Follow `crav1-add-to-spec` `references/sources.md` (drop-in: `.claude/skills/crav1-add-to-spec/references/sources.md`; plugin: sibling `skills/crav1-add-to-spec/references/sources.md`), sections **Personal data**, **Secrets**, and **Transfer data policy**. A secret is always removed and is never a choice. Use the transfer data policy when it exists. When it does not, the check may ask once and may write it after a yes, as that file says. An item it cannot place is asked one at a time.

Show the draft in one block the user can copy. Under it, one line: `Nothing was sent.`

## Language

English by default. When the user names a language, write the draft in that language. The gathered list in the chat stays in the language of this chat. Quoted technical names, product names, and values stay as they are.
