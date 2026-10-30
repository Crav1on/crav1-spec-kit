---
name: crav1-glossary
description: >-
  Use when the user asks about project terms in docs/system/glossary.md. Shows
  the glossary, writes it to a file, researches rows marked to be researched,
  or answers one term. Never adds open questions to a spec. Cross-cutting.
  Does not commit.
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

- Nothing after the command: **List** ([branches/list/BRANCH.md](branches/list/BRANCH.md)).
- `as-file`: **As file**, the same list written to a file instead of the chat.
- `research`: **Research** ([branches/research/BRANCH.md](branches/research/BRANCH.md)) every `to be researched` row. `research <term>`: only that row.
- `<term>`, any other words: **Term** ([branches/term/BRANCH.md](branches/term/BRANCH.md)). The words are the term, as in `/crav1-glossary bcas`; `/crav1-glossary file` looks up the term `file`.

## Find the glossary

Read `docs/system/glossary.md`. Match a term case-insensitively, and match an abbreviation to its written-out form when the row gives both (`BCAS (Booking Cancellation Approval Service)`). When the file is missing, say `No glossary yet: docs/system/glossary.md does not exist.` In List mode stop there. In Research mode there is nothing to fill; stop. In Term mode go on to **Research one term**; the offer to add creates the file from the template after the yes.

## Route (1.106.0)

Route first, load second. Pick the branch from the choice word or the answer to the opening question, then read only that branch file. Do not read the other branches.

- **List** (no word): follow [branches/list/BRANCH.md](branches/list/BRANCH.md).
- **As file** (`as-file`): follow [branches/as-file/BRANCH.md](branches/as-file/BRANCH.md).
- **Research** (`research`): follow [branches/research/BRANCH.md](branches/research/BRANCH.md).
- **Term** (`<term>` or `research <term>`): follow [branches/term/BRANCH.md](branches/term/BRANCH.md).

## Not found

The glossary holds definitions only. A gap never becomes an open question on a spec, never gets a `Pending:` line, and is never handed to `/crav1-show-or-ask-open-questions` or `crav1-add-to-spec` `references/open-questions.md`, so it never blocks a plan or a build. Read [references/not-found.md](references/not-found.md) only when a term is found nowhere: offer what you may know with **Correct** or **Needs research**.

## Prompt budget

At most one prompt per run: the add question (Term), or one question with the web meanings and the **Not found** guesses (Research). List and As file ask nothing. A headless or bot run asks nothing; it writes the docs/ meanings and lists the rest.

## Writes

Only `docs/system/glossary.md` (rows filled or added as above) and in As file mode `.crav1/glossary-list.md` with its `.crav1/.gitignore`, both ignored by git. Nothing else: no spec text, no research note, no notes index. Never commit, push, or open a pull request. The user commits.

## Stop

Do not invent a meaning; a guess is labelled and written only on **Correct**. Do not rewrite a row that already has a meaning; a different meaning found later is shown side by side and left for `/crav1-add-to-spec`, as `references/sources-rare.md` says. Do not web-search an internal-only term. Do not write a web meaning without its yes. Do not mark research stale from a glossary row. Never write an open question, a `Pending:` line or any other line into a spec.
