# Repos to spec: **Later re-read**

Part of `branches/repos-only/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.107.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

### Later re-read

`docs/architecture/spec.md` is already there. Add only what is new. Do not rewrite, reorder, or delete a line that is already there.

**Architecture spec.** Append a confirmed fact under **Confirmed** and under the repo heading when that fact is not already a line. Cite the path. A repo the user named that has no heading yet gets a new heading. Do not rewrite the lines under a heading that is already there. Append an accepted guess under **Accepted from a guess** when it is not already a line, and say the code does not show it. Append a link under **How the repos connect** when the code shows it and that link is not already a line. Cite the path. Do not invent a link. Leave an existing `Only one repo was named.` or `No link between these repos is in the code.` line as it is. Append an open question when the code does not show it and that question is not already a line. A guess they did not accept stays out of this file. Do not add a Left out heading. When nothing new belongs in the file, write no line. Say the architecture spec is current.

**Left-out file.** Follow **Left-out file** above. A line the code now shows is removed and written as a confirmed fact or a link, not as a guess. A line the code still does not show stays, unless this answer accepts it or dismisses it. Do not drop a line to keep the file short.

**System notes that are already there.** Add only what is new. Do not rewrite a line that is already there.

- Short description: keep every sentence. When a confirmed fact is not already named there, add one sentence at the end. Do not rephrase a sentence that is already there.
- `## How the parts connect`: append one line per new link the code shows that is not already a line. Do not edit a line that is already there.
- Diagram: keep every existing node and edge. Append a node or an edge the code shows that the fence does not already show. Do not rename a node. Do not redraw the fence. Do not invent a user, a service, or a queue. When the fence is still the template sample, replace that sample. It is not a real diagram.
- `repos.md`: append a row for a named repo that is not already listed. Add its `Synced at` line under `## Synced at`, set as under **Synced at** below. Do not rewrite an existing row.
- `glossary.md`: append a new row only for a word the code already uses that is not already a row. Do not rewrite an existing row. A new row goes in sorted place by term (1.84.0, `crav1-add-to-spec` `references/merge-safe.md`). The glossary rules above still apply. An accepted guess does not add a row.
- Feature index: when `docs/architecture/spec.md` exists and the architecture row is missing, append that one row. Do not rewrite other rows.
- `adr/`: do not rewrite an existing ADR. Write a new ADR only when the code shows a real choice, with real alternatives, that is not already an ADR. A guess is not an ADR.
- v0, bulk assumptions, and constraints: append a confirmed fact that is not already a line. Do not rewrite a line that is already there. Leave `None the code states.` in place.

When `docs/system/` is missing or only the untouched template, those notes are not already there. Write them with the first-write table. Still add only what is new to the architecture spec.

Do not run `/crav1-refresh-system-notes`. This pass is the add.

Do not write `plan.md`, `tasks.md`, `diagrams.md` inside the spec folder, `adr/` inside the spec folder, `export/`, `verify.md`, `fix-log.md`, `security.md`, or `work-item.md`. `docs/architecture/left-out.md` is the file for guesses that stay left out. Do not read `work-item-offer.md`. Do not write application code. Do not design the next feature. No goals for a feature, no acceptance list for work to build, no “should”.
