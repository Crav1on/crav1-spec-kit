# Progress file

Read this when `walk-progress.md` is already beside the spec, and again when you record a step. The file is `docs/specs/<slug>/walk-progress.md`. It records completed steps, when, and the version of each file that step covered. It is not the source of truth.

The script `scripts/walk_progress.py` in this skill reads and writes it. Do not hand-edit it. `record` writes only with `--yes`, after you have shown the line and the user has confirmed.

A version is the first 12 hex characters of the SHA-256 of the file's bytes. A missing file is `missing`. The playbook version is the same kind of hash. A spec change does not reopen the playbook step. The playbook is intake only.

Shape of the file:

```text
Walk: tighten-and-plan-ready-to-build
Slice: docs/specs/orders-retry/

- Step: playbook
  Done: 2026-11-09T10:19:09+01:00
  Result: applied
  Playbook: docs/notes/2026-11/orders-playbook.md@a1b2c3d4e5f6

- Step: plan-from-spec
  Done: 2026-11-09T10:19:09+01:00
  Result: done
  Spec version: a1b2c3d4e5f6
  Plan version: b2c3d4e5f6a1
  Tasks version: c3d4e5f6a1b2

- Step: tasks-ready-to-build
  Done: 2026-11-09T10:19:09+01:00
  Result: nothing-to-do
  Spec version: a1b2c3d4e5f6
  Plan version: b2c3d4e5f6a1
  Tasks version: c3d4e5f6a1b2
  Verify version: missing
```

A playbook step records `Playbook:` only. It does not record spec, plan, or tasks versions. Other result words are `skipped` and `reapplied`. The ready check is the only step that records `Verify version:`.

On resume, run `resume`. With no playbook on this command, add `--no-playbook` so a playbook step that was never started stays skipped. The script returns `keep`, `reopen`, or `not-started`, and `continue_from`. Explain each reopen with its `impact` before redoing it. Leave `keep` steps as they are. After a step writes, run `resume` again.

`playbook-status` answers whether this walk already applied that file. It does not read the spec. The apply compare in step 1 does that.
