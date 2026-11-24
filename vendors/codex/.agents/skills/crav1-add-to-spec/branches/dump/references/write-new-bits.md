# Match dump to specs: **Write the new bits**

Part of `branches/dump/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.111.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

## Write the new bits

When a confirmed quote comes from a mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original file, follow the imported-sources convention before that quote (this skill's `references/sources.md`). Its personal-data and secrets check is in that file; flagged items, the transfer data policy, and the one question are in `references/sources-flagged.md`, and a mail's images in `references/sources-mail.md` and `references/sources-binary.md`, all in `crav1-add-to-spec`. Write `docs/sources/YYYY-MM-DD-<slug>/` once per source. Add the `Source:` and `Trace:` lines from that file. Do not commit. A quote that is not from an imported source does not get a source folder. With `mail`, read `sources.md` and `sources-mail.md` before the sort. With `chat`, an exported chat file is an imported source; pasted chat text is not.

Edit `docs/specs/<slug>/spec.md` for slugs in the confirmed **belongs** pile. An imported source also writes its source folder, as that convention says. Write them in this chat. Do not launch a worker.

For each of those files:

- Quote their words. The quote is the record. Do not replace it with a paraphrase. For a diagram or screenshot, quote the text on it. A reading you add that the file does not state is inferred or it stays out.
- Label what is new versus what was already there.
- Keep inferred facts labeled inferred. A fact you were not told, and that the file did not already say, is inferred or it stays out. A fact that was not on the confirmed sort stays inferred or stays out.
- Do not invent acceptance, architecture, or tasks to fill gaps. A proposed ADR or diagram edit later is only a change their words require.
- Do not change match status unless the new information itself says the status changed.
- Do not write `plan.md`, `tasks.md`, `diagrams.md`, `adr/`, `export/`, `verify.md`, `fix-log.md`, or `work-item.md` in the spec folder.
- Do not replace the file with a template.

Labels, in the section the words belong to:

- `**New:** "…"` — their words, added this pass, in sorted place among the `**New:**` lines there (1.84.0, `references/merge-safe.md`).
- `**Already there:**` — do not paste a second copy. Leave the existing sentence. The **already** pile is the report, not a second paste.
- `**Inferred:**` — a connection you drew. Not an accepted fact.

When the file already has `## Trace`, append one line: what this pass marked new, already there, and inferred. Do not create `## Trace` only for that line. An imported source is the exception: the `Source:` and `Trace:` lines in the imported-sources convention are required, and `## Trace` is created when it is missing.

A thin spec stays thin, as **Thin spec** in `crav1-add-to-spec` `SKILL.md` says.

A fuller spec keeps its headings. Place the quote in the section it extends. Add an acceptance checkbox only when they stated a check a stranger could run, and label that checkbox `**New:**`. That checkbox stays yes/no. Name unit, system, or browser only when that kind is already obvious from the source. Otherwise leave the kind for plan. Do not invent a test list. Do not turn a wish into a checkbox.

Expected headings when the file already uses the full spec shape: this skill’s `assets/spec.md` (same file as `docs/specs/_template/spec.md`; this skill's `branches/dump/assets/spec.md`). A match-shaped spec does not have to grow those headings.

Read this skill's `references/dump-answers.md` only when the confirmed sort has a fact with `Answers:` or a line under `Asked in this dump`.

The full note is written under **Write the full note**. It does not become a spec. The **does not fit** pile is listed and left alone. Do not create a spec for it. If they say to create one, do not write a folder here. Point at the skill that creates a spec, and do not run it:

Read this skill's `references/dump-new-spec.md` for which skill to point at.
