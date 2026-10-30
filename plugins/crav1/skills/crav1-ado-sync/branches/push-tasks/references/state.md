# Tasks to Azure Boards: **State**

Part of `branches/push-tasks/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.107.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

### State

The kit sets only two states: New and the saved done state. It never sets Active, Resolved, or any other in-progress state. Those stay with people. It never sends Reason. Azure Boards fills its default.

On a **Create**, an open box is created as New and a ticked box as the done state, so the Feature shows all its work.

On an **Update**, compare the `tasks.md` box with the State that `az boards work-item show` returns. Use the `tasks.md` git history (`git log -p -- docs/specs/<slug>/tasks.md`) to tell whether the box changed locally since the item was created.

| `tasks.md` box | State in Azure Boards | Preview |
| --- | --- | --- |
| Ticked | Done state | Nothing. They match |
| Ticked, and the tick is newer than the create | Not done (New, Active, Resolved, …) | Offer **State: <current> → <done state>** |
| Open, and the box was ticked before | Done state | Offer **Reopen: <done state> → New** |
| Open | Not done | Nothing. Leave Active or any other state as it is |
| Ticked, and the tick is not newer than the create; or open, and never ticked in the history | Done state differs from the box |  **Conflict.** Show both sides: the box and its last change in `tasks.md`, and the Azure Boards State with who changed it and when from the history. Ask each time: set Azure Boards to match `tasks.md`, or leave Azure Boards and bring it back with the pull tasks branch of `/crav1-ado-sync`, or leave both |

When the history cannot tell, treat the row as a conflict and ask. Never pick a winner on your own. A state change is its own line in the preview and its own yes. Send it only on that yes. A skip leaves the State as it is.
