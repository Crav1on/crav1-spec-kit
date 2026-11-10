# Step 7, ready to build

Read this only at the ready check.

Run `/crav1-tasks-ready-to-build` for this slug. It writes nothing and runs no skill. Pass its rows to `scripts/walk_progress.py readiness`, with `--root` set to the spec folder. Use the script's step and command for each row. Do not invent a step the script leaves unmapped. Say the script has no step for it, and do not report ready.

A reopened walk step is a blocker. The script names it and sets `clear` to `nothing new`. The check is not ready while any step is reopened. Offer jump back and rerun that step (Recommended), or clear it. Clear is the one line `nothing new`. On that, run `clear --step <id> --yes`, then run this check again.

The script maps:

- No `plan.md` to `/crav1-plan-from-spec`.
- An open question to `/crav1-resolve-open-questions`.
- A plan risk, a dependency, a cycle, or an `(after:)` mark that names no task to step 6, starting at `/crav1-tighten-plan` after `/crav1-review-plan` when the review line is missing.
- A plan-review warning (`plan review unknown`, or open `P#`) as an assumption, not as ready. The ready skill still lists those tasks as Ready with a warning. This walk does not. An open assumption is not a clear check.
- **Needs verify** to `/crav1-verify-build-against-spec`. That skill is outside this walk. Name it, do not jump into it, and do not start it.

When the script says the check is not ready, name each row's step in the words the script returns. Offer to jump back. Options: jump back (Recommended) when at least one row can jump, clear with `nothing new` when a walk step is reopened, or stop. On jump back, rerun the affected steps in walk order, then run this check again. On `nothing new`, clear only the step just named. A row that cannot jump back stays named. The check is still not ready.

Ready is only when the script says `ready` and `start_build` is false, with no blockers, no Needs verify, and no assumptions. Then say the slice is ready to build. One line: `Next: /crav1-build-tasks, because the slice is ready to build.` Do not run it. Add the Uncommitted line when `walk-progress.md` is not committed. Stop.

When they pick stop and the check is not ready, `Next` is the first row's command, because that row blocks ready. Do not list the other rows in the ending. They were already named in the check. This walk still runs a step when they pick jump back.

Record step `tasks-ready-to-build` with the versions the script stores, including `Verify version:`, after the user confirms the record. A later change to `verify.md` reopens only this check.
