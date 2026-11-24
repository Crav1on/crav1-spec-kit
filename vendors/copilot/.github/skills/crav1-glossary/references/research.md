# Research one term (1.101.0)

How `/crav1-glossary` looks for a meaning: in `research` mode for each `to be researched` row, and in `<term>` mode for a term the glossary does not define.

## 1. docs/ first

Search every file under `docs/` for the term, case-insensitively, and for its written-out form when the row or a source gives one. Skip `docs/specs/retired/`, `docs/system/glossary.md` itself, and `docs/system/_template/`.

A line states a meaning when it:

- writes the term out: `BCAS (Booking Cancellation Approval Service)`, `Booking Cancellation Approval Service (BCAS)`;
- defines it: `BCAS is ...`, `BCAS means ...`, `BCAS: ...` in a definition list or a glossary-style table;
- or quotes a source that does one of these.

A line that only uses the word (`send it to BCAS`) is not a meaning. Two lines that disagree: keep neither, show both with their paths and lines, and treat the term as not found.

Keep the first clear line in this order: `docs/system/`, `docs/specs/`, `docs/research/`, `docs/architecture/`, `docs/notes/`, `docs/sources/`. Record the path and the 1-based line number. The link written into the row is relative to `docs/system/glossary.md`: `[docs/specs/cancel-booking/spec.md:12](../specs/cancel-booking/spec.md#L12)`.

## 2. Public or internal

Decide before any web search. The default is internal.

A term is **public** only when it is a general word or abbreviation of a trade, a standard, a product, or a vendor (`PNR`, `SLA`, `OAuth`), and nothing in this project ties it to a private name.

A term is **internal-only** when any of these is true:

- it names the client, a customer, a partner, a person, a team, or a place;
- it names a project, system, service, repo, environment or codename that appears only in this project's sources;
- the personal-data and secrets check (`crav1-add-to-spec` `references/sources.md`, [Data policy](../../crav1-docs/concepts/data-policy.md)) flags the search words;
- you cannot tell.

An internal-only term never goes to the web: no web search, no fetch, no reworded query. Say `Internal term: not searched on the web.` in the summary.

## 3. Web, public terms only

Search for `<term> abbreviation` or `<term> meaning`, with no quote, no name, and no other project word. Keep a meaning only when the page states it and it fits how the project's docs use the term (the same field). Record the URL and today's date.

A web meaning is never written without the user's yes. Show the meaning and the URL first.

## 4. Nothing found

The term stays `to be researched`, and the skill routes it as its **Not found** section says.
