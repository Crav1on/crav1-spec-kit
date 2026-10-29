---
name: crav1-glossary
description: >-
  The project glossary in docs/system/glossary.md. No word: show the whole
  glossary in the chat, in the file's order, and name the file. file: write
  the same list to .crav1/glossary-list.md, kept out of git. research:
  fill the rows whose Meaning is to be researched, docs/ first (written
  with a file and line link), then the web for public terms only, after
  the personal-data check (a web meaning is written only after a yes).
  <term>: answer one term from its row, or research it the same way and
  offer to add the row. Not found anywhere: offer a guess with Correct or
  Needs research; never an open question on a spec. Cross-cutting. Not a
  starter option. Does not commit.
disable-model-invocation: true
icon: book-a
color: teal
---

# Glossary

The glossary is `docs/system/glossary.md`: the words and abbreviations this system already uses, one table row per term, `| Term | Meaning |`. Its rules are in the template `docs/system/_template/glossary.md` and in `crav1-add-to-spec` `references/sources-rare.md`: a meaning is only what a source says; when no source says it, the Meaning is `to be researched`. This skill shows the glossary, answers one term, and fills the `to be researched` rows.

Command: `/crav1-glossary`.

This is cross-cutting. It is not a lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It is a later skill, not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`.

Other skills do not run this one. It does not run another skill. It may name one.

## Choice words

Exact words for bots and scripted runs. There are no `--flags`. There is no opening question: the words pick the mode.

- Nothing after the command: **List**.
- `as-file`: **As file**, the same list written to a file instead of the chat.
- `research`: **Research** every `to be researched` row. `research <term>`: only that row.
- `<term>`, any other words: **Term**. The words are the term, as in `/crav1-glossary bcas`; `/crav1-glossary file` looks up the term `file`.

## Find the glossary

Read `docs/system/glossary.md`. Match a term case-insensitively, and match an abbreviation to its written-out form when the row gives both (`BCAS (Booking Cancellation Approval Service)`). When the file is missing, say `No glossary yet: docs/system/glossary.md does not exist.` In List mode stop there. In Research mode there is nothing to fill; stop. In Term mode go on to **Research one term**; the offer to add creates the file from the template after the yes.

## List

Show the whole glossary in the chat. Write nothing. Create no file, not even a temporary one.

- Every row, in the same order as the file. Do not sort, group, or move rows. The `to be researched` rows stay where the file has them (last, today).
- One Markdown table, `| Term | Meaning |`, each Meaning as written, links kept.
- Above the table, one count line: `<n> terms, <m> to be researched.`
- End with the file as a code span, never a link, as **Naming local files** in `crav1.mdc` says: ``Glossary file: `docs/system/glossary.md` ``. To get the list as a file, name `/crav1-glossary as-file`.
- When there are `to be researched` rows, the last line names `/crav1-glossary research`. Do not run it.

## As file

- The file is `.crav1/glossary-list.md` at the repo root. Create it with `.crav1/.gitignore` holding the one line `*`, so git ignores the folder. Do not touch the repo's `.gitignore`.
- Content: `# Glossary`, the count line, the **List** table, and ``Source: `docs/system/glossary.md` ``. Overwrite an older copy.
- In the chat: the count line and ``Glossary list file: `.crav1/glossary-list.md` (not in git) ``. Not the table.
- Write nothing else; never stage or commit it. No glossary: stop as **Find the glossary** says.

## Research

Fill the rows whose Meaning is exactly `to be researched`, one at a time, in file order. With `research <term>`, only that row; when it is not a `to be researched` row, say what it says and stop.

For each row, run **Research one term**. Then:

