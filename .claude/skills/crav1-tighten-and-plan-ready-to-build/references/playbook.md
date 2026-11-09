# Step 1, playbook

Read this only when the command names a playbook file. The file is a `report-playbook-short` or `report-playbook-full` report. The playbook is intake only. It is not the source of truth.

Run `playbook-status` from `scripts/walk_progress.py` on that file.

- **already-applied** (this walk recorded `applied` or `reapplied` for the same file and the same contents): ask one question. Options: `skip` (Recommended), `reapply`. `skip` records `Result: skipped` only when the previous result was not already an apply; if it was applied, leave the applied line as it is and move on. `reapply` shows the changes and writes only on yes.
- **already-skipped** (same file and contents, result `skipped`): options `skip` (Recommended), `apply`. `apply` is the show-changes path below.
- **not-recorded**, **changed**, or **different-file**: do not call it already applied. Show the changes, then apply only on yes.

Showing and applying uses the existing apply path, skill `crav1-resolve-open-questions`, `references/apply.md`, command `/crav1-resolve-open-questions apply <file>`. That file already sorts each filled item as new, already settled the same way, or conflicting, and it writes nothing until one yes. Kept items (K) are written through `/crav1-add-to-spec`'s rules inside that same apply. Do not call `/crav1-add-to-spec` again for those items. A second call would write them twice.

If that compare finds every filled item already settled the same way, say the playbook was already applied even though this walk has no progress line for it, and offer `skip` (Recommended) or `reapply`. The progress script cannot see that compare. It only knows what this walk recorded.

On yes, let apply write. Then record step `playbook` with result `applied` or `reapplied`, the playbook path, and its content version. On skip, record `skipped` when no apply line exists yet. Empty answer lines stay open. Do not edit the playbook file.

A missing playbook file stops step 1. Say so. Do not invent answers.
