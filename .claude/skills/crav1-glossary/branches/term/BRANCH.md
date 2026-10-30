# Glossary: Term branch

Read only when `SKILL.md` routes here (`<term>` or `research <term>`). Moved word for word from `SKILL.md` in 1.106.0; the rules are unchanged. The shared sections in `SKILL.md` still apply. A `references/…` or `assets/…` path is relative to the skill folder, not this branch.

## Term

Answer one term.

1. **In the glossary with a meaning.** Answer from the row: the term, its meaning, its source as the row gives it, and `From docs/system/glossary.md`. Write nothing. Ask nothing.
2. **In the glossary as `to be researched`.** Say so, then run **Research** for that one row (`research <term>`).
3. **Not in the glossary.** Run **Research one term**. Answer first: the meaning and its source (file and line, or URL), or that nothing was found. Then, when a meaning was found, offer to add the row: `Add <term> to the glossary?` with `Add (Recommended)` and `Skip`. On the yes, add `| <Term> | <meaning> Source: <link> |` in sorted place by term, before the first `to be researched` row when it sorts after them, as `crav1-add-to-spec` `references/merge-safe.md` says. No yes: write nothing. Nothing found: run **Not found** for that term (the row is added only on **Correct**, or as `to be researched` on **Needs research**).

A term that is a kit word, not a project word, is answered from the kit's own glossary (`crav1-docs/concepts/glossary.md` next to the skills) and labelled `Kit glossary`; it is never added to the project glossary.

## Research one term

Read [references/research.md](../../references/research.md) and follow it. In short:

1. **docs/ first.** Search every file under `docs/` (specs, system notes, notes, sources, research, architecture) for the term and its written-out form, skipping `docs/specs/retired/` and the glossary file itself. A meaning counts only when a line states it (an expansion, `X is ...`, `X means ...`, a definition list). A line that only uses the word is not a meaning. Keep the first clear one: its path and line number.
2. **Public or internal.** Before any web search, decide whether the term is public. Run the personal-data and secrets check of `crav1-add-to-spec` `references/sources.md` on the search words. A term that names the client, a person, a project, a system or a codename found only in this project's sources, or that the check flags, is internal-only. An internal-only term never goes to the web: no web search, no fetch, not even reworded.
3. **Web, public terms only.** Search for the term with one neutral context word (`<term> abbreviation`), never with a quote, a name, or another project word. Keep a meaning only when a source page states it and it fits how the project's docs use the word. Name the URL.
