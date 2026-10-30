# Meeting to specs: **In one batch (1.70.0)**, **Keep**, **Answer**, **Leave**, **Dismiss**

Part of `branches/meeting/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.107.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

## In one batch (1.70.0)

Ask about every item in one questions call, one question per item; a single `yes` takes the recommended option for every item. Use the questions tool when it is available. The question text names the item and the spec when one fits, then the same `State` line that is on the item. It does not say `Recommendation:`. The options are only these three. The recommended one comes first with ` (Recommended)` at the end of its label; the others keep this order:

- **Keep**
- **Leave**
- **Dismiss**

```text
M1: dev and prod containers. Add this to <slug>?
State: partly built. Dev container done (task 4 checked); prod not in tasks.md.
```

Options: **Keep (Recommended)**, Leave, Dismiss.

```text
M1: source-to-target mapping of the SQL tables. No spec fits.
```

Options: **Leave (Recommended)**, Keep, Dismiss. Left, it stays in the full note.

When `Fits` is `none`, the question has no `State` line. The options stay Keep, Leave, and Dismiss.

Stop until the user answers. Do not write before that reply. Then apply the answered items in order.

A batch (`M1 keep, M2 leave`) applies only the items named in that batch, in order. An item with no mark stays unanswered. Do not treat silence as dismiss. When a keep needs a further question, ask that question and do not apply the rest of the batch in that turn.

### Keep

Follow the case already on that item.

**Addition.** When one spec fits, and this source is not yet imported, follow the imported-sources convention before the handoff (this skill's `references/sources.md`). Its personal-data and secrets check is in that file; flagged items, the transfer data policy, and the one question are in `references/sources-flagged.md`, and a mail's images in `references/sources-mail.md` and `references/sources-binary.md`, all in `crav1-add-to-spec`. Write `docs/sources/YYYY-MM-DD-<slug>/` once for that source. Do not commit. A later kept addition from the same source reuses that folder. Do not ask those questions again. The policy questions are once per repo, as that file says.

Then hand the quote to the fact branch of `/crav1-add-to-spec` for that slug. Pass the quote after any redaction that convention made. Pass the kind and the date for this run, and the source folder. When there is no date, pass the kind and the folder. Pass the path of the full note so the spec line links it and the note gets the slug in `used_by`. Do not pass the `State` line. It is not quote text. Do not pass the recommendation. Follow only the handoff **From the meeting branch of /crav1-add-to-spec** in that skill (this skill's `SKILL.md`), which runs **Add to that spec.md** and **Impact** from that skill's `references/fact.md`. One item. Then stop that handoff. The impact check still runs there, including research. That check follows this skill's `references/research-stale.md`. This skill does not run that check a second time. It does not write the stale block. Do not write the spec in this skill. Do not create a slug.

When more than one spec fits, ask which one before the handoff. Options only. One option per candidate, plus **Treat as a new feature**. Do not ask the user to type a slug. Stop until the user picks. A picked spec gets the addition handoff. Treat as a new feature follows the new-feature rule below.

**New feature.** Name the next command. Do not run it. Do not create a slug. Do not seed `docs/system/`. Do not write the source folder here.

- One kept new feature that is one or two sentences: `/crav1-spark-to-spec`
- One kept new feature that is a pile of ideas and technical hunches: `/crav1-ideas-to-spec`
- Two or more kept new features: `/crav1-bundle-to-specs`

When a later keep brings the new-feature count to two or more, the next command for those items is `/crav1-bundle-to-specs`. Say that in the recap. Do not run it.

**Bug.** Name `/crav1-fix-bug`. Do not run it. Do not name the lane. Do not edit code. Do not write `explore.md`.

**Unclear.** Ask with options only. One option per existing spec folder, labeled `docs/specs/<slug>/` and the title line when `spec.md` has one, plus **Treat as a new feature**. Do not ask the user to type a slug. Stop until the user picks. A picked spec gets the addition handoff. Treat as a new feature follows the new-feature rule. When no spec folder exists, treat the keep as a new feature and do not ask for a slug.

### Answer

An `answer` item is not asked. When this source is not yet imported, follow the imported-sources convention first, exactly as for a kept addition. Then hand it to the fact branch of `/crav1-add-to-spec` for that slug. Follow only the handoff **From an import: answer links and asked marks** in that skill. Pass the question, the quote after any redaction, who answered, the kind, the date, and the source folder. Pass the `Asked in this <kind>` lines for that spec in the same handoff. When a spec has only asked lines and no answer, hand those lines alone. They do not need a source folder. Do not write the spec in this skill. When the answer would change a spec line, name `/crav1-resolve-open-questions` for that slug. Do not run it.

When the imported-sources check asks a question, that question is this turn. Then continue with the next item.

### Leave

Write nothing. The item stays listed as left for this run. The next run starts fresh and can offer it again.

### Dismiss

Write nothing. Dismiss is for this run only. Do not write a dismissals file. Do not record the quote on a spec. The next run starts fresh and can offer the item again. Do not remember a dismiss across runs.
