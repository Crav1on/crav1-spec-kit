# Step 7, ready to build

Read this only at the ready check.

When a playbook was named, do not run this check until that question is answered. Resume may already have reported status.

Run `scripts/walk_progress.py readiness --root <spec-folder>`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. It runs `task_order.py` and `question_blocks.py`, builds the rows, and adds the `Reviewed:` warnings. Do not hand-build a rows JSON file. Do not pass `--json`. Use the script's step and command for each row. Do not invent a step the script leaves unmapped. Say the script has no step for it, and do not report ready.

Row buckets: `waits-in-order` is a task that only waits on an earlier real task. `waiting` is a task held by an open question. `blocked` is a true blocker only (a cycle, an `(after:)` that names no task, a missing plan or tasks file, a plan risk, or a question that is still a jump back).

Ready means the first task can start, the rest wait in order, and nothing else blocks. A reason `waits on T#` for a real task is not a hit. A cycle, or an `(after:)` that names no task, is a blocker.

A reopened walk step is a blocker. The script names it and sets `clear` to `nothing new`. The check is not ready while any step is reopened. Offer jump back and rerun that step (Recommended) only when `recommend_jump` is true, or clear it. Clear is the one line `nothing new`. On that, run `clear --step <id> --yes`, then run this check again. Do not record `nothing-to-do` for a reopened step. When the step was `done`, a `nothing-to-do` record keeps `done`.

The script maps:

- No `plan.md` or no `tasks.md` to `/crav1-plan-from-spec`.
- An open question to `/crav1-resolve-open-questions`, unless that step is already `keep` at the current spec. Then the row is `waiting`, not a jump back. Who comes first from the question's own "Waiting for <who>" phrase, then from the latest `Pending:` or `Asked:` line. When neither names anyone, who is `not named yet`, and that task still counts in `waiting_line`. `can_jump_back` is false. Do not mark that jump back Recommended. It cannot change anything.
- A plan risk, a cycle, or an `(after:)` mark that names no task to step 6, starting at `/crav1-tighten-plan` after `/crav1-review-plan` when the review line is missing.
- A plan-review warning (`plan review unknown`, or open `P#`) as an assumption, not as ready. The ready skill still lists those tasks as Ready with a warning. This walk does not. An open assumption is not a clear check.
- **Needs verify** to `/crav1-verify-build-against-spec`. That skill is outside this walk. Name it, do not jump into it, and do not start it.

When the script says the check is not ready, name each row's step in the words the script returns. Offer to jump back only for rows with `can_jump_back`. Options: jump back (Recommended) when `recommend_jump` is true, clear with `nothing new` when a walk step is reopened, or stop. On jump back, rerun the owning skill, even for a small patch, then run this check again. The walk does not edit `spec.md`, `plan.md`, or `tasks.md` on a jump back, and it does not write `Reviewed:`. That line belongs to `/crav1-review-plan`. On `nothing new`, clear only the step just named. A row that cannot jump back stays named. The check is still not ready.

When the only rows are `waiting`, do not offer jump back. The stop ending adds the script's `waiting_line`: `Waiting: <n> tasks wait on open questions (<who>).` Next is the script's `waiting_next`: `/crav1-show-or-ask-open-questions <slug>` when the questions are not asked yet, or this walk when the answers arrive.

Ready is only when the script says `ready` and `start_build` is false, with no blockers, no waiting, no Needs verify, and no assumptions. Then say the slice is ready to build. One line: `Next: /crav1-build-tasks, because the slice is ready to build.` Do not run it. Add the Uncommitted line when `walk-progress.md` is not committed. Stop.

When they pick stop and the check is not ready, and the rows are not only waiting, `Next` is the first jump-back row's command, because that row blocks ready. Do not list the other rows in the ending. They were already named in the check. This walk still runs a step when they pick jump back, by running that skill.

Record step `tasks-ready-to-build` when this check finishes, one `record` call, with the versions the script stores, including `Verify version:`, after the user confirms the record. Use `Result: ready` when the script says `ready`, and `Result: not-ready` when it does not. Do not record `Result: done` for this step. An older `Result: done` still reads as recorded. Do not batch it with other steps. Do not pass `--when`. A later change to `verify.md` reopens only this check.
