# Progress file

Read this when `walk-progress.md` is already beside the spec, and again when you record a step. The file is `docs/specs/<slug>/walk-progress.md`. It records completed steps, when, and the version of each file that step covered. It is not the source of truth.

The script `scripts/walk_progress.py` in this skill reads and writes it. Do not hand-edit it. `record` writes only with `--yes`. Show the progress line and get a yes before `record --yes`. The answers inside tighten, open questions, or the plan do not cover that line. Skip this confirm only when the step's own confirm already included this record. An extra's yes is that case, and it stays one confirm.

A version is the first 12 hex characters of the SHA-256 of the file's bytes. A missing file is `missing`. The playbook version is the same kind of hash, of the committed file when one exists. A spec change does not reopen the playbook step. The playbook is intake only. After apply, the `Playbook:` line is `docs/playbooks/<topic>.md@<12 hex>`, not the outside path, so resume works on any machine. The script stores that docs path when the file has a `Docs path: docs/playbooks/<topic>.md` line or the same subject as a file under `docs/playbooks/`. Specs apply touched use `Playbook: docs/playbooks/<topic>.md`.

Shape of the file:

```text
Walk: tighten-and-plan-ready-to-build
Slice: docs/specs/orders-retry/

- Step: playbook
  Done: 2026-11-09T10:19:09+01:00
  Result: applied
  Playbook: docs/playbooks/orders-retry.md@a1b2c3d4e5f6

- Step: plan-from-spec
  Done: 2026-11-09T10:19:09+01:00
  Result: done
  Spec version: a1b2c3d4e5f6
  Plan version: b2c3d4e5f6a1
  Tasks version: c3d4e5f6a1b2

- Step: tasks-ready-to-build
  Done: 2026-11-09T10:19:09+01:00
  Result: ready
  Spec version: a1b2c3d4e5f6
  Plan version: b2c3d4e5f6a1
  Tasks version: c3d4e5f6a1b2
  Verify version: missing
```

A playbook step records `Playbook:` only. It does not record spec, plan, or tasks versions. Other result words are `skipped` and `reapplied`. The ready check records `Result: ready` when the readiness output says ready, and `Result: not-ready` when it does not. Do not record `Result: done` for that step. An older `Result: done` on that step still reads as recorded. Resume treats `ready`, `not-ready`, and an older `done` as recorded. The ready check is the only step that records `Verify version:`. An extra records spec, plan, and tasks versions:

```text
- Extra: review-security
  Done: 2026-11-09T10:19:09+01:00
  Result: done
  Spec version: a1b2c3d4e5f6
  Plan version: b2c3d4e5f6a1
  Tasks version: c3d4e5f6a1b2
```

The script stamps `Done` itself, as `YYYY-MM-DDTHH:MM:SS+HH:MM`. Do not pass `--when`. A date alone is rejected. Record one step per call, right when that step finishes. Do not record several steps in one command. `resume` and `readiness` return `done_stamp_warning` when two or more steps share a Done stamp that has not been acknowledged. Say that warning. Those steps were recorded together. The times are not evidence each one finished then.

A shared stamp from before the one-step rule can be acknowledged once. Show the line, get a yes, then run `walk_progress.py ack-stamps --root <spec-folder> --yes`. It writes one line, before the steps:

```text
Acknowledged stamp: 2026-11-10T12:00:00+00:00 (tighten-spec, resolve-open-questions)
```

After that line, the warning stays quiet for those records. A new shared stamp warns again. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says.

Recording a step updates the versions on earlier steps. Their `Done` and `Result` stay. A later step's write does not reopen them. That includes a plan step that edits the plan.

An optional extra this walk offered and ran is recorded when it finishes, before `resume`. The user does not run `cover` for that. The line is `- Extra: review-security` (or `research`, `model-data`, `show-or-ask-open-questions`, `suggest-tests-for-code`), with `Done`, `Result`, and the spec, plan, and tasks versions. The yes that ran the extra is enough. That record leaves earlier steps done. An extra is not a locked step. Resume does not stop on it, and a later outside change does not reopen it.

`cover --yes` is optional. It counts the current spec, plan, tasks, and verify as part of the walk and does not add an `- Extra:` line. Use it when a write happened outside this walk and you want that write counted here. It does not touch the playbook line.

A change from outside the walk is one nobody recorded or covered. A hand edit, or `/crav1-add-to-spec` between sessions, is outside. Resume then reopens only the steps that change affects.

- A spec change reopens tighten-spec, resolve-open-questions, and the plan steps. It does not reopen the architecture review once a later spec step is recorded. When that review is the only spec step so far, a spec change reopens it.
- A plan or tasks change reopens the plan review and the ready check. It does not reopen plan-from-spec. A spec change does, because the plan was written from the spec.
- A `verify.md` change reopens only the ready check. A playbook file change reopens only the playbook step.

At the start of a run, resume before recording anything. Resume may report status. When a playbook was named, it does not start a later step, and the playbook question is answered first, including before a read-only check. Redo `continue_from` only after that choice. Do not record a later step to clear an earlier reopen.

On resume, run `resume`. With no playbook on this command, add `--no-playbook` so a playbook step that was never started stays skipped. The script returns `keep`, `reopen`, or `not-started`, and `continue_from`. A recorded extra is `keep` and does not change `continue_from`. Explain each reopen with its `impact` before redoing it. Leave `keep` steps as they are. After a step or an extra is recorded, run `resume` again.

`clear --step <id> --yes` refreshes one reopened step after the user says `nothing new`. `Done` and `Result` stay. Other steps stay as they are. That is the path when a reopened step has nothing new. Do not record `nothing-to-do` over it. A `nothing-to-do` record keeps an earlier `done` Result.

`playbook-status` answers whether this walk already applied that file. It does not read the spec. The apply compare in step 1 does that.

## Stop

When the user stops partway, including after a record, end with one paused-at line and the shared ending. No other next-step prose.

```text
Paused at resolve-open-questions.
Next: /crav1-tighten-and-plan-ready-to-build docs/playbooks/orders-retry.md, because the walk paused before plan-from-spec.
Uncommitted: 2 files; commit with /crav1-finalize-commit when ready.
```

`Paused at` is the step just recorded, or the step they stopped in. `Next` names this command and `continue_from` from `resume`. Include the playbook path when `resume` returns one. Add `Waiting:` only when that next step is blocked. Leave `Uncommitted:` out when nothing is uncommitted.
