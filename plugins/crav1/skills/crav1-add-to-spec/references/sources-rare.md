# Imported sources: rare cases

Read only for the case a section names. [sources.md](sources.md) is the convention. Moved word for word from `sources.md` in 1.71.2; the rules are unchanged.

## Reading the document

### Black-boxed text

Text under a black box in a PDF is redacted, even when it can still be extracted. Never copy it into a file, a quote, or the chat. Mark the spot `[redacted in source]`.

### Word files

Read a `.docx` as if every tracked change were accepted, and flag each change in the README (what changed, who, and when, as the file shows). List each comment in the README with its author and date. A change or a comment that affects a spec becomes an open question in that spec.

### Dates

Never guess an ambiguous date such as `03/04`. Keep it as the source wrote it and add an open question that asks which date is meant. Fill it in only once answered. When the context settles it (the document's locale, a weekday next to it), apply it the normal way.

## Versions and conflicts

### Superseded versions

When an import brings a newer version of a document already imported, or an older one, mark the older folder's README `Superseded by: docs/sources/<newer>/`. Keep the old folder. Read only the newest version for specs.

### Source precedence

When sources disagree, the newest source that records a decision wins. When no source settles it, write an open question. After an intake of several files, run one conflict pass across them before the specs are final.

### Plain facts

A plain uncontested fact, such as a date or a name that no source contradicts, is applied without asking. List every one in the run summary. A fact that changes a decision, or that conflicts with text already in the spec, is still asked.

### Glossary

Add a new glossary term without asking. Before rewriting an existing row, show the old and the new definition side by side with the source, and wait for the user's yes.

## Headless runs (two-pass)

A run with no window (for example `-p`) cannot stop to ask. Run it in two passes:

1. **Pass 1** does everything that needs no answer, writes every question to a file in the system temp folder, names that file, and stops. It writes nothing to `docs/sources/` or a spec that depends on an answer.
2. **Pass 2** is pointed at that file with the answers filled in, applies them, and finishes.

When the file is gone at pass 2 (temp was cleaned), ask the questions again with a new pass 1.
