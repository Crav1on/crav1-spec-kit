# Shared rules

Guided only. There is no automatic mode. Every write is explained and confirmed before it happens, using the confirm the skill that owns the write already uses. Do not add a second confirm for the same write. Do not write on a headless or bot run. Stop and say the walk needs a person.

The spec folder is the one the user @-mentions. Otherwise the most recently edited tree under `docs/specs/`, excluding `_template`. If several are current, ask which slug once.

Two routes, one walk. With a playbook, step 1 is that file. Without a playbook, step 1 is skipped. Steps 2 through 7 are the same, and the ready check is the same.

Run each locked skill by following that skill's own `SKILL.md`. Do not copy its rules into this walk. Do not replace it.

This walk's own prompts are the playbook choice, asked even when that file is already applied, one batch of optional extras once after open questions when any extra applies, one batch for kept-open questions that still have no `Blocks:` line after the plan, one jump-back question when the check is not clear, and the yes before `walk-progress.md` is written. That yes shows the progress line, unless the step's own confirm already included this record. An extra's yes is that case. Questions inside a step belong to that step's skill.

The progress script is `scripts/walk_progress.py` in this skill. Use it for versions, resume, playbook status, and the ready check. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. The ready check is `readiness --root`. Do not hand-build rows. Do not keep a second copy of those rules in chat. Pass `--yes` only after you have shown the line and the user has confirmed that record.

When a playbook was named, ask that question before any later step, including a read-only check. Resume may report status. It does not start the next step.

After a step finishes, record that one step, then run `resume`. One `record` call per step, right then. Do not put several records in one command. Do not pass `--when`. `record` refuses more than one step. Recording updates earlier steps, so this step's write does not reopen them. When an optional extra this walk offered and ran finishes, record that extra in the same way. The yes that ran the extra is the yes for that record. Do not ask the user to run `cover`. A write in an earlier step can still reopen a later one. A change from outside the walk reopens only the steps that change affects. Explain that impact in the script's words before redoing only those steps.

Spec, plan, and tasks remain the source of truth. The progress file does not. A jump back reruns the skill that owns the step, even for a small patch. This walk does not edit `spec.md`, `plan.md`, or `tasks.md` on that jump, and it does not write the `Reviewed:` line.

Do not run `/crav1-build-tasks`, `/crav1-build-features`, `/crav1-verify-build-against-spec`, or `/crav1-fix-build-gaps`. Do not create a git commit. The playbook copy under `docs/playbooks/` is a file write inside apply, not a git commit.
