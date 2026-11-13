# Needs yes (1.141.0)

Read only when `SKILL.md` says a worker returns `needs_yes`. Do not open this file on `done`. The rules are unchanged.

A worker `needs_yes` is waiting, not blocked. The task stays unticked. The parent offers the Approval needed item, as skill `crav1-build-tasks`, `references/approval-needed.md` says. It does not write `Approved:`.
