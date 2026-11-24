# crav1-verify-build-against-spec: scoped verify

Read when a previous `verify.md` exists, before re-verifying. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says.

## Re-verify only what moved (1.172.0)

With a previous `verify.md`, run `scripts/verify_rows.py scope --file docs/specs/<slug>/verify.md --repo <code repo>` first. Verify again only the `rerun` rows: a row whose branch or tip moved, a row with no recorded tip, or every row when spec.md, plan.md or tasks.md changed (a ticked checkbox does not count). Keep the `kept` rows as they are, and print its `kept_line` in the reply. Do not rerun live checks for a kept row.

Write each row with `scripts/verify_rows.py set --file <verify.md> --task T# --status "<status>" --evidence "<evidence>" --branch <branch> --tip <sha> --yes`. It recounts the TL;DR and records the tip under `## Row tips`. Do not edit rows one line at a time. Adding or rewriting one row does not move the whole-file `Spec stamp:` (1.182.0), so rows that were not verified again still rerun after a spec change. When `scope` said every row reruns, add `--all-rows` to the last row's `set`; that moves the stamp.
