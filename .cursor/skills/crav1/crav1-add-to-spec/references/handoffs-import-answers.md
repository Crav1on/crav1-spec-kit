# crav1-add-to-spec: handoff

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0 and from `handoffs.md` in 1.71.1; the rules are unchanged.

## From an import: answer links and asked marks

When `/crav1-add-to-spec` hands an answer link or an asked mark for an existing spec, the spec is the one that skill already named. Do not ask for a slug. Do not ask keep or apply. Follow [references/open-questions.md](open-questions.md).

- An answer link writes one `Answered:` line under that open question: the date, who, the kind, the quote as handed (after any redaction), and the source folder. Do not paraphrase. Do not rewrite the question. Do not remove it from `## Open questions`. Do not change any other spec line. When the answer would change a spec line, name `/crav1-resolve-open-questions` for that slug. Do not run it.
- An asked mark writes or replaces the `Asked:` line for that person under that question, with the date from the source. It replaces a `Pending:` line for the same person.

When the handoff includes a source folder, add the `Source:` and `Trace:` lines from [references/sources.md](sources.md). Do not ask the imported-sources questions again.

Then run **Impact** for the research part only. When the question is one a stale research point waits on, follow the answered-later part of [references/research-stale-clear.md](research-stale-clear.md). Do not ask the user whether the point is settled. Do not ask the landscape question for an answer link. Do not run the picture offer. Do not commit.
