# verify.md behind (1.136.0)

Read this when `readiness --root` sets `verify_behind`, or when a task is recorded merged and still unticked.

`verify_behind` is true when a ticked task is still `Not implemented`, when a `Next:` line in `verify.md` names a ticked task, or when a merged unticked task is still `Not implemented`. Merged means `(PR n)` and the word `merged` on the task line, or on the Match `Branch:` line for its `(branch:)` or `(map:)` branch. There is no host check.

A merged task whose row is still `[ ]`, and whose verify status is `Implemented, verified, tick pending`, is not behind. The checkbox is the only leftover. A `Next:` line that names that task is not stale. Merged tasks stay done for dependents and for `can_start`.

A `verify.md` table row for a T# that does not exist in `tasks.md` is an orphan row (1.153.0). Print one Waiting line that names the T# and says to fix it with `/crav1-verify-build-against-spec` or `/crav1-tighten-plan`. Report only; do not edit `verify.md`.

Print `verify_waiting` and do not print `stale_next`. A verify-only change does not force `not-ready`. The result stays `ready` or `ready-partial`, and `verify_waiting` is shown when verify is behind. This command writes only `build-map.md`. It does not write `verify.md`. It does not restamp `walk-progress.md`. Only the walk's record or `clear --yes` restamps that file.

`scripts/task_order.py` treats a recorded-merged task as done. It is not Ready and not Next. It is listed under `Needs tick` while the box is open. A `Waits in order` line includes the short title.
