# Tasks to Azure Boards: **Child type**

Part of `branches/push-tasks/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.107.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

## Child type

Read the child work item type and its done state for **that task's home** from the lines in `docs/environments/marks.md`:

```text
Azure Boards task type (<project>): <type>
Azure Boards task done state (<project>): <state>
```

A line without `(<project>)` is the line for the marks.md project. Each home asks its own type once.

When the type line is there, use it. Do not ask. The user changes it by editing that line. When the type line is there and the done-state line is missing, read the type's states once as [references/child-items.md](../references/child-items.md) says and append the done-state line. Do not ask.

When the line is missing, read the project's work item types as [references/child-items.md](../references/child-items.md) says, and ask once which type a task becomes. Options only: the returned types.

Recommend one, as [references/child-items.md](../references/child-items.md) says. Read the project's process and its backlog levels. The recommendation is the type on the requirement backlog level, the level directly under Feature. Put it first, marked `(Recommended)`, with one plain reason:

| Process | Recommended | Reason |
| --- | --- | --- |
| Agile | User Story | A User Story sits directly under a Feature. A Task belongs under a User Story. |
| Scrum | Product Backlog Item | A Product Backlog Item sits directly under a Feature. |
| Basic | Issue | Issue is the requirement level in Basic. A Task belongs under an Issue. |
| CMMI | Requirement | A Requirement sits directly under a Feature. |

An inherited or custom process uses its requirement backlog level, whatever its name. Use the type that level returns, not the table, when they differ. Offer `Bug` as the recommendation only when the team tracks bugs as requirements. Otherwise `Bug` stays an option without a mark.

When the process or the backlog levels cannot be read, say so in one line and give no recommendation. Do not guess from the type names.

Use the questions tool when it is available. Stop until they pick. Then read that type's states, as [references/child-items.md](../references/child-items.md) says: the done state is the state in the `Completed` category, for example `Closed` on Agile and `Done` on Scrum and Basic. Append the type line and the done-state line to `docs/environments/marks.md`. Create the file when it is missing. Do not rewrite other lines. When the states cannot be read, say so, append only the type line, and send no state other than New in this run.

Then read that type's fields once, as `azure-boards.md` reads the Feature fields, to see whether it has Acceptance Criteria.
