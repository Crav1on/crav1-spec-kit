# Walk restamp (1.148.0)

Read this only when the spec just written has `walk-progress.md` beside it.

Run `<interpreter> -X utf8 <skill crav1-tighten-and-plan-ready-to-build>/scripts/walk_progress.py resume --root <spec-folder> --no-playbook`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Do not run `python3` alone.

Say `reopen_line` once when it is present.

When `restamp_only` is true, the change is only `## Match`, `## In the code`, a `Synced at:` line, or an already-answered question. No step reopens. Offer one card:

- Restamp (Recommended). Run `walk_progress.py restamp-covered --root <spec-folder> --yes`. `Done` and `Result` stay.
- Leave the stamps. Do not run it. Resume still does not reopen.

A headless run takes Restamp. Do not reopen a step. Do not start the walk.

When `restamp_only` is false and `reopen_steps` is not empty, do not restamp. The walk reopens those steps on its next resume. This command does not run the walk.

When the line says `Reopen: none` and `restamp_only` is false, a question mark changed and the words did not. Do not restamp. Do not reopen.
