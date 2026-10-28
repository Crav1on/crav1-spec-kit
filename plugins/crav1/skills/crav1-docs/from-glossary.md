# The glossary: show it, look up a word, fill the gaps

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not).

The project glossary is `docs/system/glossary.md`: one row per word the system's sources use, `| Term | Meaning |`. Import skills add rows; a word whose meaning no source states gets the Meaning `to be researched` (see [Glossary rows](concepts/glossary.md)). `/crav1-glossary` (1.101.0) is how you read it and how those rows get filled.

This is cross-cutting. It may run from any lane and does not move work into Specify, Plan, or Build. It is a later skill, not a starter option. It never commits.

## Four modes

The word after the command picks the mode. There is no opening question.

| You type | What happens |
| --- | --- |
| `/crav1-glossary` | The whole glossary in the chat, in the file's order (the `to be researched` rows stay last), a count line on top, and the path `docs/system/glossary.md` named at the end (as text, not a link, like every local file the kit names). Writes nothing, creates no file. |
| `/crav1-glossary as-file` | The same list written to `.crav1/glossary-list.md` for you to open (1.102.0). The chat shows only the count line and the path. |
| `/crav1-glossary research` | Fills every `to be researched` row. `research <term>` fills only that one. |
| `/crav1-glossary bcas` | Answers one term from its row. When the glossary does not define it, researches it, answers, then offers to add the row. |

## The list as a file

The mode word is `as-file`, not `file`, so a term literally named `file` still works with a bare lookup: `/crav1-glossary file` answers that term.

`/crav1-glossary as-file` writes the list to `.crav1/glossary-list.md` at the repo root and overwrites an older copy. The first run also creates `.crav1/.gitignore` with the single line `*`, so git ignores the whole `.crav1/` folder: the file never shows up in `git status`, is never committed, and your own `.gitignore` is not touched. Delete the folder whenever you like.

## How a meaning is found

1. **docs/ first.** Every file under `docs/` is searched (not retired specs). Only a line that states the meaning counts: a written-out abbreviation, `X is ...`, `X means ...`. A docs/ meaning is written into its `to be researched` row right away, with a file and line link, for example `Source: [docs/system/landscape.md:7](landscape.md#L7)`.
2. **Public or internal.** Before any web search the term is checked: the personal-data and secrets check from the [Data policy](concepts/data-policy.md) runs on the search words, and a client, person, project, system or codename that only this project uses is internal-only. Internal-only terms never go to the web. When in doubt, a term is internal.
3. **The web, public terms only.** A meaning found there is shown with its URL and written only after your yes.
4. **Nowhere.** The row stays `to be researched`. When a spec uses the word, that spec gets the open question `What does <term> mean here?` with a `Pending:` line naming who may know; `/crav1-show-or-ask-open-questions ask` drafts it for them. When no spec uses it, you get a research request drafted in the chat. Nothing is sent.

## First prompts

```text
/crav1-glossary
```

```text
/crav1-glossary as-file
```

```text
/crav1-glossary research
```

```text
/crav1-glossary bcas
```

## What it writes

Only rows in `docs/system/glossary.md`, the ignored `.crav1/glossary-list.md` in as-file mode, and on a not-found term the open question on the spec that uses it. A row that already has a meaning is never rewritten here; a different meaning from a new source goes through `/crav1-add-to-spec`, which shows old and new side by side. At most one question per run. Headless and bot runs ask nothing: they write the docs/ meanings and list web meanings as waiting for a yes.

Next: `/crav1-finalize-commit` when a row changed. See the [skill page](reference/skills/crav1-glossary.md).
