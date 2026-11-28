# UI gate (1.211.0)

Read this before any file is written, every run. A slice with no UI passes in one line.

Run `<interpreter> -X utf8 ../crav1-design-ui/scripts/ui_screens.py gate --root <spec-folder> --text` (skill `crav1-design-ui`), as `crav1-docs/reference/running-scripts.md` says, and show its lines as printed. It writes nothing.

- It compares each screen in `ui/experience.md` and `ui/design.md` with its item's `Screen:` mark under `## Approval needed`. A `Cleared:` mark, or a material change since the yes, counts as no yes. A typo keeps the yes.
- A `UI: none` line in `spec.md`, or a spec that names no screen and has no `ui/` folder, means no UI step: plan the whole slice as usual.
- **Run next printed** (a UI slice with no signed-off screen, an unclear UI, or a binary file under `ui/`): stop. Write neither `plan.md` nor `tasks.md`, and end with that Run next as printed. It names `$crav1-design-ui` and `$crav1-record-approval`.
- **Otherwise** the plan covers only the signed-off screens the gate names. A screen still waiting for its yes gets no task; list it under Risks as waiting for sign-off.

## Planning the signed-off screens

- Read `ui/design.md` and `ui/experience.md` for those screens. Never read `ui/mock/`: the mock is not a plan input and never a file likely touched.
- Each check `(S<n>-C<n>)` of a signed-off screen maps to a task with `(verify: ui — <named check>) (spec: ui/experience.md S<n>-C<n>)`, or `browser` when the check needs the whole path.
- After `tasks.md` is written, run the same script with `trace --root <spec-folder>` and fix every `UI checks with no task` line, and every `Tasks for screens with no yes` line, before the recap.
- No screenshot or pixel comparison is a check. Verify marks the written line.
