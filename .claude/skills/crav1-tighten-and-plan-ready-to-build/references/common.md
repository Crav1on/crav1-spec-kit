# Shared rules

Guided only. There is no automatic mode. Every write is explained and confirmed before it happens, using the confirm the skill that owns the write already uses. Do not add a second confirm for the same write. Do not write on a headless or bot run. Stop and say the walk needs a person.

The spec folder is the one the user @-mentions. Otherwise the most recently edited tree under `docs/specs/`, excluding `_template`. If several are current, ask which slug once.

Two routes, one walk. With a playbook, step 1 is that file. Without a playbook, step 1 is skipped. Steps 2 through 7 are the same, and the ready check is the same.

Run each locked skill by following that skill's own `SKILL.md`. Do not copy its rules into this walk. Do not replace it.

This walk's own prompts are the playbook choice, one batch of optional offers when any apply, one jump-back question when the check is not clear, and the yes before `walk-progress.md` is written when that yes is not already the step's confirm. Questions inside a step belong to that step's skill.

The progress script is `scripts/walk_progress.py` in this skill. Use it for versions, resume, playbook status, and the ready-check map. Do not keep a second copy of those rules in chat. Pass `--yes` only after the user has confirmed that record.

After a step finishes, run `resume` again. A write in an earlier step can reopen a later one. Explain that impact in the script's words before redoing only those steps.

Spec, plan, and tasks remain the source of truth. The progress file does not.

Do not run `/crav1-build-tasks`, `/crav1-build-features`, `/crav1-verify-build-against-spec`, or `/crav1-fix-build-gaps`. Do not commit.
