# UI checks (1.211.0)

Read this only when a task's verify note is `(verify: ui — <named check>)`.

- The check is the written line in `ui/experience.md` that the task's `(spec: ui/experience.md S1-C1)` names. Open that line and look at the running screen in the browser. Mark it **pass** or **fail** with what you saw, or **untested** with the reason when no browser or running host is there.
- The written Markdown is the source of truth. There is no screenshot or pixel comparison against the mock or a PlantUML Salt block. The mock under `ui/mock/` is not evidence and not the thing under test.
- Do not save a screenshot under `docs/specs/`. Describe what the screen showed in the evidence cell.
- A UI check whose screen has no yes (its Approval needed item has no `Approved:` line, or a `Cleared:` mark after it) was not planned. Its row is **missing**, not a failure.