- **Found in docs/.** Write the meaning into the row right away, no question. The Meaning is the source's words, shortened only, followed by the source as a link with the line: `Booking Cancellation Approval Service: approves a cancellation after the cut-off. Source: [docs/system/landscape.md:7](landscape.md#L7)`. The link is relative to `docs/system/`. Replace only `to be researched` in that one row; do not rewrite another row, do not move the row.
- **Found on the web.** Show the meaning and its source URL, and ask `Add this meaning for <term>?` with `Add (Recommended)` and `Skip`. Write it only on that yes, as `<meaning> Source: <URL> (web, <date>)`. No yes, or a headless or bot run with no person to answer: write nothing for that row and list it under **Waiting for your yes** with the meaning and URL.
- **Found nowhere.** The row stays `to be researched` unless the user picks **Correct** on a guess, as **Not found** says.

Several web meanings in one run are asked in one question, one option per term plus `None`, so the run stays inside its prompt budget.

End with one summary: written from docs/ (term and source), waiting for a yes, routed (term and where), still `to be researched`.

## Term

Answer one term.

1. **In the glossary with a meaning.** Answer from the row: the term, its meaning, its source as the row gives it, and `From docs/system/glossary.md`. Write nothing. Ask nothing.
2. **In the glossary as `to be researched`.** Say so, then run **Research** for that one row (`research <term>`).
3. **Not in the glossary.** Run **Research one term**. Answer first: the meaning and its source (file and line, or URL), or that nothing was found. Then, when a meaning was found, offer to add the row: `Add <term> to the glossary?` with `Add (Recommended)` and `Skip`. On the yes, add `| <Term> | <meaning> Source: <link> |` in sorted place by term, before the first `to be researched` row when it sorts after them, as `crav1-add-to-spec` `references/merge-safe.md` says. No yes: write nothing. Nothing found: run **Not found** for that term (the row is added only on **Correct**, or as `to be researched` on **Needs research**).

A term that is a kit word, not a project word, is answered from the kit's own glossary (`crav1-docs/concepts/glossary.md` next to the skills) and labelled `Kit glossary`; it is never added to the project glossary.

## Research one term

Read [references/research.md](references/research.md) and follow it. In short:

1. **docs/ first.** Search every file under `docs/` (specs, system notes, notes, sources, research, architecture) for the term and its written-out form, skipping `docs/specs/retired/` and the glossary file itself. A meaning counts only when a line states it (an expansion, `X is ...`, `X means ...`, a definition list). A line that only uses the word is not a meaning. Keep the first clear one: its path and line number.
2. **Public or internal.** Before any web search, decide whether the term is public. Run the personal-data and secrets check of `crav1-add-to-spec` `references/sources.md` on the search words. A term that names the client, a person, a project, a system or a codename found only in this project's sources, or that the check flags, is internal-only. An internal-only term never goes to the web: no web search, no fetch, not even reworded.
3. **Web, public terms only.** Search for the term with one neutral context word (`<term> abbreviation`), never with a quote, a name, or another project word. Keep a meaning only when a source page states it and it fits how the project's docs use the word. Name the URL.

## Not found

The glossary holds definitions only. A gap never becomes an open question on a spec, never gets a `Pending:` line, and is never handed to `/crav1-show-or-ask-open-questions` or `crav1-add-to-spec` `references/open-questions.md`, so it never blocks a plan or a build. Read [references/not-found.md](references/not-found.md) only when a term is found nowhere: offer what you may know with **Correct** or **Needs research**.

## Prompt budget

At most one prompt per run: the add question (Term), or one question with the web meanings and the **Not found** guesses (Research). List and As file ask nothing. A headless or bot run asks nothing; it writes the docs/ meanings and lists the rest.

## Writes

Only `docs/system/glossary.md` (rows filled or added as above) and in As file mode `.crav1/glossary-list.md` with its `.crav1/.gitignore`, both ignored by git. Nothing else: no spec text, no research note, no notes index. Never commit, push, or open a pull request. The user commits.

## Stop

Do not invent a meaning; a guess is labelled and written only on **Correct**. Do not rewrite a row that already has a meaning; a different meaning found later is shown side by side and left for `/crav1-add-to-spec`, as `references/sources-rare.md` says. Do not web-search an internal-only term. Do not write a web meaning without its yes. Do not mark research stale from a glossary row. Never write an open question, a `Pending:` line or any other line into a spec.
