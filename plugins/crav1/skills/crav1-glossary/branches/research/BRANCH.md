# Glossary: Research branch

Read only when `SKILL.md` routes here (`research`). Moved word for word from `SKILL.md` in 1.106.0; the rules are unchanged. The shared sections in `SKILL.md` still apply. A `references/…` or `assets/…` path is relative to the skill folder, not this branch.

## Research

Fill the rows whose Meaning is exactly `to be researched`, one at a time, in file order. With `research <term>`, only that row; when it is not a `to be researched` row, say what it says and stop.

For each row, run **Research one term**. Then:

- **Found in docs/.** Write the meaning into the row right away, no question. The Meaning is the source's words, shortened only, followed by the source as a link with the line: `Booking Cancellation Approval Service: approves a cancellation after the cut-off. Source: [docs/system/landscape.md:7](landscape.md#L7)`. The link is relative to `docs/system/`. Replace only `to be researched` in that one row; do not rewrite another row, do not move the row.
- **Found on the web.** Show the meaning and its source URL, and ask `Add this meaning for <term>?` with `Add (Recommended)` and `Skip`. Write it only on that yes, as `<meaning> Source: <URL> (web, <date>)`. No yes, or a headless or bot run with no person to answer: write nothing for that row and list it under **Waiting for your yes** with the meaning and URL.
- **Found nowhere.** The row stays `to be researched` unless the user picks **Correct** on a guess, as **Not found** says.

Several web meanings in one run are asked in one question, one option per term plus `None`, so the run stays inside its prompt budget.

End with one summary: written from docs/ (term and source), waiting for a yes, routed (term and where), still `to be researched`.
