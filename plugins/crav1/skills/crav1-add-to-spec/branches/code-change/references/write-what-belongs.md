# Code into specs: **Write what belongs**

Part of `branches/code-change/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.111.2; the rules are unchanged. Paths in backticks are relative to the skill folder.

## Write what belongs

Edit only `docs/specs/<slug>/spec.md` for slugs in the confirmed **belongs** pile. Write them in this chat. Do not launch a worker.

For each of those files, write the same way the fact branch of `/crav1-add-to-spec` writes:

- Quote what the change does. The quote is the record. Do not replace it with a paraphrase. A reading you add that the change does not show is inferred or it stays out.
- Label what is new versus what was already there.
- Keep inferred facts labeled inferred. A fact you were not shown by the change, and that the file did not already say, is inferred or it stays out. A fact that was not on the confirmed sort stays inferred or stays out.
- Do not invent acceptance, architecture, or tasks to fill gaps. A proposed ADR or diagram edit later is only a change the diff requires.
- Do not change match status unless the change itself says the status changed.
- Do not write `plan.md`, `tasks.md`, `diagrams.md`, `adr/`, `export/`, `verify.md`, `fix-log.md`, or `work-item.md` in the spec folder.
- Do not replace the file with a template.

Labels, in the section the words belong to:

- `**New:** "…"` — what the change does, added this pass, in sorted place among the `**New:**` lines there (1.84.0, `references/merge-safe.md`).
- `**Already there:**` — do not paste a second copy. Leave the existing sentence. The **already described there** pile is the report, not a second paste.
- `**Inferred:**` — a connection you drew. Not an accepted fact.

When the file already has `## Trace`, append one line: what this pass marked new, already there, and inferred. Do not create `## Trace` only for that line.

A thin spec (match status `not in the code`, or only Match / What the dump says / In the code / Trace / Open questions) stays thin. Put the quote under the heading it belongs to. Add a heading only when the change is that content. Do not add Problem, Goals, Users and journeys, or Acceptance criteria to fill the file out. Do not add `## In the code` unless the change names code that is there.

A fuller spec keeps its headings. Place the quote in the section it extends. Add an acceptance checkbox only when the change states a check a stranger could run, and label that checkbox `**New:**`. That checkbox stays yes/no. Name unit, system, or browser only when that kind is already obvious from the source. Otherwise leave the kind for plan. Do not invent a test list. Do not turn a behavior into a checkbox the change did not state.

Expected headings when the file already uses the full spec shape: this skill’s `assets/spec.md` (same file as `docs/specs/_template/spec.md`; this skill's `branches/code-change/assets/spec.md`). A match-shaped spec does not have to grow those headings.

The **fits none of them** pile is listed and left alone. Do not create a spec for it. If they say to create one, do not write a folder here. Point at the skill that creates a spec, and do not run it:

- one or two sentences for one feature: `/crav1-spark-to-spec`
- one unstructured pile for one feature: `/crav1-ideas-to-spec`
- several new features, or several repos: `/crav1-bundle-to-specs`
- repos that already make up the system, and this leftover is a slice to match: the repos and bundle branch of `/crav1-existing-to-specs`
