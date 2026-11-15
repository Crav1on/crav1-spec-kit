# verify.md behind (1.136.0)

Read this when `readiness --root` sets `verify_behind`, or when a task is recorded merged and still unticked.

`verify_behind` is true when a ticked task is still `Not implemented`, when a `Next:` line in `verify.md` names a ticked task, or when a merged unticked task is still `Not implemented`. Merged means `(PR n)` and the word `merged` on the task line, or on the Match `Branch:` line for its `(branch:)` or `(map:)` branch. There is no host check.

A merged task whose row is still `[ ]`, and whose verify status is `Implemented, verified, tick pending`, is not behind. The checkbox is the only leftover. A `Next:` line that names that task is not stale. Merged tasks stay done for dependents and for `can_start`.

A `verify.md` table row for a T# that does not exist in `tasks.md` is an orphan row (1.153.0). Since 1.167.0 it is in the ending's `**Catch up first**` block at the top of Run next, with `/crav1-verify-build-against-spec <slug>`, which drops that row when it rewrites the Tasks overview. Report only; this check does not edit `verify.md`, and the reply never says to edit it by hand.

Since 1.167.0 verify.md behind is the `**Catch up first**` block (`catch_up` in the JSON, already in `ending`), not a Waiting line: `Check T4 and T7 against the spec:` and `` `/crav1-verify-build-against-spec <slug>` ``. A behind task and an orphan row share that one command and one label. A specs repo ahead of origin adds `Push the specs repo (<n> commits ahead):` and `` `git push` `` to the same block. `verify_waiting` stays in the JSON. Do not print `stale_next`. A verify-only change does not force `not-ready`. The result stays `ready` or `ready-partial`, and `verify_waiting` is shown when verify is behind. This command writes only `build-map.md`. It does not write `verify.md`. It does not restamp `walk-progress.md`. Only the walk's record or `clear --yes` restamps that file.

`scripts/task_order.py` treats a recorded-merged task as done. It is not Ready and not Next. It is listed under `Needs tick` while the box is open. A `Waits in order` line includes the short title.
