# Step 1, playbook

Read this only when the command names a playbook file. The file is a `report-playbook-short` or `report-playbook-full` report, outside the project or already at `docs/playbooks/<topic>.md`. Both are accepted. The playbook is intake only. It is not the source of truth.

Ask this question before any later step, including a read-only check such as readiness. Resume may already have reported status. No step runs until the choice below is answered.

Run `playbook-status` from `scripts/walk_progress.py` on that file. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. A `docs/playbooks/` path is the same playbook this walk recorded when the path matches.

- **already-applied** (this walk recorded `applied` or `reapplied` for the same file and the same contents): ask one question, even when the file has not changed. Do not move on without it. Options: `skip` (Recommended), `reapply`. `skip` records `Result: skipped` only when the previous result was not already an apply; if it was applied, leave the applied line as it is and move on. `reapply` shows the changes and writes only on yes.
- **already-skipped** (same file and contents, result `skipped`): options `skip` (Recommended), `apply`. `apply` is the show-changes path below.
- **not-recorded**, **changed**, or **different-file**: do not call it already applied. Show the changes, then apply only on yes.

Showing and applying uses the existing apply path, skill `crav1-resolve-open-questions`, `references/apply.md`, command `/crav1-resolve-open-questions apply <file>`. That file already sorts each filled item as new, already settled the same way, or conflicting, and it writes nothing until one yes. Kept items (K) are written through `/crav1-add-to-spec`'s rules inside that same apply. Do not call `/crav1-add-to-spec` again for those items. A second call would write them twice.

If that compare finds every filled item already settled the same way, say the playbook was already applied even though this walk has no progress line for it, and offer `skip` (Recommended) or `reapply`. The progress script cannot see that compare. It only knows what this walk recorded.

On yes, let apply write. Apply copies a filled playbook with `scripts/playbook_store.py` in skill `crav1-resolve-open-questions` (see that skill's `references/apply.md`). It shows the kebab-case name once before the first copy, and it shows the diff before overwrite when `Applied as:` says the committed file was edited in the repo. A `Docs path:` line, or the one committed file with the same subject, is the same playbook. The name stays fixed after that. Then record step `playbook` with result `applied` or `reapplied`, the `docs/playbooks/<topic>.md` path apply returned, and that file's content version. Do not record the outside path. On skip, record `skipped` when no apply line exists yet, and record the `docs/playbooks/` path when the playbook already has one. Empty answer lines stay open. Do not edit `Answer:` or `Change:` lines. A draft with no filled line is not copied.

A missing playbook file stops step 1. Say so. Do not invent answers.
